#!/usr/bin/env bash
# podcast-batch-v15.sh — Blueprint AI Podcast v1.5 full batch
# Uses rebuilt 18KB+ source docs with HOST DIRECTIVE + prompt_1/2/3
# Council v19: 10 improvements applied. Auth via chrome-cookie-bridge.
# Run: bash scripts/podcast-batch-v15.sh

set -euo pipefail

REPO=/Users/openclaw/fki-preview
PODCASTS="$REPO/podcasts"
NLM="$REPO/.venv/bin/notebooklm"
BRIDGE_SCRIPT="$REPO/scripts/chrome-cookie-bridge.py"
BRIDGE="$REPO/.venv/bin/python3"
MIN_SIZE_BYTES=5242880  # 5MB — Council #5

LEADS=(
  'branson-maxwell:Branson Maxwell'
  'brent-attaway:Brent Attaway'
  'brittney-warnick:Brittney Warnick'
  'chris-lpnw:Chris LPNW'
  'court-lundberg:Court Lundberg'
  'dave-wood:Dave Wood'
  'melissa-tash-srp:Melissa Tash'
  'paul-muus:Paul Muus'
  'rey-31consulting:Rey 31consulting'
  'zachary-red-sands:Zachary Red Sands'
)

echo "=== Podcast Batch v1.5 Starting — $(date) ==="
echo "Source docs: 18KB+ with HOST DIRECTIVE + prompt_1/2/3"
echo ""

VERIFIED=0
FAILED=0
FAILED_LIST=()

for lead_entry in "${LEADS[@]}"; do
  SLUG=$(echo "$lead_entry" | cut -d: -f1)
  NAME=$(echo "$lead_entry" | cut -d: -f2)
  MP3_OUT="${PODCASTS}/${SLUG}-blueprint-podcast.mp3"
  SOURCE_DOC="${PODCASTS}/${SLUG}-podcast-source.md"

  echo "--- [$(date '+%H:%M:%S')] $NAME ($SLUG) ---"

  # Skip if already done and verified
  if [ -f "$MP3_OUT" ]; then
    EXISTING_SIZE=$(stat -f%z "$MP3_OUT" 2>/dev/null || echo "0")
    if [ "$EXISTING_SIZE" -gt "$MIN_SIZE_BYTES" ]; then
      echo "SKIP $SLUG — MP3 already exists and verified (${EXISTING_SIZE} bytes)"
      VERIFIED=$((VERIFIED + 1))
      continue
    fi
    echo "Re-running $SLUG — existing MP3 too small ($EXISTING_SIZE bytes)"
  fi

  # Verify source doc exists and is ≥18KB (Council #7)
  if [ ! -f "$SOURCE_DOC" ]; then
    echo "ERROR: No source doc for $SLUG at $SOURCE_DOC"
    FAILED=$((FAILED + 1))
    FAILED_LIST+=("$SLUG: no source doc")
    continue
  fi
  SOURCE_SIZE=$(stat -f%z "$SOURCE_DOC" 2>/dev/null || echo "0")
  if [ "$SOURCE_SIZE" -lt 18000 ]; then
    echo "ERROR: Source doc too small for $SLUG — ${SOURCE_SIZE} bytes (min 18KB)"
    FAILED=$((FAILED + 1))
    FAILED_LIST+=("$SLUG: source doc ${SOURCE_SIZE} bytes < 18KB")
    continue
  fi
  echo "Source doc: ${SOURCE_SIZE} bytes ✓"

  # Refresh auth before each lead
  "$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR|cookie"

  # Create fresh notebook
  NB_NAME="FKI Blueprint AI v1.5 - $NAME"
  CREATE_RESULT=$("$NLM" create "$NB_NAME" --json 2>&1)
  NB_ID=$(echo "$CREATE_RESULT" | python3 -c 'import sys,json; d=json.load(sys.stdin); nb=d.get("notebook",d); print(nb.get("id",""))' 2>/dev/null)

  if [ -z "$NB_ID" ]; then
    echo "ERROR: Could not create notebook for $SLUG: $CREATE_RESULT"
    FAILED=$((FAILED + 1))
    FAILED_LIST+=("$SLUG: notebook creation failed")
    continue
  fi
  echo "Notebook: $NB_ID"

  # Add source doc
  ADD_RESULT=$("$NLM" source add "$SOURCE_DOC" -n "$NB_ID" 2>&1)
  echo "$ADD_RESULT" | head -2
  # Small wait for source to index
  sleep 10

  # Generate audio
  GEN_RESULT=$("$NLM" generate audio --json -n "$NB_ID" 2>&1)
  TASK_ID=$(echo "$GEN_RESULT" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("task_id",""))' 2>/dev/null)

  if [ -z "$TASK_ID" ]; then
    echo "ERROR: No task_id returned for $SLUG: $GEN_RESULT"
    FAILED=$((FAILED + 1))
    FAILED_LIST+=("$SLUG: audio generation failed to start")
    continue
  fi
  echo "Audio generating: $TASK_ID"

  # Refresh auth again before wait (up to 15 min)
  "$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR"
  "$NLM" artifact wait "$TASK_ID" -n "$NB_ID" --timeout 900 2>&1

  # Refresh auth before download
  "$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR"

  # Download — positional path arg, not --output (Council #6 fix)
  "$NLM" download audio -n "$NB_ID" "$MP3_OUT" --force 2>&1 | head -5

  # Verify file on disk ≥5MB (Council #5)
  if [ ! -f "$MP3_OUT" ]; then
    echo "ERROR: Download reported success but file not found: $MP3_OUT"
    FAILED=$((FAILED + 1))
    FAILED_LIST+=("$SLUG: file not on disk after download")
    continue
  fi

  ACTUAL_SIZE=$(stat -f%z "$MP3_OUT")
  ACTUAL_MB=$(echo "scale=1; $ACTUAL_SIZE / 1048576" | bc)
  if [ "$ACTUAL_SIZE" -lt "$MIN_SIZE_BYTES" ]; then
    echo "ERROR: File too small — ${ACTUAL_MB}MB (min 5MB): $MP3_OUT"
    FAILED=$((FAILED + 1))
    FAILED_LIST+=("$SLUG: file ${ACTUAL_MB}MB < 5MB")
    continue
  fi

  echo "✓ VERIFIED: $SLUG — ${ACTUAL_MB}MB"
  VERIFIED=$((VERIFIED + 1))

  # Commit and push immediately after each verified MP3
  cd "$REPO"
  git pull origin main --rebase 2>/dev/null || true
  git add "podcasts/${SLUG}-blueprint-podcast.mp3"
  git commit -m "podcast v1.5: ${SLUG} ready (${ACTUAL_MB}MB) — HOST DIRECTIVE + prompt_1/2/3"
  git push origin main
  echo "PUSHED: https://bennett-maxwell.github.io/fki-preview/podcasts/${SLUG}-blueprint-podcast.mp3"
  echo ""

  # 30s delay between leads (not 60 — save time, auth is stable)
  sleep 30
done

echo ""
echo "====================================="
echo "BATCH v1.5 COMPLETE — $(date)"
echo "VERIFIED: $VERIFIED / ${#LEADS[@]}"
echo "FAILED:   $FAILED"
if [ ${#FAILED_LIST[@]} -gt 0 ]; then
  echo "Failures:"
  for f in "${FAILED_LIST[@]}"; do
    echo "  - $f"
  done
fi
echo "====================================="
