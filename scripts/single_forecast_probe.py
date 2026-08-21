"""Execute the one authorized Phoenix future heatmap probe.

This script is intentionally single-use: it submits exactly one POST
/v1/heatmap, then only polls that activity and reads credit usage. It never
calls env_params, retries the heatmap, or changes the AOI/location.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))

from fortyguard import FortyGuardClient  # type: ignore[import-not-found]
from fortyguard_agent.cache import JsonCache, request_hash
from fortyguard_agent.guardrails import FortyGuardRequestGuard
from fortyguard_agent.thermal import (
    ThermalContractError,
    _intersection_area,
    assert_heatmap_schema,
)
from fortyguard_agent.timezones import as_project_local, project_timezone


UTC = timezone.utc
EVIDENCE_DIR = ROOT / "evidence" / "crewclock-live-validation" / "single-forecast-probe"
EVIDENCE_PATH = EVIDENCE_DIR / "single_forecast_probe.json"
HISTORICAL_PATH = ROOT / ".agent_cache" / "live_geographies" / "phoenix_paved_industrial.json"
STARTING_CREDITS = 1_787_060


def load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        if "=" not in raw or raw.lstrip().startswith("#"):
            continue
        key, value = raw.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def utc_iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def json_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def polygon_area_mi2(ring: list[list[float]]) -> float:
    lat = sum(pair[1] for pair in ring) / len(ring)
    scale_x, scale_y = 69.172 * math.cos(math.radians(lat)), 69.0
    planar = [(pair[0] * scale_x, pair[1] * scale_y) for pair in ring]
    return abs(sum(planar[i][0] * planar[(i + 1) % len(planar)][1] - planar[(i + 1) % len(planar)][0] * planar[i][1] for i in range(len(planar))) / 2)


def validate_aoi(aoi: dict[str, Any]) -> dict[str, Any]:
    if aoi.get("type") != "FeatureCollection":
        raise ValueError("aoi_must_be_feature_collection")
    features = aoi.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise ValueError("aoi_must_have_one_feature")
    geometry = features[0].get("geometry") or {}
    if geometry.get("type") != "Polygon":
        raise ValueError("aoi_must_be_polygon")
    rings = geometry.get("coordinates")
    if not isinstance(rings, list) or len(rings) != 1:
        raise ValueError("aoi_must_have_one_ring")
    ring = rings[0]
    if not isinstance(ring, list) or len(ring) < 4 or ring[0] != ring[-1]:
        raise ValueError("aoi_ring_must_be_closed")
    if any(
        not isinstance(pair, list)
        or len(pair) < 2
        or not all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in pair[:2])
        or not -180 <= float(pair[0]) <= 180
        or not -90 <= float(pair[1]) <= 90
        for pair in ring
    ):
        raise ValueError("aoi_coordinates_invalid")
    if not all(24 <= float(pair[1]) <= 50 and -125 <= float(pair[0]) <= -66 for pair in ring):
        raise ValueError("aoi_outside_us_coverage")
    area = polygon_area_mi2(ring)
    if area > 10:
        raise ValueError("aoi_exceeds_basic_plan_limit")
    winding = sum(ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1] for i in range(len(ring) - 1)) / 2
    return {
        "area_mi2": round(area, 9),
        "coordinate_order": "longitude,latitude",
        "crs_assumption": "WGS84 GeoJSON; no crs member",
        "closed": True,
        "winding_shoelace": winding,
        "us_coverage": True,
    }


def capture_client_traffic(client: Any, status_events: list[dict[str, Any]], timestamps: dict[str, str], http_events: list[dict[str, Any]]) -> None:
    original_request = client._session.request

    def traced_request(method: str, url: str, **kwargs: Any) -> Any:
        started = datetime.now(UTC)
        try:
            response = original_request(method, url, **kwargs)
        except Exception:
            finished = datetime.now(UTC)
            http_events.append({"method": method, "path": url.split(client.base_url, 1)[-1], "started_at": utc_iso(started), "finished_at": utc_iso(finished), "status_code": None})
            raise
        finished = datetime.now(UTC)
        path = url.split(client.base_url, 1)[-1]
        http_events.append({"method": method, "path": path, "started_at": utc_iso(started), "finished_at": utc_iso(finished), "status_code": response.status_code})
        if method.upper() == "POST" and path == "/v1/heatmap":
            timestamps["post_timestamp_utc"] = utc_iso(started)
            timestamps["post_finished_utc"] = utc_iso(finished)
            try:
                body = response.json()
                timestamps["submission_response"] = body
            except ValueError:
                timestamps["submission_response"] = {"non_json_response": True}
        if method.upper() == "GET" and path.startswith("/v1/status/"):
            event: dict[str, Any] = {
                "observed_at_utc": utc_iso(finished),
                "http_status": response.status_code,
            }
            if response.status_code == 200:
                try:
                    body = response.json()
                    data = body.get("data") if isinstance(body, dict) else None
                    event["status"] = str((data or {}).get("status", "unknown"))
                    event["envelope"] = data
                except ValueError:
                    event["status"] = "invalid_json"
            elif response.status_code == 404:
                event["status"] = "pending"
            else:
                event["status"] = "http_error"
            status_events.append(event)
        return response

    client._session.request = traced_request


def tile_polygon(feature: dict[str, Any]) -> list[tuple[float, float]]:
    geometry = feature.get("geometry") or {}
    coordinates = geometry.get("coordinates") or []
    if geometry.get("type") != "Polygon" or not coordinates or len(coordinates[0]) < 4:
        raise ThermalContractError("returned_tile_polygon_invalid")
    return [tuple(map(float, pair[:2])) for pair in coordinates[0][:-1]]


def evaluate_result(result: dict[str, Any], aoi: dict[str, Any]) -> dict[str, Any]:
    features = ((result.get("map_data") or {}).get("features") or [])
    stats = result.get("stats_data") or {}
    feature_count = len(features)
    n_cells = stats.get("n_cells")
    units = stats.get("units")
    units_valid = units is None or str(units).lower() in {"celsius", "°c", "deg_c", "c"}
    schema_valid = False
    schema_error: str | None = None
    try:
        assert_heatmap_schema(result, "tcm")
        schema_valid = True
    except ThermalContractError as exc:
        schema_error = str(exc)
    aoi_ring = [tuple(map(float, pair[:2])) for pair in aoi["features"][0]["geometry"]["coordinates"][0][:-1]]
    intersections = []
    temperatures = []
    for feature in features:
        try:
            intersections.append(_intersection_area(aoi_ring, tile_polygon(feature)) > 0)
        except ThermalContractError:
            intersections.append(False)
        properties = feature.get("properties") or {}
        if isinstance(properties.get("average_temperature"), (int, float)):
            temperatures.append({"tile_id": properties.get("tile_id", feature.get("id")), "average_temperature_c": properties["average_temperature"]})
    temperatures.sort(key=lambda row: row["average_temperature_c"])
    return {
        "feature_count": feature_count,
        "n_cells": n_cells,
        "returned_units": units,
        "units_interpreted_as": "celsius_by_current_tcm_contract" if units is None else units,
        "tcm_schema_valid": schema_valid,
        "schema_error": schema_error,
        "units_valid": units_valid,
        "aoi_intersection_valid": bool(intersections) and all(intersections),
        "temperature_summary": {
            "coolest_tile": temperatures[0] if temperatures else None,
            "hottest_tile": temperatures[-1] if temperatures else None,
            "average_temperature_range_c": round(temperatures[-1]["average_temperature_c"] - temperatures[0]["average_temperature_c"], 6) if len(temperatures) >= 2 else 0.0,
        },
        "pass_condition": bool(
            feature_count > 0
            and isinstance(n_cells, (int, float))
            and n_cells > 0
            and schema_valid
            and units_valid
            and bool(intersections)
            and all(intersections)
        ),
    }


def main() -> int:
    load_env_file()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    execution_started_utc = datetime.now(UTC)
    phoenix_tz = project_timezone("America/Phoenix")
    execution_started_local = execution_started_utc.astimezone(phoenix_tz)
    target_local = execution_started_local.replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)
    target_utc = target_local.astimezone(UTC)

    historical = json.loads(HISTORICAL_PATH.read_text(encoding="utf-8"))
    aoi = copy.deepcopy(historical["request"]["aoi"])
    aoi_validation = validate_aoi(aoi)
    payload = {
        "polygon_aoi": aoi,
        "date_time": {
            "start_date": target_local.date().isoformat(),
            "start_time": target_local.strftime("%H:%M"),
            "filter_type": 1,
        },
        "granularity": 100,
        "analytic_type": "tcm",
    }
    request_key = request_hash("/v1/heatmap", payload)
    cache_hit = JsonCache(ROOT / ".agent_cache").get(request_key) is not None
    if cache_hit:
        evidence = {
            "probe": "single_forecast_probe",
            "status": "BLOCKED_BEFORE_SUBMISSION",
            "reason": "request_hash_already_cached",
            "request_hash": request_key,
            "request": payload,
            "execution_started_utc": utc_iso(execution_started_utc),
            "execution_started_phoenix": execution_started_local.isoformat(),
            "target_phoenix_hour": target_local.isoformat(),
            "target_utc_hour": utc_iso(target_utc),
            "aoi_validation": aoi_validation,
            "live_call_made": False,
        }
        EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(evidence, sort_keys=True))
        return 2

    guard = FortyGuardRequestGuard(remaining_credits=STARTING_CREDITS)
    try:
        guard.validate("/v1/heatmap", payload, request_at=target_utc, now=execution_started_utc)
        request_validation = "PASS"
    except Exception as exc:
        evidence = {
            "probe": "single_forecast_probe",
            "status": "BLOCKED_BEFORE_SUBMISSION",
            "reason": str(exc),
            "request_hash": request_key,
            "request": payload,
            "execution_started_utc": utc_iso(execution_started_utc),
            "execution_started_phoenix": execution_started_local.isoformat(),
            "target_phoenix_hour": target_local.isoformat(),
            "target_utc_hour": utc_iso(target_utc),
            "aoi_validation": aoi_validation,
            "live_call_made": False,
        }
        EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(evidence, sort_keys=True))
        return 2

    client = FortyGuardClient(api_key=os.environ.get("FORTYGUARD_API_KEY"), base_url=os.environ.get("FORTYGUARD_BASE_URL"))
    status_events: list[dict[str, Any]] = []
    http_events: list[dict[str, Any]] = []
    timestamps: dict[str, Any] = {}
    capture_client_traffic(client, status_events, timestamps, http_events)
    before: dict[str, Any] = {}
    after: dict[str, Any] = {}
    activity_id: str | None = None
    terminal_status: str | None = None
    terminal_envelope: dict[str, Any] | None = None
    result: dict[str, Any] = {}
    error: str | None = None
    try:
        before = client.fetch_api_key_usage().get("credit_summary", {})
        activity_id = client._submit("/v1/heatmap", payload)
        try:
            result = client.wait_for(activity_id, poll_interval=3.0, timeout=600.0, on_tick=None)
        finally:
            if status_events:
                terminal_envelope = status_events[-1].get("envelope")
                terminal_status = status_events[-1].get("status")
    except Exception as exc:
        error = f"{type(exc).__name__}: {str(exc)[:240]}"
        if status_events:
            terminal_envelope = status_events[-1].get("envelope")
            terminal_status = status_events[-1].get("status")
    finally:
        try:
            after = client.fetch_api_key_usage().get("credit_summary", {})
        except Exception as exc:
            after = {"usage_error": f"{type(exc).__name__}: {str(exc)[:240]}"}

    result_evaluation = evaluate_result(result, aoi) if result else {
        "feature_count": 0,
        "n_cells": None,
        "returned_units": None,
        "tcm_schema_valid": False,
        "units_valid": False,
        "aoi_intersection_valid": False,
        "pass_condition": False,
    }
    post_timestamp_utc = datetime.fromisoformat(timestamps["post_timestamp_utc"].replace("Z", "+00:00")) if timestamps.get("post_timestamp_utc") else None
    lead_hours = (target_utc - post_timestamp_utc).total_seconds() / 3600 if post_timestamp_utc else None
    evidence = {
        "probe": "single_forecast_probe",
        "status": "PASS" if not error and terminal_status and terminal_status.lower() in {"completed", "succeeded"} and result_evaluation["pass_condition"] else "FAIL",
        "request_validation": request_validation,
        "live_call_made": True,
        "endpoint": "/v1/heatmap",
        "execution_started_utc": utc_iso(execution_started_utc),
        "execution_started_phoenix": execution_started_local.isoformat(),
        "post_timestamp_utc": timestamps.get("post_timestamp_utc"),
        "post_timestamp_phoenix": as_project_local(post_timestamp_utc).isoformat() if post_timestamp_utc else None,
        "post_finished_utc": timestamps.get("post_finished_utc"),
        "target_phoenix_hour": target_local.isoformat(),
        "target_utc_hour": utc_iso(target_utc),
        "forecast_lead_hours": lead_hours,
        "request": payload,
        "request_hash": request_key,
        "activity_id": activity_id,
        "submission_response": timestamps.get("submission_response"),
        "status_transitions": status_events,
        "http_events": http_events,
        "terminal_status": terminal_status,
        "terminal_envelope": terminal_envelope,
        "raw_result": result,
        "result_hash": json_hash(result),
        "result_evaluation": result_evaluation,
        "credits_before": before,
        "credits_after": after,
        "credits_consumed": (after.get("cycle_credits_used") - before.get("cycle_credits_used")) if isinstance(after.get("cycle_credits_used"), int) and isinstance(before.get("cycle_credits_used"), int) else None,
        "error": error,
        "aoi_validation": aoi_validation,
        "workface_decision_signal": "NOT_TESTABLE",
        "workface_finding": "The canonical project scenario has zone IDs but no GeoJSON workface coordinates, so returned live tiles cannot be attributed to synthetic workfaces without inventing geometry.",
        "provenance": "LIVE FORTYGUARD",
    }
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": evidence["status"],
        "activity_id": activity_id,
        "post_timestamp_utc": evidence["post_timestamp_utc"],
        "target_utc_hour": evidence["target_utc_hour"],
        "forecast_lead_hours": evidence["forecast_lead_hours"],
        "feature_count": result_evaluation["feature_count"],
        "n_cells": result_evaluation["n_cells"],
        "credits_consumed": evidence["credits_consumed"],
        "evidence_path": str(EVIDENCE_PATH),
    }, sort_keys=True))
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
