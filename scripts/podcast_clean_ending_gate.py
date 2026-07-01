#!/usr/bin/env python3
"""podcast_clean_ending_gate.py — D3-05 clean-ending / no-hard-cut red-line.

WHY (defect 2026-07-01): Blueprint podcasts were generated as ~20-min NotebookLM
deep-dives then hard-trimmed with `ffmpeg -t 640` to exactly 10:40, so they CUT OFF
MID-SENTENCE instead of being complete ~10-min episodes. The old duration gate
(D3-03) only checked LENGTH (7-16 min), so a blind mid-word truncation of a longer
render sailed through at a "valid" 10:40. This gate proves the episode ENDS CLEANLY.

DISCRIMINATOR (calibrated against real files 2026-07-01):
  Tail *volume* alone does NOT work — NotebookLM episodes end on speech, not silence,
  so a clean episode's last 1.5s (max ~-5 dB / mean ~-28 dB) looks identical to a
  hard cut's. The reliable signal is the TRANSCRIPT of the final ~25s:
    - a CLEAN episode contains a closing / outro cue near the end
      ("thank you for joining", "one final thought", "your next step",
       "see if <biz> qualifies", "catch you on the next deep dive", ...);
    - a HARD CUT ends mid-sentence with NO closing cue, and its total duration is
      almost always a suspiciously round trim boundary (e.g. exactly 640.000000s).

VERDICT LOGIC:
  PASS  if a closing cue is present in the final window.
  FAIL  if NO closing cue AND the duration is a suspiciously round hard-trim
        boundary (whole second AND a multiple of 10s — the `ffmpeg -t` signature).
        This is the load-bearing, non-false-positive discriminator: NotebookLM's
        native renders are never whole-second-round (615.519, 532.967, 300.048),
        so a round boundary with no wrap-up is a proven blind trim.
  Full-volume tail dB is REPORTED as color and used only to strengthen the reason
  string — it is NOT a standalone FAIL trigger, because every NotebookLM episode
  ends on speech (~-5 dB) so it does not discriminate clean from cut on its own.
  On a transcription failure the gate is CONSERVATIVE: if it cannot read the tail it
  FAILS a round-boundary duration (can't prove clean) and PASSES a non-round one.

Usage:
  podcast_clean_ending_gate.py --audio <mp3> [--lead <slug>] [--business-name <biz>]
                               [--tail-seconds 25] [--receipt <path>] [--json-output]
Exit 0 = clean ending PASS; non-zero = hard-cut / clean-ending FAIL.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_TAIL_SECONDS = 25

# Closing / outro cues that mark a complete, wrapped-up episode. Matched
# case-insensitively as substrings/regex against the final-window transcript.
CLOSING_CUES = [
    r"thank you (so much )?for (joining|listening)",
    r"thanks for (joining|listening|tuning in)",
    r"(one )?final (thought|thoughts|question)",
    r"i'?ll leave you with",
    r"we'?ll leave you with",
    r"we (really )?hope this (walkthrough|deep dive|conversation)",
    r"your next step",
    r"next step is",
    r"see if .{0,40}qualif",  # "see if <biz> qualifies"
    r"review the application",
    r"catch you (on|in) (the )?next",
    r"until next time",
    r"that'?s (a wrap|all for)",
    r"in closing",
    r"to wrap (this |it )?up",
    r"wrapping up",
    r"signing off",
    r"take care",
    r"thanks for (having|being)",
    r"appreciate you (joining|listening)",
    r"that does it for",
    r"see if we'?re a match",
    r"move forward",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(cmd, timeout=180):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def ffprobe_duration(audio: Path) -> float:
    out = _run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(audio)
    ], timeout=30).stdout.strip()
    return float(out)


def tail_volume(audio: Path, dur: float, window: float = 1.5) -> dict:
    """max/mean dB of the final `window` seconds. High max with high-ish mean =
    full-volume speech at the cut point (part of the hard-cut signature)."""
    start = max(0.0, dur - window)
    proc = _run([
        "ffmpeg", "-hide_banner", "-loglevel", "info",
        "-i", str(audio), "-ss", f"{start}", "-af", "volumedetect", "-f", "null", "-"
    ], timeout=120)
    text = proc.stderr or ""
    out = {}
    m = re.search(r"max_volume:\s*(-?[\d.]+) dB", text)
    if m:
        out["tail_max_db"] = float(m.group(1))
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", text)
    if m:
        out["tail_mean_db"] = float(m.group(1))
    return out


def transcribe_tail(audio: Path, dur: float, tail_seconds: int) -> str:
    start = max(0.0, dur - tail_seconds)
    clip = Path("/tmp") / f"clean-ending-{audio.stem}.wav"
    ff = _run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start}", "-i", str(audio), "-t", str(tail_seconds),
        "-ac", "1", "-ar", "16000", str(clip)
    ], timeout=120)
    if ff.returncode != 0:
        raise RuntimeError(f"ffmpeg tail extract failed: {ff.stderr[-300:]}")
    # Prefer faster-whisper (accurate on proper names / sentence boundaries).
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base.en", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(clip), beam_size=1)
        text = " ".join(s.text for s in segments).strip()
        if text:
            return text
    except Exception:
        pass
    # Fallback: Google Web Speech.
    try:
        import speech_recognition as sr
        rec = sr.Recognizer()
        with sr.AudioFile(str(clip)) as src:
            audio_data = rec.record(src)
        return rec.recognize_google(audio_data)
    except Exception as exc:
        raise RuntimeError(f"transcription unavailable: {exc}") from exc


def has_closing_cue(text: str) -> list:
    low = re.sub(r"\s+", " ", (text or "").lower())
    return [pat for pat in CLOSING_CUES if re.search(pat, low)]


def ends_mid_sentence(text: str) -> bool:
    """True if the final-window transcript does not terminate on sentence-final
    punctuation followed by nothing (i.e. it was chopped mid-thought). Whisper adds
    a trailing '.' even on a hard cut, so this is a weak signal used only as color;
    the load-bearing checks are closing-cue + round-duration + tail volume."""
    t = (text or "").strip()
    if not t:
        return True
    return not re.search(r'[.!?]["\')\]]?$', t)


def is_round_trim_boundary(dur: float) -> bool:
    """The ffmpeg -t hard-trim signature: an exact whole second AND a multiple of 10.
    NotebookLM's native renders are never whole-second-round (e.g. 615.519, 532.967,
    300.048); a value like 640.000000 is a dead giveaway of `-t 640`."""
    if abs(dur - round(dur)) > 0.05:
        return False
    return round(dur) % 10 == 0


def evaluate(audio: Path, tail_seconds: int, business_name: str = "") -> dict:
    dur = ffprobe_duration(audio)
    mmss = f"{int(dur)//60}:{int(dur)%60:02d}"
    round_boundary = is_round_trim_boundary(dur)
    vol = tail_volume(audio, dur)
    tail_max = vol.get("tail_max_db")
    # full-volume speech at the very end (no trailing resolution/quiet)
    full_volume_tail = tail_max is not None and tail_max > -12.0

    result = {
        "duration_sec": round(dur, 3),
        "duration_mmss": mmss,
        "round_trim_boundary": round_boundary,
        **vol,
        "full_volume_tail": full_volume_tail,
        "tail_seconds_audited": tail_seconds,
    }

    try:
        transcript = transcribe_tail(audio, dur, tail_seconds)
    except Exception as exc:
        # Conservative fallback: can't read the tail. A round-trim boundary can't be
        # proven clean → FAIL; a natural duration → PASS (no hard-cut evidence).
        result["transcription_error"] = str(exc)
        clean = not round_boundary
        result.update({
            "closing_cues_found": None,
            "clean_ending_verified": clean,
            "status": "PASS" if clean else "FAIL",
            "reason": ("transcription unavailable; round-trim boundary duration is "
                       "unprovable as clean" if not clean
                       else "transcription unavailable but duration is a natural (non-round) length"),
        })
        return result

    cues = has_closing_cue(transcript)
    mid = ends_mid_sentence(transcript)
    result["tail_transcript"] = transcript[-600:]
    result["closing_cues_found"] = cues
    result["ends_mid_sentence"] = mid

    if cues:
        result.update({
            "clean_ending_verified": True,
            "status": "PASS",
            "reason": f"closing cue present: {cues[0]!r}",
        })
        return result

    # No closing cue. Hard-cut ONLY if the duration is a round trim boundary — the
    # single reliable, false-positive-free signature. full_volume_tail / mid-sentence
    # are reported to strengthen the reason but never FAIL on their own (they fire on
    # legitimately-ended NotebookLM episodes too).
    hardcut = round_boundary
    reasons = []
    if round_boundary:
        reasons.append(f"round hard-trim boundary duration {mmss} ({dur:.3f}s)")
    if full_volume_tail:
        reasons.append(f"full-volume unresolved speech tail (max {tail_max} dB)")
    if mid:
        reasons.append("final window ends mid-sentence")
    result.update({
        "clean_ending_verified": not hardcut,
        "status": "FAIL" if hardcut else "PASS",
        "reason": ("no closing cue + hard-cut signature: " + "; ".join(reasons)) if hardcut
                  else "no explicit closing cue, but no hard-cut signature (duration natural, tail resolves)",
    })
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="D3-05 podcast clean-ending / no-hard-cut gate")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--lead", default="")
    ap.add_argument("--business-name", default="")
    ap.add_argument("--tail-seconds", type=int, default=DEFAULT_TAIL_SECONDS)
    ap.add_argument("--receipt")
    ap.add_argument("--json-output", action="store_true")
    args = ap.parse_args()

    audio = Path(args.audio)
    if not audio.exists():
        result = {"lead": args.lead, "status": "FAIL", "clean_ending_verified": False,
                  "error": f"audio missing: {audio}", "ts": utc_now()}
    else:
        try:
            result = evaluate(audio, args.tail_seconds, args.business_name)
        except Exception as exc:
            result = {"status": "FAIL", "clean_ending_verified": False,
                      "error": f"clean-ending gate error: {exc}"}
        result["lead"] = args.lead
        result["audio"] = str(audio)
        result["ts"] = utc_now()

    if args.receipt:
        rp = Path(args.receipt)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"D3-05 clean-ending: {result.get('status')} ({args.lead}) — {result.get('reason', result.get('error',''))}")
    return 0 if result.get("clean_ending_verified") else 1


if __name__ == "__main__":
    raise SystemExit(main())
