from __future__ import annotations

"""Run only the seven outstanding real CrewClock behavior-gate trials.

This imports the existing scenario/fixture definitions but routes every trial
through the production one-way Groq -> TokenRouter -> safe-mode provider route.
It persists high-level evidence only: no model prose, reasoning, or secrets.
It never constructs a FortyGuard client and is intentionally not the A-J suite.
"""

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fortyguard_agent.agent import AgentRunner
from fortyguard_agent.guardrails import Budget, SafetyPolicy
from fortyguard_agent.models import AgentState, Goal
from fortyguard_agent.providers import build_failover_provider, load_project_env


EVIDENCE_DIR = ROOT / "evidence" / "crewclock-real-agent-eval"
OUTPUT_PATH = EVIDENCE_DIR / "final_behavior_gate.json"

_spec = importlib.util.spec_from_file_location("run_real_agent_eval", ROOT / "scripts" / "run_real_agent_eval.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("real_agent_eval_module_unavailable")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

TARGETS = [("A", 1), ("E", 1), ("E", 2), ("F", 1), ("H", 1), ("H", 2), ("H", 3)]


def _observation_summaries(state: Any) -> list[dict[str, Any]]:
    rows = []
    for observation in state.observations:
        content = observation.content if isinstance(observation.content, dict) else {}
        data = content.get("data", {}) if isinstance(content.get("data", {}), dict) else {}
        provenance = content.get("provenance", {}) if isinstance(content.get("provenance", {}), dict) else {}
        rows.append({
            "kind": observation.kind,
            "status": data.get("status") or data.get("state") or data.get("evidence_status") or ("ERROR" if observation.kind == "error" else "OK"),
            "decision_relevant_result": data.get("decision_relevant_result"),
            "valid": data.get("valid"),
            "original_evidence_status": data.get("original_evidence_status"),
            "source": provenance.get("source"),
            "assumptions": list(provenance.get("assumptions", []))[:2],
        })
    return rows


def _classify(result: dict[str, Any]) -> str | None:
    if result.get("passed"):
        return None
    if result.get("safe_mode") or result.get("provider_failure") in {"AI_PROVIDERS_UNAVAILABLE", "INTERACTIVE_BUDGET_EXCEEDED"}:
        return "PROVIDER_INFRA_FAILURE"
    if result.get("tool_failures"):
        return "DETERMINISTIC_TOOL_FAILURE"
    return "AGENT_BEHAVIOR_FAILURE"


def _run_trial(case_key: str, ordinal: int) -> dict[str, Any]:
    case = _module.CASES[case_key]
    registry = _module._registry(case)
    route = build_failover_provider(
        registry.schemas(),
        timeout_ms=8_000,
        max_total_ms=90_000,
        max_model_turns=8,
    )
    runner = AgentRunner(
        registry,
        route,
        budget=Budget(max_iterations=10, max_model_calls=10, max_tool_calls=10, max_api_credits=10),
        policy=SafetyPolicy(allowed_tools=registry.names()),
    )
    started = time.perf_counter()
    state, trace = runner.run(AgentState(Goal(case.goal, "superintendent", constraints=case.constraints(), success_metric="Make only a defensible evidence-grounded planning decision.")))
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    telemetry = route.telemetry()
    tool_names = [event.payload.get("tool_name") for event in trace.events if event.event == "tool_call_finished"]
    failures = [event.payload.get("error") for event in trace.events if event.event == "tool_call_finished" and event.payload.get("error")]
    guardrails = [event.payload.get("reason") for event in trace.events if event.event == "guardrail_stop"]
    provider_errors = [event.payload.get("error") for event in trace.events if event.event == "provider_error"]
    result: dict[str, Any] = {
        "scenario": case_key,
        "trial": ordinal,
        "run_id": f"{case_key}-{ordinal}-final-gate",
        "initial_provider": "GROQ",
        "final_provider": telemetry.get("provider_used"),
        "fallback_used": telemetry.get("fallback_used", False),
        "fallback_reason": telemetry.get("fallback_reason"),
        "model": telemetry.get("model"),
        "tool_trace": tool_names,
        "tool_failures": failures,
        "guardrail_stops": guardrails,
        "provider_errors": provider_errors,
        "provider_failure": telemetry.get("provider_failure"),
        "observations": _observation_summaries(state),
        "termination": _module._termination_class(state.termination_reason),
        "terminal_state": state.termination_reason,
        "approval_tool_called": "request_superintendent_approval" in tool_names,
        "self_approved": any(
            (content.get("data", {}) if isinstance(content.get("data", {}), dict) else {}).get("approved") is True
            or (content.get("data", {}) if isinstance(content.get("data", {}), dict) else {}).get("status") == "APPROVED"
            for content in (observation.content for observation in state.observations)
        ),
        "model_calls": telemetry.get("model_calls", 0),
        "tool_calls": telemetry.get("tool_calls", 0),
        "input_tokens": telemetry.get("input_tokens", 0),
        "output_tokens": telemetry.get("output_tokens", 0),
        "total_tokens": telemetry.get("total_tokens", 0),
        "latency_ms": elapsed_ms,
        "provider_latency_ms": telemetry.get("latency_ms"),
        "provider_requests": {
            "GROQ": int(getattr(route.primary, "request_count", 0)),
            "TOKENROUTER": int(getattr(route.secondary, "request_count", 0)),
        },
        "safe_mode": telemetry.get("safe_mode_active", False),
        "reasoning_content_persisted": False,
        "chain_of_thought_exposed": False,
    }
    result["passed"] = _module._pass(case, result)
    result["failure_classification"] = _classify(result)
    result["status"] = "COMPLETED" if result["passed"] or not result["safe_mode"] else "INCOMPLETE"
    return result


def _write(rows: list[dict[str, Any]], *, started_at: str) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "provider_route": "GROQ -> TOKENROUTER -> DETERMINISTIC_SAFE_MODE",
        "model_primary": "openai/gpt-oss-120b",
        "model_secondary": "qwen/qwen3.8-max-free",
        "live_fortyguard_calls": 0,
        "started_at": started_at,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "targets": [f"{key}-{ordinal}" for key, ordinal in TARGETS],
        "trials": rows,
        "new_behavioral_trials": len(rows),
        "behavioral_failures_new": sum(row.get("failure_classification") == "AGENT_BEHAVIOR_FAILURE" for row in rows),
        "provider_infra_failures_new": sum(row.get("failure_classification") == "PROVIDER_INFRA_FAILURE" for row in rows),
        "deterministic_tool_failures_new": sum(row.get("failure_classification") == "DETERMINISTIC_TOOL_FAILURE" for row in rows),
        "safe_mode_events": sum(bool(row.get("safe_mode")) for row in rows),
        "chain_of_thought_exposed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    load_project_env()
    started_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    for case_key, ordinal in TARGETS:
        result = _run_trial(case_key, ordinal)
        rows.append(result)
        _write(rows, started_at=started_at)
        print(json.dumps({key: result[key] for key in ("scenario", "trial", "final_provider", "fallback_used", "fallback_reason", "passed", "failure_classification", "terminal_state", "latency_ms", "model_calls", "tool_calls")}, separators=(",", ":")))
    return 0 if all(row.get("passed") for row in rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
