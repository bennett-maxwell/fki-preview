#!/bin/bash
# Blueprint AI Pipeline -- Enhanced Lead Scoring
# Usage: ./score-leads.sh [leads-dir]
#
# Scoring dimensions (max 15 points):
#   - Has website URL (+2)
#   - Industry detected (not Unknown) (+1)
#   - Has email (+1)
#   - Has phone (+1)
#   - Has GHL contact ID (+1)
#   - Has 3+ services (+2)
#   - Website was scraped successfully (+1)
#   - Has meta description (+1)
#   - Has brand color (not default) (+1)
#   - Profile completeness: >8 fields populated (+2)
#   - Recent activity: intake_ts within 7 days (+2)
#
# Tiers: hot (>=10), warm (>=6), cold (<6)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="${1:-$REPO_DIR/leads}"

if [ "${1:-}" = "--help" ]; then
    echo "Usage: $0 [leads-dir] [--json]"
    echo ""
    echo "Enhanced lead scoring with 11 dimensions, max 15 points."
    echo "Tiers: hot (>=10), warm (>=6), cold (<6)"
    exit 0
fi

JSON_MODE=false
[ "${2:-}" = "--json" ] && JSON_MODE=true

echo "=== Enhanced Lead Scoring ==="
echo ""
printf "%-25s %-6s %-6s %s\n" "LEAD" "SCORE" "TIER" "DIMENSIONS"
printf "%-25s %-6s %-6s %s\n" "----" "-----" "----" "----------"

for profile in "$LEADS_DIR"/*.json; do
    [ -f "$profile" ] || continue

    RESULT=$(python3 - "$profile" <<'PYEOF'
import json, sys, datetime

p = json.load(open(sys.argv[1]))
dims = []
score = 0

# 1. Has website URL (+2)
if p.get('url') and p['url'] not in ('', 'None'):
    score += 2; dims.append('url+2')

# 2. Industry detected (+1)
if p.get('industry') and p['industry'] not in ('Unknown', '', 'business services'):
    score += 1; dims.append('industry+1')

# 3. Has email (+1)
if p.get('email') and p['email'] not in ('', 'None'):
    score += 1; dims.append('email+1')

# 4. Has phone (+1)
if p.get('phone') and p['phone'] not in ('', 'None'):
    score += 1; dims.append('phone+1')

# 5. Has GHL contact ID (+1)
if p.get('ghl_contact_id') and p['ghl_contact_id'] not in ('', 'None'):
    score += 1; dims.append('ghl+1')

# 6. Has 3+ services (+2)
svcs = p.get('services', [])
if len(svcs) >= 3:
    score += 2; dims.append(f'svcs({len(svcs)})+2')

# 7. Website scraped (+1)
if p.get('scraped') is True:
    score += 1; dims.append('scraped+1')

# 8. Has meta description (+1)
if p.get('meta_description') and len(p['meta_description']) > 10:
    score += 1; dims.append('meta+1')

# 9. Brand color not default (+1)
color = p.get('accent_color', '#007AFF')
if color not in ('#007AFF', '#2563EB', '#B75E42'):
    score += 1; dims.append('color+1')

# 10. Profile completeness (+2)
populated = sum(1 for v in p.values() if v and v not in ('', 'None', [], False, 0))
if populated > 8:
    score += 2; dims.append(f'fields({populated})+2')

# 11. Recent intake (+2)
if p.get('intake_ts'):
    try:
        ts = datetime.datetime.strptime(p['intake_ts'], '%Y-%m-%dT%H:%M:%SZ')
        if (datetime.datetime.utcnow() - ts).days <= 7:
            score += 2; dims.append('recent+2')
    except: pass

tier = 'cold'
if score >= 10: tier = 'hot'
elif score >= 6: tier = 'warm'

# Update profile
p['lead_score'] = score
p['lead_tier'] = tier
json.dump(p, open(sys.argv[1], 'w'), indent=2)

name = p.get('lead_name', 'Unknown')[:24]
print(f"{name}|{score}|{tier}|{', '.join(dims)}")
PYEOF
    )

    IFS='|' read -r NAME SCORE TIER DIMS <<< "$RESULT"
    printf "%-25s %-6s %-6s %s\n" "$NAME" "$SCORE" "$TIER" "$DIMS"
done

echo ""
echo "Scoring complete. Profiles updated in place."
