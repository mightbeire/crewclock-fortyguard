from __future__ import annotations

from fortyguard_agent import production_service as service


def _run(status: str = "recommended") -> dict:
    recommendation = {"T1": "07:00"} if status == "recommended" else None
    return {
        "run": {
            "status": status,
            "recommendation": recommendation,
            "stats": {"candidatesConsidered": 2 if recommendation else 0, "feasibleCandidates": 1 if recommendation else 0, "rejectedCandidates": 1 if recommendation else 0},
            "recommendationVerification": {"passed": True} if recommendation else None,
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
