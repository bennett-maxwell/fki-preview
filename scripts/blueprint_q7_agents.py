#!/usr/bin/env python3
"""Extract the customer-specific Q7 agent labels for a Blueprint package."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def clean_names(names):
    out=[]; seen=set()
    for name in names:
        text = re.sub(r'<[^>]+>', '', str(name or '')).replace('&amp;', '&').replace('&mdash;', '—').strip()
        key = re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()
        if text and key not in seen:
            seen.add(key); out.append(text)
    return out

def extract(profile_path: Path, slug: str, limit: int = 6):
    profile=json.loads(profile_path.read_text(encoding='utf-8'))
    names=[]
    html_path=ROOT/'blueprints'/f'{slug}.html'
    if html_path.exists():
        html=html_path.read_text(encoding='utf-8', errors='replace')
        names.extend(re.findall(r'<div class=["\']agent-name["\']>(.*?)</div>', html, flags=re.I|re.S))
    for key in ('agents','ai_agents','agent_cards'):
        val=profile.get(key)
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict): names.append(item.get('name') or item.get('title') or item.get('usecase') or '')
                else: names.append(str(item))
    if isinstance(profile.get('qualifier_q7_agents'), list):
        for item in profile['qualifier_q7_agents']:
            if isinstance(item, dict): names.append(item.get('name') or item.get('title') or item.get('usecase') or '')
            else: names.append(str(item))
    ap=profile.get('applicable_prompts')
    if isinstance(ap, dict):
        for item in ap.values():
            if isinstance(item, dict): names.append(item.get('name') or '')
    if isinstance(profile.get('ai_use_cases'), list):
        names.extend(str(x) for x in profile['ai_use_cases'])
    return clean_names(names)[:limit]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('profile')
    ap.add_argument('--slug', required=True)
    ap.add_argument('--json-output', action='store_true')
    args=ap.parse_args()
    names=extract(Path(args.profile), args.slug)
    if args.json_output:
        import json as _json; print(_json.dumps({'agents': names}, indent=2))
    else:
        print(','.join(names))
if __name__ == '__main__':
    main()
