# Demo geography research

Date: August 19, 2026. Eight strategically selected U.S. sites were tested with one 100 m full-day `tcm` heatmap and one Premium satellite segmentation request each. Results are cached in `.agent_cache/live_geographies/`. Three environmental profiles and four multi-day analysis maps were then tested in `.agent_cache/live_followups/`. No identical successful request was repeated.

## Geography matrix

| Site | Live heatmap | Live heat signal | Satellite composition | Interpretation |
|---|---|---|---|---|
| Phoenix paved/industrial | 1 tile | avg 37.08°C, max 40.15°C | Response was `others=100%` | Strong heat, unusable physical context; agent should report uncertainty, not infer pavement. |
| Las Vegas dense/paved | 1 tile | avg 37.35°C, max 41.31°C | 73.87% building, 12.94% road/route, 4.93% tree, 2.38% plant | Best current surface-conditioned demo candidate: high heat plus interpretable mixed labels. |
| Houston ship channel | 0 cells | no map features | 40.97% tree, 24.96% earth/ground, 17.10% road/route | Useful satellite contrast, but no live heatmap coverage at this coordinate/date; reject for demo. |
| Dallas-Fort Worth logistics | 0 cells | no map features | `others=100%` | No usable paired evidence; reject. |
| Atlanta airport | 1 tile | avg 30.22°C, max 36.30°C | 43.64% building, 56.36% others | Heatmap works; satellite labels are too coarse for a confident airport-surface claim. |
| Los Angeles airport/rail | 1 tile | avg 20.35°C, max 24.51°C | 86.79% building, 1.06% rail, 4.65% earth/ground | Best rail-context satellite signal, but the selected date was cool; use for rail evidence, not generic heat stress. |
| New York dense built | 0 cells | no map features | 32.96% building, 20.14% road/route, 33.93% earth/ground | No paired heat evidence at this coordinate/date; reject. |
| Portland green industrial | 0 cells | no map features | 42.85% building, 15.31% grass, 11.36% tree, 11.28% road/route | Strong physical contrast but no paired heatmap coverage; reject. |

Satellite responses returned `image_year=2026` even though the request date was 2025-07-15. This is recorded as an API behavior and must be disclosed if satellite imagery is used; the agent should not silently treat image year as the heatmap observation year.

## Targeted follow-ups

| Follow-up | Result | Credit delta | Use |
|---|---|---:|---|
| Phoenix env params | 24 hourly values; apparent temperature 28.9–42.5°C; heat index field 39.3–45.7 | 2,900 | Strong temporal scheduling profile. |
| Las Vegas env params | 24 hourly values; apparent temperature 28.1–42.2°C; heat index field 38.0–44.3 | 2,900 | Strong hot/dry surface-conditioned demo candidate. |
| Atlanta env params | 24 hourly values; apparent temperature 26.6–41.3°C; relative humidity 33.3–97.6% | 2,900 | Humidity context is useful; `heat_index_celsius` reached 77.9 and is not trusted as Celsius without unit clarification. |
| Phoenix `time_of_measure` | 99 cells, peak hour 04–16 UTC, only two unique values | 4,220 | Supports temporal prioritization; spatial peak-hour variation exists but is limited in this AOI. |
| Phoenix `persistence` | 99 cells, all 8 hours above 38°C | 4,220 | Confirms duration can be a strong operational constraint even when spatial variation is weak. |
| Los Angeles `time_of_measure` | 108 cells, all 15 UTC | 4,220 | Supports a simple consistent patrol window for the tested corridor. |
| Los Angeles `persistence` | 108 cells, all 7 hours above 23°C | 4,220 | Supports a corridor-wide duration warning, not fine-grained ranking. |

The geography pass used 148,960 credits; targeted follow-ups used 25,580 credits. Total account usage is 204,500, leaving 1,795,500 credits. The successful result caches are ignored and remain local.

## Recommendations without MVP selection

- **Las Vegas** is the best current geography for Surface-conditioned Road Repair or Industrial Yard Surface Intervention: high heat and interpretable building/road/tree labels in one paired response.
- **Phoenix** is the best current geography for Thermal Sequence Planner or RailHeat-style temporal scheduling: the live profile is hot, and multi-day maps expose peak-hour/persistence behavior.
- **Los Angeles** is the best current geography for RailHeat Patrol Sequencer: satellite detected a rail class and the multi-day heat analyses completed, but the selected date is not a high-heat stress case.
- **Atlanta** is a useful humidity stress test but is not a safe demo geography until the heat-index unit anomaly is clarified.
- Houston, DFW, New York, and Portland are retained as coverage/uncertainty evidence, not demo recommendations.
