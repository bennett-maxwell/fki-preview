#!/usr/bin/env python3
"""Gate Bennett approval preview email as a customer-view artifact.

Internal proof memos are allowed separately, but cannot pass this gate or count as
Stage 7 Bennett approval preview.
"""
from __future__ import annotations
import argparse, json, re, urllib.parse
from pathlib import Path

BANNED_INTERNAL = [
    'gatekeeper', 'pass_preview_only', 'external send', 'customer send remains blocked',
    'no customer send', 'gmail thread', 'message id', 'sha256', 'public readback',
    'blueprint audit', 'completion gate', 'receipt', 'codex', 'root cause', 'proof ledger',
    'approval state', 'thread:', 'notion:', 'human gate', 'bennett approval before'
]
REQUIRED_PHRASES = [
    'Your AI Blueprint is Ready', 'Built specifically for', 'Hi ', 'I put together a complete AI implementation blueprint',
    'Your AI Playbook', 'View Your AI Playbook', 'Your AI Audio Walkthrough', 'Listen to Your Walkthrough',
    'What To Do Next', 'See If You Qualify', 'Madison Lanz | Franchise KI'
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--email', required=True)
    ap.add_argument('--profile')
    ap.add_argument('--subject')
    ap.add_argument('--json-output', action='store_true')
    args=ap.parse_args()
    path=Path(args.email)
    html=path.read_text(encoding='utf-8', errors='replace')
    low=re.sub(r'\s+', ' ', html).lower()
    failures=[]
    missing=[p for p in REQUIRED_PHRASES if p.lower() not in low]
    for p in missing:
        failures.append({'type':'missing_customer_view_phrase','phrase':p})
    for phrase in BANNED_INTERNAL:
        if phrase in low:
            failures.append({'type':'internal_proof_language_in_customer_preview','phrase':phrase})
    if re.search(r'\{\{[A-Z_]+\}\}', html):
        failures.append({'type':'unresolved_template_token'})
    if 'qualify.html' not in low:
        failures.append({'type':'missing_qualify_cta'})
    if 'agents=' not in low:
        failures.append({'type':'missing_tailored_agents_param_on_qualify_cta'})
    if 'leadconnectorhq' in low or 'widget/bookings' in low or 'calendly' in low:
        failures.append({'type':'direct_calendar_or_booking_link_in_delivery_email'})
    if args.subject:
        subj=urllib.parse.unquote_plus(args.subject).lower()
        if 'codex' in subj or 'approval' in subj and 'customer view' not in subj:
            failures.append({'type':'non_customer_view_subject','subject':args.subject})
    out={'status':'PASS' if not failures else 'FAIL','pass':not failures,'email':str(path),'failures':failures}
    if args.json_output: print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(f"blueprint_approval_email_gate: {out['status']} failures={len(failures)}")
        for f in failures: print(f)
    return 0 if not failures else 1
if __name__ == '__main__':
    raise SystemExit(main())
