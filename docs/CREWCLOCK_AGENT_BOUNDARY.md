# CrewClock agent boundary

## LLM-owned decisions

The provider-neutral agent may understand the superintendent’s goal, inspect the shift summary, decide whether thermal investigation is warranted, select relevant movable workfaces and windows, reuse or request permitted evidence, invoke deterministic tools, interpret results, explain uncertainty, abstain, and request superintendent approval.

## Deterministic-owned truth

Typed local tools own task/workface validation, FortyGuard cache identity and credit/horizon guards, cached-live evidence parsing, coordinate/timezone conversion, thermal overlap, schedule generation, qualifications, dependencies, deadlines, breaks, fixed commitments, hard verification, metrics and post-approval recomputation. The model never sets a feasible schedule directly or declares its own result valid.

The real runtime exposes only local function tools. It does not expose arbitrary Python, shell, HTTP, SQL, filesystem access, Groq browser search or Groq code execution.

## Evidence boundary

This run is offline and provider-gated. `get_workface_thermal_evidence` requires an explicit fixture and returns compact summaries with a truthful source state. A completed activity with zero cells is `COMPLETED_BUT_EMPTY = INVALID_EVIDENCE`; it cannot support a recommendation.

SHHCH is deterministic and accepts only valid FortyGuard `exceedance` windows,
polygon workface overlap, and the project modeled-temperature trigger.
`env_params` can provide optional time-matched context but cannot provide
exceedance duration, a diurnal forecast, WBGT, or spatial ranking.

Evidence contracts distinguish `DECISION_GRADE_THERMAL_EVIDENCE` from
`CONTEXTUAL_ENVIRONMENTAL_EVIDENCE`. TCM, env_params, apparent-temperature
curves and illustrative visuals cannot satisfy SHHCH. Every decision-grade
window binds AOI, date, start/end, timezone, analytic source, project trigger,
units, direction, provenance, and result hash/version. `RECHECK_THERMAL_EVIDENCE`
preserves the current schedule, clears invalid evidence, and retries only when
explicitly invoked.

Terminal states are explicit: `NO_ACTION_REQUIRED`, `EVIDENCE_UNAVAILABLE`,
`KEEP_CURRENT_PLAN`, `KEEP_CURRENT_PLAN_AND_RECHECK`,
`NO_FEASIBLE_IMPROVEMENT`, `AWAITING_APPROVAL`, `APPROVED`, `REJECTED`, and
`ERROR_SAFE`, and `FINAL_VERIFICATION_FAILED`. A schedule-changing
recommendation is not ready before deterministic verification; approval moves
through `AWAITING_APPROVAL` → `APPROVAL_RECEIVED` → final deterministic
verification → `APPROVED`.

## Untrusted input boundary

Task descriptions, imported notes, policy text and external evidence are data. They cannot redefine the system instructions. The system prompt explicitly states this boundary, and the prompt-injection evaluation treats “ignore previous instructions” inside a task description as text rather than an instruction.

## Limits and failure handling

The bounded runner enforces maximum iterations, model calls, tool calls, input characters, estimated credits and repeated tool calls. The production provider route is Groq → TokenRouter Qwen → deterministic safe mode with a one-way failover ceiling, configurable per-turn/total interactive budgets, and zero interactive provider retries. Provider outage, timeout, rate limit, invalid JSON, malformed tool calls, unknown tools and invalid arguments produce a safe stop or bounded observation. Iteration/model-limit exhaustion returns a safe incomplete abstention.

The connection gate now passes: the target model returned usable content, the production adapter parsed it, and a harmless local tool-call smoke test completed. Real evaluation transport failures are classified separately from agent behavior, paced from returned Groq headers, retried within a bounded ceiling, and checkpointed for resume. No provider interruption is reported as a behavioral scenario failure. The deterministic demo provider remains the fallback when real evidence is incomplete.

Rate-aware execution is infrastructure reliability only. It does not change the product policy, thermal model, deterministic scheduler, verification boundary or superintendent approval boundary.

## Approval

The model may request a recommendation and approval. It cannot approve its own recommendation, publish a schedule or execute an external operational action. Final verification remains deterministic.
