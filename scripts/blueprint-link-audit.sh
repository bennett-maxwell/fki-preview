#!/usr/bin/env bash
set -euo pipefail

ROOT="${BLUEPRINT_LINK_AUDIT_ROOT:-blueprints}"
OUT_DIR="${BLUEPRINT_LINK_AUDIT_OUT_DIR:-monitor-reports}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="$OUT_DIR/blueprint-link-audit-$STAMP.json"

mkdir -p "$OUT_DIR"

failures=()
total_links=0
qualified_links=0
missing_identity=0
direct_booking=0
legacy_apply=0

while IFS= read -r -d '' file; do
  while IFS= read -r href; do
    [[ -z "$href" ]] && continue
    total_links=$((total_links + 1))
    if [[ "$href" == *"qualify.html"* ]]; then
      qualified_links=$((qualified_links + 1))
      if [[ "$href" != *"lead="* || "$href" != *"biz="* || "$href" != *"src="* ]]; then
        missing_identity=$((missing_identity + 1))
        failures+=("missing_identity_params:$file:$href")
      fi
    fi
    if [[ "$href" == *"/widget/bookings/"* || "$href" == *"calendly.com"* ]]; then
      direct_booking=$((direct_booking + 1))
      failures+=("direct_booking_link:$file:$href")
    fi
    if [[ "$href" == *"/apply/"* || "$href" == *"apply?"* ]]; then
      legacy_apply=$((legacy_apply + 1))
      failures+=("legacy_apply_link:$file:$href")
    fi
  done < <(perl -ne 'while (/href=["'\'']([^"'\'']+)["'\'']/g) { print "$1\n" }' "$file")
done < <(find "$ROOT" -maxdepth 1 -type f -name '*.html' -print0)

status="pass"
if (( ${#failures[@]} > 0 )); then
  status="fail"
fi

failures_json="[]"
if (( ${#failures[@]} > 0 )); then
  failures_json="$(printf '%s\n' "${failures[@]}" | jq -R . | jq -s .)"
fi

jq -n \
  --arg timestamp "$STAMP" \
  --arg root "$ROOT" \
  --arg status "$status" \
  --argjson total_links "$total_links" \
  --argjson qualified_links "$qualified_links" \
  --argjson missing_identity "$missing_identity" \
  --argjson direct_booking "$direct_booking" \
  --argjson legacy_apply "$legacy_apply" \
  --argjson failures "$failures_json" \
  '{
    timestamp: $timestamp,
    root: $root,
    status: $status,
    counts: {
      total_links: $total_links,
      qualifier_links: $qualified_links,
      missing_identity_params: $missing_identity,
      direct_booking_links: $direct_booking,
      legacy_apply_links: $legacy_apply
    },
    failures: $failures
  }' | tee "$OUT_FILE"

[[ "$status" == "pass" ]]
