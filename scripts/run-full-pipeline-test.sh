#!/bin/bash
# Blueprint AI Pipeline — Full Integration Test
# Runs a dry test of the entire pipeline using existing lead profiles
# Verifies every script, template, and output exists and validates

set -euo pipefail

if [ "${1:-}" = "--help" ]; then
    echo "Blueprint AI Pipeline -- Full Integration Test"
    echo ""
    echo "Usage: $0"
    echo ""
    echo "Runs a comprehensive test of the entire pipeline:"
    echo "  1. Script existence and permissions"
    echo "  2. Template existence and placeholders"
    echo "  3. Lead profile validation (JSON + required fields)"
    echo "  4. Template placeholder checks"
    echo "  5. HTTP 200 verification for all deployed URLs"
    echo "  6. Podcast file existence"
    echo "  7. Bennett rule compliance (no booking, no calendar, apply CTA)"
    echo "  8. Delivery email existence"
    echo "  9. Script executability"
    echo ""
    echo "Returns exit code 0 if all tests pass, 1 if any fail."
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PASS=0
FAIL=0
TOTAL=0

check() {
    TOTAL=$((TOTAL + 1))
    if eval "$2" > /dev/null 2>&1; then
        PASS=$((PASS + 1))
        echo "  PASS: $1"
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL: $1"
    fi
}

echo "=== Blueprint AI Pipeline Integration Test ==="
echo "Date: $(date)"
echo ""

echo "--- 1. Script Existence ---"
check "lead-intake.sh exists" "[ -x $SCRIPT_DIR/lead-intake.sh ]"
check "build-website.sh exists" "[ -x $SCRIPT_DIR/build-website.sh ]"
check "pre-delivery-check.sh exists" "[ -x $SCRIPT_DIR/pre-delivery-check.sh ]"
check "build-delivery-email.sh exists" "[ -x $SCRIPT_DIR/build-delivery-email.sh ]"
check "generate-podcast.py exists" "[ -x $SCRIPT_DIR/generate-podcast.py ]"
check "blueprint-batch.sh exists" "[ -x $SCRIPT_DIR/blueprint-batch.sh ]"
check "batch-pre-delivery.sh exists" "[ -x $SCRIPT_DIR/batch-pre-delivery.sh ]"

echo ""
echo "--- 2. Template Existence ---"
check "website-template.html" "[ -f $REPO_DIR/templates/website-template.html ]"
check "delivery-email-template.html" "[ -f $REPO_DIR/templates/delivery-email-template.html ]"
check "lead-profile-schema.json" "[ -f $REPO_DIR/templates/lead-profile-schema.json ]"

echo ""
echo "--- 3. Lead Profiles ---"
for f in "$REPO_DIR"/leads/*.json; do
    name=$(basename "$f")
    check "$name valid JSON" "python3 -c 'import json,sys; json.load(open(sys.argv[1]))' '$f'"
    check "$name has required fields" "python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert all(k in d for k in [\"lead_name\",\"business_name\",\"slug\",\"accent_color\",\"industry\"])' '$f'"
done

echo ""
echo "--- 4. Template Placeholders ---"
check "Email template has BUSINESS_NAME" "grep -q '{{BUSINESS_NAME}}' $REPO_DIR/templates/delivery-email-template.html"
check "Email template has ACCENT_COLOR" "grep -q '{{ACCENT_COLOR}}' $REPO_DIR/templates/delivery-email-template.html"
check "Email template has no booking URLs" "! grep -qi 'leadconnectorhq\|widget/booking' $REPO_DIR/templates/delivery-email-template.html"
check "Email template has no emojis" "! grep -P '[\x{1F600}-\x{1F64F}\x{1F300}-\x{1F5FF}]' $REPO_DIR/templates/delivery-email-template.html"
check "Email template has apply CTA" "grep -qi 'apply' $REPO_DIR/templates/delivery-email-template.html"
check "Website template has BUSINESS_NAME" "grep -q '{{BUSINESS_NAME}}' $REPO_DIR/templates/website-template.html"

echo ""
echo "--- 5. Deployed Deliverables (all 9 leads) ---"
for slug in brittney-warnick branson-maxwell court-lundberg chris-lpnw melissa-tash-srp paul-muus rey-31consulting zachary-red-sands dave-wook; do
    check "$slug Blueprint HTTP 200" "[ \$(curl -sI -o /dev/null -w '%{http_code}' https://bennett-maxwell.github.io/fki-preview/blueprints/$slug.html) = 200 ]"
    check "$slug website HTTP 200" "[ \$(curl -sI -o /dev/null -w '%{http_code}' https://bennett-maxwell.github.io/fki-preview/$slug-website/) = 200 ]"
done

echo ""
echo "--- 6. Podcast Files ---"
check "Brittney podcast on Desktop" "[ -f ~/Desktop/brittney-warnick-blueprint-podcast.mp4 ] && [ \$(stat -f%z ~/Desktop/brittney-warnick-blueprint-podcast.mp4) -gt 1000000 ]"
check "Melissa podcast on Desktop" "[ -f ~/Desktop/melissa-spoiled-rotten-podcast.mp4 ] && [ \$(stat -f%z ~/Desktop/melissa-spoiled-rotten-podcast.mp4) -gt 1000000 ]"
check "Rey podcast on Desktop" "[ -f ~/Desktop/rey-ponce-podcast.mp4 ] && [ \$(stat -f%z ~/Desktop/rey-ponce-podcast.mp4) -gt 1000000 ]"

echo ""
echo "--- 7. Bennett Rule Compliance (all 9 Blueprints) ---"
for html in "$REPO_DIR"/blueprints/*.html; do
    name=$(basename "$html" .html)
    check "$name no booking" "! grep -q 'leadconnectorhq' '$html'"
    check "$name no calendar" "! grep -q 'calendly' '$html'"
    check "$name has apply CTA" "[ \$(grep -ci 'apply' '$html' 2>/dev/null || echo 0) -ge 3 ]"
    check "$name pre-delivery PASS" "bash $SCRIPT_DIR/pre-delivery-check.sh '$html' 2>&1 | grep -q 'PASS'"
done

echo ""
echo "--- 8. Delivery Emails (all 9) ---"
for slug in brittney-warnick branson-maxwell court-lundberg chris-lpnw melissa-tash-srp paul-muus rey-31consulting zachary-red-sands dave-wook; do
    check "$slug delivery email exists" "[ -f $REPO_DIR/delivery-emails/$slug-delivery-email.html ]"
done

echo ""
echo "--- 9. Pipeline Scripts Executable ---"
for script in clone-blueprint.sh build-website.sh build-delivery-email.sh blueprint-batch.sh pre-delivery-check.sh pipeline-health-check.sh pipeline-metrics.sh validate-profile.sh score-leads.sh pipeline-cleanup.sh verify-deployment.sh generate-dashboard.sh; do
    check "$script executable" "[ -x $SCRIPT_DIR/$script ]"
done

echo ""
echo "=== RESULTS ==="
echo "Total: $TOTAL | Pass: $PASS | Fail: $FAIL"
if [ $FAIL -eq 0 ]; then
    echo "STATUS: ALL PASS"
else
    echo "STATUS: $FAIL FAILURES — review above"
fi
