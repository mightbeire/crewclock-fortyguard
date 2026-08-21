# CrewClock thermal model

## Signal boundary

FortyGuard measures environmental/spatial signals. CrewClock derives a planning decision from those signals and an employer-configured trigger.

Primary signal: heatmap tiles at the requested granularity. `tcm` is a temperature snapshot; `time_of_measure` is UTC peak hour; `exceedance` counts hours above/below a Celsius threshold; `persistence` measures the longest continuous run. Each response is schema- and unit-asserted before use.

`env_params` is not the primary signal. A range response applies the submitted temperature anchor over the response and can create misleading overnight heat-index artifacts. CrewClock rejects using such a range as a shift exposure series, raw maximum, or hourly schedule forecast. A single future-hour response may be used only if its timestamp is demonstrably matched to a valid heatmap hour; the controlled 2026-08-21 probe was ambiguous because the future heatmap returned zero cells.

`wet_bulb_temperature_celsius` remains wet-bulb temperature. It is never renamed or compared directly to WBGT occupational limits. Certified WBGT and authoritative onsite measurements are outside CrewClock's authority.

## Spatial model

One shared project AOI is requested for relevant workfaces. Local spatial joining maps heatmap tiles to workface polygons. The value is area-weighted across every overlapping tile. A point-like area may use deterministic point-in-tile assignment and must be labelled as such.

The canonical Phoenix fixture uses the previously successful historical AOI and
four WGS84 workface polygons inside that shared AOI. On 2026-08-21 the first
two-hour exceedance request failed twice; no tile geometry is treated as
coverage unless the API returns a completed, non-empty response.

## Hero metric

For each outdoor task, FortyGuard `analytic_type=exceedance` duration is area-weighted over its polygon workface, intersected with that task's scheduled interval, and multiplied by crew size. The result is `scheduled high-heat crew-hours (SHHCH)`. A project thermal trigger names FortyGuard's modeled temperature quantity; it is not heat index or WBGT. The deterministic engine fails closed when schedule-aligned exceedance evidence is missing. `env_params` remains optional context and cannot supply duration.
