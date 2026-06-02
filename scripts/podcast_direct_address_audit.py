#!/usr/bin/env python3
"""Audit the opening of a Blueprint podcast for direct-address quality.

This is intentionally narrow: the most common NotebookLM failure is opening as
an analysis of "source material" and talking about the prospect in third person.
The gate fails those patterns before a delivery email can pass production.
"""

import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_SECONDS = 180


BANNED_PATTERNS = [
    r"\bsource materials?\b",
    r"\bsources?\b",
    r"\bsource documents?\b",
    r"\bthis source\b",
    r"\bthe source\b",
    r"\bthis document\b",
    r"\bthe document\b",
    r"\bthis brief\b",
    r"\bthe brief\b",
    r"\bresearch brief\b",
    r"\bthese materials\b",
    r"\bthe materials\b",
    r"\bwe (are|'re) (looking at|analyzing|analysing)\b",
    r"\bwe('ll| will) look at\b",
    r"\bwhat we (are|'re) analyzing\b",
    r"\bspecific client\b",
    r"\bgolden state\b",
    r"\bdelete delete\b",
    r"\bi said\b",
    r"\bhigh chad\b",
    r"\bbennett preview\b",
    r"\bcustomer send\b",
    r"\bgatekeeper\b",
    r"\bproduction gatekeeper\b",
    r"\binternal audit\b",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def transcribe_with_speech_recognition(audio_path: Path, seconds: int) -> str:
    try:
        import speech_recognition as sr
    except Exception as exc:
        raise RuntimeError(f"speech_recognition unavailable: {exc}") from exc

    tmp_root = Path("/tmp") / f"podcast-direct-address-{audio_path.stem}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    recognizer = sr.Recognizer()
    chunks = []
    chunk_len = 60
    for start in range(0, seconds, chunk_len):
        wav = tmp_root / f"chunk-{start}.wav"
        ffmpeg = run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(audio_path), "-ss", str(start), "-t", str(chunk_len),
            "-ac", "1", "-ar", "16000", str(wav),
        ], timeout=120)
        if ffmpeg.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {ffmpeg.stderr[-400:]}")
        with sr.AudioFile(str(wav)) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except Exception as exc:
            text = f"[UNTRANSCRIBED:{type(exc).__name__}]"
        chunks.append(text)
    return " ".join(chunks)


def transcribe(audio_path: Path, seconds: int) -> str:
    """Prefer faster-whisper — it transcribes proper names ('Britt', 'Kamoto')
    accurately, where free Google Web Speech mishears them ('Brett'/'hybrid'/'Komodo')
    and caused false D3-02 fails on correctly-steered podcasts. Falls back to Google."""
    try:
        from faster_whisper import WhisperModel
        clip = Path("/tmp") / f"pda-{audio_path.stem}-{seconds}.wav"
        ff = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(audio_path),
                  "-t", str(seconds), "-ac", "1", "-ar", "16000", str(clip)], timeout=180)
        if ff.returncode == 0:
            model = WhisperModel("base.en", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(str(clip), beam_size=1)
            text = " ".join(s.text for s in segments).strip()
            if text:
                return text
    except Exception:
        pass
    return transcribe_with_speech_recognition(audio_path, seconds)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def phrase_present(text: str, phrase: str, min_ratio: float = 0.86) -> bool:
    if not phrase:
        return False
    if phrase in text:
        return True
    words = re.findall(r"\b[a-z0-9']+\b", text)
    target = re.findall(r"\b[a-z0-9']+\b", phrase)
    if not target:
        return False
    width = len(target)
    for idx in range(0, max(0, len(words) - width) + 1):
        candidate = " ".join(words[idx:idx + width])
        if difflib.SequenceMatcher(None, candidate, " ".join(target)).ratio() >= min_ratio:
            return True
    return False


def audit_transcript(transcript: str, first_name: str, lead_name: str, business_name: str) -> dict:
    text = normalize(transcript)
    first = normalize(first_name)
    lead = normalize(lead_name)
    business = normalize(business_name)
    opening_variants = [
        normalize(f"Hi {first_name}, welcome. This walkthrough was built for you and {business_name}, from what you told us."),
        normalize(f"Hello {first_name}, welcome. This walkthrough was built for you and {business_name}, from what you told us."),
        normalize(f"{first_name}, welcome. This walkthrough was built for you and {business_name}, from what you told us."),
        normalize(f"Hi {first_name}, welcome. This walkthrough was built specifically for you and {business_name}, based on everything you told us."),
    ]
    expected_opening = opening_variants[0]
    opening_window = text[:500]
    # ASR-tolerant: the free speech-recognizer mishears the greeting ("Hi"->"Ty")
    # and the business name ("Kamoto"->"Komodo"). This gate verifies INTENT — the
    # owner's first name addressed at the open, adjacent to "welcome" — not a perfect
    # transcription. All CONTENT red-lines (banned phrases, third-person, you-count,
    # business-present, name-count) remain strict below.
    opening_direct = bool(first and (
        re.search(rf"\b(?:hi|hello|hey)\s+{re.escape(first)}\b", opening_window, re.I)
        or re.search(rf"\b{re.escape(first)}\b.{{0,60}}\bwelcome\b", opening_window, re.I)
    ))
    opening_exact_or_close = any(
        phrase_present(opening_window, variant, min_ratio=0.78)
        for variant in opening_variants
    )

    banned_found = []
    for pat in BANNED_PATTERNS:
        if re.search(pat, text, re.I):
            banned_found.append(pat)

    first_name_count = len(re.findall(rf"\b{re.escape(first)}\b", text, re.I)) if first else 0
    business_present = phrase_present(text, business)
    you_count = len(re.findall(r"\b(you|your|yours|you're|you've|you'll|you'd)\b", text, re.I))

    third_person_patterns = []
    if lead:
        third_person_patterns.extend([
            rf"\b{re.escape(lead)}\b.*\b(owner|client)\b",
            rf"\b(owner|client)\b.*\b{re.escape(lead)}\b",
            rf"\b{re.escape(lead)}\b\s+(runs?|owns?|operates?|has|is|was|needs?|wants?)\b",
        ])
    if business:
        third_person_patterns.extend([
            rf"\bowner of (a |the )?{re.escape(business)}\b",
            rf"\b{re.escape(business)}\b\s+(runs?|owns?|operates?|has|is|was|needs?|wants?)\b",
        ])
    third_person_patterns.extend([
        r"\b(the|this) company\b",
        r"\b(the|this) business\b",
        r"\b(the|this) owner\b",
        r"\b(his|her|their) (business|company|team)\b",
        r"\b(he|she|they)\s+(runs?|owns?|operates?|has|is|was|needs?|wants?)\b",
    ])
    third_person_found = [pat for pat in third_person_patterns if re.search(pat, text, re.I)]

    pass_now = (
        opening_direct
        and opening_exact_or_close
        and first_name_count >= 1
        and business_present
        and you_count >= 5
        and not banned_found
        and not third_person_found
    )
    return {
        "pass": pass_now,
        "status": "PASS" if pass_now else "FAIL",
        "first_name_count": first_name_count,
        "business_present": business_present,
        "opening_direct_address_verified": opening_direct,
        "opening_exact_or_close": opening_exact_or_close,
        "expected_opening": expected_opening,
        "you_your_count": you_count,
        "banned_audio_phrases_found": banned_found,
        "third_person_patterns_found": third_person_found,
        "transcript_excerpt": transcript[:1200],
    }


def public_url_probe(url: str) -> dict:
    if not url:
        return {}
    proc = run([
        "curl", "-L", "-s", "-o", "/dev/null",
        "-w", "%{http_code} %{size_download} %{content_type}",
        url,
    ], timeout=180)
    if proc.returncode != 0:
        return {"public_url": url, "http_probe_error": proc.stderr[-400:]}
    parts = proc.stdout.strip().split(" ", 2)
    return {
        "public_url": url,
        "http_code": int(parts[0]) if parts and parts[0].isdigit() else 0,
        "size_download": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0,
        "content_type": parts[2] if len(parts) > 2 else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Blueprint podcast direct-address quality")
    parser.add_argument("--audio", required=True, help="MP3/M4A audio path")
    parser.add_argument("--first-name", required=True)
    parser.add_argument("--lead-name", required=True)
    parser.add_argument("--business-name", required=True)
    parser.add_argument("--lead", required=True, help="Lead slug")
    parser.add_argument("--seconds", type=int, default=DEFAULT_SECONDS)
    parser.add_argument("--transcript-file", help="Use an existing transcript text file")
    parser.add_argument("--receipt", help="Write JSON receipt here")
    parser.add_argument("--public-url", help="Public podcast URL to verify")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        result = {
            "lead": args.lead,
            "status": "FAIL",
            "pass": False,
            "error": f"audio missing: {audio_path}",
            "ts": utc_now(),
        }
    else:
        try:
            if args.transcript_file:
                transcript = Path(args.transcript_file).read_text(encoding="utf-8", errors="replace")
            else:
                transcript = transcribe(audio_path, args.seconds)
            result = audit_transcript(transcript, args.first_name, args.lead_name, args.business_name)
            result.update({
                "lead": args.lead,
                "audio": str(audio_path),
                "audio_sha256": file_sha256(audio_path),
                "audio_size_bytes": audio_path.stat().st_size,
                "seconds_audited": args.seconds,
                "direct_address_audio_verified": result["pass"],
                "ts": utc_now(),
            })
            result.update(public_url_probe(args.public_url or ""))
        except Exception as exc:
            result = {
                "lead": args.lead,
                "audio": str(audio_path),
                "audio_sha256": file_sha256(audio_path),
                "audio_size_bytes": audio_path.stat().st_size,
                "status": "FAIL",
                "pass": False,
                "direct_address_audio_verified": False,
                "error": str(exc),
                "ts": utc_now(),
            }
            result.update(public_url_probe(args.public_url or ""))

    if args.receipt:
        receipt_path = Path(args.receipt)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Podcast direct-address audit: {result['status']} ({args.lead})")
        if not result.get("pass"):
            print(result.get("error") or result.get("transcript_excerpt", "")[:400])
    return 0 if result.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
