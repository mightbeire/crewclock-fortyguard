from __future__ import annotations

"""Truthful, bounded site geometry for operator-created shifts.

The operator supplies a real latitude/longitude anchor and approximate site
dimensions.  This module derives a small rectangular AOI and four deterministic
workfaces.  It never geocodes a city label or claims surveyed precision.
"""

from dataclasses import dataclass
import math
from typing import Any


class SiteGeometryError(ValueError):
    pass


US_LATITUDE = (24.0, 50.0)
US_LONGITUDE = (-125.0, -66.0)
MIN_SITE_METERS = 20.0
MAX_SITE_METERS = 1_000.0


@dataclass(frozen=True)
class SiteGeometry:
    aoi: dict[str, Any]
    workfaces: tuple[dict[str, Any], ...]
    latitude: float
    longitude: float
    width_m: float
    height_m: float
    precision: str = "APPROXIMATE_OPERATOR_ANCHOR_DERIVED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "aoi": self.aoi,
            "workfaces": list(self.workfaces),
            "anchor": {"latitude": self.latitude, "longitude": self.longitude},
            "dimensions_m": {"width": self.width_m, "height": self.height_m},
            "precision": self.precision,
        }


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise SiteGeometryError(f"{field}_must_be_finite_number")
    return float(value)


def validate_anchor(latitude: Any, longitude: Any) -> tuple[float, float]:
    lat, lon = _finite(latitude, "latitude"), _finite(longitude, "longitude")
    if not US_LATITUDE[0] <= lat <= US_LATITUDE[1]:
        raise SiteGeometryError("latitude_must_be_in_supported_us_range")
    if not US_LONGITUDE[0] <= lon <= US_LONGITUDE[1]:
        raise SiteGeometryError("longitude_must_be_in_supported_us_range")
    return lat, lon


def _dimension(value: Any, field: str) -> float:
    result = _finite(value, field)
    if not MIN_SITE_METERS <= result <= MAX_SITE_METERS:
        raise SiteGeometryError(f"{field}_must_be_between_{int(MIN_SITE_METERS)}_and_{int(MAX_SITE_METERS)}_meters")
    return result


def _rectangle(latitude: float, longitude: float, width_m: float, height_m: float) -> list[list[float]]:
    # WGS84 degree approximations are appropriate for a bounded site-scale AOI;
    # the disclosure remains approximate because the operator did not provide a
    # surveyed boundary.
    lat_delta = height_m / 111_320.0 / 2.0
    cos_lat = max(0.2, math.cos(math.radians(latitude)))
    lon_delta = width_m / (111_320.0 * cos_lat) / 2.0
    return [
        [longitude - lon_delta, latitude - lat_delta],
        [longitude + lon_delta, latitude - lat_delta],
        [longitude + lon_delta, latitude + lat_delta],
        [longitude - lon_delta, latitude + lat_delta],
        [longitude - lon_delta, latitude - lat_delta],
    ]


def _feature(coords: list[list[float]], *, label: str, precision: str) -> dict[str, Any]:
    return {
        "type": "Feature",
        "properties": {"label": label, "geometry_precision": precision},
        "geometry": {"type": "Polygon", "coordinates": [coords]},
    }


def build_site_geometry(latitude: Any, longitude: Any, width_m: Any = 200, height_m: Any = 200) -> SiteGeometry:
    lat, lon = validate_anchor(latitude, longitude)
    width, height = _dimension(width_m, "site_width"), _dimension(height_m, "site_height")
    outer = _rectangle(lat, lon, width, height)
    lat_delta = (outer[2][1] - outer[0][1]) / 2
    lon_delta = (outer[1][0] - outer[0][0]) / 2
    west, east = lon - lon_delta, lon + lon_delta
    south, north = lat - lat_delta, lat + lat_delta
    mid_lon, mid_lat = lon, lat
    precision = "APPROXIMATE_OPERATOR_ANCHOR_DERIVED"
    faces = (
        ("site-northwest", "Northwest workface", [[west, mid_lat], [mid_lon, mid_lat], [mid_lon, north], [west, north], [west, mid_lat]]),
        ("site-northeast", "Northeast workface", [[mid_lon, mid_lat], [east, mid_lat], [east, north], [mid_lon, north], [mid_lon, mid_lat]]),
        ("site-southwest", "Southwest workface", [[west, south], [mid_lon, south], [mid_lon, mid_lat], [west, mid_lat], [west, south]]),
        ("site-southeast", "Southeast workface", [[mid_lon, south], [east, south], [east, mid_lat], [mid_lon, mid_lat], [mid_lon, south]]),
    )
    workfaces = tuple({
        "id": face_id,
        "label": label,
        "polygon": coords[:-1],
        "geometry": {"type": "Polygon", "coordinates": [coords]},
        "geometry_precision": precision,
        "source": "OPERATOR_ANCHOR_AND_APPROXIMATE_SITE_DIMENSIONS",
    } for face_id, label, coords in faces)
    aoi = {"type": "FeatureCollection", "features": [_feature(outer, label="Operator-entered site AOI", precision=precision)]}
    return SiteGeometry(aoi, workfaces, lat, lon, width, height, precision)


def validate_feature_collection(aoi: Any) -> dict[str, Any]:
    if not isinstance(aoi, dict) or aoi.get("type") != "FeatureCollection":
        raise SiteGeometryError("aoi_must_be_feature_collection")
    features = aoi.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise SiteGeometryError("aoi_must_contain_one_site_feature")
    geometry = features[0].get("geometry") if isinstance(features[0], dict) else None
    if not isinstance(geometry, dict) or geometry.get("type") != "Polygon":
        raise SiteGeometryError("aoi_polygon_required")
    rings = geometry.get("coordinates")
    if not isinstance(rings, list) or len(rings) != 1 or not isinstance(rings[0], list) or len(rings[0]) < 4:
        raise SiteGeometryError("aoi_polygon_ring_required")
    ring = rings[0]
    if ring[0] != ring[-1]:
        raise SiteGeometryError("aoi_polygon_must_be_closed")
    for pair in ring:
        if not isinstance(pair, (list, tuple)) or len(pair) < 2:
            raise SiteGeometryError("aoi_coordinate_pair_invalid")
        validate_anchor(pair[1], pair[0])
    return aoi


def validate_workfaces(workfaces: Any, aoi: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    if not isinstance(workfaces, list) or not workfaces:
        raise SiteGeometryError("workfaces_required")
    validate_feature_collection(aoi)
    ids: set[str] = set()
    result: list[dict[str, Any]] = []
    for face in workfaces:
        if not isinstance(face, dict) or not isinstance(face.get("id"), str) or not face["id"] or face["id"] in ids:
            raise SiteGeometryError("workface_id_must_be_unique")
        ids.add(face["id"])
        polygon = face.get("polygon")
        if not isinstance(polygon, list) or len(polygon) < 3:
            raise SiteGeometryError(f"workface_polygon_required:{face['id']}")
        closed = polygon + [polygon[0]]
        for pair in closed:
            validate_anchor(pair[1], pair[0])
        result.append({**face, "polygon": [list(pair[:2]) for pair in polygon], "geometry_precision": face.get("geometry_precision", "APPROXIMATE_OPERATOR_ANCHOR_DERIVED")})
    return tuple(result)
