from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from .cache import JsonCache, request_hash
from .guardrails import FortyGuardRequestGuard, GuardrailError
from .models import Provenance, ToolResult
from .thermal import ThermalContractError, assert_env_params_schema, assert_heatmap_schema, env_params_role


class FortyGuardToolkit:
    """Safe adapter around the vendored FortyGuard client plus derived tools.

    Live calls are opt-in: callers must pass a client. Offline fixtures are
    explicit and always carry ``sample`` provenance.
    """

    def __init__(self, client: Any | None = None, cache: JsonCache | None = None, request_guard: FortyGuardRequestGuard | None = None) -> None:
        self.client = client
        self.cache = cache or JsonCache()
        self.request_guard = request_guard or FortyGuardRequestGuard()

    def _cached_or_live(self, endpoint: str, payload: dict[str, Any], call: Any) -> ToolResult:
        key = request_hash(endpoint, payload)
        cached = self.cache.get(key)
        if cached is not None:
            return ToolResult(
                data=cached["data"],
                provenance=Provenance(source="cached", endpoint=endpoint, request_hash=key, activity_id=cached.get("activity_id"), assumptions=tuple(cached.get("assumptions", []))),
                estimated_credits=0,
            )
        if self.client is None:
            return ToolResult(
                data={},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key),
                error="live_client_not_configured",
            )
        try:
            estimated = self.request_guard.validate(endpoint, payload)
            raw = call()
            result = raw.get("result", raw) if isinstance(raw, dict) else raw
            activity_id = raw.get("activity_id") if isinstance(raw, dict) else None
            if endpoint == "/v1/heatmap":
                analytic_type = str(payload.get("analytic_type", "tcm"))
                assert_heatmap_schema(result, analytic_type)
            if endpoint == "/v1/env_params":
                assert_env_params_schema(result)
            self.cache.put_success(key, endpoint=endpoint, request=payload, data=result, provenance={"activity_id": activity_id, "provenance": "LIVE", "assumptions": []})
            self.request_guard.commit(estimated)
            return ToolResult(
                data=result if isinstance(result, dict) else {"result": result},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key, activity_id=activity_id),
                estimated_credits=estimated,
            )
        except ThermalContractError as exc:
            return ToolResult(
                data={},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key),
                error=str(exc),
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
        try:
            self.request_guard.validate("/v1/heatmap", payload)
        except GuardrailError as exc:
            return ToolResult({}, Provenance(source="derived", endpoint="/v1/heatmap"), error=str(exc))
        return self._cached_or_live("/v1/heatmap", payload, lambda: self.client.create_heatmap(**payload, verbose=False))

    def get_environmental_parameters(self, arguments: dict[str, Any]) -> ToolResult:
        payload = dict(arguments)
        fixture = payload.pop("fixture", None)
        if fixture:
            return self.load_fixture(fixture, endpoint="/v1/env_params")
        if payload.get("use_as_exposure_metric") or payload.get("derive_hours_above_threshold"):
            return ToolResult({}, Provenance(source="derived", endpoint="/v1/env_params"), error="env_params_range_cannot_be_exposure_forecast")
        try:
            self.request_guard.validate("/v1/env_params", payload)
        except GuardrailError as exc:
            return ToolResult({}, Provenance(source="derived", endpoint="/v1/env_params"), error=str(exc))
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
        if arguments.get("source_endpoint") == "/v1/env_params" and arguments.get("range_response", True):
            return ToolResult({}, Provenance(source="derived", endpoint="local:summarize_heat_profile"), error="env_params_anchor_curve_cannot_be_shift_exposure")
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
        if arguments.get("source_endpoint") == "/v1/env_params":
            return ToolResult({}, Provenance(source="derived", endpoint="local:calculate_exposure_metric"), error="env_params_anchor_curve_cannot_be_shift_exposure")
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
    def inspect_shift_plan(arguments: dict[str, Any]) -> ToolResult:
        tasks = arguments.get("tasks", [])
        return ToolResult({"task_count": len(tasks), "outdoor_task_ids": [t.get("id") for t in tasks if t.get("outdoor", t.get("environment") != "indoor")], "source": "SYNTHETIC OPERATIONAL INPUT"}, Provenance(source="derived", endpoint="local:inspect_shift_plan"))

    @staticmethod
    def identify_thermal_candidates(arguments: dict[str, Any]) -> ToolResult:
        tasks = arguments.get("tasks", [])
        candidates = [t.get("id") for t in tasks if t.get("outdoor", False) and not t.get("fixed", False)]
        return ToolResult({"candidate_task_ids": candidates, "reason": "movable outdoor work only"}, Provenance(source="derived", endpoint="local:identify_thermal_candidates"))

    @staticmethod
    def calculate_thermal_overlap(arguments: dict[str, Any]) -> ToolResult:
        from datetime import datetime
        from .thermal import ThermalTrigger, calculate_thermal_overlap as overlap
        trigger = ThermalTrigger(arguments["trigger_name"], datetime.fromisoformat(arguments["trigger_start"]), datetime.fromisoformat(arguments["trigger_end"]), arguments.get("threshold_c"), "employer_configured", arguments.get("provenance", "EMPLOYER_CONFIGURED"))
        result = overlap(datetime.fromisoformat(arguments["task_start"]), datetime.fromisoformat(arguments["task_end"]), trigger, int(arguments["crew_size"]), evidence_source=arguments.get("evidence_source", "DERIVED"))
        return ToolResult({"overlap_minutes": result.overlap_minutes, "crew_hours": result.crew_hours, "trigger_name": result.trigger_name, "confidence": result.confidence}, Provenance(source="derived", endpoint="local:calculate_thermal_overlap"))

    @staticmethod
    def generate_feasible_schedule_alternatives(arguments: dict[str, Any]) -> ToolResult:
        return ToolResult({"status": "DETERMINISTIC_SCHEDULER_REQUIRED", "requested_task_ids": arguments.get("task_ids", []), "thermal_objective_subordinate_to_hard_constraints": True}, Provenance(source="derived", endpoint="local:generate_feasible_schedule_alternatives"))

    @staticmethod
    def verify_schedule(arguments: dict[str, Any]) -> ToolResult:
        return ToolResult({"status": "DETERMINISTIC_VERIFIER_REQUIRED", "schedule_hash": request_hash("local:verify_schedule", arguments)}, Provenance(source="derived", endpoint="local:verify_schedule"))

    @staticmethod
    def compare_schedule_metrics(arguments: dict[str, Any]) -> ToolResult:
        before, after = float(arguments.get("before_crew_hours", 0)), float(arguments.get("after_crew_hours", 0))
        return ToolResult({"before_scheduled_high_heat_crew_hours": before, "after_scheduled_high_heat_crew_hours": after, "delta": round(before - after, 4), "metric_type": "DERIVED SCHEDULE METRIC"}, Provenance(source="derived", endpoint="local:compare_schedule_metrics"))

    @staticmethod
    def request_superintendent_approval(arguments: dict[str, Any]) -> ToolResult:
        return ToolResult({"status": "PENDING_SUPERINTENDENT_APPROVAL", "recommendation_id": arguments.get("recommendation_id"), "publish_blocked_until_approval": True}, Provenance(source="derived", endpoint="local:request_superintendent_approval"))

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
