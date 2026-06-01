#!/usr/bin/env bash
# podcast-batch-v14b.sh — Fresh notebooks for 8 leads that had empty notebooks
# Runs in parallel with recover script (different leads)

PODCASTS=/Users/openclaw/fki-preview/podcasts
NLM=/Users/openclaw/fki-preview/.venv/bin/notebooklm
REPO=/Users/openclaw/fki-preview
BRIDGE=/Users/openclaw/fki-preview/.venv/bin/python3
BRIDGE_SCRIPT=/Users/openclaw/fki-preview/scripts/chrome-cookie-bridge.py

LEADS=(
  'chris-lpnw:Chris LPNW'
  'rj-kitchenguard:RJ Schultz'
  'paul-muus:Paul Muus'
  'brent-attaway:Brent Attaway'
  'dave-wood:Dave Wood'
  'melissa-tash-srp:Melissa Tash'
  'court-lundberg:Court Lundberg'
)

echo "=== Batch v14b Starting — $(date) ==="

for lead_entry in "${LEADS[@]}"; do
  SLUG=$(echo "$lead_entry" | cut -d: -f1)
  NAME=$(echo "$lead_entry" | cut -d: -f2)
  MP3_OUT="${PODCASTS}/${SLUG}-v14.mp3"
  SOURCE_DOC="${PODCASTS}/${SLUG}-podcast-source.md"

  if [ -f "$MP3_OUT" ]; then
    echo "SKIP $SLUG — already have MP3"
    continue
  fi

  if [ ! -f "$SOURCE_DOC" ]; then
    echo "ERROR: No source doc for $SLUG"
    continue
  fi

  SIZE_KB=$(du -k "$SOURCE_DOC" | cut -f1)
  echo ""
  echo "--- [$(date '+%H:%M:%S')] $NAME ($SLUG) ${SIZE_KB}KB ---"

  # Refresh auth
  "$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR"

  # Create fresh notebook
  NB_NAME="FKI Blueprint - $NAME - v1.4b"
  CREATE_RESULT=$("$NLM" create "$NB_NAME" --json 2>&1)
  NB_ID=$(echo "$CREATE_RESULT" | python3 -c 'import sys,json; d=json.load(sys.stdin); nb=d.get("notebook",d); print(nb.get("id",""))' 2>/dev/null)

  if [ -z "$NB_ID" ]; then
    echo "ERROR: Could not create notebook: $CREATE_RESULT"
    continue
  fi
  echo "Notebook: $NB_ID"

  # Add source
  ADD_RESULT=$("$NLM" source add "$SOURCE_DOC" -n "$NB_ID" 2>&1)
  echo "$ADD_RESULT" | head -2

  # Generate audio
  GEN_RESULT=$("$NLM" generate audio --json -n "$NB_ID" 2>&1)
  TASK_ID=$(echo "$GEN_RESULT" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("task_id",""))' 2>/dev/null)

  if [ -z "$TASK_ID" ]; then
    echo "ERROR: No task_id: $GEN_RESULT"
    continue
  fi
  echo "Audio generating: $TASK_ID"

  # Wait (up to 15 min)
  "$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR"
  "$NLM" artifact wait "$TASK_ID" -n "$NB_ID" --timeout 900 2>&1

  # Download
  "$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR"
  "$NLM" download audio -n "$NB_ID" "$MP3_OUT" --force 2>&1 | head -5

  if [ -f "$MP3_OUT" ]; then
    MP3_SIZE=$(du -k "$MP3_OUT" | cut -f1)
    echo "OK: $SLUG — ${MP3_SIZE}KB"
    cd "$REPO"
    git pull origin main 2>/dev/null
    git add "podcasts/${SLUG}-v14.mp3"
    git commit -m "podcast: ${SLUG} v1.4 ready (${MP3_SIZE}KB)"
    git push origin main
    echo "DONE: $NAME -> https://bennett-maxwell.github.io/fki-preview/podcasts/${SLUG}-v14.mp3"
  else
    echo "ERROR: Download failed for $SLUG"
  fi
done

echo ""
echo "=== Batch v14b Complete — $(date) ==="
