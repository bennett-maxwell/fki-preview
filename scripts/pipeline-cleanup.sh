#!/bin/bash
# Blueprint AI Pipeline -- Cleanup stale/incomplete artifacts
# Usage: ./pipeline-cleanup.sh [--dry-run] [--max-age-days 30]
#
# Identifies:
#   - Website dirs with no matching lead profile
#   - Empty or undersized output files
#   - Stale log files older than max-age-days
#   - Orphaned delivery emails with no matching lead

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$HOME/.openclaw/logs"

DRY_RUN=false
MAX_AGE_DAYS=30

# Parse args
if [ "${1:-}" = "--help" ]; then
    echo "Usage: $0 [--dry-run] [--max-age-days N]"
    echo ""
    echo "Cleans up stale pipeline artifacts:"
    echo "  - Website dirs with no matching lead profile"
    echo "  - Empty or undersized output files (< 1KB)"
    echo "  - Stale log files older than N days (default: 30)"
    echo "  - Orphaned delivery emails"
    echo ""
    echo "Options:"
    echo "  --dry-run          Show what would be removed without removing"
    echo "  --max-age-days N   Max age for log files (default: 30)"
    exit 0
fi

for arg in "$@"; do
    [ "$arg" = "--dry-run" ] && DRY_RUN=true
done

# Parse --max-age-days
while [ $# -gt 0 ]; do
    case "$1" in
        --max-age-days) MAX_AGE_DAYS="$2"; shift 2 ;;
        *) shift ;;
    esac
done

echo "=== Pipeline Cleanup ==="
echo "Date: $(date)"
echo "Dry run: $DRY_RUN"
echo "Max log age: ${MAX_AGE_DAYS} days"
echo ""

REMOVED=0
WOULD_REMOVE=0

# Collect known slugs from lead profiles
KNOWN_SLUGS=()
for profile in "$REPO_DIR"/leads/*.json; do
    [ -f "$profile" ] || continue
    S=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('slug',''))" "$profile" 2>/dev/null || echo "")
    [ -n "$S" ] && KNOWN_SLUGS+=("$S")
done

# 1. Orphaned website directories
echo "--- Orphaned Website Directories ---"
for ws_dir in "$REPO_DIR"/*-website; do
    [ -d "$ws_dir" ] || continue
    DIR_NAME=$(basename "$ws_dir")
    SLUG="${DIR_NAME%-website}"
    FOUND=false
    for ks in "${KNOWN_SLUGS[@]}"; do
        [ "$ks" = "$SLUG" ] && FOUND=true && break
    done
    if [ "$FOUND" = false ]; then
        echo "  ORPHAN: $DIR_NAME (no matching lead profile)"
        WOULD_REMOVE=$((WOULD_REMOVE + 1))
        if [ "$DRY_RUN" = false ]; then
            rm -rf "$ws_dir"
            REMOVED=$((REMOVED + 1))
        fi
    fi
done

# 2. Empty or undersized output files
echo "--- Undersized Files ---"
for f in "$REPO_DIR"/blueprints/*.html "$REPO_DIR"/delivery-emails/*.html; do
    [ -f "$f" ] || continue
    FSIZE=$(wc -c < "$f" | tr -d ' ')
    if [ "$FSIZE" -lt 1024 ]; then
        echo "  TINY: $(basename "$f") (${FSIZE}B)"
        WOULD_REMOVE=$((WOULD_REMOVE + 1))
        if [ "$DRY_RUN" = false ]; then
            rm -f "$f"
            REMOVED=$((REMOVED + 1))
        fi
    fi
done

# 3. Stale log files
echo "--- Stale Logs (> ${MAX_AGE_DAYS} days) ---"
if [ -d "$LOG_DIR" ]; then
    STALE_LOGS=$(find "$LOG_DIR" -name "blueprint-batch-*" -mtime +"$MAX_AGE_DAYS" 2>/dev/null || true)
    if [ -n "$STALE_LOGS" ]; then
        echo "$STALE_LOGS" | while IFS= read -r logfile; do
            echo "  STALE: $(basename "$logfile")"
            WOULD_REMOVE=$((WOULD_REMOVE + 1))
            if [ "$DRY_RUN" = false ]; then
                rm -f "$logfile"
                REMOVED=$((REMOVED + 1))
            fi
        done
    fi
fi

echo ""
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN: $WOULD_REMOVE items would be removed. Run without --dry-run to delete."
else
    echo "Cleaned up: $REMOVED items removed."
fi
