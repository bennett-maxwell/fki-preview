#!/usr/bin/env bash
# Watch for all 11 v14 MP3s then update tracker + send email
PODCASTS=/Users/openclaw/fki-preview/podcasts
REPO=/Users/openclaw/fki-preview
LOG=/Users/openclaw/.openclaw/logs/podcast-completion-watcher.log

exec >> "$LOG" 2>&1
echo "=== Completion Watcher Started — $(date) ==="

SLUGS=(
  zachary-red-sands
  branson-maxwell
  brittney-warnick
  chris-lpnw
  rey-31-consulting
  court-lundberg
  melissa-tash-srp
  dave-wood
  brent-attaway
  paul-muus
  rj-kitchenguard
)

wait_all() {
  local max_wait=7200  # 2hr max
  local elapsed=0
  while [ $elapsed -lt $max_wait ]; do
    local missing=0
    local ready=()
    local not_ready=()
    for slug in "${SLUGS[@]}"; do
      if [ -f "${PODCASTS}/${slug}-v14.mp3" ]; then
        ready+=("$slug")
      else
        not_ready+=("$slug")
        missing=$((missing+1))
      fi
    done
    echo "[$(date '+%H:%M:%S')] Ready: ${#ready[@]}/11 — Missing: ${not_ready[*]}"
    if [ $missing -eq 0 ]; then
      return 0
    fi
    sleep 120
    elapsed=$((elapsed+120))
  done
  return 1
}

if wait_all; then
  echo "All 11 MP3s present — running tracker finalize and email"

  # Update tracker
  /Users/openclaw/fki-preview/.venv/bin/python3 /Users/openclaw/fki-preview/scripts/tracker-finalize.py 2>&1

  # Commit and push tracker
  cd "$REPO"
  git pull origin main 2>/dev/null
  git add podcasts/tracker.html
  git commit -m "tracker: all 11 v1.4 podcasts ready" 2>/dev/null
  git push origin main 2>/dev/null
  echo "Tracker pushed"

  # Build email
  BASE="https://bennett-maxwell.github.io/fki-preview/podcasts"
  BODY="<h2>🎙️ All 11 Blueprint Podcasts v1.4 Ready</h2>
<p>Your personalized AI-powered podcast episodes are live. Each one addresses the lead by name, references their specific situation, and delivers tailored franchise insights.</p>
<table style='border-collapse:collapse;width:100%;font-family:sans-serif'>
<tr style='background:#166534;color:white'><th style='padding:8px 12px;text-align:left'>Lead</th><th style='padding:8px 12px'>Listen</th></tr>
<tr><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Zak Oldham — Red Sands Vacation Properties</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/zachary-red-sands-v14.mp3'>▶ Listen</a></td></tr>
<tr style='background:#f8fafc'><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Branson Maxwell</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/branson-maxwell-v14.mp3'>▶ Listen</a></td></tr>
<tr><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Brittney Warnick</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/brittney-warnick-v14.mp3'>▶ Listen</a></td></tr>
<tr style='background:#f8fafc'><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Chris — LPNW</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/chris-lpnw-v14.mp3'>▶ Listen</a></td></tr>
<tr><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Rey — 31 Consulting</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/rey-31-consulting-v14.mp3'>▶ Listen</a></td></tr>
<tr style='background:#f8fafc'><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Court Lundberg</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/court-lundberg-v14.mp3'>▶ Listen</a></td></tr>
<tr><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Melissa Tash — Spoiled Rotten Photography</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/melissa-tash-srp-v14.mp3'>▶ Listen</a></td></tr>
<tr style='background:#f8fafc'><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Dave Wood</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/dave-wood-v14.mp3'>▶ Listen</a></td></tr>
<tr><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Brent Attaway — CRM Xperts</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/brent-attaway-v14.mp3'>▶ Listen</a></td></tr>
<tr style='background:#f8fafc'><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'>Paul Muus</td><td style='padding:8px 12px;border-bottom:1px solid #e2e8f0'><a href='${BASE}/paul-muus-v14.mp3'>▶ Listen</a></td></tr>
<tr><td style='padding:8px 12px'>RJ Schultz — Kitchen Guard</td><td style='padding:8px 12px'><a href='${BASE}/rj-kitchenguard-v14.mp3'>▶ Listen</a></td></tr>
</table>
<p style='margin-top:20px'><a href='https://bennett-maxwell.github.io/fki-preview/podcasts/tracker.html' style='background:#166534;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold'>View Full Tracker</a></p>
<p style='color:#64748b;font-size:0.85rem;margin-top:16px'>Podcast skill v1.4 — personalized intros, name-direct from Segment 1, tone rules 10-14, Reviews as Segment 3</p>"

  /usr/local/bin/gog gmail send \
    --to="bennett@franchiseki.com" \
    --subject="🎙️ All 11 Blueprint Podcasts v1.4 Are Ready" \
    --body-html="$BODY" 2>&1 | head -5 || \
  /opt/homebrew/bin/gog gmail send \
    --to="bennett@franchiseki.com" \
    --subject="🎙️ All 11 Blueprint Podcasts v1.4 Are Ready" \
    --body-html="$BODY" 2>&1 | head -5

  echo "Email sent to bennett@franchiseki.com"
  echo "=== COMPLETE — $(date) ==="
else
  echo "TIMEOUT: Not all MP3s downloaded after 2 hours"
fi
