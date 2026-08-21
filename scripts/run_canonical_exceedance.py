from __future__ import annotations

"""Acquire the five canonical historical Phoenix exceedance windows.

This script is deliberately separate from the Groq evaluator.  It makes only
schedule-aligned historical ``/v1/heatmap`` exceedance calls, validates each
completed response, and stores sanitized cached-live evidence for deterministic
CrewClock replay.
"""

import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))

from fortyguard import FortyGuardClient  # type: ignore[import-not-found]


DATE = "2025-07-15"
GRANULARITY = 100
THRESHOLD_C = 32.0
THRESHOLD_PROVENANCE = (
    "CrewClock project_thermal_trigger configured before live retrieval; "
    "FortyGuard modeled-temperature/TCM quantity, not heat index."
)
STARTING_CREDITS = 1_782_840
MAX_CALLS = 5
MAX_RUN_CREDITS = 25_000
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

# These are the minimum windows needed to cover every original and proposed
# task boundary in the canonical 06:00–16:00 Phoenix shift.
WINDOWS = (
    ("06:00", "08:00"),
    ("08:00", "10:00"),
    ("10:00", "12:00"),
    ("12:00", "14:00"),
    ("14:00", "16:00"),
)

WORKFACE_POLYGONS = {
    "north": [(-112.01840, 33.43400), (-112.01800, 33.43400), (-112.01800, 33.43440), (-112.01840, 33.43440)],
    "south": [(-112.01840, 33.43360), (-112.01800, 33.43360), (-112.01800, 33.43400), (-112.01840, 33.43400)],
    "laydown": [(-112.01795, 33.43360), (-112.01760, 33.43360), (-112.01760, 33.43395), (-112.01795, 33.43395)],
    "access": [(-112.01795, 33.43405), (-112.01760, 33.43405), (-112.01760, 33.43440), (-112.01795, 33.43440)],
}

EVIDENCE_DIR = ROOT / "evidence" / "crewclock-canonical-exceedance"


def _load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def _ring(aoi: dict[str, Any]) -> list[tuple[float, float]]:
    features = aoi.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise ValueError("aoi_must_contain_one_feature")
    geometry = features[0].get("geometry") if isinstance(features[0], dict) else None
    coordinates = geometry.get("coordinates") if isinstance(geometry, dict) else None
    if not isinstance(coordinates, list) or not coordinates or len(coordinates[0]) < 4:
        raise ValueError("aoi_polygon_required")
    return [(float(pair[0]), float(pair[1])) for pair in coordinates[0][:-1]]


def _point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    inside = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > point[1]) != (b[1] > point[1]):
            x = (b[0] - a[0]) * (point[1] - a[1]) / (b[1] - a[1]) + a[0]
            if point[0] < x:
                inside = not inside
    return inside


def _validate_geometry() -> None:
    aoi_ring = _ring(AOI)
    if not all(-180 <= lon <= 180 and -90 <= lat <= 90 for lon, lat in aoi_ring):
        raise ValueError("aoi_coordinates_must_be_wgs84_lon_lat")
    if not all(-125 < lon < -65 and 24 < lat < 50 for lon, lat in aoi_ring):
        raise ValueError("aoi_must_be_within_us")
    min_lon = min(point[0] for point in aoi_ring)
    max_lon = max(point[0] for point in aoi_ring)
    min_lat = min(point[1] for point in aoi_ring)
    max_lat = max(point[1] for point in aoi_ring)
    # The proven AOI is far below the basic plan's 10 square-mile limit.
    area_mi2 = (max_lon - min_lon) * 52.5 * (max_lat - min_lat) * 69.0
    if area_mi2 <= 0 or area_mi2 >= 10:
        raise ValueError("aoi_area_outside_basic_plan_limit")
    for workface_id, polygon in WORKFACE_POLYGONS.items():
        if len(polygon) < 3 or not all(_point_in_polygon(point, aoi_ring) for point in polygon):
            raise ValueError(f"workface_outside_shared_aoi:{workface_id}")


def _usage(client: FortyGuardClient) -> dict[str, Any]:
    body = client.fetch_api_key_usage()
    summary = body.get("credit_summary", {}) if isinstance(body, dict) else {}
    return {
        "cycle_credits_used": summary.get("cycle_credits_used"),
        "cycle_remaining_credits": summary.get("cycle_remaining_credits"),
    }


def _features(result: dict[str, Any]) -> list[dict[str, Any]]:
    map_data = result.get("map_data")
    return map_data.get("features", []) if isinstance(map_data, dict) and isinstance(map_data.get("features"), list) else []


def _validate_result(result: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not isinstance(result, dict):
        raise ValueError("completed_result_must_be_object")
    stats = result.get("stats_data")
    if not isinstance(stats, dict) or stats.get("analytic_type") != "exceedance":
        raise ValueError("exceedance_analytic_type_required")
    if stats.get("units") not in {"hour", "hours"} or int(stats.get("n_cells", 0)) <= 0:
        raise ValueError("exceedance_units_or_cells_invalid")
    features = _features(result)
    if not features:
        raise ValueError("completed_but_empty")
    aoi_ring = _ring(AOI)
    min_lon = min(point[0] for point in aoi_ring)
    max_lon = max(point[0] for point in aoi_ring)
    min_lat = min(point[1] for point in aoi_ring)
    max_lat = max(point[1] for point in aoi_ring)
    for feature in features:
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates") if isinstance(geometry, dict) else None
        properties = feature.get("properties", {})
        if geometry.get("type") != "Polygon" or not coordinates or not coordinates[0]:
            raise ValueError("exceedance_tile_polygon_required")
        value = properties.get("value") if isinstance(properties, dict) else None
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or value < 0:
            raise ValueError("exceedance_tile_value_invalid")
        points = [(float(pair[0]), float(pair[1])) for pair in coordinates[0]]
        tile_min_lon = min(point[0] for point in points)
        tile_max_lon = max(point[0] for point in points)
        tile_min_lat = min(point[1] for point in points)
        tile_max_lat = max(point[1] for point in points)
        if tile_max_lon < min_lon or tile_min_lon > max_lon or tile_max_lat < min_lat or tile_min_lat > max_lat:
            raise ValueError("exceedance_tile_does_not_intersect_project_aoi")
    return features, stats


def _safe_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _path(start: str, end: str) -> Path:
    return EVIDENCE_DIR / f"phoenix_{DATE}_{start.replace(':', '')}_{end.replace(':', '')}.json"


def main() -> int:
    _load_env()
    _validate_geometry()
    if not os.getenv("FORTYGUARD_API_KEY"):
        raise RuntimeError("fortyguard_api_key_not_configured")
    client = FortyGuardClient(api_key=os.environ["FORTYGUARD_API_KEY"], base_url=os.getenv("FORTYGUARD_BASE_URL"))
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    live_calls = 0
    run_spend = 0
    for start, end in WINDOWS:
        path = _path(start, end)
        if path.is_file():
            cached = json.loads(path.read_text(encoding="utf-8"))
            _validate_result(cached["result"])
            records.append(cached)
            continue
        if live_calls >= MAX_CALLS:
            raise RuntimeError("live_analysis_call_cap_reached")
        before = _usage(client)
        expected_cost = 4220
        if run_spend + expected_cost > MAX_RUN_CREDITS:
            raise RuntimeError("run_credit_cap_would_be_exceeded")
        remaining = before.get("cycle_remaining_credits")
        if isinstance(remaining, int) and remaining < expected_cost:
            raise RuntimeError("insufficient_live_credits_for_next_window")
        request = {
            "date": DATE,
            "start_time": start,
            "end_time": end,
            "filter_type": 2,
            "granularity": GRANULARITY,
            "analytic_type": "exceedance",
            "threshold_c": THRESHOLD_C,
            "direction": "above",
            "aoi": AOI,
        }
        raw = client.create_heatmap(
            polygon_aoi=AOI,
            start_date=DATE,
            start_time=start,
            end_time=end,
            filter_type=2,
            granularity=GRANULARITY,
            analytic_type="exceedance",
            threshold=THRESHOLD_C,
            direction="above",
            poll_interval=3.0,
            timeout=600.0,
            verbose=False,
        )
        result = raw.get("result", raw) if isinstance(raw, dict) else raw
        features, stats = _validate_result(result)
        after = _usage(client)
        before_used = before.get("cycle_credits_used")
        after_used = after.get("cycle_credits_used")
        delta = after_used - before_used if isinstance(after_used, int) and isinstance(before_used, int) else None
        if isinstance(delta, int):
            run_spend += delta
        else:
            run_spend += expected_cost
        live_calls += 1
        record = {
            "status": "COMPLETED",
            "provenance": "LIVE_FORTYGUARD",
            "operation": "POST /v1/heatmap",
            "activity_id": raw.get("activity_id") if isinstance(raw, dict) else None,
            "request": request,
            "historical_date": DATE,
            "local_window": {"start": start, "end": end, "timezone": "America/Phoenix"},
            "project_thermal_trigger": {"threshold_c": THRESHOLD_C, "quantity": "fortyguard_modeled_temperature", "provenance": THRESHOLD_PROVENANCE},
            "granularity_m": GRANULARITY,
            "result": result,
            "result_sha256": _safe_hash(result),
            "feature_count": len(features),
            "stats": stats,
            "retrieved_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "credit_delta": delta,
            "credits_before": before,
            "credits_after": after,
        }
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        records.append(record)
        print(json.dumps({"window": f"{start}-{end}", "activity_id": record["activity_id"], "feature_count": len(features), "credit_delta": delta}, separators=(",", ":")))
    manifest = {
        "status": "COMPLETE" if len(records) == len(WINDOWS) else "PARTIAL",
        "provenance": "LIVE_FORTYGUARD",
        "historical_control_date": DATE,
        "aoi": AOI,
        "project_thermal_trigger": {"threshold_c": THRESHOLD_C, "quantity": "fortyguard_modeled_temperature", "provenance": THRESHOLD_PROVENANCE},
        "windows": [{"start": start, "end": end, "evidence_path": str(_path(start, end).relative_to(ROOT))} for start, end in WINDOWS],
        "live_analysis_calls_this_run": live_calls,
        "credits_used_this_run": run_spend,
        "credit_cap": MAX_RUN_CREDITS,
        "starting_credits_reported": STARTING_CREDITS,
        "records": [{"window": record["local_window"], "activity_id": record.get("activity_id"), "feature_count": record["feature_count"], "stats": record["stats"], "result_sha256": record["result_sha256"]} for record in records],
    }
    (EVIDENCE_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "live_analysis_calls": live_calls, "credits_used": run_spend, "windows": len(records)}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
