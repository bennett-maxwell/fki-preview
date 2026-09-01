#!/usr/bin/env python3
"""
advaita-rebrand.py — apply the canonical Advaita brand to a blueprint page.

Brand authority: brand-guide-advaita-skill v2.0
  Drive 1FR6BqiapCJ0KMvpmVNE8URyNrGxFdjvI (folder 16OVg07toZ6XzAld3xuzZhbfMfItvdKL7)
  Plum #4A1F63 (human) · Saffron #F5A623 (AI) · Warm Ivory #F7F2E9
  Ink Plum #17111F · Mauve Mist #EADFF0
  Fonts: Space Grotesk (display) + Inter (body). NEVER blue/teal/cold gradients.
  Clay #CC6B45 deprecated 2026-07-09 (WO-V2-003) — not used here.

Scope guard: COLORS · FONTS · LOGO TREATMENT ONLY.
No layout changes, no copy changes, no structural/markup changes.

Every rule below is exact-string. Any rule that does not match is reported and
the run exits non-zero, so palette drift can never pass silently.

Usage:
  advaita-rebrand.py <in.html> <out.html>
  advaita-rebrand.py --in-place <file.html>
  advaita-rebrand.py --check <file.html>     # verify already rebranded
"""
import argparse
import pathlib
import re
import sys

PLUM = "#4A1F63"
SAFFRON = "#F5A623"
IVORY = "#F7F2E9"
INK = "#17111F"
MAUVE = "#EADFF0"
# Plum-hue neutrals, matching Brent's live blueprint.meetadvaita.com build
# (--muted-foreground 278 20% 40% -> #6B527A, --border 278 20% 85% -> #DBD1E0).
# Cold grays are what read as "generic blue template", so neutrals stay in-hue.
PLUM_MUTED = "#6B527A"
# #725787, not a lighter tint: it must clear WCAG 4.5:1 on ALL THREE surfaces it
# lands on — white 6.12:1, Warm Ivory 5.49:1, Mauve Mist 4.76:1 — while staying
# visibly lighter than PLUM_MUTED so the three-tier text hierarchy survives.
# Mauve Mist is the binding constraint: #7C5E8D failed there at 4.24:1, and that
# pairing only occurs in the crmx lineage. Verified by contrast-audit.py.
PLUM_LIGHT = "#725787"
PLUM_BORDER = "#DBD1E0"

FONT_LINKS = """  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
"""

NEW_ROOT = """    :root {
      /* Advaita brand — brand-guide-advaita-skill v2.0 (Drive 1FR6BqiapCJ0KMvpmVNE8URyNrGxFdjvI).
         Plum #4A1F63 (human) · Saffron #F5A623 (AI) · Warm Ivory #F7F2E9
         Ink Plum #17111F · Mauve Mist #EADFF0. Locked + identical on every
         blueprint. NEVER blue/teal/cold gradients. NEVER a per-lead accent. */
      --brand:        #4A1F63;
      --brand-dark:   #17111F;
      --brand-light:  #EADFF0;
      --saffron:      #F5A623;
      --steel:        #6B527A;
      --neutral-bg:   #F7F2E9;
      --brand-red:    #4A1F63; /* alias kept for markup compatibility — Plum */
      --crmx-red:     #4A1F63; /* alias kept for markup compatibility — Plum */
      --accent-bg:    rgba(74, 31, 99, 0.08); /* Plum at 8% */
      --white:        #ffffff; /* cards + text on dark only; page bg is Warm Ivory */
      --text:         #17111F;
      --text-muted:   #6B527A;
      --text-light:   #725787; /* WCAG 4.5:1 on ivory AND white; see contrast-audit.py */
      --border:       #DBD1E0;
      --bg:           #F7F2E9; /* alias for --neutral-bg; consumed by .agent-prompt */
      --text-mid:     #6B527A; /* alias for --text-muted; consumed by .agent-prompt/.agent-time */
      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
      --font-display: 'Space Grotesk', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      --radius: 12px;
      --shadow: 0 4px 24px rgba(23,17,31,0.08);
      --shadow-md: 0 8px 40px rgba(23,17,31,0.12);
    }"""

# Space Grotesk is display-only per the brand guide (big claims, hero, section
# titles). Body/labels stay Inter. Appended last so it wins on equal specificity
# without editing each existing rule (= no layout churn).
DISPLAY_FONT_BLOCK = """    /* Advaita typography — Space Grotesk display tier (brand-guide-advaita-skill v2.0) */
    h1, h2, h3, .nav-logo, .hero h1, .section-title, .cta-section h2,
    .hero-stat .num, .results-table .result-num, .pillar-title, .gap-title,
    .gap-num, .prompt-header h3, .diy-or-partner h3, .pod-header h3 {
      font-family: var(--font-display);
    }
"""

# Two template lineages exist and they are NOT interchangeable:
#   format3 -> blueprints/TEMPLATE.html, the real clone source; all 84 generated
#              pages match it token-for-token. Dark-surface accents use --brand.
#   crmx    -> Drive brent-attaway-crmx.html, the older 15-section base the
#              blueprint-skill hook names. Dark-surface accents use --brand-light.
# Applying one lineage's rules to the other silently no-ops, so the variant is
# detected and only its own rule set is enforced.

# (label, find, replace) — exact strings. Present in BOTH lineages.
SHARED_RULES = [
    (
        "body page background -> Warm Ivory (brand guide: never pure white)",
        "body { font-family: var(--font-sans); color: var(--text); background: var(--white);",
        "body { font-family: var(--font-sans); color: var(--text); background: var(--neutral-bg);",
    ),
    (
        "alternating sections -> Mauve Mist (keeps the alternation, on-brand)",
        ".section-alt { background: var(--neutral-bg); }",
        ".section-alt { background: var(--brand-light); }",
    ),
    (
        "nav wordmark -> Space Grotesk display",
        ".nav-logo { color: var(--white); font-weight: 700; font-size: 1rem; }",
        ".nav-logo { color: var(--white); font-weight: 700; font-size: 1rem; letter-spacing: -0.01em; }",
    ),
    (
        "hero stat labels -> raise white alpha 0.68 -> 0.92 (4.13:1 -> 6.0:1)",
        ".hero-stat .label { font-size: 0.8rem; color: rgba(255,255,255,0.68);",
        ".hero-stat .label { font-size: 0.8rem; color: rgba(255,255,255,0.92);",
    ),
]

# Drive brent-attaway-crmx.html lineage. Accents on dark used --brand-light
# (light CRMX blue); under the Advaita palette that token is Mauve Mist, so the
# brand-correct dark-surface accent is Saffron, matching format3.
RULES_CRMX = [
    (
        "nav wordmark accent -> Saffron",
        ".nav-logo span { color: var(--brand-light); }",
        ".nav-logo span { color: var(--saffron); }",
    ),
    (
        "nav link hover -> Saffron",
        ".nav-links a:hover { color: var(--brand-light); }",
        ".nav-links a:hover { color: var(--saffron); }",
    ),
    (
        "hero gradient -> Ink Plum -> Plum -> muted plum (matches format3)",
        ".hero { background: linear-gradient(135deg, var(--text) 0%, var(--brand-dark) 40%, var(--brand) 100%);",
        ".hero { background: linear-gradient(135deg, var(--brand-dark) 0%, #4A1F63 50%, var(--steel) 100%);",
    ),
    (
        "hero badge -> Saffron text on an Ink Plum scrim",
        "background: rgba(13,71,161,0.18); border: 1px solid var(--brand-light); color: var(--brand-light);",
        "background: rgba(23,17,31,0.45); border: 1px solid var(--saffron); color: var(--saffron);",
    ),
    (
        "hero H1 accent word -> Saffron",
        ".hero h1 span { color: var(--brand-light); }",
        ".hero h1 span { color: var(--saffron); }",
    ),
    (
        "hero stat number -> Saffron on dark",
        ".hero-stat .num { font-size: 2rem; font-weight: 800; color: var(--brand-light); display: block; }",
        ".hero-stat .num { font-size: 2rem; font-weight: 800; color: var(--saffron); display: block; }",
    ),
    (
        "footer link -> Saffron",
        "footer a { color: var(--brand-light); text-decoration: none; }",
        "footer a { color: var(--saffron); text-decoration: none; }",
    ),
    (
        "gap-tag revenue -> Plum tint (was magenta #fde8f3/#b02060)",
        ".gap-tag.revenue { background: #fde8f3; color: #b02060; }",
        ".gap-tag.revenue { background: rgba(74,31,99,0.10); color: var(--brand); }",
    ),
    (
        "gap-tag efficiency -> Ink Plum tint (was cold blue #e8eff7/#0a3578)",
        ".gap-tag.efficiency { background: #e8eff7; color: #0a3578; }",
        ".gap-tag.efficiency { background: rgba(23,17,31,0.07); color: var(--steel); }",
    ),
    (
        "gap-tag brand -> Saffron tint",
        ".gap-tag.brand { background: #f0e8fd; color: var(--brand-dark); }",
        ".gap-tag.brand { background: rgba(245,166,35,0.18); color: var(--brand-dark); }",
    ),
    (
        "table zebra row -> Plum 3% tint",
        ".opp-table tr:nth-child(even) td { background: #fafafa; }",
        ".opp-table tr:nth-child(even) td { background: rgba(74,31,99,0.03); }",
    ),
    (
        "impact-tag -> Saffron tint (was green #e8f5e9/#2e7d32)",
        "border-radius: 100px; background: #e8f5e9; color: #2e7d32; }",
        "border-radius: 100px; background: rgba(245,166,35,0.18); color: var(--brand); }",
    ),
    (
        "ignore-x chip -> Plum tint",
        "border-radius: 50%; background: #fde8e8;",
        "border-radius: 50%; background: rgba(74,31,99,0.10);",
    ),
    (
        "ignore-x glyph -> Plum (was red #c0392b)",
        ".ignore-x span { color: #c0392b;",
        ".ignore-x span { color: var(--brand);",
    ),
]

# blueprints/TEMPLATE.html lineage (the real clone source).
RULES_FORMAT3 = [
    (
        "nav wordmark accent -> Saffron (Saffron = the AI half of the brand)",
        ".nav-logo span { color: var(--brand); }",
        ".nav-logo span { color: var(--saffron); }",
    ),
    (
        "nav link hover -> Saffron (Plum is invisible on the Ink Plum bar)",
        ".nav-links a:hover { color: var(--brand); }",
        ".nav-links a:hover { color: var(--saffron); }",
    ),
    # ---------- hero (dark surface: accents must be Saffron, not Plum) ----------
    (
        "hero gradient midpoint -> Plum (was cold navy #1a2138)",
        "var(--brand-dark) 0%, #1a2138 50%, var(--steel) 100%",
        "var(--brand-dark) 0%, #4A1F63 50%, var(--steel) 100%",
    ),
    (
        # An 8-14% Saffron tint LIGHTENS the gradient behind it and drags Saffron
        # text down to 2.79:1. An Ink Plum scrim darkens instead -> 4.9:1 worst case.
        "hero badge -> Saffron text on an Ink Plum scrim",
        "background: rgba(0,113,227,0.12); border: 1px solid var(--brand); color: var(--brand);",
        "background: rgba(23,17,31,0.45); border: 1px solid var(--saffron); color: var(--saffron);",
    ),
    (
        # THE reported bug. Also broken BEFORE the rebrand (blue-on-navy, 1.08:1),
        # so this word has been invisible on every blueprint already shipped.
        "hero H1 accent word -> Saffron (was Plum-on-Plum, 1.0:1 = invisible)",
        ".hero h1 span { color: var(--brand); }",
        ".hero h1 span { color: var(--saffron); }",
    ),
    (
        "footer link -> Saffron (Plum on Ink Plum was 1.47:1)",
        "footer a { color: var(--brand); text-decoration: none; }",
        "footer a { color: var(--saffron); text-decoration: none; }",
    ),
    (
        "podcast timestamps -> Ink Plum at 0.75 (translucent black was 3.35:1)",
        "font-size: .78rem; color: rgba(0,0,0,.45); }",
        "font-size: .78rem; color: rgba(23,17,31,0.75); }",
    ),
    (
        "hero stat number -> Saffron on dark",
        ".hero-stat .num { font-size: 2rem; font-weight: 800; color: var(--brand); display: block; }",
        ".hero-stat .num { font-size: 2rem; font-weight: 800; color: var(--saffron); display: block; }",
    ),
    # ---------- tinted chips / rows: derived from brand hexes via rgba ----------
    (
        "gap-tag revenue -> Plum tint",
        ".gap-tag.revenue { background: #fde8eb;",
        ".gap-tag.revenue { background: rgba(74,31,99,0.10);",
    ),
    (
        "gap-tag efficiency -> Ink Plum tint (was cold blue-gray #e8eaf3)",
        ".gap-tag.efficiency { background: #e8eaf3;",
        ".gap-tag.efficiency { background: rgba(23,17,31,0.07);",
    ),
    (
        "gap-tag brand -> Saffron tint",
        ".gap-tag.brand { background: #f3e8f0;",
        ".gap-tag.brand { background: rgba(245,166,35,0.18);",
    ),
    (
        "impact-tag -> Saffron tint",
        "border-radius: 100px; background: #fde8eb; color: var(--brand); }",
        "border-radius: 100px; background: rgba(245,166,35,0.18); color: var(--brand); }",
    ),
    (
        "ignore-x chip -> Plum tint",
        "border-radius: 50%; background: #fde8e8;",
        "border-radius: 50%; background: rgba(74,31,99,0.10);",
    ),
    (
        "podcast error box -> Plum tint",
        "background: #fff3f3;",
        "background: rgba(74,31,99,0.08);",
    ),
    (
        "table zebra row -> Plum 3% tint",
        ".opp-table tr:nth-child(even) td { background: #fdfafb; }",
        ".opp-table tr:nth-child(even) td { background: rgba(74,31,99,0.03); }",
    ),
]

# Retired hexes that survive inside `var(--token, #FALLBACK)` declarations.
# Harmless while the token is defined, but they are still retired colors and
# would silently resurface if a token were ever removed.
FALLBACK_REMAP = {
    "#F5F5F7": IVORY,
    "#1D1D1F": INK,
    "#6E6E73": PLUM_MUTED,
    "#A1A1A6": PLUM_LIGHT,
    "#E5E5EA": PLUM_BORDER,
    "#EBF4FF": MAUVE,
    "#0071E3": PLUM,
}

# Remaining blue rgba + cold shadow rgba, applied as regex sweeps.
REGEX_RULES = [
    (
        "residual Apple-blue rgba -> Plum rgba",
        re.compile(r"rgba\(\s*0\s*,\s*113\s*,\s*227\s*,\s*(\.?\d*\.?\d+)\s*\)"),
        lambda m: f"rgba(74,31,99,{m.group(1)})",
    ),
    (
        "cold shadow rgba -> Ink Plum rgba",
        re.compile(r"rgba\(\s*10\s*,\s*14\s*,\s*26\s*,\s*(\.?\d*\.?\d+)\s*\)"),
        lambda m: f"rgba(23,17,31,{m.group(1)})",
    ),
    (
        "residual CRMX-blue rgba -> Plum rgba",
        re.compile(r"rgba\(\s*13\s*,\s*71\s*,\s*161\s*,\s*(\.?\d*\.?\d+)\s*\)"),
        lambda m: f"rgba(74,31,99,{m.group(1)})",
    ),
]

def detect_variant(html: str) -> str:
    """Which template lineage is this? Rules are not interchangeable."""
    if "--crmx-red" in html or "#0071E3" in html or "rgba(0,113,227" in html:
        return "format3"
    if "#0D47A1" in html or "rgba(13,71,161" in html or "--brand-light:  #1565C0" in html:
        return "crmx"
    # Already rebranded: pick by the accent token each lineage uses on dark.
    return "crmx" if ".hero h1 span { color: var(--brand-light)" in html else "format3"


BANNED = {
    "#0071E3": "retired Apple-blue brand token",
    "#1D1D1F": "retired cold navy",
    "#EBF4FF": "retired blue tint",
    "#6E6E73": "retired cold gray",
    "#F5F5F7": "retired cold page bg",
    "#0D47A1": "CRMX blue",
    "#1565C0": "CRMX blue",
    "#0A0E1A": "CRMX black",
    "#CC6B45": "Clay (deprecated 2026-07-09)",
    "#1A2138": "cold navy gradient stop",
    # crmx-lineage leftovers
    "#1565C0": "CRMX light blue",
    "#FDE8F3": "magenta tint",
    "#B02060": "magenta text",
    "#E8EFF7": "cold blue-gray tint",
    "#0A3578": "navy text",
    "#F0E8FD": "lilac tint",
    "#E8F5E9": "green tint",
    "#2E7D32": "green text",
    "#C0392B": "red glyph",
    "#FAFAFA": "cold zebra row",
}


def rebrand(html: str) -> tuple[str, list[str], list[str]]:
    applied, missed = [], []
    variant = detect_variant(html)
    applied.append(f"lineage detected: {variant}")

    # 1. Google Fonts, immediately before the stylesheet.
    if "fonts.googleapis.com" in html:
        applied.append("font links already present (skipped)")
    else:
        # Indentation differs between lineages.
        m = re.search(r"^([ \t]*)<style>", html, re.MULTILINE)
        if m:
            html = html.replace(m.group(0), FONT_LINKS + m.group(0), 1)
            applied.append("Google Fonts: Space Grotesk + Inter")
        else:
            missed.append("could not locate '<style>' to insert font links")

    # 2. :root palette.
    root_re = re.compile(r"    :root \{.*?\n    \}", re.DOTALL)
    if root_re.search(html):
        html = root_re.sub(lambda _: NEW_ROOT, html, count=1)
        applied.append(":root -> Advaita palette + --saffron + --font-display")
    else:
        missed.append("could not locate :root block")

    # 3. Exact-string rules: shared, then this lineage's own.
    ruleset = SHARED_RULES + (RULES_FORMAT3 if variant == "format3" else RULES_CRMX)
    for label, find, repl in ruleset:
        if find in html:
            html = html.replace(find, repl)
            applied.append(label)
        elif repl in html:
            applied.append(f"{label} (already applied)")
        else:
            missed.append(label)

    # 4. Regex sweeps.
    for label, pat, repl in REGEX_RULES:
        html, n = pat.subn(repl, html)
        if n:
            applied.append(f"{label} ({n}x)")

    # 5. Retired hexes left inside var() fallbacks.
    for old, new in FALLBACK_REMAP.items():
        pat = re.compile(r"(var\(--[a-z-]+,\s*)" + re.escape(old) + r"(\s*\))", re.IGNORECASE)
        html, n = pat.subn(lambda m: m.group(1) + new + m.group(2), html)
        if n:
            applied.append(f"var() fallback {old} -> {new} ({n}x)")

    # 6. Display font block, appended last so it wins on equal specificity.
    if "Advaita typography — Space Grotesk display tier" in html:
        applied.append("display-font block already present (skipped)")
    else:
        # First </style> only — later inline <style> blocks are unrelated.
        m = re.search(r"^([ \t]*)</style>", html, re.MULTILINE)
        if m:
            html = html.replace(m.group(0), DISPLAY_FONT_BLOCK + m.group(0), 1)
            applied.append("display-font block (Space Grotesk on headings)")
        else:
            missed.append("could not locate '</style>' to append display-font block")

    return html, applied, missed


def banned_hits(html: str) -> list[str]:
    hits = []
    for hexcode, why in BANNED.items():
        n = len(re.findall(re.escape(hexcode), html, re.IGNORECASE))
        if n:
            hits.append(f"{hexcode} x{n} ({why})")
    if re.search(r"rgba\(\s*0\s*,\s*113\s*,\s*227", html):
        hits.append("rgba(0,113,227,*) Apple-blue")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    src = pathlib.Path(a.src)
    html = src.read_text(encoding="utf-8")

    if a.check:
        hits = banned_hits(html)
        print(f"CHECK {src}")
        for h in hits:
            print(f"  FAIL retired color present: {h}")
        ok_font = "Space+Grotesk" in html and "--font-display" in html
        print(f"  {'PASS' if ok_font else 'FAIL'} Advaita typography wired")
        ok = not hits and ok_font
        print("RESULT:", "PASS" if ok else "FAIL")
        return 0 if ok else 1

    out, applied, missed = rebrand(html)

    print(f"REBRAND {src}")
    for x in applied:
        print(f"  ok   {x}")
    for x in missed:
        print(f"  MISS {x}")

    hits = banned_hits(out)
    for h in hits:
        print(f"  FAIL retired color survived: {h}")

    if missed or hits:
        print("RESULT: FAIL — nothing written")
        return 1

    dst = src if a.in_place else pathlib.Path(a.dst)
    dst.write_text(out, encoding="utf-8")
    print(f"RESULT: PASS -> {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
