#!/usr/bin/env python3
"""
render-scripted-podcast.py — fleet renderer for D3-02-safe podcasts.

Single-voice scripted TTS is the ONLY deterministic way to pass the D3-02
direct-address gate (NotebookLM two-host output fails it — drops the scripted
opening, drifts third-person, transcribes banned words). This tool renders a
controlled script to single-voice audio so every transcribed word is controlled.

Usage:
  render-scripted-podcast.py <slug>
      Reads  podcasts/<slug>-spoken.txt
      Writes podcasts/<slug>.mp3   (mono 96kbps, targets the 6-20MB window)

  render-scripted-podcast.py <slug> --from-source
      If no -spoken.txt exists, derive it from podcasts/<slug>-podcast-source.md
      (extracts the "Spoken script begins below." section, else the whole body).

Env: ELEVENLABS_API_KEY in ~/.openclaw/gateway.env.
Voice W2qLLfPvONwTEm2AyN4W (Bennett PVC, confirmed on account); model eleven_v3.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PODCASTS = REPO / "podcasts"
GATEWAY_ENV = Path.home() / ".openclaw" / "gateway.env"
VOICE = "W2qLLfPvONwTEm2AyN4W"
MODEL = "eleven_v3"
CHUNK_CHARS = 1200
MIN_MB, MAX_MB = 6, 20


def load_key() -> str:
    for line in GATEWAY_ENV.read_text().splitlines():
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("ELEVENLABS_API_KEY not found in gateway.env")


def _clean_lines(body: str) -> str:
    """Drop comments, separators, and markdown headings — none are spoken,
    and headings carry "<Business> is today" phrases that trip the D3-02
    third-person verb check."""
    lines = []
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith("<!--") or s.startswith("=") or s.startswith("#"):
            continue
        if s.startswith("---"):
            continue
        lines.append(ln)
    return "\n".join(lines).strip()


def derive_spoken_from_source(slug: str) -> str:
    src = PODCASTS / f"{slug}-podcast-source.md"
    if not src.exists():
        raise SystemExit(f"No -spoken.txt and no source doc for {slug}")
    text = src.read_text()
    marker = "Spoken script begins below."
    if marker in text:
        return _clean_lines(text.split(marker, 1)[1].strip())
    # v1.6 markerless format: a metadata header + a SPEAKER INSTRUCTIONS block
    # (which itself contains banned words and third-person name references) sit
    # ABOVE the real second-person script, which starts at "## SECTION 1". TTS'ing
    # the whole body would fail D3-02. Start below the instructions and prepend the
    # exact RULE 2 opening so the direct-address opening match is deterministic.
    opening = ""
    m = re.search(r'EXACTLY these words:\s*"(Hi .+?told us\.)"', text, re.DOTALL)
    if m:
        opening = re.sub(r"\s+", " ", m.group(1)).strip()
    idx = text.find("## SECTION 1")
    body = text[idx:] if idx != -1 else text
    cleaned = _clean_lines(body)
    return (opening + "\n\n" + cleaned).strip() if opening else cleaned


def chunk(text: str) -> list:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 > CHUNK_CHARS and cur:
            chunks.append(cur)
            cur = p
        else:
            cur = (cur + "\n\n" + p) if cur else p
    if cur:
        chunks.append(cur)
    return chunks


def tts(chunk_text: str, key: str) -> bytes:
    body = json.dumps({
        "text": chunk_text, "model_id": MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0},
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
        data=body,
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    last = None
    attempts = 6
    for attempt in range(attempts):
        try:
            # eleven_v3 can take >4min on a full 2400-char chunk under load;
            # 420s gives slow generations room before we treat it as a failure.
            with urllib.request.urlopen(req, timeout=420) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:200]}"
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            # Socket read timeouts / transient network errors are not HTTPError —
            # retry them with backoff instead of crashing the whole render.
            last = f"NET {type(e).__name__}: {e}"
        if attempt < attempts - 1:
            time.sleep(8 * (attempt + 1))
    raise SystemExit(f"TTS failed after {attempts} attempts: {last}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Render a D3-02-safe single-voice podcast")
    ap.add_argument("slug")
    ap.add_argument("--from-source", action="store_true",
                    help="Derive -spoken.txt from the source doc if absent")
    args = ap.parse_args()
    slug = args.slug

    spoken = PODCASTS / f"{slug}-spoken.txt"
    if not spoken.exists():
        if args.from_source:
            text = derive_spoken_from_source(slug)
            spoken.write_text(text)
            print(f"derived {spoken} ({len(text)} chars)")
        else:
            raise SystemExit(f"Missing {spoken} (use --from-source to derive)")
    text = spoken.read_text()

    key = load_key()
    chunks = chunk(text)
    print(f"{len(chunks)} chunks, {len(text)} chars")

    tmp = Path("/tmp") / f"{slug}-tts"
    tmp.mkdir(exist_ok=True)
    parts = []
    for i, ch in enumerate(chunks):
        out = tmp / f"part-{i:02d}.mp3"
        out.write_bytes(tts(ch, key))
        print(f"chunk {i}: {out.stat().st_size} bytes", flush=True)
        parts.append(out)
        # Space requests out — back-to-back TTS calls on long fleet batches
        # appear to trip ElevenLabs throttling, which surfaces as read timeouts.
        time.sleep(3)

    listf = tmp / "list.txt"
    listf.write_text("\n".join(f"file '{p}'" for p in parts))
    dest = PODCASTS / f"{slug}.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
         "-ac", "1", "-b:a", "96k", "-map_metadata", "-1", str(dest)],
        check=True, capture_output=True,
    )
    sz = dest.stat().st_size
    mb = sz / 1024 / 1024
    ok = MIN_MB * 1024 * 1024 < sz < MAX_MB * 1024 * 1024
    print(f"FINAL {sz:,} bytes = {mb:.1f}MB window_ok={ok} -> {dest}")
    # Clean up TTS parts.
    for p in parts:
        p.unlink(missing_ok=True)
    listf.unlink(missing_ok=True)
    tmp.rmdir()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
