# FortyGuard Hackathon '26 — money-first problem research

Research date: 2026-08-20
Decision state: **evidence ranking only; `FINAL_MVP_SELECTED = NO`**
FortyGuard boundary: **`LIVE_FORTYGUARD_CALLS = 0`**; only the existing sanitized cache was inspected.
Full citation ledger: [`MONEY_FIRST_SOURCES.md`](./MONEY_FIRST_SOURCES.md)

## Executive finding

The previous finalist set was optimized around understandable, attractive demonstrations. The money-first search reverses that ranking.

The strongest proven demand is not “help people avoid a hot place.” It is **help an operations owner execute a response they already perform when temperature changes, across too many assets and constraints for a static alert to finish the job**.

Three findings survive that standard:

1. **NightWatch Grid** — distribution operators already reduce voltage, pre-cool equipment, shift load, stage generation and crews, and replace heat-failed transformers. SCE installed **492 transformers in eight days** during a 2022 heat wave because high overnight temperatures prevented equipment cooling. This is the current evidence leader because the pain, operator, response, public grid geography, cached Los Angeles thermal evidence, and visible before/after all line up.
2. **FreezeLine** — gas-field operators already heat-trace, inject methanol, raise flow, staff facilities, clear roads, and file weather-readiness plans. During Uri, Texas gas production fell **more than 10 Bcf/day** over Feb. 8–17, mostly from freeze-offs. It is the strongest pure business case, but the local cache contains no usable Texas cold-event FortyGuard map; that is a real demo blocker, not a footnote.
3. **CrewClock** — construction superintendents already change schedules, tasks, breaks, rotation, and cooling when heat rises. OSHA's proposed-rule analysis cites **39,450 heat cases with days away from work in 2011–2022** and estimates **$7.8B annual compliance cost** and **$9.179B annualized benefits** across all covered industries. The agent can turn a policy into a constraint-valid daily work plan, but FortyGuard must not be represented as WBGT or a compliance sensor.

The prior three do not survive. ShiftShield has no evidence that delivery organizations already re-route for temperature or that its scenario minutes map to a corporate KPI. CourseCorrect is episodic, route changes are made too early, and participant-minutes are not an established financial metric. Recess Relay has human relevance but no demonstrated budget owner, economic KPI, or buying signal.

## Evidence and scoring rules

- A reported number keeps its provenance: direct report, agency estimate, academic model, industry estimate, or derived demo calculation.
- No dollar conversion was invented. Where only operational thresholds or capacity exist, the metric remains hours, MW, Bcf/day, cases, lane-miles, or assets.
- `EXISTING_TEMPERATURE_RESPONSE`, `ECONOMIC_ALIGNMENT`, `FORTYGUARD_DEPENDENCE`, `AGENTIC_NECESSITY`, `BUYING_SIGNAL`, `DEMO_DATA_QUALITY`, `TEN_SECOND_CLARITY`, and `DEMO_WOW` are 0–10 research judgments.
- `INCUMBENT_THREAT`, `DUPLICATION_RISK`, and `BUILD_RISK` are adverse scores: 10 is worst.
- The official-rubric score is `0.40 Impact + 0.35 Technical + 0.15 Innovation + 0.10 Communication`.
- The risk-adjusted rank is deliberately lower when a concept lacks cached FortyGuard coverage, authoritative operational inputs, or safe decision authority.

## Phase 1–13: 34 operational problem areas

| # | Temperature-driven operating problem | Measurable evidence and provenance | What changes today | Concrete user | ETR / EA | Disposition and falsification result |
|---:|---|---|---|---|---:|---|
| 1 | Distribution-transformer heat overload/failure | SCE directly reported 492 transformers installed in eight days and ~295,000 temporary customer outages during a nine-day 2022 heat wave; ORNL cites a 7°C hotspot rise doubling aging acceleration and 2,000 California distribution transformers failing in a 2006 heat wave. | Pre-cooling, voltage reduction, load relief/transfer, patrols, infrared surveys, mobile generation, extra crews, customer demand response. | Distribution System Operator / Dispatcher | 10 / 10 | **SURVIVE.** Real asset damage, capacity, overtime, reliability, and current response. FortyGuard is only an uninstrumented-asset screening layer, never winding telemetry. |
| 2 | Natural-gas well/gathering freeze-offs | EIA directly reports Texas output fell >10 Bcf/day Feb. 8–17, 2021, mostly from freeze-offs; Henry Hub hit $23.86/MMBtu. FERC reports 20,000 MW rolling blackouts and 43.3% of gas-production decline tied to freezing/weather. | Heat tracing, heating, methanol injection, higher flow, staff staging, road preparation, line-pack/storage changes, readiness attestation. | Gas Field Operations Supervisor | 10 / 10 | **SURVIVE.** Exceptional money/reliability proof and buying signal. Cached FortyGuard Texas heatmaps returned zero cells and no cold-event cache exists. |
| 3 | Outdoor construction heat planning | OSHA cites 39,450 days-away heat cases in 2011–2022; its proposed-rule economic model estimates $7.8B annual compliance cost and $9.179B benefits across covered industries, not construction alone. | Cooler-time scheduling, shorter shifts, work/rest, rotation, lower workload, shade/cooling, acclimatization, emergency plans. | Construction Superintendent | 10 / 9 | **SURVIVE.** Existing policy must become a daily plan. Must use employer-approved WBGT/policy and onsite verification; FortyGuard alone is not compliance evidence. |
| 4 | Asphalt placement windows | FHWA specifies no HMA on wet or under-minimum-temperature surfaces; example minima are 5/8/10°C by lift thickness and require three surface readings. Metric is compliant placement hours, directly specified—not dollars. | Reschedule, change lift/mix, heat screed, stop placement, obtain warranty/exception, take local surface readings. | DOT Construction Manager / Paving Superintendent | 10 / 8 | **SURVIVE.** Temperature is literally in acceptance workflow; public jobs exist. Direct nationwide dollar loss is not proven. |
| 5 | Hot/cold concrete placement and curing | FHWA says >32°C hot-weather placement can create early-age damage; evening/night placement is generally recommended, with chilled water/ice/insulation alternatives. Metric is compliant/low-risk pour window. | Change pour time, cool or heat ingredients, use admixtures/insulation, alter curing, monitor concrete/pavement temperature. | Concrete Superintendent / DOT Materials Engineer | 10 / 8 | **MERGED into PaveWindow.** Same buyer/data/agent shell; mix temperature and maturity remain authoritative. |
| 6 | Winter road anti-icing and material use | FHWA reports Michigan DOT's estimate of 25% less salt = ~$2.1M/year plus $680k/year reporting labor savings; MnDOT says salt melts >5× as much ice at 30°F as at 20°F. | Choose material/rate/time, pre-treat bridges, call shifts, dispatch routes, compare actual vs recommended application. | Winter Maintenance Superintendent | 10 / 9 | **SURVIVE ROUND 1; KILL ROUND 2.** Strong pain but existing MDSS already combines pavement forecasts, rules, fleet and treatment recommendations. FortyGuard is a layer an incumbent can add. |
| 7 | Gas/combined-cycle plant heat derating | ORNL/CEC model: NGCC capacity falls 0.3–0.5% per °C above 15°C; EIA publishes summer vs winter capability. Model, not universal observed conversion. | Apply OEM derate curves, change commitment/reserves, schedule maintenance, use inlet cooling where available. | Generation Operations Manager / Power System Operator | 10 / 9 | **SURVIVE.** Real MW and price exposure with excellent public assets, but ordinary forecasts and plant telemetry weaken FortyGuard dependence. |
| 8 | Transmission ambient-adjusted/dynamic line rating | DOE example: a 10°C cooler forecast can raise an ambient-adjusted rating ~10%; Oncor demonstration reported average DLR gains of 6–14% (345 kV) and 8–12% (138 kV) over AAR. | Recalculate hourly ratings, switch/transfer load, constrain dispatch, monitor sag/conductor/weather sensors. | Transmission System Operator | 10 / 9 | **KILL ROUND 1.** DLR needs wind/conductor/sag sensors; AAR is deterministic and ordinary forecast-accessible. FortyGuard lacks a defensible unique wedge. |
| 9 | Thermal-plant cooling-water heat | EIA reports warmer intake/discharge water can lower capability or force curtailment; exact plant impact is site-specific. | Derate/curtail, change dispatch, monitor discharge permits and water conditions. | Plant Operations Manager | 10 / 9 | **MERGED into PlantReserve.** Water temperature/flow and permits, not FortyGuard tiles, are authoritative. |
| 10 | Data-center cooling/economizer operation | DOE recommends 65–80°F intake and rack/onboard sensing; outside air changes economizer hours. No U.S. heat-specific outage dollars established here. | Adjust supply air/setpoints, economizers, airflow, water/chiller mode, load. | Data Center Facilities Manager | 10 / 9 | **KILL.** Indoor/rack telemetry and building controls dominate; Weather.com is often enough for economizer planning. |
| 11 | Commercial-building HVAC/demand response | DOE documents economizer/setpoint savings; Con Edison pays customers to reduce load during hot demand periods. | Pre-cool, reset temperatures, shed flexible loads, enroll in DR. | Portfolio Energy Manager | 10 / 8 | **KILL.** BMS telemetry, tariff/DR signal, and ordinary forecast already close the loop; tile heat is secondary. |
| 12 | Supermarket refrigeration heat load/failure | EPA confirms dedicated compressor/case systems; food safety requires internal product/case limits. No external-temperature-specific U.S. spoilage number verified. | Stage defrost, adjust compressors/setpoints, alarm/transfer stock, call service. | Refrigeration/Fleet Facilities Manager | 10 / 8 | **KILL.** Case temperature/refrigerant telemetry is decisive; hyperlocal outdoor heat is an auxiliary feature. |
| 13 | Refrigerated-truck loading/dwell | USDA says time-temperature abuse is additive even during loading/unloading and can cause considerable quality loss. | Pre-cool, reduce door-open dwell, check product temperature, adjust reefer setpoint, reject/hold loads. | Cold-Chain Operations Manager | 10 / 9 | **KILL.** Product/reefer probes and telematics outperform environmental tiles; no public operational load data. |
| 14 | Warehouse/dock worker heat | OSHA verifies work/rest/schedule changes; O*NET verifies warehouse managers plan staffing against fluctuating workload. | Shift breaks/tasks, move dock assignments, use cooling, change staffing. | Distribution Center Operations Manager | 9 / 8 | **KILL.** Indoor dock heat is poorly represented by outdoor tiles; private labor/throughput data and WBGT sensors are necessary. |
| 15 | Manufacturing-floor heat productivity | OSHA documents heat-related performance/productivity effects and work controls. | Work/rest, ventilation, line speed, job rotation, maintenance timing. | Production Manager | 9 / 8 | **KILL.** Process heat and indoor sensors dominate; a generic “factory heat agent” is too broad. |
| 16 | Dairy heat stress | USDA-hosted estimate: $1.69–$2.36B/year livestock losses in 2002 dollars, dairy 53–64%; USDA model projects 0.6–1.3% lower milk output by 2030. | Fans, misters/sprinklers, shade, water, ration/milking changes, intense cooling. | Dairy Operations Manager | 10 / 9 | **SURVIVE ROUND 1; KILL ROUND 2.** Strong money and response, but barn THI/sensors and herd telemetry dominate; exact-farm public demo data are poor. |
| 17 | Swine heat stress | USDA reports an industry estimate of $481M annual U.S. revenue loss. | Ventilation, sprinklers, cool water, early transport; USDA HotHog already predicts six thermal states from local weather. | Swine Production Manager | 10 / 9 | **KILL ROUND 1.** USDA already offers a purpose-built weather decision app; barn sensing and animal-specific models beat a generic temperature layer. |
| 18 | Poultry heat stress | USDA source-cited estimate is $127–165M/year in 2002 dollars. | Tunnel ventilation, cooling, water/feed changes, transport timing. | Poultry Complex Manager | 10 / 8 | **KILL.** Indoor house sensors/control systems dominate; no compelling FortyGuard wedge. |
| 19 | EV-fleet cold range/charging | DOE controlled tests show nearly 40% lower EV efficiency at 20°F vs 77°F. | Precondition, charge more, change route/vehicle, use covered parking. | Fleet Manager | 10 / 9 | **KILL.** Vehicle SOC, route, charger and OEM range models dominate; ordinary forecast can supply temperature. |
| 20 | Airline hot-weather takeoff performance | FAA confirms offloading cargo/passengers, lower fuel, or added stops may be required when heat reduces lift. | Certified performance calculation, payload/fuel changes, runway/flight timing. | Airline Dispatcher | 10 / 10 | **KILL.** Safety authority is the aircraft manual plus official airport weather; FortyGuard cannot enter the dispatch release as controlling data. |
| 21 | Aircraft deicing/anti-icing | FAA holdover tables vary by outside temperature and precipitation; short windows can be minutes. | Deice, choose fluid, sequence aircraft, recheck holdover, return for treatment. | Airport Deicing Coordinator | 10 / 9 | **KILL.** METAR/official sensors, precipitation and wing inspection govern; liability and incumbent systems are prohibitive. |
| 22 | Continuous-welded rail heat | FRA plans tie inspections/speed restrictions to measured rail temperature, neutral temperature, cuts/breaks and track restraint. | Slow orders, inspections, rail adjustment, qualified-person decisions. | Track Supervisor / Dispatcher | 10 / 9 | **KILL.** Ambient/surface heat can trigger investigation but cannot determine safe rail action. Prior RailHeat concept remains killed. |
| 23 | Transit overhead-catenary/signal heat | FTA says heat may cause visual-monitoring increases, slow orders/cancellations, set-point adjustment, or retensioning; CTA added trains for heat slow orders. | Inspect more, issue slow orders, add trains, adjust/repair OCS and cooling. | Rail Operations Control Manager | 10 / 8 | **KILL.** Asset-specific temperatures/tolerances and private network condition are mandatory; public demo action is too synthetic. |
| 24 | Solar-PV module heat derating | ORNL synthesis cites a 0.66%/°C crystalline-silicon model above 25°C; cell temperature also depends on irradiance, wind and system properties. | Mostly forecast/accept derate; inspect faults, curtail for grid reasons, clean/maintain. | Solar Operations Manager | 5 / 8 | **KILL.** The industry usually does not have a movable daily response to module heat; existing-response test fails. |
| 25 | Telecommunications shelter/battery heat | Thermal management and preventive maintenance are real, but no strong U.S.-specific cost/response number was verified in this pass. | HVAC alarms, setpoint/cooling, battery inspection/replacement, dispatch. | Network Operations Center Manager | 8 / 7 | **KILL.** Enclosure sensors are decisive; public site/SLA data are weak. |
| 26 | Water-main freeze/break response | EPA confirms main breaks cause lost revenue, wasted resources and quality risk; a temperature-specific national cost was not verified. | Leak detection, emergency repair, pressure isolation, crew staging. | Water Distribution Operations Manager | 8 / 8 | **KILL.** Pipe age, soil/frost depth and hydraulic telemetry dominate; ordinary cold forecasts suffice for staging. |
| 27 | Roofing/coating/adhesive temperature windows | Manufacturer/specification limits and crew-heat changes are real, but no U.S.-wide measurable loss was verified. | Reschedule, shade/heat materials, change product, test substrate. | Roofing/Industrial Maintenance Superintendent | 9 / 6 | **KILL.** Strong sponsor fit but weak quantified pain and fragmented product-specific rules. |
| 28 | Waste-collection heat scheduling | Municipal agencies shift start times and apply OSHA work controls; no temperature-attributable fleet-cost number was verified. | Earlier shifts, route/break changes, extra water/cooling, overtime. | Solid Waste Operations Manager | 9 / 7 | **KILL.** Public routes can demo it, but the core is worker heat policy and ordinary dispatch; weak FortyGuard dependence. |
| 29 | Airport-ramp heat operations | OSHA controls apply and airports adjust breaks/tasks; public airport geometry exists but turn rosters and heat-cost attribution do not. | Rotate tasks, add breaks/cooling, change staffing and ground sequence. | Ramp Operations Manager | 9 / 7 | **KILL.** Private task data plus onsite WBGT; weaker buyer case than construction. |
| 30 | Last-mile delivery heat routing (ShiftShield) | No primary evidence found that U.S. delivery organizations already re-sequence stops by hyperlocal temperature or value “hottest-cell minutes.” | Breaks/cooling and generic heat programs exist; route order is governed by service/travel constraints. | Delivery Operations Manager | 4 / 5 | **KILL.** Solution-first metric, unproven corporate KPI, crowded routing incumbents. |
| 31 | Race/event route heat (CourseCorrect) | FAA/OSHA-style heat response exists for events, but no recurring business loss or buyer spend was verified; closures are fixed early. | Wave changes, hydration/medical resources, cancellation, contingency routes. | Race Director | 7 / 5 | **KILL.** Participant-minutes are derived, market is episodic, and thermal evidence arrives after major route authority decisions. |
| 32 | School outdoor-space scheduling (Recess Relay) | Human-health relevance is clear, but no operating-cost/capacity KPI or buying program for within-campus thermal scheduling was verified. | Move activities indoors, change times/locations, cancel. | School Administrator | 8 / 4 | **KILL.** No balance-sheet proof, procurement weak, cached thermal data were mapped onto a synthetic campus. |
| 33 | Parks/golf turf heat and irrigation | Turf managers alter irrigation and maintenance; no defensible U.S. temperature-attributable loss number was verified. | Irrigate, syringe/cool, restrict use, shift mowing/crew work. | Golf Course Superintendent / Parks Manager | 9 / 6 | **KILL.** Soil moisture/ET/turf sensors and water rules dominate; economic evidence weak. |
| 34 | Crop frost/harvest timing | Growers already use frost protection and harvest timing; losses can be large but crop/site specificity and exact-farm public data are limiting. | Irrigate, wind machines/heaters, harvest early, redeploy crews. | Farm Operations Manager | 10 / 8 | **KILL.** Established ag-weather and field-sensor products; broad “agriculture agent” lacks a narrow wedge. |

`ETR` = existing temperature response. `EA` = economic alignment.

### First elimination result

Nine survivors met the initial bar of real pain, evidence, a current response, a clear user, and economic alignment:

1. NightWatch Grid
2. FreezeLine
3. CrewClock
4. PaveWindow
5. SaltWise
6. PlantReserve
7. DairyCool
8. Rail Heat-Plan Audit
9. Cold-Chain Dwell Control

Everything else died for one or more explicit reasons in the table: authoritative onsite telemetry displaced FortyGuard, there was no current temperature response, the buyer/KPI was vague, the public demo inputs were fictional, or a deterministic incumbent already performed the job.

### Second elimination result

| Survivor | FG dep. | Agent need | Clarity | Econ. | Demo data | Decision |
|---|---:|---:|---:|---:|---:|---|
| NightWatch Grid | 8 | 9 | 9 | 10 | 8 | **FINAL FIVE** |
| FreezeLine | 8 theoretical / 3 cached proof | 9 | 10 | 10 | 6 | **FINAL FIVE**, with a material sponsor-data blocker |
| CrewClock | 8 planning / 3 compliance | 9 | 10 | 9 | 8 | **FINAL FIVE** |
| PaveWindow | 9 planning / 4 go-no-go | 8 | 9 | 8 | 9 | **FINAL FIVE** |
| PlantReserve | 6 | 7 | 9 | 9 | 10 | **FINAL FIVE** |
| SaltWise | 5 | 5 | 10 | 9 | 10 | KILL — MDSS/RWIS already perform the core recommendation loop. |
| DairyCool | 4 | 6 | 9 | 9 | 4 | KILL — barn THI and animal telemetry dominate. |
| Rail Heat-Plan Audit | 3 | 6 | 8 | 8 | 6 | KILL — rail temperature/neutral temperature and qualified authority dominate. |
| Cold-Chain Dwell Control | 3 | 6 | 9 | 9 | 5 | KILL — product/reefer sensors dominate and task data are private. |

The “planning / compliance” split is intentional. FortyGuard may prioritize where to investigate; it does not become the legal or engineering measurement used for a final safety/quality decision.

## Phase 15: five serious candidates

### 1. NightWatch Grid

**ONE SENTENCE**
We are building this for distribution system operators to stop neighborhood transformers from failing during sustained heat.

**MONEY / OPERATIONS PROOF**
SCE directly reported installing **492 new transformers in eight days**, repairing 300 wire sections, deploying 226 crews, and seeing about 295,000 temporary customer outages during its 2022 heat wave. High overnight temperatures prevented equipment cooling. ORNL separately cites 2,000 California distribution transformers failing during a 2006 heat wave and a research finding that a 7°C transformer-hotspot increase can double the aging acceleration factor. These are operator reports/research, not our conversion.

**SOURCE**
[Southern California Edison](https://energized.edison.com/stories/powering-through-an-unprecedented-heat-wave); [DOE/ORNL](https://www.energy.gov/oe/articles/oak-ridge-national-laboratory-response-grid-rfi).

**WHAT THEY DO TODAY**
Utilities pre-cool transformers, use fans/water where available, reduce voltage, transfer or shed load, invoke demand response, patrol/infrared-scan feeders, stage mobile generators and crews, and replace failed equipment.

**WHAT IT COSTS**
Transformer replacement and accelerated aging; crew/contractor overtime; lost reliability; customer outages; emergency generation; and scarce replacement inventory with DOE-reported 12–30 month lead times in 2023.

**PERSON / AUTHORITY / SOFTWARE / KPI**
The Distribution System Operator/Dispatcher monitors and controls distribution equipment, prepares switching orders, routes current around failures, estimates loads, and coordinates field workers ([O*NET](https://www.onetonline.org/link/details/51-8012.00)). They work through ADMS/SCADA, outage management, GIS, EAM/APM and workforce systems. KPIs: overload margin, customers interrupted, outage duration, emergency replacements, thermal-aging budget, and planned actions completed before peak. Any voltage reduction, switching, DER dispatch, or work order stays inside approved utility procedures and human control.

**AGENT JOB**
1. Watch FortyGuard persistence/time-of-peak across circuit or network geometry plus approved load forecasts and transformer/feeder condition.
2. Rank only assets where local persistence materially changes the baseline risk.
3. Pull asset age/condition, contingency topology, crew, mobile generation, DER/DR and maintenance constraints.
4. Ask a deterministic transformer/loading model to test alternatives: no action, pre-cooling, load relief/transfer, demand response, mobile generation, inspection, or crew staging.
5. Produce an evidence packet with provenance and a reversible recommendation; request operator approval.
6. After action, verify projected loading margin and completion state; replan or escalate if margin remains below the utility threshold.

**WHY FORTYGUARD**
Millions of distribution assets lack winding sensors. Portfolio-scale 60–100 m thermal differences, peak timing, and persistence—especially failure to cool overnight—can identify which circuits deserve expensive telemetry queries, patrols, or load-relief planning first.

**WHY NOT WEATHER API**
A city forecast cannot rank adjacent paved/built and greener circuits or show sustained local nighttime heat; it still remains a baseline input.

**WHY NOT A DASHBOARD**
A dashboard stops at risk; the job is to investigate topology/assets/resources, construct allowed options, seek authority, and verify margin.

**WHY NOT AN OPTIMIZER ALONE**
The power-flow/thermal calculation should be deterministic, but an agent must select evidence, reconcile multiple systems, explain uncertainty, choose when deeper investigation is worth it, and route approval.

**EXISTING SOFTWARE**
GE GridBeats/APM and ADMS, Siemens Electrification X, Hitachi Energy APM/TXpert/Lumada, Schneider Electric/ArcFM/EcoStruxure, Oracle Utilities, Esri utility GIS, and transformer-monitoring vendors. Incumbent threat is high; the wedge is the **weather-to-approved-action evidence loop for uninstrumented assets**, not another APM screen.

**BUYING SIGNAL**
Utilities already buy APM, sensors, load-relief equipment, mobile generation, demand response, and grid hardening. Con Edison regulatory plans fund heat/contingency programs; SCE mobilized 226 crews and hundreds of replacement assets.

**REAL DEMO INPUT**
SCE public DRPEP circuit/substation/capacity layers or Con Edison public hosting-capacity REST data; cached-live Los Angeles or New York FortyGuard responses (New York heatmap was zero-cell and must visibly fail over to “insufficient sponsor evidence”); public load proxies; explicitly labeled scenario asset age/load/work orders. The strongest executable geography is **SCE + cached Los Angeles**, not New York.

**HERO METRIC**
`high-risk circuits with an approved load-relief or field-action plan before peak / high-risk circuits detected`. Secondary deterministic metric: minimum projected post-action overload margin. Do not claim “failures avoided” in the demo.

**WOW MOMENT**
An orange circuit keeps glowing after sunset; the agent opens its load/age/contingency evidence, rejects two unsafe switching options, assembles DR + mobile-generation + crew staging, the operator approves, and the circuit changes from “uncovered” to “plan verified” while the minimum overload margin crosses the approved threshold.

**EXPANSION**
Transformer replacement prioritization, storm/heat mutual-assistance staging, demand-response targeting, substation cooling, non-wires alternatives, grid-capacity planning, and regulator-ready resilience evidence.

**BIGGEST WEAKNESS**
True transformer risk depends on winding hotspot, loading, wind/cooling and condition; FortyGuard is a screening signal, and public demo data omit the very telemetry and topology that authorize action.

### 2. FreezeLine

**ONE SENTENCE**
We are building this for gas field operations supervisors to stop high-volume wells and gathering equipment from freezing before a winter emergency.

**MONEY / OPERATIONS PROOF**
During February 8–17, 2021, Texas gas production fell **more than 10 Bcf/day**, mostly from freeze-offs; monthly Texas output was down a record 4.3 Bcf/day (15%). Henry Hub reached $23.86/MMBtu. FERC/NERC reports ERCOT ordered 20,000 MW of rolling blackouts and 43.3% of gas-production declines were caused by freezing/weather. All are directly reported agency metrics.

**SOURCE**
[EIA](https://www.eia.gov/todayinenergy/detail.php?id=47896); [FERC/NERC Uri report summary](https://www.ferc.gov/news-events/news/final-report-february-2021-freeze-underscores-winterization-recommendations).

**WHAT THEY DO TODAY**
Producers ensure heat trace/heating works, inject methanol, increase flow, stage field personnel, pre-arrange snow/ice removal and road treatment; pipelines monitor forecasts, staff compressor stations, increase line pack, ready storage and issue critical notices. Texas critical facilities must implement facility-specific weather measures and attest readiness.

**WHAT IT COSTS**
Lost production and sales; commodity-price exposure; power-plant fuel shortages; emergency labor/material; forced-stoppage reporting; reliability penalties/oversight; and administrative fines that Texas says can reach $1M.

**PERSON / AUTHORITY / SOFTWARE / KPI**
A Field Operations Supervisor/Roustabout Field Supervisor assigns crews, inspects sites, enforces safety, coordinates maintenance, and records operations ([O*NET](https://www.onetonline.org/link/details/47-1011.00)). Software includes SCADA, production surveillance, EAM/CMMS, GIS, field-service/work management, weather services, and RRC's WE PREP portal. KPIs: Bcf/day deliverability, critical facilities readiness-complete, forced stoppages, work orders overdue, and staffed/heated high-volume sites.

**AGENT JOB**
Watch sub-freezing persistence; intersect with public wells/production and private criticality/readiness; inspect high-volume sites for heat-trace, methanol, backup power, road access and staffing evidence; prioritize a feasible crew/material route; request supervisor approval; verify work-order completion and readiness attestation; replan when access or inventory fails.

**WHY FORTYGUARD**
Hundreds of remote sites can cross and remain below thresholds at different times; spatial persistence and portfolio screening determine which assets merit detailed SCADA/work-order investigation first.

**WHY NOT WEATHER API**
County/city forecasts do not rank site-level persistence across a dispersed field, but FortyGuard must first prove reliable cold-event coverage in that basin.

**WHY NOT A DASHBOARD**
The bottleneck is closing missing evidence and sequencing staff, methanol, heat-trace repair, backup power and road access before the deadline—not seeing a freeze map.

**WHY NOT AN OPTIMIZER ALONE**
Routing is one subproblem; the agent must interpret heterogeneous readiness documents, decide which sites need deeper inspection, handle missing/conflicting status, create auditable work packages, and replan.

**EXISTING SOFTWARE**
IBM Maximo, SAP EAM, ServiceNow, P2/Quorum upstream software, Weatherford/SLB production systems, SCADA historians, field-service products, bespoke weatherization checklists, and regulator portals. The wedge is cross-system evidence closure against a weather deadline.

**BUYING SIGNAL**
Texas made weatherization, readiness attestation, inspections and outage reporting mandatory for mapped critical facilities; operators already spend on heat trace, methanol, backup power, staffing and winter road access.

**REAL DEMO INPUT**
RRC public well/pipeline GIS and production records plus employer-policy fixtures. The local DFW and Houston FortyGuard cache returned **zero cells**, and there is no cached Texas cold event. A demo can show the agent refusing to invent sponsor evidence, but it cannot yet show the intended thermal map.

**HERO METRIC**
`share of high-volume critical facilities with all required preparedness evidence completed before the freeze deadline`. Do not call that Bcf/day “saved.”

**WOW MOMENT**
Thousands of wells appear, the agent narrows to the few high-volume sites with the longest under-threshold persistence and missing heat-trace/backup-power evidence, builds a constrained crew plan, then verifies every critical gap closed—while explicitly flagging the no-data basin instead of hallucinating confidence.

**EXPANSION**
Pipeline/compressor readiness, gas-electric coordination, regulator attestation audit, spare-parts positioning, blackstart fuel assurance, and summer heat preparation.

**BIGGEST WEAKNESS**
The exact sponsor evidence required for the demo does not exist in the approved cache; the theoretical FortyGuard fit is strong but empirically unproven in the target geography and cold regime.

### 3. CrewClock

**ONE SENTENCE**
We are building this for construction superintendents to turn the company's heat policy into a workable daily crew plan before the shift starts.

**MONEY / OPERATIONS PROOF**
OSHA cites **39,450** U.S. work-related heat injuries/illnesses with days away from work in 2011–2022. Its proposed-rule model estimates **$7.8B annual compliance cost** and **$9.179B annualized benefits** across all covered industries. These are agency statistics/estimates, not construction-only observed dollars.

**SOURCE**
[OSHA proposed rule and economic analysis](https://www.osha.gov/laws-regs/federalregister/2024-08-30).

**WHAT THEY DO TODAY**
Superintendents shift work to cooler hours, shorten unacclimatized shifts, add/lengthen breaks, rotate jobs, reduce workload, provide shade/cooling/water, and maintain emergency plans.

**WHAT IT COSTS**
Lost productive hours, reactive stoppage, overtime/resequence, paid rest and cooling resources, supervision/admin time, schedule delay, injuries/illness and compliance exposure.

**PERSON / AUTHORITY / SOFTWARE / KPI**
Construction Superintendent is an O*NET-supported title with project scheduling, labor dispatch, budget, deadline, quality and compliance responsibility. Software: Procore, Autodesk Construction Cloud, Primavera P6, HCSS, payroll/timekeeping, safety systems, Perry Weather/Kestrel/onsite WBGT. KPIs: planned vs actual crew-hours, required protections completed, task/crew constraints met, rework, overtime, and schedule variance.

**AGENT JOB**
Read employer policy and task plan; rank job zones/windows using FortyGuard; combine onsite WBGT when available, worker acclimatization, workload/PPE, competencies, equipment, dependencies, deadlines and break/cooling capacity; generate alternatives; have a deterministic scheduler validate them; request superintendent approval; at shift start require onsite measurement; verify breaks/tasks and replan if conditions or progress change.

**WHY FORTYGUARD**
Multiple roofs, yards, paved zones and work fronts in one city can have different thermal timing/persistence. FortyGuard helps decide where to spend scarce onsite measurement and which tasks/sites to examine first.

**WHY NOT WEATHER API**
A city heat index cannot distinguish work fronts or surface/radiant context; however a proper onsite WBGT remains the controlling measurement.

**WHY NOT A DASHBOARD**
An alert does not reconcile worker acclimatization, task dependencies, equipment, certifications, break capacity and deadlines into an executable plan.

**WHY NOT AN OPTIMIZER ALONE**
The solver should schedule, but an agent must parse policy and daily-plan changes, acquire missing evidence, explain tradeoffs, request authority, monitor execution and replan.

**EXISTING SOFTWARE**
Procore/Autodesk/Oracle Primavera/HCSS for projects; Perry Weather, DTN, Kestrel and OSHA-NIOSH tools for heat; EHS platforms for policy/compliance. The wedge is the closed loop from **site evidence → daily construction schedule → onsite verification**, not another heat alert.

**BUYING SIGNAL**
Employers already fund EHS programs, shade/water/cooling, weather monitoring, scheduling software and supervisors; OSHA modeled $7.8B annual compliance cost if its proposed federal rule were adopted, and five states already had heat rules when OSHA published the proposal.

**REAL DEMO INPUT**
Public Chicago/Phoenix/LA building permits or construction projects; cached Phoenix/LA FortyGuard; public OSHA policy; clearly labeled scenario crew/task/PPE/acclimatization data. No fake customer roster.

**HERO METRIC**
`planned crew-hours assigned within employer-approved heat controls while all task/deadline constraints remain satisfied`; show protected breaks separately. Never label tile temperature as WBGT or claim injuries avoided.

**WOW MOMENT**
The baseline Gantt strands a roofing crew at the hottest work front and breaks a concrete dependency. The agent moves high-exertion work earlier, shifts a trained crew to an indoor prerequisite during peak, preserves the pour and required breaks, and the timeline turns constraint-valid after onsite verification.

**EXPANSION**
Daily plan-of-day agents, multi-project labor balancing, heat-policy evidence, overtime reduction, subcontractor coordination, material windows, and weather-aware look-ahead planning.

**BIGGEST WEAKNESS**
FortyGuard tile data cannot calculate effective WBGT or individual risk; without employer policy and onsite measurements, the product degenerates into unsafe schedule theater.

### 4. PaveWindow

**ONE SENTENCE**
We are building this for paving superintendents to stop crews and material arriving when the road surface is outside the job's placement rules.

**MONEY / OPERATIONS PROOF**
FHWA's example HMA rules prohibit placement on wet/below-minimum surfaces and set **5°C, 8°C, or 10°C minimums by lift thickness**, using three local readings. FHWA recommends evening/night concrete paving above 32°C to reduce early-age damage and user cost. The strongest honest metric is compliant production time; no national dollar loss was found.

**SOURCE**
[FHWA HMA review](https://www.fhwa.dot.gov/construction/reviews/revhma01.cfm); [FHWA HIPERPAV](https://www.fhwa.dot.gov/publications/research/infrastructure/pavements/pccp/04122/05.cfm).

**WHAT THEY DO TODAY**
Check pavement/mix temperature and moisture, reschedule, alter lift/mix or cooling/heating/curing plan, coordinate plant/trucks/closures/inspectors, or stop work.

**WHAT IT COSTS**
Idle crews, plant and trucks; wasted closure windows; overtime/remobilization; rejected or damaged material; early-age distress/rework; traffic user cost; delayed project throughput.

**PERSON / AUTHORITY / SOFTWARE / KPI**
Paving/Construction Superintendent or DOT Construction Manager coordinates schedule, labor, supplier, inspection and acceptance. Software: HCSS/B2W/Trimble/Primavera, DOT construction-management systems, HIPERPAV, RWIS/weather, plant/telematics. KPI: tons or lane-feet accepted per shift, compliant placement minutes, truck/crew idle, closure used, rejected material, schedule variance.

**AGENT JOB**
Parse project specs and work order; use FortyGuard to screen work surfaces/windows; check mix/lift, plant/truck/crew, closure, inspector and dependency constraints; test start-time/site alternatives; produce a plan; require the specified onsite surface/mix readings before release; verify accepted quantity and actual conditions; replan if the measured surface differs.

**WHY FORTYGUARD**
Surface temperature and localized peak timing are the operational variable, and sparse RWIS/airport weather cannot screen every planned road segment.

**WHY NOT WEATHER API**
Air temperature can differ materially from pavement temperature and cannot choose between shaded/exposed segments; final handheld/embedded readings still control.

**WHY NOT A DASHBOARD**
The job is to move plant, trucks, closure, crew and inspector into a valid window and prove the plan stayed compliant.

**WHY NOT AN OPTIMIZER ALONE**
A solver can schedule known tasks, but the agent must read varied specifications, decide which sites need thermal investigation, handle missing readings, gather approvals and verify field acceptance.

**EXISTING SOFTWARE**
FHWA HIPERPAV, HCSS, B2W, Trimble, Primavera, DOT construction systems, RWIS/MDSS and plant dispatch. The wedge is portfolio screening + spec parsing + field-verification orchestration.

**BUYING SIGNAL**
Agencies already buy RWIS, construction-management systems, sensors, inspection, night paving, cooling/heating and warranty/quality programs. Temperature is contractually inside the acceptance loop.

**REAL DEMO INPUT**
MyLA311 or Portland road-maintenance work orders, public road geometry/specifications, cached LA/Portland FortyGuard (Portland heatmap returned zero cells and must fail closed), plus labeled mix/closure/crew fixtures.

**HERO METRIC**
`spec-compliant paving minutes recovered` and `planned jobs with required onsite readings before release`. No invented dollars.

**WOW MOMENT**
Three road jobs collide with one crew/plant/closure plan. The agent reads each job's different rule, moves one to evening and one to a warmer segment, refuses a third until field readings arrive, and the timeline flips from two invalid starts to a fully verified shift.

**EXPANSION**
Concrete pours, coatings, roofing, striping, sealants, bridge decks and any material with surface/curing windows.

**BIGGEST WEAKNESS**
The pain proof is an operating threshold and quality mechanism, not a broad dollar number; exact go/no-go remains a local reading and inspector decision.

### 5. PlantReserve

**ONE SENTENCE**
We are building this for generation operations managers to find heat-driven plant capacity shortfalls before the grid commits power that will not be available.

**MONEY / OPERATIONS PROOF**
The ORNL-hosted CEC model estimates natural-gas combined-cycle capacity falls **0.3–0.5% per °C above 15°C**. EIA publishes distinct summer/winter capability because temperature affects generator cooling. This is an academic/agency model and plant capabilities, not observed universal loss.

**SOURCE**
[DOE/ORNL synthesis](https://www.energy.gov/oe/articles/oak-ridge-national-laboratory-response-grid-rfi); [EIA capability explanation](https://www.eia.gov/tools/faqs/faq.php?id=104&t=3).

**WHAT THEY DO TODAY**
Apply OEM/plant-specific derate curves, monitor ambient and cooling water, change unit availability/commitment/reserves, run inlet cooling, reschedule maintenance and coordinate with the balancing authority.

**WHAT IT COSTS**
Unavailable MW during peak-price/high-demand hours, fuel/heat-rate penalties, imbalance/replacement power, reserve shortfall and reliability risk.

**PERSON / AUTHORITY / SOFTWARE / KPI**
Generation Operations Manager, plant manager and system operator coordinate unit capability through DCS/SCADA, historian/APM, OEM performance models, EAM and market/commitment software such as PLEXOS/PSO tools. KPIs: available MW, heat rate, forced derate, reserve margin, replacement power and outage/maintenance adherence.

**AGENT JOB**
Screen plant locations and heat persistence; retrieve plant-specific curves, cooling design, current condition/maintenance and market/reserve needs; calculate deterministic derates; investigate only material gaps; generate commitment/maintenance/inlet-cooling alternatives; request operator approval; verify updated declared capability and reserve.

**WHY FORTYGUARD**
Plant portfolios across one balancing area can have different local thermal timing and surface context; high-resolution screening can find which plant curves deserve recalculation first.

**WHY NOT WEATHER API**
Ordinary hourly forecasts may be enough at isolated plants; FortyGuard only wins when spatial differences or sparse observations change portfolio commitment.

**WHY NOT A DASHBOARD**
A heat/derate chart does not retrieve plant constraints, change the commitment plan, document authority and verify reserve restoration.

**WHY NOT AN OPTIMIZER ALONE**
Unit commitment should remain deterministic; the agent acquires/validates heterogeneous capability evidence, selects material investigations, explains provenance and manages approvals/exceptions.

**EXISTING SOFTWARE**
Siemens Omnivise, GE APM, OSI/Emerson/AVEVA historians and plant controls, Energy Exemplar PLEXOS and RTO/ISO commitment systems. Incumbent threat is severe.

**BUYING SIGNAL**
Generators already buy APM/performance monitoring, inlet cooling, production-cost software, weather feeds and capacity testing; EIA explicitly tracks net summer/winter capability.

**REAL DEMO INPUT**
EIA-860 plant/generator points, nameplate and summer/winter capability; cached Phoenix/LA/Atlanta FortyGuard; public EIA grid demand; labeled plant-specific curve/maintenance fixtures.

**HERO METRIC**
`MW of previously overstated availability corrected before commitment` and `post-action reserve above approved requirement`. This is a deterministic scenario calculation, not a claimed historical saving.

**WOW MOMENT**
The grid plan looks green until the agent checks three plants' local peaks and curves; a reserve hole appears, maintenance moves, one inlet-cooling option activates, and verified reserve returns above the line.

**EXPANSION**
Renewable derates, water-temperature constraints, fuel assurance, outage scheduling, market bidding and extreme-weather readiness.

**BIGGEST WEAKNESS**
Plant telemetry, OEM curves and ordinary forecasts are stronger than FortyGuard for most single sites; an incumbent optimizer/APM could add the same field.

## Phase 16: scoring the five

### Official rubric and risk-adjusted rank

| Rank | Candidate | Impact 40% | Technical 35% | Innovation 15% | Communication 10% | Official weighted | Risk-adjusted evidence score |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | NightWatch Grid | 9.6 | 9.2 | 8.7 | 9.6 | **9.33** | **8.74** |
| 2 | CrewClock | 9.2 | 9.1 | 8.6 | 9.8 | **9.14** | **8.49** |
| 3 | FreezeLine | 9.9 | 8.8 | 9.0 | 9.7 | **9.36** | **8.27** |
| 4 | PaveWindow | 8.4 | 8.9 | 8.8 | 9.4 | **8.74** | **8.18** |
| 5 | PlantReserve | 9.4 | 8.7 | 7.5 | 8.9 | **8.82** | **7.96** |

FreezeLine's official-rubric ceiling is highest, but risk adjustment penalizes missing cached sponsor evidence. The ordering is an evidence ranking, not a hidden rubric rewrite.

### Operating and delivery scores

| Candidate | Econ | Existing response | FG dep. | Agent | Buy | Demo data | Clarity | Wow | Dup risk | Incumbent | Build risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| NightWatch Grid | 10 | 10 | 8 | 9 | 10 | 8 | 9 | 10 | 6 | 9 | 7 |
| CrewClock | 9 | 10 | 8 planning / 3 compliance | 9 | 9 | 8 | 10 | 9 | 6 | 8 | 6 |
| FreezeLine | 10 | 10 | 8 theoretical / 3 cached proof | 9 | 10 | 6 | 10 | 10 | 4 | 7 | 9 |
| PaveWindow | 8 | 10 | 9 planning / 4 release | 8 | 9 | 9 | 9 | 9 | 5 | 8 | 5 |
| PlantReserve | 9 | 10 | 6 | 7 | 9 | 10 | 9 | 9 | 7 | 10 | 7 |

## Phase 17: hostile corporate-buyer test

| Candidate | CFO/COO objection | Evidence-backed answer | Residual downgrade |
|---|---|---|---|
| NightWatch Grid | “Why not what I already pay Hitachi/GE/Siemens for?” | Those platforms own asset telemetry/APM. NightWatch must sit above them only where local persistence changes which uninstrumented circuits are investigated and where it closes an approved load-relief/crew plan. If a utility APM already ingests equivalent spatial weather and orchestrates action, there is no wedge. | High integration/OT procurement; no public condition data. |
| CrewClock | “Does this save time, or just force more breaks?” | It does not optimize away protections. It makes the legally/employer-required response executable earlier, reducing reactive resequencing, preserving dependencies and reporting planned/actual crew-hours. Any savings must be measured in a pilot. | Safety liability; cannot use FortyGuard as WBGT. |
| FreezeLine | “We already have SCADA, weather and a winterization checklist.” | SCADA sees instrumented assets; the agent's value is evidence closure across thousands of sites, work orders, staff/material/road access and readiness attestations before a persistence deadline. | No approved cached Texas cold map; confidential criticality/status. |
| PaveWindow | “My foreman owns a thermometer.” | Keep the thermometer. FortyGuard screens portfolio windows early; the agent coordinates plant/trucks/closure/inspection; release still requires specified field readings. | No national dollar number; incumbent construction schedulers can add weather. |
| PlantReserve | “My unit-commitment and OEM models already do this.” | If they already ingest spatially correct forecasts and current curves, they win. The only wedge is cross-portfolio evidence acquisition and exception handling before commitment. | Often a feature, not a company; FG differentiation weakest. |

## Phase 18: hostile hackathon-judge test

| Candidate | Central FortyGuard? | Real agent? | Honest metric/data? | Memorable stage transformation? | Verdict |
|---|---|---|---|---|---|
| NightWatch Grid | Yes for local persistence screening; not for winding temperature. | Yes: investigate, model alternatives, seek operator approval, verify margin. | Yes if metric is plan coverage/margin, not failures avoided; SCE map + cached LA + labeled telemetry fixtures. | Strong: circuit, evidence, rejected options, approved relief, verified margin. | **PASS WITH BOUNDARY** |
| FreezeLine | Conceptually yes; empirically absent in approved cache. | Strongest workflow: evidence audit + field-resource replanning. | Pain/data are real; sponsor map is not. | Extremely strong if cold coverage exists; currently the most honest demo may be a fail-closed no-data state. | **PASS BUSINESS / FAIL CURRENT SPONSOR DEMO** |
| CrewClock | Yes for site ranking; no for compliance trigger. | Yes when policy, roster, dependencies, breaks and replan are all visible. | Public sites + cached heat; worker plan is a labeled fixture. Metric is constraint-valid hours. | Strong Gantt/map transformation. | **PASS WITH ONSITE-VERIFY GATE** |
| PaveWindow | Best direct surface relationship. | Yes, though narrower than top three. | Public jobs/specs + cached heat; field readings remain fixture/verification. | Strong multi-job timeline. | **PASS; MONEY PROOF WEAKER** |
| PlantReserve | Moderate; ordinary forecast/telemetry may suffice. | Agent + deterministic model is credible. | EIA assets/capabilities are real; curves/commitment are fixtures. | Strong reserve-hole reveal. | **HOLD; SPONSOR DEPENDENCE BORDERLINE** |

## Phase 19: three money-backed finalists

### Finalist 1 — NightWatch Grid

- **One-liner:** We are building this for distribution system operators to stop neighborhood transformers from failing during sustained heat.
- **Pain number:** 492 transformers installed in eight days of an SCE heat wave; about 295,000 temporary outages over nine days (operator report).
- **Source:** [Southern California Edison](https://energized.edison.com/stories/powering-through-an-unprecedented-heat-wave).
- **Person:** Distribution System Operator / Dispatcher.
- **Current response:** pre-cooling, voltage/load relief, DR, patrols, mobile generation, crew staging and replacement.
- **Agent loop:** detect persistent local heat → inspect load/asset/topology/resources → evaluate deterministic relief alternatives → request operator approval → verify margin and work state → replan/escalate.
- **FortyGuard advantage:** ranks uninstrumented circuit geographies by local peak and overnight persistence before expensive investigation.
- **Business outcome:** fewer uncovered high-risk circuits, earlier load-relief decisions, better crew/mobile-resource readiness, and protected asset life/reliability.
- **Hero metric:** high-risk circuits with an approved action plan before peak; minimum projected post-action overload margin.
- **Demo arc:** hot circuit stays orange overnight → agent opens evidence and rejects invalid switches → operator approves DR/mobile/crew plan → margin crosses threshold and plan coverage reaches 100%.
- **Existing competitors:** Hitachi APM/TXpert/Lumada, GE GridBeats/ADMS, Siemens Electrification X, Schneider/Oracle/Esri and sensor vendors.
- **Unique wedge:** persistent hyperlocal heat as a selective trigger for a cross-system, operator-approved, verified action packet—not a condition-monitoring dashboard.
- **Biggest weakness:** operational truth is private loading/topology/winding condition; a well-integrated APM incumbent can absorb the wedge.

### Finalist 2 — CrewClock

- **One-liner:** We are building this for construction superintendents to turn the company's heat policy into a workable daily crew plan before the shift starts.
- **Pain number:** 39,450 days-away heat cases in 2011–2022; OSHA agency model: $7.8B annual compliance cost and $9.179B benefits across all covered industries.
- **Source:** [OSHA proposed rule](https://www.osha.gov/laws-regs/federalregister/2024-08-30).
- **Person:** Construction Superintendent.
- **Current response:** cooler-time work, shorter shifts, work/rest, rotation, lower exertion, shade/cooling, acclimatization and emergency plans.
- **Agent loop:** read policy/site/task/worker constraints → rank work fronts → generate solver-validated schedule → approve → require onsite WBGT → monitor progress/conditions → replan.
- **FortyGuard advantage:** ranks site/work-front thermal timing so onsite measurement and schedule changes go to the right place first.
- **Business outcome:** fewer reactive stoppages/resequences, protected schedule dependencies, auditable policy execution and measurable planned/actual crew-hours.
- **Hero metric:** crew-hours placed inside employer-approved controls while deadlines, qualifications and required breaks remain satisfied.
- **Demo arc:** heat breaks the baseline Gantt → agent moves high-exertion work and crews while preserving the pour/deadline → onsite check verifies → schedule turns valid.
- **Existing competitors:** Procore, Autodesk, Primavera, HCSS, Perry Weather, DTN, Kestrel, EHS platforms.
- **Unique wedge:** turns a heat policy and site evidence into a constraint-valid construction plan with field verification.
- **Biggest weakness:** it must never imply that FortyGuard equals WBGT or certifies safety.

### Finalist 3 — FreezeLine

- **One-liner:** We are building this for gas field operations supervisors to stop high-volume wells and gathering equipment from freezing before a winter emergency.
- **Pain number:** Texas production fell >10 Bcf/day during Feb. 8–17, 2021, mostly due to freeze-offs.
- **Source:** [U.S. EIA](https://www.eia.gov/todayinenergy/detail.php?id=47896).
- **Person:** Gas Field Operations Supervisor.
- **Current response:** heat trace/heating, methanol, higher flow, staff/road prep, compressor staffing, line-pack/storage changes, readiness attestation.
- **Agent loop:** detect under-threshold persistence → join criticality/volume/readiness → close missing evidence → optimize staff/material/access route → approve → verify work/attestation → replan.
- **FortyGuard advantage:** site-level under-threshold persistence can rank a dispersed portfolio better than county forecasts—if coverage is proven.
- **Business outcome:** more high-volume critical facilities evidence-complete and operationally prepared before the freeze deadline.
- **Hero metric:** percent of high-volume critical facilities with all preparedness requirements complete before deadline.
- **Demo arc:** thousands of wells collapse to a short auditable intervention list → missing heat trace/power/access appears → crews/material route → verified readiness.
- **Existing competitors:** Maximo/SAP/ServiceNow, Quorum/P2, SLB/Weatherford, SCADA/historians, field-service and bespoke winterization tools.
- **Unique wedge:** combines thermal persistence, public asset/volume data, readiness evidence, field resources and regulator-facing verification.
- **Biggest weakness:** approved DFW/Houston cache has zero heatmap cells and no cold event, so the intended FortyGuard demo cannot currently be made honestly.

## Phase 20: explicit comparison with the prior three

| Concept | Proven money/operations | Existing temp response | FG necessity | Agent necessity | Recurring buyer | Current status |
|---|---|---|---|---|---|---|
| NightWatch Grid | Replacement, outage, overtime, aging, load margin; 492 transformers/8 days | Direct and extensive | 8 as portfolio screen | 9 | Utility distribution operations | **NEW LEADER** |
| CrewClock | OSHA cases and economy-wide compliance/benefit model; schedule/overtime hours | Direct and policy-driven | 8 planning / 3 compliance | 9 | Construction superintendent/EHS | **TOP THREE** |
| FreezeLine | >10 Bcf/day production decline, extreme prices, grid fuel loss, fines | Direct and regulated | 8 theoretical / 3 cached proof | 9 | Gas field operations | **TOP THREE, DEMO BLOCKED** |
| ShiftShield | No organization-level temperature-routing loss or established heat-minute KPI | Worker heat response exists; route resequencing not verified | 7 visually, weaker economically | 7, largely VRP | Delivery operations | **KILLED** |
| CourseCorrect | No recurring loss/buyer spend; participant-minutes are a demo derivation | Heat contingency exists; route authority is early/episodic | 8 visually | 7 | Race director, episodic | **KILLED** |
| Recess Relay | No balance-sheet/capacity KPI or buying signal verified | Schedules/locations do change | 8 visually | 6 | School administrator, weak procurement | **KILLED** |

Why all three prior concepts die:

- **ShiftShield:** its strongest number (44% fewer scenario minutes in hottest cells) is our own scenario arithmetic, not a reported delivery cost. Delivery firms already optimize service/travel and apply heat programs, but no source showed hyperlocal temperature is already in the route-order decision. An incumbent can add a weather cost.
- **CourseCorrect:** the stage transformation remains excellent, but race routes/closures are often fixed before short-horizon thermal evidence; the market is episodic; the hero metric does not map to a buyer's recognized dollar, capacity or SLA.
- **Recess Relay:** the within-campus contrast explains FortyGuard well, but the evidence is public-health relevance rather than an operating balance-sheet pain. The current demo transfers city evidence onto a synthetic campus and has no established software/buying program.

## Decision

`CURRENT_EVIDENCE_LEADER = NightWatch Grid`
`FINAL_MVP_SELECTED = NO`

NightWatch leads because it is the only candidate with a direct operator-reported heat failure event, a recognizable recurring control-room user, documented actions that visibly change operations, strong incumbent/buying evidence, public distribution-grid geography, and usable cached FortyGuard evidence in the same broad geography (Los Angeles).

FreezeLine is the best business case and most agentic workflow. It should overtake NightWatch only after a **zero-credit** path to existing cached cold-event sponsor data is found or the human team later authorizes a live call. CrewClock is the best ten-second pitch and safest buildable top-three fallback if the demo is explicit that onsite WBGT controls.

## Critical next evidence—not authorization to select an MVP

1. NightWatch: obtain a realistic, non-sensitive feeder/transformer telemetry fixture reviewed by a utility practitioner; prove that cached LA tile persistence changes action ranking relative to ordinary forecasts.
2. CrewClock: encode one real employer/state heat policy and verify a schedule with onsite-WBGT gate semantics; do not invent a universal work/rest rule.
3. FreezeLine: locate an already-cached FortyGuard cold event over an RRC-covered field. Current cache audit says none exists; no live request is authorized.
4. PaveWindow: attach one real DOT project/specification and quantify historical compliant-window loss without converting to fake dollars.
5. PlantReserve: test whether NOAA/NWS plus plant telemetry makes FortyGuard redundant. Kill it if spatial differences do not change the commitment decision.

## Run accounting

```text
MONEY_FIRST_RESEARCH = COMPLETE
LIVE_FORTYGUARD_CALLS = 0
FORTYGUARD_CREDITS_REMAINING = 1795500

INDUSTRIES_RESEARCHED = 34
PRIMARY_SOURCES_REVIEWED = 43
SECONDARY_SOURCES_REVIEWED = 7
MEASURABLE_PAIN_POINTS_FOUND = 26
TEMPERATURE_DRIVEN_WORKFLOWS_VERIFIED = 31
EXISTING_PRODUCTS_ANALYZED = 21
PUBLIC_DATASETS_FOUND = 13

FINALIST_1 = NightWatch Grid
WE_ARE_BUILDING_THIS_FOR = distribution system operators
TO_SOLVE = neighborhood transformers failing during sustained heat
PAIN_NUMBER = 492 transformers installed in eight days; about 295,000 temporary outages over nine days
PAIN_SOURCE = Southern California Edison, 2022 operator report
WHAT_THEY_DO_TODAY = Pre-cool, reduce voltage or load, transfer demand, dispatch DR/mobile generation, patrol equipment, stage crews, and replace failures.
ECONOMIC_ALIGNMENT = 10
FORTYGUARD_DEPENDENCE = 8
AGENTIC_NECESSITY = 9
BUYING_SIGNAL = 10
TEN_SECOND_CLARITY = 9
DEMO_WOW = 10
HERO_METRIC = high-risk circuits with an approved action plan before peak; minimum projected post-action overload margin
RUBRIC_SCORE = 9.33
BIGGEST_WEAKNESS = Private loading/topology/winding condition—not FortyGuard—controls the real decision, and APM incumbents can absorb the wedge.

FINALIST_2 = CrewClock
WE_ARE_BUILDING_THIS_FOR = construction superintendents
TO_SOLVE = turning the company heat policy into a workable daily crew plan before the shift
PAIN_NUMBER = 39,450 days-away heat cases in 2011–2022; OSHA model estimates $7.8B annual compliance cost and $9.179B annualized benefits across covered industries
PAIN_SOURCE = OSHA proposed rule and preliminary economic analysis, 2024
WHAT_THEY_DO_TODAY = Shift work, add breaks, rotate jobs, reduce workload, cool workers, acclimatize staff, and maintain emergency plans.
ECONOMIC_ALIGNMENT = 9
FORTYGUARD_DEPENDENCE = 8 for planning; 3 for compliance
AGENTIC_NECESSITY = 9
BUYING_SIGNAL = 9
TEN_SECOND_CLARITY = 10
DEMO_WOW = 9
HERO_METRIC = crew-hours inside employer-approved controls with qualifications, dependencies, deadlines, and required breaks satisfied
RUBRIC_SCORE = 9.14
BIGGEST_WEAKNESS = FortyGuard tile data is not WBGT and cannot certify worker safety.

FINALIST_3 = FreezeLine
WE_ARE_BUILDING_THIS_FOR = gas field operations supervisors
TO_SOLVE = high-volume wells and gathering equipment freezing before a winter emergency
PAIN_NUMBER = Texas gas production fell more than 10 Bcf/day during February 8–17, 2021, mostly due to freeze-offs
PAIN_SOURCE = U.S. Energy Information Administration
WHAT_THEY_DO_TODAY = Check heat trace/heating, inject methanol, increase flow, stage crews, prepare roads, staff compressors, adjust line pack/storage, and attest readiness.
ECONOMIC_ALIGNMENT = 10
FORTYGUARD_DEPENDENCE = 8 theoretical; 3 with approved cache
AGENTIC_NECESSITY = 9
BUYING_SIGNAL = 10
TEN_SECOND_CLARITY = 10
DEMO_WOW = 10
HERO_METRIC = percent of high-volume critical facilities with all preparedness evidence complete before deadline
RUBRIC_SCORE = 9.36 ceiling; 8.27 risk-adjusted
BIGGEST_WEAKNESS = The approved DFW/Houston cache returned zero heatmap cells and contains no cold event, so the sponsor demo is currently blocked.

SHIFTSHIELD_STATUS = KILLED
COURSECORRECT_STATUS = KILLED
RECESS_RELAY_STATUS = KILLED

CURRENT_EVIDENCE_LEADER = NightWatch Grid
FINAL_MVP_SELECTED = NO

BEST_BUSINESS_CASE = FreezeLine converts a >10 Bcf/day freeze-off failure and mandatory readiness work into an auditable field-operations loop.
BEST_10_SECOND_PITCH = CrewClock turns the construction company's heat policy into tomorrow's workable crew plan.
BEST_AGENTIC_WORKFLOW = FreezeLine investigates missing readiness evidence, sequences scarce people/material/access, verifies completion, and replans failures.
BEST_FORTYGUARD_DEPENDENCE = PaveWindow uses surface-specific timing to screen road jobs, while retaining required onsite readings for release.
BEST_STAGE_MOMENT = NightWatch rejects unsafe grid options, assembles approved relief and crew actions, then visibly restores overload margin before peak.

MOST_SURPRISING_REAL_COST = SCE installed 492 transformers in eight days because sustained heat prevented overnight cooling.
BIGGEST_PREVIOUS_ASSUMPTION_KILLED = A visually compelling heat-exposure metric is not a buyer KPI; all three prior finalists lacked proof that organizations already make the proposed temperature decision.
MOST_DANGEROUS_REMAINING_QUESTION = Does FortyGuard materially change a real operator's action ranking after authoritative telemetry and ordinary forecasts are already present?

TESTS = PASS — typecheck, ESLint, 2 Vitest tests, and 13 Pytest tests
SECRET_SCAN = PASS
COMMIT = reported in final handoff
USER_ACTION_REQUIRED = none
```
