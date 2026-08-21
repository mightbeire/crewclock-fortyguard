from __future__ import annotations

"""Canonical content identities for CrewClock decision artifacts."""

from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
import hashlib
import json
from typing import Any, Mapping


ARTIFACT_VERSION = "crewclock.recommendation.v1"


def _canonical(value: Any) -> Any:
    if is_dataclass(value):
        return _canonical(asdict(value))
    if isinstance(value, datetime):
        normalized = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return normalized.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, set):
        return sorted((_canonical(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
        raise ValueError("non_finite_hash_value")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def content_hash(value: Any, *, domain: str) -> str:
    payload = canonical_json({"domain": domain, "content": value})
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def policy_content_hash(policy: Any) -> str:
    return content_hash(policy, domain="crewclock.policy.v1")


def project_state_hash(tasks: Any, crews: Any) -> str:
    return content_hash({"tasks": tasks, "crews": crews}, domain="crewclock.project-state.v1")


def source_schedule_hash(source_schedule: Any) -> str | None:
    if source_schedule is None:
        return None
    return content_hash(source_schedule, domain="crewclock.source-schedule.v1")


def evidence_bundle_hash(evidence: Any) -> str:
    return content_hash(evidence or {}, domain="crewclock.evidence-bundle.v1")


def candidate_hash_from_verification_arguments(arguments: Mapping[str, Any]) -> str | None:
    tasks, schedule, crews = arguments.get("tasks"), arguments.get("schedule"), arguments.get("crews")
    if not isinstance(tasks, list) or not isinstance(schedule, dict) or not isinstance(crews, dict):
        return None
    return content_hash(
        {
            "tasks": tasks,
            "schedule": schedule,
            "crews": crews,
            "policy": arguments.get("policy", {}),
            "break_reservations": arguments.get("break_reservations", []),
            "source_schedule": arguments.get("source_schedule"),
        },
        domain="crewclock.candidate.v1",
    )


def verification_result_hash(data: Mapping[str, Any]) -> str:
    return content_hash(
        {key: data.get(key) for key in ("status", "valid", "checks", "candidate_hash", "source_schedule_hash", "evidence_hash", "policy_hash", "project_state_hash")},
        domain="crewclock.verification-result.v1",
    )


def recommendation_id(*, candidate_hash: str, source_schedule_hash_value: str | None, evidence_hash: str, policy_hash: str, project_state_hash_value: str, verification_hash: str) -> str:
    return content_hash(
        {
            "artifact_version": ARTIFACT_VERSION,
            "candidate_hash": candidate_hash,
            "source_schedule_hash": source_schedule_hash_value,
            "evidence_hash": evidence_hash,
            "policy_hash": policy_hash,
            "project_state_hash": project_state_hash_value,
            "verification_hash": verification_hash,
        },
        domain="crewclock.recommendation-id.v1",
    )
