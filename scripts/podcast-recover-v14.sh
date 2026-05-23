#!/usr/bin/env bash
# podcast-recover-v14.sh — Download MP3s from existing notebooks, create+generate for missing
# Notebooks already exist from batch runs; just need correct download syntax

PODCASTS=/Users/openclaw/fki-preview/podcasts
LOGFILE=/Users/openclaw/.openclaw/logs/podcast-recover-v14.log
NLM=/Users/openclaw/fki-preview/.venv/bin/notebooklm
REPO=/Users/openclaw/fki-preview
TRACKER=$REPO/podcasts/tracker.html
BRIDGE=/Users/openclaw/fki-preview/.venv/bin/python3
BRIDGE_SCRIPT=/Users/openclaw/fki-preview/scripts/chrome-cookie-bridge.py

exec >> "$LOGFILE" 2>&1

echo "=== Podcast Recovery v1.4 — $(date) ==="

# slug:notebook_id:name — use first/most recent notebook per lead
# Branson already has MP3, skipped
declare -a JOBS=(
  "zachary-red-sands:a506f59d-0955-4f35-b0f7-d992642e1952:Zak Oldham"
  "brittney-warnick:88389d54-235b-4180-a4a6-4fda55721e0a:Brittney Warnick"
  "chris-lpnw:4b4389d2-8d3f-4a1a-88c3-9ed8f12bad1e:Chris LPNW"
  "rj-kitchenguard:573f8734-2f6d-4173-89dc-1702ddb6d1dd:RJ Schultz"
  "paul-muus:d053a771-daf2-44ed-a835-1cc93536008c:Paul Muus"
  "brent-attaway:c2700efe-0218-423b-ba02-e857c551f499:Brent Attaway"
  "dave-wood:334e8704-f8f3-474c-9f39-c2ee17e955a2:Dave Wood"
  "melissa-tash-srp:55c74df2-d671-4fb7-b57d-94b74d5b4883:Melissa Tash"
  "court-lundberg:7a0a4208-d727-46e1-9122-93dd2a277ee8:Court Lundberg"
)

# Rey needs fresh notebook (not in any batch log)
REY_NEEDS_CREATE=true

update_tracker() {
  local slug="$1" url="$2"
  sed -i '' "s|id=\"badge-${slug}\"[^<]*<[^<]*>|id=\"badge-${slug}\">Ready</span></div><div class=\"status\"><a class=\"listen-btn\" href=\"${url}\" target=\"_blank\">Listen</a>|g" "$TRACKER" 2>/dev/null
  local ready_count
  ready_count=$(grep -c 'badge-ready' "$TRACKER" 2>/dev/null || echo 0)
  sed -i '' "s|<div class=\"num\" id=\"ready\">.*</div>|<div class=\"num\" id=\"ready\">${ready_count}</div>|" "$TRACKER" 2>/dev/null
  cd "$REPO" && git add podcasts/tracker.html && git commit -m "tracker: ${slug} ready" 2>/dev/null
  echo "Tracker updated: $slug"
}

push_mp3() {
  local slug="$1" mp3="$2"
  cd "$REPO"
  git add "podcasts/${slug}-v14.mp3"
  git commit -m "podcast: ${slug} v1.4 ready"
  git push origin main
  echo "Pushed: $slug"
}

# Refresh auth
"$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR"

# Process existing notebooks
for job in "${JOBS[@]}"; do
  SLUG=$(echo "$job" | cut -d: -f1)
  NB_ID=$(echo "$job" | cut -d: -f2)
  NAME=$(echo "$job" | cut -d: -f3)
  MP3_OUT="${PODCASTS}/${SLUG}-v14.mp3"

  if [ -f "$MP3_OUT" ]; then
    MP3_SIZE=$(du -k "$MP3_OUT" | cut -f1)
    echo "SKIP $SLUG — already have ${MP3_SIZE}KB"
    URL="https://bennett-maxwell.github.io/fki-preview/podcasts/${SLUG}-v14.mp3"
    push_mp3 "$SLUG" "$MP3_OUT" 2>/dev/null
    update_tracker "$SLUG" "$URL"
    continue
  fi

  echo ""
  echo "--- [$(date '+%H:%M:%S')] Downloading: $NAME ($SLUG) from $NB_ID ---"
  "$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR"

  # Try download from existing notebook (audio may already be ready)
  "$NLM" download audio -n "$NB_ID" "$MP3_OUT" --force 2>&1 | head -5

  if [ ! -f "$MP3_OUT" ]; then
    echo "No audio yet for $NB_ID — generating..."
    GEN_RESULT=$("$NLM" generate audio --json -n "$NB_ID" 2>&1)
    TASK_ID=$(echo "$GEN_RESULT" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("task_id",""))' 2>/dev/null)
    if [ -z "$TASK_ID" ]; then
      echo "ERROR: Could not get task_id for $SLUG: $GEN_RESULT"
      continue
    fi
    echo "Waiting for audio: $TASK_ID"
    "$NLM" artifact wait "$TASK_ID" -n "$NB_ID" --timeout 900 2>&1
    "$NLM" download audio -n "$NB_ID" "$MP3_OUT" --force 2>&1 | head -5
  fi

  if [ -f "$MP3_OUT" ]; then
    MP3_SIZE=$(du -k "$MP3_OUT" | cut -f1)
    echo "OK: ${SLUG} — ${MP3_SIZE}KB"
    URL="https://bennett-maxwell.github.io/fki-preview/podcasts/${SLUG}-v14.mp3"
    push_mp3 "$SLUG" "$MP3_OUT"
    update_tracker "$SLUG" "$URL"
    echo "DONE: $NAME -> $URL"
  else
    echo "ERROR: Download failed for $SLUG"
  fi
done

# Handle Rey separately (needs fresh notebook)
echo ""
echo "--- [$(date '+%H:%M:%S')] Processing Rey 31 Consulting (fresh notebook) ---"
"$BRIDGE" "$BRIDGE_SCRIPT" 2>&1 | grep -E "VALID|ERROR"

REY_SLUG="rey-31-consulting"
REY_MP3="${PODCASTS}/${REY_SLUG}-v14.mp3"
REY_SOURCE="${PODCASTS}/${REY_SLUG}-podcast-source.md"

if [ -f "$REY_MP3" ]; then
  echo "SKIP rey — already have MP3"
else
  if [ ! -f "$REY_SOURCE" ]; then
    echo "ERROR: Rey source doc missing at $REY_SOURCE"
  else
    SIZE_KB=$(du -k "$REY_SOURCE" | cut -f1)
    echo "Creating notebook for Rey (${SIZE_KB}KB source)..."
    CREATE_RESULT=$("$NLM" create "FKI Blueprint - Rey 31 Consulting - v1.4" --json 2>&1)
    NB_ID=$(echo "$CREATE_RESULT" | python3 -c 'import sys,json; d=json.load(sys.stdin); nb=d.get("notebook",d); print(nb.get("id",""))' 2>/dev/null)
    if [ -z "$NB_ID" ]; then
      echo "ERROR: Could not create Rey notebook: $CREATE_RESULT"
    else
      echo "Notebook: $NB_ID"
      "$NLM" source add "$REY_SOURCE" -n "$NB_ID" 2>&1 | head -3
      GEN_RESULT=$("$NLM" generate audio --json -n "$NB_ID" 2>&1)
      TASK_ID=$(echo "$GEN_RESULT" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("task_id",""))' 2>/dev/null)
      echo "Waiting for audio: $TASK_ID"
      "$NLM" artifact wait "$TASK_ID" -n "$NB_ID" --timeout 900 2>&1
      "$NLM" download audio -n "$NB_ID" "$REY_MP3" --force 2>&1 | head -5
      if [ -f "$REY_MP3" ]; then
        MP3_SIZE=$(du -k "$REY_MP3" | cut -f1)
        echo "OK: rey — ${MP3_SIZE}KB"
        URL="https://bennett-maxwell.github.io/fki-preview/podcasts/${REY_SLUG}-v14.mp3"
        push_mp3 "$REY_SLUG" "$REY_MP3"
        update_tracker "$REY_SLUG" "$URL"
        echo "DONE: Rey -> $URL"
      else
        echo "ERROR: Rey download failed"
      fi
    fi
  fi
fi

# Final push of Branson (already have it)
BRANSON_MP3="${PODCASTS}/branson-maxwell-v14.mp3"
if [ -f "$BRANSON_MP3" ] && ! git -C "$REPO" ls-files --error-unmatch "podcasts/branson-maxwell-v14.mp3" 2>/dev/null; then
  echo ""
  echo "Pushing pre-downloaded Branson MP3..."
  cd "$REPO" && git add "podcasts/branson-maxwell-v14.mp3" && git commit -m "podcast: branson-maxwell v1.4 ready" && git push origin main
  URL="https://bennett-maxwell.github.io/fki-preview/podcasts/branson-maxwell-v14.mp3"
  update_tracker "branson-maxwell" "$URL"
fi

echo ""
echo "=== Recovery Complete — $(date) ==="
echo "Tracker: https://bennett-maxwell.github.io/fki-preview/podcasts/tracker.html"
