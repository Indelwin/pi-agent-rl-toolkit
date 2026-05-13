"""Mine optimizer-ready examples from rollout traces."""

from __future__ import annotations

from collections.abc import Iterable

from .traces import TraceStore
from .types import OptimizerExample, RolloutTrace


def mine_examples_from_traces(
    source: TraceStore | Iterable[RolloutTrace],
    *,
    program_id: str | None = None,
    status: str = "completed",
    min_reward: float | None = None,
    limit: int | None = None,
) -> list[OptimizerExample]:
    """Return input/output examples from completed rollout traces."""

    if isinstance(source, TraceStore):
        runs = source.list_runs(program_id=program_id, status=status, limit=limit or 100)
    else:
        runs = list(source)
        if program_id is not None:
            runs = [run for run in runs if run.program_id == program_id]
        if status is not None:
            runs = [run for run in runs if run.status == status]
        runs.sort(key=lambda run: run.started_at, reverse=True)
        if limit is not None:
            runs = runs[:limit]

    examples: list[OptimizerExample] = []
    for run in runs:
        if run.output is None:
            continue
        reward = None if run.score is None else run.score.reward
        if min_reward is not None and (reward is None or reward < min_reward):
            continue
        examples.append(
            OptimizerExample(
                id=run.run_id,
                input=run.input,
                output=run.output,
                score=reward,
                meta={
                    "task_id": run.task_id,
                    "category": run.category,
                    "program_id": run.program_id,
                    "model": run.model,
                    "provider": run.provider,
                },
            )
        )
    return examples
