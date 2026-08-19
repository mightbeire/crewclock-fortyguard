from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .guardrails import Budget, GuardrailError, SafetyPolicy
from .models import AgentState, AgentTrace, ApprovalRequest, Observation, ToolResult
from .providers import LLMProvider


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], ToolResult]
    requires_approval: bool = False


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
                decision = self.provider.next_decision(state)
                trace.record("provider_decision", kind=decision.kind, tool_name=decision.tool_name, message=decision.message)
                if decision.kind == "finish":
                    state.terminated = True
                    state.termination_reason = decision.message or "provider_finished"
                    break
                if decision.kind == "proposal" and decision.proposal is not None:
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
                cost = self.budget.reserve_tool(name)
                spec = self.registry.get(name)
                trace.record("tool_call_started", tool_name=name, arguments=decision.arguments, reserved_credits=cost)
                result = spec.handler(decision.arguments)
                called_tools.append(name)
                state.observations.append(Observation(kind="tool_result" if result.ok else "error", content=result.to_dict()))
                self.provider.observe(result, state)
                trace.record("tool_call_finished", tool_name=name, ok=result.ok, provenance=result.provenance.source, error=result.error)
            except GuardrailError as exc:
                state.terminated = True
                state.termination_reason = str(exc)
                state.observations.append(Observation(kind="error", content={"error": str(exc)}))
                trace.record("guardrail_stop", reason=str(exc))
        trace.record("goal_finished", reason=state.termination_reason, iterations=state.iteration, tool_calls=self.budget.tool_calls, reserved_credits=self.budget.api_credits_reserved)
        return state, trace
