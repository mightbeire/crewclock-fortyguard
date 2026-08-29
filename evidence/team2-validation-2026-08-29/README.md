# Team Member 2 Independent Validation Evidence

This directory contains curated judge-facing engineering evidence from an independent validation campaign executed using the second team member's FortyGuard allocation on August 29, 2026.

## Testing Disclosure & Evidence Classification

The campaign used synthetic construction schedules for controlled testing. CrewClock processed them through the real product runtime. FortyGuard evidence is labeled as live, cached, unavailable, or replayed for each scenario. No judge-facing result is presented as field production data.

Primary accepted product demo evidence (San Diego, California: 18h → 9h, 50% reduction, 3 flexible tasks moved, 0 fixed tasks moved, 6/6 constraints, human approval recorded, final reverification passed) is maintained separately in `evidence/san-diego-final-positive/`. Team Member 2 validation is an independent audit.

## Campaign Matrix & Verified Scenario Results

The campaign executed 11 systematic scenarios:

| Scenario ID | Test Classification | Location & Date | FortyGuard Evidence Class | Baseline Constraints | SHHCH Before → After | Tasks Moved (Flex / Fixed) | Final Constraints | Approval & Reverification | Outcome & Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T2-001** | Synthetic Valid | San Diego, CA<br>2025-08-28 | FRESH LIVE<br>*(LIVE_ACQUIRED_SEGMENTED)* | 6/6 PASS | 0h → 0h | 0 / 0 | 6/6 PASS | Not Applicable (No change issued) · Reverified PASS | **PASS** (No Feasible Improvement; 0 exceedance measured) |
| **T2-002** | Synthetic Valid | Phoenix, AZ<br>2025-07-15 | FRESH LIVE<br>*(LIVE_ACQUIRED_SEGMENTED)* | 6/6 PASS | 15h → 15h | 0 / 0 | 6/6 PASS | Not Applicable · Reverified PASS | **PASS** (No Feasible Improvement; dependencies preserved) |
| **T2-003** | Synthetic Valid | Phoenix, AZ<br>2025-07-15 | FRESH LIVE<br>*(LIVE_ACQUIRED_SEGMENTED)* | 6/6 PASS | 8h → 8h | 0 / 0 | 6/6 PASS | Not Applicable · Reverified PASS | **PASS** (No Feasible Improvement; morning shift below peak) |
| **T2-004** | Synthetic Valid | Phoenix, AZ<br>2026-08-27 | EVIDENCE UNAVAILABLE<br>*(0 outdoor tasks)* | 6/6 PASS | N/A (0 outdoor) | 0 / 0 | 6/6 PASS | Not Applicable · Reverified PASS | **PASS** (All-indoor support shift cleanly preserved) |
| **T2-005** | Synthetic Invalid | San Diego, CA<br>2025-08-28 | EVIDENCE UNAVAILABLE<br>*(Pre-flight blocked)* | **5/6 FAIL**<br>*(Crew conflict)* | N/A | 0 / 0 | 5/6 FAIL | N/A · Pre-flight Rejected | **PASS (REJECTED)** (Crew overbooking blocked upfront) |
| **T2-006** | Synthetic Invalid | San Diego, CA<br>2025-08-28 | EVIDENCE UNAVAILABLE<br>*(Pre-flight blocked)* | **5/6 FAIL**<br>*(Dep inversion)* | N/A | 0 / 0 | 5/6 FAIL | N/A · Pre-flight Rejected | **PASS (REJECTED)** (Dependency inversion blocked upfront) |
| **T2-007** | Synthetic Invalid | San Diego, CA<br>2025-08-28 | EVIDENCE UNAVAILABLE<br>*(Pre-flight blocked)* | **5/6 FAIL**<br>*(Deadline breach)* | N/A | 0 / 0 | 5/6 FAIL | N/A · Pre-flight Rejected | **PASS (REJECTED)** (Deadline violation blocked upfront) |
| **T2-008** | Synthetic Valid | San Diego, CA<br>2025-08-28 | EVIDENCE UNAVAILABLE | 6/6 PASS | NOT VERIFIED | 0 / 0 | 6/6 PASS | Not Applicable · Reverified PASS | **PASS** (Fixed outdoor commitments anchored) |
| **T2-009** | Synthetic Valid | Phoenix, AZ<br>2026-08-27 | EVIDENCE UNAVAILABLE | 6/6 PASS | N/A | 0 / 0 | 6/6 PASS | Not Applicable · Reverified PASS | **PASS (FAIL-CLOSED)** (Current shift preserved unchanged) |
| **T2-010** | Historical Replay | Phoenix, AZ<br>2025-07-15 | HISTORICAL REPLAY<br>*(CANONICAL_FORTYGUARD)* | **5/6 FAIL**<br>*(Break policy)* | 91.5h → 91.5h | 1 / 0 | 6/6 PASS | Approved · Reverified PASS | **PASS** (Repaired break constraint; 0 live API calls) |
| **T2-011** | Synthetic Valid | Phoenix, AZ<br>2025-07-15 | SYNTHETIC TEST SCENARIO | 6/6 PASS | **39h → 20h**<br>*(-48.7%)* | 7 / 0 | 6/6 PASS | Approved · Reverified PASS | **PASS** (Positive retiming demonstrated; approved & reverified) |

## Screenshot Provenance

All retained screenshots were captured from live browser navigation of real completed CrewClock runs at 1920x1080 resolution without devtools or window chrome:

| Filename | Scenario ID | Fixture Type | FortyGuard Evidence Class | Visible SHHCH | Visible Moves | Capture Source | Truthfulness Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `01-baseline-schedule.png` | `T2-011` | Synthetic Valid | `SYNTHETIC_TEST_SCENARIO` | None (Watchpoint) | 0 moved (7 eligible) | Completed upcoming shift scene | **VERIFIED** |
| `02-fortyguard-evidence-audit.png` | `T2-011` | Synthetic Valid | `SYNTHETIC_TEST_SCENARIO` | 39h → 20h | 7 flexible retimed | Why This Plan proof drawer | **VERIFIED** |
| `03-verified-transformation-decision.png` | `T2-011` | Synthetic Valid | `SYNTHETIC_TEST_SCENARIO` | 39h → 20h | 7 flexible retimed | Decision & transformation scene | **VERIFIED** |
| `04-superintendent-approval-verified.png` | `T2-011` | Synthetic Valid | `SYNTHETIC_TEST_SCENARIO` | None (Post-approval) | 7 retimed | Approved & reverified scene | **VERIFIED** |
| `05-all-indoor-work-handling.png` | `T2-004` | Synthetic Valid | `EVIDENCE_UNAVAILABLE` | None (0 outdoor) | 0 moved | All-indoor watchpoint scene | **VERIFIED** |

## Validation & Security Notes

- **Zero Secret Exposure**: All `.env` files and API keys remain uncommitted and scrubbed from all evidence.
- **Verification Integrity**: All 6 hard-constraint families were deterministically evaluated by code before and after schedule generation.
