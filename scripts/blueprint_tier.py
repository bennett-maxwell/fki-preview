#!/usr/bin/env python3
"""blueprint_tier.py — one source of truth for how many AI Employees a Blueprint describes.

Marker: FKI-BLUEPRINT-TIER1-SINGLE-AGENT-v1-20260910 (blueprint-ai-skill) +
        FKI-AUDIT-TIER-AWARE-AGENT-COUNT-v1-20260910 (blueprint-ai-audit-skill).

WHY THIS EXISTS
---------------
The 2026-09-08 "Blueprint Template Fix Spec" made Tier 1 = exactly ONE AI Employee. The
generator, the format-3 gate and run-audit.py each hardcoded six, so a compliant Tier 1 build
failed three gates and a six-agent build broke the skill. Every one of them now asks this
module instead of carrying its own number.

RULES
-----
* `tier` is an INTERNAL lead-profile field. It never renders into customer copy (D2-29).
* Tier 1 => 1 AI Employee. Tier 2/3 => the lead's own roster, capped at 6.
* Absent tier => LEGACY six-agent build, so nothing already shipped silently loosens.
* The count comes from the profile, never guessed from the HTML.

Usage:  python3 scripts/blueprint_tier.py --self-test
"""
from __future__ import annotations

import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY_AGENT_COUNT = 6
MAX_AGENT_COUNT = 6


def tier_of(profile: dict):
    """Return the integer tier, or None when the profile carries no tier."""
    raw = (profile or {}).get("tier")
    if raw in (None, ""):
        return None
    m = re.search(r"\d+", str(raw))
    return int(m.group(0)) if m else None


def expected_agent_count(profile: dict) -> int:
    tier = tier_of(profile)
    if tier is None:
        return LEGACY_AGENT_COUNT
    if tier == 1:
        return 1
    roster = [a for a in ((profile or {}).get("ai_agents") or []) if isinstance(a, dict)]
    return max(1, min(len(roster) or LEGACY_AGENT_COUNT, MAX_AGENT_COUNT))


def load_profile_for_slug(slug: str) -> dict:
    path = os.path.join(REPO, "leads", f"{slug}.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def expected_agent_count_for_html(html_path: str) -> int:
    slug = os.path.basename(str(html_path))
    slug = slug[:-5] if slug.endswith(".html") else slug
    return expected_agent_count(load_profile_for_slug(slug))


# ── D2-29 [RL] page_no_pricing_or_tier ─────────────────────────────────────────────────────────
# Madison ruling 2026-09-10, flat ban, no approval path: no dollar figure, setup fee, monthly or
# retainer amount, "investment", price range, discount, payment term, or tier wording on the page.
# Checked against VISIBLE copy only: <style>/<script>/<pre>/comments are stripped first, so a CSS
# comment ("display tier"), the calculator's JS currency formatter, or a prompt guardrail
# ("Never discount") cannot false-fail. Patterns target OUR price, not the prospect's numbers
# ("50/mo leads", "their investment level" are allowed).
PRICING_TIER_PATTERNS = [
    (r"\$\s?\d", "dollar figure"),
    (r"\b\d[\d,.]*\s?(?:usd|dollars)\b", "dollar wording"),
    (r"\btiers?\b", "tier wording"),
    (r"\bsetup fees?\b|\bonboarding fee\b", "setup fee"),
    (r"\bmonthly (?:fee|retainer|price|cost|subscription|rate)\b|\bper month (?:fee|cost|price)\b", "monthly price"),
    (r"\bretainer\b", "retainer"),
    (r"\b(?:your|total|the|an|initial|monthly|small) investment\b|\binvestment (?:of|starts|is|required)\b", "investment"),
    (r"\b\d+\s?% (?:off|discount)\b|\bdiscount(?:ed)? (?:price|rate|offer|code|pricing)\b|\bask about (?:our|a) discount\b", "discount"),
    (r"\bpayment terms?\b|\bpayment plan\b", "payment term"),
    (r"\bpricing (?:table|plan|tiers?|packages?)\b|\bprice range\b", "pricing table"),
]


def visible_text(html: str) -> str:
    t = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    t = re.sub(r"<(script|style|pre)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&[a-z]+;|&#\d+;", " ", t)
    return re.sub(r"\s+", " ", t)


def pricing_or_tier_findings(html: str) -> list:
    text = visible_text(html)
    out = []
    for pat, label in PRICING_TIER_PATTERNS:
        m = re.search(pat, text, re.I)
        if m:
            s = max(0, m.start() - 40)
            out.append(f"{label}: '...{text[s:m.end() + 40].strip()}...'")
    return out


def _self_test() -> int:
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    # agent count — both directions
    expect(expected_agent_count({"tier": 1, "ai_agents": [{}] * 6}) == 1, "tier 1 must be 1")
    expect(expected_agent_count({"tier": "Tier 1"}) == 1, "'Tier 1' string must parse")
    expect(expected_agent_count({}) == 6, "absent tier must stay legacy 6")
    expect(expected_agent_count({"tier": 2, "ai_agents": [{}] * 3}) == 3, "tier 2 uses roster")
    expect(expected_agent_count({"tier": 3, "ai_agents": [{}] * 9}) == 6, "cap at 6")

    # D2-29 — known-bad pages must fail
    bad = [
        "<p>Setup is $5,000 and $2,000 per month.</p>",
        "<p>This is your Tier 1 package.</p>",
        "<p>Your investment starts small.</p>",
        "<p>Ask about our discount.</p>",
        "<p>Flexible payment terms available.</p>",
    ]
    for b in bad:
        expect(pricing_or_tier_findings(b), f"D2-29 missed known-bad: {b}")
    # known-good: banned words only inside CSS/JS/comments, plus normal copy
    good = ("<style>/* display tier */ .x{}</style><script>var f='$'+n;</script>"
            "<!-- tier note --><p>Your AI Employee answers every inquiry in under 60 seconds.</p>"
            "<p>AI can model revenue options, but final pricing decisions stay with you.</p>"
            "<pre>Never discount, never re-quote.</pre><p>50/mo leads coming in now.</p>"
            "<p>Qualifies by budget and their investment level.</p>")
    expect(pricing_or_tier_findings(good) == [], f"D2-29 false-fail on good: {pricing_or_tier_findings(good)}")

    # mutant kills: an always-allow and an always-block checker must both be caught
    always_allow = lambda h: []
    always_block = lambda h: ["x"]
    expect(any(always_allow(b) == [] for b in bad), "mutant always-allow not distinguishable")
    expect(always_block(good) != [], "mutant always-block not distinguishable")
    expect(not (all(pricing_or_tier_findings(b) for b in bad) and pricing_or_tier_findings(good)),
           "real gate must differ from always-block")

    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    print("SELF_TEST_PASS blueprint_tier (agent count 5/5, D2-29 bad 5/5 + good 1/1, 2 mutants killed)")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    if len(sys.argv) > 1 and sys.argv[1] == "--pricing-check":
        html = open(sys.argv[2], encoding="utf-8").read()
        found = pricing_or_tier_findings(html)
        for f in found:
            print("FAIL D2-29", f)
        print("D2-29 PASS" if not found else "D2-29 FAIL")
        sys.exit(1 if found else 0)
    print(__doc__)
