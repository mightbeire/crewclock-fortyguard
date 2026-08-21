from __future__ import annotations

"""Explicit deterministic workflow states shared by tools and evaluators."""

from typing import Any


TERMINAL_STATES = frozenset({
    "NO_ACTION_REQUIRED",
    "EVIDENCE_UNAVAILABLE",
    "KEEP_CURRENT_PLAN",
    "KEEP_CURRENT_PLAN_AND_RECHECK",
    "NO_FEASIBLE_IMPROVEMENT",
    "AWAITING_APPROVAL",
    "APPROVED",
    "REJECTED",
    "ERROR_SAFE",
})

# These values have all appeared at different provider/tool boundaries.  They
# describe the same operational fact: thermal evidence cannot support a
# decision.  Keep this vocabulary here so no model prompt has to remember the
# equivalence.
INVALID_EVIDENCE_STATES = frozenset({
    "COMPLETED_BUT_EMPTY",
    "NOT_DEMONSTRATED",
    "EVIDENCE_UNAVAILABLE",
    "EMPTY_FEATURE_COLLECTION",
    "INVALID_SCHEMA",
    "WRONG_UNITS",
    "UNCOVERED_REQUIRED_INTERVAL",
    "INVALID_EVIDENCE",
})

THERMAL_OPERATIONAL_ACTIONS = frozenset({
    "calculate_thermal_overlap",
    "generate_feasible_schedule_alternatives",
    "calculate_scheduled_high_heat_crew_hours",
    "compare_schedule_metrics",
    "request_superintendent_approval",
})


def _normalise_token(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _evidence_error_text(data: dict[str, Any]) -> str:
    values = [data.get(key) for key in ("state", "status", "evidence_status", "reason", "error")]
    return " ".join(str(value or "").upper().replace("-", "_") for value in values)


def invalid_evidence_status(data: dict[str, Any] | None) -> str | None:
    """Return the canonical invalid-evidence trigger, if ``data`` has one."""
    if not isinstance(data, dict):
        return None
    for key in ("status", "state", "evidence_status"):
        token = _normalise_token(data.get(key))
        if token in INVALID_EVIDENCE_STATES:
            return token
    if data.get("thermal_evidence_valid") is False:
        return "EVIDENCE_UNAVAILABLE"
    text = _evidence_error_text(data)
    if any(token in text for token in INVALID_EVIDENCE_STATES):
        return next(token for token in INVALID_EVIDENCE_STATES if token in text)
    # Tool adapters often expose contract failures as descriptive errors
    # rather than one of the labels above.  Normalize those descriptions too.
    if "EMPTY_FEATURE" in text or "FEATURE_COLLECTION" in text:
        return "EMPTY_FEATURE_COLLECTION"
    if "NOT_DEMONSTRATED" in text:
        return "NOT_DEMONSTRATED"
    if "SCHEMA" in text:
        return "INVALID_SCHEMA"
    if "UNIT" in text or "CELSIUS" in text:
        return "WRONG_UNITS"
    if "UNCOVERED" in text or ("TASK_INTERVAL" in text and "COVER" not in text):
        return "UNCOVERED_REQUIRED_INTERVAL"
    if any(token in text for token in ("EVIDENCE_UNAVAILABLE", "NO_EVIDENCE", "MISSING_EVIDENCE", "INVALID_EVIDENCE")):
        return "EVIDENCE_UNAVAILABLE"
    return None


def normalize_invalid_evidence(
    data: dict[str, Any],
    *,
    provenance: str = "DETERMINISTIC_EVIDENCE_AUTHORITY",
) -> dict[str, Any] | None:
    """Normalize every invalid thermal-evidence representation.

    The returned envelope is authoritative.  Any original status is retained
    only as diagnostic context and cannot alter the operational decision.
    """
    original = invalid_evidence_status(data)
    if original is None:
        return None
    return deterministic_decision_result(
        status="EVIDENCE_UNAVAILABLE",
        valid=False,
        decision_relevant_result="CURRENT_PLAN_PRESERVED",
        provenance=provenance,
        next_allowed_actions=["KEEP_CURRENT_PLAN", "RECHECK_AVAILABLE"],
        original_evidence_status=original,
        state="EVIDENCE_UNAVAILABLE",
        evidence_status="EVIDENCE_UNAVAILABLE",
        thermal_evidence_valid=False,
        current_plan_preserved=True,
        thermal_optimization_allowed=False,
        recommended_action="KEEP_CURRENT_PLAN",
    )


def workflow_requires_thermal_evidence(constraints: dict[str, Any] | None) -> bool:
    """Infer the thermal boundary from structured workflow input, not prose."""
    if not isinstance(constraints, dict):
        return False
    explicit = constraints.get("thermal_evidence_required")
    if isinstance(explicit, bool):
        return explicit
    shift_plan = constraints.get("shift_plan")
    tasks = shift_plan.get("tasks", []) if isinstance(shift_plan, dict) else []
    if not isinstance(tasks, list):
        return False
    return any(
        isinstance(task, dict) and bool(task.get("outdoor", task.get("environment") != "indoor"))
        for task in tasks
    )


def authoritative_evidence_from_constraints(constraints: dict[str, Any] | None) -> dict[str, Any] | None:
    """Build the unavailable-evidence terminal from initial workflow state."""
    if not workflow_requires_thermal_evidence(constraints):
        return None
    evidence_status = constraints.get("evidence_status") if isinstance(constraints, dict) else None
    if not isinstance(evidence_status, str):
        return None
    return normalize_invalid_evidence(
        {"status": evidence_status, "evidence_status": evidence_status},
        provenance="DETERMINISTIC_WORKFLOW_AUTHORITY",
    )


def terminal_status(value: Any) -> str | None:
    """Map internal/legacy terminal labels to the operational state names."""
    token = _normalise_token(value)
    aliases = {
        "AWAITING_HUMAN_APPROVAL": "AWAITING_APPROVAL",
        "APPROVED_RECOMMENDATION": "APPROVED",
        "REJECTED_RECOMMENDATION": "REJECTED",
        "KEEP_CURRENT_PLAN_AND_RECHECK": "EVIDENCE_UNAVAILABLE",
    }
    token = aliases.get(token, token)
    return token if token in TERMINAL_STATES else None


def deterministic_decision_result(
    *,
    status: str,
    valid: bool,
    decision_relevant_result: str,
    provenance: str,
    next_allowed_actions: list[str],
    **fields: Any,
) -> dict[str, Any]:
    """Build a small, authoritative result envelope for model observations."""
    return {
        "status": status,
        "decision_relevant_result": decision_relevant_result,
        "valid": valid,
        "provenance": provenance,
        "next_allowed_actions": next_allowed_actions,
        **fields,
    }
