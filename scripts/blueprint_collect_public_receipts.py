#!/usr/bin/env python3
"""Collect public HTTP receipts for a Blueprint AI package.

This writes only the receipts it can honestly prove from public URLs:
- production 42: public blueprint page HTTP 200
- production 47: public MP3 HTTP 200 and size floor
Other production receipts, such as Drive registry, Notion row, GHL readback,
repeat-submit proof, and Bennett approval, must come from their owning systems.
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin


REPO = Path(__file__).resolve().parents[1]
BASE_URL = "https://bennett-maxwell.github.io/fki-preview/"
MIN_PRODUCTION_AUDIO_BYTES = 29 * 1024 * 1024


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch(url: str, max_bytes: int = 512) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FKI-Blueprint-Receipt/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read(max_bytes)
            return {
                "url": url,
                "http_code": resp.status,
                "content_type": resp.headers.get("content-type", ""),
                "bytes_sampled": len(body),
                "content_length": int(resp.headers.get("content-length") or 0),
                "redirected_url": resp.geturl(),
            }
    except Exception as exc:
        return {"url": url, "http_code": 0, "error": str(exc)}


def fetch_size(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FKI-Blueprint-Receipt/1.0"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            total = 0
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
            return {
                "url": url,
                "http_code": resp.status,
                "content_type": resp.headers.get("content-type", ""),
                "size_download": total,
                "redirected_url": resp.geturl(),
            }
    except Exception as exc:
        return {"url": url, "http_code": 0, "size_download": 0, "error": str(exc)}


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lead", required=True)
    parser.add_argument("--html", required=True)
    parser.add_argument("--receipt-dir", required=True)
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.is_absolute():
        html_path = REPO / html_path
    html = html_path.read_text(encoding="utf-8", errors="replace")
    receipt_dir = Path(args.receipt_dir)
    if not receipt_dir.is_absolute():
        receipt_dir = REPO / receipt_dir

    blueprint_url = urljoin(args.base_url, f"blueprints/{args.lead}.html")
    page = fetch(blueprint_url)
    page_pass = page.get("http_code") == 200 and "text/html" in page.get("content_type", "")
    page.update({"ts": now(), "status": "PASS" if page_pass else "FAIL", "pass": page_pass})
    write(receipt_dir / f"{args.lead}-production-42.json", page)

    mp3_refs = re.findall(r'(?:src|href)=["\']([^"\']*podcasts/[^"\']+\.mp3[^"\']*)["\']', html, re.I)
    if mp3_refs:
        mp3_url = mp3_refs[0] if mp3_refs[0].startswith("http") else urljoin(args.base_url, mp3_refs[0].lstrip("/"))
    else:
        mp3_url = urljoin(args.base_url, f"podcasts/{args.lead}.mp3")
    audio = fetch_size(mp3_url)
    audio_pass = audio.get("http_code") == 200 and int(audio.get("size_download") or 0) >= MIN_PRODUCTION_AUDIO_BYTES
    audio.update({
        "ts": now(),
        "status": "PASS" if audio_pass else "FAIL",
        "pass": audio_pass,
        "min_required_bytes": MIN_PRODUCTION_AUDIO_BYTES,
    })
    write(receipt_dir / f"{args.lead}-production-47.json", audio)

    out = {
        "lead": args.lead,
        "status": "PASS" if page_pass and audio_pass else "FAIL",
        "receipts": {
            "production_42": str(receipt_dir / f"{args.lead}-production-42.json"),
            "production_47": str(receipt_dir / f"{args.lead}-production-47.json"),
        },
    }
    print(json.dumps(out, indent=2))
    return 0 if out["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
