#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# End-to-end RL training pipeline
#
# Pushes environment, launches training, monitors until done,
# deploys adapter, runs eval comparison, and saves report.
#
# Usage:
#   scripts/full_pipeline.sh <config.toml> <openrouter_key>
#
# Example:
#   scripts/full_pipeline.sh configs/rl/pi-agent-30b-judge.toml sk-or-v1-...
# ─────────────────────────────────────────────────────────────

set -euo pipefail

CONFIG="${1:?Usage: full_pipeline.sh <config.toml> <openrouter_key>}"
OR_KEY="${2:?Usage: full_pipeline.sh <config.toml> <openrouter_key>}"

echo "═══════════════════════════════════════════════════"
echo "  PI Agent RL Training Pipeline"
echo "═══════════════════════════════════════════════════"
echo ""

# ─── Step 1: Push environment ───
echo "📦 Step 1/6: Pushing environment..."
prime env push --path ./environments/pi_agent_env 2>&1 | tail -3
echo ""

# ─── Step 2: Launch training ───
echo "🚀 Step 2/6: Launching training run..."
RUN_OUTPUT=$(prime rl run "$CONFIG" \
  -e OPENAI_API_KEY="$OR_KEY" \
  -e OPENAI_BASE_URL=https://openrouter.ai/api/v1 2>&1)
echo "$RUN_OUTPUT"

# Extract run ID (look for the run ID pattern in output)
RUN_ID=$(echo "$RUN_OUTPUT" | grep -oE '[a-z0-9]{20,}' | head -1)
if [[ -z "$RUN_ID" ]]; then
    echo "❌ Could not extract run ID from output"
    echo "   Parse the output above and run manually:"
    echo "   scripts/monitor.sh <run_id> --watch"
    exit 1
fi
echo ""
echo "Run ID: $RUN_ID"
echo ""

# ─── Step 3: Monitor until completion ───
echo "📊 Step 3/6: Monitoring (polling every 90s)..."
echo ""
scripts/monitor.sh "$RUN_ID" --watch 90
echo ""

# ─── Step 4: Deploy adapter ───
echo "🔧 Step 4/6: Deploying adapter..."
scripts/deploy.sh "$RUN_ID"
ADAPTER_ID=$(prime deployments list -o json 2>/dev/null | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for a in data['models']:
    if a.get('rft_run_id') == '$RUN_ID' and a['deployment_status'] == 'DEPLOYED':
        print(a['id'])
        break
")
echo "Adapter ID: $ADAPTER_ID"
echo ""

# ─── Step 5: Run evaluation ───
echo "📋 Step 5/6: Running evaluation..."
RESULTS_DIR="eval/results_${RUN_ID}"
python3 eval/run_eval.py \
    --adapter "$ADAPTER_ID" \
    --tasks eval/held_out_tasks.json \
    --output "$RESULTS_DIR" 2>&1
echo ""

# ─── Step 6: Summary ───
echo "═══════════════════════════════════════════════════"
echo "  Pipeline Complete!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Run ID:     $RUN_ID"
echo "  Adapter ID: $ADAPTER_ID"
echo "  Results:    $RESULTS_DIR/"
echo ""
echo "  To undeploy adapter (save credits):"
echo "    scripts/deploy.sh --undeploy $ADAPTER_ID"
echo ""
echo "  To continue training from this run:"
echo "    Add checkpoint_id to your config, then relaunch"
echo ""
