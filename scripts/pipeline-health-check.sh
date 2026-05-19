#!/bin/bash
# Blueprint AI Pipeline Health Check — runs hourly via LaunchAgent
LOG="$HOME/.openclaw/logs/pipeline-health.log"
mkdir -p "$(dirname "$LOG")"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Check webhook listener
WH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8090 2>/dev/null)
WH_STATUS="DOWN"
[ "$WH" = "200" ] && WH_STATUS="UP"

# Check GitHub Pages (sample 3 random leads)
GP_PASS=0
for slug in melissa-tash-srp brittney-warnick branson-maxwell; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://bennett-maxwell.github.io/fki-preview/blueprints/${slug}.html" 2>/dev/null)
  [ "$code" = "200" ] && GP_PASS=$((GP_PASS + 1))
done

# Check lead count
LEAD_COUNT=$(ls "$HOME/fki-preview/leads/"*.json 2>/dev/null | wc -l | tr -d ' ')

echo "$TS webhook=$WH_STATUS github_pages=${GP_PASS}/3 leads=$LEAD_COUNT" >> "$LOG"

# Alert if webhook down
if [ "$WH_STATUS" = "DOWN" ]; then
  echo "$TS ALERT: Webhook listener DOWN on port 8090" >> "$LOG"
fi
