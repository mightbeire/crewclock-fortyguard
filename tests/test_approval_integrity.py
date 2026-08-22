from __future__ import annotations

from copy import deepcopy
import pytest

from fortyguard_agent.agent import AgentRunner
from fortyguard_agent.guardrails import Budget, SafetyPolicy
from fortyguard_agent.integrity import candidate_hash_from_verification_arguments
from fortyguard_agent.models import ActionProposal, AgentState, Goal
from fortyguard_agent.providers import MockProvider, ProviderDecision
from fortyguard_agent.registry import build_tool_registry
from fortyguard_agent.toolkit import FortyGuardToolkit


def verification_arguments() -> dict:
    task = {
        "id": "A", "duration": 60, "crew_id": "ground", "qualification": "competent-person",
        "deadline": "2026-08-21T16:00:00+00:00", "baseline_start": "2026-08-21T06:00:00+00:00",
        "dependencies": [], "fixed": False, "outdoor": True, "workface": "north",
    }
    return {
        "tasks": [task], "schedule": {"A": "2026-08-21T06:00:00+00:00"},
        "source_schedule": {"A": "2026-08-21T06:00:00+00:00"},
        "crews": {"ground": {"qualifications": ["competent-person"]}},
        "policy": {"policy_id": "p1", "version": "1", "name": "policy", "source": "DEMO_POLICY", "break_rules": []},
        "evidence": {"bundle": "e1"}, "break_reservations": [],
        "shift_start": "2026-08-21T06:00:00+00:00", "shift_end": "2026-08-21T16:00:00+00:00",
        "trigger_start": "2026-08-21T11:00:00+00:00", "trigger_end": "2026-08-21T15:00:00+00:00",
    }


def pending_state(parameters: dict | None = None) -> AgentState:
    toolkit = FortyGuardToolkit()
    registry = build_tool_registry(toolkit)
    parameters = deepcopy(parameters or verification_arguments())
    provider = MockProvider([
        ProviderDecision.call_tool("verify_schedule", parameters),
        ProviderDecision.propose(ActionProposal("schedule_change", "Use the verified candidate.", parameters, 0.9)),
    ])
    runner = AgentRunner(registry, provider, budget=Budget(max_iterations=3, max_model_calls=3, max_tool_calls=2), policy=SafetyPolicy(allowed_tools=registry.names()))
    state, _ = runner.run(AgentState(Goal("verify a schedule", "superintendent")))
    assert state.termination_reason == "awaiting_human_approval"
    assert len(state.approvals) == 1
    return state


def approve(state: AgentState, *, recommendation_id: str | None = None, candidate_hash: str | None = None) -> AgentState:
    request = state.approvals[0]
    return AgentRunner(build_tool_registry(FortyGuardToolkit()), MockProvider([])).resolve_approval(
        state, 0, True,
        recommendation_id=request.recommendation_id if recommendation_id is None else recommendation_id,
        candidate_hash=request.candidate_hash if candidate_hash is None else candidate_hash,
    )


def test_verify_a_approve_a_unchanged_passes() -> None:
    state = approve(pending_state())
    assert state.operational_state == "APPROVED"


@pytest.mark.parametrize("mutation", [
    lambda args: args.update(schedule={"A": "2026-08-21T07:00:00+00:00"}),
    lambda args: args["tasks"][0].update(crew_id="concrete"),
    lambda args: args.update(break_reservations=[{"crew_id": "ground", "start": "2026-08-21T11:00:00+00:00", "end": "2026-08-21T11:30:00+00:00"}]),
    lambda args: args["tasks"][0].update(workface="south"),
    lambda args: args.update(source_schedule={"A": "2026-08-21T06:30:00+00:00"}),
    lambda args: args["policy"].update(break_rules=[{"trigger_name": "heat", "after_continuous_minutes": 90, "duration_minutes": 30}]),
])
def test_mutated_candidate_context_is_rejected(mutation) -> None:
    state = pending_state()
    mutation(state.approvals[0].proposal.parameters)
    state = approve(state)
    assert state.operational_state == "FINAL_VERIFICATION_FAILED"


def test_evidence_hash_change_is_rejected() -> None:
    state = pending_state()
    state.approvals[0].proposal.parameters["evidence"] = {"bundle": "changed"}
    assert approve(state).operational_state == "FINAL_VERIFICATION_FAILED"


@pytest.mark.parametrize("kwargs", [
    {"recommendation_id": "forged"},
    {"candidate_hash": "omitted"},
    {"recommendation_id": "wrong", "candidate_hash": "wrong"},
])
def test_missing_or_forged_approval_identity_is_rejected(kwargs) -> None:
    state = pending_state()
    request = state.approvals[0]
    assert approve(state, recommendation_id=kwargs.get("recommendation_id", request.recommendation_id), candidate_hash=kwargs.get("candidate_hash", None if "candidate_hash" in kwargs else request.candidate_hash)).operational_state == "FINAL_VERIFICATION_FAILED"


def test_stale_verification_artifact_is_rejected() -> None:
    state = pending_state()
    state.approvals[0].verification_hash = "stale"
    assert approve(state).operational_state == "FINAL_VERIFICATION_FAILED"


def test_replacing_proposal_and_all_visible_identity_fields_is_rejected() -> None:
    state = pending_state()
    request = state.approvals[0]
    replacement = deepcopy(request.proposal.parameters)
    replacement["schedule"] = {"A": "2026-08-21T07:00:00+00:00"}
    request.proposal.parameters = replacement
    for field in ("recommendation_id", "candidate_hash", "source_schedule_hash", "evidence_hash", "policy_hash", "project_state_hash", "task_state_hash", "verification_hash", "artifact_version"):
        setattr(request, field, "forged")
    assert approve(state, recommendation_id="forged", candidate_hash="forged").operational_state == "FINAL_VERIFICATION_FAILED"


def test_forged_recommendation_artifact_id_is_rejected() -> None:
    state = pending_state()
    for observation in state.observations:
        if observation.kind == "tool_result" and observation.content.get("data", {}).get("status") == "VERIFIED":
            observation.content["data"]["recommendation_id"] = "forged-artifact-id"
    assert approve(state).operational_state == "FINAL_VERIFICATION_FAILED"


def test_logically_equivalent_schedule_serialization_has_same_hash() -> None:
    first = verification_arguments()
    second = {"evidence": {"bundle": "e1"}, "policy": {"break_rules": [], "name": "policy", "version": "1", "source": "DEMO_POLICY", "policy_id": "p1"}, "crews": {"ground": {"qualifications": ["competent-person"]}}, "source_schedule": {"A": "2026-08-21T06:00:00+00:00"}, "schedule": {"A": "2026-08-21T06:00:00+00:00"}, "tasks": [{"workface": "north", "outdoor": True, "fixed": False, "dependencies": [], "baseline_start": "2026-08-21T06:00:00+00:00", "deadline": "2026-08-21T16:00:00+00:00", "qualification": "competent-person", "crew_id": "ground", "duration": 60, "id": "A"}]}
    assert candidate_hash_from_verification_arguments(first) == candidate_hash_from_verification_arguments(second)


def test_llm_candidate_substitution_is_rejected_before_approval() -> None:
    args = verification_arguments()
    replacement = deepcopy(args)
    replacement["schedule"] = {"A": "2026-08-21T07:00:00+00:00"}
    toolkit = FortyGuardToolkit()
    registry = build_tool_registry(toolkit)
    state, _ = AgentRunner(registry, MockProvider([
        ProviderDecision.call_tool("verify_schedule", args),
        ProviderDecision.propose(ActionProposal("schedule_change", "Substitute candidate.", replacement, 0.9)),
    ]), budget=Budget(max_iterations=3, max_model_calls=3, max_tool_calls=2), policy=SafetyPolicy(allowed_tools=registry.names())).run(AgentState(Goal("verify", "superintendent")))
    assert state.termination_reason == "FINAL_VERIFICATION_FAILED"
    assert state.approvals == []


def malformed_arguments(task) -> dict:
    args = verification_arguments()
    args["tasks"] = task
    args["schedule"] = {"A": "2026-08-21T06:00:00+00:00"} if isinstance(task, list) and task else {}
    return args


@pytest.mark.parametrize("task", [
    [],
    [None],
    ["not-a-task"],
    [{"duration": 60, "crew_id": "ground", "qualification": "competent-person", "deadline": "2026-08-21T16:00:00+00:00"}],
    [{"id": "A", "duration": 60, "crew_id": "ground", "qualification": "competent-person", "deadline": "not-time"}],
    [{"id": "A", "duration": 60, "crew_id": "unknown", "qualification": "competent-person", "deadline": "2026-08-21T16:00:00+00:00"}],
    [{"id": "A", "duration": 60, "crew_id": "ground", "qualification": "competent-person", "deadline": "2026-08-21T16:00:00+00:00"}, {"id": "A", "duration": 30, "crew_id": "ground", "qualification": "competent-person", "deadline": "2026-08-21T16:00:00+00:00"}],
])
def test_malformed_schedule_is_structured_fail_closed(task) -> None:
    result = FortyGuardToolkit().verify_schedule(malformed_arguments(task))
    assert result.data["status"] == "VERIFICATION_FAILED"
    assert "INVALID_SCHEDULE_SCHEMA" in " ".join(str(check) for check in result.data.get("checks", [])) or result.data.get("error") == "canonical_verifier_inputs_required"


def test_break_duration_boundary_and_window() -> None:
    from fortyguard_agent.policy import BreakRule, EmployerPolicy
    from fortyguard_agent.scheduler import verify_schedule

    policy = EmployerPolicy("p", "1", "p", "DEMO_POLICY", "2026-01-01", "modeled-temperature", None, 32, "celsius", (BreakRule("heat", 90, 30, "DEMO_POLICY"),))
    task = lambda task_id, start, crew="ground": {"id": task_id, "duration": 90, "crew_id": crew, "qualification": "q", "deadline": "2026-08-21T16:00:00+00:00", "baseline_start": start, "dependencies": [], "fixed": False, "outdoor": True}
    crews = {"ground": {"qualifications": ["q"]}, "other": {"qualifications": ["q"]}}
    def check(gap: int, reservation=None):
        first = "2026-08-21T11:00:00+00:00"
        second_minutes = 12 * 60 + 30 + gap
        second = f"2026-08-21T{second_minutes // 60:02d}:{second_minutes % 60:02d}:00+00:00"
        tasks = [task("A", first), task("B", second)]
        return verify_schedule(tasks, {"A": first, "B": second}, crews, policy, shift_start="2026-08-21T06:00:00+00:00", shift_end="2026-08-21T16:00:00+00:00", trigger_start="2026-08-21T11:00:00+00:00", trigger_end="2026-08-21T15:00:00+00:00", break_reservations=reservation).passed
    assert check(1) is False
    assert check(29) is False
    assert check(30) is True
    assert check(45) is True
    assert check(30, [{"crew_id": "ground", "start": "2026-08-21T10:00:00+00:00", "end": "2026-08-21T10:30:00+00:00"}]) is False
    assert check(1, [{"crew_id": "other", "start": "2026-08-21T12:00:00+00:00", "end": "2026-08-21T12:30:00+00:00"}]) is False
    assert check(30, [{"crew_id": "ground", "start": "2026-08-21T12:00:00+00:00", "end": "2026-08-21T12:30:00+00:00"}]) is False
