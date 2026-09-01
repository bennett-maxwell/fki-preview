#!/usr/bin/env python3
"""Blueprint host-base gate.

Proves the active Blueprint factory can render future packages against a configurable
host base (GHL/Cloudflare/etc.) while keeping GitHub Pages as the default preview host.
The gate is network-free and side-effect-contained inside the receipt directory.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_BASE = "https://bennett-maxwell.github.io/fki-preview"


def copy_required_tree(repo: Path, harness: Path) -> None:
    for rel in [
        "scripts/clone-blueprint.sh",
        "scripts/blueprint_home_services_patch.py",
        "scripts/blueprint_restaurant_patch.py",
        "scripts/roi-industry-config.json",
        "blueprints/TEMPLATE.html",
    ]:
        src = repo / rel
        dst = harness / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy2(src, dst)
    (harness / "leads").mkdir(parents=True, exist_ok=True)


def load_profile(src: Path, slug: str) -> dict:
    profile = json.loads(src.read_text())
    profile["slug"] = slug
    profile["lead_name"] = profile.get("lead_name") or "Host Base Gate"
    profile["business_name"] = profile.get("business_name") or "Host Base Gate Business"
    profile["first_name"] = profile.get("first_name") or str(profile["lead_name"]).split()[0]
    profile["lead_first_name"] = profile.get("lead_first_name") or profile["first_name"]
    # Seed with legacy GitHub URLs so the gate proves override behavior, not only empty fallback behavior.
    profile["blueprint_url"] = f"{DEFAULT_BASE}/blueprints/{slug}.html"
    profile["podcast_url"] = f"{DEFAULT_BASE}/podcasts/{slug}.mp3"
    profile["qualify_url"] = f"{DEFAULT_BASE}/qualify.html"
    return profile


def active_source_checks(repo: Path) -> list[dict]:
    checks = []
    required = {
        "scripts/clone-blueprint.sh": ["BLUEPRINT_BASE_URL", "{{BLUEPRINT_URL}}", "host_scoped_url", "/qualify.html"],
        # scripts/build-delivery-email.sh REMOVED 2026-08-03: retired by RL-DE2 on 2026-07-17,
        # so its host-base tokens can never be checked. The Stage-7 email is Drive-sourced now.
        "scripts/blueprint-pipeline-orchestrator.py": ["BLUEPRINT_BASE_URL", "BLUEPRINTS_URL_BASE"],
        "scripts/gen-blueprint.py": ["BLUEPRINT_BASE_URL", "{{BLUEPRINT_URL}}", "host_scoped_url"],
        "blueprints/TEMPLATE.html": ["{{BLUEPRINT_URL}}"],
    }
    for rel, needles in required.items():
        text = (repo / rel).read_text(errors="ignore")
        for needle in needles:
            checks.append({"name": f"{rel} contains {needle}", "pass": needle in text})
    return checks


def href_host_ok(html: str, target_base: str, slug: str) -> list[dict]:
    checks = []
    checks.append({"name": "generated og:url uses target host", "pass": f'content="{target_base}/blueprints/{slug}.html"' in html})
    checks.append({"name": "generated podcast URL uses target host", "pass": f'{target_base}/podcasts/{slug}.mp3' in html})
    checks.append({"name": "generated qualify CTA uses target host", "pass": f'{target_base}/qualify.html?' in html})
    checks.append({"name": "generated qualify path is root qualifier not /apply/qualify", "pass": "/apply/qualify.html" not in html})
    checks.append({"name": "generated output has no remaining BLUEPRINT_URL token", "pass": "{{BLUEPRINT_URL}}" not in html})
    return checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--lead-profile", default="leads/mike-norton-origins-20260603.json")
    ap.add_argument("--target-base", default="https://ghl.example.test/fki-preview")
    ap.add_argument("--receipt-dir", default="audit-receipts/blueprint-host-base-gate-20260604")
    ap.add_argument("--json-output", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    receipt_dir = (repo / args.receipt_dir).resolve() if not Path(args.receipt_dir).is_absolute() else Path(args.receipt_dir)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    harness = receipt_dir / "harness"
    harness.mkdir(parents=True, exist_ok=True)

    slug = "host-base-gate-20260604"
    target_base = args.target_base.rstrip("/")
    copy_required_tree(repo, harness)
    profile = load_profile(repo / args.lead_profile, slug)
    profile_path = harness / "leads" / f"{slug}.json"
    profile_path.write_text(json.dumps(profile, indent=2))

    env = os.environ.copy()
    env["BLUEPRINT_BASE_URL"] = target_base
    proc = subprocess.run(
        ["bash", "scripts/clone-blueprint.sh", str(profile_path), "--dry-run"],
        cwd=harness,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )

    output_file = harness / "blueprints" / f"{slug}.html"
    html = output_file.read_text(errors="ignore") if output_file.exists() else ""
    checks = active_source_checks(repo)
    checks.append({"name": "harness clone-blueprint dry-run exits 0", "pass": proc.returncode == 0})
    checks.extend(href_host_ok(html, target_base, slug))

    result = {
        "gate": "blueprint_host_base_gate",
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "default_base": DEFAULT_BASE,
        "target_base": target_base,
        "harness": str(harness),
        "generated_file": str(output_file),
        "source_profile": str((repo / args.lead_profile).resolve()),
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-2000:],
        "checks": checks,
    }
    out = receipt_dir / "blueprint-host-base-gate-current-20260604.json"
    out.write_text(json.dumps(result, indent=2))
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']} {out}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
