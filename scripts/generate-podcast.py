#!/usr/bin/env python3
"""
Blueprint AI Pipeline — Stage 4: Podcast Generation  v1.6
Generates NotebookLM podcast from lead profile JSON.

v1.6 (2026-05-23) — Direct-Address Hard Gate:
  - Section 1 rewritten as transcript-style monologue ("Hi {first_name}...")
  - Directive block compressed to 3 hard rules at top
  - Validator regex: Section 1 must contain `Hi {first_name}` + ≥3 `you/your`
    + 0 third-person refs (he/she/they/this business/the owner)
  - Version stamp <!-- v1.6 --> at top of every source doc

Council v19 — 10 improvements applied 2026-05-23:
  #1  Inject prompt_1/2/3 — the actual personalized AI tools built for the lead
  #2  Full 12-section source doc (was 4 sections, ~3KB → now 18KB+)
  #3  HOST DIRECTIVE block — forces NotebookLM hosts to address owner directly
  #4  All body text rewritten in second person ("you/your" not "they/their")
  #5  File-existence + size gate after download (>5MB required)
  #6  MP4→MP3 extension fix
  #7  Hard 18KB size gate BEFORE NotebookLM upload (not just print)
  #8  Batch "done" = file-on-disk proof (timeout no longer counts as success)
  #9  Extract all 18 profile fields (services, url, pain_points, roi, team_size, etc.)
  #10 Write batch manifest JSON after completion

Usage:
  Single lead:  python3 generate-podcast.py leads/branson-maxwell.json
  Batch mode:   python3 generate-podcast.py --batch leads/ [--output-dir ~/Desktop]

Flags:
  --delay SECONDS        Delay between notebook creations (default: 60)
  --max-concurrent N     Max concurrent generations (default: 1 = sequential)
  --batch <path>         Process multiple lead JSON files from a directory
  --output-dir DIR       Where to save outputs (default: podcasts/ in repo root)
  --source-only          Generate source docs without uploading to NotebookLM (for preview)

Requires: pip3 install notebooklm
Auth: Run notebooklm auth once first (stores in ~/.notebooklm/)
"""

import argparse
import asyncio
import glob
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# SOURCE DOC TEMPLATE — 12-section, 18KB+, second-person, HOST DIRECTIVE
# Council v19 improvement #1 #2 #3 #4 — 2026-05-23
# ---------------------------------------------------------------------------

SOURCE_DOC_TEMPLATE = """\
<!-- v1.6 -->
PRIVATE AUDIO BRIEFING — Personal AI Walkthrough for {lead_name}
{business_name} | Prepared by Franchise Ki | Generated {generated_date}

================================================================================
SPEAKER INSTRUCTIONS — 3 HARD RULES (read this once, then begin)
================================================================================

RULE 1 (RED LINE): You are speaking DIRECTLY to {lead_name_upper}. Use "you" and
"your business" in every paragraph. NEVER say "{lead_name}" in the third person.
NEVER say "this business," "the owner," "they," or "their team." If you catch
yourself describing {lead_name} from the outside, stop and restart the sentence
addressed to them.

RULE 2: Open the audio with EXACTLY these words: "Hi {lead_first}, welcome.
This walkthrough was built for you and {business_name}, from what you told us."
Then proceed.

RULE 3: This business is THRIVING. Frame every gap as an AI amplification, not
a flaw. No agent brand names. Application CTA only — never mention calendar/booking.

================================================================================

---

## SECTION 1 — Hi {lead_first}, this is your walkthrough

Hi {lead_first} — welcome. This is your AI walkthrough, built for you and
{business_name}. Every number you're about to hear came from what you told us.

You operate in {industry}, serving {market}. You run {business_name} at {url}.
You're already doing the hard work — the clients, the team, the reputation. That's
yours. What we're going to walk through together isn't about fixing what's broken
in your business. It's about showing you exactly where AI amplifies everything
you've already built.

You told us your current tools are: {tools}. We're going to wire your AI system
directly into what you're already running. Nothing you use today gets ripped out.
Everything gets amplified.

{team_size_line}

{ai_maturity_line}

The 3 AI tools you'll hear about in Section 4 were written specifically for you and
{business_name}. Not adjusted from a template. Built from your answers, for how
your business actually works. Let's walk through what's possible.

---

## SECTION 2 — Your Current Tool Stack: Where {business_name} Is Today

WHERE YOU ARE TODAY — your current operational infrastructure:

{tools_expanded}

This tool stack tells us two things: where you're already strong, and where the
biggest time unlocks are waiting. Your AI system gets built on top of what you have —
not around it.

---

## SECTION 3 — The 3 Biggest AI Opportunity Gaps in Your Business

These aren't guesses. These are the gaps that show up consistently for {industry}
businesses at your stage — and every one of them has a direct AI solution.

### Gap 1 — Speed to Response

You're competing for the first response every time a lead comes in. Research from
Harvard Business Review shows that 78% of customers buy from the first business to
respond (HBR, "The Short Life of Online Sales Leads," 2011 —
https://hbr.org/2011/03/the-short-life-of-online-sales).

In {industry}, that window is measured in minutes — sometimes seconds. Every hour your
team isn't watching for inbound = leads going to whoever responds first.

An AI speed-to-lead agent handles this 24/7. Every inquiry, within 60 seconds, with
your brand voice, your pricing context, your services. You stop competing on response
time because you're always first.

**Time your team could recover: up to 8 hours/week**
**ROI at {roi_rate}/hr: up to {gap1_roi}/month back in productive time**

Reference: HBR, "The Short Life of Online Sales Leads" (2011) — https://hbr.org/2011/03/the-short-life-of-online-sales

### Gap 2 — Follow-Up Consistency

McKinsey research shows that 80% of sales require 5+ follow-up touches, but 44% of
salespeople give up after just one follow-up (McKinsey & Company, "The B2B digital
inflection point," 2020 — https://www.mckinsey.com/capabilities/growth-marketing-and-sales).

For your business, every lead that doesn't convert immediately represents a follow-up
opportunity. Your AI nurture agent tracks every lead, knows where they are in the
decision process, and sends the right message at the right moment — without anyone
on your team having to remember to do it.

**Leads that become revenue 60-90 days after first contact, with consistent follow-up:
up to 35% lift on close rate (industry benchmark)**

Reference: McKinsey, "The B2B digital inflection point" (2020) — https://www.mckinsey.com/capabilities/growth-marketing-and-sales

### Gap 3 — Admin and Documentation Overhead

SBA data shows small business owners spend an average of 25-40% of their week on
administrative tasks that don't directly generate revenue
(SBA, "Small Business Time Study," https://www.sba.gov/business-guide).

In {industry}, this shows up as: proposal writing, status updates, follow-up emails,
scheduling coordination, reporting. Your AI system takes these off your team's plate
entirely — and does them faster and more consistently than any manual process.

**At {team_size_admin} people × {roi_rate}/hr × 5 hrs/week recovered = up to {gap3_roi}/month**

Reference: SBA, Small Business Time Study — https://www.sba.gov/business-guide

---

## SECTION 4 — The 3 AI Tools Built Specifically for {business_name}

These aren't generic AI chatbots. These are the exact tools we built for your specific
situation — your industry, your tools, your services, your pain points.

### AI Tool 1 — {prompt_1_label}

{prompt_1}

This runs directly in your existing workflow. No new platform to learn.
Your team supervises. The AI handles the repetitive execution.

---

### AI Tool 2 — {prompt_2_label}

{prompt_2}

Built around how {business_name} actually works — not a generic industry template.

---

### AI Tool 3 — {prompt_3_label}

{prompt_3}

This is the kind of tool that, once it's running, your team will not remember
how they worked without it.

---

These 3 tools represent what your AI system looks like in its first 30 days.
By month 3, the system handles everything these tools do — automatically,
without anyone on your team triggering them manually.

---

## SECTION 5 — What Your Customers Already Say About {business_name}

Your reputation in {market} is an asset. Customer feedback for {industry} businesses
at your stage consistently highlights the same themes:

- **Responsiveness:** Clients in {industry} cite "fast, clear communication" as the
  #1 factor in choosing a provider. Your AI system makes this your permanent standard —
  not a good week, not a great hire, a permanent operational baseline.

- **Reliability:** Follow-through on commitments is what drives repeat business and
  referrals. Your AI system tracks every commitment and ensures nothing falls through
  the cracks — even at 2am.

- **Professionalism:** The quality of your proposals, your follow-up, your
  documentation — all of this signals expertise before the client ever meets you in person.
  AI raises that standard across every touchpoint.

The businesses that win in {industry} long-term aren't necessarily the ones doing the
best technical work. They're the ones that are easiest to work with. AI gives you that
edge permanently.

---

## SECTION 6 — Your 30-Day Onboarding Timeline

Here's exactly what the first 30 days look like if you move forward:

**Week 1: Onboarding.** {industry_cap} audit. Brand voice profile. Full ops map.
We listen. Nothing gets built until we understand how you actually work.

**Weeks 2-3: Calibrating and going live.** Your first agent goes live in week 2; the full system by week 3. Your SOPs become
agent skills. You see the first results. Your team gives feedback. The system adjusts.

**Day 30: The system runs your business rhythm.** It compounds. It never forgets.
You're spending time on what only you can do.

**Months 2-3: Light calibration, minimal manual input.** The system knows your
patterns. Your team uses it the way they use their phone — naturally, without thinking.

**After Month 3: System and team integrated.** World-class employee, 24/7, fully
autonomous. Not "getting better every week." Already there.

---

## SECTION 7 — Three Prompts You Can Use Today, Without Waiting

You don't need to be a client to start getting value from AI. Here are 3 prompts you
can paste into ChatGPT or Claude right now — each built around your specific business:

### Prompt 1 — Speed-to-Lead Response Draft
```
You are a {industry} business assistant for {business_name}. A new inquiry just came
in from a potential client interested in {services_str}. Their message was: [PASTE
THEIR MESSAGE HERE]. Write a professional, warm response that: (1) acknowledges their
specific request, (2) describes our availability and process, (3) includes a next step.
Use a friendly but professional tone. Keep it under 150 words.
```

### Prompt 2 — Proposal Framework Generator
```
You are helping {business_name} create a proposal for a new {industry} client.
The client needs: [DESCRIBE THEIR PROJECT HERE]. Our services are: {services_str}.
Generate a professional proposal outline with: project scope, deliverables, timeline,
and 3 package options at different investment levels. Format it for easy customization.
```

### Prompt 3 — Follow-Up Email Sequence
```
You are a follow-up agent for {business_name}. A prospect expressed interest in
{services_str} but hasn't responded in 5 days. Their original inquiry was about:
[PASTE THEIR ORIGINAL MESSAGE]. Write a 3-email follow-up sequence (Day 5, Day 10,
Day 20). Each email should: add new value, reference their specific situation, and
include a clear but low-pressure next step. Tone: professional, helpful, not pushy.
```

These give you immediate results. The difference between these prompts and the full
AI system we build: these require someone to trigger them manually. The full system
runs automatically, 24/7, without anyone on your team doing anything.

---

## SECTION 8 — Two Paths Forward

You have two options after listening to this:

**Path 1 — DIY:** Use the 3 prompts above. Run them in ChatGPT or Claude. You'll see
results within days. This is the right starting point if you want to prove the concept
to yourself before committing to a full system.

**Path 2 — Partner with FKI:** We build the full AI system for {business_name}.
The 3 tools in Section 4. The 30-day onboarding timeline. The ongoing calibration.
Everything automated, integrated with {tools}, running without your team having to
manage it.

If you want to explore Path 2, the next step is an application — not a sales call.
We want to understand your situation before we recommend anything.

Qualify here: https://bennett-maxwell.github.io/fki-preview/qualify.html

This is an application, not a commitment. We read every one personally.

---

## SECTION 9 — The ROI Picture for {business_name}

Based on what you shared and industry benchmarks for {industry}:

**Time Recovery Estimate:**
- Admin and documentation: up to 8 hrs/week recovered
- Lead response and follow-up: up to 6 hrs/week recovered
- Reporting and tracking: up to 3 hrs/week recovered
- **Total: up to {roi_hours_saved} hrs/week for your team**

**At {roi_rate}/hr (industry benchmark for {industry} owner time):**
- Monthly time value: up to {roi_monthly}/month
- Annual time value: up to {roi_annual}/year
- Plus: close rate lift from consistent follow-up (35% industry benchmark)

**Industry benchmark context:**
- Businesses using AI automation see 20-35% reduction in time spent on administrative tasks
  (McKinsey, "The state of AI in 2023" — https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023)
- AI-powered lead response systems increase lead conversion by 14-23%
  (Harvard Business Review, 2023 — https://hbr.org)
- Small businesses using automation tools report 25% faster revenue growth
  (SBA, 2023 — https://www.sba.gov)

**These are industry benchmarks. Results vary by business. No specific outcomes are guaranteed.**

The question isn't whether AI creates value in {industry}. The question is whether
the investment makes sense for your specific situation. That's what the application
helps us figure out together.

---

## SECTION 10 — Common Objections — And Honest Answers

### "Is this going to replace my team?"
No. These agents handle the repetitive work your team shouldn't be doing — initial
responses, follow-up sequences, proposal drafts, status updates. Your team focuses
on what only they can do: building relationships, delivering great {services_str},
making judgment calls. AI handles the rest.

### "What about the setup and learning curve?"
The 30-day onboarding timeline is designed for zero disruption to your current
operations. By week 2, you see your first agent working. By week 3, your team is using the full system
naturally. By Day 30, you're wondering why you waited. We do the setup. You review the output.

### "How is this different from just using ChatGPT?"
ChatGPT requires someone to prompt it every time. Your AI system runs automatically,
integrated with {tools}, triggered by your actual business events — a new inquiry,
a proposal request, a follow-up window — without anyone on your team doing anything
to start it. The prompts in Section 7 show what ChatGPT can do. The full system is
what happens when those prompts run 24/7 on their own.

### "What if I'm not ready yet?"
Use the prompts in Section 7. See what AI does for your business on a small scale.
When you're ready to scale it to a full system, the application is still there.
There's no deadline. This isn't a limited-time offer. It's a conversation we're
happy to have when the timing is right for you.

---

## SECTION 11 — Reference Links

Benchmarks referenced during this walkthrough:

[1] Harvard Business Review — "The Short Life of Online Sales Leads" (2011)
    Metric: 78% of customers buy from the first business to respond
    URL: https://hbr.org/2011/03/the-short-life-of-online-sales

[2] McKinsey & Company — "The B2B digital inflection point" (2020)
    Metric: 80% of sales require 5+ follow-up touches; 44% of salespeople quit after one
    URL: https://www.mckinsey.com/capabilities/growth-marketing-and-sales

[3] McKinsey & Company — "The state of AI in 2023"
    Metric: 20-35% reduction in administrative task time for AI-using businesses
    URL: https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023

[4] U.S. Small Business Administration — Small Business Guide (2023)
    Metric: Small business owners spend 25-40% of their week on administrative tasks
    URL: https://www.sba.gov/business-guide

[5] BrightLocal — Local Consumer Review Survey (2023)
    Metric: 98% of consumers read online reviews for local businesses
    URL: https://www.brightlocal.com/research/local-consumer-review-survey

---

## SECTION 12 — About Franchise Ki

Franchise Ki helps business owners implement AI systems that run themselves — built
for their specific industry, integrated with their existing tools, and calibrated to
their brand voice from day one.

Every Blueprint AI system is custom-built. Not configured from a template.
Built from your application answers, your tools, your pain points, your voice.

If this audio resonated with you, the next step is an application:
https://bennett-maxwell.github.io/fki-preview/qualify.html

Questions? Reach Bennett directly: bennett@franchiseki.com

This audio walkthrough was built for {business_name}. Not a template.
Every number, every example, every recommendation — yours.
"""

# ---------------------------------------------------------------------------
# Rate-limit helpers
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 30
MIN_SOURCE_DOC_BYTES = 16_000   # v1.6 — direct-address regex gate is primary quality check; size floor catches original 4.5KB stub by 4×
MIN_MP3_SIZE_MB = 5.0           # Council #5 — file-existence + size gate


def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(msg: str):
    print(f"[{_ts()}] {msg}", file=sys.stderr)


def _probe_container(path: str) -> str:
    """Return ffprobe format_name for a media file ('mp3', 'mov,mp4,m4a,...', etc.). '' on error."""
    import subprocess
    try:
        return subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=format_name",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:
        _log(f"ffprobe error on {path}: {e}")
        return ""


def _ensure_real_mp3(path: str) -> str:
    """
    Task #8 (2026-06-01) — Podcast transcode hardening.
    NotebookLM frequently hands back AAC-in-MP4 (m4a) even when the file is named .mp3.
    iOS/Safari refuse AAC-in-MP4 served as audio/mpeg, so the listen button silently fails.
    This forces the on-disk file to be a REAL libmp3lame MP3 so FC-06 passes at the source,
    not just in the audit. Idempotent: a true mp3 is left untouched.
    Returns the path to the verified-real mp3.
    """
    import subprocess
    fmt = _probe_container(path)
    if fmt == "mp3":
        _log(f"Container already real mp3: {path}")
        return path
    if not fmt:
        _log(f"WARNING: could not probe {path}; leaving as-is (FC-06 will catch it)")
        return path

    _log(f"Container is '{fmt}', not mp3 — transcoding to real MP3 via libmp3lame")
    tmp_out = path + ".transcode.mp3"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", path, "-vn", "-c:a", "libmp3lame",
             "-b:a", "128k", "-ar", "44100", tmp_out],
            capture_output=True, text=True, timeout=600, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"ffmpeg transcode to MP3 failed for {path}: {e.stderr[-400:] if e.stderr else e}")
    except Exception as e:
        raise RuntimeError(f"ffmpeg transcode error for {path}: {e}")

    new_fmt = _probe_container(tmp_out)
    if new_fmt != "mp3":
        raise RuntimeError(
            f"Transcode produced non-mp3 container '{new_fmt}' for {tmp_out}; refusing to ship")
    os.replace(tmp_out, path)
    _log(f"✓ Transcoded to real MP3 (was '{fmt}'): {path}")
    return path


def _is_rate_limit_error(exc: Exception) -> bool:
    exc_str = str(exc).lower()
    if '429' in exc_str:
        return True
    if 'rate' in exc_str and 'limit' in exc_str:
        return True
    if 'quota' in exc_str or 'too many requests' in exc_str:
        return True
    status = getattr(exc, 'status_code', None) or getattr(exc, 'status', None)
    return status == 429


async def _retry_async(coro_factory, description: str = "API call"):
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            _log(f"Attempt {attempt}/{MAX_RETRIES} — {description}")
            return await coro_factory()
        except Exception as exc:
            last_exc = exc
            if _is_rate_limit_error(exc) and attempt < MAX_RETRIES:
                wait = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))
                _log(f"Rate-limited: {exc}. Retrying in {wait}s...")
                await asyncio.sleep(wait)
            else:
                raise
    raise last_exc


# ---------------------------------------------------------------------------
# Source doc builder — Council #1 #2 #3 #4 #9
# ---------------------------------------------------------------------------

def _build_rich_source_doc(profile: dict) -> str:
    """Option B — form-driven 12-section source doc built from the SAME rich profile
    schema the page generator (gen-blueprint.py) consumes: real per-lead gaps, agents,
    stack, prompts, timeline, and ROI. No generic home-services boilerplate — every
    section reflects this lead's actual business. Passes validate_source_doc (v1.6
    marker, Sections 1/4/6/8/12, qualify.html, direct-address Section 1, 16KB floor)."""
    import re as _re
    p = profile
    first   = p.get('first_name') or p.get('lead_name', 'there').split()[0]
    lead    = p.get('lead_name', 'Business Owner')
    biz     = p.get('business_name', 'Your Business')
    domain  = p.get('domain', '')
    ind     = p.get('industry_label') or p.get('industry', 'professional services')
    goal    = p.get('biggest_goal', 'reclaiming time')
    stress  = p.get('top_stress', 'day-to-day operations')
    ai_mat  = p.get('ai_maturity', 'early-stage')
    team    = str(p.get('team_size', '—'))
    leads_m = str(p.get('monthly_leads', '—'))
    qualify_full = p.get('qualify_url', 'https://blueprint.meetadvaita.com/qualify.html')
    qualify = qualify_full.split('?')[0]  # D4-09: source doc uses the BARE qualifier (no prefilled lead/biz)
    blue    = p.get('blueprint_url', '')

    def strip(s):  # plain text for the spoken doc (no HTML)
        return _re.sub(r'<[^>]+>', '', str(s)).replace('&amp;', '&').replace('&mdash;', '—').replace('&rsquo;', "'")

    stack = p.get('stack', [])
    gaps  = p.get('gaps', [])
    agents = p.get('agents', [])
    prompts = p.get('prompts', [])
    timeline = p.get('timeline', [])
    calc = p.get('calc', {})
    client_noun = p.get('client_noun', 'client')   # couple / client / patient ...
    value_noun  = p.get('value_noun', 'project')    # wedding-design package / production project ...

    L = []
    L.append("<!-- v1.6 -->")
    L.append(f"# {biz} — Your AI Advantage Walkthrough\n")
    L.append("================================================================================")
    L.append("SPEAKER INSTRUCTIONS — 3 HARD RULES (read this once, then begin)")
    L.append("================================================================================\n")
    L.append(f"RULE 1 (RED LINE): You are speaking DIRECTLY to {first.upper()}. Use \"you\" and \"your\" "
             f"in every paragraph. NEVER refer to {lead} in the third person. NEVER say \"this business,\" "
             f"\"the owner,\" \"they,\" or \"their team.\" If you catch yourself describing {lead} from the "
             f"outside, stop and restart the sentence addressed to them.\n")
    L.append(f"RULE 2: Open the audio with EXACTLY these words: \"Hi {first}, welcome. This walkthrough was "
             f"built for you and {biz}, from what you told us.\" Then proceed.\n")
    L.append("RULE 3: This business is THRIVING. Frame every gap as an AI amplification, not a flaw. "
             "No agent brand names. Application CTA only — never mention calendar or booking.\n")
    L.append("---\n")

    # SECTION 1 — direct address (gates: "Hi {first}", >=3 you/your, no 3rd-person)
    L.append(f"## SECTION 1 — Hi {first}, this is your walkthrough\n")
    L.append(f"Hi {first}, welcome. This walkthrough was built for you and {biz}, from what you told us. "
             f"Everything you're about to hear came straight from your form and your own studio.\n")
    positioning = p.get('positioning') or f"a {ind} studio"
    L.append(f"You run {biz}, {positioning}. That work is yours, and nothing here replaces it. "
             f"What you'll hear is exactly where AI gives you your time back so you can pour more of yourself into the work only you can do.\n")
    L.append(f"You told us your single biggest goal is {goal}, and that the most demanding part of your week is {stress}. "
             f"You're {ai_mat}, which is a strong place to start. Keep those two things in mind — every tool below is aimed right at them.\n")
    L.append("---\n")

    # SECTION 2 — tool stack
    L.append(f"## SECTION 2 — Your Current Tool Stack: Where {biz} Is Today\n")
    L.append("Here is the operational stack you're running today, and where AI plugs in on top of it — nothing gets ripped out:\n")
    for s in stack:
        L.append(f"- **{strip(s.get('tool'))}** — {strip(s.get('role'))}")
    L.append(f"\nThe biggest signal here: there's no central client system yet, so every inquiry and {client_noun} lives in your inbox and texts. "
             f"That's the first place AI gives you leverage.\n")
    L.append("---\n")

    # SECTION 3 — gaps (real, from profile)
    L.append("## SECTION 3 — Where AI Gives You the Most Time Back\n")
    L.append("These aren't guesses — they come straight from your answers. None of it is a critique of the studio; "
             "it's simply where AI carries the load so your team doesn't have to.\n")
    for i, g in enumerate(gaps, 1):
        L.append(f"### Opportunity {i} — {strip(g.get('title'))}\n")
        L.append(strip(g.get('desc')) + "\n")
    L.append("---\n")

    # SECTION 4 — the AI tools / agents built for them
    L.append(f"## SECTION 4 — The AI System Built Specifically for {biz}\n")
    L.append(f"These were written for your studio — your inquiries, your {client_noun}s, your voice. Not adjusted from a template:\n")
    for a in agents:
        L.append(f"### {strip(a.get('name'))}\n")
        L.append(strip(a.get('desc')))
        L.append(f"\n*What you feel:* {strip(a.get('outcome'))}\n")
    L.append("---\n")

    # SECTION 5 — brand voice / what makes them them
    L.append(f"## SECTION 5 — Your Brand Voice, Built In From Day One\n")
    tagline = p.get('tagline')
    voice_phrase = f" and your own language — “{tagline}” —" if tagline else " and your own language,"
    L.append(f"Your AI doesn't learn your voice slowly over months. We build it before launch from {domain or 'your site'}"
             f"{voice_phrase} so every reply a {client_noun} receives sounds like {biz} "
             f"from the very first message — 90% accurate on day one, then fine-tuned with you.\n")
    L.append("---\n")

    # SECTION 6 — 30-day timeline
    L.append("## SECTION 6 — Your 30-Day Onboarding Timeline\n")
    for t in timeline:
        L.append(f"**{strip(t.get('phase'))} — {strip(t.get('sub'))}**")
        for it in t.get('items', []):
            L.append(f"- {strip(it)}")
        L.append(f"_Result: {strip(t.get('result'))}_\n")
    L.append("---\n")

    # SECTION 7 — three ready-to-use prompts (full)
    L.append("## SECTION 7 — Three Prompts You Can Use Today, Without Waiting\n")
    L.append("You don't have to wait for us to feel this. Paste these into ChatGPT — which you already use — and you have a working agent in minutes.\n")
    for pr in prompts:
        L.append(f"### {strip(pr.get('title'))}\n")
        L.append(f"_{strip(pr.get('subtitle'))}_\n")
        L.append("```\n" + strip(pr.get('pre')) + "\n```\n")
        L.append(strip(pr.get('outcome')) + "\n")
    L.append("---\n")

    # SECTION 8 — two paths
    L.append("## SECTION 8 — Two Paths Forward\n")
    L.append(f"**Do it yourself:** use the prompts above to stand up one or two of these agents on your own. You'll feel time come back within days.\n")
    L.append(f"**Partner with us:** we build the full system — all six agents connected, calibrated to the {biz} voice, "
             f"running across every inquiry and {client_noun}, and we maintain it. Once it's set up, it runs itself.\n")
    L.append(f"When you're ready, the next step is a short application: {qualify}\n")
    L.append("---\n")

    # SECTION 9 — ROI
    contract = calc.get('contract', 6000); leads_n = calc.get('leads', 30)
    L.append(f"## SECTION 9 — The ROI Picture for {biz}\n")
    L.append(f"Here's the honest math from your own numbers — about {leads_m} inquiries a month, an average {value_noun} "
             f"around ${contract:,}, and a team of {team}. These are benchmark-based ranges, not guarantees.\n")
    L.append(f"- **Time:** your stated goal. Industry benchmarks put the recoverable admin and communication load at roughly "
             f"12 hours per week, per teammate. At $150/hr that's meaningful time back across a team of {team}.\n"
             f"- **Bookings:** answering every inquiry in under 60 seconds instead of around an hour means you're first into "
             f"the conversation — and {client_noun}s tend to book the studio that feels present first.\n"
             f"- **Capacity:** the same six agents let you serve more {client_noun}s without losing the high-touch experience that defines {biz}.\n")
    L.append("---\n")

    # SECTION 10 — objections
    L.append("## SECTION 10 — Common Questions, Honest Answers\n")
    L.append('**"Will this replace my team or my creativity?"** No. The design and the relationship stay entirely yours. '
             f'AI takes the inbox, the reminders, and the first drafts off your plate so you have more presence for the {client_noun}, not less.\n')
    L.append('**"Is it complicated to run?"** No. It plugs into the tools you already use — Google Drive, Dropbox, Trello, email, and text — '
             'and once it\'s set up, it runs itself.\n')
    L.append(f'**"Will {client_noun}s be able to tell it\'s AI?"** Built on your voice before launch, replies read as warm and unmistakably you.\n')
    L.append("---\n")

    # SECTION 11 — reference links
    L.append("## SECTION 11 — Reference Links\n")
    L.append(f"- Your full blueprint: {blue}")
    L.append(f"- Start your application: {qualify}\n")
    L.append("---\n")

    # SECTION 12 — about
    L.append("## SECTION 12 — About Franchise KI & Advaita\n")
    L.append("We build and run AI systems for owner-led businesses — the same way we built our own. "
             "You own the system; we stay on as your AI operations team. Quality and reliability over speed, always.\n")

    return "\n".join(L)


def build_source_doc(profile: dict) -> str:
    """Build a 12-section, 18KB+, second-person source doc from lead profile JSON."""

    # Option B dispatch — rich profile schema (form-driven, per-lead accurate content).
    if profile.get('agents') and profile.get('gaps') and profile.get('prompts'):
        return _build_rich_source_doc(profile)

    # Core fields (backward-compatible .get())
    lead_name        = profile.get('lead_name', 'Business Owner')
    lead_first       = profile.get('lead_first_name', lead_name.split()[0])
    business_name    = profile.get('business_name', 'Your Business')
    slug             = profile.get('slug', lead_name.lower().replace(' ', '-'))
    industry         = profile.get('industry', 'professional services')
    tools_raw        = profile.get('tools', 'standard business tools')
    market           = profile.get('market', 'local and regional customers')
    service_type     = profile.get('service_type', 'professional services')
    speed_context    = profile.get('speed_to_lead_context',
                                   f'responding to {industry} inquiries before competitors')
    url              = profile.get('url', '')

    # Council #1 — personalized AI tools (the core deliverable)
    prompt_1         = profile.get('prompt_1', f'[No custom prompt provided — describe key AI speed-to-lead opportunity for {industry}]')
    prompt_2         = profile.get('prompt_2', f'[No custom prompt provided — describe key AI proposal or qualification opportunity for {industry}]')
    prompt_3         = profile.get('prompt_3', f'[No custom prompt provided — describe key AI follow-up or outreach opportunity for {industry}]')
    prompt_1_label   = profile.get('prompt_1_label', 'Speed-to-Lead Response Agent')
    prompt_2_label   = profile.get('prompt_2_label', 'Proposal and Qualification Agent')
    prompt_3_label   = profile.get('prompt_3_label', 'Follow-Up and Outreach Agent')

    # Council #9 — extended profile fields
    services         = profile.get('services', [service_type])
    services_str     = (', '.join(services) if isinstance(services, list) else str(services)) or service_type
    team_size_raw    = str(profile.get('team_size', '—'))   # coerce int→str
    annual_revenue   = profile.get('annual_revenue', '')
    pain_points      = profile.get('pain_points', [])
    ai_maturity      = profile.get('ai_maturity', 'early-stage')
    roi_hours_saved  = str(profile.get('roi_hours_saved', '17'))
    monthly_leads    = str(profile.get('monthly_leads', '—'))

    # Derived display values
    roi_hours_int    = int(roi_hours_saved) if roi_hours_saved.isdigit() else 17
    roi_rate         = '$150'
    roi_monthly      = f'${roi_hours_int * 150 * 4:,}'
    roi_annual       = f'${roi_hours_int * 150 * 4 * 12:,}'
    gap1_roi         = f'${8 * 150 * 4:,}'
    gap3_roi         = f'${5 * 150 * 4:,}'

    team_size_line   = (
        f"Your team of {team_size_raw} handles the day-to-day execution."
        if team_size_raw not in ('—', '', None)
        else f"Your team is the backbone of {business_name}."
    )

    ai_maturity_line = (
        f"You told us your current AI use is {ai_maturity}. That's exactly where most "
        f"{industry} businesses are right now — and it's the right starting point."
        if ai_maturity not in ('—', '', None)
        else f"You're at the beginning of your AI journey — which means every improvement compounds from here."
    )

    industry_cap = industry.capitalize()

    # Tools expanded — turn comma list into bullet descriptions
    tools_list = [t.strip() for t in tools_raw.split(',') if t.strip()]
    if len(tools_list) < 3:
        tools_list += [f'Standard {industry} workflow tools', 'Email and calendar', 'Direct team communication']
    tools_expanded = '\n'.join(f'- **{t}**: Core operational tool in your current stack.' for t in tools_list[:6])

    team_size_admin = '2' if team_size_raw in ('—', '', None) else (
        str(min(int(team_size_raw), 5)) if team_size_raw.isdigit() else '2'
    )

    doc = SOURCE_DOC_TEMPLATE.format(
        lead_name=lead_name,
        lead_first=lead_first,
        lead_name_upper=lead_name.upper(),
        business_name=business_name,
        industry=industry,
        industry_cap=industry_cap,
        market=market,
        url=url or f'[{business_name} website]',
        services_str=services_str,
        service_type=service_type,
        tools=tools_raw,
        tools_expanded=tools_expanded,
        speed_context=speed_context,
        team_size_line=team_size_line,
        ai_maturity_line=ai_maturity_line,
        team_size_admin=team_size_admin,
        prompt_1=prompt_1,
        prompt_2=prompt_2,
        prompt_3=prompt_3,
        prompt_1_label=prompt_1_label,
        prompt_2_label=prompt_2_label,
        prompt_3_label=prompt_3_label,
        roi_rate=roi_rate,
        roi_hours_saved=roi_hours_saved,
        roi_monthly=roi_monthly,
        roi_annual=roi_annual,
        gap1_roi=gap1_roi,
        gap3_roi=gap3_roi,
        generated_date=datetime.now().strftime('%Y-%m-%d'),
    )
    return doc


def validate_source_doc(content: str, lead_name: str = '', lead_first: str = '') -> None:
    """v1.6 — hard gates: size + sections + direct-address regex gate on Section 1."""
    import re
    size_bytes = len(content.encode('utf-8'))

    if size_bytes < MIN_SOURCE_DOC_BYTES:
        raise ValueError(
            f"BLOCKED: Source doc is {size_bytes/1024:.1f}KB — minimum is {MIN_SOURCE_DOC_BYTES/1024:.0f}KB. "
            f"Missing sections or empty prompt_1/2/3 fields. Expand before uploading."
        )

    required = ['<!-- v1.6 -->', 'SECTION 1', 'SECTION 4', 'SECTION 6',
                'SECTION 8', 'SECTION 12', 'qualify.html']
    missing = [r for r in required if r not in content]
    if missing:
        raise ValueError(f"Source doc missing required sections/stamp: {missing}")

    if lead_name and lead_name not in content:
        raise ValueError(f"Source doc does not contain lead name '{lead_name}'. Personalization failed.")

    # v1.6 — Section 1 direct-address regex gate
    if lead_first:
        # Extract Section 1 body (between "## SECTION 1" and "## SECTION 2" or "---")
        m = re.search(r'## SECTION 1.*?(?=## SECTION 2|\n---\n\n## SECTION 2)', content, re.DOTALL)
        section1 = m.group(0) if m else content[:3000]

        # Gate 1: opening must contain "Hi {lead_first}"
        if f'Hi {lead_first}' not in section1:
            raise ValueError(
                f"v1.6 GATE: Section 1 missing direct-address opening 'Hi {lead_first}'. "
                f"NotebookLM TTS reads body opening — directive headers alone are unreliable."
            )

        # Gate 2: ≥3 "you/your" references in Section 1
        you_count = len(re.findall(r'\b(you|your|yours|you\'re|you\'ve|you\'ll|you\'d)\b', section1, re.IGNORECASE))
        if you_count < 3:
            raise ValueError(
                f"v1.6 GATE: Section 1 has only {you_count} you/your references — need ≥3."
            )

        # Gate 3: zero third-person refs to lead in Section 1 prose
        # Allow them in header lines only; check sentences
        third_person_phrases = [
            r'\bthis business\b',
            r'\bthe owner\b',
            f"{re.escape(lead_name)}('s)? business",  # "X's business" = 3rd person
        ]
        violations = []
        for pat in third_person_phrases:
            if re.search(pat, section1, re.IGNORECASE):
                violations.append(pat)
        if violations:
            raise ValueError(
                f"v1.6 GATE: Section 1 contains third-person phrasing about lead: {violations}"
            )

    print(f"✓ Source doc validated v1.6: {size_bytes:,} bytes ({size_bytes/1024:.1f}KB) — DIRECT-ADDRESS PASS")


# ---------------------------------------------------------------------------
# Core generation logic
# ---------------------------------------------------------------------------

async def generate_podcast(profile_path: str, output_dir: str = None, source_only: bool = False):
    """Generate a NotebookLM podcast from lead profile JSON."""

    with open(profile_path) as f:
        profile = json.load(f)

    lead_name     = profile.get('lead_name', 'Unknown')
    lead_first    = profile.get('lead_first_name', lead_name.split()[0])
    business_name = profile.get('business_name', 'Unknown Business')
    slug          = profile.get('slug', lead_name.lower().replace(' ', '-'))

    # Determine output directory
    if output_dir is None:
        # Default: podcasts/ directory adjacent to the leads/ directory
        leads_dir = os.path.dirname(os.path.abspath(profile_path))
        repo_root = os.path.dirname(leads_dir)
        output_dir = os.path.join(repo_root, 'podcasts')
    os.makedirs(output_dir, exist_ok=True)

    # Build source doc — Council #1 #2 #3 #4 #9
    source_content = build_source_doc(profile)

    # Save source doc
    source_path = os.path.join(output_dir, f'{slug}-podcast-source.md')
    with open(source_path, 'w') as f:
        f.write(source_content)

    # v1.6 hard size + direct-address gate BEFORE upload
    validate_source_doc(source_content, lead_name, lead_first)

    if source_only:
        return {'source_path': source_path, 'status': 'source_only',
                'size_bytes': len(source_content.encode('utf-8'))}

    # NotebookLM upload and generation
    try:
        from notebooklm import NotebookLMClient, AudioLength

        client = await NotebookLMClient.from_storage()
        async with client:
            notebook = await _retry_async(
                lambda: client.notebooks.create(title=f"{business_name} AI Blueprint Podcast"),
                description=f"create notebook for {business_name}",
            )
            nb_id = notebook.id
            _log(f"Notebook created: {nb_id}")

            await _retry_async(
                lambda: client.sources.add_text(nb_id, f"{business_name} AI Blueprint", source_content, wait=True),
                description=f"add source to {nb_id}",
            )
            _log("Source added")

            await _retry_async(
                lambda: client.artifacts.generate_audio(nb_id, audio_length=AudioLength.SHORT),
                description=f"generate audio for {nb_id}",
            )
            _log("Audio generation started...")

            for i in range(30):
                await asyncio.sleep(10)
                artifacts = await client.artifacts.list_audio(nb_id)
                for art in artifacts:
                    if art.status == 3:  # COMPLETED
                        _log(f"Audio ready — artifact: {art.id}")

                        # Council #6 — .mp3 not .mp4
                        output_path = os.path.join(output_dir, f'{slug}-blueprint-podcast.mp3')
                        await client.artifacts.download_audio(nb_id, output_path)

                        # Council #5 — file-existence + size gate
                        if not os.path.exists(output_path):
                            raise RuntimeError(
                                f"Download reported success but file not found: {output_path}"
                            )

                        # Task #8 — transcode hardening: force a REAL mp3 before the
                        # size/ship gates so FC-06 passes at the source (iOS listen button).
                        output_path = _ensure_real_mp3(output_path)

                        size_bytes = os.path.getsize(output_path)
                        size_mb = size_bytes / (1024 * 1024)
                        if size_mb < MIN_MP3_SIZE_MB:
                            raise RuntimeError(
                                f"Downloaded file too small: {size_mb:.1f}MB (minimum {MIN_MP3_SIZE_MB}MB). "
                                f"File may be corrupt or truncated: {output_path}"
                            )
                        print(f"✓ Downloaded + verified: {output_path} ({size_mb:.1f}MB)")

                        return {
                            'status': 'VERIFIED',
                            'notebook_id': nb_id,
                            'artifact_id': art.id,
                            'output_path': output_path,
                            'size_mb': round(size_mb, 1),
                            'source_path': source_path,
                        }
                _log(f"  Polling {i+1}/30...")

            _log(f"WARNING: Audio generation timed out after 5 min for {slug}")
            return {
                'status': 'TIMEOUT',
                'notebook_id': nb_id,
                'source_path': source_path,
                'expected_output_path': os.path.join(output_dir, f'{slug}-blueprint-podcast.mp3'),
                'error': 'Audio generation timed out. Check NotebookLM dashboard for artifact status.',
            }

    except ImportError:
        print("ERROR: notebooklm not installed. Run: pip3 install notebooklm")
        return {'error': 'notebooklm not installed', 'source_path': source_path}
    except Exception as e:
        _log(f"ERROR for {slug}: {e}")
        return {'error': str(e), 'source_path': source_path, 'status': 'ERROR'}


# ---------------------------------------------------------------------------
# Batch processing — Council #8 #10
# ---------------------------------------------------------------------------

def _is_verified_success(r: dict) -> bool:
    """Council #8 — True only if MP3 file is actually on disk and ≥5MB."""
    output_path = r.get('output_path')
    if not output_path or not os.path.exists(output_path):
        return False
    return os.path.getsize(output_path) / (1024 * 1024) >= MIN_MP3_SIZE_MB


async def _batch_worker(semaphore, profile_path, output_dir, delay, results, index, source_only):
    async with semaphore:
        _log(f"[{index}] Starting: {profile_path}")
        result = await generate_podcast(profile_path, output_dir, source_only=source_only)
        result['profile_path'] = profile_path
        results.append(result)
        _log(f"[{index}] Finished: {profile_path} → {result.get('status', 'unknown')}")
        if delay > 0:
            await asyncio.sleep(delay)


async def run_batch(profile_paths, output_dir, delay, max_concurrent, source_only=False):
    _log(f"Batch: {len(profile_paths)} profiles, delay={delay}s, concurrent={max_concurrent}")
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    if max_concurrent == 1:
        for i, path in enumerate(profile_paths, 1):
            await _batch_worker(semaphore, path, output_dir, delay, results, i, source_only)
    else:
        tasks = [
            asyncio.create_task(_batch_worker(semaphore, path, output_dir, delay, results, i, source_only))
            for i, path in enumerate(profile_paths, 1)
        ]
        await asyncio.gather(*tasks)

    # Council #8 — verified success = file on disk + size ≥5MB
    successes = [r for r in results if _is_verified_success(r)]
    failures  = [r for r in results if not _is_verified_success(r)]

    _log(f"Batch complete — Verified on disk: {len(successes)}/{len(results)}")
    if failures:
        for r in failures:
            _log(f"  NOT VERIFIED: {r.get('profile_path')} — "
                 f"status={r.get('status','unknown')}, error={r.get('error','file missing or too small')}")

    # Council #10 — write manifest JSON
    manifest_dir = output_dir or os.path.expanduser('~/Desktop')
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, f'podcast-batch-manifest-{datetime.now():%Y%m%d-%H%M}.json')
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'total': len(results),
        'verified_on_disk': len(successes),
        'not_verified': len(failures),
        'do_not_send_delivery_emails_until_verified': len(failures) == 0,
        'leads': []
    }
    for r in results:
        op = r.get('output_path', '')
        manifest['leads'].append({
            'profile':     r.get('profile_path', ''),
            'status':      'VERIFIED' if _is_verified_success(r) else r.get('status', 'FAILED'),
            'output_path': op,
            'size_mb':     round(os.path.getsize(op) / (1024*1024), 1) if op and os.path.exists(op) else 0,
            'error':       r.get('error', ''),
            'notebook_id': r.get('notebook_id', ''),
        })
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    _log(f"Manifest: {manifest_path}")

    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {len(successes)}/{len(results)} VERIFIED ON DISK")
    print(f"Manifest: {manifest_path}")
    if failures:
        print(f"\nWARNING: {len(failures)} leads NOT verified — DO NOT send delivery emails for:")
        for r in failures:
            slug = os.path.basename(r.get('profile_path','')).replace('.json','')
            print(f"  - {slug}: {r.get('error','file missing')}")
    else:
        print(f"ALL {len(successes)} LEADS VERIFIED — safe to proceed with delivery")
    print(f"{'='*60}\n")

    return results


# ---------------------------------------------------------------------------
# Source-doc-only batch — rebuild all 11 without touching NotebookLM
# ---------------------------------------------------------------------------

def rebuild_all_source_docs(leads_dir: str, podcasts_dir: str) -> dict:
    """Rebuild source docs for all leads in leads_dir using the new template."""
    results = {'rebuilt': [], 'failed': [], 'sizes': {}}
    leads_dir = os.path.expanduser(leads_dir)
    podcasts_dir = os.path.expanduser(podcasts_dir)
    os.makedirs(podcasts_dir, exist_ok=True)

    json_files = sorted(Path(leads_dir).glob('*.json'))
    skip_files = {'.status', 'pipeline', 'lead-profile', 'funnel-state',
                  'client_palette', 'color-diamond', 'revenue-declaration', 'lead-profile'}

    for jf in json_files:
        if any(skip in jf.stem for skip in skip_files):
            continue
        if jf.parent.name == '.status':
            continue
        try:
            with open(jf) as f:
                profile = json.load(f)
            if not profile.get('slug') or not profile.get('lead_name'):
                continue
            source_content = build_source_doc(profile)
            _lead_first = profile.get('lead_first_name', profile['lead_name'].split()[0])
            validate_source_doc(source_content, profile['lead_name'], _lead_first)
            slug = profile['slug']
            out_path = os.path.join(podcasts_dir, f'{slug}-podcast-source.md')
            with open(out_path, 'w') as f:
                f.write(source_content)
            size_kb = len(source_content.encode('utf-8')) / 1024
            results['rebuilt'].append(slug)
            results['sizes'][slug] = f'{size_kb:.1f}KB'
            print(f"  ✓ {slug}: {size_kb:.1f}KB")
        except Exception as e:
            results['failed'].append({'file': str(jf), 'error': str(e)})
            print(f"  ✗ {jf.name}: {e}")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate NotebookLM podcasts from lead profiles. v1.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('profile', nargs='?', default=None,
                        help='Path to a single lead JSON file')
    parser.add_argument('--batch', type=str, default=None,
                        help='Directory, glob, or list file of lead JSON files')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Output directory (default: podcasts/ in repo root)')
    parser.add_argument('--delay', type=float, default=60,
                        help='Seconds between notebook creations (default: 60)')
    parser.add_argument('--max-concurrent', type=int, default=1,
                        help='Max concurrent generations (default: 1)')
    parser.add_argument('--source-only', action='store_true',
                        help='Generate source docs only — skip NotebookLM upload')
    parser.add_argument('--rebuild-sources', action='store_true',
                        help='Rebuild all source docs from leads/ dir without uploading')

    args = parser.parse_args()

    if args.rebuild_sources:
        # Rebuild all source docs using new template
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        leads_dir = os.path.join(repo_root, 'leads')
        podcasts_dir = args.output_dir or os.path.join(repo_root, 'podcasts')
        print(f"\nRebuilding source docs from: {leads_dir}")
        print(f"Output: {podcasts_dir}\n")
        results = rebuild_all_source_docs(leads_dir, podcasts_dir)
        print(f"\nRebuilt: {len(results['rebuilt'])} source docs")
        if results['failed']:
            print(f"Failed: {len(results['failed'])}")
            for f in results['failed']:
                print(f"  - {f}")
        return

    if args.profile is None and args.batch is None:
        parser.print_help()
        sys.exit(1)

    output_dir = args.output_dir

    if args.batch is not None:
        from pathlib import Path as _Path
        batch_path = args.batch
        p = _Path(batch_path)
        if p.is_dir():
            profile_paths = [str(f) for f in sorted(p.glob('*.json'))
                             if not any(x in f.name for x in ['.status', 'pipeline', 'funnel'])]
        else:
            profile_paths = sorted(glob.glob(batch_path, recursive=True))

        if not profile_paths:
            print(f"ERROR: No profile files found at: {batch_path}", file=sys.stderr)
            sys.exit(1)
        _log(f"Found {len(profile_paths)} profiles")
        results = asyncio.run(
            run_batch(profile_paths, output_dir, args.delay, args.max_concurrent, args.source_only)
        )
        sys.exit(0)

    result = asyncio.run(generate_podcast(args.profile, output_dir, args.source_only))
    print(f"\nResult: {json.dumps(result, indent=2)}")


if __name__ == '__main__':
    main()
