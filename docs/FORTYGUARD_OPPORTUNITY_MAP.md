# FortyGuard opportunity map

## Capability → decision → actor → cost of a bad decision → agent job

| Verified capability | Decision it unlocks | Existing decision-maker | Bad-decision consequence | Useful autonomous work |
|---|---|---|---|---|
| Heatmap | Which block/site/route should be used first? | Field, school, event, fleet and city operator | People or work are concentrated in a hotter microzone | Compare candidate locations, score constraints, propose a reallocation, verify exposure proxy |
| Environmental parameters | When do local thermal/environmental conditions best fit a task? | Operations or facilities manager | Delays, discomfort, energy waste or avoidable exposure | Retrieve hourly evidence, match tasks to windows, preserve deadlines, re-check result |
| Exceedance | Which places spend meaningful time above a chosen planning threshold? | Portfolio/facilities/city manager | One-time peaks distract from persistent operational burden | Rank sustained exceptions, investigate alternatives, generate an intervention queue |
| Persistence | Is the problem chronic enough to justify changing the plan? | School, city, property, event or utility operator | Resources chase noise instead of recurring hotspots | Separate chronic from transient sites and choose durable vs temporary action |
| Peak timing | What can move before or after the worst local window? | Delivery, outdoor work, venue and campus operator | Movable activity remains in the worst part of the day | Re-sequence tasks and verify constraints/derived minutes |
| Spatial differences | Which nearby alternative is materially cooler? | Route, venue, campus, fleet or emergency planner | Citywide weather treats distinct blocks as identical | Search alternatives and justify why the recommended location changes |
| Satellite segmentation | What physical context may explain a heat pattern? | Facilities, city, campus and property operator | Intervention ignores surface context | Request contextual evidence, distinguish trees/roads/buildings, choose an inspectable intervention hypothesis |
| Asynchronous analysis | How can many sites be investigated without blocking the workflow? | Portfolio operator | Slow/manual lookup prevents timely comparison | Submit bounded work, poll status, handle failure, cache result, continue when evidence arrives |
| Cached-live evidence | Can the decision be demonstrated and audited without a new call? | Demo operator / evaluator | Rehearsal burns credits or mislabels stale data as live | Replay a deterministic trace with source, timestamp, status and assumptions |

## 25 candidates and hard-kill pass

Every one-liner uses the required form. Scores are `visual / clarity / FortyGuard / agentic / impact / duplication / buildability`.

### Survivors (8)

| Candidate | Required one-liner | Why anyone cares | Agent magic | Why FortyGuard | Before → after | Hero metric / wow | Scores |
|---|---|---|---|---|---|---|---|
| **ShiftShield** | We are building this for delivery operations managers to solve drivers spending avoidable time in the hottest blocks. | Thousands of movable stops create a planning problem no driver can solve manually. It affects comfort, continuity and productivity without claiming medical certification. | Observes stop geography, investigates peak timing, re-sequences flexible stops, requests approval, then recomputes hot-zone minutes. | City weather cannot distinguish adjacent paved/green delivery blocks or local peak timing. | Static route order → constraint-valid cooler sequence. | **44% fewer scenario minutes in hottest cells**; route animates away from red cells. | 10/10/9/9/9/3/9 |
| **Recess Relay** | We are building this for school administrators to solve outdoor activities happening in the hottest parts of campus. | Children and staff use yards that can heat unevenly; schedules and spaces are often fixed by habit. | Compares campus zones and periods, swaps movable activities, checks supervision/capacity, requests approval, verifies student-minutes. | Generic weather cannot choose between the asphalt court, field and shaded assembly area. | One timetable/yard → cooler campus allocation. | **student-minutes shifted from hottest zone**; timetable and map flip together. | 9/10/9/8/9/3/8 |
| **CourseCorrect** | We are building this for race organizers to solve participants being routed through avoidable street heat. | A race route and aid plan can concentrate thousands of people on exposed blocks. | Investigates route segments and peak timing, tests detours/wave times, preserves distance/closures, proposes and verifies. | Generic weather cannot compare street-by-street thermal segments along alternatives. | Fixed hot segment → same-distance lower-exposure course. | **participant-minutes avoided**; the route redraws live. | 10/10/9/9/9/3/8 |
| **QueueCool** | We are building this for event organizers to solve long outdoor queues forming in the hottest venue zones. | Entrances and staffing are movable, but organizers lack block-level evidence when the rush arrives. | Predicts queue load from scenario inputs, compares entrances, reallocates lanes/staff, checks access rules, verifies queue-minutes by zone. | Nearby gates with different pavement/shade context can have different local heat profiles. | Default gate plan → balanced cooler entry plan. | **hot-zone queue-minutes avoided**; crowds flow to cooler gates. | 9/10/8/8/8/2/8 |
| **CoolCrew Dispatch** | We are building this for city operations teams to solve flexible outdoor jobs being assigned to the hottest site at the worst time. | Cities already juggle many low-risk movable inspections and maintenance visits. | Investigates sites, reorders eligible work, preserves urgency/skills, requests supervisor approval, verifies an exposure proxy. | Citywide forecasts cannot rank hyperlocal sites or their different peaks. | FIFO work queue → evidence-aware route and schedule. | **crew-minutes moved out of peak cells**; pins reorder visibly. | 9/9/9/9/9/4/9 |
| **Oasis Allocator** | We are building this for emergency heat-response teams to solve mobile cooling resources being placed where they help least. | Limited pop-up shade, water and outreach capacity must be placed before peak demand. | Combines public vulnerability/footfall scenario data with persistence, proposes deployments, checks coverage, awaits approval, verifies coverage. | Generic weather cannot locate persistent micro-hotspots inside a neighborhood. | Equal allocation → evidence-weighted coverage plan. | **people-within-cool-zone proxy**; mobile resources move on a map. | 10/9/10/9/10/4/7 |
| **Venue Turn** | We are building this for sports facility operators to solve practices using the hottest field when cooler fields are available. | Multi-field facilities can swap spaces and times without cancelling the whole program. | Compares fields/times, checks bookings and surface constraints, proposes swaps, verifies participant-minutes. | A single forecast cannot distinguish adjacent turf, court and shaded field conditions. | Cancel/all-go choice → targeted space/time swaps. | **sessions preserved while hot-field minutes fall**. | 9/10/9/8/8/3/9 |
| **DockShift** | We are building this for warehouse operators to solve outdoor loading work clustering on the hottest dock apron. | Yard and dock tasks are often flexible across doors and short windows. | Compares apron zones, sequences appointments/equipment, checks capacity, requests approval and verifies. | Generic weather cannot see heat differences across paved yards and building edges. | First-available dock → thermal-aware slot/door assignment. | **outdoor task-minutes shifted**; trailers re-slot on a thermal yard. | 9/9/8/9/8/3/8 |

### Killed candidates (17)

| Candidate | One-liner | Scores | Kill reason |
|---|---|---|---|
| HeatPing | We are building this for ordinary consumers to solve not knowing when it is hot outside. | 4/10/2/1/5/5/10 | Generic weather; just an alert. |
| AC Whisperer | We are building this for homeowners to solve high cooling bills. | 5/9/3/4/7/5/7 | Smart thermostats + weather solve most of it; FortyGuard not necessary. |
| HotRoof Certifier | We are building this for roofers to solve unsafe roof work. | 7/9/5/6/9/3/7 | Unsupported safety claim; direct roof/WBGT measurements remain authoritative. |
| InsureHeat | We are building this for insurers to solve pricing heat risk. | 6/8/7/5/8/3/4 | Inaccessible claims/actuarial data and weak agent necessity. |
| Pharmacy Forecast | We are building this for clinics to solve heat-linked medicine demand. | 6/8/4/6/8/3/4 | Needs sensitive/proprietary data; medical claim boundary. |
| Asphalt Oracle | We are building this for paving crews to solve choosing a paving window. | 6/7/5/6/7/4/7 | Fails clarity and direct material/substrate measurement dominates. |
| RailGuard | We are building this for rail teams to solve heat-related track risk. | 8/9/4/6/10/3/4 | Ambient/surface context cannot replace rail temperature, RNT and regulated inspection. |
| SolarYield Agent | We are building this for solar operators to solve heat reducing panel output. | 7/8/4/5/7/4/6 | On-panel telemetry and forecast models dominate; agent adds little. |
| Pool Patrol | We are building this for pool managers to solve busy hot days. | 6/9/3/4/5/2/8 | Generic forecast adequate; mostly staffing dashboard. |
| PetWalk | We are building this for dog owners to solve hot pavement walks. | 7/10/5/3/6/5/8 | Direct pavement checks are required; alert/app duplication high. |
| BusStop Ranker | We are building this for cities to solve hot bus stops. | 8/10/9/4/9/5/8 | Strong FortyGuard use but primarily a ranking dashboard, not necessary agent behavior. |
| TreePlanner | We are building this for city planners to solve where to plant shade trees. | 9/9/9/5/9/5/6 | Long-horizon GIS optimization; three-minute agent transformation is weak. |
| ColdChain Sentinel | We are building this for logistics companies to solve spoiled deliveries. | 6/9/3/6/9/4/5 | Vehicle/package sensors dominate ambient thermal maps. |
| CraneWindow | We are building this for construction managers to solve heat-related lift timing. | 7/8/4/6/8/3/5 | Wind and lift engineering dominate; FortyGuard dependence too low. |
| FireWatch | We are building this for emergency teams to solve wildfire detection. | 10/10/4/7/10/5/4 | Fire/weather/satellite products already dominate and repository capability is not fire detection. |
| GardenBuddy | We are building this for gardeners to solve when to water. | 6/10/4/4/4/5/8 | Soil sensors and standard weather solve it; low stakes. |
| FacadeFix | We are building this for property managers to solve facade inspection timing. | 5/7/4/5/5/2/7 | Requires domain explanation and has no compelling transformation. |

## Duplication attack on survivors

Conceptual searches covered heat-routing, worker heat planning, school heat, event heat, cooling-center placement, field-service scheduling, dock scheduling and sports heat tools across Devpost, GitHub and public product pages. None warrants a uniqueness claim.

- **Highest collision:** CoolCrew Dispatch and Oasis Allocator. Heat/work planning and cooling-center maps are established categories; the wedge must be autonomous constraint-aware reallocation plus verification.
- **Moderate collision:** ShiftShield and CourseCorrect. Route optimization and weather routing exist, but block-level thermal evidence + human-approved replanning + a recomputed exposure proxy is a less common combination.
- **Lower collision:** Recess Relay, QueueCool, Venue Turn and DockShift. The recognizable workflow is narrower, but incumbents can add weather; the defensible wedge is within-site spatial differences and actual operational rearrangement.
- Another FortyGuard contestant is most likely to build heat-risk mapping or work alerts. A dynamic spatial allocation demo is less obvious than those defaults.

Relevant comparators: [NWS HeatRisk](https://www.wpc.ncep.noaa.gov/heatrisk/), [OSHA-NIOSH Heat Safety Tool](https://www.cdc.gov/niosh/heat-stress/communication-resources/app.html), [Perry Weather work/rest products](https://perryweather.com/features/heat-stress-and-wbgt-monitoring/work-rest-cycles/), [Google OR-Tools routing](https://developers.google.com/optimization/routing), [NYC cooling center finder](https://finder.nyc.gov/coolingcenters/), [Heat in Climate gallery](https://health-in-climate-ai-hackathon.devpost.com/project-gallery), [NASA SkySense winner](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/).

## Data reality for the top eight

| Candidate | Real public/cached demo data | Clearly labelled synthetic constraints |
|---|---|---|
| ShiftShield | Cached Phoenix/LA/Las Vegas FortyGuard; OpenStreetMap streets; public parcel/road geometry | Stops, service duration, promises, driver shift |
| Recess Relay | Cached FortyGuard; public school/campus geometry and calendars where available | Activity roster, supervision and capacity |
| CourseCorrect | Cached FortyGuard; OpenStreetMap route graph; public race route or road closures | Wave sizes, aid capacity, allowed detours |
| QueueCool | Cached FortyGuard; public venue/entrance geometry | Arrival curve, gate capacity, staff availability |
| CoolCrew Dispatch | Cached FortyGuard; LA 311 or other open work orders | Crew skills, task movability and shift constraints |
| Oasis Allocator | Cached FortyGuard; Census ACS, public cooling centers, OSM | Mobile resource inventory and demand proxy |
| Venue Turn | Cached FortyGuard; public facility geometry/schedules | Participant counts and swap rules |
| DockShift | Cached industrial-area FortyGuard; public parcel/road geometry | Appointments, door compatibility and handling times |

## 25 → 8 rubric scorecard

Weighted score = Impact 40% + Technical Execution 35% + Innovation 15% + Communication 10%.

| Rank | Candidate | Impact | Tech | Innovation | Communication | Weighted | Clarity | Visual | FG | Agent | Dup risk | Build risk |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | ShiftShield | 9.2 | 9.1 | 8.2 | 9.8 | **9.08** | 10 | 10 | 9 | 9 | 3 | 2 |
| 2 | CourseCorrect | 9.0 | 8.8 | 8.6 | 9.8 | **8.99** | 10 | 10 | 9 | 9 | 3 | 3 |
| 3 | Recess Relay | 9.2 | 8.4 | 8.8 | 9.7 | **8.89** | 10 | 9 | 9 | 8 | 3 | 3 |
| 4 | Oasis Allocator | 9.8 | 8.0 | 8.3 | 9.1 | **8.88** | 9 | 10 | 10 | 9 | 4 | 4 |
| 5 | CoolCrew Dispatch | 9.0 | 9.0 | 7.7 | 9.0 | **8.81** | 9 | 9 | 9 | 9 | 4 | 2 |
| 6 | QueueCool | 8.2 | 8.4 | 8.8 | 9.6 | **8.50** | 10 | 9 | 8 | 8 | 2 | 3 |
| 7 | Venue Turn | 8.1 | 8.3 | 8.2 | 9.4 | **8.29** | 10 | 9 | 9 | 8 | 3 | 2 |
| 8 | DockShift | 8.0 | 8.6 | 8.0 | 9.0 | **8.31** | 9 | 9 | 8 | 9 | 3 | 3 |

## Stage test

1. **ShiftShield:** “Every day, delivery managers send drivers through a city that is not one temperature. Watch our agent move flexible stops away from the hottest blocks, preserve every promise, and prove the minutes avoided.” Visual: pins lift from orange cells and snap into a cooler route.
2. **CourseCorrect:** “Every race director draws a course, but the street can be hotter than the forecast. Watch our agent inspect every segment, redraw one avoidable hot stretch, and verify the participant-minutes it removes.” Visual: red route segment dissolves and a green equal-distance segment appears.
3. **Recess Relay:** “Every school has one weather forecast, but not one campus temperature. Watch our agent swap the yard, field and timetable while preserving supervision.” Visual: class blocks and campus heat cells change together.
4. **Oasis Allocator:** “Every city has too few mobile cooling resources for a heat emergency. Watch our agent find persistent hotspots, move the resources and prove how much coverage changes.” Visual: shade/water icons move and coverage halos expand.
5. **CoolCrew Dispatch:** “Every day, city crews inherit a queue that ignores which block gets hottest when. Watch our agent re-order only the movable jobs and verify the new plan.” Visual: numbered work pins reorder across the map.
6. **QueueCool:** “Every event has a front gate—and sometimes that gate is the hottest place to wait. Watch our agent open a cooler entrance and rebalance the lanes without breaking access rules.” Visual: crowd particles split toward a cooler gate.
7. **Venue Turn:** “Every sports complex can have a hot field and a cooler field minutes apart. Watch our agent swap practices instead of cancelling the day.” Visual: schedule tiles trade places over two thermal zones.
8. **DockShift:** “Every warehouse assigns the next truck to the next dock. Watch our agent use local thermal evidence to change the door and time while keeping throughput intact.” Visual: trailers re-slot and the exposure counter falls.

All eight pass the spoken-stage test. Only the top three advance because Oasis Allocator needs more assumptions about need/footfall, and CoolCrew Dispatch has higher incumbent/contestant collision.

