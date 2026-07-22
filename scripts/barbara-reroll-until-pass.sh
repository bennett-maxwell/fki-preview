#!/bin/bash
# Loop: re-roll Barbara podcast (URL-clean + D3-02 greeting) until audit VERDICT=PASS, then push + swap live page.
cd /Users/madisonlanz/Desktop/fki-preview || exit 1
SLUG=barbara-upper-crust-designs
for i in $(seq 1 8); do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  python3 ~/.notebooklm/refresh_auth.py >/dev/null 2>&1
  python3 scripts/fetch-podcast.py --slug $SLUG \
    --source podcasts/$SLUG-podcast-source.md \
    --business-name "Upper Crust Designs" --first-name "Barbara" --timeout 1400 2>&1 | tail -2
  dur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 podcasts/$SLUG.mp3 2>/dev/null)
  echo "duration: $dur sec"
  if python3 run-audit.py --lead $SLUG 2>&1 | tail -2 | grep -q "VERDICT=PASS"; then
    echo "=== PASS on attempt $i — pushing ==="
    git add podcasts/$SLUG.mp3 audit-receipts/$SLUG/ 2>/dev/null
    git commit -q -m "blueprint: Barbara podcast clean re-roll (URL-stripped + D3-02 greeting, audit PASS) — seamless live-page swap" && \
    git push origin main 2>&1 | tail -2
    echo "PUSHED. Hub cache (max-age 600) will serve new file within ~10min at same URL."
    exit 0
  fi
  echo "attempt $i not PASS, retrying..."
done
echo "EXHAUSTED 8 attempts without PASS"
exit 2
