# CrewClock exceedance metric lock

CrewClock's hero metric is Scheduled High-Heat Crew-Hours (SHHCH). Its only
duration source is a FortyGuard heatmap with `analytic_type="exceedance"`.
`env_params` is optional, time-matched context and is never a duration,
spatial-ranking, WBGT, or SHHCH source.

## Calculation contract

```text
FortyGuard exceedance windows
  → area-weight tiles over the task workface polygon
  → intersect that window with the task's scheduled interval
  → weighted exceedance hours × crew size
  → sum outdoor task contributions
```

The same temporal window must support both the exceedance duration and the
scheduled task overlap. A whole-shift duration cannot be multiplied by an
arbitrary scheduled crew count. A task scheduled from 12:00–14:00 with two
hours of exceedance and five people contributes 10 crew-hours; moving it to a
zero-exceedance 06:00–08:00 window contributes zero.

The deterministic implementation is `calculate_scheduled_high_heat_crew_hours`
in `src/fortyguard_agent/shhch.py` and the equivalent demo implementation in
`src/demo/shhch.ts`. It preserves per-task provenance and fails closed for
missing workfaces, uncovered intervals, stale/invalid evidence, wrong units,
unsupported thresholds, and absent schedule-aligned windows.

## Threshold semantics

`project_thermal_trigger` is a project-configured threshold in FortyGuard's
modeled heatmap temperature quantity. It is not a heat-index or WBGT threshold.
Employer heat-index rules, breaks, acclimatization, onsite verification,
escalation, workload, PPE, and worker-condition controls remain independent
feasibility and policy rules.

## Current Phoenix evidence

The cached Phoenix set contains TCM, time-of-measure, persistence, and optional
environmental context. It does not contain Phoenix schedule-aligned exceedance
windows. A separate cached exceedance validation response is a different AOI
and is not substituted into the Phoenix sample. Therefore usable
`CACHED_EXCEEDANCE_EVIDENCE = NONE` for the canonical Phoenix fixture. The
acquisition run is recorded as `PARTIAL` because it has failure evidence but
zero valid windows; the demo emits no fabricated SHHCH number until valid
windows are inserted.

On 2026-08-21, two exact historical requests for the first canonical window
(`2025-07-15`, Phoenix, `06:00–08:00`, `filter_type=2`) reached terminal
`Failed` without a result and consumed zero credits. A single discriminating
TCM request using the same AOI/date/window also reached terminal `Failed` with
an exact retained poll history and no credit change. The sanitized activity
records are in `evidence/crewclock-canonical-exceedance/`, with the conclusion
in `docs/CREWCLOCK_EXCEEDANCE_FORENSICS.md`. The remaining four windows were
not requested. This is a provider range-path validation gap, not evidence that
the interval had zero exceedance.

Future forecast status remains `FORTYGUARD_FUTURE_FORECAST_STATUS =
NOT_DEMONSTRATED` because the retained Phoenix future probes completed with
zero cells.
