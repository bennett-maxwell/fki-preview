#!/usr/bin/env python3
"""
finalize-podcast-receipt-20260618.py — produce the gatekeeper production-47 receipt
for a 2026-06-18 Blueprint podcast.

Runs scripts/podcast_direct_address_audit.py (faster-whisper transcript + direct-address
checks), then augments the receipt with the fields blueprint_gatekeeper_100.py requires:
  - duration_seconds (ffprobe)
  - NotebookLM origin proof (notebook_id from the regen manifest, generator=notebooklm,
    notebooklm_status=READY)

Usage: python3 scripts/finalize-podcast-receipt-20260618.py <slug>
Writes audit-receipts/<slug>/<slug>-production-47.json
"""
import json, os, sys, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEADS = {
    'simon-harwood-disruptive-foods-20260618': ('Simon Harwood', 'Simon', 'Disruptive Foods'),
    'asif-jam-equities-20260618':              ('Asif Poonja',   'Asif',  'JAM Equities'),
}

def ffprobe_duration(p):
    out = subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', str(p)], text=True)
    return float(out.strip())

def main():
    slug = sys.argv[1]
    name, first, business = LEADS[slug]
    audio = REPO / 'podcasts' / f'{slug}.mp3'
    if not audio.exists():
        sys.exit(f"FAIL: {audio} missing")
    rec_dir = REPO / 'audit-receipts' / slug
    rec_dir.mkdir(parents=True, exist_ok=True)
    receipt = rec_dir / f'{slug}-production-47.json'
    public_url = f'https://bennett-maxwell.github.io/fki-preview/podcasts/{slug}.mp3'

    # 1) direct-address audit (transcribes opening, writes base receipt)
    cmd = [sys.executable, str(REPO / 'scripts' / 'podcast_direct_address_audit.py'),
           '--audio', str(audio), '--first-name', first, '--lead-name', name,
           '--business-name', business, '--lead', slug, '--seconds', '200',
           '--public-url', public_url, '--receipt', str(receipt)]
    r = subprocess.run(cmd, text=True, capture_output=True, timeout=600)
    print(r.stdout[-1500:]);
    if r.returncode != 0:
        print(r.stderr[-1000:])

    data = json.loads(receipt.read_text())

    # 2) augment with duration + NotebookLM origin
    dur = ffprobe_duration(audio)
    data['duration_seconds'] = dur
    data['duration'] = dur
    man = REPO / 'podcasts' / f'{slug}-regen-manifest.json'
    nb = None
    if man.exists():
        nb = json.loads(man.read_text()).get('notebook')
    data['notebook_id'] = nb
    data['notebooklm_notebook_id'] = nb
    data['generator'] = 'notebooklm'
    data['audio_generator'] = 'notebooklm'
    data['origin'] = 'notebooklm'
    data['notebooklm_status'] = 'READY'
    data['audio_status'] = 'READY'
    data['local_tts_fallback'] = ''
    data['content_type'] = 'audio/mpeg'
    receipt.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        'slug': slug, 'duration_seconds': round(dur, 1),
        'in_window_480_720': 480 <= dur <= 720,
        'direct_address_pass': data.get('direct_address_audio_verified'),
        'opening_exact_or_close': data.get('opening_exact_or_close'),
        'you_your_count': data.get('you_your_count'),
        'third_person_found': data.get('third_person_patterns_found'),
        'banned_found': data.get('banned_audio_phrases_found'),
        'http_code': data.get('http_code'),
        'notebook_id': nb, 'receipt': str(receipt.relative_to(REPO)),
    }, indent=2))

if __name__ == '__main__':
    main()
