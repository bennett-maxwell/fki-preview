#!/usr/bin/env python3
"""Summarize Blueprint AI production readiness from proof receipts.

This script exists to prevent the repeated failure mode where a local audit is
treated as a production send approval. It reports local proof separately from
strict production readiness and keeps no-send true until every required receipt
is positive.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def bool_pass(data: Dict[str, Any]) -> bool:
    if not data:
        return False
    token = data.get("pass_token")
    if isinstance(token, dict) and token.get("pass") is True:
        return True
    if data.get("pass") is True or data.get("ok") is True or data.get("verified") is True:
        return True
    if data.get("overall_pass") is True:
        return True
    summary = data.get("summary")
    if isinstance(summary, dict) and summary.get("overall_pass") is True:
        return True
    status = str(data.get("status") or data.get("verdict") or "").strip().upper()
    return status in {"PASS", "PASSED", "OK", "SUCCESS", "GREEN", "DIAMOND_PASS"}


def receipt_detail(data: Dict[str, Any]) -> str:
    if not data:
        return "missing or invalid receipt"
    blocker = data.get("blocker")
    if isinstance(blocker, str) and blocker.strip():
        return blocker.strip()
    failures = data.get("failures")
    if isinstance(failures, list) and failures:
        return "; ".join(str(item) for item in failures[:6])
    critical = data.get("critical_failures")
    if isinstance(critical, list) and critical:
        return "; ".join(str(item) for item in critical[:6])
    return str(data.get("status") or data.get("verdict") or "receipt did not prove pass")


def receipt_status(path: Path) -> Dict[str, Any]:
    data = load_json(path)
    passed = bool_pass(data)
    return {
        "path": str(path.relative_to(REPO)) if path.exists() else str(path),
        "exists": path.exists(),
        "pass": passed,
        "status": data.get("status") if data else "MISSING",
        "detail": "PASS" if passed else receipt_detail(data),
    }


def completion_gate_status(path: Path) -> Dict[str, Any]:
    data = load_json(path)
    status = receipt_status(path)
    status["summary"] = data.get("summary", {})
    status["require_production"] = data.get("require_production")
    if data and data.get("require_production") is not True:
        status["pass"] = False
        status["detail"] = "strict completion gate receipt must have require_production=true"
    production = {}
    scores = data.get("category_scores")
    if isinstance(scores, dict):
        production = scores.get("Production") or {}
    failures = []
    if isinstance(production, dict):
        failures.extend(production.get("failures") or [])
    failures.extend(data.get("critical_failures") or [])
    status["production_failures"] = sorted(set(str(item) for item in failures))
    return status


def gatekeeper_status(path: Path) -> Dict[str, Any]:
    data = load_json(path)
    status = receipt_status(path)
    status["diamond"] = data.get("diamond")
    status["score"] = data.get("score")
    status["failures"] = data.get("failures") or []
    return status


def require_schema(label: str, path: Path, validator) -> Tuple[Dict[str, Any], List[str]]:
    data = load_json(path)
    status = receipt_status(path)
    failures = validator(data)
    if failures:
        status["pass"] = False
        status["detail"] = "; ".join(failures)
    return status, [f"{label}: {failure}" for failure in failures]


def validate_drive_registry(data: Dict[str, Any]) -> List[str]:
    failures = []
    if not bool_pass(data):
        failures.append("Drive artifact registry receipt is not PASS")
    if not data.get("registry_file"):
        failures.append("registry_file is missing")
    if data.get("verified") is not True:
        failures.append("verified=true is missing")
    return failures


def validate_ghl_readback(data: Dict[str, Any]) -> List[str]:
    contact = data.get("contact") if isinstance(data.get("contact"), dict) else {}
    conversation = data.get("conversation") if isinstance(data.get("conversation"), dict) else {}
    failures = []
    if not bool_pass(data):
        failures.append("HighLevel readback receipt is not PASS")
    if int(data.get("exact_contact_count") or 0) != 1:
        failures.append("exact_contact_count=1 is missing")
    if not contact.get("id"):
        failures.append("contact.id is missing")
    if not conversation.get("id"):
        failures.append("conversation.id is missing")
    if data.get("instant_response_verified") is not True:
        failures.append("instant_response_verified=true is missing")
    return failures


def validate_repeat_submit(data: Dict[str, Any]) -> List[str]:
    failures = []
    if not bool_pass(data):
        failures.append("repeat-submit receipt is not PASS")
    if int(data.get("relay_http_status") or 0) != 200:
        failures.append("relay_http_status=200 is missing")
    if data.get("relay_mode") not in {"updated", "matched"}:
        failures.append("relay_mode must be updated or matched")
    if not data.get("returned_contact_id"):
        failures.append("returned_contact_id is missing")
    if data.get("returned_contact_id") != data.get("expected_contact_id"):
        failures.append("returned_contact_id does not match expected_contact_id")
    if int(data.get("exact_contact_count_after_repeat") or 0) != 1:
        failures.append("exact_contact_count_after_repeat=1 is missing")
    return failures


def add_blocker(blockers: List[Dict[str, str]], key: str, status: Dict[str, Any]) -> None:
    if status.get("pass") is True:
        return
    blockers.append({
        "key": key,
        "receipt": status.get("path", ""),
        "detail": status.get("detail", "missing proof"),
    })


def build_summary(lead: str, receipt_dir: Path) -> Dict[str, Any]:
    receipt_dir = receipt_dir.resolve()
    paths = {
        "completion_gate": receipt_dir / f"{lead}-completion-gate.json",
        "gatekeeper_production": receipt_dir / f"{lead}-gatekeeper-production-output.json",
        "public_http": receipt_dir / f"{lead}-public-http.json",
        "email_click_test": receipt_dir / f"{lead}-email-click-test.json",
        "desktop_render": receipt_dir / f"{lead}-desktop-render.json",
        "mobile_render": receipt_dir / f"{lead}-mobile-render.json",
        "audit": receipt_dir / f"{lead}-audit.json",
        "closeout": receipt_dir / f"{lead}-closeout.json",
        "production_43": receipt_dir / f"{lead}-production-43.json",
        "production_45": receipt_dir / f"{lead}-production-45.json",
        "production_46": receipt_dir / f"{lead}-production-46.json",
        "production_47": receipt_dir / f"{lead}-production-47.json",
        "production_48": receipt_dir / f"{lead}-production-48.json",
    }

    receipts: Dict[str, Any] = {
        "completion_gate": completion_gate_status(paths["completion_gate"]),
        "gatekeeper_production": gatekeeper_status(paths["gatekeeper_production"]),
        "public_http": receipt_status(paths["public_http"]),
        "email_click_test": receipt_status(paths["email_click_test"]),
        "desktop_render": receipt_status(paths["desktop_render"]),
        "mobile_render": receipt_status(paths["mobile_render"]),
        "audit": receipt_status(paths["audit"]),
        "closeout": receipt_status(paths["closeout"]),
        "production_47_podcast": receipt_status(paths["production_47"]),
        "production_48_approval_scope": receipt_status(paths["production_48"]),
    }

    production_43, schema_43 = require_schema("production_43_drive_registry", paths["production_43"], validate_drive_registry)
    production_45, schema_45 = require_schema("production_45_ghl_readback", paths["production_45"], validate_ghl_readback)
    production_46, schema_46 = require_schema("production_46_repeat_submit", paths["production_46"], validate_repeat_submit)
    receipts["production_43_drive_registry"] = production_43
    receipts["production_45_ghl_readback"] = production_45
    receipts["production_46_repeat_submit"] = production_46

    blockers: List[Dict[str, str]] = []
    for key in [
        "completion_gate",
        "gatekeeper_production",
        "mobile_render",
        "closeout",
        "production_43_drive_registry",
        "production_45_ghl_readback",
        "production_46_repeat_submit",
    ]:
        add_blocker(blockers, key, receipts[key])

    local_ready = all(
        receipts[key].get("pass") is True
        for key in ["public_http", "email_click_test", "desktop_render", "audit", "production_47_podcast"]
    )
    strict_production_ready = not blockers

    return {
        "lead": lead,
        "ts": utc_now(),
        "receipt_dir": str(receipt_dir),
        "local_public_preview_ready": local_ready,
        "strict_production_ready": strict_production_ready,
        "external_send_allowed": strict_production_ready,
        "no_send": not strict_production_ready,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "schema_failures": schema_43 + schema_45 + schema_46,
        "next_physical_actions": [
            "Update/read back Drive artifact registry with registry_file and verified=true.",
            "Reauthenticate HighLevel and rerun exact contact plus instant-response readback.",
            "Rerun repeat-submit proof and confirm one same GHL contact after repeat.",
            "Capture mobile render proof with a real mobile viewport or approved browser receipt.",
            "Regenerate closeout and production Gatekeeper token only after every blocker is PASS.",
        ],
        "receipts": receipts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lead", required=True)
    parser.add_argument("--receipt-dir", required=True)
    parser.add_argument(
        "--allow-blocked-exit-zero",
        action="store_true",
        help="Print the blocked summary without failing the shell command.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the JSON summary receipt.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary(args.lead, Path(args.receipt_dir))
    payload = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = REPO / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    if summary["strict_production_ready"] or args.allow_blocked_exit_zero:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
