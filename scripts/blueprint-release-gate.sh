#!/usr/bin/env bash
set -euo pipefail

ALLOW_DIRTY="false"
if [[ "${1:-}" == "--allow-dirty" || "${BLUEPRINT_RELEASE_ALLOW_DIRTY:-}" == "1" ]]; then
  ALLOW_DIRTY="true"
fi

OUT_DIR="${BLUEPRINT_RELEASE_OUT_DIR:-monitor-reports}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="$OUT_DIR/blueprint-release-gate-$STAMP.json"
mkdir -p "$OUT_DIR"

failures=()
warnings=()

if [[ "$ALLOW_DIRTY" != "true" && -n "$(git status --short)" ]]; then
  failures+=("dirty_worktree")
elif [[ -n "$(git status --short)" ]]; then
  warnings+=("dirty_worktree_allowed")
fi

secret_hits="$(rg -n "Authorization:\\s*Bearer|GHL_PRIVATE_TOKEN|pit-[a-zA-Z0-9]|sk-[A-Za-z0-9]" apply qualify.html blueprints --glob '!**/*.bak*' --glob '!**/_obsolete/**' 2>/dev/null || true)"
if [[ -n "$secret_hits" ]]; then
  failures+=("possible_public_secret_reference")
fi

apply_html="$(curl -fsSL "${BLUEPRINT_BASE_URL:-https://bennett-maxwell.github.io/fki-preview}/apply/")"
qualify_html="$(curl -fsSL "${BLUEPRINT_BASE_URL:-https://bennett-maxwell.github.io/fki-preview}/qualify.html")"

for marker in "name=\"first_name\"" "name=\"last_name\"" "name=\"email\"" "name=\"phone\"" "name=\"business_name\"" "blueprint_apply_submit"; do
  [[ "$apply_html" == *"$marker"* ]] || failures+=("public_apply_missing_${marker//[^a-zA-Z0-9]/_}")
done

for marker in "id=\"lead-first\"" "id=\"lead-last\"" "id=\"lead-email\"" "id=\"lead-phone\"" "id=\"lead-business\"" "blueprint_qualifier_submit" "BOOKING_URL"; do
  [[ "$qualify_html" == *"$marker"* ]] || failures+=("public_qualify_missing_${marker//[^a-zA-Z0-9]/_}")
done

if [[ "$qualify_html" != *"ki.franchiseki.com/widget/bookings/ai-strategy-call-wuvot-1"* ]]; then
  failures+=("public_qualify_booking_url_not_allowlisted")
fi

latest_pages_status="unknown"
if command -v gh >/dev/null 2>&1; then
  latest_pages_status="$(gh api repos/bennett-maxwell/fki-preview/pages/builds/latest --jq '.status' 2>/dev/null || true)"
  [[ "$latest_pages_status" == "built" ]] || warnings+=("github_pages_status_$latest_pages_status")
else
  warnings+=("gh_cli_unavailable")
fi

# Format-3 conformance lock (full-chain PF0-5 — 2026-06-01).
# Any deliverable blueprint that carries the format-3 brand signature (#0071E3) MUST
# pass scripts/format-conformance-check.py (exit 0) or it is a hard failure — a format-3
# blueprint can never silently drift. Legacy (pre-format-3) blueprints are migration-pending
# WARN, not fail, and auto-promote to the hard lock the moment they are regenerated on gold.
CONF="scripts/format-conformance-check.py"
if [[ -f "$CONF" ]]; then
  for h in blueprints/*.html; do
    [[ -e "$h" ]] || continue
    b="$(basename "$h" .html)"
    [[ "$b" == "TEMPLATE" ]] && continue
    case "$h" in *.bak*) continue;; esac
    if grep -q "0071E3" "$h"; then
      if ! python3 "$CONF" "$h" >/dev/null 2>&1; then
        failures+=("format3_conformance_drift_${b//[^a-zA-Z0-9]/_}")
      fi
    else
      warnings+=("format3_migration_pending_${b//[^a-zA-Z0-9]/_}")
    fi
  done
else
  warnings+=("format_conformance_check_missing")
fi

status="pass"
if (( ${#failures[@]} > 0 )); then
  status="fail"
fi

failures_json="[]"
warnings_json="[]"
if (( ${#failures[@]} > 0 )); then
  failures_json="$(printf '%s\n' "${failures[@]}" | jq -R . | jq -s .)"
fi
if (( ${#warnings[@]} > 0 )); then
  warnings_json="$(printf '%s\n' "${warnings[@]}" | jq -R . | jq -s .)"
fi

jq -n \
  --arg timestamp "$STAMP" \
  --arg status "$status" \
  --arg latest_pages_status "$latest_pages_status" \
  --argjson failures "$failures_json" \
  --argjson warnings "$warnings_json" \
  '{
    timestamp: $timestamp,
    status: $status,
    github_pages_status: $latest_pages_status,
    warnings: $warnings,
    failures: $failures
  }' | tee "$OUT_FILE"

[[ "$status" == "pass" ]]
