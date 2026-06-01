#!/usr/bin/env bash
set -euo pipefail

LOCATION_ID="${GHL_LOCATION_ID:-14RD8KklxR9G4e0Rf7v2}"
CONTACT_ID="${BLUEPRINT_MONITOR_CONTACT_ID:?Set BLUEPRINT_MONITOR_CONTACT_ID}"
APPOINTMENT_ID="${BLUEPRINT_MONITOR_APPOINTMENT_ID:?Set BLUEPRINT_MONITOR_APPOINTMENT_ID}"
OUT_DIR="${BLUEPRINT_APPOINTMENT_OUT_DIR:-monitor-reports}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="$OUT_DIR/blueprint-appointment-attach-$STAMP.json"
mkdir -p "$OUT_DIR"

failures=()
events_json='{"events":[]}'
appointment_count=0

if [[ -z "${GHL_PRIVATE_TOKEN:-}" ]]; then
  failures+=("missing_GHL_PRIVATE_TOKEN")
else
  events_json="$(curl -sS "https://services.leadconnectorhq.com/contacts/$CONTACT_ID/appointments?locationId=$LOCATION_ID" \
    -H "Authorization: Bearer $GHL_PRIVATE_TOKEN" \
    -H 'Version: 2021-07-28')"
  appointment_count="$(jq --arg id "$APPOINTMENT_ID" --arg cid "$CONTACT_ID" '[.events[]? | select(.id==$id and .contactId==$cid)] | length' <<<"$events_json")"
  [[ "$appointment_count" == "1" ]] || failures+=("appointment_not_attached_to_contact")
fi

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
  --arg status "$status" \
  --arg contact_id "$CONTACT_ID" \
  --arg appointment_id "$APPOINTMENT_ID" \
  --argjson appointment_count "$appointment_count" \
  --argjson failures "$failures_json" \
  '{
    timestamp: $timestamp,
    status: $status,
    contact_id: $contact_id,
    appointment_id: $appointment_id,
    appointment_count: $appointment_count,
    failures: $failures
  }' | tee "$OUT_FILE"

[[ "$status" == "pass" ]]
