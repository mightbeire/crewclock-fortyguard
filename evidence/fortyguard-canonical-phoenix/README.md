# CrewClock canonical Phoenix FortyGuard evidence

This package records the bounded live validation of the frozen CrewClock
scenario against FortyGuard's resolved backend.

## What was run

- Historical date: `2025-07-15`
- Request clock semantics: AOI-local time
- AOI timezone: `America/Phoenix` (Phoenix UTC−7, no DST)
- AOI: the existing validated Phoenix WGS84 polygon used by CrewClock
- Analytic: `exceedance`
- Trigger: `32.0 °C` modeled temperature, direction `above`
- Windows: `06:00–08:00`, `08:00–10:00`, `10:00–12:00`, `12:00–14:00`, `14:00–16:00`
- Granularity: `100 m`
- Environmental-parameter calls: `0`

One fresh sanity request completed first. Four additional non-overlapping
windows then completed. All five returned one usable polygon tile with
`stats_data.analytic_type=exceedance`, `units=hour`, `n_cells=1`, and value
`2.0` hours. The provider returned geometry overlapping each declared
workface; the transformed matrix retains the provider result hash and source
activity ID for every contribution.

## Result

The real canonical result is `REAL_NO_FEASIBLE_IMPROVEMENT`.

The frozen area-weighted SHHCH calculation produces:

- Baseline total: `91.5` crew-hours
- Baseline movable: `67.0` crew-hours
- Baseline fixed: `24.5` crew-hours

The deterministic scheduler found `42` feasible alternatives after rejecting
`102` candidates. Because every covered canonical window reports the same
`2.0` qualifying exceedance hours and the existing objective cannot reduce the
result by retiming within the bounded shift, no candidate with a strict SHHCH
improvement was selected. No proposed plan is presented as an improvement.

The baseline itself fails the synthetic employer break-policy family, while
the generated feasible alternatives pass all six hard-constraint families.
This is preserved as evidence about the existing sample inputs, not hidden or
repaired in the canonical result.

## Files

- `request_manifest.json`: request, activity, status, geometry, coverage, and credit accounting.
- `phoenix_*.json`: sanitized raw usable FortyGuard responses and provenance.
- `workface_time_matrix.json`: task × scheduled interval × workface evidence transformation.
- `shhch_derivation.json`: baseline SHHCH contributions and fixed/movable split.
- `scheduler_comparison.json`: deterministic scheduler counts, constraint verification, and comparison.
- `canonical_outcome.json`: compact machine-readable outcome.
- `README.md`: scope and interpretation of this package.

No API key or secret is included. The canonical product demo remains the
clearly labelled synthetic-positive rehearsal; this package is the separate
real FortyGuard historical replay and does not claim physiological exposure
reduction, safety, or OSHA compliance.
