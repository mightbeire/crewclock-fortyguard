"""Stress conditional investigation, stopping, recovery, and approval behavior."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fortyguard_agent.agent import AgentRunner, ToolRegistry, ToolSpec
from fortyguard_agent.guardrails import Budget, SafetyPolicy
from fortyguard_agent.models import ActionProposal, AgentState, Goal, Provenance, ToolResult
from fortyguard_agent.providers import ProviderDecision


class AdaptiveProvider:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.observations: list[ToolResult] = []

    def next_decision(self, state: AgentState) -> ProviderDecision:
        if not self.observations:
            return ProviderDecision.call_tool("primary_evidence", {})
        last = self.observations[-1]
        if self.mode == "enough" and last.ok:
            return ProviderDecision.finish("enough_evidence_no_extra_call")
        if self.mode == "replan" and not last.ok:
            if len(self.observations) == 1:
                return ProviderDecision.call_tool("fallback_evidence", {})
        if self.mode == "replan" and len(self.observations) == 2 and last.ok:
            return ProviderDecision.propose(ActionProposal("schedule_change", "Use the fallback evidence to draft a human-reviewed schedule change.", {}, 0.7, True, ["fallback evidence verified"]))
        return ProviderDecision.finish("no_safe_decision")

    def observe(self, result: ToolResult, state: AgentState) -> None:
        self.observations.append(result)


def run(mode: str) -> dict[str, Any]:
    registry = ToolRegistry()

    def primary(_: dict[str, Any]) -> ToolResult:
        if mode == "replan":
            return ToolResult({}, Provenance(source="live", endpoint="/v1/heatmap"), error="coverage_gap")
        return ToolResult({"confidence": 0.86}, Provenance(source="cached", endpoint="/v1/env_params"))

    def fallback(_: dict[str, Any]) -> ToolResult:
        return ToolResult({"confidence": 0.71}, Provenance(source="cached", endpoint="/v1/heatmap"))

    registry.register(ToolSpec("primary_evidence", "Primary evidence", {"type": "object"}, primary))
    registry.register(ToolSpec("fallback_evidence", "Fallback evidence", {"type": "object"}, fallback))
    provider = AdaptiveProvider(mode)
    state, trace = AgentRunner(registry, provider, budget=Budget(max_iterations=5, max_tool_calls=3, max_api_credits=3), policy=SafetyPolicy(allowed_tools=registry.names())).run(AgentState(Goal("test adaptive evidence", "operator")))
    return {"mode": mode, "termination": state.termination_reason, "tool_calls": len(provider.observations), "trace_events": len(trace.events), "approval_count": len(state.approvals), "passed": (mode == "enough" and state.termination_reason == "enough_evidence_no_extra_call" and len(provider.observations) == 1) or (mode == "replan" and state.termination_reason == "awaiting_human_approval" and len(provider.observations) == 2)}


def main() -> None:
    results = [run("enough"), run("replan")]
    print(json.dumps({"results": results, "all_passed": all(item["passed"] for item in results)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
