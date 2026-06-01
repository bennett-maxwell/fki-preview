#!/bin/bash
# Blueprint AI Pipeline -- Automated Screenshot Capture (QA)
# Usage: ./capture-screenshots.sh [leads-dir]
#
# Captures screenshots of all live Blueprint and website URLs for QA review.
# Requires: Chrome or Chromium in headless mode.
#
# Output: screenshots/ directory with <slug>-blueprint.png and <slug>-website.png

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="${1:-$REPO_DIR/leads}"
SCREENSHOTS_DIR="$REPO_DIR/screenshots"
mkdir -p "$SCREENSHOTS_DIR"

if [ "${1:-}" = "--help" ]; then
    echo "Usage: $0 [leads-dir]"
    echo ""
    echo "Captures screenshots of all live pages for QA review."
    echo "Requires Chrome/Chromium installed for headless capture."
    echo "Output: screenshots/ directory"
    exit 0
fi

# Detect Chrome path
CHROME=""
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif command -v chromium &>/dev/null; then
    CHROME="chromium"
elif command -v google-chrome &>/dev/null; then
    CHROME="google-chrome"
fi

if [ -z "$CHROME" ]; then
    echo "WARNING: Chrome/Chromium not found. Screenshots will be skipped."
    echo "Install Chrome or set CHROME_PATH environment variable."
    exit 0
fi

PAGES_BASE="https://bennett-maxwell.github.io/fki-preview"
TOTAL=0
CAPTURED=0

echo "=== Screenshot Capture ==="
echo "Chrome: $CHROME"
echo ""

for profile in "$LEADS_DIR"/*.json; do
    [ -f "$profile" ] || continue
    SLUG=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('slug','unknown'))" "$profile")
    LEAD=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('lead_name','Unknown'))" "$profile")

    # Blueprint screenshot
    BP_URL="$PAGES_BASE/blueprints/$SLUG.html"
    BP_SCREENSHOT="$SCREENSHOTS_DIR/${SLUG}-blueprint.png"
    TOTAL=$((TOTAL + 1))
    "$CHROME" --headless --disable-gpu --screenshot="$BP_SCREENSHOT" --window-size=1440,900 "$BP_URL" 2>/dev/null && {
        CAPTURED=$((CAPTURED + 1))
        echo "  CAPTURED: $SLUG blueprint"
    } || {
        echo "  FAILED: $SLUG blueprint"
    }

    # Website screenshot
    WS_URL="$PAGES_BASE/${SLUG}-website/"
    WS_SCREENSHOT="$SCREENSHOTS_DIR/${SLUG}-website.png"
    TOTAL=$((TOTAL + 1))
    "$CHROME" --headless --disable-gpu --screenshot="$WS_SCREENSHOT" --window-size=1440,900 "$WS_URL" 2>/dev/null && {
        CAPTURED=$((CAPTURED + 1))
        echo "  CAPTURED: $SLUG website"
    } || {
        echo "  FAILED: $SLUG website"
    }
done

echo ""
echo "Total: $TOTAL | Captured: $CAPTURED | Failed: $((TOTAL - CAPTURED))"
echo "Screenshots: $SCREENSHOTS_DIR/"
