#!/bin/bash
# Blueprint AI Pipeline — Status Dashboard
# Shows current state of all leads in the pipeline
# Usage: ./pipeline-status.sh [leads-dir]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "${1:-}" = "--help" ]; then
    echo "Blueprint AI Pipeline -- Status Dashboard"
    echo ""
    echo "Usage: $0 [leads-dir] [--json]"
    echo ""
    echo "Shows status of all leads: Blueprint, Website, Podcast, Email."
    echo "Status: LIVE (deployed), LOCAL (built), MISSING (not built)."
    echo ""
    echo "Options:"
    echo "  leads-dir   Directory containing lead .json profiles (default: leads/)"
    echo "  --json      Append JSON summary line at the end"
    exit 0
fi

LEADS_DIR="${1:-$REPO_DIR/leads}"
JSON_MODE=false
[ "${2:-}" = "--json" ] && JSON_MODE=true

echo "=========================================="
echo "  Blueprint AI Pipeline Status Dashboard"
echo "  $(date '+%Y-%m-%d %H:%M %Z')"
echo "=========================================="
echo ""

printf "%-20s %-12s %-12s %-12s %-12s %-8s\n" "LEAD" "BLUEPRINT" "WEBSITE" "PODCAST" "EMAIL" "STATUS"
printf "%-20s %-12s %-12s %-12s %-12s %-8s\n" "----" "---------" "-------" "-------" "-----" "------"

TOTAL=0
COMPLETE=0

for profile in "$LEADS_DIR"/*.json; do
    [ -f "$profile" ] || continue
    TOTAL=$((TOTAL + 1))

    SLUG=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('slug','unknown'))" "$profile")
    LEAD=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('lead_first_name', d.get('lead_name','?')[:12]))" "$profile")

    # Check Blueprint
    BP_FILE="$REPO_DIR/blueprints/$SLUG.html"
    if [ -f "$BP_FILE" ]; then
        BP_URL="https://bennett-maxwell.github.io/fki-preview/blueprints/$SLUG.html"
        BP_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "$BP_URL" 2>/dev/null || echo "000")
        [ "$BP_CODE" = "200" ] && BP="LIVE" || BP="LOCAL"
    else
        BP="MISSING"
    fi

    # Check Website
    WS_DIR=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); url=d.get('website_url',''); slug=url.rstrip('/').split('/')[-1] if url else d.get('slug','')+'-website'; print(slug)" "$profile")
    if [ -d "$REPO_DIR/$WS_DIR" ]; then
        WS_URL="https://bennett-maxwell.github.io/fki-preview/$WS_DIR/"
        WS_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "$WS_URL" 2>/dev/null || echo "000")
        [ "$WS_CODE" = "200" ] && WS="LIVE" || WS="LOCAL"
    else
        WS="MISSING"
    fi

    # Check Podcast
    POD_URL=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('podcast_url',''))" "$profile")
    if [ -n "$POD_URL" ] && [ "$POD_URL" != "" ]; then
        POD="UPLOADED"
    elif ls ~/Desktop/*$SLUG*podcast* > /dev/null 2>&1; then
        POD="DESKTOP"
    else
        POD="MISSING"
    fi

    # Check Email
    EMAIL_FILE="$REPO_DIR/delivery-emails/${SLUG}-delivery-email.html"
    EMAIL_DESK="$HOME/Desktop/${SLUG}-delivery-email.html"
    if [ -f "$EMAIL_FILE" ] || [ -f "$EMAIL_DESK" ]; then EM="BUILT"; else EM="MISSING"; fi

    # Overall status
    if [ "$BP" = "LIVE" ] && [ "$WS" = "LIVE" ] && [ "$POD" != "MISSING" ] && [ "$EM" != "MISSING" ]; then
        STATUS="READY"
        COMPLETE=$((COMPLETE + 1))
    else
        STATUS="WIP"
    fi

    printf "%-20s %-12s %-12s %-12s %-12s %-8s\n" "$LEAD" "$BP" "$WS" "$POD" "$EM" "$STATUS"
done

echo ""
echo "Total: $TOTAL | Ready: $COMPLETE | WIP: $((TOTAL - COMPLETE))"
echo "Ready rate: $(( COMPLETE * 100 / TOTAL ))%"

# JSON output for monitoring
if [ "$JSON_MODE" = true ]; then
    echo ""
    echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"total\":$TOTAL,\"ready\":$COMPLETE,\"wip\":$((TOTAL - COMPLETE)),\"ready_pct\":$(( COMPLETE * 100 / TOTAL ))}"
fi
