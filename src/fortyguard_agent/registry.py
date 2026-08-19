from __future__ import annotations

from .agent import ToolRegistry, ToolSpec
from .toolkit import FortyGuardToolkit


def build_tool_registry(toolkit: FortyGuardToolkit) -> ToolRegistry:
    """Register the reusable FortyGuard and derived tools in one place."""
    registry = ToolRegistry()
    registry.register(ToolSpec("get_heatmap", "Retrieve a FortyGuard heatmap or explicit fixture.", {"type": "object"}, toolkit.get_heatmap))
    registry.register(ToolSpec("get_environmental_parameters", "Retrieve FortyGuard environmental parameters or an explicit fixture.", {"type": "object"}, toolkit.get_environmental_parameters))
    registry.register(ToolSpec("get_activity_status", "Check a submitted FortyGuard activity.", {"type": "object", "required": ["activity_id"]}, toolkit.get_activity_status))
    registry.register(ToolSpec("inspect_api_usage", "Inspect sanitized account credit usage.", {"type": "object"}, lambda args: toolkit.inspect_api_usage(args)))
    registry.register(ToolSpec("summarize_heat_profile", "Derive a transparent summary from hourly temperature values.", {"type": "object"}, toolkit.summarize_heat_profile))
    registry.register(ToolSpec("compare_locations", "Compare candidate location profiles with the same derived metric.", {"type": "object"}, toolkit.compare_locations))
    registry.register(ToolSpec("calculate_exposure_metric", "Calculate a labeled degree-hour proxy for a candidate work window.", {"type": "object"}, toolkit.calculate_exposure_metric))
    return registry
