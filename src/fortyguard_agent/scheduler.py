from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .policy import EmployerPolicy, required_breaks_for_outdoor_intervals


@dataclass(frozen=True)
class ConstraintCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ScheduleVerification:
    passed: bool
    checks: tuple[ConstraintCheck, ...]


def _duration(value: Any) -> timedelta:
    return value if isinstance(value, timedelta) else timedelta(minutes=float(value))


def verify_schedule(
    tasks: list[dict[str, Any]],
    schedule: dict[str, datetime],
    crews: dict[str, dict[str, Any]],
    policy: EmployerPolicy,
    *,
    shift_start: datetime,
    shift_end: datetime,
    trigger_start: datetime,
    trigger_end: datetime,
) -> ScheduleVerification:
    checks: list[ConstraintCheck] = []
    checks.append(ConstraintCheck("all_tasks_scheduled", all(task["id"] in schedule for task in tasks), "Every task has a candidate start."))
    fixed = all(not task.get("fixed") or schedule[task["id"]] == task["baseline_start"] for task in tasks)
    checks.append(ConstraintCheck("fixed_commitments", fixed, "Fixed commitments remain at baseline."))
    qualifications = all(task["qualification"] in crews[task["crew_id"]].get("qualifications", []) for task in tasks)
    checks.append(ConstraintCheck("qualifications", qualifications, "Every assignment has the required qualification."))
    bounds = all(shift_start <= schedule[task["id"]] and schedule[task["id"]] + _duration(task["duration"]) <= min(shift_end, task["deadline"]) for task in tasks)
    checks.append(ConstraintCheck("deadlines_and_shift", bounds, "Every finish remains inside the shift and deadline."))
    dependency_pass = all(schedule[dependency] + _duration(next(t["duration"] for t in tasks if t["id"] == dependency)) <= schedule[task["id"]] for task in tasks for dependency in task.get("dependencies", []))
    checks.append(ConstraintCheck("dependencies", dependency_pass, "Finish-to-start dependencies are preserved."))
    availability = True
    for crew_id in crews:
        assigned = [task for task in tasks if task["crew_id"] == crew_id]
        intervals = sorted((schedule[t["id"]], schedule[t["id"]] + _duration(t["duration"]), t) for t in assigned)
        availability = availability and all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:]))
    checks.append(ConstraintCheck("crew_availability", availability, "Same-crew intervals do not overlap."))
    break_pass = True
    for crew_id in crews:
        intervals = [(schedule[t["id"]], schedule[t["id"]] + _duration(t["duration"])) for t in tasks if t["crew_id"] == crew_id and t.get("outdoor", False)]
        try:
            required_breaks_for_outdoor_intervals(intervals, policy, trigger_start, trigger_end)
        except ValueError:
            break_pass = False
    checks.append(ConstraintCheck("policy_breaks", break_pass, "Mandatory recovery time is reserved or the candidate is rejected."))
    return ScheduleVerification(all(check.passed for check in checks), tuple(checks))
