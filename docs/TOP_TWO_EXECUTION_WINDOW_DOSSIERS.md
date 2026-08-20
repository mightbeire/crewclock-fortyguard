# Top two execution-window research dossiers

Research date: 2026-08-20

Status: research candidates, not MVPs

`FINAL_MVP_SELECTED = NO`

## Shared architecture boundary

Both candidates fit the existing provider-neutral agent core in `src/fortyguard_agent/`. Neither requires a new autonomous runtime or an LLM making deterministic safety calculations.

```text
work package + specification + product data + closure/crew constraints
                              |
                              v
                     evidence-orchestration agent
                    /       |         |          \
           cached FortyGuard  NOAA/NWS  field meters  document/rule retrieval
                    \       |         |          /
                              v
                    deterministic rule evaluator
                              |
                      feasible-window generator
                              |
                    deterministic assignment solver
                              |
                     second-pass verification
                              |
                    human approval + audit record
```

Required invariants:

1. An absent or stale required measurement is `UNKNOWN`, never `PASS`.
2. FortyGuard-derived evidence is labelled planning/screening evidence.
3. Direct substrate and product measurements remain authoritative where the specification requires them.
4. Rule calculations and optimization are deterministic, unit-tested tools.
5. The agent cannot approve work; it proposes and explains.
6. Every recommendation records source, timestamp, units, rule version, rejected alternatives and approval state.

---

## Candidate 1: Bridge Steel Coating Window Verifier

### Precise product statement

> We are building this for state/local DOT bridge-painting program managers, resident engineers, and owner coating inspectors to verify preparation, coating-application, and cure execution windows across a portfolio of scheduled bridges, because conditions at an exposed steel surface can invalidate a planned mobilization even when a city forecast looks acceptable.

### Precise user and buyer

- **Daily operator:** owner coating inspector or resident engineer reviewing tomorrow's/tonight's bridge painting plan.
- **Operational counterpart:** contractor superintendent and NACE/AMPP-qualified coating personnel where required by contract.
- **Economic buyer:** DOT bridge maintenance/construction program, bridge-preservation contractor, or inspection-services firm managing multiple simultaneous work packages.
- **Non-buyer:** a one-off painter with one bridge and no swappable work. For that user, a meter and checklist are sufficient.

### Real workflow

1. The contractor submits a look-ahead plan identifying bridge, member/zone, surface-preparation stage, coating system/coat, shift, containment, crew and expected cure interval.
2. The owner inspector identifies the governing contract clause, product data sheet and inspection plan.
3. Before work and periodically during it, the inspector measures air temperature, relative humidity, dew point, steel/surface temperature, delta-T and sometimes wind. FHWA examples require environmental checks before work and every four hours; active UFGS guidance can require continuous one-minute logging during preparation/application/cure. [P63–P67]
4. The contractor/owner considers the current and expected weather for the complete cure period. If limits fail, work is delayed, enclosure/dehumidification may be used if allowed, another stage may be performed, or the crew may be reassigned. [P63, P65]
5. Measurements, surface preparation, product batch, dry-film/wet-film evidence, nonconformance and approval are recorded.

Typical public-rule examples—not universal defaults—include ambient 40/50–100°F, RH <=85%, steel at least 5°F above dew point, and maximum steel temperature around 125–130°F. The governing contract and coating manufacturer always override the example. [P63, P65]

### Evidence for material operational impact

- Moisture/condensation and out-of-range temperature can cause adhesion, cure and corrosion failures; FHWA inspection guidance explicitly requires current and expected weather to be considered. [P63]
- Caltrans maintenance guidance gives an example 51–100°F application range, RH below 75%, and surface at least 5°F above dew point; it identifies surfactant leaching when a primer is applied outside limits. [P66]
- UFGS 09 97 13.27 requires continuous environmental monitoring at steel locations during preparation, application and cure, showing that persistence and audit are real contract requirements rather than invented AI steps. [P67]
- Public contract plans demonstrate multi-bridge painting packages, while public bid records show structural-steel painting items can be materially expensive. [P70, P71]

### Agent loop

#### Observe

Read approved work packages and look-ahead schedules. Minimum fields:

| Field | Status for demo |
|---|---|
| Work-package/bridge ID and geometry | Real from contract/NBI |
| Member/zone and work stage | Real where contract exposes it; otherwise synthetic and labelled |
| Coating system, coat and product | Must be real or from a public product/specification rule pack |
| Planned start and required cure interval | Contract where available; otherwise labelled synthetic |
| Crew, containment and equipment | Usually private; synthetic for demo |
| Lane/traffic/environmental restriction | Public contract where available; otherwise synthetic |
| Deadline/priority | Public completion clause or synthetic |

#### Investigate

- Retrieve exact contract/specification and product rule pack.
- Use cached FortyGuard hourly apparent temperature, RH, precipitation, cloud/solar and heatmap context for portfolio screening.
- Use NOAA/NWS for ordinary forecast, dew point, wind and severe-weather evidence.
- Retrieve latest direct meter readings: air, RH, dew point, steel temperature, delta-T; validate timestamp/calibration metadata when available.
- Check enclosure/dehumidification status and whether the work stage is exposed.
- Ask for the smallest missing field set; do not infer a steel temperature from ambient temperature.

#### Decide

The deterministic evaluator produces clause-level results over preparation, application and cure:

```text
PASS       all required values within rule for full interval
FAIL       at least one authoritative value violates a rule
UNKNOWN    required value absent, stale, unit-ambiguous, or source conflict unresolved
```

The agent decides what to investigate next and whether a failure is potentially mitigable. It does not alter limits.

#### Alternative search

Generate alternatives only from approved work:

- later/earlier shift on the same bridge;
- different member/stage if contract and containment permit;
- another approved bridge package for the same compatible crew/system;
- permitted enclosure/dehumidification mitigation as a separately verified alternative.

#### Constraint check

Use a deterministic constraint model:

- crew certification and availability;
- coating/product/coat compatibility and recoat interval;
- containment/equipment location and mobilization time;
- traffic closure and permit window;
- surface-preparation hold point;
- cure-before-next-coat/reopening requirement;
- contract deadline and priority;
- travel and setup time;
- owner-inspector availability.

Objective: minimize expected lost shift/mobilization and deadline impact subject to hard compliance gates. The objective weights must be explicit and configurable.

#### Verify

Re-run the entire evidence/rule/constraint chain for the proposed alternative. A weather-feasible bridge is not a viable alternative if the wrong product is loaded or the inspector cannot attend. Require an onsite steel-temperature/dew-point reading before final release.

#### Human approval

- Owner coating inspector/resident engineer approves the go/no-go or revised work package.
- Contractor superintendent confirms feasibility and means/methods.
- Ambiguous contract/product conflict goes to the engineer, not an LLM tie-break.

#### Audit

Store:

- contract/product/rule versions and quoted clause identifiers;
- raw source values, units, timestamps and quality flags;
- cached FortyGuard request/response provenance without credentials;
- field-meter ID/calibration/freshness where available;
- rule results for the full interval;
- all alternatives considered and deterministic infeasibility reasons;
- recommendation, confidence scoped to evidence completeness, approver and disposition;
- later field truth and actual outcome for evaluation.

### Deterministic algorithms

1. **Dew-point calculation:** only if the source does not supply it and input accuracy is acceptable; use a documented Magnus-type equation, tested against reference values.
2. **Delta-T:** `steel_surface_temperature - dew_point`; deterministic units and inclusive/exclusive boundaries follow the rule pack.
3. **Persistence:** all required time buckets in preparation/application/cure must pass; interpolate only under an explicit policy.
4. **Freshness:** direct readings expire after a configured interval; forecast runs carry issue timestamps.
5. **Constraint solving:** OR-Tools CP-SAT/min-cost assignment is appropriate for bridge/shift/crew combinations. [P29]
6. **Evidence comparison:** no weighted “AI risk score.” Keep clause-level results and a deterministic completeness score.

### FortyGuard role and necessity

**Role:** portfolio heat/context screen, thermal persistence, solar/cloud/RH/precipitation evidence, and spatial prioritization of field checks.

**What becomes better:** the manager can compare separated bridges before dispatch, detect a likely exposed-surface outlier, search another approved package, and issue targeted field checks with a complete evidence packet.

**What FortyGuard cannot do:** measure steel temperature, surface moisture, wind at containment height, coating temperature, dew-point meter calibration, enclosure conditions or final cure.

**Dependence: 6/10.** Better than a citywide forecast for a distributed portfolio with exposed surfaces, but capped because direct meter readings are the final authority and NWS/DTN can provide broad forecast coverage. A one-site workflow scores 3–4/10.

### Public demo data

| Input | Public source | Use |
|---|---|---|
| Bridge location, ownership, dimensions, condition | National Bridge Inventory [P69] | Real portfolio geometry and asset identity |
| Multi-bridge painting package | Illinois DOT contract plans [P70] | Real package/work context and specification trail |
| Structural-steel painting costs | Caltrans contract-cost records [P71] | Order-of-magnitude impact context; not a universal cost model |
| Environmental rules | FHWA/Caltrans/UFGS [P63–P67] | Versioned deterministic rule packs |
| Environmental profile | Cached FortyGuard + NOAA/NWS | Demo screening and alternative comparison |
| Crew/closure/field readings | Explicitly synthetic fixture unless found in contract | Demonstrate constraint and field-gate behavior without pretending customer data |

**Demo-data quality: 8/10.** Asset, geography, rules and real contracts are strong. Real look-ahead schedules, crew rosters and field meter logs are the missing customer evidence.

### System architecture mapped to existing core

- `registry`: expose read-only tools for work packages, specifications, cached FortyGuard, public weather and field-read fixtures.
- `budget`: continue zero-live-call budget and prevent duplicate provider calls.
- `provenance`: attach source URL/document version, timestamp and cache ID.
- `approval`: create a `change_work_package` or `release_start` approval; no automatic resolution.
- `provider`: LLM may propose investigations and explanations; handler validates every tool call.
- New deterministic modules needed after human selection: `coating_rules.py`, `dewpoint.py`, `window_verifier.py`, `assignment.py`.

### Measurable outputs

Hackathon/evaluation metrics:

- clause-level rule accuracy on fixed fixtures;
- missing-evidence recall (must be 100% for hard gates);
- feasible-alternative precision;
- recommendation reproducibility;
- investigation/tool-call count and latency;
- provenance completeness;
- number of live FortyGuard calls (must remain zero for this pass).

Pilot metrics:

- planned shifts caught as infeasible before mobilization;
- percentage of recommendations confirmed by direct meter readings;
- hours of avoided idle mobilization/closure;
- time from forecast change to approved revised plan;
- condition excursions, nonconformances and coating rework trend.

Do not claim reduced coating failures from a demo. That requires longitudinal pilot data and control for preparation/application quality.

### Adoption path

1. Start as a read-only next-shift review that exports an inspector packet; no automatic schedule writes.
2. Integrate direct meter logs (DeFelsko/Elcometer-style CSV/API) and the owner’s look-ahead spreadsheet.
3. Run retrospective shadow mode for one painting season.
4. Enable approval-routed recommendations only after field-confirmation precision is known.
5. Integrate with Cityworks/Maximo/Primavera rather than replacing the system of record.

### Liability and controls

- False pass can contribute to coating failure; all required field checks are hard gates.
- False fail can waste a closure or mobilization; show exact evidence and permit override with reason.
- Product/specification version errors are dangerous; pin and display versions.
- Forecast uncertainty grows over cure horizon; show issue time and uncertainty, and revalidate.
- The system must not make worker-safety or structural-safety claims from heat data.
- Contract language and engineer direction override generic examples.

### Strongest competitors and differentiation

- **Direct substitute:** DeFelsko PosiTector DPM and Elcometer 319 already measure/log the exact climatic variables and produce reports. [P89, P90]
- **Weather/decision platform:** DTN offers hyperlocal operational weather and AI-driven planning. [P91]
- **System of record/scheduling:** Maximo, Cityworks, Primavera and Trimble B2W already manage work and resources. [P34–P37, P94, P95]

Differentiation is not sensing or scheduling alone. It is the bridge-specific joining of versioned coating clauses, portfolio-scale environmental pre-screen, direct field evidence, cure-horizon verification, constraint-feasible alternative search and owner approval packet. This remains feature-sized until a buyer validates frequency and value.

### Fatal uncertainty

**Does FortyGuard improve the pre-mobilization rank over NWS plus existing meter/logging practice often enough to change a real bridge assignment?** If retrospective field logs show no meaningful incremental precision or managers lack swappable approved work, kill the concept.

### Estimated hackathon build effort

Research prototype, not production:

- 0.5 day: two public bridge packages + rule fixture normalization;
- 1 day: deterministic rule/persistence/dew-point evaluator and tests;
- 0.5 day: simple assignment alternatives over 6–10 work packages;
- 1 day: agent tools, approval packet and trace;
- 1 day: map/timeline UI and demo polish;
- 0.5 day: evaluation, secret scan, regression and video rehearsal.

Total: roughly **4.5 focused engineer-days** using the existing core. Production integration, rule governance and field validation are much larger.

---

## Candidate 2: HFST Installation Window Verifier

### Precise product statement

> We are building this for DOT district construction engineers, resident engineers, owner inspectors, and HFST contractor superintendents to verify resin installation and cure windows across already-approved HFST sites, because both low and high pavement temperatures, moisture and precipitation can invalidate the working/cure interval and waste a specialized mobilization.

### Precise user and buyer

- **Daily operator:** resident engineer/owner inspector or contractor superintendent planning the next HFST shift.
- **Economic buyer:** DOT safety/pavement program or specialist HFST contractor with multiple sites in a program.
- **Essential condition:** at least two approved sites or shift options must be genuinely interchangeable. A single fixed closure produces only a go/no-go checklist.

### Why HFST is the pavement wedge

FHWA guidance identifies a bounded application envelope at both ends: surface temperatures should generally be at least 50°F unless a special binder is used, while above roughly 95°F some resin binders can thicken or gel within minutes. General guidance places ambient conditions around 50–100°F, preferably 60–95°F, but manufacturer instructions govern. Surface must be clean and dry; conditions outside the range affect working time, cure and final strength, and can lead to aggregate loss or premature wear. [P57, P58]

HFST is stronger than the alternatives because:

- unlike HMA, it is not already dominated by a mature compaction-temperature model and direct mix/mat temperature workflow;
- unlike generic seal coating, both excessive heat and cold have an intuitive material consequence;
- unlike marking, the failure/rework stakes and cure/working-time story are stronger;
- unlike slurry/microsurfacing, the resin/product-specific rule and working-time interaction creates a real investigation step;
- its work site is a pavement surface, where solar/built-context screening is directionally relevant.

It is still a conditional build: direct pavement temperature, dryness, surface preparation and resin mixing remain decisive.

### Real workflow

1. Agency identifies friction-deficient curve/intersection sites and lets or schedules an HFST package.
2. Contractor submits product, surface-preparation, mixing/application, traffic-control and cure plan.
3. Resident engineer/inspector verifies substrate condition and environmental limits against contract and manufacturer instructions.
4. Crew prepares the surface, mixes two-component resin under controlled timing, broadcasts aggregate, allows cure, removes excess aggregate and reopens after acceptance.
5. If conditions are unsuitable, start is delayed, shift moves, special binder may be used only if approved, or a different approved site may be worked.
6. Product lot, mix/application times, environmental readings, surface preparation, cure/opening and acceptance are documented.

### Agent loop

#### Observe

Ingest work packages with:

- approved site geometry and treatment area;
- contract/product/binder;
- planned preparation, application and reopening times;
- crew/equipment/material inventory;
- lane-closure permit and traffic restriction;
- priority/deadline and travel/setup time.

#### Investigate

- Resolve the exact agency specification and manufacturer product instructions.
- Pull cached FortyGuard heatmap and hourly apparent temperature, RH, precipitation, cloud/solar evidence.
- Pull ordinary forecast/wind from NOAA/NWS.
- Retrieve direct pavement/surface temperature and moisture/dryness check.
- Validate whether cached satellite segmentation is interpretable; `others=100%` is unusable, not evidence.
- Check product lot, material storage, working time and cure rule.

#### Decide

The deterministic rule engine evaluates:

- surface and ambient minimum/maximum;
- surface dry/clean evidence;
- rain-free preparation/application/cure horizon;
- wind/contamination rule if present;
- resin working time and allowed application duration;
- cure-before-opening;
- required field-measurement freshness.

#### Alternative search

Enumerate approved alternatives by start time, shift and approved site. Do not recommend installing HFST on an unapproved road merely because its temperature is better.

#### Constraint check

- closure availability and public-notice constraints;
- same product/system and crew qualification;
- resin/aggregate inventory and mobilization;
- setup/travel time;
- treatment area versus working-time production rate;
- cure before reopening;
- inspector availability and contractual completion date.

#### Verify

Re-run all rules across preparation through cure/reopening. Require a current pavement-temperature/dryness check at the alternative before release.

#### Human approval

Resident engineer/owner inspector approves; contractor superintendent confirms feasibility. Product substitution or special binder requires formal approval.

#### Audit

Store product/spec versions, product lot, ambient/surface readings, dryness/preparation evidence, source timestamps, full-interval rules, alternatives and infeasibility reasons, recommendation, approval and eventual aggregate-loss/acceptance evidence where available.

### Deterministic algorithms

1. Product-specific range and persistence checks.
2. Rain-free/cure interval intersection.
3. Treatment-area versus working-time/production feasibility.
4. Shift/site/crew assignment optimization.
5. Field-reading freshness and source hierarchy.
6. Optional surface-temperature model only as a planning estimate, clearly separate from field truth.

### FortyGuard role and necessity

**Role:** identify likely thermally distinct sites/shifts, evaluate hourly persistence, bring solar/cloud/precipitation context, and prioritize targeted field verification.

**Exact improved decision:** rather than canceling an entire program from a city forecast or discovering excessive pavement heat after mobilization, choose which approved site/shift deserves the crew and what exact field checks must confirm it.

**Cannot replace:** infrared/contact pavement thermometer, substrate dryness/cleanliness inspection, resin/product temperature, mix timing, surface-preparation acceptance or product instructions.

**Dependence: 6/10.** Spatially separated pavement sites and solar-driven heat improve fit, but the cached 96-tile test did not prove strong differentiation and direct surface truth controls. If a retrospective comparison shows citywide NWS makes the same site/shift choices, revise to <=4 and kill.

### Public demo data

| Input | Public source | Use |
|---|---|---|
| Real scheduled street segments | NYC Street Resurfacing Schedule [P83] | Real location/date/shift/work-type schema; explicitly a schema proxy, not an HFST roster |
| Work-zone feed schema | USDOT WZDx registry [P85] | Closure/work-zone interoperability context |
| HFST technical rules | FHWA HFST guidance [P57, P58] | Rule pack and failure rationale |
| Pavement treatment comparison | TxDOT, FHWA, Caltrans, MnDOT [P46–P56, P82] | Evidence that HFST was selected rather than broad “road repair” |
| Environmental profile | Cached FortyGuard + NOAA/NWS | Site/shift screen |
| HFST-specific work package, crew, closure, product lot | Public contract if sourced; otherwise synthetic fixture and labelled | Demonstrate agent/optimizer behavior |

**Demo-data quality: 7/10.** Real public road schedules are excellent, but a public schedule is not automatically an HFST program. The demo must never relabel resurfacing records as real HFST jobs.

### System architecture mapped to existing core

Use the shared architecture plus deterministic modules `hfst_rules.py`, `window_verifier.py`, `production_window.py`, and `assignment.py`. Existing budget/repeat-call protection preserves the zero-live-call constraint. Existing human approval wraps any `change_site_or_shift` proposal.

### Measurable outputs

Hackathon/evaluation:

- exact rule result and boundary tests;
- unknown-required-field recall;
- valid alternative precision;
- full cure-horizon verification;
- provenance and synthetic-field labelling completeness;
- NWS-only versus NWS+cached-FortyGuard rank difference on the demo portfolio.

Pilot:

- infeasible shifts caught before mobilization;
- field-confirmation precision/false-alarm rate;
- idle crew/equipment hours and closure hours avoided;
- time to approved replan;
- rework/early aggregate-loss trend, with acknowledgement of preparation/mixing confounders.

### Adoption path

1. Start with an HFST contractor/DOT program spreadsheet and read-only next-shift verifier.
2. Run retrospective comparison against inspector surface-temperature logs.
3. Add field-reading capture and approval packet.
4. Integrate with DOT construction-management/EAM systems.
5. Expand only through separate validated treatment rule packs; do not create a generic “road repair weather score.”

### Liability and controls

- Never infer dry/clean substrate from no forecast rain.
- Never treat heatmap temperature as pavement temperature.
- Never recommend an unapproved site or product substitution.
- High temperature can shorten working time; evaluate treatment area/production, not just a maximum threshold.
- The agent does not claim worker safety or guarantee bond/friction performance.
- Field/engineer override requires reason and remains in the audit log.

### Strongest competitors and differentiation

- FHWA/PaveCool and road-weather MDSS show that pavement/weather decision support is established. [P11, P88]
- Iteris ClearPath supplies site-specific pavement forecasts and recommended maintenance actions. [P88]
- Cityworks/Maximo and Trimble B2W already manage municipal/civil work and resource scheduling. [P34–P37, P95]
- A spreadsheet plus weather API can implement a simple HFST threshold.

Differentiation is exact product/specification resolution, excessive-heat working-time analysis, full cure-window verification, approved-site alternative search, explicit unknown gates and an auditable approval packet. Duplication risk remains 3/5.

### Fatal uncertainty

**Are there enough simultaneously approved, genuinely swappable HFST sites—and does FortyGuard improve their pre-mobilization ordering over NWS and inspector practice?** If not, the agent is an overbuilt checklist for an episodic project.

### Estimated hackathon build effort

- 0.5 day: rule/product fixtures and public schedule subset;
- 1 day: deterministic window/production evaluator and tests;
- 0.5 day: approved-site assignment model;
- 1 day: agent investigation/approval trace;
- 1 day: map/timeline demo;
- 0.5 day: evaluation, security and rehearsal.

Total: roughly **4.5 focused engineer-days** with the existing core. Real HFST work-package and field-log acquisition is the critical-path research dependency.

---

## Direct comparison

| Dimension | Bridge steel coating | HFST installation | Leader |
|---|---|---|---|
| Precise user/workflow | Inspector process and repeated condition logs are strongly documented | Clear inspector workflow, but program frequency varies | Bridge coating |
| FortyGuard dependence | Distributed exposed steel + cure persistence; direct steel meter controls | Distributed pavement + solar heat; direct pavement meter controls | Tie: 6/10 |
| Agentic necessity | Contract/product/stage/mitigation/closure evidence is heterogeneous | Product/site/closure evidence is moderately heterogeneous | Bridge coating |
| Public demo data | NBI + real multi-bridge contracts + public bid costs | Excellent road schedules, but not necessarily HFST schedules | Bridge coating |
| Deterministic technical core | Dew point/delta-T/persistence + assignment | range/working-time/cure + assignment | HFST slightly simpler |
| Measurable outcome | Mobilization, field-confirmation, nonconformance/rework | Mobilization, field-confirmation, aggregate loss/rework | Tie |
| 3-minute communication | Strong before/after bridge swap and exact clause | Extremely intuitive hot pavement/evening shift story | HFST |
| Duplication | Instruments and broad weather platforms exist; exact orchestration gap | Road MDSS/PaveCool/EAM are close and road ideas are common | Bridge coating |
| Adoption | Established owner inspection authority; integration burden | Specialized/episodic work may limit frequency | Bridge coating |
| Fatal uncertainty | Incremental rank vs NWS + meter | Frequency/swappability plus incremental rank | HFST riskier |

## Evidence-leader decision

**Current evidence leader: Bridge Steel Coating Window Verifier.** It wins narrowly because its recurring inspection/audit loop, multi-bridge public portfolio, direct buyer/approver and consequences of condition excursions are better evidenced. HFST remains the strongest pavement concept and the cleaner visual demo.

This is not a build decision. No candidate meets the preferred FortyGuard-dependence threshold of 7/10 under the verified data contract. Human selection should wait for the retrospective decision-delta and buyer/work-package gates in the opportunity matrix.
