# CrewClock Judge Notes

## One-line pitch

CrewClock helps construction superintendents adjust an upcoming shift around hyperlocal modeled heat without breaking the schedule.

## What the AI agent does

The AI agent decides whether the shift needs thermal investigation. It selects the workfaces and time windows that need evidence. Those validated choices control the FortyGuard requests. The agent also explains the verified result and can abstain when evidence is insufficient.

The AI does not calculate SHHCH, generate final schedule times, approve a recommendation, or override hard constraints.

## What deterministic code does

Deterministic code validates inputs, calculates SHHCH, generates schedule alternatives, checks hard constraints, and verifies the approved result.

This split is intentional. The AI controls the investigation. Deterministic code controls arithmetic and operational correctness.

## Why FortyGuard matters

FortyGuard is the modeled environmental evidence source. CrewClock binds the evidence to the selected workface and time window, then connects that evidence to the actual task schedule and crew size.

Without usable evidence, CrewClock does not create a recommendation.

## Final positive proof

Palm Springs, California:

- SHHCH: **13 → 4 crew-hours**
- Flexible tasks retimed: **3**
- Constraint families: **6/6 → 6/6**
- Human approval: **PASS**
- Final deterministic verification: **PASS**
- Evidence: previously acquired live FortyGuard evidence, reused after an exact identity match

## Why the metric is valid for this MVP

SHHCH means Scheduled High-Heat Crew-Hours. It measures scheduled crew-hours that overlap the configured modeled high-heat window.

It is a schedule-placement metric. It is not a medical exposure measure, a heat-dose measure, a prediction of injury, or a statement of OSHA compliance.

## What happens when no change is useful?

CrewClock keeps the current schedule.

A no-change result is valid when no lower-SHHCH schedule can satisfy the hard constraints.

## What happens when evidence is unavailable?

CrewClock preserves the current schedule and reports that evidence is unavailable. It does not convert missing evidence into zero. It does not fabricate a recommendation.

## Why this is not a weather dashboard

A weather dashboard reports conditions. CrewClock turns workface-level evidence into a construction scheduling decision. It connects the evidence to crews, tasks, fixed commitments, qualifications, dependencies, deadlines, and employer controls.

## Why a superintendent still matters

CrewClock is planning support. The superintendent can approve the verified recommendation or keep the current shift. CrewClock does not self-approve.

## Current MVP boundary

New sites require latitude, longitude, and approximate site dimensions. CrewClock does not include address geocoding or an interactive map picker in this MVP.
