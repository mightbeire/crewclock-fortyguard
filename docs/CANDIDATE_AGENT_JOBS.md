# Candidate agent jobs

These are exploration candidates generated after the problem and duplication research. None is the selected MVP.

## 1. Thermal Sequence Planner

### NAME
Thermal Sequence Planner

### USER
We are building this for dispatch managers coordinating mobile field-service technicians across several U.S. cities.

### PROBLEM
To solve the recurring problem that feasible job sequences can create unnecessary consecutive high-heat exposure.

### CURRENT WORKFLOW
Dispatchers schedule by appointments, skills, travel time, and broad weather alerts, then reshuffle manually.

### AGENT JOB
The agent autonomously compares candidate job sequences and proposes the lowest thermal-load schedule that preserves hard appointment and skill constraints.

### AGENT LOOP
Observe jobs/constraints → Investigate FortyGuard heatmap and env parameters for candidate sites/windows → Decide sequence and breaks → Act/Recommend a resequencing proposal → Verify proxy exposure and constraint satisfaction → Adapt if a site/window fails.

### WHY NOT A DASHBOARD?
The value is in exploring alternatives and returning a feasible change, not making the dispatcher interpret another layer.

### WHY FORTYGUARD?
Tile-level peak timing, exceedance, persistence, and environmental context distinguish nearby jobs and sustained exposure better than a citywide weather alert.

### TOOLS
`get_heatmap`, `get_environmental_parameters`, `summarize_heat_profile`, `calculate_exposure_metric`, schedule constraint checker.

### ACTION
Recommend a reordered route, earlier/later appointment, crew rotation, or escalation.

### HUMAN APPROVAL
Dispatcher approves any appointment change or dispatch action; safety policy remains human-owned.

### MEASUREMENT
Thermal-load proxy reduction, jobs moved out of exceedance windows, constraints preserved, and FortyGuard calls avoided through caching.

### DEMO MOMENT
Show the same four jobs: naive order is hot-back-to-back; the agent swaps two jobs, keeps all appointments feasible, and shows the proxy drop.

### DUPLICATION RISK
3.

### FEASIBILITY
High with synthetic job constraints and cached U.S. profiles; real route optimization can remain a thin adapter.

## 2. DockShift Orchestrator

### NAME
DockShift Orchestrator

### USER
We are building this for operations managers at distribution centers with hot loading docks and outdoor yards.

### PROBLEM
To solve the recurring problem of assigning heavy dock/yard tasks to shifts without concentrating sustained heat exposure.

### CURRENT WORKFLOW
Managers use fixed labor plans and local judgment to add breaks or move tasks.

### AGENT JOB
The agent autonomously identifies which tasks and dock zones should move to a cooler window or receive added recovery capacity.

### AGENT LOOP
Observe task roster, zones, and staffing → Investigate FortyGuard spatial and temporal profiles → Decide task/shift allocation → Act/Recommend a shift change or break block → Verify throughput constraints and thermal proxy → Adapt when staffing or conditions change.

### WHY NOT A DASHBOARD?
The manager needs a concrete reassignment under labor and throughput constraints; a map alone does not do that work.

### WHY FORTYGUARD?
Persistent tile-level heat in a yard/dock footprint plus humidity/solar context creates a location-specific operational signal.

### TOOLS
Heatmap, env params, profile summary, exposure metric, staffing/throughput checker.

### ACTION
Move heavy tasks, add recovery blocks, select a cool-zone assignment, or escalate staffing.

### HUMAN APPROVAL
Operations manager approves labor changes and any worker-safety instruction.

### MEASUREMENT
Thermal-load proxy per shift, tasks in threshold windows, throughput preserved, and break-plan compliance.

### DEMO MOMENT
The agent sees three dock zones and two shifts, moves one heavy task to the cooler window, and explains the measured proxy improvement.

### DUPLICATION RISK
2.

### FEASIBILITY
High for a deterministic MVP with user-provided task data and FortyGuard fixtures.

## 3. Pavement Window Agent

### NAME
Pavement Window Agent

### USER
We are building this for municipal road-maintenance supervisors planning paving, striping, sealant, and inspection crews.

### PROBLEM
To solve the recurring decision of which work window minimizes heat-related worker and asset-quality risk while preserving traffic and crew constraints.

### CURRENT WORKFLOW
Supervisors combine traffic constraints, crew availability, broad forecasts, and engineering judgment.

### AGENT JOB
The agent autonomously screens candidate work windows, investigates the location's sustained heat profile, and returns a human-approved maintenance-window recommendation.

### AGENT LOOP
Observe work orders and constraints → Investigate FortyGuard `tcm`, peak timing, exceedance, persistence, and env context → Decide the best window → Act/Recommend a window and control plan → Verify thermal proxy and constraints → Adapt when the window or threshold changes.

### WHY NOT A DASHBOARD?
The agent converts a spatial-temporal layer into a concrete window choice and shows why alternatives lose.

### WHY FORTYGUARD?
Spatially varying pavement/work-zone heat and persistence are central; generic weather has insufficient local resolution for the comparison.

### TOOLS
Heatmap analytics, env params, profile summary, exposure/quality proxy, constraint checker, approval queue.

### ACTION
Recommend shift earlier/later, split work, add recovery controls, or escalate to an engineer.

### HUMAN APPROVAL
Supervisor/engineer approves work timing, material, and safety controls.

### MEASUREMENT
Thermal-load proxy avoided, continuous exceedance hours reduced, traffic/crew constraints satisfied, and number of rework-risk windows flagged.

### DEMO MOMENT
Two candidate windows for the same road segment: the agent selects the one with lower persistence and produces an auditable before/after metric.

### DUPLICATION RISK
2.

### FEASIBILITY
High for a thin decision spike; production engineering models remain explicitly out of scope.

## 4. Cooling Center Logistics Agent

### NAME
Cooling Center Logistics Agent

### USER
We are building this for city emergency-operations logistics planners coordinating cooling centers and water distribution during heat events.

### PROBLEM
To solve the recurring problem of prioritizing limited cooling resources as heat burden shifts across neighborhoods.

### CURRENT WORKFLOW
Planners combine alerts, facilities, population data, and manual coordination.

### AGENT JOB
The agent autonomously ranks where to stage supplies and which cooling center needs an intervention next.

### AGENT LOOP
Observe facilities, inventory, and event status → Investigate FortyGuard heat persistence and environmental parameters → Decide priority → Act/Recommend a supply/staffing move → Verify coverage and inventory constraints → Adapt as the event evolves.

### WHY NOT A DASHBOARD?
Resource allocation requires repeatedly choosing among sites under inventory and staffing constraints.

### WHY FORTYGUARD?
Persistent hyperlocal heat can complement citywide alerts and create a common operational picture.

### TOOLS
Heatmap, env params, facility/inventory data, coverage calculator, approval queue.

### ACTION
Stage water, add a cooling station, move staff, or escalate an underserved site.

### HUMAN APPROVAL
Emergency manager approves public-facing or resource-moving actions.

### MEASUREMENT
High-persistence population/sites covered, time to intervention, inventory constraint violations, and unnecessary API calls.

### DEMO MOMENT
One supply truck and three candidate sites: the agent moves it to the site with the highest sustained heat and explains the choice.

### DUPLICATION RISK
3.

### FEASIBILITY
Medium; requires realistic facility/population fixtures and careful public-health framing.

## 5. Data Center Cooling Readiness Agent

### NAME
Data Center Cooling Readiness Agent

### USER
We are building this for facilities operations leads managing cooling readiness across a small U.S. data-center portfolio.

### PROBLEM
To solve the recurring problem of prioritizing inspections and readiness actions before outdoor heat drives cooling demand.

### CURRENT WORKFLOW
Facilities teams review forecasts, maintenance plans, and telemetry in separate systems.

### AGENT JOB
The agent autonomously ranks sites for readiness checks and proposes a cooling-preparation plan.

### AGENT LOOP
Observe site telemetry/maintenance windows → Investigate FortyGuard heat, humidity, and solar profiles → Decide priority → Act/Recommend inspection or preparation → Verify constraints and proxy demand → Adapt with updated observations.

### WHY NOT A DASHBOARD?
The agent focuses limited operations attention on the next site and action, rather than exposing more charts.

### WHY FORTYGUARD?
The combination of spatial heat and environmental/solar parameters helps distinguish sites and timing relevant to cooling operations.

### TOOLS
Heatmap, env params, usage checker, site telemetry adapter, readiness score.

### ACTION
Prioritize inspection, prepare cooling capacity, shift noncritical work, or request an approved setpoint review.

### HUMAN APPROVAL
Facilities lead approves operational changes; no autonomous control of critical infrastructure.

### MEASUREMENT
High-heat site checks completed before peak, proxy cooling burden avoided, and no availability constraints violated.

### DEMO MOMENT
Three sites compete for one inspection slot; the agent picks the persistent hot site and cites the exact evidence.

### DUPLICATION RISK
2.

### FEASIBILITY
Medium; credible production use needs telemetry, but a thin spike can use site profiles and readiness constraints.

## 6. Transit Stop Intervention Triage

### NAME
Transit Stop Intervention Triage

### USER
We are building this for transit amenities managers choosing which bus stops need shade, water, or schedule interventions first.

### PROBLEM
To solve the recurring problem of ranking stops whose heat exposure is sustained during actual rider-use windows.

### CURRENT WORKFLOW
Teams use ridership, complaints, equity, and broad heat maps to plan capital work.

### AGENT JOB
The agent autonomously investigates candidate stops, compares persistent heat during service windows, and proposes a prioritized intervention list.

### AGENT LOOP
Observe stop inventory/ridership → Investigate FortyGuard heatmap and peak/persistence → Decide rank and intervention type → Act/Recommend a shortlist → Verify budget and coverage constraints → Adapt when new stops or windows are added.

### WHY NOT A DASHBOARD?
The agent must make a budget-constrained recommendation and explain the trade-off.

### WHY FORTYGUARD?
Tile-level timing and duration add operational specificity beyond a static hotspot layer.

### TOOLS
Heatmap, env params, stop data, budget optimizer, ranking evaluator.

### ACTION
Prioritize a stop, request shade/water, or escalate for design review.

### HUMAN APPROVAL
Public-works manager approves capital and equity decisions.

### MEASUREMENT
Persistent hot-stop exposure covered per dollar, ranking stability, and number of interventions moved into meaningful service windows.

### DEMO MOMENT
With one intervention budget, the agent picks a less obvious stop because its heat persists during the highest-ridership window.

### DUPLICATION RISK
3.

### FEASIBILITY
High for a ranking spike; weaker differentiation than the industrial finalists.

## 7. Event Cooling Station Planner

### NAME
Event Cooling Station Planner

### USER
We are building this for outdoor event operations directors planning setup and cooling-station placement.

### PROBLEM
To solve the recurring problem of placing limited cooling resources where heat persists during setup and peak attendance.

### CURRENT WORKFLOW
Directors use a venue map, past experience, and generic forecast alerts.

### AGENT JOB
The agent autonomously compares candidate station locations and setup windows.

### AGENT LOOP
Observe venue, crowd, and staffing constraints → Investigate FortyGuard heat and environmental context → Decide placements/windows → Act/Recommend a plan → Verify coverage and access → Adapt with event changes.

### WHY NOT A DASHBOARD?
It must select a placement and timing under a finite resource budget.

### WHY FORTYGUARD?
Hyperlocal heat persistence across the event footprint is central to placement.

### TOOLS
Heatmap, env params, venue geometry, coverage calculator, approval queue.

### ACTION
Place stations, move setup, or increase cooling staff.

### HUMAN APPROVAL
Event director approves venue and safety changes.

### MEASUREMENT
Hot-area coverage, high-persistence hours covered, setup exposure proxy, and resource utilization.

### DEMO MOMENT
The agent moves one station from the visually central location to the persistent hotspot.

### DUPLICATION RISK
3.

### FEASIBILITY
High for a fixture-backed spike.

## 8. Utility Outage Crew Stager

### NAME
Utility Outage Crew Stager

### USER
We are building this for utility operations coordinators staging crews for heat-day inspections and repairs.

### PROBLEM
To solve the recurring problem of assigning limited crews to work zones without concentrating hot, continuous exposure.

### CURRENT WORKFLOW
Coordinators prioritize outage severity, skill, distance, and broad weather.

### AGENT JOB
The agent autonomously stages crews and recommends a sequence that reduces thermal burden without hiding priority outages.

### AGENT LOOP
Observe outage/crew state → Investigate FortyGuard zones and windows → Decide staging → Act/Recommend assignment → Verify service and safety constraints → Adapt as outages change.

### WHY NOT A DASHBOARD?
Staging is a constrained allocation problem with changing state.

### WHY FORTYGUARD?
Persistent microclimate differences can change which feasible zone should be served first.

### TOOLS
Heatmap, env params, outage/crew data, assignment optimizer, approval queue.

### ACTION
Stage, resequence, rotate, or escalate a crew assignment.

### HUMAN APPROVAL
Utility supervisor approves dispatch changes.

### MEASUREMENT
Exposure proxy avoided, outage priority preserved, service time, and API calls per decision.

### DEMO MOMENT
The agent preserves the critical outage while swapping the order of two noncritical tasks to reduce heat.

### DUPLICATION RISK
3.

### FEASIBILITY
Medium-high; requires realistic outage fixtures.

## 9. Airport Ramp Rotation Planner

### NAME
Airport Ramp Rotation Planner

### USER
We are building this for airport ground-operations managers coordinating outdoor ramp tasks.

### PROBLEM
To solve the recurring problem of sequencing ramp tasks and rotations during persistent high-heat windows.

### CURRENT WORKFLOW
Managers use flight schedules, staffing, PPE, and safety guidance.

### AGENT JOB
The agent autonomously proposes a task rotation and recovery plan that keeps flights and staffing constraints feasible.

### AGENT LOOP
Observe flight/task state → Investigate FortyGuard ramp heat and environmental context → Decide rotation → Act/Recommend → Verify constraints → Adapt.

### WHY NOT A DASHBOARD?
Rotation requires action under a fast-changing schedule.

### WHY FORTYGUARD?
Spatially varying ramp heat and solar context can change the risk between nearby stands.

### TOOLS
Heatmap, env params, flight/task data, rotation checker.

### ACTION
Rotate teams, move noncritical work, or escalate staffing.

### HUMAN APPROVAL
Ramp safety/operations lead approves all changes.

### MEASUREMENT
Exposure proxy, flight constraints preserved, and recovery coverage.

### DEMO MOMENT
Two adjacent stands have different heat profiles; the agent rotates the crew without moving a flight.

### DUPLICATION RISK
2.

### FEASIBILITY
Medium; operational data and safety review are dependencies.

## 10. Commercial Property Retrofit Triage

### NAME
Commercial Property Retrofit Triage

### USER
We are building this for portfolio-operations leads prioritizing heat-resilience retrofits across U.S. properties.

### PROBLEM
To solve the recurring problem of choosing which property and intervention deserves limited retrofit budget first.

### CURRENT WORKFLOW
Teams review property data, heat maps, building assessments, and capex plans manually.

### AGENT JOB
The agent autonomously investigates a shortlist, selects the next evidence-gathering tool, and ranks interventions.

### AGENT LOOP
Observe portfolio and budget → Investigate heatmap, env params, and optional segmentation → Decide priority/intervention → Act/Recommend capex shortlist → Verify budget and evidence → Adapt.

### WHY NOT A DASHBOARD?
The agent chooses what to investigate and which action best fits the budget.

### WHY FORTYGUARD?
Hyperlocal heat, duration, and optional scene context support property comparison.

### TOOLS
Heatmap, env params, satellite/street view if enabled, portfolio optimizer.

### ACTION
Prioritize a property and retrofit or request deeper assessment.

### HUMAN APPROVAL
Asset manager/engineer approves capex.

### MEASUREMENT
Persistent hot exposure addressed per dollar and evidence/API cost per property.

### DEMO MOMENT
The agent spends expensive enrichment only on the top two properties after a cheap heatmap screen.

### DUPLICATION RISK
3.

### FEASIBILITY
High because the vendor already contains reusable parcel/real-estate fixtures; differentiation is weaker.

## 11. Concrete Pour Window Agent

### NAME
Concrete Pour Window Agent

### USER
We are building this for concrete project managers and quality engineers scheduling outdoor pours in U.S. cities.

### PROBLEM
To solve the recurring problem of choosing a pour window that limits hot-weather curing and worker exposure risk.

### CURRENT WORKFLOW
Teams combine mix design, crew availability, traffic, and broad weather forecasts.

### AGENT JOB
The agent autonomously screens candidate windows and flags when an engineer should review a hot-weather control plan.

### AGENT LOOP
Observe pour constraints → Investigate FortyGuard heat peak/exceedance/persistence → Decide best window → Act/Recommend a window and controls → Verify constraints and proxy → Adapt when conditions change.

### WHY NOT A DASHBOARD?
The agent turns a thermal profile into a selected work window plus a review trigger.

### WHY FORTYGUARD?
Site-specific persistent heat and timing are directly relevant to the candidate comparison.

### TOOLS
Heatmap analytics, env params, work-window calculator, approval queue.

### ACTION
Recommend a pour window or escalate to quality engineering.

### HUMAN APPROVAL
Engineer owns material and quality decisions.

### MEASUREMENT
Hot-window exposure proxy avoided, review triggers caught, and constraints preserved.

### DEMO MOMENT
The agent rejects the attractive midday slot and selects a cooler window with a concise evidence trail.

### DUPLICATION RISK
2.

### FEASIBILITY
High for a scheduling spike; avoid claiming structural-quality prediction.

## 12. Manufacturing Yard Task Allocator

### NAME
Manufacturing Yard Task Allocator

### USER
We are building this for plant operations managers assigning outdoor yard, loading, and maintenance tasks.

### PROBLEM
To solve the recurring problem of sequencing outdoor tasks across hot yard zones without losing production throughput.

### CURRENT WORKFLOW
Managers use production priorities, equipment, staffing, and broad weather alerts.

### AGENT JOB
The agent autonomously allocates feasible tasks to cooler windows and proposes recovery blocks.

### AGENT LOOP
Observe production/task state → Investigate FortyGuard spatial heat profiles → Decide allocation → Act/Recommend → Verify throughput and safety constraints → Adapt.

### WHY NOT A DASHBOARD?
It must solve the allocation, not expose another heat layer.

### WHY FORTYGUARD?
Yard-scale differences and sustained exceedance can change a task's recommended window.

### TOOLS
Heatmap, env params, task graph, constraint checker.

### ACTION
Reorder tasks, assign recovery, or escalate staffing.

### HUMAN APPROVAL
Plant supervisor approves production changes.

### MEASUREMENT
Exposure proxy, throughput preserved, and task changes accepted.

### DEMO MOMENT
The agent changes only the heat-sensitive tasks while keeping a critical production task fixed.

### DUPLICATION RISK
2.

### FEASIBILITY
Medium-high; fixture data is straightforward.

## 13. Delivery Hot-Zone Router

### NAME
Delivery Hot-Zone Router

### USER
We are building this for last-mile delivery operations managers dispatching drivers and couriers.

### PROBLEM
To solve the recurring problem of choosing a route/order that limits heat exposure while meeting delivery promises.

### CURRENT WORKFLOW
Routing optimizes distance/time; heat is handled through generic alerts.

### AGENT JOB
The agent autonomously compares route/order alternatives and proposes a heat-aware dispatch plan.

### AGENT LOOP
Observe stops and promises → Investigate FortyGuard corridor heat → Decide route/order → Act/Recommend → Verify ETA and thermal proxy → Adapt.

### WHY NOT A DASHBOARD?
Route choice is an action under deadlines.

### WHY FORTYGUARD?
Hyperlocal heat corridors and peak timing can alter exposure beyond ambient city forecasts.

### TOOLS
Heatmap, route engine, env params, exposure metric.

### ACTION
Reorder stops or recommend a cooler corridor.

### HUMAN APPROVAL
Dispatcher approves route changes.

### MEASUREMENT
Proxy exposure, ETA adherence, and route changes.

### DEMO MOMENT
The agent chooses a slightly longer route that avoids the persistent hotspot.

### DUPLICATION RISK
4.

### FEASIBILITY
High technically, but too obvious for the primary shortlist.

## 14. Harvest Window Assistant

### NAME
Harvest Window Assistant

### USER
We are building this for agricultural operations managers planning harvest crews and equipment windows.

### PROBLEM
To solve the recurring problem of choosing harvest windows that limit heat exposure and preserve labor/equipment constraints.

### CURRENT WORKFLOW
Managers combine crop maturity, labor, equipment, and regional forecasts.

### AGENT JOB
The agent autonomously chooses among feasible field windows and proposes rotation.

### AGENT LOOP
Observe crop/task state → Investigate FortyGuard field heat → Decide window → Act/Recommend → Verify constraints → Adapt.

### WHY NOT A DASHBOARD?
The agent selects the next field/window rather than displaying a map.

### WHY FORTYGUARD?
Field-scale heat differences and persistence could inform worker/equipment timing.

### TOOLS
Heatmap, env params, field/task data, scheduler.

### ACTION
Reschedule harvest or add recovery controls.

### HUMAN APPROVAL
Farm operations manager approves.

### MEASUREMENT
Exposure proxy and harvest completion with fewer hot-window hours.

### DEMO MOMENT
The agent shifts a field block to the morning and preserves equipment constraints.

### DUPLICATION RISK
3.

### FEASIBILITY
Low-medium because geographic/data assumptions are less certain for this account.

## 15. Heat-Aware Inspection Queue

### NAME
Heat-Aware Inspection Queue

### USER
We are building this for facilities managers triaging recurring outdoor asset inspections.

### PROBLEM
To solve the recurring problem of deciding which assets to inspect first when heat may increase worker burden or asset risk.

### CURRENT WORKFLOW
Teams use due dates, failure history, location, and manual route planning.

### AGENT JOB
The agent autonomously investigates heat burden and reprioritizes the inspection queue while protecting due-date constraints.

### AGENT LOOP
Observe asset queue → Investigate FortyGuard heat/persistence → Decide priority → Act/Recommend → Verify due dates and exposure proxy → Adapt.

### WHY NOT A DASHBOARD?
The agent produces a queue and next action, not just a risk map.

### WHY FORTYGUARD?
Spatial and temporal heat intelligence adds a measurable operational dimension to asset triage.

### TOOLS
Heatmap, status, env params, queue optimizer, exposure metric.

### ACTION
Reorder inspections, bundle nearby work, or escalate an overdue asset.

### HUMAN APPROVAL
Facilities manager approves changes to due dates or high-consequence inspections.

### MEASUREMENT
Hot exposure proxy avoided, overdue assets, travel/work efficiency, and verified queue improvement.

### DEMO MOMENT
The agent moves one non-urgent inspection out of a persistent hot window while protecting a critical due date.

### DUPLICATION RISK
2.

### FEASIBILITY
High; generic enough to reuse, but needs a sharper vertical wedge before selection.
