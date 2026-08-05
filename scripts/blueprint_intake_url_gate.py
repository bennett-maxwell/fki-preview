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

# An href pointing at a retired intake path. Canonical absolute URLs are fine.
RETIRED_HREF = re.compile(
    r"""href\s*=\s*["'](?![^"']*blueprint\.meetadvaita\.com)"""
    r"""[^"']*(?:/apply/|/apply\.html|\bapply/|\bapply\.html"""
    r"""|aiblueprintmarketing\.com/apply)[^"']*["']""",
    re.I,
)

# Field names unique to the intake questionnaire. Two or more => this file IS a form.
FORM_FIELDS = ("revenue_range", "team_size", "monthly_leads", "crm_tools",
               "operational_stress", "biggest_goal", "ai_maturity", "process_maturity")

# Only these extensions are customer-facing surfaces worth gating.
SCAN_EXT = {".html", ".htm"}

# Never gate history//backups -- they are not served as the live form.
SKIP_PARTS = ("_obsolete", ".deprecated-backups", "node_modules", ".git")
SKIP_SUFFIX = (".bak",)


def _skip(rel: str) -> bool:
    if any(p in rel for p in SKIP_PARTS):
        return True
    return any(s in rel for s in SKIP_SUFFIX)


def is_redirect_stub(text: str) -> bool:
    """A stub must send the browser to the canonical URL and carry no form of its own."""
    points_at_canonical = CANONICAL_HOST in text
    has_redirect = bool(
        re.search(r"http-equiv\s*=\s*['\"]refresh", text, re.I)
        or re.search(r"location\s*\.\s*(replace|assign|href)", text, re.I)
    )
    field_hits = sum(1 for f in FORM_FIELDS if f in text)
    return points_at_canonical and has_redirect and field_hits < 2


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
        if sum(1 for fld in FORM_FIELDS if fld in text) >= 2 and not is_redirect_stub(text):
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument("--self-test", "--selftest", dest="selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return self_test()

    root = pathlib.Path(a.root).resolve()
    findings = scan(root)
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
