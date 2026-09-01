#!/usr/bin/env bash
# advaita-palette-gate.sh — Advaita palette + WCAG contrast lock for blueprints.
#
# WHY THIS EXISTS AND WHY IT IS BLOCKING
# The Advaita palette uses Plum #4A1F63 as BOTH the primary accent AND the
# hero/nav/CTA/footer background. So `color: var(--brand)` on a dark surface
# renders 1.0:1 and the text is invisible. That defect shipped on every blueprint
# for months — the hero H1 accent word measured 1.08:1 in the pre-rebrand blue
# pages too. No grep-level check can catch it, because it only exists in the
# rendered cascade. Only a real browser render can. Hence contrast-audit.py.
#
# SCOPE (mirrors the format-3 migration convention in blueprint-release-gate.sh)
#   * Pages already on the Advaita palette  -> HARD LOCK (fail)
#   * Pages still on the retired blue       -> migration-pending WARN
# This keeps the gate from going permanently red on the pre-rebrand back catalogue.
#
# Emits one `FAIL <reason>` / `WARN <reason>` / `OK <reason>` line per finding.
# Exit 1 if any FAIL. Callers map the lines into their own failure/warning arrays.
#
# Usage:
#   advaita-palette-gate.sh                 # defaults to blueprints/*.html
#   advaita-palette-gate.sh path/a.html ...
#   SKIP_CONTRAST_GATE=1 advaita-palette-gate.sh    # local iteration ONLY
set -uo pipefail

cd "$(dirname "$0")/.." || exit 2

if (( $# > 0 )); then
  candidates=("$@")
else
  candidates=()
  for h in blueprints/*.html; do
    [[ -e "$h" ]] || continue
    candidates+=("$h")
  done
fi

RETIRED_RE='#0071E3|#1D1D1F|#F5F5F7|rgba\(0, *113, *227'
ADVAITA_RE='--saffron:|#4A1F63'

slug() { local s; s="$(basename "$1" .html)"; printf '%s' "${s//[^a-zA-Z0-9]/_}"; }

advaita_pages=()
fails=0

for h in "${candidates[@]}"; do
  [[ -e "$h" ]] || continue
  b="$(basename "$h" .html)"
  [[ "$b" == "TEMPLATE" ]] && continue
  case "$h" in *.bak*) continue;; esac

  # -e is REQUIRED: the pattern starts with "--" and grep would otherwise parse
  # it as a long option, silently reporting every page as migration-pending.
  if grep -qE -e "$ADVAITA_RE" "$h"; then
    advaita_pages+=("$h")
    # Mixed state = a partial or reverted rebrand. Never allowed.
    if grep -qiE -e "$RETIRED_RE" "$h"; then
      echo "FAIL palette_mixed_advaita_and_retired_blue_$(slug "$h")"
      fails=$((fails+1))
    fi
  else
    echo "WARN advaita_palette_migration_pending_$(slug "$h")"
  fi
done

if (( ${#advaita_pages[@]} == 0 )); then
  echo "OK no_advaita_pages_to_lock"
  exit $(( fails > 0 ? 1 : 0 ))
fi

CONTRAST="scripts/contrast-audit.py"
if [[ "${SKIP_CONTRAST_GATE:-0}" == "1" ]]; then
  echo "WARN contrast_gate_skipped_by_env"
elif [[ ! -f "$CONTRAST" ]]; then
  echo "FAIL contrast_audit_script_missing"
  fails=$((fails+1))
elif ! python3 -c 'import playwright' >/dev/null 2>&1; then
  # Unavailable enforcement is a failure, not a silent pass.
  echo "FAIL contrast_gate_unavailable_playwright_missing"
  fails=$((fails+1))
else
  # One browser for the whole batch; --quiet prints only offenders.
  out="$(python3 "$CONTRAST" "${advaita_pages[@]}" --quiet 2>&1 || true)"
  if grep -q '^RESULT: PASS' <<<"$out"; then
    echo "OK contrast_wcag_pass_${#advaita_pages[@]}_pages"
  else
    while read -r bad; do
      [[ -n "$bad" ]] || continue
      echo "FAIL contrast_wcag_fail_$(slug "$bad")"
      fails=$((fails+1))
    done < <(grep '^CONTRAST AUDIT ' <<<"$out" | sed 's/^CONTRAST AUDIT //')
    printf '%s\n' "$out" >&2
  fi
fi

exit $(( fails > 0 ? 1 : 0 ))
