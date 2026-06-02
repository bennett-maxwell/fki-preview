#!/usr/bin/env python3
"""
Templatize the format-3 GOLD blueprint into a reusable TEMPLATE.html.

Deterministic token substitution: swap the Brent/CRMX lead-identity literals for
the {{TOKENS}} the blueprint-ai-skill orchestrator fills, while preserving 100% of
format-3's structure, CSS, custom chaptered player, and rich exemplar prose.

The orchestrator fills the mechanical tokens; the Stage-3 AI rewrites the bespoke
exemplar prose for the new company (same generation model the current template uses).

Usage: python3 templatize-format3.py <gold.html> <out_template.html>
"""
import re, sys, pathlib

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
html = src.read_text()

# Order matters: most-specific / longest literals first so we never partial-match.
subs = [
    # Full podcast URL -> single token (before slug/domain rules touch it).
    (r"https://bennett-maxwell\.github\.io/fki-preview/podcasts/brent-attaway\.mp3", "{{PODCAST_URL}}"),
    # Apply / qualify funnel URLs.
    (r"https://bennett-maxwell\.github\.io/fki-preview/apply/?", "{{APPLY_URL}}"),
    (r"https://bennett-maxwell\.github\.io/fki-preview/qualify\.html", "{{QUALIFY_URL}}"),
    # Lead full name -> token (before standalone first-name rule).
    (r"Brent Attaway", "{{LEAD_NAME}}"),
    # Podcast/file slug.
    (r"brent-attaway", "{{SLUG}}"),
    # Business name (CRMX appears 73x — all become the business token).
    (r"\bCRMX\b", "{{BUSINESS_NAME}}"),
    # Domain.
    (r"gocrmx\.com", "{{DOMAIN}}"),
    # CRM tool.
    (r"GoHighLevel", "{{CRM_TOOL}}"),
    # Remaining standalone first name (the person), e.g. "Prepared for Brent".
    (r"\bBrent\b", "{{FIRST_NAME}}"),
    # Any stray surname.
    (r"\bAttaway\b", "{{LEAD_NAME}}"),
]

counts = {}
for pat, repl in subs:
    html, n = re.subn(pat, repl, html)
    counts[repl] = counts.get(repl, 0) + n

out.write_text(html)

print(f"Templatized {src.name} -> {out.name}")
for repl, n in counts.items():
    print(f"  {repl}: {n} replacements")
# Residual lead-identity literals that escaped (should be zero).
residual = []
for term in ["Brent", "Attaway", "CRMX", "gocrmx", "brent-attaway", "GoHighLevel"]:
    c = len(re.findall(rf"\b{re.escape(term)}", html))
    if c:
        residual.append(f"{term}={c}")
print(f"  RESIDUAL lead literals: {residual if residual else 'NONE (clean)'}")
