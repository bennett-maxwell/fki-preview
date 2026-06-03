#!/usr/bin/env python3
"""run-audit.py — Blueprint AI audit entrypoint (stdlib + curl). v1.1 2026-06-01"""
import sys, os, subprocess, re, json, urllib.request, hashlib, glob

REPO = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.join(REPO, "blueprints")
HISTORY = os.path.expanduser("~/.openclaw/logs/blueprint-audit-history.jsonl")
THRESHOLD = 0.90  # 90% of non-red-line checks
PODCAST_ALIAS = {
    "watson": "watson-kamoto.mp3",
    "zachary-oldham": "zachary-red-sands.mp3",
}

def curl_http(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"FKI-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except Exception as e:
        return 0

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def podcast_filename(slug):
    return PODCAST_ALIAS.get(slug, f"{slug}.mp3")

def podcast_duration_gate(slug):
    """Red-line D3-03: current Drive Blueprint AI skill uses the 6-20 MB
    walkthrough window plus D3-10 duration >5 minutes.

    The prior repo gate required 16:00-20:00. That contradicted Drive
    blueprint-ai-skill v3.26 and blueprint-ai-audit-skill D3-10, causing a
    false failure on valid NotebookLM walkthroughs that are within the
    mandatory size window and over five minutes.
    """
    MIN_BYTES, MAX_BYTES = 6 * 1024 * 1024, 20 * 1024 * 1024
    MIN_SEC, MAX_SEC = 5 * 60, 20 * 60
    path = os.path.join(REPO, "podcasts", podcast_filename(slug))
    if not os.path.exists(path):
        return False, "podcast file missing"
    size = os.path.getsize(path)
    if size < MIN_BYTES:
        return False, f"too small {size} bytes (min 6MB)"
    if size > MAX_BYTES:
        return False, f"too large {size} bytes (max 20MB)"
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30).stdout.strip()
        secs = int(float(out))
    except Exception as e:
        return False, f"ffprobe failed: {e}"
    mmss = f"{secs//60}:{secs%60:02d}"
    if secs < MIN_SEC:
        return False, f"too short {mmss} (min 5:00)"
    if secs > MAX_SEC:
        return False, f"too long {mmss} (max 20:00) — re-cut tighter"
    return True, f"{mmss}, {size} bytes OK"

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

def format_conformance_gate(html_path):
    checker = os.path.join(REPO, "scripts", "format-conformance-check.py")
    if not os.path.exists(checker):
        return False, "format-conformance-check.py missing"
    try:
        proc = subprocess.run([sys.executable, checker, html_path],
                              capture_output=True, text=True, timeout=60)
        lines = (proc.stdout or proc.stderr or "").strip().splitlines()
        detail = lines[-1] if lines else f"exit {proc.returncode}"
        return proc.returncode == 0, detail
    except Exception as e:
        return False, f"format conformance check error: {e}"

def no_orphan_classes(html):
    style_blocks = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.DOTALL | re.I))
    defined = set(re.findall(r"\.([A-Za-z_][A-Za-z0-9_-]*)", style_blocks))
    used = set()
    for attr in re.findall(r'class=["\']([^"\']+)["\']', html):
        used.update(cls for cls in re.split(r"\s+", attr.strip()) if cls)
    ignored_prefixes = ("is-", "has-", "js-", "active")
    orphan = sorted(
        cls for cls in used
        if cls not in defined and not cls.startswith(ignored_prefixes)
    )
    return len(orphan) == 0, orphan[:25]

def name_in_title(html, slug):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if not m:
        return False
    title = re.sub(r"<[^>]+>", "", m.group(1)).lower()
    first = slug.replace("-", " ").split()[0].lower()
    return first in title

def load_lead(slug):
    path = os.path.join(REPO, "leads", f"{slug}.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def attr_int(html, element_id, attr):
    m = re.search(rf'id="{re.escape(element_id)}"[^>]*\b{re.escape(attr)}="(\d+)"', html)
    return int(m.group(1)) if m else None

def calculator_gate(html, lead):
    failures = []
    ids = set(re.findall(r'id="([^"]+)"', html))
    referenced = set(re.findall(r"getElementById\('([^']+)'\)", html))
    for required in ("q-current", "q-q2", "q-q3", "q-q4"):
        if required in referenced and required not in ids:
            failures.append(f"missing calculator target #{required}")
    monthly_leads = lead.get("monthly_leads") or (lead.get("revenue_declaration") or {}).get("monthly_leads")
    if monthly_leads not in (None, "", "unknown"):
        slider_max = attr_int(html, "slider-leads", "max")
        try:
            monthly_leads = int(float(monthly_leads))
        except Exception:
            monthly_leads = None
        if monthly_leads and slider_max and monthly_leads > slider_max:
            failures.append(f"profile monthly_leads={monthly_leads} exceeds slider-leads max={slider_max}")
    return not failures, failures

def home_services_content_gate(html, lead):
    industry_blob = " ".join(str(lead.get(k, "")) for k in ("industry", "business_type", "service_type", "market")).lower()
    # SaaS/software/CRM vendors that merely SELL TO home-services operators are not
    # themselves home-services businesses. "SaaS CRM for home service businesses"
    # contains the "home service" substring but is a software vendor — its correct
    # copy (churn, recurring revenue, plan tiers) must NOT be flagged by the
    # home-services-operator copy gate. Exclude software vendors first. (2026-06-02)
    if any(term in industry_blob for term in ("saas", "software", " crm", "crm ", "platform", "b2b", "tech company")):
        return True, []
    if not any(term in industry_blob for term in ("plumb", "hvac", "electrical", "home service", "restoration")):
        return True, []
    body = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.I)
    banned = [
        "handing repeatable client setup and onboarding",
        "running an AI content agent",
        "full week of publish-ready content",
        "proposal drafts from your design library",
        "cheapest dollar in saas",
        "login frequency",
        "automation usage",
        "churn risk",
        "recurring revenue locked in",
        "support tickets",
        "account status checks",
        "billing questions",
        "feature requests",
        "product development",
        "client success onboarding agent",
        "complete onboarding lifecycle",
        "payment confirmation",
        "kickoff call",
        "login url",
        "automation templates",
        "proposal specialist",
        "requests a demo",
        "live demo where",
        "plan tier",
        "agency owners",
        "product launches",
        "marketing content as a top operational stress",
        "customer success stories",
        "educational pieces",
        "675+ accounts",
        "675+ businesses",
    ]
    found = [term for term in banned if term.lower() in body.lower()]
    return not found, found

def restaurant_content_gate(html, lead):
    """Restaurant/QSR/food-franchise red-line: block cross-industry drift."""
    industry_blob = " ".join(str(lead.get(k, "")) for k in (
        "industry", "business_type", "service_type", "market"
    )).lower()
    is_restaurant = any(term in industry_blob for term in (
        "restaurant", "qsr", "quick service", "fast casual", "food franchise",
        "food chain", "mexican grill", "catering"
    ))
    if not is_restaurant:
        return True, []

    body = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.I)
    body = re.sub(r'<style[\s\S]*?</style>', '', body, flags=re.I)
    low = body.lower()
    banned = [
        "plumber test business",
        "plumbing",
        "water heater",
        "drain cleaning",
        "sewer",
        "leak detection",
        "technician brief",
        "field-service workflow",
        "servicetitan",
        "housecall pro",
        "emergency intake agent",
        "estimate follow-up agent",
        "maintenance recall agent",
        "dispatch summary agent",
        "quoted-but-not-booked",
        "unsold estimate",
        "maintenance membership",
        "client success onboarding agent",
        "complete onboarding lifecycle",
        "payment confirmation",
        "kickoff call",
        "login url",
        "automation templates",
        "proposal specialist",
        "requests a demo",
        "live demo where",
        "product launches",
        "support tickets",
        "billing questions",
        "feature requests",
        "churn risk",
        "recurring revenue locked in",
    ]
    found = [term for term in banned if term in low]
    required_any = [
        "order", "catering", "guest", "loyalty", "rewards", "location",
        "restaurant", "pickup", "delivery", "crew", "store"
    ]
    if sum(1 for term in required_any if term in low) < 5:
        found.append("restaurant-specific vocabulary below threshold")
    return not found, found

def podcast_source_gate(slug):
    path = os.path.join(REPO, "podcasts", f"{slug}-podcast-source.md")
    if not os.path.exists(path):
        return False, ["missing podcast source"]
    text = open(path, encoding="utf-8", errors="ignore").read()
    failures = []
    if "blueprint.meetadvaita.com/apply" in text:
        failures.append("old apply URL remains")
    if "qualify.html" not in text:
        failures.append("tracked qualifier URL missing")
    if re.search(r"qualify\.html\?[^)\s]*\b(?:lead|biz)=", text, re.I):
        failures.append("podcast source qualifier URL contains prefilled lead/biz fields")
    if re.search(r"first\s+90\s+days", text, re.I):
        failures.append("first 90 days copy remains")
    banned_framing = [
        "NOTEBOOKLM SOURCE DOCUMENT",
        "source material",
        "source document",
        "Sources and Citations",
        "Source:",
        "This page",
        "this document",
        "we are analyzing",
        "we're analyzing",
        "specific client",
    ]
    for phrase in banned_framing:
        if phrase.lower() in text.lower():
            failures.append(f"podcast source contains narrator-risk framing: {phrase}")
    if not re.search(r"Open the audio with EXACTLY these words", text):
        failures.append("podcast source missing direct opening instruction")
    return not failures, failures

def podcast_audio_gate(slug, lead):
    audio_name = podcast_filename(slug)
    audio_path = os.path.join(REPO, "podcasts", audio_name)
    receipt_dir = os.path.join(REPO, "audit-receipts", slug)
    receipt_path = os.path.join(receipt_dir, f"{slug}-production-47.json")
    public_url = f"https://bennett-maxwell.github.io/fki-preview/podcasts/{audio_name}"
    require_public_audio = os.environ.get("BLUEPRINT_REQUIRE_PUBLIC_AUDIO") == "1"
    failures = []

    if not os.path.exists(audio_path):
        return False, [f"missing canonical podcast audio: podcasts/{slug}.mp3"]

    size = os.path.getsize(audio_path)
    if size < 5 * 1024 * 1024:
        failures.append(f"podcast audio too small: {size} bytes")

    current_sha = file_sha256(audio_path)
    data = {}
    if os.path.exists(receipt_path):
        try:
            with open(receipt_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            failures.append(f"invalid podcast transcript receipt: {e}")

    if data.get("audio_sha256") != current_sha:
        os.makedirs(receipt_dir, exist_ok=True)
        lead_name = lead.get("lead_name") or slug.replace("-", " ").title()
        first_name = lead.get("lead_first_name") or str(lead_name).split()[0]
        business_name = lead.get("business_name") or lead_name
        auditor = os.path.join(REPO, "scripts", "podcast_direct_address_audit.py")
        try:
            cmd = [
                sys.executable, auditor,
                "--audio", audio_path,
                "--first-name", first_name,
                "--lead-name", lead_name,
                "--business-name", business_name,
                "--lead", slug,
                "--seconds", "180",
                "--receipt", receipt_path,
                "--json-output",
            ]
            if require_public_audio:
                cmd.extend(["--public-url", public_url])
            # Auto-discover transcript file: try multiple naming conventions
            podcast_dir = os.path.dirname(audio_path)
            base = os.path.splitext(os.path.basename(audio_path))[0]  # slug without .mp3
            transcript_candidates = [
                os.path.join(podcast_dir, f"{base}-elevenlabs-transcript.txt"),
                os.path.join(podcast_dir, f"{base}-transcript.txt"),
                os.path.join(podcast_dir, f"{base}-elevenlabs-raw-elevenlabs-transcript.txt"),
            ]
            for tc in transcript_candidates:
                if os.path.exists(tc):
                    cmd.extend(["--transcript-file", tc])
                    break
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
            try:
                data = json.loads(proc.stdout)
            except Exception:
                with open(receipt_path, encoding="utf-8") as f:
                    data = json.load(f)
            if proc.returncode != 0 and not data:
                failures.append(f"podcast transcript auditor failed: {(proc.stderr or proc.stdout)[-300:]}")
        except Exception as e:
            failures.append(f"podcast transcript auditor error: {e}")

    checks = {
        "direct_address_audio_verified": data.get("direct_address_audio_verified") is True,
        "opening_direct_address_verified": data.get("opening_direct_address_verified") is True,
        "opening_exact_or_close": data.get("opening_exact_or_close") is True,
        "no_banned_audio_phrases": data.get("banned_audio_phrases_found") in ([], None),
        "no_third_person_patterns": data.get("third_person_patterns_found") in ([], None),
        "you_your_count_ge_5": int(data.get("you_your_count") or 0) >= 5,
        "audio_sha_matches": data.get("audio_sha256") == current_sha,
        "public_url_200": True if not require_public_audio else int(data.get("http_code") or 0) == 200,
    }
    for name, ok in checks.items():
        if not ok:
            failures.append(name)
    if data.get("banned_audio_phrases_found"):
        failures.append(f"banned={data.get('banned_audio_phrases_found')}")
    if data.get("third_person_patterns_found"):
        failures.append(f"third_person={data.get('third_person_patterns_found')}")
    return not failures, failures

def resolve_html_path(slug):
    """Resolve a lead slug to its blueprint HTML. Live clones carry a date suffix
    (e.g. avery-martinez-costa-vida-20260601.html), but gatekeeper/gk100 calls
    run-audit.py with the BARE slug. Prefer an exact match; otherwise fall back to
    the newest date-suffixed <slug>-YYYYMMDD.html. Fixes the fleet-wide 0/0 FAIL
    where a bare --lead slug never matched the dated filename (2026-06-02)."""
    exact = os.path.join(BP_DIR, f"{slug}.html")
    if os.path.exists(exact):
        return exact
    matches = glob.glob(os.path.join(BP_DIR, f"{slug}-*.html"))
    dated = sorted(m for m in matches if re.search(r"-\d{8}\.html$", m))
    if dated:
        return dated[-1]
    # Non-dated fallback: only safe when EXACTLY ONE candidate exists. Multiple
    # non-dated matches (e.g. slug-draft.html + slug-backup.html) are ambiguous —
    # silently picking sorted()[-1] could audit the WRONG file and report a false
    # PASS, so surface not-found and let the caller report it rather than guess.
    if len(matches) == 1:
        return matches[0]
    return exact  # non-existent or ambiguous; caller reports not found

def audit_lead(slug):
    results = {}
    redlines = {}  # keys here are HARD red-lines: any False => VERDICT FAIL regardless of score
    html_path = resolve_html_path(slug)
    if not os.path.exists(html_path):
        return {"error": f"{html_path} not found", "score": 0}
    # Canonical slug = the resolved (possibly date-suffixed) filename. Leads json,
    # podcast mp3/source, and receipt dirs all carry the SAME date-suffixed slug,
    # so a bare gk100 --lead slug must be normalized here or every downstream
    # lookup (lead, podcast, source) silently misses (2026-06-02).
    slug = os.path.basename(html_path)[:-5]
    with open(html_path) as f:
        html = f.read()
    lead = load_lead(slug)
    size = len(html)
    results["PF0-1_size_ge_40kb"] = size >= 40000
    pass_ph, tokens = check_placeholder(html)
    results["PF0-4_no_placeholders"] = pass_ph
    format_ok, format_detail = format_conformance_gate(html_path)
    results["PF0-5_format3_dense_scroll_RL"] = format_ok
    redlines["PF0-5_format3_dense_scroll_RL"] = format_ok
    results["D1-01_name_in_title"] = name_in_title(html, slug)
    results["D2-01_no_emojis"] = not bool(re.search(r'[\U0001F300-\U0001FAFF]', html))
    podcast_exists = os.path.exists(os.path.join(REPO, "podcasts", podcast_filename(slug)))
    results["D3-01_podcast_exists"] = podcast_exists
    redlines["D3-01_podcast_exists_RL"] = podcast_exists
    podcast_audio_ok, podcast_audio_detail = podcast_audio_gate(slug, lead)
    results["D3-02_podcast_audio_direct_address_RL"] = podcast_audio_ok
    redlines["D3-02_podcast_audio_direct_address_RL"] = podcast_audio_ok
    duration_ok, duration_detail = podcast_duration_gate(slug)
    results["D3-03_podcast_size_6to20mb_duration_gt5min_RL"] = duration_ok
    redlines["D3-03_podcast_size_6to20mb_duration_gt5min_RL"] = duration_ok
    orphan_ok, orphan_detail = no_orphan_classes(html)
    results["D9-01_no_orphan_classes"] = orphan_ok
    calc_ok, calc_detail = calculator_gate(html, lead)
    results["D7-22_calculator_matches_profile_RL"] = calc_ok
    redlines["D7-22_calculator_matches_profile_RL"] = calc_ok
    hs_ok, hs_detail = home_services_content_gate(html, lead)
    results["D10-22_home_services_copy_clean_RL"] = hs_ok
    redlines["D10-22_home_services_copy_clean_RL"] = hs_ok
    restaurant_ok, restaurant_detail = restaurant_content_gate(html, lead)
    results["D10-23_restaurant_copy_clean_RL"] = restaurant_ok
    redlines["D10-23_restaurant_copy_clean_RL"] = restaurant_ok
    podcast_ok, podcast_detail = podcast_source_gate(slug)
    results["D4-09_podcast_source_funnel_clean_RL"] = podcast_ok
    redlines["D4-09_podcast_source_funnel_clean_RL"] = podcast_ok
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
            "redline_fail": redline_fail, "financial_detail": fin_detail,
            "format_detail": format_detail,
            "orphan_class_detail": orphan_detail,
            "calculator_detail": calc_detail,
            "home_services_detail": hs_detail,
            "restaurant_detail": restaurant_detail,
            "podcast_detail": podcast_detail,
            "podcast_audio_detail": podcast_audio_detail}

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
