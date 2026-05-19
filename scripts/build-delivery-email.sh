#!/bin/bash
# Blueprint AI Pipeline — Stage 7: Build Delivery Email
# Usage: ./build-delivery-email.sh <lead-profile.json> [--send-preview]
#
# Reads lead profile, injects into delivery-email-template.html,
# outputs to ~/Desktop/<slug>-delivery-email.html
# With --send-preview: sends to bennett@franchiseki.com via gog

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/delivery-email-template.html"

if [ $# -lt 1 ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 <lead-profile.json> [--send-preview]"
    echo ""
    echo "lead-profile.json must contain:"
    echo '  lead_name, lead_first_name, business_name, slug, accent_color,'
    echo '  industry, blueprint_url, podcast_url, website_url,'
    echo '  prompt_1, prompt_2, prompt_3'
    exit 1
fi

PROFILE="$1"
SEND_PREVIEW=false
SEND_GHL=false
for arg in "${@:2}"; do
  case "$arg" in
    --send-preview) SEND_PREVIEW=true ;;
    --send-ghl) SEND_GHL=true ;;
  esac
done

# Extract fields from JSON
get() { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else ''))" "$PROFILE" "$1" "${2:-}" ; }

LEAD_NAME=$(get lead_name "Unknown")
LEAD_FIRST=$(get lead_first_name "there")
BUSINESS_NAME=$(get business_name "Your Business")
SLUG=$(get slug "lead")
GHL_CONTACT_ID=$(get ghl_contact_id "")
ACCENT_COLOR=$(get accent_color "#007AFF")
INDUSTRY=$(get industry "business services")
BLUEPRINT_URL=$(get blueprint_url "")
PODCAST_URL=$(get podcast_url "")
WEBSITE_URL=$(get website_url "")
PROMPT_1=$(get prompt_1 "You are a speed-to-lead response agent for a $INDUSTRY business. When a new inquiry comes in, draft a personalized response within 60 seconds that acknowledges their specific request, highlights relevant services, and suggests a next step.")
PROMPT_2=$(get prompt_2 "You are a proposal draft agent for a $INDUSTRY business. Given a prospect's requirements, generate a professional proposal including scope, timeline, pricing framework, and 3 reasons to choose this business over competitors.")
PROMPT_3=$(get prompt_3 "You are an outreach agent for a $INDUSTRY business. Generate 5 personalized LinkedIn connection messages and 5 cold email templates targeting property managers and commercial building operators who need $INDUSTRY services.")
APPLY_SUBJECT=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1] + ' - Blueprint Application'))" "$LEAD_NAME")

OUTPUT="$HOME/Desktop/${SLUG}-delivery-email.html"

# Inject into template
cp "$TEMPLATE" "$OUTPUT"
sed -i '' "s|{{LEAD_FIRST_NAME}}|$LEAD_FIRST|g" "$OUTPUT"
sed -i '' "s|{{BUSINESS_NAME}}|$BUSINESS_NAME|g" "$OUTPUT"
sed -i '' "s|{{ACCENT_COLOR}}|$ACCENT_COLOR|g" "$OUTPUT"
sed -i '' "s|{{INDUSTRY}}|$INDUSTRY|g" "$OUTPUT"
sed -i '' "s|{{BLUEPRINT_URL}}|$BLUEPRINT_URL|g" "$OUTPUT"
sed -i '' "s|{{PODCAST_URL}}|$PODCAST_URL|g" "$OUTPUT"
sed -i '' "s|{{WEBSITE_URL}}|$WEBSITE_URL|g" "$OUTPUT"
sed -i '' "s|{{APPLY_SUBJECT}}|$APPLY_SUBJECT|g" "$OUTPUT"

# Prompts need python for multi-line safety
python3 - "$OUTPUT" "$PROFILE" "$INDUSTRY" << 'PYEOF'
import json, sys
output_path, profile_path, industry = sys.argv[1], sys.argv[2], sys.argv[3]
with open(output_path, 'r') as f:
    html = f.read()
profile = json.load(open(profile_path))
default_p1 = f"You are a speed-to-lead response agent for a {industry} business. When a new inquiry comes in, draft a personalized response within 60 seconds that acknowledges their specific request, highlights relevant services, and suggests a next step."
default_p2 = f"You are a proposal draft agent for a {industry} business. Given a prospect requirements, generate a professional proposal including scope, timeline, pricing framework, and 3 reasons to choose this business over competitors."
default_p3 = f"You are an outreach agent for a {industry} business. Generate 5 personalized LinkedIn connection messages and 5 cold email templates targeting ideal clients who need {industry} services."
html = html.replace('{{PROMPT_1}}', profile.get('prompt_1', default_p1))
html = html.replace('{{PROMPT_2}}', profile.get('prompt_2', default_p2))
html = html.replace('{{PROMPT_3}}', profile.get('prompt_3', default_p3))
html = html.replace('{{LEAD_NAME}}', profile.get('lead_name', 'Unknown'))
with open(output_path, 'w') as f:
    f.write(html)
PYEOF

echo "Built: $OUTPUT ($(wc -c < "$OUTPUT" | tr -d ' ') bytes)"

# Pre-delivery check on the email
BOOKING=$(grep -ci 'leadconnectorhq\|widget/booking' "$OUTPUT" 2>/dev/null || true)
BOOKING=${BOOKING:-0}
CALENDAR=$(grep -ci 'calendly\|cal\.com\|calendar\.google' "$OUTPUT" 2>/dev/null || true)
CALENDAR=${CALENDAR:-0}
APPLY=$(grep -ci 'apply' "$OUTPUT" 2>/dev/null || true)
APPLY=${APPLY:-0}

if [ "$BOOKING" -gt 0 ] || [ "$CALENDAR" -gt 0 ] || [ "$APPLY" -lt 1 ]; then
    echo "FAIL: booking=$BOOKING calendar=$CALENDAR apply=$APPLY"
    exit 1
fi
echo "Pre-delivery: PASS (booking=0 calendar=0 apply=$APPLY)"

# Send preview via Gmail (to Bennett for review)
if [ "$SEND_PREVIEW" = true ]; then
    echo "Sending preview to bennett@franchiseki.com via Gmail..."
    gog gmail send \
        --to=bennett@franchiseki.com \
        --subject="PREVIEW: $LEAD_NAME Blueprint Delivery Email" \
        --body-html="$(cat "$OUTPUT")" \
        --no-input 2>&1 | tail -2
fi

# Send via GHL conversations API (primary delivery to lead)
if [ "$SEND_GHL" = true ]; then
    LEAD_EMAIL=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('email',''))" "$PROFILE")
    GHL_CID=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('ghl_contact_id',''))" "$PROFILE")

    if [ -n "$GHL_CID" ] && [ "$GHL_CID" != "None" ] && [ "$GHL_CID" != "" ]; then
        echo "Sending via GHL conversations API (contactId=$GHL_CID)..."
        source ~/Agent\ SDK/.env 2>/dev/null
        python3 -c "
import json, sys
with open(sys.argv[1]) as f: html = f.read()
payload = {
    'type': 'Email',
    'contactId': sys.argv[2],
    'subject': sys.argv[3] + ' - Your Custom Blueprint is Ready',
    'html': html
}
if sys.argv[4]: payload['emailTo'] = sys.argv[4]
print(json.dumps(payload))
" "$OUTPUT" "$GHL_CID" "$BUSINESS_NAME" "$LEAD_EMAIL" > /tmp/ghl-delivery-payload.json

        GHL_RESULT=$(curl -s -X POST 'https://services.leadconnectorhq.com/conversations/messages' \
            -H "Authorization: Bearer $GHL_API_KEY" \
            -H 'Version: 2021-07-28' \
            -H 'Content-Type: application/json' \
            -d @/tmp/ghl-delivery-payload.json 2>&1)
        GHL_MSG_ID=$(echo "$GHL_RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('messageId',d.get('id','FAILED')))" 2>/dev/null || echo "FAILED")
        echo "GHL send: msgId=$GHL_MSG_ID"
        rm -f /tmp/ghl-delivery-payload.json
    elif [ -n "$LEAD_EMAIL" ] && [ "$LEAD_EMAIL" != "None" ] && [ "$LEAD_EMAIL" != "" ]; then
        echo "No GHL contact ID — falling back to Gmail for $LEAD_EMAIL..."
        gog gmail send \
            --to="$LEAD_EMAIL" \
            --subject="$BUSINESS_NAME - Your Custom Blueprint is Ready" \
            --body-html="$(cat "$OUTPUT")" \
            --no-input 2>&1 | tail -2
    else
        echo "SKIP: No email or GHL contact ID in profile"
    fi
fi

echo "Done."
