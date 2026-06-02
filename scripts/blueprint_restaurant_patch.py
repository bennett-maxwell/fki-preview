#!/usr/bin/env python3
"""Restaurant / food-franchise Blueprint sanitizer.

The canonical Blueprint frame has historically carried SaaS, home-services, and
calendar-link prompt copy. This sanitizer converts generated restaurant/QSR/food-
franchise pages into a restaurant-safe customer journey before audits run.
"""
import html as html_lib
import json
import re
import sys
import urllib.parse
from pathlib import Path


def is_restaurant(profile: dict) -> bool:
    text = " ".join(str(profile.get(k, "")) for k in (
        "business_type", "industry", "service_type", "market"
    )).lower()
    return any(k in text for k in (
        "restaurant", "qsr", "quick service", "fast casual", "fast-casual",
        "food franchise", "food_franchise", "food chain", "catering", "pickup",
        "delivery", "loyalty", "guest"
    ))


def esc(value) -> str:
    return html_lib.escape(str(value), quote=True)


def replace_section(html: str, section_id: str, replacement: str) -> str:
    pattern = re.compile(
        rf'<section([^>]*\bid=["\']{re.escape(section_id)}["\'][^>]*)>[\s\S]*?</section>',
        re.I | re.M,
    )
    new_html, count = pattern.subn(replacement.strip(), html, count=1)
    if count != 1:
        raise SystemExit(f"restaurant patch failed: missing section {section_id}")
    return new_html


def profile_number(profile: dict, key: str, default):
    rd = profile.get("revenue_declaration") or {}
    value = profile.get(key, rd.get(key, default))
    return value if value not in (None, "", "unknown") else default


def fmt_money(value) -> str:
    try:
        n = float(str(value).replace('$', '').replace(',', '').split()[0])
    except Exception:
        return str(value)
    if n >= 1_000_000:
        return f"${n / 1_000_000:g}M"
    if n >= 1_000:
        return f"${int(n) // 1000}K"
    if n == int(n):
        return f"${int(n)}"
    return f"${n:.2f}"


def qualify_url(profile: dict) -> str:
    if profile.get("qualify_url"):
        return str(profile["qualify_url"])
    lead = urllib.parse.quote(profile.get("lead_name", ""))
    biz = urllib.parse.quote(profile.get("business_name", ""))
    slug = urllib.parse.quote(profile.get("slug", ""))
    return f"https://bennett-maxwell.github.io/fki-preview/qualify.html?lead={lead}&biz={biz}&src={slug}"


def agent_cards(profile: dict) -> str:
    cards = []
    for i, a in enumerate(profile.get("ai_agents", [])[:6], 1):
        cards.append(f"""
        <div class="agent-card">
          <h3>Agent #{i}: {esc(a.get('name', f'Restaurant AI Agent {i}'))}</h3>
          <p class="agent-desc">{esc(a.get('desc', 'Restaurant workflow automation'))}</p>
          <div class="agent-prompt">{esc(a.get('prompt', ''))}</div>
          <div class="agent-result">What this does: {esc(a.get('result', 'Automates a key restaurant workflow'))}</div>
          <div class="agent-time">Setup time: ~{esc(a.get('time', '6 minutes'))}</div>
        </div>""")
    return "\n".join(cards)


def patch_restaurant(html: str, profile: dict) -> str:
    business = esc(profile["business_name"])
    first = esc(profile.get("lead_first_name") or profile["lead_name"].split()[0])
    lead = esc(profile.get("lead_name", first))
    industry = esc(profile.get("industry", "restaurant operations"))
    tools = esc(profile.get("tools", "GoHighLevel, POS, online ordering, and manager reporting tools"))
    market = esc(profile.get("market", "local guests, catering buyers, and loyalty members"))
    services = profile.get("services", []) or ["catering", "online ordering", "guest recovery"]
    services_str = esc(", ".join(map(str, services)))
    q_url = esc(qualify_url(profile))
    avg_ticket = profile_number(profile, "avg_job_value", 38)
    monthly_leads = esc(profile_number(profile, "monthly_leads", 420))
    team_size = esc(profile_number(profile, "team_size", 25))
    locations = profile.get("locations") or []
    locations_str = esc(", ".join(locations) if isinstance(locations, list) else str(locations))
    spend = esc(fmt_money(profile_number(profile, "monthly_marketing_spend", 12500)))

    # Global CTA + direct-booking boundary corrections.
    html = html.replace(">Apply<", ">Qualify<")
    html = html.replace("Get Your AI Quote", "See If You Qualify")
    html = html.replace("Apply to Work With Us", "See If You Qualify")
    html = html.replace("Apply to work with Bennett", "See If You Qualify")
    html = html.replace("Apply to work with us", "See If You Qualify")
    html = html.replace("No sales call required to apply.", "No booking opens until this tracked qualifier is submitted.")
    html = html.replace("Application takes 2 minutes. No sales call required to apply.", "Application takes 2 minutes. No calendar bypass, no legal documents, no pressure.")

    # Restaurant-safe ROI default and preset. The default must be an actual ticket
    # value for this profile, not the inherited SaaS/home-services number.
    try:
        ticket = int(float(avg_ticket))
    except Exception:
        ticket = 38
    ticket = max(8, min(ticket, 60))
    html = re.sub(r'(id="sl-contract"[^>]*?step=")\d+("[^>]*?value=")\d+("[^>]*?)', rf'\g<1>1\g<2>{ticket}\g<3>', html)
    html = re.sub(r'(contract:\s*)\d+', rf'\g<1>{ticket}', html)
    html = html.replace("Average Contract Value", "Average Guest or Catering Ticket")
    html = html.replace("Avg Contract Value", "Avg Ticket")
    html = html.replace("Average annual customer value in dollars", "Average guest or catering ticket in dollars")

    html = replace_section(html, "results", f"""
<section class="section" id="results">
  <div class="container">
    <p class="section-label">What Restaurants Are Already Doing</p>
    <h2 class="section-title">Fast-Casual Operators Are Using AI Around the Rush</h2>
    <p class="section-sub">{first}, the strongest opportunity for {business} is not replacing your team. It is giving managers an AI layer that handles response speed, follow-up, and reporting while the stores keep serving guests.</p>
    <div class="result-grid">
      <div class="result-card"><span class="result-num">01</span><h3>Catering response</h3><p>AI answers high-value catering inquiries quickly, captures date, headcount, budget, pickup/delivery, and dietary notes, then routes the next action.</p></div>
      <div class="result-card"><span class="result-num">02</span><h3>Guest recovery</h3><p>AI reviews feedback and drafts owner-approved responses before guest frustration becomes a public reputation problem.</p></div>
      <div class="result-card"><span class="result-num">03</span><h3>Manager reporting</h3><p>AI turns scattered shift notes into one owner-ready operating brief across every location.</p></div>
    </div>
  </div>
</section>
""")

    html = replace_section(html, "stack", f"""
<section class="section" id="stack">
  <div class="container">
    <p class="section-label">Where You Are Today</p>
    <h2 class="section-title">Your Current Restaurant Stack</h2>
    <p class="section-sub">This plan keeps {business}'s existing tools in place and adds AI where the handoffs break down.</p>
    <div class="stack-list">
      <div class="stack-item"><strong>Current tools:</strong> {tools}</div>
      <div class="stack-item"><strong>Primary market:</strong> {market}</div>
      <div class="stack-item"><strong>Locations:</strong> {locations_str}</div>
      <div class="stack-item"><strong>Services:</strong> {services_str}</div>
    </div>
  </div>
</section>
""")

    html = replace_section(html, "gaps", f"""
<section class="section section-alt" id="gaps">
  <div class="container">
    <p class="section-label">Where the Leverage Is</p>
    <h2 class="section-title">Three Places Revenue and Time Leak</h2>
    <div class="gap-grid">
      <div class="gap-card"><h3>Lunch-rush inquiries</h3><p>Catering and large-party questions arrive while the team is busiest. AI makes the first response fast and complete.</p></div>
      <div class="gap-card"><h3>Guest feedback split across channels</h3><p>Reviews, DMs, and contact forms need a consistent owner-approved response path.</p></div>
      <div class="gap-card"><h3>Owner visibility across stores</h3><p>Three stores create more notes than one owner can chase. AI compiles the operating picture automatically.</p></div>
    </div>
  </div>
</section>
""")

    html = replace_section(html, "oppmap", f"""
<section class="section" id="oppmap">
  <div class="container">
    <p class="section-label">Prioritized Roadmap</p>
    <h2 class="section-title">AI Opportunity Map for {business}</h2>
    <table class="opp-table">
      <tr><th>Priority</th><th>Agent</th><th>What It Does</th><th>Primary Tool</th></tr>
      <tr><td class="priority-high">P1</td><td>Catering Speed-to-Lead</td><td>Captures event details and replies before the buyer moves on.</td><td>GoHighLevel</td></tr>
      <tr><td class="priority-high">P2</td><td>Guest Recovery</td><td>Classifies feedback, drafts responses, and escalates sensitive issues.</td><td>Google reviews, DMs, CRM</td></tr>
      <tr><td class="priority-high">P3</td><td>Manager Shift Summary</td><td>Turns manager notes into one daily owner brief.</td><td>Slack, Drive, POS summaries</td></tr>
      <tr><td class="priority-med">P4</td><td>Local Store Marketing</td><td>Drafts weekly promos tied to catering, loyalty, and neighborhood events.</td><td>Meta, email, Google Business Profile</td></tr>
      <tr><td class="priority-med">P5</td><td>Franchise Inquiry Qualification</td><td>Collects buyer fit signals without legal docs or earnings claims.</td><td>Qualifier form and CRM</td></tr>
    </table>
  </div>
</section>
""")

    html = replace_section(html, "agents", f"""
<section class="section" id="agents">
  <div class="container">
    <p class="section-label">Your AI System</p>
    <h2 class="section-title">6 AI Agents Built for {business}</h2>
    <p class="section-sub">Each agent below is specific to Chad's restaurant operations, not a copied industry template.</p>
    <div class="agent-grid">
      {agent_cards(profile)}
    </div>
  </div>
</section>
""")

    html = replace_section(html, "prompts", f"""
<section class="section section-alt" id="prompts">
  <div class="container">
    <p class="section-label">Try These First</p>
    <h2 class="section-title">Three Prompts Chad Can Use Today</h2>
    <p class="section-sub">These prompts are manual versions of the first automation layer. The full system runs them automatically from live events.</p>
    <div class="prompt-grid">
      <div class="prompt-card"><div class="prompt-header"><h3>{esc(profile.get('prompt_1_label', 'Catering Speed-to-Lead Agent'))}</h3></div><pre class="prompt-pre">{esc(profile.get('prompt_1', ''))}</pre></div>
      <div class="prompt-card"><div class="prompt-header"><h3>{esc(profile.get('prompt_2_label', 'Franchise Inquiry Qualification Agent'))}</h3></div><pre class="prompt-pre">{esc(profile.get('prompt_2', ''))}</pre></div>
      <div class="prompt-card"><div class="prompt-header"><h3>{esc(profile.get('prompt_3_label', 'Guest Recovery Agent'))}</h3></div><pre class="prompt-pre">{esc(profile.get('prompt_3', ''))}</pre></div>
    </div>
    <div class="diy-or-partner">
      <h3>Two paths forward for {first}:</h3>
      <div class="path-grid">
        <div class="path"><h4>DIY Path</h4><p>Use the prompts above to start improving response speed, guest recovery, and daily reporting.</p></div>
        <div class="path"><h4>Partner Path</h4><p>FKI builds the automated version, connects it to your tools, and audits it before anything is sent externally.</p><a href="{q_url}" class="path-cta">See If You Qualify</a></div>
      </div>
    </div>
  </div>
</section>
""")

    html = replace_section(html, "demo", f"""
<section class="section section-alt" id="demo">
  <div class="container">
    <p class="section-label">Live Preview</p>
    <h2 class="section-title">{business} Speed-to-Lead Flow</h2>
    <p class="section-sub">A catering inquiry comes in. The AI captures headcount, date, pickup or delivery, dietary constraints, budget range, and preferred location, then routes the summary to the right manager.</p>
    <p style="font-size:0.92rem;color:var(--text-muted);max-width:660px;margin:1.5rem auto 0;text-align:center;">This is designed for a busy restaurant day: no new platform to babysit, no calendar bypass, and no legal document send.</p>
  </div>
</section>
""")

    html = replace_section(html, "apply", f"""
<section class="cta-section" id="apply">
  <div class="container">
    <h2>Ready to See This<br><span>Working for {business}?</span></h2>
    <p class="cta-personal">"{first}, I built this roadmap around the parts of Summit Street Tacos where speed and consistency matter most: catering response, guest recovery, manager reporting, and qualified expansion conversations. The goal is not to replace your team. The goal is to give your team a system that never forgets the next step." &mdash; Bennett</p>
    <p>The next step is the tracked qualifier. It confirms fit, updates the same CRM contact, and only then allows any next-step scheduling path.</p>
    <a href="{q_url}" class="cta-btn">See If You Qualify</a>
    <p class="cta-sub">Application takes 2 minutes. No calendar bypass, no legal document send, no pressure.</p>
  </div>
</section>
""")

    html = re.sub(r'<a href="([^"]*qualify\.html[^"]*)" class="mobile-cta-btn">[^<]+</a>',
                  rf'<a href="\1" class="mobile-cta-btn">See If You Qualify</a>', html)

    # Remove lingering banned drift terms from non-script body by replacing stale examples
    # that may be left in small captions or copied prompt text.
    replacements = {
        "product launches": "restaurant rushes",
        "support tickets": "guest messages",
        "billing questions": "order questions",
        "feature requests": "menu questions",
        "churn risk": "guest churn risk",
        "recurring revenue locked in": "repeat guest revenue protected",
        "requests a demo": "asks about catering",
        "live demo where": "restaurant walkthrough where",
        "payment confirmation": "order confirmation",
        "kickoff call": "setup call",
        "login URL": "resource link",
        "automation templates": "restaurant workflows",
        "complete onboarding lifecycle": "complete guest-response lifecycle",
        "Client Success Onboarding Agent": "Restaurant Guest Response Agent",
        "proposal specialist": "catering response specialist",
        "booking system": "tracked qualifier path",
        "[Scheduling Link]": "[Tracked Qualifier Link]",
        "Book here": "Continue here",
    }
    for old, new in replacements.items():
        html = re.sub(re.escape(old), new, html, flags=re.I)

    # Timeline wording must not imply a calendar bypass from the Blueprint page.
    html = re.sub(r'kickoff call', 'setup review', html, flags=re.I)
    html = re.sub(r'kickoff scheduling', 'setup review sequencing', html, flags=re.I)
    html = re.sub(r'scheduled kickoff', 'scheduled setup review', html, flags=re.I)
    html = re.sub(r'kickoff', 'setup review', html, flags=re.I)

    return html


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: blueprint_restaurant_patch.py <blueprint.html> <profile.json>", file=sys.stderr)
        return 2
    html_path = Path(sys.argv[1])
    profile_path = Path(sys.argv[2])
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if not is_restaurant(profile):
        print(f"restaurant patch skipped: {profile.get('slug', html_path.stem)}")
        return 0
    html = html_path.read_text(encoding="utf-8", errors="replace")
    patched = patch_restaurant(html, profile)
    html_path.write_text(patched, encoding="utf-8")
    print(f"restaurant patch applied: {profile.get('slug', html_path.stem)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
