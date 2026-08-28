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

1. Validates all six hard constraint families before thermal acquisition.
2. Lets the AI agent decide which workfaces and time windows need investigation.
3. Uses those validated choices for FortyGuard requests.
4. Extends evidence coverage across reachable destination windows inside the submitted shift.
5. Calculates Scheduled High-Heat Crew-Hours (SHHCH).
6. Tests feasible schedule alternatives.
7. Verifies hard construction constraints.
8. Presents one verified recommendation, or explains why no lower-overlap change can be supported.
9. Waits for superintendent approval.
10. Verifies the exact approved schedule again before it becomes final.

If usable evidence is unavailable, CrewClock preserves the current shift. It does not invent a zero value or fabricate a recommendation.

## Why the AI agent matters

The AI agent controls the investigation path. It decides whether thermal investigation is needed and which workfaces and time windows matter. Those choices cause the evidence requests.

The AI does not own schedule arithmetic or final authority. Deterministic code owns baseline validation, SHHCH, schedule generation, hard-constraint checks, and final verification. The superintendent owns approval.

## FortyGuard evidence

CrewClock uses FortyGuard as the modeled environmental evidence source. Each request is bound to one selected workface and one selected time window.

FortyGuard heatmap activities are asynchronous. CrewClock polls activity status for up to 600 seconds so valid live activities have time to complete. Empty or unusable results remain unavailable.

CrewClock also acquires evidence for reachable destination windows. This matters because a task cannot be credited with lower SHHCH unless the destination window has decision-grade evidence. Unknown evidence is never treated as zero.

## SHHCH

**Scheduled High-Heat Crew-Hours (SHHCH)** is a schedule-placement metric. It measures scheduled crew-hours that overlap the configured modeled high-heat window.

SHHCH is **not** a physiological exposure measure, a heat-dose measure, a medical risk score, or a statement of OSHA compliance.

## Primary fresh-future proof

On August 28, 2026, CrewClock completed a same-day future San Diego stress test through the normal browser path with fresh live FortyGuard evidence.

- Baseline SHHCH: **18 crew-hours**
- Proposed SHHCH: **9 crew-hours**
- Reduction: **9 crew-hours / 50%**
- Flexible tasks retimed: **3**
- Fixed tasks changed: **0**
- Constraint families: **6/6 → 6/6**
- Human approval: **PASS**
- Final deterministic reverification: **PASS**
- Destination evidence coverage: **PASS**

This run proved the complete path: future shift → AI-selected investigation → fresh FortyGuard evidence → destination-window coverage → lower-SHHCH schedule → deterministic verification → human approval → final reverification.

## Additional positive proof

A browser acceptance run in Palm Springs used previously acquired live evidence after an exact identity match and reduced SHHCH from **13 → 4** while retiming three tasks and preserving 6/6 constraints.

A separate real Miami integration run reduced SHHCH from **21.09 → 5.03**, about a 76% reduction, with 6/6 constraints before and after.

## When the whole measured shift remains above the trigger

CrewClock does not call that schedule “optimal.” If complete evidence shows the configured modeled-temperature trigger across the full measured shift window for every investigated workface, the result says:

> **The full measured shift remains above the configured trigger.**

It then explains that retiming inside the submitted shift cannot reduce SHHCH. CrewClock does not make a safety determination. The superintendent should use the employer heat plan to decide whether to delay, modify, or keep the work.

If the evidence does not prove full-shift trigger coverage, CrewClock uses the narrower statement: **No lower-SHHCH schedule was found within this shift.**

## What final testing fixed

The final live tests exposed three integration defects before submission:

- Live polling could stop after 90 seconds even though valid FortyGuard activities can take several minutes. CrewClock now polls for up to 600 seconds.
- Baseline constraint validation happened too late. CrewClock now requires a valid baseline before AI orchestration or FortyGuard acquisition.
- The scheduler did not fully propagate the submitted shift horizon into destination evidence acquisition. CrewClock now measures reachable destination windows before it credits a schedule move with lower SHHCH.

Regression coverage protects these paths, including the rule that unknown destination evidence is never converted to zero.

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

The latest fully executed engineering gate passed:

```text
pytest: 152 passed
Vitest: 50 passed
typecheck: PASS
lint: PASS
build: PASS
secret scan: PASS
browser acceptance: PASS
```

The final terminal-state classification refinement is covered in `src/demo/decision.test.ts`; rerun the gate above before submission lock.

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