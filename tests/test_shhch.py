from fortyguard_agent.shhch import ShhchContractError, calculate_scheduled_high_heat_crew_hours


def _workfaces():
    return [{"id": "west", "polygon": [(0, 0), (10, 0), (10, 10), (0, 10)]}]


def _tiles():
    return [
        {"geometry": {"type": "Polygon", "coordinates": [[[0, 0], [5, 0], [5, 10], [0, 10], [0, 0]]]}, "properties": {"value": 2}},
        {"geometry": {"type": "Polygon", "coordinates": [[[5, 0], [10, 0], [10, 10], [5, 10], [5, 0]]]}, "properties": {"value": 0}},
    ]


def _windows():
    return [{
        "analytic_type": "exceedance",
        "start": "2025-07-15T12:00:00+00:00",
        "end": "2025-07-15T14:00:00+00:00",
        "units": "hours",
        "status": "VALID",
        "provenance": "CACHED_LIVE_FORTYGUARD:test-window",
        "tiles": _tiles(),
    }]


def _trigger():
    return {"threshold_c": 32, "quantity": "fortyguard_modeled_temperature", "provenance": "PROJECT_THERMAL_TRIGGER:test"}


def test_shhch_area_weight_and_temporal_overlap():
    result = calculate_scheduled_high_heat_crew_hours([
        {"id": "full", "start": "2025-07-15T12:00:00+00:00", "end": "2025-07-15T14:00:00+00:00", "crew_size": 5, "outdoor": True, "workface_id": "west"},
        {"id": "partial", "start": "2025-07-15T13:00:00+00:00", "end": "2025-07-15T15:00:00+00:00", "crew_size": 5, "outdoor": True, "workface_id": "west"},
    ], _workfaces(), _windows(), _trigger())
    assert result.valid is True
    # Half the workface has 2 hours of exceedance and half has zero: 1 hour
    # per full window. The second task overlaps one of those two hours.
    assert result.total_crew_hours == 7.5
    assert [item.crew_hours for item in result.contributions] == [5.0, 2.5]


def test_task_moved_outside_window_contributes_zero():
    result = calculate_scheduled_high_heat_crew_hours([
        {"id": "cool", "start": "2025-07-15T06:00:00+00:00", "end": "2025-07-15T08:00:00+00:00", "crew_size": 5, "outdoor": True, "workface_id": "west"},
    ], _workfaces(), _windows(), _trigger())
    assert result.valid is False
    assert "uncovered_task_interval:cool" in result.errors


def test_indoor_tasks_are_zero_without_thermal_evidence():
    result = calculate_scheduled_high_heat_crew_hours([
        {"id": "indoor", "start": "2025-07-15T06:00:00+00:00", "end": "2025-07-15T08:00:00+00:00", "crew_size": 5, "outdoor": False, "workface_id": "missing"},
    ], _workfaces(), [], _trigger())
    assert result.valid is False
    assert result.errors == ("schedule_aligned_exceedance_windows_required",)


def test_fail_closed_for_units_and_heat_index_threshold():
    bad_window = [{**_windows()[0], "units": "celsius"}]
    try:
        calculate_scheduled_high_heat_crew_hours([], _workfaces(), bad_window, _trigger())
    except ShhchContractError as exc:
        assert "units" in str(exc)
    else:
        raise AssertionError("wrong exceedance units were accepted")
    try:
        calculate_scheduled_high_heat_crew_hours([], _workfaces(), _windows(), {**_trigger(), "quantity": "heat_index"})
    except ShhchContractError as exc:
        assert "heat_index" in str(exc)
    else:
        raise AssertionError("heat-index trigger was accepted as FortyGuard threshold")

