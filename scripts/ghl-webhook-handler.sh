#!/bin/bash
# Blueprint AI Pipeline — GHL Webhook Handler
# Receives webhook POST from GHL form submission, triggers full pipeline
#
# Setup: Run a lightweight HTTP listener that calls this script on each POST
# Example with socat:
#   socat TCP-LISTEN:8090,reuseaddr,fork EXEC:"./ghl-webhook-handler.sh"
#
# GHL webhook payload contains: contact_id, first_name, last_name, email, phone, website, custom_fields
# Configure GHL workflow: Form Submit → Webhook → http://<host>:8090

set -euo pipefail

# Help
if [ "${1:-}" = "--help" ]; then
    echo "Blueprint AI Pipeline -- GHL Webhook Handler"
    echo ""
    echo "Usage: Receives webhook POST via socat or similar HTTP listener."
    echo "  socat TCP-LISTEN:8090,reuseaddr,fork EXEC:\"./ghl-webhook-handler.sh\""
    echo ""
    echo "Features:"
    echo "  - Parses GHL webhook JSON (first_name, last_name, email, phone, website)"
    echo "  - Deduplicates by slug and email across existing leads"
    echo "  - Rate limits to 10 leads/minute"
    echo "  - Optional webhook secret verification (set GHL_WEBHOOK_SECRET env var)"
    echo "  - Auto-scores leads into hot/warm/cold tiers"
    echo "  - Triggers full pipeline in background"
    echo ""
    echo "Environment:"
    echo "  GHL_WEBHOOK_SECRET  Optional shared secret for webhook verification"
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="$REPO_DIR/leads"
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LEADS_DIR" "$LOG_DIR"

# Read input — handles both raw JSON and HTTP POST format
BODY=$(cat)

# Webhook signature verification (optional shared secret)
# Set GHL_WEBHOOK_SECRET env var to enable. GHL sends it in X-Webhook-Secret header.
if [ -n "${GHL_WEBHOOK_SECRET:-}" ]; then
    INCOMING_SECRET=$(echo "$BODY" | head -20 | grep -i "x-webhook-secret:" | awk '{print $2}' | tr -d '\r\n' || echo "")
    if [ -n "$INCOMING_SECRET" ] && [ "$INCOMING_SECRET" != "$GHL_WEBHOOK_SECRET" ]; then
        echo "HTTP/1.1 401 Unauthorized"
        echo "Content-Type: application/json"
        echo ""
        echo '{"error":"invalid_webhook_secret"}'
        exit 1
    fi
fi

# If input starts with HTTP method, strip headers and extract body
if echo "$BODY" | head -1 | grep -qE '^(POST|GET|PUT) '; then
    BODY=$(echo "$BODY" | sed -n '/^$/,$p' | tail -n +2)
fi

# Trim leading/trailing whitespace only
BODY=$(echo "$BODY" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

# Parse JSON payload
if [ -z "$BODY" ]; then
    echo "HTTP/1.1 400 Bad Request"
    echo "Content-Type: application/json"
    echo ""
    echo '{"error":"empty payload"}'
    exit 1
fi

# Extract fields from GHL webhook JSON
LEAD_NAME=$(echo "$BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('first_name','')+ ' ' + d.get('last_name',''))" 2>/dev/null || echo "")
WEBSITE=$(echo "$BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('website', d.get('customField',{}).get('website','')))" 2>/dev/null || echo "")
EMAIL=$(echo "$BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('email',''))" 2>/dev/null || echo "")
PHONE=$(echo "$BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('phone',''))" 2>/dev/null || echo "")
CONTACT_ID=$(echo "$BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('contact_id', d.get('contactId','')))" 2>/dev/null || echo "")

LEAD_NAME=$(echo "$LEAD_NAME" | xargs) # trim whitespace

if [ -z "$LEAD_NAME" ] || [ "$LEAD_NAME" = " " ]; then
    echo "HTTP/1.1 400 Bad Request"
    echo "Content-Type: application/json"
    echo ""
    echo '{"error":"missing lead name"}'
    exit 1
fi

SLUG=$(echo "$LEAD_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
PROFILE="$LEADS_DIR/${SLUG}.json"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Rate limiting: max 10 leads per minute
RATE_FILE="$LOG_DIR/webhook-rate.tmp"
CURRENT_MINUTE=$(date +%Y%m%d%H%M)
RATE_COUNT=0
if [ -f "$RATE_FILE" ]; then
    STORED_MINUTE=$(head -1 "$RATE_FILE" 2>/dev/null || echo "")
    if [ "$STORED_MINUTE" = "$CURRENT_MINUTE" ]; then
        RATE_COUNT=$(tail -1 "$RATE_FILE" 2>/dev/null || echo "0")
        RATE_COUNT=$((RATE_COUNT + 0))  # ensure integer
    fi
fi
if [ "$RATE_COUNT" -ge 10 ]; then
    echo "HTTP/1.1 429 Too Many Requests"
    echo "Content-Type: application/json"
    echo ""
    echo "{\"error\":\"rate_limit\",\"message\":\"Max 10 leads/minute. Try again shortly.\",\"ts\":\"$TIMESTAMP\"}"
    echo "{\"ts\":\"$TIMESTAMP\",\"slug\":\"$SLUG\",\"action\":\"rate_limited\"}" >> "$LOG_DIR/ghl-webhook-intake.jsonl"
    exit 0
fi
# Update rate counter
printf '%s\n%s\n' "$CURRENT_MINUTE" "$((RATE_COUNT + 1))" > "$RATE_FILE"

# Log incoming webhook
echo "{\"ts\":\"$TIMESTAMP\",\"lead\":\"$LEAD_NAME\",\"slug\":\"$SLUG\",\"website\":\"$WEBSITE\",\"contact_id\":\"$CONTACT_ID\"}" >> "$LOG_DIR/ghl-webhook-intake.jsonl"

# Check if lead already exists (dedup by slug)
if [ -f "$PROFILE" ]; then
    echo "HTTP/1.1 200 OK"
    echo "Content-Type: application/json"
    echo ""
    echo "{\"status\":\"duplicate\",\"slug\":\"$SLUG\",\"existing_profile\":\"$PROFILE\"}"
    echo "{\"ts\":\"$TIMESTAMP\",\"slug\":\"$SLUG\",\"action\":\"dedup_skip_slug\"}" >> "$LOG_DIR/ghl-webhook-intake.jsonl"
    exit 0
fi

# Dedup by email across all existing leads
if [ -n "$EMAIL" ] && [ "$EMAIL" != "None" ] && [ "$EMAIL" != "" ]; then
    EXISTING_EMAIL=$(python3 -c "
import json, glob, sys
email = sys.argv[1]
leads_dir = sys.argv[2]
for f in glob.glob(leads_dir + '/*.json'):
    try:
        d = json.load(open(f))
        if d.get('email','').lower() == email.lower():
            print(f)
            break
    except: pass
" "$EMAIL" "$LEADS_DIR" 2>/dev/null || echo "")
    if [ -n "$EXISTING_EMAIL" ]; then
        echo "HTTP/1.1 200 OK"
        echo "Content-Type: application/json"
        echo ""
        echo "{\"status\":\"duplicate_email\",\"slug\":\"$SLUG\",\"existing\":\"$EXISTING_EMAIL\"}"
        echo "{\"ts\":\"$TIMESTAMP\",\"slug\":\"$SLUG\",\"action\":\"dedup_skip_email\",\"email\":\"$EMAIL\"}" >> "$LOG_DIR/ghl-webhook-intake.jsonl"
        exit 0
    fi
fi

# Stage 1: Generate lead profile via lead-intake.sh
if [ -n "$WEBSITE" ] && [ "$WEBSITE" != "None" ] && [ "$WEBSITE" != "" ]; then
    "$SCRIPT_DIR/lead-intake.sh" "$WEBSITE" "$LEAD_NAME" --output "$PROFILE" 2>&1 | tee -a "$LOG_DIR/ghl-webhook-intake.jsonl" || true
else
    # No website — create minimal profile
    python3 -c "
import json
profile = {
    'lead_name': '$LEAD_NAME',
    'lead_first_name': '$(echo "$LEAD_NAME" | awk "{print \$1}")',
    'business_name': '$LEAD_NAME',
    'slug': '$SLUG',
    'accent_color': '#2563EB',
    'industry': 'Unknown',
    'email': '$EMAIL',
    'phone': '$PHONE',
    'url': '',
    'ghl_contact_id': '$CONTACT_ID'
}
json.dump(profile, open('$PROFILE','w'), indent=2)
print('Minimal profile created (no website)')
"
fi

# Inject GHL contact ID + email into profile if not already present
python3 - "$PROFILE" "$CONTACT_ID" "$EMAIL" "$PHONE" <<'INJECT_PY'
import json, sys
profile_path, cid, email, phone = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
p = json.load(open(profile_path))
if cid: p['ghl_contact_id'] = cid
if email and not p.get('email'): p['email'] = email
if phone and not p.get('phone'): p['phone'] = phone
json.dump(p, open(profile_path, 'w'), indent=2)
INJECT_PY

# Auto-DQ Scoring — classify lead tier based on profile data
# Tier: hot (≥$1M rev signal), warm (has website + industry), cold (minimal data)
LEAD_TIER=$(python3 - "$PROFILE" <<'SCORE_PY'
import json, sys
profile_path = sys.argv[1]
p = json.load(open(profile_path))
score = 0
if p.get('url') and p['url'] not in ('', 'None'): score += 2
if p.get('industry') and p['industry'] not in ('Unknown', ''): score += 1
if p.get('email') and p['email'] not in ('', 'None'): score += 1
if p.get('phone') and p['phone'] not in ('', 'None'): score += 1
if p.get('ghl_contact_id') and p['ghl_contact_id'] not in ('', 'None'): score += 1
tier = 'cold'
if score >= 5: tier = 'hot'
elif score >= 3: tier = 'warm'
p['lead_score'] = score
p['lead_tier'] = tier
json.dump(p, open(profile_path, 'w'), indent=2)
print(tier)
SCORE_PY
2>/dev/null || echo "cold")

echo "{\"ts\":\"$TIMESTAMP\",\"slug\":\"$SLUG\",\"action\":\"scored\",\"tier\":\"$LEAD_TIER\"}" >> "$LOG_DIR/ghl-webhook-intake.jsonl"

# Stage 2-7: Run full pipeline via blueprint-batch.sh (single lead)
# Run in background so webhook responds immediately
nohup "$SCRIPT_DIR/blueprint-batch.sh" "$LEADS_DIR" --send-previews > "$LOG_DIR/blueprint-batch-${SLUG}-$(date +%Y%m%d%H%M).log" 2>&1 &
BATCH_PID=$!

# Respond to GHL
echo "HTTP/1.1 200 OK"
echo "Content-Type: application/json"
echo ""
echo "{\"status\":\"accepted\",\"slug\":\"$SLUG\",\"profile\":\"$PROFILE\",\"batch_pid\":$BATCH_PID}"

echo "{\"ts\":\"$TIMESTAMP\",\"slug\":\"$SLUG\",\"action\":\"pipeline_started\",\"pid\":$BATCH_PID}" >> "$LOG_DIR/ghl-webhook-intake.jsonl"
