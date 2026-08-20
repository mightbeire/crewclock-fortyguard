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

## Discrepancies that affect CrewClock

1. The README's “future dates unsupported” note conflicts with the current API docs' explicit heatmap `now + 12 hours` forecast window. CrewClock follows the live/current contract and guards `+12h` locally.
2. An older `fortyguard/client.py` docstring says TCM tiles are °F, while current docs and cached live responses are °C. CrewClock requires/asserts °C and never trusts the stale comment.
3. Old examples read `properties.temperature`; current analysis schemas use `properties.value`. CrewClock asserts the requested analytic schema.
4. The quickstart's own parcel guidance documents the anchored `env_params` overnight artifact and coarser weather grid. CrewClock therefore uses heatmap tiles for spatial discrimination and env_params only for selective context.

## Safe wrapper rules

Before submission CrewClock checks endpoint allowlist, U.S. coverage, AOI area, granularity, timestamp horizon, cache/request hash, estimated cost, per-run cap, and remaining credits. Successful responses are normalized into cache records containing request, retrieval/source timestamp, activity ID when safe, result hash, schema version, units, and provenance. Secrets are never cached.

Premium satellite, street-view, and heat-intelligence endpoints are not part of the canonical MVP path.
