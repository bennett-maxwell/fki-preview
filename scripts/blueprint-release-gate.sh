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

secret_hits="$(rg -n "Authorization:\\s*Bearer|GHL_PRIVATE_TOKEN|pit-[A-Za-z0-9]{12,}|sk-[A-Za-z0-9]{20,}" apply qualify.html blueprints --glob '!**/*.bak*' --glob '!**/_obsolete/**' 2>/dev/null || true)"
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
# Any deliverable format-3 blueprint MUST pass scripts/format-conformance-check.py
# (exit 0) or it is a hard failure — a format-3 blueprint can never silently drift.
# Legacy (pre-format-3) blueprints are migration-pending WARN, not fail, and
# auto-promote to the hard lock the moment they are regenerated on gold.
CONF="scripts/format-conformance-check.py"
format3_pages=()
if [[ -f "$CONF" ]]; then
  for h in blueprints/*.html; do
    [[ -e "$h" ]] || continue
    b="$(basename "$h" .html)"
    [[ "$b" == "TEMPLATE" ]] && continue
    case "$h" in *.bak*) continue;; esac
    # Format-3 detection uses the gold SECTION IDs, never colour. Colour is not a
    # valid signature: the brand palette was rebased off #0071E3 on 2026-08-06,
    # and several legacy pages carried #0071E3 with sec-1/sec-2 legacy IDs.
    if grep -q 'id="hero"' "$h" && grep -q 'id="profile"' "$h" && grep -q 'id="stack"' "$h" && grep -q 'id="oppmap"' "$h" && grep -q 'id="timeline"' "$h" && grep -q 'id="demo"' "$h" && grep -q 'id="listen"' "$h"; then
      format3_pages+=("$h")
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

# Advaita palette + WCAG contrast lock (2026-08-06).
# WHY THIS IS BLOCKING: the Advaita palette uses Plum #4A1F63 as BOTH the primary
# accent and the hero/nav/CTA/footer background, so `color: var(--brand)` on a dark
# surface renders 1.0:1 and the text is invisible. That exact defect shipped on every
# blueprint for months (the hero H1 accent word measured 1.08:1 in the old blue pages)
# because no grep-level check can see the rendered cascade. Only a real render can.
# Set SKIP_CONTRAST_GATE=1 to bypass during local iteration — never in a release.
# Advaita palette + WCAG contrast lock (2026-08-06). Delegated to a standalone,
# independently testable gate so its bad/good fixtures can be run without this
# script's network + git preamble. See scripts/advaita-palette-gate.sh for why
# contrast enforcement has to be a real render rather than a grep.
PGATE="scripts/advaita-palette-gate.sh"
if [[ ! -x "$PGATE" && ! -f "$PGATE" ]]; then
  failures+=("advaita_palette_gate_missing")
elif (( ${#format3_pages[@]} == 0 )); then
  warnings+=("advaita_palette_gate_no_format3_pages")
else
  while read -r verdict reason; do
    case "$verdict" in
      FAIL) failures+=("$reason") ;;
      WARN) warnings+=("$reason") ;;
    esac
  done < <(bash "$PGATE" "${format3_pages[@]}" 2>/dev/null || true)
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
