from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
from typing import Any

from .guardrails import Budget, GuardrailError, SafetyPolicy
from .models import AgentState, AgentTrace, ApprovalRequest, Observation, Provenance, ToolResult, utc_now
from .providers import LLMProvider


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], ToolResult]
    requires_approval: bool = False

    def validate_arguments(self, arguments: dict[str, Any]) -> None:
        if not isinstance(arguments, dict):
            raise GuardrailError(f"tool_arguments_must_be_object:{self.name}")
        required = self.input_schema.get("required", [])
        missing = [name for name in required if name not in arguments]
        if missing:
            raise GuardrailError(f"missing_tool_arguments:{self.name}:{','.join(missing)}")
        _validate_schema_value(arguments, self.input_schema, self.name, "arguments")


def _validate_schema_value(value: Any, schema: dict[str, Any], tool_name: str, path: str) -> None:
    """Small dependency-free JSON-schema subset for model-produced arguments."""
    if "enum" in schema and value not in schema["enum"]:
        raise GuardrailError(f"invalid_enum:{tool_name}:{path}")
    expected = schema.get("type")
    type_ok = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }
    if expected in type_ok and not type_ok[expected]:
        raise GuardrailError(f"invalid_argument_type:{tool_name}:{path}:{expected}")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise GuardrailError(f"unknown_tool_arguments:{tool_name}:{','.join(unknown)}")
        for key, child in properties.items():
            if key in value and isinstance(child, dict):
                _validate_schema_value(value[key], child, tool_name, f"{path}.{key}")
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for index, item in enumerate(value):
            _validate_schema_value(item, schema["items"], tool_name, f"{path}[{index}]")


def _redact(value: Any, key: str = "") -> Any:
    if any(token in key.lower() for token in ("api_key", "token", "secret", "password", "credential")):
        return "REDACTED"
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v, key) for v in value]
    if isinstance(value, str):
        import re
        return re.sub(r"(?i)(fg_live_|sk-)[A-Za-z0-9_-]+", r"\1REDACTED", value)
    return value


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"duplicate_tool:{spec.name}")
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise GuardrailError(f"unknown_tool:{name}") from exc

    def names(self) -> set[str]:
        return set(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [{"name": t.name, "description": t.description, "parameters": t.input_schema} for t in self._tools.values()]


class AgentRunner:
    def __init__(self, registry: ToolRegistry, provider: LLMProvider, *, budget: Budget | None = None, policy: SafetyPolicy | None = None) -> None:
        self.registry = registry
        self.provider = provider
        self.budget = budget or Budget()
        self.policy = policy or SafetyPolicy(allowed_tools=registry.names())

    def run(self, state: AgentState) -> tuple[AgentState, AgentTrace]:
        trace = AgentTrace()
        trace.record("goal_started", goal_id=state.goal.goal_id, text=state.goal.text)
        called_tools: list[str] = []
        while not state.terminated:
            try:
                self.budget.before_iteration()
                state.iteration = self.budget.iterations
                input_chars = len(json.dumps({
                    "goal": state.goal.text,
                    "constraints": state.goal.constraints,
                    "observations": [observation.content for observation in state.observations[-8:]],
                }, sort_keys=True, default=str))
                self.budget.before_model_call(input_chars)
                try:
                    decision = self.provider.next_decision(state)
                except Exception as exc:
                    state.terminated = True
                    state.termination_reason = f"provider_error:{type(exc).__name__}"
                    trace.record("provider_error", error=_redact(str(exc)[:240]))
                    break
                # Do not persist model prose or hidden reasoning in the audit trace.
                trace.record("provider_decision", kind=decision.kind, tool_name=decision.tool_name)
                if decision.kind == "finish":
                    state.terminated = True
                    state.termination_reason = decision.message or "provider_finished"
                    break
                if decision.kind == "proposal" and decision.proposal is not None:
                    if "verify_schedule" in self.registry.names() and not any(
                        observation.kind == "tool_result"
                        and observation.content.get("data", {}).get("status") in {"VERIFIED", "VALID"}
                        for observation in state.observations
                    ):
                        raise GuardrailError("recommendation_before_deterministic_verification")
                    proposal = decision.proposal
                    state.proposals.append(proposal)
                    if proposal.requires_approval or self.policy.needs_approval(proposal.action_type):
                        state.approvals.append(ApprovalRequest(proposal=proposal))
                        state.termination_reason = "awaiting_human_approval"
                    else:
                        state.termination_reason = "recommendation_ready"
                    state.terminated = True
                    trace.record("action_proposed", action_type=proposal.action_type, confidence=proposal.confidence, requires_approval=proposal.requires_approval)
                    break
                if decision.kind != "tool_call" or not decision.tool_name:
                    raise GuardrailError("malformed_provider_decision")
                name = decision.tool_name
                self.policy.check_tool(name, called_tools)
                spec = self.registry.get(name)
                spec.validate_arguments(decision.arguments)
                cost = self.budget.reserve_tool(name)
                trace.record("tool_call_started", tool_name=name, arguments=_redact(decision.arguments), reserved_credits=cost)
                try:
                    result = spec.handler(decision.arguments)
                except Exception as exc:
                    result = ToolResult({}, Provenance(source="heuristic", endpoint=f"tool:{name}", assumptions=("handler failure was converted to a bounded observation",)), error=f"tool_execution_error:{type(exc).__name__}")
                called_tools.append(name)
                state.observations.append(Observation(kind="tool_result" if result.ok else "error", content=result.to_dict()))
                try:
                    self.provider.observe(result, state, decision.tool_call_id)
                except TypeError:
                    # Preserve compatibility with older provider implementations.
                    self.provider.observe(result, state)
                trace.record("tool_call_finished", tool_name=name, ok=result.ok, provenance=result.provenance.source, error=_redact(result.error or ""))
            except GuardrailError as exc:
                state.terminated = True
                reason = str(exc)
                if reason in {"iteration_limit_reached", "model_call_limit_reached", "model_input_limit_reached"}:
                    reason = f"safe_incomplete_abstention:{reason}"
                state.termination_reason = reason
                state.observations.append(Observation(kind="error", content={"error": str(exc)}))
                trace.record("guardrail_stop", reason=str(exc))
        trace.record("goal_finished", reason=state.termination_reason, iterations=state.iteration, model_calls=self.budget.model_calls, tool_calls=self.budget.tool_calls, reserved_credits=self.budget.api_credits_reserved)
        return state, trace

    @staticmethod
    def resolve_approval(state: AgentState, index: int, approved: bool) -> AgentState:
        """Resolve a pending recommendation without executing external actions."""
        if index < 0 or index >= len(state.approvals):
            raise IndexError("approval_index_out_of_range")
        request = state.approvals[index]
        if request.status != "pending":
            raise ValueError("approval_already_resolved")
        request.status = "approved" if approved else "rejected"
        request.decided_at = utc_now()
        state.termination_reason = "approved_recommendation" if approved else "rejected_recommendation"
        return state
