# Advaita creative + project expansion seeds — "PRE-INBOUND" segment
Filed 2026-07-28 · seat Madison CC (claude-code, mac_cli) · origin lead: bri-fresh (Bri / Fresh)
Marker: ADVAITA-PRE-INBOUND-SEGMENT-SEEDS-20260728

## Why this is net-new, not a rehash
Every Advaita angle currently in rotation assumes the prospect HAS lead volume — speed-to-lead
against N leads/month, reactivation of a stale CRM, recovering a 60-minute response gap. Bri broke
that assumption: **zero inbound leads, no CRM, no PM tool, automation maturity "none."** The whole
existing pitch library has nothing to say to her, which is why her page had to make no volume claim
anywhere. That is a segment gap, not a weak lead. Agencies and service firms under $250k with 2-4
people are almost all in this state, and they are the cheapest possible Blueprint prospects to
reach because nobody is selling them anything except tools they are not ready for.

Positioning line for the whole segment: **build the operating system before the volume arrives —
retrofitting under pressure is what costs money.**

---

### Seed 1 — "The Empty CRM Problem"
- **Hook:** "You don't need a CRM. You need the thing that fills it — and you need it before the leads show up."
- **Format:** 60-90s founder-to-camera vertical video (Bennett), text-on-screen cold open.
- **CTA:** Complete the qualifier — "see what your first three AI employees would be."
- **Brand:** Advaita
- **Proof angle:** FDD-safe and evidence-cited: name only the structural fact — a request that arrives in a text thread has to be reconstructed by hand later. No lift claims, no percentages.
- **next_artifact:** shot list + on-screen text script
- **owner_agent:** Madison CC (script) → Bennett (record)
- **success_metric:** qualifier completions attributed to the pre-inbound creative set
- **revenue_link:** $5K build + $2K/mo lane

### Seed 2 — "Pre-Inbound Checklist" lead magnet
- **Hook:** "Six systems to have running before your first inbound lead — the four-week version."
- **Format:** One-page PDF / hub landing page; the six AI employees reframed as a readiness checklist rather than a product list.
- **CTA:** Qualifier.
- **Brand:** Advaita
- **Proof angle:** Pure structural checklist. Nothing numeric, so nothing to substantiate.
- **next_artifact:** `hub/pre-inbound-checklist.html` built off the canonical page base
- **owner_agent:** Madison CC
- **success_metric:** opt-ins → qualifier completion rate
- **revenue_link:** top-of-funnel feeder into the Blueprint lane

### Seed 3 — "You Are the System" cold-email sequence (3 touches)
- **Hook (t1):** "Right now the system holding your intake is you."
- **Hook (t2):** "The 15-minute reply is a promise a person is keeping, not a system."
- **Hook (t3):** "What happens the first week volume actually arrives?"
- **Format:** 3-touch Instantly sequence, form-first (no call gate — per standing rule).
- **CTA:** Complete the qualifier; no calendar link.
- **Brand:** Advaita
- **Proof angle:** Every line is a restatement of what the prospect self-reports on the form. Zero invented lift.
- **next_artifact:** sequence copy in the Advaita-ops campaign (ffafc612)
- **owner_agent:** Madison CC → Madison approves send
- **success_metric:** reply rate + qualifier completions
- **revenue_link:** direct pipeline

### Seed 4 — "Automation maturity: none" as a qualifier segment
- **Hook:** Internal, not creative — treat `automation_maturity=none` + `monthly_leads=0` as its own scored branch instead of a thin-submission penalty.
- **Format:** Qualifier logic + blueprint copy variant that leads with readiness rather than recovery.
- **CTA:** n/a (infrastructure)
- **Brand:** Advaita / Blueprint
- **Proof angle:** n/a
- **next_artifact:** copy variant in the page base + a `pre_inbound` flag on the lead schema
- **owner_agent:** Madison CC
- **success_metric:** thin submissions that currently produce empty page sections instead producing a full readiness narrative
- **revenue_link:** stops the cheapest segment from generating the weakest pages

### Seed 5 — "Before / After Week One" carousel
- **Hook:** "Week one with three people and no systems. Week one with three people and six AI employees."
- **Format:** 6-slide LinkedIn carousel, one slide per AI employee, each a single before/after line.
- **CTA:** Qualifier.
- **Brand:** Advaita
- **Proof angle:** Outcome-shaped, not numeric — "the next step lives somewhere everyone can see it" rather than any hours-saved figure.
- **next_artifact:** slide copy + design brief
- **owner_agent:** Madison CC → Christelle (LinkedIn posting, DM her directly)
- **success_metric:** carousel → profile → qualifier
- **revenue_link:** organic feeder, zero ad spend

### Seed 6 — "ChatGPT is not the system" (objection-handler short)
- **Hook:** "You already use ChatGPT. That's the reason this works — and the reason it isn't enough yet."
- **Format:** 45s short + a reusable reply block for comments/DMs.
- **CTA:** Qualifier.
- **Brand:** Advaita
- **Proof angle:** Distinguishes a tool you operate from a system that runs without you. No product claims.
- **next_artifact:** script + comment-reply ladder
- **owner_agent:** Madison CC
- **success_metric:** reply-ladder engagements → qualifier
- **revenue_link:** objection removal on the most common blocker in this segment

---

## Project expansion (durable, this session)
1. `build-podcast-source.py` — schema-drift permanent fix (sections 2/4/12 populated from `quiz.*`,
   empty-section guard, 9-12 min length, mandatory closing, non-spoken funnel token).
   Marker `BLUEPRINT-PODCAST-SOURCE-SCHEMA-DRIFT-20260728`.
2. Seed 4 above is the standing fix for thin submissions — it converts the segment's weakness into
   its own copy branch.
3. NotebookLM CLI misdiagnosis worth carrying: an auth expiry **mid-poll** is reported as
   "artifact was removed by the server… daily quota/rate limit exceeded." The artifact was alive the
   whole time. Acting on that message would mean a needless regeneration (real quota burn) or a
   false "we're rate-limited" escalation. Always re-probe auth and re-list before believing it.
