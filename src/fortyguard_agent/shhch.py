from __future__ import annotations

"""Deterministic Scheduled High-Heat Crew-Hours (SHHCH).

Evidence coverage and qualifying intervals are separate concepts: a covered
cool interval contributes zero; an uncovered interval is unavailable.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Iterable

from .thermal import ThermalContractError, area_weighted_tile_value


class ShhchContractError(ThermalContractError):
    pass


@dataclass(frozen=True)
class ProjectThermalTrigger:
    threshold_c: float
    quantity: str = "fortyguard_modeled_temperature"
    provenance: str = ""
    threshold_units: str = "celsius"
    direction: str = "above"

    def __post_init__(self) -> None:
        if isinstance(self.threshold_c, bool) or not isfinite(float(self.threshold_c)):
            raise ShhchContractError("project_thermal_trigger_threshold_required")
        if self.quantity.lower() in {"heat_index", "wbgt", "apparent_temperature"}:
            raise ShhchContractError("project_thermal_trigger_must_not_be_heat_index")
        if self.quantity not in {"fortyguard_modeled_temperature", "fortyguard_tcm_temperature"}:
            raise ShhchContractError("unsupported_project_thermal_trigger_quantity")
        if not self.provenance.strip() or self.threshold_units.lower() != "celsius" or self.direction != "above":
            raise ShhchContractError("project_thermal_trigger_binding_required")


@dataclass(frozen=True)
class ShhchTaskContribution:
    task_id: str
    workface_id: str | None
    scheduled_start: str | None
    scheduled_end: str | None
    crew_size: int
    overlapping_exceedance_hours: float
    crew_hours: float
    provenance: tuple[str, ...]
    fixed: bool = False


@dataclass(frozen=True)
class ShhchResult:
    status: str
    valid: bool
    total_crew_hours: float
    contributions: tuple[ShhchTaskContribution, ...]
    provenance: tuple[str, ...]
    errors: tuple[str, ...] = ()
    movable_crew_hours: float = 0.0
    fixed_crew_hours: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status, "valid": self.valid,
            "decision_relevant_result": "SHHCH_READY" if self.valid else "KEEP_CURRENT_PLAN_AND_RECHECK",
            "total_scheduled_high_heat_crew_hours": self.total_crew_hours if self.valid else None,
            "TOTAL_SHHCH": self.total_crew_hours if self.valid else None,
            "MOVABLE_SHHCH": self.movable_crew_hours if self.valid else None,
            "FIXED_SHHCH": self.fixed_crew_hours if self.valid else None,
            "contributions": [{"task_id": item.task_id, "workface_id": item.workface_id, "scheduled_start": item.scheduled_start, "scheduled_end": item.scheduled_end, "crew_size": item.crew_size, "overlapping_exceedance_hours": item.overlapping_exceedance_hours, "crew_hours": item.crew_hours, "fixed": item.fixed, "provenance": list(item.provenance)} for item in self.contributions],
            "provenance": list(self.provenance), "next_allowed_actions": ["COMPARE_SCHEDULE_METRICS"] if self.valid else ["KEEP_CURRENT_PLAN_AND_RECHECK"], "errors": list(self.errors),
        }


def _as_datetime(value: Any, field: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ShhchContractError(f"{field}_timestamp_invalid") from exc
    else:
        raise ShhchContractError(f"{field}_timestamp_required")
    if parsed.tzinfo is None:
        raise ShhchContractError(f"{field}_timestamp_must_be_timezone_aware")
    return parsed.astimezone(timezone.utc)


def _polygon(value: Any, field: str) -> list[tuple[float, float]]:
    if isinstance(value, dict):
        geometry = value.get("geometry", value)
        coordinates = geometry.get("coordinates") if isinstance(geometry, dict) else None
        if isinstance(geometry, dict) and geometry.get("type") == "Polygon" and coordinates:
            value = coordinates[0]
    if not isinstance(value, (list, tuple)) or len(value) < 3:
        raise ShhchContractError(f"{field}_polygon_required")
    try:
        return [(float(pair[0]), float(pair[1])) for pair in value]
    except (TypeError, ValueError, IndexError) as exc:
        raise ShhchContractError(f"{field}_polygon_invalid") from exc


def _items(value: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        value = value.get(key, value.get("items", []))
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ShhchContractError(f"{key}_array_required")
    return value


def _task_rows(schedule: Any) -> list[dict[str, Any]]:
    if isinstance(schedule, dict) and isinstance(schedule.get("tasks"), list):
        return _items(schedule, "tasks")
    if isinstance(schedule, list):
        return _items(schedule, "tasks")
    raise ShhchContractError("schedule_tasks_required")


def _workface_map(workfaces: Any) -> dict[str, list[tuple[float, float]]]:
    result: dict[str, list[tuple[float, float]]] = {}
    for row in _items(workfaces, "workfaces"):
        key = row.get("id", row.get("workface_id"))
        if not isinstance(key, str):
            raise ShhchContractError("workface_id_required")
        result[key] = _polygon(row.get("polygon", row.get("geometry", row)), f"workface:{key}")
    return result


def _trigger(value: ProjectThermalTrigger | dict[str, Any]) -> ProjectThermalTrigger:
    if isinstance(value, ProjectThermalTrigger):
        return value
    if not isinstance(value, dict):
        raise ShhchContractError("project_thermal_trigger_required")
    return ProjectThermalTrigger(float(value.get("threshold_c", value.get("threshold"))), str(value.get("quantity", value.get("metric", "fortyguard_modeled_temperature"))), str(value.get("provenance", value.get("source", ""))), str(value.get("threshold_units", value.get("units", "celsius"))), str(value.get("direction", "above")))


def _validate_binding(window: dict[str, Any], trigger: ProjectThermalTrigger, index: int) -> None:
    required = ("aoi", "date", "timezone", "analytic_source", "project_thermal_trigger", "result_hash", "version")
    if any(not window.get(key) for key in required) or not window.get("provenance"):
        raise ShhchContractError(f"exceedance_window_{index}_binding_required")
    binding = window["project_thermal_trigger"]
    if not isinstance(binding, dict) or float(binding.get("threshold_c", binding.get("threshold"))) != float(trigger.threshold_c) or str(binding.get("threshold_units", binding.get("units", ""))).lower() != trigger.threshold_units.lower() or str(binding.get("direction", "")) != trigger.direction or str(binding.get("quantity", "")) != trigger.quantity:
        raise ShhchContractError("exceedance_threshold_does_not_match_project_trigger")


def calculate_scheduled_high_heat_crew_hours(schedule: Any, workfaces: Any, exceedance_windows: Any, project_thermal_trigger: ProjectThermalTrigger | dict[str, Any]) -> ShhchResult:
    trigger = _trigger(project_thermal_trigger)
    tasks, face_map, windows = _task_rows(schedule), _workface_map(workfaces), _items(exceedance_windows, "exceedance_windows")
    if not windows:
        return ShhchResult("EVIDENCE_UNAVAILABLE", False, 0.0, (), ("FORTYGUARD_EXCEEDANCE", trigger.provenance), ("schedule_aligned_exceedance_windows_required",))
    normalized: list[tuple[datetime, datetime, dict[str, Any], str]] = []
    for index, window in enumerate(windows):
        if window.get("analytic_type") != "exceedance" or str(window.get("units", "")).lower() not in {"hour", "hours"} or window.get("valid") is False or str(window.get("status", "VALID")).upper() != "VALID":
            raise ShhchContractError("invalid_or_stale_exceedance_evidence")
        _validate_binding(window, trigger, index)
        start, end = _as_datetime(window.get("start"), f"exceedance_window_{index}_start"), _as_datetime(window.get("end"), f"exceedance_window_{index}_end")
        if end <= start:
            raise ShhchContractError("exceedance_window_end_must_follow_start")
        normalized.append((start, end, window, str(window["provenance"])))

    contributions: list[ShhchTaskContribution] = []
    errors: list[str] = []
    total = movable = fixed = 0.0
    for row in tasks:
        task_id = row.get("id")
        if not isinstance(task_id, str) or not task_id:
            errors.append("task_id_required")
            continue
        if not bool(row.get("outdoor", row.get("environment") not in {"indoor", "shaded-support"})):
            continue
        face_id = row.get("workface_id", row.get("workface", row.get("zone_id", row.get("zoneId"))))
        if not isinstance(face_id, str) or face_id not in face_map:
            errors.append(f"missing_workface:{task_id}")
            continue
        try:
            start, end = _as_datetime(row.get("start", row.get("scheduled_start")), f"task:{task_id}:start"), _as_datetime(row.get("end", row.get("scheduled_end")), f"task:{task_id}:end")
            crew_size = int(row.get("crew_size", row.get("crewSize")))
            if crew_size <= 0 or end <= start:
                raise ShhchContractError("invalid_task_interval_or_crew_size")
        except (TypeError, ValueError, ShhchContractError) as exc:
            errors.append(f"{task_id}:{exc}")
            continue
        # Full schedule coverage is required.  Qualifying windows are then
        # normalized as a union; overlapping windows cannot double count.
        boundaries = {start, end}
        for window_start, window_end, _, _ in normalized:
            boundaries.add(max(start, window_start)); boundaries.add(min(end, window_end))
        points = sorted(point for point in boundaries if start <= point <= end)
        if any(not any(window_start <= left and right <= window_end for window_start, window_end, _, _ in normalized) for left, right in zip(points, points[1:]) if right > left):
            errors.append(f"uncovered_task_interval:{task_id}")
            continue
        exceedance = 0.0
        sources: set[str] = set()
        for left, right in zip(points, points[1:]):
            if right <= left:
                continue
            rates: list[tuple[float, str]] = []
            for window_start, window_end, window, provenance in normalized:
                if window_start <= left and right <= window_end:
                    window_duration = (window_end - window_start).total_seconds() / 3600
                    weighted = area_weighted_tile_value(face_map[face_id], window.get("tiles", window.get("features", [])), "value")
                    rate = max(0.0, min(1.0, weighted / window_duration))
                    if window.get("qualifying") is False:
                        rate = 0.0
                    rates.append((rate, provenance))
            if rates:
                rate, _ = max(rates, key=lambda item: item[0])
                exceedance += (right - left).total_seconds() / 3600 * rate
                sources.update(provenance for _, provenance in rates)
        crew_hours = round(exceedance * crew_size, 6)
        is_fixed = bool(row.get("fixed", False))
        total += crew_hours
        fixed += crew_hours if is_fixed else 0.0
        movable += 0.0 if is_fixed else crew_hours
        contributions.append(ShhchTaskContribution(task_id, face_id, start.isoformat(), end.isoformat(), crew_size, round(exceedance, 6), crew_hours, tuple(sorted(sources)), is_fixed))
    if errors:
        return ShhchResult("EVIDENCE_UNAVAILABLE", False, 0.0, tuple(contributions), ("FORTYGUARD_EXCEEDANCE", trigger.provenance), tuple(errors), 0.0, 0.0)
    return ShhchResult("SHHCH_READY", True, round(total, 6), tuple(contributions), ("FORTYGUARD_EXCEEDANCE", trigger.provenance), (), round(movable, 6), round(fixed, 6))
