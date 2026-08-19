"""Run a small, idempotent live geography matrix using heatmap + satellite.

Each site is a deliberately chosen U.S. urban/industrial form. Successful
responses are cached in .agent_cache/live_geographies and the output retains
the exact request, sanitized result, and measured credit delta. Re-running
this script never repeats a cached successful request.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))
from fortyguard import FortyGuardClient  # type: ignore[import-not-found]


RUN_DIR = ROOT / ".agent_cache" / "live_geographies"
DATE = "2025-07-15"
HALF = 0.00045

SITES: list[dict[str, Any]] = [
    {"slug": "phoenix_paved_industrial", "city": "Phoenix", "lat": 33.434, "lon": -112.018, "rationale": "hot, paved industrial/warehouse form; test whether hardscape produces a clear thermal and surface signal"},
    {"slug": "las_vegas_dense_paved", "city": "Las Vegas", "lat": 36.171, "lon": -115.128, "rationale": "very dry dense urban form; test high hardscape with little vegetation"},
    {"slug": "houston_ship_channel", "city": "Houston", "lat": 29.735, "lon": -95.286, "rationale": "industrial corridor with water, roads, buildings, and exposed yard surfaces"},
    {"slug": "dfw_logistics", "city": "Dallas-Fort Worth", "lat": 32.899, "lon": -97.040, "rationale": "large logistics/airport-adjacent form; test warehouse and apron-like surfaces"},
    {"slug": "atlanta_airport", "city": "Atlanta", "lat": 33.640, "lon": -84.444, "rationale": "airport operations with paved movement areas and humid vegetation contrast"},
    {"slug": "los_angeles_airport", "city": "Los Angeles", "lat": 33.946, "lon": -118.401, "rationale": "dense airport/industrial environment; test operationally relevant pavement heat"},
    {"slug": "new_york_dense_built", "city": "New York", "lat": 40.751, "lon": -73.990, "rationale": "dense built environment; test whether a compact urban canyon differs from industrial sites"},
    {"slug": "portland_green_industrial", "city": "Portland", "lat": 45.560, "lon": -122.670, "rationale": "greener industrial city; test vegetation/building contrast against paved sites"},
]


def load_env() -> None:
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            key, value = raw.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


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


def credit_summary(body: dict[str, Any]) -> dict[str, Any]:
    return body.get("credit_summary", {})


def credit_delta(before: dict[str, Any], after: dict[str, Any]) -> int | float | None:
    b = credit_summary(before).get("cycle_credits_used")
    a = credit_summary(after).get("cycle_credits_used")
    return a - b if b is not None and a is not None else None


def aoi(lat: float, lon: float) -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": [{
        "type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[
            [lon - HALF, lat - HALF], [lon + HALF, lat - HALF],
            [lon + HALF, lat + HALF], [lon - HALF, lat + HALF],
            [lon - HALF, lat - HALF],
        ]]},
    }]}


def segment_summary(result: dict[str, Any]) -> dict[str, Any]:
    segmentation = result.get("segmentation") or {}
    segments = segmentation.get("segments") or {}
    return {
        "image_year": result.get("image_year"),
        "segment_keys": sorted(segments.keys()) if isinstance(segments, dict) else [],
        "segments": segments,
        "image_dimensions": segmentation.get("image_dimensions"),
        "mode": segmentation.get("mode"),
    }


def heat_summary(result: dict[str, Any]) -> dict[str, Any]:
    features = (result.get("map_data") or {}).get("features", [])
    props = [f.get("properties", {}) for f in features]
    def numbers(key: str) -> list[float]:
        return [float(p[key]) for p in props if p.get(key) is not None]
    summary: dict[str, Any] = {
        "feature_count": len(features),
        "property_keys": sorted(props[0].keys()) if props else [],
    }
    for key in ("average_temperature", "max_temperature", "min_temperature"):
        values = numbers(key)
        if values:
            summary[f"{key}_range_c"] = [round(min(values), 4), round(max(values), 4)]
            summary[f"{key}_mean_c"] = round(sum(values) / len(values), 4)
    stats = result.get("stats_data") or {}
    summary["stats_keys"] = sorted(stats.keys())
    return summary


def site_path(slug: str) -> Path:
    return RUN_DIR / f"{slug}.json"


def main() -> None:
    load_env()
    if not os.getenv("FORTYGUARD_API_KEY"):
        raise RuntimeError("FORTYGUARD_API_KEY is not configured")
    client = FortyGuardClient(api_key=os.environ["FORTYGUARD_API_KEY"], base_url=os.getenv("FORTYGUARD_BASE_URL"))
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for site in SITES:
        path = site_path(site["slug"])
        if path.exists():
            results.append(json.loads(path.read_text(encoding="utf-8")))
            continue
        polygon = aoi(site["lat"], site["lon"])
        before_heat = usage(client)
        heat_raw = client.create_heatmap(
            polygon_aoi=polygon, start_date=DATE, filter_type=3, granularity=100,
            analytic_type="tcm", poll_interval=3.0, timeout=600.0, verbose=False,
        )
        after_heat = usage(client)
        heat_result = heat_raw.get("result", heat_raw)
        before_satellite = usage(client)
        sat_error: dict[str, Any] | None = None
        try:
            activity_id = client.satellite_segmentation(
                latitude=site["lat"], longitude=site["lon"], start_date=DATE,
                start_time="14:00", filter_type=1, granularity=100,
                wait=False, verbose=False,
            )
            sat_raw = client.wait_for(activity_id, poll_interval=3.0, timeout=600.0)
            sat_result = sat_raw.get("result", sat_raw) if isinstance(sat_raw, dict) else sat_raw
            sat_status = "PASS"
        except Exception as exc:
            sat_result = {}
            sat_status = "FAIL"
            sat_error = {"error_type": type(exc).__name__, "error": str(exc)[:240]}
        after_satellite = usage(client)
        record = {
            "site": site,
            "request": {"date": DATE, "filter_type": 3, "granularity": 100, "analytic_type": "tcm", "aoi": polygon, "satellite_start_time": "14:00"},
            "heatmap": {"status": "PASS", "activity_id": heat_raw.get("activity_id"), "credit_delta": credit_delta(before_heat, after_heat), "summary": heat_summary(heat_result), "result": sanitize(heat_result)},
            "satellite": {"status": sat_status, "credit_delta": credit_delta(before_satellite, after_satellite), "summary": segment_summary(sat_result), "error": sat_error, "result": sanitize(sat_result)},
            "usage_after": credit_summary(after_satellite),
        }
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        results.append(record)
    output = []
    for record in results:
        output.append({
            "slug": record["site"]["slug"], "city": record["site"]["city"],
            "heatmap": record["heatmap"]["summary"], "heatmap_credits": record["heatmap"]["credit_delta"],
            "satellite": record["satellite"]["summary"], "satellite_status": record["satellite"]["status"],
            "satellite_credits": record["satellite"]["credit_delta"],
        })
    (RUN_DIR / "summary.json").write_text(json.dumps({"date": DATE, "sites": output}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
