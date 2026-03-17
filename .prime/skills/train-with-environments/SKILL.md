---
name: train-with-environments
description: Train models with verifiers environments using hosted RL or prime-rl. Use when asked to configure RL runs, tune key hyperparameters, diagnose instability, set up difficulty filtering and oversampling, or create practical train and eval loops for new environments.
---

# Train With Environments

## Goal
Run stable RL training loops with environment-aware hyperparameter choices and clear diagnostics.

## Preferred Training Paths
1. By default, assume users intend to use Hosted Training unless they explicitly ask for self-managed training.
2. Hosted Training service path from lab setup:
```bash
prime lab setup
```
3. Self-managed `prime-rl` workflow:
```bash
prime lab setup --prime-rl
uv run prime-rl configs/prime-rl/wiki-search.toml
```
4. Treat `prime-rl` as a power-user path and assume users are comfortable working with GPU infrastructure and troubleshooting.
5. Runtime expectation:
- Hosted Training is intended to be launched from a CPU machine.
- Local `prime-rl` training requires local GPU access.

## Endpoint Shortcuts And Model Family Choice
1. Encourage users to maintain endpoint aliases in `configs/endpoints.toml` for eval and train loops.
2. Ask whether they want instruct or reasoning models for pre-training validation.
3. Instruct go-tos for behavior checks: `gpt-4.1` series, `qwen3` instruct series.
4. Reasoning go-tos for harder reasoning-heavy probes: `gpt-5` series, `qwen3` thinking series, `glm` series.

## First-Run Protocol
1. Validate environment behavior before training:
```bash
prime env install my-env
prime eval run my-env -m gpt-4.1-mini -n 20 -r 3 -s
```
2. Confirm reward diversity exists at baseline.
3. Start with conservative run length and inspect samples early.

## Publish Gate Before RL
1. Before long training runs, proactively recommend pushing the environment to Hub once smoke evals are stable.
2. Ask the user explicitly whether visibility should be `PUBLIC` or `PRIVATE`.
3. Push with chosen visibility:
```bash
prime env push my-env --visibility PUBLIC
```
or
```bash
prime env push my-env --visibility PRIVATE
```
4. For hosted RL and shared workflows, prefer Hub IDs after push (for example `owner/my-env` in config `[[env]].id`).

## Hyperparameter Rules Of Thumb
1. Use `rollouts_per_example` and `batch_size` together.
2. Treat `batch_size` as total rollout samples per step, not number of groups.
3. Keep `batch_size` divisible by `rollouts_per_example`.
4. Quick tests or simpler environments:
- `rollouts_per_example = 8`
- `batch_size = 128` (or lower)
5. More complex or longer-horizon environments:
- `rollouts_per_example = 16`
- `batch_size = 512` (common strong starting point)
6. Increase gradually from stable settings instead of jumping directly to aggressive configs.

## Difficulty Filtering And Oversampling
1. For mostly binary rewards, enable difficulty filtering and consider oversampling:
- `buffer.online_difficulty_filtering = true`
- `oversampling_factor > 1` (for example `2.0`)
2. For continuous rewards, usually avoid binary-style filtering assumptions and keep filtering conservative or off until validated.
3. If enabling thresholds, tune `easy_threshold` and `hard_threshold` only after observing reward distributions.

## Stability Constraints From Prime-RL
1. Ensure `max_concurrent >= rollouts_per_example * workers_per_env`.
2. Keep async level explicit (`max_async_level`) and monitor off-policy drift.
3. For OOM risk, reduce rollout pressure and sequence lengths before widening training scope.

## Checkpoint Retention
1. **Always set `keep_cloud = -1`** in `[checkpoints]` to keep all checkpoints in cloud storage.
2. The default `keep_cloud = 5` only retains the last 5 checkpoints — older ones are permanently deleted.
3. If training degrades late (gibberish, repetition, reward collapse), you need early checkpoints to resume from. Losing them means starting over.
4. Storage is cheap; lost checkpoints are not recoverable. Always prefer keeping all:
```toml
[checkpoints]
interval = 50
keep_cloud = -1
```

## Learning Rate For Long Runs
1. The default `learning_rate = 1e-4` is too aggressive for runs beyond ~500 steps. Late-stage training can produce gibberish and repetition.
2. For runs of 500+ steps, start with `learning_rate = 1e-5` or use a lower rate.
3. Watch `filter/gibberish` and `filter/repetition` metrics on the dashboard — any upward trend means the LR is too high.
4. If continuing from a checkpoint after degeneration, drop the LR by at least 10x from the original.
5. Ask PI support about cosine LR scheduling availability — decay is preferable to a constant rate for long runs.

## Eval Best Practices
1. **Always run baseline evals before training** using `prime eval run` to establish ground truth.
2. Set `eval_base_model = true` in the `[eval]` config section for automatic before/after comparison.
3. Increase eval frequency for longer runs — use `interval = 50` rather than `interval = 100` to catch degradation early.
4. Monitor tool-level metrics (bash_calls, write_calls, etc.) alongside reward — reward can rise while behavior degrades.
5. Per-category breakdowns require custom post-processing of saved eval results.

## Failure Diagnosis
1. Flat reward near zero:
- Task too hard, rubric mismatch, or prompt/tool contract mismatch.
2. Unstable reward swings:
- Lower learning rate, increase rollout group size, reduce async aggressiveness.
3. Slow learning despite stability:
- Revisit task difficulty and reward shaping before increasing risk knobs.
4. Gibberish or repetition appearing mid-to-late training:
- Learning rate too high for current stage. Drop LR by 5-10x.
- Resume from the last clean checkpoint before degeneration started.
- This was observed in a 1000-step run at default 1e-4 LR — gibberish appeared ~step 500, spiked ~step 700-850.
5. Reward rising while tool calls collapse:
- Model is gaming the LLM judge. Add programmatic guardrail reward functions (e.g. `tool_use_required`).
- Always monitor tool-level metrics, not just aggregate reward.

## Non-Negotiable Environment Quality During Training
1. Use deterministic robust checks or LLM judges for rewards.
2. Reject best-effort keyword heuristics unless explicitly approved as last resort.
3. Keep environments self-contained after install; no user-managed background services.
4. Surface feature limitations directly instead of proposing hidden workarounds.

## Deliverable
Return:
1. Config deltas applied.
2. Why each delta was chosen.
3. Observed metrics and failure signatures.
4. Next tuning step with stop conditions.
