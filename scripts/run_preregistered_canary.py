from __future__ import annotations

"""Execute one frozen winner-closure canary and print a secret-free summary."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fortyguard_agent.production_service import Session, approve_session, execute_session  # noqa: E402
from fortyguard_agent.site_geometry import build_site_geometry  # noqa: E402


def request_for(case: dict, shared: dict) -> dict:
    site = build_site_geometry(case["latitude"], case["longitude"], case["site_width_m"], case["site_height_m"]).to_dict()
    crews = [
        {"id": crew_id, "name": f"Canary {crew_id}", "trade": "General construction", "headcount": headcount, "color": "#777777", "qualifications": ["general"]}
        for crew_id, headcount in shared["crew_headcounts"].items()
    ]
    tasks = []
    for row in shared["tasks"]:
        tasks.append({
            "id": row["id"], "name": row["name"], "crewId": row["crew"], "zoneId": row["workface"],
            "durationMinutes": row["duration_minutes"], "originalStart": row["start"], "proposedStart": row["start"],
            "fixed": row["fixed"], "environment": "shaded-support" if row["environment"] == "indoor" else "outdoor-moderate",
            "qualification": "general", "dependencies": [], "deadline": "14:00", "weatherSensitivity": {"precipitation": False},
        })
    return {
        "id": f"preregistered-canary-{case['order']}", "scenario": "new-site", "location": case["location"],
        "timezone": case["timezone"], "date": case["date"], "start": "06:00", "end": "14:00",
        "location_anchor": {"latitude": case["latitude"], "longitude": case["longitude"]},
        "site_dimensions_m": {"width": case["site_width_m"], "height": case["site_height_m"]},
        "aoi": site["aoi"], "workfaces": site["workfaces"], "tasks": tasks, "crews": crews,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, required=True, choices=range(1, 6))
    args = parser.parse_args()
    manifest = json.loads((ROOT / "evidence" / "crewclock-winner-closure" / "preregistered_canaries.json").read_text(encoding="utf-8"))
    case = manifest["canaries"][args.index - 1]
    session = Session(f"canary-{args.index}", "new-site", request_for(case, manifest["shared_schedule"]))
    execute_session(session)
    run = session.result or {}
    approval = {"approved": False, "status": "NOT_APPLICABLE"}
    if session.status == "AWAITING_APPROVAL":
        approval = approve_session(session, {"recommendationId": run.get("recommendationId"), "candidateHash": run.get("candidateHash")})
    evidence = run.get("thermalEvidence", {}) if isinstance(run, dict) else {}
    changed = [task_id for task_id, start in (run.get("recommendation") or {}).items() if start != run.get("original", {}).get(task_id)]
    print(json.dumps({
        "order": case["order"], "location": case["location"], "date": case["date"], "status": session.status,
        "run_status": run.get("status"), "baseline_shhch": run.get("beforeCrewHours"), "proposed_shhch": run.get("afterCrewHours"),
        "baseline_valid": run.get("baselineValid"),
        "original_constraint_families": {
            "passed": (run.get("originalVerification") or {}).get("passedFamilies"),
            "total": (run.get("originalVerification") or {}).get("totalFamilies"),
        },
        "proposed_constraint_families": {
            "passed": (run.get("recommendationVerification") or {}).get("passedFamilies"),
            "total": (run.get("recommendationVerification") or {}).get("totalFamilies"),
        },
        "tasks_changed": changed, "verification_passed": (run.get("recommendationVerification") or {}).get("passed"),
        "agent_explanation": run.get("agentExplanation"),
        "approval": approval, "evidence_classification": evidence.get("classification"),
        "activity_ids": evidence.get("activityIds", []), "window_count": len(evidence.get("exceedanceWindows", [])),
        "cache_reuses": sum(1 for event in session.events if event.get("status") == "THERMAL_EVIDENCE_READY" for _ in range(int(event.get("metadata", {}).get("cache_reuses", 0)))),
        "provider": session.provider, "events": [{"status": event["status"], "summary": event["summary"], "metadata": event.get("metadata", {})} for event in session.events],
    }, separators=(",", ":"), default=str))


if __name__ == "__main__":
    main()
