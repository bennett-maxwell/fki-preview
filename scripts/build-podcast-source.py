#!/usr/bin/env python3
"""build-podcast-source.py — render the 12-section NotebookLM podcast source doc
from a gen-blueprint-schema lead profile (leads/<slug>.json).

Mirrors the v1.8 source format used for mike-norton-origins-20260603 and bakes in
the direct-address red-lines (audit v2.12 D3-02 / skill v3.32 Stage 4):
  - exact opening line
  - second person only; the banned third-person phrasings are spelled out
  - duration target 12-15 min (canon window 6-20, target 12-18; ceiling guard)

Usage: python3 scripts/build-podcast-source.py <slug>
Writes podcasts/<slug>-podcast-source.md
"""
import json, sys, os, datetime, re

def clean(t):
    return re.sub(r"<[^>]+>", "", str(t or ""))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
slug = sys.argv[1]
p = json.load(open(os.path.join(REPO, "leads", f"{slug}.json"), encoding="utf-8"))

first = p.get("first_name") or p.get("lead_first_name") or p["lead_name"].split()[0]
biz = p["business_name"]
calc = p.get("calc", {})
agents = p.get("agents", [])
stack = p.get("stack", [])
gaps = p.get("gaps", [])
opening = f"Hi {first}, welcome. This walkthrough was built for you and {biz}, from what you told us."

sections = []
sections.append(f"1. About {first} and {biz}\n{clean(p.get('profile_note',''))} {clean(p.get('hero_sub',''))}")
sections.append("2. Current Tool Stack\n" + " ".join(f"{clean(s['tool'])} — {clean(s['role'])}." for s in stack[:6]))
sections.append(f"3. Industry Context\n{biz} operates in {clean(p.get('industry',''))}. {clean(p.get('market',''))}")
sections.append("4. Where Time Is Leaking\n" + " ".join(f"{clean(g['title'])}: {clean(g['desc'])}" for g in gaps[:4]))
sections.append("5. Six Recommended Agents\n" + ", ".join(a["name"] for a in agents[:6]) + ".")
for i, a in enumerate(agents[:6]):
    sections.append(f"{6+i}. Agent {i+1}: {a['name']}\n{clean(a['desc'])} Outcome for {biz}: {clean(a.get('outcome',''))}")
sections.append(
    "12. ROI Picture and Next Step\n"
    f"Use {first}'s stated numbers only: {calc.get('leads_label','')} monthly leads, "
    f"{calc.get('contract_label','')} average value, {calc.get('rate_label','')} close rate, "
    f"about {calc.get('hours_label','')} weekly admin hours. Conservative language, no guarantees. "
    f"Close by inviting {first} to open the written playbook and complete the qualifier. "
    f"The written playbook qualifier lives at https://bennett-maxwell.github.io/fki-preview/qualify.html — mention it as the qualifier page, never spell the URL aloud. No calendar-booking language."
)

doc = f"""<!-- v1.8 -->
PRIVATE AUDIO BRIEFING / AI Roadmap for {p['lead_name']} — {biz} / Prepared by Franchise Ki
Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}

Open the audio with EXACTLY these words: "{opening}"

DIRECT ADDRESS RULE: The audio must open with: {opening}
Audience: {p['lead_name']}, {biz}.
Speak TO {first} as "you" and "your" for the entire episode.
STRICT BANS (the episode fails review if any host breaks these): never refer to {biz} or {first}
in the third person — the words "the/this" + "business/company/owner" and "his/her/their" + "business/company/team"
must not be spoken; say "your business", "your company", or "your operation" instead.
Never mention where this briefing came from, never reference any written input behind the episode,
and never narrate like an outside analyst reviewing a case — you are talking directly with {first}.
Length: SHORT episode — concise walkthrough, not a lecture. Let it land at its natural short length and end cleanly.
CTA: complete the qualifier only; no calendar booking language.

12 SECTION AUDIO PACKAGE

""" + "\n\n".join(sections) + "\n"

out = os.path.join(REPO, "podcasts", f"{slug}-podcast-source.md")
open(out, "w", encoding="utf-8").write(doc)
print(f"wrote {out} ({len(doc)} bytes)")
