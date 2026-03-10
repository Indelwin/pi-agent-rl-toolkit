#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Deploy an adapter from a completed RL run
#
# Usage:
#   scripts/deploy.sh <run_id>           # deploy final adapter
#   scripts/deploy.sh --adapter <id>     # deploy specific adapter
#   scripts/deploy.sh --list             # list all adapters
#   scripts/deploy.sh --undeploy <id>    # undeploy an adapter
# ─────────────────────────────────────────────────────────────

set -euo pipefail

if [[ "${1:-}" == "--list" ]]; then
    prime deployments list
    exit 0
fi

if [[ "${1:-}" == "--undeploy" ]]; then
    ADAPTER_ID="${2:?Usage: deploy.sh --undeploy <adapter_id>}"
    echo "Undeploying $ADAPTER_ID..."
    prime deployments delete "$ADAPTER_ID"
    echo "Done."
    exit 0
fi

if [[ "${1:-}" == "--adapter" ]]; then
    ADAPTER_ID="${2:?Usage: deploy.sh --adapter <adapter_id>}"
else
    RUN_ID="${1:?Usage: deploy.sh <run_id> | --adapter <id> | --list | --undeploy <id>}"

    echo "Finding adapter for run $RUN_ID..."
    ADAPTER_ID=$(prime deployments list -o json 2>/dev/null | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for a in data['models']:
    if a.get('rft_run_id') == '$RUN_ID':
        print(a['id'])
        break
" 2>/dev/null)

    if [[ -z "$ADAPTER_ID" ]]; then
        echo "❌ No adapter found for run $RUN_ID"
        echo "   The run may still be processing. Check: prime deployments list"
        exit 1
    fi
    echo "Found adapter: $ADAPTER_ID"
fi

# Check status
STATUS=$(prime deployments list -o json 2>/dev/null | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for a in data['models']:
    if a['id'] == '$ADAPTER_ID':
        print(a['status'], a['deployment_status'])
        break
" 2>/dev/null)

MODEL_STATUS=$(echo "$STATUS" | awk '{print $1}')
DEPLOY_STATUS=$(echo "$STATUS" | awk '{print $2}')

if [[ "$DEPLOY_STATUS" == "DEPLOYED" ]]; then
    echo "✅ Adapter $ADAPTER_ID is already deployed!"
    echo ""
    echo "Use with eval:"
    echo "  python3 eval/run_eval.py --adapter $ADAPTER_ID"
    exit 0
fi

if [[ "$MODEL_STATUS" == "PENDING" ]]; then
    echo "⏳ Adapter is still processing (PENDING). Waiting..."
    while true; do
        sleep 30
        STATUS=$(prime deployments list -o json 2>/dev/null | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for a in data['models']:
    if a['id'] == '$ADAPTER_ID':
        print(a['status'])
        break
" 2>/dev/null)
        echo "  Status: $STATUS"
        if [[ "$STATUS" == "READY" ]]; then
            break
        elif [[ "$STATUS" == "FAILED" ]]; then
            echo "❌ Adapter processing failed!"
            exit 1
        fi
    done
fi

echo "Deploying adapter $ADAPTER_ID..."
echo "y" | prime deployments create "$ADAPTER_ID"

echo ""
echo "Waiting for deployment..."
while true; do
    sleep 15
    DEPLOY_STATUS=$(prime deployments list -o json 2>/dev/null | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for a in data['models']:
    if a['id'] == '$ADAPTER_ID':
        print(a['deployment_status'])
        break
" 2>/dev/null)
    echo "  Deploy status: $DEPLOY_STATUS"
    if [[ "$DEPLOY_STATUS" == "DEPLOYED" ]]; then
        break
    elif [[ "$DEPLOY_STATUS" == "FAILED" ]]; then
        echo "❌ Deployment failed!"
        exit 1
    fi
done

echo ""
echo "✅ Adapter $ADAPTER_ID is deployed!"
echo ""
echo "Next steps:"
echo "  python3 eval/run_eval.py --adapter $ADAPTER_ID"
echo ""
echo "Don't forget to undeploy when done:"
echo "  scripts/deploy.sh --undeploy $ADAPTER_ID"
