#!/usr/bin/env bash
# podcast-batch-v14.sh — Regenerate all lead podcasts under skill v1.4
# Run once notebooklm auth is restored via: notebooklm login
# Auto-updates tracker.html as each podcast completes

TRACKER=/Users/openclaw/fki-preview/podcasts/tracker.html
PODCASTS=/Users/openclaw/fki-preview/podcasts
LOGFILE=/Users/openclaw/.openclaw/logs/podcast-generation-log.json
NLM=/Users/openclaw/fki-preview/.venv/bin/notebooklm
REPO=/Users/openclaw/fki-preview

LEADS=(
  'zachary-red-sands:Zak Oldham:badge-zachary'
  'branson-maxwell:Branson Maxwell:badge-branson'
  'brittney-warnick:Brittney Warnick:badge-brittney'
  'chris-lpnw:Chris LPNW:badge-chris'
  'rey-31-consulting:Rey 31 Consulting:badge-rey'
  'court-lundberg:Court Lundberg:badge-court'
  'melissa-tash-srp:Melissa Tash:badge-melissa'
  'dave-wood:Dave Wood:badge-dave'
  'brent-attaway:Brent Attaway:badge-brent'
  'paul-muus:Paul Muus:badge-paul'
  'rj-kitchenguard:RJ Schultz:badge-rj'
)

update_tracker() {
  local slug="$1" status="$2" url="$3"
  if [ "$status" = "ready" ] && [ -n "$url" ]; then
    sed -i '' "s|<span class=\"badge badge-queued\" id=\"badge-${slug}\">Queued</span>|<span class=\"badge badge-ready\">Ready</span></div><div class=\"status\"><a class=\"listen-btn\" href=\"${url}\" target=\"_blank\">Listen</a>|g" "$TRACKER" 2>/dev/null
    sed -i '' "s|<span class=\"badge badge-queued\">Queued</span>|<span class=\"badge badge-queued\">Queued</span>|g" "$TRACKER" 2>/dev/null
  elif [ "$status" = "progress" ]; then
    sed -i '' "s|badge-queued\">Queued|badge-progress\">Generating...|g" "$TRACKER" 2>/dev/null
  fi
  # Update stats
  local ready_count=$(grep -c 'badge-ready' "$TRACKER" || echo 0)
  local queued_count=$(grep -c 'badge-queued' "$TRACKER" || echo 0)
  sed -i '' "s|<div class=\"num\" id=\"ready\">.*</div>|<div class=\"num\" id=\"ready\">${ready_count}</div>|g" "$TRACKER" 2>/dev/null
  sed -i '' "s|<div class=\"num\" id=\"queued\">.*</div>|<div class=\"num\" id=\"queued\">${queued_count}</div>|g" "$TRACKER" 2>/dev/null
  
  cd "$REPO" && git add podcasts/tracker.html && git commit -m "tracker: ${slug} ${status}" 2>/dev/null && git push origin main 2>/dev/null
  echo "[$(date '+%H:%M:%S')] Tracker updated: ${slug} -> ${status}"
}

log_version() {
  local slug="$1" url="$2" notebook_id="$3" size_kb="$4"
  local entry="{\"timestamp\":\"$(date -u +%FT%TZ)\",\"lead_slug\":\"${slug}\",\"skill_version\":\"1.4\",\"source_doc_kb\":${size_kb},\"notebooklm_notebook_id\":\"${notebook_id}\",\"mp3_github_url\":\"${url}\",\"tracking_page_updated\":true,\"tone_rules_applied\":[\"rule10_soft_effort\",\"rule11_no_failure_framing\"]}"
  python3 -c "
import json, sys
log_path = '/Users/openclaw/.openclaw/logs/podcast-generation-log.json'
try:
    with open(log_path) as f: log = json.load(f)
except: log = []
log.append(json.loads(sys.argv[1]))
with open(log_path, 'w') as f: json.dump(log, f, indent=2)
print('Version logged')
" "$entry" 2>/dev/null
}

echo "=== Podcast Batch v1.4 Starting - $(date) ==="
echo "Processing ${#LEADS[@]} leads sequentially"

# Check auth first
AUTH_TEST=$("$NLM" list --json 2>&1)
if echo "$AUTH_TEST" | grep -q 'error'; then
  echo "BLOCKED: notebooklm auth expired. Run: notebooklm login"
  echo "Then re-run this script."
  exit 1
fi

for lead_entry in "${LEADS[@]}"; do
  SLUG=$(echo "$lead_entry" | cut -d: -f1)
  NAME=$(echo "$lead_entry" | cut -d: -f2)
  
  SOURCE_DOC="${PODCASTS}/${SLUG}-podcast-source.md"
  
  if [ ! -f "$SOURCE_DOC" ]; then
    echo "SKIP $SLUG - no source doc found"
    continue
  fi
  
  echo ""
  echo "--- [$(date '+%H:%M:%S')] Processing: $NAME ($SLUG) ---"
  
  SIZE_KB=$(du -k "$SOURCE_DOC" | cut -f1)
  
  # Create notebook
  NOTEBOOK_NAME="FKI Blueprint - $NAME - v1.4"
  echo "Creating notebook: $NOTEBOOK_NAME"
  CREATE_RESULT=$("$NLM" create "$NOTEBOOK_NAME" --json 2>&1)
  NOTEBOOK_ID=$(echo "$CREATE_RESULT" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("id",""))' 2>/dev/null)
  
  if [ -z "$NOTEBOOK_ID" ]; then
    echo "ERROR: Could not create notebook for $SLUG"
    echo "$CREATE_RESULT"
    continue
  fi
  
  echo "Notebook created: $NOTEBOOK_ID"
  "$NLM" use "$NOTEBOOK_ID" 2>/dev/null
  
  # Add source doc
  echo "Adding source doc (${SIZE_KB}KB)..."
  "$NLM" source add "$SOURCE_DOC" 2>/dev/null
  
  # Generate audio
  echo "Generating audio..."
  "$NLM" generate audio 2>/dev/null
  
  # Wait for audio
  echo "Waiting for audio to complete..."
  "$NLM" artifact wait 2>/dev/null
  
  # Download audio
  MP3_OUT="${PODCASTS}/${SLUG}-v14.mp3"
  echo "Downloading MP3..."
  "$NLM" download audio --output "$MP3_OUT" 2>/dev/null
  
  if [ -f "$MP3_OUT" ]; then
    MP3_SIZE=$(du -k "$MP3_OUT" | cut -f1)
    echo "MP3 downloaded: ${MP3_SIZE}KB"
    
    # Push to GitHub Pages
    cd "$REPO"
    git add "podcasts/${SLUG}-v14.mp3"
    git commit -m "podcast: ${SLUG} v1.4 ready (${MP3_SIZE}KB)" 2>/dev/null
    git push origin main 2>/dev/null
    
    URL="https://bennett-maxwell.github.io/fki-preview/podcasts/${SLUG}-v14.mp3"
    
    # Update tracker
    update_tracker "$SLUG" "ready" "$URL"
    
    # Log version
    log_version "$SLUG" "$URL" "$NOTEBOOK_ID" "$SIZE_KB"
    
    echo "DONE: $NAME -> $URL"
  else
    echo "ERROR: MP3 download failed for $SLUG"
  fi
done

echo ""
echo "=== Batch Complete - $(date) ==="
echo "Tracker: https://bennett-maxwell.github.io/fki-preview/podcasts/tracker.html"
