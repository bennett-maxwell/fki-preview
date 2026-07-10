#!/usr/bin/env python3
"""Preserve raw GHL/source readbacks for Blueprint source-fidelity audits.

This is intentionally small and fail-closed: a GHL/form-derived Blueprint lead must
keep the raw source payload that seeded the profile so later gates can prove that
numbers, business type, website, and other customer facts were not invented from a
template.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent


def load_json_text(text: str) -> Any:
    text = text.strip()
    if not text:
        raise SystemExit("empty raw payload")
    return json.loads(text)


def read_raw(args: argparse.Namespace) -> tuple[Any, str | None]:
    if args.raw_stdin:
        return load_json_text(sys.stdin.read()), "stdin"
    if args.raw_json:
        p = Path(args.raw_json)
        return json.loads(p.read_text(encoding="utf-8")), str(p)
    raise SystemExit("provide --raw-json or --raw-stdin")


def custom_fields_from_mapping(obj: dict[str, Any]) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    for key, value in obj.items():
        if isinstance(value, (str, int, float, bool)) and value not in ("", None):
            fields.append({"id": str(key), "value": str(value)})
    return fields


def normalize_for_gate(raw: Any) -> dict[str, Any]:
    """Return a shape compatible with blueprint_source_fidelity_gate.raw_values_from_ghl."""
    if not isinstance(raw, dict):
        return {"contact": {"customFields": [{"id": "payload", "value": json.dumps(raw, sort_keys=True)}]}}
    if isinstance(raw.get("contact"), dict) or isinstance(raw.get("contacts"), list):
        return raw
    cf = raw.get("customFields") or raw.get("custom_fields") or raw.get("customField") or raw.get("custom_field")
    contact: dict[str, Any] = {
        "firstName": raw.get("firstName") or raw.get("first_name") or raw.get("firstNameLowerCase"),
        "lastName": raw.get("lastName") or raw.get("last_name"),
        "companyName": raw.get("companyName") or raw.get("company_name") or raw.get("business_name"),
        "email": raw.get("email"),
        "phone": raw.get("phone"),
        "website": raw.get("website") or raw.get("url"),
        "source": raw.get("source") or raw.get("lead_source") or "ghl-webhook",
        "state": raw.get("state") or raw.get("region"),
    }
    fields: list[dict[str, str]] = []
    if isinstance(cf, list):
        for item in cf:
            if isinstance(item, dict):
                val = item.get("value")
                if val is not None:
                    fields.append({"id": str(item.get("id") or item.get("fieldKey") or item.get("name") or "custom"), "value": str(val)})
    elif isinstance(cf, dict):
        fields.extend(custom_fields_from_mapping(cf))
    # Preserve other scalar fields too; this makes webhook payloads auditable even
    # when GHL sends form answers as top-level keys.
    known = {"firstName", "first_name", "lastName", "last_name", "companyName", "company_name", "business_name", "email", "phone", "website", "url", "source", "lead_source", "state", "region", "customFields", "custom_fields", "customField", "custom_field"}
    fields.extend(custom_fields_from_mapping({k: v for k, v in raw.items() if k not in known}))
    contact["customFields"] = fields
    return {"contact": {k: v for k, v in contact.items() if v not in (None, "")}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--profile", help="lead profile to update with raw_ghl_readback_path")
    ap.add_argument("--raw-json")
    ap.add_argument("--raw-stdin", action="store_true")
    ap.add_argument("--kind", default="ghl-contact-by-id", help="filename stem, e.g. ghl-contact-by-id or ghl-webhook-payload")
    ap.add_argument("--receipt-dir", help="override destination directory")
    ap.add_argument("--json-output", action="store_true")
    args = ap.parse_args()

    raw, source = read_raw(args)
    normalized = normalize_for_gate(raw)
    dest_dir = Path(args.receipt_dir) if args.receipt_dir else REPO / "audit-receipts" / args.slug / "source-readbacks"
    dest_dir.mkdir(parents=True, exist_ok=True)
    raw_path = dest_dir / f"{args.kind}.raw.json"
    normalized_path = dest_dir / f"{args.kind}.normalized-for-source-fidelity.raw.json"
    raw_bytes = json.dumps(raw, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    norm_bytes = json.dumps(normalized, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    raw_path.write_bytes(raw_bytes)
    normalized_path.write_bytes(norm_bytes)
    receipt = {
        "status": "PASS",
        "gate": "blueprint_raw_readback_preservation",
        "slug": args.slug,
        "source": source,
        "raw_path": str(raw_path.relative_to(REPO) if raw_path.is_relative_to(REPO) else raw_path),
        "normalized_path": str(normalized_path.relative_to(REPO) if normalized_path.is_relative_to(REPO) else normalized_path),
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "normalized_sha256": hashlib.sha256(norm_bytes).hexdigest(),
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    receipt_path = dest_dir / f"{args.kind}.preservation-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if args.profile:
        prof = Path(args.profile)
        if prof.exists():
            data = json.loads(prof.read_text(encoding="utf-8"))
            data["raw_ghl_readback_path"] = str(normalized_path.relative_to(REPO) if normalized_path.is_relative_to(REPO) else normalized_path)
            data["raw_ghl_readback_sha256"] = receipt["normalized_sha256"]
            note = data.get("source_note") or ""
            add = "Raw GHL/source readback preserved before generation."
            if add not in note:
                data["source_note"] = (note + " " + add).strip()
            prof.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json_output:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"preserved raw readback: {receipt['normalized_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
