#!/bin/bash
# Blueprint Hallucination Guard — validates HTML claims against lead JSON
# Run: bash scripts/validate-blueprints.sh

RED='\033[0;31m'; GREEN='\033[0;32m'; NC='\033[0m'
PASS=0; FAIL=0

for json in leads/*.json; do
  [[ "$(basename $json)" == "pipeline.db" ]] && continue
  slug=$(python3 -c "import json; print(json.load(open('$json')).get('slug',''))")
  html="blueprints/${slug}.html"
  [[ ! -f "$html" ]] && echo -e "${RED}MISSING: ${html}${NC}" && ((FAIL++)) && continue
  
  # Check for fabricated years
  years=$(python3 -c "import json; print(json.load(open('$json')).get('years_in_business','—'))")
  if [[ "$years" == "—" ]]; then
    founded=$(grep -oP 'Founded.*?<strong>\K[^<]+' "$html" 2>/dev/null)
    if [[ -n "$founded" && "$founded" != "—" ]]; then
      echo -e "${RED}HALLUCINATION: ${slug} — Founded '${founded}' but lead JSON has no year data${NC}"
      ((FAIL++))
    fi
  fi
  
  # Check for fabricated team size
  team=$(python3 -c "import json; print(json.load(open('$json')).get('team_size','—'))")
  if [[ "$team" == "—" ]]; then
    teamhtml=$(grep -oP 'Team Size.*?<strong>\K[^<]+' "$html" 2>/dev/null)
    if [[ -n "$teamhtml" && "$teamhtml" != "—" ]]; then
      echo -e "${RED}HALLUCINATION: ${slug} — Team Size '${teamhtml}' but lead JSON has no team data${NC}"
      ((FAIL++))
    fi
  fi
  
  ((PASS++))
done

echo ""
echo "Results: ${PASS} checked, ${FAIL} issues"
