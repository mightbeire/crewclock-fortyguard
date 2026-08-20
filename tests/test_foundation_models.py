from datetime import datetime, timedelta, timezone

import pytest

from fortyguard_agent.guardrails import FortyGuardRequestGuard, GuardrailError
from fortyguard_agent.policy import BreakRule, EmployerPolicy, required_breaks_for_outdoor_intervals
from fortyguard_agent.scheduler import verify_schedule
from fortyguard_agent.thermal import (
    ThermalContractError,
    ThermalTrigger,
    area_weighted_tile_value,
    assert_heatmap_schema,
    calculate_thermal_overlap,
)
from fortyguard_agent.timezones import as_project_local, project_timezone


UTC = timezone.utc


def policy() -> EmployerPolicy:
    return EmployerPolicy("demo", "1", "Demo employer heat plan", "DEMO_POLICY", "2026-01-01", "heatmap_tcm", 35, 38, "celsius", (BreakRule("high", 90, 30, "DEMO_POLICY"),))


def trigger() -> ThermalTrigger:
    return ThermalTrigger("project_high_heat", datetime(2026, 8, 20, 11, tzinfo=UTC), datetime(2026, 8, 20, 15, tzinfo=UTC), 38, "employer_configured", "EMPLOYER_CONFIGURED")


def test_overlap_is_schedule_metric_not_exposure_claim() -> None:
    result = calculate_thermal_overlap(datetime(2026, 8, 20, 10, 30, tzinfo=UTC), datetime(2026, 8, 20, 12, 30, tzinfo=UTC), trigger(), 6, evidence_source="LIVE FORTYGUARD")
    assert result.overlap_minutes == 90
    assert result.crew_hours == 9
    assert result.evidence_source == "LIVE FORTYGUARD"


def test_polygon_uses_area_weighted_overlapping_tiles() -> None:
    workface = [(0, 0), (2, 0), (2, 1), (0, 1)]
    tiles = [
        {"geometry": {"type": "Polygon", "coordinates": [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]}, "properties": {"value": 30}},
        {"geometry": {"type": "Polygon", "coordinates": [[(1, 0), (2, 0), (2, 1), (1, 1), (1, 0)]]}, "properties": {"value": 40}},
    ]
    assert area_weighted_tile_value(workface, tiles) == 35


def test_heatmap_analysis_units_fail_closed() -> None:
    with pytest.raises(ThermalContractError):
        assert_heatmap_schema({"map_data": {"type": "FeatureCollection", "features": [{"properties": {"value": 3}}]}, "stats_data": {"analytic_type": "exceedance", "units": "degree-hours"}}, "exceedance")


def test_break_is_a_real_constraint() -> None:
    start = datetime(2026, 8, 20, 11, tzinfo=UTC)
    with pytest.raises(ValueError, match="mandatory_break"):
        required_breaks_for_outdoor_intervals([(start, start + timedelta(minutes=120))], policy(), start, start + timedelta(hours=4))


def test_break_can_be_reserved_in_gap() -> None:
    start = datetime(2026, 8, 20, 11, tzinfo=UTC)
    breaks = required_breaks_for_outdoor_intervals([(start, start + timedelta(minutes=90)), (start + timedelta(minutes=120), start + timedelta(minutes=180))], policy(), start, start + timedelta(hours=4))
    assert breaks == []  # two task intervals are separated; no continuous run exceeds 90 minutes


def test_horizon_and_aoi_guards_fail_before_submission() -> None:
    guard = FortyGuardRequestGuard()
    payload = {"polygon_aoi": {"type": "FeatureCollection", "features": [{"geometry": {"type": "Polygon", "coordinates": [[(-112.02, 33.43), (-112.01, 33.43), (-112.01, 33.44), (-112.02, 33.44), (-112.02, 33.43)]]}}]}, "granularity": 100}
    with pytest.raises(GuardrailError, match="forecast_horizon"):
        guard.validate("/v1/heatmap", payload, request_at=datetime.now(UTC) + timedelta(hours=13), now=datetime.now(UTC))
    large = {**payload, "polygon_aoi": {"type": "FeatureCollection", "features": [{"geometry": {"type": "Polygon", "coordinates": [[(-113, 32), (-100, 32), (-100, 45), (-113, 45), (-113, 32)]]}}]}}
    with pytest.raises(GuardrailError, match="aoi"):
        guard.validate("/v1/heatmap", large)


def test_phoenix_timestamp_conversion_is_local_not_utc() -> None:
    value = as_project_local(datetime(2026, 8, 21, 5, tzinfo=UTC))
    assert value.hour == 22
    assert value.tzinfo is not None


def test_scheduler_rejects_candidate_that_has_no_reserved_break() -> None:
    start = datetime(2026, 8, 20, 11, tzinfo=UTC)
    tasks = [{"id": "O1", "crew_id": "A", "qualification": "q", "duration": 120, "deadline": start + timedelta(hours=4), "baseline_start": start, "dependencies": [], "fixed": False, "outdoor": True}]
    verification = verify_schedule(tasks, {"O1": start}, {"A": {"qualifications": ["q"]}}, policy(), shift_start=start, shift_end=start + timedelta(hours=4), trigger_start=start, trigger_end=start + timedelta(hours=4))
    assert not verification.passed
    assert any(check.name == "policy_breaks" and not check.passed for check in verification.checks)
