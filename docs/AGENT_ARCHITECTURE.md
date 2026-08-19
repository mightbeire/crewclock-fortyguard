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

## Verification semantics

The core loop does not declare success merely because a proposal was generated. A candidate product must run a verification tool or deterministic evaluator that recomputes the stated metric under the same constraints. The current spike uses a transparent degree-hour proxy and labels it heuristic/derived.

## Future provider adapter contract

An online provider should receive the goal, constraint summary, observation summaries, and tool schemas; it should return a structured tool call or proposal. It must not receive or emit credentials. The adapter must translate malformed or refusal responses into a bounded `finish`/error decision and must keep tool execution in this repository.
