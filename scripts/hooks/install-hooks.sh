#!/bin/bash
# Install Blueprint AI git hooks (G16 + G17 deletion/shrinkage guards)
REPO_ROOT="$(git rev-parse --show-toplevel)"
cp "$REPO_ROOT/scripts/hooks/pre-commit" "$REPO_ROOT/.git/hooks/pre-commit"
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"
echo "✓ pre-commit hook installed (G16 + G17 guards active)"
