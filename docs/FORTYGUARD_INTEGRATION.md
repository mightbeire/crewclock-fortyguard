# FortyGuard API integration

FortyGuard is the environmental intelligence layer that makes CrewClock's core decision possible. CrewClock does not use FortyGuard as a decorative weather feed. It binds FortyGuard heatmap evidence to specific construction workfaces and schedule windows, then uses that evidence to decide whether flexible outdoor work can move without breaking the operating plan.

Without decision-grade FortyGuard evidence, CrewClock does not make a thermal rescheduling recommendation.

## 1. What FortyGuard enables

A city-level weather value cannot answer CrewClock's main question: can this task move from this workface and time window to another reachable window with less modeled high-heat overlap?

FortyGuard gives CrewClock the spatial and temporal evidence needed to answer that question. CrewClock then combines the evidence with crews, qualifications, dependencies, deadlines, fixed commitments, and employer-configured controls.

The result is an operational decision, not a weather display.

## 2. API surfaces used

| FortyGuard surface | CrewClock use |
| --- | --- |
| `POST /v1/heatmap` | Request modeled evidence for one selected workface and one schedule window. |
| `GET /v1/status/{activity_id}` | Poll an asynchronous heatmap activity until it reaches a terminal state. |
| `exceedance` analytic | Measure modeled hours above the project's 32 °C trigger. |
| TCM | Used in controlled engineering research to compare base temperature availability with analytic availability. It is not the SHHCH decision source. |

The production decision path uses `exceedance`. Optional environmental context cannot replace the required exceedance evidence.

## 3. Request contract

CrewClock creates one heatmap request for one selected workface and one selected schedule window. The production request path requires:

- a GeoJSON polygon AOI that matches the selected workface;
- a local date;
- a local start and end time;
- `analytic_type: exceedance`;
- `threshold: 32.0`;
- `direction: above`;
- a supported granularity of 60, 80, or 100 meters.

CrewClock uses 100 meters by default. The backend also binds the request to the project's IANA timezone, workface ID, window ID, project AOI hash, provider, and provider version. This identity stays with the evidence even though the heatmap payload itself uses the AOI and local date-time fields.

A sanitized production request has this shape:

```json
{
  "polygon_aoi": "<single-workface GeoJSON FeatureCollection>",
  "start_date": "2026-08-29",
  "filter_type": 2,
  "start_time": "06:00",
  "end_time": "08:00",
  "granularity": 100,
  "analytic_type": "exceedance",
  "threshold": 32.0,
  "direction": "above"
}
```

The example omits coordinates and credentials. CrewClock never sends a FortyGuard API key to the browser.

## 4. Asynchronous request lifecycle

FortyGuard heatmap activities are asynchronous. CrewClock therefore separates submission from result validation.

```text
CrewClock
  -> POST /v1/heatmap
  -> activity_id
  -> GET /v1/status/{activity_id}
  -> processing
  -> completed or failed
  -> schema and evidence validation
  -> decision-grade evidence or evidence unavailable
```

CrewClock uses bounded polling. The production path allows up to 600 seconds because valid FortyGuard activities can take time to finish. It does not treat a still-processing activity as missing evidence. The adapter also has a bounded retry for a transient rate-limit response.

During our controlled availability study, all 84 FortyGuard activities reached a terminal state in approximately 20.6 to 45.4 seconds. None timed out.

## 5. Workface and schedule-window binding

CrewClock does not ask FortyGuard for one broad city result and apply it to every task.

The core rule is:

**one selected workface x one selected schedule window = one evidence request**

Each acquisition AOI must match the selected workface. CrewClock rejects a request when the workface ID, polygon, or project geometry does not match the submitted site.

The time window must also match the construction schedule. Origin evidence is not enough. Before CrewClock credits a proposed task move, it checks the reachable destination window as well. A lower-SHHCH recommendation cannot rely on an unmeasured destination.

This is why FortyGuard is load-bearing in CrewClock. It supplies the evidence for the actual operational choice, not only the background weather condition.

## 6. From FortyGuard evidence to SHHCH

FortyGuard `exceedance` heatmaps return modeled values in hours. CrewClock validates the returned tile geometry and values, then checks how the returned tiles overlap the selected workface.

CrewClock uses area-weighted tile overlap when a workface crosses more than one heatmap tile. It then binds the qualifying exceedance window to scheduled outdoor work. The planning metric is Scheduled High-Heat Crew-Hours, or SHHCH.

At a high level:

```text
FortyGuard exceedance evidence
  -> validate heatmap tiles
  -> bind tiles to the workface polygon
  -> bind exceedance hours to the task window
  -> apply scheduled crew size
  -> calculate SHHCH
```

SHHCH is a schedule-placement metric. It is not a physiological exposure score, heat dose, injury-risk estimate, safety certification, or compliance result.

## 7. Evidence validation contract

CrewClock does not trust a provider response only because the request completed. It validates the evidence before the scheduler can use it.

The production path checks:

- heatmap response schema;
- analytic type;
- threshold and direction;
- observation date;
- local schedule window;
- IANA timezone binding;
- AOI and workface identity;
- polygon geometry;
- heatmap-tile overlap with the workface;
- feature count;
- destination-window coverage;
- activity ID and provenance;
- content and AOI hashes.

A returned heatmap must contain usable overlapping features for the selected workface. A completed request with no usable map evidence does not become a valid zero.

CrewClock's rule is simple: **missing evidence is not zero**.

## 8. Evidence states

CrewClock separates provider outcomes because they have different meanings.

| Evidence state | CrewClock action |
| --- | --- |
| Decision-grade nonzero | Use the validated FortyGuard evidence. |
| Decision-grade explicit zero | Use zero as a valid measured result. |
| Completed-empty or incomplete | Mark evidence unavailable. Do not infer zero. |
| Failed or invalid | Stop the thermal recommendation path. |

When required origin or destination evidence is unavailable, CrewClock preserves the submitted shift.

This behavior was informed by our controlled FortyGuard availability research. See [`FORTYGUARD_AVAILABILITY_RESEARCH.md`](FORTYGUARD_AVAILABILITY_RESEARCH.md).

## 9. Agent, FortyGuard, and deterministic boundaries

CrewClock separates judgment, evidence, arithmetic, and authority.

The AI agent can select the initial investigation path, selected workfaces, and an initial set of schedule windows within deterministic bounds. After evidence acquisition, it can decide whether validated coverage is sufficient, request allowed missing windows, or abstain. It also explains the final deterministic result to the operator.

FortyGuard owns the modeled environmental evidence for the selected polygons and windows.

Deterministic code validates every selected ID, determines which evidence is ultimately required, calculates SHHCH, generates schedule alternatives, checks six hard-constraint families, seals the recommendation, and performs final reverification.

The AI cannot invent environmental evidence. It cannot set schedule timestamps. It cannot relax a hard constraint. It cannot approve its own recommendation.

The superintendent remains the final decision-maker.

For the full authority model, see [`DECISION_BOUNDARIES.md`](DECISION_BOUNDARIES.md).

## 10. Provenance, cache identity, and auditability

CrewClock keeps a traceable identity for decision-grade evidence. A live acquisition can retain:

- FortyGuard activity ID;
- request hash;
- AOI hash;
- result/content hash;
- workface ID;
- window ID;
- submitted polygon;
- observation date;
- timezone;
- analytic, threshold, and direction;
- acquisition time;
- granularity;
- evidence classification.

The live adapter writes successful results to cache only after validation. Cache reuse requires an exact decision identity match. A different workface, window, date, geometry, threshold, or analytic produces a different request identity.

Per-request evidence is marked as live acquisition or exact cache reuse. Session-level evidence can also show segmented live acquisition when CrewClock combines multiple validated workface-window activities.

This provenance lets a reviewer trace a recommendation back to the environmental evidence used to support it.

## 11. Validated live integration results

CrewClock has two positive end-to-end validation runs with fresh FortyGuard evidence.

| Run | FortyGuard evidence | Operational result |
| --- | --- | --- |
| San Diego, California — Aug. 28, 2026 | Fresh live evidence; 9 activities; 0 cache reuse | SHHCH **18 -> 9**; 50% reduction; 3 flexible tasks moved; 0 fixed tasks moved; 6/6 constraints; approved and reverified. |
| Tucson, Arizona — Aug. 29, 2026 | Fresh live evidence; 20 activities; 0 cache reuse | SHHCH **60 -> 24**; 60% reduction; 3 flexible tasks moved; 0 fixed tasks moved; 6/6 constraints; approved and reverified. |

The authoritative San Diego evidence is in [`../evidence/san-diego-final-positive/`](../evidence/san-diego-final-positive/). The independent Tucson evidence is in [`../evidence/fresh-live-positive-2026-08-29/`](../evidence/fresh-live-positive-2026-08-29/).

See [`DEMO_AND_RESULTS.md`](DEMO_AND_RESULTS.md) for the accepted demo path.

## 12. Availability research and fail-closed behavior

During integration, some valid FortyGuard requests returned decision-grade evidence while others completed without usable map evidence. We did not assume that this was a FortyGuard failure or a CrewClock bug.

We ran 84 controlled requests across 13 U.S. coordinates. The study compared TCM and `exceedance`, historical and future windows, controlled workface-sized AOIs, and limited repeats. The observed availability difference tracked request location in this test set. It did not track analytic type, historical versus future data, polling delay, or a client-classification error.

The study does not define permanent city support or a provider coverage boundary. Its product effect is narrower and more important: CrewClock treats evidence availability as part of the decision contract.

If FortyGuard returns explicit zero evidence, CrewClock can use zero. If a completed request has no decision-grade evidence, CrewClock keeps the current shift.

## 13. Security and secret handling

The FortyGuard API key is server-side only. The repository includes the variable name in `.env.example`, but it does not include a credential value.

CrewClock does not expose authorization headers in the browser, evidence screenshots, or judge-facing JSON summaries. Provider errors are also shortened and sanitized at the adapter boundary.

The public client receives decision results and safe provenance. It does not receive the FortyGuard credential.

## 14. Limits and responsible use

FortyGuard is modeled environmental intelligence. CrewClock uses it to make a schedule-placement decision.

Neither FortyGuard nor CrewClock's SHHCH metric certifies a worksite as safe. CrewClock does not claim physiological exposure, heat dose, injury prevention, medical guidance, WBGT equivalence, or regulatory compliance.

Onsite measurements, the employer's heat plan, worker condition, workload, PPE, and professional judgment remain authoritative.

## Related documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system flow and runtime boundaries.
- [`DECISION_BOUNDARIES.md`](DECISION_BOUNDARIES.md) — AI, deterministic code, FortyGuard, and superintendent authority.
- [`DEMO_AND_RESULTS.md`](DEMO_AND_RESULTS.md) — accepted demonstration result and judge path.
- [`FORTYGUARD_AVAILABILITY_RESEARCH.md`](FORTYGUARD_AVAILABILITY_RESEARCH.md) — 84-request controlled availability study.
- [`SUBMISSION.md`](SUBMISSION.md) — final project summary.

FortyGuard is not an accessory to CrewClock. It is the environmental evidence layer that turns a construction schedule from a static plan into a heat-aware operational decision.