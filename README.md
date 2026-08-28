# CrewClock

**Agentic decision intelligence for construction operations.**

CrewClock helps construction superintendents adjust an upcoming shift around hyperlocal modeled heat without breaking the schedule.

**Primary track:** Agentic AI  
**Secondary track:** Industrial & Enterprise  
**Team:** `btn operations`

## What it does

Before crews deploy, CrewClock reviews the shift, decides which outdoor workfaces and time windows need investigation, acquires bounded FortyGuard evidence, calculates schedule-specific thermal overlap, tests feasible alternatives against operational constraints, and presents the least-disruptive verified option for superintendent approval.

CrewClock is deliberately not a chatbot-first product. The agent investigates and orchestrates; deterministic code owns arithmetic, scheduling, verification, evidence identity, and final approval integrity.

## Architecture

```text
Existing shift
  ↓
CrewClock agent
  ↓
Validated workface + time-window investigation plan
  ↓
FortyGuard evidence acquisition
  ↓
Deterministic SHHCH calculation
  ↓
Deterministic constrained scheduler + verifier
  ↓
Structured agent explanation
  ↓
Superintendent approve / keep current
  ↓
Final deterministic re-verification
```

### What the AI decides

The model can decide whether investigation is needed, which validated workfaces and schedule windows to inspect, whether the returned evidence is sufficient, whether bounded follow-up evidence is needed, whether to continue or abstain, and how to explain the verified result.

The model cannot author the authoritative schedule, change SHHCH arithmetic, forge FortyGuard evidence, bypass feasibility checks, self-approve, or bypass final deterministic verification.

Production inference uses Groq first with TokenRouter failover. Provider failure preserves the current shift.

## Why FortyGuard matters

CrewClock does not treat weather as a single city-wide number. It binds modeled evidence to the actual project AOI, selected workface polygons, and schedule-relevant local-time windows. It then intersects qualifying modeled exceedance duration with outdoor task intervals and crew headcount.

The hero metric is **Scheduled High-Heat Crew-Hours (SHHCH)**.

SHHCH is a schedule-placement metric, not physiological exposure, heat dose, injury risk, WBGT, or OSHA compliance.

## Real evidence

### Real unseen-site thermal improvement — Miami

A preregistered live FortyGuard test on **Miami, Florida · 2025-08-05** produced:

- baseline SHHCH: **21.086303**
- proposed SHHCH: **5.032994**
- tasks retimed: **C2 and C3**
- constraint families: **6/6 → 6/6**
- human approval: **PASS**
- final deterministic re-verification: **PASS**

The initial execution had no cache reuse.

### Real canonical historical replay — Phoenix

The saved canonical FortyGuard replay produced **91.5 → 91.5 SHHCH** while correcting an employer-configured operational constraint from **5/6 → 6/6** by moving G4 to 13:30. CrewClock correctly makes **no thermal-improvement claim** for this case.

### Synthetic capability demo

The clearly labeled synthetic capability demo produces **39 → 20 SHHCH**, retimes **7 tasks**, and preserves **6/6** modeled constraint families. It exists to make the end-to-end behavior easy to inspect without presenting synthetic evidence as real FortyGuard output.

## Fresh-site generalization

CrewClock has also been exercised on previously unseen U.S. project inputs with no preloaded cache. The final surgical validation used **Albuquerque, New Mexico**: the real agent selected three workfaces and five two-hour windows, those exact selections controlled the live FortyGuard requests, five activity IDs were created, and the truthful result was **0 → 0 SHHCH / no improvement**.

A provider-outage test also confirmed fail-closed behavior: when inference is unavailable, CrewClock preserves the current plan and does not fabricate evidence or verifier events.

## Run locally

### 1. Configure environment

Copy `.env.example` to `.env` and add your own server-side credentials. Never commit `.env`.

Required live integrations:

- `FORTYGUARD_API_KEY`
- `GROQ_API_KEY`
- `TOKENROUTER_API_KEY`

### 2. Install and start

```bash
npm install
npm run build:runtime
npm run dev:api
```

In a second terminal:

```bash
npm run dev
```

### 3. Validate

```bash
python -m pytest -q
npm run test:ui
npm run typecheck
npm run lint
npm run build
```

Final frozen engineering candidate validation:

- **145 pytest tests passed**
- **47 Vitest tests passed**
- TypeScript typecheck: **PASS**
- ESLint: **PASS**
- production build: **PASS**
- tracked-secret scan: **PASS**

## Evidence and technical documentation

Start with:

- [`PROJECT.md`](PROJECT.md) — product scope and claim boundary
- [`docs/CREWCLOCK_ARCHITECTURE.md`](docs/CREWCLOCK_ARCHITECTURE.md) — agent / deterministic-system architecture
- [`docs/CREWCLOCK_AGENT_BOUNDARY.md`](docs/CREWCLOCK_AGENT_BOUNDARY.md) — what the model may and may not control
- [`docs/CREWCLOCK_DATA_MODEL.md`](docs/CREWCLOCK_DATA_MODEL.md) — schedule and evidence model
- [`docs/CREWCLOCK_MEASUREMENT.md`](docs/CREWCLOCK_MEASUREMENT.md) — SHHCH semantics
- [`docs/CREWCLOCK_DEMO_SCRIPT.md`](docs/CREWCLOCK_DEMO_SCRIPT.md) — demo flow
- [`evidence/`](evidence/) — saved validation evidence and provenance

## Safety and claim boundary

CrewClock is an operations-planning MVP. FortyGuard modeled temperature evidence is not WBGT and does not certify worker safety. Onsite measurement, employer policy, PPE, workload, acclimatization, worker condition, professional judgment, and stop-work authority remain outside CrewClock's decision authority.

## Frozen engineering candidate

Engineering freeze: `db8a0cb45d72b396f6abca39cf28f3922f9c13fb`

Submission packaging may change documentation or remove non-product artifacts, but the frozen product behavior should not change before judging.
