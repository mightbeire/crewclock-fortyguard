from datetime import datetime, timedelta, timezone

from fortyguard_agent.agent import AgentRunner
from fortyguard_agent.cache import JsonCache
from fortyguard_agent.guardrails import Budget, FortyGuardRequestGuard, SafetyPolicy
from fortyguard_agent.models import AgentState, Goal
from fortyguard_agent.providers import MockProvider, ProviderDecision
from fortyguard_agent.registry import build_tool_registry
from fortyguard_agent.toolkit import FortyGuardToolkit


def test_registry_exposes_narrow_agent_boundary() -> None:
    names = build_tool_registry(FortyGuardToolkit()).names()
    assert {"inspect_shift_plan", "identify_thermal_candidates", "get_workface_heatmap", "get_environmental_context", "calculate_thermal_overlap", "generate_feasible_schedule_alternatives", "verify_schedule", "compare_schedule_metrics", "request_superintendent_approval"}.issubset(names)


def test_all_indoor_selection_does_not_request_thermal_evidence() -> None:
    toolkit = FortyGuardToolkit()
    result = toolkit.identify_thermal_candidates({"tasks": [{"id": "I1", "outdoor": False, "fixed": False}]})
    assert result.data["candidate_task_ids"] == []


def test_fixed_outdoor_selection_does_not_generate_move() -> None:
    toolkit = FortyGuardToolkit()
    result = toolkit.identify_thermal_candidates({"tasks": [{"id": "F1", "outdoor": True, "fixed": True}]})
    assert result.data["candidate_task_ids"] == []


def test_env_params_artifact_is_protected() -> None:
    result = FortyGuardToolkit.summarize_heat_profile({"source_endpoint": "/v1/env_params", "hourly_c": [20, 50], "range_response": True})
    assert result.error == "env_params_anchor_curve_cannot_be_shift_exposure"


def test_duplicate_request_reuses_cache_without_new_credits(tmp_path) -> None:
    class FakeClient:
        calls = 0

        def create_heatmap(self, **kwargs):
            self.calls += 1
            return {"activity_id": "a1", "result": {"map_data": {"type": "FeatureCollection", "features": []}, "stats_data": {}}}

    client = FakeClient()
    guard = FortyGuardRequestGuard(remaining_credits=10_000)
    toolkit = FortyGuardToolkit(client, JsonCache(tmp_path), guard)
    # An empty TCM map is not a valid successful evidence response; the wrapper
    # must fail closed and therefore not cache or spend it.
    result = toolkit.get_heatmap({"polygon_aoi": {"type": "FeatureCollection", "features": [{"geometry": {"type": "Polygon", "coordinates": [[(-112.02, 33.43), (-112.01, 33.43), (-112.01, 33.44), (-112.02, 33.44), (-112.02, 33.43)]]}}]}, "start_date": "2026-08-20", "filter_type": 1, "start_time": "12:00", "granularity": 100})
    assert result.error == "heatmap_empty_feature_collection"
    assert result.data == {"state": "INVALID_EVIDENCE", "reason": "heatmap_empty_feature_collection"}
    assert guard.run_credits_used == 0


def test_provider_can_drive_tools_then_stop_at_approval() -> None:
    toolkit = FortyGuardToolkit()
    registry = build_tool_registry(toolkit)
    provider = MockProvider([
        ProviderDecision.call_tool("identify_thermal_candidates", {"tasks": [{"id": "O1", "outdoor": True, "fixed": False}]}),
        ProviderDecision.call_tool("request_superintendent_approval", {"recommendation_id": "r1"}),
        ProviderDecision.finish("approval_requested"),
    ])
    runner = AgentRunner(registry, provider, budget=Budget(max_iterations=4, max_tool_calls=3, max_api_credits=3), policy=SafetyPolicy(allowed_tools=registry.names()))
    state, _ = runner.run(AgentState(Goal("adjust the upcoming shift", "superintendent")))
    assert state.termination_reason == "approval_requested"


def test_future_horizon_request_is_rejected_before_handler() -> None:
    guard = FortyGuardRequestGuard()
    try:
        guard.validate("/v1/heatmap", {"polygon_aoi": {"features": [{"geometry": {"coordinates": [[(-112.02, 33.43), (-112.01, 33.43), (-112.01, 33.44), (-112.02, 33.44), (-112.02, 33.43)]]}}]}, "granularity": 100}, request_at=datetime.now(timezone.utc) + timedelta(hours=13), now=datetime.now(timezone.utc))
    except Exception as exc:
        assert "forecast_horizon" in str(exc)
    else:
        raise AssertionError("horizon guard did not reject")
