# Pi Agent Environment

RL environment for training agentic tool use with [Prime Intellect](https://primeintellect.ai) and [verifiers](https://github.com/primeintellect-ai/verifiers).

## Tools

6 tools replicating a coding agent's core capabilities:

- **bash** — Execute shell commands
- **read** — Read file contents
- **write** — Write/create files
- **python** — Execute Python code
- **find** — Find files matching glob patterns
- **grep** — Search file contents with regex

## Rubric

5-dimension reward combining LLM judge + programmatic scoring:

| Dimension | Weight | Type | Description |
|---|---|---|---|
| `task_completion` | 0.35 | LLM judge | Did the agent complete the task correctly? |
| `tool_use_required` | 0.20 | Programmatic | Penalizes skipping tools when the task needs them |
| `tool_outcomes` | 0.20 | Programmatic | Did tool calls execute successfully? |
| `efficiency` | 0.10 | Programmatic | Minimal calls within budget |
| `dummy_call_detection` | 0.15 | Programmatic | No redundant/wasted calls |

The `tool_use_required` dimension was added to prevent reward hacking — without it, the model learns to skip tools entirely and write confident text answers that fool the judge.

## Dataset

598 tasks across 7 categories:

| Category | Count | Description |
|---|---|---|
| zero_tool | 247 | Knowledge questions answerable without tools |
| code_execution | 100 | Tasks requiring Python/bash execution |
| terminal | 99 | Shell command tasks |
| file_ops | 54 | File creation/manipulation |
| self_improvement | 34 | Meta-tasks about coding practices |
| planning | 32 | Multi-step planning tasks |
| multi_step | 32 | Tasks requiring multiple tool calls |

53% of tasks are tagged `requires_tool: true`.

## Usage

```bash
# Evaluate with base model
prime eval run anarion/pi_agent_env -m Qwen/Qwen3-30B-A3B-Instruct-2507 -n 10

# View results
prime eval tui
```
