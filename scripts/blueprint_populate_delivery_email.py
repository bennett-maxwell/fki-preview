#!/usr/bin/env python3
"""blueprint_populate_delivery_email.py <slug> — populate the FROZEN delivery-email template.

Replaces the retired scripts/build-delivery-email.sh (RL-DE2, removed 2026-07-17) for the BODY
build only. It does exactly one thing: substitute the 7 tokens in
templates/delivery-email-template.html from leads/<slug>.json.

v3.26 EMAIL TEMPLATE FREEZE is respected literally: structure, subject and CTA copy are READ-ONLY.
This script performs token substitution and NOTHING else — it never rewrites, restructures, or
restyles the body. If the template needs a change, that is a proposal to Bennett, not an edit here.

Hard asserts before it will write anything (mirrors the audit red-lines):
  - zero unresolved {{TOKENS}} remain
  - zero drive.google.com links
  - every http(s) URL points at the canonical hub host
  - podcast URL returns HTTP 200 in-window  (RL-DE4: no draft without a live podcast)

Usage: python3 scripts/blueprint_populate_delivery_email.py <slug> [--skip-live]
"""
import json, os, re, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = "hub.aiblueprintmarketing.com"
TEMPLATE = os.path.join(REPO, "templates", "delivery-email-template.html")


def http_status(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except Exception as e:
        return getattr(e, "code", 0)


def main():
    slug = sys.argv[1]
    skip_live = "--skip-live" in sys.argv
    p = json.load(open(os.path.join(REPO, "leads", f"{slug}.json"), encoding="utf-8"))
    html = open(TEMPLATE, encoding="utf-8").read()

    industry = (p.get("industry") or "").replace("_", " ")
    tokens = {
        "{{LEAD_FIRST_NAME}}": p.get("first_name") or p["lead_name"].split()[0],
        "{{BUSINESS_NAME}}": p["business_name"],
        "{{INDUSTRY}}": industry,
        "{{ACCENT_COLOR}}": p.get("accent_color") or "#4A1F63",
        "{{BLUEPRINT_URL}}": p["blueprint_url"],
        "{{PODCAST_URL}}": p["podcast_url"],
        "{{QUALIFY_URL}}": p["qualify_url"],
    }
    for k, v in tokens.items():
        html = html.replace(k, str(v))

    # --- hard asserts -------------------------------------------------------
    left = re.findall(r"\{\{[A-Za-z_]+\}\}", html)
    assert not left, f"unresolved tokens: {sorted(set(left))}"
    assert "drive.google.com" not in html, "Drive link in delivery email (banned)"
    bad = [u for u in re.findall(r'https?://[^"\'\s>]+', html) if HUB not in u]
    assert not bad, f"non-hub URLs: {bad}"

    if not skip_live:
        for label in ("blueprint_url", "podcast_url", "qualify_url"):
            st = http_status(p[label])
            print(f"  {label:<14} {p[label]}  -> HTTP {st}")
            assert st == 200, f"{label} is not live (HTTP {st}) — RL-DE4 blocks the draft"

    out_dir = os.path.join(REPO, "delivery-emails")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{slug}-delivery-email.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"wrote {out} ({len(html)} bytes)")
    # Subject per the frozen Stage-7 format.
    print(f"SUBJECT: Your AI Blueprint — {p['business_name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
