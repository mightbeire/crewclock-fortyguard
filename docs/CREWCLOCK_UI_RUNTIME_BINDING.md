# CrewClock UI/runtime binding

## Previous audit finding

The previous canonical UI was `SCRIPTED`, not a live rendering of runtime state. `src/App.tsx` advanced visible `STAGES` with a local timer and obtained audit rows from the TypeScript `agentAudit()` helper. That path has been removed from the canonical browser route.

The earlier Python agent existed separately, but it did not drive the submitted browser. That split has now been removed from the product path.

## Binding decision

- `PREVIOUS_CANONICAL_UI_BINDING = SCRIPTED`
- `CURRENT_CANONICAL_UI_BINDING = REAL_RUNTIME`
- `REAL_AGENT_EVENT_STREAM_AVAILABLE_FOR_UX = YES`

`src/demo/runtime.ts` is now only the browser API client and inert pre-run display state. It contains no scheduling decision call. `src/fortyguard_agent/production_service.py` owns the provider-backed session and emits the safe `RuntimeUiEvent` contract rendered by `src/App.tsx`.

The browser event contract is high-level only: event id, run id, timestamp, stage, status, summary, source, provider, tool name, terminal state, and sanitized metadata. Synthetic positive, saved canonical FortyGuard replay, evidence-unavailable, and all-indoor paths all pass through the same production session runtime. Only the applicable deterministic stages run.

The closure pass replaces that intermediate deterministic browser session with the production API. `POST /api/reviews` starts a real provider-backed orchestration session; `GET /api/reviews/{id}` returns only emitted events and withholds the run result until deterministic work completes. The browser has no imported decision function and no future event array. Presentation timing begins only after an authoritative result exists.
