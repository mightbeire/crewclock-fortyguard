from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
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
    """Provider-neutral Responses API adapter with narrow function tools.

    The deterministic registry remains authoritative. This class only translates
    model tool calls into ``ProviderDecision`` and returns structured tool output
    to the model; it never executes arbitrary code or raw HTTP.
    """

    def __init__(self, client: Any, model: str, tool_schemas: list[dict[str, Any]] | None = None) -> None:
        self.client = client
        self.model = model
        self.tool_schemas = tool_schemas or []
        self.messages: list[dict[str, Any]] = []

    def next_decision(self, state: AgentState) -> ProviderDecision:
        if not self.messages:
            self.messages.append({"role": "user", "content": state.goal.text})
        response = self.client.responses.create(model=self.model, input=self.messages, tools=[{"type": "function", "name": tool["name"], "description": tool["description"], "parameters": tool["parameters"]} for tool in self.tool_schemas])
        output = getattr(response, "output", [])
        for item in output:
            if getattr(item, "type", None) == "function_call":
                arguments = getattr(item, "arguments", "{}")
                return ProviderDecision.call_tool(getattr(item, "name"), json.loads(arguments))
        text = getattr(response, "output_text", "") or "provider_finished_without_tool_call"
        return ProviderDecision.finish(text[:500])

    def observe(self, result: ToolResult, state: AgentState) -> None:
        self.messages.append({"role": "tool", "content": json.dumps(result.to_dict(), sort_keys=True)})


def build_openai_provider(tool_schemas: list[dict[str, Any]]) -> OpenAIResponsesProvider | None:
    """Return a configured real provider, or ``None`` without exposing secrets."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except ImportError:
        return None
    return OpenAIResponsesProvider(OpenAI(api_key=key), os.getenv("OPENAI_MODEL") or "gpt-4.1-mini", tool_schemas)
