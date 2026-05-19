#!/bin/bash
# Blueprint AI Pipeline — Stage 7: Build Delivery Email
# Usage: ./build-delivery-email.sh <lead-profile.json> [--send-preview]
#
# Reads lead profile, injects into delivery-email-template.html,
# outputs to ~/Desktop/<slug>-delivery-email.html
# With --send-preview: sends to bennett@franchiseki.com via gog

set -euo pipefail

# Ensure gog is in PATH (Homebrew install location)
export PATH="/opt/homebrew/bin:/opt/homebrew/Cellar/gogcli/0.13.0/bin:$PATH"

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
TEMPLATE_VARIANT=""
for arg in "${@:2}"; do
  case "$arg" in
    --send-preview) SEND_PREVIEW=true ;;
    --send-ghl) SEND_GHL=true ;;
    --template-b) TEMPLATE_VARIANT="b" ;;
    --template-c) TEMPLATE_VARIANT="c" ;;
    --force) ;; # handled later
  esac
done

# A/B test support: use variant template if specified and exists
if [ -n "$TEMPLATE_VARIANT" ]; then
    VARIANT_TEMPLATE="$SCRIPT_DIR/../templates/delivery-email-template-${TEMPLATE_VARIANT}.html"
    if [ -f "$VARIANT_TEMPLATE" ]; then
        TEMPLATE="$VARIANT_TEMPLATE"
        echo "Using template variant: $TEMPLATE_VARIANT"
    else
        echo "WARNING: Template variant '$TEMPLATE_VARIANT' not found at $VARIANT_TEMPLATE, using default"
    fi
fi

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
REPO_EMAIL="$(cd "$(dirname "$0")/.." && pwd)/delivery-emails/${SLUG}-delivery-email.html"

# Idempotency check: skip if output exists and is newer than the profile
if [ -f "$REPO_EMAIL" ] && [ "$REPO_EMAIL" -nt "$PROFILE" ]; then
    echo "SKIP: $REPO_EMAIL already exists and is newer than $PROFILE (idempotent)"
    echo "  Use --force to rebuild, or touch the profile to trigger rebuild."
    # Still check for --force flag
    FORCE=false
    for arg in "${@:2}"; do [ "$arg" = "--force" ] && FORCE=true; done
    if [ "$FORCE" = false ]; then
        exit 0
    fi
    echo "  --force specified, rebuilding..."
fi

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
# Inject build metadata
import datetime
build_ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
meta = f'<!-- Blueprint AI Pipeline v2.1 | Email Built: {build_ts} | Lead: {profile.get("lead_name","Unknown")} -->\n'
html = meta + html
with open(output_path, 'w') as f:
    f.write(html)
PYEOF

# Stamp email build timestamp into profile
python3 -c "
import json, sys, datetime
p = json.load(open(sys.argv[1]))
p['email_ts'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
json.dump(p, open(sys.argv[1], 'w'), indent=2)
" "$PROFILE" 2>/dev/null || true

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

# ============================================================
# HARD GATE: PODCAST + BENNETT-APPROVAL REQUIRED BEFORE SEND
# Bennett directive 2026-05-19 — never send to customer without both.
# ============================================================
if [ "$SEND_GHL" = true ]; then
    # Gate 1: Podcast URL must be non-empty and return HTTP 200
    if [ -z "$PODCAST_URL" ] || [ "$PODCAST_URL" = "" ]; then
        echo "BLOCKED: PODCAST_URL is empty. Cannot send to customer until podcast is live."
        echo "Run: ./build-delivery-email.sh $PROFILE --send-preview  (preview to bennett@ only)"
        mkdir -p ~/.openclaw/logs
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"lead\":\"$LEAD_NAME\",\"block\":\"empty_podcast_url\",\"profile\":\"$PROFILE\"}" >> ~/.openclaw/logs/blueprint-delivery-blocks.jsonl
        exit 1
    fi
    PODCAST_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$PODCAST_URL" 2>/dev/null || echo "000")
    if [ "$PODCAST_HTTP" != "200" ]; then
        echo "BLOCKED: podcast_url=$PODCAST_URL returned HTTP $PODCAST_HTTP (need 200)."
        echo "Podcast must be live before customer delivery."
        mkdir -p ~/.openclaw/logs
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"lead\":\"$LEAD_NAME\",\"block\":\"podcast_http_$PODCAST_HTTP\",\"url\":\"$PODCAST_URL\"}" >> ~/.openclaw/logs/blueprint-delivery-blocks.jsonl
        exit 1
    fi
    echo "Gate 1 PASS: podcast HTTP $PODCAST_HTTP"

    # Gate 2: Require --bennett-approved flag — Bennett must have reviewed the preview first
    BENNETT_APPROVED=false
    for arg in "${@:2}"; do [ "$arg" = "--bennett-approved" ] && BENNETT_APPROVED=true; done
    if [ "$BENNETT_APPROVED" = false ]; then
        echo "BLOCKED: --bennett-approved flag required. Process:"
        echo "  1. Run with --send-preview to send to bennett@franchiseki.com for review"
        echo "  2. Bennett approves (Notion checkbox or reply)"
        echo "  3. Re-run with --send-ghl --bennett-approved to deliver to customer"
        mkdir -p ~/.openclaw/logs
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"lead\":\"$LEAD_NAME\",\"block\":\"missing_bennett_approval\"}" >> ~/.openclaw/logs/blueprint-delivery-blocks.jsonl
        exit 1
    fi
    echo "Gate 2 PASS: bennett-approved flag present"
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
