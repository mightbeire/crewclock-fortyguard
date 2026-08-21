# CrewClock measurement specification

## Hero metric

> **Scheduled High-Heat Crew-Hours (SHHCH) from schedule-aligned FortyGuard exceedance windows while preserving every modeled hard constraint.**

Metric type: **derived planning proxy**. The canonical Phoenix fixture currently has no schedule-aligned exceedance windows, so no Phoenix number is emitted.

The calculation is `unique area-weighted qualifying duration over the task workface × task overlap × crew size`, summed across all outdoor tasks. `env_params` is contextual only; it is not a duration source. Overlapping evidence windows are normalized into a union before multiplication.

It measures schedule allocation. It does not measure safety, injury probability, physiological strain, compliance, productivity actually delivered, or money saved.

## Formal definition

Let `D(t, w)` be the area-weighted FortyGuard exceedance duration for task
workface `t` in exact evidence window `w`, `I(t, p)` be the scheduled task
interval, `H(t)` be assigned crew headcount, and `overlap` be temporal overlap
in hours.

```text
SHHCH(p)
  = Σ over outdoor t,w
      H(t) × D(t, w) × overlap(I(t, p), w) / duration(w)

crew_hours_shifted
  = SHHCH(original) − SHHCH(proposed)
```

Evidence windows are supplied by FortyGuard `analytic_type=exceedance`; a
project thermal trigger names its modeled-temperature quantity and is not a
heat-index or WBGT threshold. The current Phoenix window set is absent. Two
exact attempts for the first historical window returned terminal failure with
zero credit spend; this does not imply zero exceedance.

## Deterministic recomputation

The engine first checks that every outdoor task has a polygon workface and a
covering valid `analytic_type=exceedance` window in hours. It area-weights the
tiles intersecting that workface, scales the window duration by the exact
task/window overlap, and multiplies by assigned crew size. Indoor tasks
contribute zero. Fixed tasks remain fixed in the scheduler but are not silently
relabelled as movable.

The current Phoenix fixture has no schedule-aligned exceedance windows, so its
SHHCH result is `EVIDENCE_UNAVAILABLE`; no Phoenix metric is presented.

## Fixed work is included

SHHCH measures the thermal placement of the whole scheduled plan. Fixed outdoor work therefore contributes to `TOTAL_SHHCH`, even though the optimizer cannot move it. The deterministic result exposes `MOVABLE_SHHCH` and `FIXED_SHHCH` separately so optimization impact is not confused with unavoidable fixed work.

## Constraint denominator

The result is valid only if all modeled hard constraints pass:

| Constraint group | Demo check |
|---|---:|
| Tasks retained | 14/14 |
| Crew qualification sets | 3/3 |
| Dependency edges | 11/11 |
| Fixed commitments | 5/5 |
| Task deadlines | 14/14 |
| Demo employer planning control | 1/1 |

An alternative with a lower thermal overlap but any hard failure is rejected. Required `UNKNOWN` evidence blocks recommendation.

## Evidence classes

| Value | Class | Source |
|---|---|---|
| Hourly apparent-temperature profile | Cached-live | `.agent_cache/live_followups/env_phoenix.json` |
| 40.1505°C TCM maximum | Cached-live | `.agent_cache/live_geographies/phoenix_paved_industrial.json` |
| 99-cell time-of-measure analysis | Cached-live | `.agent_cache/live_followups/phoenix_time_of_measure.json` |
| 11:00–15:00 investigated window | Derived | Selected from cached hourly profile |
| Tasks, times, crews and zones | Synthetic | CrewClock demo fixture |
| Employer rule pack | Synthetic employer policy | CrewClock demo fixture |
| Phoenix SHHCH | Not demonstrated | Schedule-aligned Phoenix exceedance windows are not cached |

## UI wording contract

Allowed:

- “employer high-heat trigger”;
- “planning evidence”;
- “scheduled high-heat crew-hours”;
- “constraints preserved”;
- “cached-live historical replay”;
- “onsite WBGT and employer policy remain authoritative.”

Prohibited:

- “safe hours,” “workers protected,” or “injuries prevented”;
- “16 hours safer”;
- “compliant” unless every governing rule and authoritative input is actually represented;
- “FortyGuard WBGT”;
- “current conditions” when showing the historical cache;
- dollars saved without a customer-approved cost model.

## Verification tests

Automated tests must:

1. recompute SHHCH from exceedance tile area, exact temporal overlap and crew headcount;
2. verify fixed tasks do not move;
3. verify dependencies, qualifications and deadlines in both plans;
4. verify all evidence/policy provenance labels exist;
5. fail if cached-live evidence is relabelled current or onsite authoritative;
6. fail if the hero metric becomes a safety outcome.

The production MVP suite also verifies deterministic replay, exact solver reproduction of the canonical proposal, crew non-overlap, selective investigation, missing-evidence failure, and the no-feasible-improvement path.

## Final live-validation protocol—no calls authorized in this run

Before a production or final sponsor claim:

1. Obtain one real, non-sensitive next-day look-ahead with two or more mapped work zones.
2. Run an ordinary forecast + manual/spreadsheet baseline.
3. Run the same plan with authorized FortyGuard evidence.
4. Hold crew, policy and solver constraints constant.
5. Record whether FortyGuard changes the investigated tasks, zone ranking, selected timing, feasible plan, or superintendent decision.
6. Have the superintendent rate usefulness and correctness.
7. Compare planned with actual onsite readings and actual execution without treating correlation as safety efficacy.
8. Kill or narrow the FortyGuard claim if the operational decision does not change.

## Secondary metrics after a pilot

Only with real field data:

- minutes required to produce an approved next-day plan;
- number of last-minute revisions after shift start;
- planned-versus-actual crew-hours completed;
- overtime or standby hours;
- tasks deferred for heat-related operating reasons;
- frequency of `UNKNOWN`/escalation and override reasons;
- percentage of accepted recommendations;
- decision delta versus weather + spreadsheet.

No health-outcome or dollar conversion is authorized by the MVP evidence.

## Locked primary metric

`scheduled high-heat crew-hours = Σ(area-weighted FortyGuard exceedance duration × exact task/window overlap × crew size)` for outdoor tasks with valid polygon evidence. It is a derived schedule metric, not exposure, dose, WBGT, injuries prevented, or a safety percentage. `env_params` is never substituted for exceedance duration.
