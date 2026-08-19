from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent import AgentRunner, ToolRegistry, ToolSpec
from .guardrails import Budget, SafetyPolicy
from .models import ActionProposal, AgentState, Goal
from .providers import MockProvider, ProviderDecision
from .toolkit import FortyGuardToolkit


@dataclass
class ScenarioResult:
    name: str
    baseline_metric: float
    agent_metric: float
    improvement: float
    agent_termination: str | None
    trace_events: int
    passed: bool


def build_spike_registry(toolkit: FortyGuardToolkit, profile_by_site: dict[str, list[float]]) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ToolSpec("get_heatmap", "Retrieve a FortyGuard heat profile or fixture.", {"type": "object"}, lambda args: toolkit.get_heatmap(args)))
    registry.register(ToolSpec("summarize_heat_profile", "Summarize measured or fixture hourly temperature values.", {"type": "object"}, toolkit.summarize_heat_profile))
    registry.register(ToolSpec("calculate_exposure_metric", "Calculate a transparent degree-hour proxy for a candidate work window.", {"type": "object"}, toolkit.calculate_exposure_metric))
    registry.register(ToolSpec("compare_locations", "Compare location profiles using the same derived metric.", {"type": "object"}, toolkit.compare_locations))
    return registry


def run_deterministic_spike(name: str, profile: list[float], *, baseline_window: dict[str, int], candidate_window: dict[str, int], threshold_c: float = 32.0) -> ScenarioResult:
    toolkit = FortyGuardToolkit()
    registry = build_spike_registry(toolkit, {"site": profile})
    decisions = [
        ProviderDecision.call_tool("summarize_heat_profile", {"hourly_c": profile, "threshold_c": threshold_c}),
        ProviderDecision.call_tool("calculate_exposure_metric", {"hourly_c": profile, "work_windows": [candidate_window], "threshold_c": threshold_c}),
        ProviderDecision.propose(ActionProposal(
            action_type="maintenance_window",
            description=f"Use the candidate window {candidate_window['start_hour']}:00–{candidate_window['end_hour']}:00 after reviewing FortyGuard-derived heat evidence.",
            parameters={"window": candidate_window},
            confidence=0.82,
            requires_approval=True,
            evidence=["FortyGuard fixture-backed hourly profile", "derived thermal_load_proxy_degree_hours"],
        )),
    ]
    runner = AgentRunner(registry, MockProvider(decisions), budget=Budget(max_iterations=5, max_tool_calls=4, max_api_credits=4), policy=SafetyPolicy(allowed_tools=registry.names()))
    state, trace = runner.run(AgentState(Goal(text=f"Choose a lower-heat window for {name}", user="operations manager", success_metric="Minimize thermal load proxy while preserving the work window.")))
    baseline_result = toolkit.calculate_exposure_metric({"hourly_c": profile, "work_windows": [baseline_window], "threshold_c": threshold_c})
    agent_result = toolkit.calculate_exposure_metric({"hourly_c": profile, "work_windows": [candidate_window], "threshold_c": threshold_c})
    baseline = float(baseline_result.data["thermal_load_proxy_degree_hours"])
    agent = float(agent_result.data["thermal_load_proxy_degree_hours"])
    return ScenarioResult(name, baseline, agent, round(baseline - agent, 4), state.termination_reason, len(trace.events), state.termination_reason == "awaiting_human_approval")


def run_fixture_spikes() -> list[ScenarioResult]:
    """Use cached FortyGuard env-parameter shape with synthetic windows.

    This intentionally measures only whether the decision loop can exploit a
    real hourly profile. It is not a claim that the fixture is a live forecast
    for the demo date.
    """
    profile = [21.3, 20.3, 19.5, 18.8, 18.7, 17.6, 17.8, 19.5, 22.2, 25.7, 30.1, 33.3, 35.3, 36.5, 36.6, 35.4, 35.0, 31.8, 29.2, 27.4, 26.0, 24.4, 23.0, 20.5]
    return [
        run_deterministic_spike("thermal construction window", profile, baseline_window={"start_hour": 12, "end_hour": 15}, candidate_window={"start_hour": 7, "end_hour": 10}),
        run_deterministic_spike("field-service sequence", profile, baseline_window={"start_hour": 11, "end_hour": 14}, candidate_window={"start_hour": 8, "end_hour": 11}),
        run_deterministic_spike("warehouse dock shift", profile, baseline_window={"start_hour": 13, "end_hour": 16}, candidate_window={"start_hour": 9, "end_hour": 12}),
    ]
