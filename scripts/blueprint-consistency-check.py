#!/usr/bin/env python3
"""
blueprint-consistency-check.py — CROSS-blueprint template-conformance gate.

The existing gates (pre-commit D9/orchestrator/completion, pre-push HTTP 200)
validate each blueprint's INTERNAL integrity. NONE of them compare blueprints
to each OTHER. That blind spot is why 9 of 15 canonical blueprints shipped on
divergent templates (different colors, fonts, structure) yet all passed.

This gate enforces that every canonical blueprint conforms to TEMPLATE.html:
  - shares the brand --primary token
  - uses the Inter web-font stack + Google Fonts link
  - falls within the template's section-count band
Per-client --accent is ALLOWED to vary (that is intended branding).

Exit 0 = all conform. Exit 1 = drift (lists every offender + the reason).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BP = REPO / "blueprints"
TEMPLATE = BP / "TEMPLATE.html"

CANON = [
    "alex-ramos", "austin-iron-horse", "branson-maxwell", "brent-attaway",
    "brittney-warnick", "chris-lpnw", "court-lundberg", "dave-wood",
    "jaden-mecham", "melissa-tash-srp", "paul-muus", "rey-31-consulting",
    "rush-evans", "watson", "zachary-oldham",
]

# Section-count tolerance band around the canonical template's count.
SECTION_BAND = 4


def fingerprint(html: str) -> dict:
    primary = re.search(r"--primary:\s*([^;]+);", html)
    gfont = "fonts.googleapis.com" in html
    inter = bool(re.search(r"font-family:\s*['\"]?Inter['\"]?", html))
    sections = len(re.findall(r"<section", html))
    return {
        "primary": primary.group(1).strip() if primary else None,
        "gfont": gfont,
        "inter": inter,
        "sections": sections,
    }


def main() -> int:
    if not TEMPLATE.exists():
        print(f"FATAL: {TEMPLATE} missing — cannot establish canonical baseline")
        return 2
    tpl = fingerprint(TEMPLATE.read_text(encoding="utf-8", errors="ignore"))
    tpl_primary = tpl["primary"]  # e.g. "#1a1a2e"
    tpl_sections = tpl["sections"]

    print(f"Canonical baseline (TEMPLATE.html): primary={tpl_primary} "
          f"inter={tpl['inter']} gfont={tpl['gfont']} sections≈{tpl_sections}")
    print("-" * 64)

    fails = []
    for slug in CANON:
        f = BP / f"{slug}.html"
        if not f.exists():
            fails.append((slug, "FILE MISSING"))
            continue
        fp = fingerprint(f.read_text(encoding="utf-8", errors="ignore"))
        reasons = []
        if fp["primary"] != tpl_primary:
            reasons.append(f"primary={fp['primary']} (want {tpl_primary})")
        if not fp["inter"]:
            reasons.append("no Inter font stack")
        if not fp["gfont"]:
            reasons.append("no Google Fonts link")
        if tpl_sections and abs(fp["sections"] - tpl_sections) > SECTION_BAND:
            reasons.append(f"sections={fp['sections']} outside band "
                           f"{tpl_sections}±{SECTION_BAND}")
        status = "PASS" if not reasons else "FAIL"
        print(f"  {status}  {slug:<20} {'; '.join(reasons)}")
        if reasons:
            fails.append((slug, "; ".join(reasons)))

    print("-" * 64)
    if fails:
        print(f"CONSISTENCY GATE: BLOCKED — {len(fails)}/{len(CANON)} off-template.")
        return 1
    print(f"CONSISTENCY GATE: PASS — {len(CANON)}/{len(CANON)} conform to TEMPLATE.html.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
