#!/usr/bin/env python3
"""
podcast-d302-preflight.py — D3-02 direct-address pre-flight gate.

Catches NotebookLM two-host (third-person) podcast output BEFORE it ships,
so it gets routed to single-voice scripted-TTS regeneration instead.

Design: CHEAP aggregator. It does NOT transcribe — it reads the D3-02 receipts
that run-audit.py already writes (audit-receipts/<slug>/<slug>-production-47.json)
and classifies each lead's podcast. Re-transcription stays in run-audit; this
just gates on the latest receipt and flags anything that would fail audit.

Classification per lead with a podcasts/<slug>.mp3:
  CLEAN      — receipt.pass == True AND audio_sha256 matches the on-disk mp3
  FAIL       — receipt.pass == False (two-host / third-person → needs scripted-TTS)
  STALE      — receipt exists but audio_sha256 != current mp3 (re-audit needed)
  UNAUDITED  — mp3 present, no receipt yet (never audited)
Leads with no mp3 are skipped (no podcast yet).

Exit 0 only if every podcast is CLEAN. Any FAIL/STALE/UNAUDITED → exit 1 +
optional Slack alert to #leo-coaches (NOT #leo-auto — that channel is broken).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEADS_DIR = REPO / "leads"
PODCASTS_DIR = REPO / "podcasts"
RECEIPTS_DIR = REPO / "audit-receipts"
LOG = Path.home() / ".openclaw" / "logs" / "podcast-d302-preflight.jsonl"
SLACK_CHANNEL = "#leo-coaches"  # #leo-auto is broken — never use it


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(slug: str) -> dict:
    mp3 = PODCASTS_DIR / f"{slug}.mp3"
    if not mp3.exists():
        return {"slug": slug, "state": "NO_PODCAST"}
    receipt = RECEIPTS_DIR / slug / f"{slug}-production-47.json"
    if not receipt.exists():
        return {"slug": slug, "state": "UNAUDITED", "reason": "no D3-02 receipt"}
    try:
        data = json.loads(receipt.read_text())
    except Exception as e:
        return {"slug": slug, "state": "UNAUDITED", "reason": f"unreadable receipt: {e}"}
    current_sha = sha256_of(mp3)
    if data.get("audio_sha256") != current_sha:
        return {"slug": slug, "state": "STALE", "reason": "audio changed since last audit"}
    passed = bool(data.get("pass")) and data.get("direct_address_audio_verified") is True
    if passed:
        return {"slug": slug, "state": "CLEAN"}
    return {
        "slug": slug,
        "state": "FAIL",
        "reason": "fails D3-02 → route to scripted-TTS",
        "banned": data.get("banned_audio_phrases_found") or [],
        "third_person": data.get("third_person_patterns_found") or [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="D3-02 podcast direct-address pre-flight gate")
    ap.add_argument("--leads-dir", default=str(LEADS_DIR))
    ap.add_argument("--no-slack", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json-output", action="store_true")
    args = ap.parse_args()

    leads_dir = Path(args.leads_dir)
    if not leads_dir.is_dir():
        print(f"ERROR: leads dir missing: {leads_dir}", file=sys.stderr)
        return 2

    results = []
    for f in sorted(leads_dir.glob("*.json")):
        results.append(classify(f.stem))

    actionable = [r for r in results if r["state"] in ("FAIL", "STALE", "UNAUDITED")]
    clean = [r for r in results if r["state"] == "CLEAN"]
    no_pod = [r for r in results if r["state"] == "NO_PODCAST"]

    ts = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip()
    summary = {
        "ts": ts, "check": "d302-preflight",
        "total": len(results), "clean": len(clean),
        "fail": len([r for r in actionable if r["state"] == "FAIL"]),
        "stale": len([r for r in actionable if r["state"] == "STALE"]),
        "unaudited": len([r for r in actionable if r["state"] == "UNAUDITED"]),
        "no_podcast": len(no_pod),
        "actionable": [{"slug": r["slug"], "state": r["state"]} for r in actionable],
    }

    if args.json_output:
        print(json.dumps(summary, indent=2))
    else:
        print(f"D3-02 PRE-FLIGHT [{ts}] — {len(results)} leads: "
              f"{summary['clean']} CLEAN · {summary['fail']} FAIL · "
              f"{summary['stale']} STALE · {summary['unaudited']} UNAUDITED · "
              f"{summary['no_podcast']} no-podcast")
        for r in actionable:
            extra = ""
            if r["state"] == "FAIL":
                extra = f" banned={r.get('banned')} 3p={r.get('third_person')}"
            print(f"  {r['state']:9s} {r['slug']}{extra}")

    if not args.no_write:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a") as fh:
            fh.write(json.dumps(summary) + "\n")

    if actionable and not args.no_slack:
        slugs = ", ".join(f"{r['slug']}({r['state']})" for r in actionable)
        msg = f"⚠️ D3-02 pre-flight: {len(actionable)} podcast(s) need attention — {slugs}"
        slack = Path.home() / "bin" / "slack-post.sh"
        if slack.exists():
            subprocess.run([str(slack), SLACK_CHANNEL, msg], capture_output=True)

    return 1 if actionable else 0


if __name__ == "__main__":
    sys.exit(main())
