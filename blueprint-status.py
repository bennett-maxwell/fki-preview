#!/usr/bin/env python3
"""blueprint-status.py — Truth dashboard (Council Rec #8). Run before/after every build."""
import os, re, json, glob
from datetime import datetime

BASE = os.path.expanduser("~/fki-preview")
BLUEPRINTS = os.path.join(BASE, "blueprints")
LEADS_DIR = os.path.join(BASE, "leads")
LOCKS = os.path.expanduser("~/.claude/state/blueprint-locks")
SHIPS = os.path.expanduser("~/.claude/state/blueprint-ships")
SENDS_LOG = os.path.expanduser("~/.claude/logs/blueprint-sends.jsonl")

print(f"\n{'='*78}")
print(f"  BLUEPRINT STATUS  |  {datetime.now().strftime('%Y-%m-%d %H:%M')} MDT")
print(f"{'='*78}")
print(f"  {'SLUG':<32} {'HTML':>6} {'AUDIT':>7} {'💎':>4} {'APPROVED':>9} {'SHIPPED':>8}")
print(f"  {'-'*32} {'-'*6} {'-'*7} {'-'*4} {'-'*9} {'-'*8}")

sent_slugs = set()
if os.path.exists(SENDS_LOG):
    for line in open(SENDS_LOG):
        try:
            d = json.loads(line)
            if d.get('slug'): sent_slugs.add(d['slug'])
        except: pass

# Collect all known slugs
all_slugs = set()
for f in glob.glob(os.path.join(BLUEPRINTS, "*-canonical.html")):
    all_slugs.add(re.sub(r'-canonical\.html$','',os.path.basename(f)))
for f in glob.glob(os.path.join(LEADS_DIR, "*.json")):
    all_slugs.add(os.path.basename(f).replace('.json',''))

for slug in sorted(all_slugs):
    canonical = os.path.join(BLUEPRINTS, f"{slug}-canonical.html")
    html_col = f"{os.path.getsize(canonical)//1024}KB" if os.path.exists(canonical) else "—"

    audit_col = "—"
    for rpt in [os.path.join(BLUEPRINTS, f"{slug}-canonical-AUDIT_REPORT.json"),
                os.path.join(BLUEPRINTS, f"{slug}-AUDIT_REPORT.json")]:
        if os.path.exists(rpt):
            try:
                d = json.load(open(rpt))
                s = d.get('score', d.get('total_score','?'))
                audit_col = f"{s}%"
            except: audit_col = "err"
            break

    diamond = "💎" if os.path.exists(os.path.join(LOCKS, f"{slug}.diamond")) else "—"
    approved = "✅ YES" if os.path.exists(os.path.join(SHIPS, f"{slug}.ship")) else "—"
    shipped = "✅ SENT" if slug in sent_slugs else "—"

    print(f"  {slug:<32} {html_col:>6} {audit_col:>7} {diamond:>4} {approved:>9} {shipped:>8}")

print(f"{'='*78}\n")
