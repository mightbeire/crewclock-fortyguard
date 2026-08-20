# CrewClock

Team: `btn operations`

Primary track: Agentic AI

Secondary fit: Industrial & Enterprise
MVP decision: **CrewClock locked on 2026-08-20**

> We help construction companies plan tomorrow’s work around extreme heat without blowing the schedule.

More precisely: **We are building CrewClock for construction superintendents to turn tomorrow’s jobs, crews, deadlines, and company heat rules into a workable plan that avoids unnecessarily bad heat periods while keeping the project moving.**

## Current product

The reusable React/Vite stage shell has been converted into CrewClock mission control:

- a 14-task Phoenix construction-day fixture;
- three crews and fifteen workers with trade qualifications;
- two field workfaces and one shaded laydown zone;
- fixed inspections, traffic-control and concrete commitments;
- cached-live Phoenix FortyGuard TCM, hourly environmental parameters and time-of-measure evidence;
- a seven-step high-level agent run;
- a deterministic before/proposed schedule and independent constraint checks;
- superintendent approval;
- a recomputed `22 → 6 = 16` crew-hour planning metric;
- an evidence drawer that separates cached-live, public, derived, employer and synthetic inputs.

The UI contains no live FortyGuard request path. Current reserve remains approximately `1,795,500` credits.

## Locked architecture

```text
agent = investigate + select evidence + orchestrate + explain + verify + escalate
optimizer = deterministic scheduling under constraints
superintendent = approve / reject / revise
onsite responsible person = current measurement + employer-plan execution + stop-work authority
```

The LLM never performs schedule mathematics directly. Required evidence resolves to `PASS`, `FAIL`, or `UNKNOWN`; unknown required evidence blocks the recommendation.

## Locked hero metric

**Movable outdoor crew-hours shifted out of the highest modeled heat window while all modeled qualifications, dependencies, deadlines, fixed commitments, and employer planning controls remain satisfied.**

This is a derived planning proxy. It is not a safety, health, compliance, productivity or dollar outcome.

## Evidence boundary

- FortyGuard supports pre-shift spatial/temporal investigation and alternate-window screening.
- FortyGuard is not WBGT and does not certify safety.
- Onsite measurement, workload, PPE, acclimatization, worker condition, employer policy and professional judgment remain authoritative.
- The current demo is a reproducible historical replay, not tomorrow’s forecast.
- The 14-task work package and employer policy are realistic but synthetic.
- Public ADOT project data is context/schema evidence, not a customer work order.
- The federal OSHA heat rule remains proposed as of the research date.
- No external schedule action occurs in the MVP.

## Start here

1. Read `docs/CREWCLOCK_MVP_SPEC.md`.
2. Read `docs/CREWCLOCK_DATA_MODEL.md` and `docs/CREWCLOCK_MEASUREMENT.md`.
3. Rehearse with `docs/CREWCLOCK_DEMO_SCRIPT.md`.
4. Run `npm run dev`, `npm run test:ui`, and `python -m pytest -q`.
5. Preserve the no-live-call rule until the team explicitly authorizes final decision-delta validation.

## Final validation gate

Before claiming a sponsor-specific operational advantage, compare one real mapped multi-zone look-ahead under:

1. ordinary forecast + superintendent/spreadsheet baseline; and
2. the same constraints with authorized FortyGuard evidence.

Record whether FortyGuard changes the tasks investigated, timing/zone ranking, feasible plan, or superintendent decision. Narrow or stop the sponsor claim if it does not.

Historical exploration, due diligence, live-schema validation, money-first research and prior finalist records remain in `docs/` and Git history.
