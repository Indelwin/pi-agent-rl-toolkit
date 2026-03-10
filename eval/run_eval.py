#!/usr/bin/env python3
"""
Evaluation pipeline for Pi Agent RL training.

Runs held-out tasks against base model vs trained adapter,
produces category breakdowns and comparison reports.

Usage:
  # Eval base model only
  python3 eval/run_eval.py --base-only

  # Compare base vs adapter
  python3 eval/run_eval.py --adapter <adapter_id>

  # Use specific task file
  python3 eval/run_eval.py --tasks eval/held_out_tasks.json
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent dir so we can import the environment
sys.path.insert(0, str(Path(__file__).parent.parent / "environments" / "pi_agent_env"))

from pi_agent_env.pi_agent_env import (
    ToolUseRubric,
    _extract_tool_interactions,
    _get_final_text_response,
    PI_AGENT_TOOLS,
    SYSTEM_PROMPT,
)


def load_tasks(path: str) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    return data.get("tasks", data)


async def run_single_task(client, model: str, task: dict, tools: list[dict],
                          adapter_id: str | None = None) -> dict:
    """Run a single task and return the full conversation."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task["prompt"]},
    ]

    max_turns = task.get("max_tool_calls", 5) + 2  # allow some turns for tool use
    completion_messages = []

    for turn in range(max_turns):
        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.3,
        }

        # Only provide tools if task may need them
        if task.get("requires_tool", False) or task.get("max_tool_calls", 0) > 0:
            kwargs["tools"] = tools

        if adapter_id:
            kwargs["extra_body"] = {"adapter_id": adapter_id}

        try:
            response = await client.chat.completions.create(**kwargs)
        except Exception as e:
            completion_messages.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
            })
            break

        msg = response.choices[0].message

        # Build assistant message
        assistant_msg = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]

        completion_messages.append(assistant_msg)
        messages.append(assistant_msg)

        # If no tool calls, we're done
        if not msg.tool_calls:
            break

        # Execute tool calls
        for tc in msg.tool_calls:
            func_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}

            # Find and execute the tool
            tool_result = json.dumps({"error": f"Unknown tool: {func_name}"})
            for tool_func in PI_AGENT_TOOLS:
                if tool_func.__name__ == func_name:
                    try:
                        tool_result = tool_func(**args)
                    except Exception as e:
                        tool_result = json.dumps({"error": str(e)})
                    break

            tool_msg = {
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tc.id,
            }
            completion_messages.append(tool_msg)
            messages.append(tool_msg)

        # Check finish reason
        if response.choices[0].finish_reason == "stop":
            break

    return {
        "task_id": task["id"],
        "category": task["category"],
        "completion": completion_messages,
    }


async def score_result(rubric: ToolUseRubric, task: dict, result: dict) -> dict:
    """Score a single task result using the rubric dimensions."""
    completion = result["completion"]
    verify = task.get("verify", {})
    info = {
        "task_id": task["id"],
        "category": task["category"],
        "requires_tool": task.get("requires_tool", False),
        "max_tool_calls": task.get("max_tool_calls", 10),
    }

    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task["prompt"]},
    ]
    answer = json.dumps(verify)
    info_str = json.dumps(info)
    state = {
        "prompt": prompt,
        "completion": completion,
        "answer": answer,
        "info": info_str,
        "task": task["id"],
    }

    tc = await rubric.task_completion(prompt, completion, answer, state)
    to = await rubric.tool_outcomes(completion)
    ef = await rubric.efficiency(completion, info_str)
    dd = await rubric.dummy_call_detection(completion)

    tool_calls = len(_extract_tool_interactions(completion))
    final_response = _get_final_text_response(completion)

    weighted = (
        0.50 * tc + 0.20 * to + 0.15 * ef + 0.15 * dd
    )

    return {
        "task_id": task["id"],
        "category": task["category"],
        "reward": weighted,
        "task_completion": tc,
        "tool_outcomes": to,
        "efficiency": ef,
        "dummy_call_detection": dd,
        "tool_calls": tool_calls,
        "response_length": len(final_response),
        "response_preview": final_response[:200],
    }


def print_results(scores: list[dict], label: str):
    """Print a formatted results table."""
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")

    # Overall
    avg_reward = sum(s["reward"] for s in scores) / len(scores)
    avg_tc = sum(s["task_completion"] for s in scores) / len(scores)
    avg_to = sum(s["tool_outcomes"] for s in scores) / len(scores)
    avg_ef = sum(s["efficiency"] for s in scores) / len(scores)
    avg_dd = sum(s["dummy_call_detection"] for s in scores) / len(scores)
    avg_tools = sum(s["tool_calls"] for s in scores) / len(scores)

    print(f"\n  Overall ({len(scores)} tasks):")
    print(f"    Reward:           {avg_reward:.4f}")
    print(f"    Task Completion:  {avg_tc:.4f}")
    print(f"    Tool Outcomes:    {avg_to:.4f}")
    print(f"    Efficiency:       {avg_ef:.4f}")
    print(f"    Dummy Detection:  {avg_dd:.4f}")
    print(f"    Avg Tool Calls:   {avg_tools:.2f}")

    # By category
    categories = sorted(set(s["category"] for s in scores))
    print(f"\n  {'Category':<20} {'Reward':>7} {'TaskCompl':>9} {'Tools':>5} {'N':>3}")
    print(f"  {'-'*48}")
    for cat in categories:
        cat_scores = [s for s in scores if s["category"] == cat]
        r = sum(s["reward"] for s in cat_scores) / len(cat_scores)
        tc = sum(s["task_completion"] for s in cat_scores) / len(cat_scores)
        t = sum(s["tool_calls"] for s in cat_scores) / len(cat_scores)
        print(f"  {cat:<20} {r:>7.4f} {tc:>9.4f} {t:>5.2f} {len(cat_scores):>3}")

    # Failures (reward < 0.5)
    failures = [s for s in scores if s["reward"] < 0.5]
    if failures:
        print(f"\n  Failures (reward < 0.5): {len(failures)}")
        for f in failures:
            print(f"    {f['task_id']} ({f['category']}): reward={f['reward']:.3f} "
                  f"tc={f['task_completion']:.3f} tools={f['tool_calls']}")


def print_comparison(base_scores: list[dict], adapter_scores: list[dict]):
    """Print side-by-side comparison."""
    print(f"\n{'='*70}")
    print(f"  COMPARISON: Base Model vs Trained Adapter")
    print(f"{'='*70}")

    # Match by task_id
    base_map = {s["task_id"]: s for s in base_scores}
    adapter_map = {s["task_id"]: s for s in adapter_scores}
    common_ids = sorted(set(base_map.keys()) & set(adapter_map.keys()))

    # Overall comparison
    base_avg = sum(base_map[tid]["reward"] for tid in common_ids) / len(common_ids)
    adapter_avg = sum(adapter_map[tid]["reward"] for tid in common_ids) / len(common_ids)
    delta = adapter_avg - base_avg

    print(f"\n  Overall Reward:")
    print(f"    Base:    {base_avg:.4f}")
    print(f"    Adapter: {adapter_avg:.4f}")
    print(f"    Delta:   {delta:+.4f} {'✅' if delta > 0 else '⚠️'}")

    # By category
    categories = sorted(set(base_map[tid]["category"] for tid in common_ids))
    print(f"\n  {'Category':<20} {'Base':>7} {'Adapter':>8} {'Delta':>7} {'Status':>6}")
    print(f"  {'-'*52}")
    for cat in categories:
        cat_ids = [tid for tid in common_ids if base_map[tid]["category"] == cat]
        b = sum(base_map[tid]["reward"] for tid in cat_ids) / len(cat_ids)
        a = sum(adapter_map[tid]["reward"] for tid in cat_ids) / len(cat_ids)
        d = a - b
        status = "✅" if d > 0.01 else ("⚠️" if d < -0.01 else "—")
        print(f"  {cat:<20} {b:>7.4f} {a:>8.4f} {d:>+7.4f} {status:>6}")

    # Biggest improvements and regressions
    deltas = [(tid, adapter_map[tid]["reward"] - base_map[tid]["reward"]) for tid in common_ids]
    deltas.sort(key=lambda x: x[1])

    print(f"\n  Biggest regressions:")
    for tid, d in deltas[:3]:
        if d < -0.01:
            print(f"    {tid} ({base_map[tid]['category']}): {d:+.3f}")
    if all(d >= -0.01 for _, d in deltas[:3]):
        print(f"    None!")

    print(f"\n  Biggest improvements:")
    for tid, d in deltas[-3:]:
        if d > 0.01:
            print(f"    {tid} ({base_map[tid]['category']}): {d:+.3f}")


async def main():
    parser = argparse.ArgumentParser(description="Pi Agent Evaluation Pipeline")
    parser.add_argument("--tasks", default="eval/held_out_tasks.json",
                        help="Path to eval tasks JSON")
    parser.add_argument("--adapter", default=None,
                        help="Adapter ID for trained model")
    parser.add_argument("--base-only", action="store_true",
                        help="Only evaluate base model")
    parser.add_argument("--model", default="qwen/qwen3-30b-a3b-instruct-2507",
                        help="Base model name")
    parser.add_argument("--base-url", default="https://api.pinference.ai/api/v1",
                        help="API base URL")
    parser.add_argument("--api-key-env", default="PRIME_API_KEY",
                        help="Env var name for API key")
    parser.add_argument("--use-judge", action="store_true",
                        help="Use LLM judge for task completion scoring")
    parser.add_argument("--output", default=None,
                        help="Output directory for results JSON")
    args = parser.parse_args()

    from openai import AsyncOpenAI

    # Get API key
    api_key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Try PI config
        try:
            with open(os.path.expanduser("~/.prime/config.json")) as f:
                config = json.load(f)
                api_key = config.get("api_key")
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    if not api_key:
        print("Error: No API key found. Set PRIME_API_KEY or OPENAI_API_KEY env var.")
        sys.exit(1)

    # Load team_id for PI billing
    team_id = None
    try:
        with open(os.path.expanduser("~/.prime/config.json")) as f:
            config = json.load(f)
            team_id = config.get("team_id")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    default_headers = {}
    if team_id:
        default_headers["X-Prime-Team-ID"] = team_id

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=args.base_url,
        default_headers=default_headers,
    )

    # Build tool definitions for the API
    tools_defs = []
    for func in PI_AGENT_TOOLS:
        import inspect
        sig = inspect.signature(func)
        params = {}
        required = []
        for name, param in sig.parameters.items():
            params[name] = {"type": "string", "description": name}
            if param.default is inspect.Parameter.empty:
                required.append(name)
        tools_defs.append({
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__.split("\n")[0] if func.__doc__ else "",
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": required,
                },
            },
        })

    # Load tasks
    tasks = load_tasks(args.tasks)
    print(f"Loaded {len(tasks)} eval tasks from {args.tasks}")

    # Set up rubric
    rubric = ToolUseRubric(use_judge=args.use_judge)

    # Run base model eval
    print(f"\n--- Evaluating base model: {args.model} ---")
    base_results = []
    for i, task in enumerate(tasks):
        result = await run_single_task(client, args.model, task, tools_defs)
        score = await score_result(rubric, task, result)
        base_results.append(score)
        status = "✓" if score["reward"] >= 0.5 else "✗"
        print(f"  [{i+1}/{len(tasks)}] {status} {task['id']} ({task['category']}): "
              f"reward={score['reward']:.3f} tc={score['task_completion']:.3f} "
              f"tools={score['tool_calls']}")

    print_results(base_results, f"Base Model: {args.model}")

    # Run adapter eval if requested
    adapter_results = None
    if args.adapter and not args.base_only:
        print(f"\n--- Evaluating adapter: {args.adapter} ---")
        adapter_results = []
        for i, task in enumerate(tasks):
            result = await run_single_task(client, args.model, task, tools_defs,
                                           adapter_id=args.adapter)
            score = await score_result(rubric, task, result)
            adapter_results.append(score)
            status = "✓" if score["reward"] >= 0.5 else "✗"
            print(f"  [{i+1}/{len(tasks)}] {status} {task['id']} ({task['category']}): "
                  f"reward={score['reward']:.3f} tc={score['task_completion']:.3f} "
                  f"tools={score['tool_calls']}")

        print_results(adapter_results, f"Trained Adapter: {args.adapter}")
        print_comparison(base_results, adapter_results)

    # Save results
    output_dir = args.output or f"eval/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/base_scores.json", "w") as f:
        json.dump({"model": args.model, "scores": base_results}, f, indent=2)

    if adapter_results:
        with open(f"{output_dir}/adapter_scores.json", "w") as f:
            json.dump({"model": args.model, "adapter": args.adapter,
                        "scores": adapter_results}, f, indent=2)

    print(f"\nResults saved to {output_dir}/")


if __name__ == "__main__":
    asyncio.run(main())
