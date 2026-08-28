# CrewClock Judge Notes

## One-line pitch

CrewClock helps construction superintendents adjust an upcoming shift around hyperlocal modeled heat without breaking the schedule.

## What the AI agent does

The AI agent decides whether the shift needs thermal investigation. It selects the workfaces and time windows that need evidence. Those validated choices control the FortyGuard requests.

The AI does not calculate SHHCH, generate final schedule times, approve a recommendation, or override hard constraints.

## What deterministic code does

Deterministic code validates the baseline, calculates SHHCH, determines reachable scheduling windows, generates alternatives, checks hard constraints, and verifies the exact approved result.

This split is intentional. The AI controls the investigation. Deterministic code controls arithmetic and operational correctness.

## Why FortyGuard matters

FortyGuard is the modeled environmental evidence source. CrewClock binds evidence to the selected workface and time window, then connects it to the actual task schedule and crew size.

CrewClock also measures reachable destination windows. A task is never credited with lower SHHCH unless its destination has decision-grade evidence. Unknown evidence is not zero.

## Primary fresh-future proof

San Diego, California — August 28, 2026:

- Fresh live FortyGuard evidence: **PASS**
- Baseline SHHCH: **18 crew-hours**
- Proposed SHHCH: **9 crew-hours**
- Reduction: **50%**
- Flexible tasks retimed: **3**
- Fixed tasks changed: **0**
- Constraint families: **6/6 → 6/6**
- Human approval: **PASS**
- Final deterministic reverification: **PASS**
- Destination evidence coverage: **PASS**

This is the complete same-day future product path through the normal browser UI.

## Additional positive proof

Palm Springs: **13 → 4 SHHCH**, three tasks retimed, 6/6 constraints, approval and final reverification passed. Evidence was previously acquired live and reused after an exact identity match.

Miami: **21.09 → 5.03 SHHCH**, about a 76% reduction, with 6/6 constraints before and after.

## What final testing fixed

Three defects were found and fixed before submission:

1. Live polling could stop after 90 seconds. It now allows up to 600 seconds for asynchronous FortyGuard activities.
2. Baseline validation happened too late. All six constraint families now pass before AI orchestration or evidence acquisition.
3. Destination evidence did not cover the complete reachable shift horizon. CrewClock now acquires the evidence needed to compare origin and destination windows truthfully.

Regression coverage protects these paths.

## What happens when the full shift is modeled above the trigger?

CrewClock does **not** call the schedule optimal.

If complete evidence shows the configured modeled-temperature trigger across the full measured shift window for every investigated workface, CrewClock says:

> **The full measured shift remains above the configured trigger.**

It explains that retiming inside that shift cannot reduce SHHCH. CrewClock does not make a safety determination. The superintendent uses the employer heat plan to decide whether to delay, modify, or keep the work.

If full-shift trigger coverage is not proven, CrewClock uses the narrower result: **No lower-SHHCH schedule was found within this shift.**

## Why the metric is valid for this MVP

SHHCH means Scheduled High-Heat Crew-Hours. It measures scheduled crew-hours that overlap the configured modeled high-heat window.

It is a schedule-placement metric. It is not a medical exposure measure, a heat-dose measure, a prediction of injury, or a statement of OSHA compliance.

## What happens when evidence is unavailable?

CrewClock preserves the current schedule and reports that evidence is unavailable. It does not convert missing evidence into zero. It does not fabricate a recommendation.

## Why this is not a weather dashboard

A weather dashboard reports conditions. CrewClock connects workface-level environmental evidence to crews, tasks, fixed commitments, qualifications, dependencies, deadlines, employer controls, and reachable schedule alternatives.

## Why a superintendent still matters

CrewClock is planning support. The superintendent can approve the verified recommendation or keep the current shift. CrewClock does not self-approve.

## Current MVP boundary

New sites require latitude, longitude, and approximate site dimensions. CrewClock does not include address geocoding or an interactive map picker in this MVP.