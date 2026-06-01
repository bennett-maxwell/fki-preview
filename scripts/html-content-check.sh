#!/bin/bash
# html-content-check.sh — Blueprint content gate required by bennett-rules.md
# ("Run html-content-check.sh before any Blueprint commit/send. Exit 0 required.")
#
# Wraps the existing render/consistency/CTA gates into one exit-0/1 check so the
# rule is mechanically satisfiable. Network-free; safe in pre-commit.
#
# Usage:
#   scripts/html-content-check.sh blueprints/<slug>.html   # one file
#   scripts/html-content-check.sh --all                    # all 15 canon
#
# Exit 0 = content OK. Exit 1 = at least one check failed (details printed).

set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
D9="$HOME/.claude/skills/blueprint-ai-audit-skill/d9-audit.py"
CONSISTENCY="$REPO/scripts/blueprint-consistency-check.py"

CANON="alex-ramos austin-iron-horse branson-maxwell brent-attaway brittney-warnick \
chris-lpnw court-lundberg dave-wood jaden-mecham melissa-tash-srp paul-muus \
rey-31-consulting rush-evans watson zachary-oldham"

check_one() {
  local f="$1" fail=0 slug
  slug="$(basename "$f" .html)"
  [ -f "$f" ] || { echo "  ❌ $slug: file not found ($f)"; return 1; }

  # 1) D9 render-integrity (network-free)
  if [ -f "$D9" ]; then
    if python3 "$D9" "$f" >/dev/null 2>&1; then echo "  ✅ $slug: D9 render-integrity"; else echo "  ❌ $slug: D9 render-integrity FAILED"; fail=1; fi
  else
    echo "  ⚠ $slug: D9 auditor not found — skipped"
  fi

  # 2) CTA ban: "See If You Qualify" must point only to qualify.html
  if grep -qi "See If You Qualify" "$f"; then
    if grep -i "See If You Qualify" "$f" | grep -qiv "qualify.html"; then
      echo "  ❌ $slug: CTA ban — 'See If You Qualify' not pointing to qualify.html"; fail=1
    fi
  fi

  # 3) No unresolved template tokens.
  # TEMPLATE.html is the token SCAFFOLD the generator clones — {{TOKENS}} are
  # required there by design (mirrors the pre-commit hook's `grep -v TEMPLATE`
  # exclusion). Only deliverable blueprints must be token-free.
  if [ "$slug" != "TEMPLATE" ] && grep -qoE '\{\{[A-Z_]+\}\}' "$f"; then
    echo "  ❌ $slug: unresolved {{TOKEN}} present"; fail=1
  fi

  return $fail
}

OVERALL=0
if [ "${1:-}" = "--all" ]; then
  for slug in $CANON; do check_one "$REPO/blueprints/$slug.html" || OVERALL=1; done
  # cross-blueprint consistency (whole set)
  if [ -f "$CONSISTENCY" ]; then
    if python3 "$CONSISTENCY" >/dev/null 2>&1; then echo "  ✅ consistency: all 15 conform to TEMPLATE.html"; else echo "  ❌ consistency FAILED"; OVERALL=1; fi
  fi
  # data-plausibility (catches wrong-per-business + fabricated current-state numbers)
  PLAUSIBILITY="$REPO/scripts/blueprint-data-plausibility.py"
  if [ -f "$PLAUSIBILITY" ]; then
    if python3 "$PLAUSIBILITY" >/dev/null 2>&1; then echo "  ✅ data-plausibility: no fabricated/implausible client numbers"; else echo "  ❌ data-plausibility FAILED (run: python3 $PLAUSIBILITY)"; OVERALL=1; fi
  fi
  # financial-realism (industry-band ROI slider check — catches cross-industry clones + out-of-band $)
  REALISM="$REPO/financial-realism-check.py"
  if [ -f "$REALISM" ]; then
    if python3 "$REALISM" --all >/dev/null 2>&1; then echo "  ✅ financial-realism: ROI sliders industry-appropriate, no cross-industry clone"; else echo "  ❌ financial-realism FAILED (run: python3 $REALISM --all)"; OVERALL=1; fi
  fi
else
  [ $# -ge 1 ] || { echo "usage: $0 <blueprint.html> | --all"; exit 2; }
  check_one "$1" || OVERALL=1
fi

[ $OVERALL -eq 0 ] && echo "html-content-check: PASS" || echo "html-content-check: FAIL"
exit $OVERALL
