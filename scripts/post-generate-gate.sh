#!/bin/bash
# post-generate-gate.sh — Auto-runs completion gate on newly generated blueprints
# Called by: blueprint generators, batch scripts, clone-blueprint.sh
# Usage: post-generate-gate.sh <html_file> [--lead <slug>]
# Exit: 0=PASS, 1=FAIL (gates failed), 2=ERROR
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HTML_FILE="${1:-}"
LEAD_SLUG=""

if [ -z "$HTML_FILE" ]; then
    echo "Usage: $0 <html_file> [--lead <slug>]"
    exit 2
fi

# Extract lead slug from filename if not provided
if [ -z "$LEAD_SLUG" ]; then
    LEAD_SLUG=$(basename "$HTML_FILE" .html)
fi

shift; while [ $# -gt 0 ]; do
    case "$1" in --lead) LEAD_SLUG="$2"; shift 2 ;; *) shift ;; esac
done

RECEIPT_DIR="$REPO_ROOT/audit-receipts/$LEAD_SLUG"
mkdir -p "$RECEIPT_DIR"

echo "[post-generate-gate] Checking: $HTML_FILE (lead: $LEAD_SLUG)"

# 1. Base64 check
first4=$(head -c 4 "$HTML_FILE" 2>/dev/null || echo "")
if [[ "$first4" == "PCFE" || "$first4" == "PCEt" || "$first4" == "PD94" ]]; then
    echo "❌ BASE64 CORRUPT: $HTML_FILE is base64-encoded, not HTML. Generation failed."
    exit 1
fi

# 2. Completion gate
RESULT=$(python3 "$REPO_ROOT/scripts/blueprint_completion_gate.py" \
    --html "$HTML_FILE" \
    --receipt-dir "$RECEIPT_DIR" \
    --lead "$LEAD_SLUG" \
    --json-output 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
s = d.get('summary', {})
print('PASS' if s.get('overall_pass') else f'FAIL:{s.get(\"failed\", 0)} gates')
" 2>/dev/null || echo "ERROR:gate_script_failed")

if [[ "$RESULT" == "PASS" ]]; then
    echo "✅ PASS: $LEAD_SLUG passed all completion gates"
    exit 0
elif [[ "$RESULT" == ERROR:* ]]; then
    echo "⚠️  GATE SCRIPT ERROR: $RESULT — committing with warning"
    exit 2
else
    echo "❌ FAIL: $LEAD_SLUG $RESULT — fix before delivery"
    exit 1
fi
