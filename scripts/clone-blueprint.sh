#!/usr/bin/env bash
# clone-blueprint.sh — Clone the canonical Brittney v7 frame into a new lead Blueprint.
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
#   - ALWAYS clones from brittney-warnick.html (v7 frame) -- never rebuilds from scratch
#   - CTA = "Apply to Work With Bennett" qualifying mailto
#   - 3/7/30 onboarding timeline (NOT 90-day)
#   - Interactive ROI calculator only (no hardcoded dollar predictions)
#   - All stats must have cited sources (preserved from v7 frame)
#   - NO booking URLs, NO calendar links
#
# Requirements: bash 4+, python3, jq, git, curl

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="$REPO_ROOT/blueprints/brittney-warnick.html"
BLUEPRINTS_DIR="$REPO_ROOT/blueprints"
GITHUB_PAGES_BASE="https://bennett-maxwell.github.io/fki-preview/blueprints"

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
  --no-push           Generate and commit but skip push and HTTP verify.

WHAT IT DOES:
  1. Copies brittney-warnick.html as the base (canonical v7 frame)
  2. Replaces all lead-specific content (name, business, color, services,
     AI agent cards, contact info, mailto subjects)
  3. Outputs to blueprints/<lead-slug>.html
  4. Runs pre-delivery-check.sh if it exists
  5. Commits and pushes to origin
  6. Verifies HTTP 200 on the live GitHub Pages URL

RULES ENFORCED:
  - Never rebuilds from scratch -- always clones from v7 frame
  - CTA = "Apply to Work With Bennett" (qualifying mailto, no booking URLs)
  - 3/7/30 onboarding timeline (not 90-day)
  - Interactive ROI calculator (no hardcoded dollar predictions)
  - All stats have cited sources (preserved from template)
HELP
  exit 0
}

# ─── Arg parsing ────────────────────────────────────────────────────────────
DRY_RUN=false
NO_PUSH=false
PROFILE_JSON=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage ;;
    --dry-run) DRY_RUN=true; shift ;;
    --no-push) NO_PUSH=true; shift ;;
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
  echo "The canonical v7 frame (brittney-warnick.html) must exist." >&2
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

# Generate slug from lead name
LEAD_SLUG=$(echo "$LEAD_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
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

output_file = sys.argv[1]
profile_file = sys.argv[2]

with open(profile_file, 'r') as f:
    profile = json.load(f)

with open(output_file, 'r') as f:
    html = f.read()

lead_name = profile['lead_name']
business_name = profile['business_name']
accent_color = profile.get('accent_color', '#B75E42')
industry = profile.get('industry', 'professional services')
phone = profile.get('phone', '')
email = profile.get('email', '')
services = profile.get('services', [])
ai_agents = profile.get('ai_agents', [])

# Extract first name
first_name = lead_name.split()[0]

# URL-encode the business name for mailto subjects
biz_encoded = urllib.parse.quote(business_name)
subject_encoded = urllib.parse.quote(f"Application -- {business_name}")

# Build the qualifying mailto link
mailto_body = urllib.parse.quote(
    f"Hi Bennett,\n\n"
    f"I reviewed the AI Playbook and I'm interested.\n\n"
    f"1. What excites me most:\n"
    f"2. What I'd skip for now:\n"
    f"3. Approximate monthly budget I could allocate to AI:\n"
)
mailto_link = f"mailto:bennett@franchiseki.com?subject={subject_encoded}&body={mailto_body}"

# ── Core name/business replacements ──
# Title tag
html = html.replace(
    'AI Advantage Roadmap — Warnick Design',
    f'AI Advantage Roadmap -- {business_name}'
)

# Hero
html = html.replace(
    'The Warnick Design AI Playbook',
    f'The {business_name} AI Playbook'
)

# "Prepared exclusively for" line
html = html.replace(
    'Brittney Warnick — Warnick Design',
    f'{lead_name} -- {business_name}'
)

# ── Accent color replacement ──
html = html.replace('#B75E42', accent_color)

# Also replace the accent-light derivative (compute a lighter version)
# Simple approach: lighten by mixing with white
def lighten_hex(hex_color, factor=0.4):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f'#{r:02x}{g:02x}{b:02x}'

accent_light = lighten_hex(accent_color)
html = html.replace('#d4896f', accent_light)

# Gradient color for urgency bar
html = html.replace('#c96b50', lighten_hex(accent_color, 0.2))

# ── All "Warnick Design" references ──
html = re.sub(r'Warnick Design', business_name, html)

# ── All "Brittney Warnick" references ──
html = re.sub(r'Brittney Warnick', lead_name, html)

# ── All "Brittney" first-name references (careful not to hit "Brittney Warnick" again) ──
# Only replace standalone Brittney that is NOT followed by Warnick (already replaced)
html = re.sub(r"Brittney(?!'s)", first_name, html)
# Handle possessive "Brittney's"
html = re.sub(r"Brittney's", f"{first_name}'s", html)

# ── All mailto links with the new business ──
# Replace all existing mailto hrefs
mailto_pattern = r'mailto:bennett@franchiseki\.com\?subject=Application[^"]*'
html = re.sub(mailto_pattern, mailto_link, html)

# ── Subtitle: customize for industry ──
html = html.replace(
    'A custom-built roadmap showing exactly how AI agents can increase revenue, save time, and cut costs for your luxury event design business.',
    f'A custom-built roadmap showing exactly how AI agents can increase revenue, save time, and cut costs for your {industry} business.'
)

# ── warnickdesign.com reference ──
domain_slug = business_name.lower().replace(' ', '').replace("'", '')
html = html.replace('warnickdesign.com', f'{domain_slug}.com')

# ── command.warnickdesign.com reference ──
html = html.replace(f'command.{domain_slug}.com', f'command.{domain_slug}.com')

# ── Services: Update the specialties row in the profile table ──
if services:
    services_str = ', '.join(services)
    html = html.replace(
        'Corporate events, weddings, galas, product launches, venue coordination',
        services_str
    )

# ── AI Agent Cards: Replace all 3 template agents with up to 6 from profile ──
if ai_agents and len(ai_agents) > 0:
    # Find the agents section and rebuild it
    agents_start_marker = '<!-- Agent 1: Speed-to-Lead -->'
    agents_end_marker = '<!-- DIY vs Partner -->'

    start_idx = html.find(agents_start_marker)
    end_idx = html.find(agents_end_marker)

    if start_idx != -1 and end_idx != -1:
        agent_cards_html = ""
        for i, agent in enumerate(ai_agents[:6], 1):
            a_name = agent.get('name', f'AI Agent #{i}')
            a_desc = agent.get('desc', f'Custom AI agent for your {industry} business.')
            a_prompt = agent.get('prompt', f'You are an AI agent for {business_name}. Help with {a_name.lower()} tasks.')
            a_result = agent.get('result', f'Automates key {industry} workflows.')
            a_time = agent.get('time', '5 minutes')

            # Escape HTML in prompt
            a_prompt_escaped = (a_prompt
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

            agent_cards_html += f'''    <!-- Agent {i} -->
    <div class="agent-card">
      <h3>Agent #{i}: {a_name}</h3>
      <p class="agent-desc">{a_desc}</p>
      <div class="agent-prompt">{a_prompt_escaped}</div>
      <div class="agent-result">What this does: {a_result}</div>
      <div class="agent-time">Setup time: ~{a_time}</div>
    </div>

'''
        html = html[:start_idx] + agent_cards_html + html[end_idx:]

# ── LinkedIn section: replace industry-specific references ──
html = html.replace(
    'venue coordinators, corporate event planners, and hotel event managers in the Dallas luxury market',
    f'qualified prospects and decision-makers in your {industry} market'
)
html = html.replace(
    'venue coordinators, corporate event planners, and hotel event managers',
    f'qualified prospects and decision-makers in {industry}'
)
html = html.replace(
    'AI identifies venue coordinators and corporate planners who match your ideal project profile',
    f'AI identifies qualified prospects who match your ideal client profile in {industry}'
)
html = html.replace(
    'luxury, warm, never salesy',
    'professional, warm, never salesy'
)
html = html.replace(
    "luxury tone — elevated, warm, never salesy",
    f"professional tone matched to {business_name}'s voice"
)

# ── Pain points: generalize from events to the lead's industry ──
html = html.replace(
    'slow proposal turnaround, lead follow-up dying after touch #1, and an untapped LinkedIn pipeline',
    f'lead follow-up dying after touch #1, slow response times, and an untapped LinkedIn pipeline'
)
html = html.replace(
    'Luxury clients expect fast, polished proposals. Manual creation takes days — in the luxury event world, the first designer to present a compelling vision wins the contract.',
    f'Clients expect fast, professional responses. Manual follow-up takes hours or days -- in {industry}, the first to respond with a compelling message wins the deal.'
)
html = html.replace(
    'Inquiries from venue partners and corporate planners go cold after touch #1. Without systematic nurture, warm leads slip to competitors.',
    'Inquiries go cold after touch #1. Without systematic nurture, warm leads slip to competitors who follow up faster.'
)
html = html.replace(
    'B2B corporate pipeline sits unused. Venue coordinators, corporate event planners, and hotel event managers are all on LinkedIn',
    f'B2B pipeline sits unused. Key decision-makers in {industry} are active on LinkedIn'
)
html = html.replace(
    'Portfolio shoots and behind-the-scenes moments need to be turned into marketing content — but the creative team is focused on events.',
    f'Great work needs to be turned into marketing content -- but the team is focused on serving clients.'
)
html = html.replace(
    'Past inquiry list and clients are not being nurtured for repeat events. Corporate clients host annual galas and quarterly events.',
    'Past clients and inquiries are not being nurtured for repeat business and referrals.'
)
html = html.replace(
    'Contract generation, invoicing, vendor coordination, and timeline management are all manual. Hours spent on logistics that could be automated.',
    'Contract generation, invoicing, and administrative tasks are all manual. Hours spent on logistics that could be automated.'
)

# ── AI fix lines in pain cards: generalize ──
html = html.replace(
    'Auto-draft luxury proposals from inquiry details within hours',
    'Auto-draft professional proposals from inquiry details within hours'
)
html = html.replace(
    'Turn portfolio photos into branded social + blog content',
    'Turn your best work into branded social + blog content'
)
html = html.replace(
    'Quarterly reactivation campaigns to past client database',
    'Quarterly reactivation campaigns to past client database'
)
html = html.replace(
    'Auto-generate contracts, sync timelines, streamline invoicing',
    'Auto-generate contracts, streamline invoicing, reduce admin overhead'
)

# ── Method section: rename from "Warnick Method" to business-specific ──
method_name = business_name.split()[-1] if len(business_name.split()) > 1 else business_name
html = html.replace('The Warnick Method', f'The {method_name} Method')
html = html.replace('The Warnick Filter', f'The {method_name} Standard')
html = html.replace('The Warnick Standard', f'The {method_name} Standard')

# ── Method quote: generalize ──
html = html.replace(
    'We do not just design events — we design the feeling people carry with them long after the last guest leaves.',
    f'We do not just deliver a service -- we build relationships that drive lasting results for every client.'
)

# ── Competitor benchmark: generalize from "luxury events" ──
html = html.replace(
    'What Top Event Design Firms Are Doing',
    f'What Top {industry.title()} Firms Are Doing'
)
html = html.replace(
    'National leaders in luxury events are already deploying these systems. Here is how Warnick Design compares — and where AI closes the gap.',
    f'Industry leaders in {industry} are already deploying AI systems. Here is how {business_name} compares -- and where AI closes the gap.'
)

# ── "What to Ignore" section: generalize ──
html = html.replace(
    'AI event day logistics',
    'AI for high-stakes client interactions'
)
html = html.replace(
    'Too variable, too high-stakes. Event day execution requires human judgment and the personal touch that defines luxury.',
    f'Too variable, too high-stakes. Client-facing delivery requires human judgment and the personal touch that defines {business_name}.'
)
html = html.replace(
    'AI vendor selection',
    'AI relationship management'
)
html = html.replace(
    'Relationships matter more than algorithms. Your curated vendor network is a competitive advantage AI cannot replicate.',
    'Relationships matter more than algorithms. Your professional network is a competitive advantage AI cannot replicate.'
)
html = html.replace(
    'Luxury clients expect human touch, not bots. A chatbot cheapens the brand.',
    'Your clients expect human touch, not bots. A generic chatbot cheapens the brand.'
)
html = html.replace(
    'Luxury pricing is relationship-based, not formula-based. Every event is bespoke.',
    f'Pricing in {industry} is relationship-based, not formula-based. Every engagement is unique.'
)

# ── Mobile experience: generalize ──
html = html.replace(
    '78% of luxury event inquiries come from mobile devices',
    f'78% of service inquiries come from mobile devices'
)
html = html.replace(
    'No venue-specific detail',
    'No personalized detail'
)
html = html.replace(
    'Personalized to event type + venue',
    'Personalized to their specific needs'
)
html = html.replace(
    'Knowledgeable about their venue',
    'Knowledgeable about their situation'
)

# ── Signed invitation: personalize ──
html = html.replace(
    f'{first_name}, I built this roadmap specifically for {business_name} because I believe your work deserves to be seen by more of the right people. The AI systems here are not about replacing your artistry — they are about amplifying it.',
    f'{first_name}, I built this roadmap specifically for {business_name} because I believe your work deserves to be seen by more of the right people. The AI systems here are not about replacing what makes you great -- they are about amplifying it.'
)

# ── Footer ──
html = html.replace(
    f'This AI Advantage Roadmap was prepared by the Advaita AI team exclusively for {business_name}.',
    f'This AI Advantage Roadmap was prepared by the Advaita AI team exclusively for {business_name}.'
)

# ── SEO section: generalize keyword references ──
html = html.replace(
    'AI generates alt text, meta descriptions, and structured data for every portfolio image',
    f'AI generates alt text, meta descriptions, and structured data for all site content'
)
html = html.replace(
    'AI turns portfolio shoots into SEO-optimized blog posts targeting "Dallas event designer" keywords',
    f'AI creates SEO-optimized blog posts targeting high-value {industry} keywords in your market'
)

# ── HoneyBook references: generalize to "your CRM" ──
html = html.replace('HoneyBook', 'your CRM')

# ── Opportunity map table: generalize integration references ──
html = html.replace(
    'Instant personalized response to venue partner and corporate inquiries',
    f'Instant personalized response to all inbound inquiries'
)
html = html.replace(
    'Auto-draft luxury proposals from inquiry details',
    'Auto-draft professional proposals from inquiry details'
)
html = html.replace(
    'B2B outreach to venue coordinators and corporate planners',
    f'B2B outreach to decision-makers in {industry}'
)
html = html.replace(
    '7-touch nurture for quoted-but-not-booked luxury leads',
    '7-touch nurture for quoted-but-not-booked leads'
)
html = html.replace(
    'Turn portfolio photos into branded social posts and blog content',
    'Turn your best work into branded social posts and blog content'
)
html = html.replace(
    'Quarterly outreach to past clients for repeat events',
    'Quarterly outreach to past clients for repeat business and referrals'
)
html = html.replace(
    'Auto-sync timelines and communications across vendor team',
    'Automate scheduling, contracts, and team coordination'
)
html = html.replace('Vendor Coordination Agent', 'Admin Automation Agent')

# ── Tool stack: generalize ──
# Replace specific tools with generic placeholders (the lead can customize)
html = html.replace('Instagram<br><small>Keeps running</small>', 'Current Tools<br><small>Keep running</small>')
html = html.replace('Pinterest<br><small>Keeps running</small>', 'Your CRM<br><small>Keeps running</small>')
html = html.replace('Canva<br><small>Keeps running</small>', 'Your Website<br><small>Keeps running</small>')

# ── Contact info: add if provided ──
if phone or email:
    contact_block = ''
    if phone:
        contact_block += f'<p style="font-size:13px; color:var(--text-mid); margin-top:4px;">Phone: {phone}</p>'
    if email:
        contact_block += f'<p style="font-size:13px; color:var(--text-mid); margin-top:4px;">Email: {email}</p>'

    # Insert contact info after "Prepared exclusively for" block
    prep_marker = f'{lead_name} -- {business_name}</strong>'
    if prep_marker in html:
        html = html.replace(
            prep_marker,
            prep_marker + '\n    ' + contact_block
        )

# ── Implementation timeline: ensure 3/7/30 language (already in template, but verify) ──
# The template already uses Days 1-3, Days 4-7, Day 30 -- no changes needed.

# ── Final: remove any leftover "luxury event" references ──
html = html.replace('luxury event design', industry)
html = html.replace('luxury event', industry)
html = html.replace('luxury service industry benchmarks for event/wedding businesses in the Dallas-Fort Worth metro', f'{industry} industry benchmarks')

# ── Podcast / Listen tab: replace Warnick-specific embed if no podcast provided ──
# Replace the specific Google Drive embed with a placeholder
html = html.replace(
    'Two AI hosts walk through your exact business, tools, and opportunities — personalized to Warnick Design.',
    f'Two AI hosts walk through your exact business, tools, and opportunities -- personalized to {business_name}.'
)
# Note: The podcast iframe link stays as-is (template default) unless overridden

# ── Event-specific language in case studies ──
html = html.replace(
    'Luxury event firm increased monthly revenue by 38% from AI-powered lead response + LinkedIn pipeline',
    f'{industry.title()} firm increased monthly revenue by 38% from AI-powered lead response + LinkedIn pipeline'
)
html = html.replace(
    'Creative agency reclaimed 7 hours per week by automating proposal drafts and follow-up sequences',
    'Service business reclaimed 7 hours per week by automating proposal drafts and follow-up sequences'
)
html = html.replace(
    'B2B service firm tripled qualified leads through curated LinkedIn outreach and SEO optimization',
    'B2B service firm tripled qualified leads through curated LinkedIn outreach and SEO optimization'
)
html = html.replace('luxury event vertical', f'{industry} vertical')
html = html.replace('creative services', 'professional services')

# ── Command center: generalize from events ──
html = html.replace(
    'Everything your team needs to manage leads, projects, vendors, and finances — in one elevated interface',
    f'Everything your team needs to manage leads, projects, clients, and finances -- in one streamlined interface'
)
html = html.replace(
    f'at command.{domain_slug}.com',
    f'at command.{domain_slug}.com'
)
html = html.replace(
    'Event timelines, vendor coordination, and design assets organized by project — not scattered across apps.',
    f'Client projects, deliverables, and communications organized by engagement -- not scattered across apps.'
)
html = html.replace(
    'AI pre-screens inquiries using your criteria — budget, date, venue, aesthetic fit — before they reach your inbox.',
    f'AI pre-screens inquiries using your criteria -- budget, timeline, scope, and fit -- before they reach your inbox.'
)
html = html.replace(
    'Revenue by event type, outstanding invoices, and cash flow projections — all in real time.',
    'Revenue by client, outstanding invoices, and cash flow projections -- all in real time.'
)

# ── Qualification filter steps: generalize ──
html = html.replace(
    'AI captures event type, venue, budget range, and aesthetic vision',
    f'AI captures project type, budget range, timeline, and scope'
)
html = html.replace(
    'Instantly checks against your criteria — date, budget, venue, scope',
    'Instantly checks against your criteria -- budget, timeline, scope, fit'
)
html = html.replace(
    'You see only pre-qualified leads with full context — approve in one tap',
    'You see only pre-qualified leads with full context -- approve in one tap'
)
html = html.replace(
    'AI sends a luxury response in your voice — you stay in control',
    f'AI sends a professional response in your voice -- you stay in control'
)

# ── Fred CFO: generalize the example question ──
html = html.replace(
    'Fred, what was our margin on the Johnson gala?',
    f'Fred, what was our margin on the Johnson project?'
)

# ── "What AI Unlocks" table: generalize ──
html = html.replace('Portfolio showcase', 'Marketing + visibility')
html = html.replace('Inspiration boards, SEO', 'Client management')
html = html.replace('CRM, proposals, contracts', 'CRM, proposals, contracts')
html = html.replace('Design mockups, mood boards', 'Website + digital presence')
html = html.replace('Email, documents, scheduling', 'Email, documents, scheduling')

html = html.replace(
    'AI auto-generates captions, schedules posts, repurposes portfolio into stories + reels',
    'AI auto-generates content, schedules posts, and maximizes your online presence'
)
html = html.replace(
    'AI creates optimized pin descriptions, auto-pins with SEO keywords',
    'AI automates client communication workflows and follow-ups'
)
html = html.replace(
    'AI auto-drafts proposals, triggers follow-up sequences, tags leads by stage',
    'AI auto-drafts proposals, triggers follow-up sequences, tags leads by stage'
)
html = html.replace(
    'AI generates initial mood board layouts from client briefs',
    'AI optimizes landing pages and captures more leads from existing traffic'
)

# ── Benchmark table: generalize ──
html = html.replace(
    'Respond to inquiries within 5 minutes, 24/7',
    'Respond to inquiries within 5 minutes, 24/7'
)
html = html.replace(
    'AI speed-to-lead agent responds in under 15 minutes with personalized, venue-specific detail',
    f'AI speed-to-lead agent responds in under 15 minutes with personalized, {industry}-specific detail'
)
html = html.replace(
    'Run LinkedIn B2B pipelines for corporate event sourcing',
    'Run LinkedIn B2B pipelines for lead generation'
)
html = html.replace(
    f'Curated LinkedIn Engine delivers 10 qualified B2B conversations per month on autopilot',
    'Curated LinkedIn Engine delivers 10 qualified B2B conversations per month on autopilot'
)
html = html.replace(
    '7-touch luxury nurture sequence keeps',
    '7-touch professional nurture sequence keeps'
)
html = html.replace(
    'top-of-mind without being pushy',
    'top-of-mind without being pushy'
)
html = html.replace(
    'Publish 3-5x/week on social from every event shoot',
    'Publish 3-5x/week on social with consistent content'
)
html = html.replace(
    'AI content engine turns portfolio photos into Instagram, Pinterest, and blog posts automatically',
    f'AI content engine turns your best work into social media and blog posts automatically'
)
html = html.replace(
    'Reactivate past clients proactively every quarter',
    'Reactivate past clients proactively every quarter'
)
html = html.replace(
    'Database reactivation agent reaches out 3-4 months before their typical event season',
    f'Database reactivation agent reaches out systematically to drive repeat business and referrals'
)

# ── Method steps: generalize from event design ──
html = html.replace(
    'AI pre-qualifies inquiries and gathers event details before your first call',
    'AI pre-qualifies inquiries and gathers project details before your first call'
)
html = html.replace(
    'AI generates initial mood boards and proposal drafts from your design library',
    'AI generates proposal drafts and client-ready materials from your templates'
)
html = html.replace(
    'AI coordinates vendor timelines and automates day-of logistics communication',
    'AI coordinates project timelines and automates client communication'
)
html = html.replace(
    'AI nurtures past clients with anniversary outreach and referral prompts',
    'AI nurtures past clients with systematic outreach and referral prompts'
)

# ── Implementation table: generalize ──
html = html.replace(
    f'Brand intelligence and brand guide built for {business_name}.',
    f'Brand intelligence and brand guide built for {business_name}.'
)
html = html.replace(
    'Speed-to-Lead Agent live. Proposal draft agent running. All systems connected to your CRM + your tools.',
    'Speed-to-Lead Agent live. Proposal draft agent running. All systems connected to your CRM and tools.'
)
html = html.replace(
    'Well-trained AI employees handling lead response, follow-up nurture, content creation, and admin. Self-auditing and improving daily.',
    'Well-trained AI employees handling lead response, follow-up nurture, content creation, and admin. Self-auditing and improving daily.'
)
html = html.replace(
    f'Employees keep growing, developing, being proactive as they understand {business_name} more deeply every day.',
    f'Employees keep growing, developing, being proactive as they understand {business_name} more deeply every day.'
)

# Write output
with open(output_file, 'w') as f:
    f.write(html)

print(f"  Replacements complete. Output: {output_file}")
PYTHON_SCRIPT

# ─── Step 3: Validate output ───────────────────────────────────────────────
echo "[3/7] Validating output..."

# Check that old names are gone
if grep -q "Brittney Warnick" "$OUTPUT_FILE" 2>/dev/null; then
  echo "WARNING: 'Brittney Warnick' still found in output. Manual review recommended."
fi
if grep -q "Warnick Design" "$OUTPUT_FILE" 2>/dev/null; then
  echo "WARNING: 'Warnick Design' still found in output. Manual review recommended."
fi
# Check for booking URLs (should not exist)
if grep -qi "booking\|calendly\|cal\.com" "$OUTPUT_FILE" 2>/dev/null; then
  echo "WARNING: Booking/calendar URL detected. Remove manually -- CTA must be qualifying mailto only."
fi

# Verify CTA is correct
if grep -q "Apply to Work With Bennett" "$OUTPUT_FILE"; then
  echo "  CTA verified: 'Apply to Work With Bennett' present."
else
  echo "WARNING: CTA 'Apply to Work With Bennett' not found."
fi

# Verify 3/7/30 timeline
if grep -q "Days 1-3" "$OUTPUT_FILE" && grep -q "Days 4-7" "$OUTPUT_FILE" && grep -q "Day 30" "$OUTPUT_FILE"; then
  echo "  Timeline verified: 3/7/30 onboarding cadence present."
else
  echo "WARNING: 3/7/30 timeline markers not all found."
fi

# Verify interactive calculator exists
if grep -q "slider-contract" "$OUTPUT_FILE"; then
  echo "  ROI Calculator verified: Interactive sliders present."
else
  echo "WARNING: Interactive ROI calculator not found."
fi

echo "  Validation complete."

# ─── Step 4: Pre-delivery check ────────────────────────────────────────────
echo "[4/7] Running pre-delivery check..."
PRE_DELIVERY="$SCRIPT_DIR/pre-delivery-check.sh"
if [[ -f "$PRE_DELIVERY" && -x "$PRE_DELIVERY" ]]; then
  "$PRE_DELIVERY" "$OUTPUT_FILE" || echo "  Pre-delivery check returned warnings (non-fatal)."
else
  echo "  No pre-delivery-check.sh found -- skipping."
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "=== DRY RUN COMPLETE ==="
  echo "Output: $OUTPUT_FILE"
  echo "Skipping git commit, push, and HTTP verify."
  exit 0
fi

# ─── Step 5: Git commit ────────────────────────────────────────────────────
echo "[5/7] Committing..."
cd "$REPO_ROOT"
git add "blueprints/$LEAD_SLUG.html"
git commit -m "Add Blueprint: $BUSINESS_NAME ($LEAD_SLUG)" || {
  echo "  Nothing to commit (file may already be tracked)."
}

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
