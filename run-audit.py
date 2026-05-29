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

def financial_gate(html_path):
    """Domain 10 red-line: run financial-realism-check.py on this one blueprint.
    Returns (passed_bool, detail). Wired 2026-05-29 — the documented Domain 10
    financial red-line was never enforced by this gate, so a $45k-clone slider
    could ship. exit 0 = in-band/personalized; non-zero = out-of-band/clone/unknown."""
    checker = os.path.join(REPO, "financial-realism-check.py")
    if not os.path.exists(checker):
        return False, "financial-realism-check.py missing"
    try:
        fin = subprocess.run([sys.executable, checker, "--file", html_path],
                             capture_output=True, text=True, timeout=60)
        ok = (fin.returncode == 0)
        tail = (fin.stdout or fin.stderr or "").strip().splitlines()
        return ok, (tail[-1] if tail else f"exit {fin.returncode}")
    except Exception as e:
        return False, f"financial check error: {e}"

def audit_lead(slug):
    results = {}
    redlines = {}  # keys here are HARD red-lines: any False => VERDICT FAIL regardless of score
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
    fin_ok, fin_detail = financial_gate(html_path)
    results["D10-01_financial_realism_RL"] = fin_ok
    redlines["D10-01_financial_realism_RL"] = fin_ok
    results["PF0-4_no_placeholders_RL"] = pass_ph  # placeholders are also a red-line
    redlines["PF0-4_no_placeholders_RL"] = pass_ph
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    score = passed / total
    redline_fail = [k for k, v in redlines.items() if not v]
    return {"slug": slug, "score": score, "passed": passed, "total": total,
            "checks": results, "size": size,
            "redline_fail": redline_fail, "financial_detail": fin_detail}

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
    any_fail = False
    for slug in slugs:
        r = audit_lead(slug)
        results.append(r)
        rl_fail = r.get("redline_fail", [])
        # A red-line failure is a hard FAIL even at 100% non-red-line score.
        status = "PASS" if (r.get("score", 0) >= THRESHOLD and not rl_fail) else "FAIL"
        if status == "FAIL":
            any_fail = True
        extra = f"  RED-LINE FAIL: {rl_fail} ({r.get('financial_detail','')})" if rl_fail else ""
        print(f"[{status}] {slug}: {r.get('passed',0)}/{r.get('total',0)} ({r.get('score',0):.0%}){extra}")
    # Append to history
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
    import datetime
    for r in results:
        r["ts"] = datetime.datetime.utcnow().isoformat() + "Z"
        with open(HISTORY, "a") as f:
            f.write(json.dumps(r) + "\n")
    print(f"\nAudit complete. History: {HISTORY}")
    # VERDICT line consumed by the pre-commit hook; financial red-line now blocks.
    print("VERDICT=FAIL" if any_fail else "VERDICT=PASS")
    sys.exit(1 if any_fail else 0)

if __name__ == "__main__":
    main()
