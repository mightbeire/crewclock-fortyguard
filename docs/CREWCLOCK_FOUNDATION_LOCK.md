# CrewClock foundation lock

Status: `PARTIAL` for this run. The deterministic product, thermal, policy, and agent boundaries are frozen. A real current-future FortyGuard decision delta is not claimed because the bounded forecast probe returned empty heatmap cells and could not supply a valid time-matched environmental anchor.

## Frozen product model

CrewClock is an AI pre-shift operations agent for construction superintendents. It starts from an existing upcoming-shift plan, investigates only decision-relevant movable outdoor work, obtains guarded workface-level thermal evidence inside FortyGuard's supported horizon, asks deterministic code for feasible alternatives, verifies the result, and waits for superintendent approval.

It does not replace baseline planning, publish a plan automatically, measure worker physiology, or determine legal compliance.

## Frozen thermal model

- Primary FortyGuard signal: shared-AOI heatmap tiles (`tcm`, `time_of_measure`, `exceedance`, `persistence`) with asserted schema and units.
- Workfaces are polygons when practical; overlapping heatmap tiles are area-weighted. Point assignment is an explicit fallback only for genuinely point-like work.
- `env_params` is selective, time-matched environmental context. Its anchored range response is not a diurnal heat-index forecast and cannot produce the hero metric.
- `wet_bulb_temperature_celsius` is wet bulb, not WBGT.
- The hero metric is `scheduled high-heat crew-hours`, a schedule overlap metric derived from an employer trigger.

## Frozen policy model

The employer heat plan is explicit, versioned, configurable, and provenance-labelled. It includes triggers, controls, break/recovery requirements, task characteristics, operational constraints, and operational acclimatization categories (`established`, `new_or_returning`, `unknown`). No medical data is stored.

Mandatory breaks are scheduling constraints. A candidate that cannot reserve them fails verification.

## Frozen agent boundary

The LLM selects investigations, evidence windows, and tool calls; explains structured results; handles uncertainty; and requests approval. Deterministic code owns thermal overlap, polygon aggregation, scheduling, hard-constraint verification, metrics, cache/credit/horizon guards, replay, and post-approval verification.

## Current validation truth

`FUTURE_SINGLE_HOUR_ENV_PARAMS = AMBIGUOUS`: two valid future Phoenix heatmap calls completed but returned zero features, so no matching temperature anchor existed for an env_params call. This is an abstention state, not a threshold or fixture adjustment.
