# CrewClock filter-type 2 forensic result

Date: 2026-08-21. Scope: one historical Phoenix diagnostic after two prior
`analytic_type=exceedance` activities failed. No Groq request, forecast
request, `env_params` request, or premium request was made.

## Retained evidence

The two earlier activities are retained in
`evidence/crewclock-canonical-exceedance/failure_06_00_08_00.json`, but that
file was written after the fact and contains only the activity IDs and
terminal status. Their exact POST envelopes, submit responses, poll history,
timestamps, and provider diagnostic message were not persisted. The only
recoverable message is the terminal status `Failed`; the two retained
observations are not proof that the complete provider responses were byte
identical.

The new diagnostic is retained in
`evidence/crewclock-canonical-exceedance/diagnostic_filter2_tcm_06_00_08_00.json`.
It captured the exact submitted JSON, request SHA-256, submit response, 120
status responses, timestamps, final response, result absence, and credit
usage. The request was:

```json
{
  "polygon_aoi": "the existing Phoenix WGS84 FeatureCollection",
  "date_time": {
    "start_date": "2025-07-15",
    "start_time": "06:00",
    "end_time": "08:00",
    "filter_type": 2
  },
  "granularity": 100,
  "analytic_type": "tcm"
}
```

The POST was accepted with activity
`96b64e9c-21ec-46b9-a43b-41dba259e00a`. Every retained status response was
HTTP 200 with `error: false`; the activity remained `Processing` and then
returned `data.status = Failed`, `message = Failed`, and no result. Credits
were unchanged at `217160` used and `1782840` remaining.

## Contract and comparison

The bundled client correctly serializes the API contract as
`polygon_aoi`, `date_time`, `granularity`, and `analytic_type`. For an
exceedance request it adds top-level `threshold` in Celsius and `direction`.
The shared Phoenix AOI is byte-equivalent to the successful historical
`filter_type=3` TCM request in
`.agent_cache/live_geographies/phoenix_paved_industrial.json`; the date is
also `2025-07-15`. That known-good request does not use the `filter_type=2`
range path or a start/end time, so it cannot validate this range operation.

Official quickstart material documents `filter_type=2` as a same-day range
requiring `start_time` and `end_time`, and documents the analysis schema and
exceedance threshold/direction contract. It explicitly labels
`time_of_measure` values as UTC hour-of-day, but does not define the timezone
semantics of heatmap request clock strings. Therefore CrewClock records
request-time semantics as `UNSPECIFIED` and its conversion status as
`UNKNOWN`; it does not silently convert the Phoenix local schedule.

## Conclusion

The TCM control also failed for the same AOI/date/window before any
exceedance retest. The evidence therefore does not isolate an
`analytic_type=exceedance` defect. The most precise defensible classification
is a failure in the provider's `filter_type=2` historical range processing or
its AOI/date/time backend path, with request-time timezone semantics still
undocumented. This is not evidence of zero exceedance and does not justify a
SHHCH value.

The remaining exceedance diagnostic was deliberately not submitted. The
locked SHHCH architecture is unchanged, and the canonical Phoenix sample
continues to fail closed until schedule-aligned exceedance tiles are actually
validated.
