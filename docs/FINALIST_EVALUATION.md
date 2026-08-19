# Finalist evaluation

Scores use the brief's weights: Impact/Relevance 40%, Technical Execution 35%, Innovation 15%, Communication 10%. Scores are judgment calls based on the evidence collected, not outcomes claimed from a production deployment.

## Weighted scores

| Finalist | Impact /40 | Technical /35 | Innovation /15 | Communication /10 | Weighted /10 | Duplication | Build risk | API/data risk | Dependency risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pavement Window Agent | 8.8 | 8.1 | 8.2 | 8.7 | 8.45 | 2 | 2 | 2 | 2 |
| Thermal Sequence Planner | 8.7 | 8.6 | 7.4 | 9.2 | 8.43 | 3 | 2 | 2 | 2 |
| DockShift Orchestrator | 8.2 | 8.2 | 8.0 | 8.3 | 8.18 | 2 | 2 | 3 | 3 |
| Data Center Cooling Readiness | 8.5 | 7.7 | 8.1 | 7.6 | 8.10 | 2 | 3 | 3 | 4 |
| Cooling Center Logistics | 9.0 | 7.2 | 8.0 | 8.0 | 8.12 | 3 | 3 | 3 | 4 |
| Transit Stop Intervention Triage | 7.8 | 7.7 | 7.0 | 8.0 | 7.63 | 3 | 2 | 2 | 3 |

## Evidence and limitations

- The local FortyGuard fixtures show meaningful variation in temperature, exceedance, and persistence across a San Jose portfolio-scale AOI. They establish that duration metrics can separate candidate sites.
- The deterministic spike uses a real cached environmental hourly profile shape and synthetic operational windows. The improvement is a proxy result, not a field outcome.
- Every spike ended at a human approval checkpoint and produced a trace. This demonstrates the control loop, not a safe-to-operate certification.
- Premium endpoints and exact live per-call credit costs were not verified for the account. The finalist designs work with heatmap/env params first.

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

**Spike result:** PASS — baseline proxy 12.4, agent candidate proxy 0.0, improvement 12.4 on a fixture-backed synthetic window scenario.

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

**Spike result:** PASS — baseline proxy 9.1, agent candidate proxy 0.0, improvement 9.1 on a fixture-backed synthetic window scenario.

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

**Spike result:** PASS — baseline proxy 12.5, agent candidate proxy 1.3, improvement 11.2 on a fixture-backed synthetic window scenario.

## Ranking, not selection

1. Pavement Window Agent — current evidence leader because the wedge is specific, industrial, FortyGuard-central, and easy to explain.
2. Thermal Sequence Planner — nearly tied; strongest agentic demonstration and broadest reuse.
3. DockShift Orchestrator — strong specificity with more dependency risk around real task/throughput data.

`FINAL_MVP_SELECTED = NO`
