# CrewClock request-time calibration

Date: 2026-08-21. Historical control: Phoenix, 2025-07-15. No Groq,
`env_params`, `filter_type=2`, or canonical ten-hour calls were made.

## Zero-call conclusion

The current official heatmap documentation defines `start_time` and
`end_time` as `HH:MM` request fields and identifies `time_of_measure` output
as UTC hour-of-day, but it does not define the timezone of heatmap request
clock strings. The bundled quickstart and client code also omit a timezone or
offset from the request payload. Therefore the documented request timezone is
`UNSPECIFIED`; UTC output semantics cannot be applied to request clocks.

## Historical reference

The calibration used Phoenix Sky Harbor historical July 2025 observations as
temporal corroboration only. The reference shows the expected broad pattern
for July 15: cooler overnight/early morning conditions and substantially
hotter afternoon conditions. It is not FortyGuard TCM and is not used for
SHHCH. [NCEI describes its local climatological data](https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data) as hourly observations
from ASOS/AWOS and related station systems; the date-specific Phoenix summary
was taken from the [Phoenix Sky Harbor historical weather page](https://www.timeanddate.com/weather/usa/phoenix/historic?month=7&year=2025).

## Preselected calls

The pair was selected before either response: request clocks `14:00` and
`22:00`. Under a Phoenix-local interpretation these should contrast afternoon
heat with late-evening cooling. Under a UTC interpretation they would roughly
correspond to Phoenix `07:00` and `15:00`, reversing the contrast.

| Request clock | Activity | Outcome | Cells / AOI mean | Credits |
|---|---|---|---|---:|
| 14:00 | `5ad75edf-2f9b-4631-b757-a0d212ae2b51` | Accepted; 158 polls; final HTTP 500 `Internal server error` | unavailable; no result | +4,220 |
| 22:00 | `3f1ba537-1bb9-4645-8c32-de8e454ea51a` | Accepted; 160 polls; final HTTP 500 `Internal server error` | unavailable; no result | +4,220 |

Exact sanitized payloads, request hashes, status histories, and credit
snapshots are retained under
`evidence/crewclock-request-time-calibration/`. Failed status retrieval and
missing results do not establish request-time semantics. The two activities
also cannot support spatial workface comparison.

## Decision

`REQUEST_TIME_SEMANTICS = AMBIGUOUS` with `TIME_SEMANTICS_CONFIDENCE = LOW`.
`PROJECT_TIME_MAPPING = UNRESOLVED` and
`CANONICAL_10_CALL_CAPTURE_AUTHORIZED = NO`. The native FortyGuard
`analytic_type=exceedance` architecture remains primary; hourly TCM remains a
contingency fallback only and is not implemented.
