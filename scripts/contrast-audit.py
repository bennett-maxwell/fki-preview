#!/usr/bin/env python3
"""
contrast-audit.py — WCAG contrast audit for a rendered blueprint page.

Why this exists: the Advaita palette puts Plum #4A1F63 on both sides of the
fence — it is the primary accent AND the hero/nav/CTA background. A rule like
`.hero h1 span { color: var(--brand) }` renders Plum-on-Plum and the word
vanishes. Grep cannot see that; only the rendered cascade can.

Method:
  * walk each text node's ancestors to resolve the effective background
  * a gradient contributes EVERY one of its color stops as a candidate
    background, and the WORST contrast wins — text crossing a gradient must
    stay legible over all of it
  * WCAG 2.1: 4.5:1 normal text, 3:1 large text (>=24px, or >=18.66px bold)

Usage:
  contrast-audit.py <file.html> [--min 4.5] [--json]
Exit 1 if any visible text fails.
"""
import argparse
import json
import pathlib
import re
import sys

EXTRACT_JS = r"""
() => {
  const RGB = /rgba?\(([^)]+)\)/g;

  const parse = (s) => {
    const m = /rgba?\(([^)]+)\)/.exec(s);
    if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x.trim()));
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };

  const stops = (bgImage) => {
    const out = [];
    let m;
    RGB.lastIndex = 0;
    while ((m = RGB.exec(bgImage)) !== null) {
      const p = m[1].split(',').map(x => parseFloat(x.trim()));
      out.push({ r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 });
    }
    return out;
  };

  // Composite a possibly-translucent color over an already-resolved backdrop.
  const over = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a),
    a: 1,
  });

  // All plausible backdrops behind an element, worst-case set.
  const backdrops = (el) => {
    let cands = [{ r: 255, g: 255, b: 255, a: 1 }];  // canvas
    const chain = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) chain.push(n);
    chain.reverse();  // outermost first
    for (const n of chain) {
      const cs = getComputedStyle(n);
      const bi = cs.backgroundImage || 'none';
      if (bi !== 'none') {
        const st = stops(bi);
        if (st.length) cands = st.map(s => over(s, cands[0]));
      }
      const bc = parse(cs.backgroundColor);
      if (bc && bc.a > 0) {
        if (bc.a >= 0.999) cands = [bc];
        else cands = cands.map(c => over(bc, c));
      }
    }
    return cands;
  };

  const results = [];
  const seen = new Set();
  document.querySelectorAll('*').forEach(el => {
    // only elements holding their own visible text
    const own = Array.from(el.childNodes)
      .filter(n => n.nodeType === 3)
      .map(n => n.textContent.trim())
      .join(' ')
      .trim();
    if (!own) return;

    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return;
    if (parseFloat(cs.opacity) === 0) return;
    const box = el.getBoundingClientRect();
    if (box.width < 1 || box.height < 1) return;

    const fg = parse(cs.color);
    if (!fg) return;

    const size = parseFloat(cs.fontSize);
    const weight = parseInt(cs.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);

    const key = el.tagName + '|' + (el.className || '') + '|' + own.slice(0, 40);
    if (seen.has(key)) return;
    seen.add(key);

    results.push({
      tag: el.tagName.toLowerCase(),
      cls: typeof el.className === 'string' ? el.className : '',
      text: own.slice(0, 60),
      fg: [fg.r, fg.g, fg.b, fg.a],
      backdrops: backdrops(el).map(c => [c.r, c.g, c.b]),
      size: size,
      weight: weight,
      large: large,
    });
  });
  return results;
}
"""


def lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hexof(c):
    return "#%02X%02X%02X" % (round(c[0]), round(c[1]), round(c[2]))


def evaluate(nodes, min_ratio):
    fails = []
    for n in nodes:
        fg = n["fg"]
        need = 3.0 if n["large"] else min_ratio
        worst, worst_bg = None, None
        for bg in n["backdrops"]:
            # composite translucent text over this backdrop
            eff = [fg[i] * fg[3] + bg[i] * (1 - fg[3]) for i in range(3)]
            r = ratio(eff, bg)
            if worst is None or r < worst:
                worst, worst_bg = r, bg
        if worst is not None and worst < need:
            fails.append({
                "sel": f"{n['tag']}" + (f".{n['cls'].split()[0]}" if n["cls"] else ""),
                "text": n["text"],
                "fg": hexof(fg),
                "bg": hexof(worst_bg),
                "ratio": round(worst, 2),
                "need": need,
                "size": n["size"],
            })
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="+", help="one or more HTML files (batch reuses one browser)")
    ap.add_argument("--min", type=float, default=4.5)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="batch: print only failing files")
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright

    results = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        for path in a.path:
            url = pathlib.Path(path).resolve().as_uri()
            try:
                pg.goto(url, wait_until="load")
                pg.wait_for_timeout(1200 if len(a.path) == 1 else 400)
                nodes = pg.evaluate(EXTRACT_JS)
                results[path] = {"nodes": len(nodes), "fails": evaluate(nodes, a.min)}
            except Exception as e:  # a page that cannot render is a failure, not a skip
                results[path] = {"nodes": 0, "fails": [], "error": str(e)[:160]}
        b.close()

    if a.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        total = 0
        for path, r in results.items():
            fails = r["fails"]
            bad = fails or r.get("error")
            total += len(fails) + (1 if r.get("error") else 0)
            if a.quiet and not bad:
                continue
            print(f"CONTRAST AUDIT {path}")
            if r.get("error"):
                print(f"  ERROR {r['error']}")
                continue
            print(f"  {r['nodes']} text elements checked")
            if not fails:
                print("  PASS — no contrast failures")
            for f in sorted(fails, key=lambda x: x["ratio"]):
                print(f"  FAIL {f['ratio']}:1 (need {f['need']}) {f['sel']}")
                print(f"       fg {f['fg']} on bg {f['bg']} — \"{f['text']}\"")
        if len(results) > 1:
            clean = sum(1 for r in results.values() if not r["fails"] and not r.get("error"))
            print(f"SUMMARY: {clean}/{len(results)} files clean, {total} total failures")
        print("RESULT:", "PASS" if total == 0 else f"FAIL ({total})")

    bad = sum(len(r["fails"]) + (1 if r.get("error") else 0) for r in results.values())
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
