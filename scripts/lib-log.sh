#!/bin/bash
# lib-log.sh -- Shared structured JSON logging for Blueprint AI Pipeline
# Source this file: source "$(dirname "$0")/lib-log.sh"

PIPELINE_LOG_DIR="${PIPELINE_LOG_DIR:-$HOME/.openclaw/logs}"
PIPELINE_LOG_FILE="${PIPELINE_LOG_FILE:-$PIPELINE_LOG_DIR/pipeline-events.jsonl}"
mkdir -p "$PIPELINE_LOG_DIR"

# log_event <level> <script> <event> <message> [extra_json_fields]
# Levels: INFO, WARN, ERROR, SUCCESS
# Example: log_event INFO lead-intake.sh "scrape_start" "Scraping example.com" ',"url":"example.com"'
log_event() {
    local level="${1:-INFO}"
    local script="${2:-unknown}"
    local event="${3:-unknown}"
    local message="${4:-}"
    local extra="${5:-}"
    local ts
    ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    printf '{"ts":"%s","level":"%s","script":"%s","event":"%s","message":"%s"%s}\n' \
        "$ts" "$level" "$script" "$event" "$message" "$extra" >> "$PIPELINE_LOG_FILE"
}

# log_error <script> <event> <message> [extra]
log_error() {
    log_event "ERROR" "$1" "$2" "$3" "${4:-}"
    echo "ERROR: $3" >&2
}

# log_info <script> <event> <message> [extra]
log_info() {
    log_event "INFO" "$1" "$2" "$3" "${4:-}"
}

# log_success <script> <event> <message> [extra]
log_success() {
    log_event "SUCCESS" "$1" "$2" "$3" "${4:-}"
}

# log_warn <script> <event> <message> [extra]
log_warn() {
    log_event "WARN" "$1" "$2" "$3" "${4:-}"
}
