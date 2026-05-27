#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${BLUEPRINT_RUN_LEDGER_DIR:-blueprint-run-ledgers}"
STAMP="${BLUEPRINT_RUN_TIMESTAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
SLUG="${BLUEPRINT_RUN_SLUG:-monitor-$STAMP}"
OUT_FILE="$OUT_DIR/$SLUG.json"

mkdir -p "$OUT_DIR"

tmp="$(mktemp)"
jq -n \
  --arg timestamp "$STAMP" \
  --arg slug "$SLUG" \
  --arg lead_name "${BLUEPRINT_RUN_LEAD_NAME:-}" \
  --arg business_name "${BLUEPRINT_RUN_BUSINESS_NAME:-}" \
  --arg email "${BLUEPRINT_RUN_EMAIL:-}" \
  --arg phone "${BLUEPRINT_RUN_PHONE:-}" \
  --arg contact_id "${BLUEPRINT_RUN_CONTACT_ID:-}" \
  --arg appointment_id "${BLUEPRINT_RUN_APPOINTMENT_ID:-}" \
  --arg blueprint_url "${BLUEPRINT_RUN_BLUEPRINT_URL:-}" \
  --arg qualifier_url "${BLUEPRINT_RUN_QUALIFIER_URL:-}" \
  --arg apply_url "${BLUEPRINT_RUN_APPLY_URL:-}" \
  --arg monitor_report "${BLUEPRINT_RUN_MONITOR_REPORT:-}" \
  --arg release_gate_report "${BLUEPRINT_RUN_RELEASE_GATE_REPORT:-}" \
  --arg link_audit_report "${BLUEPRINT_RUN_LINK_AUDIT_REPORT:-}" \
  --arg status "${BLUEPRINT_RUN_STATUS:-open}" \
  '{
    timestamp: $timestamp,
    slug: $slug,
    status: $status,
    lead: {
      name: $lead_name,
      business: $business_name,
      email: $email,
      phone: $phone,
      ghl_contact_id: $contact_id
    },
    funnel: {
      blueprint_url: $blueprint_url,
      apply_url: $apply_url,
      qualifier_url: $qualifier_url,
      appointment_id: $appointment_id
    },
    proof: {
      monitor_report: $monitor_report,
      release_gate_report: $release_gate_report,
      link_audit_report: $link_audit_report
    }
  }' > "$tmp"

mv "$tmp" "$OUT_FILE"
echo "$OUT_FILE"
