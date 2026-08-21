# CrewClock UI/runtime binding

## Previous audit finding

The previous canonical UI was `SCRIPTED`, not a live rendering of runtime state. `src/App.tsx` advanced visible `STAGES` with a local timer and obtained audit rows from the TypeScript `agentAudit()` helper. That path has been removed from the canonical browser route.

This is an honest limitation of the current interface, not a claim that the agent is absent. The production runtime is available in `src/fortyguard_agent/agent.py`: `AgentRunner` emits `AgentTrace` events for provider decisions, tool-call start/finish, deterministic terminal states, safe mode, action proposals, and provider telemetry. The offline runtime evaluations exercise that same boundary without Groq, TokenRouter, or FortyGuard calls.

## Binding decision

- `PREVIOUS_CANONICAL_UI_BINDING = SCRIPTED`
- `CURRENT_CANONICAL_UI_BINDING = REAL_RUNTIME`
- `REAL_AGENT_EVENT_STREAM_AVAILABLE_FOR_UX = YES`

The canonical route now uses `src/demo/runtime.ts`: `RuntimeSession` is produced by the deterministic runtime engine, normalized to the safe `RuntimeUiEvent` contract, and rendered by `src/App.tsx`. The Python production boundary has the corresponding `trace_to_ui_events()` projection in `src/fortyguard_agent/ui_events.py`, which consumes actual `AgentTrace` and `AgentState` values without exposing prompts, secrets, or reasoning.

The browser event contract is high-level only: event id, run id, timestamp, stage, status, summary, source, provider, tool name, terminal state, and sanitized metadata. The canonical Phoenix path is generated from the runtime’s unavailable-evidence result and ends in current-plan preservation plus recheck availability. Synthetic positive evidence is explicitly labeled and passes through the same optimizer, verifier, identity binding, and runtime event adapter.

The visual UX pass may refine presentation, but the event plumbing is now connected: the browser consumes deterministic runtime results through `RuntimeSession` and the safe event contract. A live provider-backed AgentTrace transport is not required for this offline build and remains outside this pass; no UI event claims that Groq, TokenRouter, or FortyGuard ran.
