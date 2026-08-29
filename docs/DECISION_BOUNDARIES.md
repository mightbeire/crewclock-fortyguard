# Decision boundaries

CrewClock separates judgment, evidence, arithmetic, and authority.

| Layer | Owns | Does not own |
| --- | --- | --- |
| AI agent | Investigation path, workfaces, time windows, explanation, escalation | Schedule arithmetic, hard constraints, approval |
| FortyGuard | Modeled environmental evidence for selected polygons and windows | Safety certification, worker exposure, schedule feasibility |
| Deterministic code | Baseline validation, SHHCH, candidate schedules, hard constraints, approval recheck | Human judgment or employer policy decisions |
| Superintendent | Final approval, rejection, or decision to keep the current shift | None of the system's evidence or arithmetic claims |

## Six hard-constraint families

CrewClock checks:

- fixed commitments;
- dependencies;
- crew qualifications;
- deadlines and workday bounds;
- crew availability and overlap;
- employer controls.

The thermal objective cannot override a hard constraint. A failed baseline is not relabeled as a valid unchanged plan. An unavailable or ambiguous evidence state cannot produce a recommendation.

## Human control

The AI cannot approve its own recommendation. Approval is accepted only for the exact sealed candidate. CrewClock runs deterministic final reverification after approval. A mismatch blocks publication and preserves the current shift.
