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

# ── CANONICAL GENERATION STEER ───────────────────────────────────────────────
# PERMANENT FIX 2026-07-27 (marker BLUEPRINT-PODCAST-STEER-CANONICAL-20260727,
# EC-BLUEPRINT-PODCAST-THIRD-PERSON-SLIP-20260727):
# D3-02 kept failing on hosts saying "the business" / "this business" even though
# the SOURCE DOC already banned it — because the *generate-audio instruction* was
# hand-written fresh by whoever ran the build, and the ban list drifted every time.
# Cost a full regeneration on two consecutive leads (carlos-csm-power-bikes run3,
# rena-transit-system run1). The steer is now a generated per-lead artifact so every
# run passes the SAME text to NotebookLM instead of improvising it.
# Usage: notebooklm generate audio -n <nb> --length short --format deep-dive \
#          --json "$(cat podcasts/<slug>-podcast-steer.txt)"
_agent_names = [a.get("name", "") for a in agents[:6] if a.get("name")]
_agent_list = ", ".join(_agent_names[:-1]) + (" and " + _agent_names[-1] if len(_agent_names) > 1 else "")

steer = f"""Open with EXACTLY these words, spoken naturally in your own host voice: "{opening}"

THE SINGLE MOST IMPORTANT RULE — SECOND PERSON, ALWAYS. You are talking directly TO {first}, face to face, for the ENTIRE episode. Every reference to the company is "your business", "your company", "your operation", "your team", or "{biz}" by name.

These EXACT phrases are FORBIDDEN and will get the episode thrown out. Do not say any of them, not once, not in passing, not in the closing:
- "the business" / "this business" / "the company" / "this company"
- "the team" / "the owner" / "the operation"
- "her business" / "his business" / "their business" / "her team" / "his team" / "their team"
- "{first} has" / "{first} is" / "{first} runs" / "{first} needs" / "{first} wants"
- "source" / "sources" / "source material" / "this document" / "the report" / "the brief" / "we are analyzing"
Instead ALWAYS say: "your business", "your company", "your team", "you have", "you run", "you need", and "what you told us".
Read your closing line back to yourself before you say it — the ending is where hosts slip into "the business". Keep it second person all the way to the final word.

LENGTH: a full, unhurried deep dive of AT LEAST NINE MINUTES and no more than twelve. Roughly eighty seconds on EACH of the six AI Employees — do not shortchange the last two.

Body: walk through all six by name in order — {_agent_list}. For EACH one lead with the business benefit: the time it gives you back, the revenue it protects or recovers for you, the specific bottleneck it removes from your week, and what a normal week looks like for you once it is running.

Ground everything ONLY in what {first} told us on the intake form. Do NOT invent an average ticket, a close rate, admin hours, dollar figures, or percentages unless they were explicitly provided. Do NOT describe what the company does operationally — its customers, its equipment, its locations, its coverage — unless that was explicitly provided.

Sell the outcome, not the technology. Do not explain how the tech works. Do not talk about AI in general. Conversational and warm, never salesy, no marketing buzzwords. Close with a clean, complete spoken sign-off — in second person — telling {first} the next step is to open the written playbook and complete the qualifier page. Never speak or spell out any web address, domain, or file name."""

steer_out = os.path.join(REPO, "podcasts", f"{slug}-podcast-steer.txt")
open(steer_out, "w", encoding="utf-8").write(steer)
print(f"wrote {steer_out} ({len(steer)} bytes) — pass this VERBATIM to `notebooklm generate audio`")
