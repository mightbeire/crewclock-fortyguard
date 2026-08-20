from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal


PolicySource = Literal["EMPLOYER_CONFIGURED", "DEMO_POLICY", "PUBLIC_GUIDANCE_REFERENCE"]


@dataclass(frozen=True)
class BreakRule:
    trigger_name: str
    after_continuous_minutes: int
    duration_minutes: int
    source: PolicySource


@dataclass(frozen=True)
class EmployerPolicy:
    policy_id: str
    version: str
    name: str
    source: PolicySource
    effective_date: str
    metric_used: str
    initial_trigger: float | None
    high_trigger: float | None
    units: str
    break_rules: tuple[BreakRule, ...] = ()
    required_control_tier: str | None = None
    prefer_move_work_types: tuple[str, ...] = ()
    onsite_verification_required: bool = True
    superintendent_review_required: bool = True
    escalation_rule: str = "Escalate fixed work; do not create an impossible move."
    acclimatization_categories: tuple[str, ...] = ("established", "new_or_returning", "unknown")

    def validate(self) -> None:
        if self.source not in {"EMPLOYER_CONFIGURED", "DEMO_POLICY", "PUBLIC_GUIDANCE_REFERENCE"}:
            raise ValueError("invalid_policy_source")
        if self.units != "celsius" and self.high_trigger is not None:
            raise ValueError("thermal_trigger_units_must_be_celsius_or_none")
        if self.high_trigger is not None and self.initial_trigger is not None and self.high_trigger < self.initial_trigger:
            raise ValueError("high_trigger_must_not_be_below_initial_trigger")
        if set(self.acclimatization_categories) != {"established", "new_or_returning", "unknown"}:
            raise ValueError("acclimatization_categories_are_operational_only")
        for rule in self.break_rules:
            if rule.after_continuous_minutes <= 0 or rule.duration_minutes <= 0:
                raise ValueError("break_rule_durations_must_be_positive")


def required_breaks_for_outdoor_intervals(
    intervals: list[tuple[datetime, datetime]],
    policy: EmployerPolicy,
    trigger_start: datetime,
    trigger_end: datetime,
) -> list[tuple[datetime, datetime]]:
    """Return reserved breaks; an interval that cannot fit a break is a failure."""
    if not intervals or not policy.break_rules:
        return []
    rule = policy.break_rules[0]
    clipped: list[tuple[datetime, datetime]] = []
    for start, end in sorted(intervals):
        start, end = max(start, trigger_start), min(end, trigger_end)
        if end > start:
            clipped.append((start, end))
    if not clipped:
        return []
    breaks: list[tuple[datetime, datetime]] = []
    continuous_start, continuous_end = clipped[0]
    minutes = (continuous_end - continuous_start).total_seconds() / 60
    for start, end in clipped[1:]:
        if start > continuous_end:
            if minutes > rule.after_continuous_minutes:
                break_start = continuous_start + timedelta(minutes=rule.after_continuous_minutes)
                break_end = break_start + timedelta(minutes=rule.duration_minutes)
                if break_end > start:
                    raise ValueError("mandatory_break_cannot_be_reserved")
                breaks.append((break_start, break_end))
            continuous_start, continuous_end, minutes = start, end, (end - start).total_seconds() / 60
        else:
            continuous_end = max(continuous_end, end)
            minutes = (continuous_end - continuous_start).total_seconds() / 60
    if minutes > rule.after_continuous_minutes:
        break_start = continuous_start + timedelta(minutes=rule.after_continuous_minutes)
        break_end = break_start + timedelta(minutes=rule.duration_minutes)
        raise ValueError("mandatory_break_cannot_be_reserved")
    return breaks
