#!/usr/bin/env python3
"""Gate Blueprint qualifier context before Bennett preview or external send.

This catches the recurring false-pass pattern where Q7 exists but is generic.
For a Blueprint package to pass, every customer-facing qualify link must carry
lead, biz, src, and lead-specific agents, and qualify.html must enforce contact
identity plus all 8 answers.
"""
from __future__ import annotations
import argparse, json, re, sys, urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ACTION_CLASSES = {"path-cta", "cta-btn", "mobile-cta-btn", "cta-btn-primary", "btn-primary", "nav-cta"}
GENERIC_AGENT_LABELS = {
    "ai speed-to-lead bot", "lead qualification filter", "automated follow-up sequences",
    "crm automation", "voice ai / outbound calling", "speed bot", "lead filter", "follow-up",
    "crm auto", "voice ai"
}

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self._stack=[]
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            d=dict(attrs); self._stack.append({'href': d.get('href',''), 'classes': sorted(set((d.get('class') or '').split())), 'text': ''})
    def handle_data(self, data):
        if self._stack: self._stack[-1]['text'] += data
    def handle_endtag(self, tag):
        if tag.lower() == 'a' and self._stack:
            item=self._stack.pop(); item['text']=' '.join(item['text'].split()); self.links.append(item)

def norm(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', str(s or '').lower()).strip()

def parse_agents(raw: str) -> list[str]:
    vals=[]
    for item in (raw or '').split(','):
        text=urllib.parse.unquote_plus(item).strip()
        if text: vals.append(text)
    return vals

def action_links(path: Path) -> list[dict[str, Any]]:
    parser=LinkParser(); parser.feed(path.read_text(encoding='utf-8', errors='replace'))
    out=[]
    for link in parser.links:
        href=link.get('href') or ''; text=(link.get('text') or '').strip().lower(); classes=set(link.get('classes') or [])
        if 'qualify.html' in href.lower() or 'qualify' in text or classes & ACTION_CLASSES:
            out.append(link)
    return out

def visible_agents(blueprint: Path|None) -> list[str]:
    agents=[]
    if blueprint and blueprint.exists():
        html=blueprint.read_text(encoding='utf-8', errors='replace')
        agents.extend(re.findall(r'<div class=["\']agent-name["\']>(.*?)</div>', html, flags=re.I|re.S))
    return clean_agent_list(agents)

def clean_agent_list(agents: list[str]) -> list[str]:
    clean=[]; seen=set()
    for a in agents:
        txt=re.sub(r'<[^>]+>', '', str(a)).replace('&amp;', '&').replace('&mdash;', '—').strip()
        if txt and norm(txt) not in seen:
            seen.add(norm(txt)); clean.append(txt)
    return clean

def profile_agents(profile: Path|None) -> list[str]:
    agents=[]
    if profile and profile.exists():
        try: data=json.loads(profile.read_text(encoding='utf-8'))
        except Exception: data={}
        for key in ('agents','ai_agents','agent_cards'):
            val=data.get(key)
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict): agents.append(item.get('name') or item.get('title') or item.get('usecase') or '')
                    else: agents.append(str(item))
        if isinstance(data.get('qualifier_q7_agents'), list):
            for item in data['qualifier_q7_agents']:
                if isinstance(item, dict): agents.append(item.get('name') or item.get('title') or item.get('usecase') or '')
                else: agents.append(str(item))
        ap=data.get('applicable_prompts')
        if isinstance(ap, dict):
            for item in ap.values():
                if isinstance(item, dict): agents.append(item.get('name') or '')
        if isinstance(data.get('ai_use_cases'), list):
            agents.extend(str(x) for x in data['ai_use_cases'])
    return clean_agent_list(agents)

def expected_agents(blueprint: Path|None, profile: Path|None) -> list[str]:
    # If a lead profile exists, it is the source of truth. Do not union it with
    # visible page agents; that masked prior cross-lead contamination where the
    # page showed SaaS agents while the qualifier link carried electrician agents.
    from_profile=profile_agents(profile)
    return from_profile if from_profile else visible_agents(blueprint)

def validate_qualifier(path: Path) -> list[dict[str, Any]]:
    failures=[]
    html=path.read_text(encoding='utf-8', errors='replace')
    required_ids=['lead-first','lead-last','lead-business','lead-email','lead-phone']
    for fid in required_ids:
        m=re.search(r'<input[^>]*\bid=["\']'+re.escape(fid)+r'["\'][^>]*>', html, flags=re.I|re.S)
        if not m or not re.search(r'\brequired\b', m.group(0), flags=re.I):
            failures.append({'type':'identity_field_not_required','field':fid})
    checks=[
        ('identity_validation', r'function\s+isIdentityComplete\s*\(\).*?firstName.*?lastName.*?businessName.*?validEmail.*?validPhone'),
        ('all_8_answer_gate', r'const\s+allDone\s*=\s*answered\s*>=\s*8'),
        ('capability_counted', r'if\s*\(chips\.capability\)\s*answered\+\+'),
        ('contact_all8_cta_note', r'Complete the contact fields and all 8 questions'),
        ('q7_dynamic_agents', r'function\s+hydrateAgents\s*\('),
        ('q7_source_contexts', r'BLUEPRINT_Q7_CONTEXTS'),
    ]
    for name, pat in checks:
        if not re.search(pat, html, flags=re.I|re.S):
            failures.append({'type':'qualifier_invariant_missing','name':name})
    return failures

def validate_visible_vs_profile(blueprint: Path|None, expected: list[str]) -> list[dict[str, Any]]:
    failures=[]
    if not blueprint or not blueprint.exists() or not expected:
        return failures
    expected_norm={norm(a) for a in expected if norm(a)}
    visible=visible_agents(blueprint)
    visible_norm={norm(a) for a in visible if norm(a)}
    unexpected=[a for a in visible if norm(a) not in expected_norm]
    missing=[a for a in expected if norm(a) not in visible_norm]
    if unexpected or len(visible_norm & expected_norm) < min(3, len(expected_norm)):
        failures.append({
            'type':'visible_agents_do_not_match_lead_profile',
            'file':str(blueprint),
            'expected_sample':expected[:6],
            'visible_agents':visible,
            'unexpected_visible_agents':unexpected[:6],
            'missing_expected_agents':missing[:6],
        })
    return failures

def validate_links(paths: list[Path], expected: list[str], expected_slug: str|None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    failures=[]; inspected=[]
    expected_norm={norm(a) for a in expected if norm(a)}
    for path in paths:
        if not path or not path.exists():
            continue
        for link in action_links(path):
            href=link.get('href') or ''
            if 'qualify.html' not in href.lower():
                continue
            parts=urllib.parse.urlsplit(href)
            qs=urllib.parse.parse_qs(parts.query, keep_blank_values=True)
            agents=parse_agents((qs.get('agents') or [''])[0])
            item={'file':str(path),'text':link.get('text'),'href':href,'agents':agents}
            inspected.append(item)
            missing=[k for k in ('lead','biz','src','agents') if not qs.get(k)]
            if missing:
                failures.append({'type':'missing_qualifier_context_param','file':str(path),'href':href,'missing':missing})
            if expected_slug and qs.get('src') and qs['src'][0] != expected_slug:
                failures.append({'type':'wrong_src_slug','file':str(path),'href':href,'expected':expected_slug,'actual':qs['src'][0]})
            if len(agents) < 3:
                failures.append({'type':'too_few_tailored_agents','file':str(path),'href':href,'count':len(agents)})
            generic=[a for a in agents if norm(a) in GENERIC_AGENT_LABELS]
            if generic:
                failures.append({'type':'generic_q7_option_present','file':str(path),'href':href,'agents':generic})
            if expected_norm and agents:
                overlap={norm(a) for a in agents} & expected_norm
                required=min(3, len(expected_norm))
                if len(overlap) < required:
                    failures.append({'type':'q7_agents_do_not_match_blueprint','file':str(path),'href':href,'expected_sample':expected[:6],'actual':agents,'overlap':sorted(overlap)})
    if not inspected:
        failures.append({'type':'no_qualifier_links_inspected'})
    return failures, inspected

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--html', help='Blueprint HTML artifact')
    ap.add_argument('--delivery-email', help='Delivery email HTML artifact')
    ap.add_argument('--profile', help='Lead profile JSON')
    ap.add_argument('--qualifier', default='qualify.html')
    ap.add_argument('--lead', help='Expected lead slug')
    ap.add_argument('--json-output', action='store_true')
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    def res(p):
        if not p: return None
        path=Path(p)
        return path if path.is_absolute() else root/path
    html=res(args.html); email=res(args.delivery_email); profile=res(args.profile); qualifier=res(args.qualifier)
    expected=expected_agents(html, profile)
    failures=validate_qualifier(qualifier)
    failures.extend(validate_visible_vs_profile(html, expected))
    link_failures, inspected=validate_links([p for p in [html,email] if p], expected, args.lead)
    failures.extend(link_failures)
    out={'status':'PASS' if not failures else 'FAIL','pass':not failures,'qualifier':str(qualifier),'lead':args.lead,'expected_agents':expected[:12],'inspected_links':inspected,'failures':failures}
    print(json.dumps(out, indent=2, sort_keys=True)) if args.json_output else print(f"blueprint_qualifier_context_gate: {out['status']} failures={len(failures)}")
    if not args.json_output:
        for f in failures: print(f)
    return 0 if not failures else 1
if __name__ == '__main__':
    raise SystemExit(main())
