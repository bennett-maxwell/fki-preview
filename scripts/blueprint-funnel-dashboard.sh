#!/usr/bin/env bash
set -euo pipefail

LEDGER_DIR="${BLUEPRINT_RUN_LEDGER_DIR:-blueprint-run-ledgers}"
REPORT_DIR="${BLUEPRINT_MONITOR_OUT_DIR:-monitor-reports}"
OUT_DIR="${BLUEPRINT_DASHBOARD_OUT_DIR:-reports}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_JSON="$OUT_DIR/blueprint-funnel-dashboard-$STAMP.json"
OUT_MD="$OUT_DIR/blueprint-funnel-dashboard-$STAMP.md"
LATEST_JSON="$OUT_DIR/blueprint-funnel-dashboard-latest.json"
LATEST_MD="$OUT_DIR/blueprint-funnel-dashboard-latest.md"

mkdir -p "$OUT_DIR"

ledger_count="$(find "$LEDGER_DIR" -type f -name '*.json' 2>/dev/null | wc -l | tr -d ' ')"
monitor_count="$(find "$REPORT_DIR" -type f -name 'blueprint-funnel-monitor-*.json' 2>/dev/null | wc -l | tr -d ' ')"
release_gate_count="$(find "$REPORT_DIR" -type f -name 'blueprint-release-gate-*.json' 2>/dev/null | wc -l | tr -d ' ')"
link_audit_count="$(find "$REPORT_DIR" -type f -name 'blueprint-link-audit-*.json' 2>/dev/null | wc -l | tr -d ' ')"

latest_monitor="$(find "$REPORT_DIR" -type f -name 'blueprint-funnel-monitor-*.json' 2>/dev/null | sort | tail -1)"
latest_release="$(find "$REPORT_DIR" -type f -name 'blueprint-release-gate-*.json' 2>/dev/null | sort | tail -1)"
latest_link="$(find "$REPORT_DIR" -type f -name 'blueprint-link-audit-*.json' 2>/dev/null | sort | tail -1)"

latest_monitor_status="missing"
latest_release_status="missing"
latest_link_status="missing"
[[ -n "$latest_monitor" ]] && latest_monitor_status="$(jq -r '.status // "unknown"' "$latest_monitor")"
[[ -n "$latest_release" ]] && latest_release_status="$(jq -r '.status // "unknown"' "$latest_release")"
[[ -n "$latest_link" ]] && latest_link_status="$(jq -r '.status // "unknown"' "$latest_link")"

jq -n \
  --arg timestamp "$STAMP" \
  --argjson ledger_count "$ledger_count" \
  --argjson monitor_count "$monitor_count" \
  --argjson release_gate_count "$release_gate_count" \
  --argjson link_audit_count "$link_audit_count" \
  --arg latest_monitor "$latest_monitor" \
  --arg latest_monitor_status "$latest_monitor_status" \
  --arg latest_release "$latest_release" \
  --arg latest_release_status "$latest_release_status" \
  --arg latest_link "$latest_link" \
  --arg latest_link_status "$latest_link_status" \
  '{
    timestamp: $timestamp,
    counts: {
      run_ledgers: $ledger_count,
      monitor_reports: $monitor_count,
      release_gate_reports: $release_gate_count,
      link_audit_reports: $link_audit_count
    },
    latest: {
      monitor: {path: $latest_monitor, status: $latest_monitor_status},
      release_gate: {path: $latest_release, status: $latest_release_status},
      link_audit: {path: $latest_link, status: $latest_link_status}
    }
  }' | tee "$OUT_JSON" > "$LATEST_JSON"

{
  echo "# Blueprint Funnel Dashboard"
  echo
  echo "Generated: $STAMP"
  echo
  echo "| Proof | Count | Latest status | Latest file |"
  echo "|---|---:|---|---|"
  echo "| Run ledgers | $ledger_count | n/a | $LEDGER_DIR |"
  echo "| Monitor reports | $monitor_count | $latest_monitor_status | $latest_monitor |"
  echo "| Release gates | $release_gate_count | $latest_release_status | $latest_release |"
  echo "| Link audits | $link_audit_count | $latest_link_status | $latest_link |"
} | tee "$OUT_MD" > "$LATEST_MD"

echo "$OUT_JSON"
