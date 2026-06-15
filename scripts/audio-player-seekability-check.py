#!/usr/bin/env python3
"""Blueprint podcast audio-player seekability gate.

Blocks the failure mode where playback speed works but the progress slider cannot
be dragged/clicked to the middle. Static checks are required everywhere; optional
MP3 URL checks prove byte-range seeking on the deployed file.
"""
import argparse, json, re, sys, urllib.request, urllib.error
from pathlib import Path


def head(url, range_header=False):
    req = urllib.request.Request(url, method='HEAD')
    if range_header:
        req.add_header('Range','bytes=0-1')
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, {k.lower(): v for k,v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k,v in e.headers.items()}
    except Exception as e:
        return 0, {'error': str(e)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('html', type=Path)
    ap.add_argument('--slug', required=True)
    ap.add_argument('--mp3-url', default='')
    ap.add_argument('--json-output', type=Path)
    args=ap.parse_args()
    html=args.html.read_text(encoding='utf-8', errors='ignore')
    css_hit = bool(re.search(r'pod-progress-wrap\s*\{[^}]*height\s*:\s*(4[4-9]|[5-9]\d)px', html, re.I|re.S) or 'pod-progress-hit' in html)
    has_pointer = all(s in html for s in ['pointerdown','pointermove','pointerup'])
    has_fallback = all(s in html for s in ['touchstart','touchmove','touchend']) or all(s in html for s in ['mousedown','mousemove','mouseup'])
    current_time = 'currentTime' in html and re.search(r'audio\.currentTime\s*=', html) is not None
    duration_fallback = 'Number.isFinite(audio.duration)' in html and 'audio.seekable' in html and 'getSeekDuration' in html
    duration_only_gate = re.search(r'if\s*\(\s*audio\.duration\s*\)\s*audio\.currentTime\s*=', html) is not None
    release = ('pointercancel' in html or 'touchcancel' in html) and ('mouseup' in html or 'pointerup' in html or 'touchend' in html)
    storage = re.search(r"STORAGE_KEY\s*=\s*['\"]([^'\"]+)['\"]", html)
    storage_val = storage.group(1) if storage else ''
    storage_pass = storage_val == f'bpod_{args.slug}' or storage_val == 'bpod_{{SLUG}}'
    midpoint_canary_proxy = css_hit and (has_pointer or has_fallback) and current_time and duration_fallback and not duration_only_gate
    mp3_url = args.mp3_url
    if not mp3_url:
        m = re.search(r"(?:src|href)=[\"']([^\"']*podcasts/[^\"']*\.mp3[^\"']*)[\"']", html)
        mp3_url = m.group(1) if m else ''
    range_pass = None; range_detail='not_checked'
    if mp3_url and mp3_url.startswith('http'):
        s1,h1=head(mp3_url, False); s2,h2=head(mp3_url, True)
        cl = h1.get('content-length') or h2.get('content-length')
        ar = (h1.get('accept-ranges') or h2.get('accept-ranges') or '').lower()
        range_pass = bool(cl and (ar == 'bytes' or s2 == 206))
        range_detail = {'head_status':s1,'range_status':s2,'content_length':cl,'accept_ranges':ar,'error':h1.get('error') or h2.get('error')}
    checks={
        'hit_target_pass': css_hit,
        'seek_handler_pass': bool((has_pointer or has_fallback) and current_time),
        'duration_or_seekable_fallback_pass': bool(duration_fallback and not duration_only_gate),
        'release_handler_pass': bool(release),
        'midpoint_canary_pass': bool(midpoint_canary_proxy),
        'range_request_pass': True if range_pass is None else bool(range_pass),
        'storage_key_pass': bool(storage_pass),
    }
    out={'pass': all(checks.values()), 'html': str(args.html), 'slug': args.slug, 'storage_key': storage_val, 'checks': checks, 'mp3_url': mp3_url, 'range_detail': range_detail}
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True); args.json_output.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if out['pass'] else 1

if __name__ == '__main__':
    sys.exit(main())
