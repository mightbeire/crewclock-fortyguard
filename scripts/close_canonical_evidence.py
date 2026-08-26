from __future__ import annotations

"""Acquire and package the bounded canonical CrewClock evidence run.

The first 06:00-08:00 sanity activity was submitted separately and is queried
by activity id here so it is persisted without spending another credit.
"""

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))

from fortyguard import FortyGuardClient  # type: ignore[import-not-found]
from fortyguard.exceptions import FortyGuardError, TaskFailedError, TaskTimeoutError

DATE = "2025-07-15"
TIMEZONE = "America/Phoenix"
AOI = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "Polygon", "coordinates": [[
            [-112.01845, 33.43355], [-112.01755, 33.43355],
            [-112.01755, 33.43445], [-112.01845, 33.43445],
            [-112.01845, 33.43355],
        ]]},
    }],
}
WORKFACES = {
    "north": [[-112.01840, 33.43400], [-112.01800, 33.43400], [-112.01800, 33.43440], [-112.01840, 33.43440]],
    "south": [[-112.01840, 33.43360], [-112.01800, 33.43360], [-112.01800, 33.43400], [-112.01840, 33.43400]],
    "laydown": [[-112.01795, 33.43360], [-112.01760, 33.43360], [-112.01760, 33.43395], [-112.01795, 33.43395]],
    "access": [[-112.01795, 33.43405], [-112.01760, 33.43405], [-112.01760, 33.43440], [-112.01795, 33.43440]],
}
WINDOWS = (("06:00", "08:00"), ("08:00", "10:00"), ("10:00", "12:00"), ("12:00", "14:00"), ("14:00", "16:00"))
SANITY_ACTIVITY_ID = "60568d12-10d6-478b-af83-7d197c1eec37"
SANITY_CREDITS_BEFORE = {"cycle_credits_used": 225600, "cycle_remaining_credits": 1774400}
SANITY_CREDITS_AFTER = {"cycle_credits_used": 229820, "cycle_remaining_credits": 1770180}
OUT = ROOT / "evidence" / "fortyguard-canonical-phoenix"
TRIGGER = {
    "threshold_c": 32.0,
    "quantity": "fortyguard_modeled_temperature",
    "threshold_units": "celsius",
    "direction": "above",
    "provenance": "CrewClock project_thermal_trigger configured before live retrieval; FortyGuard modeled temperature, not heat index.",
}


def load_env() -> None:
    path = ROOT / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def usage(client: FortyGuardClient) -> dict[str, Any]:
    body = client.fetch_api_key_usage()
    summary = body.get("credit_summary", {}) if isinstance(body, dict) else {}
    return {"cycle_credits_used": summary.get("cycle_credits_used"), "cycle_remaining_credits": summary.get("cycle_remaining_credits")}


def result_features(result: Any) -> list[dict[str, Any]]:
    if not isinstance(result, dict):
        return []
    map_data = result.get("map_data")
    features = map_data.get("features") if isinstance(map_data, dict) else None
    return features if isinstance(features, list) and all(isinstance(item, dict) for item in features) else []


def validate_result(result: Any) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ValueError("result_must_be_object")
    stats = result.get("stats_data")
    features = result_features(result)
    if not isinstance(stats, dict) or stats.get("analytic_type") != "exceedance":
        raise ValueError("analytic_type_must_be_exceedance")
    if str(stats.get("units", "")).lower() not in {"hour", "hours"}:
        raise ValueError("units_must_be_hour")
    if not features or int(stats.get("n_cells", 0)) <= 0:
        raise ValueError("usable_cells_required")
    values: list[float] = []
    for feature in features:
        geometry = feature.get("geometry")
        props = feature.get("properties")
        if not isinstance(geometry, dict) or geometry.get("type") != "Polygon":
            raise ValueError("polygon_tile_required")
        if not isinstance(props, dict) or isinstance(props.get("value"), bool) or not isinstance(props.get("value"), (int, float)):
            raise ValueError("numeric_exceedance_value_required")
        value = float(props["value"])
        if not math.isfinite(value) or value < 0:
            raise ValueError("exceedance_value_invalid")
        values.append(value)
        ring = geometry.get("coordinates", [[]])[0]
        if not isinstance(ring, list) or len(ring) < 4:
            raise ValueError("tile_geometry_required")
        if not all(isinstance(pair, list) and len(pair) >= 2 for pair in ring):
            raise ValueError("tile_coordinates_invalid")
        if not any(AOI["features"][0]["geometry"]["coordinates"][0][0][0] <= float(pair[0]) <= AOI["features"][0]["geometry"]["coordinates"][0][2][0] and AOI["features"][0]["geometry"]["coordinates"][0][0][1] <= float(pair[1]) <= AOI["features"][0]["geometry"]["coordinates"][0][2][1] for pair in ring):
            raise ValueError("tile_does_not_overlap_aoi")
    return {"analytic_type": stats.get("analytic_type"), "units": stats.get("units"), "n_cells": stats.get("n_cells"), "feature_count": len(features), "min": stats.get("min"), "max": stats.get("max"), "mean": stats.get("mean"), "values": values}


def record_from_status(client: FortyGuardClient, activity_id: str, start: str, end: str, before: dict[str, Any] | None = None, after: dict[str, Any] | None = None, statuses: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    data = client.get_status(activity_id)
    status = str(data.get("status", "")).upper()
    result = data.get("result")
    record: dict[str, Any] = {
        "status": status,
        "provenance": "LIVE_FORTYGUARD",
        "operation": "POST /v1/heatmap; GET /v1/status/{activity_id}",
        "activity_id": activity_id,
        "request": {"polygon_aoi": AOI, "date_time": {"start_date": DATE, "start_time": start, "end_time": end, "filter_type": 2}, "granularity": 100, "analytic_type": "exceedance", "threshold": 32.0, "direction": "above"},
        "historical_date": DATE,
        "local_window": {"start": start, "end": end, "timezone": TIMEZONE},
        "request_time_semantics": "AOI_LOCAL_TIME",
        "phoenix_timezone": TIMEZONE,
        "project_thermal_trigger": TRIGGER,
        "aoi": AOI,
        "workfaces": WORKFACES,
        "status_history": statuses or [{"status": status}],
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "credits_before": before,
        "credits_after": after,
        "credit_delta": (after.get("cycle_credits_used") - before.get("cycle_credits_used")) if isinstance(before, dict) and isinstance(after, dict) and isinstance(before.get("cycle_credits_used"), int) and isinstance(after.get("cycle_credits_used"), int) else None,
    }
    if status in {"SUCCEEDED", "COMPLETED"}:
        summary = validate_result(result)
        record["result"] = result
        record["stats"] = summary
        record["feature_count"] = summary["feature_count"]
        record["result_sha256"] = digest(result)
    else:
        record["result"] = None
        record["stats"] = None
        record["feature_count"] = 0
        record["result_sha256"] = None
        record["provider_message"] = data.get("message")
    return record


def acquire_window(client: FortyGuardClient, start: str, end: str, before: dict[str, Any]) -> dict[str, Any]:
    activity_id = client.create_heatmap(polygon_aoi=AOI, start_date=DATE, start_time=start, end_time=end, filter_type=2, granularity=100, analytic_type="exceedance", threshold=32.0, direction="above", wait=False, verbose=False)
    statuses: list[dict[str, Any]] = []
    try:
        result = client.wait_for(activity_id, poll_interval=3.0, timeout=600.0, on_tick=lambda status, data: statuses.append({"status": status, "has_result": isinstance(data.get("result"), dict)}))
        after = usage(client)
        stats = validate_result(result)
        record = record_from_status(client, activity_id, start, end, before, after, statuses)
        record["result"] = result
        record["stats"] = stats
        record["feature_count"] = stats["feature_count"]
        record["result_sha256"] = digest(result)
        return record
    except (TaskFailedError, TaskTimeoutError, FortyGuardError, ValueError) as exc:
        after = usage(client)
        try:
            record = record_from_status(client, activity_id, start, end, before, after, statuses)
        except Exception:
            record = {"status": "FAILED", "provenance": "LIVE_FORTYGUARD", "activity_id": activity_id, "request": {"date": DATE, "start_time": start, "end_time": end, "filter_type": 2, "analytic_type": "exceedance", "threshold": 32.0, "direction": "above"}, "local_window": {"start": start, "end": end, "timezone": TIMEZONE}, "result": None, "stats": None, "feature_count": 0, "result_sha256": None, "credits_before": before, "credits_after": after, "credit_delta": None}
        record["error_type"] = type(exc).__name__
        record["error"] = str(exc)[:300]
        return record


def main() -> int:
    load_env()
    if not os.getenv("FORTYGUARD_API_KEY"):
        raise RuntimeError("fortyguard_api_key_not_configured")
    OUT.mkdir(parents=True, exist_ok=True)
    client = FortyGuardClient(base_url=os.getenv("FORTYGUARD_BASE_URL"))
    mission_before = usage(client)
    records: list[dict[str, Any]] = []

    # Persist the already-completed sanity activity without resubmitting it.
    sanity = record_from_status(client, SANITY_ACTIVITY_ID, "06:00", "08:00", SANITY_CREDITS_BEFORE, SANITY_CREDITS_AFTER, [{"status": "processing", "has_result": False}] * 6 + [{"status": "completed", "has_result": True}])
    records.append(sanity)
    (OUT / "phoenix_2025-07-15_0600_0800.json").write_text(json.dumps(sanity, indent=2, sort_keys=True), encoding="utf-8")

    for start, end in WINDOWS[1:]:
        before = usage(client)
        record = acquire_window(client, start, end, before)
        records.append(record)
        (OUT / f"phoenix_{DATE}_{start.replace(':', '')}_{end.replace(':', '')}.json").write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    mission_after = usage(client)
    successful = [record for record in records if record.get("status") in {"SUCCEEDED", "COMPLETED"} and record.get("feature_count", 0) > 0]
    failed = [record for record in records if record not in successful]
    spend = mission_after.get("cycle_credits_used") - mission_before.get("cycle_credits_used") if isinstance(mission_before.get("cycle_credits_used"), int) and isinstance(mission_after.get("cycle_credits_used"), int) else None
    manifest = {
        "package": "CrewClock canonical Phoenix FortyGuard evidence",
        "status": "COMPLETE" if len(successful) == len(WINDOWS) else "PARTIAL",
        "provider_status": "RESOLVED" if successful else "STILL_FAILING",
        "sanity_request": {"status": sanity.get("status"), "activity_id": SANITY_ACTIVITY_ID, "feature_count": sanity.get("feature_count"), "stats": sanity.get("stats")},
        "request_time_semantics": "AOI_LOCAL_TIME",
        "phoenix_timezone": TIMEZONE,
        "historical_date": DATE,
        "analytic_type": "exceedance",
        "thermal_trigger": TRIGGER,
        "aoi": AOI,
        "workfaces": WORKFACES,
        "windows": [{"start": start, "end": end, "path": f"phoenix_{DATE}_{start.replace(':', '')}_{end.replace(':', '')}.json", "activity_id": next((r.get("activity_id") for r in records if r.get("local_window", {}).get("start") == start), None), "status": next((r.get("status") for r in records if r.get("local_window", {}).get("start") == start), "UNKNOWN"), "feature_count": next((r.get("feature_count", 0) for r in records if r.get("local_window", {}).get("start") == start), 0)} for start, end in WINDOWS],
        "decision_grade_coverage": len(successful) == len(WINDOWS),
        "geometry_validation": "PASS" if all(record.get("feature_count", 0) > 0 for record in successful) and len(successful) == len(WINDOWS) else "FAIL",
        "credits_before_mission": mission_before,
        "credits_after_mission": mission_after,
        "credits_spent": spend,
        "successful_jobs": len(successful),
        "failed_jobs": len(failed),
        "failed_job_credits_charged": sum(record.get("credit_delta") or 0 for record in failed),
        "environmental_parameter_calls": 0,
        "api_keys_used": ["KEY_1"],
        "secrets_exposed": "NO",
        "result_hashes": {record.get("local_window", {}).get("start"): record.get("result_sha256") for record in records},
    }
    (OUT / "request_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "successful_jobs": len(successful), "failed_jobs": len(failed), "credits_spent": spend, "activities": [record.get("activity_id") for record in records]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
