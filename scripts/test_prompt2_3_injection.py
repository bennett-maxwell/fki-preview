#!/usr/bin/env python3
"""Test that clone-blueprint.sh correctly replaces prompt2/prompt3 pre content for home-services leads."""
import re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

def test_no_generic_prompt_content(slug, blueprint_path):
    html = Path(blueprint_path).read_text()
    
    # Check that generic SaaS prompt content is NOT in home-services blueprints
    generic_markers = [
        'Client Success Onboarding Agent',
        'complete onboarding lifecycle',
        'payment confirmation workflow',
    ]
    
    found = [m for m in generic_markers if m.lower() in html.lower()]
    if found:
        print(f"FAIL {slug}: generic prompt content found: {found}")
        return False
    print(f"PASS {slug}: no generic SaaS prompt content in prompt2/3")
    return True

if __name__ == '__main__':
    slug = sys.argv[1] if len(sys.argv) > 1 else 'court-lundberg'
    bp = REPO / 'blueprints' / f'{slug}.html'
    ok = test_no_generic_prompt_content(slug, bp)
    sys.exit(0 if ok else 1)
