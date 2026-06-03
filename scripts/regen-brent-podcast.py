#!/usr/bin/env python3
"""
regen-brent-podcast.py — single-lead steered regeneration for brent-attaway.
Cleaned source doc (third-person framing removed) -> NotebookLM steered audio ->
download to podcasts/brent-attaway.mp3 so D3-02 direct-address gate passes.
Mirrors podcast-v17-steered.py but for ONE lead (no 5-min fleet spacing).
"""
import json, subprocess, time, sys
from pathlib import Path
from datetime import datetime

REPO = Path('/Users/openclaw/fki-preview')
PODCASTS = REPO / 'podcasts'
NLM = 'notebooklm'  # system CLI (auth verified live)
MIN_MP3_BYTES = 5 * 1024 * 1024
MAX_POLL_MIN = 20

SLUG, NAME, FIRST, BUSINESS = 'brent-attaway', 'Brent Attaway', 'Brent', 'CRMX'
DEST = PODCASTS / f'{SLUG}.mp3'

def desc():
    return (
        f'OPENING LINE MUST BE: "Hi {FIRST}, welcome. This walkthrough was built specifically for you and {BUSINESS}, '
        f'based on everything you told us about your business." Then proceed. '
        f'THROUGHOUT the entire episode: speak DIRECTLY to {FIRST} using "you" and "your business" — '
        f'NEVER refer to {FIRST} in the third person, NEVER say "{BUSINESS} runs" or "{BUSINESS} owns" or '
        f'"this business" or "the owner" or "they". {FIRST} is listening; speak TO {FIRST}, not ABOUT {FIRST} or {BUSINESS}. '
        f'Tone: warm, personal, excited about what AI unlocks for {FIRST} and {BUSINESS}. '
        f'Cover all 12 sections. Keep it 15-20 minutes. Frame every gap as an AI amplification, never a flaw. '
        f'Close with the application CTA — never mention scheduling a call.'
    )

def log(m): print(f"[{datetime.now():%H:%M:%S}] {m}", flush=True)

def run(cmd, timeout=300):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, '', 'TIMEOUT'

def main():
    src = PODCASTS / f'{SLUG}-podcast-source.md'
    if not src.exists():
        log("FAIL: source doc missing"); sys.exit(1)

    log(f"create notebook for {NAME}...")
    rc, out, err = run([NLM, 'create', f'Brent CRMX Podcast CLEAN {datetime.now():%H%M%S}', '--json'])
    try:
        nb = json.loads(out)['notebook']['id']
    except Exception:
        log(f"FAIL create: {out} {err}"); sys.exit(1)
    log(f"notebook={nb}")

    log("add source...")
    rc, out, err = run([NLM, 'source', 'add', str(src), '-n', nb, '--type', 'text',
                        '--title', f'{NAME} AI Blueprint', '--json'])
    if rc != 0:
        log(f"FAIL source add: {out} {err}"); sys.exit(1)
    time.sleep(15)

    log("trigger steered audio gen...")
    d = desc()
    rc, out, err = run([NLM, 'generate', 'audio', '-n', nb, '--json', '--retry', '2', d])
    if '"task_id"' not in (out + err):
        log(f"FAIL trigger: {(out+err)[:300]}"); sys.exit(1)
    log("audio gen queued")

    manifest = PODCASTS / 'brent-regen-manifest.json'
    manifest.write_text(json.dumps({'notebook': nb, 'queued_at': datetime.now().isoformat()}, indent=2))

    log("poll + download...")
    deadline = time.time() + MAX_POLL_MIN * 60
    while time.time() < deadline:
        rc, out, _ = run([NLM, 'artifact', 'list', '-n', nb, '--json'])
        arts = []
        try:
            arts = [a for a in json.loads(out).get('artifacts', []) if 'audio' in str(a.get('type','')).lower()]
        except Exception:
            pass
        ready = [a for a in arts if str(a.get('status','')).lower() in ('ready','completed')]
        if ready:
            aid = ready[0].get('id')
            log(f"audio ready aid={aid}, downloading...")
            rc, o, e = run([NLM, 'download', 'audio', str(DEST), '-n', nb, '-a', aid], timeout=420)
            if DEST.exists() and DEST.stat().st_size > MIN_MP3_BYTES:
                log(f"DOWNLOADED {DEST.stat().st_size:,} bytes -> {DEST}")
                sys.exit(0)
            else:
                log(f"download failed: {o} {e}"); sys.exit(1)
        fails = [a for a in arts if str(a.get('status','')).lower() in ('failed','error')]
        if fails and not any(str(a.get('status','')).lower() in ('pending','generating','processing') for a in arts):
            log("all gen attempts failed"); sys.exit(1)
        time.sleep(30)
    log("TIMEOUT waiting for audio"); sys.exit(2)

if __name__ == '__main__':
    main()
