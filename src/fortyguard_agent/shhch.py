from __future__ import annotations

"""Deterministic Scheduled High-Heat Crew-Hours (SHHCH) calculation.

The input signal is a FortyGuard ``analytic_type=exceedance`` heatmap.  The
heatmap's per-tile duration is first aggregated over the task workface and is
then intersected with the task's actual scheduled interval.  No environmental
parameter range, heat-index value, or LLM-produced arithmetic is accepted as
the duration source.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Iterable

from .thermal import ThermalContractError, area_weighted_tile_value


class ShhchContractError(ThermalContractError):
    """The evidence or schedule cannot support a safe SHHCH calculation."""


@dataclass(frozen=True)
class ProjectThermalTrigger:
    threshold_c: float
    quantity: str = "fortyguard_modeled_temperature"
    provenance: str = ""

    def __post_init__(self) -> None:
        if isinstance(self.threshold_c, bool) or not isfinite(float(self.threshold_c)):
            raise ShhchContractError("project_thermal_trigger_threshold_required")
        if self.quantity.lower() in {"heat_index", "wbgt", "apparent_temperature"}:
            raise ShhchContractError("project_thermal_trigger_must_not_be_heat_index")
        if self.quantity not in {"fortyguard_modeled_temperature", "fortyguard_tcm_temperature"}:
            raise ShhchContractError("unsupported_project_thermal_trigger_quantity")
        if not self.provenance.strip():
            raise ShhchContractError("project_thermal_trigger_provenance_required")


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


@dataclass(frozen=True)
class ShhchResult:
    status: str
    valid: bool
    total_crew_hours: float
    contributions: tuple[ShhchTaskContribution, ...]
    provenance: tuple[str, ...]
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "valid": self.valid,
            "decision_relevant_result": "SHHCH_READY" if self.valid else "KEEP_CURRENT_PLAN_AND_RECHECK",
            "total_scheduled_high_heat_crew_hours": self.total_crew_hours if self.valid else None,
            "contributions": [
                {
                    "task_id": item.task_id,
                    "workface_id": item.workface_id,
                    "scheduled_start": item.scheduled_start,
                    "scheduled_end": item.scheduled_end,
                    "crew_size": item.crew_size,
                    "overlapping_exceedance_hours": item.overlapping_exceedance_hours,
                    "crew_hours": item.crew_hours,
                    "provenance": list(item.provenance),
                }
                for item in self.contributions
            ],
            "provenance": list(self.provenance),
            "next_allowed_actions": ["COMPARE_SCHEDULE_METRICS"] if self.valid else ["KEEP_CURRENT_PLAN_AND_RECHECK"],
            "errors": list(self.errors),
        }


def _as_datetime(value: Any, field: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ShhchContractError(f"{field}_timestamp_required")
    if parsed.tzinfo is None:
        raise ShhchContractError(f"{field}_timestamp_must_be_timezone_aware")
    return parsed.astimezone(timezone.utc)


def _polygon(value: Any, field: str) -> list[tuple[float, float]]:
    if isinstance(value, dict):
        geometry = value.get("geometry", value)
        coordinates = geometry.get("coordinates") if isinstance(geometry, dict) else None
        if geometry.get("type") == "Polygon" and coordinates:
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
    if not isinstance(value, list):
        raise ShhchContractError(f"{key}_array_required")
    return [item for item in value if isinstance(item, dict)]


def _task_rows(schedule: Any) -> list[dict[str, Any]]:
    if isinstance(schedule, dict):
        tasks = schedule.get("tasks")
        if isinstance(tasks, list):
            return [item for item in tasks if isinstance(item, dict)]
        rows = []
        for task_id, interval in schedule.items():
            if isinstance(interval, dict):
                rows.append({"id": task_id, **interval})
        return rows
    if isinstance(schedule, list):
        return [item for item in schedule if isinstance(item, dict)]
    raise ShhchContractError("schedule_tasks_required")


def _workface_map(workfaces: Any) -> dict[str, list[tuple[float, float]]]:
    rows = _items(workfaces, "workfaces")
    result: dict[str, list[tuple[float, float]]] = {}
    for row in rows:
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
    threshold = value.get("threshold_c", value.get("threshold"))
    try:
        threshold_value = float(threshold)
    except (TypeError, ValueError) as exc:
        raise ShhchContractError("project_thermal_trigger_threshold_required") from exc
    return ProjectThermalTrigger(
        threshold_c=threshold_value,
        quantity=str(value.get("quantity", value.get("metric", "fortyguard_modeled_temperature"))),
        provenance=str(value.get("provenance", value.get("source", ""))),
    )


def _window_tiles(window: dict[str, Any]) -> Iterable[dict[str, Any]]:
    tiles = window.get("tiles", window.get("features"))
    if not isinstance(tiles, list) or not tiles:
        raise ShhchContractError("exceedance_window_tiles_required")
    return tiles


def calculate_scheduled_high_heat_crew_hours(
    schedule: Any,
    workfaces: Any,
    exceedance_windows: Any,
    project_thermal_trigger: ProjectThermalTrigger | dict[str, Any],
) -> ShhchResult:
    """Calculate SHHCH with spatial and temporal overlap, or fail closed.

    Each exceedance window's tile value is an exceedance duration in hours for
    that exact window.  If a task overlaps only part of the window, only that
    fraction of the tile duration is counted.
    """
    trigger = _trigger(project_thermal_trigger)
    tasks = _task_rows(schedule)
    face_map = _workface_map(workfaces)
    windows = _items(exceedance_windows, "exceedance_windows")
    if not windows:
        return ShhchResult("EVIDENCE_UNAVAILABLE", False, 0.0, (), ("FORTYGUARD_EXCEEDANCE", trigger.provenance), ("schedule_aligned_exceedance_windows_required",))

    normalized_windows: list[tuple[datetime, datetime, dict[str, Any], str]] = []
    for index, window in enumerate(windows):
        if window.get("analytic_type") != "exceedance":
            raise ShhchContractError("exceedance_window_analytic_type_required")
        if window.get("valid") is False or str(window.get("status", "VALID")).upper() in {"STALE", "INVALID", "UNAVAILABLE", "NOT_DEMONSTRATED", "COMPLETED_BUT_EMPTY"}:
            raise ShhchContractError("invalid_or_stale_exceedance_evidence")
        units = str(window.get("units", "")).lower()
        if units not in {"hour", "hours"}:
            raise ShhchContractError("exceedance_duration_units_must_be_hours")
        start, end = _as_datetime(window.get("start"), f"exceedance_window_{index}_start"), _as_datetime(window.get("end"), f"exceedance_window_{index}_end")
        if end <= start:
            raise ShhchContractError("exceedance_window_end_must_follow_start")
        provenance = str(window.get("provenance", "")).strip()
        if not provenance:
            raise ShhchContractError("exceedance_provenance_required")
        normalized_windows.append((start, end, window, provenance))

    contributions: list[ShhchTaskContribution] = []
    errors: list[str] = []
    total = 0.0
    for row in tasks:
        task_id = str(row.get("id", ""))
        if not task_id:
            errors.append("task_id_required")
            continue
        if not bool(row.get("outdoor", row.get("environment") not in {"indoor", "shaded-support"})):
            continue
        face_id = row.get("workface_id", row.get("workface", row.get("zone_id", row.get("zoneId"))))
        if not isinstance(face_id, str) or face_id not in face_map:
            errors.append(f"missing_workface:{task_id}")
            continue
        try:
            start = _as_datetime(row.get("start", row.get("scheduled_start")), f"task:{task_id}:start")
            end = _as_datetime(row.get("end", row.get("scheduled_end")), f"task:{task_id}:end")
            crew_size = int(row.get("crew_size", row.get("crewSize")))
            if crew_size <= 0 or end <= start:
                raise ShhchContractError(f"invalid_task_interval_or_crew_size:{task_id}")
        except (TypeError, ValueError, ShhchContractError) as exc:
            errors.append(str(exc))
            continue

        task_exceedance = 0.0
        task_sources: list[str] = []
        for window_start, window_end, window, provenance in normalized_windows:
            overlap_start, overlap_end = max(start, window_start), min(end, window_end)
            if overlap_end <= overlap_start:
                continue
            window_hours = (window_end - window_start).total_seconds() / 3600
            weighted_hours = area_weighted_tile_value(face_map[face_id], _window_tiles(window), "value")
            if weighted_hours < 0 or not isfinite(weighted_hours):
                raise ShhchContractError("exceedance_duration_must_be_nonnegative_finite")
            overlap_fraction = (overlap_end - overlap_start).total_seconds() / (window_end - window_start).total_seconds()
            task_exceedance += weighted_hours * overlap_fraction
            task_sources.append(provenance)
        if not task_sources:
            errors.append(f"uncovered_task_interval:{task_id}")
            continue
        crew_hours = round(task_exceedance * crew_size, 6)
        total += crew_hours
        contributions.append(ShhchTaskContribution(task_id, face_id, start.isoformat(), end.isoformat(), crew_size, round(task_exceedance, 6), crew_hours, tuple(sorted(set(task_sources)))))

    if errors:
        return ShhchResult("EVIDENCE_UNAVAILABLE", False, 0.0, tuple(contributions), ("FORTYGUARD_EXCEEDANCE", trigger.provenance), tuple(errors))
    return ShhchResult("SHHCH_READY", True, round(total, 6), tuple(contributions), ("FORTYGUARD_EXCEEDANCE", trigger.provenance), ())
