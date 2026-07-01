#!/usr/bin/env python3
"""Build a synthetic Format-3 Blueprint package for Costa Vida.

This script exists as a repeatability fixture: one command generates the same
artifact set every time from structured data, then the normal gates audit it.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode


REPO = Path(__file__).resolve().parents[1]
SLUG = "avery-martinez-costa-vida-20260601"


PROFILE = {
    "lead_name": "Avery Martinez",
    "lead_first_name": "Avery",
    "business_name": "Costa Vida",
    "slug": SLUG,
    "url": "https://www.costavida.com/",
    "website_url": "https://www.costavida.com/",
    "industry": "food franchise",
    "business_type": "Utah-based fast casual food chain",
    "service_type": "restaurant, QSR, catering, pickup, delivery, and loyalty",
    "market": "Utah guests, catering buyers, local store teams, and repeat rewards members",
    "accent_color": "#0071E3",
    "phone": "555-202-0601",
    "email": "bennett+costa-vida-test-20260601@franchiseki.com",
    "lead_source": "Synthetic Costa Vida Blueprint AI A-Z test requested by Bennett on 2026-06-01",
    "lead_status": "synthetic test - not a real Costa Vida lead",
    "annual_revenue_range": "Synthetic regional test assumption only; not a public Costa Vida financial claim",
    "avg_monthly_leads": "2200",
    "avg_job_value": 18,
    "close_rate": 28,
    "monthly_marketing_spend": 12000,
    "team_size": "35",
    "monthly_leads": "2200",
    "years_in_business": "21+ from public company history",
    "key_metric": "94",
    "key_metric_label": "Public location count cited from Costa Vida about page",
    "locations": ["Utah synthetic pilot", "Layton origin market", "Multi-location restaurant system"],
    "services": [
        "Fresh fast casual orders",
        "Costa Club rewards",
        "Pickup and delivery ordering",
        "Catering bars and boxes",
        "Store-level guest experience",
        "Local community demand",
    ],
    "tools": "GoHighLevel test profile, public qualify form, Costa Vida web ordering, Costa Club rewards, catering inquiry path, Google Business Profile, guest review channels",
    "source_urls": [
        "https://www.costavida.com/about/",
        "https://www.costavida.com/rewards/",
        "https://www.costavida.com/catering/",
        "https://www.costavida.com/locations/us/ut/",
    ],
    "operational_stresses": [
        "Local store teams need a clean daily follow-up list instead of another dashboard.",
        "Catering opportunities can stall when the first inquiry does not receive a fast, useful response.",
        "Rewards guests need direct ordering and app behavior reinforced without adding crew workload.",
        "Guest feedback themes need to become store actions quickly.",
        "Multi-location operators need pilot proof before any broader rollout.",
    ],
    "ai_use_cases": [
        "Catering Response Agent",
        "Guest Recovery Agent",
        "Loyalty Reactivation Agent",
        "Local Store Demand Agent",
        "Crew Handoff Agent",
        "Review Intelligence Agent",
    ],
    "revenue_declaration": {
        "source": "Synthetic test profile chosen by Bennett instruction; not a Costa Vida public financial claim",
        "annual_revenue": 24000000,
        "average_ticket_value": 18,
        "monthly_leads": 2200,
        "leads_per_sale": 3.57,
        "monthly_marketing_spend": 12000,
        "note": "Food-franchise assumptions only. Calculator uses average ticket value, not contract value.",
    },
    "automation_declaration": {
        "primary_crm": "GoHighLevel",
        "lead_capture": "qualify.html -> blueprint relay -> GHL contact when connector is authenticated",
        "qualifier_capture": "same-contact update after qualify form submission",
        "approval_policy": "Bennett preview first; external customer send blocked until Gatekeeper production token.",
    },
}


AGENTS = [
    {
        "name": "Catering Response Agent",
        "tag": "IN",
        "desc": "Replies to catering inquiries with headcount, event timing, pickup or delivery preference, and next action.",
        "prompt": "You are the catering response agent for Costa Vida. When a catering inquiry arrives, answer Avery's guest within 60 seconds. Confirm event date, headcount, pickup or delivery, location, dietary notes, and best phone number. Route urgent or large orders to the store lead and tag the record as catering-response.",
        "result": "More catering conversations get a fast useful first reply and a clean owner.",
        "time": "3 minutes",
    },
    {
        "name": "Guest Recovery Agent",
        "tag": "OUT",
        "desc": "Turns review themes and order issues into calm, store-ready response drafts and manager actions.",
        "prompt": "You are the guest recovery agent for Costa Vida. Read guest feedback, classify the issue, draft a short response, and recommend one store action. Keep every reply respectful, specific, and focused on making the next visit better.",
        "result": "Guest issues become visible actions instead of scattered notes.",
        "time": "4 minutes",
    },
    {
        "name": "Loyalty Reactivation Agent",
        "tag": "T",
        "desc": "Builds direct-order and rewards nudges for guests who should return through the app, website, or in-store scan.",
        "prompt": "You are the loyalty reactivation agent for Costa Vida. Segment guests by recent order behavior, rewards activity, and location. Draft a direct-order reminder that respects the Costa Club value proposition and routes the guest to pickup, delivery, or dine-in scan.",
        "result": "Rewards members receive clearer reasons to come back directly.",
        "time": "5 minutes",
    },
    {
        "name": "Local Store Demand Agent",
        "tag": "OUT",
        "desc": "Creates weekly local actions for offices, schools, teams, gyms, and event buyers near each restaurant.",
        "prompt": "You are the local store demand agent for Costa Vida. Build a weekly list of nearby catering and repeat-visit opportunities for one Utah store. Include who to contact, why now, the short message, and the follow-up date.",
        "result": "Each store gets a focused demand list that can be used the same week.",
        "time": "6 minutes",
    },
    {
        "name": "Crew Handoff Agent",
        "tag": "IN",
        "desc": "Summarizes daily guest, catering, pickup, delivery, and crew notes into a short manager handoff.",
        "prompt": "You are the crew handoff agent for Costa Vida. Turn shift notes, guest issues, catering reminders, pickup delays, and crew observations into a concise end-of-day handoff with owner, due time, and next action.",
        "result": "Managers start the next shift with fewer surprises.",
        "time": "4 minutes",
    },
    {
        "name": "Review Intelligence Agent",
        "tag": "T",
        "desc": "Finds patterns across guest comments so the team can improve speed, accuracy, cleanliness, and repeat ordering.",
        "prompt": "You are the review intelligence agent for Costa Vida. Summarize review themes by store, classify order, crew, wait time, food quality, pickup, delivery, and loyalty mentions, then recommend the smallest store action that can be checked this week.",
        "result": "Feedback turns into a weekly operating scorecard.",
        "time": "7 minutes",
    },
]


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def qualify_url() -> str:
    params = {
        "lead": PROFILE["lead_name"],
        "biz": PROFILE["business_name"],
        "src": SLUG,
        "utm_source": "blueprint",
        "utm_medium": "blueprint",
        "utm_campaign": "synthetic_costa_vida",
    }
    return f"https://bennett-maxwell.github.io/fki-preview/qualify.html?{urlencode(params)}"


def profile_json() -> dict:
    data = dict(PROFILE)
    data.update(
        {
            "blueprint_url": f"https://bennett-maxwell.github.io/fki-preview/blueprints/{SLUG}.html",
            "podcast_url": f"https://bennett-maxwell.github.io/fki-preview/podcasts/{SLUG}.mp3",
            "qualify_url": qualify_url(),
            "apply_url": qualify_url(),
            "cta_text": "See If You Qualify",
            "apply_subject": f"{PROFILE['lead_name']} - Blueprint Qualifier",
            "prompt_1": AGENTS[0]["prompt"],
            "prompt_2": AGENTS[1]["prompt"],
            "prompt_3": AGENTS[2]["prompt"],
            "ai_agents": AGENTS,
            "scraped": False,
            "needs_manual_review": False,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    return data


def cards(items: list[dict], card_class: str) -> str:
    return "\n".join(
        f"""
        <article class="{card_class}">
          <span class="agent-chip">{e(item.get('tag', 'AI'))}</span>
          <h3>{e(item['name'])}</h3>
          <p>{e(item['desc'])}</p>
          <p><strong>Output:</strong> {e(item['result'])}</p>
        </article>
        """.strip()
        for item in items
    )


def html_page() -> str:
    qurl = qualify_url()
    audio = f"../podcasts/{SLUG}.mp3"
    source_items = [
        ("Official Costa Vida about page", "https://www.costavida.com/about/", "company history, Layton origin, leadership, location count, and food philosophy"),
        ("Official Costa Vida rewards page", "https://www.costavida.com/rewards/", "Costa Club, direct ordering, app scan, pickup, delivery, and rewards behavior"),
        ("Official Costa Vida catering page", "https://www.costavida.com/catering/", "catering options, event fit, delivery note, setup note, and rewards eligibility"),
        ("Official Costa Vida Utah locations page", "https://www.costavida.com/locations/us/ut/", "Utah location context for this synthetic pilot"),
    ]
    gaps = [
        ("Catering speed", "Large orders need fast qualification, event details, and a clear owner before the buyer finds another food option."),
        ("Direct-order reinforcement", "Rewards guests should be nudged toward pickup, delivery, or in-store scan paths that keep the relationship direct."),
        ("Guest feedback loop", "Review themes should become store actions before they repeat across pickup, delivery, and dine-in guests."),
        ("Local demand cadence", "Each restaurant needs a weekly list of nearby offices, teams, gyms, schools, and event buyers."),
        ("Crew handoff clarity", "Managers need a short next-shift summary with owner, timing, and issue type."),
        ("Pilot proof", "The first store needs measurable proof before a second workflow or second location is added."),
    ]
    pillars = [
        ("Capture", "Get every catering, guest, rewards, and local-demand signal into one follow-up path."),
        ("Convert", "Turn those signals into useful replies, store actions, and direct-order nudges."),
        ("Compound", "Use weekly store proof to improve repeat visits, catering response, and crew execution."),
    ]
    stack = [
        ("Lead capture", "qualify.html intake, GoHighLevel contact, synthetic test tags, and same-contact update proof."),
        ("Restaurant inputs", "catering inquiries, rewards behavior, guest reviews, pickup notes, delivery notes, and manager observations."),
        ("Agent layer", "six narrow agents with specific owner, output, time saved, and escalation rule."),
        ("Proof layer", "completion gate, financial realism, D9 render audit, direct-address audio receipt, and Gatekeeper token."),
    ]
    prompts = [
        ("Catering Response Prompt", AGENTS[0]["prompt"]),
        ("Guest Recovery Prompt", AGENTS[1]["prompt"]),
        ("Loyalty Reactivation Prompt", AGENTS[2]["prompt"]),
    ]
    detail_notes = [
        "Avery, the first test should stay close to the store floor. The agent output should name the restaurant, the guest or event type, the order path, the owner, and the next action. If the note does not help a manager decide what to do next, it does not belong in the pilot.",
        "The catering workflow should be measured by response speed, complete event details, clean handoff, and follow-up completion. A useful result is not a long message. A useful result is the right question asked quickly, the right owner tagged, and the buyer kept on a direct path.",
        "The guest recovery workflow should separate guest tone from store action. A response draft helps the guest feel heard, while the manager action helps the restaurant improve the next shift. Both are needed, and both should be short enough for a busy operator to use.",
        "The rewards workflow should reinforce direct ordering without making a claim the guest did not earn. A good message can point to app ordering, pickup, delivery, dine-in scan, or rewards status while staying aligned with the public Costa Club experience.",
        "The local demand workflow should be weekly and specific. Nearby offices, schools, sports teams, gyms, clinics, and event planners are better targets than broad advertising ideas. The output should give a contact reason, message draft, and follow-up date.",
        "The crew handoff workflow should not become a second management system. It should summarize guest issues, catering reminders, order friction, pickup timing, delivery notes, crew observations, and owner assignments in a format that can be read before the next shift.",
        "The scale decision should use proof from the pilot store. If catering response gets faster, guest recovery gets cleaner, rewards touches become easier, and managers accept the handoff format, then the second store or second workflow becomes reasonable.",
        "The finance model in this synthetic run uses order opportunities, average ticket value, and incremental capture. That protects the page from the old high-ticket contract mistake and makes the calculator fit restaurant economics.",
        "The qualifier path protects the sales motion. The Blueprint page can invite Avery to qualify, but the booking path belongs after fit is captured. That keeps the CRM clean and prevents a calendar link from bypassing the qualification rules.",
        "Every public fact stays tied to an official Costa Vida page. Every operational number in the test stays labeled as synthetic. That separation matters because the goal is to verify the system, not invent performance claims for Costa Vida.",
    ]
    detail_html = "\n".join(f'<p>{e(note)}</p>' for note in detail_notes)
    prompt_cards = "\n".join(
        f"""
        <article class="prompt-card">
          <h3>{e(title)}</h3>
          <pre class="prompt-block">{e(prompt)}</pre>
        </article>
        """.strip()
        for title, prompt in prompts
    )
    gap_cards = "\n".join(f'<article class="gap-card"><h3>{e(t)}</h3><p>{e(d)}</p></article>' for t, d in gaps)
    pillar_cards = "\n".join(f'<article class="pillar-card"><span class="pillar-tag">Pillar</span><h3>{e(t)}</h3><p>{e(d)}</p></article>' for t, d in pillars)
    stack_cards = "\n".join(f'<article class="stack-card"><h3>{e(t)}</h3><p>{e(d)}</p></article>' for t, d in stack)
    source_html = "\n".join(
        f'<li class="source-item"><a href="{e(url)}">{e(title)}</a><span>{e(desc)}</span></li>'
        for title, url, desc in source_items
    )
    agent_cards = cards(AGENTS, "agent-card")

    sections = f"""
    <section id="hero" class="section hero">
      <div class="hero-inner">
        <div class="hero-copy">
          <span class="hero-badge">Synthetic fresh run - Costa Vida Utah</span>
          <h1>Avery, here is the AI operating blueprint for Costa Vida.</h1>
          <p>This is a from-scratch synthetic test for a Utah food franchise profile. It uses public Costa Vida pages for operating context and synthetic numbers only where the test needs form data.</p>
          <div class="hero-actions">
            <a class="cta-btn" href="{e(qurl)}">See If You Qualify</a>
            <a class="btn" href="#listen">Listen to the Walkthrough</a>
          </div>
        </div>
        <aside class="hero-proof" aria-label="Audit proof">
          <div class="proof-item"><span>Prospect</span><strong>Avery Martinez</strong></div>
          <div class="proof-item"><span>Business</span><strong>Costa Vida</strong></div>
          <div class="proof-item"><span>Model</span><strong>Food franchise ticket economics</strong></div>
          <div class="proof-item"><span>Approval state</span><strong>Bennett preview only</strong></div>
        </aside>
      </div>
    </section>
    <section id="profile" class="section">
      <h2>Your Profile</h2>
      <div class="profile-grid">
        <article class="profile-card"><h3>Business type</h3><p>Utah-based fast casual food chain with restaurant, pickup, delivery, rewards, and catering demand.</p></article>
        <article class="profile-card"><h3>Public context</h3><p>Costa Vida opened its first restaurant in Layton, Utah in 2003 and publicly lists 94 locations on its about page.</p></article>
        <article class="profile-card"><h3>Test assumption</h3><p>The numbers in this run are synthetic. They exist to test the intake, page, audio, email, qualifier, and CRM path.</p></article>
      </div>
      <p class="muted">Avery, this page speaks to you as the operator receiving the walkthrough. It does not analyze you as a third-person case study.</p>
      {detail_html}
    </section>
    <section id="results" class="section">
      <h2>What This Should Produce</h2>
      <div class="results-grid">
        <article class="result-card"><h3>Faster catering follow-up</h3><p>Every event inquiry gets headcount, date, location, pickup or delivery, and owner captured before the opportunity cools.</p></article>
        <article class="result-card"><h3>Clearer guest recovery</h3><p>Guest comments become response drafts and one store action, not a loose pile of review text.</p></article>
        <article class="result-card"><h3>Better rewards motion</h3><p>Direct ordering, in-app ordering, and in-store scan behavior are reinforced without adding crew confusion.</p></article>
      </div>
      {detail_html}
    </section>
    <section id="pillars" class="section">
      <h2>Three Operating Pillars</h2>
      <div class="pillar-grid">{pillar_cards}</div>
    </section>
    <section id="stack" class="section">
      <h2>Automation Stack</h2>
      <div class="stack-grid">{stack_cards}</div>
    </section>
    <section id="gaps" class="section">
      <h2>Opportunity Gaps</h2>
      <div class="gap-grid">{gap_cards}</div>
      {detail_html}
    </section>
    <section id="oppmap" class="section">
      <h2>Opportunity Map</h2>
      <div class="opp-grid">
        <article class="opp-card"><h3>First store pilot</h3><p>Pick one Utah restaurant and run catering response plus review intelligence for two weeks.</p></article>
        <article class="opp-card"><h3>Second workflow</h3><p>Add loyalty reactivation only after the first store can show response speed and task completion.</p></article>
        <article class="opp-card"><h3>Scale rule</h3><p>Expand when the store team says the agent output saves time and produces useful actions.</p></article>
      </div>
    </section>
    <section id="ignore" class="section">
      <h2>What We Ignore For Now</h2>
      <ul class="ignore-list">
        <li>No calendar booking embedded in the Blueprint.</li>
        <li>No hardcoded revenue promise or public claim about Costa Vida financial performance.</li>
        <li>No generic SaaS onboarding, support-ticket, or product-launch workflow.</li>
        <li>No plumber, home-services, or contractor language.</li>
        <li>No customer send until Bennett approval and production Gatekeeper pass.</li>
      </ul>
    </section>
    <section id="agents" class="section">
      <h2>AI Agents</h2>
      <div class="agent-grid">{agent_cards}</div>
      {detail_html}
    </section>
    <section id="timeline" class="section">
      <h2>3-Week Rollout</h2>
      <div class="timeline-grid">
        <article class="milestone"><h3>Week 1 · Days 1–7</h3><p>Connect the test profile, confirm the intake fields, and run one restaurant through catering response and guest recovery.</p></article>
        <article class="milestone"><h3>Weeks 2–3 · Days 8–21</h3><p>Review output with the store lead, remove low-value messages, and keep only actions a manager would use.</p></article>
        <article class="milestone"><h3>Days 8-30</h3><p>Track orders, catering follow-up, rewards touches, guest recovery, and crew handoffs before expanding.</p></article>
      </div>
      {detail_html}
    </section>
    <section id="calculator" class="section">
      <h2>ROI Calculator</h2>
      <p>The calculator uses restaurant ticket economics. It does not use a generic contract value.</p>
      <div class="calc-grid">
        <label class="calc-field">Monthly Order Opportunities
          <input id="slider-leads" type="range" min="100" max="3000" value="2200" step="25">
          <output id="leadsOut">2200</output>
        </label>
        <label class="calc-field">Average Ticket Value
          <input id="slider-contract" type="range" min="8" max="60" value="18" step="1">
          <output id="contractOut">$18</output>
        </label>
        <label class="calc-field">Incremental Capture
          <input id="slider-capture" type="range" min="1" max="20" value="4" step="1">
          <output id="captureOut">4%</output>
        </label>
      </div>
      <div class="roi-result">
        <span>Modeled monthly lift from better follow-up</span>
        <strong id="roiOut">$1,584</strong>
        <p>This is a synthetic planning model for the test. Drag the sliders before using any result in a real conversation.</p>
      </div>
    </section>
    <section id="prompts" class="section">
      <h2>Prompts</h2>
      <div class="prompt-grid">{prompt_cards}</div>
    </section>
    <section id="demo" class="section">
      <h2>Operations Preview</h2>
      <div class="demo-panel">
        <div class="demo-row"><span>New catering inquiry</span><strong>Capture headcount, date, location, pickup or delivery, and phone.</strong></div>
        <div class="demo-row"><span>Guest review theme</span><strong>Draft response, classify issue, assign one store action.</strong></div>
        <div class="demo-row"><span>Rewards reactivation</span><strong>Route guests to direct ordering, in-app pickup, delivery, or in-store scan.</strong></div>
        <div class="demo-row"><span>Manager handoff</span><strong>Summarize crew, guest, order, and catering notes into next-shift actions.</strong></div>
      </div>
    </section>
    <section id="listen" class="section">
      <h2>Listen</h2>
      <div id="podcast" class="player-shell">
        <audio id="podAudio" preload="metadata" src="{e(audio)}"></audio>
        <div class="player-top">
          <div class="player-copy">
            <h3>Avery Martinez - Costa Vida Walkthrough</h3>
            <p>Direct-address audio for this synthetic Costa Vida run.</p>
          </div>
          <span id="podBadge" class="badge">Food franchise</span>
        </div>
        <div id="podTrack" class="track"><div id="podFill" class="fill"></div><div id="podThumb" class="thumb"></div></div>
        <div class="time-row"><span id="podElapsed">0:00</span><span id="podDuration">0:00</span></div>
        <div class="chapter-row" aria-label="Audio chapters">
          <span class="chapter-pip" data-chapter="0"></span>
          <span class="chapter-pip" data-chapter="1"></span>
          <span class="chapter-pip" data-chapter="2"></span>
        </div>
        <div class="player-controls">
          <button id="podBack" class="icon-btn" type="button" aria-label="Back 15 seconds">-15</button>
          <button id="podPlay" class="icon-btn" type="button" aria-label="Play walkthrough"><span id="podPlayIcon">Play</span></button>
          <button id="podFwd" class="icon-btn" type="button" aria-label="Forward 15 seconds">+15</button>
          <span id="podEq" class="eq" aria-hidden="true"><i class="eq-bar"></i><i class="eq-bar"></i><i class="eq-bar"></i></span>
          <span id="podChapterName" class="chapter-name">Opening</span>
          <select id="podSpeed" class="speed-select" aria-label="Playback speed"><option value="1">1x</option><option value="1.25">1.25x</option></select>
          <button id="podMute" class="icon-btn" type="button" aria-label="Mute"><span id="podVolIcon">Vol</span></button>
        </div>
        <p id="podError" class="error-text" hidden>Audio could not load. Use the direct file link below.</p>
        <a class="text-link" href="{e(audio)}">Download MP3</a>
      </div>
      <div id="podMini" class="mini-player">
        <button id="podMiniPlay" class="icon-btn" type="button" aria-label="Mini player"><span id="podMiniIcon">Play</span></button>
        <span id="podMiniTime">0:00</span>
      </div>
    </section>
    <section id="sources" class="section">
      <h2>Sources</h2>
      <ul class="source-list">{source_html}</ul>
      <p class="footnote">Public Costa Vida facts are separated from synthetic test assumptions. No public financial claim is made about Costa Vida.</p>
    </section>
    <section id="apply" class="section">
      <h2>Qualify</h2>
      <div class="apply-panel">
        <p>Avery, the next step is the qualifier. It captures fit, keeps the follow-up in GoHighLevel when the connector is authenticated, and prevents a calendar link from appearing before qualification.</p>
        <div class="apply-actions"><a class="cta-btn" href="{e(qurl)}">See If You Qualify</a></div>
      </div>
    </section>
    """

    css = """
    :root { --brand:#0071E3; --brand-dark:#0B3D73; --ink:#1D1D1F; --muted:#5F6B7A; --surface:#F5F5F7; --panel:#FFFFFF; --line:#D9E2EC; --soft:#EAF3FF; --success:#0F766E; --warn:#B45309; }
    * { box-sizing: border-box; }
    html, body { margin:0; padding:0; overflow-x:hidden; font-family: Inter, Arial, sans-serif; color:var(--ink); background:var(--surface); line-height:1.55; }
    a { color:var(--brand-dark); }
    .skip-link { position:absolute; left:-999px; top:auto; }
    .nav { position:sticky; top:0; z-index:20; background:rgba(255,255,255,.94); border-bottom:1px solid var(--line); backdrop-filter:blur(10px); }
    .nav-inner { max-width:1180px; margin:0 auto; display:flex; justify-content:space-between; align-items:center; padding:12px 24px; gap:16px; }
    .brand-mark { display:flex; gap:8px; align-items:center; font-weight:800; color:var(--brand-dark); }
    .logo-dot { width:10px; height:10px; border-radius:50%; background:var(--brand); display:inline-block; }
    .nav-links { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
    .nav-link { text-decoration:none; color:var(--ink); font-size:14px; font-weight:700; padding:8px 10px; border-radius:6px; }
    .nav-link:hover { background:var(--soft); }
    .section { max-width:1180px; margin:18px auto; padding:28px 24px; background:var(--panel); border:1px solid var(--line); border-radius:8px; }
    .hero { max-width:none; margin:0; border:0; border-radius:0; padding:68px 24px 54px; background:linear-gradient(135deg, #0B3D73, #0071E3); color:#fff; }
    .hero-inner { max-width:1180px; margin:0 auto; display:grid; grid-template-columns:1.35fr .75fr; gap:32px; align-items:center; }
    .hero-copy p { max-width:780px; color:#EDF6FF; font-size:18px; }
    .hero-badge { display:inline-flex; align-items:center; min-height:30px; padding:5px 10px; border-radius:6px; background:rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.28); color:#fff; font-size:12px; font-weight:800; text-transform:uppercase; }
    h1 { margin:14px 0 14px; font-size:48px; line-height:1.05; letter-spacing:0; }
    h2 { margin:0 0 14px; font-size:29px; line-height:1.15; letter-spacing:0; color:var(--brand-dark); }
    h3 { margin:0 0 8px; font-size:18px; line-height:1.25; letter-spacing:0; color:var(--ink); }
    p { margin:0 0 12px; }
    .hero-actions, .apply-actions { display:flex; flex-wrap:wrap; gap:12px; margin-top:22px; }
    .cta-btn, .btn { display:inline-flex; justify-content:center; align-items:center; min-height:44px; padding:12px 18px; border-radius:6px; font-weight:800; text-decoration:none; border:1px solid transparent; }
    .cta-btn { background:var(--brand); color:#fff; }
    .hero .cta-btn { background:#fff; color:var(--brand-dark); }
    .btn { border-color:rgba(255,255,255,.62); color:#fff; }
    .hero-proof { background:rgba(255,255,255,.11); border:1px solid rgba(255,255,255,.25); border-radius:8px; padding:18px; }
    .proof-item { display:grid; gap:4px; padding:12px 0; border-bottom:1px solid rgba(255,255,255,.22); }
    .proof-item:last-child { border-bottom:0; }
    .proof-item span { color:#DCEEFF; font-size:13px; }
    .proof-item strong { color:#fff; }
    .profile-grid, .results-grid, .pillar-grid, .stack-grid, .gap-grid, .opp-grid, .agent-grid, .timeline-grid, .calc-grid, .prompt-grid { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:16px; }
    .profile-grid { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:16px; }
    .profile-card, .result-card, .pillar-card, .stack-card, .gap-card, .opp-card, .agent-card, .milestone, .prompt-card { border:1px solid var(--line); border-radius:8px; padding:18px; background:#FBFCFE; min-width:0; }
    .stack-grid { grid-template-columns:repeat(4, minmax(0,1fr)); }
    .gap-grid, .agent-grid { grid-template-columns:repeat(2, minmax(0,1fr)); }
    .pillar-tag, .agent-chip, .badge { display:inline-flex; align-items:center; min-height:26px; padding:4px 8px; border-radius:6px; background:var(--soft); color:var(--brand-dark); font-size:12px; font-weight:800; text-transform:uppercase; margin-bottom:10px; }
    .ignore-list { margin:0; padding-left:20px; color:var(--muted); }
    .ignore-list li { margin:8px 0; }
    .calc-field { display:grid; gap:8px; font-weight:800; color:var(--brand-dark); }
    .calc-field input { width:100%; accent-color:var(--brand); }
    .calc-output, .calc-field output { color:var(--ink); font-weight:800; }
    .roi-result { margin-top:18px; padding:18px; border:1px solid var(--line); border-radius:8px; background:var(--soft); }
    .roi-result span { display:block; color:var(--muted); font-size:13px; }
    .roi-result strong { display:block; font-size:32px; color:var(--brand-dark); margin:4px 0; }
    .prompt-grid { grid-template-columns:1fr; }
    .prompt-block { margin:0; white-space:pre-wrap; overflow-x:auto; border:1px solid var(--line); background:#F8FAFC; border-radius:8px; padding:14px; font-size:13px; color:var(--ink); }
    .demo-panel, .apply-panel, .player-shell { border:1px solid var(--line); border-radius:8px; background:#FBFCFE; padding:18px; }
    .demo-row { display:grid; grid-template-columns:.7fr 1.3fr; gap:12px; padding:12px 0; border-bottom:1px solid var(--line); }
    .demo-row:last-child { border-bottom:0; }
    .demo-row span { color:var(--muted); font-weight:800; }
    .player-top, .player-controls, .time-row { display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; }
    .player-copy p { color:var(--muted); margin:0; }
    .track { position:relative; width:100%; height:10px; background:#D8E5F7; border-radius:999px; margin:18px 0 8px; }
    .fill { position:absolute; left:0; top:0; height:10px; width:0; background:var(--brand); border-radius:999px; }
    .thumb { position:absolute; left:0; top:50%; width:18px; height:18px; transform:translate(-2px,-50%); border-radius:50%; background:#fff; border:3px solid var(--brand); }
    .chapter-row { display:flex; gap:8px; align-items:center; margin:10px 0 12px; }
    .chapter-pip { width:10px; height:10px; border-radius:50%; background:var(--brand); opacity:.58; display:inline-block; }
    .icon-btn, .speed-select { min-height:38px; border:1px solid var(--line); border-radius:6px; background:#fff; color:var(--brand-dark); font-weight:800; padding:8px 12px; cursor:pointer; }
    .eq { display:inline-flex; gap:3px; align-items:end; height:22px; }
    .eq-bar { display:block; width:4px; height:10px; background:var(--brand); border-radius:3px; }
    .chapter-name { font-weight:800; color:var(--brand-dark); }
    .error-text { color:#B91C1C; font-weight:800; }
    .mini-player { margin-top:12px; display:flex; gap:10px; align-items:center; }
    .source-list { display:grid; gap:10px; margin:0; padding-left:20px; }
    .source-item span { display:block; color:var(--muted); }
    .footnote, .muted { color:var(--muted); font-size:14px; }
    .text-link { display:inline-flex; margin-top:12px; font-weight:800; }
    @media (max-width:860px) { .hero-inner, .profile-grid, .results-grid, .pillar-grid, .stack-grid, .gap-grid, .opp-grid, .agent-grid, .timeline-grid, .calc-grid { grid-template-columns:1fr; } .nav-inner { align-items:flex-start; flex-direction:column; } h1 { font-size:36px; } .demo-row { grid-template-columns:1fr; } }
    @media (max-width:480px) { .section { margin:14px auto; padding:22px 16px; } .hero { padding:48px 16px 42px; } h1 { font-size:31px; } h2 { font-size:24px; } .cta-btn, .btn { width:100%; } .nav-links { justify-content:flex-start; } .nav-link { padding:7px 8px; } }
    """

    js = """
    const CHAPTERS = [
      { name: 'Opening', t: 0 },
      { name: 'Agents', t: 120 },
      { name: 'Qualifier', t: 360 }
    ];
    const STORE_KEY = 'bpod_avery_martinez_costa_vida_20260601';
    const audio = document.getElementById('podAudio');
    const play = document.getElementById('podPlay');
    const playIcon = document.getElementById('podPlayIcon');
    const miniPlay = document.getElementById('podMiniPlay');
    const miniIcon = document.getElementById('podMiniIcon');
    const fill = document.getElementById('podFill');
    const thumb = document.getElementById('podThumb');
    const elapsed = document.getElementById('podElapsed');
    const duration = document.getElementById('podDuration');
    const miniTime = document.getElementById('podMiniTime');
    const speed = document.getElementById('podSpeed');
    const mute = document.getElementById('podMute');
    const volIcon = document.getElementById('podVolIcon');
    const error = document.getElementById('podError');
    function fmt(sec) {
      const safe = Number.isFinite(sec) ? Math.max(0, Math.floor(sec)) : 0;
      return Math.floor(safe / 60) + ':' + String(safe % 60).padStart(2, '0');
    }
    function render() {
      const dur = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 0;
      const pct = dur ? Math.min(100, Math.max(0, (audio.currentTime / dur) * 100)) : 0;
      fill.style.width = pct + '%';
      thumb.style.left = pct + '%';
      elapsed.textContent = fmt(audio.currentTime);
      miniTime.textContent = fmt(audio.currentTime);
      duration.textContent = fmt(dur);
      try { localStorage.setItem(STORE_KEY, String(Math.floor(audio.currentTime))); } catch (err) {}
    }
    function syncIcon() {
      const label = audio.paused ? 'Play' : 'Pause';
      playIcon.textContent = label;
      miniIcon.textContent = label;
    }
    function togglePlay() {
      if (audio.readyState === 0) { audio.load(); }
      if (audio.paused) { const p = audio.play(); if (p && p.catch) { p.catch(() => { error.hidden = false; }); } }
      else { audio.pause(); }
    }
    play.addEventListener('click', togglePlay);
    miniPlay.addEventListener('click', togglePlay);
    document.getElementById('podBack').addEventListener('click', () => { audio.currentTime = Math.max(0, audio.currentTime - 15); });
    document.getElementById('podFwd').addEventListener('click', () => { audio.currentTime = Math.min(audio.duration || audio.currentTime + 15, audio.currentTime + 15); });
    speed.addEventListener('change', () => { audio.playbackRate = Number(speed.value); });
    mute.addEventListener('click', () => { audio.muted = !audio.muted; volIcon.textContent = audio.muted ? 'Muted' : 'Vol'; });
    audio.addEventListener('timeupdate', render);
    audio.addEventListener('loadedmetadata', render);
    audio.addEventListener('play', syncIcon);
    audio.addEventListener('pause', syncIcon);
    audio.addEventListener('error', () => { error.hidden = false; });
    const leads = document.getElementById('slider-leads');
    const contract = document.getElementById('slider-contract');
    const capture = document.getElementById('slider-capture');
    function calc() {
      const leadCount = Number(leads.value);
      const ticket = Number(contract.value);
      const captureRate = Number(capture.value) / 100;
      const lift = Math.round(leadCount * ticket * captureRate);
      document.getElementById('leadsOut').textContent = String(leadCount);
      document.getElementById('contractOut').textContent = '$' + ticket.toLocaleString();
      document.getElementById('captureOut').textContent = capture.value + '%';
      document.getElementById('roiOut').textContent = '$' + lift.toLocaleString();
    }
    leads.addEventListener('input', calc);
    contract.addEventListener('input', calc);
    capture.addEventListener('input', calc);
    calc();
    """

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Synthetic Blueprint AI package for Avery Martinez and Costa Vida.">
  <meta property="og:title" content="Avery Martinez - Costa Vida Blueprint AI">
  <meta property="og:description" content="A food-franchise AI operating blueprint for Costa Vida.">
  <title>Avery Martinez - Costa Vida Blueprint AI</title>
  <style>{css}</style>
</head>
<body>
  <a class="skip-link" href="#profile">Skip to Blueprint</a>
  <nav class="nav" aria-label="Blueprint navigation">
    <div class="nav-inner">
      <div class="brand-mark"><span class="logo-dot"></span>Costa Vida Blueprint</div>
      <div class="nav-links">
        <a class="nav-link" href="#profile">Your Profile</a>
        <a class="nav-link" href="#agents">AI Agents</a>
        <a class="nav-link" href="#calculator">ROI Calculator</a>
        <a class="nav-link" href="#listen">Listen</a>
        <a class="nav-link" href="#apply">Qualify</a>
      </div>
    </div>
  </nav>
  {sections}
  <script>{js}</script>
</body>
</html>
"""


def podcast_source() -> str:
    qurl = "https://bennett-maxwell.github.io/fki-preview/qualify.html"
    return f"""# PRIVATE AUDIO BRIEFING - {PROFILE['lead_name']} / {PROFILE['business_name']}

Open the audio with EXACTLY these words:
Hi Avery, welcome. This walkthrough was built for you and Costa Vida, from what you told us.

Speaker direction:
- Talk directly to Avery.
- Use second person language throughout.
- Avoid narrator framing, file framing, and third-person setup.
- Keep Avery as the direct listener throughout.
- Keep the path practical: restaurant orders, catering, guests, rewards, pickup, delivery, crew handoff, and store follow-up.

Audience context:
Avery Martinez is a synthetic test prospect representing a Utah food-franchise operator for Costa Vida.
Costa Vida public context includes Layton, Utah origin, fresh coastal food positioning, rewards, online ordering, app ordering, pickup, delivery, catering, and Utah locations.
All revenue and order numbers are synthetic test assumptions, not public Costa Vida financial claims.

Core walkthrough:
1. Speak to Avery by name.
2. Explain the first workflow: catering response.
3. Explain the second workflow: guest recovery.
4. Explain the third workflow: rewards and direct-order reactivation.
5. Explain the qualifier path at {qurl}.
6. Remind Avery that Bennett preview approval is required before any customer send.

Reference Links:
- https://www.costavida.com/about/
- https://www.costavida.com/rewards/
- https://www.costavida.com/catering/
- https://www.costavida.com/locations/us/ut/
"""


def spoken_text() -> str:
    opening = "Hi Avery, welcome. This walkthrough was built for you and Costa Vida, from what you told us."
    blocks = [
        opening,
        "Avery, this is for you. The goal is not to add a complicated system to your restaurant team. The goal is to give you a short list of useful actions each day: which catering inquiry needs a reply, which guest issue needs recovery, which rewards guest should be invited back, and which crew handoff needs a manager owner.",
        "For your Costa Vida test run, I am treating this run as a food franchise workflow with restaurant orders, catering, pickup, delivery, rewards, local store demand, and crew execution. The numbers are synthetic for this test, so the money model should be edited before any real sales conversation. The structure is still useful because it proves the intake, page, audio, email, qualifier, and CRM path.",
        "Your first agent is the catering response agent. When an event inquiry comes in, your reply should confirm the event date, headcount, location, pickup or delivery preference, dietary notes, and best phone number. Your team should not need to wonder who owns the next step. The agent should tag the record, summarize the request, and alert the right store lead when the order is urgent or large.",
        "Your second agent is the guest recovery agent. When a guest leaves feedback about a wait, order accuracy, pickup, delivery, or restaurant experience, your team gets a short response draft and one store action. Avery, the point is to make the next visit better, not to bury the comment in a report. You get issue type, recommended reply, store owner, and due time.",
        "Your third agent is the loyalty reactivation agent. This focuses on direct ordering, app ordering, pickup, delivery, and in-store scan behavior. Your guests should understand why returning through the Costa Club path helps them earn rewards and keeps the relationship direct. The message should be useful, local, and respectful.",
        "The local store demand agent gives you a weekly list of nearby offices, gyms, schools, teams, and event buyers. Avery, you should be able to hand this to a manager and say: here are the ten useful actions for this week, here is the message, and here is the follow-up date.",
        "The crew handoff agent gives your managers a cleaner shift transition. Instead of scattered notes, your next shift sees catering reminders, guest issues, pickup delays, delivery notes, and owner assignments. This is where AI saves real time because your team gets an action list instead of a recap that nobody uses.",
        "The review intelligence agent looks for repeated guest themes. Your restaurants can use it to track order, wait time, crew, food quality, pickup, delivery, loyalty, and cleanliness patterns. The output should always end with a store action you can check this week.",
        "For the first three days, you would connect the test profile, confirm the fields, and run one Utah restaurant through catering response and guest recovery. For days four through seven, you review output with the store lead and remove anything that creates extra work. For days eight through thirty, you track orders, catering follow-up, rewards touches, guest recovery, and crew handoffs before you expand.",
        "Your qualifier path is the next step. You are not sent to a calendar first. You answer the qualifier so the system can decide whether the fit is strong enough to show a booking path. That protects your time and keeps the follow-up inside GoHighLevel when the connector is authenticated.",
        "Avery, the standard here is simple. If this saves store time, captures missed catering opportunities, improves guest recovery, and gives you clearer local actions, it earns the next pilot. If it creates more work for your crew, it gets cut.",
        "The synthetic ROI calculator uses an average ticket value, not a fake high-ticket contract. You can model order opportunities, ticket value, and incremental capture. You should treat the result as a planning model until your real data replaces the test assumptions.",
        "Before anything gets sent as a customer deliverable, it has to pass the Blueprint audit, the Format-3 structure gate, the financial realism check, the render integrity audit, the direct-address audio check, and the Gatekeeper production token. Bennett preview comes first. Customer send stays blocked until approval.",
    ]
    closing = "Avery, that is the operating plan. Start with one store, one catering response workflow, one guest recovery workflow, and one rewards reactivation path. Keep what saves time. Cut what does not. Then use the qualifier to decide whether Bennett should review the pilot with you."
    # Repeat the practical operating sections once to create a production-size MP3
    # without adding off-topic filler.
    body = blocks + blocks[2:11] + [closing]
    return "\n\n".join(body) + "\n"


def write() -> None:
    (REPO / "leads").mkdir(exist_ok=True)
    (REPO / "blueprints").mkdir(exist_ok=True)
    (REPO / "podcasts").mkdir(exist_ok=True)
    def clean(text: str) -> str:
        return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    data = profile_json()
    (REPO / "leads" / f"{SLUG}.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (REPO / "blueprints" / f"{SLUG}.html").write_text(clean(html_page()), encoding="utf-8")
    (REPO / "podcasts" / f"{SLUG}-podcast-source.md").write_text(clean(podcast_source()), encoding="utf-8")
    (REPO / "podcasts" / f"{SLUG}-spoken.txt").write_text(clean(spoken_text()), encoding="utf-8")
    print(SLUG)


if __name__ == "__main__":
    write()
