from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from .cache import JsonCache, request_hash
from .models import Provenance, ToolResult


class FortyGuardToolkit:
    """Safe adapter around the vendored FortyGuard client plus derived tools.

    Live calls are opt-in: callers must pass a client. Offline fixtures are
    explicit and always carry ``sample`` provenance.
    """

    def __init__(self, client: Any | None = None, cache: JsonCache | None = None) -> None:
        self.client = client
        self.cache = cache or JsonCache()

    def _cached_or_live(self, endpoint: str, payload: dict[str, Any], call: Any) -> ToolResult:
        key = request_hash(endpoint, payload)
        cached = self.cache.get(key)
        if cached is not None:
            return ToolResult(
                data=cached["data"],
                provenance=Provenance(source="cached", endpoint=endpoint, request_hash=key, assumptions=tuple(cached.get("assumptions", []))),
                estimated_credits=0,
            )
        if self.client is None:
            return ToolResult(
                data={},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key),
                error="live_client_not_configured",
            )
        try:
            raw = call()
            result = raw.get("result", raw) if isinstance(raw, dict) else raw
            envelope = {"data": result, "assumptions": []}
            self.cache.put(key, envelope)
            activity_id = raw.get("activity_id") if isinstance(raw, dict) else None
            return ToolResult(
                data=result,
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key, activity_id=activity_id),
                estimated_credits=1,
            )
        except Exception as exc:  # adapter boundary: expose a traceable error, never a secret
            return ToolResult(
                data={},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key),
                error=f"{type(exc).__name__}: {str(exc)[:240]}",
            )

    def get_heatmap(self, arguments: dict[str, Any]) -> ToolResult:
        payload = dict(arguments)
        fixture = payload.pop("fixture", None)
        if fixture:
            return self.load_fixture(fixture, endpoint="/v1/heatmap")
        if self.client is None:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/heatmap"), error="live_client_not_configured")
        return self._cached_or_live("/v1/heatmap", payload, lambda: self.client.create_heatmap(**payload, verbose=False))

    def get_environmental_parameters(self, arguments: dict[str, Any]) -> ToolResult:
        payload = dict(arguments)
        fixture = payload.pop("fixture", None)
        if fixture:
            return self.load_fixture(fixture, endpoint="/v1/env_params")
        return self._cached_or_live("/v1/env_params", payload, lambda: self.client.environmental_parameters(**payload, verbose=False))

    def get_activity_status(self, arguments: dict[str, Any]) -> ToolResult:
        activity_id = str(arguments["activity_id"])
        if self.client is None:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/status/{activity_id}"), error="live_client_not_configured")
        try:
            return ToolResult(self.client.get_status(activity_id), Provenance(source="live", endpoint="/v1/status/{activity_id}", activity_id=activity_id))
        except Exception as exc:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/status/{activity_id}", activity_id=activity_id), error=f"{type(exc).__name__}: {str(exc)[:240]}")

    def inspect_api_usage(self, arguments: dict[str, Any] | None = None) -> ToolResult:
        if self.client is None:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/system/fetch-api-key-usage"), error="live_client_not_configured")
        try:
            body = self.client.fetch_api_key_usage()
            # Keep account identifiers out of traces while preserving credit facts.
            safe = {k: v for k, v in body.items() if k not in {"api_key", "api_key_details", "subscription_id"}}
            return ToolResult(safe, Provenance(source="live", endpoint="/v1/system/fetch-api-key-usage"))
        except Exception as exc:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/system/fetch-api-key-usage"), error=f"{type(exc).__name__}: {str(exc)[:240]}")

    def load_fixture(self, path: str | Path, *, endpoint: str, assumptions: Iterable[str] = ()) -> ToolResult:
        path = Path(path)
        if not path.exists():
            return ToolResult({}, Provenance(source="sample", endpoint=endpoint, assumptions=tuple(assumptions)), error=f"fixture_not_found:{path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ToolResult(data, Provenance(source="sample", endpoint=endpoint, assumptions=tuple(assumptions)))
        except Exception as exc:
            return ToolResult({}, Provenance(source="sample", endpoint=endpoint), error=f"fixture_invalid:{type(exc).__name__}")

    @staticmethod
    def summarize_heat_profile(arguments: dict[str, Any]) -> ToolResult:
        """Derived summary; it never pretends to be a FortyGuard measurement."""
        profile = [float(x) for x in arguments.get("hourly_c", [])]
        if not profile:
            return ToolResult({}, Provenance(source="derived", endpoint="local:summarize_heat_profile"), error="hourly_c_required")
        threshold = float(arguments.get("threshold_c", 32.0))
        above = [i for i, value in enumerate(profile) if value > threshold]
        return ToolResult(
            {
                "min_c": min(profile),
                "max_c": max(profile),
                "mean_c": mean(profile),
                "peak_hour_index": profile.index(max(profile)),
                "hours_above_threshold": len(above),
                "threshold_c": threshold,
            },
            Provenance(source="derived", endpoint="local:summarize_heat_profile", assumptions=("hourly values are treated as Celsius",)),
        )

    @staticmethod
    def calculate_exposure_metric(arguments: dict[str, Any]) -> ToolResult:
        profile = [float(x) for x in arguments.get("hourly_c", [])]
        windows = arguments.get("work_windows", [])
        threshold = float(arguments.get("threshold_c", 32.0))
        if not profile or not windows:
            return ToolResult({}, Provenance(source="derived", endpoint="local:calculate_exposure_metric"), error="hourly_c_and_work_windows_required")
        selected: list[float] = []
        for window in windows:
            start, end = int(window["start_hour"]), int(window["end_hour"])
            selected.extend(profile[start:end])
        burden = sum(max(0.0, value - threshold) for value in selected)
        return ToolResult(
            {"thermal_load_proxy_degree_hours": round(burden, 4), "hours": len(selected), "threshold_c": threshold},
            Provenance(source="derived", endpoint="local:calculate_exposure_metric", assumptions=("proxy is degree-hours above a configurable threshold; not a medical exposure model",)),
        )

    @staticmethod
    def compare_locations(arguments: dict[str, Any]) -> ToolResult:
        locations = arguments.get("locations", {})
        threshold = float(arguments.get("threshold_c", 32.0))
        rows = []
        for name, profile in locations.items():
            values = [float(x) for x in profile]
            rows.append({"location": name, "max_c": max(values), "hours_above_threshold": sum(x > threshold for x in values), "mean_c": round(mean(values), 4)})
        rows.sort(key=lambda row: (-row["max_c"], -row["hours_above_threshold"], row["location"]))
        return ToolResult(
            {"locations": rows, "threshold_c": threshold},
            Provenance(source="derived", endpoint="local:compare_locations"),
        )


def load_live_toolkit() -> FortyGuardToolkit:
    """Opt-in helper that reads the key without ever printing it."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "vendor" / "temperature-api-quickstart"))
    try:
        from fortyguard import FortyGuardClient
    except ImportError as exc:
        raise RuntimeError("Install requests to enable live FortyGuard calls") from exc
    key = os.getenv("FORTYGUARD_API_KEY")
    if not key:
        raise RuntimeError("FORTYGUARD_API_KEY is not configured")
    return FortyGuardToolkit(FortyGuardClient(api_key=key, base_url=os.getenv("FORTYGUARD_BASE_URL")))
