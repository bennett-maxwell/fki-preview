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
DEFAULT_BLUEPRINT_BASE_URL="https://hub.aiblueprintmarketing.com"
BLUEPRINT_BASE_URL="${BLUEPRINT_BASE_URL:-$DEFAULT_BLUEPRINT_BASE_URL}"
BLUEPRINT_BASE_URL="${BLUEPRINT_BASE_URL%/}"

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
GATE_TOKEN=""
FORCE=false
EXTRA_ARGS=("${@:2}")
i=0
while [ "$i" -lt "${#EXTRA_ARGS[@]}" ]; do
  arg="${EXTRA_ARGS[$i]}"
  case "$arg" in
    --send-preview) SEND_PREVIEW=true ;;
    --send-ghl) SEND_GHL=true ;;
    --template-b) TEMPLATE_VARIANT="b" ;;
    --template-c) TEMPLATE_VARIANT="c" ;;
    --gate-token)
      i=$((i + 1))
      GATE_TOKEN="${EXTRA_ARGS[$i]:-}"
      ;;
    --force) FORCE=true ;;
  esac
  i=$((i + 1))
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
# Email-safe industry: the template appends " businesses" after {{INDUSTRY}}, so an
# industry value that already ends in "business/businesses" doubles ("... businesses businesses").
# Strip a trailing business/businesses for email copy only (blueprint industry untouched).
EMAIL_INDUSTRY=$(python3 -c "import re,sys; print(re.sub(r'\s+business(es)?\s*$','',sys.argv[1]).strip() or sys.argv[1])" "$INDUSTRY")
BLUEPRINT_URL=$(get blueprint_url "")
PODCAST_URL=$(get podcast_url "")
WEBSITE_URL=$(get website_url "")
if [[ "$BLUEPRINT_BASE_URL" != "$DEFAULT_BLUEPRINT_BASE_URL" ]]; then
  if [[ -z "$BLUEPRINT_URL" || "$BLUEPRINT_URL" == "$DEFAULT_BLUEPRINT_BASE_URL"* ]]; then
    BLUEPRINT_URL="$BLUEPRINT_BASE_URL/blueprints/$SLUG.html"
  fi
  if [[ -z "$PODCAST_URL" || "$PODCAST_URL" == "$DEFAULT_BLUEPRINT_BASE_URL"* ]]; then
    PODCAST_URL="$BLUEPRINT_BASE_URL/podcasts/$SLUG.mp3"
  fi
fi
# BARE-HREF RULE (Madison 2026-07-02): Gmail throws the "Redirect Notice" interstitial
# on any link carrying a query string / UTM / fragment; a bare canonical URL
# (scheme+host+path only) opens directly on first click. So NO tracking params are
# appended to the blueprint URL. (Previously slug=/cid= were appended for a
# blueprint_viewed relay; that broke first-click open and is retired here.)
# Strip any pre-existing query string / fragment the profile may carry.
BLUEPRINT_URL="${BLUEPRINT_URL%%\?*}"
BLUEPRINT_URL="${BLUEPRINT_URL%%#*}"
PROMPT_1=$(get prompt_1 "You are a speed-to-lead response agent for a $INDUSTRY business. When a new inquiry comes in, draft a personalized response within 60 seconds that acknowledges their specific request, highlights relevant services, and suggests a next step.")
PROMPT_2=$(get prompt_2 "You are a proposal draft agent for a $INDUSTRY business. Given a prospect's requirements, generate a professional proposal including scope, timeline, pricing framework, and 3 reasons to choose this business over competitors.")
PROMPT_3=$(get prompt_3 "You are an outreach agent for a $INDUSTRY business. Generate 5 personalized LinkedIn connection messages and 5 cold email templates targeting property managers and commercial building operators who need $INDUSTRY services.")
QUALIFIER_AGENTS=$(python3 "$SCRIPT_DIR/blueprint_q7_agents.py" "$PROFILE" --slug "$SLUG")
APPLY_SUBJECT=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1] + ' - Blueprint Application'))" "$LEAD_NAME")
APPLY_URL="$BLUEPRINT_BASE_URL/apply/?lead=$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))' "$LEAD_NAME")&biz=$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))' "$BUSINESS_NAME")&src=$SLUG"
# Canonical CTA target is qualify.html (bennett-rule: "See If You Qualify" -> qualify.html ONLY).
# Read ONLY a dedicated qualify_url field — NEVER seed from apply_url. apply/ is a
# different page; seeding QUALIFY_URL from apply_url made the "See If You Qualify"
# button point to apply/, violating the bennett-rule (brent-attaway defect 2026-06-01).
# Empty default => the python block below falls back to the canonical qualify.html.
PROFILE_QUALIFY_URL=$(get qualify_url "")
# BARE-HREF RULE (Madison 2026-07-02): the qualifier CTA must be a BARE canonical URL
# (scheme+host+path only) so Gmail opens it directly on first click instead of showing
# the "Redirect Notice" interstitial. The old build appended
# ?lead=&biz=&src=&utm_*&contactId=&agents= — a big query string that reliably tripped
# the interstitial. We DROP every query param and fragment here. Identity pre-fill is
# sacrificed in favor of "opens directly on first click" (Madison's explicit priority).
QUALIFY_URL=$(python3 - "$PROFILE_QUALIFY_URL" "$BLUEPRINT_BASE_URL" << 'PYEOF'
import sys
from urllib.parse import urlsplit, urlunsplit

profile_url, base_url = sys.argv[1:3]
DEFAULT_BASE_URL = "https://hub.aiblueprintmarketing.com"
base_url = base_url.rstrip("/") or DEFAULT_BASE_URL
if base_url != DEFAULT_BASE_URL and (not profile_url or profile_url.startswith(DEFAULT_BASE_URL)):
    url = f"{base_url}/qualify.html"
else:
    url = profile_url or f"{base_url}/qualify.html"
parts = urlsplit(url)
if not parts.scheme:
    parts = urlsplit(f"{base_url}/qualify.html")
fallback_path = urlsplit(f"{base_url}/qualify.html").path or "/qualify.html"
# scheme+host+path ONLY — no query, no fragment.
print(urlunsplit((parts.scheme, parts.netloc, parts.path or fallback_path, "", "")))
PYEOF
)
# Belt-and-suspenders: strip any query/fragment off podcast + website URLs too.
PODCAST_URL="${PODCAST_URL%%\?*}"; PODCAST_URL="${PODCAST_URL%%#*}"
WEBSITE_URL="${WEBSITE_URL%%\?*}"; WEBSITE_URL="${WEBSITE_URL%%#*}"

OUTPUT="$HOME/Desktop/${SLUG}-delivery-email.html"
REPO_EMAIL="$(cd "$(dirname "$0")/.." && pwd)/delivery-emails/${SLUG}-delivery-email.html"

# v3.26 ZERO-BYPASS AUDIT GATE: blueprint-ai-audit-skill must have run THIS session
# with score=100/100 before any Stage 7 email action. No session-memory exception.
check_session_audit_ts() {
    local TS_FILE="$HOME/.openclaw/state/session-audit-ts-${SLUG}.json"
    if [ ! -f "$TS_FILE" ]; then
        echo "BLOCKED (v3.26 zero-bypass): blueprint-ai-audit-skill has NOT run this session for $SLUG."
        echo "  Run audit: python3 scripts/blueprint_completion_gate.py --html blueprints/$SLUG.html --receipt-dir <dir> --lead $SLUG"
        echo "  Then: echo '{\"ts\":'$(date +%s)',\"slug\":\"$SLUG\",\"score\":100}' > $TS_FILE"
        exit 1
    fi
    local AGE; AGE=$(python3 -c "import json,time; d=json.load(open('$TS_FILE')); print(int(time.time()-d.get('ts',0)))" 2>/dev/null || echo 99999)
    if [ "$AGE" -gt 3600 ]; then
        echo "BLOCKED (v3.26 zero-bypass): audit receipt is ${AGE}s old (>3600s limit). Re-run audit for $SLUG."
        exit 1
    fi
    local SCORE; SCORE=$(python3 -c "import json; d=json.load(open('$TS_FILE')); print(d.get('score',0))" 2>/dev/null || echo 0)
    if [ "$SCORE" -lt 100 ]; then
        echo "BLOCKED (v3.26 zero-bypass): audit score was ${SCORE}/100 (must be 100/100) for $SLUG."
        exit 1
    fi
    echo "Session audit gate: PASS (score=${SCORE} ran ${AGE}s ago)"
}

verify_gate_token() {
    if [ -z "$GATE_TOKEN" ]; then
        echo "BLOCKED: --gate-token is required before any Bennett preview or customer send."
        echo "Run production Gatekeeper first:"
        echo "  python3 scripts/blueprint_gatekeeper_100.py --mode production --lead $SLUG --html blueprints/$SLUG.html --receipt-dir <receipts>"
        exit 1
    fi
    if [ ! -f "$GATE_TOKEN" ]; then
        echo "BLOCKED: gate token not found: $GATE_TOKEN"
        exit 1
    fi
    TOKEN_CHECK="/tmp/${SLUG}-gate-token-check.json"
    if ! python3 "$SCRIPT_DIR/blueprint_gatekeeper_100.py" \
        --verify-token \
        --mode production \
        --lead "$SLUG" \
        --html "blueprints/$SLUG.html" \
        --delivery-email "$REPO_EMAIL" \
        --profile "$PROFILE" \
        --receipt-dir "$(dirname "$GATE_TOKEN")" \
        --token "$GATE_TOKEN" \
        --json-output > "$TOKEN_CHECK"; then
        echo "BLOCKED: gate token is invalid."
        cat "$TOKEN_CHECK"
        exit 1
    fi
    echo "Gatekeeper token PASS: $GATE_TOKEN"
}

REUSE_EXISTING=false

# Idempotency check: once a Gatekeeper token exists, do not rewrite the email or
# profile timestamp before send. The token is hash-bound to the exact artifacts.
if [ -n "$GATE_TOKEN" ] && [ -f "$REPO_EMAIL" ] && [ "$FORCE" = false ]; then
    echo "REUSE: gate token supplied; using existing hash-bound email artifact"
    cp "$REPO_EMAIL" "$OUTPUT"
    REUSE_EXISTING=true
    echo "Desktop copy refreshed: $OUTPUT ($(wc -c < "$OUTPUT" | tr -d ' ') bytes)"
elif [ -f "$REPO_EMAIL" ] && [ "$REPO_EMAIL" -nt "$PROFILE" ]; then
    echo "REUSE: $REPO_EMAIL already exists and is newer than $PROFILE (idempotent)"
    echo "  Use --force to rebuild, or touch the profile to trigger rebuild."
    if [ "$FORCE" = false ]; then
        cp "$REPO_EMAIL" "$OUTPUT"
        REUSE_EXISTING=true
        echo "Desktop copy refreshed: $OUTPUT ($(wc -c < "$OUTPUT" | tr -d ' ') bytes)"
    else
        echo "  --force specified, rebuilding..."
    fi
fi

# Inject into template
if [ "$REUSE_EXISTING" = false ]; then
cp "$TEMPLATE" "$OUTPUT"
# & is the whole-match operator in a sed RHS — any value carrying a literal & (e.g.
# industry "Photography & Video", or a URL query string) corrupts its own token and
# leaves it unrendered. Escape & in every free-text/URL replacement value, not just
# the qualify URL. (2026-06-02 — rush-evans D5-20 regression caught by the HARD gate.)
sed_esc() { printf '%s' "$1" | sed 's/&/\\&/g'; }
sed -i '' "s|{{LEAD_FIRST_NAME}}|$(sed_esc "$LEAD_FIRST")|g" "$OUTPUT"
sed -i '' "s|{{BUSINESS_NAME}}|$(sed_esc "$BUSINESS_NAME")|g" "$OUTPUT"
sed -i '' "s|{{ACCENT_COLOR}}|$ACCENT_COLOR|g" "$OUTPUT"
sed -i '' "s|{{INDUSTRY}}|$(sed_esc "$EMAIL_INDUSTRY")|g" "$OUTPUT"
sed -i '' "s|{{BLUEPRINT_URL}}|$(sed_esc "$BLUEPRINT_URL")|g" "$OUTPUT"
sed -i '' "s|{{PODCAST_URL}}|$(sed_esc "$PODCAST_URL")|g" "$OUTPUT"
sed -i '' "s|{{WEBSITE_URL}}|$(sed_esc "$WEBSITE_URL")|g" "$OUTPUT"
sed -i '' "s|{{APPLY_SUBJECT}}|$(sed_esc "$APPLY_SUBJECT")|g" "$OUTPUT"
sed -i '' "s|{{APPLY_URL}}|$(sed_esc "$APPLY_URL")|g" "$OUTPUT"
sed -i '' "s|{{QUALIFY_URL}}|$(sed_esc "$QUALIFY_URL")|g" "$OUTPUT"

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
# Customer-view email must start with <!DOCTYPE html>; do not prepend build
# metadata comments because Gmail snippets/forwarded previews can expose them.
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
mkdir -p "$(dirname "$REPO_EMAIL")"
cp "$OUTPUT" "$REPO_EMAIL"
echo "Repo copy: $REPO_EMAIL ($(wc -c < "$REPO_EMAIL" | tr -d ' ') bytes)"
fi

# Pre-delivery check on the email
BOOKING=$(grep -ci 'leadconnectorhq\|widget/booking' "$OUTPUT" 2>/dev/null || true)
BOOKING=${BOOKING:-0}
CALENDAR=$(grep -ci 'calendly\|cal\.com\|calendar\.google' "$OUTPUT" 2>/dev/null || true)
CALENDAR=${CALENDAR:-0}
# Conversion-CTA gate: the canonical CTA target is qualify.html (bennett-rule), but a
# legacy email may still route to apply/. Accept either so the gate verifies "a
# conversion CTA exists" without forcing the apply/ link the bennett-rule forbids.
CTA=$(grep -ci 'qualify\|apply' "$OUTPUT" 2>/dev/null || true)
CTA=${CTA:-0}

if [ "$BOOKING" -gt 0 ] || [ "$CALENDAR" -gt 0 ] || [ "$CTA" -lt 1 ]; then
    echo "FAIL: booking=$BOOKING calendar=$CALENDAR cta=$CTA"
    exit 1
fi
echo "Pre-delivery: PASS (booking=0 calendar=0 cta=$CTA)"

# BARE-HREF GATE (Madison 2026-07-02): FAIL the build if ANY href carries a query
# string ("?"), so no generated delivery email can ever ship a link that trips Gmail's
# "Redirect Notice" interstitial. Bare canonical URLs (scheme+host+path) open directly.
BAD_HREFS=$(grep -oE 'href="[^"]*\?[^"]*"' "$OUTPUT" 2>/dev/null || true)
if [ -n "$BAD_HREFS" ]; then
    echo "FAIL (bare-href gate): delivery email contains href(s) with a query string:"
    echo "$BAD_HREFS"
    echo "  Every CTA link must be a bare canonical URL (scheme+host+path only) — no ?query, no #fragment, no UTM."
    exit 1
fi
echo "Bare-href gate: PASS (zero '?' in any href)"

# Conformance gate at generation time (D5-16..D5-23 incl. flexbox/style/white-template).
# HARD on the fresh-template path: the canonical template passes all 8, so a legit
# fresh build never blocks — only genuine off-template drift fails and aborts the build
# before it can reach a customer's Outlook inbox. REUSE path stays a non-fatal WARN
# because it copies a gate-token-bound / already-approved artifact (incl. the legacy
# delivery-emails still pending regeneration); blocking those would break idempotent
# re-sends. Once the legacy folder is regenerated from the template, all paths pass.
if [ -f "$SCRIPT_DIR/email-design-conformance.py" ]; then
    if python3 "$SCRIPT_DIR/email-design-conformance.py" "$OUTPUT" >/dev/null 2>&1; then
        echo "Conformance: PASS (D5-16..D5-23)"
    elif [ "$REUSE_EXISTING" = true ]; then
        echo "Conformance: WARN — reused artifact failed D5-16..D5-23 (review before send):"
        python3 "$SCRIPT_DIR/email-design-conformance.py" "$OUTPUT" 2>&1 | grep '\[FAIL\]' || true
    else
        echo "Conformance: FAIL — fresh-template email failed D5-16..D5-23 (build aborted):"
        python3 "$SCRIPT_DIR/email-design-conformance.py" "$OUTPUT" 2>&1 | grep '\[FAIL\]' || true
        echo "  This means the template drifted off-spec. Fix templates/delivery-email-template.html before building."
        exit 1
    fi
fi


# Customer-view approval gate: this artifact may be sent to Bennett for approval,
# but it must look like the customer email, not an internal proof memo.
if [ -f "$SCRIPT_DIR/blueprint_approval_email_gate.py" ]; then
    python3 "$SCRIPT_DIR/blueprint_approval_email_gate.py" --email "$OUTPUT" --profile "$PROFILE" --subject "$BUSINESS_NAME - Your Custom Blueprint is Ready" >/tmp/${SLUG}-approval-email-gate.json
    echo "Approval email gate: PASS (customer-view body)"
fi
if [ -f "$SCRIPT_DIR/blueprint_email_visual_gate.py" ]; then
    python3 "$SCRIPT_DIR/blueprint_email_visual_gate.py" --email "$OUTPUT" --subject "CUSTOMER VIEW PREVIEW: $BUSINESS_NAME - Your Custom Blueprint is Ready" --json-output >/tmp/${SLUG}-email-visual-gate.json
    echo "Email visual gate: PASS (customer-view format)"
fi
if [ -f "$SCRIPT_DIR/blueprint_qualifier_context_gate.py" ]; then
    python3 "$SCRIPT_DIR/blueprint_qualifier_context_gate.py" --html "blueprints/$SLUG.html" --delivery-email "$REPO_EMAIL" --profile "$PROFILE" --lead "$SLUG" --json-output >/tmp/${SLUG}-qualifier-context-gate.json
    echo "Qualifier context gate: PASS (tailored Q7 links)"
fi

# Send preview via Gmail (to Bennett for review)
if [ "$SEND_PREVIEW" = true ]; then
    check_session_audit_ts
    verify_gate_token
    echo "Sending preview to bennett@franchiseki.com via Gmail..."
    SEND_LOG="/tmp/${SLUG}-bennett-preview-send.log"
    if ! gog gmail send \
        --to=bennett@franchiseki.com \
        --cc=madison@franchiseki.com \
        --subject="CUSTOMER VIEW PREVIEW: $BUSINESS_NAME - Your Custom Blueprint is Ready" \
        --body-html="$(cat "$OUTPUT")" \
        --no-input > "$SEND_LOG" 2>&1; then
        cat "$SEND_LOG"
        exit 1
    fi
    tail -2 "$SEND_LOG"
    RECEIPT_DIR=$(python3 - "$GATE_TOKEN" << 'PYEOF'
import json, sys
data = json.load(open(sys.argv[1]))
token = data.get("pass_token", data)
print(token.get("receipt_dir") or "audit-receipts")
PYEOF
)
    PREVIEW_RECEIPT="$RECEIPT_DIR/${SLUG}-bennett-preview-send.json"
    python3 - "$SEND_LOG" "$PREVIEW_RECEIPT" "$SLUG" "$GATE_TOKEN" "$OUTPUT" "$REPO_EMAIL" << 'PYEOF'
import hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

log_path, receipt_path, slug, token_path, output_path, repo_email = sys.argv[1:7]
text = Path(log_path).read_text(encoding="utf-8", errors="replace")
def pick(patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1)
    return ""
def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
message_id = pick([r"message[_ -]?id['\"']?\s*[:=]\s*['\"']?([A-Za-z0-9._:-]+)", r"\bmessage_id\s+([A-Za-z0-9._:-]+)"])
thread_id = pick([r"thread[_ -]?id['\"']?\s*[:=]\s*['\"']?([A-Za-z0-9._:-]+)", r"\bthread_id\s+([A-Za-z0-9._:-]+)"])
receipt = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "lead": slug,
    "pass": True,
    "status": "PASS",
    "to": "bennett@franchiseki.com",
    "cc": "madison@franchiseki.com",
    "external_customer_send": False,
    "approval_scope": "bennett_preview_only",
    "gate_token": str(Path(token_path).resolve()),
    "email_sha256": sha(output_path),
    "repo_email_sha256": sha(repo_email),
    "gmail_message_id": message_id,
    "gmail_thread_id": thread_id,
    "raw_output_tail": text.strip().splitlines()[-5:],
}
Path(receipt_path).parent.mkdir(parents=True, exist_ok=True)
Path(receipt_path).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"Preview receipt: {receipt_path}")
PYEOF
fi

# ============================================================
# HARD GATE: PODCAST + BENNETT-APPROVAL REQUIRED BEFORE SEND
# Bennett directive 2026-05-19 — never send to customer without both.
# ============================================================
if [ "$SEND_GHL" = true ]; then
    check_session_audit_ts
    verify_gate_token
    if ! python3 - "$GATE_TOKEN" << 'PYEOF'
import json, sys
data = json.load(open(sys.argv[1]))
token = data.get("pass_token", data)
actions = token.get("allowed_actions", [])
sys.exit(0 if "external_send" in actions else 1)
PYEOF
    then
        echo "BLOCKED: gate token allows Bennett preview only. Regenerate after Bennett approval before customer send."
        exit 1
    fi
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

    echo "Gate 2 PASS: external_send is present in the Gatekeeper token"
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
    'html': html,
    'cc': ['bennett@franchiseki.com'],
    'bcc': ['madison@franchiseki.com', 'brent@franchiseki.com']
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
            --cc=bennett@franchiseki.com \
            --bcc=madison@franchiseki.com,brent@franchiseki.com \
            --no-input 2>&1 | tail -2
    else
        echo "SKIP: No email or GHL contact ID in profile"
    fi
fi

echo "Done."
