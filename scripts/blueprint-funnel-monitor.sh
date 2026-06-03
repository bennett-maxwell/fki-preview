#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BLUEPRINT_BASE_URL:-https://bennett-maxwell.github.io/fki-preview}"
RELAY_URL="${BLUEPRINT_RELAY_URL:-https://blueprint-ghl-relay.vercel.app/api/blueprint-lead}"
LOCATION_ID="${GHL_LOCATION_ID:-14RD8KklxR9G4e0Rf7v2}"
CONTACT_ID="${BLUEPRINT_MONITOR_CONTACT_ID:-r8PjrF8A4fZOca1wA7lH}"
CONTACT_EMAIL="${BLUEPRINT_MONITOR_EMAIL:-blueprint-diamond-20260527145257@franchiseki.com}"
CONTACT_PHONE="${BLUEPRINT_MONITOR_PHONE:-}"
APPOINTMENT_ID="${BLUEPRINT_MONITOR_APPOINTMENT_ID:-KOOvctuPJuiHIaL8KKE3}"
OUT_DIR="${BLUEPRINT_MONITOR_OUT_DIR:-monitor-reports}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="$OUT_DIR/blueprint-funnel-monitor-$STAMP.json"
LEDGER_FILE=""

mkdir -p "$OUT_DIR"

failures=()

apply_html="$(curl -fsSL "$BASE_URL/apply/")"
qualify_html="$(curl -fsSL "$BASE_URL/qualify.html")"

[[ "$apply_html" == *"$RELAY_URL"* ]] || failures+=("apply_missing_relay_url")
[[ "$apply_html" == *"submitPromise"* ]] || failures+=("apply_missing_relay_wait")
[[ "$qualify_html" == *"$RELAY_URL"* ]] || failures+=("qualifier_missing_relay_url")
[[ "$qualify_html" == *"BOOKING_URL"* ]] || failures+=("qualifier_missing_booking_url")
[[ "$qualify_html" == *'name="email"'* && "$qualify_html" == *'name="phone"'* ]] || failures+=("qualifier_missing_required_email_phone")
[[ "$qualify_html" == *"the qualifier must NEVER pre-fill any visible"* ]] || failures+=("qualifier_missing_blank_identity_guard")
[[ "$qualify_html" == *"blueprint_qualifier_submit"* ]] || failures+=("qualifier_missing_tracked_submit_event")
[[ "$apply_html" == *"blueprint_apply_submit"* ]] || failures+=("apply_missing_tracked_submit_event")

secret_hits="$(printf '%s\n%s\n' "$apply_html" "$qualify_html" | rg -n "Authorization:\\s*Bearer|GHL_PRIVATE_TOKEN|pit-[A-Za-z0-9]{12,}|sk-[A-Za-z0-9]{20,}" || true)"
[[ -z "$secret_hits" ]] || failures+=("public_frontend_possible_secret")

bad_input="$(curl -sS -w '\nHTTP_STATUS:%{http_code}\n' -X POST "$RELAY_URL" -H 'Content-Type: application/json' --data '{"event_name":"monitor_bad_input"}')"
[[ "$bad_input" == *"HTTP_STATUS:400"* && "$bad_input" == *"missing_required_identity"* ]] || failures+=("relay_bad_input_not_rejected")

contact_json="{}"
appointments_json="{}"
exact_count=0
phone_count=0
appointment_count=0

if [[ -n "${GHL_PRIVATE_TOKEN:-}" ]]; then
  contact_json="$(curl -sS "https://services.leadconnectorhq.com/contacts/?locationId=$LOCATION_ID&query=$CONTACT_EMAIL&limit=20" \
    -H "Authorization: Bearer $GHL_PRIVATE_TOKEN" \
    -H 'Version: 2021-07-28')"
  exact_count="$(jq --arg email "$CONTACT_EMAIL" '[.contacts[]? | select(.email==$email)] | length' <<<"$contact_json")"
  [[ "$exact_count" == "1" ]] || failures+=("ghl_monitor_contact_exact_count_$exact_count")

  if [[ -n "$CONTACT_PHONE" ]]; then
    phone_count="$(jq --arg phone "$CONTACT_PHONE" '[.contacts[]? | select((.phone // "")==$phone)] | length' <<<"$contact_json")"
    [[ "$phone_count" == "1" ]] || failures+=("ghl_monitor_phone_count_$phone_count")
  fi

  appointments_json="$(curl -sS "https://services.leadconnectorhq.com/contacts/$CONTACT_ID/appointments" \
    -H "Authorization: Bearer $GHL_PRIVATE_TOKEN" \
    -H 'Version: 2021-07-28')"
  appointment_count="$(jq --arg id "$APPOINTMENT_ID" '[.events[]? | select(.id==$id and .contactId=="'"$CONTACT_ID"'")] | length' <<<"$appointments_json")"
  [[ "$appointment_count" == "1" ]] || failures+=("ghl_monitor_appointment_missing")
else
  failures+=("missing_GHL_PRIVATE_TOKEN")
fi

status="pass"
if (( ${#failures[@]} > 0 )); then
  status="fail"
fi

failures_json="[]"
if (( ${#failures[@]} > 0 )); then
  failures_json="$(printf '%s\n' "${failures[@]}" | jq -R . | jq -s .)"
fi

if [[ -x "./scripts/blueprint-run-ledger.sh" ]]; then
  LEDGER_FILE="$(BLUEPRINT_RUN_TIMESTAMP="$STAMP" \
    BLUEPRINT_RUN_SLUG="monitor-$STAMP" \
    BLUEPRINT_RUN_EMAIL="$CONTACT_EMAIL" \
    BLUEPRINT_RUN_PHONE="$CONTACT_PHONE" \
    BLUEPRINT_RUN_CONTACT_ID="$CONTACT_ID" \
    BLUEPRINT_RUN_APPOINTMENT_ID="$APPOINTMENT_ID" \
    BLUEPRINT_RUN_APPLY_URL="$BASE_URL/apply/" \
    BLUEPRINT_RUN_QUALIFIER_URL="$BASE_URL/qualify.html" \
    BLUEPRINT_RUN_MONITOR_REPORT="$OUT_FILE" \
    BLUEPRINT_RUN_STATUS="$status" \
    ./scripts/blueprint-run-ledger.sh)"
fi

jq -n \
  --arg timestamp "$STAMP" \
  --arg status "$status" \
  --arg base_url "$BASE_URL" \
  --arg relay_url "$RELAY_URL" \
  --arg contact_id "$CONTACT_ID" \
  --arg contact_email "$CONTACT_EMAIL" \
  --arg appointment_id "$APPOINTMENT_ID" \
  --arg ledger_file "$LEDGER_FILE" \
  --argjson exact_count "$exact_count" \
  --argjson phone_count "$phone_count" \
  --argjson appointment_count "$appointment_count" \
  --argjson failures "$failures_json" \
  '{
    timestamp: $timestamp,
    status: $status,
    base_url: $base_url,
    relay_url: $relay_url,
    monitored_contact: {id: $contact_id, email: $contact_email},
    monitored_appointment: {id: $appointment_id},
    run_ledger: $ledger_file,
    checks: {
      public_apply_relay: true,
      public_apply_waits_for_relay: true,
      public_qualifier_relay: true,
      public_qualifier_booking: true,
      relay_bad_input_rejected: true,
      ghl_exact_contact_count: $exact_count,
      ghl_phone_count: $phone_count,
      ghl_appointment_count: $appointment_count
    },
    failures: $failures
  }' | tee "$OUT_FILE"

[[ "$status" == "pass" ]]
