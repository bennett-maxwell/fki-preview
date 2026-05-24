#!/usr/bin/env python3
"""
podcast-batch-v16-cli.py — uses notebooklm CLI subprocess (SDK add_text is broken).
For each lead: create notebook → add source via CLI → trigger audio → poll → download.
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
MAX_POLL_MIN = 12

LEADS = [
    ('branson-maxwell', 'Branson Maxwell', 'branson'),
    ('brent-attaway', 'Brent Attaway', 'brent'),
    ('brittney-warnick', 'Brittney Warnick', 'brittney'),
    ('chris-lpnw', 'Chris LPNW', 'chris'),
    ('court-lundberg', 'Court Lundberg', 'court'),
    ('dave-wood', 'Dave Wood', 'dave'),
    ('melissa-tash-srp', 'Melissa Tash', 'melissa'),
    ('paul-muus', 'Paul Muus', 'paul'),
    ('rey-31consulting', 'Rey 31Consulting', 'rey'),
    ('zachary-red-sands', 'Zachary Red Sands', 'zachary'),
]

# Pre-seeded: Brent already has a notebook (b3bc9123)
PRE_SEEDED = {}

def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)

def run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, '', 'TIMEOUT'

def create_notebook(name):
    rc, out, err = run([NLM, 'create', f'FKI Blueprint v1.6 - {name}', '--json'])
    if rc != 0:
        return None
    try:
        return json.loads(out)['notebook']['id']
    except Exception:
        return None

def add_source(nb_id, source_path, title):
    rc, out, err = run([NLM, 'source', 'add', source_path, '-n', nb_id,
                        '--type', 'text', '--title', title, '--json'])
    return rc == 0

def wait_source_ready(nb_id, max_sec=60):
    """Poll until source status = ready."""
    deadline = time.time() + max_sec
    while time.time() < deadline:
        rc, out, _ = run([NLM, 'source', 'list', '-n', nb_id, '--json'])
        if rc == 0:
            try:
                data = json.loads(out)
                sources = data.get('sources', [])
                if sources and all(s.get('status', '').lower() in ('ready', 'completed') for s in sources):
                    return True
            except Exception:
                pass
        time.sleep(5)
    return False

def trigger_audio(nb_id):
    rc, out, err = run([NLM, 'generate', 'audio', '-n', nb_id, '--json', '--retry', '2'])
    return out, err

def list_artifacts(nb_id):
    rc, out, _ = run([NLM, 'artifact', 'list', '-n', nb_id, '--json'])
    if rc != 0:
        return []
    try:
        data = json.loads(out)
        return data.get('artifacts', [])
    except Exception:
        return []

def download_audio(nb_id, artifact_id, dest):
    rc, out, err = run([NLM, 'download', 'audio', dest, '-n', nb_id, '-a', artifact_id], timeout=300)
    return rc == 0 and Path(dest).exists() and Path(dest).stat().st_size > MIN_MP3_BYTES

def main():
    log(f"=== Podcast Batch v1.6 CLI-PY — start ===")
    PODCASTS.mkdir(exist_ok=True)
    notebooks = {}  # slug -> notebook_id

    # PHASE 1: kick off all gens
    for slug, name, first in LEADS:
        source_doc = PODCASTS / f'{slug}-podcast-source.md'
        if not source_doc.exists():
            log(f"[{slug}] SKIP: source doc missing")
            continue

        if slug in PRE_SEEDED:
            nb = PRE_SEEDED[slug]
            log(f"[{slug}] Using pre-seeded: {nb}")
        else:
            log(f"[{slug}] Creating notebook...")
            nb = create_notebook(name)
            if not nb:
                log(f"[{slug}] FAIL: could not create notebook")
                continue
            log(f"[{slug}] Notebook: {nb}, adding source...")
            if not add_source(nb, str(source_doc), f"{name} AI Blueprint"):
                log(f"[{slug}] FAIL: source add failed")
                continue
            log(f"[{slug}] Waiting for source ingest...")
            if not wait_source_ready(nb, 90):
                log(f"[{slug}] WARN: source not ready in 90s, trying gen anyway")

        log(f"[{slug}] Triggering audio gen...")
        out, err = trigger_audio(nb)
        log(f"[{slug}] Gen result: {(out or err)[:200]}")
        notebooks[slug] = nb
        time.sleep(8)  # gentle rate limit

    log(f"=== Phase 1 done. {len(notebooks)} notebooks queued. ===")

    # PHASE 2: poll + download
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

            arts = list_artifacts(nb)
            audio_arts = [a for a in arts if 'audio' in str(a.get('type', '')).lower()
                          or str(a.get('artifact_type', '')) == 'AUDIO_OVERVIEW']
            if not audio_arts:
                continue

            # Get the latest one (skip "failed" status)
            ready = [a for a in audio_arts if str(a.get('status', '')).lower() in ('ready', 'completed', 'done')]
            if ready:
                a = ready[0]
                aid = a.get('id')
                log(f"[{slug}] Audio ready ({aid}), downloading...")
                if download_audio(nb, aid, str(mp3)):
                    done.add(slug)
                    log(f"[{slug}] DOWNLOADED {mp3.stat().st_size} bytes")
                else:
                    failed.add(slug)
                    log(f"[{slug}] DOWNLOAD FAILED")
                continue

            fails = [a for a in audio_arts if str(a.get('status', '')).lower() in ('failed', 'error')]
            if fails and not any(str(a.get('status', '')).lower() in ('pending', 'generating', 'processing') for a in audio_arts):
                failed.add(slug)
                log(f"[{slug}] All audio attempts FAILED")

        remaining = len(notebooks) - len(done) - len(failed)
        if remaining > 0:
            log(f"  Still generating: {remaining}  (done={len(done)} failed={len(failed)})")
            time.sleep(30)

    log(f"=== FINAL ===")
    log(f"DONE  ({len(done)}/{len(notebooks)}): {sorted(done)}")
    log(f"FAILED ({len(failed)}/{len(notebooks)}): {sorted(failed)}")

    # Write manifest
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'total': len(LEADS),
        'done': sorted(done),
        'failed': sorted(failed),
        'notebooks': notebooks,
    }
    manifest_path = PODCASTS / 'v16-batch-manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))
    log(f"Manifest: {manifest_path}")

if __name__ == '__main__':
    main()
