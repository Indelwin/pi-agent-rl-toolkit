# Pi Agent RL Toolkit

Train AI coding agents to use tools better using **reinforcement learning (GRPO)** on [Prime Intellect](https://www.primeintellect.ai/)'s hosted training infrastructure.

Works with [Pi Agent](https://github.com/mariozechner/pi-coding-agent) — a coding agent framework by Mario Zechner.

## What This Does

This toolkit lets you:

1. **Generate training tasks** — 598 synthetic tasks across 7 categories (bash, python, file ops, planning, etc.)
2. **Train via RL** — GRPO training on Prime Intellect's hosted GPUs
3. **Score with an LLM judge** — 4-dimension rubric that prevents reward hacking
4. **Evaluate** — Compare base model vs trained adapter on held-out tasks
5. **Deploy** — One command to deploy your adapter for inference

### Results

Our first training run improved tool-use capabilities without degrading knowledge:

| Category | Base Model | + RL Adapter | Change |
|---|---|---|---|
| **file_ops** | 0.785 | **0.929** | **+0.144** |
| **multi_step** | 0.935 | **0.967** | +0.032 |
| code_execution | 0.955 | 0.955 | — |
| terminal | 0.955 | 0.955 | — |
| zero_tool | 1.000 | 1.000 | — |
| **Overall** | 0.942 | **0.965** | **+0.023** |

Task completion went from 96.7% → **100%** on held-out eval tasks. Zero regressions.

Trained adapter: [Indelwin/Qwen3-30B-A3B-ToolAgent-GRPO](https://huggingface.co/Indelwin/Qwen3-30B-A3B-ToolAgent-GRPO)

## Quick Start

### Prerequisites

- [Prime Intellect account](https://app.primeintellect.ai/)
- [OpenRouter API key](https://openrouter.ai/) (about $5-10 for a full training run, for LLM judge)
- Python 3.10+
- `prime` CLI: `pip install prime-cli`

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/pi-agent-rl-toolkit.git
cd pi-agent-rl-toolkit

# Login to Prime Intellect
prime login

# Push the training environment to PI Hub
prime env push --path ./environments/pi_agent_env
```

### Train

```bash
# Quick test (10 steps, about 5 min, validates everything works)
scripts/quick_test.sh <your-openrouter-key>

# Production training (200 steps, approx 2 hours)
prime rl run configs/rl/pi-agent-30b-judge.toml \
  -e OPENAI_API_KEY=<your-openrouter-key> \
  -e OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

### Monitor

```bash
# One-shot status
scripts/monitor.sh <run_id>

# Live polling every 60s
scripts/monitor.sh <run_id> --watch
```

### Deploy & Evaluate

```bash
# Deploy the trained adapter
scripts/deploy.sh <run_id>

# Run eval: base model vs adapter
python3 eval/run_eval.py --adapter <adapter_id>

# Undeploy when done (saves credits)
scripts/deploy.sh --undeploy <adapter_id>
```

### Full Pipeline (one command)

```bash
scripts/full_pipeline.sh configs/rl/pi-agent-30b-judge.toml <your-openrouter-key>
```

This runs the entire pipeline: push environment → train → monitor → deploy → evaluate.

## How It Works

### Training Environment

The environment (`environments/pi_agent_env/`) provides:

- **6 tools**: `bash`, `python`, `read`, `write`, `find`, `grep`
- **598 training tasks** across 7 categories
- **ToolUseRubric** — a 4-dimension scoring system

### ToolUseRubric

The reward signal uses four weighted dimensions:

| Dimension | Weight | Type | What it measures |
|---|---|---|---|
| **Task Completion** | 0.50 | LLM Judge | Did the agent actually solve the task? |
| **Tool Outcomes** | 0.20 | Heuristic | Did tool calls succeed (no errors)? |
| **Efficiency** | 0.15 | Heuristic | Were tool calls within budget? |
| **Dummy Call Detection** | 0.15 | Heuristic | No redundant calls, results used? |

The LLM judge (`gpt-4.1-nano` via OpenRouter, about $0.03/step) is **critical**. Without it, the model games the heuristic metrics within about 35 steps by simply never using tools and writing plausible-sounding responses.

### Task Categories

| Category | Count | Tools | Description |
|---|---|---|---|
| `zero_tool` | 247 | None | Factual, arithmetic, reasoning — must NOT use tools |
| `code_execution` | 100 | `python` | Python computation tasks |
| `terminal` | 99 | `bash` | Shell command execution |
| `file_ops` | 54 | `read`, `write`, `bash` | File create/read/write/search |
| `self_improvement` | 34 | None | Meta-reasoning about AI capabilities |
| `planning` | 32 | Various | Plan-then-execute workflows |
| `multi_step` | 32 | Various | Efficient multi-tool workflows |

## Project Structure

```
pi-agent-rl-toolkit/
├── configs/rl/
│   ├── pi-agent-30b-judge.toml     # Production config (30B MoE + judge)
│   └── test-small.toml             # Test config (4B, 10 steps)
├── environments/pi_agent_env/
│   ├── pi_agent_env/
│   │   ├── pi_agent_env.py         # Tools + ToolUseRubric + dataset loader
│   │   └── pi_agent_tasks.json     # 598 training tasks
│   └── pyproject.toml
├── eval/
│   ├── held_out_tasks.json          # 30 held-out eval tasks
│   └── run_eval.py                  # Evaluation pipeline
├── scripts/
│   ├── full_pipeline.sh             # End-to-end automation
│   ├── monitor.sh                   # Training run monitoring
│   ├── deploy.sh                    # Adapter deployment
│   ├── quick_test.sh                # Validation run
│   └── check_balance.sh             # Account status check
├── generate_tasks.py                # Task generation (batch 1)
├── generate_tasks_batch2.py         # Task generation (batch 2)
├── generate_tasks_batch3.py         # Task generation (batch 3)
├── convert_tasks_pi.py              # Convert raw tasks → Pi Agent format
└── synthetic_tasks.json             # 738 generated tasks (pre-conversion)
```

## Configuration

### Available Models

```bash
prime rl models    # list all models available for RL training
```

Tested models:
- `Qwen/Qwen3-4B-Thinking-2507` — fast testing (about 5 min for 10 steps)
- `Qwen/Qwen3-30B-A3B-Instruct-2507` — best balance (MoE, 3B active)
- `Qwen/Qwen3-30B-A3B-Thinking-2507` — MoE with reasoning

### Config Options

```toml
model = "Qwen/Qwen3-30B-A3B-Instruct-2507"
max_steps = 200           # more steps = more training
batch_size = 256          # samples per step
rollouts_per_example = 8  # rollouts per task

[sampling]
max_tokens = 4096         # max response length

[[env]]
id = "YOUR_USERNAME/pi_agent_env"   # your pushed environment
args = { max_turns = 10 }           # max tool-calling turns

[checkpoints]
interval = 25             # save checkpoint every N steps

# Continue from previous training:
# checkpoint_id = "wf3qkqg5pclqqy7hitf4z0ho"
```

## Key Lessons

### 1. Always use the LLM judge
Without it, reward hits 1.0 by step 35. The model learns to never use tools and writes long plausible responses. With the judge (about $5-10 total), training produces genuine improvements.

### 2. Team header required for inference
When calling PI inference API from scripts, include `X-Prime-Team-ID` header or you'll get `Insufficient balance`.

### 3. RL alone works (no SFT needed)
PI hosted training only supports RL/GRPO. No SFT or adapter upload path. But GRPO alone produced meaningful improvements from the base model.

### 4. Check `scoring_ms` to verify judge is active
If `scoring_ms/mean` is <10ms in metrics, the judge isn't running. Should be 100-300ms when active.

## Adding Custom Tasks

1. Create `generate_tasks_batch4.py` following the existing pattern
2. Run it to append to `synthetic_tasks.json`
3. Convert: `python3 convert_tasks_pi.py`
4. Bump version in `environments/pi_agent_env/pyproject.toml`
5. Push: `prime env push --path ./environments/pi_agent_env`
6. Train with the updated environment

## Cost

| Component | Cost |
|---|---|
| RL training (200 steps) | Hosted on Prime Intellect |
| LLM judge (gpt-4.1-nano, 200 steps) | about $5-10 via OpenRouter |
| Eval (30 tasks, heuristic) | about $0.05 PI inference |

## License

Apache 2.0

## Acknowledgements

- [Prime Intellect](https://www.primeintellect.ai/) — hosted RL training infrastructure
- [Pi Agent](https://github.com/mariozechner/pi-coding-agent) by Mario Zechner — agent framework
- [Qwen](https://huggingface.co/Qwen) — base model
- [OpenRouter](https://openrouter.ai/) — LLM judge API access
- [prime-verifiers](https://github.com/PrimeIntellect-ai/prime-verifiers) — RL environment framework
