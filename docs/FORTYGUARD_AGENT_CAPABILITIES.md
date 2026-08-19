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
