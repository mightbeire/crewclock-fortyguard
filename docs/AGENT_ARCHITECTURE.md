# Reusable agent architecture

```text
User / Event
     ↓
Goal + constraints + success metric
     ↓
Provider-neutral planner
     ↓
Tool registry + JSON schemas + allowlist
     ↓
FortyGuard tool call (cached/live/sample)
     ↓
Observation with provenance
     ↓
Reasoning/result separated by provider decision
     ↓
Action proposal
     ↓
Constraint and safety checks
     ↓
Human approval checkpoint
     ↓
Action / recommendation
     ↓
Verification metric
     ↓
Updated state / graceful stop
```

## Implemented concepts

- `Goal`, `AgentState`, `Observation`, `ActionProposal`, `ApprovalRequest`, and trace events.
- `ToolRegistry` with descriptions and input schemas.
- Provider-neutral `ProviderDecision`, deterministic `MockProvider`, and hosted adapter seam.
- `Budget` for maximum iterations, tool calls, estimated API credits, and provider cost isolation.
- `SafetyPolicy` for allowed tools, repeated-call prevention, and approval-required action types.
- Tool argument validation stops missing required fields before handler execution; handler failures become bounded observations instead of crashing the run.
- `JsonCache` keyed by canonical endpoint/payload hash with atomic writes.
- FortyGuard toolkit with live/cached/sample provenance and bounded errors.
- Derived metric separation: measured API values are not mislabeled as recommendations.
- Graceful stop on provider exhaustion, malformed decisions, budget exhaustion, unknown tools, and repeat calls.
- Trace and error redaction for API keys, tokens, and credential-like fields.
- Explicit approval resolution records approved/rejected state and timestamp without executing an external action.
- Separate baseline evaluator reports no-assistance, static-threshold, naive-first-choice, and agent-verified proxy results.
- Conditional stress scenarios demonstrate both evidence-sufficient stopping and evidence-insufficient fallback investigation before approval.
- Provider exceptions terminate with a bounded, redacted uncertainty reason; they do not leak credentials or crash the run.

## Verification semantics

The core loop does not declare success merely because a proposal was generated. A candidate product must run a verification tool or deterministic evaluator that recomputes the stated metric under the same constraints. The current spike uses a transparent degree-hour proxy and labels it heuristic/derived.

## Reusable presentation layer

The demo shell is intentionally decoupled from product selection and the live API adapter:

- `src/demo/scenario.ts` contains sanitized cached-live measurements, explicitly synthetic operational constraints, high-level tool/action labels and a recomputable result.
- `src/App.tsx` renders the map, agent activity sequence, before/after comparison, human approval and evidence drawer.
- The browser invokes the thin CrewClock production API. Sample/canonical demos resolve approved saved evidence IDs, while user-created supported U.S. sites can invoke the narrow trusted FortyGuard heatmap acquisition path after deterministic inspection; the model never receives credentials, raw HTTP or filesystem paths.
- Activity labels disclose tool/action states only. They do not expose private model reasoning.
- Approval binds to the exact sealed recommendation and triggers final deterministic re-verification. This MVP does not mutate an external scheduling system.

### Finalist showdown state contract

All three micro-demos use the same deterministic UI state machine:

```text
opening → investigating evidence/alternatives → proposal ready
        → human approval → verification → verified result
```

The product object is injected from `SCENARIOS` (`delivery`, `race`, or `campus`). The proposal is drawn as a non-committed dashed transformation; the route/course/schedule changes only after approval, and the hero metric appears only after the verification state. This prevents visual polish from implying that a recommendation executed itself.

## Future provider adapter contract

An online provider should receive the goal, constraint summary, observation summaries, and tool schemas; it should return a structured tool call or proposal. It must not receive or emit credentials. The adapter must translate malformed or refusal responses into a bounded `finish`/error decision and must keep tool execution in this repository.
