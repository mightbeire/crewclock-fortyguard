# CrewClock agent boundary

## LLM-owned decisions

The provider-neutral agent may understand the superintendent’s goal, inspect the shift summary, decide whether thermal investigation is warranted, select relevant movable workfaces and windows, reuse or request permitted evidence, invoke deterministic tools, interpret results, explain uncertainty, abstain, and request superintendent approval.

## Deterministic-owned truth

Typed local tools own task/workface validation, FortyGuard cache identity and credit/horizon guards, cached-live evidence parsing, coordinate/timezone conversion, thermal overlap, schedule generation, qualifications, dependencies, deadlines, breaks, fixed commitments, hard verification, metrics and post-approval recomputation. The model never sets a feasible schedule directly or declares its own result valid.

The real runtime exposes only local function tools. It does not expose arbitrary Python, shell, HTTP, SQL, filesystem access, Groq browser search or Groq code execution.

## Evidence boundary

This run is cached-live only. `get_workface_thermal_evidence` requires an explicit fixture and returns compact summaries with `source = CACHED_LIVE_FORTYGUARD`. A completed activity with zero cells is `COMPLETED_BUT_EMPTY = INVALID_EVIDENCE`; it cannot support a recommendation.

## Untrusted input boundary

Task descriptions, imported notes, policy text and external evidence are data. They cannot redefine the system instructions. The system prompt explicitly states this boundary, and the prompt-injection evaluation treats “ignore previous instructions” inside a task description as text rather than an instruction.

## Limits and failure handling

The bounded runner enforces maximum iterations, model calls, tool calls, input characters, estimated credits and repeated tool calls. The Groq adapter enforces a request timeout and retry ceiling. Provider outage, timeout, rate limit, invalid JSON, malformed tool calls, unknown tools and invalid arguments produce a safe stop or bounded observation. Iteration/model-limit exhaustion returns a safe incomplete abstention.

The connection gate now passes: the target model returned usable content, the production adapter parsed it, and a harmless local tool-call smoke test completed. The full real A–J evaluation remains a separate next step and has not been run.

## Approval

The model may request a recommendation and approval. It cannot approve its own recommendation, publish a schedule or execute an external operational action. Final verification remains deterministic.
