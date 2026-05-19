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

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="$REPO_DIR/leads"
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LEADS_DIR" "$LOG_DIR"

# Read HTTP POST body from stdin
BODY=""
content_length=0
while IFS= read -r line; do
    # Skip HTTP headers, find Content-Length
    line=$(echo "$line" | tr -d '\r')
    [ -z "$line" ] && break
    case "$line" in
        Content-Length:*|content-length:*) content_length=$(echo "$line" | awk '{print $2}');;
    esac
done

if [ "$content_length" -gt 0 ] 2>/dev/null; then
    BODY=$(head -c "$content_length")
else
    BODY=$(cat)
fi

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

# Log incoming webhook
echo "{\"ts\":\"$TIMESTAMP\",\"lead\":\"$LEAD_NAME\",\"slug\":\"$SLUG\",\"website\":\"$WEBSITE\",\"contact_id\":\"$CONTACT_ID\"}" >> "$LOG_DIR/ghl-webhook-intake.jsonl"

# Check if lead already exists (dedup)
if [ -f "$PROFILE" ]; then
    echo "HTTP/1.1 200 OK"
    echo "Content-Type: application/json"
    echo ""
    echo "{\"status\":\"duplicate\",\"slug\":\"$SLUG\",\"existing_profile\":\"$PROFILE\"}"
    echo "{\"ts\":\"$TIMESTAMP\",\"slug\":\"$SLUG\",\"action\":\"dedup_skip\"}" >> "$LOG_DIR/ghl-webhook-intake.jsonl"
    exit 0
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
python3 -c "
import json
p = json.load(open('$PROFILE'))
if '$CONTACT_ID': p['ghl_contact_id'] = '$CONTACT_ID'
if '$EMAIL' and not p.get('email'): p['email'] = '$EMAIL'
if '$PHONE' and not p.get('phone'): p['phone'] = '$PHONE'
json.dump(p, open('$PROFILE','w'), indent=2)
"

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
