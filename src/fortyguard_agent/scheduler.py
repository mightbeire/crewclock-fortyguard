from __future__ import annotations

"""Canonical deterministic schedule verification and offline optimization."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from .policy import EmployerPolicy


@dataclass(frozen=True)
class ConstraintCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ScheduleVerification:
    passed: bool
    checks: tuple[ConstraintCheck, ...]

    @property
    def status(self) -> str:
        return "VERIFIED" if self.passed else "VERIFICATION_FAILED"


def _timestamp(value: Any, field: str) -> datetime:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{field}_timestamp_invalid") from exc
    else:
        raise ValueError(f"{field}_timestamp_required")
    if result.tzinfo is None:
        raise ValueError(f"{field}_timestamp_must_be_timezone_aware")
    return result.astimezone(timezone.utc)


def _duration(value: Any, field: str = "duration") -> timedelta:
    if isinstance(value, timedelta):
        result = value
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        result = timedelta(minutes=float(value))
    else:
        raise ValueError(f"{field}_minutes_required")
    if result <= timedelta(0):
        raise ValueError(f"{field}_must_be_positive")
    return result


def _check(name: str, passed: bool, detail: str) -> ConstraintCheck:
    return ConstraintCheck(name, bool(passed), detail)


def _break_check(intervals: list[tuple[datetime, datetime]], policy: EmployerPolicy, trigger_start: datetime, trigger_end: datetime) -> tuple[bool, str]:
    """Require a full policy-duration idle interval; a badge is insufficient."""
    if not intervals or not policy.break_rules:
        return True, "No required break applies."
    rule = policy.break_rules[0]
    clipped = sorted((max(start, trigger_start), min(end, trigger_end)) for start, end in intervals if min(end, trigger_end) > max(start, trigger_start))
    runs: list[tuple[datetime, datetime]] = []
    for start, end in clipped:
        # A gap shorter than the required recovery duration does not reset
        # continuous outdoor work. Exactly the policy duration is sufficient.
        if runs and (start - runs[-1][1]).total_seconds() / 60 < rule.duration_minutes:
            runs[-1] = (runs[-1][0], max(runs[-1][1], end))
        else:
            runs.append((start, end))
    for start, end in runs:
        if (end - start).total_seconds() / 60 > rule.after_continuous_minutes:
            return False, f"continuous outdoor run has no reserved {rule.duration_minutes}-minute break"
    return True, f"required {rule.duration_minutes}-minute break capacity is present"


def verify_schedule(
    tasks: list[dict[str, Any]],
    schedule: dict[str, Any],
    crews: dict[str, dict[str, Any]],
    policy: EmployerPolicy,
    *,
    shift_start: Any,
    shift_end: Any,
    trigger_start: Any,
    trigger_end: Any,
    require_thermal_evidence: bool = False,
    thermal_evidence_valid: bool = True,
    break_reservations: list[dict[str, Any]] | None = None,
) -> ScheduleVerification:
    """Verify a complete schedule against every applicable hard constraint."""
    checks: list[ConstraintCheck] = []
    try:
        shift_start_dt, shift_end_dt = _timestamp(shift_start, "shift_start"), _timestamp(shift_end, "shift_end")
        trigger_start_dt, trigger_end_dt = _timestamp(trigger_start, "trigger_start"), _timestamp(trigger_end, "trigger_end")
        policy.validate()
    except (ValueError, TypeError) as exc:
        return ScheduleVerification(False, (_check("schedule_schema", False, str(exc)),))

    schema_errors: list[str] = []
    schema_ok = isinstance(tasks, list) and bool(tasks) and isinstance(schedule, dict) and bool(schedule) and isinstance(crews, dict) and bool(crews)
    if not schema_ok:
        schema_errors.append("empty_or_wrong_container")
    task_rows = tasks if isinstance(tasks, list) else []
    if any(not isinstance(task, dict) for task in task_rows):
        schema_errors.append("task_object_required")
    ids = [task.get("id") for task in task_rows if isinstance(task, dict)]
    if any(not isinstance(task_id, str) or not task_id for task_id in ids):
        schema_errors.append("task_id_required")
    string_ids = [task_id for task_id in ids if isinstance(task_id, str)]
    if len(string_ids) != len(set(string_ids)):
        schema_errors.append("duplicate_task_id")
    if isinstance(schedule, dict) and set(schedule) != set(string_ids):
        schema_errors.append("schedule_task_ids_must_match")
    if isinstance(crews, dict):
        for crew_id, crew in crews.items():
            if not isinstance(crew_id, str) or not isinstance(crew, dict) or not isinstance(crew.get("qualifications", []), list) or not all(isinstance(item, str) for item in crew.get("qualifications", [])):
                schema_errors.append("crew_schema_invalid")
    for task in task_rows:
        if not isinstance(task, dict):
            continue
        if not any(key in task for key in ("duration", "duration_minutes", "durationMinutes")):
            schema_errors.append(f"missing_duration:{task.get('id', '<unknown>')}")
        if "deadline" not in task:
            schema_errors.append(f"missing_deadline:{task.get('id', '<unknown>')}")
        if not isinstance(task.get("dependencies", []), list) or not all(isinstance(item, str) for item in task.get("dependencies", [])):
            schema_errors.append(f"dependencies_invalid:{task.get('id', '<unknown>')}")
        elif any(item not in string_ids for item in task.get("dependencies", [])):
            schema_errors.append(f"unknown_dependency:{task.get('id', '<unknown>')}")
        if "fixed" in task and not isinstance(task["fixed"], bool):
            schema_errors.append(f"fixed_invalid:{task.get('id', '<unknown>')}")
        if "outdoor" in task and not isinstance(task["outdoor"], bool):
            schema_errors.append(f"outdoor_invalid:{task.get('id', '<unknown>')}")
        for key in ("workface", "workface_id", "zone_id", "zoneId"):
            if key in task and not isinstance(task[key], str):
                schema_errors.append(f"{key}_invalid:{task.get('id', '<unknown>')}")
        crew_id = task.get("crew_id", task.get("crewId", task.get("crew")))
        if not isinstance(crew_id, str) or crew_id not in crews:
            schema_errors.append(f"unknown_crew:{task.get('id', '<unknown>')}")
        if not isinstance(task.get("qualification"), str) or not task.get("qualification"):
            schema_errors.append(f"qualification_required:{task.get('id', '<unknown>')}")
        try:
            _duration(task.get("duration", task.get("duration_minutes", task.get("durationMinutes"))), f"task:{task.get('id', '<unknown>')}:duration")
            _timestamp(task.get("deadline"), f"task:{task.get('id', '<unknown>')}:deadline")
        except (ValueError, TypeError):
            schema_errors.append(f"task_timing_invalid:{task.get('id', '<unknown>')}")
        if isinstance(schedule, dict) and task.get("id") in schedule:
            try:
                _timestamp(schedule[task["id"]], f"task:{task['id']}:start")
            except (ValueError, TypeError):
                schema_errors.append(f"start_timestamp_invalid:{task.get('id', '<unknown>')}")
    checks.append(_check("schedule_schema", not schema_errors, f"INVALID_SCHEDULE_SCHEMA:{';'.join(schema_errors) if schema_errors else 'ok'}"))
    if not schema_ok:
        return ScheduleVerification(False, tuple(checks))
    if schema_errors:
        return ScheduleVerification(False, tuple(checks))

    parsed: dict[str, tuple[datetime, datetime, dict[str, Any]]] = {}
    malformed: list[str] = []
    for task in tasks:
        task_id = task["id"]
        try:
            start = _timestamp(schedule[task_id], f"task:{task_id}:start")
            duration = task.get("duration", task.get("duration_minutes", task.get("durationMinutes")))
            end = start + _duration(duration, f"task:{task_id}:duration")
            crew_id = task.get("crew_id", task.get("crewId", task.get("crew")))
            qualification = task.get("qualification")
            _timestamp(task.get("deadline"), f"task:{task_id}:deadline")
            if not isinstance(crew_id, str) or crew_id not in crews or not isinstance(qualification, str):
                raise ValueError("crew_assignment_required")
            parsed[task_id] = (start, end, task)
        except (ValueError, TypeError, KeyError) as exc:
            malformed.append(f"{task_id}:{exc}")
    checks.append(_check("task_schema", not malformed, "Every task has a valid interval, assignment, qualification, and deadline."))
    if malformed:
        return ScheduleVerification(False, tuple(checks))

    checks.append(_check("required_tasks", set(parsed) == set(ids), "Every required task is preserved exactly once."))
    fixed_ok = True
    for task_id, (start, _, task) in parsed.items():
        if task.get("fixed"):
            baseline = task.get("baseline_start", task.get("original_start", task.get("originalStart")))
            try:
                fixed_ok = fixed_ok and baseline is not None and start == _timestamp(baseline, f"task:{task_id}:baseline_start")
            except (ValueError, TypeError):
                fixed_ok = False
    checks.append(_check("fixed_commitments", fixed_ok, "Fixed commitments remain at their baseline starts."))

    qualifications_ok = all(task.get("qualification") in crews[task.get("crew_id", task.get("crewId", task.get("crew")))].get("qualifications", []) for _, _, task in parsed.values())
    checks.append(_check("qualifications", qualifications_ok, "Every crew assignment holds the required qualification."))
    bounds_ok = all(shift_start_dt <= start and end <= shift_end_dt and end <= _timestamp(task["deadline"], f"task:{task['id']}:deadline") for start, end, task in parsed.values())
    checks.append(_check("deadlines_and_shift", bounds_ok, "Every task finishes within shift bounds and deadline."))

    dependency_ok = True
    for task_id, (start, _, task) in parsed.items():
        for dependency in task.get("dependencies", []):
            dependency_ok = dependency_ok and dependency in parsed and parsed[dependency][1] <= start
    checks.append(_check("dependencies", dependency_ok, "All dependency finish-to-start edges are preserved."))

    availability_ok = True
    for crew_id in crews:
        intervals = sorted((start, end) for start, end, task in parsed.values() if task.get("crew_id", task.get("crewId", task.get("crew"))) == crew_id)
        availability_ok = availability_ok and all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:]))
    checks.append(_check("crew_availability", availability_ok, "No crew is assigned to overlapping work."))

    breaks_ok = True
    details: list[str] = []
    for crew_id in crews:
        intervals = [(start, end) for start, end, task in parsed.values() if task.get("crew_id", task.get("crewId", task.get("crew"))) == crew_id and bool(task.get("outdoor", task.get("environment") not in {"indoor", "shaded-support"}))]
        ok, detail = _break_check(intervals, policy, trigger_start_dt, trigger_end_dt)
        breaks_ok = breaks_ok and ok
        details.append(f"{crew_id}: {detail}")
    checks.append(_check("policy_breaks", breaks_ok, "; ".join(details)))
    reservations_ok = True
    reservation_details: list[str] = []
    reservations = break_reservations or []
    if not isinstance(break_reservations, list) and break_reservations is not None:
        reservations_ok = False
        reservation_details.append("break_reservations_must_be_array")
    elif reservations:
        if not policy.break_rules:
            reservations_ok = False
            reservation_details.append("break_rule_required_for_reservation")
        else:
            rule = policy.break_rules[0]
            for index, reservation in enumerate(reservations):
                try:
                    if not isinstance(reservation, dict):
                        raise ValueError("reservation_object_required")
                    crew_id = reservation.get("crew_id", reservation.get("crewId"))
                    start = _timestamp(reservation.get("start"), f"break:{index}:start")
                    end = _timestamp(reservation.get("end"), f"break:{index}:end")
                    if crew_id not in crews or end <= start:
                        raise ValueError("break_reservation_invalid")
                    if (end - start).total_seconds() / 60 < rule.duration_minutes or start < trigger_start_dt or end > trigger_end_dt:
                        raise ValueError("break_reservation_outside_policy_window_or_duration")
                    task_intervals = [(task_start, task_end) for task_start, task_end, task in parsed.values() if task.get("crew_id", task.get("crewId", task.get("crew"))) == crew_id]
                    if any(start < task_end and end > task_start for task_start, task_end in task_intervals):
                        raise ValueError("break_reservation_overlaps_work")
                except (ValueError, TypeError, KeyError) as exc:
                    reservations_ok = False
                    reservation_details.append(f"break:{index}:{exc}")
    checks.append(_check("break_reservations", reservations_ok, "; ".join(reservation_details) if reservation_details else "All reserved breaks meet policy duration, window, crew, and overlap rules."))
    if require_thermal_evidence:
        checks.append(_check("thermal_evidence", thermal_evidence_valid, "Thermally motivated verification requires valid compatible evidence."))
    checks.append(_check("schedule_completeness", len(parsed) == len(tasks) and bool(tasks), "The candidate is complete and non-empty."))
    return ScheduleVerification(all(check.passed for check in checks), tuple(checks))


def generate_feasible_schedule_alternatives(
    tasks: list[dict[str, Any]],
    crews: dict[str, dict[str, Any]],
    policy: EmployerPolicy,
    *,
    baseline: dict[str, Any],
    shift_start: Any,
    shift_end: Any,
    trigger_start: Any,
    trigger_end: Any,
    objective: Callable[[dict[str, Any]], tuple] | None = None,
    slot_minutes: int = 30,
) -> list[dict[str, Any]]:
    """Enumerate feasible candidates; model output never supplies schedules."""
    if not tasks or not crews or not baseline:
        return []
    shift_start_dt, shift_end_dt = _timestamp(shift_start, "shift_start"), _timestamp(shift_end, "shift_end")
    by_id = {task.get("id"): task for task in tasks}
    ordered: list[dict[str, Any]] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def topo(task: dict[str, Any]) -> None:
        task_id = task["id"]
        if task_id in visited:
            return
        if task_id in visiting:
            return
        visiting.add(task_id)
        for dependency in task.get("dependencies", []):
            if dependency in by_id:
                topo(by_id[dependency])
        visiting.remove(task_id)
        visited.add(task_id)
        ordered.append(task)

    for task in sorted(tasks, key=lambda item: item["id"]):
        topo(task)
    candidates: list[dict[str, Any]] = []

    def visit(index: int, partial: dict[str, Any]) -> None:
        if index == len(ordered):
            result = verify_schedule(tasks, partial, crews, policy, shift_start=shift_start_dt, shift_end=shift_end_dt, trigger_start=trigger_start, trigger_end=trigger_end)
            if result.passed:
                candidates.append(dict(partial))
            return
        task = ordered[index]
        task_id = task["id"]
        if task.get("fixed"):
            partial[task_id] = baseline.get(task_id)
            visit(index + 1, partial)
            partial.pop(task_id, None)
            return
        duration = _duration(task.get("duration", task.get("duration_minutes", task.get("durationMinutes"))), f"task:{task_id}:duration")
        latest = min(shift_end_dt, _timestamp(task["deadline"], f"task:{task_id}:deadline") - duration)
        cursor = shift_start_dt
        while cursor <= latest:
            dependency_ready = True
            for dependency in task.get("dependencies", []):
                predecessor = next((item for item in tasks if item["id"] == dependency), None)
                if predecessor is None or dependency not in partial or _timestamp(partial[dependency], f"task:{dependency}:start") + _duration(predecessor.get("duration", predecessor.get("duration_minutes", predecessor.get("durationMinutes"))), f"task:{dependency}:duration") > cursor:
                    dependency_ready = False
            crew_id = task.get("crew_id", task.get("crewId", task.get("crew")))
            crew_clear = True
            for other_id, other_start in partial.items():
                other = next((item for item in tasks if item["id"] == other_id), None)
                if other and other.get("crew_id", other.get("crewId", other.get("crew"))) == crew_id:
                    other_start_dt = _timestamp(other_start, f"task:{other_id}:start")
                    other_end = other_start_dt + _duration(other.get("duration", other.get("duration_minutes", other.get("durationMinutes"))), f"task:{other_id}:duration")
                    crew_clear = crew_clear and not (cursor < other_end and cursor + duration > other_start_dt)
            if dependency_ready and crew_clear:
                partial[task_id] = cursor
                visit(index + 1, partial)
                partial.pop(task_id, None)
            cursor += timedelta(minutes=slot_minutes)

    visit(0, {})
    if objective:
        candidates.sort(key=objective)
    return candidates
