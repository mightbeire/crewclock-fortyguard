from __future__ import annotations

"""Deterministic thermal evidence and workface calculations.

FortyGuard is an environmental signal.  This module deliberately keeps the
planning metric separate from physiological exposure, WBGT, and legal
compliance.  The only schedule metric in the MVP is interval overlap with an
employer-configured trigger.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Iterable, Literal


class ThermalContractError(ValueError):
    """The provider response cannot be interpreted safely."""


@dataclass(frozen=True)
class ThermalTrigger:
    name: str
    start: datetime
    end: datetime
    threshold_c: float | None
    source: Literal["employer_configured", "derived"]
    provenance: str

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ThermalContractError("trigger_timestamps_must_be_timezone_aware")
        if self.end <= self.start:
            raise ThermalContractError("trigger_end_must_follow_start")


@dataclass(frozen=True)
class ThermalOverlap:
    overlaps: bool
    overlap_minutes: int
    crew_hours: float
    evidence_source: str
    confidence: Literal["covered", "partial", "unavailable"]
    trigger_name: str


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
        raise ThermalContractError(f"{field}_must_be_finite_number")
    return float(value)


def assert_heatmap_schema(result: dict[str, Any], analytic_type: str = "tcm", *, allow_empty_analysis: bool = False) -> None:
    """Fail closed on the current documented heatmap schemas and units.

    A completed analytic heatmap may legitimately contain zero cells when no
    exceedance was found.  Callers must opt into that interpretation because
    an empty map is otherwise indistinguishable from an incomplete fixture.
    """
    map_data = result.get("map_data")
    if not isinstance(map_data, dict) or map_data.get("type") != "FeatureCollection":
        raise ThermalContractError("heatmap_map_data_must_be_feature_collection")
    features = map_data.get("features")
    if not isinstance(features, list):
        raise ThermalContractError("heatmap_features_must_be_array")
    if not features and not (allow_empty_analysis and analytic_type != "tcm"):
        raise ThermalContractError("heatmap_empty_feature_collection")
    stats = result.get("stats_data") or {}
    if analytic_type == "tcm":
        for feature in features:
            properties = feature.get("properties") or {}
            if not {"average_temperature", "min_temperature", "max_temperature"}.issubset(properties):
                raise ThermalContractError("tcm_tile_temperature_fields_missing")
            for key in ("average_temperature", "min_temperature", "max_temperature"):
                _number(properties[key], f"tcm_{key}")
        # The current API contract and successful live responses use Celsius.
        units = stats.get("units", "celsius")
        if str(units).lower() not in {"celsius", "°c", "deg_c", "c"}:
            raise ThermalContractError(f"tcm_units_not_celsius:{units}")
        return
    if analytic_type not in {"time_of_measure", "exceedance", "persistence"}:
        raise ThermalContractError(f"unsupported_heatmap_analytic_type:{analytic_type}")
    if stats.get("analytic_type") not in {None, analytic_type}:
        raise ThermalContractError("heatmap_analysis_type_mismatch")
    if not features:
        if stats.get("n_cells") not in {0, None}:
            raise ThermalContractError("heatmap_empty_feature_collection_count_mismatch")
        return
    if str(stats.get("units", "")).lower() not in {"hour", "hours"}:
        raise ThermalContractError("heatmap_analysis_units_must_be_hours")
    for feature in features:
        _number((feature.get("properties") or {}).get("value"), "heatmap_analysis_value")


def assert_env_params_schema(result: dict[str, Any], *, expected_timestamp: datetime | None = None) -> None:
    metadata = result.get("metadata") or {}
    timestamps = metadata.get("timestamps")
    locations = result.get("locations")
    if not isinstance(timestamps, list) or not timestamps:
        raise ThermalContractError("env_params_timestamps_missing")
    if not isinstance(locations, list) or not locations:
        raise ThermalContractError("env_params_locations_missing")
    if expected_timestamp is not None:
        parsed = datetime.fromisoformat(str(timestamps[0]).replace("Z", "+00:00"))
        if parsed.tzinfo is None or expected_timestamp.tzinfo is None:
            raise ThermalContractError("env_params_timestamp_must_be_timezone_aware")
        if parsed.astimezone(timezone.utc) != expected_timestamp.astimezone(timezone.utc):
            raise ThermalContractError("env_params_timestamp_not_time_matched")
    parameters = locations[0].get("parameters") or {}
    for key, values in parameters.items():
        if not isinstance(values, list):
            raise ThermalContractError(f"env_params_parameter_not_array:{key}")
        for value in values:
            if value is not None:
                _number(value, f"env_params_{key}")


def calculate_thermal_overlap(
    task_start: datetime,
    task_end: datetime,
    trigger: ThermalTrigger,
    crew_size: int,
    *,
    evidence_source: str,
    confidence: Literal["covered", "partial", "unavailable"] = "covered",
) -> ThermalOverlap:
    if task_start.tzinfo is None or task_end.tzinfo is None:
        raise ThermalContractError("task_timestamps_must_be_timezone_aware")
    if task_end <= task_start or crew_size <= 0:
        return ThermalOverlap(False, 0, 0.0, evidence_source, confidence, trigger.name)
    overlap = max(0.0, (min(task_end, trigger.end) - max(task_start, trigger.start)).total_seconds() / 60)
    minutes = int(round(overlap))
    return ThermalOverlap(
        overlaps=minutes > 0,
        overlap_minutes=minutes,
        crew_hours=round(minutes / 60 * crew_size, 4),
        evidence_source=evidence_source,
        confidence=confidence,
        trigger_name=trigger.name,
    )


def scheduled_high_heat_crew_hours(rows: Iterable[dict[str, Any]], trigger: ThermalTrigger) -> float:
    total = 0.0
    for row in rows:
        start = row["start"] if isinstance(row["start"], datetime) else datetime.fromisoformat(row["start"])
        end = row["end"] if isinstance(row["end"], datetime) else datetime.fromisoformat(row["end"])
        result = calculate_thermal_overlap(
            start, end, trigger, int(row["crew_size"]),
            evidence_source=str(row.get("evidence_source", "derived")),
            confidence=row.get("confidence", "covered"),
        )
        if row.get("outdoor", True) and not row.get("fixed", False):
            total += result.crew_hours
    return round(total, 4)


def _area(polygon: list[tuple[float, float]]) -> float:
    return abs(sum(polygon[i][0] * polygon[(i + 1) % len(polygon)][1] - polygon[(i + 1) % len(polygon)][0] * polygon[i][1] for i in range(len(polygon))) / 2)


def _clip(subject: list[tuple[float, float]], edge_a: tuple[float, float], edge_b: tuple[float, float], sign: float) -> list[tuple[float, float]]:
    if not subject:
        return []
    out: list[tuple[float, float]] = []

    def cross(point: tuple[float, float]) -> float:
        return (edge_b[0] - edge_a[0]) * (point[1] - edge_a[1]) - (edge_b[1] - edge_a[1]) * (point[0] - edge_a[0])

    def inside(point: tuple[float, float]) -> bool:
        return sign * cross(point) >= -1e-12

    for current, following in zip(subject, subject[1:] + subject[:1]):
        current_inside, following_inside = inside(current), inside(following)
        if current_inside and following_inside:
            out.append(following)
        elif current_inside and not following_inside:
            c, f = cross(current), cross(following)
            ratio = c / (c - f) if c != f else 0.0
            out.append((current[0] + (following[0] - current[0]) * ratio, current[1] + (following[1] - current[1]) * ratio))
        elif not current_inside and following_inside:
            c, f = cross(current), cross(following)
            ratio = c / (c - f) if c != f else 0.0
            out.append((current[0] + (following[0] - current[0]) * ratio, current[1] + (following[1] - current[1]) * ratio))
            out.append(following)
    return out


def _intersection_area(subject: list[tuple[float, float]], clipper: list[tuple[float, float]]) -> float:
    if len(subject) < 3 or len(clipper) < 3:
        return 0.0
    signed = sum(clipper[i][0] * clipper[(i + 1) % len(clipper)][1] - clipper[(i + 1) % len(clipper)][0] * clipper[i][1] for i in range(len(clipper)))
    result = subject
    sign = 1.0 if signed >= 0 else -1.0
    for index, edge_a in enumerate(clipper):
        result = _clip(result, edge_a, clipper[(index + 1) % len(clipper)], sign)
    return _area(result) if result else 0.0


def _point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    inside = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > point[1]) != (b[1] > point[1]) and point[0] < (b[0] - a[0]) * (point[1] - a[1]) / (b[1] - a[1]) + a[0]:
            inside = not inside
    return inside


def area_weighted_tile_value(workface: list[tuple[float, float]], tiles: Iterable[dict[str, Any]], value_key: str = "value") -> float:
    """Aggregate a workface over all overlapping convex heatmap tiles."""
    if len(workface) < 3:
        raise ThermalContractError("workface_polygon_required")
    total_area = 0.0
    weighted = 0.0
    for tile in tiles:
        geometry = tile.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        if geometry.get("type") != "Polygon" or not coordinates or len(coordinates[0]) < 4:
            raise ThermalContractError("heatmap_tile_polygon_required")
        polygon = [tuple(map(float, pair[:2])) for pair in coordinates[0][:-1]]
        properties = tile.get("properties") or {}
        value = properties.get(value_key)
        if value is None:
            raise ThermalContractError(f"tile_value_missing:{value_key}")
        overlap = _intersection_area(workface, polygon)
        total_area += overlap
        weighted += overlap * _number(value, value_key)
    if total_area <= 0:
        raise ThermalContractError("workface_does_not_overlap_heatmap_tiles")
    return round(weighted / total_area, 6)


def point_tile_value(point: tuple[float, float], tiles: Iterable[dict[str, Any]], value_key: str = "value") -> float:
    for tile in tiles:
        coordinates = (tile.get("geometry") or {}).get("coordinates") or []
        polygon = [tuple(map(float, pair[:2])) for pair in (coordinates[0][:-1] if coordinates else [])]
        if polygon and _point_in_polygon(point, polygon):
            return _number((tile.get("properties") or {}).get(value_key), value_key)
    raise ThermalContractError("point_does_not_overlap_heatmap_tiles")


def env_params_role() -> str:
    return "Selective time-matched environmental context only; never a spatial ranking engine or diurnal exposure forecast."
