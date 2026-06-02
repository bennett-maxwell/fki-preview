#!/usr/bin/env python3
"""fix-roi-slider-industry.py — give the ROI calculator's 'Average Contract Value'
slider an INDUSTRY-APPROPRIATE range per blueprint, driven by
scripts/roi-industry-config.json (single source of truth, also read by the
generator).

Root cause being fixed: the prior fix made every blueprint share ONE generic
slider (min=500 max=100000 value=500, JS fallback ||0). That is the same
"one financial profile cloned onto every industry" defect Bennett flagged with
Court Lundberg ($45K avg contract on a residential plumber), just with new
numbers — financial-realism-check.py catches it 0/15.

This sets each blueprint's slider to its industry's realistic transaction band so
the client can model THEIR real numbers. The default value stays at min +
data-no-default + calcTouched guard, so nothing is presented as the client's own
figure until they drag it (no fabricated current-state claim).

- TEMPLATE.html  -> tokenized ({{ROI_MIN}}/{{ROI_MAX}}/{{ROI_STEP}}) so the
  generator fills it per lead and can't reintroduce the clone.
- 15 canon       -> concrete per-industry numbers.

Network-free. Re-runnable. Usage: python3 scripts/fix-roi-slider-industry.py
"""
import json, re, pathlib, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
BP = REPO / "blueprints"
CFG = json.loads((REPO / "scripts" / "roi-industry-config.json").read_text())
ISL = CFG["industry_slider"]
SLUG_IND = CFG["slug_industry"]

SLIDER_RE = re.compile(r'(<input type="range" id="slider-contract")[^>]*(>)')
JSFALL_RE = re.compile(r"(getElementById\('slider-contract'\)\.value\)\s*\|\|\s*)\d+")
# Current blueprints (post avg-value-fill-in migration) use a number FILL-IN with
# id="sl-contract" and NO max. financial-realism-check.py D7-02 + the generator both
# moved to this id; this fixer still only knew the legacy range slider, so it could
# not repair the (min,value) clone fingerprint on fill-in blueprints (the detector
# advanced, the fixer didn't — same dead-id drift the v2.10 detector patch fixed).
# Set the fill-in's min/step to the industry band so the (contract_min, slider_default)
# triple becomes industry-DISTINCT (clears D7-02). The per-lead value is preserved —
# it is intentional per-lead data, not a clone axis.
FILLIN_RE = re.compile(r'<input\b[^>]*\bid="sl-contract"[^>]*>')


def slider_tag(mn, mx, st, val):
    return (f'<input type="range" id="slider-contract" min="{mn}" max="{mx}" '
            f'step="{st}" value="{val}" data-no-default="true" '
            f'oninput="calcTouched=true;updateCalc()">')


def _fillin_sub(mn, st):
    def _do(m):
        t = m.group(0)
        t = re.sub(r'\bmin="\d+"', f'min="{mn}"', t, count=1)
        t = re.sub(r'\bstep="\d+"', f'step="{st}"', t, count=1)
        return t
    return _do


def patch(path, mn, mx, st, fallback):
    html = path.read_text()
    new = SLIDER_RE.sub(slider_tag(mn, mx, st, mn), html, count=1)
    new = FILLIN_RE.sub(_fillin_sub(mn, st), new, count=1)
    new = JSFALL_RE.sub(rf"\g<1>{fallback}", new, count=1)
    changed = new != html
    if changed:
        path.write_text(new)
    return changed


def main():
    # TEMPLATE: tokens so the generator personalizes per lead
    tmpl = BP / "TEMPLATE.html"
    t_changed = patch(tmpl, "{{ROI_MIN}}", "{{ROI_MAX}}", "{{ROI_STEP}}", "{{ROI_MIN}}")
    print(f"  TEMPLATE.html: tokenized={t_changed}")

    ok = True
    for slug, industry in SLUG_IND.items():
        f = BP / f"{slug}.html"
        if not f.exists():
            print(f"  MISSING: {slug}.html"); ok = False; continue
        cfg = ISL[industry]
        ch = patch(f, cfg["min"], cfg["max"], cfg["step"], cfg["min"])
        print(f"  {slug}: {industry:<16} {cfg['min']}-{cfg['max']} step {cfg['step']}  patched={ch}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
