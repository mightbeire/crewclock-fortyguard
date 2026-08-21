# CrewClock FortyGuard contract

## Official source audit

Audited current `main` of `FortyGuard-Tech/temperature-api-quickstart` at local commit `f6de12d`, plus the current API docs and known-limitations/release-notes pages on 2026-08-21.

Primary references: [official quickstart](https://github.com/FortyGuard-Tech/temperature-api-quickstart), [heatmap contract](https://docs-api.fortyguard.com/docs/create-heatmap), [environmental parameters](https://docs-api.fortyguard.com/docs/environmental-parameters), and [known limitations](https://docs-api.fortyguard.com/docs/limitations).

Relevant current contract:

- Authentication uses the `api-key` header.
- Coverage is United States only.
- Heatmaps use a closed GeoJSON polygon AOI and 60/80/100 m granularity. Basic heatmap AOI is limited to 10 mi².
- Heatmap `filter_type=1` is a single hour; forecast heatmaps are documented through `now + 12 hours`.
- Submissions are asynchronous: POST returns an `activity_id`, then status is polled. A transient status 404 immediately after POST is eventual consistency and must be retried politely.
- `tcm` tiles contain temperature fields in °C in the current API docs and successful cached responses. Analysis maps use `properties.value`; `stats_data.units` is `hour` for `time_of_measure`, `exceedance`, and `persistence`.
- `exceedance` is a count of hours and `persistence` is the longest continuous run; neither is degree-hours.
- `time_of_measure` is UTC hour-of-day and must be converted before comparison with Phoenix schedules.
- `env_params` requires a temperature anchor and returns time-aligned arrays with metadata timestamps. Its range response keeps the supplied anchor across hours; it is not a diurnal air-temperature forecast.

The official material does not define whether heatmap request clock strings
(`start_time`/`end_time`) are interpreted as project-local time or UTC. The
Phoenix adapter therefore preserves the schedule's explicit
`America/Phoenix` meaning for local comparisons but records the provider
request-time conversion as `UNKNOWN` until the API specifies it. The UTC
label applies to returned `time_of_measure` values, not automatically to
request clock strings.

## Discrepancies that affect CrewClock

1. The README's “future dates unsupported” note conflicts with the current API docs' explicit heatmap `now + 12 hours` forecast window. CrewClock follows the live/current contract and guards `+12h` locally.
2. An older `fortyguard/client.py` docstring says TCM tiles are °F, while current docs and cached live responses are °C. CrewClock requires/asserts °C and never trusts the stale comment.
3. Old examples read `properties.temperature`; current analysis schemas use `properties.value`. CrewClock asserts the requested analytic schema.
4. The quickstart's own parcel guidance documents the anchored `env_params` overnight artifact and coarser weather grid. CrewClock therefore uses heatmap tiles for spatial discrimination and env_params only for selective context.

## Safe wrapper rules

Before submission CrewClock checks endpoint allowlist, U.S. coverage, AOI area, granularity, timestamp horizon, cache/request hash, estimated cost, per-run cap, and remaining credits. Successful responses are normalized into cache records containing request, retrieval/source timestamp, activity ID when safe, result hash, schema version, units, and provenance. Secrets are never cached.

Premium satellite, street-view, and heat-intelligence endpoints are not part of the canonical MVP path.

## Range-path forensic result

On 2026-08-21, the exact historical Phoenix `filter_type=2` `06:00–08:00`
TCM control used the bundled contract serializer and the previously
successful AOI/date. It was accepted, remained `Processing` through the
recorded poll window, then returned terminal `Failed` with no result and no
credit change. This control failure means the prior exceedance failures are
not isolated to the exceedance analytic. Full sanitized evidence is in
`docs/CREWCLOCK_EXCEEDANCE_FORENSICS.md` and the corresponding evidence JSON.

## Request-time calibration result

Two preselected historical Phoenix `filter_type=1`, `analytic_type=tcm`
requests (`14:00` and `22:00`) were accepted but their status retrievals ended
with HTTP 500 `Internal server error` and no result. Each consumed 4,220
credits. Because neither returned valid cells, request-time semantics remain
`AMBIGUOUS` with low confidence and the Phoenix local-to-request mapping is
unresolved. See `docs/CREWCLOCK_REQUEST_TIME_CALIBRATION.md`.
