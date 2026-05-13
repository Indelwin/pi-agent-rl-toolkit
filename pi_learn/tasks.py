"""Task loading helpers for the bundled Pi Agent environment dataset."""

from __future__ import annotations

import json
from collections import Counter
from importlib import resources
from pathlib import Path

from .types import LearningTask

_REPO_TASKS_PATH = (
    Path(__file__).resolve().parent.parent
    / "environments"
    / "pi_agent_env"
    / "pi_agent_env"
    / "pi_agent_tasks.json"
)


def load_tasks(path: str | Path | None = None) -> list[LearningTask]:
    """Load Pi Agent tasks from a JSON file or the bundled environment data."""

    data = _load_raw_tasks(path)
    tasks = data.get("tasks", data) if isinstance(data, dict) else data
    if not isinstance(tasks, list):
        raise ValueError("task JSON must contain a tasks array")
    return [LearningTask.from_mapping(task) for task in tasks]


def category_counts(tasks: list[LearningTask]) -> dict[str, int]:
    """Return deterministic category counts for a task list."""

    counts = Counter(task.category for task in tasks)
    return dict(sorted(counts.items()))


def _load_raw_tasks(path: str | Path | None) -> object:
    if path is not None:
        return json.loads(Path(path).read_text())
    if _REPO_TASKS_PATH.exists():
        return json.loads(_REPO_TASKS_PATH.read_text())
    try:
        task_ref = resources.files("pi_agent_env").joinpath("pi_agent_tasks.json")
        return json.loads(task_ref.read_text())
    except (FileNotFoundError, ModuleNotFoundError):
        raise FileNotFoundError("pi_agent_tasks.json not found") from None
