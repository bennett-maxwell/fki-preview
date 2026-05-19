#!/bin/bash
# Blueprint AI Pipeline — Full Integration Test
# Runs a dry test of the entire pipeline using existing lead profiles
# Verifies every script, template, and output exists and validates

set -euo pipefail

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
    check "$name valid JSON" "python3 -c \"import json; json.load(open('$f'))\""
    check "$name has required fields" "python3 -c \"import json; d=json.load(open('$f')); assert all(k in d for k in ['lead_name','business_name','slug','accent_color','industry'])\""
done

echo ""
echo "--- 4. Template Placeholders ---"
check "Email template has BUSINESS_NAME" "grep -q '{{BUSINESS_NAME}}' $REPO_DIR/templates/delivery-email-template.html"
check "Email template has ACCENT_COLOR" "grep -q '{{ACCENT_COLOR}}' $REPO_DIR/templates/delivery-email-template.html"
check "Email template has no booking URLs" "! grep -qi 'leadconnectorhq\|widget/booking' $REPO_DIR/templates/delivery-email-template.html"
check "Email template has no emojis" "python3 -c \"import re; t=open('$REPO_DIR/templates/delivery-email-template.html').read(); assert len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]',t))==0\""
check "Email template has apply CTA" "grep -qi 'apply' $REPO_DIR/templates/delivery-email-template.html"
check "Website template has BUSINESS_NAME" "grep -q '{{BUSINESS_NAME}}' $REPO_DIR/templates/website-template.html"

echo ""
echo "--- 5. Deployed Deliverables ---"
check "Brittney Blueprint HTTP 200" "[ \$(curl -sI -o /dev/null -w '%{http_code}' https://bennett-maxwell.github.io/fki-preview/blueprints/brittney-warnick.html) = 200 ]"
check "Branson Blueprint HTTP 200" "[ \$(curl -sI -o /dev/null -w '%{http_code}' https://bennett-maxwell.github.io/fki-preview/blueprints/branson-maxwell.html) = 200 ]"
check "Court Blueprint HTTP 200" "[ \$(curl -sI -o /dev/null -w '%{http_code}' https://bennett-maxwell.github.io/fki-preview/blueprints/court-lundberg.html) = 200 ]"
check "Warnick website HTTP 200" "[ \$(curl -sI -o /dev/null -w '%{http_code}' https://bennett-maxwell.github.io/fki-preview/warnick-design/) = 200 ]"
check "Branson website HTTP 200" "[ \$(curl -sI -o /dev/null -w '%{http_code}' https://bennett-maxwell.github.io/fki-preview/branson-maxwell-website/) = 200 ]"
check "Court website HTTP 200" "[ \$(curl -sI -o /dev/null -w '%{http_code}' https://bennett-maxwell.github.io/fki-preview/call-rarebreed/) = 200 ]"

echo ""
echo "--- 6. Podcast Files ---"
check "Brittney podcast on Desktop" "[ -f ~/Desktop/brittney-warnick-blueprint-podcast.mp4 ] && [ \$(stat -f%z ~/Desktop/brittney-warnick-blueprint-podcast.mp4) -gt 1000000 ]"
check "Melissa podcast on Desktop" "[ -f ~/Desktop/melissa-spoiled-rotten-podcast.mp4 ] && [ \$(stat -f%z ~/Desktop/melissa-spoiled-rotten-podcast.mp4) -gt 1000000 ]"
check "Rey podcast on Desktop" "[ -f ~/Desktop/rey-ponce-podcast.mp4 ] && [ \$(stat -f%z ~/Desktop/rey-ponce-podcast.mp4) -gt 1000000 ]"

echo ""
echo "--- 7. Bennett Rule Compliance (all Blueprints) ---"
for html in "$REPO_DIR"/blueprints/brittney-warnick.html "$REPO_DIR"/blueprints/branson-maxwell.html "$REPO_DIR"/blueprints/court-lundberg.html; do
    name=$(basename "$html" .html)
    check "$name no booking" "! grep -q 'leadconnectorhq' '$html'"
    check "$name no calendar" "! grep -q 'calendly' '$html'"
    check "$name has apply CTA" "[ \$(grep -ci 'apply' '$html' 2>/dev/null || echo 0) -ge 3 ]"
done

echo ""
echo "=== RESULTS ==="
echo "Total: $TOTAL | Pass: $PASS | Fail: $FAIL"
if [ $FAIL -eq 0 ]; then
    echo "STATUS: ALL PASS"
else
    echo "STATUS: $FAIL FAILURES — review above"
fi
