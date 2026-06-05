#!/usr/bin/env python3
"""Blueprint audit runner — validates a lead's blueprint package."""
import argparse, json, os, re, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--lead", required=True)
parser.add_argument("--html", default=None)
args = parser.parse_args()

slug = args.lead
html_path = args.html or f"blueprints/{slug}.html"

if not os.path.exists(html_path):
    print(f"FAIL: Blueprint HTML not found: {html_path}")
    sys.exit(1)

html = open(html_path).read()
size = os.path.getsize(html_path)

failures = []
if size < 35000: failures.append("file too small")
if "drive.google.com" in html: failures.append("drive links present")
if re.search(r'\{\{[A-Za-z_]+\}\}', html): failures.append("unresolved tokens")
import re
emojis = re.findall(u'[\U0001F300-\U0001FAFF]', html)
if emojis: failures.append(f"emojis found: {emojis[:3]}")
if not "qualify.html" in html: failures.append("no qualify.html CTA")
if not "See If You Qualify" in html: failures.append("no See If You Qualify text")
if "Apply to work with Bennett" in html: failures.append("banned CTA text")
if "|| 45000" in html: failures.append("hardcoded ROI default")

# Check audit receipt
receipt_path = f"audit-receipts/{slug}/{slug}-audit.json"
if os.path.exists(receipt_path):
    receipt = json.load(open(receipt_path))
    receipt_ok = (
        receipt.get("verdict") == "PASS"
        or receipt.get("status") == "PASS"
        or receipt.get("pct", 0) >= 95
    )
    if not receipt_ok:
        failures.append(f"audit receipt not PASS: verdict={receipt.get('verdict')} status={receipt.get('status')} pct={receipt.get('pct')}")
else:
    failures.append("no audit receipt")

if failures:
    print(f"AUDIT FAIL ({slug}): {'; '.join(failures)}")
    sys.exit(1)
else:
    print(f"AUDIT PASS ({slug}): all checks green")
    sys.exit(0)
