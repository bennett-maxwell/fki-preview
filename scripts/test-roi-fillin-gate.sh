#!/usr/bin/env bash
# Replay-test for the ROI Avg-Customer-Value FILL-IN hard gate (clone-blueprint.sh Step 4a0).
# Bennett directive 2026-06-02: Avg Customer Value must ALWAYS be a typed fill-in number input,
# NEVER a type="range" slider (value is still calculated). This test fails CI if either
#   (a) the gate predicate stops catching a slider regression / missing fill-in, or
#   (b) the gate is ever removed from clone-blueprint.sh.
# Run: bash scripts/test-roi-fillin-gate.sh   (exit 0 = PASS, exit 1 = FAIL)
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CLONE="$HERE/clone-blueprint.sh"
FAILS=0

# The exact gate predicate, mirrored from clone-blueprint.sh Step 4a0.
gate_verdict() {  # $1 = file -> echoes PASS or FAIL
  local f="$1"
  if grep -Eq 'type="range"[^>]*id="sl-contract"|id="sl-contract"[^>]*type="range"' "$f"; then
    echo FAIL
  elif grep -Eq 'type="number"[^>]*id="sl-contract"|id="sl-contract"[^>]*type="number"' "$f"; then
    echo PASS
  else
    echo FAIL
  fi
}

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
printf '<input type="number" class="calc-fill-input" id="sl-contract" min="0" step="100" value="2388">\n' > "$TMP/good.html"
printf '<input type="range" id="sl-contract" min="0" max="50000" value="2388">\n'                          > "$TMP/slider.html"
printf '<p>no contract field present</p>\n'                                                                 > "$TMP/missing.html"

check() {  # $1=label $2=file $3=expected
  local got; got="$(gate_verdict "$2")"
  if [ "$got" = "$3" ]; then
    echo "  PASS  $1: $got (expected $3)"
  else
    echo "  FAIL  $1: $got (expected $3)"; FAILS=$((FAILS+1))
  fi
}

echo "ROI fill-in gate replay-test:"
check "fill-in number input"   "$TMP/good.html"    PASS
check "slider regression"      "$TMP/slider.html"  FAIL
check "missing contract field" "$TMP/missing.html" FAIL

# Guard: the gate must still be wired into clone-blueprint.sh.
if grep -q 'ROI fill-in gate' "$CLONE"; then
  echo "  PASS  gate still wired into clone-blueprint.sh"
else
  echo "  FAIL  gate MISSING from clone-blueprint.sh"; FAILS=$((FAILS+1))
fi

if [ "$FAILS" -eq 0 ]; then
  echo "RESULT: PASS"; exit 0
else
  echo "RESULT: FAIL ($FAILS failing assertion(s))"; exit 1
fi
