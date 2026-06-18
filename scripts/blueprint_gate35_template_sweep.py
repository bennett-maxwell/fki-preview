#!/usr/bin/env python3
"""Sweep Blueprint artifacts for Gate 35 / PF0-7 banned template phrases."""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PHRASES = [
    "SaaS Agency", "SaaS & CRM", "675+ accounts", "675 accounts", "$199/mo", "$199 / mo",
    "Your SaaS Product", "vertical SaaS", "SaaS CRM agency",
    "subscription businesses run an AI health-monitoring agent",
    "bmellc.com/home-service", "home-service CRM", "customer health, renewals, and churn",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="blueprints")
    ap.add_argument("--tsv")
    ap.add_argument("--json")
    ap.add_argument("--include-obsolete", action="store_true")
    args = ap.parse_args()
    root = (REPO / args.root).resolve()
    rows=[]
    files = sorted(root.rglob("*.html"))
    for path in files:
        rel = path.relative_to(REPO)
        if not args.include_obsolete and "_obsolete" in rel.parts:
            continue
        text = path.read_text(errors="ignore")
        for lineno, line in enumerate(text.splitlines(), 1):
            for phrase in PHRASES:
                if phrase.lower() in line.lower():
                    rows.append({
                        "path": str(rel),
                        "line": lineno,
                        "phrase": phrase,
                        "context": re.sub(r"\s+", " ", line).strip()[:240],
                    })
    payload={
        "gate": "blueprint_gate35_template_sweep",
        "root": str(root.relative_to(REPO) if root.is_relative_to(REPO) else root),
        "include_obsolete": args.include_obsolete,
        "phrase_count": len(PHRASES),
        "finding_count": len(rows),
        "files_with_findings": len({r["path"] for r in rows}),
        "findings": rows,
    }
    if args.tsv:
        with open(args.tsv, "w", newline="", encoding="utf-8") as f:
            w=csv.DictWriter(f, fieldnames=["path","line","phrase","context"], delimiter="\t")
            w.writeheader(); w.writerows(rows)
    if args.json:
        Path(args.json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ["gate","finding_count","files_with_findings"]}, indent=2))
    return 1 if rows else 0

if __name__ == "__main__":
    raise SystemExit(main())
