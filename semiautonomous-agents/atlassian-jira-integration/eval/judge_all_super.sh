#!/bin/bash
# Phase 4: judge all 9 pipelines × 2 backends = 18 judge processes in parallel.
# Usage: ./judge_all_super.sh <super_ts>
# Requires the new super-eval runs for: a al ag g cg i eg
# Uses existing runs for: b h dg

set -u
SUPER_TS="${1:-$(cat /tmp/super_eval_ts.txt)}"
EVAL_DIR="/home/admin_jesusarguelles_altostrat_c/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/eval"
cd "$EVAL_DIR"

# Pipeline letter -> run dir
declare -A RUN_DIRS=(
    [a]="runs/super-$SUPER_TS-a"
    [al]="runs/super-$SUPER_TS-al"
    [ag]="runs/super-$SUPER_TS-ag"
    [g]="runs/super-$SUPER_TS-g"
    [cg]="runs/super-$SUPER_TS-cg"
    [i]="runs/super-$SUPER_TS-i"
    [eg]="runs/super-$SUPER_TS-eg"
    [b]="runs/20260521-101429-option-b-rovo-CLEAN"
    [h]="runs/20260519-203012-option-h-full"
    [dg]="runs/20260521-104255-option-d-gemini35-CLEAN"
)

export GCLOUD_ACCOUNT=admin@jesusarguelles.altostrat.com

mkdir -p /tmp/super_judge_logs
PIDS=()
for L in a al ag g cg i eg b h dg; do
    RUN_DIR="${RUN_DIRS[$L]}"
    RESPONSES="$RUN_DIR/responses_$L.jsonl"
    if [ ! -f "$RESPONSES" ]; then
        echo "SKIP $L: no responses at $RESPONSES"
        continue
    fi
    for BACKEND in gemini claude; do
        OUT="$RUN_DIR/judged_${L}_super_${BACKEND}.json"
        LOG="/tmp/super_judge_logs/${L}_${BACKEND}.log"
        nohup env JUDGE_BACKEND=$BACKEND GCLOUD_ACCOUNT=admin@jesusarguelles.altostrat.com \
            ./.venv/bin/python judge_v3.py "$RESPONSES" \
            --pipeline "$L" --questions questions/main.json --out "$OUT" \
            > "$LOG" 2>&1 &
        PID=$!
        PIDS+=($PID)
        echo "Launched $L $BACKEND PID=$PID"
    done
done

echo
echo "Launched ${#PIDS[@]} judge processes"
echo "PIDS: ${PIDS[@]}"
echo "${PIDS[@]}" > /tmp/super_judge_pids.txt
