#!/bin/bash
# Verify all Blueprint AI deliverables are live on GitHub Pages
BASE="https://bennett-maxwell.github.io/fki-preview"
LEADS_DIR="$(cd "$(dirname "$0")/.." && pwd)/leads"
PASS=0; FAIL=0; TOTAL=0

echo "=== GitHub Pages Verification ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

for f in "$LEADS_DIR"/*.json; do
  slug=$(python3 -c "import json; print(json.load(open('$f')).get('slug',''))")
  name=$(python3 -c "import json; print(json.load(open('$f')).get('lead_name',''))")
  
  # Check blueprint
  bp_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/blueprints/${slug}.html" 2>/dev/null)
  ws_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/${slug}-website/" 2>/dev/null)
  
  TOTAL=$((TOTAL + 2))
  bp_status="PASS"; ws_status="PASS"
  [ "$bp_code" != "200" ] && bp_status="FAIL" && FAIL=$((FAIL + 1)) || PASS=$((PASS + 1))
  [ "$ws_code" != "200" ] && ws_status="FAIL" && FAIL=$((FAIL + 1)) || PASS=$((PASS + 1))
  
  echo "$name ($slug): BP=$bp_code[$bp_status] WS=$ws_code[$ws_status]"
done

# Check apply page
apply_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/apply/" 2>/dev/null)
TOTAL=$((TOTAL + 1))
[ "$apply_code" != "200" ] && FAIL=$((FAIL + 1)) || PASS=$((PASS + 1))
echo ""
echo "Apply page: $apply_code"
echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
