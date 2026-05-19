#!/bin/bash
# Blueprint AI Pipeline — Stage 1: Lead Intake + Research
# Usage: ./lead-intake.sh <business_url> <lead_name> [--output lead-profile.json]
#
# Scrapes lead's website for business data, generates lead-profile.json

set -euo pipefail

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

LEAD_FIRST=$(echo "$LEAD_NAME" | awk '{print $1}')
SLUG=$(echo "$LEAD_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

echo "Scraping $URL for $LEAD_NAME..."

# Fetch website HTML
PAGE_HTML=$(curl -sL --max-time 15 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" "$URL" 2>/dev/null || echo "")

if [ -z "$PAGE_HTML" ]; then
    echo "WARNING: Could not fetch $URL — generating minimal profile"
    python3 << PYEOF
import json
profile = {
    "lead_name": "$LEAD_NAME",
    "lead_first_name": "$LEAD_FIRST",
    "business_name": "$LEAD_NAME",
    "slug": "$SLUG",
    "url": "$URL",
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
with open("$OUTPUT", "w") as f:
    json.dump(profile, f, indent=2)
print(f"Minimal profile: $OUTPUT")
PYEOF
    exit 0
fi

# Extract data with Python
python3 << 'PYEOF'
import re
import json
import sys

html = """PAGE_CONTENT"""
url = sys.argv[1] if len(sys.argv) > 1 else ""
lead_name = sys.argv[2] if len(sys.argv) > 2 else ""
output = sys.argv[3] if len(sys.argv) > 3 else "lead-profile.json"

# Extract title
title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
title = title_match.group(1).strip() if title_match else lead_name

# Extract business name from title (before | or - or :)
business_name = re.split(r'[|\-:]', title)[0].strip() if title else lead_name

# Extract phone numbers
phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', html)
phone = phones[0] if phones else ""

# Extract emails
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', html)
# Filter out common non-business emails
filtered_emails = [e for e in emails if not any(x in e.lower() for x in ['wix', 'squarespace', 'wordpress', 'google', 'facebook', 'sentry'])]
email = filtered_emails[0] if filtered_emails else ""

# Try to extract accent/brand color from CSS
colors = re.findall(r'(?:background-color|color|background)\s*:\s*(#[0-9a-fA-F]{6})', html)
# Filter out black, white, grays
brand_colors = [c for c in colors if c.lower() not in ('#000000', '#ffffff', '#f5f5f5', '#333333', '#666666', '#999999', '#cccccc', '#eeeeee', '#f0f0f0', '#1d1d1f')]
accent_color = brand_colors[0] if brand_colors else "#007AFF"

# Extract meta description for industry hints
meta_desc = ""
meta_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
if meta_match:
    meta_desc = meta_match.group(1)

# Build profile
slug = lead_name.lower().replace(' ', '-') if lead_name else "unknown"
lead_first = lead_name.split()[0] if lead_name else "there"

profile = {
    "lead_name": lead_name,
    "lead_first_name": lead_first,
    "business_name": business_name,
    "slug": slug,
    "url": url,
    "accent_color": accent_color,
    "industry": "business services",
    "meta_description": meta_desc[:200],
    "services": [],
    "tools": "",
    "market": "local and regional customers",
    "service_type": "professional services",
    "speed_to_lead_context": "capturing every inquiry before competitors respond",
    "phone": phone,
    "email": email,
    "scraped": True,
    "needs_manual_review": True,
    "blueprint_url": f"https://bennett-maxwell.github.io/fki-preview/blueprints/{slug}.html",
    "website_url": f"https://bennett-maxwell.github.io/fki-preview/{slug}-website/",
    "podcast_url": "",
    "apply_subject": f"{lead_name} - Blueprint Application"
}

with open(output, "w") as f:
    json.dump(profile, f, indent=2)

print(f"Profile created: {output}")
print(f"  Business: {business_name}")
print(f"  Phone: {phone or 'not found'}")
print(f"  Email: {email or 'not found'}")
print(f"  Accent: {accent_color}")
print(f"  Needs review: {profile['needs_manual_review']}")
PYEOF

# Replace PAGE_CONTENT placeholder with actual content (escaped)
ESCAPED_HTML=$(echo "$PAGE_HTML" | python3 -c "import sys; print(sys.stdin.read().replace('\\\\','\\\\\\\\').replace('\"','\\\\\"')[:50000])")

python3 -c "
import re, json, sys

html = '''$PAGE_HTML'''[:50000]
url = '$URL'
lead_name = '$LEAD_NAME'
output = '$OUTPUT'

title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
title = title_match.group(1).strip() if title_match else lead_name
business_name = re.split(r'[|\-:]', title)[0].strip() if title else lead_name

phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', html)
phone = phones[0] if phones else ''

emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', html)
filtered_emails = [e for e in emails if not any(x in e.lower() for x in ['wix','squarespace','wordpress','google','facebook','sentry'])]
email = filtered_emails[0] if filtered_emails else ''

colors = re.findall(r'(?:background-color|color|background)\s*:\s*(#[0-9a-fA-F]{6})', html)
brand_colors = [c for c in colors if c.lower() not in ('#000000','#ffffff','#f5f5f5','#333333','#666666','#999999','#cccccc','#eeeeee','#f0f0f0','#1d1d1f')]
accent_color = brand_colors[0] if brand_colors else '#007AFF'

slug = lead_name.lower().replace(' ', '-')
lead_first = lead_name.split()[0] if lead_name else 'there'

profile = {
    'lead_name': lead_name,
    'lead_first_name': lead_first,
    'business_name': business_name,
    'slug': slug,
    'url': url,
    'accent_color': accent_color,
    'industry': 'business services',
    'services': [],
    'tools': '',
    'market': 'local and regional customers',
    'service_type': 'professional services',
    'speed_to_lead_context': 'capturing every inquiry before competitors respond',
    'phone': phone,
    'email': email,
    'scraped': True,
    'needs_manual_review': True,
    'blueprint_url': f'https://bennett-maxwell.github.io/fki-preview/blueprints/{slug}.html',
    'website_url': f'https://bennett-maxwell.github.io/fki-preview/{slug}-website/',
    'podcast_url': '',
    'apply_subject': f'{lead_name} - Blueprint Application'
}

with open(output, 'w') as f:
    json.dump(profile, f, indent=2)

print(f'Profile: {output}')
print(f'  Business: {business_name}')
print(f'  Phone: {phone or \"not found\"}')
print(f'  Email: {email or \"not found\"}')
print(f'  Color: {accent_color}')
" 2>/dev/null || echo "Fallback: minimal profile created"

echo "Done. Review $OUTPUT before proceeding to Stage 2."
