from datetime import datetime, timedelta, timezone

from fortyguard_agent.policy import BreakRule, EmployerPolicy
from fortyguard_agent.scheduler import generate_feasible_schedule_alternatives, verify_schedule
from fortyguard_agent.toolkit import FortyGuardToolkit


UTC = timezone.utc


def _policy() -> EmployerPolicy:
    return EmployerPolicy("p", "v1", "demo", "DEMO_POLICY", "2026-01-01", "modeled-temperature", 32, 32, "celsius", (BreakRule("high", 90, 30, "DEMO_POLICY"),))


def _task(**overrides):
    row = {"id": "A", "duration": 60, "crew_id": "crew", "qualification": "qualified", "deadline": "2026-08-21T16:00:00+00:00", "baseline_start": "2026-08-21T06:00:00+00:00", "dependencies": [], "fixed": False, "outdoor": False}
    row.update(overrides)
    return row


def _kwargs():
    start = datetime(2026, 8, 21, 6, tzinfo=UTC)
    return {"shift_start": start, "shift_end": start + timedelta(hours=10), "trigger_start": start + timedelta(hours=5), "trigger_end": start + timedelta(hours=9)}


def test_runtime_verifier_rejects_empty_and_malformed_schedules():
    assert not verify_schedule([_task()], {}, {"crew": {"qualifications": ["qualified"]}}, _policy(), **_kwargs()).passed
    assert not verify_schedule([_task()], {"A": "not-a-time"}, {"crew": {"qualifications": ["qualified"]}}, _policy(), **_kwargs()).passed


def test_runtime_tool_verifier_is_not_a_truthy_schedule_stub():
    result = FortyGuardToolkit.verify_schedule({"schedule": {}, "tasks": [], "crews": {}, "policy": {}, **{key: value.isoformat() for key, value in _kwargs().items()}})
    assert result.data["status"] == "VERIFICATION_FAILED"
    assert result.data["valid"] is False


def test_optimizer_returns_real_candidates_and_keeps_fixed_task():
    tasks = [_task(id="F", fixed=True, baseline_start="2026-08-21T06:00:00+00:00"), _task(id="M", baseline_start="2026-08-21T07:00:00+00:00", deadline="2026-08-21T10:00:00+00:00")]
    tasks[1]["dependencies"] = ["F"]
    baseline = {"F": "2026-08-21T06:00:00+00:00", "M": "2026-08-21T07:00:00+00:00"}
    candidates = generate_feasible_schedule_alternatives(tasks, {"crew": {"qualifications": ["qualified"]}}, _policy(), baseline=baseline, **_kwargs())
    assert candidates
    assert all(candidate["F"] == baseline["F"] for candidate in candidates)


def test_break_is_not_a_detached_boolean():
    task = _task(duration=120, outdoor=True, baseline_start="2026-08-21T11:00:00+00:00")
    result = verify_schedule([task], {"A": task["baseline_start"]}, {"crew": {"qualifications": ["qualified"]}}, _policy(), **_kwargs())
    assert not result.passed
    assert any(check.name == "policy_breaks" and not check.passed for check in result.checks)
