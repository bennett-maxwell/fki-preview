#!/usr/bin/env python3
"""blueprint-data-plausibility.py — catches WRONG-PER-BUSINESS and FABRICATED data
that render/consistency gates are blind to.

Why this exists: the consistency + D9 gates passed while every blueprint showed
Court Lundberg's numbers (12 leads / $45K contract / 18% close). Court is a
residential plumbing/HVAC shop (~$850 avg job) — a $45K "average contract" is
not just leaked, it is implausible for the business type. Structural gates never
look at whether a NUMBER MAKES SENSE for THIS business. This gate does.

Checks per canonical blueprint:
  P1  No fabricated current-state literals  (||45000/12/18, hard-coded leads/close labels)
  P2  No cross-client identical current-state stat block (the original leak signature)
  P3  Displayed monthly_leads matches the lead JSON (or honest "(enter yours)")
  P4  Calculator does not auto-paint ROI on load (calcTouched guard present)
  P5  Contract/job-value defaults plausible for business_type (no $25k+ default on a trade)
  P6  Business-type-inappropriate metric WARNING (e.g. LinkedIn lead-gen on residential trades)

Exit 0 = all pass.  Exit 1 = at least one HARD check failed.  WARN does not fail.
Network-free; safe in pre-commit.
"""
import json, re, sys, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
BP = REPO / "blueprints"
LEADS = REPO / "leads"
CANON = ("alex-ramos austin-iron-horse branson-maxwell brent-attaway brittney-warnick "
         "chris-lpnw court-lundberg dave-wood jaden-mecham melissa-tash-srp paul-muus "
         "rey-31-consulting rush-evans watson zachary-oldham").split()
# slug -> lead json filename where it differs from slug
LEAD_FILE = {"rey-31-consulting": "rey-31consulting", "zachary-oldham": "zachary-red-sands"}

# Trades / local-service businesses where a five-figure "average contract" and
# LinkedIn lead-gen are implausible.
LOCAL_TRADE_TYPES = {"plumbing", "hvac", "trades", "home-services", "restoration",
                     "landscaping", "cleaning", "photography", "med-spa", "medspa",
                     "property-management", "hospitality", "restaurant", "food"}

FAB = [
    (r'\|\|\s*45000', "JS fallback contract 45000"),
    (r'id="val-leads">12<', 'hard-coded leads label "12"'),
    (r'id="val-close">18%<', 'hard-coded close label "18%"'),
    (r'id="res-time">6\.5 hrs/wk<', 'fabricated "6.5 hrs/wk" saved'),
    (r'roi-stat-grid">\s*<div class="roi-stat"><div class="val">12<', "leaked hero stat block"),
]

def load_lead(slug):
    f = LEADS / f"{LEAD_FILE.get(slug, slug)}.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text())
    except Exception:
        return {}

def current_state_signature(html):
    """Fingerprint of the numbers a page presents as the client's CURRENT reality."""
    labels = re.findall(r'id="val-(?:leads|close|contract)">([^<]*)<', html)
    return "|".join(labels)

def check_one(slug):
    f = BP / f"{slug}.html"
    if not f.exists():
        return [f"{slug}: FILE NOT FOUND"], 1
    html = f.read_text()
    lead = load_lead(slug)
    btype = (lead.get("business_type") or lead.get("industry") or "").lower()
    fails, warns = [], []

    # P1 fabricated literals
    for pat, desc in FAB:
        if re.search(pat, html):
            fails.append(f"P1 fabricated: {desc}")

    # P4 load-guard present
    if "if (!calcTouched)" not in html:
        fails.append("P4 calculator missing calcTouched load-guard (will auto-paint ROI)")

    # P3 monthly_leads consistency (only if page shows a concrete number, not 'enter yours')
    leads_label = re.search(r'id="val-leads">([^<]*)<', html)
    if leads_label:
        shown = leads_label.group(1).strip()
        if shown and not shown.lower().startswith("(enter"):
            real = str(lead.get("monthly_leads", "")).strip()
            if real and real not in ("—", "-", "") and shown.replace(",", "") != real.replace(",", ""):
                fails.append(f"P3 leads shown '{shown}' != lead JSON '{real}'")

    # P5 contract default plausibility for local trades
    m = re.search(r'id="slider-contract"[^>]*value="(\d+)"', html)
    if m and btype:
        val = int(m.group(1))
        if any(t in btype for t in LOCAL_TRADE_TYPES) and val >= 10000:
            fails.append(f"P5 contract default ${val:,} implausible for business_type '{btype}'")

    # P6 inappropriate-metric WARN
    if btype and any(t in btype for t in LOCAL_TRADE_TYPES):
        if re.search(r'LinkedIn (?:Leads|Curated|Qualified|Conversations)', html):
            warns.append(f"P6 LinkedIn lead-gen present on local-trade business_type '{btype}' (review relevance)")

    return fails, warns

def main():
    sigs, all_fail = {}, 0
    print("blueprint-data-plausibility: scanning 15 canon blueprints")
    for slug in CANON:
        fails, warns = check_one(slug)
        sigs.setdefault(current_state_signature((BP / f"{slug}.html").read_text()
                        if (BP / f"{slug}.html").exists() else ""), []).append(slug)
        if isinstance(warns, int):  # file-not-found path
            print(f"  ❌ {slug}: {fails}"); all_fail = 1; continue
        if fails:
            all_fail = 1
            for x in fails: print(f"  ❌ {slug}: {x}")
        for w in warns: print(f"  ⚠  {slug}: {w}")
        if not fails:
            print(f"  ✅ {slug}: plausibility OK")

    # P2 cross-client identical current-state block
    for sig, slugs in sigs.items():
        concrete = sig and not all(p.lower().startswith("(enter") or p == "" for p in sig.split("|"))
        if concrete and len(slugs) > 1:
            print(f"  ❌ P2 LEAK: {len(slugs)} clients share identical current-state numbers '{sig}': {slugs}")
            all_fail = 1
    if all(s.split("|")[0].lower().startswith("(enter") or s == "" for s in sigs):
        print("  ✅ P2 no cross-client identical current-state stat block")

    print("data-plausibility:", "PASS" if all_fail == 0 else "FAIL")
    return all_fail

if __name__ == "__main__":
    sys.exit(main())
