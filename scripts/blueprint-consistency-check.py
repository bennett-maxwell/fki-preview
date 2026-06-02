#!/usr/bin/env python3
"""
blueprint-consistency-check.py — CROSS-blueprint template-conformance gate.

The existing gates (pre-commit D9/orchestrator/completion, pre-push HTTP 200)
validate each blueprint's INTERNAL integrity. NONE of them compare blueprints
to each OTHER. That blind spot is why 9 of 15 canonical blueprints shipped on
divergent templates (different colors, fonts, structure) yet all passed.

This gate enforces that every canonical blueprint conforms to TEMPLATE.html:
  - shares the brand accent token (--brand for format-3, --primary for legacy)
  - uses the template's web-font stack (apple-system for format-3, Inter for legacy)
  - falls within the template's section-count band
Per-client content is ALLOWED to vary (that is intended).

v2.0 — 2026-06-01 — format-3 cutover. TEMPLATE.html is now the Bennett-approved
       format-3 single-scroll gold (16 sections, --brand:#0071E3, apple-system
       font). The 15 pre-format-3 blueprints (21 sections, --primary:#1a1a2e,
       Inter) are LEGACY: reported as migration-pending WARN, NOT a hard fail, so
       the format-3 cutover commit is not blocked by un-migrated history. A
       blueprint that matches NEITHER the new baseline NOR the known-legacy
       fingerprint is TRUE DRIFT and still FAILS. As legacy blueprints are
       regenerated on format-3 they auto-promote to enforced PASS — no code edit.

Exit 0 = all conform OR are recognized legacy (migration-pending).
Exit 1 = true drift (a blueprint matching neither baseline nor legacy).
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

# Known-legacy (pre-format-3) fingerprint. A blueprint matching this is reported
# migration-pending (WARN, non-blocking) rather than treated as random drift.
LEGACY_PRIMARY = "#1a1a2e"
LEGACY_SECTIONS = 21
# Legacy section counts vary 17-21 (e.g. court-lundberg ships 17); ±4 recognizes
# the whole pre-format-3 generation as migration-pending rather than drift.
LEGACY_BAND = 4


def fingerprint(html: str) -> dict:
    # format-3 uses --brand; legacy uses --primary. Capture whichever is present.
    brand = re.search(r"--brand:\s*(#[0-9A-Fa-f]{3,8})", html)
    primary = re.search(r"--primary:\s*([^;]+);", html)
    accent = brand.group(1).strip() if brand else (primary.group(1).strip() if primary else None)
    gfont = "fonts.googleapis.com" in html
    apple = bool(re.search(r"apple-system", html))
    inter = bool(re.search(r"font-family:\s*['\"]?Inter['\"]?", html))
    sections = len(re.findall(r"<section", html))
    return {
        "accent": accent,
        "brand": brand.group(1).strip() if brand else None,
        "primary": primary.group(1).strip() if primary else None,
        "gfont": gfont,
        "apple": apple,
        "inter": inter,
        "sections": sections,
    }


def is_legacy(fp: dict) -> bool:
    """Recognizes the pre-format-3 (21-section / #1a1a2e / Inter) shell."""
    return (
        fp["primary"] == LEGACY_PRIMARY
        and fp["inter"]
        and abs(fp["sections"] - LEGACY_SECTIONS) <= LEGACY_BAND
    )


def main() -> int:
    if not TEMPLATE.exists():
        print(f"FATAL: {TEMPLATE} missing — cannot establish canonical baseline")
        return 2
    tpl = fingerprint(TEMPLATE.read_text(encoding="utf-8", errors="ignore"))
    tpl_accent = tpl["accent"]
    tpl_sections = tpl["sections"]
    # The template's font signature: a blueprint must share whichever stack the
    # template declares (apple-system for format-3, Inter for legacy template).
    tpl_apple = tpl["apple"]
    tpl_inter = tpl["inter"]

    print(f"Canonical baseline (TEMPLATE.html): accent={tpl_accent} "
          f"apple={tpl_apple} inter={tpl_inter} gfont={tpl['gfont']} "
          f"sections≈{tpl_sections}")
    print("-" * 64)

    fails = []
    legacy = []
    for slug in CANON:
        f = BP / f"{slug}.html"
        if not f.exists():
            fails.append((slug, "FILE MISSING"))
            print(f"  FAIL  {slug:<20} FILE MISSING")
            continue
        fp = fingerprint(f.read_text(encoding="utf-8", errors="ignore"))

        # Does it conform to the NEW (format-3) baseline?
        reasons = []
        if fp["accent"] != tpl_accent:
            reasons.append(f"accent={fp['accent']} (want {tpl_accent})")
        # Match the template's declared font signature.
        if tpl_apple and not fp["apple"]:
            reasons.append("no apple-system font stack")
        if tpl_inter and not fp["inter"]:
            reasons.append("no Inter font stack")
        if tpl_sections and abs(fp["sections"] - tpl_sections) > SECTION_BAND:
            reasons.append(f"sections={fp['sections']} outside band "
                           f"{tpl_sections}±{SECTION_BAND}")

        if not reasons:
            print(f"  PASS  {slug:<20} conforms to format-3 baseline")
            continue

        # Not conformant — is it recognized legacy (migration-pending) or true drift?
        if is_legacy(fp):
            legacy.append(slug)
            print(f"  WARN  {slug:<20} legacy pre-format-3 shell — migration pending")
        else:
            fails.append((slug, "; ".join(reasons)))
            print(f"  FAIL  {slug:<20} {'; '.join(reasons)}")

    print("-" * 64)
    if legacy:
        print(f"MIGRATION PENDING: {len(legacy)} legacy blueprint(s) await format-3 "
              f"regeneration (non-blocking): {', '.join(legacy)}")
    if fails:
        print(f"CONSISTENCY GATE: BLOCKED — {len(fails)}/{len(CANON)} true-drift "
              f"(neither format-3 nor recognized legacy).")
        return 1
    print(f"CONSISTENCY GATE: PASS — {len(CANON) - len(legacy)}/{len(CANON)} on "
          f"format-3, {len(legacy)} legacy migration-pending, 0 drift.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
