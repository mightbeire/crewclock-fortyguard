import json
from pathlib import Path

from fortyguard_agent.models import AgentState, AgentTrace, Goal
from fortyguard_agent.ui_events import trace_to_ui_events

APP = Path(__file__).resolve().parents[1] / "src" / "App.tsx"


def test_agent_trace_projects_to_safe_ui_events_without_reasoning_or_secrets() -> None:
    state = AgentState(Goal("Review the shift", "superintendent"), operational_state="AWAITING_APPROVAL")
    trace = AgentTrace(trace_id="trace-fixture")
    trace.record("goal_started", goal_id="goal-fixture", text="private model prompt must not be copied")
    trace.record("tool_call_started", tool_name="verify_schedule", arguments={"api_key": "fg_live_secret"})
    trace.record("tool_call_finished", tool_name="verify_schedule", ok=True, status="VERIFIED", provenance="derived", error="")
    trace.record("action_proposed", action_type="schedule_change", confidence=0.9)
    trace.record("provider_telemetry", provider_used="PRIMARY_PROVIDER", fallback_used=False, model_calls=2, tool_calls=1, api_key="fg_live_secret")
    events = trace_to_ui_events(trace, state, run_id="run-fixture")
    payload = json.dumps(events)
    assert [event["status"] for event in events] == ["SHIFT_INSPECTION_STARTED", "VERIFICATION_STARTED", "VERIFICATION_PASSED", "AWAITING_APPROVAL", "RUNTIME_TELEMETRY"]
    assert "fg_live_secret" not in payload
    assert "private model prompt" not in payload
    telemetry = events[-1]
    assert telemetry["metadata"]["provider_used"] == "PRIMARY_PROVIDER"
    assert "api_key" not in telemetry["metadata"]
    assert all(set(event) >= {"event_id", "run_id", "timestamp", "stage", "status", "summary", "source", "provider", "metadata"} for event in events)


def test_polling_effect_has_stable_session_identity_dependencies() -> None:
    source = APP.read_text(encoding="utf-8")
    assert "[phase, session.runId, session.status]" in source
    assert "[phase, session])" not in source
    assert "window.setInterval(() => { void poll() }, 250)" in source


def test_mobile_and_approval_failure_copy_are_truthful() -> None:
    source = APP.read_text(encoding="utf-8")
    assert "Indoor / support work contributes 0 modeled high-heat crew-hours" in source
    assert "Plan wasn’t applied because final verification failed." in source
    assert "Current shift remains unchanged." in source
    assert "REAL FORTYGUARD HISTORICAL VALIDATION" in source
    assert "1 task retimed" in source
    assert "crew.qualifications[0]" in source
    assert "qualification: isSample && prior?.crewId === crew.id ? prior.qualification : 'general'" not in source
    assert "LIVE_ACQUIRED_SEGMENTED" in source
    assert "Live FortyGuard evidence acquired in schedule-aligned windows" in source
    assert "alternativesTested = run.stats.candidatesConsidered > 0" in source
