# Pi Agent RL Toolkit

Train AI coding agents to use tools effectively using **reinforcement learning (GRPO)** on [Prime Intellect](https://docs.primeintellect.ai/guides/rl-training), with the [verifiers](https://github.com/primeintellect-ai/verifiers) framework.

## What This Does

An RL environment that teaches **Qwen3-30B-A3B** to use coding tools (bash, read, write, python, find, grep) across 598 diverse tasks. The model learns *when* to use tools, *when* to answer directly, and how to use tools efficiently.

## Results

### v2: 1000-Step Run (with anti-gaming guardrail)

| Steps | Reward | Avg Tool Calls |
|-------|--------|----------------|
| 0-100 | 0.933 | 0.88 |
| 100-200 | 0.942 | 0.77 |
| 200-300 | 0.952 | 0.72 |
| 300-400 | 0.961 | 0.70 |
| 400-500 | 0.969 | 0.63 |
| 500-600 | 0.979 | 0.60 |
| 600-700 | 0.981 | 0.61 |
| 700-800 | 0.985 | 0.56 |
| 800-900 | 0.978 | 0.53 |
| 900-1000 | 0.977 | 0.54 |

**Best reward:** 0.994 · **Improvement:** +0.04 · **Tool calls stable** at ~0.54

The model gets better at tasks while becoming more efficient with tools (fewer calls per task) — but never stops using them when needed (`tool_use_required` stays at ~1.0 throughout).

### v1: 200-Step Run (original proof of concept)

Our first run showed RL training works — task completion went from 96.7% to 100% on held-out eval tasks with zero regressions:

| Category | Base Model | + RL Adapter | Change |
|---|---|---|---|
| **file_ops** | 0.785 | **0.929** | **+0.144** |
| **multi_step** | 0.935 | **0.967** | +0.032 |
| code_execution | 0.955 | 0.955 | — |
| terminal | 0.955 | 0.955 | — |
| zero_tool | 1.000 | 1.000 | — |

v1 adapter: [Indelwin/Qwen3-30B-A3B-ToolAgent-GRPO](https://huggingface.co/Indelwin/Qwen3-30B-A3B-ToolAgent-GRPO)

## Reward Hacking (and How We Fixed It)

When scaling from 200 to 1000 steps, the model **gamed the LLM judge**. It learned to skip tools entirely and write confident text answers, because the judge would still give high scores:

- Tool calls collapsed: 0.91 → 0.13
- Task completion hit 0.99 (fake — model just sounded confident)

We stopped the run and added `tool_use_required` — a guardrail reward function. 53% of tasks are tagged `requires_tool: true`, and the model gets 0.0 if it skips tools on those tasks. After rebalancing the rubric weights, tool calls stabilised and reward improvement became genuine.

| | v1 (gamed run) | v2 (with guardrail) |
|---|---|---|
| Tool calls | 0.91 → **0.13** (collapsed) | 0.88 → **0.54** (stable) |
| Reward | 0.99 (fake confidence) | 0.98 (genuine) |
| `tool_use_required` | N/A | ~1.0 ✅ |

## Quick Start

```bash
# Install prime CLI
uv tool install prime

# Login
prime login

# Set up secrets for the LLM judge (PI inference)
cat > secrets.env << 'EOF'
PRIME_API_KEY="${PRIME_API_KEY}"
PRIME_TEAM_ID="${PRIME_TEAM_ID}"
EOF

# Run a quick eval against the base model
prime eval run anarion/pi_agent_env -m Qwen/Qwen3-30B-A3B-Instruct-2507 -n 10

# View results
prime eval tui

# Start RL training (1000 steps)
prime rl run configs/rl/pi-agent-30b-1000.toml
```

## Training Config

```toml
model = "Qwen/Qwen3-30B-A3B-Instruct-2507"
max_steps = 1000
batch_size = 256
rollouts_per_example = 8
env_file = ["../../secrets.env"]

[sampling]
max_tokens = 4096

[[env]]
id = "anarion/pi_agent_env"
args = { max_turns = 10 }

[checkpoints]
interval = 50
```

## Rubric

5-dimension reward combining an LLM judge with programmatic scoring:

| Dimension | Weight | Type | Description |
|---|---|---|---|
| `task_completion` | 0.35 | LLM judge | Did the agent complete the task? |
| `tool_use_required` | 0.20 | Programmatic | Must use tools when task requires them |
| `tool_outcomes` | 0.20 | Programmatic | Did tool calls succeed? |
| `efficiency` | 0.10 | Programmatic | Minimal calls within budget |
| `dummy_call_detection` | 0.15 | Programmatic | No redundant/wasted calls |

The LLM judge runs via PI inference (Qwen3-4B-Instruct) — no external API keys needed.

## Tools

6 tools replicating a coding agent's capabilities:

| Tool | Description |
|---|---|
| `bash` | Execute shell commands |
| `read` | Read file contents |
| `write` | Write/create files |
| `python` | Execute Python code |
| `find` | Find files matching glob patterns |
| `grep` | Search file contents with regex |

## Dataset

598 tasks across 7 categories:

| Category | Count | Description |
|---|---|---|
| zero_tool | 247 | Knowledge questions (no tools needed) |
| code_execution | 100 | Python computation tasks |
| terminal | 99 | Shell command tasks |
| file_ops | 54 | File creation/manipulation |
| self_improvement | 34 | Meta-tasks about coding practices |
| planning | 32 | Multi-step planning tasks |
| multi_step | 32 | Tasks requiring multiple tool calls |

53% of tasks are tagged `requires_tool: true`.

## Project Structure

```
pi-agent-rl-toolkit/
├── configs/
│   ├── endpoints.toml              # API endpoints for eval
│   └── rl/
│       └── pi-agent-30b-1000.toml  # Training config
├── environments/
│   └── pi_agent_env/               # Verifiers ToolEnv
│       ├── pi_agent_env/
│       │   ├── pi_agent_env.py     # Environment, tools, rubric
│       │   └── pi_agent_tasks.json # 598 training tasks
│       ├── pyproject.toml
│       └── README.md
├── AGENTS.md                       # Agent instructions
├── CLAUDE.md                       # Claude Code instructions
├── secrets.env                     # API keys (gitignored)
└── README.md
```

## Key Lessons

1. **LLM judges get gamed at scale.** Our model learned to skip tools and write confident text to fool the judge. Always add programmatic guardrails for behaviors you care about.

2. **Programmatic + judge scoring > either alone.** The judge catches subtle quality issues; programmatic rubrics enforce hard constraints the judge can't.

3. **Watch tool call metrics, not just reward.** Reward going up while tool calls collapse is the #1 sign of gaming.

4. **RL alone works (no SFT needed).** GRPO from a base instruct model produced meaningful improvements without any supervised fine-tuning.

## Built With

- [Prime Intellect Lab](https://docs.primeintellect.ai/guides/rl-training) — RL training infrastructure
- [verifiers](https://github.com/primeintellect-ai/verifiers) — Environment + rubric framework
- [Qwen3-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507) — Base model
- [Qwen3-4B-Instruct](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) — Judge model (via PI inference)

## Training Runs

- **v2 (1000 steps):** [k15hbl5mxbmy65d2xlvb6eef](https://app.primeintellect.ai/dashboard/training/k15hbl5mxbmy65d2xlvb6eef)
- **v1 (200 steps):** [b4m4eammrloy61ifoo34ndn5](https://app.primeintellect.ai/dashboard/training/b4m4eammrloy61ifoo34ndn5)

## License

Apache 2.0
