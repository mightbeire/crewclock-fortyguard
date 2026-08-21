from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import math
from typing import Any

from .timezones import project_timezone


class GuardrailError(RuntimeError):
    pass


@dataclass
class Budget:
    max_iterations: int = 8
    max_model_calls: int = 8
    max_tool_calls: int = 12
    max_input_chars: int = 12_000
    max_api_credits: int = 25_000
    estimated_costs: dict[str, int] = field(default_factory=dict)
    iterations: int = 0
    model_calls: int = 0
    tool_calls: int = 0
    api_credits_reserved: int = 0

    def before_iteration(self) -> None:
        if self.iterations >= self.max_iterations:
            raise GuardrailError("iteration_limit_reached")
        self.iterations += 1

    def reserve_tool(self, tool_name: str) -> int:
        if self.tool_calls >= self.max_tool_calls:
            raise GuardrailError("tool_call_limit_reached")
        cost = int(self.estimated_costs.get(tool_name, 1))
        if self.api_credits_reserved + cost > self.max_api_credits:
            raise GuardrailError("api_credit_budget_reached")
        self.tool_calls += 1
        self.api_credits_reserved += cost
        return cost

    def before_model_call(self, input_chars: int) -> None:
        if self.model_calls >= self.max_model_calls:
            raise GuardrailError("model_call_limit_reached")
        if input_chars > self.max_input_chars:
            raise GuardrailError("model_input_limit_reached")
        self.model_calls += 1


@dataclass
class SafetyPolicy:
    allowed_tools: set[str]
    approval_required_actions: set[str] = field(default_factory=lambda: {"schedule_change", "dispatch", "maintenance_window", "send_alert"})
    max_repeated_tool_calls: int = 1

    def check_tool(self, name: str, previous_calls: list[str]) -> None:
        if name not in self.allowed_tools:
            raise GuardrailError(f"tool_not_allowed:{name}")
        if previous_calls.count(name) >= self.max_repeated_tool_calls:
            raise GuardrailError(f"repeated_tool_call_blocked:{name}")

    def needs_approval(self, action_type: str) -> bool:
        return action_type in self.approval_required_actions


@dataclass
class FortyGuardRequestGuard:
    """Local, deterministic guard before a request can reach FortyGuard."""

    remaining_credits: int = 1_795_500
    max_run_credits: int = 25_000
    run_credits_used: int = 0
    max_heatmap_area_mi2: float = 10.0
    forecast_horizon_hours: int = 12
    allowed_endpoints: set[str] = field(default_factory=lambda: {"/v1/heatmap", "/v1/env_params", "/v1/status/{activity_id}"})

    @staticmethod
    def heatmap_request_at(payload: dict[str, Any]) -> datetime | None:
        """Convert a heatmap's local start time into an aware project timestamp.

        The official client accepts flat keyword arguments while the HTTP
        contract nests these fields under ``date_time``.  Supporting both here
        keeps the pre-submit horizon check independent of the client shape.
        """
        date_time = payload.get("date_time") if isinstance(payload.get("date_time"), dict) else payload
        filter_type = date_time.get("filter_type")
        start_date = date_time.get("start_date")
        start_time = date_time.get("start_time")
        if filter_type in {1, 2} and not start_time:
            raise GuardrailError("heatmap_start_time_required")
        if not start_date or not start_time:
            return None
        try:
            naive = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        except (TypeError, ValueError) as exc:
            raise GuardrailError("invalid_heatmap_start_datetime") from exc
        return naive.replace(tzinfo=project_timezone())

    def estimate(self, endpoint: str, payload: dict[str, Any]) -> int:
        if endpoint == "/v1/heatmap":
            # Measured successful Phoenix single-hour request in the current account.
            return 4_220
        if endpoint == "/v1/env_params":
            return 2_900
        return 0

    @staticmethod
    def _aoi_area_mi2(payload: dict[str, Any]) -> float:
        aoi = payload.get("polygon_aoi") or {}
        features = aoi.get("features") or []
        if not features:
            return 0.0
        coords = ((features[0].get("geometry") or {}).get("coordinates") or [[]])[0]
        if len(coords) < 4:
            raise GuardrailError("invalid_polygon_aoi")
        lat = sum(float(pair[1]) for pair in coords) / len(coords)
        # Equirectangular approximation is sufficient for a pre-submit limit check.
        scale_x, scale_y = 69.172 * math.cos(math.radians(lat)), 69.0
        planar = [(float(pair[0]) * scale_x, float(pair[1]) * scale_y) for pair in coords]
        area = abs(sum(planar[i][0] * planar[(i + 1) % len(planar)][1] - planar[(i + 1) % len(planar)][0] * planar[i][1] for i in range(len(planar))) / 2)
        return area

    @staticmethod
    def _us_point(payload: dict[str, Any]) -> bool:
        if "latitude" in payload and "longitude" in payload:
            lat, lon = float(payload["latitude"]), float(payload["longitude"])
            return 24.0 <= lat <= 50.0 and -125.0 <= lon <= -66.0
        aoi = payload.get("polygon_aoi") or {}
        coords = (((aoi.get("features") or [{}])[0].get("geometry") or {}).get("coordinates") or [[]])[0]
        return bool(coords) and all(24.0 <= float(pair[1]) <= 50.0 and -125.0 <= float(pair[0]) <= -66.0 for pair in coords)

    def validate(self, endpoint: str, payload: dict[str, Any], *, request_at: datetime | None = None, now: datetime | None = None) -> int:
        if endpoint not in self.allowed_endpoints:
            raise GuardrailError(f"endpoint_not_allowlisted:{endpoint}")
        if not self._us_point(payload):
            raise GuardrailError("fortyguard_us_coverage_required")
        if endpoint == "/v1/heatmap":
            self.heatmap_request_at(payload)
            area = self._aoi_area_mi2(payload)
            if area > self.max_heatmap_area_mi2:
                raise GuardrailError("heatmap_aoi_exceeds_basic_plan_limit")
            granularity = payload.get("granularity")
            if granularity not in {60, 80, 100}:
                raise GuardrailError("unsupported_heatmap_granularity")
        if request_at is not None:
            if request_at.tzinfo is None:
                raise GuardrailError("forecast_request_must_be_timezone_aware")
            reference = now or datetime.now(timezone.utc)
            if request_at > reference + timedelta(hours=self.forecast_horizon_hours):
                raise GuardrailError("forecast_horizon_exceeded")
        estimated = self.estimate(endpoint, payload)
        if self.run_credits_used + estimated > self.max_run_credits:
            raise GuardrailError("run_credit_cap_would_be_exceeded")
        if estimated > self.remaining_credits:
            raise GuardrailError("remaining_credit_balance_insufficient")
        return estimated

    def commit(self, estimated: int) -> None:
        self.run_credits_used += estimated
        self.remaining_credits -= estimated
