#!/usr/bin/env bash
# validate-delivery-ready.sh — Ivan CC autopilot gate
# Returns exit 0 if all non-template leads pass pre-delivery, exit 1 otherwise
# Created: 2026-05-20 by Ivan CC (Cycle 173 council loop)
set -eo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
OUTPUT=$(bash scripts/batch-pre-delivery.sh 2>&1)
echo "$OUTPUT"
# Check for non-template failures only
FAILURES=$(echo "$OUTPUT" | grep -E "^[a-z].*FAIL" | grep -v "^TEMPLATE" || true)
if [ -n "$FAILURES" ]; then
  echo "DELIVERY NOT READY — failures: $FAILURES"
  exit 1
else
  echo "ALL LEADS DELIVERY-READY"
  exit 0
fi
