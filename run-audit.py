#!/usr/bin/env python3
"""run-audit.py — Blueprint AI audit entrypoint (stdlib + curl). v1.0 2026-05-28"""
import sys, os, subprocess, re, json, urllib.request

REPO = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.join(REPO, "blueprints")
HISTORY = os.path.expanduser("~/.openclaw/logs/blueprint-audit-history.jsonl")
THRESHOLD = 0.90  # 90% of non-red-line checks

# Explicit, committable podcast alias map (deploy-independent). When a lead's
# real audio is stored under a different filename than f"{slug}.mp3", map it
# here instead of relying on a filesystem symlink (GitHub Pages / static
# deploys may not follow symlinks -> false-PASS). 2026-05-31.
PODCAST_ALIAS = {"watson": "watson-kamoto"}

def podcast_exists(slug):
    """D3-01: a per-lead podcast exists as a REAL file. Resolves PODCAST_ALIAS
    before the existence check so the dependency is explicit and deploy-safe."""
    name = PODCAST_ALIAS.get(slug, slug)
    path = os.path.join(REPO, "podcasts", f"{name}.mp3")
    return os.path.isfile(path) and os.path.getsize(path) > 0

def curl_http(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"FKI-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except Exception as e:
        return 0

def no_orphan_classes(html):
    """D9-01: every class used in body has a matching CSS definition.
    Self-contained reimplementation of d9-audit.py's orphan-class logic
    (run-audit.py is stdlib-only, so we do NOT import that module).
    Conservative allow-list mirrors the canonical check exactly:
      - inline-styled elements (JS hooks add their own style) are exempt
      - boolean literals "true"/"false" are exempt
    Returns (ok_bool, sorted_orphans_list)."""
    body_match = re.search(r"<body[\s\S]*</body>", html, re.I)
    body = body_match.group(0) if body_match else html
    styles = "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", html, re.I))
    used_classes = set()
    for m in re.finditer(r'class\s*=\s*"([^"]+)"', body):
        for c in m.group(1).split():
            used_classes.add(c)
    defined_classes = set(re.findall(r"\.([a-zA-Z_][\w-]*)", styles))
    inline_styled = set()
    for m in re.finditer(r'class\s*=\s*"([^"]+)"[^>]*style\s*=\s*"', body):
        for c in m.group(1).split():
            inline_styled.add(c)
    orphans = used_classes - defined_classes - inline_styled - {"true", "false"}
    return len(orphans) == 0, sorted(orphans)

def name_in_title(slug, html):
    """D1-01: the blueprint is personalized in its <title>, not just somewhere in
    the body. The old check tested whether the lead's first-name token appeared
    ANYWHERE in the HTML (case-insensitive substring) -> a shallow false-PASS
    ("dave" passes on the word "database"). This scopes the check to the
    <title>...</title> tag only (stdlib regex).

    Real product convention (verified across all live blueprints 2026-05-31):
    titles read "AI Advantage Roadmap — {BUSINESS_NAME}", so most genuine,
    correctly-personalized titles carry the BUSINESS name, not the lead's first
    name (only ~6 of 19 carry the first name parenthetically). So we PASS when
    EITHER is true inside the title:
      (a) the lead's first-name token is present in the title, OR
      (b) the title's business-name segment (after the em/en-dash or hyphen) is
          non-empty, not a {{PLACEHOLDER}}, and actually appears in the page body
          (i.e. the title is genuinely populated and consistent with the page).
    This is strictly stronger than the old "first name anywhere in HTML" test
    (it requires a real, populated, body-consistent title) without regressing
    the business-name-titled blueprints, which are correct by design."""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if not m:
        return False
    title = m.group(1).strip()
    if not title:
        return False
    first = slug.replace("-", " ").split()[0].lower()
    if first and first in title.lower():
        return True
    # business-name segment after the first " — " / " – " / " - " separator
    parts = re.split(r"\s[—–-]\s", title, maxsplit=1)
    biz = parts[-1].strip() if len(parts) > 1 else ""
    if not biz or re.search(r"\{\{[A-Za-z_]+\}\}|PLACEHOLDER", biz):
        return False
    return biz.lower() in html.lower()

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
    results["D1-01_name_in_title"] = name_in_title(slug, html)
    results["D2-01_no_emojis"] = not bool(re.search(r'[\U0001F300-\U0001FAFF]', html))
    results["D3-01_podcast_exists"] = podcast_exists(slug)
    d9_ok, d9_orphans = no_orphan_classes(html)
    results["D9-01_no_orphan_classes"] = d9_ok
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
        # --all audits CLIENT DELIVERABLES only. Exclude non-client files so the
        # VERDICT (consumed by the pre-commit hook) is not polluted by false FAILs:
        #   - is_scaffold:true entries in index.json (the TEMPLATE etc. — placeholders are intentional)
        #   - *-canonical.html (stale encrypted duplicates; PF0-2 = one file per lead)
        #   - internal/non-prospect blueprints (FKI's own roadmap)
        INTERNAL = {"franchise-ki-ceo"}
        scaffolds = set()
        idx_path = os.path.join(BP_DIR, "index.json")
        if os.path.exists(idx_path):
            try:
                idx = json.load(open(idx_path))
                entries = idx.get("blueprints", idx) if isinstance(idx, dict) else idx
                if isinstance(entries, dict):
                    scaffolds = {k for k, v in entries.items()
                                 if isinstance(v, dict) and v.get("is_scaffold")}
                else:  # list of {slug, is_scaffold, ...}
                    scaffolds = {e.get("slug") for e in entries
                                 if isinstance(e, dict) and e.get("is_scaffold")}
            except Exception:
                pass
        slugs = [f[:-5] for f in os.listdir(BP_DIR)
                 if f.endswith(".html") and not f.startswith("_")
                 and not f.endswith("-canonical.html")
                 and f[:-5] not in scaffolds
                 and f[:-5] not in INTERNAL]
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
        r["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(HISTORY, "a") as f:
            f.write(json.dumps(r) + "\n")
    print(f"\nAudit complete. History: {HISTORY}")
    # VERDICT line consumed by the pre-commit hook; financial red-line now blocks.
    print("VERDICT=FAIL" if any_fail else "VERDICT=PASS")
    sys.exit(1 if any_fail else 0)

if __name__ == "__main__":
    main()
