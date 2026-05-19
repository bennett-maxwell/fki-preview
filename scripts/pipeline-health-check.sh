#!/bin/bash
# Blueprint AI Pipeline -- Health Check
# Verifies all leads end-to-end: profile -> website -> blueprint -> email
# Usage: ./pipeline-health-check.sh [leads-dir]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="${1:-$REPO_DIR/leads}"

PASS=0
FAIL=0
TOTAL=0
ERRORS=()

check() {
    TOTAL=$((TOTAL + 1))
    if eval "$2" > /dev/null 2>&1; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        ERRORS+=("$1")
    fi
}

echo "=== Pipeline Health Check ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Leads dir: $LEADS_DIR"
echo ""

for profile in "$LEADS_DIR"/*.json; do
    [ -f "$profile" ] || continue
    SLUG=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('slug','unknown'))" "$profile")
    LEAD=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('lead_name','Unknown'))" "$profile")

    echo "--- $LEAD ($SLUG) ---"

    # 1. Profile valid JSON with required fields
    check "$SLUG: profile valid JSON" "python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert all(k in d for k in [\"lead_name\",\"business_name\",\"slug\",\"accent_color\",\"industry\"])' '$profile'"

    # 2. Website directory exists with index.html
    WS_DIR="$REPO_DIR/${SLUG}-website/index.html"
    check "$SLUG: website index.html exists" "[ -f '$WS_DIR' ]"

    # 3. Website file size > 15KB
    if [ -f "$WS_DIR" ]; then
        WS_BYTES=$(wc -c < "$WS_DIR" | tr -d ' ')
        check "$SLUG: website > 15KB ($((WS_BYTES/1024))KB)" "[ $WS_BYTES -gt 15360 ]"
    fi

    # 4. Blueprint HTML exists
    BP_FILE="$REPO_DIR/blueprints/$SLUG.html"
    check "$SLUG: blueprint exists" "[ -f '$BP_FILE' ]"

    # 5. Blueprint file size > 50KB
    if [ -f "$BP_FILE" ]; then
        BP_BYTES=$(wc -c < "$BP_FILE" | tr -d ' ')
        check "$SLUG: blueprint > 50KB ($((BP_BYTES/1024))KB)" "[ $BP_BYTES -gt 51200 ]"
    fi

    # 6. Delivery email exists
    EMAIL_FILE="$REPO_DIR/delivery-emails/${SLUG}-delivery-email.html"
    check "$SLUG: delivery email exists" "[ -f '$EMAIL_FILE' ]"

    # 7. No cross-contamination (Brittney name in non-Brittney blueprints)
    if [ -f "$BP_FILE" ] && [ "$SLUG" != "brittney-warnick" ]; then
        check "$SLUG: no Brittney contamination" "! grep -q 'Brittney Warnick' '$BP_FILE'"
    fi

    # 8. Blueprint has apply CTA
    if [ -f "$BP_FILE" ]; then
        APPLY_CT=$(grep -ci 'apply' "$BP_FILE" 2>/dev/null || echo "0")
        check "$SLUG: blueprint apply CTA (count=$APPLY_CT)" "[ $APPLY_CT -ge 3 ]"
    fi

    echo ""
done

echo "=== HEALTH CHECK RESULTS ==="
echo "Total: $TOTAL | Pass: $PASS | Fail: $FAIL"

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "FAILURES:"
    for err in "${ERRORS[@]}"; do
        echo "  - $err"
    done
fi

echo ""
if [ $FAIL -eq 0 ]; then
    echo "STATUS: HEALTHY"
else
    echo "STATUS: $FAIL ISSUES DETECTED"
fi
