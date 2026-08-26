# CrewClock MVP specification

> **CrewClock helps construction superintendents adjust the upcoming shift around hyperlocal heat without breaking the schedule.**

Decision date: 2026-08-20

Decision: **`CREWCLOCK_MVP_READY = YES`**

## Metric lock amendment

The hero metric is SHHCH from FortyGuard `analytic_type=exceedance`: area-weight
tiles over polygon workfaces, intersect their duration with each task's
scheduled interval, multiply by crew size, and sum outdoor tasks. The project
thermal trigger is a separately provenance-labelled FortyGuard modeled
temperature threshold. `env_params` is optional context only. Missing Phoenix
exceedance windows are an honest evidence blocker, not a reason to use TCM,
heat-index, or synthetic duration.

Product state: CrewClock is locked as the hackathon MVP. The canonical Phoenix demo is `EVIDENCE TEMPORARILY UNAVAILABLE`; it preserves the current plan and offers `RECHECK_THERMAL_EVIDENCE`. This is a product decision, not a claim of field efficacy or safety certification.
FortyGuard boundary: **zero new live requests**; only sanitized cached-live evidence is used.

## Plain-English product

Before crews deploy, CrewClock identifies flexible outdoor work that overlaps the worst local heat, tests feasible alternatives, and lets the superintendent approve the least-disruptive adjustment. It investigates only work that thermal evidence could change, delegates the scheduling mathematics to deterministic code, verifies every hard constraint, and asks the superintendent to approve the recommendation.

The worker gets better-timed work and clearer planned controls. The company gets a workable schedule with less last-minute replanning and more productive crew-hours outside unnecessarily harsh periods.

CrewClock does **not** certify safety, calculate regulatory compliance, replace a heat-illness prevention plan, or replace onsite measurements and professional judgment.

## Final reality check

### 1. Do U.S. construction teams already modify work because of heat?

**Yes.** This is directly evidenced rather than inferred:

- [NIOSH’s construction guidance](https://www.cdc.gov/niosh/bulletin/2020/heat-stress-construction.html) tells employers to schedule hot jobs for cooler parts of the day, modify work/rest schedules, add crew, restrict overtime, postpone non-urgent work, and monitor each site.
- [OSHA’s controls guidance](https://www.osha.gov/heat-exposure/controls) describes cooler-time scheduling, shorter shifts for new or unacclimatized workers, mandatory recovery breaks, job rotation, workload reduction, mechanization, water, shade, and emergency response.
- [JE Dunn’s published heat program](https://www.osha.gov/sites/default/files/2023BeatTheHeatWinners/Contest_Message_JEDUNNConstruction_HeatProgram_508c.pdf) says high heat is addressed in pre-start plans and JSAs; work is scheduled earlier where possible; supervision observes workers; and water, shade, and breaks are provided.

This clears the mandatory “temperature is already inside the decision loop” test.

### 2. What decisions do they make?

Real operating decisions include:

- start earlier, move work later, shorten a shift, or postpone non-urgent work;
- sequence heavy outdoor work before cooler or sheltered work;
- change work/rest periods and recovery locations;
- rotate tasks, reduce physical demand, mechanize work, or add crew;
- treat new and returning workers differently under the employer’s acclimatization procedure;
- preserve delivery, inspection, traffic-control, access, and subcontractor commitments;
- ready water, shade/cooling, first aid, communications, and emergency response;
- monitor conditions onsite and stop or change work when the authorized person decides controls are insufficient.

CrewClock assists with the **pre-shift plan**. It does not make the live stop-work decision.

### 3. What do company heat plans require operational planning for?

[OSHA’s planning guidance](https://www.osha.gov/heat-exposure/planning) asks employers to define daily oversight, acclimatization, first aid and emergency response, controls and work practices, heat measurement, responses to NWS advisories, total-heat-stress assessment, and training. Industry plans add site-specific trigger levels, water and shade logistics, pre-task communication, supervision, recovery periods, and work sequencing.

The federal heat-specific standard remains a **proposal**, not a final rule as of this research date. [OSHA’s current rulemaking page](https://www.osha.gov/heat-exposure/rulemaking/) records the 2024 proposal and completed 2025 hearing/comment process. CrewClock therefore imports the employer’s adopted policy; it does not present proposed federal language as binding law.

### 4. Planning decisions versus onsite authoritative measurements

| Before-shift planning evidence | Onsite authoritative decision inputs |
|---|---|
| Upcoming-shift task, crew, qualification, deadline, dependency and fixed-commitment data | Current onsite WBGT or the employer’s approved measurement method |
| NWS advisories and ordinary forecast context | Actual workload/metabolic rate and duration |
| FortyGuard spatial screening, hourly timing, persistence, exceedance and environmental context | Clothing/PPE, radiant sources, airflow, shade and microconditions |
| Employer policy clauses and planned controls | Acclimatization status, symptoms and worker-specific conditions handled under policy |
| Proposed alternate task sequence | Superintendent/competent-person/EHS judgment and stop-work authority |

CrewClock may recommend and explain. Missing, stale, conflicting, or authoritative onsite evidence returns `UNKNOWN` and escalates; it never returns an invented pass.

### 5. Legitimate CrewClock inputs

- one-day or short look-ahead tasks;
- durations, work locations/zones, trade and crew assignments;
- qualification requirements and worker/crew qualification flags;
- task dependencies, deadlines, permits, inspections, deliveries and access windows;
- fixed versus movable work and approved alternates;
- task workload/environment category supplied by the contractor;
- employer heat-policy rules and planned controls;
- authoritative advisories and forecasts;
- cached/live FortyGuard evidence with date, geography, endpoint and unit provenance;
- onsite readings at execution time, when a future integration is authorized.

The MVP does not ingest diagnoses, medications, or other sensitive medical details.

### 6. What FortyGuard improves before the shift

FortyGuard is a **planning evidence selector**, not a safety sensor. Its verified value is:

- screening which work zones or sites deserve investigation at 100 m requested analysis granularity;
- showing hourly environmental timing through `env_params`;
- showing surface-temperature summaries through TCM;
- showing where a threshold is exceeded and for how long when an approved exceedance request exists;
- showing persistence and time-of-measure patterns across an AOI;
- adding satellite-derived physical context where segmentation is interpretable;
- ranking timing/location alternatives before scarce onsite attention is spent.

The approved Phoenix cache demonstrates an hourly apparent-temperature profile and a 99-cell time-of-measure result. It does not prove a universal spatial advantage or a production decision delta.

### 7. What FortyGuard must not be used to claim

- It is not WBGT.
- It does not establish that work is safe.
- It does not certify compliance or satisfy onsite monitoring requirements.
- It does not know workload, PPE, acclimatization, symptoms, radiant sources, or current field conditions unless an authoritative integration supplies them.
- A modeled heat window is not an injury probability.
- The MVP metric is not “lives saved,” “injuries prevented,” or “percent safer.”
- Cached historical evidence is not tomorrow’s forecast.

### 8. Honest measurable output

The MVP’s hero metric is:

> **Scheduled high-heat crew-hours above the employer-configured project trigger while all modeled hard constraints remain satisfied.**

The deterministic demo currently reports no Phoenix number because schedule-aligned exceedance evidence is not cached. When validated windows are present, the value is recomputed from tile area weighting, exact task/window overlap and headcount. It is not a health or safety outcome.

### 9. Real and public demo data

- **Real cached-live:** Phoenix FortyGuard TCM, hourly environmental parameters, and 99-cell time-of-measure analysis for 2025-07-15.
- **Real public:** [ADOT’s active project list](https://apps.azdot.gov/websurf/) provides recognizable Phoenix project names, locations and work types. The [SR-51 pavement rehabilitation project](https://azdot.gov/projects/central-district-projects/sr-51-i-10-to-shea-boulevard-pavement-rehabilitation) provides public project elements, operating windows and an explicit weather-sensitive schedule.
- **Schema authority:** [O*NET](https://www.onetonline.org/link/summary/11-9021.00) and [BLS](https://www.bls.gov/ooh/management/construction-managers.htm) support the user’s scheduling, supervision, delay-response, budget and deadline responsibilities.
- **Synthetic and labelled:** the exact 14-task work package, three crews, qualifications, dependencies, deadlines, workface geometry, fixed commitments and demo employer policy.

Public project data establishes realism and schema; it is not relabelled as a customer’s upcoming-shift schedule.

### 10. Could weather plus a spreadsheet replicate most of CrewClock?

**Not at the targeted workflow boundary, but it is the correct hostile baseline.** A skilled superintendent can use a forecast and spreadsheet to rearrange a small one-site day. CrewClock does not win merely by displaying hourly weather or moving one task.

The MVP earns its place only when it repeatedly:

1. joins a real look-ahead to crews, qualifications, dependencies, deadlines, inspections, deliveries and fixed work;
2. decides which tasks/zones merit thermal investigation instead of querying everything;
3. selects and records sponsor-specific evidence with provenance;
4. turns employer policy into explicit planning constraints without pretending to certify compliance;
5. delegates scheduling to deterministic code;
6. rejects infeasible alternatives and verifies the selected result;
7. explains exceptions and routes a reversible proposal to the superintendent;
8. records an audit trail and recomputes the outcome after approval.

If a final retrospective test shows that one ordinary forecast column plus manual sorting produces the same task ranking and verified plan with comparable effort, the FortyGuard wedge fails and the product must be narrowed or stopped. That is a final validation gate, not a reason to leave the hackathon MVP undefined.

## Exact user

### Primary user: Construction Superintendent

[O*NET](https://www.onetonline.org/link/summary/11-9021.00) lists Construction Superintendent among reported titles for construction managers and assigns the occupation responsibility for planning/scheduling work to deadlines, supervising workers, determining labor requirements, resolving work procedures and tracking cost/progress. BLS likewise says construction managers work onsite, prepare timetables, coordinate subcontractors, respond to delays/emergencies, and keep projects on time and budget.

| Field | MVP definition |
|---|---|
| Job title | Construction Superintendent |
| Responsibility | Own tomorrow’s field plan and coordinate trades, access, deliveries, inspections, production and site controls |
| CrewClock-assisted decisions | Which flexible tasks move; which fixed tasks need controls; which zones require investigation; which feasible plan should be issued |
| Approval authority | Accept/reject the recommended look-ahead; request changes; escalate safety questions; never delegate stop-work authority to CrewClock |
| KPIs | Milestones met, productive crew-hours, planned-versus-actual work, trade coordination, rework/delay avoidance, policy execution |
| Existing tools | P6/MS Project/ALICE for schedules, Procore/Autodesk for field records and look-aheads, spreadsheets, weather apps, toolbox/pre-task plans |

## Exact MVP workflow

```text
Upcoming-shift look-ahead + employer policy
                  ↓
Agent validates provenance and classifies tasks
                  ↓
Agent selects only sites/tasks where thermal evidence could change the plan
                  ↓
FortyGuard + ordinary forecast/advisory context
                  ↓
Deterministic scheduler generates feasible alternatives
                  ↓
Deterministic verifier checks:
crew qualifications · dependencies · deadlines · fixed work · planned controls
                  ↓
Agent explains the best alternative, exceptions and uncertainty
                  ↓
Construction Superintendent approves / rejects / requests revision
                  ↓
Verifier recomputes result; audit record is stored; execution remains external
```

Division of labor:

- **Agent:** investigate, select evidence, orchestrate tools, explain, verify, stop and escalate.
- **Optimizer:** scheduling/constraint mathematics and objective comparison.
- **Superintendent:** operational approval and judgment.
- **Onsite responsible person:** current heat assessment, policy implementation and stop-work response.

## Three-minute product route/state model

| State | Visible product state | Allowed transition |
|---|---|---|
| `opening` | Original plan, sites, cached evidence badge, no result | Run investigation |
| `investigating` | High-level tool actions and evidence selection | Continue or fail closed |
| `proposal` | Reordered schedule, preserved constraints, exceptions, approval gate | Approve, reject, revise |
| `verified` | Approved plan and recomputed SHHCH result when valid exceedance evidence exists | Export/audit later; no external action in MVP |
| `unknown` | Missing/stale/conflicting required evidence | Escalate; no recommendation |

Primary information architecture:

1. Upcoming shift plan
2. Thermal evidence
3. Agent activity
4. Before/after comparison
5. Constraint verification
6. Superintendent approval
7. Result and decision log

## Scope

### Must have

- single-day construction schedule with 8–15 tasks and 2–4 crews;
- task locations/zones, durations, dependencies, qualifications, deadlines and fixed/movable flags;
- employer planning policy with explicit provenance;
- map and cached FortyGuard timing/thermal layer;
- agent evidence selection and high-level activity trace;
- deterministic constraint scheduler and independent verifier;
- original/proposed plan toggle and visible schedule movement;
- approval gate, rollback-safe recommendation and audit record;
- recomputed hero metric and real/derived/synthetic evidence drawer;
- hard copy stating that onsite measurements and judgment remain authoritative.

### Should have

- CSV/JSON look-ahead import;
- configurable employer rule pack with clause-level `PASS`/`FAIL`/`UNKNOWN`;
- multiple feasible alternatives with schedule/thermal trade-off;
- onsite-reading check-in and variance capture;
- export to a field-planning tool or daily log after explicit approval;
- final decision-delta comparison against NWS/ordinary forecast only.

### Cut

- worker medical profiles or individual risk scores;
- automatic safety certification or legal-compliance claims;
- autonomous stop-work, dispatch or schedule publication;
- wearable monitoring;
- payroll, timecards and HR functionality;
- full CPM replacement, BIM authoring or generic weather dashboard;
- injury, mortality or “percent safer” estimates;
- portfolio analytics, predictive claims and production integrations before a real pilot.

## Hostile final check

1. **Why company?** It protects upcoming-shift production plan from avoidable heat-driven disruption while preserving the constraints the superintendent is paid to manage.
2. **Why worker?** Heavy outdoor work can be planned earlier where feasible, and planned controls become visible before the shift.
3. **Why not Weather.com?** Weather is one input; CrewClock selects hyperlocal evidence, joins it to work zones/tasks and proves a feasible operational change.
4. **Why not spreadsheet?** A spreadsheet can model a small day, but it does not autonomously collect/provenance evidence, reconcile heterogeneous constraints, search alternatives, explain exceptions and independently verify the result.
5. **Why not optimizer?** The optimizer cannot decide what evidence is trustworthy, map policy prose to an investigation, handle uncertainty, request missing context, explain the decision or route approval.
6. **Why agent?** Investigation and orchestration span schedule, workface, policy, thermal, advisory and exception data; the agent selects tools and stops when evidence is sufficient.
7. **Why FortyGuard?** It contributes spatial screening, hourly environmental timing, persistence/exceedance and context before onsite attention is available; it must prove a decision delta in final validation.
8. **What is real?** Cached Phoenix FortyGuard data, public ADOT project context and official workflow guidance. Tasks, crews, policy and workface geometry are labelled synthetic.
9. **What improves?** When valid schedule-aligned exceedance evidence exists, the deterministic engine can compare feasible plans by derived SHHCH; no Phoenix reduction is currently demonstrated.
10. **What if wrong?** No schedule is externally changed; stale/unknown evidence blocks recommendation; the superintendent can reject; onsite policy and measurements override; the original plan remains available.

## Lock decision

`CREWCLOCK_MVP_READY = YES`

CrewClock should be formally locked as the hackathon MVP. The locked claim is narrow: **pre-shift operational planning under the contractor’s own constraints**, not safety certification. The final sponsor validation must compare a real multi-zone task ranking under FortyGuard against ordinary forecast data and record whether the operational decision changes.

## Implemented production snapshot

- Canonical route: `/`, with one compact operational workspace and no marketing landing page.
- Deterministic run ID: `CC-PHX-0716-v1`.
- Solver: exhaustive 30-minute interval assignment by crew; feasibility, thermal objective, then minimum movement.
- Selective investigation: 7 movable outdoor tasks investigated, 2 movable shaded tasks skipped, 5 fixed commitments retained.
- Verification: 6/6 modeled hard-constraint families, before recommendation and after approval.
- Approval: local, explicit, auditable, reversible with Reset, and separated from publication.
- Guardrails: `?mode=missing-evidence`, `stale-evidence`, `tool-failure`, `ambiguous-policy`, and `no-improvement` provide deterministic fail-closed QA fixtures.
- Network boundary: the model and browser have no raw external request path; only the trusted production backend can make the controlled FortyGuard heatmap call for an explicit user-created site. Default fixture routes remain offline.
- Primary viewport: 1440×900; verified at 1024×768 and 390×844 without horizontal overflow.

## Foundation lock amendment (2026-08-21)

The product is an upcoming-shift adjustment agent, not a day-ahead “tomorrow planner”. FortyGuard `exceedance` is the SHHCH duration source; `env_params` is selective time-matched context only. The live future capability probe was ambiguous and the current Phoenix replay is labelled `EVIDENCE_UNAVAILABLE` with no demonstrated schedule-aligned exceedance windows.
