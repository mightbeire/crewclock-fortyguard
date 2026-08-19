# Duplication and obviousness research

## Public patterns found

- Worker heat apps already provide alerts, break schedules, multilingual messaging, and photo-based risk scans. Example: [Starkz AI](https://starkzai.com/).
- Heat-stress apps already use weather feeds, WBGT, schedules, and worker alerts. Example: [AIHA Heat Stress app](https://www.aiha.org/press/aiha-launches-new-heat-stress-mobile-app).
- Urban heat platforms already map hotspots, explain drivers, and prioritize greening/cooling investments. Examples: [WRI Cool Cities Lab](https://coolcities.wri.org/help), [Geoneon Heat](https://www.geoneon.com/solutions/heat), [HeatAtlas](https://heatatlas.com/), [Smart Surfaces DST](https://smartsurfacescoalition.org/decision-support-tool).
- Thermal route planning and eco-routing are active research/product themes. Examples: [thermal comfort path planning](https://arxiv.org/abs/2602.02540), [temperature intelligence use cases](https://docs-api.fortyguard.com/).
- The vendored FortyGuard quickstart already contains parcel screening, bus-stop prioritization, parks audits, and real-estate heat-risk workflows. These are reusable reference patterns, not unexplored product wedges.

## Candidate-level risk assessment

| Candidate | Risk | Why |
|---|---:|---|
| Field-service thermal sequence | 3 | Heat-aware dispatch is plausible and adjacent to worker safety apps; the constraint-preserving sequence/verification wedge differentiates it. |
| Warehouse dock heat orchestration | 2 | Specific indoor/outdoor dock workflow is less common than generic worker alerts. |
| Pavement maintenance window agent | 2 | Industrial asset-quality plus worker scheduling is a narrower wedge and uses persistence/exceedance meaningfully. |
| Cooling-center logistics allocator | 3 | Emergency heat logistics is differentiated but public-sector resource allocation is a known pattern. |
| Data-center cooling readiness | 2 | Strong industrial specificity; depends on facility telemetry for a credible production story. |
| Transit-stop intervention triage | 3 | Existing heat-planning tools make generic prioritization obvious; a time-window/action loop is needed. |
| Construction work/rest planner | 4 | Worker heat scheduling is an obvious hackathon idea and crowded by existing apps. |
| Event cooling-station planner | 3 | Specific event footprint helps, but alerts and station placement are common. |
| Utility outage crew staging | 3 | Strong operations fit, but closely resembles field-service dispatch. |
| Commercial real-estate retrofit triage | 3 | Existing FortyGuard examples and urban heat tools cover much of this. |
| Airport ramp rotation planner | 2 | Narrow operational workflow, but airport data and safety validation raise dependency risk. |
| Concrete pour QA window | 2 | Distinct asset-quality wedge; engineering/legal claims must remain human-approved. |
| Delivery hot-zone routing | 4 | Heat-aware route planning is an obvious and researched idea. |
| Agriculture harvest optimizer | 3 | Potentially useful but geographic/data coverage and crop context are weak for this account. |
| Manufacturing yard task allocator | 2 | Specific industrial workflow, but requires plant task/telemetry integration. |

## Duplication strategy

Do not claim novelty because no identical public product was found. The defensible wedge is: an agent that selects among operational alternatives, calls FortyGuard only when needed, proposes a human-approved change, and verifies a transparent metric. A static map, alert, or ranked list alone is insufficient.

The handbook reinforces this boundary: its Industrial & Enterprise examples include data-center siting, heat-sensitive cargo/worker protection in transit, and parametric heat-risk scoring; its Agentic examples include goal-driven endpoint selection, monitoring, and auditable research. Those examples increase duplication risk for generic siting, routing, alerts, or reports. The surviving concepts stay narrower by centering a repeatable operational decision and a verification loop.

The live 96-tile test also prevents overclaiming novelty through spatial precision: the selected AOI/date produced nearly uniform daily heat values and one exceedance hour per tile. Spatial differentiation must be demonstrated for a real approved geography before it is used as a finalist claim.

## Second-wave public attack

- [Perry Weather](https://perryweather.com/features/heat-stress-and-wbgt-monitoring/work-rest-cycles/) already offers location-specific heat/work-rest scheduling, so generic workforce heat scheduling is not novel.
- [IBM Maximo](https://www.ibm.com/products/maximo/field-service-management) and field-service products already offer spatial prioritization, work orders, dispatch, and AI scheduling, so Thermal Sequence must retain its conditional FortyGuard investigation and verification wedge.
- [Copeland](https://www.copeland.com/en-us/products-solutions/controls-solutions/in-transit-solutions) and [TrueCold](https://www.truecold.io/industries/logistics) already combine cold-chain telemetry, location, alerts, and intervention, so cold-chain dwell is rejected.
- Rail extreme-heat patrol rules are established in [Amtrak procedures](https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/corporate/engineering-practices/engineering-standards/procedures-installation-adjustment-maintenance-inspection-cwr-49-cfr-213-118.pdf) and [FRA ATIP](https://railroads.fra.dot.gov/railroad-safety/partnerships-programs/automated-track-inspection-program-atip), but the narrower auditable patrol-queue agent remains less obvious than a generic alert.
- 311/pothole systems already exist in [Los Angeles](https://data.lacity.org/City-Infrastructure-Service-Requests/MyLA311-Service-Request-Data-2024/b7dx-7gc3) and [Portland](https://www.portlandmaps.com/arcgis/rest/services/Public/PBOT_Maintenance/MapServer/layers); the defensible novelty is joining public work-order triage to live heat timing and satellite context, not claiming to invent repair queues.

Public duplication research therefore passes, but it lowers the ceiling for generic heat safety, generic dispatch, generic warehouse, and generic monitoring concepts.
