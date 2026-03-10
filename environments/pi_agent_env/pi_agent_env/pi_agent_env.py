"""
Pi Agent Self-Improvement Environment for Prime Intellect Verifiers.

A ToolEnv that replicates Pi Agent's core tools (bash, read, write, python,
find, grep) and scores the model using the ToolUseRubric — a 4-dimension
scoring system with LLM judge support.

Scoring dimensions:
  - task_completion (0.50): LLM judge (gpt-4.1-nano via OpenRouter) evaluates
    whether the agent completed the task correctly
  - tool_outcomes (0.20): Did tool calls succeed? (programmatic)
  - efficiency (0.15): Were tool calls efficient within budget? (programmatic)
  - dummy_call_detection (0.15): Were tool results actually used? (programmatic)

Usage:
  # Quick eval
  uv run vf-eval pi_agent_env -m openai/gpt-4.1-nano

  # Install & push
  prime env install pi_agent_env
  prime env push --path ./environments/pi_agent_env

Secrets required on PI:
  OPENAI_API_KEY  = OpenRouter API key
  OPENAI_BASE_URL = https://openrouter.ai/api/v1
"""

import json
import re
import subprocess
import os
from pathlib import Path
from typing import Any

import verifiers as vf
from verifiers.parsers.parser import Parser
from verifiers.rubrics.judge_rubric import JudgeRubric
from verifiers.rubrics.rubric import Rubric
from verifiers.types import Messages, State


# ═══════════════════════════════════════════════════════════════════════════
# Tools — matching Pi Agent's core tool names and signatures
# ═══════════════════════════════════════════════════════════════════════════

def bash(command: str) -> str:
    """Execute a shell command and return stdout/stderr.

    Args:
        command: The shell command to execute.

    Returns:
        JSON with output, exit_code, and error fields.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/tmp",
        )
        return json.dumps({
            "output": (result.stdout + result.stderr).strip()[:4000],
            "exit_code": result.returncode,
            "error": None,
        })
    except subprocess.TimeoutExpired:
        return json.dumps({"output": "", "exit_code": -1, "error": "Command timed out (30s)"})
    except Exception as e:
        return json.dumps({"output": "", "exit_code": -1, "error": str(e)})


def read(path: str) -> str:
    """Read a file and return its contents.

    Args:
        path: Absolute or relative path to the file.

    Returns:
        The file contents, or an error message.
    """
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return json.dumps({"error": f"File not found: {path}"})
        if p.is_dir():
            entries = sorted(str(e.name) for e in p.iterdir())[:100]
            return json.dumps({"entries": entries, "count": len(entries)})
        content = p.read_text(errors="replace")[:8000]
        return json.dumps({"content": content, "size": p.stat().st_size})
    except Exception as e:
        return json.dumps({"error": str(e)})


def write(path: str, content: str) -> str:
    """Write content to a file, creating parent directories as needed.

    Args:
        path: Absolute or relative path to the file.
        content: The content to write.

    Returns:
        Confirmation message or error.
    """
    try:
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return json.dumps({"status": "ok", "path": str(p), "bytes_written": len(content)})
    except Exception as e:
        return json.dumps({"error": str(e)})


def python(code: str) -> str:
    """Execute Python code and return the output.

    Args:
        code: Python code to execute.

    Returns:
        JSON with stdout output or error.
    """
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/tmp",
        )
        output = (result.stdout + result.stderr).strip()[:4000]
        return json.dumps({
            "output": output,
            "exit_code": result.returncode,
            "error": None if result.returncode == 0 else output,
        })
    except subprocess.TimeoutExpired:
        return json.dumps({"output": "", "exit_code": -1, "error": "Execution timed out (30s)"})
    except Exception as e:
        return json.dumps({"output": "", "exit_code": -1, "error": str(e)})


def find(pattern: str, path: str = "/tmp") -> str:
    """Find files matching a glob pattern.

    Args:
        pattern: Glob pattern (e.g., '*.py', '**/*.json').
        path: Directory to search in.

    Returns:
        JSON list of matching file paths.
    """
    try:
        p = Path(path).expanduser()
        matches = sorted(str(m) for m in p.glob(pattern))[:50]
        return json.dumps({"matches": matches, "count": len(matches)})
    except Exception as e:
        return json.dumps({"error": str(e)})


def grep(pattern: str, path: str = "/tmp", include: str = "*") -> str:
    """Search file contents for a regex pattern.

    Args:
        pattern: Regex pattern to search for.
        path: Directory to search in.
        include: Glob pattern for files to include (e.g., '*.py').

    Returns:
        JSON with matching lines grouped by file.
    """
    try:
        p = Path(path).expanduser()
        results = {}
        file_count = 0
        for f in p.rglob(include):
            if not f.is_file() or file_count > 50:
                break
            file_count += 1
            try:
                text = f.read_text(errors="replace")
                matches = []
                for i, line in enumerate(text.split("\n"), 1):
                    if re.search(pattern, line):
                        matches.append({"line": i, "text": line.strip()[:200]})
                if matches:
                    results[str(f)] = matches[:10]
            except Exception:
                continue
        return json.dumps({"results": results, "files_searched": file_count})
    except Exception as e:
        return json.dumps({"error": str(e)})


PI_AGENT_TOOLS = [bash, read, write, python, find, grep]


# ═══════════════════════════════════════════════════════════════════════════
# ToolUseRubric — 4-dimension scoring with LLM judge
# ═══════════════════════════════════════════════════════════════════════════

TASK_COMPLETION_JUDGE_PROMPT = """You are evaluating whether an AI agent successfully completed a task using tools.

Task given to the agent:
```
{question}
```

Expected behavior or answer:
```
{answer}
```

Full agent response (including tool calls and results):
```
{response}
```

Evaluate whether the agent accomplished the task. Consider:
1. Did the agent produce the correct final answer or outcome?
2. Did it use tools appropriately for the task?
3. Did it handle any errors or edge cases?

Respond with ONLY a score from 0 to 10:
- 0: Complete failure, no progress toward the task
- 1-3: Attempted but mostly wrong or incomplete
- 4-6: Partially correct, some aspects done well
- 7-9: Mostly correct with minor issues
- 10: Perfect task completion

Score:"""

DEFAULT_WEIGHTS = {
    "task_completion": 0.50,
    "tool_outcomes": 0.20,
    "efficiency": 0.15,
    "dummy_call_detection": 0.15,
}


# ─── Message helpers (work with OpenAI typed dicts) ──────────────────────

def _msg_get(msg, key, default=None):
    """Get a field from a message dict."""
    if isinstance(msg, dict):
        return msg.get(key, default)
    return getattr(msg, key, default)


def _is_assistant_msg(msg) -> bool:
    return _msg_get(msg, "role") == "assistant"


def _is_tool_msg(msg) -> bool:
    return _msg_get(msg, "role") == "tool"


def _extract_tool_interactions(completion: Messages) -> list[dict[str, Any]]:
    """Extract tool call + result pairs from a completion."""
    if isinstance(completion, str):
        return []

    interactions = []
    # Build map of tool_call_id -> tool result content
    result_map = {}
    for msg in completion:
        if _is_tool_msg(msg):
            content = _msg_get(msg, "content", "")
            if isinstance(content, list):
                content = " ".join(
                    b.get("text", str(b)) if isinstance(b, dict) else str(b)
                    for b in content
                )
            tid = _msg_get(msg, "tool_call_id", "")
            result_map[tid] = str(content)

    for msg in completion:
        if not _is_assistant_msg(msg):
            continue
        tool_calls = _msg_get(msg, "tool_calls")
        if not tool_calls:
            continue
        for tc in tool_calls:
            tc_id = tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", "")
            func = tc.get("function", {}) if isinstance(tc, dict) else getattr(tc, "function", {})
            if isinstance(func, dict):
                name = func.get("name", "")
                arguments = func.get("arguments", "{}")
            else:
                name = getattr(func, "name", "")
                arguments = getattr(func, "arguments", "{}")

            result_content = result_map.get(tc_id, "")
            success = _is_tool_result_success(result_content)
            try:
                args = json.loads(arguments)
            except (json.JSONDecodeError, TypeError):
                args = {}
            interactions.append({
                "tool_name": name,
                "tool_args": args,
                "tool_call_id": tc_id,
                "result_content": result_content,
                "success": success,
            })
    return interactions


def _is_tool_result_success(content: str) -> bool:
    """Heuristic: check if a tool result indicates success."""
    if not content:
        return False
    lower = content.lower()
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            if parsed.get("error") not in (None, "", False):
                return False
            if parsed.get("exit_code", 0) != 0:
                return False
            return True
    except (json.JSONDecodeError, TypeError):
        pass
    error_indicators = [
        "error:", "traceback", "exception", "file not found",
        "permission denied", "command not found", "no such file",
    ]
    if any(indicator in lower for indicator in error_indicators):
        return False
    return True


def _get_final_text_response(completion: Messages) -> str:
    """Extract the final assistant text (non-tool-call) response."""
    if isinstance(completion, str):
        return completion
    for msg in reversed(completion):
        if not _is_assistant_msg(msg):
            continue
        if _msg_get(msg, "tool_calls"):
            continue
        content = _msg_get(msg, "content")
        if content is None:
            continue
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        parts.append(block.get("text", ""))
                    elif "content" in block:
                        parts.append(str(block["content"]))
                elif isinstance(block, str):
                    parts.append(block)
            text = "\n".join(parts).strip()
        elif isinstance(content, str):
            text = content
        else:
            text = str(content)
        text = re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL).strip()
        if text:
            return text
    return ""


def _format_completion_for_judge(completion: Messages) -> str:
    """Format the full completion (including tool calls/results) for the judge."""
    if isinstance(completion, str):
        return completion
    parts = []
    for msg in completion:
        if _is_assistant_msg(msg):
            tool_calls = _msg_get(msg, "tool_calls")
            if tool_calls:
                for tc in tool_calls:
                    func = tc.get("function", {}) if isinstance(tc, dict) else getattr(tc, "function", {})
                    if isinstance(func, dict):
                        name = func.get("name", "")
                        arguments = func.get("arguments", "{}")
                    else:
                        name = getattr(func, "name", "")
                        arguments = getattr(func, "arguments", "{}")
                    parts.append(f"[Tool Call: {name}({arguments})]")
            content = _msg_get(msg, "content")
            if content:
                if isinstance(content, str):
                    parts.append(f"Assistant: {content}")
                elif isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            text_parts.append(block)
                    if text_parts:
                        parts.append(f"Assistant: {' '.join(text_parts)}")
        elif _is_tool_msg(msg):
            content = _msg_get(msg, "content", "")
            if isinstance(content, list):
                content = " ".join(
                    b.get("text", str(b)) if isinstance(b, dict) else str(b)
                    for b in content
                )
            parts.append(f"[Tool Result: {str(content)[:500]}]")
    return "\n".join(parts)


class ToolConversationParser(Parser):
    """Parser that formats full tool-calling conversations for LLM judge evaluation.

    Instead of extracting only the last assistant message, this formats the
    entire completion including tool calls and results.
    """

    def parse_answer(self, completion: Messages) -> str:
        return _format_completion_for_judge(completion)


class ToolUseRubric(JudgeRubric):
    """Rubric for evaluating tool-calling agent performance.

    Four scoring dimensions:
      1. task_completion (0.50): LLM judge or heuristic
      2. tool_outcomes (0.20): Did tool calls succeed?
      3. efficiency (0.15): Were calls within budget?
      4. dummy_call_detection (0.15): Were results actually used?
    """

    def __init__(
        self,
        use_judge: bool = True,
        weights: dict[str, float] | None = None,
        max_tool_calls: int = 10,
        judge_model: str = "openai/gpt-4.1-nano",
        **kwargs,
    ):
        judge_parser = ToolConversationParser()

        api_key = os.environ.get("OPENAI_API_KEY")
        if use_judge and api_key:
            from openai import AsyncOpenAI
            # Build client pointing at OpenRouter (env vars set via PI secrets)
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
            )
            JudgeRubric.__init__(
                self,
                parser=judge_parser,
                judge_client=client,
                judge_model=judge_model,
                judge_prompt=TASK_COMPLETION_JUDGE_PROMPT,
                **kwargs,
            )
        else:
            if use_judge and not api_key:
                import logging
                logging.getLogger(__name__).warning(
                    "OPENAI_API_KEY not set — falling back to heuristic scoring (no judge)"
                )
                use_judge = False
            Rubric.__init__(self, parser=judge_parser, **kwargs)

        self.use_judge = use_judge
        self.max_tool_calls = max_tool_calls

        # Normalize weights
        w = weights or dict(DEFAULT_WEIGHTS)
        total = sum(w.values())
        self._dimension_weights = {k: v / total for k, v in w.items()}

        # Register reward functions
        self.add_reward_func(
            self.task_completion,
            weight=self._dimension_weights["task_completion"],
        )
        self.add_reward_func(
            self.tool_outcomes,
            weight=self._dimension_weights["tool_outcomes"],
        )
        self.add_reward_func(
            self.efficiency,
            weight=self._dimension_weights["efficiency"],
        )
        self.add_reward_func(
            self.dummy_call_detection,
            weight=self._dimension_weights["dummy_call_detection"],
        )

    async def task_completion(
        self,
        prompt: Messages,
        completion: Messages,
        answer: str,
        state: State,
        **kwargs,
    ) -> float:
        """Score task completion using LLM judge or heuristic fallback."""
        if not self.use_judge:
            response = _get_final_text_response(completion)
            return 1.0 if len(response) > 10 else 0.0

        try:
            judge_response = await self.judge(
                prompt=prompt,
                completion=completion,
                answer=answer,
                state=state,
            )
        except Exception:
            # Fallback to heuristic if judge fails
            response = _get_final_text_response(completion)
            return 1.0 if len(response) > 10 else 0.0

        # Extract numeric score from judge response
        numbers = re.findall(r"\b(\d+(?:\.\d+)?)\b", judge_response)
        if numbers:
            score = float(numbers[-1])
            return min(score / 10.0, 1.0)
        lower = judge_response.lower().strip()
        if lower.startswith("yes"):
            return 1.0
        if lower.startswith("no"):
            return 0.0
        return 0.5

    async def tool_outcomes(self, completion: Messages, **kwargs) -> float:
        """Score based on whether tool calls executed successfully."""
        interactions = _extract_tool_interactions(completion)
        if not interactions:
            return 1.0
        successes = sum(1 for i in interactions if i["success"])
        return successes / len(interactions)

    async def efficiency(self, completion: Messages, info: Any = None, **kwargs) -> float:
        """Score tool call efficiency relative to a budget."""
        interactions = _extract_tool_interactions(completion)
        num_calls = len(interactions)

        if num_calls == 0:
            return 1.0

        budget = self.max_tool_calls
        if info:
            task_info = info
            if isinstance(info, str):
                try:
                    task_info = json.loads(info)
                except (json.JSONDecodeError, TypeError):
                    task_info = {}
            if isinstance(task_info, dict):
                budget = task_info.get("max_tool_calls", self.max_tool_calls)

        if num_calls <= budget:
            return 1.0 - 0.5 * (num_calls / max(budget, 1))
        else:
            overshoot = (num_calls - budget) / max(budget, 1)
            return max(0.0, 0.5 - overshoot * 0.5)

    async def dummy_call_detection(self, completion: Messages, **kwargs) -> float:
        """Detect and penalize dummy/wasteful tool calls."""
        interactions = _extract_tool_interactions(completion)
        if not interactions:
            return 1.0

        penalties = 0.0
        num_checks = 0

        # Check 1: Redundant calls (same tool + same args)
        seen_calls: set[str] = set()
        redundant_count = 0
        for interaction in interactions:
            key = f"{interaction['tool_name']}:{json.dumps(interaction['tool_args'], sort_keys=True)}"
            if key in seen_calls:
                redundant_count += 1
            seen_calls.add(key)

        if len(interactions) > 0:
            num_checks += 1
            redundant_ratio = redundant_count / len(interactions)
            penalties += redundant_ratio

        # Check 2: Repeated failures without adaptation
        failed_calls: set[str] = set()
        repeat_after_fail = 0
        for interaction in interactions:
            key = f"{interaction['tool_name']}:{json.dumps(interaction['tool_args'], sort_keys=True)}"
            if not interaction["success"]:
                if key in failed_calls:
                    repeat_after_fail += 1
                failed_calls.add(key)

        if repeat_after_fail > 0:
            num_checks += 1
            penalties += min(1.0, repeat_after_fail / len(interactions))

        # Check 3: Tool results referenced in final response
        final_response = _get_final_text_response(completion)
        if final_response and interactions:
            num_checks += 1
            any_referenced = False
            for interaction in interactions:
                result = interaction["result_content"]
                if not result or len(result) < 5:
                    continue
                try:
                    parsed_result = json.loads(result)
                    if isinstance(parsed_result, dict):
                        check_values = [
                            str(v) for v in parsed_result.values()
                            if v and isinstance(v, (str, int, float)) and str(v).strip()
                        ]
                    else:
                        check_values = [str(parsed_result)]
                except (json.JSONDecodeError, TypeError):
                    check_values = [result]

                for val in check_values:
                    val_str = str(val).strip()
                    if len(val_str) >= 3 and val_str[:50].lower() in final_response.lower():
                        any_referenced = True
                        break
                if any_referenced:
                    break

            if not any_referenced:
                penalties += 0.5

        if num_checks == 0:
            return 1.0
        return max(0.0, 1.0 - penalties / num_checks)


# ═══════════════════════════════════════════════════════════════════════════
# Dataset loading
# ═══════════════════════════════════════════════════════════════════════════

def _load_pi_tasks():
    """Load Pi Agent tasks from pi_agent_tasks.json."""
    search_paths = [
        Path(__file__).parent / "pi_agent_tasks.json",
    ]
    try:
        import importlib.resources as pkg_resources
        ref = pkg_resources.files("pi_agent_env").joinpath("pi_agent_tasks.json")
        if ref.is_file():
            return json.loads(ref.read_text())
    except (ImportError, TypeError, FileNotFoundError, ModuleNotFoundError):
        pass

    for p in search_paths:
        if p.exists():
            with open(p) as f:
                return json.load(f)

    raise FileNotFoundError(
        "pi_agent_tasks.json not found. Run convert_tasks_pi.py first."
    )


def build_dataset():
    """Build a HuggingFace Dataset from Pi Agent tasks."""
    from datasets import Dataset

    tasks_data = _load_pi_tasks()
    tasks = tasks_data.get("tasks", tasks_data)

    records = []
    for task in tasks:
        verify = task.get("verify", {})
        info = {
            "task_id": task.get("id", ""),
            "category": task.get("category", "unknown"),
            "requires_tool": task.get("requires_tool", False),
            "max_tool_calls": task.get("max_tool_calls", 10),
        }
        records.append({
            "question": task["prompt"],
            "answer": json.dumps(verify),
            "info": json.dumps(info),
        })

    return Dataset.from_list(records)


# ═══════════════════════════════════════════════════════════════════════════
# Environment entry point
# ═══════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = (
    "You are a helpful AI coding assistant with access to tools for executing "
    "shell commands, reading and writing files, running Python code, and searching "
    "the filesystem. Use tools efficiently — only when necessary, and with minimal "
    "calls. When a task doesn't require tools, answer directly without using any."
)


def load_environment(**kwargs):
    """Load the Pi Agent self-improvement environment.

    Uses ToolUseRubric with LLM judge (gpt-4.1-nano via OpenRouter) by default.
    Set use_judge=False in kwargs to disable judge and use heuristic scoring only.
    """
    use_judge = kwargs.pop("use_judge", True)
    judge_model = kwargs.pop("judge_model", "openai/gpt-4.1-nano")

    rubric = ToolUseRubric(
        use_judge=use_judge,
        judge_model=judge_model,
    )
    dataset = build_dataset()

    return vf.ToolEnv(
        dataset=dataset,
        tools=PI_AGENT_TOOLS,
        rubric=rubric,
        system_prompt=SYSTEM_PROMPT,
        **kwargs,
    )
