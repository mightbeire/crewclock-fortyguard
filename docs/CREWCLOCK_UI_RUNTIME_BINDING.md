# CrewClock UI/runtime binding

## Audit finding

The canonical demo UI is currently `SCRIPTED`, not a live rendering of the Python agent runtime. `src/App.tsx` advances the visible `STAGES` with a local timer and obtains its audit rows from the TypeScript `agentAudit()` helper. Those rows are derived from the deterministic demo run, but the UI does not currently consume `AgentRunner` or `AgentTrace` events.

This is an honest limitation of the current interface, not a claim that the agent is absent. The production runtime is available in `src/fortyguard_agent/agent.py`: `AgentRunner` emits `AgentTrace` events for provider decisions, tool-call start/finish, deterministic terminal states, safe mode, action proposals, and provider telemetry. The offline runtime evaluations exercise that same boundary without Groq, TokenRouter, or FortyGuard calls.

## Binding decision

- `CANONICAL_UI_RUNTIME_BINDING = SCRIPTED`
- `REAL_AGENT_EVENT_STREAM_AVAILABLE_FOR_UX = YES`
- No visual redesign or fake event wiring is included in this correction pass.

The later UX pass may consume a serialized `AgentTrace`/runtime event stream. Until that plumbing is connected, the UI must continue to describe its stage log as demo-derived state and must not present the timer as proof of a live LLM session.
