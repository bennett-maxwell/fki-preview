#!/usr/bin/env python3
"""Blueprint source-fidelity gate.

Blocks Blueprint artifacts when customer-facing facts are stronger than the available
source data. This is intentionally conservative: exact form/GHL values are allowed;
classified/default/template enrichments must be labeled as defaults or supported by
an explicit source/basis.
"""
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path
from html import unescape

CRITICAL_NUMERIC_FIELDS = ["monthly_leads", "avg_monthly_leads"]
CRITICAL_TEXT_FIELDS = ["business_type", "industry", "service_type"]
TEMPLATE_PHRASES = [
    "SaaS Agency", "SaaS & CRM", "675+ accounts", "$199/mo", "Your SaaS Product",
    "vertical SaaS", "SaaS CRM agency", "subscription businesses run an AI health-monitoring agent",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def extract_contact(raw: dict) -> dict:
    if isinstance(raw.get("contact"), dict):
        return raw["contact"]
    if isinstance(raw.get("contacts"), list) and raw["contacts"]:
        return raw["contacts"][0]
    return raw


def raw_values_from_ghl(raw: dict) -> set[str]:
    c = extract_contact(raw)
    vals: set[str] = set()
    for k in ["firstName", "lastName", "companyName", "email", "phone", "website", "source", "state"]:
        v = c.get(k)
        if v is not None:
            vals.add(str(v).strip().lower())
    for cf in c.get("customFields", []) or []:
        v = cf.get("value")
        if v is not None:
            vals.add(str(v).strip().lower())
    return {v for v in vals if v}


def normalize_tokens(value) -> list[str]:
    if value is None:
        return []
    text = str(value).lower()
    # Keep compact tokens plus multiword alphas.
    toks = re.findall(r"[a-z0-9]+(?:[ -][a-z0-9]+)*", text)
    return [t.strip() for t in toks if t.strip()]


def html_text(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return unescape(path.read_text(errors="ignore"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lead-json", required=True)
    ap.add_argument("--ghl-raw")
    ap.add_argument("--html")
    ap.add_argument("--json-output", action="store_true")
    args = ap.parse_args()

    lead_path = Path(args.lead_json)
    profile = load_json(lead_path)
    raw_values = set()
    if args.ghl_raw:
        raw_values = raw_values_from_ghl(load_json(Path(args.ghl_raw)))
    html = html_text(Path(args.html) if args.html else None)

    findings = []

    # 1) Never let known template SaaS claims survive in a non-SaaS artifact.
    for phrase in TEMPLATE_PHRASES:
        if phrase.lower() in html.lower():
            findings.append({
                "severity": "fail",
                "code": "template_phrase_present",
                "phrase": phrase,
                "message": f"Template/SaaS phrase present in artifact: {phrase}",
            })

    # 2) Exact numeric/customer volume facts must be present in raw GHL values or sourced.
    for field in CRITICAL_NUMERIC_FIELDS:
        if field in profile:
            val = str(profile.get(field)).strip().lower()
            if raw_values and val not in raw_values:
                findings.append({
                    "severity": "fail",
                    "code": "critical_number_not_in_raw_source",
                    "field": field,
                    "value": profile.get(field),
                    "message": f"{field}={profile.get(field)!r} not found in raw GHL values.",
                })

    # 3) If the raw form says 'other' for business type and there are no URLs, a concrete industry
    #    label like 'marketing services' is an inference. It must not be presented as a form fact.
    raw_has_other = "other" in raw_values
    has_external_sources = bool(profile.get("source_urls"))
    website_missing = str(profile.get("source_note", "")).lower().find("no company website") >= 0 or str(profile.get("website", "")).lower() in {"", "none", "null", "https://nothing", "nothing"}
    for field in CRITICAL_TEXT_FIELDS:
        text = str(profile.get(field, ""))
        low = text.lower()
        if raw_has_other and website_missing and not has_external_sources:
            if any(specific in low for specific in ["marketing services", "marketing-services", "agency", "client campaign", "small-business clients"]):
                findings.append({
                    "severity": "fail",
                    "code": "concrete_industry_from_other_without_source",
                    "field": field,
                    "value": text,
                    "message": "Raw form value is only 'other' and no website/source URL exists; concrete industry positioning must be removed or explicitly approved/sourced.",
                })

    # 4) Defaults may exist only if their basis is transparent; they cannot be called form data.
    for field in ["avg_job_value", "close_rate"]:
        if field in profile:
            basis = str(profile.get(f"{field}_basis", "") or profile.get("revenue_declaration", {}).get("customer_value_context", "")).lower()
            if raw_values and str(profile[field]).strip().lower() not in raw_values and "default" not in basis and "adjustable" not in basis:
                findings.append({
                    "severity": "fail",
                    "code": "default_or_inferred_value_unlabeled",
                    "field": field,
                    "value": profile[field],
                    "message": f"{field} is not in raw source values and lacks a visible default/adjustable basis.",
                })

    failed = any(f["severity"] == "fail" for f in findings)
    result = {
        "gate": "blueprint_source_fidelity_gate",
        "lead_json": str(lead_path),
        "html": args.html,
        "raw_value_count": len(raw_values),
        "status": "FAIL" if failed else "PASS",
        "findings": findings,
    }
    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"{result['gate']}: {result['status']} ({len(findings)} findings)")
        for f in findings:
            print(f"- {f['severity'].upper()} {f['code']}: {f['message']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
