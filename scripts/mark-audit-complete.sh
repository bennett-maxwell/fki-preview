#!/bin/bash
# mark-audit-complete.sh — writes session-audit-ts-<slug>.json after a confirmed audit pass
# Usage: mark-audit-complete.sh <slug> <score> <checks_passed> <checks_total>
# v3.26 zero-bypass: build-delivery-email.sh checks this file before any Stage 7 send
set -euo pipefail
SLUG="${1:?slug required}"; SCORE="${2:-100}"; PASSED="${3:-0}"; TOTAL="${4:-0}"
TS=$(date +%s)
OUT="$HOME/.openclaw/state/session-audit-ts-${SLUG}.json"
printf '{"ts":%s,"slug":"%s","score":%s,"gate":"audit-gate","checks_passed":%s,"checks_total":%s,"written_by":"mark-audit-complete.sh"}\n' \
  "$TS" "$SLUG" "$SCORE" "$PASSED" "$TOTAL" > "$OUT"
echo "Session audit timestamp written: $OUT"
echo "  score=${SCORE} passed=${PASSED}/${TOTAL} ts=${TS}"
