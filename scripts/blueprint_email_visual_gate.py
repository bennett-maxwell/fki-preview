#!/usr/bin/env python3
"""Strict customer-view email visual-format gate for Blueprint Stage 7.

This catches the failure class where an email is technically valid but looks bad
or is an internal proof memo instead of the customer-facing delivery format.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

BANNED = [
    'gatekeeper', 'sha256', 'public readback', 'notion', 'codex', 'receipt',
    'human gate', 'approval state', 'external send allowed', 'pass_preview_only',
    'thread id', 'message id', 'root cause', 'proof ledger'
]
REQUIRED = [
    'Your AI Blueprint is Ready', 'Built specifically for', 'Hi ',
    'Your AI Playbook', 'View Your AI Playbook', 'Your AI Audio Walkthrough',
    'Listen to Your Walkthrough', 'What To Do Next', 'See If You Qualify',
    'Madison Lanz | Franchise KI'
]

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--email', required=True)
    ap.add_argument('--subject', required=True)
    ap.add_argument('--json-output', action='store_true')
    args=ap.parse_args()
    path=Path(args.email)
    html=path.read_text(encoding='utf-8', errors='replace')
    low=re.sub(r'\s+', ' ', html).lower()
    failures=[]
    if not args.subject.startswith('CUSTOMER VIEW PREVIEW:') and 'approval' in args.subject.lower():
        failures.append({'type':'bad_subject_for_customer_view_preview','subject':args.subject})
    if html.lstrip().startswith('<!--'):
        failures.append({'type':'raw_comment_before_doctype','detail':'email clients/snippets can expose metadata; customer view must start with <!DOCTYPE html>'})
    if '<!DOCTYPE html>' not in html[:200]:
        failures.append({'type':'missing_doctype_at_top'})
    for phrase in REQUIRED:
        if phrase.lower() not in low:
            failures.append({'type':'missing_customer_view_phrase','phrase':phrase})
    for phrase in BANNED:
        if phrase in low:
            failures.append({'type':'internal_language_in_customer_email','phrase':phrase})
    if re.search(r'\{\{[A-Z_]+\}\}', html):
        failures.append({'type':'unresolved_template_token'})
    if html.lower().count('qualify.html') != 1:
        failures.append({'type':'wrong_qualify_cta_count','count':html.lower().count('qualify.html')})
    # 2026-06-19: AI Employees is canonical customer-facing language;
    # accept legacy agents= while preferring employees=.
    if 'employees=' not in html and 'agents=' not in html:
        failures.append({'type':'missing_q7_employees_context'})
    # Visual card requirements: two distinct cards with border/background and button table.
    card_count=len(re.findall(r'border:\s*1px\s+solid\s+#d2d2d7', html, flags=re.I))
    if card_count < 2:
        failures.append({'type':'missing_card_borders','count':card_count,'required':2})
    if 'box-shadow:' not in html:
        failures.append({'type':'missing_card_depth'})
    button_count=len(re.findall(r'border-radius:8px', html, flags=re.I))
    if button_count < 3:
        failures.append({'type':'button_style_missing_or_sparse','count':button_count})
    if 'background:#ffffff' not in html.lower():
        failures.append({'type':'white_background_missing'})
    if 'max-width:640px' not in html:
        failures.append({'type':'email_width_missing'})
    out={'status':'PASS' if not failures else 'FAIL','pass':not failures,'email':str(path),'subject':args.subject,'failures':failures}
    if args.json_output:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(f"blueprint_email_visual_gate: {out['status']} failures={len(failures)}")
        for f in failures: print(f)
    return 0 if not failures else 1
if __name__ == '__main__':
    raise SystemExit(main())
