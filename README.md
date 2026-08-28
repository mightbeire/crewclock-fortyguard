# CrewClock

**Agentic decision intelligence for construction operations**

CrewClock helps construction superintendents adjust an upcoming shift around hyperlocal modeled heat without breaking the schedule.

**FortyGuard Hackathon '26**  
**Team:** btn operations  
**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise

## What CrewClock does

A superintendent enters the shift that already exists. The input includes crews, headcounts, workfaces, task times, fixed work, flexible work, and site details.

CrewClock then:

1. Reviews the submitted shift.
2. Validates all six hard constraint families before thermal acquisition.
3. Decides whether thermal investigation is necessary.
4. Selects the workfaces and time windows that need evidence.
5. Uses those validated selections for the FortyGuard requests.
6. Calculates schedule overlap with the modeled high-heat window.
7. Tests feasible schedule alternatives.
8. Verifies hard construction constraints.
9. Presents one verified recommendation, or keeps the current plan when no useful change exists.
10. Waits for superintendent approval.
11. Verifies the exact approved schedule again before it becomes final.

If usable evidence is unavailable, CrewClock preserves the current shift. It does not invent a zero value or fabricate a recommendation.

## Why the AI agent matters

The AI agent controls the investigation path. It decides whether to investigate and which workfaces and time windows matter. Those choices cause the actual evidence requests.

The AI does not own schedule arithmetic or final authority.

Deterministic code owns:

- schema validation;
- baseline constraint validation;
- SHHCH calculation;
- schedule generation;
- crew and qualification checks;
- dependency and deadline checks;
- fixed-commitment checks;
- employer-control checks; and
- final verification.

The superintendent owns the final approval.

## FortyGuard evidence

CrewClock uses FortyGuard as the modeled environmental evidence source. Evidence is bound to the selected project workface and time window.

For multi-workface investigations, CrewClock requests each selected workface separately. This keeps spatial coverage explicit.

FortyGuard heatmap activities are asynchronous. CrewClock polls activity status for up to 600 seconds so valid live activities have time to complete. Empty or unusable results still remain unavailable; the longer polling window does not weaken evidence standards.

## SHHCH

**Scheduled High-Heat Crew-Hours (SHHCH)** is a schedule-placement metric.

CrewClock calculates the overlap between modeled high-heat windows, outdoor task timing, and crew size. It then sums the resulting scheduled crew-hours.

SHHCH is **not** a physiological exposure measure, a heat-dose measure, a medical risk score, or a statement of OSHA compliance.

## Final browser acceptance

The final browser-only acceptance used a Palm Springs, California, construction shift and previously acquired live FortyGuard evidence that matched the exact site and time identity.

- Baseline SHHCH: **13 crew-hours**
- Proposed SHHCH: **4 crew-hours**
- Flexible tasks retimed: **3**
- Constraint families: **6/6 → 6/6**
- Human approval: **PASS**
- Final deterministic verification: **PASS**

The same product also passed no-change and evidence-unavailable paths.

## Fresh live future proof

On August 28, 2026, CrewClock also completed a same-day future Palm Springs run through the normal browser path.

- Future shift: **10:00–16:00 local**
- Baseline constraints before thermal review: **6/6 PASS**
- FortyGuard mode: **fresh live**
- Completed schedule-aligned activities: **3**
- Baseline SHHCH: **15 crew-hours**
- Schedule candidates considered: **1,160**
- Feasible candidates: **1,080**
- Lower-SHHCH feasible candidates: **0**

CrewClock therefore returned `NO_FEASIBLE_IMPROVEMENT` and kept the valid current plan. This result proves the fresh-future acquisition and optimization path without forcing a schedule change when the evidence does not support one.

Final hardening also found two issues before submission. Live acquisition could stop polling after 90 seconds even though valid FortyGuard activities can process for several minutes. Baseline constraint validation also happened too late in the flow. CrewClock now polls for up to 600 seconds and rejects invalid baselines before AI orchestration or FortyGuard acquisition. Regression tests cover both cases.

## Run locally

Create a local environment file from `.env.example`, then add your own provider keys. Do not commit `.env`.

```bash
npm install
npm run build:runtime
npm run dev:api
```

In a second terminal:

```bash
npm run dev
```

Open the local Vite URL shown in the terminal.

## Validation

The final build passed 150 Python tests, 48 Vitest tests, typecheck, lint, build, secret scan, and browser-only acceptance.

Final engineering validation:

```text
pytest: 150 passed
Vitest: 48 passed
typecheck: PASS
lint: PASS
build: PASS
secret scan: PASS
browser-only acceptance: PASS
```

## Product boundaries

- CrewClock supports the U.S. scope supported by FortyGuard.
- It is pre-shift planning support, not a safety certification system.
- Site geometry is approximate and operator-anchor-derived. It is not surveyed geometry.
- The AI never approves its own recommendation.
- Missing evidence stays unavailable. CrewClock does not convert missing evidence into zero.

## Submission documents

- [`docs/SUBMISSION.md`](docs/SUBMISSION.md) — final submission summary, under 500 words
- [`docs/CREWCLOCK_DEMO_SCRIPT.md`](docs/CREWCLOCK_DEMO_SCRIPT.md) — final demo script
- [`docs/JUDGE_NOTES.md`](docs/JUDGE_NOTES.md) — concise judge questions and answers

Historical files in this repository record the development process. This README and the three submission documents above are the submission-facing source of truth.