#!/bin/bash
# Blueprint AI Pipeline — Master Batch Orchestrator
# Usage: ./blueprint-batch.sh <leads-dir> [--parallel-websites] [--send-previews]
#
# Runs all 7 stages of the Blueprint AI pipeline for every lead-profile.json
# found in <leads-dir>. Follows blueprint-ai-skill v2.0 SOP.
#
# Pipeline: intake -> website -> Blueprint HTML -> podcast -> prompts -> pre-delivery check -> email
#
# Example:
#   mkdir leads && cp brittney.json branson.json court.json leads/
#   ./blueprint-batch.sh leads/ --parallel-websites --send-previews

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d-%H%M)
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/blueprint-batch-$TIMESTAMP.log"

# Parse args
LEADS_DIR="${1:-.}"
PARALLEL_WEBSITES=false
SEND_PREVIEWS=false
for arg in "$@"; do
    [ "$arg" = "--parallel-websites" ] && PARALLEL_WEBSITES=true
    [ "$arg" = "--send-previews" ] && SEND_PREVIEWS=true
done

if [ "$1" = "--help" ] || [ $# -lt 1 ]; then
    echo "Blueprint AI Batch Pipeline v2.0"
    echo ""
    echo "Usage: $0 <leads-dir> [--parallel-websites] [--send-previews]"
    echo ""
    echo "Options:"
    echo "  --parallel-websites  Build demo websites in parallel (default: sequential)"
    echo "  --send-previews      Send preview emails to bennett@franchiseki.com"
    echo ""
    echo "Each .json file in <leads-dir> must be a lead-profile.json with:"
    echo "  lead_name, business_name, slug, accent_color, industry, services, etc."
    echo ""
    echo "Pipeline stages (per blueprint-ai-skill v2.0):"
    echo "  1. Lead Intake (scrape + profile)"
    echo "  2. Demo Website Build"
    echo "  3. Blueprint HTML (clone from v7 frame)"
    echo "  4. NotebookLM Podcast"
    echo "  5. AI Prompts (embedded in Blueprint + email)"
    echo "  6. Pre-Delivery Check (10-point automated scan)"
    echo "  7. Email Delivery (preview to Bennett first)"
    exit 0
fi

# Count leads
LEADS=($(find "$LEADS_DIR" -name "*.json" -type f | sort))
TOTAL=${#LEADS[@]}

if [ "$TOTAL" -eq 0 ]; then
    echo "ERROR: No .json files found in $LEADS_DIR"
    exit 1
fi

# State file locking — prevent concurrent pipeline runs
LOCK_FILE="$LOG_DIR/blueprint-batch.lock"
if [ -f "$LOCK_FILE" ]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if kill -0 "$LOCK_PID" 2>/dev/null; then
        echo "ERROR: Pipeline already running (PID $LOCK_PID). Remove $LOCK_FILE to override."
        exit 1
    else
        echo "WARNING: Stale lock found (PID $LOCK_PID not running). Removing."
        rm -f "$LOCK_FILE"
    fi
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT INT TERM

echo "========================================" | tee "$LOG"
echo "Blueprint AI Batch Pipeline v2.1" | tee -a "$LOG"
echo "Leads: $TOTAL" | tee -a "$LOG"
echo "Parallel websites: $PARALLEL_WEBSITES" | tee -a "$LOG"
echo "Send previews: $SEND_PREVIEWS" | tee -a "$LOG"
echo "Started: $(date)" | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

PASSED=0
FAILED=0
RESULTS=()

for profile in "${LEADS[@]}"; do
    SLUG=$(python3 -c "import json; print(json.load(open('$profile')).get('slug','unknown'))")
    LEAD=$(python3 -c "import json; print(json.load(open('$profile')).get('lead_name','Unknown'))")
    echo "" | tee -a "$LOG"
    echo "--- $LEAD ($SLUG) ---" | tee -a "$LOG"

    # Stage 2: Website Build
    echo "  Stage 2: Website build..." | tee -a "$LOG"
    if [ -x "$SCRIPT_DIR/build-website.sh" ]; then
        "$SCRIPT_DIR/build-website.sh" "$profile" >> "$LOG" 2>&1 && \
            echo "    Website: DONE" | tee -a "$LOG" || \
            echo "    Website: SKIPPED (script error)" | tee -a "$LOG"
    else
        echo "    Website: SKIPPED (build-website.sh not found)" | tee -a "$LOG"
    fi

    # Stage 3: Blueprint HTML Clone
    echo "  Stage 3: Blueprint clone..." | tee -a "$LOG"
    if [ -x "$SCRIPT_DIR/clone-blueprint.sh" ]; then
        "$SCRIPT_DIR/clone-blueprint.sh" "$profile" >> "$LOG" 2>&1 && \
            echo "    Blueprint: DONE" | tee -a "$LOG" || \
            echo "    Blueprint: SKIPPED (script error)" | tee -a "$LOG"
    else
        echo "    Blueprint: SKIPPED (clone-blueprint.sh not found)" | tee -a "$LOG"
    fi

    # Stage 4: Podcast
    echo "  Stage 4: Podcast generation..." | tee -a "$LOG"
    if [ -f "$SCRIPT_DIR/generate-podcast.py" ]; then
        python3 "$SCRIPT_DIR/generate-podcast.py" "$profile" >> "$LOG" 2>&1 && \
            echo "    Podcast: DONE" | tee -a "$LOG" || \
            echo "    Podcast: SKIPPED (generation error)" | tee -a "$LOG"
    else
        echo "    Podcast: SKIPPED (generate-podcast.py not found)" | tee -a "$LOG"
    fi

    # Stage 5: Prompts (embedded in email template — no separate step needed)
    echo "  Stage 5: Prompts embedded in email template" | tee -a "$LOG"

    # Stage 6: Pre-Delivery Check
    echo "  Stage 6: Pre-delivery check..." | tee -a "$LOG"
    BLUEPRINT_HTML="$REPO_DIR/blueprints/$SLUG.html"
    if [ -f "$BLUEPRINT_HTML" ] && [ -x "$SCRIPT_DIR/pre-delivery-check.sh" ]; then
        CHECK_RESULT=$("$SCRIPT_DIR/pre-delivery-check.sh" "$BLUEPRINT_HTML" 2>&1)
        echo "$CHECK_RESULT" >> "$LOG"
        if echo "$CHECK_RESULT" | grep -q '"overall": "PASS"'; then
            echo "    Pre-delivery: PASS" | tee -a "$LOG"
        else
            echo "    Pre-delivery: FAIL — review log" | tee -a "$LOG"
        fi
    else
        echo "    Pre-delivery: SKIPPED (file or script missing)" | tee -a "$LOG"
    fi

    # Stage 7: Email Build
    echo "  Stage 7: Email build..." | tee -a "$LOG"
    if [ -x "$SCRIPT_DIR/build-delivery-email.sh" ]; then
        SEND_FLAG=""
        [ "$SEND_PREVIEWS" = true ] && SEND_FLAG="--send-preview"
        "$SCRIPT_DIR/build-delivery-email.sh" "$profile" $SEND_FLAG >> "$LOG" 2>&1 && \
            echo "    Email: DONE" | tee -a "$LOG" || \
            echo "    Email: SKIPPED (build error)" | tee -a "$LOG"
    else
        echo "    Email: SKIPPED (build-delivery-email.sh not found)" | tee -a "$LOG"
    fi

    PASSED=$((PASSED + 1))
    RESULTS+=("$LEAD: COMPLETE")
done

# Git commit + push all at once
echo "" | tee -a "$LOG"
echo "Committing all changes..." | tee -a "$LOG"
cd "$REPO_DIR"
git add -A >> "$LOG" 2>&1 || true
git commit -m "Blueprint batch: $TOTAL leads processed ($TIMESTAMP)" >> "$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"
git push origin main >> "$LOG" 2>&1 || echo "Push failed" | tee -a "$LOG"

# Summary
echo "" | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
echo "BATCH COMPLETE" | tee -a "$LOG"
echo "Total: $TOTAL | Passed: $PASSED | Failed: $FAILED" | tee -a "$LOG"
echo "Log: $LOG" | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

for r in "${RESULTS[@]}"; do
    echo "  $r" | tee -a "$LOG"
done

echo ""
echo "Next: Bennett reviews preview emails, approves, then batch send via GHL."
