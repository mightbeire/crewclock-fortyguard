# CrewClock controlled live validation

Date: 2026-08-21. Geography: Phoenix, Arizona. No premium endpoint was called.

## Bounded capability probe

The probe attempted the smallest credible future-hour test: a valid Phoenix polygon AOI, a single-hour heatmap inside the documented +12h window, and a matching TCM anchor. The first request and one bounded diagnostic retry both completed but returned `map_data.features = []` and `stats_data.n_cells = 0`. Therefore no defensible Celsius anchor existed and `env_params` was not submitted.

Result: `FUTURE_SINGLE_HOUR_ENV_PARAMS = AMBIGUOUS`.

Live calls: `2` heatmap submissions. Measured successful cost: `4,220` credits each. Starting balance for this run: `1,795,500`. Used: `8,440`. Remaining: `1,787,060`. Hard run cap: `25,000`; respected.

## Canonical historical exceedance validation

The canonical Phoenix control date remains `2025-07-15`, with the previously
successful Phoenix AOI, a shared WGS84 AOI containing all four workfaces, and a
preconfigured `32.0 °C` FortyGuard modeled-temperature trigger. Two exact
`analytic_type=exceedance` requests for `06:00–08:00` using `filter_type=2`
reached terminal `Failed`. They consumed zero credits and returned no tiles.
The remaining four schedule-aligned windows were deliberately not requested;
the sanitized records are in `evidence/crewclock-canonical-exceedance/`.

Result: `CACHED_EXCEEDANCE_EVIDENCE = PARTIAL` for this validation run, with
`WINDOWS_VALID = 0/5`; no SHHCH value or schedule delta is derived.

### Filter-path diagnostic

Because the two exceedance failures retained no provider diagnostics, one
additional historical control was justified: the same AOI/date/window with
`analytic_type=tcm`. The request was accepted, produced 120 recorded status
responses, and ended `Failed` with no result. Credits remained unchanged. No
exceedance retest was made after this control failure, so the failure is not
isolated to the exceedance analytic. Request-time timezone semantics remain
unspecified by the official contract; CrewClock records conversion as
unknown rather than guessing UTC or local time.

## Decision-delta validation

The requested fair baseline-versus-FortyGuard run cannot claim a PASS from this evidence. The baseline can be computed from the same synthetic 14-task plan and employer trigger, but the live future FortyGuard run has no usable workface tiles and cannot produce a defensible FortyGuard plan. Result: `FORTYGUARD_DECISION_DELTA = FAIL`, reason: evidence unavailable/ambiguous, not a tuned threshold or cherry-picked cell.

The cached historical replay remains a deterministic product demonstration only. It is labelled `CACHED-LIVE FORTYGUARD`; tasks, crews, polygon workfaces, employer policy, and schedule are `SYNTHETIC OPERATIONAL INPUT`. No current Phoenix SHHCH comparison is demonstrated until all schedule-aligned exceedance windows validate.

## Truthful stopping rule

CrewClock remains useful without env_params and returns an explicit evidence-unavailable or insufficient-horizon state rather than inventing a recommendation. A future live decision-delta validation should be rerun only when a valid forecast heatmap returns non-empty, time-matched workface evidence.
