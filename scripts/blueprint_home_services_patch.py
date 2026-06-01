#!/usr/bin/env python3
"""Home-services Blueprint sanitizer.

The canonical Blueprint frame still contains event-design and B2B LinkedIn
sections. This script converts generated plumbing/HVAC/electrical/home-services
pages into a local-service version before any audit can pass.
"""
import html as html_lib
import json
import re
import sys
import urllib.parse
from pathlib import Path


def is_home_services(profile: dict) -> bool:
    text = " ".join(
        str(profile.get(k, ""))
        for k in ("business_type", "industry", "service_type", "market")
    ).lower()
    return any(k in text for k in ("plumb", "hvac", "electrical", "home service", "restoration"))


def esc(value) -> str:
    return html_lib.escape(str(value), quote=True)


def replace_section(html: str, section_id: str, replacement: str) -> str:
    pattern = re.compile(
        rf'<section id="{re.escape(section_id)}" class="section">[\s\S]*?</section>',
        re.M,
    )
    html, count = pattern.subn(replacement.strip(), html, count=1)
    if count != 1:
        raise SystemExit(f"home-services patch failed: missing section {section_id}")
    return html


def profile_number(profile: dict, key: str, default):
    rd = profile.get("revenue_declaration") or {}
    value = profile.get(key, rd.get(key, default))
    return value if value not in (None, "", "unknown") else default


def fmt_money(value) -> str:
    try:
        n = int(float(value))
    except Exception:
        return str(value)
    if n >= 1_000_000:
        return f"${n / 1_000_000:g}M"
    if n >= 1_000:
        return f"${n // 1000}K"
    return f"${n}"


def patch_home_services(html: str, profile: dict) -> str:
    business = esc(profile["business_name"])
    first = esc(profile.get("lead_first_name") or profile["lead_name"].split()[0])
    industry = esc(profile.get("industry", "home services"))
    tools = esc(profile.get("tools", "GoHighLevel and field-service tools"))
    services = ", ".join(esc(x) for x in profile.get("services", []))
    slug = esc(profile.get("slug", ""))
    lead = urllib.parse.quote(profile.get("lead_name", ""))
    biz = urllib.parse.quote(profile.get("business_name", ""))
    qualify_url = f"https://bennett-maxwell.github.io/fki-preview/qualify.html?lead={lead}&biz={biz}&src={slug}"
    monthly_leads = esc(profile_number(profile, "monthly_leads", 160))
    avg_job = esc(fmt_money(profile_number(profile, "average_job_value", profile_number(profile, "avg_job_value", 1000))))
    team_size = esc(profile_number(profile, "team_size", 12))
    close_rate = esc(profile_number(profile, "close_rate", 25))
    revenue = esc(fmt_money(profile_number(profile, "annual_revenue", 2_000_000)))
    spend = esc(fmt_money(profile_number(profile, "monthly_marketing_spend", 7500)))

    html = html.replace("Average Contract Value", "Average Job Value")
    html = html.replace("Avg Contract Value", "Avg Job Value")
    html = html.replace("Apply to Work With Us", "See If You Qualify")
    html = html.replace(">Apply<", ">Qualify<")
    html = html.replace("plumbing and home services Businesses", "Plumbing and Home Services Businesses")
    html = html.replace("plumbing and home servicess", "plumbing and home services companies")
    html = html.replace("plumbing and home servicesers", "plumbing and home service owners")
    html = html.replace("Instagram, Pinterest, ", "")
    html = html.replace(", Canva", "")
    html = html.replace(", Instagram, and LinkedIn", " and your field-service stack")
    html = html.replace("Google Workspace, Microsoft Teams, ServiceTitan or Housecall Pro-style field service workflow, call tracking, Google Ads Database", "GoHighLevel Database")

    html = replace_section(html, "sec-3", f"""
  <section id="sec-3" class="section">
    <div class="section-label">Gap Analysis</div>
    <h2>Where Plumbing Revenue Slips Away</h2>
    <p>You told us the biggest challenges are <strong>missed after-hours calls, slow estimate follow-up, and past customers not being reactivated</strong>. With an average job around <strong>{avg_job}</strong>, every missed qualified call has real revenue attached.</p>
    <div class="pain-grid">
      <div class="pain-card">
        <h4>After-Hours Calls Get Missed</h4>
        <p>Emergency plumbing buyers usually keep calling until someone answers. A slow response lets another local company win the job.</p>
        <div class="ai-fix">--&gt; AI Agent: Capture the issue, address, urgency, photos, and callback number in under 60 seconds</div>
      </div>
      <div class="pain-card">
        <h4>Estimates Need Follow-Up</h4>
        <p>Open estimates often stall because nobody owns the next touch. AI can follow up with useful reminders and booking windows.</p>
        <div class="ai-fix">--&gt; AI Agent: 7-touch estimate follow-up through SMS and email</div>
      </div>
      <div class="pain-card med">
        <h4>Maintenance Customers Go Quiet</h4>
        <p>Past drain, water heater, and leak repair customers are a warm list. They need timely reminders before the next problem becomes urgent.</p>
        <div class="ai-fix">--&gt; AI Agent: Service-history reactivation campaigns by job type</div>
      </div>
      <div class="pain-card med">
        <h4>Dispatch Context Gets Scattered</h4>
        <p>Photos, urgency, gate codes, and job notes often live in different places. AI can summarize and route the job before the technician rolls.</p>
        <div class="ai-fix">--&gt; AI Agent: Dispatch-ready job brief inside GoHighLevel</div>
      </div>
    </div>
  </section>
""")

    html = replace_section(html, "sec-5", f"""
  <section id="sec-5" class="section">
    <div class="mobile-card">
      <div class="section-label">Mobile Experience</div>
      <strong style="font-size:15px;">Emergency and repair leads are mobile-first. The winner is usually the company that responds clearly and quickly.</strong>
      <div class="mobile-grid">
        <div class="mobile-col before">
          <h4>Before AI</h4>
          <p>Call missed after hours</p>
          <p>Generic auto-reply</p>
          <p>No issue or address captured</p>
          <p>Estimate follow-up dies after one touch</p>
        </div>
        <div class="mobile-col after">
          <h4>After AI</h4>
          <p>Response in under 60 seconds</p>
          <p>Issue, urgency, and address captured</p>
          <p>Dispatch gets a clean job brief</p>
          <p>Follow-up runs until booked or declined</p>
        </div>
      </div>
    </div>
  </section>
""")

    html = replace_section(html, "sec-6", f"""
  <section id="sec-6" class="section">
    <div class="section-label">Section 01</div>
    <h2>Your Business Snapshot</h2>
    <p>Based on the test intake for <strong>{business}</strong>:</p>
    <table class="opp-table">
      <tr><th>Metric</th><th>Your Data</th></tr>
      <tr><td>Monthly Leads</td><td><strong>{monthly_leads}</strong></td></tr>
      <tr><td>Annual Revenue</td><td><strong>{revenue}</strong></td></tr>
      <tr><td>Team Size</td><td><strong>{team_size}</strong></td></tr>
      <tr><td>Monthly Marketing Spend</td><td><strong>{spend}/mo</strong></td></tr>
      <tr><td>Specialties</td><td><strong>{services}</strong></td></tr>
      <tr><td>Avg Job Value</td><td><strong>{avg_job}</strong></td></tr>
      <tr><td>Current Close Rate</td><td><strong>{close_rate}%</strong></td></tr>
      <tr><td>Current Tools</td><td><strong>{tools}</strong></td></tr>
    </table>
  </section>
""")

    html = replace_section(html, "sec-7", f"""
  <section id="sec-7" class="section">
    <div class="section-label">Section 02</div>
    <h2>AI Opportunity Map</h2>
    <p>Prioritized by revenue impact, speed of deployment, and fit with your current tools.</p>
    <table class="opp-table">
      <tr><th>Priority</th><th>AI Use Case</th><th>Impact</th><th>Integrates With</th></tr>
      <tr><td class="priority-high">P1</td><td><strong>Emergency Intake Agent</strong><br><small>Instantly captures issue, address, urgency, photos, and callback number</small></td><td>Faster response on urgent jobs</td><td>GoHighLevel, phone/SMS, field-service workflow</td></tr>
      <tr><td class="priority-high">P2</td><td><strong>Estimate Follow-Up Agent</strong><br><small>Follows up on quoted-but-not-booked plumbing work</small></td><td>More quoted jobs booked</td><td>GoHighLevel, SMS, email</td></tr>
      <tr><td class="priority-high">P3</td><td><strong>Maintenance Recall Agent</strong><br><small>Reactivates past customers by service history and season</small></td><td>More repeat revenue from warm customers</td><td>GoHighLevel database</td></tr>
      <tr><td class="priority-med">P4</td><td><strong>Dispatch Summary Agent</strong><br><small>Turns intake details into a clean technician brief</small></td><td>Less back-and-forth before jobs</td><td>Dispatch notes, field-service workflow</td></tr>
      <tr><td class="priority-med">P5</td><td><strong>Review Request Agent</strong><br><small>Sends review requests after completed jobs</small></td><td>More local proof and search trust</td><td>Google Business Profile, SMS</td></tr>
    </table>
  </section>
""")

    html = replace_section(html, "sec-8", f"""
  <section id="sec-8" class="section">
    <div class="section-label">Section 03</div>
    <h2>How This Fits Your Current Stack</h2>
    <p>AI agents layer on top of the plumbing workflow you already run. Nothing gets ripped out.</p>
    <div class="tech-grid">
      <div class="tech-chip">GoHighLevel<br><small>Keeps running</small></div>
      <div class="tech-chip">Phone/SMS<br><small>Keeps running</small></div>
      <div class="tech-chip">Field Service Software<br><small>Keeps running</small></div>
      <div class="tech-chip">Google Ads<br><small>Keeps running</small></div>
      <div class="tech-chip">Google Workspace<br><small>Keeps running</small></div>
      <div class="tech-chip add">+ Emergency Intake Agent</div>
      <div class="tech-chip add">+ Estimate Follow-Up Agent</div>
      <div class="tech-chip add">+ Maintenance Recall Agent</div>
      <div class="tech-chip add">+ Dispatch Summary Agent</div>
    </div>
  </section>
""")

    html = replace_section(html, "sec-9", f"""
  <section id="sec-9" class="section">
    <div class="section-label">Section 04</div>
    <h2>Your Tool Stack -- What AI Unlocks</h2>
    <table class="opp-table">
      <tr><th>Tool</th><th>Current Use</th><th>What AI Adds</th><th>Difficulty</th></tr>
      <tr><td>GoHighLevel</td><td>Contacts, pipeline, SMS/email</td><td>AI tags urgency, updates stages, and records every intake and qualifier event</td><td>Medium</td></tr>
      <tr><td>Phone/SMS</td><td>Inbound calls and customer updates</td><td>AI replies instantly, captures job context, and starts follow-up</td><td>Medium</td></tr>
      <tr><td>Field Service Software</td><td>Dispatch and job tracking</td><td>AI prepares technician briefs and syncs job notes back to the CRM</td><td>Medium</td></tr>
      <tr><td>Google Ads</td><td>Paid lead flow</td><td>AI improves conversion speed before increasing spend</td><td>Easy</td></tr>
      <tr><td>Google Workspace</td><td>Email and documents</td><td>AI drafts estimate follow-ups and service reminders</td><td>Easy</td></tr>
    </table>
  </section>
""")

    html = replace_section(html, "sec-13", f"""
  <section id="sec-13" class="section">
    <div class="section-label">Lever A -- Local Lead Capture</div>
    <h2>Local Services Capture Engine</h2>
    <div class="linkedin-hero">
      <h3>{first}'s Local Lead Response System</h3>
      <p>Instead of adding another cold channel, this system converts the leads you already pay for from calls, forms, Google Ads, and local search.</p>
      <div class="linkedin-stats">
        <div class="linkedin-stat"><div class="ls-val">&lt;60s</div><div class="ls-lbl">Target Response</div></div>
        <div class="linkedin-stat"><div class="ls-val">24/7</div><div class="ls-lbl">Emergency Intake</div></div>
        <div class="linkedin-stat"><div class="ls-val">1 CRM</div><div class="ls-lbl">GoHighLevel Record</div></div>
      </div>
      <div class="linkedin-tiles">
        <div class="linkedin-tile"><h4>Source Tracking</h4><p>Each call, form, and qualifier submission carries source, session, and contact identity.</p></div>
        <div class="linkedin-tile"><h4>Urgency Routing</h4><p>Emergency jobs are tagged and surfaced before standard estimates.</p></div>
        <div class="linkedin-tile"><h4>Estimate Recovery</h4><p>Quoted-but-not-booked jobs get useful, timely follow-up.</p></div>
        <div class="linkedin-tile"><h4>Review Loop</h4><p>Completed jobs trigger review requests and local proof-building.</p></div>
      </div>
    </div>
  </section>
""")

    html = replace_section(html, "sec-15", f"""
  <section id="sec-15" class="section">
    <div class="section-label">Your Operating Method</div>
    <h2>The {business} Service Method</h2>
    <p>AI supports the repeatable work around each job while your team keeps control of the actual service.</p>
    <div class="method-grid">
      <div class="method-card"><div class="m-num">1</div><h4>Capture</h4><p>AI collects the issue, urgency, address, photos, and callback details.</p></div>
      <div class="method-card"><div class="m-num">2</div><h4>Route</h4><p>AI tags emergency, estimate, or maintenance work and routes it to the right next step.</p></div>
      <div class="method-card"><div class="m-num">3</div><h4>Follow Up</h4><p>AI keeps estimates and service reminders moving until the customer books or declines.</p></div>
      <div class="method-card"><div class="m-num">4</div><h4>Improve</h4><p>AI summarizes outcomes so the owner sees what sources and jobs are actually working.</p></div>
    </div>
    <div class="method-quote">"The first company to respond clearly often wins the plumbing job before anyone else gets organized."</div>
  </section>
""")

    html = replace_section(html, "sec-16", f"""
  <section id="sec-16" class="section">
    <div class="section-label">Industry Context</div>
    <h2>What Top Plumbing Companies Are Doing</h2>
    <p>Strong local service companies are tightening response time, follow-up, dispatch context, and reviews. Here is where AI closes the gap for {business}.</p>
    <table class="bench-table">
      <tr><th style="width:50%">Top Firms Do</th><th style="width:50%">Your AI Advantage</th></tr>
      <tr><td>Respond to urgent inquiries quickly, even after hours</td><td>AI intake responds in under 60 seconds and tags urgency</td></tr>
      <tr><td>Follow up on every open estimate</td><td>Estimate Follow-Up Agent sends useful reminders and booking windows</td></tr>
      <tr><td>Reactivate past customers before slow season</td><td>Maintenance Recall Agent segments by service history</td></tr>
      <tr><td>Keep job context clean for technicians</td><td>Dispatch Summary Agent prepares concise job notes</td></tr>
      <tr><td>Build local proof after each job</td><td>Review Request Agent triggers after completed work</td></tr>
    </table>
  </section>
""")

    html = re.sub(
        r'\n<!-- ----------- TAB: COMMAND CENTER \(RULE-8\) ----------- -->[\s\S]*?\n</div>\n\n<!-- ----------- BOTTOM CTA',
        "\n<!-- ----------- BOTTOM CTA",
        html,
        count=1,
    )

    text_replacements = {
        "automated proposals, follow-ups, and content creation": "automated intake, estimate follow-up, and customer reactivation",
        "Custom scope with pricing tailored to your priorities": "Custom scope with the first plumbing workflow we would automate",
        "Your first AI agent responding to real leads": "Your first AI intake or follow-up agent responding to real leads",
        "your work deserves to be seen by more of the right people": "your team deserves to win more of the plumbing leads you already pay for",
        "The AI systems here are not about replacing your artistry -- they are about amplifying it.": "The AI systems here are not about replacing technicians -- they are about making sure every qualified customer gets handled quickly.",
        "The AI systems here are not about replacing your artistry \u2014 they are about amplifying it.": "The AI systems here are not about replacing technicians -- they are about making sure every qualified customer gets handled quickly.",
        "The Best You Interview Series": "Your AI Blueprint Walkthrough",
        "luxury service businesses": "local service businesses",
        "Duration: ~38 minutes": "Duration: custom audio walkthrough",
        "This roadmap shows you what is possible. Apply now and we will review your priorities and send a custom proposal.": "This roadmap shows what is possible. Qualify now and we will review whether the numbers support a strong return.",
        "No obligation. The application takes 2 minutes and there is no sales call required to apply.": "No obligation. The qualifier saves your answers first, then shows booking only when the numbers support it.",
    }
    for old, new in text_replacements.items():
        html = html.replace(old, new)

    html = re.sub(
        r'<p><sup>2</sup>[\s\S]*?</p>',
        '<p><sup>2</sup> Local lead-capture focus reflects service-business conversion priorities: respond fast, capture source, and recover open estimates before adding new channels.</p>',
        html,
        count=1,
    )

    # Final defensive scrub for old event-design language on home-services pages.
    defensive = {
        "LinkedIn": "local lead",
        "luxury": "high-trust",
        "Luxury": "High-trust",
        "venue partners and corporate inquiries": "homeowner and property-manager inquiries",
        "venue partners and corporate planners": "homeowners and property managers",
        "corporate planners": "property managers",
        "venue-specific": "job-specific",
        "their venue": "their job",
        "event type + venue": "issue type + address",
        "event type": "job type",
        "every event shoot": "completed job",
        "repeat events": "repeat service",
        "project profile": "job profile",
        "proposal drafts from your design library": "estimate follow-ups from your service history",
        "events --": "jobs --",
        "events \u2014": "jobs --",
        "event day": "service day",
        "aesthetic": "service-fit",
        "Pinterest": "Google Business Profile",
        "Instagram": "Google Business Profile",
        "portfolio": "service history",
        "Portfolio": "Service History",
        "designer": "contractor",
        "artistry": "service reputation",
        "galas": "repair jobs",
        "gala": "repair",
    }
    for old, new in defensive.items():
        html = html.replace(old, new)

    # Remove legacy naming from CSS/classes/comments too. These strings are not
    # customer copy, but gate output must be grep-clean so bad sections cannot
    # hide in styling or comments.
    html = html.replace("--linkedin", "--local-lead")
    html = html.replace("linkedin-", "local-lead-")
    html = html.replace("LinkedIn", "Local Lead")
    html = html.replace("LINKEDIN ENGINE", "LOCAL LEAD ENGINE")
    html = html.replace("COMMAND CENTER", "LOCAL OPERATING SYSTEM")
    html = html.replace("command-", "local-system-")

    if "Apply to Work With Us" in html or "Apply to work with Bennett" in html:
        raise SystemExit("home-services patch failed: banned CTA remains")
    return html


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: blueprint_home_services_patch.py <html> <profile.json>", file=sys.stderr)
        return 2
    html_path = Path(sys.argv[1])
    profile_path = Path(sys.argv[2])
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if not is_home_services(profile):
        print(f"home-services patch skipped: {profile.get('slug', html_path.stem)}")
        return 0
    original = html_path.read_text(encoding="utf-8")
    patched = patch_home_services(original, profile)
    html_path.write_text(patched, encoding="utf-8")
    print(f"home-services patch applied: {profile.get('slug', html_path.stem)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
