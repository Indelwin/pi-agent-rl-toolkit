"""Core artifact types for Pi learning workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RunStatus = Literal["completed", "failed", "cancelled"]


@dataclass(frozen=True)
class LearningTask:
    """One task row that can drive a rollout, eval, or training example."""

    id: str
    category: str
    name: str
    prompt: str
    requires_tool: bool
    max_tool_calls: int
    verify: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "LearningTask":
        known = {
            "id",
            "category",
            "name",
            "prompt",
            "requires_tool",
            "max_tool_calls",
            "verify",
        }
        return cls(
            id=str(data.get("id", "")),
            category=str(data.get("category", "unknown")),
            name=str(data.get("name", "")),
            prompt=str(data.get("prompt", "")),
            requires_tool=bool(data.get("requires_tool", False)),
            max_tool_calls=int(data.get("max_tool_calls", 10)),
            verify=dict(data.get("verify", {})),
            metadata={k: v for k, v in data.items() if k not in known},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolCallRecord:
    """A model-requested tool call."""

    tool_call_id: str
    tool_name: str
    args: dict[str, Any] = field(default_factory=dict)
    started_at: int | None = None
    completed_at: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolResultRecord:
    """The result paired with a tool call."""

    tool_call_id: str
    tool_name: str
    content: str
    success: bool
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RolloutEvent:
    """One observability event inside a rollout."""

    run_id: str
    ordinal: int
    topic: str
    payload: Any
    created_at: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "RolloutEvent":
        return cls(
            run_id=str(data["run_id"]),
            ordinal=int(data["ordinal"]),
            topic=str(data["topic"]),
            payload=data.get("payload"),
            created_at=int(data["created_at"]),
        )


@dataclass(frozen=True)
class ScoreResult:
    """Scoring output for one rollout."""

    reward: float
    dimensions: dict[str, float] = field(default_factory=dict)
    passed: bool | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ScoreResult":
        return cls(
            reward=float(data.get("reward", 0.0)),
            dimensions={str(k): float(v) for k, v in data.get("dimensions", {}).items()},
            passed=data.get("passed"),
            details=dict(data.get("details", {})),
        )


@dataclass(frozen=True)
class RolloutTrace:
    """Run-level trace used by evals, training, mining, and future UI packages."""

    run_id: str
    program_id: str
    input: dict[str, Any]
    output: dict[str, Any] | None
    status: RunStatus
    started_at: int
    completed_at: int
    duration_ms: int
    task_id: str | None = None
    category: str | None = None
    program_version: str | None = None
    model: str | None = None
    provider: str | None = None
    score: ScoreResult | None = None
    error: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
    events: list[RolloutEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["score"] = None if self.score is None else self.score.to_dict()
        data["events"] = [event.to_dict() for event in self.events]
        return data

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "RolloutTrace":
        score_data = data.get("score")
        events = [
            RolloutEvent.from_mapping(event)
            for event in data.get("events", [])
        ]
        status = data.get("status", "failed")
        if status not in ("completed", "failed", "cancelled"):
            status = "failed"
        return cls(
            run_id=str(data["run_id"]),
            program_id=str(data["program_id"]),
            input=dict(data.get("input", {})),
            output=None if data.get("output") is None else dict(data.get("output", {})),
            status=status,
            started_at=int(data["started_at"]),
            completed_at=int(data["completed_at"]),
            duration_ms=int(data["duration_ms"]),
            task_id=data.get("task_id"),
            category=data.get("category"),
            program_version=data.get("program_version"),
            model=data.get("model"),
            provider=data.get("provider"),
            score=None if score_data is None else ScoreResult.from_mapping(score_data),
            error=data.get("error"),
            meta=dict(data.get("meta", {})),
            events=events,
        )


@dataclass(frozen=True)
class OptimizerExample:
    """Input/output example mined from a completed rollout."""

    id: str
    input: dict[str, Any]
    output: dict[str, Any]
    score: float | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvalReport:
    """Summary of an eval run and its trace outputs."""

    program_id: str
    run_ids: list[str]
    total: int
    completed: int
    failed: int
    cancelled: int
    average_reward: float | None = None
    by_category: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
