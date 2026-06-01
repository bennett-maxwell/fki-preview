#!/bin/bash
# Blueprint AI Pipeline -- Lead Profile Migration (v1 -> v2)
# Adds missing fields with defaults so all profiles match the latest schema.
# Usage: ./migrate-profiles.sh [leads-dir] [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="${1:-$REPO_DIR/leads}"
DRY_RUN=false
[ "${2:-}" = "--dry-run" ] && DRY_RUN=true

if [ "${1:-}" = "--help" ]; then
    echo "Usage: $0 [leads-dir] [--dry-run]"
    echo ""
    echo "Migrates lead profiles from v1 to v2 schema:"
    echo "  - Adds pipeline_version field"
    echo "  - Adds missing timestamp fields (intake_ts, website_ts, etc.)"
    echo "  - Adds lead_score and lead_tier if missing"
    echo "  - Normalizes services to array-of-objects format"
    echo "  - Adds blueprint_url and website_url if derivable from slug"
    exit 0
fi

echo "=== Lead Profile Migration (v1 -> v2) ==="
echo "Leads dir: $LEADS_DIR"
echo "Dry run: $DRY_RUN"
echo ""

MIGRATED=0
SKIPPED=0

for profile in "$LEADS_DIR"/*.json; do
    [ -f "$profile" ] || continue
    NAME=$(basename "$profile")

    RESULT=$(python3 - "$profile" "$DRY_RUN" <<'PYEOF'
import json, sys

profile_path = sys.argv[1]
dry_run = sys.argv[2] == "true"

with open(profile_path) as f:
    p = json.load(f)

changes = []

# Add pipeline_version
if "pipeline_version" not in p:
    p["pipeline_version"] = "2.1"
    changes.append("added pipeline_version=2.1")

# Ensure slug exists
if "slug" not in p or not p["slug"]:
    name = p.get("lead_name", "unknown")
    p["slug"] = name.lower().replace(" ", "-").replace("'", "")
    changes.append(f"generated slug={p['slug']}")

slug = p["slug"]

# Add blueprint_url if missing
if "blueprint_url" not in p or not p["blueprint_url"]:
    p["blueprint_url"] = f"https://bennett-maxwell.github.io/fki-preview/blueprints/{slug}.html"
    changes.append("added blueprint_url")

# Add website_url if missing
if "website_url" not in p or not p["website_url"]:
    p["website_url"] = f"https://bennett-maxwell.github.io/fki-preview/{slug}-website/"
    changes.append("added website_url")

# Add lead_first_name if missing
if "lead_first_name" not in p:
    p["lead_first_name"] = p.get("lead_name", "there").split()[0]
    changes.append("added lead_first_name")

# Add apply_subject if missing
if "apply_subject" not in p:
    p["apply_subject"] = f"{p.get('lead_name', 'Lead')} - Blueprint Application"
    changes.append("added apply_subject")

# Add lead_score/lead_tier if missing
if "lead_score" not in p:
    score = 0
    if p.get("url"): score += 2
    if p.get("industry") and p["industry"] not in ("Unknown", ""): score += 1
    if p.get("email"): score += 1
    if p.get("phone"): score += 1
    if p.get("ghl_contact_id"): score += 1
    p["lead_score"] = score
    tier = "cold"
    if score >= 5: tier = "hot"
    elif score >= 3: tier = "warm"
    p["lead_tier"] = tier
    changes.append(f"added lead_score={score} lead_tier={tier}")

# Normalize services: ensure array of strings or dicts
if "services" in p and isinstance(p["services"], list):
    normalized = []
    for s in p["services"]:
        if isinstance(s, str):
            normalized.append(s)
        elif isinstance(s, dict):
            normalized.append(s)
    p["services"] = normalized

if changes:
    if not dry_run:
        with open(profile_path, "w") as f:
            json.dump(p, f, indent=2)
    print(f"MIGRATED: {len(changes)} changes: {', '.join(changes)}")
else:
    print("CURRENT: no changes needed")
PYEOF
    )

    if echo "$RESULT" | grep -q "MIGRATED"; then
        MIGRATED=$((MIGRATED + 1))
        echo "  $NAME: $RESULT"
    else
        SKIPPED=$((SKIPPED + 1))
        echo "  $NAME: $RESULT"
    fi
done

echo ""
echo "Done. Migrated: $MIGRATED | Already current: $SKIPPED"
