#!/usr/bin/env python3
"""Validates all lead JSON files against required schema."""
import json, glob, sys

REQUIRED = ['lead_name', 'lead_first_name', 'slug', 'business_name', 'url',
            'accent_color', 'services', 'tools', 'market', 'service_type',
            'speed_to_lead_context', 'blueprint_url', 'website_url',
            'apply_subject', 'prompt_1', 'prompt_2', 'prompt_3',
            'revenue_declaration', 'automation_declaration']

errors = 0
for f in sorted(glob.glob("leads/*.json")):
    with open(f) as fh:
        d = json.load(fh)
    slug = d.get('slug', '?')
    missing = [k for k in REQUIRED if not d.get(k)]
    
    # Type checks
    if d.get('services') and not isinstance(d['services'], list):
        missing.append('services (not a list)')
    if d.get('revenue_declaration') and not isinstance(d['revenue_declaration'], dict):
        missing.append('revenue_declaration (not a dict)')
    
    if missing:
        print(f"FAIL {slug}: {', '.join(missing)}")
        errors += 1
    else:
        print(f"PASS {slug}")

print(f"\n{10 - errors}/10 leads pass schema validation")
sys.exit(1 if errors > 0 else 0)
