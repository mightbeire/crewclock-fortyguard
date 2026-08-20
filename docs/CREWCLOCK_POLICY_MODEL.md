# CrewClock policy model

The employer heat plan is an input to feasibility, not a hidden UI badge and not a legal rules engine.

## Policy identity

`policy_id`, version, name, source (`EMPLOYER_CONFIGURED`, `DEMO_POLICY`, or `PUBLIC_GUIDANCE_REFERENCE`), effective date, metric used, initial trigger, high trigger, and units.

## Controls and work planning

The model supports a required control tier, break frequency/duration, preferential movement of specified work types, onsite verification, superintendent review, and escalation for fixed work. Tasks carry indoor/outdoor class, polygon workface, duration, crew, physical-demand category when the employer needs it, fixed/movable status, and manual-review flags.

## Acclimatization

Only operational planning categories are supported: `established`, `new_or_returning`, and `unknown`. CrewClock stores no diagnoses, symptoms, health conditions, or medical data.

## Breaks

Breaks are reserved intervals owned by deterministic scheduling. If a mandatory recovery interval cannot fit between the candidate's task intervals and deadlines, the candidate fails. The UI may explain the failure but cannot turn it into a passing badge.

Public guidance can inform a demo policy's shape, but is never silently presented as an employer obligation. CrewClock does not claim OSHA certification, OSHA compliance, or that a proposed federal rule requires a particular schedule.
