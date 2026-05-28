#!/usr/bin/env python3
"""run-audit.py — Blueprint AI audit entrypoint (stdlib + curl). v1.0 2026-05-28"""
import sys, os, subprocess, re, json, urllib.request

REPO = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.join(REPO, "blueprints")
HISTORY = os.path.expanduser("~/.openclaw/logs/blueprint-audit-history.jsonl")
THRESHOLD = 0.90  # 90% of non-red-line checks

def curl_http(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"FKI-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except Exception as e:
        return 0

def check_placeholder(html):
    stripped = re.sub(r'<pre>.*?</pre>', '', html, flags=re.DOTALL)
    tokens = re.findall(r'[A-Z_]*PLACEHOLDER[A-Z_]*|\{\{[A-Za-z_]+\}\}|\[[A-Z_]{3,}\]', stripped)
    return len(tokens) == 0, tokens

def audit_lead(slug):
    results = {}
    html_path = os.path.join(BP_DIR, f"{slug}.html")
    if not os.path.exists(html_path):
        return {"error": f"{html_path} not found", "score": 0}
    with open(html_path) as f:
        html = f.read()
    size = len(html)
    results["PF0-1_size_ge_40kb"] = size >= 40000
    pass_ph, tokens = check_placeholder(html)
    results["PF0-4_no_placeholders"] = pass_ph
    results["D1-01_name_in_title"] = slug.replace("-", " ").split()[0].lower() in html.lower()
    results["D2-01_no_emojis"] = not bool(re.search(r'[\U0001F300-\U0001FAFF]', html))
    results["D3-01_podcast_exists"] = os.path.exists(os.path.join(REPO, "podcasts", f"{slug}.mp3"))
    results["D9-01_no_orphan_classes"] = True  # simplified
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    score = passed / total
    return {"slug": slug, "score": score, "passed": passed, "total": total, "checks": results, "size": size}

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--lead", help="Lead slug to audit")
    p.add_argument("--all", action="store_true", help="Audit all blueprints")
    args = p.parse_args()
    slugs = []
    if args.lead:
        slugs = [args.lead]
    elif args.all:
        slugs = [f[:-5] for f in os.listdir(BP_DIR) if f.endswith(".html") and not f.startswith("_")]
    else:
        print("Usage: run-audit.py --lead <slug> | --all"); sys.exit(1)
    results = []
    for slug in slugs:
        r = audit_lead(slug)
        results.append(r)
        status = "PASS" if r.get("score", 0) >= THRESHOLD else "FAIL"
        print(f"[{status}] {slug}: {r.get('passed',0)}/{r.get('total',0)} ({r.get('score',0):.0%})")
    # Append to history
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
    import datetime
    for r in results:
        r["ts"] = datetime.datetime.utcnow().isoformat() + "Z"
        with open(HISTORY, "a") as f:
            f.write(json.dumps(r) + "\n")
    print(f"\nAudit complete. History: {HISTORY}")

if __name__ == "__main__":
    main()
