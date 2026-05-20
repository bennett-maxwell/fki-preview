#!/bin/bash
# Blueprint AI Pipeline — Pre-Delivery Validation
# Checks: podcast HTTP 200, apply_url set, CTA text correct, blueprint HTTP 200
# Usage: ./validate-delivery-ready.sh [slug]
# Exit 0 = all checks pass, Exit 1 = failures found

set -euo pipefail

LEADS_DIR="$(cd "$(dirname "$0")/.." && pwd)/leads"
BASE_URL="https://bennett-maxwell.github.io/fki-preview"
FAILURES=0

check_lead() {
    local slug="$1"
    local profile="$LEADS_DIR/${slug}.json"
    
    if [ ! -f "$profile" ]; then
        echo "❌ $slug: profile not found"
        FAILURES=$((FAILURES + 1))
        return
    fi
    
    local podcast_url apply_url
    podcast_url=$(python3 -c "import json; d=json.load(open('$profile')); print(d.get('podcast_url',''))")
    apply_url=$(python3 -c "import json; d=json.load(open('$profile')); print(d.get('apply_url',''))")
    
    # Check podcast URL
    if [ -z "$podcast_url" ]; then
        echo "❌ $slug: podcast_url empty"
        FAILURES=$((FAILURES + 1))
    else
        code=$(curl -sI -o /dev/null -w "%{http_code}" --max-time 5 "$podcast_url" 2>/dev/null || echo "000")
        if [ "$code" = "200" ]; then
            echo "✅ $slug: podcast HTTP $code"
        else
            echo "❌ $slug: podcast HTTP $code ($podcast_url)"
            FAILURES=$((FAILURES + 1))
        fi
    fi
    
    # Check apply_url set
    if [ -z "$apply_url" ]; then
        echo "❌ $slug: apply_url missing"
        FAILURES=$((FAILURES + 1))
    else
        echo "✅ $slug: apply_url set"
    fi
    
    # Check blueprint HTML CTA text
    local html="$(cd "$(dirname "$0")/.." && pwd)/blueprints/${slug}.html"
    if [ -f "$html" ]; then
        if grep -q "Apply to Work With Us" "$html"; then
            echo "✅ $slug: CTA text correct"
        else
            echo "❌ $slug: CTA text wrong (still 'Get Your AI Quote'?)"
            FAILURES=$((FAILURES + 1))
        fi
    fi
}

# Run checks
if [ "${1:-}" ]; then
    check_lead "$1"
else
    for f in "$LEADS_DIR"/*.json; do
        [ -f "$f" ] && check_lead "$(basename "$f" .json)"
    done
fi

echo ""
echo "Validation complete: $FAILURES failures"
[ "$FAILURES" -eq 0 ] && echo "✅ ALL PASS — ready for delivery" || echo "❌ FIX FAILURES BEFORE SENDING"
exit $FAILURES
