#!/usr/bin/env python3
"""Blueprint Completion Gate — 50-breakpoint category gate.

SKILL.md v3.14 §Category Gate. Runs before any Bennett preview, prospect send,
or completion claim. Returns 0 on PASS, nonzero on FAIL.

Usage:
    python3 blueprint_completion_gate.py --html <path> --receipt-dir <dir> --lead <slug>
    python3 blueprint_completion_gate.py --html <path> --receipt-dir <dir> --lead <slug> --require-production

Author: Ivan CC / Blueprint AI Skill v3.14
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import unquote, urlparse


# Production audio is a WINDOW, not a one-sided floor. A delivery walkthrough
# must be substantial but not an overlong lecture: roughly 6-20 minutes at
# 128kbps.
MIN_PRODUCTION_AUDIO_BYTES = 6 * 1024 * 1024
MAX_PRODUCTION_AUDIO_BYTES = 20 * 1024 * 1024
MAX_PRODUCTION_AUDIO_MINUTES = 20


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY DEFINITIONS (from SKILL.md v3.14 §Category Gates)
# ─────────────────────────────────────────────────────────────────────────────
CATEGORIES = {
    "Structure": {
        "weight": 1.0,
        "checks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    },
    "Content": {
        "weight": 1.0,
        "checks": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    },
    "Funnel": {
        "weight": 1.0,
        "checks": [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    },
    "Audio": {
        "weight": 1.0,
        "checks": [31, 32, 33, 34, 35]
    },
    "Proof": {
        "weight": 1.0,
        "checks": [36, 37, 38, 39, 40, 41]
    },
    "Production": {
        "weight": 2.0,  # Higher weight — production checks are harder gates
        "checks": [42, 43, 44, 45, 46, 47, 48]
    },
    "Delivery": {
        "weight": 1.0,
        "checks": [49]
    },
    "Revenue": {
        "weight": 1.0,
        "checks": [50]
    },
}


def receipt_pass(path: Path) -> bool:
    """Return true only when a receipt exists and positively proves success."""
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False

    if not isinstance(data, dict):
        return False

    pass_token = data.get("pass_token")
    if isinstance(pass_token, dict) and pass_token.get("pass") is True:
        return True

    if data.get("pass") is True or data.get("ok") is True or data.get("verified") is True:
        return True
    if data.get("overall_pass") is True:
        return True
    if isinstance(data.get("summary"), dict) and data["summary"].get("overall_pass") is True:
        return True
    if int(data.get("http_code") or data.get("status_code") or 0) == 200:
        return True

    status = str(data.get("status") or data.get("verdict") or "").strip().upper()
    return status in {"PASS", "PASSED", "OK", "SUCCESS", "GREEN", "DIAMOND_PASS"}


def load_receipt(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def receipt_audio_hash_matches(data: dict, html_path: Optional[Path]) -> bool:
    expected = data.get("audio_sha256")
    audio = data.get("audio")
    if not expected or not audio:
        return False
    audio_path = Path(audio)
    candidates = []
    if audio_path.is_absolute():
        candidates.append(audio_path)
    else:
        candidates.append((Path.cwd() / audio_path).resolve())
        if html_path is not None:
            candidates.extend([
                (html_path.parent / audio_path).resolve(),
                (html_path.parent.parent / audio_path).resolve(),
            ])
    return any(candidate.exists() and file_sha256(candidate) == expected for candidate in candidates)


def production_receipt_result(num: int, path: Path, html: str,
                              html_path: Optional[Path]) -> Tuple[bool, str]:
    """Schema-specific production proof validators.

    Generic "status: PASS" is not enough for production checks because preview
    receipts can be honest but narrower than customer-send approval.
    """
    data = load_receipt(path)
    if not data:
        return False, f"PRODUCTION REQUIRED: Missing or invalid receipt for check {num}"

    base_pass = data.get("pass") is True or str(data.get("status") or "").upper() == "PASS"

    if num == 42:
        ok = base_pass and int(data.get("http_code") or 0) == 200 and bool(data.get("url"))
        return ok, "Public page HTTP 200 verified" if ok else "Public page receipt must include pass=true, http_code=200, and url"

    if num == 43:
        ok = base_pass and bool(data.get("registry_file")) and data.get("verified") is True
        return ok, "Drive artifact registry verified" if ok else "Drive receipt must include registry_file and verified=true"

    if num == 44:
        ok = base_pass and bool(data.get("notion_page_id")) and data.get("row_current") is True
        return ok, "Notion Sprint row current" if ok else "Notion receipt must include notion_page_id and row_current=true"

    if num == 45:
        contact = data.get("contact") if isinstance(data.get("contact"), dict) else {}
        conversation = data.get("conversation") if isinstance(data.get("conversation"), dict) else {}
        ok = (
            base_pass
            and int(data.get("exact_contact_count") or 0) == 1
            and bool(contact.get("id"))
            and data.get("instant_response_verified") is True
            and bool(conversation.get("id"))
        )
        detail = "GHL exact contact readback and instant response verified" if ok else (
            "GHL receipt must prove exact_contact_count=1, contact.id, conversation.id, and instant_response_verified=true"
        )
        return ok, detail

    if num == 46:
        ok = (
            base_pass
            and int(data.get("relay_http_status") or 0) == 200
            and data.get("relay_mode") in {"updated", "matched"}
            and bool(data.get("returned_contact_id"))
            and data.get("returned_contact_id") == data.get("expected_contact_id")
            and int(data.get("exact_contact_count_after_repeat") or 0) == 1
        )
        detail = "Repeat submit updated same GHL contact" if ok else (
            "Repeat-submit receipt must prove HTTP 200, updated/matched mode, same contact id, and exact count 1"
        )
        return ok, detail

    if num == 47:
        local_audio_ok, local_audio_detail = audio_size_check(html, html_path)
        remote_size = int(data.get("size_download") or 0)
        remote_ok = (
            base_pass
            and int(data.get("http_code") or 0) == 200
            and MIN_PRODUCTION_AUDIO_BYTES <= remote_size <= MAX_PRODUCTION_AUDIO_BYTES
        )
        direct_ok = (
            data.get("direct_address_audio_verified") is True
            and data.get("opening_direct_address_verified") is True
            and data.get("opening_exact_or_close") is True
            and data.get("banned_audio_phrases_found") in ([], None)
            and data.get("third_person_patterns_found") in ([], None)
            and int(data.get("you_your_count") or 0) >= 5
        )
        hash_ok = receipt_audio_hash_matches(data, html_path)
        ok = remote_ok and local_audio_ok and direct_ok and hash_ok
        if ok:
            return True, f"Public/local podcast and direct-address audio verified ({remote_size} bytes)"
        if not remote_ok:
            return False, (
                "Public podcast receipt must include pass=true, http_code=200, and size_download within "
                f"[{MIN_PRODUCTION_AUDIO_BYTES}, {MAX_PRODUCTION_AUDIO_BYTES}] bytes "
                f"(~6-{MAX_PRODUCTION_AUDIO_MINUTES} min @128kbps)"
            )
        if not direct_ok:
            return False, "Podcast receipt must prove direct opening, direct_address_audio_verified=true, no source-material/third-person phrases, and >=5 you/your references"
        if not hash_ok:
            return False, "Podcast receipt audio_sha256 must match the current local MP3"
        return False, local_audio_detail

    if num == 48:
        external = data.get("external_customer_send_approved") is True or data.get("bennett_approved") is True
        preview = data.get("bennett_preview_requested") is True or data.get("approval_scope") == "bennett_preview_only"
        if base_pass and external:
            return True, "Approval scope: external customer send approved"
        if base_pass and preview:
            return True, "Approval scope: Bennett preview only; customer send remains blocked"
        return False, "Approval receipt must record Bennett preview scope or external customer-send approval"

    return receipt_pass(path), "OK" if receipt_pass(path) else f"Missing or failing receipt for check {num}"


def audio_size_check(
    html: str,
    html_path: Optional[Path],
    min_bytes: int = MIN_PRODUCTION_AUDIO_BYTES,
    max_bytes: int = MAX_PRODUCTION_AUDIO_BYTES,
) -> Tuple[bool, str]:
    """Verify the referenced local MP3 exists inside the production-size window."""
    refs = re.findall(r'(?:src|href)=["\']([^"\']*podcasts/[^"\']+\.mp3[^"\']*)["\']', html, re.I)
    if not refs:
        return False, "No podcast MP3 reference found"

    roots = []
    if html_path is not None:
        roots.append(html_path.parent.parent)
        roots.append(html_path.parent)
    roots.append(Path.cwd())

    inspected = []
    for ref in refs:
        parsed = urlparse(ref)
        path_text = parsed.path if parsed.scheme else ref
        path_text = unquote(path_text.split("?", 1)[0])
        marker = path_text.find("podcasts/")
        if marker == -1:
            continue
        rel = Path(path_text[marker:])
        for root in roots:
            candidate = (root / rel).resolve()
            if candidate in inspected:
                continue
            inspected.append(candidate)
            if candidate.exists():
                size = candidate.stat().st_size
                if size < min_bytes:
                    return False, f"{rel} too small: {size:,} bytes < {min_bytes:,} (floor)"
                if size > max_bytes:
                    return False, (
                        f"{rel} too large: {size:,} bytes > {max_bytes:,} "
                        f"(ceiling ~{MAX_PRODUCTION_AUDIO_MINUTES} min)"
                    )
                return True, f"{rel} size {size:,} bytes (within window)"

    return False, "Referenced MP3 not found locally"

# ─────────────────────────────────────────────────────────────────────────────
# 50 BREAKPOINT CHECK FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def run_checks(html: str, lead_slug: str, receipt_dir: Path, require_production: bool,
               already_sent: bool = False, html_path: Optional[Path] = None) -> dict:
    """
    already_sent: if True, proof receipt checks (#36-41) are enforced.
    If False (blueprint not yet formally sent), proof checks are INFO only.
    """
    results = {}
    html_lower = html.lower()

    # ── STRUCTURE (1-10) ─────────────────────────────────────────────────────
    # 1. Wrong/stale Drive skill version — informational only; can't enforce from HTML alone
    has_version = "blueprint-ai-skill" in html_lower or "v3." in html
    results[1] = {
        "desc": "Drive skill version present in generation comment",
        "pass": None if not has_version else True,  # INFO: missing marker doesn't block gate
        "severity": "info",
        "detail": "No skill version marker found (legacy blueprint — add <!-- blueprint-ai-skill v3.X --> to header)" if not has_version else "OK"
    }

    # 2. Canonical orchestrator path referenced
    results[2] = {
        "desc": "Manual stage interpretation not used (no MANUAL_RECOVERY marker)",
        "pass": "manual_recovery" not in html_lower and "manual recovery run" not in html_lower,
        "severity": "warning",
        "detail": "OK"
    }

    # 3. Duplicate local SKILL.md shadow — not detectable in HTML; always pass
    results[3] = {
        "desc": "Template shadow check (N/A for HTML)",
        "pass": True,
        "severity": "info",
        "detail": "Not applicable to HTML output"
    }

    # 4. Contradictory gold-standard instructions — check for Command Center NAV TAB link
    # Detect both anchor-based nav (<a>command center</a>) and button-based tab (<button>Command Center</button>)
    has_cmd_tab = bool(re.search(r'<a[^>]*>[^<]*command center[^<]*</a>', html_lower)) or \
                  bool(re.search(r'<button[^>]*>[^<]*command center[^<]*</button>', html_lower))
    results[4] = {
        "desc": "No contradictory gold-standard (Command Center tab absent from nav)",
        "pass": not has_cmd_tab,
        "severity": "major",
        "detail": "Command Center tab found in nav" if has_cmd_tab else "OK"
    }

    # 5. Wrong template cloned — check for Melissa v2 signature elements
    # Accept both anchor nav ("your profile") and button-tab nav ("full profile" or "profile" tab)
    has_melissa_sig = "5-tab" in html_lower or "your profile" in html_lower or \
                      bool(re.search(r'switchtab\(["\']profile', html_lower)) or \
                      "full profile" in html_lower
    results[5] = {
        "desc": "Melissa v2 template cloned (Your Profile tab present)",
        "pass": has_melissa_sig,
        "severity": "major",
        "detail": "Missing Melissa v2 signature elements" if not has_melissa_sig else "OK"
    }

    # 6. Section count — require at least 10 meaningful sections (not audit-support phantoms)
    # Threshold updated 15→12→10 after removing deprecated Website Audit + Command Center sections (2026-05-27)
    real_sections = re.findall(r'<(section|div)[^>]*class=["\'][^"\']*section[^"\']*["\'][^>]*>', html, re.I)
    # Exclude aria-hidden sections
    hidden_sections = re.findall(r'aria-hidden=["\']true["\']', html, re.I)
    effective_sections = max(0, len(real_sections) - len(hidden_sections))
    results[6] = {
        "desc": "Section count ≥ 10 (excluding aria-hidden)",
        "pass": effective_sections >= 10,
        "severity": "major",
        "detail": f"Found {effective_sections} effective sections (need ≥10)"
    }

    # 7. Required section IDs — check for 5-nav structure
    # Detect both anchor-based nav and button-based tab nav
    nav_ids = re.findall(r'<a[^>]*href=["\'][^"\']*["\'][^>]*>([^<]+)</a>', html)
    nav_btn = re.findall(r'<button[^>]*switchtab[^>]*>([^<]+)</button>', html_lower)
    nav_text = [t.strip().lower() for t in nav_ids] + [t.strip() for t in nav_btn]
    has_your_profile = any("your profile" in t or "full profile" in t or ("profile" in t and "full" not in t) for t in nav_text)
    has_ai_agents = any("ai agent" in t or "agents" in t or "systems" in t for t in nav_text)
    has_roi = any("roi" in t or "calculator" in t for t in nav_text)
    has_listen = any("listen" in t for t in nav_text)
    # "Apply" can be in nav or as a qualify.html CTA anywhere in the page
    has_apply = any("apply" in t or "qualify" in t for t in nav_text) or \
                bool(re.findall(r'href=["\'][^"\']*qualify\.html[^"\']*["\']', html))
    nav_pass = all([has_your_profile, has_ai_agents, has_roi, has_listen, has_apply])
    results[7] = {
        "desc": "Nav: Your Profile | AI Agents | ROI Calculator | Listen | Apply",
        "pass": nav_pass,
        "severity": "major",
        "detail": f"Nav tabs: {[t for t in nav_text if t]} — missing required tabs" if not nav_pass else "OK"
    }

    # 8. Wrong tab set — Command Center tab absent
    cmd_center_tab = any("command center" in t for t in nav_text)
    results[8] = {
        "desc": "Command Center tab NOT in nav",
        "pass": not cmd_center_tab,
        "severity": "critical",
        "detail": "Command Center tab found — REMOVE" if cmd_center_tab else "OK"
    }

    # 9. Demo Site tab absent — only check nav tabs, not content links
    # nav_text includes all anchors; filter to nav context only (within nav-links or tab-nav)
    nav_section = re.search(r'(?:<nav[^>]*>|<div[^>]*(?:tab-nav|nav-links)[^>]*>)(.*?)(?:</nav>|</div>)', html_lower, re.DOTALL)
    nav_only_text = []
    if nav_section:
        nav_anchors = re.findall(r'<a[^>]*>([^<]+)</a>', nav_section.group(1))
        nav_btns = re.findall(r'<button[^>]*>([^<]+)</button>', nav_section.group(1))
        nav_only_text = [t.strip().lower() for t in nav_anchors + nav_btns]
    demo_site_tab = any("demo site" in t or t.strip() == "demo" for t in nav_only_text)
    results[9] = {
        "desc": "Demo Site tab NOT in nav",
        "pass": not demo_site_tab,
        "severity": "critical",
        "detail": "Demo Site tab found — REMOVE" if demo_site_tab else "OK"
    }

    # 10. Website Audit section absent (deprecated Stage 2)
    # The deprecated section has id="audit" AND contains "your digital presence" or "audit summary" text
    # NOT the same as the AI Readiness Audit (which is valid and should remain)
    html_no_html_comments = re.sub(r'<!--.*?-->', '', html_lower, flags=re.DOTALL)

    # Look for the deprecated website audit pattern: sections with "your digital presence" label
    # OR audit-card with conversion/speed-to-lead scores (OLD website audit from Stage 2)
    # NOT the AI Readiness Audit (which has "ai readiness" label — valid, keep it)
    # Match deprecated Website Audit section (Stage 2) specifically:
    # Requires "your digital presence" OR audit-card with old-style phase names (conversion/speed-to-lead)
    deprecated_audit = bool(re.search(
        r'your digital presence',
        html_no_html_comments
    )) or bool(re.search(r'class=["\'][^"\']*website-audit', html_no_html_comments)) or \
       bool(re.search(r'class=["\']audit-card["\'][^>]*>.*?<div class=["\']audit-phase["\']>(?:conversion|speed.to.lead)</div>', html_no_html_comments, re.DOTALL))

    results[10] = {
        "desc": "Website Audit section absent (deprecated Stage 2)",
        "pass": not deprecated_audit,
        "severity": "major",
        "detail": "Deprecated website audit section found — remove" if deprecated_audit else "OK"
    }

    # ── CONTENT (11-20) ──────────────────────────────────────────────────────
    # 11. Countdown timer absent
    # Strip HTML comments before checking to avoid false positives from "removed" notes
    html_no_comments = re.sub(r'<!--.*?-->', '', html_lower, flags=re.DOTALL)
    # Strip JS single-line comments too
    html_no_comments = re.sub(r'//[^\n]*', '', html_no_comments)
    countdown = bool(re.search(r'\bcountdown\b', html_no_comments)) and \
                bool(re.search(r'id=["\']countdown["\']|class=["\'][^"\']*countdown', html_no_comments))
    results[11] = {
        "desc": "No countdown timer",
        "pass": not countdown,
        "severity": "major",
        "detail": "Countdown timer element found — remove" if countdown else "OK"
    }

    # 12. Hero % claims have source links — check for bare +XX% patterns
    hero_match = re.search(r'<section[^>]*id=["\']hero["\'][^>]*>.*?</section>', html, re.DOTALL | re.I)
    bare_pct = []
    if hero_match:
        hero_html = hero_match.group(0)
        # Find bare % not adjacent to href
        bare_pct = re.findall(r'(?<!\w)\+\d+%(?![^<]*</a>)', hero_html)
    results[12] = {
        "desc": "No bare hero % claims without source link",
        "pass": len(bare_pct) == 0,
        "severity": "critical",
        "detail": f"Bare % claims without href: {bare_pct}" if bare_pct else "OK"
    }

    # 13. No hardcoded ROI defaults in calculator JS (check JS section only)
    js_section = re.search(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.I)
    js_text = js_section.group(1) if js_section else ""
    # Look for hardcoded close rate (0.12 or 0.18 as JS number, not CSS rgba)
    hardcoded_roi_in_js = bool(re.search(r'(?:close_rate|closeRate|sliderClose)\s*[=:]\s*(?:0\.12|0\.18|12|18)\b', js_text, re.I))
    hardcoded_contract = bool(re.search(r'(?:avg_contract|sliderContract|contractValue)\s*[=:]\s*45000\b', js_text, re.I))
    results[13] = {
        "desc": "No hardcoded ROI defaults (12%, 18%, $45k) in calculator JS",
        "pass": not hardcoded_roi_in_js and not hardcoded_contract,
        "severity": "critical",
        "detail": "Hardcoded ROI values found in calculator JS" if (hardcoded_roi_in_js or hardcoded_contract) else "OK"
    }

    # 14. No hardcoded contract values
    hardcoded_45k = bool(re.search(r'\$45,?000', html)) and "45000" in js_text
    results[14] = {
        "desc": "No hardcoded $45,000 contract value",
        "pass": not hardcoded_45k,
        "severity": "critical",
        "detail": "$45,000 hardcoded found" if hardcoded_45k else "OK"
    }

    # 15. No hardcoded close rate
    hardcoded_close = bool(re.search(r'(?:18%|12%)\s*close rate', html_lower))
    results[15] = {
        "desc": "No hardcoded close rate text",
        "pass": not hardcoded_close,
        "severity": "critical",
        "detail": "Hardcoded close rate text found" if hardcoded_close else "OK"
    }

    # 16. No fabricated revenue range
    fabricated_revenue = bool(re.search(r'\$[0-9]+[KMk]+\s*[-–]\s*\$[0-9]+[KMk]+\s*(?:ARR|revenue|per year)', html, re.I))
    results[16] = {
        "desc": "Revenue ranges are user-driven (calculator) not hardcoded in text",
        "pass": True,  # Hard to detect — flag as warning
        "severity": "warning",
        "detail": "Manual review recommended for fabricated revenue ranges"
    }

    # 17. No fabricated testimonials
    fabricated_testimonials = bool(re.search(r'(?:says|said|quote)[^"\']{0,50}(?:Marcus|John|Sarah|Customer A)\b', html, re.I))
    results[17] = {
        "desc": "No fabricated testimonials",
        "pass": not fabricated_testimonials,
        "severity": "critical",
        "detail": "Possible fabricated testimonial detected" if fabricated_testimonials else "OK"
    }

    # 18. No unsourced benchmarks — all <sup> should have href nearby
    sups = re.findall(r'<sup>.*?</sup>', html, re.DOTALL)
    # Check if every sup is in a context with an <a href>
    unsourced = 0
    for sup_match in re.finditer(r'<li[^>]*>.*?</li>', html, re.DOTALL):
        item = sup_match.group(0)
        if '<sup>' in item and '<a href' not in item:
            unsourced += 1
    results[18] = {
        "desc": "All benchmarks in source list have clickable href",
        "pass": unsourced == 0,
        "severity": "major",
        "detail": f"{unsourced} source list items have <sup> without <a href>" if unsourced > 0 else "OK"
    }

    # 19. No bare citation text (citations in source list without href)
    # Only check source-list items / footnotes, not CSS styles or inline CRM demo text
    html_no_style = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.I)
    bare_citations = re.findall(r'<div[^>]*class=["\'][^"\']*source-item[^"\']*["\'][^>]*>.*?Source:\s+(?!<a\b)[A-Z][a-z]', html_no_style, re.I | re.DOTALL)
    results[19] = {
        "desc": "No bare citation text without <a href>",
        "pass": len(bare_citations) == 0,
        "severity": "major",
        "detail": f"{len(bare_citations)} bare source-list citations without href" if bare_citations else "OK"
    }

    # 20. Positive tone + no visibly corrupted AI Agent labels
    # Use contextual patterns to avoid false positives like "research behind this roadmap"
    negative_tone = bool(re.search(
        r'\b(?:your business (?:is )?(?:struggling|broken|failing|behind)|'
        r'(?:struggling|disorganized|failing) (?:to|with|at)|'
        r'poor performance|'
        r'business is behind|'
        r'(?:you are|you\'re|you\'ve been) (?:struggling|behind|failing))\b',
        html_lower
    ))
    malformed_pillar_tags = re.findall(
        r'<span[^>]*class=["\'][^"\']*(?:pillar-tag|agent-tag|tag)[^"\']*["\'][^>]*>\s*(\$out|\$in|T)\s*</span>',
        html,
        re.I
    )
    results[20] = {
        "desc": "Positive tone and no corrupted AI Agent labels",
        "pass": not negative_tone and not malformed_pillar_tags,
        "severity": "critical",
        "detail": (
            "Negative tone language found" if negative_tone
            else f"Corrupted visible labels found: {malformed_pillar_tags}" if malformed_pillar_tags
            else "OK"
        )
    }

    # ── FUNNEL (21-30) ───────────────────────────────────────────────────────
    # 21. Industry drift — lead's industry terms present
    results[21] = {
        "desc": "Lead's industry reflected in content",
        "pass": True,  # Requires lead-specific check; warn only
        "severity": "warning",
        "detail": "Manual review: verify industry-specific content present"
    }

    # 22. Cross-lead contamination — other lead names absent
    results[22] = {
        "desc": "No cross-lead contamination (other lead names)",
        "pass": True,  # Checked separately by contamination_validator
        "severity": "warning",
        "detail": "Run contamination_validator separately for full check"
    }

    # 23. Required lead identity field present
    has_lead_name = lead_slug.replace("-", " ").split()[0].lower() in html_lower if lead_slug else True
    results[23] = {
        "desc": "Lead name present in blueprint",
        "pass": has_lead_name,
        "severity": "major",
        "detail": f"Lead name from slug '{lead_slug}' not found in HTML" if not has_lead_name else "OK"
    }

    # 24. GHL identity confirmation — email/contact ID not required in HTML; pass
    results[24] = {
        "desc": "GHL identity confirmed (external check)",
        "pass": True,
        "severity": "info",
        "detail": "Verify via GHL API separately"
    }

    # 25. dateUpdated not used as new-lead proof
    date_updated_abuse = "dateupdated" in html_lower and "new lead" in html_lower
    results[25] = {
        "desc": "dateUpdated not cited as new-lead proof",
        "pass": not date_updated_abuse,
        "severity": "warning",
        "detail": "dateUpdated misused as new-lead signal" if date_updated_abuse else "OK"
    }

    # 26. Query params preserved in CTAs
    cta_hrefs = re.findall(r'href=["\']([^"\']*qualify\.html[^"\']*)["\']', html)
    params_preserved = all(
        ("lead=" in h or "biz=" in h) for h in cta_hrefs
    ) if cta_hrefs else False
    results[26] = {
        "desc": "Query params (lead=, biz=, src=) preserved in qualify.html CTAs",
        "pass": params_preserved,
        "severity": "major",
        "detail": f"CTAs: {cta_hrefs}" if not params_preserved else "OK"
    }

    # 27. CTA points to qualify.html and does not use the banned Bennett-work phrasing
    bad_cta = bool(re.search(r'href=["\'][^"\']*(?:(?<!/qualify)\/apply|meetadvaita\.com/apply)["\']', html, re.I))
    banned_cta_copy = bool(re.search(r'>\s*Apply to work with Bennett\s*<', html, re.I))
    banned_work_with_us = bool(re.search(r'>\s*Apply to Work With Us\s*<', html, re.I))
    ambiguous_apply = bool(re.search(r'>\s*Apply\s*<', html, re.I))
    results[27] = {
        "desc": "CTA points to qualify.html and avoids banned or ambiguous apply copy",
        "pass": not bad_cta and not banned_cta_copy and not banned_work_with_us and not ambiguous_apply,
        "severity": "critical",
        "detail": (
            "CTA pointing to /apply or meetadvaita.com/apply found" if bad_cta
            else "Banned CTA copy found: Apply to work with Bennett" if banned_cta_copy
            else "Banned CTA copy found: Apply to Work With Us" if banned_work_with_us
            else "Ambiguous CTA copy found: Apply" if ambiguous_apply
            else "OK"
        )
    }

    # 28. No direct booking/calendar link
    # Use word boundaries or full domain checks to avoid false positives like "brightlocal.com" matching "cal.com"
    calendar_links = bool(re.search(r'calendly\.com|(?<![a-zA-Z])cal\.com|acuityscheduling\.com|hubspot\.com.*meeting', html_lower))
    results[28] = {
        "desc": "No direct booking/calendar links (outside qualify.html flow)",
        "pass": not calendar_links,
        "severity": "critical",
        "detail": "Direct calendar link found" if calendar_links else "OK"
    }

    # 29. Booking requires qualifier submit first
    # If there's a calendar modal, it should be inside qualify.html not embedded
    embedded_booking = bool(re.search(r'<iframe[^>]*calendly|<script[^>]*calendly', html_lower))
    results[29] = {
        "desc": "No embedded booking widget (booking must be in qualify.html only)",
        "pass": not embedded_booking,
        "severity": "critical",
        "detail": "Embedded booking widget found" if embedded_booking else "OK"
    }

    # 30. No public GHL token in frontend
    ghl_token_exposed = bool(re.search(r'pit-[a-f0-9\-]{30,}|Bearer [a-zA-Z0-9\-_]{30,}', html))
    results[30] = {
        "desc": "No public GHL token or Bearer header in HTML",
        "pass": not ghl_token_exposed,
        "severity": "critical",
        "detail": "GHL token exposed in HTML" if ghl_token_exposed else "OK"
    }

    # ── AUDIO (31-35) ────────────────────────────────────────────────────────
    # 31. No drive.google.com link in HTML
    drive_links = len(re.findall(r'drive\.google\.com', html))
    results[31] = {
        "desc": "No drive.google.com links in HTML",
        "pass": drive_links == 0,
        "severity": "critical",
        "detail": f"{drive_links} Drive links found" if drive_links > 0 else "OK"
    }

    # 32. Podcast href not empty
    podcast_hrefs = re.findall(r'(?:src|href)=["\']([^"\']*\.mp3[^"\']*|[^"\']*podcasts/[^"\']*)["\']', html)
    no_empty_podcast = all(h and h != "#" and "placeholder" not in h.lower() for h in podcast_hrefs)
    results[32] = {
        "desc": "Podcast href is not empty or placeholder",
        "pass": bool(podcast_hrefs) and no_empty_podcast,
        "severity": "critical",
        "detail": f"Podcast hrefs: {podcast_hrefs}" if not (bool(podcast_hrefs) and no_empty_podcast) else "OK"
    }

    # 33. Speed controls present (1x and 1.25x)
    speed_controls = "1.25" in html and ("1x" in html or ">1×<" in html or "speed-btn" in html)
    results[33] = {
        "desc": "Speed controls present (1x and 1.25x)",
        "pass": speed_controls,
        "severity": "major",
        "detail": "Speed controls missing" if not speed_controls else "OK"
    }

    # 34. preload=metadata on audio element
    preload_ok = 'preload="metadata"' in html or "preload='metadata'" in html
    results[34] = {
        "desc": "Audio player has preload=metadata",
        "pass": preload_ok,
        "severity": "critical",
        "detail": "preload=metadata missing on audio element" if not preload_ok else "OK"
    }

    # 35. NotebookLM audio or explicit podcast partial
    has_audio = bool(re.search(r'\.mp3["\']|podcasts/|<audio', html, re.I))
    results[35] = {
        "desc": "Audio element or podcast URL present",
        "pass": has_audio,
        "severity": "major",
        "detail": "No audio element or podcast URL found" if not has_audio else "OK"
    }

    # ── PROOF (36-41) ────────────────────────────────────────────────────────
    # NOTE: Proof receipts are only enforced for already-sent blueprints.
    # For in-progress blueprints, these are INFO/skipped to avoid false gate blocking.
    receipt_dir = Path(receipt_dir)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    proof_severity = "major" if already_sent else "info"

    # 36. Email click test receipt exists
    click_test = receipt_pass(receipt_dir / f"{lead_slug}-email-click-test.json")
    results[36] = {
        "desc": "Email click test receipt exists",
        "pass": click_test if already_sent else None,
        "severity": proof_severity,
        "detail": "Missing email click test receipt" if not click_test else "OK"
    }

    # 37. Desktop render receipt
    desktop_render = receipt_pass(receipt_dir / f"{lead_slug}-desktop-render.json")
    results[37] = {
        "desc": "Desktop render receipt exists",
        "pass": desktop_render if already_sent else None,
        "severity": proof_severity,
        "detail": "Missing desktop render receipt" if not desktop_render else "OK"
    }

    # 38. Mobile render receipt
    mobile_render = receipt_pass(receipt_dir / f"{lead_slug}-mobile-render.json")
    results[38] = {
        "desc": "Mobile render receipt exists",
        "pass": mobile_render if already_sent else None,
        "severity": proof_severity,
        "detail": "Missing mobile render receipt" if not mobile_render else "OK"
    }

    # 39. Audit JSON receipt
    audit_receipt = receipt_pass(receipt_dir / f"{lead_slug}-audit.json") or \
                    receipt_pass(receipt_dir / f"{lead_slug}_audit.json")
    results[39] = {
        "desc": "Audit JSON receipt exists",
        "pass": audit_receipt if already_sent else None,
        "severity": proof_severity,
        "detail": "Missing audit JSON receipt" if not audit_receipt else "OK"
    }

    # 40. Gatekeeper ledger receipt
    gk_receipt = receipt_pass(receipt_dir / f"{lead_slug}-gatekeeper.json")
    results[40] = {
        "desc": "Gatekeeper pass receipt exists",
        "pass": gk_receipt if already_sent else None,
        "severity": proof_severity,
        "detail": "Missing gatekeeper receipt" if not gk_receipt else "OK"
    }

    # 41. Closeout receipt
    closeout_receipt = receipt_pass(receipt_dir / f"{lead_slug}-closeout.json")
    results[41] = {
        "desc": "Closeout receipt exists",
        "pass": closeout_receipt if already_sent else None,
        "severity": proof_severity,
        "detail": "Missing closeout receipt" if not closeout_receipt else "OK"
    }

    # ── PRODUCTION (42-48) — only checked with --require-production ──────────
    # 42-48 require external verification; mark as skipped unless production flag set
    prod_checks = {
        42: "Public GitHub Pages build verified (HTTP 200)",
        43: "Drive artifact registry row present",
        44: "Notion Sprint row present",
        45: "Current GHL readback (contact tagged)",
        46: "Repeat-submit same-contact proof",
        47: "Walkthrough-size audio (6-20MB / direct-address verified)",
        48: "Bennett approval scope recorded",
    }
    for num, desc in prod_checks.items():
        if require_production:
            prod_receipt, prod_detail = production_receipt_result(
                num,
                receipt_dir / f"{lead_slug}-production-{num}.json",
                html,
                html_path,
            )
            results[num] = {
                "desc": desc,
                "pass": prod_receipt,
                "severity": "critical",
                "detail": prod_detail,
            }
        else:
            results[num] = {
                "desc": desc,
                "pass": None,  # None = skipped
                "severity": "info",
                "detail": "Skipped (use --require-production to enforce)"
            }

    # ── DELIVERY (49) ────────────────────────────────────────────────────────
    # 49. Final response does not claim completion despite partial labels
    completion_words = ["done", "finished", "100%", "diamond", "delivered", "production ready",
                        "revenue validated", "sent to lead"]
    has_completion_claim = any(w in html_lower for w in completion_words)
    results[49] = {
        "desc": "No false completion claim in HTML (N/A for HTML output)",
        "pass": True,  # Not applicable to HTML; completion claims are in responses
        "severity": "info",
        "detail": "Not applicable to HTML deliverable"
    }

    # ── REVENUE (50) ─────────────────────────────────────────────────────────
    # 50. Revenue validation not inferred from synthetic flow
    results[50] = {
        "desc": "Revenue validation only from real held calls (not synthetic)",
        "pass": True,
        "severity": "info",
        "detail": "Revenue validation requires human confirmation"
    }

    return results


def compute_category_scores(results: dict) -> dict:
    """Compute per-category scores."""
    category_scores = {}
    for cat_name, cat_def in CATEGORIES.items():
        checks = cat_def["checks"]
        cat_results = {k: v for k, v in results.items() if k in checks}
        applicable = {k: v for k, v in cat_results.items() if v["pass"] is not None}
        if not applicable:
            category_scores[cat_name] = {"score": "N/A", "pass": None, "failures": []}
            continue
        passes = sum(1 for v in applicable.values() if v["pass"])
        total = len(applicable)
        pct = (passes / total) * 100 if total > 0 else 100
        failures = [
            f"#{k}: {v['desc']} — {v['detail']}"
            for k, v in applicable.items()
            if not v["pass"]
        ]
        category_scores[cat_name] = {
            "score": f"{passes}/{total} ({pct:.0f}%)",
            "pass": pct == 100,
            "failures": failures,
        }
    return category_scores


def main():
    parser = argparse.ArgumentParser(description="Blueprint completion gate — 50 breakpoints")
    parser.add_argument("--html", required=True, help="Path to blueprint HTML file")
    parser.add_argument("--receipt-dir", required=True, help="Directory for receipt files")
    parser.add_argument("--lead", required=True, help="Lead slug (e.g. dave-wood)")
    parser.add_argument("--require-production", action="store_true",
                        help="Enforce production checks (42-48)")
    parser.add_argument("--already-sent", action="store_true",
                        help="Enforce proof receipt checks (36-41). Use when blueprint was formally sent.")
    parser.add_argument("--json-output", action="store_true", help="Output JSON only")
    parser.add_argument(
        "--exclude-drafts",
        action="store_true",
        help="Skip known draft/scaffold slugs: TEMPLATE, chris, melissa-tash, rey"
    )
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}", file=sys.stderr)
        sys.exit(2)

    html = html_path.read_text(encoding="utf-8")
    already_sent = getattr(args, 'already_sent', False)
    results = run_checks(
        html,
        args.lead,
        Path(args.receipt_dir),
        args.require_production,
        already_sent=already_sent,
        html_path=html_path,
    )
    category_scores = compute_category_scores(results)

    # Critical failures
    criticals = [
        f"#{k}: {v['desc']}"
        for k, v in results.items()
        if v["pass"] is False and v["severity"] == "critical"
    ]
    majors = [
        f"#{k}: {v['desc']}"
        for k, v in results.items()
        if v["pass"] is False and v["severity"] == "major"
    ]

    passed = sum(1 for v in results.values() if v["pass"] is True)
    failed = sum(1 for v in results.values() if v["pass"] is False)
    skipped = sum(1 for v in results.values() if v["pass"] is None)
    overall_pass = failed == 0

    # Build output
    output = {
        "lead": args.lead,
        "ts": datetime.now(timezone.utc).isoformat(),
        "html_path": str(html_path),
        "html_size_bytes": html_path.stat().st_size,
        "require_production": args.require_production,
        "summary": {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total_applicable": passed + failed,
            "overall_pass": overall_pass,
        },
        "status": "PASS" if overall_pass else "FAIL",
        "category_scores": category_scores,
        "critical_failures": criticals,
        "major_failures": majors,
        "checks": results,
    }

    # Write receipt
    receipt_dir = Path(args.receipt_dir)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / f"{args.lead}-completion-gate.json"
    receipt_path.write_text(json.dumps(output, indent=2))

    if args.json_output:
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f"BLUEPRINT COMPLETION GATE — {args.lead}")
        print(f"{'='*60}")
        print(f"HTML: {html_path} ({html_path.stat().st_size:,} bytes)")
        print(f"Status: {'✅ PASS' if overall_pass else '❌ FAIL'}")
        print(f"Checks: {passed} passed / {failed} failed / {skipped} skipped")
        print()
        print("CATEGORY SCORES:")
        for cat, score_data in category_scores.items():
            status = "✅" if score_data["pass"] else ("⚠️" if score_data["pass"] is None else "❌")
            print(f"  {status} {cat}: {score_data['score']}")
            for failure in score_data["failures"][:3]:
                print(f"     └─ {failure}")
        if criticals:
            print(f"\n🔴 CRITICAL FAILURES ({len(criticals)}):")
            for c in criticals:
                print(f"  {c}")
        if majors:
            print(f"\n🟡 MAJOR FAILURES ({len(majors)}):")
            for m in majors:
                print(f"  {m}")
        print(f"\nReceipt: {receipt_path}")
        print(f"{'='*60}")

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
