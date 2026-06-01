#!/usr/bin/env python3
"""Neutralize fabricated client-current-state numbers in the ROI calculator + static
pillars across TEMPLATE.html and all 15 canonical blueprints.

Root cause: TEMPLATE.html hard-codes contract=$25k, leads=12, close=18% (and JS
fallbacks ||45000/12/18) and runs updateCalc() on load, so every page paints a
fabricated ROI for the client. Court Lundberg (residential plumbing, ~$850 avg
job) is the clearest proof these are wrong-per-business.

Fix = show NOTHING as the client's own number until the user enters it. No
fabricated current-state figures, no auto-compute on load.
"""
import re, sys, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
BP = REPO / "blueprints"
CANON = ("alex-ramos austin-iron-horse branson-maxwell brent-attaway brittney-warnick "
         "chris-lpnw court-lundberg dave-wood jaden-mecham melissa-tash-srp paul-muus "
         "rey-31-consulting rush-evans watson zachary-oldham").split()
FILES = [BP / "TEMPLATE.html"] + [BP / f"{s}.html" for s in CANON]

# (description, old, new) — literal string replacements
REPL = [
    ("contract slider range (trade-safe)",
     'id="slider-contract" min="25000" max="120000" step="1000" value="25000"',
     'id="slider-contract" min="500" max="100000" step="500" value="500"'),
    ("leads label",  'id="val-leads">12<',  'id="val-leads">(enter yours)<'),
    ("close label",  'id="val-close">18%<', 'id="val-close">(enter yours)<'),
    ("res-time static", 'id="res-time">6.5 hrs/wk<', 'id="res-time">&mdash;<'),
    ("pillar 6.5hrs prose",
     '6.5 hours/week reclaimed<sup>4</sup> (industry baseline 7.6 hrs, understated 15%)',
     'Hours/week reclaimed from automation &mdash; model your exact numbers in the calculator above'),
    ("JS fallback contract 45000",
     "parseInt(document.getElementById('slider-contract').value) || 45000;",
     "parseInt(document.getElementById('slider-contract').value) || 0;"),
    ("JS fallback leads 12",
     "parseInt(document.getElementById('slider-leads').value) || 12;",
     "parseInt(document.getElementById('slider-leads').value) || 0;"),
    ("JS fallback close 18",
     "(parseInt(document.getElementById('slider-close').value) || 18) / 100;",
     "(parseInt(document.getElementById('slider-close').value) || 0) / 100;"),
    ("setScenario marks touched",
     "function setScenario(s) {",
     "function setScenario(s) {\n  calcTouched = true;"),
    ("updateCalc load-guard",
     "function updateCalc() {",
     "var calcTouched = false;\nfunction updateCalc() {\n  if (!calcTouched) { return; }"),
]

def main():
    summary = {}
    for f in FILES:
        if not f.exists():
            print(f"  MISSING: {f.name}"); summary[f.name] = "MISSING"; continue
        html = f.read_text()
        per = []
        for desc, old, new in REPL:
            n = html.count(old)
            if n:
                html = html.replace(old, new)
            per.append(f"{desc}={n}")
        # oninput touch flag on the 5 calc sliders (regex, slider-* only)
        oi = len(re.findall(r'(id="slider-(?:contract|leads|close|linkedin|seo)"[^>]*?oninput=")updateCalc\(\)"', html))
        html = re.sub(r'(id="slider-(?:contract|leads|close|linkedin|seo)"[^>]*?oninput=")updateCalc\(\)"',
                      r'\1calcTouched=true;updateCalc()"', html)
        per.append(f"oninput-touch={oi}")
        f.write_text(html)
        summary[f.name] = "; ".join(per)
        print(f"  {f.name}: {summary[f.name]}")
    return summary

if __name__ == "__main__":
    main()
