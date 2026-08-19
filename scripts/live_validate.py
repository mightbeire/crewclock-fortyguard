"""Run one idempotent, credit-audited live FortyGuard validation pass.

The script uses the account usage endpoint around each controlled operation and
stores sanitized successful responses under .agent_cache/live_validation. If a
complete run already exists, it reuses it and makes no new analysis calls.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))

from fortyguard import FortyGuardClient  # type: ignore[import-not-found]


RUN_DIR = ROOT / ".agent_cache" / "live_validation"
DATE = "2025-07-15"
LAT = 37.318
LON = -121.883
AOI = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "Polygon", "coordinates": [[
            [-121.8840, 37.3175], [-121.8830, 37.3175],
            [-121.8830, 37.3185], [-121.8840, 37.3185],
            [-121.8840, 37.3175],
        ]]},
    }],
}


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        raise RuntimeError(".env not found")
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            key, value = raw.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def write_json(name: str, data: dict[str, Any]) -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / name).write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def read_json(name: str) -> dict[str, Any] | None:
    path = RUN_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def sanitize(value: Any, key: str = "") -> Any:
    if any(token in key.lower() for token in ("api_key", "token", "secret", "password", "credential")):
        return "REDACTED"
    if isinstance(value, dict):
        return {str(k): sanitize(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v, key) for v in value]
    if isinstance(value, str):
        return re.sub(r"(?i)(fg_live_|sk-)[A-Za-z0-9_-]+", r"\1REDACTED", value)
    return value


def usage(client: FortyGuardClient) -> dict[str, Any]:
    return sanitize(client.fetch_api_key_usage())


def used(usage_body: dict[str, Any]) -> int | float | None:
    summary = usage_body.get("credit_summary", {})
    return summary.get("cycle_credits_used", usage_body.get("total_credits_used"))


def delta(before: dict[str, Any], after: dict[str, Any]) -> int | float | None:
    b, a = used(before), used(after)
    if b is None or a is None:
        return None
    return a - b


def envelope(raw: dict[str, Any], operation: str) -> dict[str, Any]:
    result = raw.get("result", raw)
    return {"operation": operation, "activity_id": raw.get("activity_id"), "result": sanitize(result)}


def geometry_metrics(result: dict[str, Any]) -> dict[str, Any]:
    features = (result.get("map_data") or {}).get("features", [])
    if not features:
        return {"feature_count": 0}
    coords: list[tuple[float, float]] = []
    for feature in features:
        geometry = feature.get("geometry", {})
        for ring in geometry.get("coordinates", []):
            if geometry.get("type") == "Polygon":
                coords.extend((float(point[0]), float(point[1])) for point in ring)
            elif geometry.get("type") == "MultiPolygon":
                for polygon in ring:
                    coords.extend((float(point[0]), float(point[1])) for point in polygon)
    if not coords:
        return {"feature_count": len(features)}
    lon_values, lat_values = zip(*coords)
    mean_lat = sum(lat_values) / len(lat_values)
    meters_per_degree_lat = 111_320.0
    meters_per_degree_lon = 111_320.0
    import math
    return {
        "feature_count": len(features),
        "lon_span_m": round((max(lon_values) - min(lon_values)) * meters_per_degree_lon * math.cos(math.radians(mean_lat)), 3),
        "lat_span_m": round((max(lat_values) - min(lat_values)) * meters_per_degree_lat, 3),
        "first_feature_property_keys": sorted(features[0].get("properties", {}).keys()),
    }


def main() -> None:
    load_local_env()
    complete = read_json("summary.json")
    if complete:
        print(json.dumps({"reused": True, **complete}, indent=2, sort_keys=True))
        return
    if not os.getenv("FORTYGUARD_API_KEY"):
        raise RuntimeError("FORTYGUARD_API_KEY is not configured")
    client = FortyGuardClient(api_key=os.environ["FORTYGUARD_API_KEY"], base_url=os.getenv("FORTYGUARD_BASE_URL"))

    before_heatmap = usage(client)
    heatmap = read_json("heatmap.json")
    if heatmap is None:
        raw_heatmap = client.create_heatmap(
            polygon_aoi=AOI,
            start_date=DATE,
            filter_type=3,
            granularity=100,
            analytic_type="tcm",
            poll_interval=3.0,
            timeout=600.0,
            verbose=False,
        )
        heatmap = envelope(raw_heatmap, "POST /v1/heatmap")
        write_json("heatmap.json", heatmap)
    after_heatmap = usage(client)
    write_json("usage_before_heatmap.json", before_heatmap)
    write_json("usage_after_heatmap.json", after_heatmap)

    heat_result = heatmap["result"]
    features = (heat_result.get("map_data") or {}).get("features", [])
    max_values = [float(f.get("properties", {}).get("max_temperature")) for f in features if f.get("properties", {}).get("max_temperature") is not None]
    anchor = max(max_values) if max_values else 35.0
    heat_summary = {
        "activity_id": heatmap.get("activity_id"),
        "result_keys": sorted(heat_result.keys()),
        "stats_keys": sorted((heat_result.get("stats_data") or {}).keys()),
        "geometry": geometry_metrics(heat_result),
        "max_temperature_c_observed": max(max_values) if max_values else None,
        "min_temperature_c_observed": min(max_values) if max_values else None,
    }
    write_json("heatmap_schema_summary.json", heat_summary)

    before_env = usage(client)
    env = read_json("env_params.json")
    if env is None:
        raw_env = client.environmental_parameters(
            latitude=LAT,
            longitude=LON,
            temperature=anchor,
            start_date=DATE,
            filter_type=3,
            analysis=["apparent_temperature_celsius", "relative_humidity_percent", "wet_bulb_temperature_celsius"],
            poll_interval=3.0,
            timeout=600.0,
            verbose=False,
        )
        env = envelope(raw_env, "POST /v1/env_params")
        write_json("env_params.json", env)
    after_env = usage(client)
    write_json("usage_before_env_params.json", before_env)
    write_json("usage_after_env_params.json", after_env)
    env_result = env["result"]
    locations = env_result.get("locations", [])
    first_location = locations[0] if locations else {}
    params = first_location.get("parameters", {})
    env_summary = {
        "activity_id": env.get("activity_id"),
        "result_keys": sorted(env_result.keys()),
        "metadata_keys": sorted((env_result.get("metadata") or {}).keys()),
        "location_keys": sorted(first_location.keys()),
        "parameter_keys": sorted(params.keys()),
        "timestamp_count": len((env_result.get("metadata") or {}).get("timestamps", [])),
        "parameter_lengths": {key: len(value) for key, value in params.items() if isinstance(value, list)},
    }
    write_json("env_params_schema_summary.json", env_summary)

    before_premium = usage(client)
    premium = read_json("premium_probe.json")
    if premium is None:
        try:
            activity_id = client.satellite_segmentation(
                latitude=LAT,
                longitude=LON,
                start_date=DATE,
                start_time="14:00",
                filter_type=1,
                granularity=100,
                wait=False,
                verbose=False,
            )
            premium_result = client.wait_for(activity_id, poll_interval=3.0, timeout=600.0)
            premium = {"operation": "POST /v1/satellite", "access": "completed", "activity_id": activity_id, "result": sanitize(premium_result)}
        except Exception as exc:
            premium = {"operation": "POST /v1/satellite", "access": "denied_or_failed", "error_type": type(exc).__name__, "error": sanitize(str(exc)[:240])}
        write_json("premium_probe.json", premium)
    after_premium = usage(client)
    write_json("usage_before_premium.json", before_premium)
    write_json("usage_after_premium.json", after_premium)

    summary = {
        "date": DATE,
        "aoi": AOI,
        "heatmap": {"status": "PASS", "credit_delta": delta(before_heatmap, after_heatmap), "schema": heat_summary},
        "env_params": {"status": "PASS", "credit_delta": delta(before_env, after_env), "schema": env_summary},
        "premium": {"status": premium.get("access"), "credit_delta": delta(before_premium, after_premium), "error_type": premium.get("error_type")},
        "credits_before_total": used(before_heatmap),
        "credits_after_total": used(after_premium),
    }
    write_json("summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
