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

1. Open the [live demo](https://crewclock.oluwatomireoluwa.chatgpt.site).
2. Run the accepted San Diego replay path when available in the public interface.
3. Inspect the agent investigation and evidence stages.
4. Compare 18 SHHCH with 9 SHHCH.
5. Approve the sealed recommendation.
6. Confirm final reverification.

The live product also has fail-closed paths for unavailable evidence, invalid input, and no feasible improvement. Those paths preserve the current shift.
