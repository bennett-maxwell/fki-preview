#!/usr/bin/env python3
"""
financial-realism-check.py  — Domain 7 enforcement (Blueprint AI audit)
Catches the exact defect Bennett flagged 2026-05-29: a residential plumbing
company (Court Lundberg / Rare Breed Plumbing) shipped with a $25K-$120K ROI
slider and a $45,000 "average contract value" default — generic franchise-
consulting numbers cloned onto every business regardless of industry.

This is REAL enforcement, not "manual review". It runs the financial-credibility
checks (Domain 7) against blueprint HTML and emits a per-file pass/fail + reason.

Usage:  python3 financial-realism-check.py --all
        python3 financial-realism-check.py --file blueprints/court-lundberg.html
Exit 0 only if every checked file passes every red-line financial check.
"""
import re, sys, json, glob, os, collections

BLUEPRINTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blueprints")

# Industry -> realistic single-transaction band (USD low, high) for the value a
# customer actually pays per deal/job/ticket/treatment. Used to sanity-check the
# ROI calculator's "average contract/deal value" default + JS fallback.
# Bands are deliberately wide; the check only fails on clearly-wrong defaults
# (e.g. a $45K default for a $300-$15K home-services job).
INDUSTRY_BANDS = {
    "home_services":      (300, 20000,  "job/ticket"),     # plumbing, HVAC, electrical
    "photography":        (250, 8000,   "session/package"),
    "video_production":   (800, 50000,  "project"),
    "medspa":             (150, 6000,   "treatment/package"),
    "food_franchise":     (8,   60,     "ticket"),          # per-customer check
    "retail_firearms":    (300, 6000,   "ticket"),
    "design_agency":      (1500,40000,  "project"),
    "consulting":         (3000,150000, "engagement"),
    "retail":             (50,  2000,   "purchase/transaction"),    # retail sporting goods
    "insurance":          (500, 10000,  "policy/annual premium"),
    "professional_services": (1000,50000, "contract/project"),
    "ai_consulting":      (3000,25000,  "contract"),
    "crm_software":       (1200,75000,  "contract/ARR"),
    "medical_devices":    (5000,500000, "contract"),
    "property_mgmt":      (1000,50000,  "annual mgmt fee"),
    "marketing_agency":   (250, 25000,  "retainer/project"),   # marketing services (Sky/BME form: industry=marketing)
    "heavy_equipment":    (2000,200000, "equipment/contract"), # road equipment mfg/services (Diamond Road; muni contracts)
    "unknown":            (None, None,  "deal"),            # cannot verify -> flagged
}

# Per-lead industry classification (from business name / known intake).
LEAD_INDUSTRY = {
    "john-doe-sporting-goods-20260604": "retail",
    "court-lundberg":   "home_services",      # Rare Breed Plumbing, Heating & Air
    "branson-maxwell":  "photography",
    "melissa-tash-srp": "photography",
    "rush-evans":       "photography",
    "watson":           "video_production",   # Kamoto Productions
    "jaden-mecham":     "medspa",             # NPI Medspa
    "dave-wood":        "food_franchise",     # Mahana Fresh
    "austin-iron-horse":"retail_firearms",    # Iron Horse Armory
    "brittney-warnick": "design_agency",      # Warnick Design
    "paul-muus":        "consulting",
    "rey-31-consulting":"consulting",
    "chris-lpnw":       "consulting",         # LPNW LLC (best-known: services)
    "brent-attaway":    "crm_software",       # CRMX
    "alex-ramos":       "medical_devices",    # DePuy Synthes
    "zachary-oldham":   "property_mgmt",      # Red Sands Vacation Properties
    "sky-bme-llc":      "marketing_agency",   # BME LLC (GHL form 2026-06: industry=marketing, GoHighLevel/Asana)
    "garlon-maxwell":   "heavy_equipment",   # Diamond Road (GHL form 2026-06: heavy equipment, 500k-1m)
    "mark-bustamonte":  "consulting",        # Upfinity Consulting (GHL form 2026-06: consulting/business services)
    "simon-harwood-disruptive-foods-20260618": "food_franchise",  # Disruptive Foods — street-food product distribution to retail (GHL form 2026-06-18); per-customer ticket band
    "asif-jam-equities-20260618":              "food_franchise",  # JAM Equities — multi-unit QSR/restaurant operator (GHL form 2026-06-18); per-guest ticket band
    # Demo/sample blueprints (no leads/*.json intake). Classified by the self-declared
    # business identity in the page <title> — the SAME standard the canon 15 use — so the
    # financial gate keeps VERIFYING their bands instead of silently skipping them. A demo
    # showing a wrong-industry slider (e.g. a $45K plumber) is the exact defect we ban for
    # real clients; NON_LEAD exclusion would reintroduce the silent-skip bug this script warns about.
    "jason-martinez":   "home_services",      # Peak Comfort HVAC
    "mike-johnson":     "home_services",      # Johnson Plumbing LLC
    "rj-kitchenguard":  "home_services",      # Kitchen Guard (commercial kitchen fire suppression)
    "claude-code":      "ai_consulting",       # Claude Code Agency — AI agent development, $5K contracts
}

def _load_slug_industry():
    cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "scripts", "roi-industry-config.json")
    try:
        with open(cfg) as f:
            slug_industry = json.load(f).get("slug_industry", {})
    except Exception:
        return
    if isinstance(slug_industry, dict):
        for slug, industry in slug_industry.items():
            if industry in INDUSTRY_BANDS:
                LEAD_INDUSTRY[str(slug)] = str(industry)

_load_slug_industry()

# Industries whose buyers realistically run a LinkedIn lead-gen / social-selling
# motion. Single source of truth = scripts/roi-industry-config.json
# ("b2b_linkedin_industries"); fall back to this inline default if the config is
# missing so the gate never silently no-ops. The ROI calculator's
# "LinkedIn Leads Added/Month" slider feeds the headline revenue lift, so showing
# it on a trades/consumer-local business (a plumber, a restaurant) inflates the
# projection with an irrelevant channel — the same industry-inappropriateness
# class as a $45K average contract on a plumber.
def _load_b2b_linkedin():
    cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "scripts", "roi-industry-config.json")
    try:
        with open(cfg) as f:
            return set(json.load(f).get("b2b_linkedin_industries", []))
    except Exception:
        return {"consulting", "crm_software", "medical_devices",
                "design_agency", "video_production"}

B2B_LINKEDIN = _load_b2b_linkedin()

def grab(pattern, html, flags=0):
    m = re.search(pattern, html, flags)
    return m.groups() if m else None

def check_file(path, clone_registry):
    slug = os.path.basename(path)[:-5]
    html = open(path, encoding="utf-8", errors="ignore").read()
    fails, warns = [], []
    industry = LEAD_INDUSTRY.get(slug, "unknown")
    lo, hi, unit = INDUSTRY_BANDS[industry]

    # --- D7-01/D7-17 contract-value default within band (fill-in OR legacy slider) ---
    # Template now uses a typed fill-in <input type="number" id="sl-contract" min=".." value="..">
    # with NO max (owner types any value); older blueprints used a slider id="slider-contract"
    # with min/max/value. Match either id, then parse attrs individually so a missing max is OK.
    contract_tag = grab(r'(<input[^>]*id="s(?:l|lider)-contract"[^>]*>)', html)
    contract_min = contract_max = slider_default = None
    if contract_tag:
        tag = contract_tag[0]
        m_mn = re.search(r'min="(\d+)"', tag);   contract_min   = int(m_mn.group(1)) if m_mn else None
        m_mx = re.search(r'max="(\d+)"', tag);   contract_max   = int(m_mx.group(1)) if m_mx else None
        m_vv = re.search(r'value="(\d+)"', tag); slider_default = int(m_vv.group(1)) if m_vv else None
    js = grab(r"s(?:l|lider)-contract'\)\.value\)\s*\|\|\s*(\d+)", html)
    js_fallback = int(js[0]) if js else None
    # clone-dedup fingerprint: the numbers actually present on the contract field
    slider_triple = tuple(x for x in (contract_min, contract_max, slider_default) if x is not None) or None

    if industry == "unknown":
        # D10-05 [RL]: an unclassified lead means we CANNOT verify its money math fits
        # the industry — exactly the condition that let Court Lundberg's $45k clone ship.
        # Per the audit skill this is a RED-LINE FAIL (don't ship unverified), not a warning.
        # We never guess an industry (guessed numbers = the original defect); add the lead to
        # LEAD_INDUSTRY from real intake before it can pass.
        fails.append(f"D10-05 [RL] industry unclassified — cannot verify financials (add '{slug}' to LEAD_INDUSTRY from intake)")
    # JS fallback band check — the fill-in's empty-sentinel "|| 0" is intentional (empty = $0
    # contribution), not a seeded default, so it is exempt from the band check.
    if lo is not None and js_fallback is not None and js_fallback != 0 and not (lo <= js_fallback <= hi):
        fails.append(f"D7-17 [RL] JS fallback ${js_fallback:,} outside {industry} band ${lo:,}-${hi:,}")
    if lo is not None and slider_default is not None and not (lo <= slider_default <= hi):
        fails.append(f"D7-01 [RL] contract default ${slider_default:,} outside {industry} band ${lo:,}-${hi:,}")
    # D7-03 range overlap applies only to a bounded slider (has max); a fill-in has no max.
    if lo is not None and contract_min is not None and contract_max is not None and (contract_max < lo or contract_min > hi):
        fails.append(f"D7-03 slider range ${contract_min:,}-${contract_max:,} does not overlap {industry} band ${lo:,}-${hi:,}")

    # --- D7-10 label uses the right transaction noun for the industry ---
    if re.search(r'[Aa]verage [Cc]ontract [Vv]alue', html) and unit not in ("contract", "contract/ARR", "annual mgmt fee"):
        warns.append(f"D7-10 label 'Average Contract Value' but {industry} sells by '{unit}'")

    # --- D7-18 calculator/content FIELD RELEVANCE: B2B-only LinkedIn on non-B2B ---
    # The "LinkedIn Leads Added/Month" slider (id="slider-linkedin") feeds the
    # headline AI revenue lift (aiLeads = leads*1.15 + linkedinLeads). On a
    # trades/consumer-local business that has no LinkedIn pipeline, this inflates
    # the ROI projection with an irrelevant channel, the same defect class Bennett
    # flagged for the $45K-contract-on-a-plumber. This is now a red-line fail for
    # the checked file, because the generator has a home-services sanitizer.
    if industry not in ("unknown",) and industry not in B2B_LINKEDIN \
       and re.search(r'id="slider-linkedin"', html):
        fails.append(
            f"D7-18 [RL] B2B-only 'LinkedIn Leads Added/Month' lever shown on non-B2B "
            f"'{industry}' — inflates ROI projection with an irrelevant channel "
            f"(remove/replace it for trades)")

    if industry == "home_services":
        body = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.I)
        legacy_terms = [
            "LinkedIn",
            "luxury",
            "venue",
            "corporate planner",
            "event shoot",
            "gala",
            "Pinterest",
            "Apply to Work With Us",
            # "Command Center" removed — format-3 gold template uses "command center" in
            # explanatory copy (correct brand language). The OLD violation was the tab-nav
            # section id="command-center" pattern, which format-conformance-check.py FC-01
            # already blocks (old tab sections fail PF0-5 before reaching this check).
        ]
        leaked = [term for term in legacy_terms if re.search(r"\b" + re.escape(term) + r"\b", body, re.I)]
        # Check for the OLD command-center TAB SECTION (the real D10-21 violation) separately
        if re.search(r'id=["\']command-center["\']', html, re.I):
            leaked.append("Command Center tab-section (id=command-center — old format, must regenerate)")
        if leaked:
            fails.append(
                "D10-21 [RL] home-services blueprint contains wrong-industry/template language: "
                + ", ".join(sorted(set(leaked), key=str.lower))
            )

    # --- D7-02 clone detection: record the slider triple WITH industry for compare ---
    # The real defect Bennett flagged is ONE financial profile cloned across
    # DIFFERENT industries (a plumber + a med-device co + a restaurant all on the
    # same $25K-$120K slider). Two photography studios sharing a photography range
    # is correct, not a clone. So we key by (triple, industry) and only fail when a
    # single triple spans >=2 distinct industries (or all blueprints share one).
    if slider_triple:
        clone_registry[slider_triple].append((slug, industry))

    # --- D7-04 fabricated hardcoded $ figures in client copy (outside <script>/<input>) ---
    body = re.sub(r'<script[\s\S]*?</script>', '', html)
    body = re.sub(r'<input[^>]*>', '', body)
    hard = re.findall(r'\$\s?(\d{1,3}(?:,\d{3})+|\d{4,})\b', body)
    big = [h for h in hard if int(h.replace(',', '')) >= 10000]
    if big:
        warns.append(f"D7-04 hardcoded large $ figures in copy: {sorted(set(big))[:5]} — must trace to intake/source")

    return {"slug": slug, "industry": industry, "band": [lo, hi],
            "slider_default": slider_default, "js_fallback": js_fallback,
            "fails": fails, "warns": warns}

def main():
    args = sys.argv[1:]
    if "--file" in args:
        files = [args[args.index("--file") + 1]]
    else:
        # NON_LEAD = build template + internal demos + canonical duplicates. Everything
        # else is treated as a real prospect blueprint and MUST be financially verifiable.
        # Previously --all filtered to only slugs already in LEAD_INDUSTRY, which SILENTLY
        # skipped any unmapped lead — a brand-new blueprint with a $45k clone slider would
        # never be checked. Now --all scans every real-lead file; unmapped => D10-05 fail.
        NON_LEAD = {"TEMPLATE", "franchise-ki-ceo", "rush-evans-canonical", "local-webhookprobe"}
        files = sorted(glob.glob(os.path.join(BLUEPRINTS, "*.html")))
        files = [f for f in files
                 if not os.path.basename(f).startswith("_")
                 and os.path.basename(f)[:-5] not in NON_LEAD]
    clone_registry = collections.defaultdict(list)
    results = [check_file(f, clone_registry) for f in files]

    # D7-02 [RL] flag a slider triple that spans >=2 DISTINCT industries (true
    # cross-industry clone — the original $25K/$45K-everywhere defect). A triple
    # confined to a single industry is a legitimate shared modeling range.
    clones = {}
    for trip, entries in clone_registry.items():
        industries = {ind for _, ind in entries}
        if len(industries) >= 2:
            slugs = [s for s, _ in entries]
            clones[trip] = (slugs, industries)
            for r in results:
                if r["slug"] in slugs:
                    r["fails"].append(
                        f"D7-02 [RL] identical ROI slider {trip} cloned across "
                        f"{len(industries)} industries {sorted(industries)} — not personalized")

    npass = sum(1 for r in results if not r["fails"])
    print(f"{'SLUG':<20} {'INDUSTRY':<16} {'DEFAULT':>9} {'JS':>8}  RESULT")
    print("-" * 78)
    for r in results:
        res = "PASS" if not r["fails"] else f"FAIL ({len(r['fails'])})"
        print(f"{r['slug']:<20} {r['industry']:<16} {str(r['slider_default']):>9} {str(r['js_fallback']):>8}  {res}")
        for f in r["fails"]:
            print(f"      ✗ {f}")
        for w in r["warns"]:
            print(f"      ⚠ {w}")
    print("-" * 78)
    print(f"FINANCIAL-REALISM: {npass}/{len(results)} pass red-line financial checks")
    d7_18 = [r["slug"] for r in results if any("D7-18" in w for w in r["warns"])]
    if d7_18:
        print(f"D7-18 FIELD-RELEVANCE WARN: {len(d7_18)} non-B2B blueprint(s) show the LinkedIn lever "
              f"(staged for template gate): {sorted(d7_18)}")
    if clones:
        print(f"CROSS-INDUSTRY CLONE GROUPS: {[ (t, sorted(inds)) for t,(s,inds) in clones.items() ]}")
    sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
