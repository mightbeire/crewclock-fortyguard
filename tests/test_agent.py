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
