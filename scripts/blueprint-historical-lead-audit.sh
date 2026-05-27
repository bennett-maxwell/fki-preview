#!/usr/bin/env bash
set -euo pipefail

QUERY="${1:-${BLUEPRINT_HISTORICAL_QUERY:-Brent Attaway}}"
LOCATION_ID="${GHL_LOCATION_ID:-14RD8KklxR9G4e0Rf7v2}"
OUT_DIR="${BLUEPRINT_HISTORICAL_OUT_DIR:-monitor-reports}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SAFE_QUERY="$(tr '[:upper:] ' '[:lower:]-' <<<"$QUERY" | tr -cd 'a-z0-9-')"
OUT_FILE="$OUT_DIR/blueprint-historical-lead-audit-$SAFE_QUERY-$STAMP.json"
mkdir -p "$OUT_DIR"

failures=()
contacts_json='{"contacts":[]}'
contact_count=0
exact_email_count=0

if [[ -z "${GHL_PRIVATE_TOKEN:-}" ]]; then
  failures+=("missing_GHL_PRIVATE_TOKEN")
else
  contacts_json="$(curl -sS "https://services.leadconnectorhq.com/contacts/?locationId=$LOCATION_ID&query=$(python3 -c 'import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "$QUERY")&limit=20" \
    -H "Authorization: Bearer $GHL_PRIVATE_TOKEN" \
    -H 'Version: 2021-07-28')"
  contact_count="$(jq '[.contacts[]?] | length' <<<"$contacts_json")"
  if [[ "$QUERY" == *"@"* ]]; then
    exact_email_count="$(jq --arg email "$QUERY" '[.contacts[]? | select((.email // "") == $email)] | length' <<<"$contacts_json")"
  fi
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
  --arg query "$QUERY" \
  --argjson contact_count "$contact_count" \
  --argjson exact_email_count "$exact_email_count" \
  --argjson failures "$failures_json" \
  --argjson contacts "$contacts_json" \
  '{
    timestamp: $timestamp,
    status: $status,
    query: $query,
    contact_count: $contact_count,
    exact_email_count: $exact_email_count,
    contacts: [
      $contacts.contacts[]? | {
        id,
        firstName,
        lastName,
        email,
        phone,
        tags,
        source
      }
    ],
    failures: $failures
  }' | tee "$OUT_FILE"

[[ "$status" == "pass" ]]
