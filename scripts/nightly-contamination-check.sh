#!/bin/bash
# nightly-contamination-check.sh — Scan deployed blueprints for leftover template/Brittney contamination
# Runs nightly via LaunchAgent com.advaita.blueprint-contamination-check
# Exit 0 = clean, Exit 1 = contamination found

set -euo pipefail

BLUEPRINTS_DIR="${BLUEPRINTS_DIR:-/Users/temp/fki-preview/blueprints}"
LOG_FILE="$HOME/.openclaw/logs/contamination-check.jsonl"
SLACK_CHANNEL="C0AKXT2S1T2"
SLACK_TOKEN="${SLACK_BOT_TOKEN:-}"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Contamination phrases that should never appear in any deployed blueprint
UNIVERSAL_PHRASES=(
  "Events Designed"
  "luxury event design"
  "HoneyBook"
  "Dallas luxury market"
)

# Additional phrases that should not appear in non-Brittney files
BRITTNEY_PHRASES=(
  "Brittney Warnick"
  "Warnick Design"
  "warnickdesign.com"
)

contamination_found=0
contaminated_files=()
details=""

for file in "$BLUEPRINTS_DIR"/*.html; do
  basename="$(basename "$file")"

  # Skip the template
  if [[ "$basename" == "TEMPLATE.html" ]]; then
    continue
  fi

  file_hits=()

  # Check universal phrases
  for phrase in "${UNIVERSAL_PHRASES[@]}"; do
    if grep -qi "$phrase" "$file" 2>/dev/null; then
      file_hits+=("$phrase")
    fi
  done

  # Check Brittney-specific phrases on non-Brittney files
  if [[ "$basename" != "brittney-warnick.html" ]]; then
    for phrase in "${BRITTNEY_PHRASES[@]}"; do
      if grep -qi "$phrase" "$file" 2>/dev/null; then
        file_hits+=("$phrase")
      fi
    done
  fi

  if [[ ${#file_hits[@]} -gt 0 ]]; then
    contamination_found=1
    contaminated_files+=("$basename")
    hits_json="$(printf '%s\n' "${file_hits[@]}" | jq -R . | jq -sc .)"
    details+="• $basename: ${file_hits[*]}\n"

    # Log each contaminated file
    jq -nc \
      --arg ts "$TIMESTAMP" \
      --arg file "$basename" \
      --argjson hits "$hits_json" \
      '{"timestamp":$ts,"file":$file,"hits":$hits,"status":"CONTAMINATED"}' \
      >> "$LOG_FILE"
  fi
done

# Log clean run if nothing found
if [[ $contamination_found -eq 0 ]]; then
  jq -nc \
    --arg ts "$TIMESTAMP" \
    '{"timestamp":$ts,"status":"CLEAN","message":"All blueprints passed contamination check"}' \
    >> "$LOG_FILE"
  echo "[$(date)] Contamination check PASSED — all blueprints clean"
  exit 0
fi

# Contamination found — alert
echo "[$(date)] Contamination check FAILED — ${#contaminated_files[@]} file(s) contaminated"

# Post to Slack if token available
if [[ -n "$SLACK_TOKEN" ]]; then
  alert_text=":rotating_light: *Blueprint Contamination Alert*\n${#contaminated_files[@]} file(s) have leftover template content:\n${details}"
  curl -s -X POST "https://slack.com/api/chat.postMessage" \
    -H "Authorization: Bearer $SLACK_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$(jq -nc \
      --arg channel "$SLACK_CHANNEL" \
      --arg text "$alert_text" \
      '{"channel":$channel,"text":$text}')" \
    > /dev/null 2>&1
  echo "[$(date)] Slack alert posted to #leo-auto"
else
  echo "[$(date)] SLACK_BOT_TOKEN not set — skipping Slack alert"
fi

exit 1
