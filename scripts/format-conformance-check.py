#!/usr/bin/env python3
"""
Format-3 Structural Conformance Gate for Blueprint HTML.

The GUARANTEE mechanism Bennett asked for: "every time I ask for the blueprint AI
... I get this exact same output, but with another company's information."

This gate asserts a generated blueprint matches the format-3-red-dense-scroll
GOLD signature — same 16-section structure, same custom chaptered podcast player,
same component DNA, real-MP3 audio container, single (non-duplicated) player —
regardless of which company's content fills it.

Usage:
  python3 format-conformance-check.py <blueprint.html> [--podcast <mp3path>]

Exit codes:
  0 = conforms to the format-3 gold signature
  1 = at least one conformance check failed (DRIFT — do not ship)
  2 = file not readable / missing

v1.0 — 2026-06-01 — created per Bennett directive: lock the gold format so every
       blueprint-ai-skill run reproduces format-3 structure with new company data.
       Verified to PASS format-3-red-dense-scroll.html and FAIL the 21-section
       Melissa-v2 TEMPLATE.html (proves it discriminates the two structures).
v1.1 — 2026-06-01 — added FC-08 [RL] podcast 6-20MB byte-window gate. FC-06 proved
       the container was mp3 but NOT the length; a --length short stub (4.5MB) passed
       FC-06 yet was too thin, and an un-transcoded export (31MB+) hung the iOS player.
       FC-08 makes the 6-20MB walkthrough window machine-checked. Verified PASS on the
       14.1MB Brent deliverable, FAIL on a 66MB un-transcoded export.
"""
import re, sys, pathlib, argparse, subprocess
from typing import Optional

# --- The format-3 GOLD signature (captured 2026-06-01 from the live gold ref) ---
EXPECTED_SECTION_IDS = [
    "hero", "profile", "results", "pillars", "stack", "gaps", "oppmap",
    "ignore", "agents", "timeline", "calculator", "prompts", "demo",
    "listen", "sources", "apply",
]
# Custom chaptered player IDs — each must appear EXACTLY ONCE (single player, no
# duplicate-ID double-bind bug that broke the listen button on 2026-06-01).
PLAYER_IDS = [
    "podAudio", "podTrack", "podFill", "podThumb", "podElapsed", "podDuration",
    "podPlay", "podPlayIcon", "podBack", "podFwd", "podBadge", "podEq",
    "podChapterName", "podSpeed", "podMute", "podVolIcon", "podError",
    "podMini", "podMiniPlay", "podMiniIcon", "podMiniTime",
]
# Component DNA — class : minimum count that proves the red-dense-scroll layout.
COMPONENT_DNA = {
    "gap-card": 6,
    "pillar-card": 3,
    "stack-card": 4,
    "agent-card": 6,
    "milestone": 2,
    "prompt-card": 3,
    "hero-badge": 1,
}


def check(html_path: pathlib.Path, podcast_path: Optional[pathlib.Path] = None):
    if not html_path.exists():
        print(f"ERR: {html_path} not found")
        return 2
    html = html_path.read_text()
    body_match = re.search(r"<body[\s\S]*</body>", html, re.I)
    body = body_match.group(0) if body_match else html

    checks = []

    # FC-01 [RL] 16 sections present, in exact gold order.
    found_section_ids = re.findall(r'<section[^>]*\bid="([^"]+)"', body, re.I)
    order_ok = found_section_ids == EXPECTED_SECTION_IDS
    detail = None if order_ok else f"got {found_section_ids}"
    checks.append(("FC-01", "[RL] 16 gold sections in exact order", order_ok, detail))

    # FC-02 [RL] custom chaptered player — every signature ID present exactly once.
    dup = []
    missing = []
    for pid in PLAYER_IDS:
        n = len(re.findall(rf'\bid="{re.escape(pid)}"', html))
        if n == 0:
            missing.append(pid)
        elif n > 1:
            dup.append(f"{pid}x{n}")
    player_ok = not missing and not dup
    info = None
    if not player_ok:
        info = f"missing={missing} dup={dup}"
    checks.append(("FC-02", "[RL] custom player IDs each present exactly once", player_ok, info))

    # FC-03 [RL] single podcast player section (no duplicate id="listen").
    listen_n = len(re.findall(r'\bid="listen"', body))
    checks.append(("FC-03", f"[RL] exactly one id=\"listen\" (found {listen_n})", listen_n == 1, listen_n))

    # FC-04 component DNA — red-dense-scroll layout present at expected density.
    dna_fail = []
    for cls, minimum in COMPONENT_DNA.items():
        n = len(re.findall(rf'class="[^"]*\b{re.escape(cls)}\b', body))
        if n < minimum:
            dna_fail.append(f"{cls}={n}(<{minimum})")
    checks.append(("FC-04", "component DNA at gold density", len(dna_fail) == 0, dna_fail))

    # FC-05 chaptered player JS wiring present (togglePlay + addEventListener, no typo).
    has_toggle = "togglePlay" in html
    has_listener = bool(re.search(r"addEventListener\(\s*['\"]click['\"]", html))
    no_typo = "addEventListenener" not in html  # the 2026-06-01 dup-player typo
    js_ok = has_toggle and has_listener and no_typo
    checks.append(("FC-05", "player JS wired (togglePlay+click listener, no typo)", js_ok,
                   None if js_ok else f"toggle={has_toggle} listener={has_listener} no_typo={no_typo}"))

    # FC-07 [RL] play-button hardening present (2026-06-01 live-bug fix).
    # The large unbuffered podcast needs (a) a forced load() when readyState===0
    # and (b) a .catch() on the play() Promise to surface AbortError instead of a
    # silent dead button. FC-05 only proves togglePlay exists; FC-07 proves it is
    # the HARDENED togglePlay so a future edit can't strip the fix and still pass.
    has_play_catch = bool(re.search(r"\.play\(\)", html)) and bool(
        re.search(r"p\s*&&\s*p\.catch|\.play\(\)\s*\)?\s*;?\s*[^\n]*\.catch\(", html)
    )
    has_ready_guard = bool(re.search(r"readyState\s*===?\s*0", html)) and "load()" in html
    hard_ok = has_play_catch and has_ready_guard
    checks.append(("FC-07", "[RL] play-button hardened (play().catch + readyState load guard)",
                   hard_ok, None if hard_ok else f"play_catch={has_play_catch} ready_guard={has_ready_guard}"))

    # FC-06 [RL] audio container is a REAL mp3 (not AAC/MP4 mislabeled .mp3).
    # iOS/Safari refuses AAC-in-MP4 served as audio/mpeg. Only check if a path given.
    if podcast_path is not None:
        if not podcast_path.exists():
            checks.append(("FC-06", "[RL] podcast is real MP3", False, f"{podcast_path} missing"))
        else:
            try:
                out = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=format_name",
                     "-of", "csv=p=0", str(podcast_path)],
                    capture_output=True, text=True, timeout=30).stdout.strip()
                is_mp3 = out == "mp3"
                checks.append(("FC-06", f"[RL] podcast container is real mp3 (got '{out}')", is_mp3, out))
            except Exception as e:
                checks.append(("FC-06", "[RL] podcast is real MP3", False, f"ffprobe err:{e}"))
    else:
        checks.append(("FC-06", "[RL] podcast real-MP3 (skipped — no --podcast)", True, "SKIP"))

    # FC-08 [RL] podcast byte-size inside the 6-20MB walkthrough WINDOW.
    # Thread learning 2026-06-01: FC-06 proves the CONTAINER is mp3 but says nothing
    # about length. A --length short render passes FC-06 yet is a 4.5MB/4.7min stub
    # (too thin to be a real walkthrough); an un-transcoded NotebookLM export is a
    # 31MB+ giant that hangs the unbuffered iOS player. The enforced deliverable is a
    # 6-20MB walkthrough. This gate makes that window machine-checked, not manual.
    FLOOR, CEIL = 6 * 1024 * 1024, 20 * 1024 * 1024
    if podcast_path is not None and podcast_path.exists():
        sz = podcast_path.stat().st_size
        size_ok = FLOOR <= sz <= CEIL
        mb = sz / 1048576
        checks.append(("FC-08", f"[RL] podcast in 6-20MB window (got {mb:.1f}MB)", size_ok,
                       None if size_ok else f"{mb:.1f}MB outside 6-20MB"))
    else:
        checks.append(("FC-08", "[RL] podcast 6-20MB window (skipped — no --podcast)", True, "SKIP"))

    passed = sum(1 for c in checks if c[2])
    failed = [c for c in checks if not c[2]]
    rl_failed = [c for c in failed if "[RL]" in c[1]]
    print(f"\n=== Format-3 Conformance: {passed}/{len(checks)} — {html_path.name} ===\n")
    for cid, name, ok, info in checks:
        flag = "PASS" if ok else "FAIL"
        extra = f" — {info}" if (not ok and info) else ""
        print(f"  [{flag}] {cid} {name}{extra}")
    print(f"\nFAILED: {len(failed)}  RED-LINE FAILED: {len(rl_failed)}")
    if rl_failed:
        print("RESULT: HALT — structural drift from the gold format. Do not ship.")
    elif failed:
        print("RESULT: SOFT FAIL — non-red-line drift; review before ship.")
    else:
        print("RESULT: PASS — conforms to the format-3 gold signature.")
    return 0 if not failed else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Format-3 structural conformance gate")
    p.add_argument("html_path", type=pathlib.Path)
    p.add_argument("--podcast", type=pathlib.Path, default=None,
                   help="Path to the podcast mp3 (enables FC-06 container check)")
    a = p.parse_args()
    sys.exit(check(a.html_path, a.podcast))
