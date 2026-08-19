from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .models import ActionProposal, AgentState, ToolResult


@dataclass
class ProviderDecision:
    kind: str
    tool_name: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    proposal: ActionProposal | None = None
    message: str = ""

    @classmethod
    def call_tool(cls, name: str, arguments: dict[str, Any]) -> "ProviderDecision":
        return cls(kind="tool_call", tool_name=name, arguments=arguments)

    @classmethod
    def propose(cls, proposal: ActionProposal) -> "ProviderDecision":
        return cls(kind="proposal", proposal=proposal)

    @classmethod
    def finish(cls, message: str) -> "ProviderDecision":
        return cls(kind="finish", message=message)


class LLMProvider(Protocol):
    def next_decision(self, state: AgentState) -> ProviderDecision:
        ...

    def observe(self, result: ToolResult, state: AgentState) -> None:
        ...


class MockProvider:
    """Deterministic provider used for tests and offline spikes."""

    def __init__(self, decisions: list[ProviderDecision]) -> None:
        self.decisions = list(decisions)
        self.index = 0
        self.observations: list[ToolResult] = []

    def next_decision(self, state: AgentState) -> ProviderDecision:
        if self.index >= len(self.decisions):
            return ProviderDecision.finish("mock_provider_exhausted")
        decision = self.decisions[self.index]
        self.index += 1
        return decision

    def observe(self, result: ToolResult, state: AgentState) -> None:
        self.observations.append(result)


class OpenAIResponsesProvider:
    """Hosted-provider seam; intentionally inert until an API key is configured.

    The adapter keeps provider-specific code out of the agent loop. A production
    implementation should translate the provider response into ProviderDecision
    and keep all action execution behind this repository's tool registry.
    """

    def __init__(self, client: Any, model: str) -> None:
        self.client = client
        self.model = model

    def next_decision(self, state: AgentState) -> ProviderDecision:
        raise NotImplementedError("Hosted adapter seam is configured, but response translation is not enabled in exploration mode.")

    def observe(self, result: ToolResult, state: AgentState) -> None:
        return None
