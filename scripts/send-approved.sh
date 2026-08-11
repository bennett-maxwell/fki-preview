#!/bin/bash
# Blueprint AI Pipeline — Batch Send Approved Blueprints
# Usage: ./send-approved.sh [slug1 slug2 ...] OR ./send-approved.sh --all
# Requires a current Bennett approval receipt AND a Gatekeeper token that allows
# external_send. A CLI flag alone is never approval proof.

set -uo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_DIR="$REPO_DIR/scripts"
LEADS_DIR="$REPO_DIR/leads"

BENNETT_APPROVED=false
GATE_TOKEN_DIR=""
APPROVAL_RECEIPT_DIR=""
SLUGS=()

while [ "$#" -gt 0 ]; do
    arg="$1"
    case "$arg" in
        --bennett-approved|--approved) BENNETT_APPROVED=true ;;
        --gate-token-dir)
            shift
            GATE_TOKEN_DIR="${1:-}"
            ;;
        --approval-receipt-dir)
            shift
            APPROVAL_RECEIPT_DIR="${1:-}"
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
    echo "❌ BLOCKED: Require --bennett-approved flag plus approval receipt."
    echo "Process: Bennett replies APPROVE to preview email → save approval receipt → rerun Gatekeeper for external_send → run this script."
    exit 1
fi

if [ ${#SLUGS[@]} -eq 0 ]; then
    echo "Usage: $0 --all --bennett-approved --gate-token-dir <receipts> OR $0 court-lundberg --bennett-approved --gate-token-dir <receipts>"
    exit 1
fi

# SEND-TOKEN REWIRE 2026-08-11 (marker BLUEPRINT-SEND-TOKEN-AUDIT-GATE-CANONICAL-20260811):
# --gate-token-dir used to be required and had to hold <slug>-gatekeeper-pass-token.json from
# blueprint_gatekeeper_100.py --mode production. gatekeeper-100 is RETIRED as the token authority
# (it required receipts clone-blueprint.sh never emits, so it could not pass — 10 pass tokens vs 33
# fails repo-wide, and delivered leads carried none). The token now lives in ONE canonical place,
# ~/.openclaw/state/blueprint-approvals/<slug>.approved, minted by audit-gate.sh and bound to the
# SHA256 of the exact delivery-email bytes. The flag is accepted for backwards compatibility and
# ignored; the directory can no longer be pointed somewhere convenient to satisfy the gate.
if [ -n "$GATE_TOKEN_DIR" ]; then
    echo "ℹ️  --gate-token-dir is accepted for compatibility and IGNORED; the send token is the"
    echo "   canonical hash-bound audit-gate token (scripts/blueprint_send_token.py --verify <slug>)."
fi

if [ -z "$APPROVAL_RECEIPT_DIR" ]; then
    echo "❌ BLOCKED: Require --approval-receipt-dir <receipts>."
    echo "Each slug must have <receipts>/<slug>-bennett-approval.json with bennett_approved=true and external_customer_send_approved=true."
    exit 1
fi

echo "📦 Sending ${#SLUGS[@]} blueprints with --bennett-approved flag..."
for slug in "${SLUGS[@]}"; do
    profile="$LEADS_DIR/${slug}.json"
    if [ ! -f "$profile" ]; then
        echo "❌ $slug: profile not found, skip"
        continue
    fi
    # Send token: canonical, hash-bound to the exact email bytes. Fails CLOSED.
    if ! python3 "$SCRIPT_DIR/blueprint_send_token.py" --verify "$slug"; then
        echo "❌ $slug: send token invalid/missing/stale — external-send lock closed"
        continue
    fi
    approval="$APPROVAL_RECEIPT_DIR/${slug}-bennett-approval.json"
    if [ ! -f "$approval" ]; then
        echo "❌ $slug: Bennett approval receipt not found: $approval"
        continue
    fi
    if ! python3 - "$approval" <<'PYEOF'
import json, sys
approval = json.load(open(sys.argv[1]))
approval_ok = approval.get("bennett_approved") is True and approval.get("external_customer_send_approved") is True
if not approval_ok:
    print("approval receipt must include bennett_approved=true and external_customer_send_approved=true")
sys.exit(0 if approval_ok else 1)
PYEOF
    then
        echo "❌ $slug: human approval missing — external-send lock still closed"
        continue
    fi
    echo "→ Sending $slug..."
    # RL-DE2 REWIRE 2026-08-03 (marker BLUEPRINT-RLDE2-DEAD-CALLERS-REWIRED-20260803):
    # build-delivery-email.sh was RETIRED 2026-07-17 by RL-DE1/RL-DE2 (repo commit de31b437a).
    # This invocation had been dead ever since -- it failed on a missing file and printed a bare
    # "failed", giving no clue that the SEND PATH itself was decommissioned. It fails CLOSED (no
    # false "sent"), but opaquely, which is its own hazard on a revenue path.
    echo "  ⛔ $slug: NOT SENT -- this send path is retired."
    echo "     build-delivery-email.sh no longer exists: RL-DE2 requires the Stage-7 delivery email"
    echo "     to be built from the canonical Drive blueprint-ai-skill design every run, never a"
    echo "     local template. Send via the CRMX conversations/messages API per skill v3.52 after"
    echo "     a session audit of 100% + explicit approval. See the Drive skill Stage-7 section."
    exit 2
done
echo "Done."
