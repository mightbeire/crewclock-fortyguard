# Executive Summary

Date: 2026-08-19. This is a falsification-oriented review of the three finalists using cached-live FortyGuard results, public operational schemas, government/regulatory sources, official incumbent documentation, public datasets and duplication research. No new FortyGuard calls were made.

## Executive findings

1. **Surface-conditioned Road Repair Queue — BUILD WITH CONDITIONS.** A real public-works user and work-order workflow are verified, and road work creates a credible intersection of worker heat exposure and treatment-specific material windows. The current “reorder the queue by thermal load” claim is too broad. The build condition is to narrow the intervention to an approved road job’s execution-window verification, use site WBGT/material-temperature evidence where safety or pavement quality is claimed, and prove a real system-of-record join.
2. **Thermal Sequence Planner — HOLD.** Field-service dispatch is a real, frequent workflow, but ServiceNow, Salesforce, Dynamics, Maximo, Perry Weather and deterministic VRP solvers already cover most of the proposed job. Current technician/job/skill data is synthetic, the heat metric is not a safety measure, and FortyGuard’s incremental value is unproven. A read-only exception-agent mutation remains plausible.
3. **RailHeat Patrol Sequencer — KILL.** Rail heat risk is real, but the current intervention is not supported by the available evidence. FRA/Amtrak show that CWR decisions require rail temperature, neutral temperature, track condition, operator procedures and qualified-person authority. FortyGuard ambient heat plus satellite rail context cannot safely determine patrol need or sequence. Preserve only a plan-audit mutation.

## Research question zero

The research found an elegant solution around FortyGuard in two places: Thermal Sequence is close to “put heat into an existing optimizer,” and RailHeat is close to “use a weather layer to imply rail safety.” Road has the strongest real problem, but only after separating queue priority from work-window feasibility. The project should not claim that FortyGuard itself determines worker safety, pavement quality or rail-buckling risk.

# Surface-conditioned Road Repair Queue

## User

**Verified role:** Street Maintenance Superintendent, Public Works Operations Supervisor, Street/Highway Maintenance Scheduler, or equivalent city transportation operations role. Organization: municipal public works/transportation/street department. The role coordinates service requests, inspectors, crews, contractors, GIS/311 staff and work-order priorities. The system-of-record is likely Cityworks/Trimble Unity, Maximo, Cartegraph/OpenGov, an Esri-backed custom system or a municipal 311/CMMS combination.

Decision authority is partial: a supervisor can usually recommend or schedule work, but pavement treatment, procurement, traffic control, safety policy and contractor obligations may be owned by other roles. User exists = **VERIFIED**; exact title and approval chain require a city pilot.

## Problem

The credible problem is not “heat makes a low-priority pothole urgent.” It is: **after a street job is selected on condition, severity, equity, traffic, age and SLA grounds, which feasible execution window preserves worker safety and treatment quality without breaking the queue?** This is narrower and better supported.

## Real workflow

See `docs/WORKFLOW_RESEARCH.md`. MyLA311 and Cityworks verify intake, assignment, status, coordinates, work-order/inspection records and field closure. FHWA verifies pavement-management prioritization and treatment timing. The exact city heat policy, work-rest method, contractor SLA, mix, crew calendar, traffic-control window and post-repair quality measure are unknown.

## Evidence heat matters

| Relationship | Classification | Evidence and boundary |
|---|---|---|
| Outdoor pavement work exposes crews to heat | VERIFIED | OSHA/NIOSH identify outdoor physical activity, sunlight, humidity, clothing/PPE, workload and heat sources as relevant. |
| Ambient heat alone is a worker-safety decision | UNSUPPORTED | OSHA/NIOSH prefer site WBGT with workload, acclimatization and clothing; FortyGuard profile is not WBGT. |
| Pavement/material behavior is temperature-sensitive | VERIFIED | FHWA documents asphalt temperature, cooling, compaction and temperature-dependent pavement response. |
| FortyGuard ambient/surface temperature directly determines treatment quality | UNSUPPORTED | Mix, lift, delivery, mat temperature, surface condition and local specification are missing. |
| Heat can affect work windows and productivity | SUPPORTED BUT CONTEXT-DEPENDENT | Early/late work, breaks, traffic control, equipment and material delivery can change; no public city policy was found that validates the project’s proxy. |
| Heat should reorder a 311 backlog | WEAK | FHWA prioritizes condition/cost/timing/funding; no source supports a generic heat-based queue rank. |

## Why FortyGuard

Ordinary public weather is a serious substitute. NOAA NDFD provides gridded hourly/short-horizon forecasts at roughly 2.5 km native resolution; NWS HeatRisk adds duration, climatology and CDC heat-health context. OSHA cautions that weather reports can miss site sunlight, radiant heat, wind blockage and heat-absorbing roads, which is the strongest general case for more local/site evidence.

FortyGuard adds potentially useful properties: approximately 60/80/100 m heatmap cells in the observed API contract, time-of-measure/exceedance/persistence analysis, environmental profiles and satellite physical-context labels. But the existing 96-tile test showed only about 0.046°C variation in average temperature and about 0.016°C in maximum temperature across the selected AOI/date. That is direct falsification of the claim that the current test proves strong spatial ranking.

**FORTYGUARD DEPENDENCE = 4/10.** A normal weather API preserves most of the planning value. FortyGuard becomes important only if a real city job sits in a spatially heterogeneous surface context and the heat/surface evidence changes an approved job window or treatment choice. Satellite is an evidence gate, not a pavement-quality sensor.

## Why agent

The core prioritization is a database/rules/optimization problem. Cityworks, Maximo and pavement-management systems already own the work order, asset, map, SLA and crew data. A legitimate agent role remains:

- detect duplicates and incomplete records;
- decide which candidate jobs require environmental investigation;
- choose between heatmap, env parameters and satellite evidence within a credit budget;
- interpret heterogeneous request/asset/treatment records;
- produce window alternatives that preserve SLA and crew/material constraints;
- verify the proposed proxy and surface uncertainty;
- request supervisor approval and retain an audit trail.

**AGENTIC NECESSITY = 5/10.** It is meaningful as a conditional evidence-and-approval layer; it is not necessary for the deterministic queue or schedule calculation.

## Existing tools and competitors

Cityworks/Trimble Unity, IBM Maximo, Bentley AssetWise, 311 portals and pavement-management systems already cover asset/work data, GIS, inspections, prioritization and scheduling. FHWA’s PaveCool demonstrates that a deterministic compaction-window tool is a plausible substitute for a generic language-model recommendation. RoadAI, Spothole, Pothole Locator and related research already cover AI road detection/prioritization.

The wedge is therefore an adapter/agent beside the system of record, not a new CMMS or pavement optimizer. See `docs/COMPETITOR_ANALYSIS.md`.

## Demo data

Best non-fabricated sources: MyLA311 2024 (1.44M rows, 34 documented columns, coordinates, request/assignment/status/dates, daily refresh) and Portland PBOT public maintenance layers. They give credible input shape, but a hackathon demo still lacks validated city SLA, asset condition, treatment, crew, material and closure-outcome joins. NYC AMPS is an additional public work-order schema, not a tested FortyGuard geography.

**DEMO DATA QUALITY = 7/10.** Public intake/work-order schemas are strong; the operational decision fields and live join are missing.

## Decision model

Recommended deterministic model for the mutation:

**Inputs:** approved work orders, location/road segment, severity/condition, SLA/due date, treatment type, estimated duration, crew/equipment, traffic-control windows, materials/mix, site WBGT or qualified heat policy input, pavement/surface temperature if available, FortyGuard heat timing/persistence/surface context, and forecast uncertainty.

**Variables:** selected job batch; start/end window; crew/equipment assignment; optional defer/advance decision; evidence status.

**Hard constraints:** statutory/municipal SLA, severity/criticality, traffic-control permit, crew/equipment/skill availability, material/treatment temperature limits, local EHS policy, no schedule change without approval.

**Objective:** minimize avoidable worker exposure and treatment-quality risk plus travel/overtime/late-SLA cost, subject to preserving emergency work and approved service commitments. Exact weights must be city-approved; do not hide arbitrary weights in “thermal load.”

**Agent responsibility:** identify missing fields, select evidence, ask for approval, explain trade-offs, verify. **Optimizer/rules responsibility:** calculate feasible windows and rank alternatives.

## Measurement quality

| Current metric | Type | Audit result / replacement |
|---|---|---|
| `thermal-load proxy` | heuristic | Weak and unitless. Replace with `estimated worker heat-exposure minutes above the approved site policy threshold` only when site WBGT/workload/PPE inputs exist; otherwise call it `environmental heat-screening score`. |
| `SLA preservation` | directly measured if source fields exist | Strong operational measure: count/percentage of jobs meeting source-system due dates. Current fixture is not field outcome evidence. |
| `backlog prioritization` | derived/operational | Use risk-weighted overdue backlog with documented source weights; do not imply heat caused improvement. |
| `evidence completeness` | derived | Strong for agent quality: required fields present, source timestamps, confidence, rejected/accepted satellite context. |
| `API credits per batch` | directly measured | Strong hackathon efficiency metric, not customer impact. |
| proxy improvement 40.9 | derived over cached-live fixture | Valid computation, not pavement or safety outcome. Must be labelled fixture result. |

## Adoption

Champion: street-maintenance operations supervisor or innovation/GIS lead. Economic buyer: public works/transportation director or city CIO. Gatekeepers: GIS/IT/security, procurement, labor/EHS, legal and contractor management. System-of-record integration is the largest friction. A believable 30-day pilot is read-only: ingest 2–4 weeks of closed/open jobs, compare the agent’s proposed windows with supervisor decisions, measure missing evidence and SLA-preserving alternatives, and do not write back.

**ADOPTION PLAUSIBILITY = 5/10.** The pain is recurring and data shape is available, but municipal procurement/integration is slow and incumbent platforms can absorb the feature.

## Safety/liability

The agent may recommend a window or request additional evidence. It must never declare a worker safe, replace an EHS assessment, override an emergency/SLA decision, set a treatment temperature, or dispatch a crew automatically. Evidence must include source, timestamp, geography, metric definition, uncertainty, policy version and approval identity. All outputs are advisory until a qualified local safety/engineering authority approves them.

## Fatal weaknesses

- The current queue objective confuses backlog priority with heat-sensitive execution timing.
- FortyGuard output is not site WBGT and cannot certify worker safety.
- The live spatial test does not prove useful within-city variation.
- The demo lacks a real city system-of-record join and treatment/SLA outcomes.

## Rubric score

| Category | Score | Evidence for | Evidence against | Confidence |
|---|---:|---|---|---|
| Impact & relevance /40 | 30 | Daily municipal backlog, outdoor crews, pavement quality and service obligations are real. | Heat is not shown to be a primary queue driver. | Medium |
| Technical execution /35 | 26 | Cached-live API schemas, agent trace, approval gate and public schemas work. | Operational fields are fixtures; no real integration; proxy is weak. | High |
| Innovation /15 | 10 | Heat + physical-context evidence in a work-order approval loop is narrower than generic heat maps. | Cityworks/Maximo/FHWA and road-AI projects occupy adjacent territory. | Medium |
| Communication /10 | 8 | Clear before/after approval trace possible. | Must explain what is not measured. | Medium |
| Weighted | 7.4/10 |  |  | Medium |

## Verdict: BUILD WITH CONDITIONS

Build only the narrow work-window/evidence verifier mutation first. Do not build a generic heat-ranked municipal queue or claim pavement/worker outcomes before a real pilot dataset and approved metric exist.

# Thermal Sequence Planner

## User

**Verified roles:** Field Service Dispatch Manager, Dispatch Supervisor, Resource Scheduler, Service Operations Coordinator, Workforce Planning Manager. Organizations include utilities, telecom, HVAC, facilities, elevator, appliance and industrial service. Dispatcher, customer service, EHS, FSM administrator and IT/security share authority. User exists = **VERIFIED**; heat-specific decision authority = **PARTIAL**.

## Problem and workflow

The real problem is feasible sequences with unnecessary exposure or policy burden. The normal workflow is CRM/FSM work-order creation → priority/SLA/promise/skill/duration classification → deterministic dispatch/optimization → intraday changes → technician execution and closure. Incumbent docs from ServiceNow, Salesforce, Microsoft and IBM verify this workflow and already expose many relevant constraints.

## Evidence heat matters

| Relationship | Classification | Evidence and boundary |
|---|---|---|
| Outdoor service work creates worker heat risk | VERIFIED | OSHA/NIOSH workload, site, PPE and acclimatization guidance. |
| Job sequence can reduce exposure while preserving service | SUPPORTED BUT CONTEXT-DEPENDENT | Feasible only for a selected trade with real durations, site conditions and policy. |
| Ambient/apparent temperature is a safety measure | UNSUPPORTED | Site WBGT/workload/PPE/acclimatization are missing. |
| Heat affects equipment/service quality | SUPPORTED BUT CONTEXT-DEPENDENT | Trade/manufacturer-specific; no sector selected. |
| Heat should be a route objective | SUPPORTED BUT CONTEXT-DEPENDENT | It can be a soft cost; it cannot override hard appointment, skill, safety or SLA constraints. |

## Why FortyGuard

FortyGuard could add spatial/time evidence, exceedance/persistence and satellite context to otherwise feasible job alternatives. But NDFD/HeatRisk already provide strong public forecasts, and Perry Weather provides site WBGT/work-rest planning with policy/PPE/acclimatization. The current live evidence does not show enough within-route spatial variation to establish a unique advantage.

**FORTYGUARD DEPENDENCE = 3/10.** A normal forecast plus a site-sensor/WBGT vendor preserves most value. FortyGuard is only decisive if a pilot demonstrates a location/time decision that materially changes the incumbent schedule.

## Why agent

Scheduling math belongs in a VRPTW/constraint solver. The agent can add value by monitoring the schedule, identifying exposed jobs, deciding when deeper evidence is worth requesting, interpreting unstructured job notes, proposing alternatives and verifying hard constraints. That is a useful integration pattern but not a standalone optimizer.

**AGENTIC NECESSITY = 4/10.** Existing FSM products already have dynamic/intraday optimization and AI features; the additional evidence loop is credible but narrow.

## Existing tools and competitors

ServiceNow, Salesforce, Dynamics and Maximo already provide skills, locations, travel, appointments, SLAs, dynamic scheduling and optimization. Perry Weather provides local WBGT/work-rest policy. OR-Tools provides deterministic VRPTW primitives. A feature can be absorbed by any of them.

## Demo data

OR-Tools/VRPTW benchmarks and generic schema fixtures are credible for algorithm demonstration but are not actual field-service operations. The repository has no real technician availability, skill matrix, travel time, customer promise or closure data.

**DEMO DATA QUALITY = 4/10.** Good for a solver test; weak for an operational product claim.

## Decision model

**Inputs:** work order, location, service duration, promise window, skills, technician shift, travel matrix, priority/SLA, PPE/workload/acclimatization policy, site WBGT or approved heat input, FortyGuard temporal evidence.

**Variables:** assignment, sequence, start time, break placement, optional defer/reassign.

**Hard constraints:** appointment/promise window, technician skill/territory, shift, travel, job duration, legal/EHS policy, emergency priority.

**Objective:** minimize travel/overtime/lateness plus approved heat-exposure cost, subject to all hard constraints. Heat cost must be calibrated and should not be presented as physiological exposure without WBGT inputs.

**Agent:** monitor and investigate selectively, explain trade-offs, request approval. **Solver:** solve and verify the constrained schedule.

## Measurement quality

| Current metric | Type | Audit result / replacement |
|---|---|---|
| `thermal-load reduction` | heuristic | Not a safety outcome. Replace with `scheduled job-minutes in an approved heat-screen band` or site-WBGT exposure minutes when available. |
| jobs moved outside exceedance periods | derived | Defensible only if exceedance threshold/source is specified and appointments remain feasible. |
| appointment feasibility | directly measured | Strong: all hard promise/skill/shift constraints satisfied. |
| API calls per schedule | directly measured | Strong efficiency metric, not customer value. |
| sequence proxy improvement 2.2 | derived over synthetic jobs | Computation is valid; operational significance is unproven. |

## Adoption

Champion: dispatch operations or EHS innovation lead. Buyer: VP/Director of field service or operations. Gatekeepers: FSM admin, IT/security, customer-service leadership, legal/EHS and labor. Pilot: read-only monitor against an existing FSM schedule during one hot month; compare agent proposals with dispatcher decisions, hard-constraint violations avoided and high-heat task minutes under the employer’s approved policy.

**ADOPTION PLAUSIBILITY = 4/10.** Frequent pain, but platform absorbability and data/integration friction are high.

## Safety/liability

Never infer safe exposure from FortyGuard air temperature. Do not reorder emergency work or customer commitments automatically. Require employer policy, site measurement or qualified occupational-health review for any work/rest claim. Retain the schedule snapshot, inputs, solver result, evidence timestamps, policy version and approval.

## Fatal weaknesses

- No real field-service operational input or chosen trade.
- Existing FSM optimizers already solve the core sequence problem.
- Perry Weather and OSHA/NIOSH cover heat-safety inputs more directly.
- FortyGuard dependence and measurable-outcome strength are low.

## Rubric score

| Category | Score | Evidence for | Evidence against | Confidence |
|---|---:|---|---|---|
| Impact & relevance /40 | 29 | Daily dispatch and outdoor exposure are real. | Heat is one of many constraints; user/buyer boundary is unresolved. | Medium |
| Technical execution /35 | 28 | Agentic evidence selection, solver separation and cached-live profiles work. | No real route/job data; no deterministic production optimizer integrated. | High |
| Innovation /15 | 7 | Selective FortyGuard investigation around a schedule is a useful pattern. | Generic heat-aware scheduling is crowded and platform-absorbable. | High |
| Communication /10 | 8 | Easy to show before/after sequence and approval. | Risk of looking like a weather overlay on a route optimizer. | Medium |
| Weighted | 7.2/10 |  |  | Medium |

## Verdict: HOLD

Hold the standalone concept. Reopen only with one sector, one real FSM export, site-WBGT/policy inputs and a measurable exception workflow that existing scheduling software does not already provide.

# RailHeat Patrol Sequencer

## User

**Verified roles:** Maintenance-of-Way Planner, Track Supervisor, Roadmaster, Chief Engineer–Track, Railroad Engineering Manager, Track Inspector and Train Dispatcher/Operations Control. FRA regulations and Amtrak procedures verify the authority chain. User exists = **VERIFIED**; public access to the exact patrol decision inputs = **NO**.

## Problem and workflow

Extreme heat and CWR buckling are real. But the actual workflow begins with the railroad’s CWR plan, track class, inspection schedule, rail temperature/RNT, recent maintenance, geometry/defect history and qualified-person judgment. Track access and train movement are coordinated through railroad control; deviations trigger remedial action under regulation.

## Evidence heat matters

| Relationship | Classification | Evidence and boundary |
|---|---|---|
| Heat can cause CWR thermal compression/buckling | VERIFIED | FRA/Amtrak documents and research establish the physical hazard. |
| Ambient heat alone identifies hazardous track segments | UNSUPPORTED | Rail temperature can exceed ambient; risk depends on RNT, restraint, geometry, disturbance and operator plan. |
| Heat can create patrol/restriction consequences | VERIFIED | FRA safety advisory and track rules support additional inspection/remedial/operational controls. |
| Worker heat exposure matters | SUPPORTED BUT CONTEXT-DEPENDENT | Track work is outdoor physical work, but it is a separate hazard model from rail buckling. |
| Satellite “rail” label verifies patrol eligibility | UNSUPPORTED | Satellite context cannot supply track geometry, CWR state, RNT, defects or ownership. |

## Why FortyGuard

FortyGuard’s temporal heat/persistence layer could be a preliminary screen for a railroad’s summer-preparedness review. NOAA/NWS and local rail temperature sensors/operators are closer substitutes. The project’s cached LA satellite probe found only a 1.06% rail label at a cool selected date and no verified track inventory.

**FORTYGUARD DEPENDENCE = 1/10.** The current safety decision does not require FortyGuard; a rail-temperature sensor, railroad heat order or NWS forecast is more operationally proximate. FortyGuard could add context to a plan audit, but it cannot be the authority.

## Why agent

An agent could reconcile a CWR plan, seasonal checklist, asset/inspection records and evidence completeness, identify missing RNT/rail-temperature/track-protection fields, and draft an approval packet. It should not calculate or autonomously prescribe patrols from ambient heat.

**AGENTIC NECESSITY = 3/10.** Checklist/audit automation is useful, but deterministic compliance rules and existing rail EAM/inspection platforms can do most of it.

## Existing tools and competitors

FRA ATIP, Bentley AssetWise, Trimble rail solutions, Wabtec RailDOCS/wayside products, IBM Maximo Transportation and railroad CWR procedures already cover rail asset/inspection/maintenance planning. Public FRA GIS and safety data are context sources, not a complete patrol system.

## Demo data

FRA ATIP, safety data, grade crossings, NTAD rail lines and Amtrak documents are authoritative public sources. They do not expose an operator’s full track inventory, RNT, rail-temperature telemetry, CWR plan implementation, crew windows or train conflicts.

**DEMO DATA QUALITY = 3/10** for patrol sequencing; **6/10** for a plan-evidence audit.

## Decision model

For the current concept, required inputs would include track segment/milepost, CWR/track class, RNT, rail temperature, recent disturbance, geometry/defect history, criticality, inspection frequency, qualified crew, protection method and train windows.

The objective could minimize weighted uninspected exposure subject to regulatory frequency, qualified-person authority, track access and train conflicts—but weights and thresholds must be operator-approved. FortyGuard ambient heat can be an investigation trigger only.

**Agent:** check missing evidence, cite the CWR plan, select follow-up evidence, draft a patrol/checklist proposal, escalate ambiguity. **Deterministic/rail-authority system:** enforce regulation and solve access/crew scheduling.

## Measurement quality

| Current metric | Type | Audit result / replacement |
|---|---|---|
| weighted unpatrolled heat-hours | heuristic | Not a recognized rail-safety outcome; weights/thresholds are invented. Replace with operator-approved `segments meeting required inspection before approved trigger` and `hours of required work unassigned`, with rail-specific inputs. |
| pre-peak patrol coverage | derived | Potentially useful only against an operator-defined patrol requirement and qualified inspection record. |
| operational feasibility | directly measured if real train/crew windows exist | Current fixture does not have them. |
| false-positive contextual reviews | derived | Useful agent-quality metric for satellite/evidence rejection, not safety effectiveness. |
| proxy improvement 6.6667 | derived over fixture | Computation valid; not a rail-risk reduction claim. |

## Adoption

Champion: railroad engineering/MOW digitalization or safety program. Buyer: chief engineer, infrastructure/asset-management leader or operations technology. Gatekeepers: railroad safety, labor, operating control, cybersecurity, procurement and regulator-facing engineering. A 30-day pilot would be plan-audit/read-only on one corridor with operator-provided CWR/summer-preparedness records. It would measure missing-evidence detection and review time, not derailment or safety outcomes.

**ADOPTION PLAUSIBILITY = 2/10** for the current patrol sequencer; **4/10** for a tightly scoped audit with an operator partner.

## Safety/liability

The agent must never issue a slow order, authorize track occupancy, schedule a patrol without qualified-person review, override CWR procedures, declare rail safe, or substitute FortyGuard for rail-temperature/RNT measurements. Evidence needs operator source, plan/version, segment/milepost, timestamp, rail/ambient distinction, measurement quality and approval identity.

## Fatal weaknesses

- The current input does not measure the physical variable that drives the asset-risk claim.
- Required private/operator data is absent.
- A satellite rail label is not a track inventory or condition measurement.
- Existing rail inspection/EAM platforms and CWR plans own the workflow.
- Wrong recommendations can have safety-critical consequences.

## Rubric score

| Category | Score | Evidence for | Evidence against | Confidence |
|---|---:|---|---|---|
| Impact & relevance /40 | 27 | Rail heat risk and inspection consequences are high impact. | Current product cannot support the decision safely. | High |
| Technical execution /35 | 20 | Cached-live heat/satellite agent trace and approval gates work. | Critical rail inputs and operator integration missing. | High |
| Innovation /15 | 9 | Rail-specific evidence/audit mutation is differentiated from generic heat alerts. | Current patrol claim is an unsafe recombination of known data. | Medium |
| Communication /10 | 7 | Strong red-team story if the demo rejects unsupported evidence. | Positive patrol demo would overclaim. | High |
| Weighted | 6.3/10 |  |  | High |

## Verdict: KILL

Kill **RailHeat Patrol Sequencer as currently defined**. Do not spend MVP effort on patrol sequencing from FortyGuard ambient heat and satellite context. The plan-audit mutation is retained below as research direction, not as a current finalist rescue.

# Evidence-derived Mutations

## 1. Heat-Safe Pavement Work-Window Verifier — strongest mutation

**Parent:** Road Repair Queue. **Evidence:** FHWA makes material/compaction windows specific; OSHA makes worker heat site/workload/PPE-specific; public work-order schemas provide intake and SLA context. **User:** municipal street-maintenance supervisor plus pavement/construction engineer/EHS reviewer. **Intervention:** verify the feasible execution window for a selected treatment; do not reorder a 311 backlog from heat alone.

**Inputs:** work order/treatment/mix, surface/mat temperature if available, site WBGT or qualified policy input, crew/PPE/workload, traffic-control window, FortyGuard timing/surface context. **Agent:** detect missing evidence and choose evidence calls. **Solver/rules:** calculate allowed windows. **Human:** approve.

**Scores:** FortyGuard dependence 5/10; agentic necessity 6/10; demo data quality 6/10; adoption plausibility 6/10; liability complexity 6/10. **Verdict:** BUILD WITH CONDITIONS. The condition is a real city/contractor job sample and a qualified metric definition.

## 2. Rail Summer Preparedness Evidence Agent

**Parent:** RailHeat. **Evidence:** FRA/Amtrak show operator-specific plans, RNT/rail-temperature records and seasonal activities. **Intervention:** audit a selected corridor’s CWR/summer-preparedness packet, detect missing plan evidence, and draft a human review queue. FortyGuard is a screening trigger, not a rail-safety oracle.

**Scores:** FortyGuard dependence 2/10; agentic necessity 5/10; demo data quality 6/10 with operator records; adoption plausibility 4/10; liability complexity 9/10. **Verdict:** BUILD WITH CONDITIONS only with a railroad/qualified engineering reviewer; otherwise HOLD.

## 3. FSM Heat-Exception Evidence Agent

**Parent:** Thermal Sequence. **Evidence:** FSM incumbents solve scheduling; Perry/OSHA solve heat measurement/policy. **Intervention:** watch an existing schedule, investigate only jobs where heat could alter a feasible choice, and return an exception packet. No new optimizer, no standalone heat dashboard.

**Scores:** FortyGuard dependence 3/10; agentic necessity 5/10; demo data quality 5/10 with a chosen trade; adoption plausibility 5/10; liability complexity 7/10. **Verdict:** HOLD pending real FSM export and employer-approved policy.

# Comparative Matrix

| Dimension | Road Repair Queue | Thermal Sequence | RailHeat Patrol |
|---|---:|---:|---:|
| Actual user exists | VERIFIED | VERIFIED | VERIFIED |
| Current decision verified | PARTIAL | VERIFIED | PARTIAL |
| Heat relevance | 7/10 | 6/10 | 8/10 for asset, 4/10 for current input |
| FortyGuard dependence | 4/10 | 3/10 | 1/10 |
| Agentic necessity | 5/10 | 4/10 | 3/10 |
| Demo data quality | 7/10 | 4/10 | 3/10 current / 6/10 audit mutation |
| Adoption plausibility | 5/10 | 4/10 | 2/10 current / 4/10 mutation |
| Integration complexity | 7/10 | 8/10 | 9/10 |
| Liability complexity | 6/10 | 7/10 | 10/10 |
| Measurable-outcome strength | 5/10 | 4/10 | 2/10 current |
| 3-minute demo strength | 8/10 | 8/10 | 6/10 if showing rejection/audit; 3/10 if claiming safety |
| Duplication risk | 3/5 | 4/5 | 3/5 current, 4/5 audit feature |
| Official rubric weighted score | 7.4/10 | 7.2/10 | 6.3/10 |
| Required verdict | BUILD WITH CONDITIONS | HOLD | KILL |

# Final Research Ranking

1. **Surface-conditioned Road Repair Queue — BUILD WITH CONDITIONS**, only as the narrower Heat-Safe Pavement Work-Window Verifier.
2. **Thermal Sequence Planner — HOLD**, only as a read-only FSM exception mutation after a real sector/data partner is found.
3. **RailHeat Patrol Sequencer — KILL as stated**; preserve only the operator-specific plan-audit mutation.

This is a research ranking, not an MVP selection. `FINAL_MVP_SELECTED = NO`.

# Fatal-evidence ledger

| Concept | Fatal evidence found | Status |
|---|---|---|
| Road | OSHA metric mismatch; FHWA does not support generic heat queue ranking; current spatial test weak; no real city join. | Recoverable by narrowing to work-window verification. |
| Thermal | Mature FSM optimization; Perry Weather/OSHA cover heat policy; no real job data; heat proxy is not WBGT. | Standalone concept fails; integration mutation remains possible. |
| Rail | Rail safety depends on rail temperature/RNT/CWR/qualified authority; satellite/ambient inputs cannot establish risk; operator data private. | Fatal for current patrol sequencer. |

# Research direction if mutations also fail

Search for a recurring, approval-bound outdoor work decision where: (1) an existing system of record has public or partner-accessible work items; (2) heat changes a window or control rather than merely producing an alert; (3) the accepted metric is already defined by policy or engineering; (4) a deterministic optimizer/rules engine can enforce constraints; and (5) the agent’s unique job is evidence selection, uncertainty handling and human-approved exception management. Avoid generic heat safety, routing, satellite scoring and safety-critical asset claims without domain measurements.
