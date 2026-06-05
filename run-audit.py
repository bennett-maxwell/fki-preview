#!/usr/bin/env python3
"""Blueprint audit runner — validates a lead's blueprint package and writes a receipt."""
import argparse, hashlib, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--lead", required=True)
parser.add_argument("--html", default=None)
parser.add_argument("--json-output", action="store_true")
args = parser.parse_args()

slug = args.lead
html_path = Path(args.html or f"blueprints/{slug}.html")
receipt_dir = Path("audit-receipts") / slug
receipt_path = receipt_dir / f"{slug}-audit.json"

checks = []
def add(name, ok, detail="OK"):
    checks.append({"name": name, "pass": bool(ok), "detail": detail if ok else detail})

failures = []
if not html_path.exists():
    failures.append(f"Blueprint HTML not found: {html_path}")
    html = ""
    size = 0
else:
    html = html_path.read_text(errors="ignore")
    size = html_path.stat().st_size

add("file_exists", html_path.exists(), f"{html_path}")
add("file_size_min", size >= 35000, f"{size} bytes")
add("no_drive_links", "drive.google.com" not in html, "drive.google.com present")
add("no_unresolved_tokens", not re.search(r'\{\{[A-Za-z_]+\}\}', html), "unresolved {{TOKEN}} found")
emojis = re.findall('[\U0001F300-\U0001FAFF]', html)
add("no_emoji", not emojis, f"emojis found: {emojis[:3]}")
add("has_qualify_cta", "qualify.html" in html, "missing qualify.html CTA")
add("has_expected_cta_text", "See If You Qualify" in html, "missing See If You Qualify text")
add("no_banned_apply_copy", "Apply to work with Bennett" not in html, "banned CTA text present")
add("no_hardcoded_roi_default", "|| 45000" not in html, "hardcoded ROI default present")

failures = [c["detail"] if c["detail"] != "OK" else c["name"] for c in checks if not c["pass"]]
passed = len([c for c in checks if c["pass"]])
total = len(checks)
pct = round((passed / total) * 100, 2) if total else 0
status = "PASS" if not failures and pct >= 95 else "FAIL"

receipt = {
    "lead": slug,
    "html": str(html_path),
    "html_size_bytes": size,
    "html_sha256": hashlib.sha256(html_path.read_bytes()).hexdigest() if html_path.exists() else None,
    "checks": checks,
    "passed": passed,
    "total": total,
    "pct": pct,
    "status": status,
    "verdict": status,
    "pass": status == "PASS",
    "failures": failures,
    "ts": datetime.now(timezone.utc).isoformat(),
}
receipt_dir.mkdir(parents=True, exist_ok=True)
receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

if args.json_output:
    print(json.dumps(receipt, indent=2, sort_keys=True))
elif status == "PASS":
    print(f"AUDIT PASS ({slug}): {passed}/{total} checks green; receipt {receipt_path}")
else:
    print(f"AUDIT FAIL ({slug}): {'; '.join(failures)}; receipt {receipt_path}")
sys.exit(0 if status == "PASS" else 1)
