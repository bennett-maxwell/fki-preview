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


def _fillin_sub(mn, st, default_val):
    def _do(m):
        t = m.group(0)
        t = re.sub(r'\bmin="\d+"', f'min="{mn}"', t, count=1)
        t = re.sub(r'\bstep="\d+"', f'step="{st}"', t, count=1)
        # Also fix the value= so it sits inside the industry band (root cause of D7-01 fails)
        t = re.sub(r'\bvalue="\d+"', f'value="{default_val}"', t, count=1)
        return t
    return _do


def _get_lead_default(slug, mn, mx):
    """Read avg_customer_value from lead profile; clamp to industry band.

    Search order:
      1. leads/<slug>.json  (exact match)
      2. Newest leads/<slug>-*.json  (dated profile, e.g. mike-norton-origins-20260603.json)
    Falls back to industry minimum if no profile found or value out of band.
    """
    leads_dir = REPO / "leads"
    # 1. Exact slug match
    candidates = [leads_dir / f"{slug}.json"]
    # 2. Dated profile fallback: leads/<slug>-*.json sorted newest first
    dated = sorted(leads_dir.glob(f"{slug}-*.json"), reverse=True)
    candidates.extend(dated)
    for profile in candidates:
        if profile.exists():
            try:
                p = json.loads(profile.read_text())
                v = p.get("avg_customer_value")
                if v and isinstance(v, (int, float)) and mn <= v <= mx:
                    return int(v)
            except Exception:
                pass
    return mn  # fall back to industry minimum


def patch(path, mn, mx, st, fallback, slug=None):
    html = path.read_text()
    default_val = _get_lead_default(slug, mn, mx) if slug else mn
    new = SLIDER_RE.sub(slider_tag(mn, mx, st, mn), html, count=1)
    new = FILLIN_RE.sub(_fillin_sub(mn, st, default_val), new, count=1)
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
    patch_slug = None
    if len(sys.argv) > 1 and sys.argv[1] == "--patch" and len(sys.argv) > 2:
        patch_slug = sys.argv[2]
    for slug, industry in SLUG_IND.items():
        if patch_slug and slug != patch_slug:
            continue
        f = BP / f"{slug}.html"
        if not f.exists():
            print(f"  MISSING: {slug}.html"); ok = False; continue
        if industry not in ISL:
            print(f"  {slug}: {industry} — NO INDUSTRY CONFIG (add to roi-industry-config.json)"); ok = False; continue
        cfg = ISL[industry]
        ch = patch(f, cfg["min"], cfg["max"], cfg["step"], cfg["min"], slug=slug)
        print(f"  {slug}: {industry:<16} {cfg['min']}-{cfg['max']} step {cfg['step']}  patched={ch}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
