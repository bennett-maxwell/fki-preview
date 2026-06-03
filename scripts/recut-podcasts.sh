#!/bin/bash
# Sequential podcast re-cut orchestrator. NotebookLM forces re-auth under concurrent
# sessions, so we run ONE at a time, refresh auth before each attempt, and retry until
# the cut passes: duration 16-20 min, opens "Hi <first>", and no analyst-framing phrase.
cd ~/Desktop/fki-gen
export PATH="$HOME/.pyenv/versions/3.11.9/bin:$PATH"

check() {  # args: slug first ; echoes PASS/FAIL + reason
  local slug="$1" first="$2" f="podcasts/$slug.mp3"
  [ -f "$f" ] || { echo "FAIL no-file"; return; }
  local secs; secs=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null | cut -d. -f1)
  ffmpeg -hide_banner -loglevel error -y -i "$f" -t 14 -ac 1 -ar 16000 /tmp/chk_$slug.wav 2>/dev/null
  python3 - "$slug" "$first" "$secs" <<'PY'
import sys, re
from faster_whisper import WhisperModel
slug, first, secs = sys.argv[1], sys.argv[2], int(sys.argv[3])
# full-file analyst-phrase scan
import subprocess
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",f"podcasts/{slug}.mp3","-ac","1","-ar","16000",f"/tmp/full_{slug}.wav"],check=False)
m = WhisperModel("base.en", device="cpu", compute_type="int8")
segs,_ = m.transcribe(f"/tmp/full_{slug}.wav", beam_size=1)
txt = " ".join(s.text for s in segs)
opening = txt.strip()[:80].lower()
analyst = re.findall(r"we(?: are|'re) (?:looking at|analyzing|analysing)", txt, re.I)
mmss=f"{secs//60}:{secs%60:02d}"
reasons=[]
if not (960 <= secs <= 1200): reasons.append(f"duration {mmss}")
if f"hi {first.lower()}" not in opening and not opening.startswith(f"hi, {first.lower()}"): reasons.append(f"opening:{opening[:40]!r}")
if analyst: reasons.append(f"analyst:{analyst[:2]}")
print(("PASS " if not reasons else "FAIL ")+mmss+(" | "+"; ".join(reasons) if reasons else ""))
PY
}

declare -a LEADS=(
  "austin-iron-horse|Iron Horse Armory|Austin"
  "rush-evans|Riah Evans Photos & Video|Rush"
  "zachary-oldham|Red Sands Vacation Properties|Zachary"
)

for entry in "${LEADS[@]}"; do
  IFS='|' read -r slug biz first <<< "$entry"
  echo "===== $slug ====="
  ok=0
  for attempt in 1 2 3; do
    echo "[$slug] attempt $attempt: refreshing auth + generating..."
    python3 scripts/chrome-cookie-bridge.py >/tmp/auth_$slug.log 2>&1
    python3 scripts/fetch-podcast.py --slug "$slug" --source "podcasts/$slug-podcast-source.md" \
      --business-name "$biz" --first-name "$first" --timeout 1500 >/tmp/recut_$slug.log 2>&1
    res=$(check "$slug" "$first")
    echo "[$slug] attempt $attempt result: $res"
    if [[ "$res" == PASS* ]]; then ok=1; echo "[$slug] ACCEPTED $res"; break; fi
  done
  [ "$ok" = 0 ] && echo "[$slug] EXHAUSTED 3 attempts — best effort left in place"
done
echo "===== RECUT ORCHESTRATOR COMPLETE ====="
for entry in "${LEADS[@]}"; do
  IFS='|' read -r slug biz first <<< "$entry"
  secs=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "podcasts/$slug.mp3" 2>/dev/null | cut -d. -f1)
  echo "  $slug: $((secs/60)):$(printf %02d $((secs%60)))"
done
