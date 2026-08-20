# CrewClock implemented architecture

## Runtime boundary

CrewClock is a deterministic, offline-capable demonstration of an agent-guided construction planning workflow. The React interface never calls FortyGuard or any external service. Approved cached-live Phoenix evidence is imported from the canonical fixture; operational data and employer policy are labelled demo inputs.

```text
superintendent goal
  → agent inspects 14-task look-ahead
  → classifier selects 7 movable outdoor tasks
  → cached FortyGuard evidence loaded for 2 affected workfaces
  → deterministic scheduler enumerates crew assignments
  → hard-constraint verifier rejects infeasible schedules
  → agent prepares evidence-backed recommendation
  → superintendent approves or retains original plan
  → deterministic post-approval verification
```

The activity rail exposes only factual stages and tool labels. It contains no private chain-of-thought.

## Code map

| File | Responsibility |
|---|---|
| `src/demo/scenario.ts` | Locked crews, tasks, evidence, policy, regression fixture, display geometry helpers |
| `src/demo/engine.ts` | Investigation selection, schedule enumeration, ordered objective, verification, failure states, audit events |
| `src/App.tsx` | Mission-control presentation, deterministic stage timing, comparison, approval, reset, evidence/audit inspectors |
| `src/styles.css` | Desktop-first operational layout, transformation motion, responsive breakpoints |
| `src/demo/demo.test.ts` | Scenario, solver, measurement, constraint, provenance, guardrail and replay regression suite |

## Deterministic scheduler

For each crew, the engine anchors fixed tasks and recursively assigns each movable task to 30-minute slots between `05:30` and its deadline. It prunes crew overlaps during enumeration and validates completed assignments.

Candidates are ordered by:

1. hard feasibility;
2. minimum movable outdoor crew-hour overlap with the modeled `11:00–15:00` window;
3. minimum absolute minutes moved from the original plan.

The canonical run considers 19 complete conflict-free crew schedules, rejects those that fail modeled constraints, and independently reproduces the seven expected task moves. `proposedStart` remains only a test oracle; the UI reads the generated `recommendation` schedule.

## Constraint ownership

The deterministic verifier owns six families:

| Family | Canonical proof |
|---|---|
| Fixed commitments | 5 anchors unchanged |
| Dependencies | 11 finish-to-start edges preserved |
| Qualifications | 14 task assignments matched to crew qualifications |
| Deadlines and bounds | 14 finish times remain within deadline and workday |
| Crew availability | Same-crew task pairs do not overlap |
| Employer controls | Outdoor peak-window overlap does not exceed the modeled 90-minute planning rule |

The thermal objective is never evaluated as permission to violate a hard constraint. The LLM/agent cannot set task start times or declare feasibility.

## Agent ownership

The agent layer owns orchestration rather than schedule mathematics:

- inspect the plan and determine which tasks require thermal evidence;
- skip thermally irrelevant shaded/support work and avoid querying fixed work unnecessarily;
- load and provenance the approved cached evidence;
- decide when the deterministic solver should run;
- surface failure/uncertainty without manufacturing a result;
- explain the returned comparison;
- request explicit superintendent approval;
- trigger final verification and append factual audit events.

## State machine

```text
READY
  → CHECKING
  → SELECTING
  → EVIDENCE
  → OPTIMIZING
  → VERIFYING
  → AWAITING_APPROVAL
      ├─ reset/reject → READY + original plan
      └─ approve → APPROVED_VERIFYING → VERIFIED
```

Evidence or policy failure branches from the investigation stages to `NO_CHANGE_ISSUED`. The original plan remains visible and no approval action is offered.

## Failure behavior

`runCrewClock` returns a typed status and no recommendation for:

- missing evidence;
- stale evidence;
- cached-evidence tool failure;
- ambiguous employer policy;
- infeasible original operational input;
- no better feasible plan.

These states use the wording “No defensible improvement found” where applicable. They never relabel stale evidence as current or convert uncertainty into approval.

## Approval and audit

Approval is a local demonstration event. It records the human gate in the factual audit, changes the recommendation to an approved plan, and reruns the deterministic verification. It does not write to Primavera, Procore, dispatch, payroll, or any external system. Reset returns the exact canonical starting state.

## Provenance contract

| Label | Meaning |
|---|---|
| `FORTYGUARD · CACHED LIVE` | Values returned by prior authorized API calls and stored in sanitized local cache |
| `DERIVED` | Scheduler, verifier, and crew-hour arithmetic |
| `EMPLOYER POLICY` | Synthetic employer planning fixture, not FortyGuard and not law |
| `DEMO INPUT` | Synthetic schedule, crews, qualifications, deadlines, and workface geometry |

No interface state uses a live badge. `LIVE CALLS 0` remains visible in the header.

## Demo and QA contract

- Run ID: `CC-PHX-0716-v1`.
- Canonical route: `/`.
- Reset is one click and has no network dependency.
- Stage timing is 620 ms per step and 420 ms for approval verification, making motion readable without fake waiting.
- Failure fixtures are query-addressable for QA: `missing-evidence`, `stale-evidence`, `tool-failure`, `ambiguous-policy`, and `no-improvement`.
- Required browser sizes: 1440×900, 1024×768, and 390×844.
- Screenshot evidence lives under `evidence/crewclock-mvp/`.

## External boundary

`LIVE_FORTYGUARD_CALLS = 0`. A controlled sponsor decision-delta run remains a separate, explicitly authorized next step after submission packaging.
