#!/bin/bash
# Blueprint AI Pipeline — Status Dashboard
# Shows current state of all leads in the pipeline
# Usage: ./pipeline-status.sh [leads-dir]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="${1:-$REPO_DIR/leads}"

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

    SLUG=$(python3 -c "import json; print(json.load(open('$profile')).get('slug','unknown'))")
    LEAD=$(python3 -c "import json; print(json.load(open('$profile')).get('lead_first_name', json.load(open('$profile')).get('lead_name','?')[:12]))")

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
    WS_DIR=$(python3 -c "import json; d=json.load(open('$profile')); url=d.get('website_url',''); slug=url.rstrip('/').split('/')[-1] if url else d.get('slug','')+'-website'; print(slug)")
    if [ -d "$REPO_DIR/$WS_DIR" ]; then
        WS_URL="https://bennett-maxwell.github.io/fki-preview/$WS_DIR/"
        WS_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "$WS_URL" 2>/dev/null || echo "000")
        [ "$WS_CODE" = "200" ] && WS="LIVE" || WS="LOCAL"
    else
        WS="MISSING"
    fi

    # Check Podcast
    POD_URL=$(python3 -c "import json; print(json.load(open('$profile')).get('podcast_url',''))")
    if [ -n "$POD_URL" ] && [ "$POD_URL" != "" ]; then
        POD="UPLOADED"
    elif ls ~/Desktop/*$SLUG*podcast* > /dev/null 2>&1; then
        POD="DESKTOP"
    else
        POD="MISSING"
    fi

    # Check Email
    EMAIL_FILE="$HOME/Desktop/${SLUG}-delivery-email.html"
    [ -f "$EMAIL_FILE" ] && EM="BUILT" || EM="MISSING"

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
