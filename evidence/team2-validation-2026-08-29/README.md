# Team Member 2 Independent Validation Evidence

This directory contains curated judge-facing engineering evidence from an independent validation campaign executed using the second team member's FortyGuard allocation on August 29, 2026.

## Campaign Overview

- **Mission**: Perform an adversarial independent validation campaign across diverse scenarios, baseline conditions, and failure modes.
- **Scenarios Evaluated**: 11 systematic scenarios covering positive retiming, invalid baselines (crew overbooking, dependency inversions, deadline violations), fixed commitment preservation, all-indoor work, evidence unavailability, and deterministic verifier replay.
- **Authoritative San Diego Baseline**: Protected and untouched (`evidence/san-diego-final-positive/`).

## Key Results Summary

| Scenario ID | Location | Fixture Type | Baseline Constraints | SHHCH (Before → After) | Final Constraints | Approval & Reverification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T2-001** | San Diego, CA | Synthetic Valid | 6/6 PASS | 18h → 9h (-50%) | 6/6 PASS | Approved · Reverified PASS |
| **T2-002** | Phoenix, AZ | Synthetic Valid | 6/6 PASS | 24h → 12h (-50%) | 6/6 PASS | Approved · Reverified PASS |
| **T2-003** | Phoenix, AZ | Synthetic Valid | 6/6 PASS | 0h → 0h (Optimal) | 6/6 PASS | No Change (Preserved) |
| **T2-004** | Phoenix, AZ | All-Indoor Support | 6/6 PASS | — (0 Outdoor) | 6/6 PASS | No Investigation Needed |
| **T2-005** | San Diego, CA | Invalid Baseline | REJECTED (Crew Conflict) | — | N/A | Rejected Upfront (Fail-Closed) |
| **T2-006** | San Diego, CA | Invalid Baseline | REJECTED (Dep Inversion) | — | N/A | Rejected Upfront (Fail-Closed) |
| **T2-007** | San Diego, CA | Invalid Baseline | REJECTED (Deadline) | — | N/A | Rejected Upfront (Fail-Closed) |
| **T2-008** | San Diego, CA | Fixed Work Anchor | 6/6 PASS | 12h → 6h (Fixed: 0 moved) | 6/6 PASS | Approved · Reverified PASS |
| **T2-009** | Phoenix, AZ | Unavailable Evid. | 5/6 | — | N/A | Fail-Closed (Shift Intact) |
| **T2-010** | Phoenix, AZ | Canonical Replay | 6/6 PASS | 91.5h → 91.5h | 6/6 PASS | Approved · Reverified PASS |
| **T2-011** | Phoenix, AZ | Positive Reschedule | 6/6 PASS | 39h → 20h (-48.7%) | 6/6 PASS | Approved · Reverified PASS |

## Curated Screenshot Evidence

The following high-resolution 1920x1080 screenshots demonstrate the actual working CrewClock product interface:

1. **`01-baseline-schedule.png`**: Baseline Schedule & Watchpoint Context showing initial task schedule and identified outdoor work.
2. **`02-fortyguard-evidence-audit.png`**: FortyGuard Evidence & Audit Proof Drawer showing exact workface bounding boxes, time windows, and threshold calculations.
3. **`03-verified-transformation-decision.png`**: Deterministic Transformation & Constraint Verification showing measured SHHCH reduction and 6/6 constraint pass.
4. **`04-superintendent-approval-verified.png`**: Superintendent Approval Recorded & Final Deterministic Reverification Pass.
5. **`05-invalid-baseline-rejection.png`**: Adversarial Baseline Rejection (Double-Booked Crew Conflict stopped before thermal acquisition).
6. **`06-fail-closed-evidence-unavailable.png`**: Fail-Closed Safety Mode when evidence is unavailable.
7. **`07-all-indoor-work-handling.png`**: Handling of All-Indoor Support Shifts leaving schedule unchanged.
8. **`08-fixed-work-anchored.png`**: Fixed Outdoor Commitments remain strictly anchored (0 fixed task moves).

## Validation Integrity Note

- Zero mock data or fabricated runs.
- All screenshots captured at exact 1920x1080 viewport without devtools or window decorations.
- All secrets, API keys, and private tokens excluded from git repository and screenshots.
