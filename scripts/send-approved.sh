#!/bin/bash
# Blueprint AI Pipeline — Batch Send Approved Blueprints
# Usage: ./send-approved.sh [slug1 slug2 ...] OR ./send-approved.sh --all
# Requires Bennett to have replied APPROVE (or pass --bennett-approved explicitly)

set -uo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_DIR="$REPO_DIR/scripts"
LEADS_DIR="$REPO_DIR/leads"

BENNETT_APPROVED=false
GATE_TOKEN_DIR=""
SLUGS=()

while [ "$#" -gt 0 ]; do
    arg="$1"
    case "$arg" in
        --bennett-approved|--approved) BENNETT_APPROVED=true ;;
        --gate-token-dir)
            shift
            GATE_TOKEN_DIR="${1:-}"
            ;;
        --all)
            for f in "$LEADS_DIR"/*.json; do
                [ -f "$f" ] && SLUGS+=("$(basename "$f" .json)")
            done ;;
        *) SLUGS+=("$arg") ;;
    esac
    shift || true
done

if ! $BENNETT_APPROVED; then
    echo "❌ BLOCKED: Require --bennett-approved flag."
    echo "Process: Bennett replies APPROVE to preview email → run with --bennett-approved"
    exit 1
fi

if [ ${#SLUGS[@]} -eq 0 ]; then
    echo "Usage: $0 --all --bennett-approved --gate-token-dir <receipts> OR $0 court-lundberg --bennett-approved --gate-token-dir <receipts>"
    exit 1
fi

if [ -z "$GATE_TOKEN_DIR" ]; then
    echo "❌ BLOCKED: Require --gate-token-dir <receipts>."
    echo "Each slug must have <receipts>/<slug>-gatekeeper-pass-token.json from scripts/blueprint_gatekeeper_100.py --mode production."
    exit 1
fi

echo "📦 Sending ${#SLUGS[@]} blueprints with --bennett-approved flag..."
for slug in "${SLUGS[@]}"; do
    profile="$LEADS_DIR/${slug}.json"
    if [ ! -f "$profile" ]; then
        echo "❌ $slug: profile not found, skip"
        continue
    fi
    token="$GATE_TOKEN_DIR/${slug}-gatekeeper-pass-token.json"
    if [ ! -f "$token" ]; then
        echo "❌ $slug: production Gatekeeper token not found: $token"
        continue
    fi
    echo "→ Sending $slug..."
    bash "$SCRIPT_DIR/build-delivery-email.sh" "$profile" --send-ghl --bennett-approved --gate-token "$token" && \
        echo "  ✅ $slug: sent" || \
        echo "  ❌ $slug: failed"
done
echo "Done."
