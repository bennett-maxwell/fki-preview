#!/usr/bin/env bash
# build-website.sh -- Build a demo website from a lead profile JSON and the website template.
#
# Usage:
#   ./scripts/build-website.sh path/to/lead-profile.json
#
# The lead-profile.json must contain:
#   {
#     "business_name": "Acme Corp",
#     "lead_name": "Jane Doe",
#     "slug": "acme-corp",
#     "accent_color": "#2A5C8A",
#     "accent_dark": "#1e4568",
#     "tagline": "Professional Services, Elevated by AI",
#     "hero_description": "One-liner about the business...",
#     "phone": "(555) 123-4567",
#     "email": "info@acmecorp.com",
#     "apply_email": "bennett@franchiseki.com",
#     "apply_subject": "Application -- Acme Corp",
#     "services": [
#       {"name": "Service One", "description": "Description here.", "icon": "<svg viewBox=\"0 0 24 24\">...</svg>"},
#       ...
#     ],
#     "ai_features": [
#       {"name": "Feature One", "description": "Description here.", "icon": "<svg viewBox=\"0 0 24 24\">...</svg>"},
#       ...
#     ]
#   }
#
# Default SVG icons are provided if icon fields are omitted.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$REPO_ROOT/templates/website-template.html"

# ---------- Validate inputs ----------
if [ $# -lt 1 ]; then
  echo "Usage: $0 <lead-profile.json>"
  exit 1
fi

PROFILE="$1"

if [ ! -f "$PROFILE" ]; then
  echo "ERROR: Profile not found: $PROFILE"
  exit 1
fi

if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: Template not found: $TEMPLATE"
  exit 1
fi

# ---------- Check dependencies ----------
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 is required"
  exit 1
fi

if ! command -v git &>/dev/null; then
  echo "ERROR: git is required"
  exit 1
fi

# ---------- Build website via python3 ----------
python3 - "$TEMPLATE" "$PROFILE" "$REPO_ROOT" <<'PYEOF'
import sys, json, os, html

template_path = sys.argv[1]
profile_path = sys.argv[2]
repo_root = sys.argv[3]

with open(template_path, 'r') as f:
    tpl = f.read()

with open(profile_path, 'r') as f:
    profile = json.load(f)

# ---------- Extract fields with defaults ----------
business_name = profile.get('business_name', 'Business Name')
lead_name = profile.get('lead_name', '')
slug = profile.get('slug', business_name.lower().replace(' ', '-').replace("'", ''))
accent_color = profile.get('accent_color', '#2A5C8A')
accent_dark = profile.get('accent_dark', '#1e4568')
tagline = profile.get('tagline', f'{business_name}, Elevated by AI')
hero_description = profile.get('hero_description', f'{business_name} combines expert service with intelligent automation -- faster responses, smarter operations, and a seamless client experience from first contact to final delivery.')
phone = profile.get('phone', '')
email_addr = profile.get('email', '')
apply_email = profile.get('apply_email', 'bennett@franchiseki.com')
apply_subject = profile.get('apply_subject', f'Application -- {business_name}')
services = profile.get('services', [])
ai_features = profile.get('ai_features', [])

# ---------- Default SVG icons ----------
DEFAULT_SERVICE_ICONS = [
    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
    '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>',
    '<svg viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
]

DEFAULT_AI_ICONS = [
    '<svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    '<svg viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
]

# ---------- Normalize services/ai_features to dicts ----------
def normalize_items(items, default_desc=''):
    result = []
    for item in items:
        if isinstance(item, str):
            result.append({'name': item, 'description': default_desc})
        elif isinstance(item, dict):
            result.append(item)
    return result

industry_val = profile.get('industry', 'professional services')
services = normalize_items(services, f'Professional {industry_val} service tailored to your needs.')
ai_features = normalize_items(ai_features, f'AI-powered automation for {industry_val} businesses.')

# ---------- Render service cards ----------
service_html_parts = []
for i, svc in enumerate(services):
    icon = svc.get('icon', DEFAULT_SERVICE_ICONS[i % len(DEFAULT_SERVICE_ICONS)])
    name = html.escape(svc.get('name', f'Service {i+1}'))
    desc = html.escape(svc.get('description', ''))
    service_html_parts.append(f'''      <div class="service-card">
        <div class="service-icon">
          {icon}
        </div>
        <h3>{name}</h3>
        <p>{desc}</p>
      </div>''')
services_rendered = '\n'.join(service_html_parts)

# ---------- Render AI feature cards ----------
ai_html_parts = []
for i, feat in enumerate(ai_features):
    icon = feat.get('icon', DEFAULT_AI_ICONS[i % len(DEFAULT_AI_ICONS)])
    name = html.escape(feat.get('name', f'AI Feature {i+1}'))
    desc = html.escape(feat.get('description', ''))
    ai_html_parts.append(f'''      <div class="ai-card">
        <div class="ai-card-icon">
          {icon}
        </div>
        <h3>{name}</h3>
        <p>{desc}</p>
      </div>''')
ai_features_rendered = '\n'.join(ai_html_parts)

# ---------- Render service select options ----------
options_parts = []
for svc in services:
    val = svc.get('name', '').lower().replace(' ', '-')
    label = html.escape(svc.get('name', ''))
    options_parts.append(f'            <option value="{val}">{label}</option>')
service_options = '\n'.join(options_parts)

# ---------- Perform replacements ----------
output = tpl
output = output.replace('{{BUSINESS_NAME}}', html.escape(business_name))
output = output.replace('{{LEAD_NAME}}', html.escape(lead_name))
output = output.replace('{{ACCENT_COLOR}}', accent_color)
output = output.replace('{{ACCENT_DARK}}', accent_dark)
output = output.replace('{{TAGLINE}}', html.escape(tagline))
output = output.replace('{{HERO_DESCRIPTION}}', html.escape(hero_description))
output = output.replace('{{PHONE}}', html.escape(phone))
output = output.replace('{{EMAIL}}', html.escape(email_addr))
output = output.replace('{{APPLY_EMAIL}}', apply_email)
output = output.replace('{{APPLY_SUBJECT}}', apply_subject.replace(' ', '%20'))
output = output.replace('      <!-- SERVICES_RENDERED -->', services_rendered)
output = output.replace('      <!-- AI_FEATURES_RENDERED -->', ai_features_rendered)
output = output.replace('            <!-- SERVICE_OPTIONS -->', service_options)

# ---------- Inject build metadata ----------
import datetime
build_ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
meta_comment = f'<!-- Blueprint AI Pipeline v2.1 | Website Built: {build_ts} | Lead: {html.escape(lead_name)} | Business: {html.escape(business_name)} -->\n'
output = meta_comment + output

# ---------- Write output ----------
out_dir = os.path.join(repo_root, slug + '-website')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'index.html')

with open(out_path, 'w') as f:
    f.write(output)

print(f"SLUG={slug}")
print(f"OUTPUT={out_path}")
PYEOF

# ---------- Capture slug from profile (reuse already-loaded data) ----------
SLUG=$(python3 -c "import json,sys; p=json.load(open(sys.argv[1])); print(p.get('slug', p.get('business_name','site').lower().replace(' ','-').replace(\"'\",''))+'-website')" "$PROFILE")
OUTPUT_DIR="$REPO_ROOT/$SLUG"
OUTPUT_FILE="$OUTPUT_DIR/index.html"

# Stamp website build timestamp into profile
python3 -c "
import json, sys, datetime
p = json.load(open(sys.argv[1]))
p['website_ts'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
json.dump(p, open(sys.argv[1], 'w'), indent=2)
" "$PROFILE" 2>/dev/null || true

echo ""
echo "--- Build Complete ---"
echo "  Slug:   $SLUG"
echo "  Output: $OUTPUT_FILE"

# ---------- Git commit and push ----------
cd "$REPO_ROOT"

if [ ! -d ".git" ]; then
  echo "WARNING: Not a git repo. Skipping commit/push."
  echo "  File written to: $OUTPUT_FILE"
  exit 0
fi

git add "$SLUG/index.html"
git commit -m "Add demo website for $SLUG" || {
  echo "NOTE: Nothing to commit (file may already be up to date)."
}

echo "Pushing to origin..."
git push origin HEAD 2>&1 || {
  echo "ERROR: git push failed. File is saved locally at: $OUTPUT_FILE"
  exit 1
}

echo ""
echo "--- Deployed ---"

# ---------- Verify HTTP 200 ----------
# Determine GitHub Pages URL from remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if echo "$REMOTE_URL" | grep -q "github.com"; then
  # Extract owner/repo
  OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's#.*github\.com[:/]##; s#\.git$##')
  OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
  REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
  PAGES_URL="https://${OWNER}.github.io/${REPO}/${SLUG}/"

  echo "  Pages URL: $PAGES_URL"
  echo "  Waiting 10s for GitHub Pages deployment..."
  sleep 10

  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PAGES_URL" 2>/dev/null || echo "000")
  if [ "$HTTP_CODE" = "200" ]; then
    echo "  HTTP 200 -- LIVE"
  elif [ "$HTTP_CODE" = "404" ]; then
    echo "  HTTP 404 -- Pages may still be deploying. Check in 1-2 minutes: $PAGES_URL"
  else
    echo "  HTTP $HTTP_CODE -- Check manually: $PAGES_URL"
  fi
else
  echo "  Non-GitHub remote. Verify deployment manually."
fi

echo ""
echo "Done."
