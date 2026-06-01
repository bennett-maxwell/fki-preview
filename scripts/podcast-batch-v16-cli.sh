#!/usr/bin/env bash
# podcast-batch-v16-cli.sh — Uses notebooklm CLI directly (SDK add_text is broken).
# For each lead: create notebook → add source via CLI → trigger audio → poll → download.
# Run: bash scripts/podcast-batch-v16-cli.sh
set -o pipefail

REPO=/Users/openclaw/fki-preview
PODCASTS="$REPO/podcasts"
NLM="$REPO/.venv/bin/notebooklm"
MIN_MP3_BYTES=5242880  # 5MB
MAX_POLL_MIN=10

# Lead → (slug, display name, first name for whisper check)
LEADS=(
  "branson-maxwell|Branson Maxwell|branson"
  "brent-attaway|Brent Attaway|brent"
  "brittney-warnick|Brittney Warnick|brittney"
  "chris-lpnw|Chris LPNW|chris"
  "court-lundberg|Court Lundberg|court"
  "dave-wood|Dave Wood|dave"
  "melissa-tash-srp|Melissa Tash|melissa"
  "paul-muus|Paul Muus|paul"
  "rey-31consulting|Rey 31Consulting|rey"
  "zachary-red-sands|Zachary Red Sands|zachary"
)

# Pre-seeded test notebook (Brent already generating)
declare -A NOTEBOOK_OVERRIDE=(
  ["brent-attaway"]="b3bc9123-d146-4d50-8a68-51952fafcc50"
)

echo "=== Podcast Batch v1.6 CLI — $(date) ==="
mkdir -p "$PODCASTS"

# Phase 1: kick off ALL generations in parallel (notebook create + source add + gen trigger)
declare -A NOTEBOOK_IDS
for entry in "${LEADS[@]}"; do
  SLUG=${entry%%|*}
  rest=${entry#*|}
  NAME=${rest%%|*}
  SOURCE_DOC="${PODCASTS}/${SLUG}-podcast-source.md"

  if [ ! -f "$SOURCE_DOC" ]; then
    echo "[$SLUG] SKIP: no source doc"
    continue
  fi

  if [ -n "${NOTEBOOK_OVERRIDE[$SLUG]:-}" ]; then
    NB="${NOTEBOOK_OVERRIDE[$SLUG]}"
    echo "[$SLUG] Using pre-seeded notebook: $NB"
    NOTEBOOK_IDS["$SLUG"]="$NB"
    continue
  fi

  echo "[$SLUG] Creating notebook..."
  NB=$("$NLM" create "FKI Blueprint v1.6 — $NAME" --json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['notebook']['id'])" 2>/dev/null)

  if [ -z "$NB" ]; then
    echo "[$SLUG] ERROR creating notebook"
    continue
  fi

  echo "[$SLUG] Notebook: $NB. Adding source..."
  "$NLM" source add "$SOURCE_DOC" -n "$NB" --type text --title "$NAME AI Blueprint" --json >/dev/null 2>&1

  sleep 10  # let source ingest

  echo "[$SLUG] Triggering audio gen..."
  GEN_RESULT=$("$NLM" generate audio -n "$NB" --json --retry 2 2>&1 | tail -10)
  echo "[$SLUG] Gen result: $GEN_RESULT"

  NOTEBOOK_IDS["$SLUG"]="$NB"
  sleep 5  # gentle rate limit
done

echo ""
echo "=== Phase 1 complete: all gens triggered. Notebook map: ==="
for slug in "${!NOTEBOOK_IDS[@]}"; do
  echo "  $slug -> ${NOTEBOOK_IDS[$slug]}"
done

# Phase 2: poll for completion, download each as it finishes
echo ""
echo "=== Phase 2: polling and downloading ==="
DEADLINE=$(($(date +%s) + MAX_POLL_MIN * 60))
DONE=()
FAILED=()

while [ $(date +%s) -lt $DEADLINE ] && [ $((${#DONE[@]} + ${#FAILED[@]})) -lt ${#NOTEBOOK_IDS[@]} ]; do
  for slug in "${!NOTEBOOK_IDS[@]}"; do
    # Skip already done
    if [[ " ${DONE[*]:-} " =~ " ${slug} " ]] || [[ " ${FAILED[*]:-} " =~ " ${slug} " ]]; then
      continue
    fi

    NB="${NOTEBOOK_IDS[$slug]}"
    MP3="${PODCASTS}/${slug}-blueprint-podcast.mp3"

    # Skip if already downloaded
    if [ -f "$MP3" ] && [ "$(stat -f%z "$MP3" 2>/dev/null || echo 0)" -gt $MIN_MP3_BYTES ]; then
      DONE+=("$slug")
      continue
    fi

    # List artifacts
    ARTIFACT_INFO=$("$NLM" artifact list -n "$NB" --json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    arts = data.get('artifacts', [])
    audio = [a for a in arts if 'audio' in a.get('type', '').lower() or a.get('artifact_type') == 'AUDIO_OVERVIEW']
    if not audio:
        print('NONE')
    else:
        a = audio[0]
        print(f\"{a.get('id','')}|{a.get('status','')}\")
except Exception as e:
    print(f'ERR|{e}')
" 2>/dev/null)

    AID=${ARTIFACT_INFO%%|*}
    STATUS=${ARTIFACT_INFO##*|}

    case "$STATUS" in
      ready|completed|COMPLETED|DONE|done)
        echo "[$slug] Audio ready (artifact $AID), downloading..."
        "$NLM" download audio "$MP3" -n "$NB" -a "$AID" 2>&1 | tail -3
        if [ -f "$MP3" ] && [ "$(stat -f%z "$MP3")" -gt $MIN_MP3_BYTES ]; then
          DONE+=("$slug")
          echo "[$slug] DOWNLOADED ($(stat -f%z "$MP3") bytes)"
        else
          FAILED+=("$slug")
          echo "[$slug] DOWNLOAD FAILED"
        fi
        ;;
      failed|FAILED|error|ERROR)
        FAILED+=("$slug")
        echo "[$slug] GEN FAILED (status=$STATUS)"
        ;;
      *)
        # still pending — silent
        ;;
    esac
  done

  REMAINING=$((${#NOTEBOOK_IDS[@]} - ${#DONE[@]} - ${#FAILED[@]}))
  if [ $REMAINING -gt 0 ]; then
    echo "[$(date +%H:%M:%S)] $REMAINING leads still generating... (done=${#DONE[@]} failed=${#FAILED[@]})"
    sleep 30
  fi
done

echo ""
echo "=== FINAL ==="
echo "DONE (${#DONE[@]}): ${DONE[*]:-none}"
echo "FAILED (${#FAILED[@]}): ${FAILED[*]:-none}"
echo "Log saved to /tmp/podcast-batch-v16-cli.log"
