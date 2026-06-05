#!/usr/bin/env python3
"""Blueprint delivery-state gate.

Separates three states that were previously easy to blur:

1. PUBLIC_PREVIEW_VERIFIED_NOT_SENT: page/audio/funnel proof exists, but no
   Bennett preview email or external customer/prospect send receipt exists.
2. BENNETT_PREVIEW_SENT: Bennett preview send receipt exists and matches the
   current public artifact hash.
3. EXTERNAL_CUSTOMER_SENT: external_send token plus customer/prospect send
   receipt exists.

Default mode passes preview-only packages while making the delivery lock
machine-readable. Use --require-delivered to fail unless an external send is
actually proven.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


REPO = Path(__file__).resolve().parents[1]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def fetch(url: str) -> tuple[int | None, int, str | None, str | None]:
    try:
        req = Request(url, headers={"User-Agent": "BlueprintDeliveryStateGate/1.0"})
        with urlopen(req, timeout=30) as response:
            data = response.read()
            return response.status, len(data), sha256_bytes(data), None
    except Exception as exc:  # pragma: no cover - receipt detail only
        return None, 0, None, repr(exc)


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists() and path.stat().st_size > 0:
            return path
    return None


def find_audio_url(html: str) -> str | None:
    match = re.search(r"https?://[^\"'\s<>]+\.(?:mp3|m4a|wav)(?:\?[^\"'\s<>]*)?", html)
    return match.group(0) if match else None


def receipt_has_message_id(data: dict[str, Any]) -> bool:
    text = json.dumps(data).lower()
    keys = ["message_id", "messageid", "msg_id", "gmail_message_id", "id"]
    return any(data.get(k) for k in keys) or "message id" in text or "gmail" in text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lead", required=True)
    parser.add_argument("--receipt-dir", required=True)
    parser.add_argument("--public-url", required=True)
    parser.add_argument("--require-delivered", action="store_true")
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    lead = args.lead
    receipt_dir = Path(args.receipt_dir)
    html_path = REPO / "blueprints" / f"{lead}.html"
    email_path = REPO / "delivery-emails" / f"{lead}-delivery-email.html"

    local_html_sha = file_sha256(html_path)
    public_status, public_bytes, public_sha, public_error = fetch(args.public_url)
    html_text = html_path.read_text(encoding="utf-8", errors="ignore") if html_path.exists() else ""
    audio_url = find_audio_url(html_text)
    audio_status = audio_bytes = None
    audio_sha = audio_error = None
    if audio_url:
        audio_status, audio_bytes, audio_sha, audio_error = fetch(audio_url)

    gatekeeper = first_existing(
        [
            receipt_dir / f"{lead}-gatekeeper-pass-token.json",
            receipt_dir / f"{lead}-gatekeeper.json",
        ]
    )
    completion = first_existing(
        [
            receipt_dir / "current-production-completion-after-public-fix-20260604T2221Z.json",
            receipt_dir / f"{lead}-completion-gate.json",
        ]
    )
    conveyor = first_existing(
        [
            receipt_dir / "current-production-conveyor-after-public-fix-20260604T2221Z.json",
            receipt_dir / f"{lead}-conveyor-30-pre-bennett.final.json",
        ]
    )
    bennett_preview = first_existing([receipt_dir / f"{lead}-bennett-preview-send.json"])
    external_send = first_existing(
        [
            receipt_dir / f"{lead}-external-customer-send.json",
            receipt_dir / f"{lead}-customer-send.json",
            receipt_dir / f"{lead}-external-send.json",
        ]
    )

    gatekeeper_data = read_json(gatekeeper) if gatekeeper else {}
    completion_data = read_json(completion) if completion else {}
    conveyor_data = read_json(conveyor) if conveyor else {}
    bennett_preview_data = read_json(bennett_preview) if bennett_preview else {}
    external_send_data = read_json(external_send) if external_send else {}

    public_preview_verified = bool(
        public_status == 200
        and local_html_sha
        and public_sha == local_html_sha
        and audio_status == 200
        and audio_sha
        and gatekeeper_data.get("status") == "PASS"
        and completion_data
        and email_path.exists()
    )

    bennett_preview_sent = bool(
        bennett_preview
        and receipt_has_message_id(bennett_preview_data)
        and (bennett_preview_data.get("sha_match") is True or bennett_preview_data.get("artifact_sha256") == public_sha)
    )
    external_customer_sent = bool(
        external_send
        and receipt_has_message_id(external_send_data)
        and (
            external_send_data.get("external_send_token") is True
            or external_send_data.get("approval_token") == "external_send"
            or external_send_data.get("type") == "external_customer_send"
        )
    )

    if external_customer_sent:
        state = "EXTERNAL_CUSTOMER_SENT"
        allowed_actions = ["audit", "customer_followup"]
        pass_gate = True
    elif bennett_preview_sent:
        state = "BENNETT_PREVIEW_SENT"
        allowed_actions = ["internal_preview", "bennett_preview", "await_external_approval"]
        pass_gate = not args.require_delivered
    elif public_preview_verified:
        state = "PUBLIC_PREVIEW_VERIFIED_NOT_SENT"
        allowed_actions = ["internal_preview", "prepare_bennett_preview_only"]
        pass_gate = not args.require_delivered
    else:
        state = "BLOCKED_INCOMPLETE_PREVIEW"
        allowed_actions = []
        pass_gate = False

    failures: list[str] = []
    if public_status != 200:
        failures.append(f"public blueprint HTTP not 200: {public_status or public_error}")
    if local_html_sha and public_sha and public_sha != local_html_sha:
        failures.append("public blueprint SHA does not match local current artifact")
    if audio_status != 200:
        failures.append(f"public audio HTTP not 200: {audio_status or audio_error}")
    if not gatekeeper_data or gatekeeper_data.get("status") != "PASS":
        failures.append("Gatekeeper PASS token missing")
    if not completion_data:
        failures.append("completion receipt missing")
    if not email_path.exists():
        failures.append("delivery email artifact missing")
    if args.require_delivered and not external_customer_sent:
        failures.append("required delivered state missing external customer/prospect send receipt")

    out = {
        "schema": "blueprint_delivery_state_gate.v1",
        "lead": lead,
        "ts": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if pass_gate else "FAIL",
        "delivery_state": state,
        "public_preview_verified": public_preview_verified,
        "bennett_preview_sent": bennett_preview_sent,
        "external_customer_sent": external_customer_sent,
        "allowed_actions": allowed_actions,
        "locked_actions": {
            "bennett_preview_send": not bennett_preview_sent,
            "external_customer_send": not external_customer_sent,
        },
        "proof": {
            "public_url": args.public_url,
            "public_status": public_status,
            "public_bytes": public_bytes,
            "public_sha256": public_sha,
            "local_html_path": str(html_path),
            "local_html_sha256": local_html_sha,
            "audio_url": audio_url,
            "audio_status": audio_status,
            "audio_bytes": audio_bytes,
            "audio_sha256": audio_sha,
            "delivery_email_path": str(email_path),
            "gatekeeper_receipt": str(gatekeeper) if gatekeeper else "",
            "completion_receipt": str(completion) if completion else "",
            "conveyor_receipt": str(conveyor) if conveyor else "",
            "conveyor_phase": conveyor_data.get("phase"),
            "conveyor_summary": conveyor_data.get("summary"),
            "bennett_preview_receipt": str(bennett_preview) if bennett_preview else "",
            "external_send_receipt": str(external_send) if external_send else "",
        },
        "failures": failures,
        "interpretation": (
            "This package is verified as a public preview/proof package only; it has not been delivered by email/customer send."
            if state == "PUBLIC_PREVIEW_VERIFIED_NOT_SENT"
            else "Delivery state reflected by receipts."
        ),
    }

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json_output:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(f"{out['status']} {state}: {out['interpretation']}")
    return 0 if pass_gate else 1


if __name__ == "__main__":
    sys.exit(main())
