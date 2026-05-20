#!/bin/bash
# Nightly podcast URL health check — runs at 2AM, alerts #leo-auto on failure
# LaunchAgent: com.advaita.blueprint-podcast-health.plist

set -uo pipefail

LEADS_DIR="$(cd "$(dirname "$0")/.." && pwd)/leads"
LOG="$HOME/.openclaw/logs/blueprint-podcast-health.jsonl"
FAILURES=()

for f in "$LEADS_DIR"/*.json; do
    [ -f "$f" ] || continue
    slug=$(basename "$f" .json)
    podcast_url=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('podcast_url',''))" 2>/dev/null)
    
    if [ -z "$podcast_url" ]; then
        FAILURES+=("$slug:empty_url")
        continue
    fi
    
    code=$(curl -sI -o /dev/null -w "%{http_code}" --max-time 10 "$podcast_url" 2>/dev/null || echo "000")
    ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    echo "{\"ts\":\"$ts\",\"slug\":\"$slug\",\"url\":\"$podcast_url\",\"http\":\"$code\"}" >> "$LOG"
    
    if [ "$code" != "200" ]; then
        FAILURES+=("$slug:$code")
    fi
done

if [ ${#FAILURES[@]} -gt 0 ]; then
    # Alert via Slack #leo-auto
    MSG="⚠️ Blueprint podcast health: ${#FAILURES[@]} failure(s) — $(IFS=', '; echo "${FAILURES[*]}")"
    ~/bin/slack-post.sh "#leo-auto" "$MSG" 2>/dev/null || true
    exit 1
fi

echo "All podcast URLs healthy at $(date)"
exit 0
