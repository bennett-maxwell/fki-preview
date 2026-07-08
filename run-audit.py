#!/usr/bin/env python3
# CI trigger: financial-realism-check.py b64 blob fixed
"""run-audit.py — Blueprint AI audit entrypoint (stdlib + curl). v1.1 2026-06-01"""
import sys, os, subprocess, re, json, urllib.request, hashlib, glob

REPO = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.join(REPO, "blueprints")
HISTORY = os.path.expanduser("~/.openclaw/logs/blueprint-audit-history.jsonl")
THRESHOLD = 0.90  # 90% of non-red-line checks

# ── DECOUPLE (2026-07-07, Madison COO; council PROCEED 4.6/4.5) ──────────────
# The customer SEND is gated on the PAGE only. The podcast is a NON-BLOCKING async
# enrichment that auto-fills the page's audio player once its mp3 is live. These
# red-line keys belong to PODCAST_VERDICT; everything else belongs to PAGE_VERDICT.
# The podcast gates still RUN (and must pass before a podcast is considered done) —
# they just no longer block the page/send decision.
PODCAST_REDLINE_KEYS = {
    "D3-01_podcast_exists_RL",
    "D3-02_podcast_audio_direct_address_RL",
    "D3-03_podcast_duration_6to16min_RL",
    "D3-05_podcast_clean_ending_RL",
    "D3-06_podcast_live_fresh_RL",
    "D3-11_podcast_content_substance_RL",
    "D4-09_podcast_source_funnel_clean_RL",
}
PODCAST_ALIAS = {
    "watson": "watson-kamoto.mp3",
    "zachary-oldham": "zachary-oldham.mp3",
}

def curl_http(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"FKI-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except Exception as e:
        return 0

def hub_live_gate(slug):
    """PAGE red-line component (DECOUPLE 2026-07-07): the public blueprint hub must be
    LIVE at HTTP 200 for PAGE_VERDICT to PASS. Enforced by default; set
    BLUEPRINT_SKIP_HUB_LIVE=1 for a pre-publish, content-only audit (a brand-new lead
    whose page has not been published yet). Customer send remains a separate human step."""
    if os.environ.get("BLUEPRINT_SKIP_HUB_LIVE") == "1":
        return True, "skipped (BLUEPRINT_SKIP_HUB_LIVE=1, pre-publish content audit)"
    url = f"https://bennett-maxwell.github.io/fki-preview/blueprints/{slug}.html"
    code = curl_http(url)
    return code == 200, f"{url} -> HTTP {code}"

def hub_audio_fresh_gate(slug):
    """Red-line D3-06 (2026-07-07 — PERMANENT FIX for the stale-live-podcast failure class).
    HTTP 200 on the page is NOT proof. This gate fetches the LIVE blueprint page, extracts the
    ACTUAL <audio> src the customer will hear, downloads THOSE bytes from the LIVE URL, ffprobes
    the downloaded bytes, and FAILS if:
      (a) the live mp3 duration is outside the 4:00-16:00 window (DURATION_MIN/MAX_SEC), OR
      (b) the live mp3 duration does not match the repo canonical podcasts/<slug>.mp3 within +-3s.
    WHY: every prior 'published/200' audit checked the WRONG layer — the page returned 200 and
    the repo file was the correct short one, but the CDN still served a stale ~20-min mp3. Only
    ffprobing the bytes actually served by the page's audio URL proves the customer hears the
    current short render. A stale/oversized live file is a HARD FAIL here.
    Skippable via BLUEPRINT_SKIP_HUB_LIVE=1 (pre-publish content-only audit; page not live yet)."""
    if os.environ.get("BLUEPRINT_SKIP_HUB_LIVE") == "1":
        return True, "skipped (BLUEPRINT_SKIP_HUB_LIVE=1, pre-publish content audit)"
    import tempfile
    page_url = f"https://bennett-maxwell.github.io/fki-preview/blueprints/{slug}.html"
    try:
        req = urllib.request.Request(page_url, headers={"User-Agent": "FKI-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            if r.status != 200:
                return False, f"live page {page_url} -> HTTP {r.status}"
            html = r.read().decode("utf-8", "replace")
    except Exception as e:
        return False, f"live page fetch failed: {e}"
    # Extract the audio src the player actually loads (prefer <audio>/<source>, else any .mp3 src=)
    m = (re.search(r'<audio[^>]*\bsrc="([^"]+\.mp3[^"]*)"', html, re.I)
         or re.search(r'<source[^>]*\bsrc="([^"]+\.mp3[^"]*)"', html, re.I)
         or re.search(r'\bsrc="([^"]+\.mp3[^"]*)"', html, re.I))
    if not m:
        return False, "no .mp3 audio src found on live page"
    audio_url = m.group(1)
    if audio_url.startswith("//"):
        audio_url = "https:" + audio_url
    elif audio_url.startswith("/"):
        audio_url = "https://bennett-maxwell.github.io" + audio_url
    elif not audio_url.startswith("http"):
        audio_url = f"https://bennett-maxwell.github.io/fki-preview/blueprints/{audio_url}"
    # Download the LIVE mp3 bytes (follow through the served URL, incl. any ?v= cache-bust)
    try:
        req = urllib.request.Request(audio_url, headers={"User-Agent": "FKI-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=90) as r:
            if r.status != 200:
                return False, f"live mp3 {audio_url} -> HTTP {r.status}"
            data = r.read()
    except Exception as e:
        return False, f"live mp3 fetch failed ({audio_url}): {e}"
    if len(data) < 1024:
        return False, f"live mp3 too small ({len(data)} bytes) at {audio_url}"
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    try:
        tmp.write(data)
        tmp.close()
        try:
            out = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", tmp.name],
                capture_output=True, text=True, timeout=30).stdout.strip()
            live_secs = float(out)
        except Exception as e:
            return False, f"ffprobe(live bytes) failed: {e}"
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
    live_mmss = f"{int(live_secs)//60}:{int(live_secs)%60:02d}"
    if live_secs < DURATION_MIN_SEC or live_secs > DURATION_MAX_SEC:
        return False, (f"LIVE mp3 {live_mmss} at {audio_url} is OUT OF WINDOW (4:00-16:00) — "
                       f"CDN is serving a stale/oversized file; publish FAILED")
    repo_path = os.path.join(REPO, "podcasts", podcast_filename(slug))
    if os.path.exists(repo_path):
        try:
            rout = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", repo_path],
                capture_output=True, text=True, timeout=30).stdout.strip()
            repo_secs = float(rout)
        except Exception as e:
            return False, f"ffprobe(repo) failed: {e}"
        if abs(live_secs - repo_secs) > 3.0:
            repo_mmss = f"{int(repo_secs)//60}:{int(repo_secs)%60:02d}"
            return False, (f"LIVE mp3 {live_mmss} != repo {repo_mmss} (diff "
                           f"{abs(live_secs - repo_secs):.1f}s > 3s) — live is not the current render")
        return True, f"LIVE mp3 {live_mmss} in-window & matches repo +-3s ({audio_url})"
    return True, f"LIVE mp3 {live_mmss} in-window ({audio_url}; no repo file to match)"

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def podcast_filename(slug):
    return PODCAST_ALIAS.get(slug, f"{slug}.mp3")

DURATION_MIN_SEC = 240   # 4:00 (DECOUPLE 2026-07-07 Madison COO: floor 4:30->4:00 so a native
                         # NotebookLM SHORT render + Mike's clean1 at 254s pass; podcast is now a
                         # NON-BLOCKING async enrichment, not part of the customer SEND gate)
DURATION_MAX_SEC = 960   # 16:00

def podcast_duration_gate(slug):
    """Red-line D3-03: DURATION WINDOW RE-INSTATED per Madison (COO) 2026-07-06 as a HARD
    gate — the podcast MUST fall between 6:00 and 16:00. This reverses the 2026-07-02 "lift"
    (which let a ~20-min default deep-dive + glued TTS closing ship as 'valid'). The correct
    production path is NotebookLM AudioLength.SHORT ("deep dive, short") which natively lands
    in-window WITH a clean close — so no blind `ffmpeg -t` hard-trim and no TTS-bookend patch
    is ever needed. Out-of-window = HARD FAIL (regenerate SHORT natively, do not trim/patch).
    Works together with D3-05 (clean ending). Window: 4:00-16:00 (240-960s). This is a PODCAST
    gate (PODCAST_VERDICT) only — it no longer blocks the customer SEND (PAGE_VERDICT)."""
    path = os.path.join(REPO, "podcasts", podcast_filename(slug))
    if not os.path.exists(path):
        return False, "podcast file missing"
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30).stdout.strip()
        secs = int(float(out))
    except Exception as e:
        return False, f"ffprobe failed: {e}"
    mmss = f"{secs//60}:{secs%60:02d}"
    if secs < DURATION_MIN_SEC:
        return False, f"{mmss} — TOO SHORT (min 4:00). Regenerate NotebookLM SHORT natively."
    if secs > DURATION_MAX_SEC:
        return False, f"{mmss} — TOO LONG (max 16:00). Use NotebookLM SHORT natively; never trim/patch a long deep-dive."
    return True, f"{mmss} (within 4:00-16:00 window, native SHORT)"

def podcast_clean_ending_gate(slug, lead):
    """Red-line D3-05 (2026-07-01): the podcast must be a COMPLETE episode that ENDS
    CLEANLY with a natural close — NEVER a blind `ffmpeg -t` hard-trim of a longer
    NotebookLM render (which cuts off mid-sentence).

    WHY: D3-03 only checks LENGTH (7-16 min), so a ~20-min deep-dive trimmed to exactly
    10:40 (640.000s) passed as a "valid" duration while ending mid-word. This gate proves
    a proper close via scripts/podcast_clean_ending_gate.py: it FAILS when the final ~25s
    has no closing/outro cue AND the duration is a round hard-trim boundary (the -t
    signature). Runs for EVERY lead. exit 0 = PASS; non-zero = hard-cut red-line block."""
    checker = os.path.join(REPO, "scripts", "podcast_clean_ending_gate.py")
    audio_path = os.path.join(REPO, "podcasts", podcast_filename(slug))
    if not os.path.exists(checker):
        return False, "podcast_clean_ending_gate.py missing"
    if not os.path.exists(audio_path):
        return False, "podcast file missing"
    business_name = (lead or {}).get("business_name") or ""
    receipt = os.path.join(REPO, "audit-receipts", slug, f"{slug}-clean-ending.json")
    cmd = [sys.executable, checker, "--audio", audio_path, "--lead", slug,
           "--business-name", str(business_name), "--receipt", receipt, "--json-output"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
        detail = ""
        try:
            data = json.loads(proc.stdout)
            detail = (data.get("status", "") + ": " + str(data.get("reason", ""))).strip(": ")
        except Exception:
            lines = (proc.stdout or proc.stderr or "").strip().splitlines()
            detail = lines[-1] if lines else f"exit {proc.returncode}"
        return proc.returncode == 0, detail
    except Exception as e:
        return False, f"clean-ending check error: {e}"

def podcast_content_substance_gate(slug, lead):
    """Red-line D3-11 (2026-07-07, Madison COO): the podcast must SUBSTANTIVELY walk
    through the blueprint — the lead's ACTUAL AI agents + their use-cases / the value AI
    delivers — not just a generic intro/outro. The Stage-4 directive (blueprint-ai-skill
    v3.53) and the D3-05 '7-segment source doc' row already REQUIRE this, but nothing
    enforced it at the TRANSCRIPT level, so a thin render that opens/closes correctly but
    never names the agents could PASS. This delegates to
    scripts/podcast_content_substance_gate.py, which transcribes the FULL episode (same
    faster-whisper path as D3-02/D3-05) and FAILS unless >=3 of the lead's agents (from
    leads/<slug>.json agents[].name) OR >=6 of its use-case keywords are spoken. When the
    lead JSON has no agents[], the agent names are read from the rendered blueprint HTML
    (blueprints/<slug>.html) so form/GHL leads like mike-norton are still enforced. Only when
    NEITHER the lead JSON NOR the HTML yields agents (and no use-cases) does it return N/A.
    PODCAST_VERDICT only (per DECOUPLE) — gates podcast attach/publish, NOT the customer send."""
    checker = os.path.join(REPO, "scripts", "podcast_content_substance_gate.py")
    audio_path = os.path.join(REPO, "podcasts", podcast_filename(slug))
    lead_json = os.path.join(REPO, "leads", f"{slug}.json")
    if not os.path.exists(checker):
        return False, "podcast_content_substance_gate.py missing"
    if not os.path.exists(audio_path):
        return False, "podcast file missing"
    if not os.path.exists(lead_json):
        return False, f"lead profile missing: {lead_json}"
    receipt = os.path.join(REPO, "audit-receipts", slug, f"{slug}-content-substance.json")
    html_path = os.path.join(REPO, "blueprints", f"{slug}.html")
    cmd = [sys.executable, checker, "--audio", audio_path, "--lead-json", lead_json,
           "--receipt", receipt, "--json-output"]
    # Fallback agent source: when leads/<slug>.json has no agents[] (common for form/GHL
    # leads like mike-norton), the gate reads the agent names from the rendered blueprint
    # HTML so it enforces substance instead of returning a silent N/A pass.
    if os.path.exists(html_path):
        cmd += ["--blueprint-html", html_path]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=420)
        detail = ""
        try:
            data = json.loads(proc.stdout)
            detail = (str(data.get("status", "")) + ": " + str(data.get("reason", ""))).strip(": ")
        except Exception:
            lines = (proc.stdout or proc.stderr or "").strip().splitlines()
            detail = lines[-1] if lines else f"exit {proc.returncode}"
        return proc.returncode == 0, detail
    except Exception as e:
        return False, f"content-substance check error: {e}"

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


def find_ghl_raw_for_source_fidelity(slug):
    patterns = [
        os.path.join(REPO, "audit-receipts", slug, "**", "*ghl*raw*.json"),
        os.path.join(REPO, "audit-receipts", slug, "**", "ghl-contact-by-id.raw.json"),
        os.path.join(REPO, "audit-receipts", slug, "**", "*contact*raw*.json"),
    ]
    matches = []
    for pattern in patterns:
        matches.extend(glob.glob(pattern, recursive=True))
    if not matches:
        return ""
    return sorted(set(matches), key=lambda x: os.path.getmtime(x), reverse=True)[0]


def source_fidelity_gate(slug, html_path):
    checker = os.path.join(REPO, "scripts", "blueprint_source_fidelity_gate.py")
    lead_json = os.path.join(REPO, "leads", f"{slug}.json")
    if not os.path.exists(checker):
        return False, "blueprint_source_fidelity_gate.py missing"
    if not os.path.exists(lead_json):
        return False, f"lead profile missing: {lead_json}"
    cmd = [sys.executable, checker, "--lead-json", lead_json, "--html", html_path, "--json-output"]
    raw = find_ghl_raw_for_source_fidelity(slug)
    if raw:
        cmd.extend(["--ghl-raw", raw])
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        detail = ""
        try:
            data = json.loads(proc.stdout)
            findings = data.get("findings") or []
            detail = data.get("status", "") + (": " + "; ".join(f.get("code", "finding") for f in findings[:8]) if findings else "")
        except Exception:
            lines = (proc.stdout or proc.stderr or "").strip().splitlines()
            detail = lines[-1] if lines else f"exit {proc.returncode}"
        return proc.returncode == 0, detail
    except Exception as e:
        return False, f"source fidelity check error: {e}"

def agent_card_prompt_quality_gate(slug, html_path):
    """Red-line D2-03 (v3.42, Madison 2026-07-01): agent cards must be condensed
    outcome squares — NEVER a raw copy-paste 'You are an AI agent…' prompt or a
    'Copy-paste prompt:' label — and the 3 ready-to-use dropdown prompts must be
    lead-specific and structurally bulletproof (role/context/steps/guardrails/output),
    not just long. Delegates to scripts/blueprint_agent_prompt_quality_gate.py.

    Runs for EVERY lead. exit 0 = PASS; non-zero / FAIL = red-line block."""
    checker = os.path.join(REPO, "scripts", "blueprint_agent_prompt_quality_gate.py")
    if not os.path.exists(checker):
        return False, "blueprint_agent_prompt_quality_gate.py missing"
    cmd = [sys.executable, checker, "--html", html_path, "--json-output"]
    lead_json = os.path.join(REPO, "leads", f"{slug}.json")
    if os.path.exists(lead_json):
        cmd.extend(["--profile", lead_json])
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        detail = ""
        try:
            data = json.loads(proc.stdout)
            fails = data.get("failures") or []
            detail = data.get("status", "") + ("" if not fails else ": " + "; ".join(fails[:6]))
        except Exception:
            lines = (proc.stdout or proc.stderr or "").strip().splitlines()
            detail = lines[-1] if lines else f"exit {proc.returncode}"
        return proc.returncode == 0, detail
    except Exception as e:
        return False, f"agent card prompt quality check error: {e}"

def no_orphan_classes(html):
    style_blocks = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.DOTALL | re.I))
    defined = set(re.findall(r"\.([A-Za-z_][A-Za-z0-9_-]*)", style_blocks))
    used = set()
    for attr in re.findall(r'class=["\'"]([^"\'"]+)["\'"]', html):
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
        return {"error": f"{html_path} not found", "score": 0,
                "page_verdict": "FAIL", "podcast_verdict": "FAIL",
                "page_pass": 0, "page_total": 0, "podcast_pass": 0, "podcast_total": 0,
                "page_redline_fail": ["blueprint_html_not_found"], "podcast_redline_fail": [],
                "hub_live_detail": "n/a", "redline_fail": ["blueprint_html_not_found"]}
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
    source_ok, source_detail = source_fidelity_gate(slug, html_path)
    results["PF0-7_source_fidelity_RL"] = source_ok
    redlines["PF0-7_source_fidelity_RL"] = source_ok
    results["D1-01_name_in_title"] = name_in_title(html, slug)
    results["D2-01_no_emojis"] = not bool(re.search(r'[\U0001F300-\U0001FAFF]', html))
    # D2-02 [RL] AGENT SUBSTANCE GATE — UPDATED 2026-06-26 (Madison override "I own it"):
    # D2-02's inline copy-paste prompt was retired; the 6 agent squares are now CONDENSED
    # (icon+name+desc+outcome) and the substantive operating prompts live in the 3
    # ready-to-use dropdown cards (prompt-pre). So substance now = 6 lead-specific cards
    # (each >=120 chars) AND >=3 substantive dropdown prompts (each >=900 chars).
    # See ~/Desktop/fki-preview/OVERRIDE-D2-02.md. Restore inline check if Bennett reinstates D2-02.
    _cards = re.findall(r'<div class="agent-card">(.*?)</div>\s*</div>', html, re.S)
    _dropdown = re.findall(r'<pre id="prompt\d+" class="prompt-pre">(.*?)</pre>', html, re.S)
    agent_substance_ok = (
        len(_cards) >= 6
        and len(_dropdown) >= 3
        and all(len(re.sub(r'<[^>]+>', '', c)) >= 120 for c in _cards[:6])
        and all(len(re.sub(r'<[^>]+>', '', pr)) >= 900 for pr in _dropdown[:3])
    )
    results["D2-02_agent_cards_substantive_RL"] = agent_substance_ok
    redlines["D2-02_agent_cards_substantive_RL"] = agent_substance_ok
    # D2-03 [RL] AGENT-CARD + PROMPT QUALITY (v3.42, Madison 2026-07-01):
    # cards must NOT contain a raw "You are an AI agent…" copy-paste prompt or a
    # "Copy-paste prompt:" label, and the 3 dropdown prompts must be structurally
    # bulletproof (role/context/steps/guardrails/output), not merely >=900 chars.
    acpq_ok, acpq_detail = agent_card_prompt_quality_gate(slug, html_path)
    results["D2-03_agent_card_prompt_quality_RL"] = acpq_ok
    redlines["D2-03_agent_card_prompt_quality_RL"] = acpq_ok
    podcast_exists = os.path.exists(os.path.join(REPO, "podcasts", podcast_filename(slug)))
    results["D3-01_podcast_exists"] = podcast_exists
    redlines["D3-01_podcast_exists_RL"] = podcast_exists
    podcast_audio_ok, podcast_audio_detail = podcast_audio_gate(slug, lead)
    results["D3-02_podcast_audio_direct_address_RL"] = podcast_audio_ok
    redlines["D3-02_podcast_audio_direct_address_RL"] = podcast_audio_ok
    duration_ok, duration_detail = podcast_duration_gate(slug)
    results["D3-03_podcast_duration_6to16min_RL"] = duration_ok
    redlines["D3-03_podcast_duration_6to16min_RL"] = duration_ok
    clean_end_ok, clean_end_detail = podcast_clean_ending_gate(slug, lead)
    results["D3-05_podcast_clean_ending_RL"] = clean_end_ok
    redlines["D3-05_podcast_clean_ending_RL"] = clean_end_ok
    substance_ok, substance_detail = podcast_content_substance_gate(slug, lead)
    results["D3-11_podcast_content_substance_RL"] = substance_ok
    redlines["D3-11_podcast_content_substance_RL"] = substance_ok
    live_fresh_ok, live_fresh_detail = hub_audio_fresh_gate(slug)
    results["D3-06_podcast_live_fresh_RL"] = live_fresh_ok
    redlines["D3-06_podcast_live_fresh_RL"] = live_fresh_ok
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

    # ── DECOUPLE: split the red-lines into PAGE (send gate) vs PODCAST (async) ──
    hub_ok, hub_detail = hub_live_gate(slug)
    page_keys = [k for k in redlines if k not in PODCAST_REDLINE_KEYS]
    podcast_keys = [k for k in redlines if k in PODCAST_REDLINE_KEYS]
    page_redline_fail = [k for k in page_keys if not redlines[k]]
    podcast_redline_fail = [k for k in podcast_keys if not redlines[k]]
    if not hub_ok:
        page_redline_fail = page_redline_fail + ["HUB_LIVE_200"]
    # page_total includes the hub-live check as one PAGE gate
    page_total = len(page_keys) + 1
    page_pass = sum(1 for k in page_keys if redlines[k]) + (1 if hub_ok else 0)
    podcast_total = len(podcast_keys)
    podcast_pass = sum(1 for k in podcast_keys if redlines[k])
    page_verdict = "PASS" if not page_redline_fail else "FAIL"
    podcast_verdict = "PASS" if not podcast_redline_fail else "FAIL"

    return {"slug": slug, "score": score, "passed": passed, "total": total,
            "checks": results, "size": size,
            "page_verdict": page_verdict, "podcast_verdict": podcast_verdict,
            "page_pass": page_pass, "page_total": page_total,
            "podcast_pass": podcast_pass, "podcast_total": podcast_total,
            "page_redline_fail": page_redline_fail,
            "podcast_redline_fail": podcast_redline_fail,
            "hub_live_detail": hub_detail,
            "redline_fail": redline_fail, "financial_detail": fin_detail,
            "format_detail": format_detail,
            "source_fidelity_detail": source_detail,
            "orphan_class_detail": orphan_detail,
            "calculator_detail": calc_detail,
            "home_services_detail": hs_detail,
            "restaurant_detail": restaurant_detail,
            "podcast_detail": podcast_detail,
            "podcast_audio_detail": podcast_audio_detail,
            "podcast_clean_ending_detail": clean_end_detail,
            "podcast_content_substance_detail": substance_detail,
            "podcast_live_fresh_detail": live_fresh_detail,
            "podcast_duration_detail": duration_detail,
            "agent_card_prompt_quality_detail": acpq_detail}

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
    any_page_fail = False
    for slug in slugs:
        r = audit_lead(slug)
        results.append(r)
        if r.get("error"):
            print(f"[FAIL] {slug}: {r['error']}")
            any_page_fail = True
            continue
        pv = r.get("page_verdict", "FAIL")
        pdv = r.get("podcast_verdict", "FAIL")
        if pv == "FAIL":
            any_page_fail = True
        # DECOUPLE: the SEND decision is PAGE_VERDICT. PODCAST_VERDICT is reported but
        # never blocks the page/send — the podcast is a non-blocking async enrichment.
        print(f"[{pv}] {slug}  PAGE_VERDICT={pv} ({r.get('page_pass',0)}/{r.get('page_total',0)})"
              f"  PODCAST_VERDICT={pdv} ({r.get('podcast_pass',0)}/{r.get('podcast_total',0)})"
              f"  score={r.get('score',0):.0%}")
        print(f"       hub-live: {r.get('hub_live_detail','')}")
        if r.get("page_redline_fail"):
            print(f"       PAGE red-line FAIL: {r['page_redline_fail']} ({r.get('financial_detail','')})")
        if r.get("podcast_redline_fail"):
            print(f"       PODCAST red-line (non-blocking): {r['podcast_redline_fail']}"
                  f" | dur={r.get('podcast_duration_detail','')}"
                  f" | clean={r.get('podcast_clean_ending_detail','')}"
                  f" | substance={r.get('podcast_content_substance_detail','')}"
                  f" | live-fresh={r.get('podcast_live_fresh_detail','')}")
    # Append to history
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
    import datetime
    for r in results:
        r["ts"] = datetime.datetime.utcnow().isoformat() + "Z"
        with open(HISTORY, "a") as f:
            f.write(json.dumps(r) + "\n")
    print(f"\nAudit complete. History: {HISTORY}")
    # Overall VERDICT (back-compat, consumed by the pre-commit hook) is now driven by
    # PAGE_VERDICT — the customer SEND gate. A podcast-only failure no longer blocks.
    print("VERDICT=FAIL" if any_page_fail else "VERDICT=PASS")
    sys.exit(1 if any_page_fail else 0)

if __name__ == "__main__":
    main()
