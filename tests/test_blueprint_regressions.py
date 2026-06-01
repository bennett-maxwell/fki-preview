#!/usr/bin/env python3
"""
test_blueprint_regressions.py — stdlib-only regression suite that pins the
8 hard-won Blueprint AI invariants so a future edit can't silently reintroduce
a fixed defect.

Every check below is currently TRUE. Each one corresponds to a real bug that
was found and fixed; the assert is the tripwire. Run:

    python3 tests/test_blueprint_regressions.py ; echo "exit=$?"

Prints per-check PASS/FAIL + a summary. Exits 0 iff every check passes, else 1.
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP_DIR = os.path.join(REPO, "blueprints")
FIN_CHECK = os.path.join(REPO, "financial-realism-check.py")
RUN_AUDIT = os.path.join(REPO, "run-audit.py")


def _read(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def check_no_linkedin_slider_in_template():
    """1. The build TEMPLATE must never carry the B2B-only slider-linkedin
    lever — it is the seed every blueprint is cloned from, so a single copy
    there would propagate the D7-18 defect to every new non-B2B client."""
    html = _read(os.path.join(BP_DIR, "TEMPLATE.html"))
    n = html.count("slider-linkedin")
    assert n == 0, f"TEMPLATE.html contains {n} slider-linkedin (expected 0)"


def check_no_nonb2b_linkedin_violation():
    """2. (CORRECTED) The real contract is INDUSTRY-CONDITIONAL, not a blanket
    ban. B2B blueprints (consulting, crm_software, medical_devices, design_agency,
    video_production) may LEGITIMATELY contain slider-linkedin — that's a valid
    lead-gen lever for them. Only NON-B2B industries (a plumber, a restaurant)
    must not show it (D7-18). So we do NOT raw-grep for "slider-linkedin" across
    client files; instead we assert on the enforcer's verdict: run
    financial-realism-check.py over the whole blueprints dir and require exit 0,
    i.e. ZERO D7-18 non-B2B slider red-line failures. This pins the actual
    industry-conditional contract rather than a contradictory blanket rule."""
    proc = subprocess.run(
        [sys.executable, FIN_CHECK, "--all"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert proc.returncode == 0, (
        "financial-realism-check.py --all exited "
        f"{proc.returncode} (expected 0 — a D7-18 non-B2B slider or other "
        f"red-line financial failure regressed):\n{proc.stdout}\n{proc.stderr}"
    )


def check_d7_18_is_hard_fail():
    """3. D7-18 must be a HARD FAIL, not a soft warning. Confirm the checker
    appends D7-18 to `fails` and never to `warns` (it was promoted WARN->FAIL
    on 2026-05-31 once all 7 client violations were cleared)."""
    src = _read(FIN_CHECK)
    fails_d7_18 = re.search(r"fails\.append\([^)]*D7-18", src, re.S) \
        or "D7-18" in "".join(
            re.findall(r"fails\.append\((.*?)\)", src, re.S))
    assert fails_d7_18, "no fails.append(...) references D7-18"
    warns_d7_18 = bool(
        re.search(r"warns\.append\((?:(?!\)).)*?D7-18", src, re.S))
    assert not warns_d7_18, "D7-18 must not appear in any warns.append( )"


def check_financial_gate_wired_in_precommit():
    """4. The financial red-line gate must be wired into the pre-commit hook so
    a $45k-clone slider can never be committed without the check running."""
    hook = _read(os.path.join(REPO, ".git", "hooks", "pre-commit"))
    assert "financial-realism-check.py" in hook, \
        "pre-commit hook does not reference financial-realism-check.py"


def check_industry_config_is_single_source():
    """5. The industry classification + B2B-LinkedIn allow-list must load from
    the single source of truth (scripts/roi-industry-config.json), not only an
    inline dict that could drift."""
    src = _read(FIN_CHECK)
    assert "roi-industry-config.json" in src, \
        "financial-realism-check.py does not reference roi-industry-config.json"


def check_d9_01_is_real_not_stub():
    """6. D9-01 (no orphan CSS classes) must be a REAL check, not a hardcoded
    True stub. Ensure run-audit.py has a real implementation and is not pinned."""
    src = _read(RUN_AUDIT)
    assert 'results["D9-01_no_orphan_classes"] = True' not in src, \
        "D9-01 is stubbed to literal True in run-audit.py"
    assert "def no_orphan_classes(" in src, \
        "run-audit.py missing real no_orphan_classes() implementation"


def check_podcast_alias_explicit():
    """7. Per-lead podcast resolution must use the explicit, committable
    PODCAST_ALIAS map (deploy-safe), NOT a filesystem symlink — GitHub Pages /
    static deploys may not follow symlinks, producing a false-PASS. Confirm the
    alias map exists and watson.mp3 is not a symlink."""
    src = _read(RUN_AUDIT)
    assert "PODCAST_ALIAS" in src, "run-audit.py missing PODCAST_ALIAS map"
    watson = os.path.join(REPO, "podcasts", "watson.mp3")
    assert os.path.islink(watson) is False, \
        "podcasts/watson.mp3 is a symlink — must be resolved via PODCAST_ALIAS"


def check_d1_01_checks_title():
    """8. D1-01 (personalization) must scope to the <title>, not a shallow
    'first name anywhere in HTML' substring test. Confirm the real
    name_in_title() function exists."""
    src = _read(RUN_AUDIT)
    assert "def name_in_title(" in src, \
        "run-audit.py missing name_in_title() implementation"


CHECKS = [
    ("NO_LINKEDIN_SLIDER_IN_TEMPLATE", check_no_linkedin_slider_in_template),
    ("NO_NONB2B_LINKEDIN_VIOLATION", check_no_nonb2b_linkedin_violation),
    ("D7_18_IS_HARD_FAIL", check_d7_18_is_hard_fail),
    ("FINANCIAL_GATE_WIRED_IN_PRECOMMIT", check_financial_gate_wired_in_precommit),
    ("INDUSTRY_CONFIG_IS_SINGLE_SOURCE", check_industry_config_is_single_source),
    ("D9_01_IS_REAL_NOT_STUB", check_d9_01_is_real_not_stub),
    ("PODCAST_ALIAS_EXPLICIT", check_podcast_alias_explicit),
    ("D1_01_CHECKS_TITLE", check_d1_01_checks_title),
]


def main():
    passed = 0
    for name, fn in CHECKS:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            print(f"FAIL  {name}: unexpected error: {e}")
    total = len(CHECKS)
    print("-" * 60)
    print(f"SUMMARY: {passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
