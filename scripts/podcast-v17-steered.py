#!/usr/bin/env python3
"""
podcast-v17-steered.py — Description-steered NotebookLM batch.

Key v1.7 insight: NotebookLM TTS hosts IGNORE source-doc opening structure.
The `description` arg to `generate audio` is the ONLY reliable steering lever.

Spaces generations 5min apart to avoid Google rate limit.
"""
import json
import subprocess
import time
import sys
from pathlib import Path
from datetime import datetime

REPO = Path('/Users/openclaw/fki-preview')
PODCASTS = REPO / 'podcasts'
NLM = str(REPO / '.venv' / 'bin' / 'notebooklm')
MIN_MP3_BYTES = 5 * 1024 * 1024
GAP_BETWEEN_GENS = 320  # 5min 20s gap — Google rate limit
MAX_POLL_MIN = 15

LEADS = [
    ('branson-maxwell', 'Branson Maxwell', 'Branson', 'Branson Maxwell Photo and Video'),
    ('brent-attaway', 'Brent Attaway', 'Brent', 'CRMX'),
    ('brittney-warnick', 'Brittney Warnick', 'Brittney', 'Britt Warnick Designs'),
    ('chris-lpnw', 'Chris LPNW', 'Chris', 'LPNW'),
    ('court-lundberg', 'Court Lundberg', 'Court', 'Lundberg Photography'),
    ('dave-wood', 'Dave Wood', 'Dave', 'Dave Wood Photography'),
    ('melissa-tash-srp', 'Melissa Tash', 'Melissa', 'SRP'),
    ('paul-muus', 'Paul Muus', 'Paul', 'Paul Muus Photography'),
    ('rey-31consulting', 'Rey 31Consulting', 'Rey', '31 Consulting'),
    ('zachary-red-sands', 'Zachary Red Sands', 'Zachary', 'Red Sands'),
]

def description_for(first, business):
    """Steering prompt — passed as `description` arg to generate audio."""
    return (
        f'OPENING LINE MUST BE: "Hi {first}, welcome. This walkthrough was built specifically for you and {business}, '
        f'based on everything you told us about your business." '
        f'Then proceed. THROUGHOUT the entire episode: speak DIRECTLY to {first} using "you" and "your business" — '
        f'NEVER refer to {first} in the third person, NEVER say "this business" or "the owner" or "they". '
        f'{first} is listening; speak TO {first}, not ABOUT {first}. '
        f'Tone: warm, personal, excited about what AI unlocks for {first} and {business}. '
        f'Cover all 12 sections of the source document. Keep it 15-20 minutes. '
        f'Frame every gap as an AI amplification opportunity, never as a flaw. '
        f'Close with the application CTA — never mention scheduling a call.'
    )

def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)

def run(cmd, timeout=180):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, '', 'TIMEOUT'

def create_notebook(name):
    rc, out, _ = run([NLM, 'create', f'FKI Blueprint v1.7 - {name}', '--json'])
    if rc != 0:
        return None
    try:
        return json.loads(out)['notebook']['id']
    except Exception:
        return None

def add_source(nb_id, source_path, title):
    rc, _, _ = run([NLM, 'source', 'add', source_path, '-n', nb_id,
                    '--type', 'text', '--title', title, '--json'])
    return rc == 0

def trigger_audio_steered(nb_id, description):
    """Use steering prompt. Returns (success: bool, error: str)."""
    rc, out, err = run([NLM, 'generate', 'audio', '-n', nb_id, '--json', '--retry', '2', description])
    text = out + err
    if '"task_id"' in text:
        return True, ''
    if 'RATE_LIMITED' in text:
        return False, 'RATE_LIMITED'
    return False, text[:200]

def list_audio_artifacts(nb_id):
    rc, out, _ = run([NLM, 'artifact', 'list', '-n', nb_id, '--json'])
    if rc != 0:
        return []
    try:
        data = json.loads(out)
        return [a for a in data.get('artifacts', [])
                if 'audio' in str(a.get('type', '')).lower()]
    except Exception:
        return []

def download(nb_id, aid, dest):
    rc, _, _ = run([NLM, 'download', 'audio', dest, '-n', nb_id, '-a', aid], timeout=300)
    p = Path(dest)
    return p.exists() and p.stat().st_size > MIN_MP3_BYTES

def main():
    log("=== v1.7 description-steered batch start ===")
    PODCASTS.mkdir(exist_ok=True)
    notebooks = {}  # slug -> nb_id

    # PHASE 1: kick off all gens with 5-min spacing
    for i, (slug, name, first, business) in enumerate(LEADS):
        source_doc = PODCASTS / f'{slug}-podcast-source.md'
        if not source_doc.exists():
            log(f"[{slug}] SKIP: source doc missing")
            continue

        log(f"[{slug}] ({i+1}/{len(LEADS)}) Creating notebook...")
        nb = create_notebook(name)
        if not nb:
            log(f"[{slug}] FAIL: notebook create")
            continue

        log(f"[{slug}] {nb}, adding source...")
        if not add_source(nb, str(source_doc), f"{name} AI Blueprint"):
            log(f"[{slug}] FAIL: source add")
            continue
        time.sleep(15)  # source ingest

        desc = description_for(first, business)
        log(f"[{slug}] Triggering steered audio gen (description: {len(desc)} chars)...")
        ok, err = trigger_audio_steered(nb, desc)
        if ok:
            log(f"[{slug}] ✓ Audio gen queued")
            notebooks[slug] = nb
        else:
            log(f"[{slug}] ✗ Trigger failed: {err}")
            # Save anyway so we can retry later
            notebooks[slug] = nb

        # Gap to avoid rate limit (except last)
        if i < len(LEADS) - 1:
            log(f"[{slug}] Sleeping {GAP_BETWEEN_GENS}s before next gen (Google rate limit)...")
            time.sleep(GAP_BETWEEN_GENS)

    log(f"=== Phase 1 done. {len(notebooks)} notebooks queued. ===")
    manifest_path = PODCASTS / 'v17-batch-manifest.json'
    manifest_path.write_text(json.dumps({
        'phase1_completed_at': datetime.now().isoformat(),
        'notebooks': notebooks,
    }, indent=2))

    # PHASE 2: poll + download (loose — most should be done already since we spaced gens)
    log("=== Phase 2: polling + downloading ===")
    done = set()
    failed = set()
    deadline = time.time() + MAX_POLL_MIN * 60

    while time.time() < deadline and (len(done) + len(failed)) < len(notebooks):
        for slug, nb in notebooks.items():
            if slug in done or slug in failed:
                continue
            mp3 = PODCASTS / f'{slug}-blueprint-podcast.mp3'
            if mp3.exists() and mp3.stat().st_size > MIN_MP3_BYTES:
                done.add(slug)
                continue
            arts = list_audio_artifacts(nb)
            ready = [a for a in arts if str(a.get('status', '')).lower() in ('ready', 'completed')]
            if ready:
                a = ready[0]
                aid = a.get('id')
                log(f"[{slug}] Audio ready, downloading...")
                if download(nb, aid, str(mp3)):
                    done.add(slug)
                    log(f"[{slug}] ✓ DOWNLOADED {mp3.stat().st_size:,} bytes")
                else:
                    failed.add(slug)
                    log(f"[{slug}] ✗ Download failed")
                continue
            fails = [a for a in arts if str(a.get('status', '')).lower() in ('failed', 'error')]
            if fails and not any(str(a.get('status', '')).lower() in ('pending', 'generating', 'processing') for a in arts):
                failed.add(slug)
                log(f"[{slug}] ✗ All gen attempts failed")
        remaining = len(notebooks) - len(done) - len(failed)
        if remaining > 0:
            log(f"  Polling... remaining={remaining} done={len(done)} failed={len(failed)}")
            time.sleep(45)

    log("=== FINAL ===")
    log(f"DONE  ({len(done)}/{len(LEADS)}): {sorted(done)}")
    log(f"FAILED ({len(failed)}/{len(LEADS)}): {sorted(failed)}")

    final_manifest = {
        'completed_at': datetime.now().isoformat(),
        'done': sorted(done),
        'failed': sorted(failed),
        'notebooks': notebooks,
    }
    manifest_path.write_text(json.dumps(final_manifest, indent=2))
    log(f"Manifest: {manifest_path}")

if __name__ == '__main__':
    main()
