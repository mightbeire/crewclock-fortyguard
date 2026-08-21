# CrewClock zero-cell forecast forensics

Status: PARTIAL — the provider behavior is observed, but the earlier probe did not persist the exact POST timestamps or the first activity ID. This report records that loss instead of reconstructing it as fact.

## Scope and accounting

This run made no FortyGuard request. The two requests below belong to the prior controlled run. That run consumed 8,440 credits (4,220 each) and left the account at 1,787,060 credits. No API secret is included here.

## Side-by-side reconstruction

| Field | Request 1 | Request 2 |
|---|---|---|
| Endpoint | POST /v1/heatmap | POST /v1/heatmap |
| Request construction | Explicit now + 6h, floored to the hour; Phoenix fixed UTC−07 fallback after missing Windows tzdata | Explicit now + 5h, floored to the hour; Phoenix fixed UTC−07 |
| Recorded command launch | 2026-08-20T23:42:00.234Z | 2026-08-20T23:42:55.941Z |
| Exact HTTP POST timestamp | NOT PERSISTED | NOT PERSISTED |
| Requested local time | 2026-08-20 22:00, America/Phoenix | Reconstructed from launch-time code as 2026-08-20 21:00, America/Phoenix; exact payload was not persisted |
| Requested UTC time | 2026-08-21T05:00:00Z | Reconstructed from launch-time code as 2026-08-21T04:00:00Z; exact payload was not persisted |
| Lead time | Exact submission lead is not recoverable. Launch-bound target delta: 5:17:59.766 | Exact submission lead is not recoverable. Launch-bound target delta: 4:17:04.059 |
| start_date | 2026-08-20 | 2026-08-20 (code reconstruction) |
| start_time | 22:00 | 21:00 (code reconstruction) |
| filter_type | 1 (single hour) | 1 (single hour) |
| analytic_type | tcm | tcm |
| granularity | 100 m | 100 m |
| AOI | FeatureCollection → one Feature → closed Polygon; center (-112.018, 33.434), half-size 0.0005° | FeatureCollection → one Feature → closed Polygon; center (-112.018, 33.434), half-size 0.001° |
| AOI area | 0.003983 mi² | 0.015932 mi² |
| Coordinate order / CRS | GeoJSON [longitude, latitude], WGS84 assumption; no crs member | Same |
| Activity ID | NOT PERSISTED | 0fc7aa9d-6162-4038-8127-d8f2caf44b71 |
| Terminal status | Completed according to the prior run record; raw status body not saved | Completed according to the prior run record; raw status body not saved |
| Raw result | Exact body not saved; prior run records zero features and no usable TCM anchor | {"map_data":{"type":"FeatureCollection","features":[]},"stats_data":{"activity_id":"0fc7aa9d-6162-4038-8127-d8f2caf44b71","n_cells":0}} |
| map_data | Recorded present with zero features; exact raw body unavailable | Present, FeatureCollection, zero features |
| stats_data | Recorded as zero-cell result; exact keys unavailable | Present; activity_id, n_cells: 0 |
| Warning / error / message | No provider warning or error was captured; client raised locally only because no TCM anchor existed | No provider warning or error in captured result |
| Credits consumed | 4,220 | 4,220 |

The first activity ID, exact POST timestamps, and first raw status/result envelope cannot be obtained from the saved repository artifacts without querying the provider again. That is outside this run’s authorization.

## Horizon and timezone math

Phoenix is UTC−07 year-round for these dates. The target hours were well inside the documented now + 12h heatmap window, not at the boundary. The local-to-UTC conversions do not cross a date rollover in the requested local date: 22:00 → 05:00Z and 21:00 → 04:00Z on the following UTC date. The original first script did not use a guessed display string; it calculated an aware UTC target and converted it to Phoenix local time. The retry used the same offset explicitly.

Because the exact POST instants were not persisted, the exact lead at provider submission is unavailable. The launch-bound deltas above are the only reproducible timing calculations. Neither request was rejected for being over the horizon.

## AOI validation and historical control

Both AOIs are valid simple rectangles: closed rings, positive winding, longitude-first coordinate pairs, U.S. coordinates, and areas far below the Basic 10 mi² limit. The historical successful Phoenix AOI was [-112.01845, 33.43355] to [-112.01755, 33.43445], approximately 0.003226 mi², and overlaps the smaller failed AOI’s center. Its cached 100 m TCM response contains one tile with average_temperature, max_temperature, min_temperature, and tile_id.

The same local parser accepts that historical response and rejects the captured future empty response with heatmap_empty_feature_collection. Therefore:

AOI_AND_PARSER = VALID

This proves geometry and downstream parsing can work for the Phoenix site. It does not prove a future provider tile exists for a particular hour. The synthetic CrewClock workfaces are not provider-owned geometries; their inclusion is a local spatial decision and cannot be used to claim the provider returned coverage for them.

## Parser audit

The current official docs and current main quickstart agree that a TCM tile uses properties.average_temperature, min_temperature, and max_temperature; analysis heatmaps use properties.value with stats_data.units = hour. The successful cached Phoenix TCM response matches the TCM branch. The second future response is not a changed schema: it is a valid FeatureCollection with an empty features array and stats_data.n_cells = 0.

ZERO_CELLS_CONFIRMED_BY_RAW_RESPONSE = YES for Request 2. The same zero-cell fact is recorded for Request 1, but its raw body was not persisted; therefore Request 1 is confirmed by the prior run’s sanitized record, not independently re-read from a saved raw envelope.

The wrapper now treats any completed heatmap with an empty FeatureCollection as COMPLETED_BUT_EMPTY = INVALID_EVIDENCE; it does not cache it, commit credits locally, or allow downstream scheduling evidence to consume it.

## Forecast-contract finding

Current official heatmap docs say forecast heatmaps are supported up to 12 hours ahead, filter_type = 1 is the single-hour form, start_time is required, and tcm is a supported snapshot analytic. Current limitations say filter types 1/2/3 are supported, U.S. coverage is required, and completed tasks consume credits. The current quickstart README still contains a contradictory “future dates are unsupported” note, while the current docs explicitly describe heatmap forecasting. Recent official quickstart history corrected the TCM units and documented the analysis schema, but it does not document a successful future single-hour Phoenix example or define “Completed + zero cells” as a valid evidence state.

No official source found in the current docs, current quickstart, current quickstart history, or its zero-issue tracker explains why an accepted, completed forecast can return zero cells. The evidence supports a provider-side forecast availability/coverage gap or undocumented empty-result behavior, but it cannot distinguish those causes. It does not support blaming tcm, filter_type = 1, Phoenix coverage, timezone conversion, AOI validity, or our parser.

ROOT_CAUSE = Provider returned a completed empty forecast result for the requested Phoenix hour; the saved evidence cannot distinguish missing forecast coverage from undocumented provider empty-result behavior.

ROOT_CAUSE_CONFIDENCE = LOW for the underlying provider cause; HIGH for the observed empty-result fact.

## One proposed next probe — do not run in this report

Use one request only, in Phoenix, against the same validated historical AOI (not a new city):

    POST https://api.fortyguard.com/v1/heatmap
    polygon_aoi = the exact cached Phoenix FeatureCollection
    date_time.start_date = the current Phoenix local date
    date_time.start_time = the next whole local hour at submission, chosen at +1h to +2h lead
    date_time.filter_type = 1
    granularity = 100
    analytic_type = tcm

The request must be constructed from one captured UTC now, converted with America/Phoenix, and persisted before submission with the exact JSON, POST timestamp, activity ID, status envelopes, raw result, and before/after credit usage. Expected cost is approximately 4,220 credits. A pass requires Completed, a non-empty map_data.features array, valid TCM temperature fields in Celsius, a non-zero stats_data.n_cells, and at least one returned tile intersecting the AOI. A fail is either provider rejection or Completed with zero features/zero cells/invalid TCM schema; do not spend a second credit on a retry.

If this one probe passes, run the CrewClock decision-delta validation with that time-matched workface evidence. If it completes empty again, stop live spending and classify future Phoenix behavior as unreliable/unsupported for this use; demonstrate only with validated cached-live historical evidence and clearly label the absence of a live forecast decision delta. Never fabricate one.

## LLM readiness audit

The provider-neutral runtime is ready for a later real credential. The current OpenAI adapter requires only these configuration fields:

OPENAI_API_KEY

OPENAI_MODEL (optional; defaults to gpt-4.1-mini)

No credential value was printed, created, purchased, or used in this run. Gemini and Groq names are present as future configuration placeholders only; they are not wired to a live runtime in this repository.

## Official sources checked

- https://docs-api.fortyguard.com/docs/create-heatmap
- https://docs-api.fortyguard.com/docs/limitations
- https://docs-api.fortyguard.com/docs/quickstart
- https://github.com/FortyGuard-Tech/temperature-api-quickstart/commits/main
- https://raw.githubusercontent.com/FortyGuard-Tech/temperature-api-quickstart/main/README.md
- https://raw.githubusercontent.com/FortyGuard-Tech/temperature-api-quickstart/main/fortyguard/client.py
