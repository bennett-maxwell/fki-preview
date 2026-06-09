#!/usr/bin/env python3
"""Validate Blueprint qualifier CTAs resolve to the canonical qualifier path.

Catches the failure mode where a CTA contains the string `qualify.html` but points
at a 404 path such as `/apply/qualify.html`.
"""
from __future__ import annotations
import argparse, json, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ACTION_CLASSES = {"path-cta", "cta-btn", "mobile-cta-btn", "cta-btn-primary", "btn-primary", "nav-cta"}
BANNED_CTA_TEXT = {"get your ai quote", "apply to work with bennett", "apply to work with us"}

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

def is_action(link):
    text=(link.get('text') or '').strip().lower(); classes=set(link.get('classes') or []); href=(link.get('href') or '').lower()
    return bool(classes & ACTION_CLASSES) or 'qualify' in text or text in BANNED_CTA_TEXT or 'qualify.html' in href or '/apply' in href

def check_http(url: str):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            body = r.read(128)
            return {'url': url, 'http_code': getattr(r, 'status', 0), 'pass': getattr(r, 'status', 0) == 200, 'sample': body.decode('utf-8','replace')[:80]}
    except Exception as exc:
        return {'url': url, 'http_code': 0, 'pass': False, 'error': str(exc)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--html', required=True)
    ap.add_argument('--check-http', action='store_true')
    ap.add_argument('--json-output', action='store_true')
    args=ap.parse_args()
    path=Path(args.html)
    parser=LinkParser(); parser.feed(path.read_text(errors='replace'))
    failures=[]; action_links=[]; http=[]
    for link in parser.links:
        if not is_action(link): continue
        href=link.get('href') or ''; text=link.get('text') or ''
        action_links.append(link); low_href=href.lower(); low_text=text.lower().strip()
        if '\\' in href or '"' in href or "'" in href:
            failures.append({'type':'malformed_href', 'text': text, 'href': href}); continue
        if low_text in BANNED_CTA_TEXT:
            failures.append({'type':'banned_cta_text', 'text': text, 'href': href})
        if low_href == '#apply':
            continue
        if '/apply' in low_href:
            failures.append({'type':'legacy_apply_path', 'text': text, 'href': href})
        if 'qualify.html' not in low_href:
            failures.append({'type':'missing_qualify_html', 'text': text, 'href': href}); continue
        parsed=urllib.parse.urlsplit(href)
        if not (parsed.path.endswith('/qualify.html') or parsed.path == 'qualify.html'):
            failures.append({'type':'wrong_qualifier_path', 'text': text, 'href': href, 'path': parsed.path})
        qs=urllib.parse.parse_qs(parsed.query)
        missing=[k for k in ('lead','biz','src') if not qs.get(k)]
        if missing:
            failures.append({'type':'missing_identity_params', 'text': text, 'href': href, 'missing': missing})
        if args.check_http and parsed.scheme in ('http','https'):
            res=check_http(href); http.append(res)
            if not res.get('pass'):
                failures.append({'type':'http_not_200', 'text': text, 'href': href, 'http': res})
    if not action_links:
        failures.append({'type':'no_action_links_found'})
    out={'html': str(path), 'status': 'PASS' if not failures else 'FAIL', 'action_link_count': len(action_links), 'action_links': action_links, 'http_checks': http, 'failures': failures}
    if args.json_output: print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(f"blueprint_qualify_link_gate: {out['status']} action_links={len(action_links)} failures={len(failures)}")
        for f in failures: print(f)
    return 0 if not failures else 1
if __name__ == '__main__':
    raise SystemExit(main())
