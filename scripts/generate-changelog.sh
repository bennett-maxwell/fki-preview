#!/bin/bash
# Blueprint AI Pipeline -- Auto-generate Changelog from Git Commits
# Usage: ./generate-changelog.sh [--since "7 days ago"] [--format html|text]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SINCE="${2:-7 days ago}"
FORMAT="text"

if [ "${1:-}" = "--help" ]; then
    echo "Usage: $0 [--since \"N days ago\"] [--format html|text]"
    echo ""
    echo "Generates a changelog from git commits."
    echo "Default: last 7 days, text format."
    exit 0
fi

# Parse args
while [ $# -gt 0 ]; do
    case "$1" in
        --since) SINCE="$2"; shift 2 ;;
        --format) FORMAT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

cd "$REPO_DIR"

if [ ! -d ".git" ]; then
    echo "ERROR: Not a git repository"
    exit 1
fi

echo "=== Blueprint AI Pipeline Changelog ==="
echo "Since: $SINCE"
echo "Generated: $(date)"
echo ""

# Categorize commits
BLUEPRINTS=$(git log --since="$SINCE" --oneline --grep="Blueprint" 2>/dev/null || echo "")
WEBSITES=$(git log --since="$SINCE" --oneline --grep="website" 2>/dev/null || echo "")
PIPELINE=$(git log --since="$SINCE" --oneline --grep="pipeline\|batch\|fix\|improve" 2>/dev/null || echo "")
ALL=$(git log --since="$SINCE" --oneline 2>/dev/null || echo "")

COMMIT_COUNT=$(echo "$ALL" | grep -c "." 2>/dev/null || echo "0")
echo "Total commits: $COMMIT_COUNT"
echo ""

if [ -n "$BLUEPRINTS" ]; then
    echo "-- Blueprints --"
    echo "$BLUEPRINTS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  $line"
    done
    echo ""
fi

if [ -n "$WEBSITES" ]; then
    echo "-- Websites --"
    echo "$WEBSITES" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  $line"
    done
    echo ""
fi

if [ -n "$PIPELINE" ]; then
    echo "-- Pipeline --"
    echo "$PIPELINE" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  $line"
    done
    echo ""
fi

# File change summary
echo "-- Files Changed --"
git diff --stat "HEAD~${COMMIT_COUNT}" HEAD 2>/dev/null | tail -1 || echo "  (no changes)"
echo ""
echo "=== End Changelog ==="
