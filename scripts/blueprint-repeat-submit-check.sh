#!/usr/bin/env bash
set -euo pipefail

RELAY_URL="${BLUEPRINT_RELAY_URL:-https://blueprint-ghl-relay.vercel.app/api/blueprint-lead}"
LOCATION_ID="${GHL_LOCATION_ID:-14RD8KklxR9G4e0Rf7v2}"
OUT_DIR="${BLUEPRINT_REPEAT_OUT_DIR:-monitor-reports}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EMAIL="${BLUEPRINT_REPEAT_EMAIL:-blueprint-repeat-$(tr '[:upper:]' '[:lower:]' <<<"$STAMP")@franchiseki.com}"
PHONE="${BLUEPRINT_REPEAT_PHONE:-+1555000${STAMP:9:6}}"
OUT_FILE="$OUT_DIR/blueprint-repeat-submit-$STAMP.json"
mkdir -p "$OUT_DIR"

failures=()
responses='[]'
contact_count=0
contact_id=""

for i in 1 2 3 4 5; do
  payload="$(jq -n \
    --arg email "$EMAIL" \
    --arg phone "$PHONE" \
    --arg run "$STAMP" \
    --argjson i "$i" \
    '{
      event_name: "blueprint_qualifier_submit",
      form_version: "2026-05-27-repeat-submit-check",
      locationId: "'"$LOCATION_ID"'",
      firstName: "Blueprint",
      lastName: "RepeatCheck",
      email: $email,
      phone: $phone,
      businessName: "Blueprint Repeat Submit Check",
      source: "blueprint_ai_qualifier",
      original_source: "repeat_submit_check",
      blueprint_slug: "repeat-submit-check",
      contact_id: "'"$contact_id"'",
      lead_session_id: ("repeat-" + $run),
      qualification_band: "strong",
      ai_qualified: true,
      monthly_leads: 50,
      average_deal_value: 5000,
      leads_per_sale: 5,
      response_speed: "under_5_minutes",
      owner_hours_per_week: 15,
      team_members: 2,
      team_hours_per_member: 5,
      first_deploy: "ready_now",
      monthly_ad_spend: 2000,
      questions_answered: 8,
      tags: ["advaita-ai-qualifier", "advaita-qualified", "blueprint_ai_qualifier", "blueprint-repeat-submit-check"],
      note: ("Blueprint repeat-submit check run " + ($i|tostring) + "/5 at " + $run),
      submitted_at: (now | todateiso8601)
    }')"
  response="$(curl -sS -w '\nHTTP_STATUS:%{http_code}\n' -X POST "$RELAY_URL" -H 'Content-Type: application/json' --data "$payload")"
  status_code="$(awk -F: '/HTTP_STATUS/{print $2}' <<<"$response" | tr -d '\r')"
  body="$(sed '/HTTP_STATUS:/d' <<<"$response")"
  [[ "$status_code" == "200" || "$status_code" == "201" ]] || failures+=("relay_submit_${i}_http_$status_code")
  returned_contact_id="$(jq -r '.contactId // empty' <<<"$body" 2>/dev/null || true)"
  [[ -n "$returned_contact_id" ]] && contact_id="$returned_contact_id"
  response_summary="$(jq -c '.' <<<"$body" 2>/dev/null || jq -n --arg raw "$body" '{raw: $raw}')"
  responses="$(jq --argjson old "$responses" --arg status "$status_code" --arg contact "$returned_contact_id" --argjson body "$response_summary" '$old + [{http_status: $status, contactId: $contact, body: $body}]' <<<"{}")"
  sleep "${BLUEPRINT_REPEAT_SLEEP_SECONDS:-2}"
done

contacts_json='{"contacts":[]}'
if [[ -z "${GHL_PRIVATE_TOKEN:-}" ]]; then
  failures+=("missing_GHL_PRIVATE_TOKEN")
else
  contacts_json="$(curl -sS "https://services.leadconnectorhq.com/contacts/?locationId=$LOCATION_ID&query=$EMAIL&limit=20" \
    -H "Authorization: Bearer $GHL_PRIVATE_TOKEN" \
    -H 'Version: 2021-07-28')"
  contact_count="$(jq --arg email "$EMAIL" '[.contacts[]? | select((.email // "" | ascii_downcase)==($email | ascii_downcase))] | length' <<<"$contacts_json")"
  if [[ "$contact_count" == "0" && -n "$contact_id" ]]; then
    contact_by_id="$(curl -sS "https://services.leadconnectorhq.com/contacts/$contact_id" \
      -H "Authorization: Bearer $GHL_PRIVATE_TOKEN" \
      -H 'Version: 2021-07-28')"
    contact_count="$(jq --arg email "$EMAIL" 'if (.contact.email // "" | ascii_downcase) == ($email | ascii_downcase) then 1 else 0 end' <<<"$contact_by_id")"
  fi
  [[ "$contact_count" == "1" ]] || failures+=("repeat_submit_exact_contact_count_$contact_count")
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
  --arg email "$EMAIL" \
  --arg phone "$PHONE" \
  --arg contact_id "$contact_id" \
  --argjson contact_count "$contact_count" \
  --argjson responses "$responses" \
  --argjson failures "$failures_json" \
  '{
    timestamp: $timestamp,
    status: $status,
    test_identity: {email: $email, phone: $phone, contactId: $contact_id},
    submissions: $responses,
    exact_contact_count: $contact_count,
    failures: $failures
  }' | tee "$OUT_FILE"

[[ "$status" == "pass" ]]
