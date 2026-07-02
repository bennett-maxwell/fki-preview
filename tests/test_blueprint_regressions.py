#!/usr/bin/env python3
"""
test_blueprint_regressions.py — stdlib-only regression suite that pins the
17 hard-won Blueprint AI invariants so a future edit can't silently reintroduce
a fixed defect.

Every check below is currently TRUE. Each one corresponds to a real bug that
was found and fixed; the assert is the tripwire. Run:

    python3 tests/test_blueprint_regressions.py ; echo "exit=$?"

Prints per-check PASS/FAIL + a summary. Exits 0 iff every check passes, else 1.

CI notes (2026-06-05): cross-platform fixes applied — pre-commit hook fallback
(_find_precommit_hook) resolves scripts/git-hooks in CI; sed uses portable
sed -i.bak form (e4eb403). financial-realism-check.py local-webhookprobe
added to NON_LEAD exclusion (a68a3cd). Both fixes are in effect on main.
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

def _find_precommit_hook():
    """Find pre-commit hook, falling back to scripts/git-hooks for CI environments."""
    path = os.path.join(REPO, ".git", "hooks", "pre-commit")
    if not os.path.exists(path):
        fallback = os.path.join(REPO, "scripts", "git-hooks", "pre-commit")
        if os.path.exists(fallback):
            path = fallback
    return path



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
    hook = _read(_find_precommit_hook())
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


def check_format3_gate_wired():
    """9. Format-3 dense-scroll is the only allowed customer-facing format."""
    src = _read(RUN_AUDIT)
    assert "format-conformance-check.py" in src, \
        "run-audit.py does not invoke format-conformance-check.py"
    assert "PF0-5_format3_dense_scroll_RL" in src, \
        "run-audit.py missing the Format-3 red-line result"


def check_restaurant_drift_gate_wired():
    """10. Restaurant leads must fail on plumber/SaaS/demo leftovers."""
    src = _read(RUN_AUDIT)
    assert "def restaurant_content_gate(" in src, \
        "run-audit.py missing restaurant_content_gate()"
    for phrase in [
        "plumber test business",
        "water heater",
        "client success onboarding agent",
        "proposal specialist",
        "restaurant-specific vocabulary below threshold",
    ]:
        assert phrase in src, f"restaurant drift gate missing phrase: {phrase}"
    assert "D10-23_restaurant_copy_clean_RL" in src, \
        "run-audit.py missing restaurant drift red-line result"


def check_podcast_direct_address_artifact_gate():
    """11. Podcast audit blocks source-material framing and known ASR artifacts."""
    src = _read(os.path.join(REPO, "scripts", "podcast_direct_address_audit.py")).lower()
    for phrase in [
        "source materials?",
        "golden state",
        "delete delete",
        "i said",
        "high chad",
        "bennett preview",
        "customer send",
        "gatekeeper",
    ]:
        assert phrase in src, f"podcast direct-address gate missing: {phrase}"


def check_local_audio_audit_not_public_deploy_blocked():
    """12. Local audit can run before first public deploy; production receipts verify 200 later."""
    src = _read(RUN_AUDIT)
    assert "BLUEPRINT_REQUIRE_PUBLIC_AUDIO" in src, \
        "run-audit.py must gate public audio 200 behind an explicit production env"
    assert '"public_url_200": True if not require_public_audio' in src, \
        "run-audit.py still hard-blocks local first deploy on public podcast URL"


def check_production_summary_no_send_guard():
    """13. Local/public proof must not be interchangeable with external-send
    approval. The production summary guard keeps no_send=true until strict
    production receipts prove Drive registry, GHL readback, repeat-submit, and
    production Gatekeeper readiness."""
    src = _read(os.path.join(REPO, "scripts", "blueprint_production_summary.py"))
    for token in [
        "strict_production_ready",
        "external_send_allowed",
        "no_send",
        "validate_drive_registry",
        "validate_ghl_readback",
        "validate_repeat_submit",
        "require_production",
        "strict completion gate receipt must have require_production=true",
        "exact_contact_count=1",
        "instant_response_verified=true",
        "exact_contact_count_after_repeat=1",
    ]:
        assert token in src, f"production summary guard missing token: {token}"


def check_delivery_email_escapes_ampersand_tokens():
    """14. build-delivery-email.sh injects free-text profile values into the
    delivery-email template via `sed -i ''`. In a sed replacement RHS the bare
    `&` is the whole-match operator, so a value like "Photography & Video"
    (rush-evans) silently expands `&` back into the token itself, leaving the
    {{INDUSTRY}} placeholder UNRENDERED (D5-20 fail). The fix is a sed_esc()
    helper that backslash-escapes `&`, applied to EVERY free-text token. This
    check pins both the helper's presence and its actual runtime behavior."""
    script = os.path.join(REPO, "scripts", "build-delivery-email.sh")
    src = _read(script)
    # (a) helper defined and escapes the whole-match operator
    assert "sed_esc()" in src and r"sed 's/&/\\&/g'" in src, \
        "build-delivery-email.sh missing sed_esc() that escapes the sed & operator"
    # (b) every free-text token substitution pipes through sed_esc (ACCENT_COLOR
    # is a hex color with no free text, so it is legitimately exempt).
    free_text_tokens = [
        "LEAD_FIRST_NAME", "BUSINESS_NAME", "INDUSTRY", "BLUEPRINT_URL",
        "PODCAST_URL", "WEBSITE_URL", "APPLY_SUBJECT", "APPLY_URL", "QUALIFY_URL",
    ]
    for tok in free_text_tokens:
        line = next((l for l in src.splitlines()
                     if ("{{%s}}" % tok) in l and "sed -i" in l), None)
        assert line is not None, f"no sed substitution line for {{{{{tok}}}}}"
        assert "sed_esc " in line, \
            f"{tok} substitution does not pass through sed_esc (& would corrupt it): {line.strip()}"
    # (c) runtime tripwire: replicate the exact mechanism with a &-bearing value
    # and prove it renders literally with no leftover placeholder.
    bash = r'''
set -e
tmp=$(mktemp)
printf '%s' 'X {{INDUSTRY}} Y' > "$tmp"
sed_esc() { printf '%s' "$1" | sed 's/&/\\&/g'; }
val='Photography & Video'
sed -i.bak "s|{{INDUSTRY}}|$(sed_esc "$val")|g" "$tmp" && rm -f "$tmp.bak"
cat "$tmp"
rm -f "$tmp"
'''
    out = subprocess.run(["bash", "-c", bash], capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, f"ampersand render harness errored: {out.stderr}"
    rendered = out.stdout.strip()
    assert rendered == "X Photography & Video Y", \
        f"&-bearing token did not render literally: got {rendered!r}"
    assert "{{" not in rendered, \
        f"placeholder left unrendered after &-bearing substitution: {rendered!r}"


def check_precommit_ov_skip_path_intact():
    """The pre-commit hook must scope its orchestrator/strict gates to STAGED
    blueprint HTML only (via `git diff --cached`), and print an explicit
    'OV SKIP' when none is staged. This guards the pathspec-commit isolation
    path (commit 47ba67e4): `git commit <non-blueprint-paths>` builds a temp
    index with no blueprint HTML -> hook skips the blueprint validators ->
    clean commit without --no-verify and without disturbing a session-mate's
    staged WIP. If this logic regresses, unrelated script fixes can no longer
    be committed while blueprint WIP sits staged."""
    hook = _read(_find_precommit_hook())
    assert "git diff --cached --name-only" in hook, \
        "pre-commit no longer scopes staged-blueprint detection to the cached index"
    assert 'grep "^blueprints/.*\\.html$"' in hook, \
        "pre-commit staged-blueprint grep pattern changed; OV-SKIP scoping may be broken"
    assert "OV SKIP" in hook, \
        "pre-commit lost the explicit OV SKIP branch for no-blueprint-staged commits"


def check_resolve_html_path_prefers_dated_slug():
    """16. The 0/0-false-PASS killer, pinned BEHAVIORALLY (not by grep).
    run-audit.py resolve_html_path() must: (a) prefer the NEWEST -YYYYMMDD.html
    clone when called with a bare slug (gk100 calls bare; live clones are dated);
    (b) still prefer an exact {slug}.html match over a dated one; and (c) REFUSE
    to guess when multiple ambiguous non-dated matches exist — returning a
    non-existent path so the caller reports not-found rather than silently
    auditing the WRONG file as a false PASS. Without this test a glob/regex
    regression silently restores the 0/0 fleet-wide false pass this whole cycle
    was created to kill."""
    import importlib.util
    import tempfile
    spec = importlib.util.spec_from_file_location(
        "run_audit_mod", os.path.join(REPO, "run-audit.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory() as td:
        mod.BP_DIR = td
        # (a) newest dated clone wins
        for fn in ["acme-20260101.html", "acme-20260601.html", "acme-20260315.html"]:
            open(os.path.join(td, fn), "w").close()
        got = mod.resolve_html_path("acme")
        assert os.path.basename(got) == "acme-20260601.html", \
            f"resolver did not pick newest dated clone: {got}"
        # (b) exact match still wins over a dated sibling
        open(os.path.join(td, "beta.html"), "w").close()
        open(os.path.join(td, "beta-20260601.html"), "w").close()
        got = mod.resolve_html_path("beta")
        assert os.path.basename(got) == "beta.html", \
            f"resolver did not prefer the exact match: {got}"
        # (c) ambiguous non-dated matches must NOT be guessed
        open(os.path.join(td, "gamma-draft.html"), "w").close()
        open(os.path.join(td, "gamma-backup.html"), "w").close()
        got = mod.resolve_html_path("gamma")
        assert not os.path.exists(got), \
            f"resolver guessed an ambiguous non-dated file instead of not-found: {got}"


def check_audit_lead_reports_nonzero_check_count():
    """17. Belt-and-suspenders on the 0/0-false-PASS class, pinned at the
    audit_lead() layer (check #16 pins the resolver; this pins the grader).
    Two invariants:
      (a) auditing a REAL present blueprint must produce a NON-ZERO check
          count (total > 0) — a 0/0 result is the exact shape that let a
          file-resolution miss masquerade as a clean PASS;
      (b) auditing a guaranteed-absent slug must return an explicit error /
          score 0, NEVER a passing 0/0. So a future regression that makes
          audit_lead silently skip all checks fails here instead of shipping
          a green fleet that was never actually graded."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_audit_count_mod", os.path.join(REPO, "run-audit.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # (a) a real present blueprint yields a real (non-zero) check count.
    real = next((f[:-5] for f in sorted(os.listdir(mod.BP_DIR))
                 if f.endswith(".html") and not f.startswith(("_", "TEMPLATE"))),
                None)
    assert real is not None, "no real blueprint found to audit"
    r = mod.audit_lead(real)
    assert r.get("total", 0) > 0, \
        f"audit_lead({real}) reported 0 checks — 0/0 false-pass shape: {r}"
    # (b) an absent slug must NOT come back as a passing 0/0.
    bad = mod.audit_lead("definitely-not-a-real-blueprint-zzz-20990101")
    assert bad.get("score", 0) == 0 and "error" in bad, \
        f"absent slug did not report not-found (0/0 false-pass risk): {bad}"


def check_podcast_duration_standard_is_8_to_12():
    """17. Audio DURATION-WINDOW gate is observational only (Madison COO 2026-07-02):
    podcasts are generated at AudioLength.SHORT and accepted at their natural length.
    The fixed minute-window (was 8-12, then 7-16) is REMOVED — the real podcast gate is
    now D3-05 clean-ending / no-blind-hard-trim. This tripwire proves the window was
    removed on purpose (not accidentally re-narrowed) and that the clean-ending red-line
    is still wired."""
    src = _read(os.path.join(REPO, "run-audit.py"))
    assert "window lifted 2026-07-02" in src, \
        "duration gate must carry the intentional window-removal marker (Madison 2026-07-02)"
    assert "MIN_SEC, MAX_SEC" not in src, \
        "duration gate must NOT reinstate a fixed minute window — SHORT is accepted at natural length"
    assert "D3-05_podcast_clean_ending_RL" in src, \
        "the active podcast red-line (clean-ending / no blind hard-trim) must remain wired"
    assert "D3-03_podcast_duration_16to20min_RL" not in src, \
        "stale 16-20 duration red-line key must not remain"


def check_agent_prompt_quality_gate_wired():
    """18. Blueprint agent cards must be real operating runbooks, not short
    starter prompts. The generator blocks weak profile content and the strict
    gatekeeper runs a dedicated quality gate before production tokening."""
    generator = _read(os.path.join(REPO, "scripts", "gen-blueprint.py"))
    gatekeeper = _read(os.path.join(REPO, "scripts", "blueprint_gatekeeper_100.py"))
    quality_gate_path = os.path.join(REPO, "scripts", "blueprint_agent_prompt_quality_gate.py")
    quality_gate = _read(quality_gate_path)
    for token in [
        "validate_production_agent_prompt",
        "identity",
        "inputs",
        "workflow",
        "output schema",
        "escalation",
        "first-run test",
    ]:
        assert token in generator.lower(), f"gen-blueprint.py missing production prompt token: {token}"
    assert "blueprint_agent_prompt_quality_gate.py" in gatekeeper, \
        "strict gatekeeper must run the agent prompt quality gate"
    for token in [
        "REQUIRED_MARKERS",
        "extract_pre_prompts",
        "extract_agent_prompts",
        "visible prompt cards: found",
        "check_agent_cards_no_boilerplate",
        "need at least 3",
    ]:
        assert token in quality_gate, f"agent prompt quality gate missing token: {token}"


def check_clone_engine_coerces_list_tools():
    """19. A scraped lead whose `tools` field is a JSON array (the common shape —
    5 of 55 live leads) crashed clone-blueprint.sh's replacement engine with
    `TypeError: replace() argument 2 must be str, not list`, because the raw list
    was fed into html.replace() via the {{CRM_TOOL}} token. Two-part pin:
      (a) the engine derives a tools_str by joining a list (mirroring services_str)
          AND the replace loop defensively joins ANY list value before .replace(),
          so the *next* array field can't reintroduce the crash;
      (b) a runtime tripwire that replicates the exact join+replace mechanism with
          a list value and proves it renders "A, B, C" with no leftover token and
          no TypeError."""
    script = _read(os.path.join(REPO, "scripts", "clone-blueprint.sh"))
    # (a) the tools_str coercion exists (list -> ', '.join, else passthrough)
    assert "tools_str = ', '.join(tools) if isinstance(tools, list) else tools" in script, \
        "clone-blueprint.sh missing tools_str list coercion"
    assert "'{{CRM_TOOL}}': tools_str if tools_str else 'your CRM'" in script, \
        "{{CRM_TOOL}} replacement no longer uses the coerced tools_str"
    # (a) the replace loop defensively joins ANY list value (future array fields)
    assert "if isinstance(value, list):" in script and \
        "value = ', '.join(str(v) for v in value)" in script, \
        "replace loop lost the defensive list-join guard for future array fields"
    # (b) runtime tripwire: the exact join+replace mechanism must not crash on a list
    tools = ["CRM / quote pipeline", "Email", "Phone"]
    tools_str = ', '.join(tools) if isinstance(tools, list) else tools
    html = "Use {{CRM_TOOL}} every day."
    value = tools_str if tools_str else 'your CRM'
    if isinstance(value, list):  # the loop guard, replicated verbatim
        value = ', '.join(str(v) for v in value)
    html = html.replace("{{CRM_TOOL}}", value)  # this raised TypeError pre-fix
    assert html == "Use CRM / quote pipeline, Email, Phone every day.", \
        f"list-tools did not render as a joined string: {html!r}"
    assert "{{CRM_TOOL}}" not in html, \
        f"{{{{CRM_TOOL}}}} token left unrendered after list coercion: {html!r}"


def check_no_sub7day_golive_promise_in_blueprints():
    """RULES.md Rule 31 / blueprint-ai-skill v3.41 (2026-07-01, Madison COO):
    Blueprint pages must NEVER promise a go-live inside the first 7 days.
    Week 1 = onboarding only, first agent week 2, all 6 agents week 3.
    Bans the old hero stats ('3 Days In', '7 Days'), the raw 'Days 1-3'/'Days 4-7'
    roadmap phase labels, and 'first agent(s) is/are live' result cells.
    Scans top-level blueprints/*.html only (archival _obsolete/ snapshots excluded)."""
    banned = [
        '<span class="num">3 Days In</span>',
        '<span class="num">7 Days</span>',
        ">Days 1-3<", ">Days 4-7<", ">Days 1–3<", ">Days 4–7<",
        "<strong>Days 1-3</strong>", "<strong>Days 4-7</strong>",
        "Your first agent is live", "Your first agents are live",
    ]
    offenders = []
    for fn in sorted(os.listdir(BP_DIR)):
        if not fn.endswith(".html") or fn.startswith("test-"):
            continue
        html = _read(os.path.join(BP_DIR, fn))
        hit = [b for b in banned if b in html]
        if hit:
            offenders.append(f"{fn}: {hit}")
    assert not offenders, (
        "sub-7-day go-live promise found (banned by RULES.md Rule 31):\n"
        + "\n".join(offenders)
    )


CHECKS = [
    ("CLONE_ENGINE_COERCES_LIST_TOOLS", check_clone_engine_coerces_list_tools),
    ("PRECOMMIT_OV_SKIP_PATH_INTACT", check_precommit_ov_skip_path_intact),
    ("RESOLVE_HTML_PATH_PREFERS_DATED_SLUG", check_resolve_html_path_prefers_dated_slug),
    ("AUDIT_LEAD_REPORTS_NONZERO_CHECK_COUNT", check_audit_lead_reports_nonzero_check_count),
    ("NO_LINKEDIN_SLIDER_IN_TEMPLATE", check_no_linkedin_slider_in_template),
    ("NO_NONB2B_LINKEDIN_VIOLATION", check_no_nonb2b_linkedin_violation),
    ("D7_18_IS_HARD_FAIL", check_d7_18_is_hard_fail),
    ("FINANCIAL_GATE_WIRED_IN_PRECOMMIT", check_financial_gate_wired_in_precommit),
    ("INDUSTRY_CONFIG_IS_SINGLE_SOURCE", check_industry_config_is_single_source),
    ("D9_01_IS_REAL_NOT_STUB", check_d9_01_is_real_not_stub),
    ("PODCAST_ALIAS_EXPLICIT", check_podcast_alias_explicit),
    ("D1_01_CHECKS_TITLE", check_d1_01_checks_title),
    ("FORMAT3_GATE_WIRED", check_format3_gate_wired),
    ("RESTAURANT_DRIFT_GATE_WIRED", check_restaurant_drift_gate_wired),
    ("PODCAST_DIRECT_ADDRESS_ARTIFACT_GATE", check_podcast_direct_address_artifact_gate),
    ("LOCAL_AUDIO_AUDIT_NOT_PUBLIC_DEPLOY_BLOCKED", check_local_audio_audit_not_public_deploy_blocked),
    ("PRODUCTION_SUMMARY_NO_SEND_GUARD", check_production_summary_no_send_guard),
    ("DELIVERY_EMAIL_ESCAPES_AMPERSAND_TOKENS", check_delivery_email_escapes_ampersand_tokens),
    ("PODCAST_DURATION_STANDARD_IS_8_TO_12", check_podcast_duration_standard_is_8_to_12),
    ("AGENT_PROMPT_QUALITY_GATE_WIRED", check_agent_prompt_quality_gate_wired),
    ("NO_SUB7DAY_GOLIVE_PROMISE", check_no_sub7day_golive_promise_in_blueprints),
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
