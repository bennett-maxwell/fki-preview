#!/bin/bash
# Blueprint AI Pipeline -- GitHub Pages Deployment Verification
# Usage: ./verify-deployment.sh [leads-dir] [--max-wait 60]
#
# Checks all lead URLs return HTTP 200 from GitHub Pages.
# Useful after a git push to verify deployment.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="${1:-$REPO_DIR/leads}"
MAX_WAIT=60

if [ "${1:-}" = "--help" ]; then
    echo "Usage: $0 [leads-dir] [--max-wait seconds]"
    echo ""
    echo "Verifies all Blueprint and website URLs are live on GitHub Pages."
    echo "Retries with backoff up to --max-wait seconds (default: 60)."
    exit 0
fi

# Parse --max-wait
for i in "$@"; do
    if [ "$i" = "--max-wait" ]; then
        shift
        MAX_WAIT="${1:-60}"
        break
    fi
done

PAGES_BASE="https://bennett-maxwell.github.io/fki-preview"
PASS=0
FAIL=0
TOTAL=0
FAILURES=()

echo "=== GitHub Pages Deployment Verification ==="
echo "Date: $(date)"
echo ""

for profile in "$LEADS_DIR"/*.json; do
    [ -f "$profile" ] || continue
    SLUG=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('slug','unknown'))" "$profile")
    LEAD=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('lead_name','Unknown'))" "$profile")

    # Check Blueprint URL
    BP_URL="$PAGES_BASE/blueprints/$SLUG.html"
    TOTAL=$((TOTAL + 1))
    HTTP_CODE=$(curl -sI --max-time 10 -o /dev/null -w "%{http_code}" "$BP_URL" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        PASS=$((PASS + 1))
        echo "  LIVE: $SLUG blueprint ($HTTP_CODE)"
    else
        # Retry once after 5s
        sleep 5
        HTTP_CODE=$(curl -sI --max-time 10 -o /dev/null -w "%{http_code}" "$BP_URL" 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            PASS=$((PASS + 1))
            echo "  LIVE: $SLUG blueprint ($HTTP_CODE, retry)"
        else
            FAIL=$((FAIL + 1))
            FAILURES+=("$SLUG blueprint: HTTP $HTTP_CODE")
            echo "  DOWN: $SLUG blueprint ($HTTP_CODE)"
        fi
    fi

    # Check Website URL
    WS_URL="$PAGES_BASE/${SLUG}-website/"
    TOTAL=$((TOTAL + 1))
    HTTP_CODE=$(curl -sI --max-time 10 -o /dev/null -w "%{http_code}" "$WS_URL" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        PASS=$((PASS + 1))
        echo "  LIVE: $SLUG website ($HTTP_CODE)"
    else
        sleep 5
        HTTP_CODE=$(curl -sI --max-time 10 -o /dev/null -w "%{http_code}" "$WS_URL" 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            PASS=$((PASS + 1))
            echo "  LIVE: $SLUG website ($HTTP_CODE, retry)"
        else
            FAIL=$((FAIL + 1))
            FAILURES+=("$SLUG website: HTTP $HTTP_CODE")
            echo "  DOWN: $SLUG website ($HTTP_CODE)"
        fi
    fi
done

echo ""
echo "=== RESULTS ==="
echo "Total: $TOTAL | Live: $PASS | Down: $FAIL"

if [ ${#FAILURES[@]} -gt 0 ]; then
    echo ""
    echo "FAILURES:"
    for f in "${FAILURES[@]}"; do
        echo "  - $f"
    done
fi

[ "$FAIL" -eq 0 ] && echo "STATUS: ALL DEPLOYED" || echo "STATUS: $FAIL URLs NOT RESPONDING"
