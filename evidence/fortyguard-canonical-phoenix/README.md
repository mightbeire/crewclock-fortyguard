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

The real canonical result is `REAL_FEASIBLE_OPERATIONAL_CORRECTION`.

The frozen area-weighted SHHCH calculation produces:

- Baseline total: `91.5` crew-hours
- Baseline movable: `67.0` crew-hours
- Baseline fixed: `24.5` crew-hours

The deterministic scheduler found `42` feasible alternatives after rejecting
`102` candidates. Because every covered canonical window reports the same
`2.0` qualifying exceedance hours, no candidate reduces modeled SHHCH. The
baseline nevertheless fails the employer break/recovery control, so CrewClock
selects the least-disruptive feasible correction: `G4 → 13:30` (60 minutes of
disruption), with `91.5 → 91.5` SHHCH and `5/6 → 6/6` hard-constraint families.
This is an operational correction, not a thermal improvement.

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

No API key or secret is included. This Phoenix package is retained as historical
engineering evidence and a saved real-FortyGuard replay; it is not the final
submission hero run. The authoritative submission demonstration is the
**San Diego, August 28, 2026 fresh-live run (18 → 9 SHHCH)** in
[`../san-diego-final-positive/`](../san-diego-final-positive/), with the
**Tucson, August 29 fresh-live run (60 → 24 SHHCH)** in
[`../fresh-live-positive-2026-08-29/`](../fresh-live-positive-2026-08-29/) as
independent validation. None of these results claims physiological exposure
reduction, safety, or OSHA compliance.
