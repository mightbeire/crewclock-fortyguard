from __future__ import annotations

from .agent import ToolRegistry, ToolSpec
from .toolkit import FortyGuardToolkit


def build_tool_registry(toolkit: FortyGuardToolkit) -> ToolRegistry:
    """Register only narrow, typed tools; raw HTTP is never exposed to an agent."""
    registry = ToolRegistry()
    registry.register(ToolSpec("inspect_shift_plan", "Inspect a submitted upcoming-shift plan.", {"type": "object", "properties": {"tasks": {"type": "array"}}, "required": ["tasks"]}, toolkit.inspect_shift_plan))
    registry.register(ToolSpec("identify_thermal_candidates", "Select movable outdoor tasks that justify thermal investigation.", {"type": "object", "properties": {"tasks": {"type": "array"}}, "required": ["tasks"]}, toolkit.identify_thermal_candidates))
    registry.register(ToolSpec("get_workface_heatmap", "Retrieve the guarded shared-AOI FortyGuard heatmap.", {"type": "object", "properties": {"polygon_aoi": {"type": "object"}, "start_date": {"type": "string"}, "filter_type": {"type": "integer"}, "granularity": {"type": "integer"}}, "required": ["polygon_aoi", "start_date", "filter_type", "granularity"]}, toolkit.get_heatmap))
    registry.register(ToolSpec("get_environmental_context", "Retrieve selective, time-matched FortyGuard environmental context.", {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}, "temperature": {"type": "number"}, "start_date": {"type": "string"}, "filter_type": {"type": "integer"}}, "required": ["latitude", "longitude", "temperature", "start_date", "filter_type"]}, toolkit.get_environmental_parameters))
    # Backward-compatible aliases remain available for existing offline traces.
    registry.register(ToolSpec("get_heatmap", "Retrieve a FortyGuard heatmap or explicit fixture.", {"type": "object"}, toolkit.get_heatmap))
    registry.register(ToolSpec("get_environmental_parameters", "Retrieve FortyGuard environmental parameters or an explicit fixture.", {"type": "object"}, toolkit.get_environmental_parameters))
    registry.register(ToolSpec("get_activity_status", "Check a submitted FortyGuard activity.", {"type": "object", "required": ["activity_id"]}, toolkit.get_activity_status))
    registry.register(ToolSpec("inspect_api_usage", "Inspect sanitized account credit usage.", {"type": "object"}, lambda args: toolkit.inspect_api_usage(args)))
    registry.register(ToolSpec("calculate_thermal_overlap", "Calculate scheduled overlap with the employer trigger.", {"type": "object", "required": ["task_start", "task_end", "trigger_name", "trigger_start", "trigger_end", "crew_size"]}, toolkit.calculate_thermal_overlap))
    registry.register(ToolSpec("generate_feasible_schedule_alternatives", "Ask deterministic scheduling code for feasible alternatives.", {"type": "object", "required": ["task_ids"]}, toolkit.generate_feasible_schedule_alternatives))
    registry.register(ToolSpec("verify_schedule", "Verify a candidate schedule against hard constraints.", {"type": "object", "required": ["schedule"]}, toolkit.verify_schedule))
    registry.register(ToolSpec("compare_schedule_metrics", "Compare derived schedule metrics with provenance.", {"type": "object", "required": ["before_crew_hours", "after_crew_hours"]}, toolkit.compare_schedule_metrics))
    registry.register(ToolSpec("request_superintendent_approval", "Create the human approval gate; never publish a plan.", {"type": "object", "required": ["recommendation_id"]}, toolkit.request_superintendent_approval, requires_approval=True))
    registry.register(ToolSpec("summarize_heat_profile", "Derive a transparent summary from permitted thermal samples.", {"type": "object"}, toolkit.summarize_heat_profile))
    registry.register(ToolSpec("compare_locations", "Compare candidate location profiles with the same derived metric.", {"type": "object"}, toolkit.compare_locations))
    registry.register(ToolSpec("calculate_exposure_metric", "Optional secondary degree-crew-hour calculation from time-matched samples only.", {"type": "object"}, toolkit.calculate_exposure_metric))
    return registry
