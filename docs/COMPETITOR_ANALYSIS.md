# Competitor and substitute analysis

Date: 2026-08-19. Competitor count in this pass: 18 named products/platforms plus public/regulatory substitutes. Product pages establish feature overlap, not independently verified outcomes.

## Competitor matrix

| Competitor / substitute | Target user | Current functionality | Heat/weather | Scheduling/optimization | AI/agent | Integrations/data | Remaining wedge |
|---|---|---|---|---|---|---|---|
| Cityworks / Trimble Unity Maintain | Public works, utilities, local government | GIS asset registry, service requests, work orders, inspections, mobile execution | Not a core heat intelligence product; can consume GIS/weather layers | Work management and configurable workflows; route/dispatch varies by deployment | Automation and configurable dashboards; not the same evidence-aware agent claim | ArcGIS/geodatabase, feature services, mobile/offline | Heat-specific work-window evidence and approval layer, if it writes back safely |
| IBM Maximo FSM / Scheduler | Asset-intensive field operations, transport, utilities | EAM, work orders, crews, skills, SLAs, inventory, maps, mobile, approvals | Weather alerts/integration and environmental factors documented | 600+ constraints, dynamic dispatch, appointments, availability, reoptimization | Maximo Assistant, work-order intelligence, visual inspection | Enterprise EAM, GIS, sensors, inventory and contracts | A narrow FortyGuard evidence adapter that augments rather than replaces Maximo; difficult standalone sale |
| Bentley AssetWise Inspections | Transportation infrastructure owner/operators | Inspection capture, asset inventory, project prioritization, work scheduling, compliance | No demonstrated heat-specific differentiation | Maintenance planning and prioritization | Analytics; not positioned as a general agent | Linear/transportation asset data, inspections | Heat-triggered evidence review, but overlap is high for roads/rail |
| Bentley AssetWise Rail Condition Analytics | Rail asset managers, reliability engineers | Rail condition analytics and risk-based maintenance strategy | Not a public heat-specific product | Maintenance strategy optimization | Predictive/analytics | Rail condition and asset lifecycle data | Only if the agent uses operator heat/RNT data to explain a gap, not ambient-only patrols |
| Trimble rail solutions / E2M / GEDO | Rail owners, MOW, survey and maintenance teams | Asset maintenance, inspection, track surveying, monitoring, predictive analytics | Temperature may be an asset/environment input; not the tested wedge | Maintenance programs, exam planning, resource allocation | Analytics and automation | Track survey, remote diagnostics, asset systems | Public-data evidence packet for a narrow pilot; incumbent integration is a gate |
| Wabtec RailDOCS / wayside software | Railroad maintenance, signal, train-control and inspection teams | Inspection, configuration, reporting, maintenance, availability, compliance records | Wayside sensors can capture condition; no evidence FortyGuard is needed | Maintenance planning and employee availability | Automated condition monitoring | 6M+ forms/100k locations claimed in vendor brief; operator systems | Seasonal evidence/audit workflow around existing data, not new patrol authority |
| FRA ATIP and operator inspection systems | FRA, Class I railroads, safety stakeholders | Geometry, gage restraint, machine vision, asset inventory, risk and manual-inspection allocation | Actual track condition/inspection evidence is stronger than satellite context | Patrol/inspection resource allocation | Machine vision and analytics | High-value rail inspection datasets | Could supply a heat-triggered evidence query, but not replace inspection systems |
| Perry Weather | EHS, construction, sports, outdoor worksites | On-site WBGT, heat index, alerts, work/rest cycles, policy, historical records | Core product; 15-min local station data and 72-hour forecasts | Work/rest cycle and heat policy timing | Rules/automation; not a route optimizer | Sensors, alerts, user groups, records | Route/work-order constraint orchestration across existing FSM, but Perry is a direct heat input competitor |
| OSHA/NIOSH Heat Safety App + WBGT calculator | Employers and workers | Heat-index screening, WBGT guidance/calculator, workload/acclimatization/clothing considerations | Core reference | Guidance, not dispatch optimization | No | Public app/guidance | An agent can translate policy into a draft schedule, but cannot claim safety certification |
| NOAA/NWS NDFD + HeatRisk | Public, commercial weather users, emergency managers | Gridded forecasts, heat-risk category, duration/climatology/CDC context | Strong baseline; NDFD about 2.5 km native, HeatRisk 7-day daily | Inputs can feed scheduling; not operational work-order changes | No | Open/public data, APIs, weather vendors | FortyGuard must add measured spatial/physical context that changes a decision, not simply temperature |
| ServiceNow FSM | Enterprise field dispatch | Dynamic scheduling, schedule optimization, skills, travel, task priority, intraday reoptimization | Weather can be a contextual input; not core heat-specific | Core capability; runs on intervals/on demand | “Intelligent” recommendations and automation | ServiceNow tables, mobile and enterprise workflows | Heat-evidence exception agent, with strong integration hurdle |
| Salesforce Field Service | Enterprise service organizations | Global/in-day/resource optimization, appointments, territories, skills, promises | Weather not core; can integrate data | Core capability, evaluates many schedule permutations | Agentforce/AI-assisted operations | CRM, service resources, mobile, APIs | A heat-aware policy/evidence layer; Salesforce could absorb the feature |
| Microsoft Dynamics 365 Field Service | Enterprise field service | Resource Scheduling Optimization, promises, requirements, characteristics, time windows | Not core heat intelligence | Core constraint/goal system | Scheduling Operations Agent preview | Dynamics work orders, resources, characteristics | Heat evidence as a new objective/constraint, but platform owner has strong absorbability |
| Google OR-Tools / Route Optimization | Developers, operations researchers | VRP/VRPTW, time windows, travel, vehicle and objective constraints | Any numeric heat cost can be added by implementer | Deterministic solver | No agent required | Custom matrices and APIs | Agent can select evidence and explain alternatives; solver should own math |
| Pave / RoadBotics-style road condition analytics | Road agencies, asset owners | Road imagery/condition assessment, pavement intelligence, prioritization | Weather/season may be a contextual variable | Maintenance prioritization, not necessarily crew sequencing | ML/vision, not general agent | Dashcams, imagery, pavement condition data | Work-window decision tied to heat and material specs; still crowded by road analytics |
| FixMyStreet / 311 portals | Citizens and municipalities | Intake, geocoding, routing to authority, status communication | Usually not heat-conditioned | Not an optimizer; feeds work queues | Basic classification/automation varies | Public requests, GIS and agency systems | Downstream decision layer, not intake; must prove writeback value |
| Road/rail internal CMMS/EAM and spreadsheets | Supervisors/planners | Existing local priorities, checklists, work orders, manual judgement | Weather apps, policy docs, local gauges | Manual boards, spreadsheets, deterministic rules | Human judgement often best contextual source | Private assets, crews, restrictions, history | Narrow evidence audit and explainability; low change-management burden needed |
| Hackathon/open-source pothole and scheduling projects | Hackathon judges/developers | Pothole detection, repair ranking, AI scheduling, conversational shift planning | Often weather/heat absent or generic | Routing/scheduling is common | LLM/vision agents common | Public imagery, synthetic jobs | The only defensible novelty is a specific, measured, human-approved heat intervention |

## Direct / indirect / substitute classification

### Road Repair Queue

Direct: pavement-condition/road-maintenance analytics and AI work-order products. Indirect: Cityworks, Trimble Unity, IBM Maximo, Cartegraph/OpenGov-style public works systems, 311 portals, Esri GIS. Substitutes: supervisor queue review, pavement-management scoring, crew board, contractor SLA report, spreadsheet. Adjacent entrants: Maximo, Bentley, Trimble, Esri partners, road-vision vendors.

The potential wedge is narrower than claimed: **evidence-backed work-window verification for a repair already selected by pavement condition/SLA**, with optional queue re-ranking only when a documented treatment/crew constraint makes heat operationally relevant.

### Thermal Sequence Planner

Direct: heat-safety/work-rest products for outdoor crews and FSM schedule optimizers. Indirect: ServiceNow, Salesforce, Dynamics, Maximo, Oracle Field Service, route-optimization engines. Substitutes: dispatcher judgement, NWS/NOAA forecast, OSHA/NIOSH calculator, manual swap, fixed work/rest policy. Adjacent entrants: every major FSM/EAM platform has an incentive to add heat as one more constraint.

The potential wedge is **a read-only exception agent** that monitors schedules already produced by an incumbent, selects only exposed jobs for deeper evidence, proposes alternatives and stops for approval. A standalone sequence planner is not defensible.

### RailHeat Patrol Sequencer

Direct: rail asset/inspection/condition-monitoring platforms and railroad summer-preparedness checklists. Indirect: IBM Maximo Transportation, Bentley AssetWise, Trimble rail, Wabtec RailDOCS, FRA ATIP, operator dispatch/track systems. Substitutes: CWR plan, railroad heat orders, track supervisor and qualified inspector judgement, manual patrol board. Adjacent entrants: incumbents with track geometry/asset data and vendors of rail temperature/condition sensors.

The potential wedge is **a plan-evidence/audit agent** that checks operator-provided CWR/summer-preparedness records for missing inputs and drafts a review queue. The current patrol sequencer is not defensible from public data plus FortyGuard alone.

## Incumbent absorbability test

| Concept | Could an incumbent absorb it? | Why |
|---|---|---|
| Road queue | Yes, high | Cityworks/Maximo already own the work order, asset, map and approval path; a weather/heat layer is an integration feature. |
| Thermal sequence | Yes, very high | FSM platforms already have objectives, constraints, intraday optimization and AI agents; heat can become a cost/constraint field. |
| Rail patrol | Yes, high | Rail EAM/inspection vendors already own the asset, inspection, compliance and planning data; a separate app lacks authority and inputs. |

## Competitor conclusion

The work cannot be sold as “AI scheduling” or “hyperlocal heat alerts.” The defensible hackathon claim is narrower: **a provider-neutral, tool-using evidence agent that audits whether a heat-sensitive operational recommendation is actually supported, calls FortyGuard selectively, invokes deterministic optimization where appropriate, preserves system constraints, and produces a human-approval packet with uncertainty.** That is a workflow wedge, not a standalone market category yet.
