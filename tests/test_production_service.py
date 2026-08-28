from __future__ import annotations

from fortyguard_agent import production_service as service
from fortyguard_agent.models import Provenance, ToolResult
from fortyguard_agent.site_geometry import build_site_geometry


def _run(status: str = "recommended", *, baseline_valid: bool = True, before_crew_hours: float | None = None) -> dict:
    recommendation = {"T1": "07:00"} if status == "recommended" else None
    return {
        "run": {
            "status": status,
            "recommendation": recommendation,
            "stats": {"candidatesConsidered": 2 if recommendation else 0, "feasibleCandidates": 1 if recommendation else 0, "rejectedCandidates": 1 if recommendation else 0},
            "recommendationVerification": {"passed": True} if recommendation else None,
            "baselineValid": baseline_valid,
            "beforeCrewHours": before_crew_hours,
            "message": "No change",
        }
    }


def test_positive_session_events_are_emitted_after_actual_steps(monkeypatch) -> None:
    session = service.Session("run-test", "synthetic-positive", {})
    monkeypatch.setattr(service, "orchestrate", lambda current, inspection: "INVESTIGATE")
    monkeypatch.setattr(service, "run_engine", lambda payload: _run())
    service.execute_session(session)
    statuses = [event["status"] for event in session.events]
    assert session.status == "AWAITING_APPROVAL"
    assert statuses == [
        "THERMAL_INVESTIGATION_REQUIRED", "THERMAL_EVIDENCE_REQUESTED", "THERMAL_EVIDENCE_READY",
        "OPTIMIZATION_STARTED", "CANDIDATES_GENERATED", "VERIFICATION_STARTED", "VERIFICATION_PASSED", "AWAITING_APPROVAL",
    ]


def test_unavailable_evidence_never_generates_or_verifies(monkeypatch) -> None:
    session = service.Session("run-unavailable", "evidence-unavailable", {})
    monkeypatch.setattr(service, "orchestrate", lambda current, inspection: "INVESTIGATE")
    monkeypatch.setattr(service, "run_engine", lambda payload: _run("missing-evidence"))
    service.execute_session(session)
    statuses = [event["status"] for event in session.events]
    assert session.status == "EVIDENCE_UNAVAILABLE"
    assert "OPTIMIZATION_STARTED" not in statuses
    assert "VERIFICATION_STARTED" not in statuses
    assert "CURRENT_PLAN_PRESERVED" in statuses


def test_all_indoor_skips_evidence_and_optimization(monkeypatch) -> None:
    session = service.Session("run-indoor", "all-indoor", {})
    monkeypatch.setattr(service, "orchestrate", lambda current, inspection: "NO_THERMAL_INVESTIGATION")
    monkeypatch.setattr(service, "run_engine", lambda payload: _run("no-improvement"))
    service.execute_session(session)
    statuses = [event["status"] for event in session.events]
    assert statuses[0] == "NO_THERMAL_INVESTIGATION"
    assert "THERMAL_EVIDENCE_REQUESTED" not in statuses
    assert "OPTIMIZATION_STARTED" not in statuses


def test_terminal_events_distinguish_zero_shhch_from_invalid_baseline(monkeypatch) -> None:
    zero = service.Session("run-zero", "synthetic-positive", {})
    monkeypatch.setattr(service, "orchestrate", lambda current, inspection: "INVESTIGATE")
    monkeypatch.setattr(service, "run_engine", lambda payload: ({"verification": {"passed": True, "passedFamilies": 6, "totalFamilies": 6, "families": []}} if payload.get("action") == "validate-baseline" else _run("no-improvement", before_crew_hours=0)))
    service.execute_session(zero)
    assert zero.status == "NO_FEASIBLE_IMPROVEMENT"
    assert zero.events[-1]["summary"] == "No thermal schedule change needed."
    assert "hard" not in zero.events[-1]["summary"].lower()

    invalid = service.Session("run-invalid", "synthetic-positive", {})
    monkeypatch.setattr(service, "run_engine", lambda payload: _run("no-feasible-correction", baseline_valid=False))
    service.execute_session(invalid)
    assert invalid.status == "NO_FEASIBLE_CORRECTION"
    assert invalid.events[-1]["summary"] == "A hard operational constraint requires attention."
    assert invalid.events[-1]["terminal_state"] == "NO_FEASIBLE_CORRECTION"


def test_unknown_evidence_scenario_fails_closed(monkeypatch) -> None:
    session = service.Session("run-unknown", "not-approved", {})
    service.execute_session(session)
    assert session.status == "AI_ANALYSIS_UNAVAILABLE"
    assert session.result is None


def test_registry_binds_canonical_manifest_hash() -> None:
    synthetic = service.EVIDENCE_REGISTRY["phoenix_synthetic_positive_v2"]
    registered = service.EVIDENCE_REGISTRY["phoenix_canonical_2025_07_15"]
    assert synthetic["classification"] == "SYNTHETIC_TEST"
    assert synthetic["content_hash"] == "1a64a8928d8e8ff25841300cdb3e37bc136cacc4bc4885b12ee849ebf751e413"
    assert registered["classification"] == "CANONICAL_FORTYGUARD"
    assert registered["content_hash"] == "7f7af007a3a4020c07b16f8de63bb01425a53d70affb966d03e6467f37d7692a"


def test_new_site_submits_one_request_per_selected_workface_and_window(monkeypatch) -> None:
    site = build_site_geometry(33.8303, -116.5453, 200, 200).to_dict()
    faces = list(site["workfaces"][:2])
    request = {
        "id": "pair-cardinality-test", "location": "Palm Springs, California", "timezone": "America/Los_Angeles",
        "date": "2025-07-15", "start": "06:00", "end": "10:00", "aoi": site["aoi"], "workfaces": site["workfaces"],
        "location_anchor": {"latitude": 33.8303, "longitude": -116.5453}, "site_dimensions_m": {"width": 200, "height": 200},
        "crews": [{"name": "Crew A", "headcount": 4}, {"name": "Crew B", "headcount": 4}],
        "tasks": [
            {"id": "T1", "zoneId": faces[0]["id"], "originalStart": "06:00", "durationMinutes": 60, "fixed": False, "environment": "outdoor-moderate"},
            {"id": "T2", "zoneId": faces[1]["id"], "originalStart": "08:00", "durationMinutes": 60, "fixed": False, "environment": "outdoor-moderate"},
        ],
    }
    calls: list[dict] = []

    class FakeToolkit:
        def acquire_workface_thermal_evidence(self, arguments, *, on_status=None):
            calls.append(arguments)
            face_id, window_id = arguments["workface_id"], arguments["window_id"]
            start, end = window_id.split("-")
            data = {
                "status": "LIVE_ACQUIRED", "classification": "LIVE_ACQUIRED", "granularity": 100,
                "workface_id": face_id, "window_id": window_id, "activity_id": f"activity-{face_id}-{window_id}",
                "submitted_polygon": arguments["polygon_aoi"], "provider_result": {"pair": [face_id, window_id]},
                "resultHash": f"hash-{face_id}-{window_id}",
                "exceedanceWindows": [{"analyticType": "exceedance", "start": start, "end": end, "status": "VALID", "units": "hours", "qualifying": False, "provider": "FortyGuard", "activityId": f"activity-{face_id}-{window_id}", "workfaceIds": [face_id], "workface_id": face_id, "window_id": window_id, "aoi": "pair", "aoiHash": "pair", "date": "2025-07-15", "timezone": "America/Los_Angeles", "analyticSource": "FortyGuard:/v1/heatmap", "projectThermalTrigger": {"thresholdC": 32, "quantity": "fortyguard_modeled_temperature", "thresholdUnits": "celsius", "direction": "above"}, "resultHash": f"hash-{face_id}-{window_id}", "version": "v3", "provenance": "LIVE", "tiles": [{"polygon": faces[0]["polygon"], "valueHours": 0}] }],
            }
            return ToolResult(data, Provenance(source="mock", endpoint="/v1/heatmap", activity_id=data["activity_id"]))

    monkeypatch.setattr(service, "orchestrate", lambda current, inspection: {"decision": "INVESTIGATE", "workface_ids": [face["id"] for face in faces], "window_ids": ["06:00-08:00", "08:00-10:00"]})
    monkeypatch.setattr(service, "load_live_toolkit", lambda: FakeToolkit())
    monkeypatch.setattr(service, "decide_evidence_sufficiency", lambda *args, **kwargs: {"decision": "PROCEED", "window_ids": [], "reason": "complete"})
    monkeypatch.setattr(service, "run_engine", lambda payload: ({"verification": {"passed": True, "passedFamilies": 6, "totalFamilies": 6, "families": []}} if payload.get("action") == "validate-baseline" else _run("no-improvement", before_crew_hours=0)))
    monkeypatch.setattr(service, "explain_structured_result", lambda session, run: {"action": "PRESENT_NO_CHANGE", "explanation": "No change.", "request_superintendent_decision": False})

    session = service.Session("pair-cardinality", "new-site", request)
    service.execute_session(session)

    assert len(calls) == 4
    assert {(call["workface_id"], call["window_id"]) for call in calls} == {(face["id"], window) for face in faces for window in ("06:00-08:00", "08:00-10:00")}
    assert all(len(call["polygon_aoi"]["features"]) == 1 for call in calls)
    assert all(call["polygon_aoi"]["features"][0]["properties"]["workface_id"] == call["workface_id"] for call in calls)


def test_invalid_new_site_baseline_stops_before_agent_and_fortyguard(monkeypatch) -> None:
    site = build_site_geometry(33.8303, -116.5453, 200, 200).to_dict()
    request = {
        "id": "invalid-baseline", "location": "Palm Springs, California", "timezone": "America/Los_Angeles",
        "date": "2026-08-28", "start": "06:00", "end": "14:00", "aoi": site["aoi"], "workfaces": site["workfaces"],
        "location_anchor": {"latitude": 33.8303, "longitude": -116.5453}, "site_dimensions_m": {"width": 200, "height": 200},
        "crews": [{"id": "crew-1", "name": "Crew 1", "headcount": 4, "qualifications": ["general"]}],
        "tasks": [{"id": "T1", "name": "Conflicting work", "zoneId": site["workfaces"][0]["id"], "originalStart": "10:00", "durationMinutes": 120, "deadline": "11:00", "crewId": "crew-1", "qualification": "general", "dependencies": [], "fixed": False, "environment": "outdoor-moderate"}],
    }
    verification = {"passed": False, "passedFamilies": 5, "totalFamilies": 6, "families": [{"label": "Deadlines + bounds", "passed": False}]}
    monkeypatch.setattr(service, "run_engine", lambda payload: {"verification": verification})
    monkeypatch.setattr(service, "orchestrate", lambda *args: (_ for _ in ()).throw(AssertionError("agent must not run")))
    monkeypatch.setattr(service, "load_live_toolkit", lambda: (_ for _ in ()).throw(AssertionError("FortyGuard must not run")))
    session = service.Session("invalid-baseline", "new-site", request)
    service.execute_session(session)
    assert session.status == "NO_FEASIBLE_CORRECTION"
    assert session.result["baselineValid"] is False
    assert session.result["beforeCrewHours"] is None
    assert [event["status"] for event in session.events] == ["BASELINE_VALIDATION_FAILED", "NO_FEASIBLE_CORRECTION"]
