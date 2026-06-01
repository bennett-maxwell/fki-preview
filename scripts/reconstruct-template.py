#!/usr/bin/env python3
"""
reconstruct-template.py — Rebuild a clean, contamination-free TEMPLATE.html from
three line-aligned good blueprints (court / paul / branson).

Method (contamination-free by construction):
  - All three good files are exactly 2033 lines, line-aligned (clean `Nc N` diff hunks).
  - A line identical across all THREE (three different industries) contains zero
    client-specific data => pure skeleton => copy verbatim.
  - A line that differs is a token slot => reverse-substitute court's values to
    {{TOKENS}} that match clone-blueprint.sh's forward map exactly.
  - Final guard: scan the output; ANY residual court-specific string on a tokenized
    line => hard fail (means the reverse map is incomplete).
"""
import json
import re
import sys
import urllib.parse
from pathlib import Path

BP = Path(__file__).resolve().parent.parent / "blueprints"
LEADS = Path(__file__).resolve().parent.parent / "leads"

court = (BP / "court-lundberg.html").read_text().splitlines(keepends=True)
paul = (BP / "paul-muus.html").read_text().splitlines(keepends=True)
branson = (BP / "branson-maxwell.html").read_text().splitlines(keepends=True)

assert len(court) == len(paul) == len(branson), \
    f"line counts differ: court={len(court)} paul={len(paul)} branson={len(branson)}"

prof = json.loads((LEADS / "court-lundberg.json").read_text())

lead_name = prof["lead_name"]                       # Court Lundberg
first_name = lead_name.split()[0]                   # Court
business_name = prof["business_name"]               # Rare Breed Plumbing, Heating And Air
industry = prof["industry"]                          # plumbing and HVAC
accent = prof["accent_color"]                        # #124d77
key_metric = str(prof["key_metric"])                 # 150+
key_metric_label = prof["key_metric_label"]          # 5-Star Google Reviews
team_size = str(prof["team_size"])                   # 30
monthly_leads = str(prof["monthly_leads"])           # 260
services = prof.get("services", [])
services_str = ", ".join(services)
slug = prof["slug"]                                  # court-lundberg
method_name = business_name.split()[-1]              # Air
domain = business_name.lower().replace(" ", "").replace("'", "") + ".com"  # rarebreed...,...com


def lighten_hex(hex_color, factor=0.4):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


accent_light = lighten_hex(accent, 0.4)              # #7094ad
accent_mid = lighten_hex(accent, 0.2)                # #417092

lead_enc = urllib.parse.quote(lead_name)             # Court%20Lundberg or Court+Lundberg?
biz_enc = urllib.parse.quote(business_name)
# the live files use '+' for spaces (quote_plus); cover both forms
lead_encp = urllib.parse.quote_plus(lead_name)
biz_encp = urllib.parse.quote_plus(business_name)

qualify_url = (f"https://bennett-maxwell.github.io/fki-preview/qualify.html"
               f"?lead={lead_encp}&biz={biz_encp}&src={slug}")
apply_url = (f"https://bennett-maxwell.github.io/fki-preview/apply/"
             f"?lead={lead_encp}&biz={biz_encp}&src={slug}")
podcast_url = f"https://bennett-maxwell.github.io/fki-preview/podcasts/{slug}.mp3"
blueprint_url = f"https://bennett-maxwell.github.io/fki-preview/blueprints/{slug}.html"

# Ordered reverse-substitution map. LONGEST / most-specific FIRST so short tokens
# (Air, 30, 260, Court) never clobber a substring of a longer match.
SUBS = [
    (apply_url, "{{APPLY_URL}}"),
    (qualify_url, "{{QUALIFY_URL}}"),
    (podcast_url, "{{PODCAST_URL}}"),
    (blueprint_url, blueprint_url.replace(slug, "{{SLUG}}")),
    (f"command.{domain}", "command.{{DOMAIN}}"),
    (services_str, "{{SERVICES_LIST}}"),
    (business_name, "{{BUSINESS_NAME}}"),
    (domain, "{{DOMAIN}}"),
    (industry, "{{INDUSTRY}}"),
    ("The Air Method", "The {{METHOD_NAME}} Method"),
    ("The Air Standard", "The {{METHOD_NAME}} Standard"),
    ("Air Method", "{{METHOD_NAME}} Method"),
    ("Air Standard", "{{METHOD_NAME}} Standard"),
    (key_metric_label, "{{KEY_METRIC_LABEL}}"),
    (lead_name, "{{LEAD_NAME}}"),
    (key_metric, "{{KEY_METRIC}}"),
    (accent.lower(), "{{ACCENT_COLOR}}"),
    (accent_light.lower(), "{{ACCENT_LIGHT}}"),
    (accent_mid.lower(), "{{ACCENT_MID}}"),
    ("your current tools", "{{CRM_TOOL}}"),
    (f"bpod_{slug}", "bpod_{{SLUG}}"),
    (slug, "{{SLUG}}"),
    (first_name, "{{FIRST_NAME}}"),
]

# Line-specific numeric stat cards (whole-line replacement to avoid clobbering "30 days").
LINE_EXACT = {
    f'      <div class="num">{team_size}</div>\n': '      <div class="num">{{TEAM_SIZE}}</div>\n',
    f'      <div class="num">{monthly_leads}</div>\n': '      <div class="num">{{MONTHLY_LEADS}}</div>\n',
}

# Court-specific residue that must NOT survive on a tokenized line.
RESIDUE = [
    "Court", "Lundberg", "Rare Breed", "plumbing", "HVAC", "124d77",
    "7094ad", "417092", "150+", "court-lundberg", "rarebreed",
]

out = []
tokenized_lines = 0
for i, cline in enumerate(court):
    if cline == paul[i] == branson[i]:
        out.append(cline)                      # pure skeleton
        continue
    # token slot — reverse substitute
    if cline in LINE_EXACT:
        out.append(LINE_EXACT[cline])
        tokenized_lines += 1
        continue
    new = cline
    for needle, tok in SUBS:
        if needle:
            new = new.replace(needle, tok)
            # also handle case variants for hex colors already lowercased
    out.append(new)
    tokenized_lines += 1

result = "".join(out)

# ---- contamination guard: no court residue on any NON-skeleton line ----
problems = []
res_out = "".join(out)
for i, line in enumerate(out):
    if court[i] == paul[i] == branson[i]:
        continue  # skeleton, untouched by definition
    for r in RESIDUE:
        if r in line:
            problems.append((i + 1, r, line.rstrip()[:120]))

print(f"lines total          : {len(court)}")
print(f"skeleton (verbatim)  : {sum(1 for i,c in enumerate(court) if c==paul[i]==branson[i])}")
print(f"tokenized line slots : {tokenized_lines}")
print(f"sections in result   : {result.count('<section')}")
print(f"residue problems     : {len(problems)}")
for ln, r, txt in problems[:40]:
    print(f"  L{ln}: [{r}] {txt}")

if problems:
    print("RECONSTRUCTION FAILED — residue remains. Template NOT written.")
    sys.exit(1)

# remove the pre-existing build-meta comment line if it became line 1 token slot
(BP / "TEMPLATE.candidate.html").write_text(result)
print(f"WROTE {BP / 'TEMPLATE.candidate.html'}")
