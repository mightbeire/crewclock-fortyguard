# Decisions

## 2026-08-21 — Lock SHHCH to schedule-aligned exceedance

CrewClock now treats FortyGuard `analytic_type=exceedance` as the sole
duration signal for Scheduled High-Heat Crew-Hours: tiles are area-weighted
over polygon workfaces, intersected with the exact scheduled task interval, and
multiplied by crew size. `env_params` is optional contextual evidence only.
The project trigger is a separately named FortyGuard modeled-temperature
threshold, never a silent heat-index mapping. Phoenix currently has no cached
schedule-aligned exceedance windows, so the canonical demo fails closed and
reports `CACHED_EXCEEDANCE_EVIDENCE = NONE`.

## 2026-08-21 — Stop canonical exceedance validation on repeated terminal failure

The existing successful Phoenix control date/AOI and preconfigured 32.0 °C
modeled-temperature trigger were retained. Two exact historical `exceedance`
requests for the first `06:00–08:00` schedule window returned terminal
`Failed`, consumed zero credits, and produced no tiles. The remaining four
windows were not requested because incomplete schedule coverage cannot support
SHHCH. The sanitized records are retained under
`evidence/crewclock-canonical-exceedance/`; no metric or schedule change is
claimed.

## 2026-08-21 — Repair offline agent terminal boundaries

Forensics distinguish A/E/F behavioral stopping, E provider interruption, and
H's scenario-gated deterministic approval bug. Deterministic result envelopes
now expose validity, decision relevance, provenance, and next allowed actions.
Untrusted prompt text remains inert data; verified feasible schedules can enter
the human approval gate without scenario-name logic.

## 2026-08-19 — Preserve the vendored quickstart

The existing FortyGuard quickstart contains the most valuable local research, client wrapper, notebooks, and sanitized fixtures. It is retained as a vendor/reference layer rather than rewritten.

## 2026-08-19 — Use official docs as the current API authority

The local quickstart and current official docs disagree on a few details, notably date coverage and some unit wording. We record both, prefer current official docs for request construction, and treat cached fixture values as evidence with explicit provenance.

## 2026-08-19 — Handbook supersedes earlier assumptions

The supplied participant handbook is authoritative for the U.S.-only scope, 2021-present date range, twelve-hour forecast horizon, team/submission rules, tracks, judging, conduct, and API endpoint plan access. The handbook’s approximate 2 m platform claim is not treated as API output precision because the API contract and live test expose 60/80/100 m grid granularity.

## 2026-08-19 — Use a bounded live validation budget

After the non-billable usage check, five distinct analysis calls were made and cached: heatmap `tcm`, env params, satellite segmentation, exceedance, and multi-tile `tcm`. Measured deltas are recorded in `docs/LIVE_API_VALIDATION.md`; successful requests are not repeated.

## 2026-08-19 — Premium access is capability-specific

Satellite segmentation completed for the Hackathon account. Street-view and heat-intelligence access were not tested, so no finalist may depend on them.

## 2026-08-19 — Live evidence favors temporal scheduling over unsupported spatial claims

The live environmental profile supports a real hourly temporal workflow. A 96-tile test showed only small daily temperature variation and uniform one-hour exceedance in the selected AOI/date. This does not falsify the concepts, but it does falsify any claim that this test already proves strong spatial ranking; finalist confidence is downgraded and the MVP remains unselected.

## 2026-08-19 — Live analysis calls are cached and idempotent

## 2026-08-19 — Satellite is an evidence gate, not a visualization

The satellite endpoint returns physical-context percentages that can make an operational decision possible, but quality varies: some sites returned interpretable building/road/tree/rail labels and some returned `others=100%`. Agents must use segmentation to support or reject an interpretation, never to invent a material classification.

## 2026-08-19 — Geography selection is evidence-driven

Las Vegas is the strongest current paired heat/surface candidate; Phoenix is strongest for high-heat temporal scheduling; Los Angeles is strongest for a rail-context experiment. Houston, DFW, New York, and Portland were retained as negative coverage/context evidence because the selected heatmap requests returned zero cells.

## 2026-08-19 — New leader is tentative and can still be killed

The Surface-conditioned Road Repair Queue currently outranks Thermal Sequence Planner because it has a public work-order input path, interpretable live Las Vegas surface labels, and a stronger cached-live proxy spike. Its critical assumption is a real city work-order join to FortyGuard coverage; if that fails, Thermal Sequence can recover the lead.

## 2026-08-19 — Do not trust unvalidated environmental units

The live Atlanta `heat_index_celsius` array contains values up to 77.9 alongside plausible apparent-temperature and humidity values. Until the API clarifies the field, the agent will use apparent temperature/wet bulb and surface the heat-index anomaly as uncertainty.

Authentication was verified with the usage endpoint. Cached responses are sufficient for schema and metric work; repeating identical analysis requests would waste credits and create no new evidence.

## 2026-08-19 — Mock-first agent core

The agent loop is provider-neutral and deterministic by default. A hosted LLM may propose tool calls later, but it cannot bypass the registry, budgets, repeat-call protection, or human approval.

## 2026-08-19 — Do not select the MVP

The exploration run ranks three finalists but intentionally stops before product selection, as required by the brief.

## 2026-08-19 — Deep due diligence changes the claims

The current finalist claims are not equally supported. Surface-conditioned Road Repair Queue remains the evidence leader only when narrowed from generic heat-based backlog ranking to a heat-safe pavement work-window verifier. Thermal Sequence Planner is held because incumbent FSM products already solve constrained scheduling and the repository lacks real technician/job inputs. RailHeat Patrol Sequencer is killed as stated because FRA/Amtrak evidence requires rail temperature, neutral temperature, CWR plan, track condition and qualified authority; FortyGuard ambient heat plus satellite context cannot establish a safe patrol decision.

## 2026-08-19 — Safety metric boundary

OSHA/NIOSH guidance is authoritative for worker heat: WBGT, workload, clothing/PPE and acclimatization matter. FortyGuard apparent temperature, heat-index fields and the project’s thermal-load proxy are not safety determinations. Future demos must label them as environmental screening or operational proxies unless a qualified pilot supplies the required measurements.

## 2026-08-19 — Use deterministic optimization for mathematics

Queue ranking, VRPTW sequencing and rail access constraints belong in rules/SQL/optimization systems. The agent’s defensible role is evidence selection, heterogeneous-input interpretation, uncertainty handling, explanation, verification and approval routing. “Uses tools” alone is not sufficient evidence of agentic necessity.

## 2026-08-19 — No new FortyGuard calls in deep research

The deep product-research pass used cached-live responses, existing fixtures, public sources and project results only. Measured account state remains 204,500 used and 1,795,500 remaining; no new paid endpoint was called.

## 2026-08-20 — Execution-window verification is the durable pattern

The best mutation is not a generic heat queue, alert or schedule. It begins with already-approved work and verifies whether this place/time/condition interval is executable, searches only valid alternatives, checks operational constraints, verifies again and routes the proposal to the authorized human.

## 2026-08-20 — HFST is the single pavement wedge

High-friction surface treatment is more defensible than broad road repair, HMA paving, patching, crack sealing, slurry, microsurfacing, seal coating or marking. Both low and excessive pavement heat can affect resin working/cure behavior, and the product has an understandable full-window decision. Direct pavement temperature, dryness, surface preparation, mixing and manufacturer instructions remain hard gates.

## 2026-08-20 — Bridge steel coating is the evidence leader, not the MVP

Bridge steel coating narrowly leads HFST because its inspector workflow, direct environmental records, cure persistence, multi-bridge public portfolio, program buyer and failure/audit consequences are better evidenced. The tie on the official rubric is retained rather than manufactured away. Human selection remains pending.

## 2026-08-20 — No candidate clears the preferred FortyGuard-dependence bar

Bridge coating, HFST and SPF roofing score 6/10. Direct steel/pavement/roof temperature and moisture/dew-point instruments control final release; wind is also missing from the verified cached FortyGuard contract. FortyGuard’s defensible role is portfolio screening, spatial/temporal investigation and alternate-window verification. If retrospective tests show NWS plus site meters produce the same assignment, kill the concept.

## 2026-08-20 — Unknown required evidence is never a pass

Every execution-window rule pack must return clause-level `PASS`, `FAIL` or `UNKNOWN`. A missing, stale, unit-ambiguous or conflicting required field blocks release and is escalated. The LLM selects evidence and coordinates tools; deterministic code performs dew-point, persistence, production and assignment mathematics.

## 2026-08-20 — Public schedules are schema evidence, not customer work orders

NYC resurfacing, NBI, WZDx, Chicago permits and public bridge contracts may supply real locations, dates, assets and contract structure. They must not be relabelled as real HFST/roof/coating work packages. Missing crew, closure, product and field-reading constraints may be synthetic only when explicitly marked.

## 2026-08-20 — Zero live FortyGuard calls in the opportunity hunt

The second research pass used only cached-live responses, fixtures, primary sources and public data. Measured account state remains 204,500 used and 1,795,500 remaining.
# 2026-08-20 — Winner-archetype and reusable-stage pass

- Reviewed 40 public winners/finalists and coded recurring demo/product characteristics instead of treating project descriptions as strategy.
- Adopted a winner blueprint centered on one recognizable user, one operational canvas, sponsor-specific evidence in the causal path, a visible agent loop, human authority and a recomputed result.
- Generated 25 fresh concepts. Seventeen were killed for clarity, dependency, agent necessity, claim, data or demo failures.
- Advanced ShiftShield, CourseCorrect and Recess Relay as unresolved finalists. ShiftShield is the current evidence leader by weighted score, not the selected MVP.
- Rejected health/safety outcome language. Demo metrics are planning-exposure proxies and must remain labelled derived.
- Built the reusable UI as a separate Vite/React layer. It imports a static sanitized scenario and contains no live FortyGuard request path.
- Chose cached Phoenix/Los Angeles/Las Vegas values because they provide verified temperatures and satellite context while keeping rehearsal deterministic and credit-safe.
- Preserved human approval as a recommendation gate; the demo never executes an external operational action.
- `FINAL_MVP_SELECTED = NO`.
# 2026-08-20 — Built finalist showdown

- Stopped concept generation and built equal micro-demos for the three existing finalists.
- Standardized the comparison: six high-level agent actions, cached FortyGuard evidence, deterministic operational inputs, constraint verification, human approval and recomputed results.
- Added distinct product-native transformations: stop resequencing for ShiftShield, course/crowd rerouting for CourseCorrect, and linked campus/timetable swaps for Recess Relay.
- Recorded all operational constraints and hero metrics as deterministic scenario data. No health, safety, production or current-data claim is made.
- The five-judge mean is CourseCorrect 8.92, Recess Relay 8.88 and ShiftShield 8.78. Judges disagree materially; the spread is too small for automatic selection.
- Recommend CourseCorrect at 61% confidence for stage experience, with Recess Relay runner-up. The main counterargument is the mismatch between thermal-information timing and course/closure lead time.
- `FINAL_MVP_SELECTED = NO`.

# 2026-08-20 — Lock CrewClock as the hackathon MVP

- Human preference selected CrewClock for a final narrow validation; broad idea generation stopped.
- Primary user is **Construction Superintendent**. O*NET and BLS support responsibility for onsite scheduling, trade coordination, supervision, deadlines, delay response, progress and budget.
- OSHA, NIOSH and a published JE Dunn heat program verify that construction employers already change work timing, work/rest periods, workload, crew allocation and controls because of heat.
- CrewClock is a pre-shift operations planner, not a heat-safety or compliance system. FortyGuard is not WBGT. Onsite measurement, employer policy, workload, PPE, acclimatization, symptoms and authorized judgment remain controlling.
- The federal OSHA heat-specific rule is still proposed as of the decision date. The product imports employer rules and must never present the proposal as binding federal law.
- The agent selects evidence, orchestrates, explains, verifies and escalates. Deterministic code performs schedule and metric mathematics. The Construction Superintendent approves; the MVP performs no external action.
- The locked hero metric is **SHHCH: area-weighted FortyGuard exceedance duration intersected with the exact outdoor task interval and multiplied by crew size**. The Phoenix fixture emits no number until schedule-aligned exceedance evidence is validated.
- The 14 tasks, three crews, qualifications, dependencies, deadlines, fixed commitments, workface geometry and employer rule pack are explicitly synthetic. Phoenix FortyGuard evidence is cached-live; ADOT/OSHA/NIOSH inputs are public context.
- Ordinary forecast plus a spreadsheet is the hostile baseline. CrewClock survives only as an evidence-selection, multi-constraint scheduling, verification and approval workflow. A final real multi-zone test must show whether FortyGuard changes the operational decision.
- The reusable finalist shell is converted into CrewClock mission control with schedule, thermal profile, workface map, agent activity, before/after, approval, hero metric and evidence boundary.
- `CREWCLOCK_MVP_READY = YES`; CrewClock is formally locked as the hackathon MVP, subject to the documented final decision-delta gate.
- Zero new live FortyGuard requests were made. Reserve remains approximately `1,795,500` credits.

# 2026-08-20 — Ship the deterministic CrewClock production MVP

- The canonical recommendation is no longer accepted from fixture timestamps. `src/demo/engine.ts` enumerates 30-minute crew assignments, applies feasibility first, minimizes eligible peak-window crew-hours second, and minimizes schedule movement third.
- The solver remains deterministic and fixture proposal times remain only operational inputs; SHHCH is now independently recomputed from exceedance windows rather than TCM or env_params.
- Verification is grouped into fixed commitments, dependencies, qualifications, deadlines/bounds, crew availability, and employer policy. Approval triggers a final recomputation; it does not publish externally.
- Conditional investigation is explicit: seven movable outdoor tasks across two workfaces are investigated, two movable shaded tasks are skipped, and five fixed commitments are retained without unnecessary thermal queries.
- Missing/stale evidence, tool failure, ambiguous policy, infeasible source input, and no-improvement outcomes fail closed and issue no proposal.
- The one-screen desktop layout is the canonical demo surface. Query-string failure fixtures exist only for deterministic QA and do not add presenter controls.
- The bounded 2026-08-21 probe made two live heatmap calls and consumed 8,440 credits from the 1,795,500 run balance; no env_params or premium call was made.

## Foundation lock amendment — 2026-08-21

- Current official quickstart `main` is `f6de12d`; heatmap forecast horizon is guarded at +12h, TCM/analysis units are asserted, and transient status 404 is treated as eventual consistency.
- `env_params` is never used as a range-based shift forecast. The controlled future Phoenix probe made two heatmap calls (8,440 credits) and returned zero cells both times; no env_params call was submitted. `FUTURE_SINGLE_HOUR_ENV_PARAMS = AMBIGUOUS`.
- Product language is “upcoming shift”, and the hero metric is `scheduled high-heat crew-hours`. Heatmap is the primary spatial signal; polygon workfaces are area-weighted over the shared AOI.
- Mandatory policy breaks are real scheduling constraints. The agent may choose evidence windows and tools; deterministic code owns overlap, feasibility, verification, metrics, budgets and approval recheck.

## Real-agent runtime amendment — 2026-08-21

- Use Groq `openai/gpt-oss-120b` through the OpenAI-compatible Chat Completions local-tool-calling interface. CrewClock, not Groq, owns tool execution and orchestration.
- Keep the provider-neutral `LLMProvider` boundary. Groq-specific HTTP and response translation stays in the provider adapter.
- Treat the absence of `GROQ_API_KEY` as “real model not connected,” not as a reason to fabricate a model evaluation. The deterministic provider and offline A–J protocol suite remain the demo fallback.
- Keep the future Phoenix forecast path closed. The real runtime reads only explicit cached-live fixtures in this run; it makes zero FortyGuard calls.
- The project `.env` fields were found and loaded without exposing the key, but Groq returned HTTP 403 for both model listing and minimal chat completion. Do not label A–J offline protocol traces as real-model results; keep the deterministic fallback active until credential access is repaired.

## Groq connection gate amendment — 2026-08-21

- The target model `openai/gpt-oss-120b` is now visible and returned HTTP 200 with usable assistant content under a bounded raw request.
- The production adapter required a narrow transport/shape correction: omit empty tool fields for no-tool calls and use the fixed-host low-level HTTPS transport. The adapter then passed a real completion and a harmless local `echo_status` tool-call smoke test.
- Reasoning-related response fields may be present; their contents are never persisted or displayed.
- Full real A–J evaluation remains a separate next run. No FortyGuard call was made.

## Groq evaluation stop amendment — 2026-08-21

- The target model and production adapter passed the connection gate and a harmless local tool-call smoke test.
- The real A–J evaluation was stopped immediately after a sanitized HTTP 429 `rate_limit_exceeded` response during the first A workflow. No further Groq requests were made.
- The real evaluation is `PARTIAL`, not a model-behavior pass. Offline deterministic protocol tests remain useful, but cannot substitute for A–J evidence.
- No FortyGuard calls were made; cached-live evidence remained the only evidence source.

## Rate-aware real-agent evaluation amendment — 2026-08-21

- All real CrewClock Groq evaluation calls share one runtime rate governor. Returned limit/reset/retry headers are the source of truth; no permanent free-tier limits are hard-coded.
- The evaluator is strictly sequential and checkpoints each logical trial, including an in-progress marker before the first model call. Resume hydrates capacity/accounting state and starts at the first incomplete trial.
- Provider rate/transient/fatal failures are not behavioral failures. A genuine model mistake is classified separately and may trigger a general prompt/tool/state repair followed by targeted reruns.
- Persisted evidence is sanitized high-level operational data only. No FortyGuard calls, secrets, provider messages or chain-of-thought are permitted.
