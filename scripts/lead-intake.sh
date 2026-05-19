#!/bin/bash
# Blueprint AI Pipeline — Stage 1: Lead Intake + Research
# Usage: ./lead-intake.sh <business_url> <lead_name> [--output lead-profile.json]
#
# Scrapes lead's website for business data, generates lead-profile.json

set -euo pipefail

# Source structured logging
SCRIPT_NAME="lead-intake.sh"
source "$(dirname "$0")/lib-log.sh" 2>/dev/null || true

if [ $# -lt 2 ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 <business_url> <lead_name> [--output lead-profile.json]"
    echo ""
    echo "Example: $0 https://smithplumbing.com 'John Smith' --output john-smith.json"
    exit 1
fi

URL="$1"
LEAD_NAME="$2"
OUTPUT="${4:-lead-profile.json}"
[ "${3:-}" = "--output" ] && OUTPUT="${4:-lead-profile.json}"

# --- Input validation ---
# URL format check
if ! echo "$URL" | grep -qE '^https?://[a-zA-Z0-9]'; then
    echo "ERROR: Invalid URL format: $URL (must start with http:// or https://)"
    exit 1
fi

# Name length limits
if [ ${#LEAD_NAME} -lt 2 ]; then
    echo "ERROR: Lead name too short (min 2 chars): '$LEAD_NAME'"
    exit 1
fi
if [ ${#LEAD_NAME} -gt 100 ]; then
    echo "ERROR: Lead name too long (max 100 chars): '${LEAD_NAME:0:20}...'"
    exit 1
fi

# Name must contain at least one letter
if ! echo "$LEAD_NAME" | grep -qE '[a-zA-Z]'; then
    echo "ERROR: Lead name must contain at least one letter: '$LEAD_NAME'"
    exit 1
fi

LEAD_FIRST=$(echo "$LEAD_NAME" | awk '{print $1}')
SLUG=$(echo "$LEAD_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

log_info "$SCRIPT_NAME" "intake_start" "Scraping $URL for $LEAD_NAME" ",\"url\":\"$URL\",\"lead\":\"$LEAD_NAME\"" 2>/dev/null || true
echo "Scraping $URL for $LEAD_NAME..."

# Fetch website HTML with retry (3 attempts, exponential backoff)
PAGE_HTML=""
for attempt in 1 2 3; do
    PAGE_HTML=$(curl -sL --max-time 15 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" "$URL" 2>/dev/null || echo "")
    if [ -n "$PAGE_HTML" ]; then
        break
    fi
    echo "  Retry $attempt/3 for $URL (waiting ${attempt}s)..."
    sleep "$attempt"
done

if [ -z "$PAGE_HTML" ]; then
    echo "WARNING: Could not fetch $URL — generating minimal profile"
    python3 - "$LEAD_NAME" "$LEAD_FIRST" "$SLUG" "$URL" "$OUTPUT" <<'PYEOF'
import json, sys
lead_name, lead_first, slug, url, output = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
profile = {
    "lead_name": lead_name,
    "lead_first_name": lead_first,
    "business_name": lead_name,
    "slug": slug,
    "url": url,
    "accent_color": "#007AFF",
    "industry": "business services",
    "services": [],
    "tools": "",
    "market": "local customers",
    "service_type": "professional services",
    "speed_to_lead_context": "capturing every inquiry before competitors respond",
    "phone": "",
    "email": "",
    "scraped": False,
    "needs_manual_review": True
}
with open(output, "w") as f:
    json.dump(profile, f, indent=2)
print(f"Minimal profile: {output}")
PYEOF
    exit 0
fi

# Extract data with Python — HTML passed via stdin, args via sys.argv (safe from injection)
echo "$PAGE_HTML" | python3 - "$URL" "$LEAD_NAME" "$OUTPUT" <<'PYEOF'
import re, json, sys

html = sys.stdin.read()[:50000]
url = sys.argv[1]
lead_name = sys.argv[2]
output = sys.argv[3]

# Extract title
title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
title = title_match.group(1).strip() if title_match else lead_name

# Extract business name from title (before | or - or :)
business_name = re.split(r'[|\-:]', title)[0].strip() if title else lead_name

# Extract phone numbers
phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', html)
phone = phones[0] if phones else ''

# Extract emails
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', html)
filtered_emails = [e for e in emails if not any(x in e.lower() for x in ['wix','squarespace','wordpress','google','facebook','sentry'])]
email = filtered_emails[0] if filtered_emails else ''

# Extract accent/brand color from CSS
colors = re.findall(r'(?:background-color|color|background)\s*:\s*(#[0-9a-fA-F]{6})', html)
brand_colors = [c for c in colors if c.lower() not in ('#000000','#ffffff','#f5f5f5','#333333','#666666','#999999','#cccccc','#eeeeee','#f0f0f0','#1d1d1f')]
accent_color = brand_colors[0] if brand_colors else '#007AFF'

# Extract meta description
meta_desc = ''
meta_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
if meta_match:
    meta_desc = meta_match.group(1)

# Industry auto-detection from page text
INDUSTRY_KEYWORDS = {
    'plumbing': ['plumb', 'drain', 'pipe', 'water heater', 'sewer', 'faucet'],
    'HVAC': ['hvac', 'heating', 'cooling', 'air condition', 'furnace', 'duct'],
    'roofing': ['roof', 'shingle', 'gutter', 'siding'],
    'electrical': ['electric', 'wiring', 'panel', 'outlet', 'circuit'],
    'landscaping': ['landscape', 'lawn', 'mow', 'irrigation', 'garden', 'tree service'],
    'interior design': ['interior design', 'decor', 'staging', 'remodel'],
    'real estate': ['real estate', 'realtor', 'property', 'listing', 'mls', 'brokerage'],
    'dental': ['dental', 'dentist', 'orthodont', 'teeth', 'oral'],
    'medical': ['medical', 'clinic', 'doctor', 'physician', 'patient', 'healthcare'],
    'legal': ['law firm', 'attorney', 'lawyer', 'legal', 'litigation'],
    'insurance': ['insurance', 'coverage', 'policy', 'claim', 'underwriting'],
    'franchise operations': ['franchise', 'franchis', 'multi-unit', 'multi-location'],
    'restaurant': ['restaurant', 'dining', 'menu', 'chef', 'catering', 'food service'],
    'automotive': ['auto', 'car', 'vehicle', 'mechanic', 'collision', 'tire'],
    'fitness': ['fitness', 'gym', 'workout', 'personal training', 'crossfit'],
    'salon and spa': ['salon', 'spa', 'hair', 'beauty', 'nail', 'massage'],
    'photography': ['photo', 'portrait', 'wedding photo', 'studio', 'videograph'],
    'consulting': ['consult', 'advisory', 'strategy', 'coaching', 'business development'],
    'renewable energy': ['solar', 'renewable', 'energy', 'wind', 'sustainable', 'green energy'],
    'vacation rentals': ['vacation rental', 'airbnb', 'vrbo', 'short-term rental', 'property management'],
    'construction': ['construct', 'builder', 'general contractor', 'remodel', 'renovation'],
    'pest control': ['pest', 'exterminator', 'termite', 'rodent'],
    'cleaning services': ['cleaning', 'janitorial', 'maid', 'pressure wash'],
    'accounting': ['accounting', 'bookkeep', 'cpa', 'tax prep', 'payroll'],
    'marketing agency': ['marketing agency', 'digital marketing', 'seo', 'ad agency', 'ppc'],
}
text_lower = (html + ' ' + meta_desc).lower()
industry = 'business services'
best_score = 0
for ind, keywords in INDUSTRY_KEYWORDS.items():
    score = sum(1 for kw in keywords if kw in text_lower)
    if score > best_score:
        best_score = score
        industry = ind

slug = lead_name.lower().replace(' ', '-') if lead_name else 'unknown'
lead_first = lead_name.split()[0] if lead_name else 'there'

# Sales Intelligence: extract social links
social = {}
fb = re.search(r'href=["\']?(https?://(?:www\.)?facebook\.com/[^\s"\'<>]+)', html, re.I)
if fb: social['facebook'] = fb.group(1)
ig = re.search(r'href=["\']?(https?://(?:www\.)?instagram\.com/[^\s"\'<>]+)', html, re.I)
if ig: social['instagram'] = ig.group(1)
li = re.search(r'href=["\']?(https?://(?:www\.)?linkedin\.com/[^\s"\'<>]+)', html, re.I)
if li: social['linkedin'] = li.group(1)
yt = re.search(r'href=["\']?(https?://(?:www\.)?youtube\.com/[^\s"\'<>]+)', html, re.I)
if yt: social['youtube'] = yt.group(1)
gm = re.search(r'href=["\']?(https?://(?:www\.)?google\.com/maps[^\s"\'<>]+)', html, re.I)
if gm: social['google_maps'] = gm.group(1)

# Sales Intelligence: extract review/testimonial signals
review_keywords = ['review', 'testimonial', 'rating', 'star', '5-star', 'customer said', 'what our clients']
review_signal = sum(1 for kw in review_keywords if kw in text_lower)
has_reviews = review_signal >= 2

# Sales Intelligence: extract service list items
svc_items = re.findall(r'<li[^>]*>\s*([A-Z][^<]{5,60})</li>', html)
services = list(set(s.strip() for s in svc_items[:15]))

# Sales Intelligence: detect CTA/form presence
has_form = bool(re.search(r'<form[^>]*>', html, re.I))
has_cta_button = bool(re.search(r'(?:book|schedule|call|contact|get.?(?:a|free)|request)\s', text_lower))

# UTM tracking: propagate through pipeline (Item 2)
import urllib.parse
parsed_url = urllib.parse.urlparse(url)
qs = urllib.parse.parse_qs(parsed_url.query)
utm_source = qs.get('utm_source', [''])[0]
utm_medium = qs.get('utm_medium', [''])[0]
utm_campaign = qs.get('utm_campaign', [''])[0]

# Lead source normalization (Item 4)
lead_source = 'unknown'
if utm_source:
    lead_source = utm_source.lower().strip()
elif 'facebook' in url.lower():
    lead_source = 'facebook'
elif 'linkedin' in url.lower():
    lead_source = 'linkedin'
elif 'google' in url.lower():
    lead_source = 'google'
else:
    lead_source = 'direct'

# Form submission analytics stub (Item 3)
form_count = len(re.findall(r'<form[^>]*>', html, re.I))
input_count = len(re.findall(r'<input[^>]*>', html, re.I))
form_analytics = {
    'form_count': form_count,
    'input_field_count': input_count,
    'has_conversion_form': has_form and input_count >= 3,
}

# Tech stack detection (Item B9 - early extraction)
tech_stack = []
if re.search(r'wp-content|wordpress', html, re.I): tech_stack.append('WordPress')
if re.search(r'Shopify\.theme|cdn\.shopify', html, re.I): tech_stack.append('Shopify')
if re.search(r'squarespace', html, re.I): tech_stack.append('Squarespace')
if re.search(r'wix\.com|wixsite', html, re.I): tech_stack.append('Wix')
if re.search(r'webflow', html, re.I): tech_stack.append('Webflow')
if re.search(r'next|__next', html, re.I): tech_stack.append('Next.js')
if re.search(r'react', html, re.I) and 'Next.js' not in tech_stack: tech_stack.append('React')
if re.search(r'google.*analytics|gtag|UA-\d+|G-[A-Z0-9]+', html, re.I): tech_stack.append('Google Analytics')
if re.search(r'google.*tag.*manager|gtm\.js', html, re.I): tech_stack.append('GTM')
if re.search(r'facebook.*pixel|fbq\(', html, re.I): tech_stack.append('FB Pixel')
if re.search(r'hubspot', html, re.I): tech_stack.append('HubSpot')

# Lead profile photo/logo extraction (Item 10)
logo_url = ''
logo_match = re.search(r'<(?:img|link)[^>]*(?:logo|brand|site-icon)[^>]*(?:src|href)=["\']([^"\']+)["\']', html, re.I)
if not logo_match:
    logo_match = re.search(r'<link[^>]*rel=["\'](?:icon|apple-touch-icon)["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
if logo_match:
    logo_url = logo_match.group(1)
    if logo_url.startswith('/'):
        logo_url = urllib.parse.urljoin(url, logo_url)

profile = {
    'lead_name': lead_name,
    'lead_first_name': lead_first,
    'business_name': business_name,
    'slug': slug,
    'url': url,
    'accent_color': accent_color,
    'industry': industry,
    'meta_description': meta_desc[:200],
    'services': services,
    'social_links': social,
    'has_reviews': has_reviews,
    'review_signal_score': review_signal,
    'has_form': has_form,
    'has_cta': has_cta_button,
    'form_analytics': form_analytics,
    'tools': '',
    'market': 'local and regional customers',
    'service_type': 'professional services',
    'speed_to_lead_context': 'capturing every inquiry before competitors respond',
    'phone': phone,
    'email': email,
    'scraped': True,
    'needs_manual_review': best_score < 2,
    'blueprint_url': f'https://bennett-maxwell.github.io/fki-preview/blueprints/{slug}.html',
    'website_url': f'https://bennett-maxwell.github.io/fki-preview/{slug}-website/',
    'podcast_url': '',
    'apply_subject': f'{lead_name} - Blueprint Application',
    'utm_source': utm_source,
    'utm_medium': utm_medium,
    'utm_campaign': utm_campaign,
    'lead_source': lead_source,
    'tech_stack': tech_stack,
    'logo_url': logo_url,
    'lead_status': 'new',
}

with open(output, 'w') as f:
    json.dump(profile, f, indent=2)

print(f'Profile: {output}')
print(f'  Business: {business_name}')
print(f'  Industry: {industry} (confidence: {best_score} keyword hits)')
print(f'  Phone: {phone or "not found"}')
print(f'  Email: {email or "not found"}')
print(f'  Color: {accent_color}')
PYEOF

# Stamp intake timestamp into profile
python3 -c "
import json, sys, datetime
p = json.load(open(sys.argv[1]))
p['intake_ts'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
p.setdefault('pipeline_version', '2.1')
json.dump(p, open(sys.argv[1], 'w'), indent=2)
" "$OUTPUT" 2>/dev/null || true

log_success "$SCRIPT_NAME" "intake_complete" "Profile generated: $OUTPUT" ",\"output\":\"$OUTPUT\"" 2>/dev/null || true
echo "Done. Review $OUTPUT before proceeding to Stage 2."
