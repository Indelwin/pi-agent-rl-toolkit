#!/usr/bin/env python3
"""
Convert synthetic_tasks.json from raw tool names to Pi Agent tool names.

Raw → Pi Agent mapping:
  terminal       → bash
  execute_code   → python
  read_file      → read
  write_file     → write
  search_files   → find / grep

Dropped (no Pi Agent equivalent):
  memory, skills_list, skills_view, session_search, cron, todo

Usage:
  python3 convert_tasks_pi.py
  python3 convert_tasks_pi.py --input synthetic_tasks.json --output environments/pi_agent_env/pi_agent_tasks.json
"""

import json
import re
import argparse
from pathlib import Path


# ─── Tool name mappings ──────────────────────────────────────────────────────

# Raw tool name → Pi Agent tool name
TOOL_RENAME = {
    "terminal": "bash",
    "execute_code": "python",
    "read_file": "read",
    "write_file": "write",
    "search_files": "find",
}

# Categories that have no Pi Agent equivalent
DROP_CATEGORIES = {"memory", "skills", "session_search", "cron", "todo"}

# Tool names that have no Pi Agent equivalent
LEGACY_ONLY_TOOLS = {"memory", "skills_list", "skills_view", "session_search",
                     "cron_schedule", "cron_list", "cron_remove", "todo",
                     "todo_write", "todo_read"}

# Prompt text replacements (case-insensitive patterns → replacements)
PROMPT_REPLACEMENTS = [
    # Tool name references in prompts
    (r'\bUse terminal\b', 'Use bash'),
    (r'\buse terminal\b', 'use bash'),
    (r'\bthe terminal\b', 'the bash'),
    (r'\bterminal tool\b', 'bash tool'),
    (r'\bterminal command\b', 'bash command'),
    (r'\bexecute_code\b', 'python'),
    (r'\bUse execute_code\b', 'Use python'),
    (r'\buse execute_code\b', 'use python'),
    (r'\bread_file\b', 'read'),
    (r'\bUse read_file\b', 'Use read'),
    (r'\buse read_file\b', 'use read'),
    (r'\bwrite_file\b', 'write'),
    (r'\bUse write_file\b', 'Use write'),
    (r'\buse write_file\b', 'use write'),
    (r'\bsearch_files\b', 'grep'),
    (r'\bUse search_files\b', 'Use grep'),
    (r'\buse search_files\b', 'use grep'),
]


def convert_prompt(prompt: str) -> str:
    """Apply all tool name replacements to a prompt string."""
    result = prompt
    for pattern, replacement in PROMPT_REPLACEMENTS:
        result = re.sub(pattern, replacement, result)
    return result


def convert_expected_tool(expected: str) -> str:
    """Convert expected_tool field from raw to Pi Agent names."""
    if not expected:
        return expected
    # Handle "tool1 AND tool2" format
    parts = [p.strip() for p in expected.split("AND")]
    converted = []
    for part in parts:
        renamed = TOOL_RENAME.get(part.strip(), part.strip())
        converted.append(renamed)
    return " AND ".join(converted)


def has_legacy_only_references(task: dict) -> bool:
    """Check if a task references legacy-only tools that can't be mapped."""
    prompt_lower = task["prompt"].lower()
    for tool in LEGACY_ONLY_TOOLS:
        if tool in prompt_lower:
            return True
    # Also check expected_tool field
    expected = task.get("expected_tool", "")
    if expected:
        parts = [p.strip().lower() for p in expected.split("AND")]
        for part in parts:
            if part in LEGACY_ONLY_TOOLS:
                return True
    return False


def convert_task(task: dict) -> dict:
    """Convert a single task from raw to Pi Agent format."""
    converted = task.copy()

    # Convert prompt
    converted["prompt"] = convert_prompt(task["prompt"])

    # Convert expected_tool
    if "expected_tool" in converted:
        converted["expected_tool"] = convert_expected_tool(converted["expected_tool"])

    return converted


def main():
    parser = argparse.ArgumentParser(
        description="Convert synthetic tasks from raw to Pi Agent tool names"
    )
    parser.add_argument("--input", type=str, default="synthetic_tasks.json",
                        help="Input tasks file")
    parser.add_argument("--output", type=str,
                        default="environments/pi_agent_env/pi_agent_tasks.json",
                        help="Output converted tasks file")
    parser.add_argument("--keep-all", action="store_true",
                        help="Keep all categories (don't drop legacy-specific)")
    args = parser.parse_args()

    # Load
    input_path = Path(args.input)
    print(f"Loading tasks from {input_path}...")
    with open(input_path) as f:
        data = json.load(f)

    tasks = data.get("tasks", data)
    print(f"  Total tasks: {len(tasks)}")

    # Category breakdown before filtering
    cats_before = {}
    for t in tasks:
        c = t["category"]
        cats_before[c] = cats_before.get(c, 0) + 1
    print("\n  Categories before filtering:")
    for c in sorted(cats_before, key=lambda x: -cats_before[x]):
        marker = " [DROP]" if c in DROP_CATEGORIES else ""
        print(f"    {c}: {cats_before[c]}{marker}")

    # Filter and convert
    kept = []
    dropped_category = 0
    dropped_legacy_ref = 0

    for task in tasks:
        # Drop legacy-specific categories
        if not args.keep_all and task["category"] in DROP_CATEGORIES:
            dropped_category += 1
            continue

        # Drop tasks that reference legacy-only tools even in kept categories
        if has_legacy_only_references(task):
            dropped_legacy_ref += 1
            continue

        # Convert tool names
        converted = convert_task(task)
        kept.append(converted)

    print(f"\n  Dropped {dropped_category} tasks (legacy-specific categories)")
    print(f"  Dropped {dropped_legacy_ref} tasks (legacy-only tool references)")
    print(f"  Kept {len(kept)} tasks")

    # Category breakdown after
    cats_after = {}
    for t in kept:
        c = t["category"]
        cats_after[c] = cats_after.get(c, 0) + 1
    print("\n  Categories after filtering:")
    for c in sorted(cats_after, key=lambda x: -cats_after[x]):
        print(f"    {c}: {cats_after[c]}")

    # Verify some conversions
    print("\n  Sample conversions:")
    for t in kept:
        if t["category"] == "terminal":
            print(f"    terminal → bash: \"{t['prompt'][:80]}...\"")
            break
    for t in kept:
        if t["category"] == "code_execution":
            print(f"    code_exec → python: \"{t['prompt'][:80]}...\"")
            break
    for t in kept:
        if t["category"] == "file_ops":
            print(f"    file_ops → read/write: \"{t['prompt'][:80]}...\"")
            break

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "meta": {
            "version": "3.0.0-pi-agent",
            "description": "Pi Agent eval tasks (converted from synthetic tasks)",
            "source_version": data.get("meta", {}).get("version", "unknown"),
            "total_tasks": len(kept),
            "dropped_tasks": dropped_category + dropped_legacy_ref,
        },
        "tasks": kept,
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n  Written to {output_path}")
    print(f"  Total: {len(kept)} tasks")


if __name__ == "__main__":
    main()
