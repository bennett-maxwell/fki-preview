#!/usr/bin/env python3
"""blueprint_intake_url_gate.py — BLOCKING gate: one intake form, one URL, forever.

Marker: BLUEPRINT-INTAKE-URL-CANONICAL-20260805
EC:     EC-BLUEPRINT-STALE-INTAKE-FORM-STILL-SERVED-20260805

Madison directive 2026-08-05: `https://blueprint.meetadvaita.com/` is the ONLY Advaita
Blueprint intake form. It is the only form we ever send to a lead or client, and the only
one that may be served from this repo.

The defect this closes: `hub.aiblueprintmarketing.com` (this repo's GitHub Pages domain) was
still SERVING a full 67KB copy of an older intake form at `/apply/`, and four live entry
points fed it -- `apply/index.html`, `apply.html`, the hub ROOT `index.html`, and the
`advaita-lp.html` ad CTA. Both forms returned HTTP 200, so "the link works" was true and
useless. A URL returning 200 is not evidence it is the canonical one.

RED LINES (any hit = exit 1):
  RL-IU1  a live customer-facing file links to a retired intake path (/apply/, apply.html,
          or hub.aiblueprintmarketing.com/apply)
  RL-IU2  a retired intake path is not a redirect stub pointing at the canonical URL
  RL-IU3  a live customer-facing file ships intake FORM FIELDS (i.e. is itself a form)
          without being the canonical redirect stub

Usage:
  python3 scripts/blueprint_intake_url_gate.py                # scan repo, exit 1 on any red line
  python3 scripts/blueprint_intake_url_gate.py --root <dir>   # scan a specific tree
  python3 scripts/blueprint_intake_url_gate.py --self-test    # both directions + mutant kill
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import tempfile

CANONICAL = "https://blueprint.meetadvaita.com/"
CANONICAL_HOST = "blueprint.meetadvaita.com"

# Paths that used to serve an intake form. They must exist ONLY as redirect stubs.
RETIRED_INTAKE_PATHS = ("apply/index.html", "apply.html", "index.html")

# An href pointing at the retired BLUEPRINT intake path.
#
# PRECISION MATTERS MORE THAN REACH HERE. The first cut of this pattern matched any
# `apply.html` / `apply/` substring and produced 43 false positives on its first full-tree
# run -- `thank-you-apply.html` (a thank-you page, matched because `-` is a word boundary)
# and all 40 pages of `advaita-site-20260715/`, a SEPARATE marketing site whose own
# relative `apply.html` is titled "Book a fit call" and contains zero intake fields.
# A gate that cries wolf gets switched off, so this now matches only:
#   * an absolute URL on a retired HOST that ends at /apply
#   * a root-absolute /apply or /fki-preview/apply
# A bare relative `apply.html` belongs to whatever site contains it and is NOT our concern.
RETIRED_HREF = re.compile(
    r"""href\s*=\s*["']("""
    r"""https?://(?:bennett-maxwell\.github\.io|hub\.aiblueprintmarketing\.com)"""
    r"""(?:/fki-preview)?/apply(?:/|\.html)?"""
    r"""|/(?:fki-preview/)?apply(?:/|\.html)?"""
    r""")(?:[?#][^"']*)?["']""",
    re.I,
)

# Field names unique to the intake questionnaire.
FORM_FIELDS = ("revenue_range", "team_size", "monthly_leads", "crm_tools",
               "operational_stress", "biggest_goal", "ai_maturity", "process_maturity")

# RL-IU3 must fire on a real FORM, not on a page that merely mentions these names.
# Blueprint pages legitimately carry `team_size` / `monthly_leads` as ROI-calculator
# variables -- that is not an intake form. Require an actual form control plus the
# submit label, and a majority of the field set.
FORM_MARKERS = ("<form", "<input", "<select")
SUBMIT_LABEL = "build my"

# Only these extensions are customer-facing surfaces worth gating.
SCAN_EXT = {".html", ".htm"}

# Never gate history//backups -- they are not served as the live form.
SKIP_PARTS = ("_obsolete", ".deprecated-backups", "node_modules", ".git")
SKIP_SUFFIX = (".bak",)


def _skip(rel: str) -> bool:
    if any(p in rel for p in SKIP_PARTS):
        return True
    return any(s in rel for s in SKIP_SUFFIX)


def ships_intake_form(text: str) -> bool:
    """True only when this file IS an intake questionnaire, not merely mentions its fields."""
    low = text.lower()
    if not any(m in low for m in FORM_MARKERS):
        return False                      # no form controls at all
    if SUBMIT_LABEL not in low:
        return False                      # no intake submit label
    return sum(1 for f in FORM_FIELDS if f in text) >= 4


def is_redirect_stub(text: str) -> bool:
    """A stub must send the browser to the canonical URL and carry no form of its own."""
    points_at_canonical = CANONICAL_HOST in text
    has_redirect = bool(
        re.search(r"http-equiv\s*=\s*['\"]refresh", text, re.I)
        or re.search(r"location\s*\.\s*(replace|assign|href)", text, re.I)
    )
    return points_at_canonical and has_redirect and not ships_intake_form(text)


def scan(root: pathlib.Path) -> list[str]:
    findings: list[str] = []

    # RL-IU2 — retired paths must be redirect stubs.
    for rel in RETIRED_INTAKE_PATHS:
        f = root / rel
        if not f.exists():
            continue  # deleting it outright also satisfies the directive
        text = f.read_text(encoding="utf-8", errors="replace")
        if not is_redirect_stub(text):
            findings.append(
                f"RL-IU2 {rel}: retired intake path is not a redirect stub to {CANONICAL}"
            )

    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in SCAN_EXT:
            continue
        rel = str(f.relative_to(root))
        if _skip(rel):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")

        # RL-IU1 — no links to a retired intake path.
        for m in RETIRED_HREF.finditer(text):
            findings.append(f"RL-IU1 {rel}: links to retired intake path -> {m.group(0)[:90]}")

        # RL-IU3 — a live page must not itself be an intake form.
        if ships_intake_form(text) and not is_redirect_stub(text):
            findings.append(f"RL-IU3 {rel}: ships intake form fields; only {CANONICAL} may host the form")

    return findings


# ---------------------------------------------------------------- self-test

_STUB = (
    '<!DOCTYPE html><html><head><link rel="canonical" href="https://blueprint.meetadvaita.com/">'
    '<meta http-equiv="refresh" content="0; url=https://blueprint.meetadvaita.com/">'
    '<script>window.location.replace("https://blueprint.meetadvaita.com/");</script></head>'
    '<body><a href="https://blueprint.meetadvaita.com/">Continue</a></body></html>'
)
_STALE_FORM = (
    '<!DOCTYPE html><html><body><form><input name="revenue_range"><input name="team_size">'
    '<input name="crm_tools"><button>Build My Free Blueprint</button></form></body></html>'
)
_LINKS_OLD = '<!DOCTYPE html><html><body><a href="/apply/">Get My Free Blueprint</a></body></html>'

# A REAL intake questionnaire: form controls + the submit label + a majority of the fields.
_REAL_FORM = (
    '<!DOCTYPE html><html><body><form>'
    '<input name="revenue_range"><input name="team_size"><input name="monthly_leads">'
    '<select name="crm_tools"></select><input name="biggest_goal">'
    '<button>Build My Free Blueprint</button></form></body></html>'
)
# Regression fixtures for the 43 false positives this gate produced on its first full run.
_THANK_YOU = '<!DOCTYPE html><html><body><a href="thank-you-apply.html">Thanks</a></body></html>'
_OTHER_SITE = '<!DOCTYPE html><html><body><a href="apply.html">Book a fit call</a></body></html>'
_ROI_PAGE = (
    '<!DOCTYPE html><html><body><script>const team_size=3;const monthly_leads=50;'
    'const revenue_range="u250k";</script></body></html>'
)


def _mk(d: pathlib.Path, rel: str, body: str) -> None:
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def self_test() -> int:
    cases = []

    # GOOD: every retired path is a stub, nothing links to the old form.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for rel in RETIRED_INTAKE_PATHS:
            _mk(d, rel, _STUB)
        _mk(d, "advaita-lp.html", f'<a href="{CANONICAL}">Get My Free Blueprint</a>')
        cases.append(("GOOD repo fully migrated", scan(d), False))

    # GOOD: retired paths deleted entirely (also satisfies the directive).
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _mk(d, "blueprints/x.html", f'<a href="{CANONICAL}">form</a>')
        cases.append(("GOOD retired paths deleted", scan(d), False))

    # GOOD: history/backups are ignored.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for rel in RETIRED_INTAKE_PATHS:
            _mk(d, rel, _STUB)
        _mk(d, "blueprints/_obsolete/old.html", _LINKS_OLD)
        _mk(d, "blueprints/t.html.bak", _STALE_FORM)
        cases.append(("GOOD obsolete+bak ignored", scan(d), False))

    # BAD: the stale form is still served at apply/.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _mk(d, "apply/index.html", _STALE_FORM)
        _mk(d, "apply.html", _STUB)
        _mk(d, "index.html", _STUB)
        cases.append(("BAD stale form served at apply/", scan(d), True))

    # BAD: a live page links to the retired path (the advaita-lp CTA defect).
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for rel in RETIRED_INTAKE_PATHS:
            _mk(d, rel, _STUB)
        _mk(d, "advaita-lp.html", _LINKS_OLD)
        cases.append(("BAD live CTA -> /apply/", scan(d), True))

    # BAD: hub root still redirects to the old form instead of canonical.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _mk(d, "index.html", '<meta http-equiv="refresh" content="0; url=/apply/">'
                             '<a href="/apply/">go</a>')
        cases.append(("BAD hub root -> /apply/", scan(d), True))

    # BAD: absolute stale host link.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _mk(d, "email.html", '<a href="https://hub.aiblueprintmarketing.com/apply/">form</a>')
        cases.append(("BAD absolute stale host link", scan(d), True))

    # GOOD (regression): a thank-you page whose name merely ENDS in -apply.html.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for rel in RETIRED_INTAKE_PATHS:
            _mk(d, rel, _STUB)
        _mk(d, "qualify/index.html", _THANK_YOU)
        cases.append(("GOOD thank-you-apply.html not flagged", scan(d), False))

    # GOOD (regression): a DIFFERENT site's own relative apply.html ("Book a fit call").
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for rel in RETIRED_INTAKE_PATHS:
            _mk(d, rel, _STUB)
        _mk(d, "advaita-site/index.html", _OTHER_SITE)
        _mk(d, "advaita-site/apply.html", _OTHER_SITE)
        cases.append(("GOOD other site's relative apply.html not flagged", scan(d), False))

    # GOOD (regression): a blueprint page carrying ROI variable names but no form.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for rel in RETIRED_INTAKE_PATHS:
            _mk(d, rel, _STUB)
        _mk(d, "partners/x/index.html", _ROI_PAGE)
        cases.append(("GOOD ROI variable names are not a form", scan(d), False))

    # BAD: a real intake questionnaire served from a non-canonical path.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for rel in RETIRED_INTAKE_PATHS:
            _mk(d, rel, _STUB)
        _mk(d, "sites/rogue-intake.html", _REAL_FORM)
        cases.append(("BAD second intake form elsewhere in repo", scan(d), True))

    # BAD: a "stub" that redirects somewhere else entirely.
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _mk(d, "apply/index.html",
            '<meta http-equiv="refresh" content="0; url=https://example.com/">')
        cases.append(("BAD stub points off-canonical", scan(d), True))

    ok = True
    for name, findings, want_fail in cases:
        got_fail = bool(findings)
        good = got_fail == want_fail
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: "
              f"{'findings' if got_fail else 'clean'} ({len(findings)})")
        if not good:
            for f in findings[:4]:
                print(f"        {f}")

    # Mutant kill: a gate that always allows, or always blocks, must not survive.
    good_clean = not scan_dir_fixture(_STUB, stale=False)
    bad_dirty = bool(scan_dir_fixture(_STALE_FORM, stale=True))
    always_allow_dead = bad_dirty          # always-allow would report clean on the bad tree
    always_block_dead = good_clean         # always-block would report findings on the good tree
    print(f"  [{'PASS' if always_allow_dead else 'FAIL'}] mutant killed: always-allow")
    print(f"  [{'PASS' if always_block_dead else 'FAIL'}] mutant killed: always-block")
    ok &= always_allow_dead and always_block_dead

    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def scan_dir_fixture(body: str, stale: bool) -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for rel in RETIRED_INTAKE_PATHS:
            _mk(d, rel, _STUB)
        if stale:
            _mk(d, "apply/index.html", body)
        return scan(d)


# ---------------------------------------------------------------- live probe
#
# REPO-GREEN IS NOT LIVE-GREEN (added 2026-08-05, marker BLUEPRINT-INTAKE-URL-LIVE-PROBE-20260805).
# On 2026-08-05 this gate passed, CI was green, and every file on origin/main was a correct redirect
# stub -- while hub.aiblueprintmarketing.com/apply/ was STILL serving the 67,570-byte stale intake form
# for ~45 minutes, because the Pages deploy carrying the fix had been cancelled by a later push
# (pages.yml sets cancel-in-progress: true). Three green signals, one wrong customer surface.
#
# --live therefore checks the SERVED BYTES, not the working tree. It is opt-in so offline/CI runs stay
# deterministic and never fail on a network blip.

LIVE_HOST = "https://hub.aiblueprintmarketing.com"
LIVE_PATHS = ("/apply/", "/apply.html", "/", "/advaita-lp.html")


def probe_live(timeout: int = 25) -> list[str]:
    """Fetch each retired entry point and prove the CUSTOMER gets the canonical form."""
    import urllib.request
    findings: list[str] = []
    req_hdrs = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
    for path in LIVE_PATHS:
        url = LIVE_HOST + path
        try:
            req = urllib.request.Request(url, headers=req_hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", "replace")
        except Exception as exc:
            findings.append(f"RL-IU4 {url}: unreachable ({exc.__class__.__name__}) -- cannot prove live state")
            continue
        fields = sum(1 for f in FORM_FIELDS if f in body)
        canon = body.count(CANONICAL_HOST)
        # advaita-lp is a real landing page, not a stub: it only needs its CTA on canonical.
        if path == "/advaita-lp.html":
            if canon < 1:
                findings.append(f"RL-IU4 {url}: landing page does not link {CANONICAL} (canonical refs 0)")
            if fields >= 2:
                findings.append(f"RL-IU4 {url}: LIVE page ships {fields} intake fields of its own")
            continue
        if fields >= 2:
            findings.append(f"RL-IU4 {url}: LIVE surface is STILL SERVING an intake form "
                            f"({fields} fields, {len(body)} bytes) -- a deploy has not landed")
        if canon < 1:
            findings.append(f"RL-IU4 {url}: LIVE surface has 0 references to {CANONICAL_HOST} "
                            f"({len(body)} bytes) -- not redirecting to the canonical form")
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument("--self-test", "--selftest", dest="selftest", action="store_true")
    ap.add_argument("--live", action="store_true",
                    help="ALSO probe the served bytes on the live hub (repo-green is not live-green)")
    a = ap.parse_args()

    if a.selftest:
        return self_test()

    root = pathlib.Path(a.root).resolve()
    findings = scan(root)
    if a.live:
        findings += probe_live()
    if findings:
        print(f"BLUEPRINT INTAKE URL GATE: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print("  -", f)
        print(f"\nThe ONLY intake form is {CANONICAL} (marker BLUEPRINT-INTAKE-URL-CANONICAL-20260805).")
        return 1
    print(f"BLUEPRINT INTAKE URL GATE: PASS — {CANONICAL} is the only intake form served.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
