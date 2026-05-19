#!/bin/bash
# validate-profile.sh -- Validate a lead profile JSON against the schema
# Usage: ./validate-profile.sh <lead-profile.json>
# Returns 0 if valid, 1 if invalid

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCHEMA="$SCRIPT_DIR/../templates/lead-profile-schema.json"

if [ $# -lt 1 ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 <lead-profile.json>"
    echo ""
    echo "Validates a lead profile against the Blueprint AI schema."
    echo "Checks: required fields, field types, slug format, color format."
    exit 0
fi

PROFILE="$1"

if [ ! -f "$PROFILE" ]; then
    echo "ERROR: File not found: $PROFILE"
    exit 1
fi

# Validate using python3 (no external deps needed)
python3 - "$PROFILE" "$SCHEMA" <<'PYEOF'
import json, sys, re

profile_path = sys.argv[1]
schema_path = sys.argv[2]

try:
    with open(profile_path) as f:
        profile = json.load(f)
except json.JSONDecodeError as e:
    print(f"FAIL: Invalid JSON in {profile_path}: {e}")
    sys.exit(1)

try:
    with open(schema_path) as f:
        schema = json.load(f)
except Exception:
    # If schema file missing, do basic validation only
    schema = None

errors = []

# Required fields check
required = ["lead_name", "business_name", "slug", "accent_color", "industry"]
if schema:
    required = schema.get("required", required)

for field in required:
    if field not in profile or not profile[field]:
        errors.append(f"Missing required field: {field}")

# Type checks
if "lead_name" in profile and not isinstance(profile["lead_name"], str):
    errors.append("lead_name must be a string")
if "business_name" in profile and not isinstance(profile["business_name"], str):
    errors.append("business_name must be a string")

# Slug format check
if "slug" in profile:
    slug = profile["slug"]
    if not re.match(r'^[a-z0-9-]+$', slug):
        errors.append(f"slug has invalid chars (must be lowercase alphanumeric + hyphens): {slug}")

# Accent color format check
if "accent_color" in profile:
    color = profile["accent_color"]
    if not re.match(r'^#[0-9a-fA-F]{6}$', color):
        errors.append(f"accent_color must be a hex color (#RRGGBB): {color}")

# Services type check
if "services" in profile:
    svc = profile["services"]
    if not isinstance(svc, list):
        errors.append("services must be an array")

# Email format check (if present)
if profile.get("email"):
    email = profile["email"]
    if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', email):
        errors.append(f"email format invalid: {email}")

if errors:
    print(f"FAIL: {profile_path}")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"PASS: {profile_path} (all {len(required)} required fields present, formats valid)")
    sys.exit(0)
PYEOF
