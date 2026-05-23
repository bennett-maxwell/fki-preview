#!/usr/bin/env python3
"""Update tracker.html with Ready status for all v14 MP3s that exist on GitHub Pages."""
import re
import subprocess
from pathlib import Path

REPO = Path("/Users/openclaw/fki-preview")
TRACKER = REPO / "podcasts/tracker.html"
BASE_URL = "https://bennett-maxwell.github.io/fki-preview/podcasts"

LEADS = [
    ("lead-zachary-red-sands", "zachary-red-sands"),
    ("lead-branson-maxwell", "branson-maxwell"),
    ("lead-brittney-warnick", "brittney-warnick"),
    ("lead-chris-lpnw", "chris-lpnw"),
    ("lead-rey-31", "rey-31-consulting"),
    ("lead-court-lundberg", "court-lundberg"),
    ("lead-melissa-tash", "melissa-tash-srp"),
    ("lead-dave-wood", "dave-wood"),
    ("lead-brent-attaway", "brent-attaway"),
    ("lead-paul-muus", "paul-muus"),
    ("lead-rj-kitchenguard", "rj-kitchenguard"),
]

html = TRACKER.read_text()
updated = []
ready_count = 0

for card_id, slug in LEADS:
    mp3 = REPO / f"podcasts/{slug}-v14.mp3"
    url = f"{BASE_URL}/{slug}-v14.mp3"

    if not mp3.exists():
        print(f"SKIP {slug} — MP3 not downloaded yet")
        continue

    listen_btn = f'<a class="listen-btn" href="{url}" target="_blank" style="display:inline-block;padding:6px 16px;background:#166534;color:white;border-radius:20px;text-decoration:none;font-size:0.8rem;font-weight:600;">&#9654; Listen</a>'
    ready_badge = f'<span class="badge badge-ready">Ready</span>'

    # Replace the status div inside this lead card
    pattern = rf'(<div class="lead-card" id="{card_id}".*?<div class="status">)(.*?)(</div>\s*</div>)'
    replacement = rf'\1\n        {ready_badge}\n        {listen_btn}\n      \3'
    new_html = re.sub(pattern, replacement, html, count=1, flags=re.DOTALL)
    if new_html != html:
        html = new_html
        ready_count += 1
        updated.append(slug)
        print(f"OK {slug}")
    else:
        print(f"WARN {slug} — pattern not matched (check card id)")

# Update stats counters
queued_remaining = len(LEADS) - ready_count
html = re.sub(r'<div class="num" id="ready">\d*</div>', f'<div class="num" id="ready">{ready_count}</div>', html)
html = re.sub(r'<div class="num" id="queued">\d+</div>', f'<div class="num" id="queued">{queued_remaining}</div>', html)

TRACKER.write_text(html)
print(f"\nTracker updated: {ready_count} ready, {queued_remaining} remaining")
print(f"Updated: {', '.join(updated)}")
