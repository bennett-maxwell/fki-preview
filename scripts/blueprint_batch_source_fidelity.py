#!/usr/bin/env python3
"""Batch-run Blueprint PF0-7/source-fidelity across lead profiles."""
from __future__ import annotations
import argparse, csv, glob, json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def raw_candidates(slug: str) -> list[Path]:
    roots=[REPO/'audit-receipts'/slug]
    pats=['**/*ghl*raw*.json','**/*contact*raw*.json','**/*.raw.json','**/*normalized-for-source-fidelity.raw.json']
    out=[]
    for root in roots:
        if root.exists():
            for pat in pats: out.extend(root.glob(pat))
    return sorted(set(out))

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-tsv', required=True)
    ap.add_argument('--details-dir', required=True)
    ap.add_argument('--limit', type=int, default=0)
    args=ap.parse_args()
    details=Path(args.details_dir); details.mkdir(parents=True, exist_ok=True)
    results=[]
    leads=sorted((REPO/'leads').glob('*.json'))
    if args.limit: leads=leads[:args.limit]
    for lead in leads:
        try: profile=json.loads(lead.read_text())
        except Exception as e:
            results.append({'slug':lead.stem,'status':'ERROR','finding_count':1,'codes':['lead_json_parse_error'],'error':str(e)}); continue
        slug=profile.get('slug') or lead.stem
        html=REPO/'blueprints'/f'{slug}.html'
        if not html.exists():
            results.append({'slug':slug,'status':'SKIP_NO_HTML','finding_count':0,'codes':[]}); continue
        raws=raw_candidates(slug)
        raw=raws[-1] if raws else None
        cmd=[sys.executable, str(REPO/'scripts'/'blueprint_source_fidelity_gate.py'), '--lead-json', str(lead), '--html', str(html), '--json-output']
        if raw: cmd += ['--ghl-raw', str(raw)]
        cp=subprocess.run(cmd, cwd=REPO, text=True, capture_output=True)
        (details/f'{slug}.json').write_text(cp.stdout or cp.stderr or '')
        try:
            payload=json.loads(cp.stdout); findings=payload.get('findings',[]); status=payload.get('status')
        except Exception:
            findings=[{'code':'gate_execution_error','message':(cp.stderr or cp.stdout)[:500]}]; status='ERROR'
        results.append({'slug':slug,'status':status,'finding_count':len(findings),'codes':sorted({f.get('code','unknown') for f in findings if isinstance(f,dict)}),'phrases':[f.get('phrase') for f in findings if isinstance(f,dict) and f.get('phrase')],'raw_used':str(raw.relative_to(REPO)) if raw else ''})
    summary={'total_checked':len(results),'pass':sum(r['status']=='PASS' for r in results),'fail':sum(r['status']=='FAIL' for r in results),'skip_no_html':sum(r['status']=='SKIP_NO_HTML' for r in results),'error':sum(r['status']=='ERROR' for r in results),'results':results}
    Path(args.out_json).write_text(json.dumps(summary,indent=2)+'\n')
    with open(args.out_tsv,'w',newline='') as f:
        w=csv.writer(f,delimiter='\t'); w.writerow(['slug','status','finding_count','codes','phrases','raw_used'])
        for r in results: w.writerow([r['slug'],r['status'],r['finding_count'],','.join(r['codes']),'|'.join([p for p in r.get('phrases',[]) if p]),r.get('raw_used','')])
    print(json.dumps({k:summary[k] for k in ['total_checked','pass','fail','skip_no_html','error']}, indent=2))
    return 1 if summary['fail'] or summary['error'] else 0
if __name__ == '__main__': raise SystemExit(main())
