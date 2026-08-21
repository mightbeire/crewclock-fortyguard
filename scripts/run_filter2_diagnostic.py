from __future__ import annotations

"""Run one bounded, historical filter_type=2 FortyGuard diagnostic.

The forensic runbook requires the exact request and every returned status
envelope to be retained.  This script deliberately uses the bundled client
session for transport, but captures sanitized envelopes around it so a
terminal failure is diagnosable without storing the API key.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "temperature-api-quickstart"))

from fortyguard import FortyGuardClient  # type: ignore[import-not-found]


DATE = "2025-07-15"
START_TIME = "06:00"
END_TIME = "08:00"
GRANULARITY = 100
THRESHOLD_C = 32.0
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
OUT_DIR = ROOT / "evidence" / "crewclock-canonical-exceedance"


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
    lowered = key.lower()
    if any(token in lowered for token in ("api_key", "token", "secret", "password", "credential")):
        return "REDACTED"
    if isinstance(value, dict):
        return {str(k): sanitize(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(item, key) for item in value]
    if isinstance(value, str) and ("fg_live_" in value or "sk-" in value):
        return "REDACTED"
    return value


def sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def usage(client: FortyGuardClient) -> dict[str, Any]:
    body = client.fetch_api_key_usage()
    summary = body.get("credit_summary", {}) if isinstance(body, dict) else {}
    return sanitize({
        "cycle_credits_used": summary.get("cycle_credits_used"),
        "cycle_remaining_credits": summary.get("cycle_remaining_credits"),
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analytic-type", choices=("tcm", "exceedance"), required=True)
    parser.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args()

    load_env()
    if not os.getenv("FORTYGUARD_API_KEY"):
        raise RuntimeError("fortyguard_api_key_not_configured")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUT_DIR / f"diagnostic_filter2_{args.analytic_type}_06_00_08_00.json"
    if output.is_file():
        print(json.dumps({"status": "CACHED", "path": str(output.relative_to(ROOT))}))
        return 0

    client = FortyGuardClient(
        api_key=os.environ["FORTYGUARD_API_KEY"],
        base_url=os.getenv("FORTYGUARD_BASE_URL"),
    )
    date_time = {
        "start_date": DATE,
        "start_time": START_TIME,
        "end_time": END_TIME,
        "filter_type": 2,
    }
    payload: dict[str, Any] = {
        "polygon_aoi": AOI,
        "date_time": date_time,
        "granularity": GRANULARITY,
        "analytic_type": args.analytic_type,
    }
    if args.analytic_type == "exceedance":
        payload["threshold"] = THRESHOLD_C
        payload["direction"] = "above"

    record: dict[str, Any] = {
        "status": "STARTED",
        "provenance": "LIVE_FORTYGUARD_DIAGNOSTIC",
        "operation": "POST /v1/heatmap",
        "request": payload,
        "request_sha256": sha256(payload),
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "status_responses": [],
    }
    before = usage(client)
    record["credits_before"] = before

    post_url = f"{client.base_url}/v1/heatmap"
    post = client._session.post(post_url, json=payload, timeout=client.timeout)
    try:
        post_body = post.json()
    except ValueError:
        post_body = {"text": post.text[:2000]}
    record["submit_response"] = sanitize({
        "http_status": post.status_code,
        "body": post_body,
    })
    if not post.ok:
        record["status"] = "SUBMIT_FAILED"
        record["failure_message"] = f"POST /v1/heatmap -> HTTP {post.status_code}"
        record["credits_after"] = usage(client)
        output.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({"status": record["status"], "path": str(output.relative_to(ROOT))}))
        return 1

    activity_id = ((post_body.get("data") or {}).get("activity_id") if isinstance(post_body, dict) else None)
    if not isinstance(activity_id, str) or not activity_id:
        record["status"] = "SUBMIT_SHAPE_FAILED"
        record["failure_message"] = "submit response did not contain data.activity_id"
        record["credits_after"] = usage(client)
        output.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({"status": record["status"], "path": str(output.relative_to(ROOT))}))
        return 1
    record["activity_id"] = activity_id

    deadline = time.monotonic() + args.timeout
    while True:
        status_response: dict[str, Any] = {"retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
        response = client._session.get(f"{client.base_url}/v1/status/{activity_id}", timeout=client.timeout)
        try:
            body = response.json()
        except ValueError:
            body = {"text": response.text[:2000]}
        status_response.update({"http_status": response.status_code, "body": sanitize(body)})
        record["status_responses"].append(status_response)
        data = body.get("data", {}) if isinstance(body, dict) else {}
        status = str(data.get("status", "")).lower() if isinstance(data, dict) else ""
        if status in {"completed", "succeeded"}:
            record["status"] = "COMPLETED"
            record["result"] = sanitize(data.get("result"))
            break
        if status in {"failed", "error"}:
            record["status"] = "FAILED"
            record["failure_message"] = sanitize(data.get("message") or data.get("error") or body)
            break
        if time.monotonic() >= deadline:
            record["status"] = "TIMEOUT"
            record["failure_message"] = f"activity remained {status or 'unknown'} for {args.timeout:.0f}s"
            break
        time.sleep(3.0)

    record["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    record["credits_after"] = usage(client)
    output.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": record["status"],
        "activity_id": activity_id,
        "path": str(output.relative_to(ROOT)),
        "status_polls": len(record["status_responses"]),
    }))
    return 0 if record["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
