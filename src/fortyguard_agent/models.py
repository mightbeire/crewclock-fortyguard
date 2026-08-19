from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Provenance:
    source: Literal["live", "cached", "sample", "derived", "heuristic", "mock"]
    endpoint: str | None = None
    request_hash: str | None = None
    retrieved_at: str = field(default_factory=utc_now)
    activity_id: str | None = None
    assumptions: tuple[str, ...] = ()


@dataclass
class ToolResult:
    data: dict[str, Any]
    provenance: Provenance
    error: str | None = None
    estimated_credits: int = 0

    @property
    def ok(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": self.data,
            "provenance": asdict(self.provenance),
            "error": self.error,
            "estimated_credits": self.estimated_credits,
        }


@dataclass(frozen=True)
class Goal:
    text: str
    user: str
    constraints: dict[str, Any] = field(default_factory=dict)
    success_metric: str = "Produce a traceable recommendation that improves the stated metric."
    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Observation:
    kind: Literal["tool_result", "note", "error"]
    content: dict[str, Any]
    created_at: str = field(default_factory=utc_now)


@dataclass
class ActionProposal:
    action_type: str
    description: str
    parameters: dict[str, Any]
    confidence: float
    requires_approval: bool = True
    evidence: list[str] = field(default_factory=list)


@dataclass
class ApprovalRequest:
    proposal: ActionProposal
    status: Literal["pending", "approved", "rejected"] = "pending"
    requested_at: str = field(default_factory=utc_now)
    decided_at: str | None = None


@dataclass
class AgentState:
    goal: Goal
    observations: list[Observation] = field(default_factory=list)
    proposals: list[ActionProposal] = field(default_factory=list)
    approvals: list[ApprovalRequest] = field(default_factory=list)
    iteration: int = 0
    terminated: bool = False
    termination_reason: str | None = None


@dataclass
class TraceEvent:
    event: str
    payload: dict[str, Any]
    created_at: str = field(default_factory=utc_now)


@dataclass
class AgentTrace:
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    events: list[TraceEvent] = field(default_factory=list)

    def record(self, event: str, **payload: Any) -> None:
        self.events.append(TraceEvent(event=event, payload=payload))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
