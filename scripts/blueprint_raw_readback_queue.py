#!/usr/bin/env python3
"""List GHL/form-derived Blueprint leads missing preserved raw source readbacks."""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path
REPO=Path(__file__).resolve().parent.parent

def has_raw(slug):
    root=REPO/'audit-receipts'/slug
    return root.exists() and any(root.glob('**/*raw*.json'))
def formish(p):
    text=' '.join(str(p.get(k,'')) for k in ['source_note','lead_source','source','form','workflow'])
    return bool(p.get('ghl_contact_id') or p.get('contact_id') or re.search(r'\b(GHL|GoHighLevel|form|intake|blueprint_ai_apply|AI_Advantage_blueprint)\b', text, re.I))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out-json',required=True); ap.add_argument('--out-tsv',required=True); args=ap.parse_args()
    rows=[]
    for lead in sorted((REPO/'leads').glob('*.json')):
        try: p=json.loads(lead.read_text())
        except: continue
        slug=p.get('slug') or lead.stem
        if formish(p) and not has_raw(slug):
            rows.append({'slug':slug,'lead_json':str(lead.relative_to(REPO)),'email_present':bool(p.get('email')),'ghl_contact_id_present':bool(p.get('ghl_contact_id') or p.get('contact_id')),'source':p.get('source') or p.get('lead_source') or ''})
    payload={'missing_raw_readback_count':len(rows),'rows':rows}
    Path(args.out_json).write_text(json.dumps(payload,indent=2)+'\n')
    with open(args.out_tsv,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['slug','lead_json','email_present','ghl_contact_id_present','source'],delimiter='\t'); w.writeheader(); w.writerows(rows)
    print(json.dumps({'missing_raw_readback_count':len(rows)}, indent=2))
if __name__=='__main__': main()
