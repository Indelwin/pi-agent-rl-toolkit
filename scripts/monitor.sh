#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Monitor a Prime Intellect RL training run
#
# Usage:
#   scripts/monitor.sh <run_id>              # one-shot status
#   scripts/monitor.sh <run_id> --watch      # poll every 60s
#   scripts/monitor.sh <run_id> --watch 30   # poll every 30s
# ─────────────────────────────────────────────────────────────

set -euo pipefail

RUN_ID="${1:?Usage: monitor.sh <run_id> [--watch [interval_secs]]}"
WATCH=false
INTERVAL=60

if [[ "${2:-}" == "--watch" ]]; then
    WATCH=true
    INTERVAL="${3:-60}"
fi

show_status() {
    local status
    status=$(prime rl get "$RUN_ID" 2>&1 | grep "Status:" | head -1 | awk '{print $NF}')

    prime rl metrics "$RUN_ID" 2>/dev/null | python3 -c "
import sys, json, datetime

data = json.load(sys.stdin)
metrics = data.get('metrics', [])
if not metrics:
    print('No metrics yet — run may still be starting up.')
    sys.exit(0)

rewards = [m['reward/mean'] for m in metrics]
tc = [m.get('metrics/task_completion', 0) for m in metrics]
tools = [m.get('metrics/total_tool_calls', 0) for m in metrics]
scoring = [m.get('scoring_ms/mean', 0) for m in metrics]

total_steps = 200  # default
n = len(metrics)
pct = n * 100 // total_steps

# Recent averages (last 5)
k = min(5, n)
r_avg = sum(rewards[-k:]) / k
tc_avg = sum(tc[-k:]) / k
t_avg = sum(tools[-k:]) / k
s_avg = sum(scoring[-k:]) / k

# Trend (first 20 vs last 20)
trend_str = ''
if n >= 40:
    early = rewards[:20]
    late = rewards[-20:]
    delta = sum(late)/20 - sum(early)/20
    trend_str = f'  Trend:             first 20={sum(early)/20:.3f} → last 20={sum(late)/20:.3f} (Δ{delta:+.4f})'

# Judge status
judge = '✅ Active' if s_avg > 10 else '⚠️  INACTIVE (heuristic only)'

now = datetime.datetime.now().strftime('%H:%M:%S')
print(f'')
print(f'  [{now}] Run: $RUN_ID  Status: ${status:-unknown}')
print(f'  Steps: {n}/{total_steps} (~{pct}%)')
print(f'  ──────────────────────────────────────')
print(f'  Reward (last {k}):   {r_avg:.4f}')
print(f'  Task Completion:   {tc_avg:.4f}')
print(f'  Tool Calls/sample: {t_avg:.2f}')
print(f'  Scoring latency:   {s_avg:.0f}ms')
print(f'  Judge:             {judge}')
print(f'  Best Reward:       {max(rewards):.4f} (step {metrics[rewards.index(max(rewards))][\"step\"]})')
if trend_str:
    print(trend_str)
print()
" 2>/dev/null || echo "  Could not fetch metrics for $RUN_ID"

    # Show if completed
    if [[ "$status" == "COMPLETED" ]]; then
        echo "  🎉 Run completed!"
        echo ""
        echo "  Next steps:"
        echo "    prime deployments list                    # find adapter"
        echo "    prime deployments create <adapter_id>     # deploy it"
        echo "    python3 eval/run_eval.py --adapter <id>   # evaluate"
        return 1  # signal to stop watching
    elif [[ "$status" == "FAILED" || "$status" == "STOPPED" ]]; then
        echo "  ❌ Run $status"
        echo ""
        echo "  Check logs: prime rl logs $RUN_ID"
        return 1
    fi
    return 0
}

if $WATCH; then
    echo "Monitoring $RUN_ID every ${INTERVAL}s (Ctrl+C to stop)"
    while true; do
        show_status || break
        sleep "$INTERVAL"
    done
else
    show_status || true
fi
