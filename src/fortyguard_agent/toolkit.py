from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from .cache import JsonCache, request_hash
from .guardrails import FortyGuardRequestGuard, GuardrailError
from .models import Provenance, ToolResult
from .state_machine import deterministic_decision_result
from .thermal import ThermalContractError, assert_env_params_schema, assert_heatmap_schema, env_params_role


class FortyGuardToolkit:
    """Safe adapter around the vendored FortyGuard client plus derived tools.

    Live calls are opt-in: callers must pass a client. Offline fixtures are
    explicit and always carry ``sample`` provenance.
    """

    def __init__(self, client: Any | None = None, cache: JsonCache | None = None, request_guard: FortyGuardRequestGuard | None = None) -> None:
        self.client = client
        self.cache = cache or JsonCache()
        self.request_guard = request_guard or FortyGuardRequestGuard()

    def _cached_or_live(self, endpoint: str, payload: dict[str, Any], call: Any, *, request_at: Any = None) -> ToolResult:
        key = request_hash(endpoint, payload)
        cached = self.cache.get(key)
        if cached is not None:
            return ToolResult(
                data=cached["data"],
                provenance=Provenance(source="cached", endpoint=endpoint, request_hash=key, activity_id=cached.get("activity_id"), assumptions=tuple(cached.get("assumptions", []))),
                estimated_credits=0,
            )
        if self.client is None:
            return ToolResult(
                data={},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key),
                error="live_client_not_configured",
            )
        try:
            estimated = self.request_guard.validate(endpoint, payload, request_at=request_at)
            raw = call()
            result = raw.get("result", raw) if isinstance(raw, dict) else raw
            activity_id = raw.get("activity_id") if isinstance(raw, dict) else None
            if endpoint == "/v1/heatmap":
                analytic_type = str(payload.get("analytic_type", "tcm"))
                assert_heatmap_schema(result, analytic_type)
            if endpoint == "/v1/env_params":
                assert_env_params_schema(result)
            self.cache.put_success(key, endpoint=endpoint, request=payload, data=result, provenance={"activity_id": activity_id, "provenance": "LIVE", "assumptions": []})
            self.request_guard.commit(estimated)
            return ToolResult(
                data=result if isinstance(result, dict) else {"result": result},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key, activity_id=activity_id),
                estimated_credits=estimated,
            )
        except ThermalContractError as exc:
            return ToolResult(
                data={"state": "INVALID_EVIDENCE", "reason": str(exc)},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key),
                error=str(exc),
            )
        except Exception as exc:  # adapter boundary: expose a traceable error, never a secret
            return ToolResult(
                data={},
                provenance=Provenance(source="live", endpoint=endpoint, request_hash=key),
                error=f"{type(exc).__name__}: {str(exc)[:240]}",
            )

    def get_heatmap(self, arguments: dict[str, Any]) -> ToolResult:
        payload = dict(arguments)
        fixture = payload.pop("fixture", None)
        if fixture:
            return self.load_fixture(fixture, endpoint="/v1/heatmap")
        if self.client is None:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/heatmap"), error="live_client_not_configured")
        try:
            request_at = self.request_guard.heatmap_request_at(payload)
            self.request_guard.validate("/v1/heatmap", payload, request_at=request_at)
        except GuardrailError as exc:
            return ToolResult({}, Provenance(source="derived", endpoint="/v1/heatmap"), error=str(exc))
        return self._cached_or_live("/v1/heatmap", payload, lambda: self.client.create_heatmap(**payload, verbose=False), request_at=request_at)

    def get_workface_thermal_evidence(self, arguments: dict[str, Any]) -> ToolResult:
        """Return compact cached-live evidence; this tool cannot submit a request."""
        fixture = arguments.get("fixture")
        endpoint = "/v1/heatmap"
        if not fixture:
            return ToolResult({}, Provenance(source="cached", endpoint=endpoint, assumptions=("CACHED_LIVE_FORTYGUARD",)), error="cached_live_fixture_required")
        loaded = self.load_fixture(fixture, endpoint=endpoint)
        if not loaded.ok:
            return ToolResult({}, Provenance(source="cached", endpoint=endpoint, assumptions=("CACHED_LIVE_FORTYGUARD",)), error=loaded.error)
        wrapper = loaded.data
        raw_result = wrapper.get("heatmap", {}).get("result", wrapper.get("result", wrapper)) if isinstance(wrapper, dict) else {}
        analytic_type = str(arguments.get("analytic_type", "tcm"))
        provenance = Provenance(
            source="cached",
            endpoint=endpoint,
            request_hash=request_hash(endpoint, {key: value for key, value in arguments.items() if key != "fixture"}),
            activity_id=(wrapper.get("heatmap", {}).get("activity_id") if isinstance(wrapper, dict) else None) or (wrapper.get("activity_id") if isinstance(wrapper, dict) else None),
            assumptions=("CACHED_LIVE_FORTYGUARD", "raw tile arrays omitted from model context"),
        )
        try:
            assert_heatmap_schema(raw_result, analytic_type)
        except ThermalContractError as exc:
            # A completed upstream activity with no usable cells is evidence failure,
            # never a successful empty result.
            return ToolResult(
                deterministic_decision_result(
                    status="COMPLETED_BUT_EMPTY",
                    valid=False,
                    decision_relevant_result="KEEP_CURRENT_PLAN_AND_RECHECK",
                    provenance="CACHED_LIVE_FORTYGUARD",
                    next_allowed_actions=["KEEP_CURRENT_PLAN_AND_RECHECK"],
                    state="COMPLETED_BUT_EMPTY",
                    evidence_status="INVALID_EVIDENCE",
                    thermal_evidence_valid=False,
                ),
                provenance,
                error=f"COMPLETED_BUT_EMPTY:{exc}",
            )
        features = raw_result.get("map_data", {}).get("features", [])
        properties = [feature.get("properties", {}) for feature in features]
        decision_grade = analytic_type == "exceedance"
        compact: dict[str, Any] = {
            "status": "VALID_THERMAL_EVIDENCE" if decision_grade else "CONTEXT_AVAILABLE",
            "decision_relevant_result": "THERMAL_EVIDENCE_AVAILABLE" if decision_grade else "OPTIONAL_CONTEXT_ONLY",
            "valid": True,
            "next_allowed_actions": ["CALCULATE_THERMAL_OVERLAP", "GENERATE_FEASIBLE_SCHEDULE_ALTERNATIVES"],
            "workfaces": arguments.get("workfaces", []),
            "window": arguments.get("window"),
            "analytic_type": analytic_type,
            "feature_count": len(features),
            "n_cells": (raw_result.get("stats_data") or {}).get("n_cells", len(features)),
            "source": "CACHED_LIVE_FORTYGUARD",
            "coverage": "VALID",
            "thermal_evidence_valid": decision_grade,
            "evidence_class": "DECISION_GRADE_THERMAL_EVIDENCE" if decision_grade else "CONTEXTUAL_ENVIRONMENTAL_EVIDENCE",
            "evidence_id": provenance.request_hash,
        }
        if analytic_type == "tcm":
            values = [float(item["average_temperature"]) for item in properties]
            compact.update({"average_temperature_c": round(mean(values), 4), "max_temperature_c": max(float(item["max_temperature"]) for item in properties), "min_temperature_c": min(float(item["min_temperature"]) for item in properties)})
        else:
            values = [float(item["value"]) for item in properties]
            compact.update({"min_value": min(values), "max_value": max(values), "mean_value": round(mean(values), 4), "units": (raw_result.get("stats_data") or {}).get("units")})
        return ToolResult(compact, provenance)

    def get_environmental_parameters(self, arguments: dict[str, Any]) -> ToolResult:
        payload = dict(arguments)
        fixture = payload.pop("fixture", None)
        if fixture:
            return self.load_fixture(fixture, endpoint="/v1/env_params")
        if payload.get("use_as_exposure_metric") or payload.get("derive_hours_above_threshold"):
            return ToolResult({}, Provenance(source="derived", endpoint="/v1/env_params"), error="env_params_range_cannot_be_exposure_forecast")
        try:
            self.request_guard.validate("/v1/env_params", payload)
        except GuardrailError as exc:
            return ToolResult({}, Provenance(source="derived", endpoint="/v1/env_params"), error=str(exc))
        return self._cached_or_live("/v1/env_params", payload, lambda: self.client.environmental_parameters(**payload, verbose=False))

    def get_environmental_context(self, arguments: dict[str, Any]) -> ToolResult:
        """Cached-only optional context for the real agent runtime."""
        fixture = arguments.get("fixture")
        if not fixture:
            return ToolResult({}, Provenance(source="cached", endpoint="/v1/env_params", assumptions=("CACHED_LIVE_FORTYGUARD",)), error="cached_live_fixture_required")
        loaded = self.load_fixture(fixture, endpoint="/v1/env_params")
        if not loaded.ok:
            return ToolResult({}, Provenance(source="cached", endpoint="/v1/env_params", assumptions=("CACHED_LIVE_FORTYGUARD",)), error=loaded.error)
        raw = loaded.data.get("result", loaded.data) if isinstance(loaded.data, dict) else {}
        try:
            assert_env_params_schema(raw)
        except ThermalContractError as exc:
            return ToolResult(
                deterministic_decision_result(
                    status="EVIDENCE_UNAVAILABLE",
                    valid=False,
                    decision_relevant_result="KEEP_CURRENT_PLAN_AND_RECHECK",
                    provenance="CACHED_LIVE_FORTYGUARD_ENV_PARAMS",
                    next_allowed_actions=["KEEP_CURRENT_PLAN_AND_RECHECK"],
                    state="INVALID_EVIDENCE",
                    thermal_evidence_valid=False,
                ),
                Provenance(source="cached", endpoint="/v1/env_params", assumptions=("CACHED_LIVE_FORTYGUARD",)),
                error=str(exc),
            )
        locations = raw.get("locations", [])
        first = locations[0] if locations else {}
        params = first.get("parameters", {})
        return ToolResult(
            deterministic_decision_result(
                status="CONTEXT_AVAILABLE",
                valid=True,
                decision_relevant_result="OPTIONAL_CONTEXT_ONLY",
                provenance="CACHED_LIVE_FORTYGUARD_ENV_PARAMS",
                next_allowed_actions=["CONTINUE_WITH_EXCEEDANCE_EVIDENCE"],
                location_count=len(locations),
                parameter_names=sorted(params)[:12],
                timestamp_count=len((raw.get("metadata") or {}).get("timestamps", [])),
                source="CACHED_LIVE_FORTYGUARD",
                coverage="VALID",
                role="context_only_not_shhch_source",
                evidence_class="CONTEXTUAL_ENVIRONMENTAL_EVIDENCE",
            ),
            Provenance(source="cached", endpoint="/v1/env_params", assumptions=("CACHED_LIVE_FORTYGUARD", "range arrays omitted from model context")),
        )

    def get_activity_status(self, arguments: dict[str, Any]) -> ToolResult:
        activity_id = str(arguments["activity_id"])
        if self.client is None:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/status/{activity_id}"), error="live_client_not_configured")
        try:
            return ToolResult(self.client.get_status(activity_id), Provenance(source="live", endpoint="/v1/status/{activity_id}", activity_id=activity_id))
        except Exception as exc:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/status/{activity_id}", activity_id=activity_id), error=f"{type(exc).__name__}: {str(exc)[:240]}")

    def inspect_api_usage(self, arguments: dict[str, Any] | None = None) -> ToolResult:
        if self.client is None:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/system/fetch-api-key-usage"), error="live_client_not_configured")
        try:
            body = self.client.fetch_api_key_usage()
            # Keep account identifiers out of traces while preserving credit facts.
            safe = {k: v for k, v in body.items() if k not in {"api_key", "api_key_details", "subscription_id"}}
            return ToolResult(safe, Provenance(source="live", endpoint="/v1/system/fetch-api-key-usage"))
        except Exception as exc:
            return ToolResult({}, Provenance(source="live", endpoint="/v1/system/fetch-api-key-usage"), error=f"{type(exc).__name__}: {str(exc)[:240]}")

    def load_fixture(self, path: str | Path, *, endpoint: str, assumptions: Iterable[str] = ()) -> ToolResult:
        path = Path(path)
        if not path.exists():
            return ToolResult({}, Provenance(source="sample", endpoint=endpoint, assumptions=tuple(assumptions)), error=f"fixture_not_found:{path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ToolResult(data, Provenance(source="sample", endpoint=endpoint, assumptions=tuple(assumptions)))
        except Exception as exc:
            return ToolResult({}, Provenance(source="sample", endpoint=endpoint), error=f"fixture_invalid:{type(exc).__name__}")

    @staticmethod
    def summarize_heat_profile(arguments: dict[str, Any]) -> ToolResult:
        """Derived summary; it never pretends to be a FortyGuard measurement."""
        if arguments.get("source_endpoint") == "/v1/env_params" and arguments.get("range_response", True):
            return ToolResult({}, Provenance(source="derived", endpoint="local:summarize_heat_profile"), error="env_params_anchor_curve_cannot_be_shift_exposure")
        profile = [float(x) for x in arguments.get("hourly_c", [])]
        if not profile:
            return ToolResult({}, Provenance(source="derived", endpoint="local:summarize_heat_profile"), error="hourly_c_required")
        threshold = float(arguments.get("threshold_c", 32.0))
        above = [i for i, value in enumerate(profile) if value > threshold]
        return ToolResult(
            {
                "min_c": min(profile),
                "max_c": max(profile),
                "mean_c": mean(profile),
                "peak_hour_index": profile.index(max(profile)),
                "hours_above_threshold": len(above),
                "threshold_c": threshold,
            },
            Provenance(source="derived", endpoint="local:summarize_heat_profile", assumptions=("hourly values are treated as Celsius",)),
        )

    @staticmethod
    def calculate_contextual_temperature_summary(arguments: dict[str, Any]) -> ToolResult:
        if arguments.get("source_endpoint") == "/v1/env_params":
            return ToolResult({}, Provenance(source="derived", endpoint="local:calculate_contextual_temperature_summary"), error="env_params_context_cannot_supply_shhch")
        profile = [float(x) for x in arguments.get("hourly_c", [])]
        windows = arguments.get("work_windows", [])
        threshold = float(arguments.get("threshold_c", 32.0))
        if not profile or not windows:
            return ToolResult({}, Provenance(source="derived", endpoint="local:calculate_contextual_temperature_summary"), error="hourly_c_and_work_windows_required")
        selected: list[float] = []
        for window in windows:
            start, end = int(window["start_hour"]), int(window["end_hour"])
            selected.extend(profile[start:end])
        burden = sum(max(0.0, value - threshold) for value in selected)
        return ToolResult(
            {"contextual_temperature_exceedance_degree_hours": round(burden, 4), "hours": len(selected), "threshold_c": threshold},
            Provenance(source="derived", endpoint="local:calculate_contextual_temperature_summary", assumptions=("context-only arithmetic; never a SHHCH source",)),
        )


    @staticmethod
    def inspect_shift_plan(arguments: dict[str, Any]) -> ToolResult:
        tasks = arguments.get("tasks", [])
        outdoor = [t for t in tasks if bool(t.get("outdoor", t.get("environment") != "indoor"))]
        fixed = [t for t in tasks if bool(t.get("fixed", False))]
        crew_ids = sorted({str(t.get("crew_id", t.get("crewId", t.get("crew")))) for t in tasks if t.get("crew_id", t.get("crewId", t.get("crew"))) is not None})
        workfaces = sorted({str(t.get("workface", t.get("workface_id", t.get("zoneId", t.get("zone_id"))))) for t in tasks if t.get("workface", t.get("workface_id", t.get("zoneId", t.get("zone_id")))) is not None})
        dependencies = sum(len(t.get("dependencies", [])) for t in tasks if isinstance(t.get("dependencies", []), list))
        return ToolResult({
            "task_count": len(tasks), "indoor_tasks": len(tasks) - len(outdoor), "outdoor_tasks": len(outdoor),
            "fixed_tasks": len(fixed), "movable_tasks": len(tasks) - len(fixed),
            "outdoor_task_ids": [t.get("id") for t in outdoor], "crews": crew_ids, "workfaces": workfaces,
            "shift_bounds": {"start": arguments.get("shift_start"), "end": arguments.get("shift_end")},
            "major_dependencies": dependencies, "source": "SHIFT_PLAN",
        }, Provenance(source="derived", endpoint="local:inspect_shift_plan"))

    @staticmethod
    def identify_thermal_candidates(arguments: dict[str, Any]) -> ToolResult:
        tasks = arguments.get("tasks", [])
        candidates = [t.get("id") for t in tasks if t.get("outdoor", False) and not t.get("fixed", False)]
        return ToolResult({"candidate_task_ids": candidates, "reason": "movable outdoor work only"}, Provenance(source="derived", endpoint="local:identify_thermal_candidates"))

    @staticmethod
    def calculate_thermal_overlap(arguments: dict[str, Any]) -> ToolResult:
        from datetime import datetime
        from .thermal import ThermalTrigger, calculate_thermal_overlap as overlap
        trigger = ThermalTrigger(arguments["trigger_name"], datetime.fromisoformat(arguments["trigger_start"]), datetime.fromisoformat(arguments["trigger_end"]), arguments.get("threshold_c"), "employer_configured", arguments.get("provenance", "EMPLOYER_CONFIGURED"))
        result = overlap(datetime.fromisoformat(arguments["task_start"]), datetime.fromisoformat(arguments["task_end"]), trigger, int(arguments["crew_size"]), evidence_source=arguments.get("evidence_source", "DERIVED"))
        return ToolResult({"overlap_minutes": result.overlap_minutes, "crew_hours": result.crew_hours, "trigger_name": result.trigger_name, "confidence": result.confidence}, Provenance(source="derived", endpoint="local:calculate_thermal_overlap"))

    @staticmethod
    def generate_feasible_schedule_alternatives(arguments: dict[str, Any]) -> ToolResult:
        from .policy import BreakRule, EmployerPolicy
        from .scheduler import generate_feasible_schedule_alternatives
        endpoint = "local:generate_feasible_schedule_alternatives"
        tasks, crews, baseline = arguments.get("tasks"), arguments.get("crews"), arguments.get("baseline", arguments.get("schedule"))
        if not isinstance(tasks, list) or not isinstance(crews, dict) or not isinstance(baseline, dict):
            return ToolResult({}, Provenance(source="derived", endpoint=endpoint), error="canonical_scheduler_inputs_required")
        policy_data = arguments.get("policy") or {}
        try:
            rules = tuple(BreakRule(str(item["trigger_name"]), int(item["after_continuous_minutes"]), int(item["duration_minutes"]), "DEMO_POLICY") for item in policy_data.get("break_rules", []))
            policy = EmployerPolicy(str(policy_data.get("policy_id", "runtime")), str(policy_data.get("version", "1")), str(policy_data.get("name", "runtime policy")), "DEMO_POLICY", str(policy_data.get("effective_date", "1970-01-01")), "modeled-temperature", policy_data.get("initial_trigger"), policy_data.get("high_trigger"), str(policy_data.get("units", "celsius")), rules)
            candidates = generate_feasible_schedule_alternatives(tasks, crews, policy, baseline=baseline, shift_start=arguments["shift_start"], shift_end=arguments["shift_end"], trigger_start=arguments["trigger_start"], trigger_end=arguments["trigger_end"])
        except (KeyError, TypeError, ValueError) as exc:
            return ToolResult({}, Provenance(source="derived", endpoint=endpoint), error=f"scheduler_input_invalid:{exc}")
        return ToolResult({"status": "FEASIBLE_ALTERNATIVES" if candidates else "NO_FEASIBLE_IMPROVEMENT", "valid": bool(candidates), "candidates": candidates, "candidate_count": len(candidates), "deterministic": True, "next_allowed_actions": ["VERIFY_SCHEDULE"] if candidates else ["KEEP_CURRENT_PLAN"]}, Provenance(source="derived", endpoint=endpoint))

    @staticmethod
    def verify_schedule(arguments: dict[str, Any]) -> ToolResult:
        from .policy import BreakRule, EmployerPolicy
        from .scheduler import verify_schedule
        endpoint = "local:verify_schedule"
        tasks, schedule, crews = arguments.get("tasks"), arguments.get("schedule"), arguments.get("crews")
        if not isinstance(tasks, list) or not isinstance(schedule, dict) or not isinstance(crews, dict):
            return ToolResult({"status": "VERIFICATION_FAILED", "valid": False, "error": "canonical_verifier_inputs_required"}, Provenance(source="derived", endpoint=endpoint), error="canonical_verifier_inputs_required")
        policy_data = arguments.get("policy") or {}
        try:
            rules = tuple(BreakRule(str(item["trigger_name"]), int(item["after_continuous_minutes"]), int(item["duration_minutes"]), "DEMO_POLICY") for item in policy_data.get("break_rules", []))
            policy = EmployerPolicy(str(policy_data.get("policy_id", "runtime")), str(policy_data.get("version", "1")), str(policy_data.get("name", "runtime policy")), "DEMO_POLICY", str(policy_data.get("effective_date", "1970-01-01")), "modeled-temperature", policy_data.get("initial_trigger"), policy_data.get("high_trigger"), str(policy_data.get("units", "celsius")), rules)
            result = verify_schedule(tasks, schedule, crews, policy, shift_start=arguments["shift_start"], shift_end=arguments["shift_end"], trigger_start=arguments["trigger_start"], trigger_end=arguments["trigger_end"], require_thermal_evidence=bool(arguments.get("require_thermal_evidence", False)), thermal_evidence_valid=bool(arguments.get("thermal_evidence_valid", True)))
        except (KeyError, TypeError, ValueError) as exc:
            return ToolResult({"status": "VERIFICATION_FAILED", "valid": False, "error": str(exc)}, Provenance(source="derived", endpoint=endpoint), error=str(exc))
        data = {"status": result.status, "valid": result.passed, "decision_relevant_result": "VERIFIED_SCHEDULE" if result.passed else "KEEP_CURRENT_PLAN_AND_RECHECK", "checks": [{"name": check.name, "passed": check.passed, "detail": check.detail} for check in result.checks], "schedule_hash": request_hash(endpoint, {"tasks": tasks, "schedule": schedule, "crews": crews, "policy": policy_data}), "evidence_hash": request_hash("local:evidence", arguments.get("evidence", arguments.get("thermal_evidence", {}))), "task_state_hash": request_hash("local:task-state", {"tasks": tasks, "crews": crews}), "policy_version": policy.version, "next_allowed_actions": ["COMPARE_SCHEDULE_METRICS", "REQUEST_SUPERINTENDENT_APPROVAL"] if result.passed else ["KEEP_CURRENT_PLAN_AND_RECHECK"]}
        return ToolResult(data, Provenance(source="derived", endpoint=endpoint))

    @staticmethod
    def compare_schedule_metrics(arguments: dict[str, Any]) -> ToolResult:
        before, after = float(arguments.get("before_crew_hours", 0)), float(arguments.get("after_crew_hours", 0))
        return ToolResult({"before_scheduled_high_heat_crew_hours": before, "after_scheduled_high_heat_crew_hours": after, "delta": round(before - after, 4), "metric_type": "DERIVED SCHEDULE METRIC"}, Provenance(source="derived", endpoint="local:compare_schedule_metrics"))

    @staticmethod
    def calculate_scheduled_high_heat_crew_hours(arguments: dict[str, Any]) -> ToolResult:
        from .shhch import ShhchContractError, calculate_scheduled_high_heat_crew_hours

        try:
            result = calculate_scheduled_high_heat_crew_hours(
                arguments.get("schedule"),
                arguments.get("workfaces"),
                arguments.get("exceedance_windows"),
                arguments.get("project_thermal_trigger"),
            )
        except (ShhchContractError, TypeError, ValueError) as exc:
            return ToolResult(
                deterministic_decision_result(
                    status="ERROR_SAFE",
                    valid=False,
                    decision_relevant_result="KEEP_CURRENT_PLAN_AND_RECHECK",
                    provenance="DETERMINISTIC_LOCAL_SHHCH",
                    next_allowed_actions=["KEEP_CURRENT_PLAN_AND_RECHECK"],
                    error=str(exc),
                ),
                Provenance(source="derived", endpoint="local:calculate_scheduled_high_heat_crew_hours"),
                error=str(exc),
            )
        return ToolResult(result.to_dict(), Provenance(source="derived", endpoint="local:calculate_scheduled_high_heat_crew_hours", assumptions=("FORTYGUARD_EXCEEDANCE_ONLY",)))

    @staticmethod
    def request_superintendent_approval(arguments: dict[str, Any]) -> ToolResult:
        return ToolResult({"status": "PENDING_SUPERINTENDENT_APPROVAL", "recommendation_id": arguments.get("recommendation_id"), "publish_blocked_until_approval": True}, Provenance(source="derived", endpoint="local:request_superintendent_approval"))

    @staticmethod
    def recheck_thermal_evidence(arguments: dict[str, Any]) -> ToolResult:
        """Explicit, guarded recheck transition; this method never calls a provider."""
        return ToolResult({"status": "EVIDENCE_UNAVAILABLE", "action": "RECHECK_THERMAL_EVIDENCE", "retry_invoked": True, "current_schedule_preserved": arguments.get("current_schedule"), "valid_evidence_cleared": True, "live_provider_call": False, "next_allowed_actions": ["RECHECK_THERMAL_EVIDENCE"]}, Provenance(source="derived", endpoint="local:recheck_thermal_evidence"))

    @staticmethod
    def compare_locations(arguments: dict[str, Any]) -> ToolResult:
        locations = arguments.get("locations", {})
        threshold = float(arguments.get("threshold_c", 32.0))
        rows = []
        for name, profile in locations.items():
            values = [float(x) for x in profile]
            rows.append({"location": name, "max_c": max(values), "hours_above_threshold": sum(x > threshold for x in values), "mean_c": round(mean(values), 4)})
        rows.sort(key=lambda row: (-row["max_c"], -row["hours_above_threshold"], row["location"]))
        return ToolResult(
            {"locations": rows, "threshold_c": threshold},
            Provenance(source="derived", endpoint="local:compare_locations"),
        )


def load_live_toolkit() -> FortyGuardToolkit:
    """Opt-in helper that reads the key without ever printing it."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "vendor" / "temperature-api-quickstart"))
    try:
        from fortyguard import FortyGuardClient
    except ImportError as exc:
        raise RuntimeError("Install requests to enable live FortyGuard calls") from exc
    key = os.getenv("FORTYGUARD_API_KEY")
    if not key:
        raise RuntimeError("FORTYGUARD_API_KEY is not configured")
    return FortyGuardToolkit(FortyGuardClient(api_key=key, base_url=os.getenv("FORTYGUARD_BASE_URL")))
