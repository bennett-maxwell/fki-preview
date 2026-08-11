#!/bin/bash
# audit-gate.sh — blueprint-ai-audit-skill v2.8 HARD 100% GATE (Bennett directive 2026-06-01).
#
# Mints a hash-bound approval token ONLY when every deterministic enforcer passes (100%).
# RETIRED CALLER NOTE (2026-08-03): build-delivery-email.sh (which used to call this immediately
# before any send) was retired by RL-DE2 on 2026-07-17. This token gate still applies -- no token =>
# no send -- but it is now the Drive-sourced Stage-7 path that must honour it.
#
# Usage: audit-gate.sh <slug> <email_html> [blueprint_html]
# Exit 0 + token minted = approved for THESE EXACT email bytes.
# Exit 1 = blocked (prints failing enforcer).
set -euo pipefail
SLUG="${1:-}"; EMAIL_HTML="${2:-}"; BP_HTML="${3:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
APPROVE_DIR="$HOME/.openclaw/state/blueprint-approvals"
TOKEN="$APPROVE_DIR/${SLUG}.approved"
mkdir -p "$APPROVE_DIR"

if [ -z "$SLUG" ] || [ -z "$EMAIL_HTML" ] || [ ! -f "$EMAIL_HTML" ]; then
    echo "audit-gate BLOCKED: usage audit-gate.sh <slug> <email_html> [blueprint_html] (email file must exist)"
    exit 1
fi

FAILS=0

# --- Enforcer 1: email design conformance (D5-16..D5-21, all red-line) ---
echo "audit-gate: email-design-conformance.py ..."
if ! python3 "$SCRIPT_DIR/email-design-conformance.py" "$EMAIL_HTML"; then
    FAILS=$((FAILS+1))
fi

# --- Enforcers 2-4: blueprint HTML checks (only if a blueprint file is provided) ---
if [ -n "$BP_HTML" ] && [ -f "$BP_HTML" ]; then
    if [ -f "$SCRIPT_DIR/format-conformance-check.py" ]; then
        echo "audit-gate: format-conformance-check.py ..."
        if ! python3 "$SCRIPT_DIR/format-conformance-check.py" "$BP_HTML"; then FAILS=$((FAILS+1)); fi
    else
        echo "audit-gate: format-conformance-check.py missing"
        FAILS=$((FAILS+1))
    fi
    if [ -f "$SCRIPT_DIR/audio-player-seekability-check.py" ]; then
        echo "audit-gate: audio-player-seekability-check.py ..."
        if ! python3 "$SCRIPT_DIR/audio-player-seekability-check.py" "$BP_HTML" --slug "$SLUG"; then FAILS=$((FAILS+1)); fi
    else
        echo "audit-gate: audio-player-seekability-check.py missing"
        FAILS=$((FAILS+1))
    fi

    if [ -f "$REPO_DIR/financial-realism-check.py" ]; then
        echo "audit-gate: financial-realism-check.py ..."
        if ! python3 "$REPO_DIR/financial-realism-check.py" --file "$BP_HTML"; then FAILS=$((FAILS+1)); fi
    else
        echo "audit-gate: financial-realism-check.py missing"
        FAILS=$((FAILS+1))
    fi

    D9_AUDIT="$HOME/.claude/skills/blueprint-ai-audit-skill/d9-audit.py"
    if [ -f "$D9_AUDIT" ]; then
        echo "audit-gate: d9-audit.py ..."
        if ! python3 "$D9_AUDIT" "$BP_HTML"; then FAILS=$((FAILS+1)); fi
    else
        echo "audit-gate: d9-audit.py missing"
        FAILS=$((FAILS+1))
    fi

    # COVERAGE TRANSFER 2026-08-11 (marker BLUEPRINT-SEND-TOKEN-AUDIT-GATE-CANONICAL-20260811):
    # blueprint_gatekeeper_100.py was the only token-path caller of the D2-03 agent-card /
    # ready-to-use-prompt quality gate. Retiring gatekeeper as the token authority would have
    # SILENTLY dropped that red-line from the send path, so it moves here. Without this line the
    # retirement would have been a quiet loss of coverage rather than a swap.
    APQ="$SCRIPT_DIR/blueprint_agent_prompt_quality_gate.py"
    if [ -f "$APQ" ]; then
        echo "audit-gate: blueprint_agent_prompt_quality_gate.py (D2-03) ..."
        APQ_ARGS=(--html "$BP_HTML")
        [ -f "$REPO_DIR/leads/$SLUG.json" ] && APQ_ARGS+=(--profile "$REPO_DIR/leads/$SLUG.json")
        if ! python3 "$APQ" "${APQ_ARGS[@]}"; then FAILS=$((FAILS+1)); fi
    else
        echo "audit-gate: blueprint_agent_prompt_quality_gate.py missing"
        FAILS=$((FAILS+1))
    fi
fi

if [ "$FAILS" -gt 0 ]; then
    echo "audit-gate BLOCKED: $FAILS enforcer group(s) failed. Score < 100%. Token NOT minted. Send refused."
    rm -f "$TOKEN"   # never leave a stale token behind a failed run
    exit 1
fi

# --- 100% reached: mint hash-bound token ---
HASH=$(shasum -a 256 "$EMAIL_HTML" | awk '{print $1}')
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cat > "$TOKEN" <<JSON
{
  "slug": "$SLUG",
  "score": 100,
  "total_possible_pct": 100,
  "red_line_pass": true,
  "approved_html_sha256": "$HASH",
  "email_html_path": "$EMAIL_HTML",
  "minted_at": "$TS",
  "minted_by": "audit-gate.sh v2.8",
  "gate": "blueprint-ai-audit-skill v2.8 HARD 100%"
}
JSON
echo "audit-gate PASS: 100% conformance. Token minted -> $TOKEN (sha256=$HASH)"
exit 0
