#!/usr/bin/env python3
"""Blueprint Gatekeeper 100.

Repo-local hard gate for Blueprint AI deliverables. It is intentionally stricter
than the historical pre-commit hooks: a production token is written only when
local audits, proof receipts, production receipts, visual text checks, and the
strict completion gate all pass.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote, urlparse


REPO = Path(__file__).resolve().parents[1]
# Production audio is duration-first. The Blueprint short-podcast standard is
# 8-12 minutes, with bytes kept only as a bitrate/corruption sanity check.
MIN_PRODUCTION_AUDIO_BYTES = 6 * 1024 * 1024
MAX_PRODUCTION_AUDIO_BYTES = 20 * 1024 * 1024
MIN_PRODUCTION_AUDIO_SECONDS = 8 * 60
MAX_PRODUCTION_AUDIO_SECONDS = 12 * 60
TARGET_PRODUCTION_AUDIO_MINUTES = 10


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def optional_artifact_hash(path: Path) -> str:
    return file_sha256(path) if path.exists() else ""


def default_delivery_email_path(lead: str) -> Path:
    return REPO / "delivery-emails" / f"{lead}-delivery-email.html"


def default_lead_profile_path(lead: str) -> Path:
    return REPO / "leads" / f"{lead}.json"


def receipt_pass(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        data = load_json(path)
    except Exception:
        return False
    token = data.get("pass_token")
    if isinstance(token, dict) and token.get("pass") is True:
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



def find_ghl_raw_for_source_fidelity(lead: str, receipt_dir: Path) -> Optional[Path]:
    candidates = []
    for root in [receipt_dir, REPO / "audit-receipts" / lead]:
        if root.exists():
            candidates.extend(root.glob("**/*ghl*raw*.json"))
            candidates.extend(root.glob("**/ghl-contact-by-id.raw.json"))
            candidates.extend(root.glob("**/*contact*raw*.json"))
    unique = sorted({c.resolve() for c in candidates if c.exists()}, key=lambda x: x.stat().st_mtime, reverse=True)
    return unique[0] if unique else None


def source_fidelity_cmd(lead: str, html_path: Path, profile_path: Path, receipt_dir: Path) -> List[str]:
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "blueprint_source_fidelity_gate.py"),
        "--lead-json",
        str(profile_path),
        "--html",
        str(html_path),
        "--json-output",
    ]
    raw = find_ghl_raw_for_source_fidelity(lead, receipt_dir)
    if raw:
        cmd.extend(["--ghl-raw", str(raw)])
    return cmd

def run_cmd(name: str, cmd: List[str], cwd: Path = REPO, timeout: int = 180) -> Dict[str, Any]:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
    return {
        "name": name,
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout.strip().splitlines()[-20:],
        "stderr_tail": proc.stderr.strip().splitlines()[-20:],
        "pass": proc.returncode == 0,
    }


def resolve_html(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = REPO / path
    return path.resolve()


def html_surface_gates(html: str) -> Tuple[bool, List[str]]:
    failures = []
    checks = [
        (r'>\s*Apply to work with Bennett\s*<', "banned CTA copy: Apply to work with Bennett"),
        (r'>\s*Apply to Work With Us\s*<', "banned CTA copy: Apply to Work With Us"),
        (r'>\s*Apply\s*<', "ambiguous CTA copy: Apply"),
        (r'>\s*Command Center\s*<', "deprecated Command Center content"),
        (r'\.tab-nav\b', "revoked old tab navigation CSS"),
        (r'\.tab-panel\b', "revoked old tab panel CSS"),
        (r'\bswitchTab\s*\(', "revoked old tab JavaScript"),
        (r"Playfair\s+Display", "revoked old display font"),
        (r"format-4-light-clean-scroll|format-5-purple-creative", "revoked alternate blueprint format reference"),
        (r'<span[^>]*class=["\'][^"\']*(?:pillar-tag|agent-tag|tag)[^"\']*["\'][^>]*>\s*\$out\s*</span>', "corrupt visible badge: $out"),
        (r'<span[^>]*class=["\'][^"\']*(?:pillar-tag|agent-tag|tag)[^"\']*["\'][^>]*>\s*\$in\s*</span>', "corrupt visible badge: $in"),
        (r'<span[^>]*class=["\'][^"\']*(?:pillar-tag|agent-tag|tag)[^"\']*["\'][^>]*>\s*T\s*</span>', "corrupt visible badge: T"),
        (r'drive\.google\.com', "customer-facing Drive URL"),
        (r'notion\.so/', "customer-facing Notion URL"),
        (r'\{\{[A-Za-z_]+\}\}', "unresolved template token"),
    ]
    for pattern, label in checks:
        if re.search(pattern, html, re.I):
            failures.append(label)
    return not failures, failures


def referenced_audio_paths(html: str, html_path: Path) -> List[Path]:
    refs = re.findall(r'(?:src|href)=["\']([^"\']*podcasts/[^"\']+\.mp3[^"\']*)["\']', html, re.I)
    roots = [html_path.parent.parent, REPO]
    paths = []
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
            if candidate not in paths:
                paths.append(candidate)
    return paths


def audio_size_gate(html: str, html_path: Path) -> Tuple[bool, str]:
    paths = referenced_audio_paths(html, html_path)
    if not paths:
        return False, "no referenced MP3"
    details = []
    in_window = None
    over_ceiling = None
    bad_duration = None
    for path in paths:
        if path.exists():
            size = path.stat().st_size
            duration = audio_duration_seconds(path)
            details.append(f"{path.name}={int(duration)}s/{size}")
            if (
                MIN_PRODUCTION_AUDIO_BYTES <= size <= MAX_PRODUCTION_AUDIO_BYTES
                and MIN_PRODUCTION_AUDIO_SECONDS <= duration <= MAX_PRODUCTION_AUDIO_SECONDS
            ):
                in_window = (path, duration, size)
            elif size > MAX_PRODUCTION_AUDIO_BYTES:
                over_ceiling = (path, size)
            elif duration and not (MIN_PRODUCTION_AUDIO_SECONDS <= duration <= MAX_PRODUCTION_AUDIO_SECONDS):
                bad_duration = (path, duration)
    if in_window:
        return True, f"{in_window[0].name} {int(in_window[1])}s / {in_window[2]} bytes within Blueprint 10-minute window"
    if bad_duration:
        return False, (
            f"{bad_duration[0].name} duration {bad_duration[1]:.0f}s outside "
            f"{MIN_PRODUCTION_AUDIO_SECONDS}-{MAX_PRODUCTION_AUDIO_SECONDS}s Blueprint window"
        )
    if over_ceiling:
        return False, (
            f"{over_ceiling[0].name} {over_ceiling[1]} bytes exceeds walkthrough ceiling "
            f"{MAX_PRODUCTION_AUDIO_BYTES} (byte sanity ceiling)"
        )
    return False, "all referenced MP3 files below production floor or missing: " + ", ".join(details)


def audio_duration_seconds(path: Path) -> float:
    try:
        raw = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path)
        ], text=True, timeout=30).strip()
        return float(raw)
    except Exception:
        return 0.0


def audio_direct_address_gate(receipt_dir: Path, lead: str) -> Tuple[bool, str]:
    path = receipt_dir / f"{lead}-production-47.json"
    if not path.exists():
        return False, f"missing podcast production receipt: {path.name}"
    try:
        data = load_json(path)
    except Exception as exc:
        return False, f"invalid podcast production receipt: {exc}"
    expected_sha = data.get("audio_sha256")
    audio_path = data.get("audio")
    duration_seconds = float(data.get("duration_seconds") or data.get("duration") or 0)
    hash_ok = False
    if expected_sha and audio_path:
        path = Path(audio_path)
        candidates = [path] if path.is_absolute() else [(REPO / path).resolve(), (Path.cwd() / path).resolve()]
        hash_ok = any(candidate.exists() and file_sha256(candidate) == expected_sha for candidate in candidates)
    ok = (
        data.get("direct_address_audio_verified") is True
        and data.get("opening_direct_address_verified") is True
        and data.get("opening_exact_or_close") is True
        and data.get("banned_audio_phrases_found") in ([], None)
        and data.get("third_person_patterns_found") in ([], None)
        and int(data.get("you_your_count") or 0) >= 5
        and MIN_PRODUCTION_AUDIO_SECONDS <= duration_seconds <= MAX_PRODUCTION_AUDIO_SECONDS
        and hash_ok
    )
    if ok:
        return True, "direct-address audio receipt passed"
    return False, (
        "podcast audio content failed or missing: direct opening, direct_address_audio_verified=true, "
        "no source-material/third-person phrases, >=5 you/your references, duration_seconds 480-720, "
        "and matching audio_sha256 required"
    )


def audio_notebooklm_origin_gate(receipt_dir: Path, lead: str) -> Tuple[bool, str]:
    """Require NotebookLM-origin proof for production Blueprint podcasts.

    A local TTS fallback can pass duration/hash/direct-address checks while still
    sounding unacceptable and bypassing the Blueprint podcast SOP. Production
    Gatekeeper must fail closed unless the receipt proves NotebookLM generation
    or an equivalent NotebookLM artifact/notebook/source id.
    """
    path = receipt_dir / f"{lead}-production-47.json"
    if not path.exists():
        return False, f"missing podcast production receipt: {path.name}"
    try:
        data = load_json(path)
    except Exception as exc:
        return False, f"invalid podcast production receipt: {exc}"
    fallback = str(data.get("local_tts_fallback") or data.get("tts_fallback") or "").strip()
    if fallback:
        return False, f"local TTS fallback present ({fallback}); NotebookLM origin required"
    status = str(data.get("notebooklm_status") or data.get("audio_status") or "").upper()
    if any(token in status for token in ("PARTIAL", "AUTH", "EXPIRED", "FAIL", "BLOCK", "FALLBACK")):
        return False, f"NotebookLM status is not acceptable: {status or 'missing'}"
    origin = str(data.get("generator") or data.get("audio_generator") or data.get("origin") or "").lower()
    artifact_fields = (
        data.get("notebooklm_artifact_id"),
        data.get("artifact_id"),
        data.get("notebook_id"),
        data.get("notebooklm_notebook_id"),
        data.get("source_id"),
        data.get("notebooklm_source_id"),
    )
    if (
        data.get("notebooklm_generated") is True
        or data.get("notebooklm_origin_verified") is True
        or origin in {"notebooklm", "notebooklm-mcp", "notebooklm-cli"}
        or any(bool(value) for value in artifact_fields)
    ):
        return True, "NotebookLM origin verified"
    return False, "missing NotebookLM origin proof (artifact/notebook/source id or explicit notebooklm_generated=true)"


def validate_token(token_path: Path, lead: str, require_production: bool,
                   html_path: Path = None, delivery_email_path: Path = None,
                   lead_profile_path: Path = None, receipt_dir: Path = None) -> Tuple[bool, List[str]]:
    failures = []
    if not token_path.exists():
        return False, [f"missing token: {token_path}"]
    try:
        data = load_json(token_path)
    except Exception as exc:
        return False, [f"invalid token json: {exc}"]
    token = data.get("pass_token", data)
    if token.get("pass") is not True:
        failures.append("token pass is not true")
    if token.get("lead") != lead:
        failures.append(f"token lead mismatch: {token.get('lead')} != {lead}")
    if int(token.get("score") or 0) != 100:
        failures.append("token score is not 100")
    if str(token.get("diamond") or "").upper() != "PASS":
        failures.append("token diamond is not PASS")
    if require_production and token.get("strict_production") is not True:
        failures.append("token is not a strict production token")
    artifact_hashes = token.get("artifact_hashes")
    if html_path or delivery_email_path or lead_profile_path:
        if not isinstance(artifact_hashes, dict):
            failures.append("token missing artifact_hashes")
        else:
            comparisons = [
                ("blueprint_html_sha256", html_path),
                ("delivery_email_sha256", delivery_email_path),
                ("lead_profile_sha256", lead_profile_path),
            ]
            if receipt_dir is not None:
                comparisons.append((
                    "podcast_production_47_sha256",
                    receipt_dir / f"{lead}-production-47.json",
                ))
            for key, path in comparisons:
                if path is None:
                    continue
                if not path.exists():
                    failures.append(f"artifact missing for hash verification: {path}")
                    continue
                expected = artifact_hashes.get(key)
                actual = file_sha256(path)
                if not expected:
                    failures.append(f"token missing {key}")
                elif expected != actual:
                    failures.append(f"token {key} mismatch")
    return not failures, failures


def external_send_approved(receipt_dir: Path, lead: str) -> bool:
    approval_path = receipt_dir / f"{lead}-production-48.json"
    if not approval_path.exists():
        return False
    try:
        data = load_json(approval_path)
    except Exception:
        return False
    return data.get("external_customer_send_approved") is True or data.get("bennett_approved") is True


def main() -> int:
    parser = argparse.ArgumentParser(description="Blueprint Gatekeeper 100")
    parser.add_argument("--html", help="Blueprint HTML path")
    parser.add_argument("--lead", required=True, help="Lead slug")
    parser.add_argument("--receipt-dir", default="audit-receipts", help="Receipt directory")
    parser.add_argument("--mode", choices=["local", "production"], default="local")
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument("--verify-token", action="store_true", help="Only verify a pass token")
    parser.add_argument("--token", help="Gatekeeper pass-token JSON path")
    parser.add_argument("--delivery-email", help="Delivery email artifact to bind/verify")
    parser.add_argument("--profile", help="Lead profile JSON artifact to bind/verify")
    args = parser.parse_args()

    receipt_dir = Path(args.receipt_dir)
    if not receipt_dir.is_absolute():
        receipt_dir = (REPO / receipt_dir).resolve()

    if args.verify_token:
        if not args.token:
            print("ERROR: --token is required with --verify-token", file=sys.stderr)
            return 2
        verify_html = resolve_html(args.html) if args.html else None
        verify_delivery = resolve_html(args.delivery_email) if args.delivery_email else None
        verify_profile = resolve_html(args.profile) if args.profile else None
        ok, failures = validate_token(
            Path(args.token).resolve(),
            args.lead,
            args.mode == "production",
            verify_html,
            verify_delivery,
            verify_profile,
            receipt_dir,
        )
        out = {"status": "PASS" if ok else "FAIL", "lead": args.lead, "failures": failures}
        print(json.dumps(out, indent=2) if args.json_output else out["status"])
        return 0 if ok else 1

    if not args.html:
        print("ERROR: --html is required", file=sys.stderr)
        return 2

    html_path = resolve_html(args.html)
    if not html_path.exists():
        print(f"ERROR: HTML not found: {html_path}", file=sys.stderr)
        return 2
    html = html_path.read_text(encoding="utf-8", errors="replace")

    checks: List[Dict[str, Any]] = []
    failures: List[str] = []

    visible_ok, visible_failures = html_surface_gates(html)
    checks.append({"name": "visible_html_surface", "pass": visible_ok, "failures": visible_failures})
    failures.extend([f"visible_html_surface: {item}" for item in visible_failures])

    completion_cmd = [
        sys.executable,
        str(REPO / "scripts" / "blueprint_completion_gate.py"),
        "--html",
        str(html_path),
        "--receipt-dir",
        str(receipt_dir),
        "--lead",
        args.lead,
        "--json-output",
    ]
    if args.mode == "production":
        completion_cmd.append("--require-production")
    completion = run_cmd("completion_gate", completion_cmd)
    checks.append(completion)
    if not completion["pass"]:
        failures.append("completion_gate failed")

    profile_for_agent_gate = Path(args.profile) if args.profile else default_lead_profile_path(args.lead)
    if not profile_for_agent_gate.is_absolute():
        profile_for_agent_gate = REPO / profile_for_agent_gate

    source_fidelity = run_cmd("source_fidelity_gate", source_fidelity_cmd(args.lead, html_path, profile_for_agent_gate, receipt_dir), timeout=90)
    checks.append(source_fidelity)
    if not source_fidelity["pass"]:
        failures.append("source-fidelity gate failed")
    agent_prompt_cmd = [
        sys.executable,
        str(REPO / "scripts" / "blueprint_agent_prompt_quality_gate.py"),
        "--html",
        str(html_path),
        "--receipt",
        str(receipt_dir / f"{args.lead}-agent-prompt-quality.json"),
        "--json-output",
    ]
    if profile_for_agent_gate.exists():
        agent_prompt_cmd.extend(["--profile", str(profile_for_agent_gate)])
    agent_prompt_quality = run_cmd("agent_prompt_quality_gate", agent_prompt_cmd, timeout=90)
    checks.append(agent_prompt_quality)
    if not agent_prompt_quality["pass"]:
        failures.append("agent prompt quality gate failed")

    qualify_link = run_cmd(
        "qualify_link_gate",
        [sys.executable, str(REPO / "scripts" / "blueprint_qualify_link_gate.py"), "--html", str(html_path), "--check-http", "--json-output"],
        timeout=90,
    )
    checks.append(qualify_link)
    if not qualify_link["pass"]:
        failures.append("qualify link gate failed")

    qualifier_context_cmd = [
        sys.executable,
        str(REPO / "scripts" / "blueprint_qualifier_context_gate.py"),
        "--html",
        str(html_path),
        "--lead",
        args.lead,
        "--json-output",
    ]
    delivery_email_for_context = Path(args.delivery_email) if args.delivery_email else default_delivery_email_path(args.lead)
    if not delivery_email_for_context.is_absolute():
        delivery_email_for_context = REPO / delivery_email_for_context
    profile_for_context = Path(args.profile) if args.profile else default_lead_profile_path(args.lead)
    if not profile_for_context.is_absolute():
        profile_for_context = REPO / profile_for_context
    if delivery_email_for_context.exists():
        qualifier_context_cmd.extend(["--delivery-email", str(delivery_email_for_context)])
    if profile_for_context.exists():
        qualifier_context_cmd.extend(["--profile", str(profile_for_context)])
    qualifier_context = run_cmd("qualifier_context_gate", qualifier_context_cmd, timeout=90)
    checks.append(qualifier_context)
    if not qualifier_context["pass"]:
        failures.append("qualifier context gate failed")

    if delivery_email_for_context.exists():
        approval_email = run_cmd(
            "approval_email_customer_view_gate",
            [sys.executable, str(REPO / "scripts" / "blueprint_approval_email_gate.py"), "--email", str(delivery_email_for_context), "--profile", str(profile_for_context), "--json-output"],
            timeout=90,
        )
        checks.append(approval_email)
        if not approval_email["pass"]:
            failures.append("approval email customer-view gate failed")
        email_visual = run_cmd(
            "email_visual_format_gate",
            [sys.executable, str(REPO / "scripts" / "blueprint_email_visual_gate.py"), "--email", str(delivery_email_for_context), "--subject", f"CUSTOMER VIEW PREVIEW: {args.lead} - Your Custom Blueprint is Ready", "--json-output"],
            timeout=90,
        )
        checks.append(email_visual)
        if not email_visual["pass"]:
            failures.append("email visual format gate failed")

    audit = run_cmd("blueprint_audit", [sys.executable, str(REPO / "run-audit.py"), "--lead", args.lead])
    checks.append(audit)
    if not audit["pass"]:
        failures.append("run-audit.py failed")

    financial = run_cmd("financial_realism", [sys.executable, str(REPO / "financial-realism-check.py"), "--file", str(html_path)])
    checks.append(financial)
    if not financial["pass"]:
        failures.append("financial-realism-check.py failed")

    d9_path = Path.home() / ".claude" / "skills" / "blueprint-ai-audit-skill" / "d9-audit.py"
    if d9_path.exists():
        d9 = run_cmd("d9_render_integrity", [sys.executable, str(d9_path), str(html_path)])
    else:
        d9 = {"name": "d9_render_integrity", "pass": False, "returncode": 127, "stdout_tail": [], "stderr_tail": [f"missing {d9_path}"]}
    checks.append(d9)
    if not d9["pass"]:
        failures.append("D9 render-integrity audit failed or missing")

    if args.mode == "production":
        proof_receipts = {
            "email_click_test": receipt_dir / f"{args.lead}-email-click-test.json",
            "desktop_render": receipt_dir / f"{args.lead}-desktop-render.json",
            "mobile_render": receipt_dir / f"{args.lead}-mobile-render.json",
            "audit_json": receipt_dir / f"{args.lead}-audit.json",
            "closeout": receipt_dir / f"{args.lead}-closeout.json",
        }
        for name, path in proof_receipts.items():
            ok = receipt_pass(path)
            checks.append({"name": f"proof_{name}", "path": str(path), "pass": ok})
            if not ok:
                failures.append(f"proof receipt missing or failing: {path.name}")

        audio_ok, audio_detail = audio_size_gate(html, html_path)
        checks.append({"name": "production_audio_size", "pass": audio_ok, "detail": audio_detail})
        if not audio_ok:
            failures.append(f"production audio size failed: {audio_detail}")

        audio_direct_ok, audio_direct_detail = audio_direct_address_gate(receipt_dir, args.lead)
        checks.append({"name": "production_audio_direct_address", "pass": audio_direct_ok, "detail": audio_direct_detail})
        if not audio_direct_ok:
            failures.append(f"production audio direct-address failed: {audio_direct_detail}")

        audio_notebooklm_ok, audio_notebooklm_detail = audio_notebooklm_origin_gate(receipt_dir, args.lead)
        checks.append({"name": "production_audio_notebooklm_origin", "pass": audio_notebooklm_ok, "detail": audio_notebooklm_detail})
        if not audio_notebooklm_ok:
            failures.append(f"production audio NotebookLM origin failed: {audio_notebooklm_detail}")

    pass_now = not failures
    token_path = receipt_dir / f"{args.lead}-gatekeeper-pass-token.json"
    gatekeeper_receipt = receipt_dir / f"{args.lead}-gatekeeper.json"

    output: Dict[str, Any] = {
        "status": "PASS" if pass_now else "FAIL",
        "lead": args.lead,
        "mode": args.mode,
        "ts": utc_now(),
        "html_path": str(html_path),
        "receipt_dir": str(receipt_dir),
        "score": 100 if pass_now else 0,
        "diamond": "PASS" if pass_now else "FAIL",
        "checks": checks,
        "failures": failures,
    }

    if pass_now and args.mode == "production":
        allowed_actions = ["internal_preview", "bennett_preview"]
        if external_send_approved(receipt_dir, args.lead):
            allowed_actions.append("external_send")
        delivery_email = resolve_html(args.delivery_email) if args.delivery_email else default_delivery_email_path(args.lead)
        lead_profile = resolve_html(args.profile) if args.profile else default_lead_profile_path(args.lead)
        output["pass_token"] = {
            "pass": True,
            "lead": args.lead,
            "score": 100,
            "diamond": "PASS",
            "strict_production": True,
            "approval_state": "external_send_approved" if "external_send" in allowed_actions else "bennett_preview_only",
            "generated_at": utc_now(),
            "html_path": str(html_path),
            "receipt_dir": str(receipt_dir),
            "allowed_actions": allowed_actions,
            "artifact_hashes": {
                "blueprint_html_sha256": file_sha256(html_path),
                "delivery_email_sha256": optional_artifact_hash(delivery_email),
                "lead_profile_sha256": optional_artifact_hash(lead_profile),
                "podcast_production_47_sha256": optional_artifact_hash(receipt_dir / f"{args.lead}-production-47.json"),
            },
            "artifact_paths": {
                "blueprint_html": str(html_path),
                "delivery_email": str(delivery_email),
                "lead_profile": str(lead_profile),
            },
        }
        write_json(gatekeeper_receipt, output)

        strict_cmd = completion_cmd + ["--already-sent"]
        strict = run_cmd("strict_completion_gate_with_gatekeeper_receipt", strict_cmd)
        output["checks"].append(strict)
        if strict["pass"]:
            write_json(gatekeeper_receipt, output)
            write_json(token_path, output)
            output["token_path"] = str(token_path)
        else:
            output["status"] = "FAIL"
            output["score"] = 0
            output["diamond"] = "FAIL"
            output["failures"].append("strict completion gate failed after gatekeeper receipt")
            if gatekeeper_receipt.exists():
                gatekeeper_receipt.unlink()
            if token_path.exists():
                token_path.unlink()
            write_json(receipt_dir / f"{args.lead}-gatekeeper-fail.json", output)
            pass_now = False
    elif pass_now:
        write_json(receipt_dir / f"{args.lead}-gatekeeper-local.json", output)
    else:
        if token_path.exists():
            token_path.unlink()
        if gatekeeper_receipt.exists():
            gatekeeper_receipt.unlink()
        write_json(receipt_dir / f"{args.lead}-gatekeeper-fail.json", output)

    if args.json_output:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"Blueprint Gatekeeper 100: {output['status']} ({args.lead}, {args.mode})")
        for failure in output["failures"][:20]:
            print(f"- {failure}")
        if output.get("token_path"):
            print(f"Token: {output['token_path']}")

    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
