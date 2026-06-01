#!/usr/bin/env python3
"""Blueprint Gatekeeper 100.

Repo-local hard gate for Blueprint AI deliverables. It is intentionally stricter
than the historical pre-commit hooks: a production token is written only when
local audits, proof receipts, production receipts, visual text checks, and the
strict completion gate all pass.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import unquote, urlparse


REPO = Path(__file__).resolve().parents[1]
MIN_PRODUCTION_AUDIO_BYTES = 29 * 1024 * 1024


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
    for path in paths:
        if path.exists():
            size = path.stat().st_size
            details.append(f"{path.name}={size}")
            if size >= MIN_PRODUCTION_AUDIO_BYTES:
                return True, f"{path.name} {size} bytes"
    return False, "all referenced MP3 files below production floor or missing: " + ", ".join(details)


def validate_token(token_path: Path, lead: str, require_production: bool) -> Tuple[bool, List[str]]:
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
    return not failures, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Blueprint Gatekeeper 100")
    parser.add_argument("--html", help="Blueprint HTML path")
    parser.add_argument("--lead", required=True, help="Lead slug")
    parser.add_argument("--receipt-dir", default="audit-receipts", help="Receipt directory")
    parser.add_argument("--mode", choices=["local", "production"], default="local")
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument("--verify-token", action="store_true", help="Only verify a pass token")
    parser.add_argument("--token", help="Gatekeeper pass-token JSON path")
    args = parser.parse_args()

    receipt_dir = Path(args.receipt_dir)
    if not receipt_dir.is_absolute():
        receipt_dir = (REPO / receipt_dir).resolve()

    if args.verify_token:
        if not args.token:
            print("ERROR: --token is required with --verify-token", file=sys.stderr)
            return 2
        ok, failures = validate_token(Path(args.token).resolve(), args.lead, args.mode == "production")
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
        output["pass_token"] = {
            "pass": True,
            "lead": args.lead,
            "score": 100,
            "diamond": "PASS",
            "strict_production": True,
            "generated_at": utc_now(),
            "html_path": str(html_path),
            "receipt_dir": str(receipt_dir),
            "allowed_actions": ["internal_preview", "bennett_preview", "external_send"],
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
