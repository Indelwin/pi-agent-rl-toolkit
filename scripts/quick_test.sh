#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Quick test: validate environment + rubric with a 10-step run
#
# Run this before committing to a long production training run.
# Verifies that the judge is active and scoring is meaningful.
#
# Usage:
#   scripts/quick_test.sh <openrouter_key>
# ─────────────────────────────────────────────────────────────

set -euo pipefail

OR_KEY="${1:?Usage: quick_test.sh <openrouter_key>}"

echo "🧪 Quick test: 10-step run on Qwen3-4B"
echo ""

# Push latest environment
echo "📦 Pushing environment..."
prime env push --path ./environments/pi_agent_env 2>&1 | tail -2
echo ""

# Launch test run
echo "🚀 Launching test run..."
RUN_OUTPUT=$(prime rl run configs/rl/test-small.toml \
  -e OPENAI_API_KEY="$OR_KEY" \
  -e OPENAI_BASE_URL=https://openrouter.ai/api/v1 2>&1)
echo "$RUN_OUTPUT"

RUN_ID=$(echo "$RUN_OUTPUT" | grep -oE '[a-z0-9]{20,}' | head -1)
echo ""
echo "Run ID: $RUN_ID"
echo "Waiting for completion (~5-10 min)..."
echo ""

# Wait and monitor
while true; do
    sleep 60
    STATUS=$(prime rl get "$RUN_ID" 2>&1 | grep "Status:" | head -1 | awk '{print $NF}')
    
    if [[ "$STATUS" == "COMPLETED" ]]; then
        echo "✅ Test run completed!"
        break
    elif [[ "$STATUS" == "FAILED" || "$STATUS" == "STOPPED" ]]; then
        echo "❌ Test run $STATUS"
        echo "Check logs: prime rl logs $RUN_ID"
        exit 1
    fi
    
    # Show progress
    prime rl metrics "$RUN_ID" 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
m = data.get('metrics', [])
if m:
    r = m[-1]
    scoring = r.get('scoring_ms/mean', 0)
    judge = '✅' if scoring > 10 else '⚠️'
    print(f'  Step {r[\"step\"]}: reward={r[\"reward/mean\"]:.3f} scoring={scoring:.0f}ms judge={judge}')
else:
    print('  Waiting for first metrics...')
" 2>/dev/null || echo "  ..."
done

echo ""
echo "Checking results..."
prime rl metrics "$RUN_ID" 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
m = data.get('metrics', [])
if not m:
    print('No metrics recorded')
    sys.exit(1)

rewards = [x['reward/mean'] for x in m]
scoring = [x.get('scoring_ms/mean', 0) for x in m]
avg_scoring = sum(scoring) / len(scoring)

print(f'Steps: {len(m)}')
print(f'Reward: {rewards[0]:.3f} → {rewards[-1]:.3f}')
print(f'Avg scoring latency: {avg_scoring:.0f}ms')
print()

if avg_scoring > 10:
    print('✅ Judge is active — scoring is meaningful')
else:
    print('⚠️  Judge appears INACTIVE (scoring <10ms)')
    print('   Check that OPENAI_API_KEY was passed correctly')

if max(rewards) < 0.99:
    print('✅ Reward not saturated — rubric is not being gamed')
else:
    print('⚠️  Reward hit 1.0 — rubric may be gameable')

print()
print('If both checks pass, you are ready for a production run:')
print(f'  prime rl run configs/rl/pi-agent-30b-judge.toml \\\\')
print(f'    -e OPENAI_API_KEY={OR_KEY[:20]}... \\\\')
print(f'    -e OPENAI_BASE_URL=https://openrouter.ai/api/v1')
" 2>/dev/null
