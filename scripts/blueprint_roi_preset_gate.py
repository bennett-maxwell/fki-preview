#!/usr/bin/env python3
"""
blueprint_roi_preset_gate.py — BLUEPRINT-ROI-PRESET-FROM-FORM-20260727

Blocks the bug-class where the ROI calculator ships lead-agnostic template
defaults instead of the lead's own intake numbers.

Root incident (EC-BLUEPRINT-ROI-TEMPLATE-DEFAULT-LEAK-20260727): TEMPLATE.html
hardcoded both the calculator input `value=` attributes AND the PRESETS object
(contract 2388 / leads 10 / rate 18 / hours 15). Every lead inherited them.
Carlos Medina stated 50 monthly leads; his page rendered 10.

Why the existing gates missed it: blueprint_completion_gate.py check 13 only
greps the calculator *JS* for hardcoded ROI defaults, and run-audit.py's
D7-22 calculator check did not compare rendered values against the lead profile.
An HTML `value="18"` attribute and a PRESETS literal both slipped through.

Checks (all red-line):
  RL-ROI1  every rendered ROI control value matches the lead profile when the
           lead PROVIDED that number (monthly leads is the common case)
  RL-ROI2  no banned hardcoded ROI constant anywhere in the calculator block
           (18 close rate, 2388 / 45000 contract) unless the LEAD stated it
  RL-ROI3  PRESETS scenarios are not lead-agnostic literals — they must carry
           the same values as the rendered inputs (scenarios differ by `lift`)
  RL-ROI4  zero unresolved {{ROI_*}} tokens

Usage:
  python3 scripts/blueprint_roi_preset_gate.py --lead <slug>
  python3 scripts/blueprint_roi_preset_gate.py --lead <slug> --html <path> --profile <path>
  python3 scripts/blueprint_roi_preset_gate.py --all
Exit 0 = PASS.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Hardcoded values that must never appear as a ROI default unless the lead said so.
# 18 = Rule 14 banned close rate. 2388 / 45000 = Rule 18 fabricated avg ticket.
BANNED = {"rate": [18], "contract": [2388, 45000]}


def num(v):
    if v in (None, "", "—"):
        return None
    m = re.search(r"\d+(?:\.\d+)?", str(v).replace(",", ""))
    return float(m.group(0)) if m else None


def profile_num(profile, *keys):
    quiz = profile.get("quiz") or {}
    for k in keys:
        for src in (profile, quiz):
            n = num(src.get(k))
            if n is not None:
                return n
    return None


def rendered(html, ctrl):
    m = re.search(r'id="sl-%s"[^>]*\bvalue="([^"]+)"' % ctrl, html)
    if not m:
        m = re.search(r'\bvalue="([^"]+)"[^>]*id="sl-%s"' % ctrl, html)
    return num(m.group(1)) if m else None


def control_limits(html, ctrl, fallback):
    """Read the control's ACTUAL min/max off the rendered page.

    PERMANENT FIX 2026-08-17 (marker BLUEPRINT-ROI-LEADS-SLIDER-MAX-ADAPTIVE-20260817,
    EC-BLUEPRINT-ROI-CLAMP-GUARD-CARRIED-THE-SAME-CEILING-20260817).
    This gate used to hardcode leads=(2,100) — the SAME constant the template hardcoded.
    So when the generator was fixed to widen the slider for a lead stating >100 monthly
    leads, the guard clamped the expected value to 100 itself and reported the CORRECT
    rendered 150 as a "template default leaked". A guard that hardcodes the very constant
    it is guarding cannot detect a change in it. The ceiling is a property of the rendered
    control, so read it from the control.
    """
    lo, hi = fallback
    m = re.search(r'id="sl-%s"[^>]*>' % ctrl, html) or re.search(r'<input[^>]*id="sl-%s"' % ctrl, html)
    if m:
        tag = m.group(0)
        mn = re.search(r'\bmin="([0-9.]+)"', tag)
        mx = re.search(r'\bmax="([0-9.]+)"', tag)
        if mn:
            lo = float(mn.group(1))
        if mx:
            hi = float(mx.group(1))
    return lo, hi


def presets(html):
    m = re.search(r"const PRESETS\s*=\s*\{(.*?)\};", html, re.S)
    if not m:
        return None
    out = {}
    for scen, body in re.findall(r"(\w+)\s*:\s*\{([^}]*)\}", m.group(1)):
        vals = {}
        for k, v in re.findall(r"(\w+)\s*:\s*([0-9.]+)", body):
            vals[k] = float(v)
        out[scen] = vals
    return out


def check(slug, html_path=None, profile_path=None):
    html_path = html_path or os.path.join(REPO, "blueprints", f"{slug}.html")
    profile_path = profile_path or os.path.join(REPO, "leads", f"{slug}.json")
    fails = []
    if not os.path.exists(html_path):
        return [f"missing html: {html_path}"]
    html = open(html_path, encoding="utf-8", errors="ignore").read()
    profile = {}
    if os.path.exists(profile_path):
        profile = json.load(open(profile_path, encoding="utf-8"))

    stated = {
        "leads": profile_num(profile, "monthly_leads", "lead_volume", "avg_monthly_lead_volume"),
        "rate": profile_num(profile, "close_rate", "current_close_rate"),
        "hours": profile_num(profile, "admin_hours", "admin_hours_per_week", "weekly_admin_hours"),
        "contract": profile_num(profile, "avg_contract_value", "avg_ticket", "average_customer_value"),
    }
    # Ceilings are read off the rendered controls, never hardcoded here — see control_limits().
    fallbacks = {"leads": (2, 100), "rate": (5, 60), "hours": (2, 40), "contract": (None, None)}
    limits = {
        c: (fallbacks[c] if fallbacks[c][0] is None else control_limits(html, c, fallbacks[c]))
        for c in fallbacks
    }
    got = {c: rendered(html, c) for c in ("leads", "rate", "hours", "contract")}

    # RL-ROI1 — stated values must actually render
    for ctrl, want in stated.items():
        if want is None:
            continue
        lo, hi = limits[ctrl]
        if lo is not None:
            want = max(lo, min(hi, want))
        if got[ctrl] is None:
            fails.append(f"RL-ROI1 {ctrl}: control not found in rendered page")
        elif abs(got[ctrl] - want) > 0.01:
            fails.append(
                f"RL-ROI1 {ctrl}: lead stated {want:g} but page renders {got[ctrl]:g} "
                f"(template default leaked)"
            )

    # RL-ROI2 — banned constants unless the lead genuinely stated them
    for ctrl, bad in BANNED.items():
        if got[ctrl] is not None and int(got[ctrl]) in bad:
            if stated[ctrl] is None or int(stated[ctrl]) != int(got[ctrl]):
                fails.append(
                    f"RL-ROI2 {ctrl}: banned hardcoded ROI default {int(got[ctrl])} rendered "
                    f"and the lead did not state it (Rule 14/18)"
                )

    # RL-ROI3 — PRESETS must match the rendered inputs; scenarios differ by lift only
    ps = presets(html)
    if ps is None:
        fails.append("RL-ROI3: PRESETS object not found")
    else:
        for scen, vals in ps.items():
            for ctrl in ("leads", "rate", "hours", "contract"):
                if ctrl not in vals or got[ctrl] is None:
                    continue
                if abs(vals[ctrl] - got[ctrl]) > 0.01:
                    fails.append(
                        f"RL-ROI3 {scen}.{ctrl}={vals[ctrl]:g} != rendered {got[ctrl]:g} "
                        f"(lead-agnostic preset literal)"
                    )

    # RL-ROI4 — no unresolved tokens
    left = re.findall(r"\{\{ROI_[A-Z_]+\}\}", html)
    if left:
        fails.append(f"RL-ROI4: unresolved tokens {sorted(set(left))}")

    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lead")
    ap.add_argument("--html")
    ap.add_argument("--profile")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json-output")
    a = ap.parse_args()

    targets = []
    if a.all:
        for f in sorted(os.listdir(os.path.join(REPO, "leads"))):
            if f.endswith(".json"):
                targets.append(f[:-5])
    elif a.lead:
        targets = [a.lead]
    else:
        ap.error("--lead or --all required")

    bad = 0
    results = {}
    for slug in targets:
        fails = check(slug, a.html, a.profile)
        results[slug] = fails
        if fails:
            bad += 1
            print(f"[FAIL] {slug}")
            for f in fails:
                print(f"   - {f}")
        elif not a.all:
            print(f"[PASS] {slug}: ROI presets match the lead's stated intake numbers")
    if a.all:
        print(f"\nROI preset gate: {len(targets) - bad}/{len(targets)} pass, {bad} fail")
    if a.json_output:
        json.dump({"results": results, "pass": bad == 0}, open(a.json_output, "w"), indent=2)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
