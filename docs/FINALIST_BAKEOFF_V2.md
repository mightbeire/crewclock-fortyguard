# Finalist bakeoff v2

Date: August 19, 2026. This bakeoff combines the original six candidates, the 12 second-wave concepts, public duplication research, realistic input research, and cached-live geography/challenger spikes. It is a ranking, not an MVP selection.

## Hard elimination

- **Killed:** generic heat alerts/work-rest guidance. Products such as [Perry Weather](https://perryweather.com/features/heat-stress-and-wbgt-monitoring/work-rest-cycles/) already cover localized heat, WBGT/heat index, and work/rest schedules.
- **Killed:** generic field-service or route optimization. Products such as [IBM Maximo](https://www.ibm.com/products/maximo/field-service-management) and commercial field-service suites already cover scheduling, spatial prioritization, and dispatch.
- **Killed:** cold-chain monitoring/dwell alerts. [Copeland](https://www.copeland.com/en-us/products-solutions/controls-solutions/in-transit-solutions) and [TrueCold](https://www.truecold.io/industries/logistics) already combine sensor, location, temperature, and intervention workflows.
- **Killed:** undifferentiated dock/yard scheduling. Public heat playbooks and dock-safety tools already describe the workflow; a new product needs a narrower physical-surface or intervention wedge.
- **Killed:** solar cleaning as a standalone product. Academic optimization is mature and satellite segmentation does not identify panels reliably in the live responses.
- **Killed:** underwriting/property scoring as a finalist. The handbook makes it a valid track example, but claims/portfolio inputs and calibration data are unavailable.
- **Downgraded:** utility vegetation, airport, telecom, and data-center concepts because operational inventories, thresholds, and approval workflows are mostly private.

## Five-concept scorecard

Scores use the handbook rubric: Impact/Relevance 40%, Technical Execution 35%, Innovation 15%, Communication 10%. A score is not a claim of field effectiveness.

| Concept | Impact /40 | Technical /35 | Innovation /15 | Communication /10 | Weighted /10 | Duplication | Input risk | FortyGuard dependence | Build risk | Demo strength | Adoption plausibility |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Surface-conditioned Road Repair Queue | 8.8 | 8.1 | 8.5 | 9.0 | 8.53 | 2 | 2 | 5 | 2 | 9 | 8 |
| Thermal Sequence Planner | 8.5 | 8.4 | 7.4 | 9.1 | 8.36 | 3 | 3 | 5 | 2 | 9 | 8 |
| RailHeat Patrol Sequencer | 8.7 | 7.8 | 8.7 | 8.3 | 8.35 | 2 | 3 | 5 | 3 | 8 | 8 |
| Utility Vegetation Clearance Release Agent | 8.4 | 7.1 | 8.4 | 7.9 | 7.90 | 3 | 4 | 5 | 3 | 7 | 8 |
| Airport Apron Crew Load Balancer | 8.2 | 7.0 | 8.4 | 8.1 | 7.80 | 3 | 4 | 5 | 3 | 8 | 7 |

FortyGuard dependence is intentionally scored separately: 5 means the concept fails or loses its distinctive decision without FortyGuard’s spatial/time evidence. The top three all require more than a decorative API call.

## Challenger spike evidence

### Surface-conditioned Road Repair Queue

- **Source:** cached-live Las Vegas heatmap/env_params/satellite; public schema reference is MyLA311/PBOT.
- **Result:** PASS. Baseline thermal-load proxy 66.0; agent proxy 25.1; improvement 40.9. The agent made three tool calls, verified the metric, produced a trace, and stopped at human approval.
- **Interpretation:** This is the strongest new challenger because it combines a credible public work-order shape, high live heat, interpretable satellite labels, and a clear queue/window action. The metric remains a proxy over schema-faithful work items, not actual repair outcomes.

### RailHeat Patrol Sequencer

- **Source:** cached-live Los Angeles heatmap `time_of_measure`/`persistence` plus satellite; public input reference is FRA ATIP/grade-crossing inventory.
- **Result:** PASS. Weighted unpatrolled heat-hour proxy fell from 23.3333 to 16.6667; improvement 6.6667. The agent made three tool calls, verified the 15:00 UTC peak and 7-hour persistence, produced a trace, and stopped at human approval.
- **Interpretation:** This is a genuinely different enterprise workflow with authoritative heat-patrol rationale. The live rail label is only 1.06% and not a complete track inventory, so the agent must keep the uncertainty visible.

### Thermal Sequence Planner

- **Source:** cached-live Phoenix/Las Vegas/Atlanta environmental profiles, with synthetic job/route constraints.
- **Result:** PASS on all three existing live-profile spikes: Pavement Window 3.2 proxy improvement, Thermal Sequence 2.2, DockShift 2.5; each stopped for human approval.
- **Interpretation:** It survives, but the new road queue now has stronger input realism and a more specific physical-context wedge. Thermal Sequence is not entitled to remain the leader.

## Three evidence-backed finalists

### 1. Surface-conditioned Road Repair Queue

**We are building this for municipal street-maintenance supervisors to solve the problem of prioritizing pavement work orders without exposing crews to avoidable high-heat windows.**

**It requires an agent because it must deduplicate and rank work orders, decide when surface evidence is insufficient, compare windows under SLA constraints, verify the proxy, and ask for approval before changing the work plan.**

**It requires FortyGuard because the decision depends on location/time heat evidence plus environmental context, while satellite segmentation supplies physical-surface context that generic weather and a 311 queue do not provide.**

**We can prove it helped by measuring risk-weighted backlog/SLA preservation, thermal-load proxy reduction, evidence completeness, and API credits per approved batch.**

- **Unique wedge:** public work-order triage joined to live heat timing and physical-context evidence; not a city heat map or generic dispatch tool.
- **Live capabilities:** heatmap `tcm`, env_params, satellite segmentation.
- **Satellite matters:** yes; it is a gate on whether a road/pavement interpretation is supported, and `others=100%` should cause uncertainty rather than a fabricated conclusion.
- **Best demo geography:** Las Vegas dense/paved site.
- **Public duplication evidence:** 311/work-order systems already exist, but the heat/surface-conditioned approval loop is narrower and more defensible; generic heat/work-rest and dispatch products were downgraded.
- **Riskiest assumption:** a city’s live work-order coordinates and severity/SLA fields can be joined to a FortyGuard-covered geography.
- **Spike:** PASS, cached-live Las Vegas evidence, proxy improvement 40.9.

### 2. Thermal Sequence Planner

**We are building this for field-service dispatch managers to solve the problem of feasible job sequences that create unnecessary consecutive high-heat exposure.**

**It requires an agent because it must choose which jobs and FortyGuard calls deserve budget, explore sequence alternatives, preserve appointment/skill constraints, verify a lower proxy, and stop when more evidence is not worth the credits.**

**It requires FortyGuard because tile-level temporal heat, exceedance, persistence, and environmental context are the evidence needed to distinguish otherwise feasible job orders.**

**We can prove it helped by measuring thermal-load proxy reduction, jobs moved out of exceedance windows, appointment feasibility, and API calls per accepted schedule.**

- **Unique wedge:** verification-aware sequence optimization with a credit budget, not merely heat-aware routing.
- **Live capabilities:** env_params; heatmap analysis behavior verified and available for targeted calls.
- **Satellite matters:** no for the base product; it is optional evidence only.
- **Best demo geography:** Phoenix for hot temporal profiles; Las Vegas for a more interpretable surface context if a route site is available.
- **Public duplication evidence:** field-service scheduling and work/rest tools are common; the differentiator is conditional FortyGuard investigation plus verified constraints.
- **Riskiest assumption:** a credible public/partner-like job, skill, travel, and appointment dataset can be attached before submission.
- **Spike:** PASS, cached-live profile; Thermal Sequence improvement 2.2, but operational inputs remain synthetic.

### 3. RailHeat Patrol Sequencer

**We are building this for railroad maintenance planners to solve the problem of deciding which track segments need hot-weather patrols and which patrol window should be used.**

**It requires an agent because it must combine inventory/criticality, peak timing, persistence, rail-context evidence, crew/train constraints, and verification before producing an approval-ready patrol queue.**

**It requires FortyGuard because live heatmap timing and persistence provide the spatial-temporal thermal trigger, while satellite can confirm whether a candidate pixel contains rail-like physical context.**

**We can prove it helped by measuring weighted unpatrolled heat-hours, priority-segment coverage before peak, train-window feasibility, and false-positive context reviews.**

- **Unique wedge:** converts existing extreme-heat rail inspection rules into a source-cited, context-checked patrol queue.
- **Live capabilities:** heatmap `time_of_measure`, heatmap `persistence`, satellite segmentation.
- **Satellite matters:** yes, but as a contextual check rather than a track inventory; the live LA probe found 1.06% rail.
- **Best demo geography:** Los Angeles airport/rail context, with a clear caveat that the selected date was cool.
- **Public duplication evidence:** rail heat rules and inspection systems exist, but an auditable agentic patrol sequencer appears less common than generic alerts; FRA data makes the workflow legible.
- **Riskiest assumption:** actual track geometry, milepost, and operator thresholds are available for the chosen demo corridor.
- **Spike:** PASS, cached-live LA analysis + satellite, proxy improvement 6.6667.

`PREVIOUS_LEADER_SURVIVED = YES`
`CURRENT_EVIDENCE_LEADER = Surface-conditioned Road Repair Queue (tentative)`
`FINAL_MVP_SELECTED = NO`
