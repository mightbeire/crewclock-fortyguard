from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class GuardrailError(RuntimeError):
    pass


@dataclass
class Budget:
    max_iterations: int = 8
    max_tool_calls: int = 12
    max_api_credits: int = 20
    estimated_costs: dict[str, int] = field(default_factory=dict)
    iterations: int = 0
    tool_calls: int = 0
    api_credits_reserved: int = 0

    def before_iteration(self) -> None:
        if self.iterations >= self.max_iterations:
            raise GuardrailError("iteration_limit_reached")
        self.iterations += 1

    def reserve_tool(self, tool_name: str) -> int:
        if self.tool_calls >= self.max_tool_calls:
            raise GuardrailError("tool_call_limit_reached")
        cost = int(self.estimated_costs.get(tool_name, 1))
        if self.api_credits_reserved + cost > self.max_api_credits:
            raise GuardrailError("api_credit_budget_reached")
        self.tool_calls += 1
        self.api_credits_reserved += cost
        return cost


@dataclass
class SafetyPolicy:
    allowed_tools: set[str]
    approval_required_actions: set[str] = field(default_factory=lambda: {"schedule_change", "dispatch", "maintenance_window", "send_alert"})
    max_repeated_tool_calls: int = 1

    def check_tool(self, name: str, previous_calls: list[str]) -> None:
        if name not in self.allowed_tools:
            raise GuardrailError(f"tool_not_allowed:{name}")
        if previous_calls.count(name) >= self.max_repeated_tool_calls:
            raise GuardrailError(f"repeated_tool_call_blocked:{name}")

    def needs_approval(self, action_type: str) -> bool:
        return action_type in self.approval_required_actions
