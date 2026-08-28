from __future__ import annotations

"""Deterministic schedule-aligned evidence planning and bundle assembly."""

from datetime import datetime, timedelta
import hashlib
import json
from typing import Any, Iterable


class InvestigationPlanError(ValueError):
    pass


def schedule_windows(start: str, end: str, *, minutes: int = 120) -> list[dict[str, str]]:
    if minutes <= 0:
        raise InvestigationPlanError("window_size_must_be_positive")
    try:
        left = datetime.strptime(start, "%H:%M")
        right = datetime.strptime(end, "%H:%M")
    except ValueError as exc:
        raise InvestigationPlanError("shift_time_must_be_hh_mm") from exc
    if right <= left:
        raise InvestigationPlanError("shift_end_must_follow_start")
    result: list[dict[str, str]] = []
    cursor = left
    while cursor < right:
        window_end = min(right, cursor + timedelta(minutes=minutes))
        start_text, end_text = cursor.strftime("%H:%M"), window_end.strftime("%H:%M")
        result.append({"id": f"{start_text}-{end_text}", "start": start_text, "end": end_text})
        cursor = window_end
    return result


def _minutes(value: str) -> int:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def investigation_facts(request: dict[str, Any], windows: list[dict[str, str]]) -> dict[str, Any]:
    tasks = request.get("tasks") if isinstance(request.get("tasks"), list) else []
    relevant: list[dict[str, Any]] = []
    for task in tasks:
        if not isinstance(task, dict) or task.get("environment") == "shaded-support":
            continue
        start = str(task.get("originalStart", ""))
        duration = task.get("durationMinutes")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool):
            continue
        try:
            task_start, task_end = _minutes(start), _minutes(start) + int(duration)
        except ValueError:
            continue
        # Fixed work can only need its actual windows. Movable work can be
        # considered anywhere inside the shift, so its deterministic feasible
        # window set must be covered before a cooler retiming can be proven.
        eligible = [window["id"] for window in windows] if not bool(task.get("fixed")) else [window["id"] for window in windows if max(task_start, _minutes(window["start"])) < min(task_end, _minutes(window["end"]))]
        relevant.append({
            "task_id": task.get("id"), "workface_id": task.get("zoneId"),
            "fixed": bool(task.get("fixed")), "window_ids": eligible,
        })
    return {"windows": windows, "relevant_outdoor_tasks": relevant}


def default_investigation_plan(facts: dict[str, Any]) -> dict[str, Any]:
    tasks = facts.get("relevant_outdoor_tasks", [])
    faces = sorted({str(task["workface_id"]) for task in tasks if task.get("workface_id")})
    window_ids = sorted({window_id for task in tasks for window_id in task.get("window_ids", [])})
    return {"decision": "INVESTIGATE" if tasks else "NO_THERMAL_INVESTIGATION", "workface_ids": faces, "window_ids": window_ids, "reason": "bounded schedule relevance"}


def validate_investigation_plan(plan: Any, facts: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise InvestigationPlanError("investigation_plan_must_be_object")
    decision = plan.get("decision")
    tasks = facts.get("relevant_outdoor_tasks", [])
    if decision not in {"INVESTIGATE", "NO_THERMAL_INVESTIGATION"}:
        raise InvestigationPlanError("investigation_decision_invalid")
    if decision == "NO_THERMAL_INVESTIGATION":
        if tasks:
            raise InvestigationPlanError("outdoor_work_requires_investigation_or_explicit_abstention")
        return {"decision": decision, "workface_ids": [], "window_ids": [], "reason": str(plan.get("reason", ""))[:240]}
    faces = plan.get("workface_ids")
    window_ids = plan.get("window_ids")
    if not isinstance(faces, list) or not isinstance(window_ids, list) or not faces or not window_ids:
        raise InvestigationPlanError("investigation_requires_workfaces_and_windows")
    if len(faces) != len(set(faces)) or len(window_ids) != len(set(window_ids)):
        raise InvestigationPlanError("duplicate_investigation_request")
    relevant_faces = {task.get("workface_id") for task in tasks if task.get("workface_id")}
    valid_windows = {window["id"] for window in facts.get("windows", [])}
    if any(face not in relevant_faces for face in faces):
        raise InvestigationPlanError("investigation_workface_not_relevant")
    # A decision-grade global SHHCH result cannot treat an uninvestigated
    # outdoor workface as zero. The model chooses the bounded workfaces, but
    # deterministic validation requires complete spatial coverage before any
    # acquisition plan may proceed. Omitted relevant faces trigger the normal
    # bounded correction path rather than a silent fetch-all expansion.
    if set(faces) != relevant_faces:
        raise InvestigationPlanError("investigation_workface_coverage_incomplete")
    if any(window not in valid_windows for window in window_ids):
        raise InvestigationPlanError("investigation_window_outside_shift")
    relevant_pairs = {(task.get("workface_id"), window) for task in tasks for window in task.get("window_ids", [])}
    if any(not any((face, window) in relevant_pairs for face in faces) for window in window_ids):
        raise InvestigationPlanError("investigation_window_does_not_intersect_relevant_work")
    return {"decision": decision, "workface_ids": list(faces), "window_ids": list(window_ids), "reason": str(plan.get("reason", ""))[:240]}


def assemble_evidence_bundle(parts: Iterable[dict[str, Any]], *, plan: dict[str, Any], aoi_hash: str) -> dict[str, Any]:
    rows = list(parts)
    if not rows:
        raise InvestigationPlanError("evidence_parts_required")
    evidence_records = []
    for row in rows:
        required = ("workface_id", "window_id", "activity_id", "submitted_polygon", "provider_result")
        if any(key not in row for key in required):
            raise InvestigationPlanError("evidence_record_identity_required")
        evidence_records.append({key: row[key] for key in required})
    windows = [window for row in rows for window in row.get("exceedanceWindows", [])]
    identities = [
        {"activity_id": row.get("activityId"), "result_hash": row.get("resultHash"), "window": [window.get("start"), window.get("end")]}
        for row in rows for window in row.get("exceedanceWindows", [])
    ]
    bundle_hash = hashlib.sha256(json.dumps({"aoi_hash": aoi_hash, "plan": plan, "identities": identities}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    first = rows[0]
    cache_reuse_count = sum(row.get("status") == "LIVE_CACHE_REUSED" for row in rows)
    acquisition_mode = "CACHE_REUSED" if cache_reuse_count == len(rows) else "LIVE" if cache_reuse_count == 0 else "MIXED"
    return {
        **first,
        "status": "LIVE_ACQUIRED_SEGMENTED",
        "classification": "LIVE_ACQUIRED_SEGMENTED",
        "aoiHash": aoi_hash,
        "evidenceBundleHash": bundle_hash,
        "investigationPlan": plan,
        "activityIds": [row.get("activityId") for row in rows],
        "resultHashes": [row.get("resultHash") for row in rows],
        "acquisitionMode": acquisition_mode,
        "cacheReuseCount": cache_reuse_count,
        "evidenceRecords": evidence_records,
        "exceedanceWindows": windows,
        "coverage": "VALID_SEGMENTED",
        "granularity": first.get("granularity", 100),
    }
