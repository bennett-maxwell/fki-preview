#!/usr/bin/env bash
# Advaita launch — one-command deploy to bennett-maxwell/fki-preview
# Live URL: https://bennett-maxwell.github.io/fki-preview/advaita/

set -e

FUNNEL_DIR="/Users/temp/Desktop/advaita-launch-2026-05-10/funnel"
REPO_DIR="$HOME/code/fki-preview"
TARGET_DIR="$REPO_DIR/advaita"
LIVE_URL="https://bennett-maxwell.github.io/fki-preview/advaita/"

echo "==> Advaita launch starting"

# 1. Ensure ~/code exists
mkdir -p "$HOME/code"

# 2. Clone repo if missing
if [ ! -d "$REPO_DIR" ]; then
  echo "==> Cloning bennett-maxwell/fki-preview"
  cd "$HOME/code"
  if ! gh repo clone bennett-maxwell/fki-preview 2>/dev/null; then
    git clone https://github.com/bennett-maxwell/fki-preview.git || {
      echo "FAIL: clone failed — flag G_GH_AUTH"
      exit 1
    }
  fi
fi

# 3. Sync funnel files
echo "==> Copying funnel to $TARGET_DIR"
mkdir -p "$TARGET_DIR"
cp -R "$FUNNEL_DIR"/* "$TARGET_DIR/"

# 4. Commit + push
cd "$REPO_DIR"
git add advaita/
if git diff --cached --quiet; then
  echo "==> No changes to commit"
else
  git commit -m "Advaita launch 2026-05-11"
  git push || {
    echo "FAIL: push failed — flag G_GH_AUTH"
    exit 1
  }
fi

# 5. Verify
echo "==> Waiting 30s for GitHub Pages build"
sleep 30
echo "==> Verifying $LIVE_URL"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L "$LIVE_URL")
if [ "$HTTP_CODE" = "200" ]; then
  echo "==> LIVE: $LIVE_URL (HTTP $HTTP_CODE)"
else
  echo "==> WARN: HTTP $HTTP_CODE — Pages may still be building. Retry in 2 min: curl -I $LIVE_URL"
fi

echo ""
echo "LIVE URL: $LIVE_URL"
echo "QUIZ:     ${LIVE_URL}quiz.html"
echo "RESULT:   ${LIVE_URL}result.html?score=65&band=growth&rev=165000"
