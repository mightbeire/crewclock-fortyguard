# CrewClock measurement specification

## Hero metric

> **Movable outdoor crew-hours shifted out of the highest modeled heat window while preserving every modeled hard constraint.**

Metric type: **derived planning proxy**.

It measures schedule allocation. It does not measure safety, injury probability, physiological strain, compliance, productivity actually delivered, or money saved.

## Formal definition

Let:

- `T` be tomorrow’s tasks;
- `E(t)` be true when task `t` is movable and classified by the employer as outdoor moderate/heavy;
- `H(t)` be assigned crew headcount;
- `I(t, p)` be the scheduled interval for task `t` under plan `p`;
- `W` be the highest modeled thermal investigation window;
- `overlap(a, b)` be interval overlap in hours.

```text
peak_window_crew_hours(p)
  = Σ over t in T where E(t)
      H(t) × overlap(I(t, p), W)

crew_hours_shifted
  = peak_window_crew_hours(original)
    − peak_window_crew_hours(proposed)
```

The MVP window is `11:00–15:00`, selected from the cached Phoenix hourly apparent-temperature profile for 2025-07-15. The window is a demo investigation choice, not an OSHA threshold.

## Deterministic recomputation

### Original eligible overlap

| Task | Crew | Headcount | Overlap with 11:00–15:00 | Crew-hours |
|---|---|---:|---:|---:|
| Fine grade & compact | A | 6 | 1.0h | 6 |
| Conduit bedding | A | 6 | 2.0h | 12 |
| Pull signal conductors | C | 4 | 1.0h | 4 |
| **Total** | | | | **22** |

### Proposed eligible overlap

| Task | Crew | Headcount | Overlap with 11:00–15:00 | Crew-hours |
|---|---|---:|---:|---:|
| Conduit bedding | A | 6 | 1.0h | 6 |
| **Total** | | | | **6** |

### Result

```text
22 − 6 = 16 movable outdoor crew-hours shifted
```

Sheltered/support tasks do not enter the metric. Fixed work does not enter the “movable” metric even if it overlaps the window; it remains visible as work requiring the employer’s planned controls and onsite authority.

## Why fixed work is excluded

The metric answers whether CrewClock found better timing for work the superintendent was allowed to move. Including a fixed concrete delivery or inspection would reward or punish CrewClock for obligations it could not change. The UI still shows fixed work, locks its time, and verifies its associated policy controls.

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
| 22, 6 and 16 crew-hours | Derived deterministic | `src/demo/engine.ts` with fixture regression in `src/demo/scenario.ts` |

## UI wording contract

Allowed:

- “modeled peak window”;
- “planning evidence”;
- “crew-hours shifted”;
- “constraints preserved”;
- “cached-live historical replay”;
- “onsite WBGT and employer policy remain authoritative.”

Prohibited:

- “safe hours,” “workers protected,” or “injuries prevented”;
- “16 hours safer”;
- “compliant” unless every governing rule and authoritative input is actually represented;
- “FortyGuard WBGT”;
- “tomorrow’s conditions” when showing the historical cache;
- dollars saved without a customer-approved cost model.

## Verification tests

Automated tests must:

1. recompute `22`, `6`, and `16` from task intervals and crew headcount;
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
