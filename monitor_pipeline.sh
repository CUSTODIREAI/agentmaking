#!/bin/bash
# Autonomous Pipeline Monitor - runs in background
# Usage: nohup /tmp/monitor_pipeline.sh > /tmp/monitor.log 2>&1 &

LOGFILE="/tmp/monitor_pipeline.log"
INTERVAL=120  # Check every 2 minutes
DURATION=7200 # Run for 2 hours (7200 seconds)
START_TIME=$(date +%s)

OUT_DIR="/home/bender/Desktop/PRODUCTION/TEST/OUT/performers_part_1"
ERROR_DIR="$OUT_DIR/ERRORS"

echo "=== Pipeline Monitor Started: $(date) ===" >> "$LOGFILE"
echo "Monitoring for $((DURATION/60)) minutes..." >> "$LOGFILE"

while true; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))

    if [ $ELAPSED -ge $DURATION ]; then
        echo "=== Monitor completed after $((DURATION/60)) minutes: $(date) ===" >> "$LOGFILE"
        break
    fi

    # Count metrics
    CONTAINERS=$(sudo docker ps -q 2>/dev/null | wc -l)
    STARTED=$(ls -d "$OUT_DIR"/performers1_*/ 2>/dev/null | wc -l)
    ERRORS=$(ls "$ERROR_DIR"/*.log 2>/dev/null | wc -l)
    SUCCESS=$((STARTED - ERRORS))

    # GPU stats
    GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1)
    GPU_MEM=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null | head -1)

    # Latest activity from pipeline output
    LATEST=$(tail -3 /tmp/claude/-home-bender/tasks/bf4da99.output 2>/dev/null | head -1)

    # Log status
    echo "[$(date '+%H:%M:%S')] Containers: $CONTAINERS | Started: $STARTED | Success: $SUCCESS | Errors: $ERRORS | GPU: ${GPU_UTIL}% ($GPU_MEM)" >> "$LOGFILE"

    # Alert on low containers
    if [ "$CONTAINERS" -lt 15 ]; then
        echo "[ALERT] Only $CONTAINERS containers running!" >> "$LOGFILE"
    fi

    # Check for OOM
    if dmesg 2>/dev/null | tail -20 | grep -q "Out of memory"; then
        echo "[ALERT] OOM detected in dmesg!" >> "$LOGFILE"
    fi

    sleep $INTERVAL
done

echo "Final counts: Started=$STARTED, Success=$SUCCESS, Errors=$ERRORS" >> "$LOGFILE"
