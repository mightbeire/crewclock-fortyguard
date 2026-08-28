from __future__ import annotations

from pathlib import Path

from fortyguard_agent.cache import JsonCache
from fortyguard_agent.guardrails import FortyGuardRequestGuard
from fortyguard_agent.site_geometry import SiteGeometryError, acquisition_aoi_for_workfaces, build_site_geometry
from fortyguard_agent.toolkit import FortyGuardToolkit


def _request(site: dict, *, date: str = "2025-07-15") -> dict:
    return {
        "project_id": "new-site-test",
        "location": "Raleigh, North Carolina",
        "polygon_aoi": site["aoi"],
        "workfaces": site["workfaces"],
        "date": date,
        "timezone": "America/New_York",
        "start_time": "06:00",
        "end_time": "10:00",
        "threshold": 32.0,
        "analytic_type": "exceedance",
        "direction": "above",
        "granularity": 100,
    }


class FakeFortyGuard:
    def __init__(self, site: dict, *, failed: bool = False) -> None:
        self.site = site
        self.failed = failed
        self.create_calls: list[dict] = []
        self.status_calls = 0

    def create_heatmap(self, **kwargs):
        self.create_calls.append(kwargs)
        return "activity-new-site"

    def get_status(self, activity_id: str) -> dict:
        self.status_calls += 1
        if self.failed:
            return {"status": "failed", "message": "provider rejected request"}
        if self.status_calls == 1:
            return {"status": "processing"}
        polygon = self.site["workfaces"][0]["polygon"]
        ring = polygon + [polygon[0]]
        return {"status": "Completed", "result": {"map_data": {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]}, "properties": {"value": 2.0}}]}, "stats_data": {"analytic_type": "exceedance", "units": "hours", "n_cells": 1}}}


class EmptyCompletedFortyGuard(FakeFortyGuard):
    def get_status(self, activity_id: str) -> dict:
        return {"status": "Completed", "result": {"map_data": {"type": "FeatureCollection", "features": []}, "stats_data": {"analytic_type": "exceedance", "n_cells": 0}}}


def test_site_geometry_is_closed_bounded_and_explicit() -> None:
    site = build_site_geometry(35.7796, -78.6382, 200, 160)
    ring = site.aoi["features"][0]["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1]
    assert len(site.workfaces) == 4
    assert all(face["geometry_precision"] == "APPROXIMATE_OPERATOR_ANCHOR_DERIVED" for face in site.workfaces)
    assert all(face["polygon"][0] != face["polygon"][-1] for face in site.workfaces)


def test_site_geometry_rejects_city_without_real_anchor() -> None:
    try:
        build_site_geometry("Raleigh", "North Carolina", 200, 200)
    except SiteGeometryError as exc:
        assert "latitude" in str(exc)
    else:
        raise AssertionError("city labels must not be accepted as coordinates")


def test_live_acquisition_submits_polls_validates_and_caches(tmp_path: Path) -> None:
    site = build_site_geometry(35.7796, -78.6382, 200, 160).to_dict()
    client = FakeFortyGuard(site)
    toolkit = FortyGuardToolkit(client, JsonCache(tmp_path), FortyGuardRequestGuard(remaining_credits=100_000, max_run_credits=10_000))
    statuses: list[str] = []
    result = toolkit.acquire_workface_thermal_evidence(_request(site), on_status=lambda status, _: statuses.append(status))
    assert result.ok
    assert result.provenance.source == "live"
    assert result.data["status"] == "LIVE_ACQUIRED"
    assert result.data["exceedanceWindows"][0]["projectThermalTrigger"]["thresholdC"] == 32
    assert result.data["exceedanceWindows"][0]["analyticType"] == "exceedance"
    assert client.create_calls[0]["analytic_type"] == "exceedance"
    assert client.create_calls[0]["threshold"] == 32.0
    assert client.create_calls[0]["direction"] == "above"
    assert "processing" in statuses

    reused = toolkit.acquire_workface_thermal_evidence(_request(site))
    assert reused.ok
    assert reused.provenance.source == "cached"
    assert reused.data["status"] == "LIVE_CACHE_REUSED"
    assert len(client.create_calls) == 1

    changed = toolkit.acquire_workface_thermal_evidence(_request(site, date="2025-07-16"))
    assert changed.ok
    assert len(client.create_calls) == 2


def test_failed_activity_is_unavailable_not_zero_heat(tmp_path: Path) -> None:
    site = build_site_geometry(35.7796, -78.6382, 200, 160).to_dict()
    client = FakeFortyGuard(site, failed=True)
    toolkit = FortyGuardToolkit(client, JsonCache(tmp_path), FortyGuardRequestGuard(remaining_credits=100_000, max_run_credits=10_000))
    result = toolkit.acquire_workface_thermal_evidence(_request(site))
    assert not result.ok
    assert result.data["status"] == "EVIDENCE_UNAVAILABLE"
    assert result.data["thermal_evidence_valid"] is False
    assert result.data.get("total_scheduled_high_heat_crew_hours") is None


def test_completed_empty_exceedance_map_is_valid_no_overlap(tmp_path: Path) -> None:
    site = build_site_geometry(35.7796, -78.6382, 200, 160).to_dict()
    client = EmptyCompletedFortyGuard(site)
    toolkit = FortyGuardToolkit(client, JsonCache(tmp_path), FortyGuardRequestGuard(remaining_credits=100_000, max_run_credits=10_000))
    result = toolkit.acquire_workface_thermal_evidence(_request(site))
    assert result.ok
    assert result.data["status"] == "LIVE_ACQUIRED"
    assert result.data["decisionGradeThermalEvidence"] is True
    assert result.data["featureCount"] == 0
    assert result.data["maxValueHours"] == 0
    assert result.data["exceedanceWindows"][0]["qualifying"] is False


def test_selected_workface_geometry_is_the_actual_provider_payload_and_cache_identity(tmp_path: Path) -> None:
    site = build_site_geometry(35.7796, -78.6382, 200, 160).to_dict()
    selected = [site["workfaces"][0]]
    provider_aoi = acquisition_aoi_for_workfaces(selected, site["aoi"])
    request = _request(site)
    request.update({
        "polygon_aoi": provider_aoi,
        "project_aoi": site["aoi"],
        "workfaces": selected,
        "workface_ids": [selected[0]["id"]],
    })
    client = FakeFortyGuard(site)
    toolkit = FortyGuardToolkit(client, JsonCache(tmp_path), FortyGuardRequestGuard(remaining_credits=100_000, max_run_credits=10_000))
    result = toolkit.acquire_workface_thermal_evidence(request)
    assert result.ok
    assert client.create_calls[0]["polygon_aoi"] == provider_aoi
    assert client.create_calls[0]["polygon_aoi"] != site["aoi"]
    assert result.data["exceedanceWindows"][0]["workfaceIds"] == [selected[0]["id"]]

    mismatched = dict(request)
    mismatched["polygon_aoi"] = site["aoi"]
    rejected = toolkit.acquire_workface_thermal_evidence(mismatched)
    assert not rejected.ok
    assert "acquisition_aoi_must_match_selected_workfaces" in (rejected.error or "")
