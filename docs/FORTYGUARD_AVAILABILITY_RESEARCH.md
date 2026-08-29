# FortyGuard Availability Research

## Purpose

CrewClock depends on decision-grade environmental evidence. During integration, some valid FortyGuard heatmap requests returned usable evidence while others completed without usable map evidence. We ran a controlled experiment to determine whether the observed variation tracked location, forecast timing, analytic type, asynchronous processing, or the CrewClock client.

## Method

The experiment tested **13 U.S. point-centered workfaces** with **84 API requests**. The request matrix held geometry, granularity, threshold, polling policy, and local-time relationships as consistent as practical.

The matrix compared:

- TCM and `exceedance` analytics;
- future and historical windows;
- equivalent workface-sized AOIs;
- a 32 °C exceedance trigger where applicable;
- limited repeat requests for determinism.

Each asynchronous activity was allowed to reach a terminal state. Completed requests were separated into decision-grade nonzero evidence, decision-grade explicit zero evidence, and completed-empty evidence.

## Results

| Measure | Result |
| --- | ---: |
| Locations tested | **13** |
| Total API requests | **84** |
| Future requests | **56** |
| Historical requests | **28** |
| Repeat requests | **6** |
| Decision-grade nonzero | **49** |
| Decision-grade explicit zero | **3** |
| Completed-empty | **32** |
| Provider failures | **0** |
| Timed out | **0** |
| Invalid requests | **0** |
| Client errors | **0** |

All activities completed in approximately **20.561–45.424 seconds**. Repeat results were deterministic.

Equivalent paired TCM and `exceedance` requests returned decision-grade evidence in all primary cells at **eight tested coordinates**. The same controlled request pattern completed with empty evidence in all primary cells at **five tested coordinates**: Yuma, Arizona; El Centro, California; Riverside, California; Austin, Texas; and Sacramento, California.

These observations apply only to the tested coordinates and windows. They do not establish permanent support or non-support for an entire city.

## Findings

**Geographic variation: supported.** Under the controlled matrix, result availability tracked request location.

**Forecast variation: not supported.** The experiment did not find a systematic future-versus-historical explanation.

**Analytic-specific variation: not supported.** Paired TCM and `exceedance` behavior did not isolate the issue to one analytic path.

**Asynchronous delay: not supported.** All activities reached a terminal state within the experiment timeout, and none timed out.

**CrewClock client issue: not found.** No client-classification errors were observed.

The strongest supported conclusion is therefore narrow: **FortyGuard heatmap result availability varied by request location in this controlled test set.** The experiment does not identify the provider-side cause.

## CrewClock implication

CrewClock separates three conditions:

1. **Decision-grade nonzero evidence:** usable environmental evidence with qualifying values.
2. **Decision-grade explicit zero:** valid evidence that reports zero qualifying exceedance.
3. **Missing, incomplete, or completed-empty evidence:** not equivalent to zero.

CrewClock can make a thermal scheduling decision only from decision-grade evidence. When required evidence is unavailable, it preserves the current shift rather than inventing a value.

## Validated positive locations

End-to-end positive CrewClock runs were validated with fresh FortyGuard evidence in:

- **San Diego, California** — August 28, 2026: SHHCH **18 → 9**, 50% reduction, 3 flexible tasks moved, 0 fixed tasks moved, 6/6 constraints, human approval, final reverification.
- **Tucson, Arizona** — August 29, 2026: SHHCH **60 → 24**, 60% reduction, 3 flexible tasks moved, 0 fixed tasks moved, 6/6 constraints, human approval, final reverification, 20 fresh activities, 0 cache reuse.

Palm Springs, California, also returned usable FortyGuard evidence during prior testing.

## Suggested limitation statement

FortyGuard heatmap availability varied by request location during controlled testing of 13 U.S. point-centered workfaces. CrewClock uses only completed, decision-grade evidence, treats explicit zero as valid evidence, and preserves the current shift when a tested request returns missing or incomplete evidence. These observations do not define permanent city support or a coverage boundary.

## Potential FortyGuard product feedback

The integration would be easier to reason about if the API exposed clearer availability semantics for completed-empty results, forecast-data availability metadata, and explicit guidance that distinguishes a valid zero result from a completed request with no usable map evidence.
