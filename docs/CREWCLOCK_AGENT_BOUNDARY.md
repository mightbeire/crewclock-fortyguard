# CrewClock agent boundary

## LLM-owned decisions

The provider-neutral agent may inspect the incoming shift plan, classify outdoor/fixed/movable work, select a small number of decision-relevant workfaces and windows, decide whether cached evidence is sufficient, choose whether selective enrichment is justified, invoke deterministic tools, interpret structured results, explain uncertainty, stop when more calls are not justified, and request superintendent approval.

## Deterministic-owned truth

Typed tools and local code own FortyGuard request guards, schema/unit validation, cache identity, credit budgets, polygon overlap, thermal interval arithmetic, candidate generation, qualifications, dependencies, deadlines, fixed commitments, crew availability, employer controls, mandatory breaks, comparison metrics, approval re-verification, and deterministic replay.

The LLM never receives unrestricted raw HTTP and never sets a task start time directly. A malformed or wrong model call fails closed, falls back to the original plan, or requests human clarification.

## Approval

The proposal shows original versus proposed plan, moved tasks, evidence, policy implication, metric change, and constraint results. The superintendent can approve or reject. Publication is blocked until approval; final deterministic verification runs after approval.

Failure states include no investigation required, unsupported forecast horizon, unavailable/stale evidence, policy ambiguity, hard constraint failure, no feasible improvement, no meaningful thermal delta, and approval rejection.
