# Problem research

The strongest opportunities are recurring operational decisions where a heat layer changes what happens next. Health guidance is treated as a constraint and source of workflow evidence, not as a claim that the prototype can diagnose or guarantee safety.

## 1. Field-service and utility maintenance sequencing

- Industry: field service, utilities, facilities.
- Specific user: dispatch managers coordinating mobile technicians across several U.S. cities.
- Current workflow: schedule by appointment windows, travel time, skills, and ordinary weather alerts; supervisors manually reshuffle when heat becomes severe.
- Pain: a route can be feasible yet create avoidable consecutive hot-site exposure.
- Frequency/consequences: daily during hot periods; fatigue, missed appointments, breaks, and injury risk.
- Missing information: hyperlocal differences between work sites, peak timing, and sustained threshold duration.
- Why temperature intelligence matters: FortyGuard can compare candidate locations and time windows at tile scale, then investigate exceedance/persistence rather than relying on one citywide temperature.
- Action: recommend resequencing, earlier/later windows, crew rotation, or human escalation.
- Material FortyGuard fit: high, if the dispatch tool uses actual tile/time outputs and verifies a lower proxy metric.

Evidence: [NIOSH workplace recommendations](https://www.cdc.gov/niosh/heat-stress/recommendations/index.html), [OSHA planning](https://www.osha.gov/heat-exposure/planning).

## 2. Warehouse dock and yard shift planning

- Industry: warehousing and logistics.
- Specific user: operations managers at partially climate-controlled distribution centers.
- Current workflow: fixed labor shifts and dock assignments; local supervisors add breaks when conditions feel hot.
- Pain: loading docks, yards, and high-throughput tasks combine physical work with heat and humidity; one generic alert does not say which work should move.
- Frequency/consequences: every shift in hot season; throughput loss, fatigue, errors, and heat illness risk.
- Missing information: which dock/yard zone is hottest, when the peak persists, and which tasks can move.
- Why temperature intelligence matters: tile-level exceedance/persistence and env parameters can rank zones and windows.
- Action: move heavy outdoor tasks, add recovery blocks, prioritize a cool-zone assignment, or escalate a staffing change.
- Material FortyGuard fit: medium-high; operational task data must be supplied by the warehouse.

Evidence: [OSHA warehousing hazards](https://www.osha.gov/warehousing/hazards-solutions), [OSHA Water Rest Shade](https://www.osha.gov/heat-exposure/water-rest-shade).

## 3. Road and pavement maintenance windows

- Industry: transportation infrastructure.
- Specific user: a municipal road-maintenance supervisor planning paving, striping, sealant, or inspection crews.
- Current workflow: choose work windows around traffic, crew availability, and broad weather forecasts; engineering judgment handles heat effects.
- Pain: hot pavement changes material behavior and creates worker exposure; a daily air-temperature forecast misses spatial surface differences and persistence.
- Frequency/consequences: repeated across maintenance seasons; premature defects, rework, delays, and worker risk.
- Missing information: location-specific heat profile, duration above a threshold, and a defensible alternative window.
- Why temperature intelligence matters: heatmap tiles, peak timing, exceedance, and persistence directly describe the thermal window around the work zone.
- Action: choose a work window, change crew/rest pattern, or escalate a material/engineering review.
- Material FortyGuard fit: high for screening and scheduling, while engineering acceptance remains human-approved.

Evidence: [FHWA roadway resilience](https://highways.fhwa.dot.gov/federal-lands/planning/studies/fhwa-building-resilience-through-maintenance-final.pdf), [FHWA pavement temperature](https://www.fhwa.dot.gov/pavement/pub_details.cfm?id=229), [FHWA hot-weather concrete](https://www.fhwa.dot.gov/publications/research/infrastructure/pavements/pccp/04122/03.cfm).

## 4. Construction work/rest and concrete-pour planning

- Industry: construction.
- Specific user: a site superintendent planning outdoor heavy work and concrete operations.
- Current workflow: crew plan and pour schedule are set, then safety staff interpret heat guidance and add controls.
- Pain: schedules often treat a city as one temperature and fail to expose sustained hot windows for particular sites.
- Frequency/consequences: daily during active projects; productivity loss, heat illness risk, curing/quality issues, and expensive schedule changes.
- Missing information: peak hour and continuous exceedance at the actual site plus contextual humidity/solar conditions.
- Why temperature intelligence matters: FortyGuard can quantify when and where the threshold is exceeded, then provide environmental context.
- Action: shift heavy work, split a task, add shade/rest, or escalate a pour decision.
- Material FortyGuard fit: high for decision support; no automated safety clearance.

Evidence: [CDC heat stress and workers](https://www.cdc.gov/niosh/heat-stress/about/index.html), [NIOSH construction guidance](https://www.cdc.gov/niosh/bulletin/2020/heat-stress-construction.html).

## 5. Emergency heat-response logistics

- Industry: emergency management.
- Specific user: a city emergency operations logistics planner coordinating cooling centers and water distribution.
- Current workflow: use alerts, population maps, facility lists, and manual coordination.
- Pain: the response must repeatedly prioritize sites, supplies, and staffing as a heat event evolves.
- Frequency/consequences: episodic but high impact; delayed cooling access and stressed responders.
- Missing information: which neighborhoods/sites sustain the highest heat burden and when demand will be most operationally difficult.
- Why temperature intelligence matters: spatial persistence and environmental context can refine resource staging.
- Action: prioritize a site, move supplies, add a cooling station, or escalate an unmet need.
- Material FortyGuard fit: high in a U.S. city, but external population/facility data and public-sector workflow introduce dependency risk.

Evidence: [FEMA extreme heat planning](https://www.fema.gov/sites/default/files/documents/fema_response-recovery_climate-change-planning-guidance_20230630.pdf), [FEMA incident support](https://www.fema.gov/es/about/offices/response/incident-support).

## 6. Data-center cooling readiness

- Industry: facilities and data centers.
- Specific user: a facilities operations lead preparing a multi-site cooling/economizer readiness plan.
- Current workflow: review outdoor forecasts, load plans, cooling telemetry, and maintenance windows.
- Pain: outdoor heat and solar load can shift cooling demand; teams need to identify which site or maintenance window deserves attention first.
- Frequency/consequences: daily monitoring, with high cost during peaks; efficiency loss, water/energy use, and availability risk.
- Missing information: hyperlocal ambient/solar profiles and persistence around each facility.
- Why temperature intelligence matters: FortyGuard environmental parameters include solar irradiance, humidity, and temperature context; heatmap spatial comparison can rank campuses.
- Action: prioritize inspection, prepare cooling capacity, shift noncritical work, or request human approval for setpoint changes.
- Material FortyGuard fit: medium-high; live facility telemetry is necessary for a credible production product.

Evidence: [DOE data-center cooling](https://www.energy.gov/cmei/femp/cooling-water-efficiency-opportunities-federal-data-centers), [DOE data centers](https://www.energy.gov/hgeo/geothermal/geothermal-and-data-centers).

## 7. Transit stop and public-space intervention priority

- Industry: transit/public works.
- Specific user: a transit amenities manager choosing which bus stops receive shade, water, or schedule attention first.
- Current workflow: rank by ridership, complaints, equity, and broad urban heat maps.
- Pain: static prioritization does not show when a stop is hot for long enough to matter operationally.
- Frequency/consequences: seasonal capital planning; poor rider comfort and inequitable exposure.
- Missing information: tile-level peak timing, persistence, and intervention candidate comparison.
- Why temperature intelligence matters: FortyGuard can supply a common spatial/time scale for stop comparison.
- Action: rank stops for intervention or send a site for human design review.
- Material FortyGuard fit: high, but it competes with established heat-planning dashboards.

Evidence: [WRI Cool Cities Lab](https://coolcities.wri.org/help), [Smart Surfaces decision tool](https://smartsurfacescoalition.org/decision-support-tool).

## 8. Event setup and crowd-safety operations

- Industry: events and venue operations.
- Specific user: an outdoor event operations director placing cooling stations and sequencing setup crews.
- Current workflow: venue map, staffing plan, and weather alert; cooling resources are placed before the event.
- Pain: setup and crowd areas have different surfaces, shade, and peak timing; resources may be placed by habit.
- Frequency/consequences: each event; heat emergencies, staff strain, and costly last-minute changes.
- Missing information: site-specific persistent heat and environmental context.
- Why temperature intelligence matters: hyperlocal heat layers can compare the event footprint and candidate cooling locations.
- Action: place a station, move setup earlier, increase staffing, or escalate a heat plan.
- Material FortyGuard fit: medium-high, with event geometry and crowd data required.

## Research synthesis

The best agent wedges are not generic alerts. They are bounded, repeatable decisions with a candidate set, constraints, an action proposal, and a measurable before/after proxy. The three most buildable wedges are road/construction windows, field-service sequences, and warehouse dock shifts.
