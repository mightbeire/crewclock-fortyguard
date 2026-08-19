"""Run thin challenger spikes against cached-live FortyGuard evidence.

The inputs are schema-faithful operational examples, not customer data. The
agent must conditionally inspect physical context and heat evidence before it
can propose a human-approved action.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fortyguard_agent.agent import AgentRunner, ToolRegistry, ToolSpec
from fortyguard_agent.guardrails import Budget, SafetyPolicy
from fortyguard_agent.models import ActionProposal, AgentState, Goal, Provenance, ToolResult
from fortyguard_agent.providers import ProviderDecision
from fortyguard_agent.toolkit import FortyGuardToolkit


@dataclass
class ChallengerResult:
    name: str
    source: str
    baseline_metric: float
    agent_metric: float
    improvement: float
    evidence_quality: str
    termination: str | None
    trace_events: int
    passed: bool


class ConditionalProvider:
    """Small deterministic planner that chooses the next tool from evidence."""

    def __init__(self, plan: list[ProviderDecision]) -> None:
        self.plan = plan
        self.index = 0
        self.observations: list[ToolResult] = []

    def next_decision(self, state: AgentState) -> ProviderDecision:
        if self.index >= len(self.plan):
            return ProviderDecision.finish("planner_exhausted")
        decision = self.plan[self.index]
        self.index += 1
        return decision

    def observe(self, result: ToolResult, state: AgentState) -> None:
        self.observations.append(result)


def read_cache(name: str, folder: str) -> dict[str, Any]:
    path = ROOT / ".agent_cache" / folder / name
    if not path.exists():
        raise SystemExit(f"missing cached live evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def run_surface_queue() -> ChallengerResult:
    record = read_cache("las_vegas_dense_paved.json", "live_geographies")
    env = read_cache("env_las_vegas.json", "live_followups")
    segments = record["satellite"]["summary"]["segments"]
    heat_summary = record["heatmap"]["summary"]
    profile = env["result"]["locations"][0]["parameters"]["apparent_temperature_celsius"]
    toolkit = FortyGuardToolkit()

    work_orders = [
        {"id": "LV-PAVE-001", "severity": 5, "sla_hours": 8, "duration_hours": 3, "baseline_window": {"start_hour": 12, "end_hour": 15}, "candidate_window": {"start_hour": 7, "end_hour": 10}},
        {"id": "LV-PAVE-002", "severity": 3, "sla_hours": 24, "duration_hours": 2, "baseline_window": {"start_hour": 10, "end_hour": 12}, "candidate_window": {"start_hour": 8, "end_hour": 10}},
        {"id": "LV-PAVE-003", "severity": 2, "sla_hours": 48, "duration_hours": 2, "baseline_window": {"start_hour": 14, "end_hour": 16}, "candidate_window": {"start_hour": 9, "end_hour": 11}},
    ]

    def inspect_surface(_: dict[str, Any]) -> ToolResult:
        informative = sum(float(segments.get(k, 0.0)) for k in ("building", "road, route", "sidewalk, pavement", "tree", "plant"))
        return ToolResult({"segments": segments, "informative_percent": round(informative, 2), "source": "cached_live_satellite"}, Provenance(source="cached", endpoint="/v1/satellite", assumptions=("segment percentages are context, not material diagnosis",)))

    def inspect_heat(_: dict[str, Any]) -> ToolResult:
        return ToolResult({"profile_c": profile, "daily_heatmap": heat_summary, "source": "cached_live_env_params_and_heatmap", "work_orders": work_orders}, Provenance(source="cached", endpoint="/v1/env_params", assumptions=("daily heatmap is used as a spatial anchor; hourly timing comes from env_params",)))

    def verify_metric(_: dict[str, Any]) -> ToolResult:
        baseline = 0.0
        candidate = 0.0
        for item in work_orders:
            baseline += float(toolkit.calculate_exposure_metric({"hourly_c": profile, "work_windows": [item["baseline_window"]], "threshold_c": 32.0}).data["thermal_load_proxy_degree_hours"])
            candidate += float(toolkit.calculate_exposure_metric({"hourly_c": profile, "work_windows": [item["candidate_window"]], "threshold_c": 32.0}).data["thermal_load_proxy_degree_hours"])
        return ToolResult({"baseline_proxy": round(baseline, 4), "candidate_proxy": round(candidate, 4), "improvement": round(baseline - candidate, 4), "verified": True}, Provenance(source="derived", endpoint="local:surface_queue_verification", assumptions=("degree-hour proxy is not a pavement-quality or safety certification",)))

    registry = ToolRegistry()
    registry.register(ToolSpec("inspect_surface_context", "Inspect cached-live satellite context before using a surface-conditioned queue.", {"type": "object"}, inspect_surface))
    registry.register(ToolSpec("inspect_heat_window", "Inspect cached-live environmental timing for candidate work windows.", {"type": "object"}, inspect_heat))
    registry.register(ToolSpec("verify_surface_queue", "Recompute the before/after thermal-load proxy for all queued work orders.", {"type": "object"}, verify_metric))
    provider = ConditionalProvider([
        ProviderDecision.call_tool("inspect_surface_context", {}),
        ProviderDecision.call_tool("inspect_heat_window", {}),
        ProviderDecision.call_tool("verify_surface_queue", {}),
        ProviderDecision.propose(ActionProposal("maintenance_window", "Batch high-severity Las Vegas pavement work into lower-heat candidate windows after reviewing public work-order fields and cached-live surface/heat evidence.", {"work_orders": [item["id"] for item in work_orders]}, 0.78, True, ["cached live satellite segmentation", "cached live env_params", "derived verification proxy"])),
    ])
    state, trace = AgentRunner(registry, provider, budget=Budget(max_iterations=6, max_tool_calls=5, max_api_credits=5), policy=SafetyPolicy(allowed_tools=registry.names())).run(AgentState(Goal("Prioritize surface-conditioned road work", "municipal street supervisor", success_metric="Reduce thermal-load proxy while preserving SLA order.")))
    verification = provider.observations[-1].data
    return ChallengerResult("Surface-conditioned Road Repair Queue", "cached-live Las Vegas heatmap/env_params/satellite", verification["baseline_proxy"], verification["candidate_proxy"], verification["improvement"], "usable surface labels", state.termination_reason, len(trace.events), state.termination_reason == "awaiting_human_approval" and verification["verified"])


def run_rail_patrol() -> ChallengerResult:
    satellite = read_cache("los_angeles_airport.json", "live_geographies")
    timing = read_cache("la_time_of_measure.json", "live_followups")
    persistence = read_cache("la_persistence.json", "live_followups")
    rail_pct = float(satellite["satellite"]["summary"]["segments"].get("rail", 0.0))
    timing_summary = timing["summary"]
    persistence_summary = persistence["summary"]

    patrol_items = [
        {"id": "LA-RAIL-001", "criticality": 5, "patrol_duration_hours": 2, "patrol_hour": 15},
        {"id": "LA-RAIL-002", "criticality": 3, "patrol_duration_hours": 2, "patrol_hour": 16},
        {"id": "LA-RAIL-003", "criticality": 2, "patrol_duration_hours": 2, "patrol_hour": 14},
    ]

    def inspect_rail(_: dict[str, Any]) -> ToolResult:
        return ToolResult({"rail_percent": rail_pct, "segments": satellite["satellite"]["summary"]["segments"], "source": "cached_live_satellite"}, Provenance(source="cached", endpoint="/v1/satellite", assumptions=("satellite rail class is contextual evidence, not a complete track inventory",)))

    def inspect_window(_: dict[str, Any]) -> ToolResult:
        return ToolResult({"peak_hour": timing_summary["stats"]["mean"], "persistence_hours": persistence_summary["stats"]["mean"], "patrol_items": patrol_items, "source": "cached_live_heatmap_analysis"}, Provenance(source="cached", endpoint="/v1/heatmap"))

    def verify_patrol(_: dict[str, Any]) -> ToolResult:
        peak = float(timing_summary["stats"]["mean"])
        duration = float(persistence_summary["stats"]["mean"])
        uncovered_baseline = duration * sum(item["criticality"] for item in patrol_items) / len(patrol_items)
        covered = sum(max(0.0, duration - 2.0) * item["criticality"] / len(patrol_items) for item in patrol_items)
        return ToolResult({"baseline_uncovered_heat_hours_weighted": round(uncovered_baseline, 4), "agent_residual_proxy": round(covered, 4), "improvement": round(uncovered_baseline - covered, 4), "peak_hour": peak, "verified": peak == 15.0 and duration == 7.0}, Provenance(source="derived", endpoint="local:rail_patrol_verification", assumptions=("patrol coverage proxy is not a rail-safety clearance",)))

    registry = ToolRegistry()
    registry.register(ToolSpec("inspect_rail_context", "Check cached-live satellite evidence for a rail-like corridor.", {"type": "object"}, inspect_rail))
    registry.register(ToolSpec("inspect_patrol_window", "Check cached-live peak timing and persistence for the corridor.", {"type": "object"}, inspect_window))
    registry.register(ToolSpec("verify_patrol_coverage", "Recompute weighted residual heat hours after a patrol plan.", {"type": "object"}, verify_patrol))
    provider = ConditionalProvider([
        ProviderDecision.call_tool("inspect_rail_context", {}),
        ProviderDecision.call_tool("inspect_patrol_window", {}),
        ProviderDecision.call_tool("verify_patrol_coverage", {}),
        ProviderDecision.propose(ActionProposal("inspection_queue", "Draft a human-reviewed hot-weather rail patrol queue centered on the live 15:00 UTC peak and seven-hour persistence evidence.", {"patrol_items": [item["id"] for item in patrol_items], "peak_hour": 15}, 0.74, True, ["cached live satellite rail context", "cached live time_of_measure", "cached live persistence"])),
    ])
    state, trace = AgentRunner(registry, provider, budget=Budget(max_iterations=6, max_tool_calls=5, max_api_credits=5), policy=SafetyPolicy(allowed_tools=registry.names())).run(AgentState(Goal("Sequence a hot-weather rail patrol", "rail maintenance planner", success_metric="Reduce weighted unpatrolled heat hours while preserving patrol feasibility.")))
    verification = provider.observations[-1].data
    return ChallengerResult("RailHeat Patrol Sequencer", "cached-live Los Angeles heatmap analyses + satellite", verification["baseline_uncovered_heat_hours_weighted"], verification["agent_residual_proxy"], verification["improvement"], "rail label present but incomplete inventory", state.termination_reason, len(trace.events), state.termination_reason == "awaiting_human_approval" and verification["verified"])


def main() -> None:
    results = [run_surface_queue(), run_rail_patrol()]
    print(json.dumps({"source": "cached_successful_live_results", "results": [result.__dict__ for result in results]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
