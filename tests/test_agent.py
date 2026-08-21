from fortyguard_agent.agent import AgentRunner, ToolRegistry, ToolSpec
from fortyguard_agent.guardrails import Budget, SafetyPolicy
from fortyguard_agent.models import ActionProposal, AgentState, Goal, Provenance, ToolResult
from fortyguard_agent.providers import MockProvider, ProviderDecision


def ok_tool(arguments: dict) -> ToolResult:
    return ToolResult({"seen": arguments}, Provenance(source="mock", endpoint="local:test"))


def test_agent_stops_for_approval() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("inspect", "Inspect", {"type": "object"}, ok_tool))
    provider = MockProvider([
        ProviderDecision.call_tool("inspect", {"site": "A"}),
        ProviderDecision.propose(ActionProposal("schedule_change", "Move job", {"hour": 8}, 0.9)),
    ])
    runner = AgentRunner(registry, provider, budget=Budget(max_iterations=3, max_tool_calls=2, max_api_credits=2), policy=SafetyPolicy(allowed_tools={"inspect"}))
    state, trace = runner.run(AgentState(Goal("choose a window", "supervisor")))
    assert state.termination_reason == "awaiting_human_approval"
    assert len(state.approvals) == 1
    assert any(event.event == "tool_call_finished" for event in trace.events)


def test_repeated_tool_calls_are_blocked() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("inspect", "Inspect", {"type": "object"}, ok_tool))
    provider = MockProvider([
        ProviderDecision.call_tool("inspect", {}),
        ProviderDecision.call_tool("inspect", {}),
    ])
    runner = AgentRunner(registry, provider, budget=Budget(max_iterations=4, max_tool_calls=4, max_api_credits=4), policy=SafetyPolicy(allowed_tools={"inspect"}))
    state, _ = runner.run(AgentState(Goal("inspect", "operator")))
    assert state.termination_reason == "repeated_tool_call_blocked:inspect"


def test_missing_required_arguments_stop_without_crashing() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("inspect", "Inspect", {"type": "object", "required": ["site"]}, ok_tool))
    provider = MockProvider([ProviderDecision.call_tool("inspect", {})])
    runner = AgentRunner(registry, provider, budget=Budget(max_iterations=2, max_tool_calls=2, max_api_credits=2), policy=SafetyPolicy(allowed_tools={"inspect"}))
    state, _ = runner.run(AgentState(Goal("inspect", "operator")))
    assert state.termination_reason == "missing_tool_arguments:inspect:site"


def test_approval_can_be_resolved_without_executing_action() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("inspect", "Inspect", {"type": "object"}, ok_tool))
    provider = MockProvider([ProviderDecision.propose(ActionProposal("schedule_change", "Move job", {}, 0.9))])
    runner = AgentRunner(registry, provider, budget=Budget(max_iterations=2, max_tool_calls=1, max_api_credits=1), policy=SafetyPolicy(allowed_tools={"inspect"}))
    state, _ = runner.run(AgentState(Goal("choose", "operator")))
    runner.resolve_approval(state, 0, True)
    assert state.approvals[0].status == "rejected"
    assert state.termination_reason == "FINAL_VERIFICATION_FAILED"


def test_handler_failure_becomes_observation_and_provider_can_finish() -> None:
    def fail(_: dict) -> ToolResult:
        raise RuntimeError("temporary upstream failure")

    registry = ToolRegistry()
    registry.register(ToolSpec("inspect", "Inspect", {"type": "object"}, fail))
    provider = MockProvider([ProviderDecision.call_tool("inspect", {}), ProviderDecision.finish("insufficient_evidence")])
    runner = AgentRunner(registry, provider, budget=Budget(max_iterations=3, max_tool_calls=2, max_api_credits=2), policy=SafetyPolicy(allowed_tools={"inspect"}))
    state, trace = runner.run(AgentState(Goal("inspect", "operator")))
    assert state.termination_reason == "ERROR_SAFE"
    assert state.observations[0].kind == "error"
    assert state.observations[0].content["error"] == "tool_execution_error:RuntimeError"
    assert any(event.event == "tool_call_finished" and event.payload["ok"] is False for event in trace.events)


def test_provider_failure_stops_with_redacted_trace() -> None:
    class FailingProvider:
        def next_decision(self, state: AgentState) -> ProviderDecision:
            raise RuntimeError("fg_live_" + "super_secret")

        def observe(self, result: ToolResult, state: AgentState) -> None:
            return None

    registry = ToolRegistry()
    registry.register(ToolSpec("inspect", "Inspect", {"type": "object"}, ok_tool))
    runner = AgentRunner(registry, FailingProvider(), budget=Budget(max_iterations=1, max_tool_calls=1, max_api_credits=1), policy=SafetyPolicy(allowed_tools={"inspect"}))
    state, trace = runner.run(AgentState(Goal("inspect", "operator")))
    assert state.termination_reason == "provider_error:RuntimeError"
    provider_error = next(event for event in trace.events if event.event == "provider_error")
    assert "fg_live_" + "super_secret" not in provider_error.payload["error"]
    assert "REDACTED" in provider_error.payload["error"]
