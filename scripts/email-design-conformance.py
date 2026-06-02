#!/usr/bin/env python3
"""
Email Design Conformance — blueprint-ai-audit-skill v2.8 D5-16..D5-21 (all RED-LINE).

Verifies a blueprint delivery email matches the approved Advaita design. A hand-rolled
or drifted email FAILS, so it can never mint the 100% approval token (audit-gate.sh).

Usage: email-design-conformance.py <email_html_path>
Exit 0 = all checks pass. Exit 1 = at least one red-line fail (prints which).
"""
import re
import sys

BANNED_CTA = [
    "get your ai quote",
    "get a quote",
    "apply to work with",
    "apply now",
    "book a call",
    "schedule a call",
]
BANNED_HREF = ["/apply/", "/apply.html", "calendly", "cal.com", "calendar.google", "leadconnectorhq", "widget/booking"]

# Emoji ranges (variation selectors / pictographs / symbols). Plain text + â†’ arrow allowed.
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF\U0000FE00-\U0000FE0F\U00002190-\U000021FF\U00002B00-\U00002BFF]"
)
# allow the simple right-arrow U+2192 used in "See If You Qualify â†’"
ALLOWED = {"\u2192"}


def fail(checks):
    for cid, ok, detail in checks:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {cid}: {detail}")
    bad = [c for c in checks if not c[1]]
    if bad:
        print(f"FAIL: {len(bad)} red-line email-design check(s) failed.")
        sys.exit(1)
    print("PASS: email design conforms (D5-16..D5-21 all green).")
    sys.exit(0)


def main():
    if len(sys.argv) < 2:
        print("usage: email-design-conformance.py <email_html>")
        sys.exit(2)
    html = open(sys.argv[1], encoding="utf-8").read()
    low = html.lower()

    # D5-16 build-script provenance marker
    d16 = "<!-- blueprint-delivery-email v2 -->" in low

    # D5-17 Advaita palette present
    palette = all(t in low for t in ["#0071e3", "#1d1d1f", "#f5f5f7", "-apple-system"])

    # D5-18 CTA text + href correct, banned absent
    cta_text = "see if you qualify" in low
    href_qualify = bool(re.search(r'href="[^"]*qualify\.html', low))
    banned_text = any(b in low for b in BANNED_CTA)
    banned_href = any(b in low for b in BANNED_HREF)
    d18 = cta_text and href_qualify and not banned_text and not banned_href

    # D5-19 zero emoji
    emojis = [c for c in html if EMOJI_RE.match(c) and c not in ALLOWED]
    d19 = len(emojis) == 0

    # D5-20 no unrendered tokens
    d20 = "{{" not in html and "}}" not in html

    # D5-21 exactly one action anchor, and it points to qualify.html
    anchors = re.findall(r'<a\b[^>]*href="([^"]+)"', low)
    action = [h for h in anchors if "qualify.html" in h or "/apply" in h or "calendly" in h or "cal.com" in h]
    d21 = len(action) == 1 and "qualify.html" in action[0]

    checks = [
        ("D5-16", d16, "build-script provenance marker present" if d16 else "missing <!-- BLUEPRINT-DELIVERY-EMAIL v2 --> (hand-rolled?)"),
        ("D5-17", palette, "Advaita palette present" if palette else "missing #0071E3/#1D1D1F/#F5F5F7/-apple-system"),
        ("D5-18", d18, "CTA 'See If You Qualify' -> qualify.html, no banned" if d18 else f"cta_text={cta_text} href_qualify={href_qualify} banned_text={banned_text} banned_href={banned_href}"),
        ("D5-19", d19, "zero emoji" if d19 else f"{len(emojis)} emoji found: {emojis[:6]}"),
        ("D5-20", d20, "no unrendered {{tokens}}" if d20 else "unrendered {{ }} placeholders remain"),
        ("D5-21", d21, "exactly one CTA anchor -> qualify.html" if d21 else f"action anchors={action}"),
    ]
    fail(checks)


if __name__ == "__main__":
    main()
