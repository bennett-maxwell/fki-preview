#!/usr/bin/env bash
set -euo pipefail
# pre-delivery-check.sh — Blueprint AI v2.0 Pre-Delivery Validation
# Usage: ./pre-delivery-check.sh <blueprint.html> [--leads "Name One,Name Two"]
# Output: JSON with pass/fail per check and overall verdict
# Compatible with bash 3.2+ (macOS default)

# ── Usage guard ──────────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <blueprint.html> [--leads \"Lead Name One,Lead Name Two\"]"
  echo ""
  echo "Runs all 10 Blueprint AI v2.0 pre-delivery checks against an HTML file."
  echo ""
  echo "Checks:"
  echo "  1.  booking_urls        — No leadconnectorhq/widget/booking links"
  echo "  2.  discovery_call      — No 'discovery call' phrasing"
  echo "  3.  90day_timeline      — No long 90-day onboarding plans"
  echo "  4.  emojis              — No Unicode emojis in deliverable"
  echo "  5.  apply_cta           — 'apply' appears >= 3 times (case-insensitive)"
  echo "  6.  cadence_3730        — 3-day/7-day/30-day cadence present >= 3 times"
  echo "  7.  calendar_links      — No Calendly/cal.com/calendar.google links"
  echo "  8.  cross_contamination — No other lead names bleed through"
  echo "  9.  all_urls_200        — All GitHub Pages / fki-preview URLs return 200"
  echo "  10. file_size           — File > 50KB (content-rich deliverable)"
  exit 0
fi

FILE="$1"
LEADS_ARG=""

# Parse --leads optional argument
shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --leads)
      LEADS_ARG="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# ── Validate file exists ──────────────────────────────────────────────────────
if [[ ! -f "$FILE" ]]; then
  printf '{"error": "File not found: %s"}\n' "$FILE"
  exit 1
fi

ABS_FILE="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# ── Safe integer count helper ─────────────────────────────────────────────────
# Runs grep and returns a clean integer, never fails the script
safe_grep_count() {
  local result
  result=$(grep -ciE "$1" "$FILE" 2>/dev/null) || result=0
  # Strip all whitespace
  echo "${result//[[:space:]]/}"
}

safe_grep_count_literal() {
  local result
  result=$(grep -ciF "$1" "$FILE" 2>/dev/null) || result=0
  echo "${result//[[:space:]]/}"
}

safe_grep_match_count() {
  local result
  result=$(grep -oiE "$1" "$FILE" 2>/dev/null | wc -l 2>/dev/null) || result=0
  echo "${result//[[:space:]]/}"
}

# ── CHECK 1: booking_urls ─────────────────────────────────────────────────────
booking_count=$(safe_grep_count "leadconnectorhq|widget/booking")
if [[ "${booking_count}" -eq 0 ]]; then
  booking_pass="true"
else
  booking_pass="false"
fi

# ── CHECK 2: discovery_call ───────────────────────────────────────────────────
discovery_count=$(safe_grep_count "discovery call")
if [[ "${discovery_count}" -eq 0 ]]; then
  discovery_pass="true"
else
  discovery_pass="false"
fi

# ── CHECK 3: 90day_timeline ───────────────────────────────────────────────────
# Match "90-day" or "90 day", exclude CSS and financial 30/60/90 patterns
raw_90_lines=$(grep -iE "90.?day" "$FILE" 2>/dev/null || true)
if [[ -n "$raw_90_lines" ]]; then
  filtered_90=$(printf '%s\n' "$raw_90_lines" \
    | grep -viE "90deg|90px|90%|30/60/90|60/90|rotate\(90|transform.*90" \
    || true)
  if [[ -n "$filtered_90" ]]; then
    ninety_count=$(printf '%s\n' "$filtered_90" | grep -c ".")
  else
    ninety_count=0
  fi
else
  ninety_count=0
fi
ninety_count="${ninety_count//[[:space:]]/}"
if [[ "${ninety_count}" -eq 0 ]]; then
  ninety_pass="true"
else
  ninety_pass="false"
fi

# ── CHECK 4: emojis ───────────────────────────────────────────────────────────
# python3 one-liner scans for Unicode emoji codepoint ranges
emoji_count=$(python3 - "$FILE" <<'PYEOF'
import sys, re

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0000FE00-\U0000FE0F"
    "\U0001F1E0-\U0001F1FF"
    "]+",
    flags=re.UNICODE
)

try:
    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    text_only = re.sub(r'<[^>]+>', '', content)
    matches = EMOJI_PATTERN.findall(text_only)
    print(len(matches))
except Exception:
    print(0)
PYEOF
)
emoji_count="${emoji_count//[[:space:]]/}"
emoji_count="${emoji_count:-0}"
if [[ "${emoji_count}" -eq 0 ]]; then
  emoji_pass="true"
else
  emoji_pass="false"
fi

# ── CHECK 5: apply_cta ────────────────────────────────────────────────────────
apply_count=$(safe_grep_match_count "apply")
if [[ "${apply_count}" -ge 3 ]]; then
  apply_pass="true"
else
  apply_pass="false"
fi

# ── CHECK 6: cadence_3730 ─────────────────────────────────────────────────────
cadence_count=$(safe_grep_match_count "(3|7|30)[[:space:]-]day")
if [[ "${cadence_count}" -ge 3 ]]; then
  cadence_pass="true"
else
  cadence_pass="false"
fi

# ── CHECK 7: calendar_links ───────────────────────────────────────────────────
calendar_count=$(safe_grep_count "calendly\.com|cal\.com|calendar\.google\.com")
if [[ "${calendar_count}" -eq 0 ]]; then
  calendar_pass="true"
else
  calendar_pass="false"
fi

# ── CHECK 8: cross_contamination ─────────────────────────────────────────────
contamination_hits=""
contamination_count=0
if [[ -n "$LEADS_ARG" ]]; then
  # Split on comma, check each name
  IFS=',' read -ra LEAD_NAMES <<< "$LEADS_ARG"
  for lead in "${LEAD_NAMES[@]}"; do
    # Trim whitespace
    lead_trimmed=$(printf '%s' "$lead" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [[ -n "$lead_trimmed" ]]; then
      hit=$(safe_grep_count_literal "$lead_trimmed")
      if [[ "${hit}" -gt 0 ]]; then
        contamination_count=$((contamination_count + 1))
        if [[ -n "$contamination_hits" ]]; then
          contamination_hits="$contamination_hits, $lead_trimmed"
        else
          contamination_hits="$lead_trimmed"
        fi
      fi
    fi
  done
fi
if [[ "$contamination_count" -eq 0 ]]; then
  contamination_pass="true"
  contamination_value="0"
else
  contamination_pass="false"
  contamination_value="$contamination_count"
fi

# ── CHECK 9: all_urls_200 ─────────────────────────────────────────────────────
# Extract GitHub Pages / fki-preview URLs; curl HEAD each
URLS_LIST=$(grep -oE 'https?://[^"'\''<> ]+' "$FILE" 2>/dev/null \
  | grep -iE "github\.io|fki-preview" \
  | sort -u || true)

url_fail_count=0
url_total=0
url_fail_details=""

if [[ -z "$URLS_LIST" ]]; then
  urls_pass="true"
  url_value='"no_github_urls_found"'
else
  while IFS= read -r url; do
    [[ -z "$url" ]] && continue
    url_total=$((url_total + 1))
    http_code=$(curl -sI --max-time 10 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    if [[ "$http_code" != "200" && "$http_code" != "301" && "$http_code" != "302" ]]; then
      url_fail_count=$((url_fail_count + 1))
      url_fail_details="${url_fail_details}${url}:${http_code} "
    fi
  done <<< "$URLS_LIST"

  if [[ "$url_fail_count" -eq 0 ]]; then
    urls_pass="true"
    url_value="\"${url_total}_urls_ok\""
  else
    urls_pass="false"
    url_value="\"${url_fail_count}_of_${url_total}_failed\""
  fi
fi

# ── CHECK 10: file_size ───────────────────────────────────────────────────────
file_bytes=$(wc -c < "$FILE")
file_bytes="${file_bytes//[[:space:]]/}"
file_kb=$((file_bytes / 1024))
if [[ "$file_bytes" -gt 51200 ]]; then
  size_pass="true"
else
  size_pass="false"
fi

# ── Collect failures ──────────────────────────────────────────────────────────
failures_json="["
sep=""

add_failure() {
  failures_json+="${sep}\"$1\""
  sep=", "
}

[[ "$booking_pass" == "false" ]]       && add_failure "booking_urls (found ${booking_count})"
[[ "$discovery_pass" == "false" ]]     && add_failure "discovery_call (found ${discovery_count})"
[[ "$ninety_pass" == "false" ]]        && add_failure "90day_timeline (found ${ninety_count})"
[[ "$emoji_pass" == "false" ]]         && add_failure "emojis (found ${emoji_count})"
[[ "$apply_pass" == "false" ]]         && add_failure "apply_cta (found ${apply_count}, need >= 3)"
[[ "$cadence_pass" == "false" ]]       && add_failure "cadence_3730 (found ${cadence_count}, need >= 3)"
[[ "$calendar_pass" == "false" ]]      && add_failure "calendar_links (found ${calendar_count})"
[[ "$contamination_pass" == "false" ]] && add_failure "cross_contamination (names: ${contamination_hits})"
[[ "$urls_pass" == "false" ]]          && add_failure "all_urls_200 (${url_fail_details})"
[[ "$size_pass" == "false" ]]          && add_failure "file_size (${file_kb}KB, need > 50KB)"

failures_json+="]"

# ── Overall verdict ───────────────────────────────────────────────────────────
if [[ "$failures_json" == "[]" ]]; then
  overall="PASS"
else
  overall="FAIL"
fi

# ── Emit JSON ─────────────────────────────────────────────────────────────────
cat <<EOF
{
  "file": "$ABS_FILE",
  "timestamp": "$TIMESTAMP",
  "checks": {
    "booking_urls":        {"value": ${booking_count},        "pass": ${booking_pass}},
    "discovery_call":      {"value": ${discovery_count},      "pass": ${discovery_pass}},
    "90day_timeline":      {"value": ${ninety_count},         "pass": ${ninety_pass}},
    "emojis":              {"value": ${emoji_count},          "pass": ${emoji_pass}},
    "apply_cta":           {"value": ${apply_count},          "pass": ${apply_pass}},
    "cadence_3730":        {"value": ${cadence_count},        "pass": ${cadence_pass}},
    "calendar_links":      {"value": ${calendar_count},       "pass": ${calendar_pass}},
    "cross_contamination": {"value": ${contamination_value},  "pass": ${contamination_pass}},
    "all_urls_200":        {"value": $url_value,              "pass": ${urls_pass}},
    "file_size":           {"value": "${file_bytes}B",        "pass": ${size_pass}}
  },
  "overall": "$overall",
  "failures": $failures_json
}
EOF
