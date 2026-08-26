# CrewClock canonical FortyGuard gate

Date of acquisition: 2026-08-26. Frozen product baseline:
`88d1653c49cc096b64a4dd52e085ce4c3976e57a`.

FortyGuard's resolved operational semantics were applied: heatmap request
times are local at the AOI, Phoenix is `America/Phoenix` (UTC−7, no DST), and
the project trigger remains the existing `32.0 °C` modeled-temperature
threshold with direction `above`.

The first fresh sanity request used the existing Phoenix AOI, historical date
`2025-07-15`, `filter_type=2`, `06:00–08:00`, `granularity=100`, and
`analytic_type=exceedance`. Activity
`60568d12-10d6-478b-af83-7d197c1eec37` completed with one usable cell,
`n_cells=1`, `units=hour`, and value `2.0`. Four additional non-overlapping
windows through `16:00` completed successfully. No environmental-parameter
request was made. The bounded run used 5 successful heatmap jobs and 21,100
credits, from 225,600 used / 1,774,400 remaining to 246,700 used /
1,753,300 remaining.

The provider-backed workface/time matrix is complete for the five requested
time windows and preserves every activity ID and result hash. Provider tiles
overlap all four declared workfaces; the package reports overlap ratios and
does not claim full-face coverage where the returned tile footprint is
partial.

Using the frozen area-weighted tile intersection and schedule-aligned
exceedance union, the real canonical baseline is:

- Total SHHCH: `91.5`
- Movable SHHCH: `67.0`
- Fixed SHHCH: `24.5`

The deterministic scheduler considered 144 candidates, rejected 102, and
found 42 feasible alternatives. All feasible alternatives have the same
canonical qualifying-window cost because all five windows report 2.0
exceedance hours. No strict improvement exists, so the truthful result is
`REAL_NO_FEASIBLE_IMPROVEMENT`; no proposed schedule is accepted or shown as
an improvement. The baseline’s synthetic employer-break policy family is
false, while the generated feasible alternatives pass all six hard-constraint
families.

The canonical UI remains unchanged. Its existing synthetic-positive rehearsal
remains explicitly synthetic; the real result is packaged separately under
`evidence/fortyguard-canonical-phoenix/`.
