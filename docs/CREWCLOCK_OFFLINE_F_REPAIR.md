# CrewClock offline F repair

The retained F-1 trace showed one successful `inspect_shift_plan` call followed
by an LLM prose stop. The prose correctly mentioned `COMPLETED_BUT_EMPTY` and
preserving the current plan, but the runtime stored that text as
`approval_or_pending`; no structured evidence result or terminal state existed.
The exact defect was accepting a provider `finish` event as workflow completion
before validating the deterministic CrewClock state.

The runtime now derives `EVIDENCE_UNAVAILABLE` from structured workflow input or
tool output before a model can schedule, calculate thermal overlap/SHHCH, claim
an improvement, or request approval. Equivalent invalid evidence labels are
normalized to one authoritative envelope:

- `valid: false`
- `current_plan_preserved: true`
- `thermal_optimization_allowed: false`
- `next_allowed_actions: [KEEP_CURRENT_PLAN, RECHECK_AVAILABLE]`

Provider stops are transport events, not terminal states. A non-terminal stop
gets one bounded continuation; a second non-terminal stop becomes
`ERROR_SAFE`. `EVIDENCE_UNAVAILABLE` remains distinct from
`AI_ANALYSIS_UNAVAILABLE`: the former means thermal evidence is invalid, while
the latter means both inference providers were unavailable.

The repair is runtime/state-machine enforcement, with offline adversarial tests;
it makes no live Groq, TokenRouter, or FortyGuard requests and does not branch
on scenario names.
