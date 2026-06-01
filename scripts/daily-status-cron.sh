#!/bin/bash
# Blueprint AI Pipeline -- Daily Status Cron
# Designed to run via launchd or cron. Logs status to file.
# Usage: ./daily-status-cron.sh
#
# Install as launchd:
#   Label: com.fki.blueprint-daily-status
#   Program: /Users/temp/fki-preview/scripts/daily-status-cron.sh
#   StartCalendarInterval: Hour=8, Minute=0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d)
STATUS_LOG="$LOG_DIR/pipeline-daily-status-${TIMESTAMP}.log"
METRICS_LOG="$LOG_DIR/pipeline-daily-metrics-${TIMESTAMP}.json"

echo "=== Daily Pipeline Status — $(date) ===" > "$STATUS_LOG"

# Run pipeline status
if [ -x "$SCRIPT_DIR/pipeline-status.sh" ]; then
    "$SCRIPT_DIR/pipeline-status.sh" "$REPO_DIR/leads" >> "$STATUS_LOG" 2>&1
fi

echo "" >> "$STATUS_LOG"

# Run metrics
if [ -x "$SCRIPT_DIR/pipeline-metrics.sh" ]; then
    "$SCRIPT_DIR/pipeline-metrics.sh" "$REPO_DIR/leads" >> "$STATUS_LOG" 2>&1
    "$SCRIPT_DIR/pipeline-metrics.sh" "$REPO_DIR/leads" --json > "$METRICS_LOG" 2>&1
fi

echo "" >> "$STATUS_LOG"

# Run health check
if [ -x "$SCRIPT_DIR/pipeline-health-check.sh" ]; then
    "$SCRIPT_DIR/pipeline-health-check.sh" "$REPO_DIR/leads" >> "$STATUS_LOG" 2>&1
fi

echo "" >> "$STATUS_LOG"
echo "Daily status complete. Log: $STATUS_LOG" >> "$STATUS_LOG"

# Print summary to stdout (for cron email or logging)
tail -5 "$STATUS_LOG"
