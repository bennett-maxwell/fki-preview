#!/bin/bash
# Blueprint AI Pipeline -- Metrics Dashboard
# Computes: lead count, build times, success rates, file sizes, etc.
# Usage: ./pipeline-metrics.sh [leads-dir] [--json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="${1:-$REPO_DIR/leads}"
JSON_MODE=false
[ "${2:-}" = "--json" ] && JSON_MODE=true

# Help
if [ "${1:-}" = "--help" ]; then
    echo "Usage: $0 [leads-dir] [--json]"
    echo ""
    echo "Computes pipeline metrics: lead counts, file sizes, success rates."
    echo "Use --json for machine-readable output."
    exit 0
fi

TOTAL_LEADS=0
TOTAL_BLUEPRINTS=0
TOTAL_WEBSITES=0
TOTAL_EMAILS=0
TOTAL_BP_BYTES=0
TOTAL_WS_BYTES=0
TOTAL_EM_BYTES=0
SCORED_LEADS=0
HOT_LEADS=0
WARM_LEADS=0
COLD_LEADS=0

for profile in "$LEADS_DIR"/*.json; do
    [ -f "$profile" ] || continue
    TOTAL_LEADS=$((TOTAL_LEADS + 1))

    SLUG=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('slug','unknown'))" "$profile")
    TIER=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('lead_tier','unscored'))" "$profile" 2>/dev/null || echo "unscored")

    if [ "$TIER" != "unscored" ]; then
        SCORED_LEADS=$((SCORED_LEADS + 1))
        [ "$TIER" = "hot" ] && HOT_LEADS=$((HOT_LEADS + 1))
        [ "$TIER" = "warm" ] && WARM_LEADS=$((WARM_LEADS + 1))
        [ "$TIER" = "cold" ] && COLD_LEADS=$((COLD_LEADS + 1))
    fi

    # Blueprint
    BP="$REPO_DIR/blueprints/$SLUG.html"
    if [ -f "$BP" ]; then
        TOTAL_BLUEPRINTS=$((TOTAL_BLUEPRINTS + 1))
        BP_BYTES=$(wc -c < "$BP" | tr -d ' ')
        TOTAL_BP_BYTES=$((TOTAL_BP_BYTES + BP_BYTES))
    fi

    # Website
    WS="$REPO_DIR/${SLUG}-website/index.html"
    if [ -f "$WS" ]; then
        TOTAL_WEBSITES=$((TOTAL_WEBSITES + 1))
        WS_BYTES=$(wc -c < "$WS" | tr -d ' ')
        TOTAL_WS_BYTES=$((TOTAL_WS_BYTES + WS_BYTES))
    fi

    # Email
    EM="$REPO_DIR/delivery-emails/${SLUG}-delivery-email.html"
    if [ -f "$EM" ]; then
        TOTAL_EMAILS=$((TOTAL_EMAILS + 1))
        EM_BYTES=$(wc -c < "$EM" | tr -d ' ')
        TOTAL_EM_BYTES=$((TOTAL_EM_BYTES + EM_BYTES))
    fi
done

# Compute averages
AVG_BP_KB=0
AVG_WS_KB=0
AVG_EM_KB=0
[ "$TOTAL_BLUEPRINTS" -gt 0 ] && AVG_BP_KB=$((TOTAL_BP_BYTES / TOTAL_BLUEPRINTS / 1024))
[ "$TOTAL_WEBSITES" -gt 0 ] && AVG_WS_KB=$((TOTAL_WS_BYTES / TOTAL_WEBSITES / 1024))
[ "$TOTAL_EMAILS" -gt 0 ] && AVG_EM_KB=$((TOTAL_EM_BYTES / TOTAL_EMAILS / 1024))

# Completion rates
BP_RATE=0
WS_RATE=0
EM_RATE=0
[ "$TOTAL_LEADS" -gt 0 ] && BP_RATE=$((TOTAL_BLUEPRINTS * 100 / TOTAL_LEADS))
[ "$TOTAL_LEADS" -gt 0 ] && WS_RATE=$((TOTAL_WEBSITES * 100 / TOTAL_LEADS))
[ "$TOTAL_LEADS" -gt 0 ] && EM_RATE=$((TOTAL_EMAILS * 100 / TOTAL_LEADS))

# Log file metrics
LOG_DIR="$HOME/.openclaw/logs"
LOG_COUNT=0
if [ -d "$LOG_DIR" ]; then
    LOG_COUNT=$(find "$LOG_DIR" -name "blueprint-batch-*" -type f 2>/dev/null | wc -l | tr -d ' ')
fi

PIPELINE_EVENTS=0
if [ -f "$LOG_DIR/pipeline-events.jsonl" ]; then
    PIPELINE_EVENTS=$(wc -l < "$LOG_DIR/pipeline-events.jsonl" | tr -d ' ')
fi

if [ "$JSON_MODE" = true ]; then
    cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "leads": {"total": $TOTAL_LEADS, "hot": $HOT_LEADS, "warm": $WARM_LEADS, "cold": $COLD_LEADS, "scored": $SCORED_LEADS},
  "blueprints": {"total": $TOTAL_BLUEPRINTS, "rate_pct": $BP_RATE, "avg_size_kb": $AVG_BP_KB},
  "websites": {"total": $TOTAL_WEBSITES, "rate_pct": $WS_RATE, "avg_size_kb": $AVG_WS_KB},
  "emails": {"total": $TOTAL_EMAILS, "rate_pct": $EM_RATE, "avg_size_kb": $AVG_EM_KB},
  "pipeline": {"batch_runs": $LOG_COUNT, "event_log_lines": $PIPELINE_EVENTS}
}
EOF
else
    echo "==========================================="
    echo "  Blueprint AI Pipeline Metrics"
    echo "  $(date '+%Y-%m-%d %H:%M %Z')"
    echo "==========================================="
    echo ""
    echo "LEADS"
    echo "  Total: $TOTAL_LEADS"
    echo "  Scored: $SCORED_LEADS (hot=$HOT_LEADS warm=$WARM_LEADS cold=$COLD_LEADS)"
    echo ""
    echo "DELIVERABLES"
    printf "  %-12s %-8s %-8s %-12s\n" "Type" "Count" "Rate" "Avg Size"
    printf "  %-12s %-8s %-8s %-12s\n" "Blueprints" "$TOTAL_BLUEPRINTS" "${BP_RATE}%" "${AVG_BP_KB}KB"
    printf "  %-12s %-8s %-8s %-12s\n" "Websites" "$TOTAL_WEBSITES" "${WS_RATE}%" "${AVG_WS_KB}KB"
    printf "  %-12s %-8s %-8s %-12s\n" "Emails" "$TOTAL_EMAILS" "${EM_RATE}%" "${AVG_EM_KB}KB"
    echo ""
    echo "PIPELINE"
    echo "  Batch runs: $LOG_COUNT"
    echo "  Event log entries: $PIPELINE_EVENTS"
    echo ""
    echo "==========================================="
fi
