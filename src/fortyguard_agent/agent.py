from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
from typing import Any

from .guardrails import Budget, GuardrailError, SafetyPolicy
from .cache import request_hash
from .models import AgentState, AgentTrace, ApprovalRequest, Observation, Provenance, ToolResult, utc_now
from .providers import LLMProvider
from .state_machine import (
    THERMAL_OPERATIONAL_ACTIONS,
    TERMINAL_STATES,
    authoritative_evidence_from_constraints,
    normalize_invalid_evidence,
    terminal_status,
    workflow_requires_thermal_evidence,
)


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
    MAX_MODEL_STOP_CONTINUATIONS = 1

    def __init__(self, registry: ToolRegistry, provider: LLMProvider, *, budget: Budget | None = None, policy: SafetyPolicy | None = None) -> None:
        self.registry = registry
        self.provider = provider
        self.budget = budget or Budget()
        self.policy = policy or SafetyPolicy(allowed_tools=registry.names())

    def run(self, state: AgentState) -> tuple[AgentState, AgentTrace]:
        trace = AgentTrace()
        trace.record("goal_started", goal_id=state.goal.goal_id, text=state.goal.text)
        called_tools: list[str] = []
        rejected_model_stops = 0
        if self._apply_authoritative_state(state, trace):
            trace.record("goal_finished", reason=state.termination_reason, iterations=state.iteration, model_calls=0, tool_calls=0, reserved_credits=0)
            return state, trace
        while not state.terminated:
            try:
                if self._apply_authoritative_state(state, trace):
                    break
                self.budget.before_iteration()
                state.iteration = self.budget.iterations
                input_chars = len(json.dumps({
                    "goal": state.goal.text,
                    "constraints": state.goal.constraints,
                    "observations": [observation.content for observation in state.observations[-8:]],
                }, sort_keys=True, default=str))
                self.budget.before_model_call(input_chars)
                try:
                    complete = getattr(self.provider, "complete", self.provider.next_decision)
                    decision = complete(state)
                except Exception as exc:
                    safe_mode_factory = getattr(self.provider, "safe_mode_result", None)
                    if callable(safe_mode_factory):
                        safe_result = safe_mode_factory(state)
                        state.terminated = True
                        state.termination_reason = "AI_ANALYSIS_UNAVAILABLE"
                        state.operational_state = "AI_ANALYSIS_UNAVAILABLE"
                        state.observations.append(Observation(kind="error", content=safe_result.to_dict()))
                        trace.record("provider_error", error=_redact(str(exc)[:240]))
                        trace.record("safe_mode", status="AI_ANALYSIS_UNAVAILABLE", current_plan_preserved=True, retry_available=True, fabrication_count=0)
                        break
                    state.terminated = True
                    state.termination_reason = f"provider_error:{type(exc).__name__}"
                    trace.record("provider_error", error=_redact(str(exc)[:240]))
                    break
                # Do not persist model prose or hidden reasoning in the audit trace.
                trace.record("provider_decision", kind=decision.kind, tool_name=decision.tool_name)
                if decision.kind == "finish":
                    terminal = self._finish_reason(state, decision.message)
                    if terminal is not None:
                        self._set_terminal(state, terminal)
                        break
                    # A provider stop is only a transport/model event.  Give
                    # the provider one bounded continuation opportunity, then
                    # fail closed instead of accepting prose as a workflow
                    # terminal or looping forever.
                    rejected_model_stops += 1
                    trace.record("model_stop_rejected", reason="non_terminal_workflow_state", continuation=rejected_model_stops)
                    if rejected_model_stops <= self.MAX_MODEL_STOP_CONTINUATIONS:
                        state.observations.append(Observation(kind="error", content={"error": "model_stop_before_terminal_state", "decision_relevant_result": "CONTINUE_WORKFLOW"}))
                        continue
                    self._set_safe_error(state, trace, "model_stop_before_terminal_state")
                    break
                if decision.kind == "proposal" and decision.proposal is not None:
                    if self._apply_authoritative_state(state, trace):
                        break
                    if self._thermal_evidence_required_but_missing(state):
                        self._set_evidence_unavailable(state, trace, "proposal_forbidden_without_valid_evidence")
                        break
                    if "verify_schedule" in self.registry.names() and not any(
                        observation.kind == "tool_result"
                        and observation.content.get("data", {}).get("status") in {"VERIFIED", "VALID"}
                        for observation in state.observations
                    ):
                        raise GuardrailError("recommendation_before_deterministic_verification")
                    proposal = decision.proposal
                    state.proposals.append(proposal)
                    if proposal.requires_approval or self.policy.needs_approval(proposal.action_type):
                        verified = next((observation.content.get("data", {}) for observation in reversed(state.observations) if observation.kind == "tool_result" and observation.content.get("data", {}).get("status") == "VERIFIED"), {})
                        state.approvals.append(ApprovalRequest(
                            proposal=proposal,
                            candidate_hash=verified.get("schedule_hash"),
                            evidence_hash=verified.get("evidence_hash") or verified.get("evidence_provenance_hash"),
                            policy_version=verified.get("policy_version"),
                            task_state_hash=verified.get("task_state_hash"),
                            verification_hash=request_hash("local:verification", verified) if verified else None,
                        ))
                        state.termination_reason = "awaiting_human_approval"
                    else:
                        state.termination_reason = "recommendation_ready"
                        state.operational_state = "AWAITING_APPROVAL" if not proposal.requires_approval else "AWAITING_APPROVAL"
                    state.terminated = True
                    if proposal.requires_approval or self.policy.needs_approval(proposal.action_type):
                        state.operational_state = "AWAITING_APPROVAL"
                    trace.record("action_proposed", action_type=proposal.action_type, confidence=proposal.confidence, requires_approval=proposal.requires_approval)
                    break
                if decision.kind != "tool_call" or not decision.tool_name:
                    raise GuardrailError("malformed_provider_decision")
                name = decision.tool_name
                self._guard_thermal_action(state, name)
                self.policy.check_tool(name, called_tools)
                spec = self.registry.get(name)
                spec.validate_arguments(decision.arguments)
                cost = self.budget.reserve_tool(name)
                trace.record("tool_call_started", tool_name=name, arguments=_redact(decision.arguments), reserved_credits=cost)
                try:
                    result = spec.handler(decision.arguments)
                except Exception as exc:
                    result = ToolResult({}, Provenance(source="heuristic", endpoint=f"tool:{name}", assumptions=("handler failure was converted to a bounded observation",)), error=f"tool_execution_error:{type(exc).__name__}")
                normalized_data = dict(result.data)
                if result.error:
                    normalized_data["error"] = result.error
                normalized = normalize_invalid_evidence(normalized_data)
                if normalized is not None:
                    result = ToolResult(normalized, result.provenance, error=result.error, estimated_credits=result.estimated_credits)
                called_tools.append(name)
                state.observations.append(Observation(kind="tool_result" if result.ok else "error", content=result.to_dict()))
                try:
                    self.provider.observe(result, state, decision.tool_call_id)
                except TypeError:
                    # Preserve compatibility with older provider implementations.
                    self.provider.observe(result, state)
                trace.record("tool_call_finished", tool_name=name, ok=result.ok, provenance=result.provenance.source, error=_redact(result.error or ""))
                terminal = self._deterministic_terminal(result)
                if terminal is not None:
                    self._set_terminal(state, terminal, result.data)
                    trace.record("deterministic_terminal", status=terminal)
            except GuardrailError as exc:
                if str(exc).startswith("thermal_action_forbidden_without_evidence:"):
                    self._set_evidence_unavailable(state, trace, str(exc))
                    break
                state.terminated = True
                state.operational_state = "ERROR_SAFE"
                reason = str(exc)
                if reason in {"iteration_limit_reached", "model_call_limit_reached", "model_input_limit_reached"}:
                    reason = f"safe_incomplete_abstention:{reason}"
                state.termination_reason = reason
                state.observations.append(Observation(kind="error", content={"error": str(exc)}))
                trace.record("guardrail_stop", reason=str(exc))
        trace.record("goal_finished", reason=state.termination_reason, iterations=state.iteration, model_calls=self.budget.model_calls, tool_calls=self.budget.tool_calls, reserved_credits=self.budget.api_credits_reserved)
        telemetry = getattr(self.provider, "telemetry", None)
        if callable(telemetry):
            trace.record("provider_telemetry", **telemetry())
        return state, trace

    @staticmethod
    def _set_terminal(state: AgentState, status: str, result: dict[str, Any] | None = None) -> None:
        operational = terminal_status(status) or "ERROR_SAFE"
        state.operational_state = operational
        state.authoritative_result = result
        state.terminated = True
        state.termination_reason = "awaiting_human_approval" if operational == "AWAITING_APPROVAL" else operational

    @classmethod
    def _set_safe_error(cls, state: AgentState, trace: AgentTrace, reason: str) -> None:
        result = {
            "status": "ERROR_SAFE",
            "valid": False,
            "decision_relevant_result": "CURRENT_PLAN_PRESERVED",
            "provenance": "DETERMINISTIC_RUNTIME_GUARD",
            "next_allowed_actions": ["KEEP_CURRENT_PLAN", "RECHECK_AVAILABLE"],
            "current_plan_preserved": True,
            "thermal_optimization_allowed": False,
            "error": reason,
        }
        state.observations.append(Observation(kind="error", content={"data": result}))
        cls._set_terminal(state, "ERROR_SAFE", result)
        trace.record("guardrail_stop", reason=reason)

    @classmethod
    def _set_evidence_unavailable(cls, state: AgentState, trace: AgentTrace, reason: str) -> None:
        result = normalize_invalid_evidence(
            {"status": "EVIDENCE_UNAVAILABLE", "error": reason},
            provenance="DETERMINISTIC_WORKFLOW_AUTHORITY",
        )
        assert result is not None
        state.observations.append(Observation(kind="error", content={"data": result}))
        cls._set_terminal(state, "EVIDENCE_UNAVAILABLE", result)
        trace.record("deterministic_terminal", status="EVIDENCE_UNAVAILABLE", source="action_guard", reason=reason)

    @staticmethod
    def _has_valid_thermal_evidence(state: AgentState) -> bool:
        for observation in state.observations:
            content = observation.content if isinstance(observation.content, dict) else {}
            data = content.get("data") if isinstance(content.get("data"), dict) else content
            if data.get("valid") is True and (
                data.get("thermal_evidence_valid") is True
                or data.get("status") == "VALID_THERMAL_EVIDENCE"
                or data.get("decision_relevant_result") == "THERMAL_EVIDENCE_AVAILABLE"
            ):
                return True
        return False

    @classmethod
    def _thermal_evidence_required_but_missing(cls, state: AgentState) -> bool:
        return workflow_requires_thermal_evidence(state.goal.constraints) and not cls._has_valid_thermal_evidence(state)

    @classmethod
    def _apply_authoritative_state(cls, state: AgentState, trace: AgentTrace) -> bool:
        """Apply deterministic evidence state before a model can act or stop."""
        if state.operational_state == "EVIDENCE_UNAVAILABLE":
            state.terminated = True
            return True
        for observation in reversed(state.observations):
            content = observation.content if isinstance(observation.content, dict) else {}
            data = content.get("data") if isinstance(content.get("data"), dict) else content
            normalized = normalize_invalid_evidence(data)
            if normalized is not None:
                if state.authoritative_result != normalized:
                    state.observations.append(Observation(kind="error", content={"data": normalized}))
                cls._set_terminal(state, "EVIDENCE_UNAVAILABLE", normalized)
                trace.record("deterministic_terminal", status="EVIDENCE_UNAVAILABLE", source="observation_normalization")
                return True
        constraints_result = authoritative_evidence_from_constraints(state.goal.constraints)
        if constraints_result is not None:
            state.observations.append(Observation(kind="error", content={"data": constraints_result}))
            cls._set_terminal(state, "EVIDENCE_UNAVAILABLE", constraints_result)
            trace.record("deterministic_terminal", status="EVIDENCE_UNAVAILABLE", source="workflow_preflight")
            return True
        return False

    @classmethod
    def _guard_thermal_action(cls, state: AgentState, tool_name: str) -> None:
        if tool_name in THERMAL_OPERATIONAL_ACTIONS and cls._thermal_evidence_required_but_missing(state):
            raise GuardrailError(f"thermal_action_forbidden_without_evidence:{tool_name}")

    @staticmethod
    def _deterministic_terminal(result: ToolResult) -> str | None:
        status = result.data.get("status") or result.data.get("state") or result.data.get("evidence_status")
        if status in {"EVIDENCE_UNAVAILABLE", "INVALID_EVIDENCE", "COMPLETED_BUT_EMPTY", "NOT_DEMONSTRATED", "EMPTY_FEATURE_COLLECTION", "INVALID_SCHEMA", "WRONG_UNITS", "UNCOVERED_REQUIRED_INTERVAL"}:
            return "EVIDENCE_UNAVAILABLE"
        if status in {"NO_FEASIBLE_IMPROVEMENT", "KEEP_CURRENT_PLAN", "KEEP_CURRENT_PLAN_AND_RECHECK", "NO_ACTION_REQUIRED", "REJECTED_FIXED_COMMITMENT"}:
            return str(status)
        if status in {"PENDING_SUPERINTENDENT_APPROVAL", "AWAITING_APPROVAL", "APPROVAL_RECEIVED"}:
            return "AWAITING_APPROVAL"
        if status == "FINAL_VERIFICATION_FAILED":
            return "FINAL_VERIFICATION_FAILED"
        if status == "APPROVED":
            return "APPROVED"
        if status == "AI_ANALYSIS_UNAVAILABLE":
            return "AI_ANALYSIS_UNAVAILABLE"
        return None

    @staticmethod
    def _finish_reason(state: AgentState, message: str | None) -> str | None:
        """Return a terminal only when deterministic state proves one exists."""
        if state.operational_state in TERMINAL_STATES:
            return state.operational_state
        statuses = [
            observation.content.get("data", {}).get("status")
            for observation in state.observations
            if observation.kind == "tool_result"
        ]
        safe_terminal = {
            "NO_ACTION_REQUIRED",
            "EVIDENCE_UNAVAILABLE",
            "COMPLETED_BUT_EMPTY",
            "NOT_DEMONSTRATED",
            "NO_FEASIBLE_IMPROVEMENT",
            "KEEP_CURRENT_PLAN",
            "KEEP_CURRENT_PLAN_AND_RECHECK",
            "REJECTED_FIXED_COMMITMENT",
        }
        if "VERIFIED" not in statuses and any(status in {"FEASIBLE_ALTERNATIVES", "CANDIDATE_READY", "THERMAL_OVERLAP_READY"} for status in statuses):
            return "ERROR_SAFE"
        if any(status in safe_terminal for status in statuses):
            return str(next(status for status in statuses if status in safe_terminal))
        inspected = [
            observation.content.get("data", {})
            for observation in state.observations
            if observation.kind == "tool_result" and isinstance(observation.content.get("data", {}), dict)
        ]
        if any(data.get("source") == "SHIFT_PLAN" and int(data.get("outdoor_tasks", 1)) == 0 for data in inspected):
            return "NO_ACTION_REQUIRED"
        return None

    def resolve_approval(self, state: AgentState, index: int, approved: bool, *, final_verification: Callable[[ActionProposal], bool] | None = None) -> AgentState:
        """Resolve approval only after context checks and final verification."""
        if index < 0 or index >= len(state.approvals):
            raise IndexError("approval_index_out_of_range")
        request = state.approvals[index]
        if request.status != "pending":
            raise ValueError("approval_already_resolved")
        if not approved:
            request.status = "rejected"
            request.decided_at = utc_now()
            state.termination_reason = "rejected_recommendation"
            state.operational_state = "REJECTED"
            return state
        latest = next((observation.content.get("data", {}) for observation in reversed(state.observations) if observation.kind == "tool_result" and observation.content.get("data", {}).get("status") == "VERIFIED"), None)
        context_ok = isinstance(latest, dict) and latest.get("valid") is True and all((request.candidate_hash, request.evidence_hash, request.policy_version, request.task_state_hash, request.verification_hash)) and request.candidate_hash == latest.get("schedule_hash") and request.evidence_hash == latest.get("evidence_hash") and request.policy_version == latest.get("policy_version") and request.task_state_hash == latest.get("task_state_hash") and request.verification_hash == request_hash("local:verification", latest)
        if final_verification is not None:
            final_ok = bool(final_verification(request.proposal))
        elif "verify_schedule" in self.registry.names():
            try:
                final_result = self.registry.get("verify_schedule").handler(request.proposal.parameters)
                final_ok = final_result.ok and final_result.data.get("status") == "VERIFIED" and final_result.data.get("valid") is True
            except Exception:
                final_ok = False
        else:
            final_ok = False
        if not context_ok or not final_ok:
            request.status = "rejected"
            request.decided_at = utc_now()
            state.termination_reason = "FINAL_VERIFICATION_FAILED"
            state.operational_state = "FINAL_VERIFICATION_FAILED"
            state.authoritative_result = {"status": "FINAL_VERIFICATION_FAILED", "valid": False, "approval_boundary": "human approval alone is insufficient"}
            return state
        request.status = "approved"
        request.decided_at = utc_now()
        state.termination_reason = "approved_recommendation"
        state.operational_state = "APPROVED"
        return state
