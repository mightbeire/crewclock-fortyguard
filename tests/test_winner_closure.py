from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import pytest

from fortyguard_agent import production_service as service
from fortyguard_agent.evidence_windows import InvestigationPlanError, assemble_evidence_bundle, investigation_facts, schedule_windows, validate_investigation_plan
from fortyguard_agent.site_geometry import SiteGeometryError, acquisition_aoi_for_workfaces, build_site_geometry, validate_workfaces


def _task(task_id: str, workface: str, start: str, *, fixed: bool = False, indoor: bool = False) -> dict:
    return {"id": task_id, "zoneId": workface, "originalStart": start, "durationMinutes": 60, "fixed": fixed, "environment": "shaded-support" if indoor else "outdoor-moderate"}


def test_arbitrary_shift_segments_into_two_hours_with_partial_final_window() -> None:
    assert schedule_windows("06:15", "11:00") == [
        {"id": "06:15-08:15", "start": "06:15", "end": "08:15"},
        {"id": "08:15-10:15", "start": "08:15", "end": "10:15"},
        {"id": "10:15-11:00", "start": "10:15", "end": "11:00"},
    ]


def test_model_plan_changes_with_workface_and_schedule_facts() -> None:
    windows = schedule_windows("06:00", "12:00")
    one = investigation_facts({"tasks": [_task("A", "north", "06:00", fixed=True)]}, windows)
    many = investigation_facts({"tasks": [_task("A", "north", "06:00", fixed=True), _task("B", "south", "10:00", fixed=True)]}, windows)
    assert validate_investigation_plan({"decision": "INVESTIGATE", "workface_ids": ["north"], "window_ids": ["06:00-08:00"], "reason": "fixed task"}, one)["workface_ids"] == ["north"]
    accepted = validate_investigation_plan({"decision": "INVESTIGATE", "workface_ids": ["north", "south"], "window_ids": ["06:00-08:00", "10:00-12:00"], "reason": "two fixed tasks"}, many)
    assert accepted["workface_ids"] == ["north", "south"]
    assert accepted["window_ids"] != ["06:00-08:00"]


def test_invalid_model_plan_is_rejected_not_silently_replaced() -> None:
    facts = investigation_facts({"tasks": [_task("A", "north", "06:00")]}, schedule_windows("06:00", "10:00"))
    with pytest.raises(InvestigationPlanError, match="workface_not_relevant"):
        validate_investigation_plan({"decision": "INVESTIGATE", "workface_ids": ["phoenix-sample"], "window_ids": ["06:00-08:00"], "reason": "invalid"}, facts)
    with pytest.raises(InvestigationPlanError, match="requires_investigation"):
        validate_investigation_plan({"decision": "NO_THERMAL_INVESTIGATION", "workface_ids": [], "window_ids": [], "reason": "skip"}, facts)


def test_segmented_bundle_preserves_distinct_window_identities() -> None:
    base = {"status": "LIVE_ACQUIRED", "granularity": 100, "exceedanceWindows": [{"start": "06:00", "end": "08:00"}], "activityId": "activity-a", "resultHash": "hash-a"}
    later = {**base, "activityId": "activity-b", "resultHash": "hash-b", "exceedanceWindows": [{"start": "08:00", "end": "10:00"}]}
    plan = {"decision": "INVESTIGATE", "workface_ids": ["north"], "window_ids": ["06:00-08:00", "08:00-10:00"]}
    bundle = assemble_evidence_bundle([base, later], plan=plan, aoi_hash="aoi")
    assert [(row["start"], row["end"]) for row in bundle["exceedanceWindows"]] == [("06:00", "08:00"), ("08:00", "10:00")]
    assert bundle["activityIds"] == ["activity-a", "activity-b"]
    assert bundle["evidenceBundleHash"]


def test_workface_must_be_inside_and_bound_to_aoi() -> None:
    site = build_site_geometry(35.0, -80.0, 200, 200).to_dict()
    accepted = validate_workfaces(site["workfaces"], site["aoi"])
    assert all(face["aoi_hash"] == accepted[0]["aoi_hash"] for face in accepted)
    outside = deepcopy(site["workfaces"])
    outside[0]["polygon"][0][0] -= 1
    with pytest.raises(SiteGeometryError, match="outside_project_aoi"):
        validate_workfaces(outside, site["aoi"])



def test_investigation_plan_cannot_omit_relevant_outdoor_workface() -> None:
    windows = schedule_windows("06:00", "10:00")
    facts = investigation_facts({"tasks": [_task("A", "north", "06:00"), _task("B", "south", "08:00")]}, windows)
    with pytest.raises(InvestigationPlanError, match="workface_coverage_incomplete"):
        validate_investigation_plan({"decision": "INVESTIGATE", "workface_ids": ["north"], "window_ids": ["06:00-08:00"], "reason": "partial"}, facts)
    accepted = validate_investigation_plan({"decision": "INVESTIGATE", "workface_ids": ["north", "south"], "window_ids": ["06:00-08:00"], "reason": "bounded initial window"}, facts)
    assert accepted["workface_ids"] == ["north", "south"]


def test_new_site_horizon_guard_accepts_historical_and_near_future_without_mutation() -> None:
    request = {
        "date": "2025-07-15", "timezone": "America/New_York", "start": "06:00", "end": "10:00",
        "tasks": [_task("A", "north", "06:00")],
    }
    original = deepcopy(request)
    service.validate_new_site_review_window(request, reference_utc=datetime(2026, 8, 27, 8, 0, tzinfo=timezone.utc))
    assert request == original

    near = {**request, "date": "2026-08-27"}
    service.validate_new_site_review_window(near, reference_utc=datetime(2026, 8, 27, 8, 0, tzinfo=timezone.utc))


def test_new_site_horizon_guard_rejects_unsupported_future_before_review_without_mutation() -> None:
    request = {
        "date": "2026-08-28", "timezone": "America/New_York", "start": "06:00", "end": "10:00",
        "tasks": [_task("A", "north", "06:00")],
    }
    original = deepcopy(request)
    with pytest.raises(SiteGeometryError, match="selected_shift_outside_fortyguard_12h_forecast_horizon"):
        service.validate_new_site_review_window(request, reference_utc=datetime(2026, 8, 27, 8, 0, tzinfo=timezone.utc))
    assert request == original


def test_selected_workfaces_build_exact_provider_geometry_inside_project_aoi() -> None:
    site = build_site_geometry(35.0, -80.0, 200, 200).to_dict()
    selected = [site["workfaces"][0], site["workfaces"][2]]
    provider_aoi = acquisition_aoi_for_workfaces(selected, site["aoi"])
    assert [feature["properties"]["workface_id"] for feature in provider_aoi["features"]] == [selected[0]["id"], selected[1]["id"]]
    assert provider_aoi != site["aoi"]


def test_model_safety_language_is_rejected_then_corrected(monkeypatch) -> None:
    session = service.Session("agent-safety", "new-site", {})
    run = {"status": "recommended", "baselineValid": True, "beforeCrewHours": 10, "afterCrewHours": 4, "recommendation": {"A": "06:00"}, "original": {"A": "10:00"}, "recommendationVerification": {"passed": True}}
    actions = iter([
        {"action": "PRESENT_RECOMMENDATION", "explanation": "The plan cuts modeled overlap while meeting safety constraints.", "request_superintendent_decision": True},
        {"action": "PRESENT_RECOMMENDATION", "explanation": "The plan reduces scheduled high-heat crew-hours from 10 to 4 while preserving all hard operational constraints.", "request_superintendent_decision": True},
    ])
    monkeypatch.setattr(service, "_bounded_model_action", lambda *args, **kwargs: next(actions))
    presentation = service.explain_structured_result(session, run)
    assert "safety" not in presentation["explanation"].lower()
    rejected = [event for event in session.events if event["status"] == "AGENT_DECISION_REJECTED"]
    assert rejected and rejected[0]["metadata"]["claim_violation"] is not None

def test_live_approval_reconstructs_live_evidence_branch(monkeypatch) -> None:
    captured: dict = {}
    run = {"status": "recommended", "thermalEvidence": {"classification": "LIVE_ACQUIRED_SEGMENTED"}, "workfaces": [], "recommendationId": "rec", "candidateHash": "candidate"}
    session = service.Session("live", "new-site", {"tasks": [], "crews": []}, status="AWAITING_APPROVAL", result=run)
    def fake_engine(payload: dict) -> dict:
        captured.update(payload)
        return {"decision": {"approved": True}}
    monkeypatch.setattr(service, "run_engine", fake_engine)
    result = service.approve_session(session, {"recommendationId": "rec", "candidateHash": "candidate"})
    assert result["approved"] is True
    assert captured["scenario"] == "live-acquired"
    assert captured["thermalEvidence"] is run["thermalEvidence"]


def test_stale_live_identity_still_fails_closed(monkeypatch) -> None:
    session = service.Session("live", "new-site", {}, status="AWAITING_APPROVAL", result={"status": "recommended", "thermalEvidence": {"classification": "LIVE_ACQUIRED_SEGMENTED"}, "workfaces": []})
    monkeypatch.setattr(service, "run_engine", lambda payload: {"decision": {"approved": False}})
    result = service.approve_session(session, {"recommendationId": "stale", "candidateHash": "stale"})
    assert result == {"approved": False, "status": "FINAL_VERIFICATION_FAILED"}


def test_model_evidence_sufficiency_has_validated_causal_actions(monkeypatch) -> None:
    session = service.Session("agent", "new-site", {})
    facts = {"relevant_outdoor_tasks": [{"workface_id": "north", "window_ids": ["06:00-08:00", "08:00-10:00"]}]}
    plan = {"workface_ids": ["north"], "window_ids": ["06:00-08:00"]}
    monkeypatch.setattr(service, "_bounded_model_action", lambda *args, **kwargs: {"decision": "REQUEST_MISSING", "window_ids": ["08:00-10:00"], "reason": "coverage gap"})
    action = service.decide_evidence_sufficiency(session, plan, facts, ["06:00-08:00"])
    assert action["decision"] == "REQUEST_MISSING"
    assert action["window_ids"] == ["08:00-10:00"]


def test_model_cannot_proceed_over_missing_evidence(monkeypatch) -> None:
    session = service.Session("agent", "new-site", {})
    facts = {"relevant_outdoor_tasks": [{"workface_id": "north", "window_ids": ["06:00-08:00", "08:00-10:00"]}]}
    plan = {"workface_ids": ["north"], "window_ids": ["06:00-08:00"]}
    monkeypatch.setattr(service, "_bounded_model_action", lambda *args, **kwargs: {"decision": "PROCEED", "window_ids": [], "reason": "invent complete"})
    with pytest.raises(RuntimeError, match="sufficiency_validation_failed"):
        service.decide_evidence_sufficiency(session, plan, facts, ["06:00-08:00"])


def test_model_explanation_must_match_deterministic_terminal(monkeypatch) -> None:
    session = service.Session("agent", "new-site", {})
    run = {"status": "recommended", "baselineValid": True, "beforeCrewHours": 10, "afterCrewHours": 4, "recommendation": {"A": "06:00"}, "original": {"A": "10:00"}, "recommendationVerification": {"passed": True}}
    monkeypatch.setattr(service, "_bounded_model_action", lambda *args, **kwargs: {"action": "PRESENT_RECOMMENDATION", "explanation": "Validated overlap fell from 10 to 4 crew-hours.", "request_superintendent_decision": True})
    presentation = service.explain_structured_result(session, run)
    assert presentation["request_superintendent_decision"] is True
    monkeypatch.setattr(service, "_bounded_model_action", lambda *args, **kwargs: {"action": "PRESENT_NO_CHANGE", "explanation": "wrong branch", "request_superintendent_decision": False})
    with pytest.raises(RuntimeError, match="presentation_validation_failed"):
        service.explain_structured_result(session, run)


def test_model_explanation_rejects_internal_field_language_then_corrects(monkeypatch) -> None:
    session = service.Session("agent", "new-site", {})
    run = {"status": "recommended", "baselineValid": True, "beforeCrewHours": 10, "afterCrewHours": 4, "recommendation": {"A": "06:00"}, "original": {"A": "10:00"}, "recommendationVerification": {"passed": True}}
    actions = iter([
        {"action": "PRESENT_RECOMMENDATION", "explanation": "Baseline valid true and verification_passed true.", "request_superintendent_decision": True},
        {"action": "PRESENT_RECOMMENDATION", "explanation": "One task was retimed, reducing scheduled high-heat crew-hours from 10 to 4.", "request_superintendent_decision": True},
    ])
    monkeypatch.setattr(service, "_bounded_model_action", lambda *args, **kwargs: next(actions))
    presentation = service.explain_structured_result(session, run)
    assert presentation["explanation"].startswith("One task")
    assert any(event["status"] == "AGENT_DECISION_REJECTED" for event in session.events)
