"""Idempotent LA airport/rail-context heatmap follow-up."""

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
LAT, LON = 33.946, -118.401


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


def polygon() -> dict[str, Any]:
    half = 0.005
    return {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[
        [LON - half, LAT - half], [LON + half, LAT - half], [LON + half, LAT + half], [LON - half, LAT + half], [LON - half, LAT - half]
    ]]}}]}


def summary(result: dict[str, Any]) -> dict[str, Any]:
    features = (result.get("map_data") or {}).get("features", [])
    values = [float(f.get("properties", {}).get("value")) for f in features if f.get("properties", {}).get("value") is not None]
    stats = result.get("stats_data") or {}
    return {"feature_count": len(features), "value_range": [min(values), max(values)] if values else [], "unique_value_count": len(set(values)), "stats": {k: stats.get(k) for k in ("analytic_type", "units", "n_cells", "min", "max", "mean") if k in stats}}


def run(client: FortyGuardClient, name: str, analytic_type: str, extra: dict[str, Any]) -> dict[str, Any]:
    path = RUN_DIR / f"la_{name}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    before = usage(client)
    raw = client.create_heatmap(
        polygon_aoi=polygon(), start_date=DATE, end_date="2025-07-21", filter_type=4,
        granularity=100, analytic_type=analytic_type, **extra,
        poll_interval=3.0, timeout=600.0, verbose=False,
    )
    after = usage(client)
    result = raw.get("result", raw)
    record = {"request": {"date": DATE, "end_date": "2025-07-21", "filter_type": 4, "granularity": 100, "analytic_type": analytic_type, **extra}, "activity_id": raw.get("activity_id"), "credit_delta": delta(before, after), "summary": summary(result), "result": sanitize(result), "usage_after": after.get("credit_summary", {})}
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return record


def main() -> None:
    load_env()
    client = FortyGuardClient(api_key=os.environ["FORTYGUARD_API_KEY"], base_url=os.getenv("FORTYGUARD_BASE_URL"))
    records = [run(client, "time_of_measure", "time_of_measure", {}), run(client, "persistence", "persistence", {"threshold": 23.0, "direction": "above"})]
    print(json.dumps([{k: r[k] for k in ("credit_delta", "summary")} for r in records], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
