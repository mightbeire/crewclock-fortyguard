# Finalist evaluation

Scores use the handbook's weights: Impact/Relevance 40%, Technical Execution 35%, Innovation 15%, Communication 10%. Scores are judgment calls based on the evidence collected, not outcomes claimed from a production deployment. Live evidence has lowered confidence in spatial differentiation and in all operational metrics because the work windows and constraints remain synthetic.

## Weighted scores

| Finalist | Impact /40 | Technical /35 | Innovation /15 | Communication /10 | Weighted /10 | Duplication | Build risk | API/data risk | Dependency risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pavement Window Agent | 8.2 | 8.0 | 8.1 | 8.7 | 8.17 | 2 | 2 | 3 | 2 |
| Thermal Sequence Planner | 8.5 | 8.5 | 7.4 | 9.2 | 8.41 | 3 | 2 | 3 | 2 |
| DockShift Orchestrator | 8.0 | 8.0 | 8.0 | 8.3 | 8.03 | 2 | 2 | 3 | 3 |
| Data Center Cooling Readiness | 8.5 | 7.7 | 8.1 | 7.6 | 8.10 | 2 | 3 | 3 | 4 |
| Cooling Center Logistics | 9.0 | 7.2 | 8.0 | 8.0 | 8.12 | 3 | 3 | 3 | 4 |
| Transit Stop Intervention Triage | 7.8 | 7.7 | 7.0 | 8.0 | 7.63 | 3 | 2 | 2 | 3 |

## Handbook alignment

The three finalists align most directly with the Agentic Track and Industrial & Enterprise track: each plans, calls, compares, and proposes an operational decision. The handbook requires a live demo, judge-accessible code/README, a roughly three-minute video, and a maximum 500-word problem → user → FortyGuard → measured-result summary. Those are submission-stage requirements; none is being produced or implied as complete during discovery.

## Live validation and falsification attempt

- `/v1/heatmap` and `/v1/env_params` completed against the live Hackathon account. The exact schemas, temporal resolution, and credit deltas are recorded in `docs/LIVE_API_VALIDATION.md`.
- The three spikes were rerun using the cached successful live apparent-temperature profile. They all passed the agent control-loop check, but their work windows, route/task constraints, and measured improvements are synthetic proxy inputs.
- A 96-tile live heatmap test produced only approximately 0.05°C average-temperature range and approximately 0.02°C maximum-temperature range across the selected small AOI/date. A live exceedance test returned one hour for every tile. This falsifies the claim that the current test already proves strong spatial ranking. It does not eliminate the concepts, but it downgrades spatial/API confidence and makes temporal scheduling the more defensible current evidence.
- No finalist was eliminated because the test was designed to probe API behavior and temporal/spatial signal, not to make a production claim about any one geography. The ranking remains tentative and is not an MVP selection.

## Evidence and limitations

- The local fixtures show meaningful variation across a broader synthetic portfolio, but the live multi-tile test did not reproduce strong variation in its selected small AOI/date. Fixture evidence is therefore not sufficient for spatial finalist claims.
- The deterministic spikes use a successful cached-live environmental hourly profile and synthetic operational windows. The improvement is a proxy result, not a field outcome.
- Every spike ended at a human approval checkpoint and produced a trace. This demonstrates the control loop, not a safe-to-operate certification.
- Satellite Premium access is verified, but exact live per-call costs vary by request and street-view/heat-intelligence access remain unverified. The finalist designs work with heatmap/env params first.

## Three exploration finalists

### 1. Pavement Window Agent

**One-sentence product definition:** We are building this for municipal road-maintenance supervisors to choose lower-heat paving, striping, sealant, or inspection windows without breaking traffic and crew constraints.

**Why agent:** It investigates only the candidate work zones/windows that need evidence, compares alternatives, proposes a window, and verifies the proxy plus hard constraints before asking for approval.

**Why FortyGuard:** Heatmap peak timing, exceedance, and persistence give a spatial-temporal view of the actual work zone that a generic weather alert cannot replace.

**Agent loop:** Work order → coarse heat profile → targeted exceedance/persistence → window candidates → constraint check → approval proposal → proxy verification → adapt.

**Demo story:** Two work windows for one road segment compete; the agent selects the less persistent hot window, cites the exact FortyGuard evidence, and pauses for supervisor approval.

**Measured outcome:** Difference in thermal-load proxy and continuous exceedance hours between baseline and selected window, with all traffic/crew constraints satisfied.

**Required data:** Work-zone polygon, candidate windows, crew/traffic constraints, threshold policy, and FortyGuard heatmap/env responses.

**Build estimate:** A thin MVP can use the existing toolkit, fixture-backed heat layers, a small work-window schema, and a minimal action proposal view.

**Unique wedge:** Asset-quality review plus worker scheduling for one industrial work order, rather than a generic heat alert or city heat map.

**Spike result:** PASS — cached-live profile; baseline proxy 3.2, agent candidate proxy 0.0, improvement 3.2. The approval checkpoint passed; operational constraints are synthetic.

### 2. Thermal Sequence Planner

**One-sentence product definition:** We are building this for field-service dispatch managers to resequence technician jobs so hot-site exposure is lower while appointments, skills, and travel constraints remain feasible.

**Why agent:** It must explore combinatorial job orders, decide which FortyGuard evidence is worth the API budget, propose a resequence, and verify feasibility and proxy improvement.

**Why FortyGuard:** Nearby jobs can have different tile-level peaks and persistence; the agent needs those differences to choose between otherwise feasible sequences.

**Agent loop:** Jobs/constraints → location screen → targeted profile calls → sequence alternatives → constraint check → approval proposal → metric verification → adapt.

**Demo story:** A four-job route is feasible but thermally poor; the agent swaps two jobs, preserves the appointment promises, and shows a lower proxy.

**Measured outcome:** Thermal-load proxy reduction, jobs moved out of exceedance windows, appointment feasibility, and API calls per schedule.

**Required data:** Job coordinates/windows/durations, technician skills, travel-time fixture, threshold policy, and FortyGuard responses.

**Build estimate:** High feasibility; the hardest part is a credible small constraint solver, not the API integration.

**Unique wedge:** Verification-aware sequence optimization with a credit budget, not merely heat-aware routing.

**Spike result:** PASS — cached-live profile; baseline proxy 2.2, agent candidate proxy 0.0, improvement 2.2. The approval checkpoint passed; route, appointment, and skills constraints are synthetic.

### 3. DockShift Orchestrator

**One-sentence product definition:** We are building this for distribution-center operations managers to allocate hot dock and yard tasks across shifts while preserving throughput and recovery capacity.

**Why agent:** It chooses which task to move, which zone to investigate more deeply, and how to satisfy staffing/throughput constraints instead of making a manager read a heatmap.

**Why FortyGuard:** Persistent tile-level heat and environmental context in dock/yard zones provide an operational signal that indoor facility averages miss.

**Agent loop:** Task roster → zone heat screen → targeted exceedance/env call → shift allocation → constraint check → approval proposal → metric verification → adapt.

**Demo story:** Three zones and two shifts are shown; the agent moves one heavy task to a cooler window and keeps throughput constraints intact.

**Measured outcome:** Thermal-load proxy per shift, tasks inside threshold windows, throughput preserved, and break-plan changes.

**Required data:** Task durations/intensity, zones, shifts, staffing, throughput constraints, and FortyGuard responses.

**Build estimate:** High for a deterministic spike; real deployment needs warehouse integration and safety review.

**Unique wedge:** A dock/yard workflow that converts heat intelligence into a staffing/throughput action, not a worker notification.

**Spike result:** PASS — cached-live profile; baseline proxy 2.5, agent candidate proxy 0.0, improvement 2.5. The approval checkpoint passed; task, staffing, and throughput constraints are synthetic.

## Ranking, not selection

1. Thermal Sequence Planner — tentative current evidence leader for the strongest temporal agent loop, but dependent on real route/appointment data.
2. Pavement Window Agent — specific and industrial, with a clear FortyGuard-centered temporal workflow; engineering and work-zone data remain unverified.
3. DockShift Orchestrator — specific workflow, but highest dependency risk for real task/staffing/throughput data.

`FINAL_MVP_SELECTED = NO`
