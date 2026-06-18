#!/usr/bin/env python3
"""Replace PF0-7 failing Blueprint HTML pages with a noindex quarantine page."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
REPO=Path(__file__).resolve().parent.parent

def quarantine_html(slug: str, reason: str) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <title>Deliverable Not Approved</title>
  <style>body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f5f5f7;color:#1d1d1f;display:grid;place-items:center;min-height:100vh;margin:0}}.card{{max-width:680px;background:#fff;border:1px solid #e5e5ea;border-radius:22px;padding:36px;box-shadow:0 20px 60px rgba(0,0,0,.08)}}.badge{{display:inline-block;background:#fff3cd;color:#7a4d00;border:1px solid #ffe08a;border-radius:999px;padding:6px 12px;font-size:13px;font-weight:700;margin-bottom:16px}}h1{{margin:0 0 12px;font-size:34px}}p{{font-size:17px;line-height:1.55;color:#515154}}code{{background:#f5f5f7;padding:2px 5px;border-radius:5px}}.small{{font-size:13px;color:#86868b;margin-top:20px}}</style>
</head>
<body>
  <main class="card" data-blueprint-quarantine="true" data-blueprint-slug="{slug}">
    <div class="badge">NOT APPROVED FOR DELIVERY</div>
    <h1>This deliverable is not approved yet.</h1>
    <p>This Blueprint page has been intentionally quarantined while source-fidelity, production audit, and Bennett approval are pending.</p>
    <p>No customer-facing deliverable should be sent from this URL until the full Blueprint approval path passes.</p>
    <p class="small">Internal status: blocked by PF0-7/source-fidelity cleanup. Reason: <code>{reason}</code>. Quarantined at {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}.</p>
  </main>
</body>
</html>
'''

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--batch-json',required=True); ap.add_argument('--out-json',required=True); ap.add_argument('--dry-run',action='store_true'); args=ap.parse_args()
    batch=json.load(open(args.batch_json))
    changed=[]; skipped=[]
    for r in batch.get('results',[]):
        if r.get('status')!='FAIL': continue
        slug=r['slug']; html=REPO/'blueprints'/f'{slug}.html'
        if not html.exists(): skipped.append({'slug':slug,'reason':'no_html'}); continue
        codes=','.join(r.get('codes',[])) or 'source_fidelity_fail'
        before=html.read_text(errors='ignore')
        if 'data-blueprint-quarantine="true"' in before:
            skipped.append({'slug':slug,'reason':'already_quarantined'}); continue
        if not args.dry_run:
            html.write_text(quarantine_html(slug,codes), encoding='utf-8')
        changed.append({'slug':slug,'html':str(html.relative_to(REPO)),'reason':codes})
    payload={'status':'DRY_RUN' if args.dry_run else 'PASS','changed_count':len(changed),'skipped_count':len(skipped),'changed':changed,'skipped':skipped}
    Path(args.out_json).write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({k:payload[k] for k in ['status','changed_count','skipped_count']}, indent=2))
if __name__=='__main__': main()
