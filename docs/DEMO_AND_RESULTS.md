# Demo and results

## Authoritative run

**Location:** San Diego, California

**Date:** August 28, 2026

**Shift:** 12:00–17:00 local time

**Evidence:** fresh live FortyGuard evidence during the accepted run

| Gate | Result |
| --- | ---: |
| Baseline SHHCH | **18** |
| Proposed SHHCH | **9** |
| Reduction | **50%** |
| Flexible tasks moved | **3** |
| Fixed tasks moved | **0** |
| Constraints | **6/6 → 6/6** |
| Human approval | **PASS** |
| Final reverification | **PASS** |

The run covered the origin and reachable destination windows. The accepted run summary is [`evidence/san-diego-final-positive/run-summary.json`](../evidence/san-diego-final-positive/run-summary.json). Focused screenshots in the same directory show the baseline, agent investigation, FortyGuard evidence, schedule difference, approval, and final audit.

## Suggested judge path

1. Watch the [final 2:48 CrewClock demo](https://youtu.be/gbTTAxec-f4) for the authoritative San Diego fresh-live run.
2. Inspect [`evidence/san-diego-final-positive/`](../evidence/san-diego-final-positive/) for the committed run summary and proof screenshots behind the **18 → 9 SHHCH** result.
3. Open the [public CrewClock prototype](https://crewclock.oluwatomireoluwa.chatgpt.site) to inspect the product flow, deterministic verification, human-decision boundary, replay/capability paths, and fail-closed behavior.
4. Inspect [`evidence/fresh-live-positive-2026-08-29/`](../evidence/fresh-live-positive-2026-08-29/) for the independent Tucson fresh-live validation (**60 → 24 SHHCH**, 20 fresh activities, 0 cache reuse).
5. Review [`FORTYGUARD_INTEGRATION.md`](FORTYGUARD_INTEGRATION.md) for the exact API, evidence, agent, deterministic-code, and approval boundaries.

The public hosted prototype is an interactive judge surface; it should not be interpreted as replaying the San Diego fresh-live acquisition on demand. The authoritative live-acquisition proof is the final video plus the committed San Diego evidence, with Tucson as an independent fresh-live validation. Operator-created shifts preserve the current plan whenever deployment-side decision-grade evidence is unavailable.

The product also has fail-closed paths for unavailable evidence, invalid input, and no feasible improvement. Those paths preserve the current shift.
