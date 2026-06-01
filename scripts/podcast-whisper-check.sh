#!/usr/bin/env bash
# podcast-whisper-check.sh — v1.6 post-generation gate
# Transcribes first 30s of each podcast MP3 and verifies owner's first name appears.
# Writes JSON report to /tmp/podcast-whisper-check.json
#
# Usage: bash scripts/podcast-whisper-check.sh

set -uo pipefail

PODCASTS=/Users/openclaw/fki-preview/podcasts
MODEL=/tmp/ggml-base.en.bin
REPORT=/tmp/podcast-whisper-check.json
TMPDIR=$(mktemp -d)

# Map: slug → first name (lowercase for grep)
declare -a LEADS=(
  'branson-maxwell:branson'
  'brent-attaway:brent'
  'brittney-warnick:brittney'
  'chris-lpnw:chris'
  'court-lundberg:court'
  'dave-wood:dave'
  'melissa-tash-srp:melissa'
  'paul-muus:paul'
  'rey-31consulting:rey'
  'zachary-red-sands:zachary'
)

echo "{\"checked_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"results\":[" > "$REPORT"
FIRST=1
PASS=0
FAIL=0

for entry in "${LEADS[@]}"; do
  SLUG=${entry%:*}
  FIRST_NAME=${entry#*:}
  MP3="${PODCASTS}/${SLUG}-blueprint-podcast.mp3"

  # Find MP3 — try both naming patterns
  if [ ! -f "$MP3" ]; then
    MP3=$(ls "${PODCASTS}/${SLUG}"*.mp3 2>/dev/null | head -1)
  fi

  if [ -z "$MP3" ] || [ ! -f "$MP3" ]; then
    STATUS="MISSING"
    TRANSCRIPT=""
    echo "  $SLUG: MP3 MISSING"
  else
    # Extract first 30s as 16kHz mono WAV (whisper requires this)
    WAV="${TMPDIR}/${SLUG}-30s.wav"
    ffmpeg -y -ss 0 -t 30 -i "$MP3" -ar 16000 -ac 1 "$WAV" 2>/dev/null

    # Transcribe
    TRANSCRIPT=$(whisper-cli -m "$MODEL" -f "$WAV" -nt 2>/dev/null | tr '\n' ' ' | sed 's/  */ /g' | sed 's/"/\\"/g')

    # Check if owner's first name appears
    if echo "$TRANSCRIPT" | grep -qi "\b${FIRST_NAME}\b"; then
      STATUS="PASS"
      PASS=$((PASS+1))
      echo "  ✓ $SLUG: PASS — '$FIRST_NAME' heard in first 30s"
    else
      STATUS="FAIL_NO_NAME"
      FAIL=$((FAIL+1))
      echo "  ✗ $SLUG: FAIL — '$FIRST_NAME' NOT in first 30s"
      echo "    Transcript: ${TRANSCRIPT:0:200}"
    fi
  fi

  [ $FIRST -eq 0 ] && echo "," >> "$REPORT"
  FIRST=0
  printf '{"slug":"%s","first_name":"%s","mp3":"%s","status":"%s","transcript":"%s"}' \
    "$SLUG" "$FIRST_NAME" "$MP3" "$STATUS" "${TRANSCRIPT:0:500}" >> "$REPORT"
done

echo "]," >> "$REPORT"
echo "\"summary\":{\"pass\":$PASS,\"fail\":$FAIL,\"total\":${#LEADS[@]}}}" >> "$REPORT"

echo ""
echo "=== WHISPER CHECK COMPLETE ==="
echo "PASS: $PASS / ${#LEADS[@]}"
echo "FAIL: $FAIL / ${#LEADS[@]}"
echo "Report: $REPORT"

rm -rf "$TMPDIR"
