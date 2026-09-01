#!/usr/bin/env bash
# clone-blueprint.sh — Build a Blueprint from clean TEMPLATE.html using lead profile data.
# Takes a lead-profile.json, performs all replacements, outputs to blueprints/<slug>.html,
# runs pre-delivery checks, commits, pushes, and verifies HTTP 200.
#
# Usage:
#   ./scripts/clone-blueprint.sh path/to/lead-profile.json
#   ./scripts/clone-blueprint.sh --help
#
# lead-profile.json schema:
#   {
#     "lead_name": "Court Lundberg",
#     "business_name": "Lundberg Properties",
#     "accent_color": "#2E7D32",
#     "industry": "real estate",
#     "phone": "555-123-4567",
#     "email": "court@lundbergproperties.com",
#     "services": ["Residential Sales", "Commercial Leasing", "Property Management"],
#     "ai_agents": [
#       {"name": "Speed-to-Lead Agent", "desc": "Instant response to property inquiries", "prompt": "You are...", "result": "Every inquiry answered in minutes", "time": "5 minutes"},
#       {"name": "Follow-Up Nurture Agent", "desc": "7-touch sequence for warm leads", "prompt": "You are...", "result": "Recovers 15-20% of lost leads", "time": "7 minutes"},
#       {"name": "Past Client Reactivation Agent", "desc": "Re-engage past buyers for referrals", "prompt": "You are...", "result": "Reactivates past clients at $0 ad spend", "time": "5 minutes"},
#       {"name": "Content Engine Agent", "desc": "Turn listings into social content", "prompt": "You are...", "result": "6+ hours/week saved on content", "time": "5 minutes"},
#       {"name": "SEO Optimization Agent", "desc": "Optimize listings for local search", "prompt": "You are...", "result": "Increased organic traffic", "time": "10 minutes"},
#       {"name": "Admin Automation Agent", "desc": "Automate contracts and scheduling", "prompt": "You are...", "result": "Eliminates manual admin overhead", "time": "5 minutes"}
#     ]
#   }
#
# Rules enforced:
#   - ALWAYS builds from clean TEMPLATE.html (zero business-specific content in template)
#   - All lead data comes from profile JSON (stats, name, business, industry, services)
#   - CTA = "See If You Qualify" with lead-specific params into the tracked qualifier
#   - 3/7/30 onboarding timeline (NOT 90-day)
#   - Interactive ROI calculator only (no hardcoded dollar predictions)
#   - NO direct booking URLs in blueprint pages; booking opens only after tracked qualifier submit
#   - Post-build contamination check: FAILS if Brittney/Warnick/wedding content detected
#
# Requirements: bash 4+, python3, jq, git, curl

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="$REPO_ROOT/blueprints/TEMPLATE.html"
BLUEPRINTS_DIR="$REPO_ROOT/blueprints"
BLUEPRINT_BASE_URL="${BLUEPRINT_BASE_URL:-https://bennett-maxwell.github.io/fki-preview}"
BLUEPRINT_BASE_URL="${BLUEPRINT_BASE_URL%/}"
GITHUB_PAGES_BASE="$BLUEPRINT_BASE_URL/blueprints"

# ─── Help ───────────────────────────────────────────────────────────────────
usage() {
  cat <<'HELP'
clone-blueprint.sh -- Clone the v7 Blueprint frame for a new lead.

USAGE:
  ./scripts/clone-blueprint.sh <lead-profile.json>
  ./scripts/clone-blueprint.sh --help

ARGUMENTS:
  lead-profile.json   Path to a JSON file with the lead profile.
                      See header comment in this script for the full schema.

OPTIONS:
  --help              Show this help message and exit.
  --dry-run           Generate the HTML but skip git commit/push and HTTP verify.
  --no-commit         Generate the HTML but skip git commit/push and HTTP verify.
  --no-push           Generate and commit but skip push and HTTP verify.

WHAT IT DOES:
  1. Copies clean TEMPLATE.html (zero business-specific content)
  2. Fills all {{PLACEHOLDER}} tokens from lead profile JSON
  3. Outputs to blueprints/<lead-slug>.html
  4. Runs pre-delivery-check.sh if it exists
  5. Commits and pushes to origin
  6. Verifies HTTP 200 on the live GitHub Pages URL

RULES ENFORCED:
  - Builds from clean TEMPLATE.html (no business-specific content in base)
  - All data comes from lead profile JSON (zero hallucinated stats)
  - CTA = "See If You Qualify" (tracked qualifier URL, no direct booking URLs)
  - 3/7/30 onboarding timeline (not 90-day)
  - Interactive ROI calculator (no hardcoded dollar predictions)
  - Post-build contamination check catches any template leakage
HELP
  exit 0
}

# ─── Arg parsing ────────────────────────────────────────────────────────────
DRY_RUN=false
NO_COMMIT=false
NO_PUSH=false
NO_COMMIT=false
PROFILE_JSON=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage ;;
    --dry-run) DRY_RUN=true; shift ;;
    --no-commit) NO_COMMIT=true; shift ;;
    --no-push) NO_PUSH=true; shift ;;
    --no-commit) NO_COMMIT=true; NO_PUSH=true; shift ;;
    -*) echo "ERROR: Unknown option: $1" >&2; exit 1 ;;
    *) PROFILE_JSON="$1"; shift ;;
  esac
done

if [[ -z "$PROFILE_JSON" ]]; then
  echo "ERROR: No lead-profile.json provided." >&2
  echo "Run with --help for usage." >&2
  exit 1
fi

if [[ ! -f "$PROFILE_JSON" ]]; then
  echo "ERROR: File not found: $PROFILE_JSON" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required but not found. Install with: brew install jq" >&2
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 is required but not found." >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "ERROR: Template not found at $TEMPLATE" >&2
  echo "TEMPLATE.html must exist in blueprints/ directory." >&2
  exit 1
fi

# ─── Extract fields from JSON ──────────────────────────────────────────────
LEAD_NAME=$(jq -r '.lead_name' "$PROFILE_JSON")
BUSINESS_NAME=$(jq -r '.business_name' "$PROFILE_JSON")
ACCENT_COLOR=$(jq -r '.accent_color // "#B75E42"' "$PROFILE_JSON")
INDUSTRY=$(jq -r '.industry // "professional services"' "$PROFILE_JSON")
PHONE=$(jq -r '.phone // ""' "$PROFILE_JSON")
EMAIL=$(jq -r '.email // ""' "$PROFILE_JSON")

if [[ "$LEAD_NAME" == "null" || -z "$LEAD_NAME" ]]; then
  echo "ERROR: lead_name is required in the profile JSON." >&2
  exit 1
fi
if [[ "$BUSINESS_NAME" == "null" || -z "$BUSINESS_NAME" ]]; then
  echo "ERROR: business_name is required in the profile JSON." >&2
  exit 1
fi

# Slug: honor explicit profile.slug (canonical filename); else derive from lead name.
PROFILE_SLUG=$(jq -r '.slug // empty' "$PROFILE_JSON")
if [[ -n "$PROFILE_SLUG" && "$PROFILE_SLUG" != "null" ]]; then
  LEAD_SLUG="$PROFILE_SLUG"
else
  LEAD_SLUG=$(echo "$LEAD_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
fi
OUTPUT_FILE="$BLUEPRINTS_DIR/$LEAD_SLUG.html"

echo "=== Blueprint Clone ==="
echo "  Lead:     $LEAD_NAME"
echo "  Business: $BUSINESS_NAME"
echo "  Industry: $INDUSTRY"
echo "  Color:    $ACCENT_COLOR"
echo "  Slug:     $LEAD_SLUG"
echo "  Output:   $OUTPUT_FILE"
echo ""

# ─── Step 1: Copy template ─────────────────────────────────────────────────
echo "[1/7] Copying v7 frame template..."
cp "$TEMPLATE" "$OUTPUT_FILE"

# ─── Step 2: Run python3 replacement engine ─────────────────────────────────
echo "[2/7] Running replacement engine..."

python3 - "$OUTPUT_FILE" "$PROFILE_JSON" <<'PYTHON_SCRIPT'
import sys
import json
import re
import urllib.parse
import datetime
import math
import os

output_file = sys.argv[1]
profile_file = sys.argv[2]
DEFAULT_BLUEPRINT_BASE_URL = "https://bennett-maxwell.github.io/fki-preview"
blueprint_base_url = os.environ.get("BLUEPRINT_BASE_URL", DEFAULT_BLUEPRINT_BASE_URL).rstrip("/")

with open(profile_file, 'r') as f:
    profile = json.load(f)

with open(output_file, 'r') as f:
    html = f.read()

# ── Extract all fields from profile ──
lead_name = profile['lead_name']
business_name = profile['business_name']
first_name = lead_name.split()[0]
accent_color = profile.get('accent_color', '#007AFF')
industry = profile.get('industry', 'professional services')

# ── HUMANIZE THE INDUSTRY FOR CUSTOMER-FACING COPY ───────────────────────────
# PERMANENT FIX 2026-07-28 (marker BLUEPRINT-NO-TEXT-OVERFLOW-20260728,
# EC-BLUEPRINT-RAW-SLUG-OVERFLOW-20260728):
# `industry` doubles as the ROI-banding KEY (scripts/roi-industry-config.json), so it is a
# snake_case slug like `professional_services`. It was rendered VERBATIM into two customer-facing
# places — the Industry snapshot card and the "businesses in the ___ space" line. A snake_case
# slug is one unbreakable token, so it blew past its 147px card (254px of text) and read like a
# database field to the prospect. Same class as the raw-GHL-value leak the second-person gate
# already guards (`u250k`).
# The banding key stays raw; only the DISPLAY strings are humanized.
_industry_raw = str(industry or '').strip()
_industry_words = _industry_raw.replace('_', ' ').replace('-', ' ').split()
industry_phrase = ' '.join(w.lower() for w in _industry_words) or 'professional services'
_SMALL = {'and', 'or', 'of', 'for', 'to', 'in', 'the', 'a', 'an'}
industry_display = ' '.join(
    w.capitalize() if (i == 0 or w.lower() not in _SMALL) else w.lower()
    for i, w in enumerate(industry_phrase.split())
)
industry = industry_display  # {{INDUSTRY}} is customer-facing from here on
print(f"  Industry display: raw='{_industry_raw}' -> card='{industry_display}' prose='{industry_phrase}'")
phone = profile.get('phone', '')
email = profile.get('email', '')
services = profile.get('services', [])
ai_agents = profile.get('ai_agents', [])
tools = profile.get('tools', 'your current tools')

# Stat card fields (from lead data — NEVER from template)
years_in_business = profile.get('years_in_business', '—')
key_metric = profile.get('key_metric', '—')
key_metric_label = profile.get('key_metric_label', 'Projects Completed')
team_size = profile.get('team_size', '—')
monthly_leads = profile.get('monthly_leads', '—')
primary_goal = str(profile.get('primary_goal') or profile.get('quiz', {}).get('biggest_goal') or '—').strip().title()

# Derived values
method_name = business_name.split()[-1] if len(business_name.split()) > 1 else business_name
domain_slug = business_name.lower().replace(' ', '').replace("'", '')

# PERMANENT FIX 2026-07-30 (Madison, blueprint-ai project) — marker
# BLUEPRINT-DOMAIN-FABRICATED-FROM-BUSINESS-NAME-20260730,
# EC-BLUEPRINT-INVENTED-DOMAIN-PRESENTED-AS-LEAD-SITE-20260730:
# {{DOMAIN}} was ALWAYS `business_name.lower().replace(' ','') + '.com'` — a GUESS. It is
# rendered to the customer 5 times as a statement of fact ("Brand voice built from X",
# "a structured review of X"). When the guess is wrong we tell the prospect we reviewed a
# website that is not theirs. Caught on lisa-red-carpet-auto: business name yields
# `lisasredcarpetautoexperience.com` while her real, live site is `drivewithlisa.com`.
# It only ever "worked" by luck when the name slug happened to equal the real domain
# (e.g. william-diggers-catch -> diggerscatch.com). Same bug-class as the ROI/stack
# template-default leaks: per-lead content that was never sourced from the lead.
# Rule: use the lead's REAL website when the profile has one; guess only as a last resort.
#
# PERMANENT FIX 2026-08-03 (marker BLUEPRINT-DOMAIN-NO-GUESS-EVER-20260803,
# EC-BLUEPRINT-DOMAIN-GUESS-FALLBACK-STILL-LIVE-20260803):
# The 7/30 fix resolved the domain from profile['website'] but LEFT THE GUESS FALLBACK LIVE, so
# the defect simply moved: any lead with a missing OR PLACEHOLDER website re-inherited it.
# Proven on cindy-broken-in-treasures (FB paid lead): her submitted website was the placeholder
# "https://000000000", and the builder printed `brokenintreasures.com` and stated it to the
# customer as fact 6 times -- a domain that does not resolve (NXDOMAIN on .com/.net/.org/.co/
# .shop/llc.com; brokentreasures.com is a GoDaddy parked page). Paid-ad leads routinely leave the
# website field blank or garbage, so this is the common case, not the edge case.
# Rule now: a domain is used ONLY if it is structurally a real domain. There is NO guess, ever.
# When absent, domain_display is empty and the domain-bearing sentences are rewritten to neutral
# copy below (same approach as the no-CRM prose fix), then hard-asserted.
_site_raw = str(profile.get('website') or profile.get('domain') or '').strip()
_d = ''
if _site_raw:
    _d = re.sub(r'^https?://', '', _site_raw, flags=re.I).strip('/')
    _d = re.sub(r'^www\.', '', _d, flags=re.I).split('/')[0].strip().lower()
# Structural validity: must have a dot, a >=2-char alphabetic TLD, and a label that is not all
# digits/zeros. Catches "000000000", "0", "n/a", "none", "tbd", bare words, and IP-ish junk.
_valid_domain = bool(
    _d
    and re.match(r'^(?=.{4,253}$)([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}$', _d)
    and not re.match(r'^[0-9.]+$', _d)
    and _d.split('.')[0] not in ('none', 'na', 'tbd', 'null', 'example', 'test')
    and not re.match(r'^0+$', _d.split('.')[0])
)
if _valid_domain:
    domain_display = _d
    domain_provenance = 'lead_website'
else:
    domain_display = ''
    domain_provenance = ('absent_no_usable_website' if not _site_raw
                         else f'absent_rejected_placeholder({_site_raw[:40]})')
print(f"  Domain: '{domain_display}'  provenance={domain_provenance}")
services_str = ', '.join(services) if services else f'{industry} services'
# tools may be a list (normal profile shape, e.g. ["CRM","Email","Phone"]) or a str.
# Coerce to a string so {{CRM_TOOL}} html.replace() never sees a list (was TypeError,
# CL#4 2026-07-17 Madison CC — restores main's coercion so this branch matches main).
tools_str = ', '.join(tools) if isinstance(tools, list) else tools
# PERMANENT FIX 2026-07-17 (Madison, blueprint-ai project): when the lead's form
# answer for CRM / project-management tool is "none"/"other"/"n-a"/blank, render the
# clean literal "None" — NEVER the generic "your CRM". Truthful to the form, cleaner,
# less confusing. Applies to every future blueprint build (fleet-wide).
_tv = (tools_str or '').strip()
_NONE_SET = ('', 'none', 'n/a', 'na', 'n-a', 'other', 'no', 'not applicable', 'nothing')
crm_display = 'None' if _tv.lower() in _NONE_SET else _tv

# PERMANENT FIX 2026-07-23 (Madison, blueprint-ai project) — marker
# BLUEPRINT-STACK-NO-TEMPLATE-DEFAULT-LEAK-20260723: the stack cards for
# Project/SOP (was hardcoded "Notion"), Team Communication (was "Slack"), and
# File Storage (was "Google Drive") are now driven by the lead's REAL quiz answers,
# with the same none/other/blank -> literal "None" coercion as CRM. NEVER ship a
# branded tool the lead did not submit. Root cause: those three cards were hardcoded
# in TEMPLATE.html and never tokenized, so every lead inherited fake Notion/Slack.
_quiz = profile.get('quiz', {}) or {}
def _tool_display(v):
    s = (', '.join(v) if isinstance(v, list) else (v or '')).strip()
    return 'None' if s.lower() in _NONE_SET else s
pm_display = _tool_display(_quiz.get('project_management_tools'))
# PERMANENT FIX 2026-08-09 (Madison, blueprint-ai project) — marker
# BLUEPRINT-STACK-COMMS-KEY-MISMATCH-20260809: this read ONLY
# 'communication_channels', a key that no lead profile and no GHL custom field has
# ever used — the field is 'communication_tools'. So the 2026-07-23 de-hardcoding
# fix swapped a fake "Slack" for a silently wrong "None", and EVERY lead built since
# has rendered "Team Communication: None" while their own form listed real channels
# (karen-melting-pot-studio shipped this way with Slack/Text/WhatsApp/Email on file).
# Read the canonical key first, keep the old one as a fallback so nothing regresses.
team_comms_display = _tool_display(
    _quiz.get('communication_tools') or _quiz.get('communication_channels')
)
storage_display = _tool_display(_quiz.get('storage_tools'))

# Accent color derivatives
def lighten_hex(hex_color, factor=0.4):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f'#{r:02x}{g:02x}{b:02x}'

accent_light = lighten_hex(accent_color)
accent_mid = lighten_hex(accent_color, 0.2)

# Build tracked qualifier URL and mailto link
def host_scoped_url(profile_key, path):
    value = profile.get(profile_key) or ''
    if blueprint_base_url != DEFAULT_BLUEPRINT_BASE_URL and (not value or value.startswith(DEFAULT_BLUEPRINT_BASE_URL)):
        return f'{blueprint_base_url}{path}'
    return value or f'{blueprint_base_url}{path}'

def q7_agent_names():
    names = []
    for agent in profile.get('ai_agents', []) or []:
        if isinstance(agent, dict):
            names.append(agent.get('name') or agent.get('title') or agent.get('usecase') or '')
        else:
            names.append(str(agent))
    ap = profile.get('applicable_prompts')
    if isinstance(ap, dict):
        for item in ap.values():
            if isinstance(item, dict):
                names.append(item.get('name') or '')
    cleaned = []
    seen = set()
    for name in names:
        text = re.sub(r'<[^>]+>', '', str(name)).strip()
        key = re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()
        if text and key not in seen:
            seen.add(key); cleaned.append(text)
    return cleaned[:6]

lead_encoded = urllib.parse.quote(lead_name)
biz_encoded = urllib.parse.quote(business_name)
slug = profile.get('slug', lead_name.lower().replace(' ', '-'))
q7_agents = q7_agent_names()
agent_query = '&agents=' + urllib.parse.quote(','.join(q7_agents)) if q7_agents else ''
qualify_url = host_scoped_url('qualify_url', f'/qualify.html?lead={lead_encoded}&biz={biz_encoded}&src={slug}{agent_query}')

subject_encoded = urllib.parse.quote(f"Application -- {business_name}")
mailto_body = urllib.parse.quote(
    f"Hi Bennett,\n\n"
    f"I reviewed the AI Playbook and I'm interested.\n\n"
    f"1. What excites me most:\n"
    f"2. What I'd skip for now:\n"
    f"3. Approximate monthly budget I could allocate to AI:\n"
)
mailto_link = f"mailto:bennett@franchiseki.com?subject={subject_encoded}&body={mailto_body}"

urgency_text = f'2027 {industry} season demand is accelerating'

# ── ROI calculator slider: INDUSTRY-APPROPRIATE range (no cloned/fabricated $) ──
# Source of truth = scripts/roi-industry-config.json. Default value sits at min +
# data-no-default + calcTouched guard, so nothing displays as the client's own
# number until they drag it. Range lets the client model THEIR real transaction
# size instead of one generic franchise-consulting figure cloned onto every page.
import os as _os
_cfg_path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(output_file))), 'scripts', 'roi-industry-config.json')
roi_min, roi_max, roi_step = 500, 100000, 500  # safe generic fallback
try:
    with open(_cfg_path) as _cf:
        _roi = json.load(_cf)
    _bt = (profile.get('business_type') or industry or '').lower()
    _bt_map = {
        'plumbing': 'home_services', 'hvac': 'home_services', 'electrical': 'home_services',
        'home services': 'home_services', 'home-services': 'home_services', 'restoration': 'home_services',
        'photography': 'photography', 'photographer': 'photography',
        'video': 'video_production', 'videography': 'video_production',
        'medspa': 'medspa', 'med spa': 'medspa', 'aesthetics': 'medspa',
        'restaurant': 'food_franchise', 'food': 'food_franchise', 'franchise': 'food_franchise',
        'firearms': 'retail_firearms', 'retail': 'retail_firearms',
        'design': 'design_agency', 'agency': 'design_agency', 'marketing': 'design_agency',
        'consulting': 'consulting', 'consultant': 'consulting', 'coaching': 'consulting',
        'crm': 'crm_software', 'software': 'crm_software', 'saas': 'crm_software',
        'medical device': 'medical_devices', 'medtech': 'medical_devices',
        'property management': 'property_mgmt', 'property': 'property_mgmt', 'vacation rental': 'property_mgmt',
    }
    _ind = _roi['slug_industry'].get(slug)
    if not _ind:
        for _k, _v in _bt_map.items():
            if _k in _bt:
                _ind = _v; break
    if _ind and _ind in _roi['industry_slider']:
        _s = _roi['industry_slider'][_ind]
        roi_min, roi_max, roi_step = _s['min'], _s['max'], _s['step']
except Exception:
    pass

# ── SIMPLE PLACEHOLDER REPLACEMENT (no more 700-line find-and-replace) ──
# ── AI Prompt section fill (FIX 2026-07-17 Madison CC): TEMPLATE has {{PROMPT_ONE/TWO/THREE}}
#    (+ _TITLE) but the engine had NO mapping → every build hard-failed at the unfilled-placeholder
#    gate (sys.exit(1)). Source from profile['ai_prompts']=[{title,prompt},...]; fall back to
#    ai_agents' prompts; final generic fallback so this can never silently break a build again. ──
def _html_esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))
_ai_prompts = profile.get('ai_prompts') or []
def _prompt_at(i, field):
    if i < len(_ai_prompts) and isinstance(_ai_prompts[i], dict):
        v = _ai_prompts[i].get(field)
        if v:
            return v
    # fall back to ai_agents prompt/name
    if i < len(ai_agents) and isinstance(ai_agents[i], dict):
        if field == 'title':
            return ai_agents[i].get('name') or f'AI Workflow #{i+1}'
        return ai_agents[i].get('prompt') or ''
    if field == 'title':
        return ['Speed-to-Lead', 'Follow-Up & Reactivation', 'Admin & Content Automation'][i] if i < 3 else f'AI Workflow #{i+1}'
    return f'You are an AI assistant for {business_name}, a {industry} business. Help handle the task described above end to end, asking for any missing detail before acting.'
p1t, p1 = _prompt_at(0, 'title'), _prompt_at(0, 'prompt')
p2t, p2 = _prompt_at(1, 'title'), _prompt_at(1, 'prompt')
p3t, p3 = _prompt_at(2, 'title'), _prompt_at(2, 'prompt')

# ── ROI CALCULATOR PRESETS FROM THE LEAD'S OWN FORM ──────────────────────────
# PERMANENT FIX 2026-07-27 (marker BLUEPRINT-ROI-PRESET-FROM-FORM-20260727,
# EC-BLUEPRINT-ROI-TEMPLATE-DEFAULT-LEAK-20260727):
# The calculator inputs AND the PRESETS object were hardcoded in TEMPLATE.html
# (contract 2388 / leads 10 / rate 18 / hours 15), so EVERY lead saw the same
# lead-agnostic numbers no matter what they submitted. Carlos told us 50 monthly
# leads and the page still showed 10. Same bug-class as the 2026-07-23 stack leak
# (BLUEPRINT-STACK-NO-TEMPLATE-DEFAULT-LEAK-20260723): content hardcoded in the
# template and never tokenized.
# Rule: a value the lead ACTUALLY PROVIDED is preset. A value they did NOT provide
# is never fabricated — it falls back to a neutral, user-adjustable starting point,
# and never to a banned constant (18 close rate, 2388/45000 contract — Rules 14/18).
def _roi_num(*keys, default=None):
    """First numeric value found across profile top level then profile['quiz']."""
    quiz = profile.get('quiz') or {}
    for k in keys:
        for src in (profile, quiz):
            v = src.get(k)
            if v in (None, '', '—'):
                continue
            m = re.search(r'\d+(?:\.\d+)?', str(v).replace(',', ''))
            if m:
                return float(m.group(0))
    return default

_leads_val = _roi_num('monthly_leads', 'lead_volume', 'avg_monthly_lead_volume')
_rate_val = _roi_num('close_rate', 'current_close_rate')
_hours_val = _roi_num('admin_hours', 'admin_hours_per_week', 'weekly_admin_hours')
_contract_val = _roi_num('avg_contract_value', 'avg_ticket', 'average_customer_value')

# Clamp to each control's real min/max so a stated number can never render off-slider.
def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

# PERMANENT FIX 2026-08-17 (marker BLUEPRINT-ROI-LEADS-SLIDER-MAX-ADAPTIVE-20260817,
# EC-BLUEPRINT-ROI-LEADS-CLAMPED-BELOW-STATED-20260817)
# DEFECT: the Monthly New Leads slider was hardcoded max="100" in TEMPLATE.html, so ANY lead
# stating more than 100 monthly leads had their own number silently clamped down. Proven on
# corky-main-street-online-marketing: form said 150, page rendered 100 -- the lead reads a
# number they contradicted on their own intake. Same class as the Carlos 50-vs-10 defect
# (BLUEPRINT-ROI-PRESET-FROM-FORM-20260727): per-lead content pinned by a template constant.
# The 7/27 rule said "clamp to the control's min/max", which quietly LICENSED this; the
# governing rule is "every ROI control the lead PROVIDED a number for must render that number".
# FIX: the ceiling is now derived per lead with headroom, so the stated value always renders.
_leads_ceiling = 100
if _leads_val is not None and _leads_val > 100:
    _leads_ceiling = int(math.ceil((_leads_val * 1.5) / 50.0) * 50)
ROI_LEADS_MAX = _leads_ceiling
ROI_LEADS = int(_clamp(_leads_val, 2, ROI_LEADS_MAX)) if _leads_val is not None else 10
ROI_RATE = int(_clamp(_rate_val, 5, 60)) if _rate_val is not None else 20
ROI_HOURS = int(_clamp(_hours_val, 2, 40)) if _hours_val is not None else 15
ROI_CONTRACT = int(_contract_val) if _contract_val is not None else int(roi_min)

roi_preset_provenance = {
    'leads': 'form' if _leads_val is not None else 'neutral_default_not_provided',
    'rate': 'form' if _rate_val is not None else 'neutral_default_not_provided',
    'hours': 'form' if _hours_val is not None else 'neutral_default_not_provided',
    'contract': 'form' if _contract_val is not None else 'industry_band_min_not_provided',
}
print(f"  ROI presets: leads={ROI_LEADS} rate={ROI_RATE} hours={ROI_HOURS} "
      f"contract={ROI_CONTRACT}  provenance={roi_preset_provenance}")
print(f"  ROI leads slider ceiling: max={ROI_LEADS_MAX} "
      f"({'widened for stated value' if ROI_LEADS_MAX != 100 else 'template default'}); "
      f"stated={_leads_val} renders={ROI_LEADS} "
      f"{'OK' if (_leads_val is None or int(_leads_val) == ROI_LEADS) else 'CLAMPED — INVESTIGATE'}")

# Per-lead note slot (BLUEPRINT-LEAD-NOTE-SLOT-20260824). Empty for every lead that does not
# set `lead_note`, so this is additive and changes no existing page. Content lives in the lead
# JSON, never in the template -- same contract as blueprint_render_sections.py.
_lead_note = (profile.get('lead_note') or '').strip()
lead_note_html = (
    '<p style="font-size:0.92rem;color:var(--text-muted);margin-top:1rem;'
    'padding-top:0.85rem;border-top:1px solid var(--border, #d2d2d7);">' + _lead_note.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') + '</p>'
) if _lead_note else ''

replacements = {
    '{{ROI_LEADS_MAX}}': str(ROI_LEADS_MAX),
    '{{ROI_LEADS}}': str(ROI_LEADS),
    '{{ROI_RATE}}': str(ROI_RATE),
    '{{ROI_HOURS}}': str(ROI_HOURS),
    '{{ROI_CONTRACT}}': str(ROI_CONTRACT),
    '{{PROMPT_ONE_TITLE}}': p1t,
    '{{PROMPT_ONE}}': _html_esc(p1),
    '{{PROMPT_TWO_TITLE}}': p2t,
    '{{PROMPT_TWO}}': _html_esc(p2),
    '{{PROMPT_THREE_TITLE}}': p3t,
    '{{PROMPT_THREE}}': _html_esc(p3),
    '{{ROI_MIN}}': str(roi_min),
    '{{ROI_MAX}}': str(roi_max),
    '{{ROI_STEP}}': str(roi_step),
    '{{SLUG}}': slug,
    '{{BLUEPRINT_URL}}': host_scoped_url('blueprint_url', f'/blueprints/{slug}.html'),
    '{{PODCAST_URL}}': host_scoped_url('podcast_url', f'/podcasts/{slug}.mp3'),
    '{{LEAD_NAME}}': lead_name,
    '{{FIRST_NAME}}': first_name,
    '{{BUSINESS_NAME}}': business_name,
    '{{BIZ_NAME}}': business_name,
    '{{ACCENT_COLOR}}': accent_color,
    '{{ACCENT_LIGHT}}': accent_light,
    '{{ACCENT_MID}}': accent_mid,
    '{{INDUSTRY}}': industry,
    '{{INDUSTRY_PHRASE}}': industry_phrase,
    '{{YEARS_IN_BUSINESS}}': str(years_in_business),
    '{{KEY_METRIC}}': str(key_metric),
    '{{KEY_METRIC_LABEL}}': key_metric_label,
    '{{TEAM_SIZE}}': str(team_size),
    '{{MONTHLY_LEADS}}': str(monthly_leads),
    '{{PRIMARY_GOAL}}': primary_goal,
    '{{APPLY_URL}}': qualify_url,
    '{{QUALIFY_URL}}': qualify_url,
    '{{MAILTO_LINK}}': mailto_link,
    '{{SERVICES_LIST}}': services_str,
    '{{DOMAIN}}': domain_display,
    '{{CRM_TOOL}}': crm_display,
    '{{PM_TOOL}}': pm_display,
    '{{TEAM_COMMS_TOOL}}': team_comms_display,
    '{{STORAGE_TOOL}}': storage_display,
    '{{METHOD_NAME}}': method_name,
    '{{URGENCY_TEXT}}': urgency_text,
    '{{LEAD_NOTE}}': lead_note_html,
}

for placeholder, value in replacements.items():
    # Defensive: any list value (e.g. a scraped array field) joins to a string
    # so html.replace() never sees a non-str — same coercion as services_str/tools_str.
    if isinstance(value, list):
        value = ', '.join(str(v) for v in value)
    html = html.replace(placeholder, value)

# PERMANENT FIX 2026-07-30 (Madison, blueprint-ai project) — marker
# BLUEPRINT-NO-CRM-BROKEN-PROSE-20260730, EC-BLUEPRINT-YOUR-NONE-SENTENCES-20260730:
# The 2026-07-23 stack fix correctly coerces a missing CRM to the literal "None" for the
# STACK CARD and the oppmap tools cells (a label, where "None" is right). But {{CRM_TOOL}}
# is ALSO dropped into five running SENTENCES, where "None" is not a label — it is a noun.
# Those render as broken English to the customer: "wired into your None", "your None data",
# "initial None configuration", "your None forms", "built on your None account".
# Verified live 2026-07-30 on the already-DELIVERED william-diggers-catch page, which shows
# "your None account", "your None data", "your None forms" and "your None that answers".
# Any lead who answers no-CRM hits this, and no-CRM is common on the Advaita intake form.
# Fix: when there is no CRM, rewrite those five SENTENCE slots into grammatical copy that
# promises nothing the lead did not say and invents no tool name. Label slots keep "None".
if crm_display == 'None':
    _no_crm_prose = [
        ('wired into your None that answers every inbound',
         'wired into your website and text inquiries that answers every inbound'),
        ('pulled directly from your None data',
         'pulled directly from the customer records we set up with you'),
        ('and initial None configuration',
         'and initial CRM setup'),
        ('connected to your None forms',
         'connected to your website and text inquiries'),
        ('built on your None account',
         'built on the CRM account we set up for you'),
    ]
    _fixed = 0
    for _bad, _good in _no_crm_prose:
        if _bad in html:
            html = html.replace(_bad, _good)
            _fixed += 1
    print(f"  no-CRM prose: rewrote {_fixed}/{len(_no_crm_prose)} sentence slots "
          f"(stack card + tools cells keep the literal 'None')")
    if 'your None' in html or ' None configuration' in html:
        import sys as _sys
        print("ERROR: a 'None' sentence slot survived the no-CRM prose fix.", file=_sys.stderr)
        _sys.exit(1)

# PERMANENT FIX 2026-08-03 (marker BLUEPRINT-DOMAIN-NO-GUESS-EVER-20260803):
# When the lead has NO usable website, the template's domain-bearing sentences must not name a
# domain at all. Rewrite them to neutral, still-true copy, then hard-fail if any address survives.
if not domain_display:
    import re as _re2
    _domain_prose = [
        (r'Brand voice is calibrated from\s+and the language your customers already use',
         'Brand voice is calibrated from your own words and the language your customers already use'),
        (r'Brand voice is built instantly from\s+and your existing customer language',
         'Brand voice is built from your own words and your existing customer language'),
        (r'Brand voice built from\s+and your existing ([^<]{1,80}?) messaging',
         r'Brand voice built from your own words in the kickoff call'),
        (r'based on your intake answers and a structured review of\s*\.',
         'based on your intake answers.'),
        (r'a structured review of\s+([A-Za-z0-9.-]*)\.', 'a structured review of what you told us.'),
        (r'trained on your brand voice from\s+that converts', 'trained on your brand voice that converts'),
        (r'\bfrom\s+and\b', 'from your own words and'),
        (r'\breview of\s+\.', 'review of what you told us.'),
    ]
    _dfix = 0
    for _pat, _rep in _domain_prose:
        html, _n = _re2.subn(_pat, _rep, html)
        _dfix += _n
    # collapse any doubled spaces the empty token left behind, inside text only
    html = _re2.sub(r'(?<=[a-z,])  +(?=[a-z])', ' ', html)
    print(f"  no-domain prose: rewrote {_dfix} sentence slot(s) (no website supplied -> no domain named)")
    # HARD ASSERT: no fabricated domain may survive. The business-name guess is the exact string
    # the old fallback would have produced; if it appears anywhere, the build is lying to the customer.
    _guess = f'{domain_slug}.com'
    if _guess.lower() in html.lower():
        import sys as _sys
        print(f"ERROR: fabricated domain '{_guess}' present although the lead supplied no usable "
              f"website (BLUEPRINT-DOMAIN-NO-GUESS-EVER-20260803).", file=_sys.stderr)
        _sys.exit(1)

# PERMANENT FIX 2026-07-23 (marker BLUEPRINT-STACK-NO-TEMPLATE-DEFAULT-LEAK-20260723):
# After tokens resolve, the oppmap "Tools It Connects" cells can contain repeats or
# multiple "None" (e.g. "None, None, Email"). Dedup each plain-text tools cell and drop
# "None" whenever a real tool is present, so cells stay truthful + tidy. Never invents a tool.
import re as _re
def _clean_tools_cell(m):
    parts = [p.strip() for p in m.group(1).split(',') if p.strip()]
    seen = []
    for p in parts:
        if p.lower() not in [s.lower() for s in seen]:
            seen.append(p)
    reals = [p for p in seen if p.lower() != 'none']
    out = reals if reals else (['None'] if seen else [])
    return '<td>' + ', '.join(out) + '</td>'
def _clean_oppmap(h):
    def _repl(mt):
        return _re.sub(r'<td>([^<]*)</td>', _clean_tools_cell, mt.group(0))
    return _re.sub(r'<table class="opp-table">.*?</table>', _repl, h, flags=_re.S)
html = _clean_oppmap(html)

# ── AI Agent Cards: Replace template agents with lead-specific ones ──
if ai_agents and len(ai_agents) > 0:
    agents_start_marker = '<!-- Agent 1: Speed-to-Lead -->'
    agents_end_marker = '<!-- DIY vs Partner -->'
    start_idx = html.find(agents_start_marker)
    end_idx = html.find(agents_end_marker)

    if start_idx != -1 and end_idx != -1:
        agent_cards_html = ""
        for i, agent in enumerate(ai_agents[:6], 1):
            a_name = agent.get('name', f'AI Agent #{i}')
            a_desc = agent.get('desc', f'Custom AI agent for your {industry} business.')
            a_result = agent.get('result') or agent.get('outcome') or f'Automates key {industry} workflows.'
            a_desc_escaped = (str(a_desc)
                .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            a_result_escaped = (str(a_result)
                .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

            # v3.42 (Madison 2026-07-01) HARD RED-LINE D2-03: the 6 agent squares are
            # CONDENSED, outcome-first cards — icon + name + desc + outcome ONLY. They
            # must NEVER carry a raw "Copy-paste prompt:" block / "You are an AI agent…"
            # boilerplate (that reads as a lazy paste and hard-fails
            # blueprint_agent_prompt_quality_gate.check_agent_cards_no_boilerplate).
            # The full copy-paste operating runbooks live ONLY in the 3 ready-to-use
            # dropdown prompts (prompt-pre, from ai_prompts / {{PROMPT_ONE..THREE}}).
            icon_svg = '<div class="agent-icon"><svg viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg></div>'
            agent_cards_html += f'''    <!-- Agent {i} -->
      <div class="agent-card">{icon_svg}<div class="agent-name">{a_name}</div><div class="agent-desc">{a_desc_escaped}</div><div class="agent-outcome">{a_result_escaped}</div></div>

'''
        html = html[:start_idx] + agent_cards_html + html[end_idx:]

# ── Contact info injection ──
if phone or email:
    contact_block = ''
    if phone:
        contact_block += f'<p style="font-size:13px; color:var(--text-mid); margin-top:4px;">Phone: {phone}</p>'
    if email:
        contact_block += f'<p style="font-size:13px; color:var(--text-mid); margin-top:4px;">Email: {email}</p>'
    prep_marker = f'{lead_name} -- {business_name}</strong>'
    if prep_marker in html:
        html = html.replace(prep_marker, prep_marker + '\n    ' + contact_block)

# ── Strip box-drawing chars + emoji entities for pre-delivery check ──
def strip_box_drawing(text):
    return ''.join('-' if 0x2500 <= ord(ch) <= 0x257F else ch for ch in text)
html = strip_box_drawing(html)
html = html.replace('<div class="icon">&#128176;</div>', '<div class="icon" style="font-size:20px;font-weight:800;color:var(--accent);">$</div>')
html = html.replace('<div class="icon">&#9201;</div>', '<div class="icon" style="font-size:20px;font-weight:800;color:var(--accent);">T</div>')
html = html.replace('<div class="icon">&#128161;</div>', '<div class="icon" style="font-size:20px;font-weight:800;color:var(--accent);">%</div>')
html = html.replace('&#8594;', '-->').replace('&#128202;', '#').replace('&#10003;', 'OK')

# ── Ensure 3/7/30 cadence markers ──
if 'Our 3-day, 7-day, 30-day onboarding cadence' not in html:
    html = html.replace(
        'Pretty much everything is done within 30 days.',
        'Pretty much everything is done within 30 days. Our 3-day, 7-day, 30-day onboarding cadence means you see results fast.'
    )

# ── Build metadata ──
build_ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
meta_comment = f'<!-- Blueprint AI Pipeline v3.0 | Built: {build_ts} | Lead: {lead_name} | Industry: {industry} -->\n'
html = meta_comment + html

# ── POST-BUILD CONTAMINATION CHECK ──
# Check for TEMPLATE-specific phrases (not generic words that could be legitimate lead data)
# Template contamination = phrases that should ONLY appear in Brittney's original template
# but should never leak into other leads' blueprints
contamination_phrases = [
    'Events Designed',           # Brittney's stat card label
    'luxury event design',       # Brittney's industry phrase
    'HoneyBook',                 # Brittney's CRM tool
    'Dallas luxury market',      # Brittney's market
]
# Only check business-name-specific terms if this is NOT a Warnick lead (Brittney
# Warnick was the original template lead; Britt Warnick is a real prospect whose
# business "Britt Warnick Designs" legitimately contains "Warnick Design").
if 'warnick' not in lead_name.lower():
    contamination_phrases.extend([
        'Brittney Warnick',
        'Warnick Design',
        'warnickdesign.com',
    ])

found = []
for phrase in contamination_phrases:
    if phrase.lower() in html.lower():
        found.append(phrase)
if found:
    print(f"  CONTAMINATION DETECTED: {found}")
    sys.exit(1)

# Verify no unfilled placeholders remain
unfilled = re.findall(r'\{\{[A-Z_]+\}\}', html)
if unfilled:
    print(f"  UNFILLED PLACEHOLDERS: {set(unfilled)}")
    sys.exit(1)

with open(output_file, 'w') as f:
    f.write(html)

print(f"  Replacements complete. Output: {output_file}")
PYTHON_SCRIPT

# PERMANENT FIX 2026-08-03 (marker BLUEPRINT-TEMPLATE-SECTIONS-PER-LEAD-20260803, Madison directive):
# Render gaps/oppmap/results/ignore/timeline FROM THE LEAD PROFILE. TEMPLATE.html hardcoded these
# five sections as lead-agnostic B2B-agency copy, so every build shipped a different AI-employee
# roster than the lead's own six, two FABRICATED "You flagged X as a top stress" claims, "Agent"
# instead of "AI Employee", and plural-team copy on solo operators -- and run-audit.py scored those
# pages 19/19 anyway. Both janet-drawn-logic and cindy-broken-in-treasures had to be hand-repaired.
# This makes it structural. BLOCKING: a surviving leak refuses the build.
RENDER_SECTIONS="$SCRIPT_DIR/blueprint_render_sections.py"
if [[ -f "$RENDER_SECTIONS" ]]; then
  python3 "$RENDER_SECTIONS" --lead "$LEAD_SLUG" --html "$OUTPUT_FILE" || {
    echo "ERROR: per-lead section render failed its own leak check -- refusing to continue" >&2
    echo "       (BLUEPRINT-TEMPLATE-SECTIONS-PER-LEAD-20260803)" >&2
    exit 1
  }
fi

# Convert legacy event-design/B2B sections into a home-services page before any
# gate can pass. The frame is still canonical; this patch removes wrong-industry
# content for plumbing/HVAC/electrical/home-service profiles.
HOME_SERVICES_PATCH="$SCRIPT_DIR/blueprint_home_services_patch.py"
if [[ -f "$HOME_SERVICES_PATCH" ]]; then
  python3 "$HOME_SERVICES_PATCH" "$OUTPUT_FILE" "$PROFILE_JSON"
fi

# Convert legacy SaaS/home-services prompt copy into a restaurant/QSR page before
# any audit can pass. This preserves the canonical frame while removing stale
# cross-industry language and enforcing qualifier-only CTAs for food brands.
RESTAURANT_PATCH="$SCRIPT_DIR/blueprint_restaurant_patch.py"
if [[ -f "$RESTAURANT_PATCH" ]]; then
  python3 "$RESTAURANT_PATCH" "$OUTPUT_FILE" "$PROFILE_JSON"
fi

# Stamp blueprint build timestamp into profile
python3 -c "
import json, sys, datetime
p = json.load(open(sys.argv[1]))
p['blueprint_ts'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
json.dump(p, open(sys.argv[1], 'w'), indent=2)
" "$PROFILE_JSON" 2>/dev/null || true

# ─── Step 3: Validate output ───────────────────────────────────────────────
echo "[3/7] Validating output..."

# Check for TEMPLATE-SPECIFIC contamination (not generic words that could be legitimate)
CONTAMINATION=0
for PHRASE in "Events Designed" "The Warnick Method" "The Warnick Filter" "HoneyBook" "luxury event design" "Dallas luxury market"; do
  if grep -qi "$PHRASE" "$OUTPUT_FILE" 2>/dev/null; then
    echo "FAIL: '$PHRASE' found in output — template contamination!"
    CONTAMINATION=1
  fi
done
# Only check name-specific terms if this is NOT a Warnick lead
# (Brittney Warnick = template origin; Britt Warnick = real prospect whose business
# "Britt Warnick Designs" legitimately contains "Warnick Design" as a substring)
LEAD_NAME_LOWER=$(echo "$LEAD_NAME" | tr '[:upper:]' '[:lower:]')
if [[ "$LEAD_NAME_LOWER" != *"warnick"* ]]; then
  for NAME_PHRASE in "Brittney Warnick" "Warnick Design" "warnickdesign.com"; do
    if grep -qi "$NAME_PHRASE" "$OUTPUT_FILE" 2>/dev/null; then
      echo "FAIL: '$NAME_PHRASE' found in another lead's blueprint!"
      CONTAMINATION=1
    fi
  done
fi
if [ "$CONTAMINATION" -eq 1 ]; then
  echo "ABORTING: Template contamination detected. Blueprint NOT clean."
  exit 1
fi
echo "  Contamination check: PASS (zero template leakage)"
# Check for direct booking URLs (should not exist in blueprint pages)
if grep -qi "booking\|calendly\|cal\.com" "$OUTPUT_FILE" 2>/dev/null; then
  echo "WARNING: Direct booking/calendar URL detected. Route through qualify.html instead."
fi

# Verify CTA is correct
if grep -q "See If You Qualify" "$OUTPUT_FILE"; then
  echo "  CTA verified: 'See If You Qualify' present."
else
  echo "WARNING: CTA 'See If You Qualify' not found."
fi

# Verify 3/7/30 timeline
if grep -q "Days 1-3" "$OUTPUT_FILE" && grep -q "Days 4-7" "$OUTPUT_FILE" && grep -q "Day 30" "$OUTPUT_FILE"; then
  echo "  Timeline verified: 3/7/30 onboarding cadence present."
else
  echo "WARNING: 3/7/30 timeline markers not all found."
fi

# Verify interactive calculator exists (Avg Customer Value = fill-in input, 3 sliders)
if grep -Eq 'id="sl-(leads|rate|hours)"' "$OUTPUT_FILE"; then
  echo "  ROI Calculator verified: Interactive sliders present."
else
  echo "WARNING: Interactive ROI calculator not found."
fi

echo "  Validation complete."

# ─── Step 4: HARD GATE — auto-heal -> D9 -> pre-delivery (v2 2026-05-29) ─────
# Council-approved generator gate. Blocks commit/push of any regressed re-emit
# (Command Center / countdown / old-player / contamination / CTA / cadence).
# Additive + reversible: does NOT alter generation logic above.
echo "[4/7] Running HARD gates (auto-heal -> D9 -> pre-delivery)..."
PRE_DELIVERY="$SCRIPT_DIR/pre-delivery-check.sh"
GATE_FAIL=0

# 4a0. ROI AVG-CUSTOMER-VALUE FILL-IN GATE (HARD — Bennett directive 2026-06-02).
#      The Avg Customer Value field MUST be a typed fill-in <input type="number"
#      id="sl-contract">, NEVER a type="range" slider. This is the GUARANTEE that
#      the slider can never ship again: any regression to a range slider for this
#      field, or a missing fill-in input, hard-fails the build (exit 1) below.
#      Bennett asked for this repeatedly; the gate makes the rule un-skippable.
if grep -Eq 'type="range"[^>]*id="sl-contract"|id="sl-contract"[^>]*type="range"' "$OUTPUT_FILE"; then
  echo "  ROI fill-in gate: FAIL -- Avg Customer Value is a type=\"range\" SLIDER (must be a fill-in number input)."
  GATE_FAIL=1
elif grep -Eq 'type="number"[^>]*id="sl-contract"|id="sl-contract"[^>]*type="number"' "$OUTPUT_FILE"; then
  echo "  ROI fill-in gate: PASS -- Avg Customer Value is a typed fill-in number input."
else
  echo "  ROI fill-in gate: FAIL -- no <input type=\"number\" id=\"sl-contract\"> fill-in found for Avg Customer Value."
  GATE_FAIL=1
fi

# 3b. ROI PRESET-FROM-FORM gate (BLUEPRINT-ROI-PRESET-FROM-FORM-20260727, HARD)
# Blocks the template-default leak: a number the lead actually stated (e.g. Carlos's
# 50 monthly leads) must render on the page, PRESETS must not carry lead-agnostic
# literals, and banned ROI constants (18 rate / 2388 / 45000 contract) must not ship.
if python3 "$SCRIPT_DIR/blueprint_roi_preset_gate.py" --lead "$LEAD_SLUG" --html "$OUTPUT_FILE" --profile "$PROFILE_JSON" >/tmp/roi-preset-gate.$$ 2>&1; then
  echo "  ROI preset gate: PASS -- calculator matches the lead's stated intake numbers."
else
  echo "  ROI preset gate: FAIL -- calculator is showing template defaults, not this lead's numbers:"
  sed 's/^/    /' /tmp/roi-preset-gate.$$
  GATE_FAIL=1
fi
rm -f /tmp/roi-preset-gate.$$

# 3c. TEXT-OVERFLOW / RAW-TOKEN gate (BLUEPRINT-NO-TEXT-OVERFLOW-20260728, HARD)
# Renders the built page in a real browser at desktop AND mobile widths and fails on any
# text wider than its own box, or any raw snake_case identifier in customer-facing copy.
if python3 "$SCRIPT_DIR/blueprint_text_overflow_gate.py" --lead "$LEAD_SLUG" --local >/tmp/overflow-gate.$$ 2>&1; then
  echo "  text-overflow gate: PASS -- no clipped text, no raw internal tokens."
else
  echo "  text-overflow gate: FAIL -- customer-visible text problem:"
  sed 's/^/    /' /tmp/overflow-gate.$$
  GATE_FAIL=1
fi
rm -f /tmp/overflow-gate.$$

# 4a. Auto-heal generator reverts before gating
AUTOFIX="/Users/openclaw/Documents/New project/scripts/blueprint_autofix.py"
if [[ -f "$AUTOFIX" ]]; then
  healout=$(python3 "$AUTOFIX" "$OUTPUT_FILE" 2>/dev/null || true)
  echo "  autofix: ${healout:-no-op}"
fi

# 4b. D9 render-integrity audit (HARD — 20 binary checks, network-free)
D9_AUDIT="$HOME/.claude/skills/blueprint-ai-audit-skill/d9-audit.py"
if [[ -f "$D9_AUDIT" ]]; then
  if python3 "$D9_AUDIT" "$OUTPUT_FILE" --business-name "$BUSINESS_NAME" >/dev/null 2>&1; then
    echo "  D9: PASS (20/20)"
  else
    echo "  D9: FAIL -- render-integrity audit failed (run: python3 $D9_AUDIT $OUTPUT_FILE --business-name \"$BUSINESS_NAME\")"
    GATE_FAIL=1
  fi
else
  echo "  WARNING: d9-audit.py not found -- D9 gate skipped"
fi

# 4c. Pre-delivery 10-check (HARD). --leads MUST be the OTHER canonical leads
#     (memory gotcha: own-name in --leads false-fails cross_contamination).
if [[ -f "$PRE_DELIVERY" && -x "$PRE_DELIVERY" ]]; then
  OTHER_LEADS=$(cd "$REPO_ROOT/blueprints" 2>/dev/null && ls *.html 2>/dev/null \
    | sed 's/\.html$//' | grep -v "^${LEAD_SLUG}$" | grep -v "^TEMPLATE$" | paste -sd, -)
  if "$PRE_DELIVERY" "$OUTPUT_FILE" --leads "$OTHER_LEADS" >/dev/null 2>&1; then
    echo "  pre-delivery: PASS"
  else
    echo "  pre-delivery: FAIL -- run: $PRE_DELIVERY $OUTPUT_FILE --leads \"$OTHER_LEADS\""
    GATE_FAIL=1
  fi
else
  echo "  No pre-delivery-check.sh found -- pre-delivery gate skipped"
fi

if [[ "$GATE_FAIL" == "1" ]]; then
  echo "ERROR: HARD GATE FAILED -- refusing to commit/push a regressed blueprint." >&2
  echo "  File left at: $OUTPUT_FILE (fix the failing gate above, then re-run)." >&2
  exit 1
fi
echo "  Validation complete -- all HARD gates PASS."

if [[ "$DRY_RUN" == "true" || "$NO_COMMIT" == "true" ]]; then
  echo ""
  echo "=== NO-COMMIT COMPLETE ==="
  echo "Output: $OUTPUT_FILE"
  echo "Skipping git commit, push, and HTTP verify."
  exit 0
fi

# ─── Step 4.5: Post-generate quality gate ───────────────────────────────────
echo "[4.5/7] Running post-generate completion gate..."
GATE_SCRIPT="$REPO_ROOT/scripts/post-generate-gate.sh"
if [ -f "$GATE_SCRIPT" ]; then
  bash "$GATE_SCRIPT" "$REPO_ROOT/blueprints/$LEAD_SLUG.html" --lead "$LEAD_SLUG" || {
    echo "⚠️  Completion gate FAIL — blueprint has quality issues but continuing commit."
    echo "   Fix issues before delivery. Run: python3 scripts/blueprint_completion_gate.py --html blueprints/$LEAD_SLUG.html --receipt-dir audit-receipts/$LEAD_SLUG --lead $LEAD_SLUG"
  }
else
  echo "  post-generate-gate.sh not found — skipping"
fi

# ─── Step 5: Git commit ─────────────────────────────────────────────────────
echo "[5/7] Committing..."
cd "$REPO_ROOT"
if [[ "$NO_COMMIT" == "true" ]]; then
  echo "  --no-commit mode: skipping per-lead git commit (batch orchestrator handles commit)"
else
  # Clear stale index.lock before git op
  [ -f ".git/index.lock" ] && rm -f ".git/index.lock" && echo "  Cleared stale index.lock"
  git add "blueprints/$LEAD_SLUG.html"
  git commit -m "Add Blueprint: $BUSINESS_NAME ($LEAD_SLUG)" || {
    echo "  Nothing to commit (file may already be tracked)."
  }
fi

if [[ "$NO_PUSH" == "true" ]]; then
  echo ""
  echo "=== COMPLETE (no-push mode) ==="
  echo "Output: $OUTPUT_FILE"
  echo "Committed but not pushed."
  exit 0
fi

# ─── Step 6: Git push ──────────────────────────────────────────────────────
echo "[6/7] Pushing to origin..."
git push origin HEAD || {
  echo "ERROR: Push failed. Check remote configuration." >&2
  exit 1
}

# ─── Step 7: Verify HTTP 200 ───────────────────────────────────────────────
echo "[7/7] Verifying live URL..."
LIVE_URL="$GITHUB_PAGES_BASE/$LEAD_SLUG.html"
echo "  URL: $LIVE_URL"

# Give GitHub Pages a moment to deploy
echo "  Waiting 15s for GitHub Pages deployment..."
sleep 15

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$LIVE_URL" 2>/dev/null || echo "000")

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "  HTTP 200 confirmed. Blueprint is live."
else
  echo "  HTTP $HTTP_CODE -- page may still be deploying. Check again in 1-2 minutes."
  echo "  URL: $LIVE_URL"
fi

echo ""
echo "=== BLUEPRINT CLONE COMPLETE ==="
echo "  Lead:     $LEAD_NAME"
echo "  Business: $BUSINESS_NAME"
echo "  File:     $OUTPUT_FILE"
echo "  Live URL: $LIVE_URL"
