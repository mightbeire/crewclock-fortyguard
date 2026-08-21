# CrewClock provider failover

CrewClock uses one deterministic-first state machine and one typed local tool
registry for every model provider. The production route is:

`Groq (primary) → TokenRouter Qwen (secondary) → deterministic safe mode`

The adapters normalize OpenAI-compatible chat-completions responses into the
same `ProviderDecision` shape. They never execute tools, calculate SHHCH,
generate schedules, verify constraints, or approve recommendations.

## Routing policy

- Groq success continues on Groq.
- Groq 429, timeout, network failure, transient 5xx, or fatal configuration
  failure makes one immediate switch to TokenRouter.
- Provider retry ceilings are zero in the interactive failover route, so a
  `Retry-After` header cannot create a multi-minute spinner.
- TokenRouter failure, capacity exhaustion, malformed provider response, or an
  interactive budget breach terminates in deterministic safe mode.
- The route never switches back and never bounces indefinitely.

## Handoff

The secondary receives a compact structured continuation containing the goal,
shift summary, evidence/scheduler state, recent deterministic statuses,
verification/provenance summaries, proposals, and approval state. Raw geometry,
GeoJSON, map payloads, and model prose are excluded.

## Safe mode

Safe mode returns `AI_ANALYSIS_UNAVAILABLE`, preserves the current plan, keeps
deterministic checks visible, and marks retry as available. It reports zero
fabricated values and cannot create a recommendation or approve a plan.

Interactive defaults are configurable through `.env`:

```text
LLM_INTERACTIVE_TIMEOUT_MS=8000
LLM_MAX_INTERACTIVE_TOTAL_MS=15000
LLM_MAX_INTERACTIVE_MODEL_TURNS=3
```

Telemetry contains provider/model, fallback reason, latency, model/tool call
counts, token usage, prompt estimates, and a false chain-of-thought exposure
flag. It contains no API keys or model reasoning.
