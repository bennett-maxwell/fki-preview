#!/bin/bash
# Install Blueprint AI git hooks from canonical committed source.
# Run this once after every fresh clone so the verified delivery gates travel
# with the repo instead of living only in one machine's .git/hooks.
#
# Installs:
#   pre-commit  — G16 SKILL.md gate strings + orchestrator validators
#                 + completion-gate + D9 render-integrity (network-free)
#   pre-push    — HTTP 200 check on changed blueprint HTML + referenced podcast MP3
#
# Canonical source: scripts/git-hooks/  (kept in sync with the verified live hooks)

set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"
SRC="$REPO_ROOT/scripts/git-hooks"
DEST="$REPO_ROOT/.git/hooks"

for hook in pre-commit pre-push; do
  if [ -f "$SRC/$hook" ]; then
    cp "$SRC/$hook" "$DEST/$hook"
    chmod +x "$DEST/$hook"
    echo "✓ installed $hook"
  else
    echo "⚠ missing canonical $SRC/$hook — skipped"
  fi
done

echo "✓ Blueprint AI git hooks installed. Verified delivery gates are now active in this clone."
