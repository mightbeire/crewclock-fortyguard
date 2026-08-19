"""One idempotent live heatmap exceedance validation over a small multi-tile AOI."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))
from fortyguard import FortyGuardClient  # type: ignore[import-not-found]


RUN_DIR = ROOT / ".agent_cache" / "live_validation"
OUT = RUN_DIR / "heatmap_exceedance.json"
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
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            key, value = raw.split("=", 1)
            import os
            os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    load_env()
    if OUT.exists():
        print(OUT.read_text(encoding="utf-8"))
        return
    import os
    client = FortyGuardClient(api_key=os.environ["FORTYGUARD_API_KEY"], base_url=os.getenv("FORTYGUARD_BASE_URL"))
    before_body = client.fetch_api_key_usage()
    before = before_body.get("credit_summary", {})
    raw = client.create_heatmap(
        polygon_aoi=AOI,
        start_date=DATE,
        filter_type=3,
        granularity=100,
        analytic_type="exceedance",
        threshold=32.0,
        direction="above",
        poll_interval=3.0,
        timeout=600.0,
        verbose=False,
    )
    result = raw.get("result", raw)
    after_body = client.fetch_api_key_usage()
    after = after_body.get("credit_summary", {})
    features = (result.get("map_data") or {}).get("features", [])
    values = [float(f.get("properties", {}).get("value")) for f in features if f.get("properties", {}).get("value") is not None]
    safe = {
        "operation": "POST /v1/heatmap",
        "activity_id": raw.get("activity_id"),
        "request": {"date": DATE, "filter_type": 3, "granularity": 100, "analytic_type": "exceedance", "threshold_c": 32.0, "direction": "above", "aoi": AOI},
        "result": result,
        "credits": {
            "before_used": before.get("cycle_credits_used"),
            "after_used": after.get("cycle_credits_used"),
            "delta": (after.get("cycle_credits_used") - before.get("cycle_credits_used")) if before.get("cycle_credits_used") is not None and after.get("cycle_credits_used") is not None else None,
            "before_remaining": before.get("cycle_remaining_credits"),
            "after_remaining": after.get("cycle_remaining_credits"),
        },
        "summary": {
            "feature_count": len(features),
            "value_min_hours": min(values) if values else None,
            "value_max_hours": max(values) if values else None,
            "value_mean_hours": sum(values) / len(values) if values else None,
            "unique_value_count": len(set(values)),
            "stats_keys": sorted((result.get("stats_data") or {}).keys()),
            "first_feature_property_keys": sorted(features[0].get("properties", {}).keys()) if features else [],
        },
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(safe, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"activity_id": safe["activity_id"], "summary": safe["summary"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
