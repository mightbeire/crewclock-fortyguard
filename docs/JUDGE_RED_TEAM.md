# Judge red team

Date: 2026-08-19. Answers are deliberately blunt. `STRONG` means directly supported by evidence; `ADEQUATE` means plausible but conditional; `WEAK` means a judge can reasonably reject it; `FATAL` means the current claim should be removed or the concept killed.

## Surface-conditioned Road Repair Queue

| # | Hard question | Answer | Rating |
|---:|---|---|---|
| 1 | Why is heat a queue-priority signal rather than a worker-safety or work-window signal? | The evidence supports worker exposure and treatment-specific pavement windows, but does not prove ambient heat should reorder 311 severity. Reframe the intervention to window verification. | WEAK |
| 2 | Why not use NOAA/NWS? | NDFD and HeatRisk already provide gridded, hourly/daily and duration-aware weather. FortyGuard adds value only if measured surface/context evidence changes a repair-window decision. | ADEQUATE |
| 3 | Is the thermal-load metric invented? | Yes, in the current spike it is an operational proxy over fixture jobs, not a validated health or pavement model. It must not be called thermal load without units and calibration. | FATAL |
| 4 | Where did the work orders come from? | The public MyLA311/PBOT schemas are real, but the spike uses schema-faithful fixtures because this environment did not ingest raw operational rows. | ADEQUATE |
| 5 | Who is the buyer? | A public-works/street-maintenance supervisor or director; IT/GIS and procurement are gatekeepers. A named city and system-of-record are not selected. | ADEQUATE |
| 6 | Does satellite identify pavement well enough? | Sometimes it returns interpretable road/pavement labels, sometimes `others=100%`. It is an evidence gate, not a pavement inventory or defect detector. | ADEQUATE |
| 7 | Can this write back to Cityworks/Maximo? | Not yet. The architecture can produce an approval packet, but a pilot needs an API/export contract and permissions. | WEAK |
| 8 | Why not just use FHWA pavement management? | FHWA already optimizes condition, cost, timing and funding. The wedge is an execution-window check after treatment/priority is determined, not a replacement PMS. | ADEQUATE |
| 9 | What does the agent do that SQL cannot? | Deduplication and missing-field detection can be SQL/rules. The agent’s credible role is selecting evidence, interpreting heterogeneous records, explaining alternatives and requesting approval. | ADEQUATE |
| 10 | What happens if heat evidence is wrong? | No autonomous schedule mutation; the recommendation is advisory, with source, timestamp, uncertainty and local safety-policy caveat. | STRONG |
| 11 | Does FortyGuard’s 100 m evidence materially change city decisions? | The existing 96-tile test showed nearly uniform daily values in one AOI, so spatial value is not proven. A real geography/treatment test is a condition. | WEAK |
| 12 | Is this road repair or heat safety? | Currently both, which is a product-positioning problem. The strongest mutation is heat-safe pavement work-window verification. | WEAK |
| 13 | Can you prove reduced pavement failures? | No. The current metric is a proxy; a pilot would need actual treatment, mat-temperature and closure/rework outcomes. | FATAL |
| 14 | Why would a city change a queue under SLA/liability pressure? | Only when the recommendation preserves severity/SLA and makes the trade-off auditable; otherwise supervisor judgement and incumbent workflows win. | ADEQUATE |
| 15 | Is this just a dashboard? | Without selective investigation, constraint checking, approval and post-decision verification, yes. The agent loop must be visible in the demo. | ADEQUATE |

Road verdict pressure: the original queue claim is too broad. Keep only with a narrower execution-window intervention and a real work-order/SLA join.

## Thermal Sequence Planner

| # | Hard question | Answer | Rating |
|---:|---|---|---|
| 1 | Why not let the FSM optimizer add heat as a cost? | That is the correct deterministic architecture. The product has value only as a selective evidence/exception layer around an incumbent optimizer. | STRONG |
| 2 | Why not use Perry Weather? | Perry already provides site WBGT, policy, work/rest cycles and forecasts. The remaining wedge is cross-job sequence feasibility, not heat monitoring. | ADEQUATE |
| 3 | Why not use NWS HeatRisk/NDFD? | They already provide duration-aware public forecasts. FortyGuard must change a site-level alternative or the dependence score is low. | ADEQUATE |
| 4 | Where are real technician jobs and skills? | They are absent; current profiles and constraints are synthetic/schema-faithful. This prevents a production or adoption claim. | FATAL |
| 5 | What is the safety metric? | A schedule heat proxy is not WBGT exposure. A defensible pilot needs site WBGT or a qualified occupational-health model, workload/PPE/acclimatization and exposure duration. | FATAL |
| 6 | Why an LLM instead of a rules engine? | Rules can apply known heat policies. An agent is justified only for incomplete records, selective tool choice, heterogeneous inputs and explanation—not for route mathematics. | ADEQUATE |
| 7 | Does the dispatcher have authority to break appointments? | Usually not unilaterally; customer commitments, SLA, skill and territory constraints are hard. The product must propose, not execute. | STRONG |
| 8 | Could moving a job increase travel and emissions? | Yes. The objective must include travel, overtime, lateness and workload, with deterministic trade-off reporting. | STRONG |
| 9 | Does FortyGuard resolve a real problem or decorate scheduling? | Current evidence does not establish enough spatial differentiation; it may be decoration unless a pilot shows a schedule change unavailable to standard weather. | WEAK |
| 10 | What sector is this for? | “Field service” is too broad. HVAC, telecom tower, utility line, or industrial inspection each has different PPE, duration and technical limits. | WEAK |
| 11 | Is there a public benchmark? | OR-Tools/Solomon-style VRPTW benchmarks exist, but they are not actual field-service operations and do not validate heat impact. | ADEQUATE |
| 12 | What is the adoption path? | Add a read-only monitor to an existing FSM for a 30-day heat season pilot; no system-of-record replacement. | ADEQUATE |
| 13 | Could incumbent vendors ship this? | Yes, extremely easily once a customer asks for a heat cost/constraint. | WEAK |
| 14 | What happens if the schedule violates heat policy? | Hard constraints and policy checks block the recommendation; no approval packet if required inputs are missing. | STRONG |
| 15 | Does this demonstrate a 10x agentic workflow? | Not yet. The current spike demonstrates tool choice/verification, but not real schedule complexity or measurable dispatch time saved. | WEAK |

Thermal verdict pressure: keep as a research benchmark or integration feature, not a standalone product until a sector and real schedule are secured.

## RailHeat Patrol Sequencer

| # | Hard question | Answer | Rating |
|---:|---|---|---|
| 1 | Does ambient temperature tell you whether rail will buckle? | No. Rail temperature relative to neutral temperature, track restraint, geometry, disturbance and operator rules matter. | FATAL |
| 2 | Can satellite segmentation identify track geometry or CWR condition? | No. It can provide weak physical-context evidence, not a safety-grade track inventory or condition assessment. | FATAL |
| 3 | Who has authority to order a patrol or restriction? | The track owner’s qualified person/engineering and operating-control chain under the railroad’s CWR/inspection procedures. | STRONG |
| 4 | What private fields are missing? | Milepost/track segment, class, CWR plan, RNT, rail temperature, recent surfacing/disturbance, geometry/defect history, crew protection and train conflicts. | FATAL |
| 5 | Why not use FRA ATIP/operator inspection systems? | They already collect materially stronger track-condition evidence. The proposed app cannot replace them. | STRONG |
| 6 | Why not use Maximo/Bentley/Trimble/Wabtec? | Those platforms already own rail assets, inspections, maintenance planning and compliance. A new product must be an evidence/audit layer. | STRONG |
| 7 | Is “weighted unpatrolled heat-hours” a real metric? | No. It is a derived heuristic unless weights map to operator-approved risk and rail-specific thermal measurements. | FATAL |
| 8 | Is this a worker-safety product or asset-safety product? | It is currently confused. Track-worker heat and rail-buckling risk are different hazard models and buyers. | WEAK |
| 9 | Can public FRA data support a credible patrol demo? | It can supply network/crossing/safety context, not the operator’s patrol queue, CWR state or train windows. | ADEQUATE |
| 10 | What happens if the agent recommends the wrong segment? | The consequence can be a missed safety inspection or inappropriate operational action. Autonomous execution is unacceptable. | STRONG |
| 11 | Why FortyGuard rather than a rail-temperature sensor? | A rail-temperature sensor or operator heat rule is closer to the decision. FortyGuard is a screening trigger at best. | FATAL |
| 12 | Does the LA live probe prove rail relevance? | No. It found a small rail segmentation label at a selected date, but the date was cool and the label is not a verified track inventory. | STRONG |
| 13 | Can a 3-minute hackathon demo prove safety value? | No. It can prove evidence rejection, plan-audit traceability and approval gates, not patrol safety or derailment reduction. | STRONG |
| 14 | What is the better intervention? | Audit a railroad-provided summer-preparedness/CWR plan for missing evidence and draft a checklist; do not sequence patrols from ambient heat. | STRONG |
| 15 | Is the current concept worth building? | Not without a rail operator, operator-approved rules/data and a redesigned scope. Under current evidence it should be killed as stated. | FATAL |

Rail verdict pressure: kill the current patrol-sequencing claim. Preserve the evidence-derived plan-audit mutation only as a separate, conditional concept.

## Cross-cutting investor attack

- **Painkiller or vitamin?** Road and thermal are potentially painkillers only at a specific intervention; generic heat ranking is vitamin-like.
- **Frequency?** Road queues and field-service dispatch happen daily; rail summer-preparedness is seasonal and operator-specific.
- **Budget?** Road/rail budgets exist but procurement and integration are slow. FSM vendors already own the budget line.
- **Defensibility?** FortyGuard data alone is not a moat; the defensible asset would be validated decision policy, integration, audit history and outcome data.
- **10x improvement?** Not demonstrated. Current spikes prove a reusable agent loop and cached-live evidence alignment, not operational throughput or safety outcomes.
- **Standalone or feature?** Road/thermal look like features of Cityworks/Maximo/FSM; rail looks like a compliance/audit feature of rail EAM.
- **Expansion?** A narrow evidence-agent platform could expand across heat-sensitive workflows, but only after one integration proves repeated value.
