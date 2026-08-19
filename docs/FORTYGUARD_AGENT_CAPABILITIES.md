# FortyGuard capabilities useful to agents

## Capability map

| Capability | Verified input/output | Agent value | Cost protection |
|---|---|---|---|
| Heatmap | Polygon AOI, time filter, 60/80/100 m; GeoJSON tiles and stats | Agent chooses geography, resolution, and analysis type based on uncertainty | Cache by canonical request; investigate coarse-to-fine |
| `tcm` | Per-tile temperature snapshot and aggregate distribution | Establish baseline and compare candidate sites/windows | Reuse same AOI/date; do not re-request identical snapshot |
| `time_of_measure` | Peak hour per tile | Decide when a task or inspection should happen | Use after a hotspot is identified |
| `exceedance` | Hours over/under a Celsius threshold | Optimize duration, not just peak temperature | Prefer one range request over many hourly snapshots |
| `persistence` | Longest continuous threshold run | Detect sustained operational risk and escalation need | Use as a confirmation call after ranking |
| Environmental parameters | Time-aligned apparent temperature, heat index, wet bulb, humidity, precipitation, AQI/gases, solar irradiance | Investigate why a hotspot matters and distinguish heat/humidity/solar context | Request only needed analysis fields where plan allows |
| Activity status | Processing/Completed/Failed and result | Agent can poll, stop, retry once, and verify completion | Backoff and deadline; never busy-loop |
| Usage | Current/custom credit summaries | Agent can reserve budget and verify actual usage | Check before expensive exploration |
| Premium imagery/report endpoints | Segmentation and PDF report | Explain likely land-cover/scene drivers for a selected location | Spend only on top-N candidates and only if enabled |

## Important schema and data notes

- The handbook is authoritative for event scope: U.S.-only analysis, dates from `2021-01-01` through present, and forecasts up to 12 hours ahead. It also describes an approximate platform/LTM resolution of 2 m, but the API request contract exposes 60/80/100 m grid granularity. The live granularity-100 result measured approximately 100 m tiles; do not represent the API as 2 m output.
- Live `/v1/heatmap` `tcm` output contains `map_data.features[].properties` fields `tile_id`, `average_temperature`, `max_temperature`, and `min_temperature`, plus `stats_data` distributions. A full-day request is a daily summary per tile, not an hourly sequence. Live `exceedance` output used `properties.value` and `stats_data.units = "hour"`.
- Live `/v1/env_params` returned `metadata`, `locations`, and 24 hourly timestamps. Each location included coordinates/elevation, temperature, parameters, and solar irradiance; the tested request asked for three analyses but the account returned a broader parameter set. Do not rely on field filtering until confirmed for the target plan/request.
- The live Premium probe completed satellite segmentation. Street-view and heat-intelligence access were not tested and are not product dependencies.
- Empirical credit deltas for the cached validation run were: heatmap `tcm` 4,220; env params 2,900; satellite segmentation 14,400; exceedance 4,220; multi-tile heatmap `tcm` 4,220. See `docs/LIVE_API_VALIDATION.md` for request shapes and limits.
- Current official docs describe `tcm` as Celsius and analysis heatmaps as hourly units. The older vendored quickstart says some tcm output is Fahrenheit in prose; cached JSON values look like Celsius. The toolkit does not convert values silently and preserves provenance.
- `env_params` requires a temperature anchor. The local notebook notes that heat index can become a humidity-sensitivity curve at a fixed anchor, not a diurnal air-temperature forecast. For ranking sites, use heatmap layers; use env params for context.
- Spatial intelligence is tile-based, so parcel/asset joins need overlap-aware or documented nearest-tile logic. Do not claim parcel-level precision below the selected granularity.
- The account and local notes support U.S. examples; the final product should stay inside the verified geographic coverage until a live location check is approved.

## Agent tool contracts

All tool results return:

1. normalized data;
2. source (`live`, `cached`, `sample`, `derived`, `heuristic`, or `mock`);
3. endpoint/request hash/activity ID where available;
4. retrieval timestamp;
5. assumptions;
6. a bounded error string when unsuccessful.

The agent must distinguish API measurements from derived metrics and heuristic recommendations. `calculate_exposure_metric` is deliberately named a proxy and is not a medical or regulatory exposure model.

## Sources

[Heatmap API](https://docs-api.fortyguard.com/docs/create-heatmap), [Environmental Parameters API](https://docs-api.fortyguard.com/docs/environmental-parameters), [Status API](https://docs-api.fortyguard.com/docs/check-status), [Satellite Segmentation](https://docs-api.fortyguard.com/docs/satellite-view-segmentation), [Street View Segmentation](https://docs-api.fortyguard.com/docs/street-view-segmentation), [Heat Intelligence](https://docs-api.fortyguard.com/docs/heat-intelligence), [Quickstart](https://docs-api.fortyguard.com/docs/quickstart).

Live evidence and sanitized cache: `docs/LIVE_API_VALIDATION.md` and `.agent_cache/live_validation/`.
