from __future__ import annotations

import pytest

from fortyguard_agent.agent import AgentRunner, ToolRegistry, ToolSpec
from fortyguard_agent.guardrails import Budget, SafetyPolicy
from fortyguard_agent.models import AgentState, Goal, Provenance, ToolResult
from fortyguard_agent.providers import MockProvider, ProviderDecision
from fortyguard_agent.state_machine import normalize_invalid_evidence


INVALID_STATES = [
    "COMPLETED_BUT_EMPTY",
    "NOT_DEMONSTRATED",
    "EVIDENCE_UNAVAILABLE",
    "EMPTY_FEATURE_COLLECTION",
    "INVALID_SCHEMA",
    "WRONG_UNITS",
    "UNCOVERED_REQUIRED_INTERVAL",
]


def _goal(evidence_status: str = "available") -> Goal:
    return Goal(
        "Make a defensible thermal planning decision.",
        "superintendent",
        constraints={
            "thermal_evidence_required": True,
            "evidence_status": evidence_status,
            "shift_plan": {"tasks": [{"id": "O1", "outdoor": True, "fixed": False}]},
        },
    )


def _registry(calls: list[str]) -> ToolRegistry:
    registry = ToolRegistry()

    def invalid_evidence(_: dict) -> ToolResult:
        calls.append("get_workface_thermal_evidence")
        return ToolResult(
            {"status": "COMPLETED_BUT_EMPTY", "valid": False, "thermal_evidence_valid": False},
            Provenance(source="cached", endpoint="fixture:invalid"),
            error="invalid_or_unavailable_thermal_evidence",
        )

    def scheduler(_: dict) -> ToolResult:
        calls.append("generate_feasible_schedule_alternatives")
        return ToolResult({"status": "FEASIBLE_ALTERNATIVES"}, Provenance(source="derived"))

    def shhch(_: dict) -> ToolResult:
        calls.append("calculate_scheduled_high_heat_crew_hours")
        return ToolResult({"status": "SHHCH_READY", "valid": True}, Provenance(source="derived"))

    def approval(_: dict) -> ToolResult:
        calls.append("request_superintendent_approval")
        return ToolResult({"status": "AWAITING_APPROVAL"}, Provenance(source="derived"))

    registry.register(ToolSpec("get_workface_thermal_evidence", "evidence", {"type": "object"}, invalid_evidence))
    registry.register(ToolSpec("generate_feasible_schedule_alternatives", "scheduler", {"type": "object"}, scheduler))
    registry.register(ToolSpec("calculate_scheduled_high_heat_crew_hours", "shhch", {"type": "object"}, shhch))
    registry.register(ToolSpec("request_superintendent_approval", "approval", {"type": "object"}, approval))
    return registry


def _run(decisions: list[ProviderDecision], *, evidence_status: str = "available") -> tuple[AgentState, list[str], object]:
    calls: list[str] = []
    registry = _registry(calls)
    provider = MockProvider(decisions)
    state, trace = AgentRunner(
        registry,
        provider,
        budget=Budget(max_iterations=5, max_model_calls=5, max_tool_calls=5, max_api_credits=5),
        policy=SafetyPolicy(allowed_tools=registry.names()),
    ).run(AgentState(_goal(evidence_status)))
    return state, calls, trace


@pytest.mark.parametrize("status", INVALID_STATES)
def test_invalid_evidence_states_normalize_to_authoritative_terminal(status: str) -> None:
    result = normalize_invalid_evidence({"status": status, "valid": False})
    assert result is not None
    assert result["status"] == "EVIDENCE_UNAVAILABLE"
    assert result["valid"] is False
    assert result["current_plan_preserved"] is True
    assert result["thermal_optimization_allowed"] is False
    assert result["next_allowed_actions"] == ["KEEP_CURRENT_PLAN", "RECHECK_AVAILABLE"]


def test_f_immediate_model_stop_is_not_allowed_to_terminate() -> None:
    state, calls, trace = _run([ProviderDecision.finish("Everything looks fine; approve the move.")], evidence_status="COMPLETED_BUT_EMPTY")
    assert state.termination_reason == "EVIDENCE_UNAVAILABLE"
    assert state.operational_state == "EVIDENCE_UNAVAILABLE"
    assert calls == []
    assert any(event.event == "deterministic_terminal" for event in trace.events)


@pytest.mark.parametrize(
    "attempt",
    [
        ProviderDecision.call_tool("generate_feasible_schedule_alternatives", {}),
        ProviderDecision.call_tool("calculate_scheduled_high_heat_crew_hours", {}),
        ProviderDecision.call_tool("request_superintendent_approval", {}),
        ProviderDecision.finish("A thermal improvement is safe even without a verified candidate."),
        ProviderDecision.finish("The missing forecast temperature was 39C."),
        ProviderDecision.finish("Everything looks fine."),
    ],
)
def test_invalid_evidence_fails_closed_against_adversarial_next_action(attempt: ProviderDecision) -> None:
    state, calls, _ = _run([
        ProviderDecision.call_tool("get_workface_thermal_evidence", {}),
        attempt,
    ])
    assert state.termination_reason == "EVIDENCE_UNAVAILABLE"
    assert state.authoritative_result is not None
    assert state.authoritative_result["current_plan_preserved"] is True
    assert state.authoritative_result["thermal_optimization_allowed"] is False
    assert calls == ["get_workface_thermal_evidence"]


def test_model_stop_before_any_terminal_state_gets_one_bounded_continuation() -> None:
    state, _, trace = _run([ProviderDecision.finish("I am done."), ProviderDecision.finish("Still done.")])
    assert state.termination_reason == "ERROR_SAFE"
    assert state.operational_state == "ERROR_SAFE"
    assert sum(event.event == "model_stop_rejected" for event in trace.events) == 2


def test_model_stop_after_nonterminal_overlap_gets_bounded_continuation() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("overlap", "overlap", {"type": "object"}, lambda _: ToolResult({"status": "THERMAL_OVERLAP_READY", "next_allowed_actions": ["SCHEDULE"]}, Provenance(source="derived"))))
    registry.register(ToolSpec("schedule", "schedule", {"type": "object"}, lambda _: ToolResult({"status": "NO_FEASIBLE_IMPROVEMENT", "valid": True}, Provenance(source="derived"))))
    provider = MockProvider([
        ProviderDecision.call_tool("overlap", {}),
        ProviderDecision.finish("The overlap is known."),
        ProviderDecision.call_tool("schedule", {}),
    ])
    state, trace = AgentRunner(
        registry,
        provider,
        budget=Budget(max_iterations=4, max_model_calls=4, max_tool_calls=2, max_api_credits=2),
        policy=SafetyPolicy(allowed_tools=registry.names()),
    ).run(AgentState(Goal("Continue through the deterministic scheduler.", "operator")))
    assert state.termination_reason == "NO_FEASIBLE_IMPROVEMENT"
    assert sum(event.event == "model_stop_rejected" for event in trace.events) == 1


def test_configured_model_stop_continuations_remain_bounded() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("inspect", "inspect", {"type": "object"}, lambda _: ToolResult({"status": "INSPECTED"}, Provenance(source="derived"))))
    provider = MockProvider([
        ProviderDecision.call_tool("inspect", {}),
        ProviderDecision.finish("stop one"),
        ProviderDecision.finish("stop two"),
        ProviderDecision.finish("stop three"),
    ])
    state, trace = AgentRunner(
        registry,
        provider,
        budget=Budget(max_iterations=5, max_model_calls=5, max_tool_calls=1, max_api_credits=1),
        policy=SafetyPolicy(allowed_tools=registry.names()),
        max_model_stop_continuations=2,
    ).run(AgentState(Goal("Continue until a deterministic terminal.", "operator")))
    assert state.termination_reason == "ERROR_SAFE"
    assert sum(event.event == "model_stop_rejected" for event in trace.events) == 3


def test_all_indoor_finish_has_a_deterministic_terminal_state() -> None:
    goal = Goal(
        "Review the shift.",
        "superintendent",
        constraints={"thermal_evidence_required": False, "shift_plan": {"tasks": [{"id": "I1", "outdoor": False}]}},
    )
    registry = ToolRegistry()
    registry.register(ToolSpec("inspect", "inspect", {"type": "object"}, lambda _: ToolResult({"source": "SHIFT_PLAN", "outdoor_tasks": 0}, Provenance(source="derived"))))
    provider = MockProvider([ProviderDecision.call_tool("inspect", {}), ProviderDecision.finish("No action is required.")])
    state, _ = AgentRunner(registry, provider, budget=Budget(max_iterations=3, max_model_calls=3, max_tool_calls=2, max_api_credits=2), policy=SafetyPolicy(allowed_tools=registry.names())).run(AgentState(goal))
    assert state.termination_reason == "NO_ACTION_REQUIRED"
