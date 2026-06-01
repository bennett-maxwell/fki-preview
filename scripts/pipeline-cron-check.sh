#!/bin/bash
# Blueprint AI Pipeline — Daily cron health check
# Run via: crontab -e → 0 8 * * * /Users/temp/fki-preview/scripts/pipeline-cron-check.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LOG_DIR"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Run pipeline status in JSON mode
STATUS=$("$SCRIPT_DIR/pipeline-status.sh" "$SCRIPT_DIR/../leads" --json 2>/dev/null | tail -1)
echo "{\"ts\":\"$TS\",\"check\":\"daily-cron\",\"status\":$STATUS}" >> "$LOG_DIR/pipeline-health.jsonl"

# Run integration tests
TEST_RESULT=$(bash "$SCRIPT_DIR/run-full-pipeline-test.sh" 2>&1 | tail -1)
PASS_COUNT=$(echo "$TEST_RESULT" | grep -oE 'Pass: [0-9]+' | grep -oE '[0-9]+')
FAIL_COUNT=$(echo "$TEST_RESULT" | grep -oE 'Fail: [0-9]+' | grep -oE '[0-9]+')
echo "{\"ts\":\"$TS\",\"check\":\"integration-test\",\"pass\":$PASS_COUNT,\"fail\":$FAIL_COUNT}" >> "$LOG_DIR/pipeline-health.jsonl"

# Alert if failures
if [ "$FAIL_COUNT" -gt 0 ]; then
    echo "ALERT: $FAIL_COUNT test failures detected at $TS" >> "$LOG_DIR/pipeline-alerts.log"
fi
