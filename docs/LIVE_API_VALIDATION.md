# Live FortyGuard API validation

Date: August 19, 2026. Account: Hackathon plan. The API key was read from the ignored `.env` file but was never printed, committed, or stored in the cache.

## Usage guardrail

The non-billable usage check reported 2,000,000 total credits, 2,000,000 remaining, and 0 used before analysis testing. The first validation pass used 29,960 credits. A second, deliberately bounded discovery pass used 174,540 additional credits: eight geography pairs plus seven targeted heat/env analyses. The current usage reading is 204,500 used and 1,795,500 remaining. The scripts under `scripts/` reuse successful cache files and do not repeat identical paid requests.

| Test | Request shape | Result | Measured credit delta | Cache |
|---|---|---|---:|---|
| `/v1/heatmap` `tcm` | Tiny closed GeoJSON polygon, 2025-07-15, `filter_type=3`, `granularity=100` | PASS | 4,220 | `heatmap.json` |
| `/v1/env_params` | One point, 2025-07-15, `filter_type=3`, three requested analyses | PASS | 2,900 | `env_params.json` |
| `/v1/satellite` | Same tiny AOI/date, segmentation request | PASS; completed | 14,400 | `premium_probe.json` |
| `/v1/heatmap` `exceedance` | Approximately 1 km × 1 km AOI, threshold 32°C, full day | PASS | 4,220 | `heatmap_exceedance.json` |
| `/v1/heatmap` `tcm` multi-tile | Same approximately 1 km × 1 km AOI, full day, granularity 100 | PASS | 4,220 | `heatmap_multitile_tcm.json` |

Credit deltas are empirical observations for these requests, not a universal price list. Usage-report calls were used to measure before/after state; no separate analysis delta was observed for the measurement calls.

## Heatmap schema and behavior

The completed result had top-level keys `map_data` and `stats_data`. `map_data.features` contained GeoJSON features whose properties were:

- `tile_id`
- `average_temperature`
- `max_temperature`
- `min_temperature`

The tiny test returned one tile. Its geometry spanned approximately 99 m east-west by 105 m north-south, consistent with the requested 100 m granularity. The full-day `filter_type=3` result is a daily summary per tile: it does not contain a 24-value hourly sequence in each feature. The live values were approximately 21.28°C average, 32.48°C maximum, and 15.02°C minimum for the tested tile. `stats_data` included temperature distributions and summary statistics.

The live exceedance response returned 96 features with `tile_id` and `value`, and `stats_data` included `analytic_type`, `n_cells`, `min`, `mean`, `max`, and `units="hour"`. Every tile in that test returned one hour above the 32°C threshold.

The 96-tile `tcm` test returned 96 features. Across that AOI/date, average-temperature values ranged only from 21.2397°C to 21.2858°C, maximum-temperature values from 32.4652°C to 32.4807°C, and minimum-temperature values from 14.9291°C to 15.0225°C. This is useful falsification evidence: the selected live test does not support strong spatial ranking.

## Environmental-parameter schema and behavior

The completed result had top-level keys `metadata` and `locations`. Metadata included `time_range`, `timestamps`, `timezone`, and `timezone_offset_hours`. Each location included `lat`, `lon`, `elevation`, `temperature`, `parameters`, and `solar_irradiance`.

The returned timestamp array contained 24 hourly values from midnight through 23:00 local time on 2025-07-15. The tested request named `apparent_temperature_celsius`, `relative_humidity_percent`, and `wet_bulb_temperature_celsius`, but the account returned a broader set including air-quality fields, cloud cover, CO2, heat index, methane, precipitation, and the requested fields. Each returned parameter array had 24 values. Solar irradiance included `ghi`, `dni`, and `dhi`.

The live apparent-temperature profile used by the finalist spikes was:

```text
[16.4, 16.3, 15.9, 15.5, 14.9, 14.9, 15.3, 17.0,
 20.0, 23.5, 27.5, 30.6, 32.7, 33.5, 33.0, 31.6,
 29.3, 28.5, 25.9, 22.6, 19.5, 17.5, 16.3, 15.8]
```

The heatmap maximum and environmental temperature anchor were consistent for the tested point/date. This validates schema alignment, not a universal equivalence for every endpoint or filter.

## Premium capability

`/v1/satellite` completed successfully and returned segmentation content, dimensions, legend, mode, processing time, request ID, and segment data. Satellite segmentation is therefore verified for this Hackathon account. Street-view segmentation and heat-intelligence report access were not tested and remain `NONE` for capability planning.

## Second-wave geography and analysis validation

The eight-site matrix and follow-ups are recorded in `docs/DEMO_GEOGRAPHY_RESEARCH.md`. Each geography pair was one 100 m full-day `tcm` heatmap and one satellite segmentation call. The most useful paired responses were Las Vegas (high heat plus building/road/tree labels), Phoenix (high heat plus useful temporal analysis), and Los Angeles (rail label plus consistent 15:00 UTC peak/7-hour persistence). Zero-cell heatmap responses in Houston, DFW, New York, and Portland are retained as coverage/uncertainty evidence.

The live environmental follow-ups also exposed a schema warning: Atlanta `heat_index_celsius` values reached 77.9, while apparent temperature stayed within 26.6–41.3°C and relative humidity reached 97.6%. This field is not trusted as Celsius until clarified. Satellite `image_year=2026` was returned for a 2025 request date; provenance keeps the two dates separate.

## Finalist validation boundary

`scripts/run_live_spikes.py` reran all three first-wave finalist control loops from cached-live environmental profiles. `scripts/run_challenger_spikes.py` then ran Surface-conditioned Road Repair Queue and RailHeat Patrol Sequencer against cached-live geography/analysis/satellite results. Every spike produced a trace and stopped at human approval. The resulting proxy improvements are real computations over cached-live values, but work orders, rail inventory, route/task data, and hard constraints are schema-faithful examples rather than field outcomes. Therefore the live run validates reusable agent behavior and evidence alignment, not safety certification or production deployment.
