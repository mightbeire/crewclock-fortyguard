from __future__ import annotations

"""Run the two preselected historical Phoenix request-time calibration calls."""

from argparse import ArgumentParser
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))
from fortyguard import FortyGuardClient  # type: ignore[import-not-found]

DATE = "2025-07-15"
GRANULARITY = 100
CALIBRATION_TIMES = ("14:00", "22:00")  # selected before either response
EXPECTED_COST = 4220
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
    "north": [(-112.01840, 33.43400), (-112.01800, 33.43400), (-112.01800, 33.43440), (-112.01840, 33.43440)],
    "south": [(-112.01840, 33.43360), (-112.01800, 33.43360), (-112.01800, 33.43400), (-112.01840, 33.43400)],
    "laydown": [(-112.01795, 33.43360), (-112.01760, 33.43360), (-112.01760, 33.43395), (-112.01795, 33.43395)],
    "access": [(-112.01795, 33.43405), (-112.01760, 33.43405), (-112.01760, 33.43440), (-112.01795, 33.43440)],
}
OUT_DIR = ROOT / "evidence" / "crewclock-request-time-calibration"


def load_env() -> None:
    path = ROOT / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def sanitize(value: Any, key: str = "") -> Any:
    if any(token in key.lower() for token in ("api_key", "token", "secret", "password", "credential")):
        return "REDACTED"
    if isinstance(value, dict):
        return {str(k): sanitize(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(item, key) for item in value]
    if isinstance(value, str) and ("fg_live_" in value or "sk-" in value):
        return "REDACTED"
    return value


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def usage(client: FortyGuardClient) -> dict[str, Any]:
    body = client.fetch_api_key_usage()
    summary = body.get("credit_summary", {}) if isinstance(body, dict) else {}
    return sanitize({
        "cycle_credits_used": summary.get("cycle_credits_used"),
        "cycle_remaining_credits": summary.get("cycle_remaining_credits"),
    })


def polygon_area(points: list[tuple[float, float]]) -> float:
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))) / 2


def clip_polygon(subject: list[tuple[float, float]], edge_a: tuple[float, float], edge_b: tuple[float, float]) -> list[tuple[float, float]]:
    """Clip a convex polygon against one directed edge."""
    if not subject:
        return []
    ax, ay = edge_a
    bx, by = edge_b

    def inside(point: tuple[float, float]) -> bool:
        return (bx - ax) * (point[1] - ay) - (by - ay) * (point[0] - ax) >= -1e-12

    def intersection(start: tuple[float, float], end: tuple[float, float]) -> tuple[float, float]:
        dx, dy = end[0] - start[0], end[1] - start[1]
        ex, ey = bx - ax, by - ay
        denominator = dx * ey - dy * ex
        if abs(denominator) < 1e-15:
            return end
        t = ((ax - start[0]) * ey - (ay - start[1]) * ex) / denominator
        return (start[0] + t * dx, start[1] + t * dy)

    output: list[tuple[float, float]] = []
    previous = subject[-1]
    for current in subject:
        current_inside, previous_inside = inside(current), inside(previous)
        if current_inside:
            if not previous_inside:
                output.append(intersection(previous, current))
            output.append(current)
        elif previous_inside:
            output.append(intersection(previous, current))
        previous = current
    return output


def intersection_area(first: list[tuple[float, float]], second: list[tuple[float, float]]) -> float:
    clipped = first
    # Workface and returned tile rings are convex and consistently wound.
    for a, b in zip(second, second[1:] + second[:1]):
        clipped = clip_polygon(clipped, a, b)
    return polygon_area(clipped) if clipped else 0.0


def temperature(properties: dict[str, Any]) -> float | None:
    for key in ("average_temperature", "temperature", "temperature_c"):
        value = properties.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
            return float(value)
    return None


def workface_summary(features: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name, face in WORKFACES.items():
        face_area = polygon_area(face)
        covered_area = 0.0
        weighted = 0.0
        for feature in features:
            geometry = feature.get("geometry", {})
            ring = geometry.get("coordinates", [[]])[0] if isinstance(geometry, dict) else []
            props = feature.get("properties", {})
            if not isinstance(ring, list) or not isinstance(props, dict):
                continue
            tile = [(float(pair[0]), float(pair[1])) for pair in ring]
            value = temperature(props)
            if value is None:
                continue
            overlap = intersection_area(face, tile)
            covered_area += overlap
            weighted += overlap * value
        ratio = min(1.0, covered_area / face_area) if face_area else 0.0
        output[name] = {
            "coverage_ratio": round(ratio, 6),
            "status": "COMPLETE" if ratio >= 1 - 1e-6 else ("PARTIAL" if ratio > 0 else "NONE"),
            "area_weighted_temperature_c_over_covered_area": round(weighted / covered_area, 6) if covered_area else None,
        }
    return output


def summarize_result(result: Any) -> dict[str, Any]:
    if not isinstance(result, dict):
        return {"valid": False, "reason": "result_not_object", "cell_count": 0}
    map_data = result.get("map_data")
    features = map_data.get("features", []) if isinstance(map_data, dict) else []
    valid = isinstance(features, list) and bool(features)
    values = [temperature(f.get("properties", {})) for f in features if isinstance(f, dict) and isinstance(f.get("properties"), dict)]
    values = [value for value in values if value is not None]
    stats = result.get("stats_data", {})
    stats_mean = stats.get("temperature_stats", {}).get("mean") if isinstance(stats, dict) and isinstance(stats.get("temperature_stats"), dict) else None
    if not isinstance(stats_mean, (int, float)):
        stats_mean = sum(values) / len(values) if values else None
    return {
        "valid": valid and bool(values),
        "schema": "TCM",
        "cell_count": len(features) if isinstance(features, list) else 0,
        "provider_n_cells": stats.get("n_cells") if isinstance(stats, dict) else None,
        "aoi_mean_c": round(float(stats_mean), 6) if isinstance(stats_mean, (int, float)) else None,
        "aoi_min_c": min(values) if values else None,
        "aoi_max_c": max(values) if values else None,
        "workfaces": workface_summary(features if isinstance(features, list) else []),
    }


def run_one(client: FortyGuardClient, request_clock: str, timeout: float) -> dict[str, Any]:
    payload = {
        "polygon_aoi": AOI,
        "date_time": {"start_date": DATE, "start_time": request_clock, "filter_type": 1},
        "granularity": GRANULARITY,
        "analytic_type": "tcm",
    }
    output = {
        "request_clock": request_clock,
        "request": payload,
        "request_sha256": digest(payload),
        "provenance": "LIVE_FORTYGUARD_CALIBRATION",
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "status_responses": [],
    }
    before = usage(client)
    output["credits_before"] = before
    response = client._session.post(f"{client.base_url}/v1/heatmap", json=payload, timeout=client.timeout)
    try:
        body = response.json()
    except ValueError:
        body = {"text": response.text[:2000]}
    output["submit_response"] = sanitize({"http_status": response.status_code, "body": body})
    if not response.ok:
        output.update({"status": "SUBMIT_FAILED", "failure": f"HTTP {response.status_code}"})
    else:
        activity_id = ((body.get("data") or {}).get("activity_id") if isinstance(body, dict) else None)
        output["activity_id"] = activity_id
        if not isinstance(activity_id, str) or not activity_id:
            output.update({"status": "SUBMIT_SHAPE_FAILED", "failure": "missing_activity_id"})
        else:
            deadline = time.monotonic() + timeout
            while True:
                status_response: dict[str, Any] = {"retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
                status_http = client._session.get(f"{client.base_url}/v1/status/{activity_id}", timeout=client.timeout)
                try:
                    status_body = status_http.json()
                except ValueError:
                    status_body = {"text": status_http.text[:2000]}
                status_response.update({"http_status": status_http.status_code, "body": sanitize(status_body)})
                output["status_responses"].append(status_response)
                data = status_body.get("data", {}) if isinstance(status_body, dict) else {}
                status = str(data.get("status", "")).lower() if isinstance(data, dict) else ""
                if status in {"completed", "succeeded"}:
                    result = data.get("result")
                    output["status"] = "COMPLETED"
                    output["result"] = sanitize(result)
                    output["result_sha256"] = digest(result)
                    output["summary"] = summarize_result(result)
                    break
                if status in {"failed", "error"}:
                    output.update({"status": "FAILED", "failure": sanitize(data.get("message") or data.get("error") or status_body)})
                    break
                if time.monotonic() >= deadline:
                    output.update({"status": "TIMEOUT", "failure": f"status remained {status or 'unknown'}"})
                    break
                time.sleep(3.0)
    output["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    output["credits_after"] = usage(client)
    return output


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args()
    load_env()
    if not os.getenv("FORTYGUARD_API_KEY"):
        raise RuntimeError("fortyguard_api_key_not_configured")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = FortyGuardClient(api_key=os.environ["FORTYGUARD_API_KEY"], base_url=os.getenv("FORTYGUARD_BASE_URL"))
    records = []
    for request_clock in CALIBRATION_TIMES:
        path = OUT_DIR / f"phoenix_{DATE}_{request_clock.replace(':', '')}.json"
        if path.is_file():
            record = json.loads(path.read_text(encoding="utf-8"))
        else:
            record = run_one(client, request_clock, args.timeout)
            path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        records.append(record)
        print(json.dumps({"request_clock": request_clock, "status": record.get("status"), "activity_id": record.get("activity_id"), "summary": record.get("summary")}, separators=(",", ":")))
    manifest = {
        "status": "COMPLETE" if all(record.get("status") == "COMPLETED" and record.get("summary", {}).get("valid") for record in records) else "PARTIAL",
        "historical_date": DATE,
        "selected_request_clocks_before_responses": list(CALIBRATION_TIMES),
        "filter_type": 1,
        "analytic_type": "tcm",
        "granularity_m": GRANULARITY,
        "aoi": AOI,
        "expected_cost_per_call": EXPECTED_COST,
        "records": [{"request_clock": r.get("request_clock"), "activity_id": r.get("activity_id"), "status": r.get("status"), "request_sha256": r.get("request_sha256"), "result_sha256": r.get("result_sha256"), "summary": r.get("summary")} for r in records],
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return 0 if manifest["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
