#!/bin/bash
# qualify-url-verify.sh — verify all passed leads have qualify_url in their blueprints
# Auto-run: can be added to daily pipeline check
REPO="$(dirname "$(dirname "$0")")"
LEADS_DIR="$REPO/leads"
PASS=0
FAIL=0
MISSING=()

for json_file in "$LEADS_DIR"/*.json; do
    slug=$(basename "$json_file" .json)
    qualify_url=$(python3 -c "import json; d=json.load(open('$json_file')); print(d.get('qualify_url',''))" 2>/dev/null)
    if [[ -n "$qualify_url" && "$qualify_url" != "None" ]]; then
        PASS=$((PASS+1))
    else
        # Check if it has a blueprint
        bp=$(ls "$REPO/blueprints/$slug"*.html 2>/dev/null | head -1)
        if [[ -n "$bp" ]]; then
            FAIL=$((FAIL+1))
            MISSING+=("$slug")
        fi
    fi
done

echo "qualify_url coverage: $PASS with URL, $FAIL missing"
if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "Missing qualify_url:"
    for m in "${MISSING[@]}"; do echo "  - $m"; done
fi
