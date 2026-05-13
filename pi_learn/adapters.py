"""Adapters from Verifiers/Pi-style completions into trace artifacts."""

from __future__ import annotations

import json
import time
from uuid import uuid4
from typing import Any

from .types import (
    LearningTask,
    RolloutEvent,
    RolloutTrace,
    ScoreResult,
    ToolCallRecord,
    ToolResultRecord,
)


def completion_to_tool_records(
    completion: list[Any] | str,
) -> tuple[list[ToolCallRecord], list[ToolResultRecord]]:
    """Extract tool call/result records from OpenAI-compatible messages."""

    if isinstance(completion, str):
        return [], []
    calls: list[ToolCallRecord] = []
    results: list[ToolResultRecord] = []
    call_names: dict[str, str] = {}

    for message in completion:
        if _msg_get(message, "role") != "assistant":
            continue
        for tool_call in _msg_get(message, "tool_calls", []) or []:
            call_id = str(_tc_get(tool_call, "id", ""))
            function = _tc_get(tool_call, "function", {}) or {}
            name = str(_func_get(function, "name", ""))
            args = _parse_args(_func_get(function, "arguments", {}))
            call_names[call_id] = name
            calls.append(
                ToolCallRecord(
                    tool_call_id=call_id,
                    tool_name=name,
                    args=args,
                )
            )

    for message in completion:
        role = _msg_get(message, "role")
        if role not in ("tool", "toolResult"):
            continue
        call_id = str(
            _msg_get(message, "tool_call_id")
            or _msg_get(message, "toolCallId")
            or ""
        )
        content = _content_text(_msg_get(message, "content", ""))
        name = str(
            _msg_get(message, "name")
            or _msg_get(message, "toolName")
            or call_names.get(call_id, "")
        )
        success, error = _tool_success(content)
        results.append(
            ToolResultRecord(
                tool_call_id=call_id,
                tool_name=name,
                content=content,
                success=success,
                error=error,
            )
        )

    return calls, results


def trace_from_verifiers_completion(
    *,
    task: LearningTask,
    completion: list[Any] | str,
    answer: dict[str, Any] | None = None,
    score: ScoreResult | dict[str, Any] | None = None,
    run_id: str | None = None,
    program_id: str = "pi-agent-env",
    program_version: str | None = None,
    model: str | None = None,
    provider: str | None = None,
    started_at: int | None = None,
    completed_at: int | None = None,
    status: str = "completed",
    error: str | None = None,
    meta: dict[str, Any] | None = None,
) -> RolloutTrace:
    """Build a trace from one Verifiers completion."""

    now = int(time.time() * 1000)
    started = now if started_at is None else started_at
    completed = now if completed_at is None else completed_at
    trace_id = run_id or f"run_{uuid4().hex}"
    calls, results = completion_to_tool_records(completion)
    events: list[RolloutEvent] = []
    ordinal = 0
    for call in calls:
        events.append(
            RolloutEvent(
                run_id=trace_id,
                ordinal=ordinal,
                topic="tool.call",
                payload=call.to_dict(),
                created_at=started,
            )
        )
        ordinal += 1
    for result in results:
        events.append(
            RolloutEvent(
                run_id=trace_id,
                ordinal=ordinal,
                topic="tool.result",
                payload=result.to_dict(),
                created_at=completed,
            )
        )
        ordinal += 1

    score_result = score
    if isinstance(score_result, dict):
        score_result = ScoreResult.from_mapping(score_result)

    return RolloutTrace(
        run_id=trace_id,
        task_id=task.id,
        category=task.category,
        program_id=program_id,
        program_version=program_version,
        model=model,
        provider=provider,
        input={
            "prompt": task.prompt,
            "task_id": task.id,
            "category": task.category,
            "requires_tool": task.requires_tool,
            "max_tool_calls": task.max_tool_calls,
        },
        output={
            "response": _final_text(completion),
            "answer": answer if answer is not None else task.verify,
        },
        status=_status(status),
        score=score_result,
        error=error,
        started_at=started,
        completed_at=completed,
        duration_ms=max(0, completed - started),
        meta=meta or {},
        events=events,
    )


def _msg_get(message: Any, key: str, default: Any = None) -> Any:
    if isinstance(message, dict):
        return message.get(key, default)
    return getattr(message, key, default)


def _tc_get(tool_call: Any, key: str, default: Any = None) -> Any:
    if isinstance(tool_call, dict):
        return tool_call.get(key, default)
    return getattr(tool_call, key, default)


def _func_get(function: Any, key: str, default: Any = None) -> Any:
    if isinstance(function, dict):
        return function.get(key, default)
    return getattr(function, key, default)


def _parse_args(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or item))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def _tool_success(content: str) -> tuple[bool, str | None]:
    if not content:
        return False, "empty tool result"
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        error = parsed.get("error")
        if error not in (None, "", False):
            return False, str(error)
        if parsed.get("exit_code", 0) != 0:
            return False, str(parsed.get("output") or "non-zero exit code")
        return True, None
    lowered = content.lower()
    for marker in ("traceback", "exception", "permission denied", "not found"):
        if marker in lowered:
            return False, marker
    return True, None


def _final_text(completion: list[Any] | str) -> str:
    if isinstance(completion, str):
        return completion
    for message in reversed(completion):
        if _msg_get(message, "role") != "assistant":
            continue
        if _msg_get(message, "tool_calls"):
            continue
        content = _content_text(_msg_get(message, "content", ""))
        if content.strip():
            return content.strip()
    return ""


def _status(value: str) -> str:
    if value in ("completed", "failed", "cancelled"):
        return value
    return "failed"
