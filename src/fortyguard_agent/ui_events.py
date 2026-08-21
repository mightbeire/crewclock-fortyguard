"""Safe UI event projection for the production AgentTrace boundary.

Only high-level operational transitions are exposed. Provider prompts, model
prose, tool arguments, secrets, and hidden reasoning never enter this shape.
"""

from __future__ import annotations

from typing import Any

from .models import AgentState, AgentTrace

UI_EVENT_CONTRACT_VERSION = "crewclock.ui-events.v1"


def _status_for_trace_event(event: str, payload: dict[str, Any]) -> str | None:
    if event == "goal_started":
        return "SHIFT_INSPECTION_STARTED"
    if event == "tool_call_started":
        return {
            "inspect_shift_plan": "SHIFT_INSPECTION_STARTED",
            "identify_thermal_candidates": "THERMAL_INVESTIGATION_REQUIRED",
            "get_workface_thermal_evidence": "THERMAL_EVIDENCE_REQUESTED",
            "generate_feasible_schedule_alternatives": "OPTIMIZATION_STARTED",
            "verify_schedule": "VERIFICATION_STARTED",
            "request_superintendent_approval": "AWAITING_APPROVAL",
        }.get(str(payload.get("tool_name")), "RUNTIME_TOOL_STARTED")
    if event == "tool_call_finished":
        tool = str(payload.get("tool_name"))
        if tool == "inspect_shift_plan":
            return "SHIFT_INSPECTION_COMPLETED"
        if tool == "generate_feasible_schedule_alternatives":
            return "CANDIDATES_GENERATED"
        if tool == "get_workface_thermal_evidence":
            return "THERMAL_EVIDENCE_READY" if payload.get("status") in {"VALID_THERMAL_EVIDENCE", "THERMAL_EVIDENCE_AVAILABLE"} else "THERMAL_EVIDENCE_UNAVAILABLE"
        if tool == "verify_schedule":
            return "VERIFICATION_PASSED" if payload.get("status") == "VERIFIED" else "VERIFICATION_FAILED"
        if tool == "request_superintendent_approval":
            return "AWAITING_APPROVAL" if payload.get("ok") else "FINAL_VERIFICATION_FAILED"
    if event == "action_proposed":
        return "AWAITING_APPROVAL"
    if event == "safe_mode" or event == "provider_error":
        return "AI_ANALYSIS_UNAVAILABLE"
    if event == "provider_telemetry":
        return "RUNTIME_TELEMETRY"
    if event == "deterministic_terminal":
        terminal = str(payload.get("status", "RUN_COMPLETED"))
        return {
            "EVIDENCE_UNAVAILABLE": "THERMAL_EVIDENCE_UNAVAILABLE",
            "NO_FEASIBLE_IMPROVEMENT": "NO_FEASIBLE_IMPROVEMENT",
            "FINAL_VERIFICATION_FAILED": "FINAL_VERIFICATION_FAILED",
            "APPROVED": "APPROVED",
        }.get(terminal, "RUN_COMPLETED")
    if event == "goal_finished":
        return "RUN_COMPLETED"
    return None


def trace_to_ui_events(trace: AgentTrace, state: AgentState, *, run_id: str | None = None) -> list[dict[str, Any]]:
    """Project a real AgentTrace into the browser-safe event contract."""
    effective_run_id = run_id or trace.trace_id
    events: list[dict[str, Any]] = []
    for index, trace_event in enumerate(trace.events):
        status = _status_for_trace_event(trace_event.event, trace_event.payload)
        if status is None:
            continue
        tool = trace_event.payload.get("tool_name")
        source = "DETERMINISTIC_VERIFIER" if tool == "verify_schedule" or trace_event.event == "deterministic_terminal" else "RUNTIME"
        provider = "DETERMINISTIC_LOCAL" if source != "RUNTIME" else "RUNTIME"
        metadata: dict[str, Any] = {"contract_version": UI_EVENT_CONTRACT_VERSION}
        if trace_event.event == "safe_mode":
            metadata.update({"current_plan_preserved": True, "retry_available": True})
        if trace_event.event == "provider_telemetry":
            for key in ("provider_used", "primary_provider", "fallback_used", "fallback_reason", "latency_ms", "model_calls", "tool_calls", "safe_mode_active"):
                if key in trace_event.payload:
                    metadata[key] = trace_event.payload[key]
        events.append({
            "event_id": f"{effective_run_id}-{index + 1:03d}",
            "run_id": effective_run_id,
            "timestamp": trace_event.created_at,
            "stage": str(tool or trace_event.event),
            "status": status,
            "summary": _safe_summary(status, state),
            "source": source,
            "provider": provider,
            "tool": tool,
            "terminal_state": state.operational_state if status in {"RUN_COMPLETED", "THERMAL_EVIDENCE_UNAVAILABLE", "AI_ANALYSIS_UNAVAILABLE", "FINAL_VERIFICATION_FAILED", "APPROVED"} else None,
            "metadata": metadata,
        })
    return events


def _safe_summary(status: str, state: AgentState) -> str:
    if status == "AI_ANALYSIS_UNAVAILABLE":
        return "AI analysis is unavailable; the current plan is preserved and retry is available."
    if status == "THERMAL_EVIDENCE_UNAVAILABLE":
        return "Decision-grade thermal evidence is unavailable; no recommendation was issued."
    if status == "FINAL_VERIFICATION_FAILED":
        return "Final deterministic verification failed; approval was blocked."
    if status == "APPROVED":
        return "The exact verified recommendation was approved."
    if status == "RUN_COMPLETED":
        return f"Runtime completed in state {state.operational_state or 'UNKNOWN'}."
    return status.replace("_", " ").title()
