#!/bin/bash
# Blueprint AI Pipeline -- Generate Pipeline Dashboard HTML
# Usage: ./generate-dashboard.sh [leads-dir]
# Outputs: pipeline-dashboard.html in repo root (auto-refresh every 60s)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEADS_DIR="${1:-$REPO_DIR/leads}"
OUTPUT="$REPO_DIR/pipeline-dashboard.html"

if [ "${1:-}" = "--help" ]; then
    echo "Usage: $0 [leads-dir]"
    echo ""
    echo "Generates an HTML dashboard showing status of all leads."
    echo "Output: $OUTPUT"
    exit 0
fi

python3 - "$LEADS_DIR" "$REPO_DIR" "$OUTPUT" <<'PYEOF'
import json, sys, os, glob, datetime

leads_dir = sys.argv[1]
repo_dir = sys.argv[2]
output_path = sys.argv[3]

leads = []
for f in sorted(glob.glob(os.path.join(leads_dir, '*.json'))):
    try:
        with open(f) as fh:
            p = json.load(fh)
        slug = p.get('slug', 'unknown')
        lead = {
            'name': p.get('lead_name', 'Unknown'),
            'business': p.get('business_name', 'Unknown'),
            'industry': p.get('industry', 'Unknown'),
            'slug': slug,
            'tier': p.get('lead_tier', 'unscored'),
            'score': p.get('lead_score', 0),
            'color': p.get('accent_color', '#007AFF'),
            'has_blueprint': os.path.exists(os.path.join(repo_dir, 'blueprints', f'{slug}.html')),
            'has_website': os.path.exists(os.path.join(repo_dir, f'{slug}-website', 'index.html')),
            'has_email': os.path.exists(os.path.join(repo_dir, 'delivery-emails', f'{slug}-delivery-email.html')),
            'intake_ts': p.get('intake_ts', ''),
            'blueprint_ts': p.get('blueprint_ts', ''),
            'website_ts': p.get('website_ts', ''),
            'email_ts': p.get('email_ts', ''),
        }
        bp_path = os.path.join(repo_dir, 'blueprints', f'{slug}.html')
        ws_path = os.path.join(repo_dir, f'{slug}-website', 'index.html')
        lead['bp_size'] = os.path.getsize(bp_path) // 1024 if lead['has_blueprint'] else 0
        lead['ws_size'] = os.path.getsize(ws_path) // 1024 if lead['has_website'] else 0
        leads.append(lead)
    except Exception as e:
        pass

total = len(leads)
complete = sum(1 for l in leads if l['has_blueprint'] and l['has_website'] and l['has_email'])
now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

rows = ''
for l in leads:
    status = 'READY' if (l['has_blueprint'] and l['has_website'] and l['has_email']) else 'WIP'
    status_color = '#22c55e' if status == 'READY' else '#eab308'
    tier_color = {'hot': '#ef4444', 'warm': '#f59e0b', 'cold': '#6b7280'}.get(l['tier'], '#9ca3af')
    bp_cell = f"<span style='color:#22c55e'>{l['bp_size']}KB</span>" if l['has_blueprint'] else "<span style='color:#ef4444'>MISSING</span>"
    ws_cell = f"<span style='color:#22c55e'>{l['ws_size']}KB</span>" if l['has_website'] else "<span style='color:#ef4444'>MISSING</span>"
    em_cell = "<span style='color:#22c55e'>BUILT</span>" if l['has_email'] else "<span style='color:#ef4444'>MISSING</span>"
    rows += f"""<tr>
      <td><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{l['color']};margin-right:8px;vertical-align:middle"></span>{l['name']}</td>
      <td>{l['business']}</td>
      <td>{l['industry']}</td>
      <td><span style="color:{tier_color};font-weight:600">{l['tier'].upper()}</span></td>
      <td>{bp_cell}</td>
      <td>{ws_cell}</td>
      <td>{em_cell}</td>
      <td><span style="color:{status_color};font-weight:700">{status}</span></td>
    </tr>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="60">
  <title>Blueprint AI Pipeline Dashboard</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
    h1 {{ font-size: 24px; margin-bottom: 4px; color: #f1f5f9; }}
    .subtitle {{ color: #94a3b8; font-size: 14px; margin-bottom: 24px; }}
    .stats {{ display: flex; gap: 16px; margin-bottom: 24px; }}
    .stat-card {{ background: #1e293b; border-radius: 8px; padding: 16px 24px; flex: 1; }}
    .stat-num {{ font-size: 32px; font-weight: 700; color: #f1f5f9; }}
    .stat-label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }}
    table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }}
    th {{ background: #334155; padding: 12px 16px; text-align: left; font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }}
    td {{ padding: 12px 16px; border-bottom: 1px solid #334155; font-size: 14px; }}
    tr:hover {{ background: #334155; }}
  </style>
</head>
<body>
  <h1>Blueprint AI Pipeline Dashboard</h1>
  <p class="subtitle">Last updated: {now} | Auto-refreshes every 60 seconds</p>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-num">{total}</div>
      <div class="stat-label">Total Leads</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{complete}</div>
      <div class="stat-label">Ready to Deliver</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{total - complete}</div>
      <div class="stat-label">Work in Progress</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{round(complete/total*100) if total else 0}%</div>
      <div class="stat-label">Completion Rate</div>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Lead Name</th>
        <th>Business</th>
        <th>Industry</th>
        <th>Tier</th>
        <th>Blueprint</th>
        <th>Website</th>
        <th>Email</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>"""

with open(output_path, 'w') as f:
    f.write(html)
print(f"Dashboard generated: {output_path}")
PYEOF
