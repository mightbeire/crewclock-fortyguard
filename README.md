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
2. Decides whether thermal investigation is necessary.
3. Selects the workfaces and time windows that need evidence.
4. Uses those validated selections for the FortyGuard requests.
5. Calculates schedule overlap with the modeled high-heat window.
6. Tests feasible schedule alternatives.
7. Verifies hard construction constraints.
8. Presents one verified recommendation, or keeps the current plan when no useful change exists.
9. Waits for superintendent approval.
10. Verifies the exact approved schedule again before it becomes final.

If usable evidence is unavailable, CrewClock preserves the current shift. It does not invent a zero value or fabricate a recommendation.

## Why the AI agent matters

The AI agent controls the investigation path. It decides whether to investigate and which workfaces and time windows matter. Those choices cause the actual evidence requests.

The AI does not own schedule arithmetic or final authority.

Deterministic code owns:

- schema validation;
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

The same product also passed no-change and evidence-unavailable paths. A fresh Austin, Texas, run returned no usable thermal evidence, and CrewClock correctly preserved the current schedule.

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

The final build passed 148 Python tests, 48 Vitest tests, typecheck, lint, build, secret scan, and browser-only acceptance.

Final engineering validation:

```text
pytest: 148 passed
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