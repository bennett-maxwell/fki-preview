#!/usr/bin/env python3
"""
blueprint_text_overflow_gate.py — BLUEPRINT-NO-TEXT-OVERFLOW-20260728

Blocks two related customer-visible defects:

  RL-TO1  RAW INTERNAL TOKEN LEAK — a snake_case / SCREAMING_CASE identifier rendered
          into customer-facing copy. Root incident: `industry` doubles as the ROI-banding
          key in scripts/roi-industry-config.json, so `professional_services` was printed
          verbatim into the Industry snapshot card and the "businesses in the ___ space"
          line on Rena's page. It reads like a database field to the prospect.

  RL-TO2  TEXT OVERFLOW / CLIPPING — a value whose rendered content is wider than its own
          box. `professional_services` is a single unbreakable token: 254px of text in a
          147px card, so it spilled past the border and clipped. Measured in a real
          browser at desktop AND mobile widths, because this is a layout fact, not a
          string fact — grep cannot see it.

Why the pre-existing gates missed it: run-audit.py PF0-4 greps for {{TOKENS}} and
[BRACKETS] but a bare snake_case word is not a template token; D9 render-integrity checks
orphan CSS classes, not box geometry; and the completion gate never rendered the page.

Usage:
  python3 scripts/blueprint_text_overflow_gate.py --lead <slug>            # live URL
  python3 scripts/blueprint_text_overflow_gate.py --lead <slug> --local    # local file
  python3 scripts/blueprint_text_overflow_gate.py --all --local
Exit 0 = PASS. Requires playwright chromium; absent => explicit PARTIAL, never silent pass.
"""
import argparse
import json
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

# Customer-facing regions to scan for raw tokens. Prompt <pre> blocks are excluded:
# their bracket placeholders are intentional operator instructions.
TEXT_SELECTORS = (
    ".snapshot-val, .snapshot-key, .agent-name, .agent-outcome, .gap-title, "
    "h1, h2, h3, .section-sub, .hero-sub, .profile-note"
)

# A raw identifier: two+ word-parts joined by _ , or any ALL_CAPS_WITH_UNDERSCORES.
RAW_TOKEN = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b|\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")

VIEWPORTS = {"desktop": (1440, 900, False), "mobile": (390, 844, True)}


def check(url, slug):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, ["PARTIAL gate:playwright_absent — cannot measure box geometry; install "
                      "playwright + chromium. NOT a pass."]
    fails = []
    detail = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, (w, h, mob) in VIEWPORTS.items():
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob,
                                has_touch=mob)
            pg = ctx.new_page()
            resp = pg.goto(url, wait_until="networkidle", timeout=60000)
            pg.wait_for_timeout(900)
            if resp and resp.status != 200:
                fails.append(f"RL-TO2 {name}: page returned HTTP {resp.status}")

            # RL-TO2 — any leaf element whose content is wider than its own box.
            spills = pg.evaluate("""() => {
              const out = [];
              document.querySelectorAll('*').forEach(e => {
                if (e.children.length) return;
                const t = (e.textContent || '').trim();
                if (!t) return;
                if (e.closest('pre')) return;              // operator prompt blocks
                const cs = getComputedStyle(e);
                if (cs.display === 'none' || cs.visibility === 'hidden') return;
                if (e.scrollWidth > e.clientWidth + 1 && e.clientWidth > 0) {
                  out.push({cls: (e.className||'').toString().slice(0,40),
                            text: t.slice(0,60), scrollW: e.scrollWidth,
                            clientW: e.clientWidth, overflowX: cs.overflowX});
                }
              });
              return out;
            }""")
            for s in spills:
                fails.append(
                    f"RL-TO2 {name}: .{s['cls']} content {s['scrollW']}px overflows its "
                    f"{s['clientW']}px box — \"{s['text']}\" (overflow-x:{s['overflowX']})"
                )

            # RL-TO1 — raw internal identifiers in customer-facing text.
            texts = pg.eval_on_selector_all(
                TEXT_SELECTORS,
                "els => els.filter(e => !e.closest('pre'))"
                "        .map(e => (e.textContent||'').trim()).filter(Boolean)")
            seen = set()
            for t in texts:
                for m in RAW_TOKEN.findall(t):
                    if m.lower() in seen:
                        continue
                    seen.add(m.lower())
                    fails.append(
                        f"RL-TO1 {name}: raw internal token '{m}' rendered in customer-facing "
                        f"copy — humanize it before display")
            detail[name] = {"spills": len(spills), "raw_tokens": sorted(seen)}
            ctx.close()
        b.close()
    return detail, fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lead")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--local", action="store_true", help="scan the local file instead of the live URL")
    ap.add_argument("--json-output")
    a = ap.parse_args()

    slugs = []
    if a.all:
        slugs = sorted(p.stem for p in (REPO / "blueprints").glob("*.html")
                       if p.stem not in ("TEMPLATE", "GOLDEN"))
    elif a.lead:
        slugs = [a.lead]
    else:
        ap.error("--lead or --all required")

    bad = 0
    results = {}
    for slug in slugs:
        if a.local:
            f = REPO / "blueprints" / f"{slug}.html"
            if not f.exists():
                print(f"[SKIP] {slug}: no local file")
                continue
            url = f.as_uri()
        else:
            url = f"https://hub.aiblueprintmarketing.com/blueprints/{slug}.html"
        detail, fails = check(url, slug)
        results[slug] = {"detail": detail, "fails": fails}
        partial = any(f.startswith("PARTIAL") for f in fails)
        if fails:
            bad += 1
            print(f"[{'PARTIAL' if partial else 'FAIL'}] {slug}")
            for f in fails[:12]:
                print(f"   - {f}")
        else:
            print(f"[PASS] {slug}: no overflow, no raw tokens (desktop + mobile)")
    if a.json_output:
        json.dump({"results": results, "pass": bad == 0},
                  open(a.json_output, "w"), indent=2)
    if a.all:
        print(f"\ntext-overflow gate: {len(slugs)-bad}/{len(slugs)} pass, {bad} fail")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
