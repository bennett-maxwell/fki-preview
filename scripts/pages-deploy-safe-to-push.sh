#!/usr/bin/env bash
# pages-deploy-safe-to-push.sh — don't cancel a customer-facing deploy with a trivial push.
#
# PERMANENT FIX 2026-08-05 (marker BLUEPRINT-PAGES-PUSH-CANCEL-GUARD-20260805,
# EC-PAGES-DEPLOY-CANCELLED-BY-LATER-PUSH-20260805, occurrence 2).
#
# WHY
# ---
# `.github/workflows/pages.yml` sets:
#     concurrency: {group: pages, cancel-in-progress: true}
# so ANY push while a Pages deploy is running KILLS that deploy. Whatever was only in the cancelled
# commit stays stale on the live hub.
#
#   2026-07-28 (occurrence 1) the commit carrying podcasts/bri-fresh.mp3 was cancelled by the next
#              push; the resulting 404 looked like a missing/oversized file. Self-inflicted.
#   2026-08-05 (occurrence 2) the commit RETIRING THE STALE INTAKE FORM was cancelled by a
#              suite-wiring push. hub.aiblueprintmarketing.com/apply/ kept serving a 67,570-byte
#              look-alike intake form for ~45 extra minutes -- on a path fed by the ad CTA -- while
#              the repo, the gate, and CI were all green.
#
# The trap: "the deploy is still running" and "I cancelled the deploy" produce IDENTICAL symptoms.
# Only the run conclusion tells them apart, and by then the damage is done.
#
# USAGE
#   bash scripts/pages-deploy-safe-to-push.sh            # advise; exit 1 if a deploy is in flight
#   bash scripts/pages-deploy-safe-to-push.sh --wait     # block until it finishes, then exit 0
#   bash scripts/pages-deploy-safe-to-push.sh --wait 900 # custom timeout (default 1200s)
#
# Works unauthenticated on this public repo (no token, no gh CLI needed). GITHUB_TOKEN is used if set.

set -uo pipefail

REPO="${PAGES_GUARD_REPO:-bennett-maxwell/fki-preview}"
API="https://api.github.com/repos/$REPO/actions/runs?per_page=10"
WAIT=false
TIMEOUT=1200

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wait) WAIT=true; shift; [[ "${1:-}" =~ ^[0-9]+$ ]] && { TIMEOUT="$1"; shift; } ;;
    -h|--help) sed -n '1,32p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

fetch() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    curl -s -H "Authorization: Bearer $GITHUB_TOKEN" "$API"
  else
    curl -s "$API"
  fi
}

# Prints "<status> <conclusion> <sha7>" for the newest Pages deploy, or nothing.
newest_pages_run() {
  fetch | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for r in d.get("workflow_runs", []):
    if str(r.get("name", "")).startswith("Deploy static site to Pages"):
        print(r.get("status"), r.get("conclusion"), str(r.get("head_sha", ""))[:7])
        break
'
}

read -r STATUS CONCL SHA <<<"$(newest_pages_run)"

if [[ -z "${STATUS:-}" ]]; then
  echo "pages-guard: could not read run status (network/API) — proceeding, but verify the LIVE url after push." >&2
  exit 0
fi

if [[ "$STATUS" != "in_progress" && "$STATUS" != "queued" ]]; then
  echo "pages-guard: OK — newest Pages deploy is $STATUS/$CONCL ($SHA). Safe to push."
  exit 0
fi

echo "pages-guard: ⛔ a Pages deploy is $STATUS for commit $SHA."
echo "  pages.yml uses cancel-in-progress:true, so pushing NOW will CANCEL it and whatever is only in"
echo "  that commit stays STALE on the live hub. This has happened twice (7/28 podcast 404,"
echo "  8/5 stale intake form served ~45 min longer)."
echo "  Options: (a) wait   -> re-run with --wait"
echo "           (b) batch  -> fold your change into the same push"
echo "           (c) accept -> only if your change IS the more urgent customer-facing fix"

if [[ "$WAIT" != "true" ]]; then
  exit 1
fi

echo "pages-guard: waiting up to ${TIMEOUT}s for $SHA to finish..."
ELAPSED=0
while (( ELAPSED < TIMEOUT )); do
  sleep 20; ELAPSED=$((ELAPSED + 20))
  read -r STATUS CONCL SHA2 <<<"$(newest_pages_run)"
  if [[ "$STATUS" != "in_progress" && "$STATUS" != "queued" ]]; then
    echo "pages-guard: deploy finished ($STATUS/$CONCL, ${ELAPSED}s). Safe to push."
    exit 0
  fi
  (( ELAPSED % 120 == 0 )) && echo "  ...still $STATUS (${ELAPSED}s)"
done

echo "pages-guard: still $STATUS after ${TIMEOUT}s. Deploys can exceed 15 min (podcasts/ is ~2.9GB and"
echo "  pages.yml uploads path '.'). Re-run --wait, or push knowing you will cancel $SHA." >&2
exit 1
