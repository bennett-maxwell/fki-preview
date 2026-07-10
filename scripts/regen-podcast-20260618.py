#!/usr/bin/env python3
"""
regen-podcast-20260618.py — single-lead steered NotebookLM podcast generation for the
Simon Harwood + Asif Poonja Blueprint runs. Mirrors regen-brent-podcast.py but:
  - v3.37 short-standard steering: "Keep it 9 to 11 minutes" (accept 8-12 / 480-720s)
  - direct-address opening, second-person throughout, application CTA only,
    no source-material framing, no third-person opener.

Usage: python3 scripts/regen-podcast-20260618.py <slug>
"""
import json, subprocess, time, sys
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent
PODCASTS = REPO / 'podcasts'
NLM = 'notebooklm'  # system CLI, auth refreshed via chrome-cookie-bridge
MIN_MP3_BYTES = 2 * 1024 * 1024
MAX_POLL_MIN = 22

LEADS = {
    'simon-harwood-disruptive-foods-20260618': ('Simon Harwood', 'Simon', 'Disruptive Foods'),
    'asif-jam-equities-20260618':              ('Asif Poonja',   'Asif',  'JAM Equities'),
}

def desc(first, business):
    return (
        f'OPENING LINE MUST BE: "Hi {first}, welcome. This walkthrough was built specifically for you and '
        f'{business}, based on everything you told us about your business." Then proceed. '
        f'THROUGHOUT the entire episode: speak DIRECTLY to {first} using "you" and "your business" — '
        f'NEVER refer to {first} in the third person, NEVER say "{business} runs" or "the owner" or "this business" '
        f'or "they". {first} is listening; speak TO {first}, not ABOUT {first} or {business}. '
        f'Do NOT mention "source material", "the document", "the brief", or "analyzing" — this is a personal walkthrough, not a summary. '
        f'Tone: warm, personal, excited about what AI unlocks for {first} and {business}. '
        f'LENGTH IS CRITICAL: target about 10 minutes; do NOT exceed 12 minutes and do NOT go under 8 minutes. '
        f'Be tight and concise — cover the AI agents and the opportunities briskly, no rambling, no long tangents. '
        f'Frame every gap as an AI amplification, never a flaw. '
        f'Close with the application CTA — invite {first} to see if {business} qualifies; never mention scheduling a call.'
    )

def log(m): print(f"[{datetime.now():%H:%M:%S}] {m}", flush=True)

def run(cmd, timeout=420):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, '', 'TIMEOUT'

def main():
    slug = sys.argv[1]
    name, first, business = LEADS[slug]
    dest = PODCASTS / f'{slug}.mp3'
    src = PODCASTS / f'{slug}-podcast-source.md'
    if not src.exists():
        log("FAIL: source doc missing"); sys.exit(1)

    log(f"create notebook for {name}...")
    rc, out, err = run([NLM, 'create', f'{business} Blueprint Podcast {datetime.now():%m%d-%H%M%S}', '--json'])
    try:
        nb = json.loads(out)['notebook']['id']
    except Exception:
        log(f"FAIL create: {out} {err}"); sys.exit(1)
    log(f"notebook={nb}")

    log("add source...")
    rc, out, err = run([NLM, 'source', 'add', str(src), '-n', nb, '--type', 'text',
                        '--title', f'{name} AI Blueprint', '--json'])
    if rc != 0:
        log(f"FAIL source add: {out} {err}"); sys.exit(1)
    time.sleep(15)

    log("trigger steered audio gen (deep-dive/default + strong ~10min steering)...")
    rc, out, err = run([NLM, 'generate', 'audio', '-n', nb, '--format', 'deep-dive', '--length', 'short',
                        '--json', '--retry', '2', desc(first, business)])
    if '"task_id"' not in (out + err) and 'task' not in (out+err).lower():
        log(f"FAIL trigger: {(out+err)[:400]}"); sys.exit(1)
    log("audio gen queued")
    (PODCASTS / f'{slug}-regen-manifest.json').write_text(
        json.dumps({'notebook': nb, 'queued_at': datetime.now().isoformat()}, indent=2))

    log("poll + download...")
    deadline = time.time() + MAX_POLL_MIN * 60
    while time.time() < deadline:
        rc, out, _ = run([NLM, 'artifact', 'list', '-n', nb, '--json'])
        try:
            arts = [a for a in json.loads(out).get('artifacts', []) if 'audio' in str(a.get('type','')).lower()]
        except Exception:
            arts = []
        ready = [a for a in arts if str(a.get('status','')).lower() in ('ready','completed')]
        if ready:
            aid = ready[0].get('id')
            log(f"audio ready aid={aid}, downloading...")
            rc, o, e = run([NLM, 'download', 'audio', str(dest), '-n', nb, '-a', aid], timeout=600)
            if dest.exists() and dest.stat().st_size > MIN_MP3_BYTES:
                log(f"DOWNLOADED {dest.stat().st_size:,} bytes -> {dest}  notebook={nb} aid={aid}")
                sys.exit(0)
            log(f"download failed: {o} {e}"); sys.exit(1)
        fails = [a for a in arts if str(a.get('status','')).lower() in ('failed','error')]
        if fails and not any(str(a.get('status','')).lower() in ('pending','generating','processing') for a in arts):
            log("all gen attempts failed"); sys.exit(1)
        time.sleep(30)
    log("TIMEOUT waiting for audio"); sys.exit(2)

if __name__ == '__main__':
    main()
