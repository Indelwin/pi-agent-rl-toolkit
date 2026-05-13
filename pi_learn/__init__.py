"""Reusable learning utilities for Pi Agent training and evaluation."""

from .adapters import completion_to_tool_records, trace_from_verifiers_completion
from .metrics import (
    all_fields_match,
    average_metrics,
    contains_field_match,
    exact_field_match,
    jaccard_field_similarity,
)
from .mining import mine_examples_from_traces
from .tasks import category_counts, load_tasks
from .traces import TraceStore
from .types import (
    EvalReport,
    LearningTask,
    OptimizerExample,
    RolloutEvent,
    RolloutTrace,
    ScoreResult,
    ToolCallRecord,
    ToolResultRecord,
)

__all__ = [
    "EvalReport",
    "LearningTask",
    "OptimizerExample",
    "RolloutEvent",
    "RolloutTrace",
    "ScoreResult",
    "ToolCallRecord",
    "ToolResultRecord",
    "TraceStore",
    "all_fields_match",
    "average_metrics",
    "category_counts",
    "completion_to_tool_records",
    "contains_field_match",
    "exact_field_match",
    "jaccard_field_similarity",
    "load_tasks",
    "mine_examples_from_traces",
    "trace_from_verifiers_completion",
]
