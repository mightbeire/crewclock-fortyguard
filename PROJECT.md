# CrewClock

Team: `btn operations`

Primary track: Agentic AI

Secondary fit: Industrial & Enterprise
MVP decision: **CrewClock locked on 2026-08-20**

> CrewClock helps construction superintendents adjust the upcoming shift around hyperlocal heat without breaking the schedule.

More precisely: **Before crews deploy, CrewClock identifies flexible outdoor work that overlaps the worst local heat, tests feasible alternatives, and lets the superintendent approve the least-disruptive adjustment.**

## Current product

CrewClock is now a submission-grade, single-screen React/Vite mission-control workspace:

- a 14-task Phoenix construction-day fixture;
- three crews and fifteen workers with trade qualifications;
- two field workfaces and one shaded laydown zone;
- fixed inspections, traffic-control and concrete commitments;
- cached-live Phoenix FortyGuard TCM, hourly environmental parameters and time-of-measure evidence;
- a seven-step high-level agent run;
- an executable deterministic interval scheduler that independently reproduces the locked proposal;
- six modeled hard-constraint families with candidate rejection and post-approval verification;
- selective investigation that queries seven movable outdoor tasks while skipping shaded and fixed work;
- superintendent approval;
- a recomputed `22 → 6 = 16` crew-hour planning metric;
- evidence and audit inspectors that separate cached-live, derived, employer and synthetic inputs;
- fail-closed states for missing/stale evidence, tool failure, ambiguous policy, infeasible input and no better plan;
- deterministic reset and query-addressable QA fixtures with no network dependency.

The UI contains no live FortyGuard request path. The current recorded reserve for this task is `1,782,840` credits; this runtime made no FortyGuard request.

## Real agent runtime status

The provider-neutral orchestration layer now has a bounded Groq Chat Completions adapter for `openai/gpt-oss-120b` with local CrewClock tool calling. The model can select evidence, deterministic calculations, alternatives, verification and approval; deterministic code remains authoritative for every factual calculation and hard constraint. The project `.env` fields are present and loaded safely, but Groq returned HTTP 403 for the minimal authentication/model checks, so no real-model evaluation is claimed. The deterministic provider remains the submission fallback.

See `docs/CREWCLOCK_REAL_AGENT_EVAL.md` for offline A–J protocol traces and measured counts.

## Locked architecture

```text
agent = investigate + select evidence + orchestrate + explain + verify + escalate
optimizer = deterministic scheduling under constraints
superintendent = approve / reject / revise
onsite responsible person = current measurement + employer-plan execution + stop-work authority
```

The LLM never performs schedule mathematics directly. Required evidence resolves to `PASS`, `FAIL`, or `UNKNOWN`; unknown required evidence blocks the recommendation.

## Locked hero metric

**Scheduled high-heat crew-hours, derived from outdoor movable task overlap with the employer-configured trigger while all modeled hard constraints remain satisfied.**

This is a derived planning proxy. It is not a safety, health, compliance, productivity or dollar outcome.

## Evidence boundary

- FortyGuard supports pre-shift spatial/temporal investigation and alternate-window screening.
- FortyGuard is not WBGT and does not certify safety.
- Onsite measurement, workload, PPE, acclimatization, worker condition, employer policy and professional judgment remain authoritative.
- The current demo is a reproducible cached-live historical replay, not a current forecast.
- The 14-task work package and employer policy are realistic but synthetic.
- Public ADOT project data is context/schema evidence, not a customer work order.
- The federal OSHA heat rule remains proposed as of the research date.
- No external schedule action occurs in the MVP.

## Start here

1. Read `docs/CREWCLOCK_MVP_SPEC.md`.
2. Read `docs/CREWCLOCK_DATA_MODEL.md` and `docs/CREWCLOCK_MEASUREMENT.md`.
3. Rehearse with `docs/CREWCLOCK_DEMO_SCRIPT.md`.
4. Run `npm run dev`, `npm run test:ui`, `npm run typecheck`, `npm run lint`, `npm run build`, and `python -m pytest -q`.
5. Read `docs/CREWCLOCK_ARCHITECTURE.md` for the implemented agent/scheduler boundary.
6. Preserve the no-live-call rule until the team explicitly authorizes final decision-delta validation.

## Final validation gate

Before claiming a sponsor-specific operational advantage, compare one real mapped multi-zone look-ahead under:

1. ordinary forecast + superintendent/spreadsheet baseline; and
2. the same constraints with authorized FortyGuard evidence.

Record whether FortyGuard changes the tasks investigated, timing/zone ranking, feasible plan, or superintendent decision. Narrow or stop the sponsor claim if it does not.

Historical exploration, due diligence, live-schema validation, money-first research and prior finalist records remain in `docs/` and Git history.
