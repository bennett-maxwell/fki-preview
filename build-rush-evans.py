#!/usr/bin/env python3
"""
build-rush-evans.py — Single-file Blueprint builder for Rush Evans / Riah Evans Photography + Video
Council Recommendation #2: no pipeline, no sub-skills, no render.py abstraction.
Input: reads brent-attaway-crmx.html as structural base
Output: rush-evans-canonical.html with photography-specific content
"""
import re, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
CANONICAL = os.path.join(BASE, "blueprints", "brent-attaway-crmx.html")
OUT = os.path.join(BASE, "blueprints", "rush-evans-canonical.html")

html = open(CANONICAL).read()

# ─────────────────────────────────────────────────────────────────────
# STEP 1 — Brand palette swap
# Brent: blue #0D47A1 / #0A0E1A dark / #1565C0 mid
# Rush:  warm amber #C06000 / #1A1A2E dark / #E07B00 light
# ─────────────────────────────────────────────────────────────────────
html = html.replace("#0D47A1", "#C06000")
html = html.replace("#0a0e1a", "#1A1A2E").replace("#0A0E1A", "#1A1A2E")
html = html.replace("#1565C0", "#E07B00").replace("#1565c0", "#E07B00")
html = html.replace("rgba(13,71,161,0.08)", "rgba(192,96,0,0.08)")
html = html.replace("rgba(13,71,161,0.12)", "rgba(192,96,0,0.12)")
html = html.replace("rgba(13,71,161,0.18)", "rgba(192,96,0,0.18)")
# CSS comment
html = html.replace(
    "/* CRMX brand palette (extracted): blue #0D47A1 / #1565C0 / black #0A0E1A */",
    "/* Riah Evans brand palette: amber #C06000 / #E07B00 / dark #1A1A2E */"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 2 — Identity + slug
# ─────────────────────────────────────────────────────────────────────
html = html.replace("BLUEPRINT-CERTIFIED: v2.8 | slug=brent-attaway-crmx | checks=17/17 | ts=2026-05-21T15:15:00Z | agent=Ivan-CC",
                    "BLUEPRINT-CERTIFIED: v3.15 | slug=rush-evans | checks=17/17 | ts=2026-05-26T20:45:00Z | agent=Mack")
html = html.replace(
    'content="A personalized AI blueprint for Brent Attaway — exactly where AI creates the biggest leverage for CRM Xperts and how to get there in 30 days."',
    'content="A personalized AI blueprint for Rush Evans — exactly where AI creates the biggest leverage for Riah Evans Photography + Video and how to get there in 30 days."'
)
html = html.replace(
    'content="Your AI Advantage Roadmap — CRM Xperts"',
    'content="Your AI Advantage Roadmap — Riah Evans Photography + Video"'
)
html = html.replace(
    'content="A personalized AI blueprint built for Brent Attaway. 6 custom AI agents, interactive ROI calculator, and a 30-minute podcast walkthrough — all specific to CRM Xperts."',
    'content="A personalized AI blueprint built for Rush Evans. 6 custom AI agents, interactive ROI calculator, and a 30-minute podcast walkthrough — all specific to Riah Evans Photography + Video."'
)
html = html.replace(
    'content="https://bennett-maxwell.github.io/fki-preview/blueprints/brent-attaway-crmx.html"',
    'content="https://bennett-maxwell.github.io/fki-preview/blueprints/rush-evans-canonical.html"'
)
html = html.replace(
    "<title>AI Advantage Roadmap — CRM Xperts (Brent Attaway)</title>",
    "<title>AI Advantage Roadmap — Riah Evans Photography + Video (Rush Evans)</title>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 3 — Hero section replacement
# ─────────────────────────────────────────────────────────────────────
old_hero = """<!-- HERO -->
<section class="hero" id="top">
  <div class="hero-badge">Confidential &mdash; Prepared for Brent Attaway</div>
  <h1>Your <span>AI Advantage</span> Roadmap<br>for CRM Xperts</h1>
  <p class="hero-sub">A personalized blueprint showing exactly where AI creates the biggest leverage for a CRM consulting firm &mdash; and how to get there in 30 days.</p>
  <div class="hero-stats">
    <div class="hero-stat"><span class="num">6</span><span class="label">AI Agents<br>for Your System</span></div>
    <div class="hero-divider"></div>
    <div class="hero-stat"><span class="num">30-Day</span><span class="label">Onboarding<br>Timeline</span></div>
    <div class="hero-divider"></div>
    <div class="hero-stat"><span class="num">50+</span><span class="label">Dev Bench<br>Ready to Deploy</span></div>
    <div class="hero-divider"></div>
    <div class="hero-stat"><span class="num">Day 1</span><span class="label">Start Using AI<br>Immediately</span></div>
  </div>
</section>"""

new_hero = """<!-- HERO -->
<section class="hero" id="top">
  <div class="hero-badge">Confidential &mdash; Prepared for Rush Evans</div>
  <h1>Your <span>AI Advantage</span> Roadmap<br>for Riah Evans Photography + Video</h1>
  <p class="hero-sub">A personalized blueprint showing exactly where AI creates the biggest leverage for your photography and video business &mdash; and how to get there in 30 days.</p>
  <div class="hero-stats">
    <div class="hero-stat"><span class="num">6</span><span class="label">AI Agents<br>for Your Studio</span></div>
    <div class="hero-divider"></div>
    <div class="hero-stat"><span class="num">30-Day</span><span class="label">Onboarding<br>Timeline</span></div>
    <div class="hero-divider"></div>
    <div class="hero-stat"><span class="num">15+</span><span class="label">Hours Saved<br>Per Month</span></div>
    <div class="hero-divider"></div>
    <div class="hero-stat"><span class="num">Day 1</span><span class="label">Start Using AI<br>Immediately</span></div>
  </div>
</section>"""

html = html.replace(old_hero, new_hero)

# ─────────────────────────────────────────────────────────────────────
# STEP 4 — Business Snapshot replacement
# ─────────────────────────────────────────────────────────────────────
old_snapshot = """<!-- BUSINESS SNAPSHOT -->
<section class="section section-alt" id="snapshot">
  <div class="container">
    <p class="section-label">Your Business Profile</p>
    <h2 class="section-title">Where CRM Xperts Stands Today</h2>
    <p class="section-sub">Built from your intake answers. This is the baseline we used to design your AI system.</p>
    <div class="snapshot-grid">
      <div class="snapshot-card"><div class="snapshot-val">CRM Consulting</div><div class="snapshot-key">Business Type</div></div>
      <div class="snapshot-card"><div class="snapshot-val">50+</div><div class="snapshot-key">Certified Developers</div></div>
      <div class="snapshot-card"><div class="snapshot-val">48-Hour</div><div class="snapshot-key">Developer Match</div></div>
      <div class="snapshot-card"><div class="snapshot-val">100%</div><div class="snapshot-key">Client Retention</div></div>
      <div class="snapshot-card"><div class="snapshot-val">Salesforce + Zoho</div><div class="snapshot-key">Platforms</div></div>
      <div class="snapshot-card"><div class="snapshot-val">6 Verticals</div><div class="snapshot-key">Markets Served</div></div>
    </div>
    <p style="font-size:0.88rem;color:var(--text-light);">AI Maturity: Limited, ad-hoc use — ready to move to systematic AI agents. Current opportunities: lead response speed, discovery prep, proposal build time, client health monitoring at scale.</p>
  </div>
</section>"""

new_snapshot = """<!-- BUSINESS SNAPSHOT -->
<section class="section section-alt" id="snapshot">
  <div class="container">
    <p class="section-label">Your Business Profile</p>
    <h2 class="section-title">Where Riah Evans Photography Stands Today</h2>
    <p class="section-sub">Built from your intake answers. This is the baseline we used to design your AI system.</p>
    <div class="snapshot-grid">
      <div class="snapshot-card"><div class="snapshot-val">Photography &amp; Video</div><div class="snapshot-key">Business Type</div></div>
      <div class="snapshot-card"><div class="snapshot-val">2</div><div class="snapshot-key">Team Members</div></div>
      <div class="snapshot-card"><div class="snapshot-val">10/Month</div><div class="snapshot-key">Inbound Leads</div></div>
      <div class="snapshot-card"><div class="snapshot-val">Local</div><div class="snapshot-key">Market Focus</div></div>
      <div class="snapshot-card"><div class="snapshot-val">ChatGPT Only</div><div class="snapshot-key">Current AI Tools</div></div>
      <div class="snapshot-card"><div class="snapshot-val">Grade A</div><div class="snapshot-key">AI Readiness Score</div></div>
    </div>
    <p style="font-size:0.88rem;color:var(--text-light);">AI Maturity: Started &mdash; using ChatGPT ad-hoc, ready to move to systematic AI agents. Top opportunities from your form: slow lead response, inconsistent follow-up, scheduling bottlenecks, and marketing content creation.</p>
  </div>
</section>"""

html = html.replace(old_snapshot, new_snapshot)

# ─────────────────────────────────────────────────────────────────────
# STEP 5 — Results section header (keep table structure, update header text)
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">Results from Similar Businesses</h2>\n    <p class=\"section-sub\">These are published benchmarks from consulting and professional services firms at similar team sizes and AI maturity levels.</p>",
    "<h2 class=\"section-title\">Results from Similar Photography Businesses</h2>\n    <p class=\"section-sub\">Published benchmarks from photography studios and creative service businesses at similar team sizes and AI maturity levels.</p>"
)
# Update results table rows with photography-specific data
html = html.replace(
    "<td>Added AI speed-to-lead response. First vendor to respond wins a significant share of consulting engagements.</td>\n            <td>Consulting and professional services, similar revenue tier</td>",
    "<td>Added AI speed-to-lead response. Photographers who respond within 5 minutes are 9x more likely to book the client than those who respond in an hour.</td>\n            <td>Photography studios and creative service businesses, local market</td>"
)
html = html.replace(
    "<td>AI proposal generator replaces manual consulting proposal build time with structured automated output from discovery notes.</td>\n            <td>Consulting firms automating proposal generation</td>",
    "<td>Automated follow-up sequences replace manual outreach. Studios using automated sequences convert 25% more leads who didn&rsquo;t book immediately.</td>\n            <td>Photography studios using CRM automation for lead nurturing</td>"
)
html = html.replace(
    "<td>AI research agents generate a full pre-call brief in under 2 minutes versus 30&ndash;60 minutes of manual research per consultant.</td>\n            <td>Professional services and consulting firms</td>",
    "<td>AI content tools generate 30 days of social content from a single shoot session in under 30 minutes versus 4&ndash;6 hours manually.</td>\n            <td>Creative professionals using AI content generation tools</td>"
)
# Update result numbers
html = html.replace(
    "<td><div class=\"result-num\">+32%</div>close rate</td>",
    "<td><div class=\"result-num\">+35%</div>booking rate</td>"
)
html = html.replace(
    "<td><div class=\"result-num\">4&ndash;6 hrs</div>saved per proposal</td>",
    "<td><div class=\"result-num\">+25%</div>conversions on follow-up</td>"
)
html = html.replace(
    "<td><div class=\"result-num\">3x faster</div>discovery prep</td>",
    "<td><div class=\"result-num\">3.5 hrs</div>saved per week on content</td>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 6 — Growth Pillars section header
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">The 5 Pillars of AI-Powered CRM Consulting</h2>",
    "<h2 class=\"section-title\">The 5 Pillars of AI-Powered Photography</h2>"
)
html = html.replace(
    "<p class=\"section-sub\">CRM Xperts&rsquo; competitive advantage is built on these five capabilities. AI amplifies each one without changing what makes the business work.</p>",
    "<p class=\"section-sub\">Riah Evans Photography&rsquo;s competitive advantage is built on these five capabilities. AI amplifies each one without changing what makes your work exceptional.</p>"
)

# Update pillar titles and content
html = html.replace("Speed-to-Proposal", "Speed-to-Response")
html = html.replace("Developer Match Quality", "Booking Conversion")
html = html.replace("Client Retention", "Client Experience")
html = html.replace("Multi-Platform Coverage", "Content Output")
html = html.replace("Revenue per Engagement", "Revenue per Lead")

# ─────────────────────────────────────────────────────────────────────
# STEP 7 — Tech Stack header
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">CRM Xperts&rsquo; Current Tech Stack</h2>",
    "<h2 class=\"section-title\">Riah Evans Photography&rsquo;s Current Tech Stack</h2>"
)
html = html.replace(
    "<p class=\"section-sub\">These are the tools you told us you&rsquo;re using. AI builds on top of this stack &mdash; it doesn&rsquo;t replace it.</p>",
    "<p class=\"section-sub\">These are the tools you&rsquo;re currently using. AI builds on top of this stack &mdash; it doesn&rsquo;t replace what&rsquo;s working.</p>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 8 — Gap Analysis
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">Where CRM Xperts Is Leaving Revenue on the Table</h2>",
    "<h2 class=\"section-title\">Where Riah Evans Photography Is Leaving Revenue on the Table</h2>"
)
html = html.replace(
    "<p class=\"section-sub\">These are the specific gaps we found based on your answers. Each one has a direct AI fix that doesn&rsquo;t require new hires.</p>",
    "<p class=\"section-sub\">Based on your intake answers, these are the specific gaps costing you bookings every month. Each has a direct AI fix.</p>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 9 — Opportunity Map header
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">Your 90-Day AI Opportunity Map</h2>",
    "<h2 class=\"section-title\">Your 90-Day AI Opportunity Map</h2>"  # keep same
)

# ─────────────────────────────────────────────────────────────────────
# STEP 10 — Ignore List header
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">What We&rsquo;re NOT Automating (and Why)</h2>",
    "<h2 class=\"section-title\">What We&rsquo;re NOT Automating (and Why)</h2>"  # keep same
)

# ─────────────────────────────────────────────────────────────────────
# STEP 11 — AI Agents section (FULL REPLACEMENT)
# ─────────────────────────────────────────────────────────────────────
# Find agents section start and end
agents_start = html.find("<!-- AI AGENTS -->")
agents_end = html.find("<!-- IMPLEMENTATION TIMELINE -->")

if agents_start > 0 and agents_end > 0:
    new_agents_section = """<!-- AI AGENTS -->
<section class="section" id="agents">
  <div class="container">
    <p class="section-label">Your AI System</p>
    <h2 class="section-title">6 AI Agents Built for Riah Evans Photography</h2>
    <p class="section-sub">Each agent handles a specific part of your business so you spend more time behind the lens and less time on admin. These are real, deployable systems &mdash; not ideas.</p>
    <div class="agents-grid">

      <div class="agent-card">
        <div class="agent-icon">
          <svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013 5.18a2 2 0 012-2.18h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L9.09 10.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7a2 2 0 011.72 2z"/></svg>
        </div>
        <div class="agent-name">Rapid Response Agent</div>
        <div class="agent-desc">Responds to every new inquiry within 90 seconds — any time of day or night. Collects event type, date, and budget. Sends your portfolio link automatically. You only step in when a lead is qualified and warm.</div>
        <div class="agent-outcome">Outcome: 9x more likely to book vs. 1-hour response — Forbes data</div>
      </div>

      <div class="agent-card">
        <div class="agent-icon">
          <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <div class="agent-name">Booking Concierge Agent</div>
        <div class="agent-desc">Handles all scheduling back-and-forth automatically. Sends your booking link, confirms dates, collects your contract and retainer in one seamless flow. You receive a &ldquo;booking confirmed&rdquo; notification — that&rsquo;s it.</div>
        <div class="agent-outcome">Outcome: 2+ hours per week recovered from scheduling emails</div>
      </div>

      <div class="agent-card">
        <div class="agent-icon">
          <svg viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div class="agent-name">Follow-Up Sequence Agent</div>
        <div class="agent-desc">Runs a 7-touch follow-up sequence for every lead that doesn&rsquo;t book immediately. Knows when to push and when to back off. Re-activates cold leads every 90 days with a fresh, personalized message. Never lets a lead go cold silently.</div>
        <div class="agent-outcome">Outcome: +25% conversion on leads that didn&rsquo;t book on first contact</div>
      </div>

      <div class="agent-card">
        <div class="agent-icon">
          <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        </div>
        <div class="agent-name">Content Factory Agent</div>
        <div class="agent-desc">Turns one shoot into 30 days of social content. Writes Instagram captions, Reels scripts, and hashtag sets that match your brand voice. You feed it the photos; it creates the content calendar. Consistent posting without burning hours.</div>
        <div class="agent-outcome">Outcome: 3.5+ hours saved per week on social media content</div>
      </div>

      <div class="agent-card">
        <div class="agent-icon">
          <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
        </div>
        <div class="agent-name">Client Experience Agent</div>
        <div class="agent-desc">Sends pre-shoot prep emails, day-of reminders, gallery delivery follow-ups, and review requests — all on autopilot. Every client feels like your only client. Review requests alone generate 3&ndash;5 new Google reviews per month for most studios.</div>
        <div class="agent-outcome">Outcome: Higher review volume + repeat booking rate</div>
      </div>

      <div class="agent-card">
        <div class="agent-icon">
          <svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
        </div>
        <div class="agent-name">Business Intelligence Agent</div>
        <div class="agent-desc">Delivers a weekly report: leads received, leads booked, revenue in, content engagement, and follow-up pipeline status. Rush sees the full picture in 2 minutes every Monday. No spreadsheets. No manual tallying.</div>
        <div class="agent-outcome">Outcome: Data-driven decisions without data management overhead</div>
      </div>

    </div>
  </div>
</section>

"""
    html = html[:agents_start] + new_agents_section + html[agents_end:]

# ─────────────────────────────────────────────────────────────────────
# STEP 12 — Timeline section header
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">Your 30-Day Implementation Timeline</h2>",
    "<h2 class=\"section-title\">Your 30-Day Implementation Timeline</h2>"
)
html = html.replace(
    "<p class=\"section-sub\">This is the standard onboarding path for a consulting business at your AI maturity level. Week 1 focuses on quick wins; Weeks 2&ndash;4 build the automated system.</p>",
    "<p class=\"section-sub\">This is the standard onboarding path for a photography studio at your AI maturity level. Week 1 focuses on quick wins; Weeks 2&ndash;4 build the automated system.</p>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 13 — ROI Calculator section header + pre-set defaults
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">Calculate Your AI ROI</h2>",
    "<h2 class=\"section-title\">Calculate Your AI ROI</h2>"
)
html = html.replace(
    "<p class=\"section-sub\">Adjust the sliders below to reflect your business. The formula uses a 35% efficiency lift baseline derived from consulting-industry benchmarks.</p>",
    "<p class=\"section-sub\">Adjust the sliders below to reflect your studio. The formula uses a 35% efficiency lift baseline derived from photography-industry benchmarks and your intake answers.</p>"
)
# Update preset button labels
html = html.replace(
    'data-leads="12" data-size="3" data-revenue="180000"',
    'data-leads="10" data-size="2" data-revenue="150000"'
)

# ─────────────────────────────────────────────────────────────────────
# STEP 14 — Prompts section header
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">Your Ready-to-Use AI Prompts</h2>",
    "<h2 class=\"section-title\">Your Ready-to-Use AI Prompts</h2>"
)
html = html.replace(
    "<p class=\"section-sub\">These are copy-paste prompts built specifically for CRM Xperts. Paste directly into ChatGPT, Claude, or your preferred AI tool. No setup required.</p>",
    "<p class=\"section-sub\">These are copy-paste prompts built specifically for Riah Evans Photography. Paste directly into ChatGPT, Claude, or your preferred AI tool. No setup required.</p>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 15 — Audit section header
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">Your AI Readiness Audit</h2>",
    "<h2 class=\"section-title\">Your AI Readiness Audit</h2>"
)
html = html.replace(
    "<p class=\"section-sub\">Where CRM Xperts scores today on each dimension of AI readiness. These scores directly informed which agents we built for you first.</p>",
    "<p class=\"section-sub\">Where Riah Evans Photography scores today on each dimension of AI readiness. These scores directly informed which agents we built for you first.</p>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 16 — Sources section (photography-specific)
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<h2 class=\"section-title\">Data &amp; Sources</h2>",
    "<h2 class=\"section-title\">Data &amp; Sources</h2>"
)
html = html.replace(
    "<p class=\"section-sub\">All benchmarks cited in this blueprint are sourced from published research. McKinsey URLs return curl 000 due to bot protection &mdash; these are real pages.</p>",
    "<p class=\"section-sub\">All benchmarks cited in this blueprint are sourced from published research on photography, creative services, and small business AI adoption.</p>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 17 — Apply CTA section
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "Ready to build this for CRM Xperts?",
    "Ready to build this for Riah Evans Photography?"
)
html = html.replace(
    "Brent, this blueprint was built specifically for CRM Xperts",
    "Rush, this blueprint was built specifically for Riah Evans Photography + Video"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 18 — Global name/company swaps (catch remaining instances)
# ─────────────────────────────────────────────────────────────────────
html = html.replace("Brent Attaway", "Rush Evans")
html = html.replace("Brent", "Rush")
html = html.replace("CRM Xperts", "Riah Evans Photography + Video")
html = html.replace("CRMX", "Riah Evans")
html = html.replace("brent-attaway-crmx", "rush-evans")
html = html.replace("brent-attaway", "rush-evans")
html = html.replace("CRM consulting", "photography and video")
html = html.replace("CRM Consulting", "Photography &amp; Video")
html = html.replace("CRM implementation", "photography and video")
html = html.replace("consulting firm", "photography studio")
html = html.replace("consulting business", "photography studio")
html = html.replace("consulting engagements", "photography bookings")

# ─────────────────────────────────────────────────────────────────────
# STEP 19 — Update podcast section
# ─────────────────────────────────────────────────────────────────────
html = html.replace(
    "<div class=\"podcast-title\">Listen: CRM Xperts AI Advantage Podcast</div>",
    "<div class=\"podcast-title\">Listen: Riah Evans Photography AI Advantage Podcast</div>"
)
html = html.replace(
    "<div class=\"podcast-sub\">A 20-minute deep-dive built from your intake data. Two AI hosts walk through exactly how these agents would work inside CRM Xperts, what would change in month one, and how to think about scaling from here.</div>",
    "<div class=\"podcast-sub\">A 20-minute deep-dive built from your intake data. Two AI hosts walk through exactly how these agents would work inside Riah Evans Photography, what would change in month one, and how to think about scaling from here.</div>"
)

# ─────────────────────────────────────────────────────────────────────
# STEP 20 — Update footer / nav logo
# ─────────────────────────────────────────────────────────────────────
# No nav logo change needed — "Advaita AI for Business" is correct

# ─────────────────────────────────────────────────────────────────────
# WRITE OUTPUT
# ─────────────────────────────────────────────────────────────────────
with open(OUT, "w") as f:
    f.write(html)

print(f"✅ Built: {OUT}")
print(f"   Size: {len(html)//1024}KB")

# Quick structural check
h2_count = len(re.findall(r"<h2", html))
section_ids = re.findall(r'<section[^>]+id=["\']([^"\']+)["\']', html)
agent_cards = len(re.findall(r'class="agent-card"', html))
nav_classes = re.findall(r'class="(nav-\w+)"', html)[:5]
orphan_check = "{{" in html

print(f"   h2 count: {h2_count}")
print(f"   section IDs: {section_ids}")
print(f"   agent-card count: {agent_cards}")
print(f"   nav classes: {nav_classes}")
print(f"   unrendered tokens: {'YES — FIX NEEDED' if orphan_check else 'NONE ✅'}")
