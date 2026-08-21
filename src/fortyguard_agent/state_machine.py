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

