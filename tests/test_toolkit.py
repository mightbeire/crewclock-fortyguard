from fortyguard_agent.models import Provenance
from fortyguard_agent.toolkit import FortyGuardToolkit
from fortyguard_agent.registry import build_tool_registry


def test_derived_metric_is_marked_derived() -> None:
    result = FortyGuardToolkit.calculate_contextual_temperature_summary({
        "hourly_c": [20.0, 35.0, 40.0],
        "work_windows": [{"start_hour": 1, "end_hour": 3}],
        "threshold_c": 30.0,
    })
    assert result.data["contextual_temperature_exceedance_degree_hours"] == 15.0
    assert result.provenance.source == "derived"
    assert "context-only" in result.provenance.assumptions[0]


def test_live_call_without_client_fails_explicitly() -> None:
    result = FortyGuardToolkit().get_heatmap({"start_date": "2026-08-19"})
    assert result.error == "live_client_not_configured"
    assert result.provenance.source == "live"


def test_registry_contains_reusable_fortyguard_tools() -> None:
    names = build_tool_registry(FortyGuardToolkit()).names()
    assert {"get_workface_thermal_evidence", "get_environmental_context", "calculate_contextual_temperature_summary"}.issubset(names)
    assert {"get_heatmap", "get_environmental_parameters", "get_activity_status", "inspect_api_usage"}.isdisjoint(names)


def test_model_facing_registry_rejects_arbitrary_evidence_paths() -> None:
    registry = build_tool_registry(FortyGuardToolkit())
    spec = registry.get("get_workface_thermal_evidence")
    try:
        spec.validate_arguments({"fixture": "C:/arbitrary/evidence.json"})
    except Exception as exc:
        assert "missing_tool_arguments" in str(exc) or "unknown_tool_arguments" in str(exc)
    else:
        raise AssertionError("arbitrary model-facing fixture path was accepted")
