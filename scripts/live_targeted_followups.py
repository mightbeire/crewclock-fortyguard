"""Idempotent follow-up probes for the strongest live geographies.

Uses only new request payloads: three hourly environmental profiles and two
multi-day Phoenix analysis maps. Successful responses are retained in the
ignored live cache.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))
from fortyguard import FortyGuardClient  # type: ignore[import-not-found]

RUN_DIR = ROOT / ".agent_cache" / "live_followups"
DATE = "2025-07-15"
ENV_SITES = {
    "phoenix": (33.434, -112.018, 40.1505),
    "las_vegas": (36.171, -115.128, 41.31),
    "atlanta": (33.640, -84.444, 36.3),
}


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


def delta(before: dict[str, Any], after: dict[str, Any]) -> int | float | None:
    b = before.get("credit_summary", {}).get("cycle_credits_used")
    a = after.get("credit_summary", {}).get("cycle_credits_used")
    return a - b if b is not None and a is not None else None


def phoenix_aoi() -> dict[str, Any]:
    lat, lon = ENV_SITES["phoenix"][:2]
    half = 0.005
    return {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[
        [lon - half, lat - half], [lon + half, lat - half], [lon + half, lat + half], [lon - half, lat + half], [lon - half, lat - half]
    ]]}}]}


def summarize_env(result: dict[str, Any]) -> dict[str, Any]:
    metadata = result.get("metadata") or {}
    location = (result.get("locations") or [{}])[0]
    params = location.get("parameters") or {}
    summary: dict[str, Any] = {"timestamp_count": len(metadata.get("timestamps", [])), "parameter_keys": sorted(params.keys())}
    for key in ("apparent_temperature_celsius", "heat_index_celsius", "wet_bulb_temperature_celsius", "relative_humidity_percent", "solar_irradiance"):
        values = params.get(key) if key != "solar_irradiance" else location.get("solar_irradiance")
        if isinstance(values, list) and values:
            numeric = [float(x) for x in values if isinstance(x, (int, float))]
            if numeric:
                summary[key] = {"min": min(numeric), "max": max(numeric), "mean": round(sum(numeric) / len(numeric), 4), "count": len(numeric)}
    return summary


def summarize_analysis(result: dict[str, Any]) -> dict[str, Any]:
    features = (result.get("map_data") or {}).get("features", [])
    values = [float(f.get("properties", {}).get("value")) for f in features if f.get("properties", {}).get("value") is not None]
    stats = result.get("stats_data") or {}
    return {"feature_count": len(features), "value_range": [min(values), max(values)] if values else [], "unique_value_count": len(set(values)), "stats": {k: stats.get(k) for k in ("analytic_type", "units", "n_cells", "min", "max", "mean") if k in stats}}


def run_once(client: FortyGuardClient, name: str, call: Any, summary_fn: Any, request: dict[str, Any]) -> dict[str, Any]:
    path = RUN_DIR / f"{name}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    before = usage(client)
    raw = call()
    after = usage(client)
    result = raw.get("result", raw) if isinstance(raw, dict) else raw
    record = {"name": name, "request": request, "activity_id": raw.get("activity_id") if isinstance(raw, dict) else None, "credit_delta": delta(before, after), "summary": summary_fn(result), "result": sanitize(result), "usage_after": after.get("credit_summary", {})}
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return record


def main() -> None:
    load_env()
    client = FortyGuardClient(api_key=os.environ["FORTYGUARD_API_KEY"], base_url=os.getenv("FORTYGUARD_BASE_URL"))
    records: list[dict[str, Any]] = []
    for name, (lat, lon, anchor) in ENV_SITES.items():
        records.append(run_once(
            client, f"env_{name}",
            lambda lat=lat, lon=lon, anchor=anchor: client.environmental_parameters(
                latitude=lat, longitude=lon, temperature=anchor, start_date=DATE, filter_type=3,
                analysis=["apparent_temperature_celsius", "heat_index_celsius", "wet_bulb_temperature_celsius", "relative_humidity_percent"],
                poll_interval=3.0, timeout=600.0, verbose=False,
            ), summarize_env,
            {"endpoint": "/v1/env_params", "lat": lat, "lon": lon, "date": DATE, "filter_type": 3},
        ))
    polygon = phoenix_aoi()
    for analytic_type, extra in (("time_of_measure", {}), ("persistence", {"threshold": 38.0, "direction": "above"})):
        records.append(run_once(
            client, f"phoenix_{analytic_type}",
            lambda analytic_type=analytic_type, extra=extra: client.create_heatmap(
                polygon_aoi=polygon, start_date=DATE, end_date="2025-07-21", filter_type=4,
                granularity=100, analytic_type=analytic_type, **extra,
                poll_interval=3.0, timeout=600.0, verbose=False,
            ), summarize_analysis,
            {"endpoint": "/v1/heatmap", "date": DATE, "end_date": "2025-07-21", "filter_type": 4, "granularity": 100, "analytic_type": analytic_type, **extra},
        ))
    print(json.dumps([{k: record[k] for k in ("name", "credit_delta", "summary")} for record in records], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
