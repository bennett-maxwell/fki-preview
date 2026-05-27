#!/bin/bash
# blueprint-propagate.sh — Auto-propagation script
# Purpose: When blueprint-schema.json changes, retroactively fix all blueprint HTML files
# Created: 2026-05-27 | Phase 2 permanent fix

REPO_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /Users/openclaw/fki-preview)"
SCHEMA="$REPO_DIR/blueprint-schema.json"
BLUEPRINTS_DIR="$REPO_DIR/blueprints"
ORCH="$HOME/.claude/skills/blueprint-ai-skill/orchestrator/blueprint_orchestrator.py"

echo "=== Blueprint Propagate — $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "Schema: $SCHEMA"
echo "Blueprints: $BLUEPRINTS_DIR"

# Load schema values
CANONICAL_CTA=$(python3 -c "import json; d=json.load(open('$SCHEMA')); print(d['cta']['approved_phrases'][0])")
BANNED_PHRASES=$(python3 -c "import json; d=json.load(open('$SCHEMA')); print('|'.join(d['cta']['banned_phrases']))")
QUALIFY_URL=$(python3 -c "import json; d=json.load(open('$SCHEMA')); print(d['links']['qualify_url'])")

echo "Canonical CTA: $CANONICAL_CTA"
echo "Banned patterns: $BANNED_PHRASES"

FIXED=0
FAILED=0
SKIPPED=0

for f in "$BLUEPRINTS_DIR"/*.html; do
    name=$(basename "$f")
    
    # Skip template files
    [[ "$name" == "TEMPLATE.html" ]] && { SKIPPED=$((SKIPPED+1)); continue; }
    
    echo ""
    echo "=== Processing: $name ==="
    
    # Check for banned phrases
    has_banned=$(python3 -c "
import re, sys
banned = ['Apply to Work with Bennett', 'Apply to work with Bennett', 'Get Your AI Agent Quote', 'Get Your AI Quote', 'Get Your Blueprint Quote']
with open('$f') as fh:
    content = fh.read()
found = [p for p in banned if p in content]
print(','.join(found) if found else '')
")
    
    if [ -n "$has_banned" ]; then
        echo "  FIXING banned phrases: $has_banned"
        # Apply fixes
        python3 << PYFIX
with open('$f', 'r') as fh:
    c = fh.read()
banned = ['Apply to Work with Bennett', 'Apply to work with Bennett', 'Get Your AI Agent Quote', 'Get Your AI Quote', 'Get Your Blueprint Quote']
for phrase in banned:
    c = c.replace(phrase, '$CANONICAL_CTA')
with open('$f', 'w') as fh:
    fh.write(c)
print('  Fixed.')
PYFIX
    else
        echo "  CTA OK — no banned phrases"
    fi
    
    # Validate with orchestrator
    slug=$(basename "$f" .html)
    result=$(python3 "$ORCH" --lead "$slug" --validate-only 2>&1)
    rc=$?
    if [ $rc -eq 0 ]; then
        echo "  ✅ Validator PASS"
        FIXED=$((FIXED+1))
    else
        echo "  ❌ Validator FAIL (file needs manual podcast upgrade)"
        echo "$result" | grep "FAIL\|miss" | head -3
        FAILED=$((FAILED+1))
    fi
done

echo ""
echo "=== PROPAGATION COMPLETE ==="
echo "Fixed/validated: $FIXED"
echo "Failed (need manual fix): $FAILED"
echo "Skipped: $SKIPPED"

if [ "$FAILED" -gt 0 ]; then
    echo "⚠️  $FAILED files need manual podcast player upgrade before they can be committed"
    exit 1
fi

echo "✅ All blueprints comply with blueprint-schema.json"
exit 0
