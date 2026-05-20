#!/bin/bash
# One-click: Generate Paul Muus podcast and push to GitHub Pages
# Usage: ./gen-paul-muus-podcast.sh
# Requires: notebooklm-py installed and authenticated, or ElevenLabs TTS fallback

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="paul-muus"
SOURCE_DOC="$REPO_DIR/podcasts/paul-muus-podcast-source.md"
OUTPUT_MP3="$REPO_DIR/podcasts/${SLUG}.mp3"
PODCAST_URL="https://bennett-maxwell.github.io/fki-preview/podcasts/${SLUG}.mp3"

echo "🎙️ Generating Paul Muus podcast..."

# Try notebooklm-py first
if command -v notebooklm-py &>/dev/null || python3 -c "import notebooklm" &>/dev/null 2>&1; then
    echo "Using notebooklm-py..."
    python3 - << 'PYEOF'
import notebooklm
client = notebooklm.Client()
# Create notebook with source doc
with open('/Users/temp/fki-preview/podcasts/paul-muus-podcast-source.md') as f:
    source = f.read()
nb = client.create_notebook(title="Paul Muus Blueprint AI")
nb.add_source(text=source)
audio = nb.generate_audio()
with open('/Users/temp/fki-preview/podcasts/paul-muus.mp3', 'wb') as f:
    f.write(audio)
print("Podcast generated via NotebookLM")
PYEOF
else
    echo "notebooklm-py not found — using ElevenLabs TTS fallback..."
    # ElevenLabs TTS fallback (requires ELEVENLABS_API_KEY)
    API_KEY="${ELEVENLABS_API_KEY:-$(grep ELEVENLABS ~/.openclaw/.env 2>/dev/null | cut -d= -f2)}"
    TEXT=$(cat "$SOURCE_DOC" | head -500)
    if [ -n "$API_KEY" ]; then
        curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" \
          -H "xi-api-key: $API_KEY" \
          -H "Content-Type: application/json" \
          -d "{\"text\": \"$(echo "$TEXT" | tr '"' "'")\", \"model_id\": \"eleven_monolingual_v1\"}" \
          --output "$OUTPUT_MP3"
    else
        echo "❌ No TTS API key found. Manual generation required."
        exit 1
    fi
fi

echo "✅ MP3 generated: $OUTPUT_MP3"

# Update lead profile
python3 -c "
import json
path = '/Users/temp/fki-preview/leads/paul-muus.json'
d = json.load(open(path))
d['podcast_url'] = '$PODCAST_URL'
d['podcast_carry_forward'] = False
d['status'] = 'v8_improved'
json.dump(d, open(path, 'w'), indent=2)
print('Lead profile updated')
"

# Push to GitHub
cd "$REPO_DIR"
git add "podcasts/${SLUG}.mp3" "leads/${SLUG}.json"
git commit -m "Add Paul Muus podcast + update profile"
git push origin main

echo "🚀 Paul Muus podcast live at: $PODCAST_URL"
