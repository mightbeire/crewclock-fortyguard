# Second-wave operational research and concepts

Date: August 19, 2026. This wave adds 12 workflows that were not in the original 15-candidate list. The strongest new signal is the combination of live heat timing/duration with physical-context segmentation: satellite can return labels such as `building`, `road, route`, `sidewalk, pavement`, `tree`, `grass`, `rail`, `truck`, and `car`, but it can also return `others=100%`. The agent must treat unusable segmentation as uncertainty and stop or request review.

## Live evidence exploited

- Phoenix: 100 m heatmap at the tested site reached 40.15°C maximum; a 99-cell, seven-day `time_of_measure` map had peak-hour values 04 or 16 UTC, while persistence above 38°C was uniformly 8 hours.
- Los Angeles airport/rail context: 100 m heatmap maximum 24.51°C at the tested date; a 108-cell, seven-day `time_of_measure` map was uniformly 15 UTC and persistence above 23°C was uniformly 7 hours. Satellite detected `rail` at 1.06% of the image, alongside 86.79% building.
- Atlanta: the tested tile reached 36.3°C maximum and the environmental profile had 97.6% peak relative humidity. The live `heat_index_celsius` field produced values up to 77.9, which is not credible as Celsius; the agent must not use that field without unit validation. Apparent temperature and wet-bulb values are safer inputs in this run.

## 12 new agentic concepts

### 1. RailHeat Patrol Sequencer — satellite-assisted

- **User / problem:** We are building this for railroad maintenance planners to decide which track segments need a hot-weather patrol and which patrol window to use before heat-related defects become service restrictions.
- **Current workflow:** Planners combine heat rules, track inventory, inspection history, and crew availability manually; extreme-heat rules already trigger additional inspections or speed controls. Sources: [Amtrak CWR procedures](https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/corporate/engineering-practices/engineering-standards/procedures-installation-adjustment-maintenance-inspection-cwr-49-cfr-213-118.pdf), [FRA ATIP](https://railroads.fra.dot.gov/railroad-safety/partnerships-programs/automated-track-inspection-program-atip).
- **Agent loop:** ingest track/crossing work items → call heat timing/persistence → filter by rail/ground context → rank patrols → check train-window and crew constraints → propose a patrol plan → verify coverage and residual hot hours.
- **FortyGuard dependency:** heatmap timing and persistence describe when the track corridor is thermally stressed; satellite can confirm that the selected pixel contains rail-like context rather than an arbitrary building.
- **Action / approval:** create a draft hot-weather patrol queue or recommend a speed-review handoff; rail control/engineering approves before dispatch.
- **Measurement / demo:** high-priority segments covered before their peak; hours of unpatrolled exceedance; 20-second moment is the agent rejecting a false “rail” candidate when satellite returns `others=100%`, then choosing the segment with live rail context and a defensible patrol hour.
- **Risk:** duplication 2/5; feasibility medium; data dependency 3/5 because actual track geometry and railroad thresholds are not public everywhere.

### 2. Surface-conditioned Road Repair Queue — satellite-assisted

- **User / problem:** We are building this for municipal street-maintenance supervisors to prioritize pavement work orders that are both operationally urgent and likely to be executed in the least damaging heat window.
- **Current workflow:** 311 requests are triaged by age, severity, district, and crew availability; heat and surface composition are rarely part of the same queue. A credible public input shape exists in [MyLA311 service requests](https://data.lacity.org/City-Infrastructure-Service-Requests/MyLA311-Service-Request-Data-2024/b7dx-7gc3) and Portland’s [PBOT pothole layer](https://www.portlandmaps.com/arcgis/rest/services/Public/PBOT_Maintenance/MapServer/layers).
- **Agent loop:** deduplicate/geocode work orders → screen heatmap → inspect satellite surface composition → choose the next repair batch and window → verify urgency/crew constraints → approval proposal.
- **FortyGuard dependency:** heatmap provides the location/date signal; satellite distinguishes a pavement/road candidate from a mostly building/vegetation tile and supplies an auditable reason for prioritization.
- **Action / approval:** draft a repair sequence and work window; street operations approves changes to the work plan.
- **Measurement / demo:** weighted backlog age reduced without violating severity/SLA; thermal-load proxy for selected work windows; 20-second moment is a 311 queue becoming a heat-and-surface-aware batch with evidence chips.
- **Risk:** duplication 2/5; feasibility high; data dependency 2/5 because public 311/work-order schemas are available, though live FortyGuard coverage varies by city.

### 3. Utility Vegetation Clearance Release Agent — satellite-assisted

- **User / problem:** We are building this for electric-utility vegetation-management planners to release the safest, highest-consequence tree-clearance work packages first during hot periods.
- **Current workflow:** work packages are scheduled by circuit risk, cycle date, contractors, and wildfire rules; heat exposure is an additional manual safety concern. Utility vegetation data standards document tree/project identifiers and spatial work packages ([California Energy Safety GIS standard](https://energysafety.ca.gov/wp-content/uploads/energy-safety-gis-data-reporting-standard_version2.1_09072021_final.pdf)); an open vegetation schedule example is [Hydro-Québec’s planning dataset](https://donnees.hydroquebec.com/explore/dataset/calendrier-travaux-degagement-distribution-json/).
- **Agent loop:** ingest circuit/package priority → inspect tree/ground/building context → call local heat and wet-bulb profile → allocate crews and release order → require approval → verify completed package and deferred exposure.
- **FortyGuard dependency:** physical vegetation context and hyperlocal heat timing tell the agent which outdoor clearance tasks need a cooler window and which can wait.
- **Action / approval:** draft crew-release order, not an autonomous line-clearance instruction; utility operations approves.
- **Measurement / demo:** high-priority packages released on time, worker heat proxy reduced, circuit-risk SLA preserved; 20-second moment is the agent refusing a package with missing/ambiguous satellite context.
- **Risk:** duplication 3/5; feasibility medium; data dependency 4/5 because U.S. utility work packages are often private.

### 4. Airport Apron Crew Load Balancer — satellite-assisted

- **User / problem:** We are building this for airport ground-operations planners to assign exposed ramp, baggage, and equipment tasks across apron zones and shifts.
- **Current workflow:** ramp plans follow flights, gates, equipment, labor, and safety rules; microclimate evidence is rarely attached to the assignment. Public airport context is available through [FAA Aviation Facilities](https://catalog.data.gov/dataset/aviation-facilities-9c677) and FAA airport diagram releases.
- **Agent loop:** ingest apron/task roster → call heat peak/persistence → inspect building/road/vehicle context → rebalance tasks → check aircraft turnaround constraints → propose approval → verify throughput and residual heat burden.
- **FortyGuard dependency:** it adds spatial/time heat evidence to the existing flight/ground plan; satellite can distinguish a paved movement area from a terminal or vegetated buffer.
- **Action / approval:** draft task reassignment or recovery rotation; airport operations approves.
- **Measurement / demo:** turnarounds preserved, high-heat task-hours reduced, assignments remain skill-valid; 20-second moment is a hot apron task moved while a flight deadline stays fixed.
- **Risk:** duplication 3/5; feasibility medium-low; data dependency 4/5 because detailed apron and labor data are proprietary.

### 5. Telecom Site Access Window Agent — satellite-assisted

- **User / problem:** We are building this for telecom field-operations coordinators to schedule tower and cabinet work when heat exposure and site surface context are manageable.
- **Current workflow:** work orders are prioritized by outage/SLA, technician certification, access permits, and travel; the [ITU preventive-maintenance recommendation](https://www.itu.int/epublications/publication/itu-t-m-3370-2025-03-telecommunication-preventive-maintenance-task-overview/en) explicitly models work-order prioritization, scheduling, dispatch, and verification.
- **Agent loop:** prioritize outage/SLA → check site heat and humidity → inspect building/ground/tree context → choose window/crew → approval → verify closure and missed-SLA risk.
- **FortyGuard dependency:** a tower/rooftop work site can have a materially different heat window from the nearest city forecast; satellite adds physical access context.
- **Action / approval:** draft a permitted access window and crew assignment.
- **Measurement / demo:** outage SLA preserved, high-heat task-hours reduced, API calls per approved work order.
- **Risk:** duplication 3/5; feasibility medium; data dependency 3/5.

### 6. Solar O&M Access-and-Cleaning Agent — satellite-assisted

- **User / problem:** We are building this for a solar O&M portfolio manager to decide which maintenance blocks should be cleaned, inspected, or deferred based on heat, access surface, and crew capacity.
- **Current workflow:** operators combine plant telemetry, cleaning intervals, weather, and travel manually; optimization research shows site-specific cleaning schedules matter ([PV cleaning scheduling study](https://doi.org/10.1016/j.renene.2025.122971)).
- **Agent loop:** rank soiling/underperformance tasks → call heat and solar context → inspect ground/building/road context → allocate water/crew → approval → verify expected production and time-cost proxy.
- **FortyGuard dependency:** hyperlocal heat/solar context can change safe access windows and water/cleaning priority; satellite is useful for access context but does not prove that a segment is a panel.
- **Action / approval:** draft a cleaning/inspection queue.
- **Measurement / demo:** expected production loss avoided per crew-hour and water unit; 20-second moment is the agent declining to infer “solar panel” from a generic building label.
- **Risk:** duplication 3/5; feasibility medium; data dependency 4/5.

### 7. Waste Route Heat-Exposure Balancer

- **User / problem:** We are building this for municipal sanitation fleet supervisors to sequence outdoor collection tasks and recovery breaks without missing route service commitments.
- **Current workflow:** routes are planned by vehicle, zone, tonnage, and pickup windows; heat is handled through blanket alerts or supervisor judgment. OSHA identifies refuse collection as an outdoor physical-work exposure category ([OSHA heat resources](https://www.osha.gov/heat-exposure)).
- **Agent loop:** ingest route/stop/vehicle roster → call heat windows for stop clusters → resequence eligible stops → check disposal and service windows → approval → verify route completion and heat proxy.
- **FortyGuard dependency:** stop-level spatial/time differences matter more than a citywide alert for exposed collection work.
- **Action / approval:** draft route/recovery change.
- **Measurement / demo:** missed pickups, overtime, and thermal-load proxy.
- **Risk:** duplication 4/5; feasibility medium; data dependency 3/5. Reject unless a narrower fleet/yard wedge appears.

### 8. Fleet Yard Charging-and-Loading Slot Agent

- **User / problem:** We are building this for fleet-yard managers to place charging, loading, inspection, and fueling tasks into lower-heat surface/time windows.
- **Current workflow:** yard managers juggle charger availability, vehicle departures, dock conflicts, and inspections; heat is not tied to the yard slot plan.
- **Agent loop:** read departures and asset constraints → screen yard zones → use satellite to classify pavement/building/vehicle context → allocate slots → approval → verify departure coverage and heat proxy.
- **FortyGuard dependency:** yard microclimate and physical surfaces affect exposed tasks and equipment dwell.
- **Action / approval:** draft slot allocation.
- **Measurement / demo:** on-time departures, charger/dock utilization, heat burden.
- **Risk:** duplication 4/5; feasibility medium; data dependency 3/5. It is close to DockShift and is rejected from the final five.

### 9. Cold-Chain Yard Dwell Exception Agent

- **User / problem:** We are building this for cold-chain terminal managers to decide which trailer/door exception needs intervention first when outdoor dwell and heat threaten cargo.
- **Current workflow:** sensor platforms already monitor temperature, location, and door state; the missing decision is which physical yard bottleneck to clear first. Existing products already market this capability ([Copeland cargo monitoring](https://www.copeland.com/en-us/products-solutions/controls-solutions/in-transit-solutions), [TrueCold](https://www.truecold.io/industries/logistics)).
- **Agent loop:** detect dwell/temperature exception → add yard heat and surface context → rank door/trailer intervention → approval → verify release/temperature trajectory.
- **FortyGuard dependency:** ambient hyperlocal heat explains external dwell risk but cannot replace cargo sensors.
- **Action / approval:** draft door/trailer escalation.
- **Measurement / demo:** dwell time, excursion risk, spoilage claims.
- **Risk:** duplication 4/5; feasibility medium-low; data dependency 4/5. Reject as too close to existing monitoring platforms.

### 10. Commercial Roof Inspection Queue

- **User / problem:** We are building this for commercial-property maintenance managers to decide which roof/roof-edge inspections deserve the next crew visit after a hot spell.
- **Current workflow:** inspections are scheduled by age, leaks, warranty, and tenant complaints; heat/surface context is not part of prioritization.
- **Agent loop:** aggregate work orders → check heat persistence and building context → rank inspection urgency → propose crew/window → approval → verify closure and deferred-risk list.
- **FortyGuard dependency:** persistent heat can be a defensible screening signal, while satellite confirms building/ground context; it is not a structural-damage diagnosis.
- **Action / approval:** draft inspection queue.
- **Measurement / demo:** overdue inspections closed, travel hours, risk-weighted backlog.
- **Risk:** duplication 3/5; feasibility high; data dependency 3/5. Public [NYC AMPS work orders](https://catalog.data.gov/dataset/asset-management-parks-system-amps-work-orders) show the kind of work-order schema available, but a commercial portfolio is not public.

### 11. Industrial Yard Surface Intervention Agent — satellite-assisted

- **User / problem:** We are building this for industrial-yard managers to decide whether to move a task, add shade/air movement, or schedule a surface intervention in the hottest yard zone.
- **Current workflow:** supervisors know where trucks, containers, and crews queue but rely on local observation rather than a repeatable evidence trail.
- **Agent loop:** inventory task/zone/throughput constraints → call heat and environmental context → inspect road/building/truck/tree mix → compare relocation versus intervention → approval → verify throughput and heat proxy.
- **FortyGuard dependency:** it couples hyperlocal thermal timing to physical yard composition; satellite is not decorative because it determines whether a proposed control addresses pavement, building, or vegetation context.
- **Action / approval:** draft task relocation or low-capex intervention request.
- **Measurement / demo:** throughput preserved, high-heat task-hours reduced, cost per avoided proxy degree-hour.
- **Risk:** duplication 3/5; feasibility medium; data dependency 3/5.

### 12. Heat-Conditioned Property Underwriting Evidence Agent — satellite-assisted

- **User / problem:** We are building this for commercial-property underwriters to request evidence and rank site reviews where heat exposure and physical surface context create operational or financial exposure.
- **Current workflow:** underwriting teams combine property schedules, catastrophe models, photos, engineering reports, and manual triage; the handbook itself names parametric heat-risk scoring as an Industrial & Enterprise example.
- **Agent loop:** screen a property portfolio → call heat/temporal exposure → inspect surface context → identify missing evidence → rank human review → approval → produce source-cited evidence packet.
- **FortyGuard dependency:** the combination of hyperlocal thermal history and physical surface labels is more specific than a generic weather score.
- **Action / approval:** draft evidence requests and review priority, never bind coverage automatically.
- **Measurement / demo:** review time per property, evidence completeness, calibration against claims/engineering labels.
- **Risk:** duplication 3/5; feasibility medium; data dependency 4/5. Keep as a research branch, not a finalist, because claims and underwriting integration are unavailable.

## Early elimination signal

The strongest new workflows are RailHeat Patrol Sequencer and Surface-conditioned Road Repair Queue. They have distinct operational actions, public input structures, and a clear reason to combine FortyGuard heat timing with physical-context evidence. The original Thermal Sequence Planner remains viable but must now beat these challengers on traceability and input realism. Generic alerts, route optimization, cold-chain monitoring, and undifferentiated scheduling are downgraded because public products already cover them ([Perry Weather work/rest cycles](https://perryweather.com/features/heat-stress-and-wbgt-monitoring/work-rest-cycles/), [field-service scheduling](https://www.ibm.com/products/maximo/field-service-management), [warehouse heat playbooks](https://www.mangoapps.com/templates/heat-illness-prevention-playbook)).
