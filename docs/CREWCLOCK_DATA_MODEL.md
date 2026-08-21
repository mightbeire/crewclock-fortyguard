# CrewClock MVP data model

## Locked thermal evidence fields

Tasks include `weather_sensitivity.precipitation` as a future feasibility
constraint; missing precipitation evidence is `UNKNOWN` and cannot reject a
task. Workfaces are polygons with stable IDs. Exceedance evidence is a list of
`{analytic_type, start, end, units: hours, status, provenance, tiles}` windows.
Each tile carries a duration value for that exact window. The project trigger
stores `threshold_c`, a modeled-temperature `quantity`, and provenance. No
`env_params` field is permitted as an SHHCH duration input.

## Design principles

1. Every datum carries a provenance class: `public`, `cached_live`, `employer`, `synthetic`, `derived`, or `onsite_authoritative`.
2. Unknown required evidence never silently passes.
3. LLM output cannot modify constraint mathematics.
4. A recommendation is immutable once presented; revisions create a new plan version.
5. Approval and external execution are separate events.
6. The MVP stores no worker medical data.

## Core entities

```text
Project 1 ── * WorkZone
Project 1 ── * LookAheadPlan 1 ── * Task
LookAheadPlan 1 ── * CrewAssignment * ── 1 Crew
Task * ── * TaskDependency
Task * ── 1 WorkZone
Task * ── 1..* QualificationRequirement
Crew * ── * Qualification
EmployerPolicy 1 ── * PolicyClause
ThermalInvestigation * ── 1 WorkZone
ThermalInvestigation * ── * EvidenceArtifact
OptimizationRun 1 ── * PlanAlternative
PlanAlternative 1 ── * ScheduledTask
PlanAlternative 1 ── * ConstraintResult
Recommendation 1 ── 1 PlanAlternative
Recommendation 1 ── 0..1 ApprovalDecision
Recommendation 1 ── 1 MeasurementResult
```

## Types

### `Project`

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable internal ID |
| `name` | string | Human project/work-package label |
| `organization_id` | string | Contractor/owner boundary |
| `timezone` | IANA timezone | Required for hourly alignment |
| `public_reference_url` | URL? | Optional public context, never represented as a customer record |

### `WorkZone`

| Field | Type | Notes |
|---|---|---|
| `id` | string | Zone ID |
| `name` | string | Superintendent-facing label |
| `geometry` | GeoJSON Polygon/Point | Provenance required |
| `environment_class` | enum | Outdoor, sheltered, indoor-conditioned, unknown |
| `geometry_provenance` | provenance | Demo geometry is `synthetic` |

### `LookAheadPlan`

| Field | Type | Notes |
|---|---|---|
| `id` | string | Versioned plan ID |
| `project_id` | string | Parent |
| `work_date` | local date | Day being planned |
| `status` | enum | Draft, investigated, proposed, approved, rejected, superseded |
| `source` | provenance + URI | Procore/P6/CSV/demo fixture |
| `created_at` | timestamp | Audit |

### `Task`

| Field | Type | Notes |
|---|---|---|
| `id`, `name` | string | Work item identity |
| `zone_id` | string | Spatial join |
| `duration_minutes` | integer | Deterministic |
| `original_start` | local datetime | Baseline |
| `earliest_start`, `latest_finish` | local datetime | Feasible window |
| `fixed` | boolean | Fixed time cannot move |
| `movability_reason` | string | User-supplied |
| `environment` | enum | Outdoor-heavy, outdoor-moderate, shaded-support, unknown |
| `qualification_ids` | string[] | Hard crew gate |
| `dependency_ids` | string[] | Finish-to-start in MVP |
| `planned_controls` | string[] | Employer policy reference, not FortyGuard |
| `provenance` | provenance | Demo tasks are synthetic |

### `Crew`

| Field | Type | Notes |
|---|---|---|
| `id`, `name`, `trade` | string | Crew identity |
| `headcount` | integer | Metric multiplier |
| `qualification_ids` | string[] | No individual medical attributes |
| `availability_windows` | interval[] | Hard constraints |
| `acclimatization_flag` | enum | `employer-cleared`, `employer-controls-required`, `unknown`; never inferred by CrewClock |

### `EmployerPolicy` and `PolicyClause`

| Field | Type | Notes |
|---|---|---|
| `policy_id`, `version` | string | Version must be shown |
| `effective_at` | timestamp | Audit |
| `clause_id` | string | Atomic rule |
| `scope` | enum | Planning or onsite-authoritative |
| `rule_type` | enum | Prefer, require, prohibit, escalate |
| `expression` | structured rule | Deterministic where possible |
| `source_text` | string | Quoted/imported employer text |
| `approver` | role | Employer authority |

The demo policy is explicitly `synthetic`. OSHA/NIOSH guidance informs its shape but is not silently converted into law.

### `EvidenceArtifact`

| Field | Type | Notes |
|---|---|---|
| `id` | string | Artifact ID |
| `kind` | enum | TCM, env parameters, exceedance, persistence, time-of-measure, forecast, advisory, onsite reading |
| `provider` | string | FortyGuard, NWS, onsite device, employer |
| `observed_for` | interval | Environmental time |
| `retrieved_at` | timestamp | Freshness |
| `geometry` | GeoJSON | Coverage |
| `units` | string | Never inferred silently |
| `cache_path` | string? | Sanitized local cache |
| `provenance` | provenance | Required |
| `quality_status` | enum | Pass, fail, unknown |
| `limitations` | string[] | Visible to approver |

### `ThermalInvestigation`

Records why evidence was or was not requested:

```json
{
  "task_ids": ["G2", "G3", "G4"],
  "zone_id": "north",
  "question": "Could approved timing alternatives reduce overlap with the modeled peak window?",
  "selected_tools": ["fortyguard.cached_env", "fortyguard.cached_time_of_measure"],
  "stop_reason": "Enough evidence to rank timing alternatives; onsite release is out of scope",
  "status": "sufficient_for_planning"
}
```

### `ConstraintResult`

Each hard clause returns:

```text
PASS | FAIL | UNKNOWN
```

Required fields: `constraint_id`, `category`, `status`, `evidence_ids`, `explanation`, `checked_at`, `checker_version`.

MVP categories:

- crew availability;
- qualification;
- dependency;
- task deadline;
- fixed commitment;
- work-zone collision;
- employer planning control;
- evidence freshness/coverage.

Any hard `FAIL` rejects an alternative. Any required `UNKNOWN` blocks recommendation and escalates.

### `OptimizationRun`

| Field | Type | Notes |
|---|---|---|
| `input_plan_hash` | SHA-256 | Reproducibility |
| `policy_version` | string | Rule binding |
| `evidence_ids` | string[] | Exact evidence |
| `solver_version` | string | Deterministic engine |
| `objective` | ordered list | First feasibility, then minimum peak-window eligible crew-hours, then minimum change |
| `alternatives_tested` | integer | Audit |
| `status` | enum | Complete, infeasible, unknown, error |

The LLM cannot set a plan directly. It may request a solve and explain returned alternatives.

### `Recommendation` and `ApprovalDecision`

Recommendation fields: selected alternative, before/after diff, evidence summary, constraint results, known limitations, rollback plan, created timestamp and agent trace ID.

Approval fields: authorized role, approve/reject/revise, timestamp, comment, exact recommendation hash. MVP approval changes only local demo state; it does not publish to a project system.

## Demo fixture

### Crews

| Crew | Trade | Headcount | Qualifications |
|---|---|---:|---|
| Crew A | Groundworks | 6 | competent person, excavation, equipment |
| Crew B | Concrete | 5 | concrete placement, finishing |
| Crew C | Electrical | 4 | journey electrician, signal systems |

### Fourteen-task day

| ID | Task | Crew | Zone | Duration | Before | Proposed | Fixed |
|---|---|---|---|---:|---:|---:|---|
| G0 | Traffic-control handoff | A | North | 0.5h | 05:30 | 05:30 | Yes |
| G1 | Equipment service & staging | A | Laydown | 2h | 06:00 | 12:00 | No |
| G2 | Signal trench excavation | A | North | 2h | 08:00 | 06:00 | No |
| G3 | Fine grade & compact | A | North | 2h | 10:00 | 08:00 | No |
| G4 | Conduit bedding | A | North | 2h | 12:00 | 10:00 | No |
| C1 | Foundation formwork | B | South | 2h | 06:00 | 06:00 | No |
| C2 | Rebar & anchor bolts | B | South | 1h | 08:00 | 08:00 | No |
| C3 | City inspection hold | B | South | 0.5h | 09:00 | 09:00 | Yes |
| C4 | Foundation concrete pour | B | South | 2h | 09:30 | 09:30 | Yes |
| C5 | Finish & protect concrete | B | South | 1.5h | 11:30 | 11:30 | Yes |
| E1 | Cabinet pre-wire | C | Laydown | 2h | 06:00 | 10:00 | No |
| E2 | Proof duct & pull line | C | South | 2h | 08:00 | 06:00 | No |
| E3 | Pull signal conductors | C | South | 2h | 10:00 | 08:00 | No |
| E4 | Inspector test window | C | South | 1h | 13:00 | 13:00 | Yes |

All operational fields in this table are synthetic demo data.

## App route and state structure

```text
/
└── tomorrow-plan
    ├── opening
    ├── investigating
    ├── proposal
    └── verified

drawer:evidence
drawer:decision-log
plan-view:original | proposed
```

The MVP implements these as local React state to keep the stage path deterministic. `src/demo/engine.ts` owns schedule generation and verification; `src/App.tsx` only orchestrates presentation and approval state. Production routing can map them to `/projects/:projectId/plans/:planId` without changing the domain model.

## Implemented solver contract

The engine creates a `Schedule` map of task IDs to local start times, enumerates 30-minute starts within each deadline and the modeled workday, and combines the best feasible crew schedules. Its objective order is:

1. all hard-constraint families pass;
2. minimize eligible crew-hour overlap with `11:00–15:00`;
3. minimize absolute minutes moved from the original plan.

The locked `proposedStart` values are a regression oracle, not solver input. The generated canonical schedule must match them exactly.

## Remaining integration seams

- Look-ahead import: CSV first, then Procore/Autodesk/P6 adapters.
- Thermal provider: existing guarded FortyGuard toolkit and cache.
- Solver: deterministic interval/constraint service.
- Policy: employer-authored structured rule pack with immutable version.
- Approval: role-based, explicit and separate from external publication.
- Onsite: optional measurement ingest used only as authoritative execution-time evidence.

## Foundation lock additions

`WorkZone.geometry` is a polygon where practical. Thermal values are area-weighted over all intersecting 60/80/100 m heatmap tiles; point assignment is explicit for point-like areas. `EmployerPolicy` includes provenance-labelled triggers and `BreakRule` intervals. `EvidenceArtifact` records endpoint, request hash, source/retrieval timestamps, schema version, units, and LIVE/CACHED-LIVE state. No range-based anchored `env_params` curve may populate a schedule exposure metric.
