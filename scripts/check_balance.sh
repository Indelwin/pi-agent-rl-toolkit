#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Check PI account status, credits, and active deployments
#
# Usage:
#   scripts/check_balance.sh
# ─────────────────────────────────────────────────────────────

set -euo pipefail

echo "═══════════════════════════════════════"
echo "  Prime Intellect Account Status"
echo "═══════════════════════════════════════"
echo ""

# Account info
echo "👤 Account:"
prime whoami 2>&1 | head -10 || true
echo ""

# Active deployments (these cost credits while running)
echo "🔧 Active Deployments:"
DEPLOYED=$(prime deployments list -o json 2>/dev/null | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
deployed = [a for a in data['models'] if a['deployment_status'] == 'DEPLOYED']
if not deployed:
    print('  None (good — no ongoing costs)')
else:
    for a in deployed:
        print(f'  ⚠️  {a[\"id\"]} ({a.get(\"base_model\",\"?\")}) — DEPLOYED')
    print(f'  {len(deployed)} adapter(s) deployed — costing credits!')
    print(f'  Undeploy with: scripts/deploy.sh --undeploy <id>')
" 2>/dev/null)
echo "$DEPLOYED"
echo ""

# Active training runs
echo "🏃 Active Training Runs:"
prime rl list 2>&1 | grep -E "RUNNING|PENDING" || echo "  None"
echo ""

# Quick inference test
echo "🔌 Inference Test:"
API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.prime/config.json'))['api_key'])" 2>/dev/null)
TEAM_ID=$(python3 -c "import json; print(json.load(open('$HOME/.prime/config.json'))['team_id'])" 2>/dev/null)

if [[ -n "$API_KEY" && -n "$TEAM_ID" ]]; then
    RESULT=$(curl -s https://api.pinference.ai/api/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $API_KEY" \
      -H "X-Prime-Team-ID: $TEAM_ID" \
      -d '{
        "model": "qwen/qwen3-8b",
        "messages": [{"role": "user", "content": "Say ok"}],
        "max_tokens": 3
      }' 2>&1)
    
    if echo "$RESULT" | grep -q '"choices"'; then
        echo "  ✅ Inference working"
    elif echo "$RESULT" | grep -q 'Insufficient balance'; then
        echo "  ❌ Insufficient balance — add credits at app.primeintellect.ai"
    else
        echo "  ⚠️  Unexpected response: $(echo "$RESULT" | head -1)"
    fi
else
    echo "  ⚠️  No config found at ~/.prime/config.json"
fi
echo ""
