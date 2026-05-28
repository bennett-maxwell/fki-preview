#!/bin/bash
# Nightly podcast URL health check — runs at 2AM, alerts #leo-auto on failure
# LaunchAgent: com.advaita.blueprint-podcast-health.plist

set -uo pipefail

LEADS_DIR="$(cd "$(dirname "$0")/.." && pwd)/leads"
LOG="$HOME/.openclaw/logs/blueprint-podcast-health.jsonl"
NO_SLACK=0
NO_WRITE=0
DRY_RUN=0
FAILURES=()

while [ "$#" -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=1
            NO_SLACK=1
            NO_WRITE=1
            shift
            ;;
        --no-slack)
            NO_SLACK=1
            shift
            ;;
        --no-write)
            NO_WRITE=1
            shift
            ;;
        --leads-dir)
            if [ -z "${2:-}" ]; then
                echo "ERROR: --leads-dir requires a path" >&2
                exit 2
            fi
            LEADS_DIR="$2"
            shift 2
            ;;
        --log)
            if [ -z "${2:-}" ]; then
                echo "ERROR: --log requires a path" >&2
                exit 2
            fi
            LOG="$2"
            shift 2
            ;;
        *)
            echo "ERROR: Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

if [ ! -d "$LEADS_DIR" ]; then
    echo "ERROR: leads dir missing: $LEADS_DIR" >&2
    exit 1
fi

for f in "$LEADS_DIR"/*.json; do
    [ -f "$f" ] || continue
    slug=$(basename "$f" .json)
    podcast_url=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('podcast_url',''))" 2>/dev/null)
    
    if [ -z "$podcast_url" ]; then
        FAILURES+=("$slug:empty_url")
        continue
    fi
    
    if [[ "$podcast_url" == mock://* ]]; then
        code="${podcast_url#mock://}"
    else
        code=$(curl -sI -o /dev/null -w "%{http_code}" --max-time 10 "$podcast_url" 2>/dev/null || echo "000")
    fi
    ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    line="{\"ts\":\"$ts\",\"slug\":\"$slug\",\"url\":\"$podcast_url\",\"http\":\"$code\"}"
    if [ "$NO_WRITE" -eq 1 ]; then
        echo "NO_WRITE: $line"
    else
        echo "$line" >> "$LOG"
    fi
    
    if [ "$code" != "200" ]; then
        FAILURES+=("$slug:$code")
    fi
done

if [ ${#FAILURES[@]} -gt 0 ]; then
    # Alert via Slack #leo-auto
    MSG="⚠️ Blueprint podcast health: ${#FAILURES[@]} failure(s) — $(IFS=', '; echo "${FAILURES[*]}")"
    if [ "$NO_SLACK" -eq 1 ]; then
        echo "NO_SLACK: Would alert #leo-auto: $MSG"
    else
        ~/bin/slack-post.sh "#leo-auto" "$MSG" 2>/dev/null || true
    fi
    exit 1
fi

if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY_RUN: All podcast URLs healthy at $(date)"
else
    echo "All podcast URLs healthy at $(date)"
fi
exit 0
