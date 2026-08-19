"""One idempotent live multi-tile tcm check for spatial differentiation."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))
from fortyguard import FortyGuardClient  # type: ignore[import-not-found]

RUN_DIR = ROOT / ".agent_cache" / "live_validation"
OUT = RUN_DIR / "heatmap_multitile_tcm.json"
DATE = "2025-07-15"
AOI = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[
            [-121.890, 37.313], [-121.880, 37.313], [-121.880, 37.323], [-121.890, 37.323], [-121.890, 37.313]
        ]]},
    }],
}


def load_env() -> None:
    import os
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            key, value = raw.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    load_env()
    if OUT.exists():
        d = json.loads(OUT.read_text(encoding="utf-8"))
        print(json.dumps({"activity_id": d["activity_id"], "summary": d["summary"], "credits": d["credits"]}, indent=2, sort_keys=True))
        return
    import os
    client = FortyGuardClient(api_key=os.environ["FORTYGUARD_API_KEY"], base_url=os.getenv("FORTYGUARD_BASE_URL"))
    before_body = client.fetch_api_key_usage()
    before = before_body.get("credit_summary", {})
    raw = client.create_heatmap(polygon_aoi=AOI, start_date=DATE, filter_type=3, granularity=100, analytic_type="tcm", poll_interval=3.0, timeout=600.0, verbose=False)
    after_body = client.fetch_api_key_usage()
    after = after_body.get("credit_summary", {})
    result = raw.get("result", raw)
    features = (result.get("map_data") or {}).get("features", [])
    def values(field: str) -> list[float]:
        return [float(f.get("properties", {}).get(field)) for f in features if f.get("properties", {}).get(field) is not None]
    maxima, averages, minima = values("max_temperature"), values("average_temperature"), values("min_temperature")
    safe = {
        "operation": "POST /v1/heatmap",
        "activity_id": raw.get("activity_id"),
        "request": {"date": DATE, "filter_type": 3, "granularity": 100, "analytic_type": "tcm", "aoi": AOI},
        "result": result,
        "credits": {"before_used": before.get("cycle_credits_used"), "after_used": after.get("cycle_credits_used"), "delta": (after.get("cycle_credits_used") - before.get("cycle_credits_used")) if before.get("cycle_credits_used") is not None and after.get("cycle_credits_used") is not None else None, "after_remaining": after.get("cycle_remaining_credits")},
        "summary": {"feature_count": len(features), "max_temperature_range_c": [min(maxima), max(maxima)] if maxima else [], "average_temperature_range_c": [min(averages), max(averages)] if averages else [], "min_temperature_range_c": [min(minima), max(minima)] if minima else [], "unique_max_count": len(set(maxima)), "unique_average_count": len(set(averages)), "first_feature_property_keys": sorted(features[0].get("properties", {}).keys()) if features else []},
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(safe, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"activity_id": safe["activity_id"], "summary": safe["summary"], "credits": safe["credits"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
