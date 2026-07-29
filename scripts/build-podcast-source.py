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

# ── PERMANENT FIX 2026-07-28 (marker BLUEPRINT-PODCAST-SOURCE-SCHEMA-DRIFT-20260728,
# EC-BLUEPRINT-PODCAST-EMPTY-SECTIONS-20260728) ──────────────────────────────────
# DEFECT: this script read p["stack"], p["gaps"] and p["calc"], but NO lead JSON in
# leads/ has ever carried those keys — the gen-blueprint schema emits quiz.* instead.
# So sections 2 and 4 rendered as BARE HEADERS with no body, and section 12 emitted
# blank number placeholders ("  monthly leads,  average value"), on EVERY lead.
# Verified 2026-07-28 across bri-fresh, tom-reliant-bridge, rena-transit-system:
# stack/gaps/calc absent in all three; tom + rena were DELIVERED with 2 of 12
# sections empty. Fix: derive the stack and the time-leaks from quiz.* facts the
# lead actually submitted, and NEVER emit a section header with an empty body.
quiz = p.get("quiz", {}) or {}

def _has(v):
    """True only for a real submitted value — 'None'/'none'/'' are non-answers."""
    s = str(v or "").strip()
    return bool(s) and s.lower() not in ("none", "n/a", "na", "-", "0 ")

def _build_stack_body():
    if stack:
        return " ".join(f"{clean(s['tool'])} — {clean(s['role'])}." for s in stack[:6])
    # Key spellings differ between GHL field sets: the live GPCi3 form emits
    # communication_tools, older profiles used communication_channels. Accept both —
    # on shak-sevaa-lightwork the single-key lookup reported "no communication" for a
    # lead who answered "Email Only", which would have had the hosts contradict him.
    # ALSO: only assert an absence when the lead was actually ASKED and answered a
    # non-answer ("None"). If the key is absent entirely the question was never put to
    # them, so say nothing — "no AI tool already in hand" was being asserted about
    # leads who were never asked about AI tooling.
    have, missing = [], []
    for label, keys in (("storage", ("storage_tools",)),
                        ("CRM", ("crm_tools",)),
                        ("project management", ("project_management_tools",)),
                        ("communication", ("communication_tools", "communication_channels")),
                        ("AI tool already in hand", ("current_ai_tool",))):
        present_key = next((k for k in keys if k in quiz), None)
        if present_key is None:
            continue  # never asked — never assert either way
        val = quiz.get(present_key)
        (have if _has(val) else missing).append(
            f"{clean(val)} is your {label}" if _has(val) else f"no {label}")
    bits = []
    if have:
        bits.append("Here is exactly what you are running on today, in your own words: "
                    + "; ".join(have) + ".")
    if _has(quiz.get("response_speed")):
        bits.append(f"You answer new inquiries {clean(quiz['response_speed'])}, and that standard is yours, not a tool's.")
    if missing:
        bits.append("And the gaps you named: " + ", ".join(missing)
                    + ". Treat a light stack as an advantage — there is no tangle of "
                      "half-configured tools to unwind first. Never frame it as criticism.")
    return " ".join(bits)

def _build_leaks_body():
    if gaps:
        return " ".join(f"{clean(g['title'])}: {clean(g['desc'])}" for g in gaps[:4])
    leaks = []
    if not _has(quiz.get("crm_tools")):
        leaks.append("With no CRM, every new inquiry starts life inside a conversation thread, so "
                     "the record has to be reconstructed by hand later instead of just existing.")
    if _has(quiz.get("response_speed")):
        leaks.append(f"Answering new inquiries {clean(quiz['response_speed'])} is a standard held by a person, "
                     "not a system — so it holds only when someone on the team is free to hold it.")
    if not _has(quiz.get("project_management_tools")):
        leaks.append("With no project-management tool, coordination happens ad hoc, so the next step "
                     "lives in someone's memory instead of somewhere everyone can see it.")
    if str(quiz.get("automation_maturity", "")).strip().lower() in ("none", "low", ""):
        leaks.append("With automation maturity at none, every piece of repeat admin is still being "
                     "done by hand.")
    for area in (quiz.get("operational_stress_areas") or [])[:2]:
        if _has(area):
            leaks.append(f"You named {clean(area)} as a stress area.")
    if not leaks:
        return ""
    return ("Walk these through as capacity you get back, never as criticism. "
            + " ".join(leaks))

sections = []
sections.append(f"1. About {first} and {biz}\n{clean(p.get('profile_note',''))} {clean(p.get('hero_sub',''))}")
_stack_body = _build_stack_body()
if _stack_body.strip():
    sections.append("2. Current Tool Stack\n" + _stack_body)
sections.append(f"3. Industry Context\n{biz} operates in {clean(p.get('industry','')).replace('_',' ')}. {clean(p.get('market',''))}")
_leaks_body = _build_leaks_body()
if _leaks_body.strip():
    sections.append("4. Where Time Is Leaking\n" + _leaks_body)
sections.append("5. Six Recommended Agents\n" + ", ".join(a["name"] for a in agents[:6]) + ".")
for i, a in enumerate(agents[:6]):
    sections.append(f"{6+i}. Agent {i+1}: {a['name']}\n{clean(a['desc'])} Outcome for {biz}: {clean(a.get('outcome',''))}")
# PERMANENT FIX 2026-07-28: only name a number the lead actually submitted, and
# state the withheld ones as explicit DO-NOT-INVENT bans. The old version emitted
# blank placeholders ("  monthly leads,  average value") because calc was always {},
# which reads to the host as an invitation to fill the gap with a plausible figure.
# Also: the literal qualifier URL/filename is no longer written into the source doc
# at all (EC-PODCAST-SPOKEN-URL) — a filename in the doc is a filename the host can
# read aloud, which is exactly how Barbara's episode ended on a spoken URL.
_num_have, _num_missing = [], []
for _label, _key, _qkey in (("monthly leads", "leads_label", "monthly_leads"),
                            ("average value", "contract_label", None),
                            ("close rate", "rate_label", None),
                            ("weekly admin hours", "hours_label", None)):
    _v = calc.get(_key) or (p.get(_qkey) if _qkey else None) or (quiz.get(_qkey) if _qkey else None)
    if _has(_v) or (str(_v).strip() == "0" and _label == "monthly leads"):
        _num_have.append(f"{clean(_v)} {_label}")
    else:
        _num_missing.append(_label)

_roi = [f"Ground this ONLY in what {first} actually submitted."]
if _num_have:
    _roi.append("On record: " + ", ".join(_num_have) + ".")
if str(p.get("monthly_leads", quiz.get("monthly_leads", ""))).strip() in ("0", "0.0"):
    _roi.append("There are ZERO inbound leads a month right now — do NOT imply any lead volume exists.")
if _num_missing:
    _roi.append("There is NO " + ", NO ".join(_num_missing)
                + " on record — do NOT state, guess, or imply any of those.")
_roi.append("No dollar projections, no percentages, no guarantees. Conservative language throughout.")
_roi.append(
    f'Then close the episode properly: say "to wrap up", tell {first} that your next step is to open '
    'your written playbook and complete the qualifier page, and thank them for listening. '
    'No calendar-booking language. The final words of the episode must be a genuine spoken '
    'sign-off, not the call to action alone.')
# D4-09 requires the tracked qualifier token to be present in the source (it proves the funnel
# points at the qualifier and NOT the retired blueprint.meetadvaita.com/apply URL). But
# EC-PODCAST-SPOKEN-URL says a readable filename is a filename a host can read aloud — that is
# how Barbara's episode ended on a spoken URL. Both rules are satisfied by carrying the token as
# an explicitly NON-SPOKEN routing annotation with the ban welded to it, never as prose the host
# could narrate. Keep the bare token: a prefilled ?lead=/?biz= query string fails D4-09.
_roi.append(
    'FUNNEL TARGET — internal routing token, NEVER spoken: qualify.html . Speak of it ONLY as '
    '"the qualifier page". NEVER say, spell, or read aloud any web address, domain, or file name.')
sections.append("12. ROI Picture and Next Step\n" + " ".join(_roi))

doc = f"""<!-- v1.9 -->
PRIVATE AUDIO BRIEFING / AI Roadmap for {p['lead_name']} — {biz} / Prepared by Franchise Ki
Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}

Open the audio with EXACTLY these words: "{opening}"

DIRECT ADDRESS RULE: The audio must open with: {opening}
Audience: {p['lead_name']}, {biz}.
Speak TO {first} as "you" and "your" for the entire episode.
STRICT BANS (the episode fails review if any host breaks these): never refer to {biz} or {first}
in the third person — the words "the/this" + "business/company/owner" and "his/her/their" + "business/company/team"
must not be spoken; say "your business", "your company", or "your operation" instead. Never say "she",
"her", "he", "him", "{first} has", "{first} is", or "{first} runs" — you are speaking TO {first}, never about {first}.
Never mention where this briefing came from, never reference any written input behind the episode,
and never narrate like an outside analyst reviewing a case — you are talking directly with {first}.
These EXACT words must NEVER be spoken, not once: "source", "sources", "source material",
"this document", "the document", "the report", "the brief", "the material", "we are analyzing",
"we're analyzing". There is no document in this conversation — there is only what {first} told us.
Say "what you told us" instead. (Added 2026-07-28: the steer alone banned these and a host still
said "sources" on shak-sevaa-lightwork, costing a full regeneration — the ban now lives in the
ingested source too, not only in the per-run instruction.)
LENGTH: a full, unhurried deep dive of AT LEAST NINE MINUTES and no more than twelve. Spend roughly
eighty seconds on EACH of the six AI Employees — do not shortchange the last two. This is a complete
walkthrough, not a summary.
MANDATORY CLOSING: the episode must end with an explicit spoken wrap-up and sign-off — say "to wrap up",
give {first} the next step in the words "your next step is", and close by thanking {first} for listening.
Never stop immediately after the call to action; the final words must be a real sign-off.
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

Sell the outcome, not the technology. Do not explain how the tech works. Do not talk about AI in general. Conversational and warm, never salesy, no marketing buzzwords. Never speak or spell out any web address, domain, or file name — refer to it only as "the qualifier page".

MANDATORY CLOSING — the episode is rejected without it. Do NOT stop talking the moment you give the call to action. End with a real, explicit, spoken wrap-up in second person, in this order: say "to wrap up", then "your next step is to open your written playbook and complete the qualifier page", then thank {first} for listening. The final words of the episode must be that sign-off. An episode that ends immediately after the call to action, or trails off mid-thought, fails review and has to be regenerated."""

steer_out = os.path.join(REPO, "podcasts", f"{slug}-podcast-steer.txt")
open(steer_out, "w", encoding="utf-8").write(steer)
print(f"wrote {steer_out} ({len(steer)} bytes) — pass this VERBATIM to `notebooklm generate audio`")
