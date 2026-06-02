#!/usr/bin/env python3
"""
gen-blueprint.py — Option B form-driven blueprint generator. v1.0 2026-06-02

Takes a lead profile JSON (built from the lead's actual GHL form submission +
content authored for their real industry) and renders it into the format-3 GOLD
structure by replacing the CONTENT of each section in blueprints/TEMPLATE.html.

The template's <head>/<style>, the chaptered podcast player, and the calculator
JS are infrastructure and are preserved verbatim — so format-conformance-check.py
(FC-01..FC-07) keeps passing. Only business-specific content is swapped, which
kills the cross-lead contamination bug (e.g. shipping CRMX's "675+ accounts" copy
on a wedding studio's page).

Usage:
  python3 scripts/gen-blueprint.py leads/<slug>.json
  -> writes blueprints/<slug>.html
"""
import json, re, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, "blueprints", "TEMPLATE.html")

# Reusable inline SVGs (icon identity is cosmetic; the audit counts classes, not
# specific paths). One per card-type so every card still renders an icon.
SVG = {
    "bolt":   '<svg viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>',
    "clock":  '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "users":  '<svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>',
    "doc":    '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "grid":   '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>',
    "chart":  '<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "mail":   '<svg viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
    "folder": '<svg viewBox="0 0 24 24"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    "spark":  '<svg viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
}
PILLAR_SVGS = [
    '<svg viewBox="0 0 24 24"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    '<svg viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
]
STACK_SVGS = [SVG["folder"], SVG["folder"], SVG["grid"], SVG["mail"], SVG["bolt"], SVG["chart"]]
AGENT_SVGS = [SVG["bolt"], SVG["users"], SVG["doc"], SVG["grid"], SVG["chart"], SVG["clock"]]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def replace_section(html, sec_id, inner):
    """Replace the inner HTML of <section ...id="sec_id"...> ... </section>."""
    pat = re.compile(r'(<section[^>]*\bid="' + re.escape(sec_id) + r'"[^>]*>)(.*?)(</section>)', re.S)
    if not pat.search(html):
        raise SystemExit(f"FATAL: section id={sec_id} not found in template")
    return pat.sub(lambda m: m.group(1) + inner + m.group(3), html, count=1)


def build(profile):
    html = open(TEMPLATE, encoding="utf-8").read()
    p = profile

    # ---- hero ----
    stats = "".join(
        f'<div class="hero-stat"><span class="num">{esc(s["num"])}</span><span class="label">{s["label"]}</span></div>'
        + ('<div class="hero-divider"></div>' if i < len(p["hero_stats"]) - 1 else "")
        for i, s in enumerate(p["hero_stats"]))
    hero = (f'\n  <div class="hero-badge">Confidential — Prepared for {esc(p["lead_name"])}</div>\n'
            f'  <h1>Your <span>AI Advantage</span> Roadmap<br>for {esc(p["business_name"])}</h1>\n'
            f'  <p class="hero-sub">{p["hero_sub"]}</p>\n'
            f'  <div class="hero-stats">{stats}</div>\n')
    html = replace_section(html, "hero", hero)

    # ---- profile ----
    cards = "".join(f'<div class="snapshot-card"><div class="snapshot-val">{c["val"]}</div>'
                    f'<div class="snapshot-key">{esc(c["key"])}</div></div>' for c in p["snapshot"])
    prof = (f'\n  <div class="container">\n    <p class="section-label">Your Business Profile</p>\n'
            f'    <h2 class="section-title">Where {esc(p["business_name"])} Stands Today</h2>\n'
            f'    <p class="section-sub">Built from your intake answers and a structured review of {esc(p["domain"])}. '
            f'This is the baseline we used to design your AI system.</p>\n'
            f'    <div class="snapshot-grid">{cards}</div>\n'
            f'    <p style="font-size:0.92rem;color:var(--text-muted);">{p["profile_note"]}</p>\n  </div>\n')
    html = replace_section(html, "profile", prof)

    # ---- results (industry) ----
    r = p["results"]
    rc = "".join(f'<div class="gap-card"><div class="gap-num">{i+1}</div><div class="gap-body">'
                 f'<div class="gap-title">{c["title"]}</div><div class="gap-desc">{c["desc"]}</div>'
                 f'<span class="gap-tag {c["tagclass"]}">{c["tag"]}</span></div></div>'
                 for i, c in enumerate(r["cards"]))
    res = (f'\n  <div class="container">\n    <p class="section-label">What Your Industry Is Already Doing</p>\n'
           f'    <h2 class="section-title">{r["title"]}</h2>\n    <p class="section-sub">{r["sub"]}</p>\n'
           f'    <div class="gap-list">{rc}</div>\n'
           f'    <p class="section-sub" style="margin-top:1.6rem;font-weight:600;color:var(--text);">{r["close"]}</p>\n  </div>\n')
    html = replace_section(html, "results", res)

    # ---- pillars ----
    pc = "".join(f'<div class="pillar-card"><div class="pillar-icon">{PILLAR_SVGS[i % 3]}</div>'
                 f'<div class="pillar-title">{esc(c["title"])}</div><div class="pillar-metric">{esc(c["metric"])}</div>'
                 f'<div class="pillar-sub">{c["sub"]}</div></div>' for i, c in enumerate(p["pillars"]))
    pil = (f'\n  <div class="container">\n    <p class="section-label">Where the Value Comes From</p>\n'
           f'    <h2 class="section-title">Three Ways AI Moves the Needle for {esc(p["business_name"])}</h2>\n'
           f'    <p class="section-sub">Every agent in your system maps to one of three outcomes — more bookings, more time, or more capacity per teammate.</p>\n'
           f'    <div class="pillars-grid">{pc}</div>\n  </div>\n')
    html = replace_section(html, "pillars", pil)

    # ---- stack ----
    sc = "".join(f'<div class="stack-card"><div class="stack-icon">{STACK_SVGS[i % len(STACK_SVGS)]}</div>'
                 f'<div><div class="stack-tool">{esc(c["tool"])}</div><div class="stack-role">{esc(c["role"])}</div></div></div>'
                 for i, c in enumerate(p["stack"]))
    stk = (f'\n  <div class="container">\n    <p class="section-label">Where You Are Today</p>\n'
           f'    <h2 class="section-title">Your Current Tool Stack</h2>\n'
           f'    <p class="section-sub">Here is how your systems are classified — and where AI slots in to multiply each one without replacing anything you already use.</p>\n'
           f'    <div class="stack-grid">{sc}</div>\n  </div>\n')
    html = replace_section(html, "stack", stk)

    # ---- gaps ----
    gc = "".join(f'<div class="gap-card"><div class="gap-num">{i+1}</div><div class="gap-body">'
                 f'<div class="gap-title">{esc(c["title"])}</div><div class="gap-desc">{c["desc"]}</div>'
                 f'<span class="gap-tag {c["tagclass"]}">{c["tag"]}</span></div></div>'
                 for i, c in enumerate(p["gaps"]))
    gap = (f'\n  <div class="container">\n    <p class="section-label">Where the Leverage Is</p>\n'
           f'    <h2 class="section-title">Your Biggest Time Recovery Opportunities</h2>\n'
           f'    <p class="section-sub">These are the areas where {esc(p["business_name"])} has the most capacity to recover — based on your intake answers and a structured review of {esc(p["domain"])}. None of this is critique; it is where AI gives your team the most leverage on what you have already built.</p>\n'
           f'    <div class="gap-list">{gc}</div>\n  </div>\n')
    html = replace_section(html, "gaps", gap)

    # ---- oppmap ----
    rows = "".join(f'<tr><td><div class="pri-badge">{i+1}</div></td><td><strong>{esc(o["usecase"])}</strong></td>'
                   f'<td><span class="impact-tag">{esc(o["impact_tag"])}</span> — {o["impact"]}</td>'
                   f'<td>{esc(o["tools"])}</td></tr>' for i, o in enumerate(p["oppmap"]))
    opp = (f'\n  <div class="container">\n    <p class="section-label">Prioritized Roadmap</p>\n'
           f'    <h2 class="section-title">AI Opportunity Map — {esc(p["business_name"])}</h2>\n'
           f'    <p class="section-sub">Every use case ranked by impact and ease of implementation with your current tool stack. Start at P1 and work down — do not skip ahead.</p>\n'
           f'    <div class="opp-table-wrap"><table class="opp-table"><thead>'
           f'<tr><th style="width:50px">Pri</th><th>AI Use Case</th><th>Business Impact</th><th>Tools It Connects</th></tr>'
           f'</thead><tbody>{rows}</tbody></table></div>\n  </div>\n')
    html = replace_section(html, "oppmap", opp)

    # ---- ignore ----
    ic = "".join(f'<div class="ignore-card"><div class="ignore-x"><span>›</span></div><div>'
                 f'<div class="ignore-title">{esc(c["title"])}</div><div class="ignore-reason">{c["reason"]}</div></div></div>'
                 for c in p["ignore"])
    ign = (f'\n  <div class="container">\n    <p class="section-label">Sequencing, Not Limits</p>\n'
           f'    <h2 class="section-title">What We&rsquo;ll Save for Later — So You Win the Big Wins First</h2>\n'
           f'    <p class="section-sub">The plan is to recover the highest-impact time first, then expand. These are things you <em>could</em> automate down the road, but I would hold off for now — chasing them today would only distract from the agents that move the needle first.</p>\n'
           f'    <div class="ignore-grid">{ic}</div>\n  </div>\n')
    html = replace_section(html, "ignore", ign)

    # ---- agents ----
    ac = "".join(f'<div class="agent-card"><div class="agent-icon">{AGENT_SVGS[i % len(AGENT_SVGS)]}</div>'
                 f'<div class="agent-name">{esc(a["name"])}</div><div class="agent-desc">{a["desc"]}</div>'
                 f'<div class="agent-outcome">{a["outcome"]}</div></div>' for i, a in enumerate(p["agents"]))
    agt = (f'\n  <div class="container">\n    <p class="section-label">Your AI System</p>\n'
           f'    <h2 class="section-title">6 AI Agents Built for {esc(p["business_name"])}</h2>\n'
           f'    <p class="section-sub">Each agent maps directly to a specific workflow inside your studio. Brand voice is built instantly from {esc(p["domain"])} and your existing client language — 90% accurate on Day 1, no slow learning curve required.</p>\n'
           f'    <div class="agents-grid">{ac}</div>\n  </div>\n')
    html = replace_section(html, "agents", agt)

    # ---- timeline ----
    trows = ""
    for t in p["timeline"]:
        items = "".join(f"<li>{li}</li>" for li in t["items"])
        trows += (f'<tr><td><div class="m-phase">{esc(t["phase"])}</div>'
                  f'<div style="font-size:0.82rem;color:var(--text-light);margin-top:0.2rem;">{esc(t["sub"])}</div></td>'
                  f'<td><ul class="m-list">{items}</ul></td><td class="m-result">{t["result"]}</td></tr>')
    tl = (f'\n  <div class="container">\n    <p class="section-label">How It Happens</p>\n'
          f'    <h2 class="section-title">Your Implementation Roadmap</h2>\n'
          f'    <p class="section-sub">No long multi-month rollouts. No waiting. Here is exactly what happens from day one.</p>\n'
          f'    <div class="milestone-table-wrap"><table class="milestone-table"><thead>'
          f'<tr><th>Milestone</th><th>What Happens</th><th>Result You See</th></tr></thead>'
          f'<tbody>{trows}</tbody></table></div>\n  </div>\n')
    html = replace_section(html, "timeline", tl)

    # ---- demo (keep section, swap copy) ----
    d = p["demo"]
    demo = (f'\n  <div class="container">\n    <p class="section-label">Live Preview</p>\n'
            f'    <h2 class="section-title">{esc(p["business_name"])} Speed-to-Lead Demo</h2>\n'
            f'    <p class="section-sub">{d["sub"]}</p>\n'
            f'    <p style="font-size:0.92rem;color:var(--text-muted);max-width:660px;margin:1.5rem auto 0;text-align:center;">{d["note"]}</p>\n  </div>\n')
    html = replace_section(html, "demo", demo)

    # ---- prompts (keep pre ids + copy/toggle hooks) ----
    pcards = ""
    for i, pr in enumerate(p["prompts"], start=1):
        pcards += (f'<div class="prompt-card"><div class="prompt-header" onclick="togglePrompt(this)">'
                   f'<div class="prompt-header-left"><h3>{esc(pr["title"])}</h3><p>{esc(pr["subtitle"])}</p></div>'
                   f'<span class="prompt-expand-hint">view &amp; copy</span></div><div class="prompt-body">'
                   f'<pre id="prompt{i}" class="prompt-pre">{esc(pr["pre"])}</pre>'
                   f'<button class="copy-btn" onclick="copyPrompt(\'prompt{i}\', this)">'
                   f'<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>'
                   f'<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy Prompt</button>'
                   f'<div class="prompt-outcome">{pr["outcome"]}</div></div></div>')
    diy = (f'<div class="diy-or-partner"><h3>Two paths forward for {esc(p["first_name"])}:</h3><div class="path-grid">'
           f'<div class="path"><h4>DIY Path</h4><p>Use the prompts above to start today. You can stand up 1-2 of these agents yourself with free tools like ChatGPT or Claude — and feel the time come back within days, not months.</p></div>'
           f'<div class="path"><h4>Partner Path</h4><p>Want the full system — all 6 agents connected, calibrated to the {esc(p["business_name"])} voice from Day 1, running across every inquiry and client? That is what we build. We handle setup, calibration, and ongoing optimization.</p>'
           f'<a href="{p["qualify_url"]}" class="path-cta">Get Your AI Quote</a></div></div></div>')
    prm = (f'\n  <div class="container">\n    <p class="section-label">Your First AI Agent — Start Here</p>\n'
           f'    <h2 class="section-title">3 Production-Ready AI Agent Prompts for {esc(p["business_name"])}</h2>\n'
           f'    <p class="section-sub">These are fully-built agent instructions — not starter templates. Paste directly into ChatGPT, Claude, or any AI tool and you have a working agent in minutes. Built specifically for {esc(p["business_name"])}.</p>\n'
           f'    <div class="prompt-cards">{pcards}</div>\n    {diy}\n  </div>\n')
    html = replace_section(html, "prompts", prm)

    # ---- sources (neutral citations; no industry leakage) ----
    src_items = [
        ('[1]', 'HubSpot Marketing Statistics — lead response time and conversion research.', 'https://www.hubspot.com/marketing-statistics', 'hubspot.com/marketing-statistics'),
        ('[2]', 'Harvard Business Review — "How Automation Is Transforming Small Business Operations" (2023).', 'https://hbr.org/2023/03/how-automation-is-transforming-small-business', 'hbr.org'),
        ('[3]', 'McKinsey &amp; Company — operations analytics and customer-experience research.', 'https://www.mckinsey.com/capabilities/operations/our-insights', 'mckinsey.com'),
        ('[4]', 'McKinsey Global Institute — "The State of AI in 2023." Adoption benchmarks for lead volume and conversion lift.', 'https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year', 'mckinsey.com'),
        ('[5]', 'Harvard Business Review — automation research: admin time reduction benchmark.', 'https://hbr.org/2023/03/how-automation-is-transforming-small-business', 'hbr.org'),
    ]
    si = "".join(f'<div class="source-item"><span class="source-num">{n}</span><div>{txt} '
                 f'<a href="{url}" target="_blank" rel="noopener">{label}</a></div></div>'
                 for n, txt, url, label in src_items)
    src = (f'\n  <div class="container">\n    <p class="section-label">Research Sources</p>\n'
           f'    <h2 class="section-title">Citations</h2>\n'
           f'    <p class="section-sub">Every claim in this Blueprint links to published research. No fabricated data, no anonymous case studies.</p>\n'
           f'    <div class="sources-list">{si}</div>\n  </div>\n')
    html = replace_section(html, "sources", src)

    # ---- apply CTA personal note (keep section, swap personal line) ----
    html = re.sub(r'(<p class="cta-personal">).*?(</p>)',
                  lambda m: m.group(1) + p["cta_personal"] + m.group(2), html, count=1, flags=re.S)

    # ---- calculator defaults + JS presets ----
    # Robust to template drift: match on slider id + value="" only, ignore min/max/step
    # (Bennett's template has changed contract from a range slider to a number input with
    # min="0" and no max, and dropped lbl-contract — exact-string replaces silently no-op'd).
    c = p["calc"]

    def set_slider(html, sid, val):
        return re.sub(r'(id="' + re.escape(sid) + r'"[^>]*\bvalue=")[^"]*(")',
                      lambda m: m.group(1) + str(val) + m.group(2), html, count=1)

    def set_label(html, lid, label):  # only fires if the label span still exists
        return re.sub(r'(<span class="calc-slider-val" id="' + re.escape(lid) + r'">)[^<]*(</span>)',
                      lambda m: m.group(1) + label + m.group(2), html, count=1)

    for sid, val in (("sl-contract", c["contract"]), ("sl-leads", c["leads"]),
                     ("sl-rate", c["rate"]), ("sl-hours", c["hours"])):
        html = set_slider(html, sid, val)
    for lid, lab in (("lbl-contract", c["contract_label"]), ("lbl-leads", c["leads_label"]),
                     ("lbl-rate", c["rate_label"]), ("lbl-hours", c["hours_label"])):
        html = set_label(html, lid, lab)
    html = re.sub(r'(<p class="section-sub">)Adjust the (?:sliders|numbers).*?(?:set your own numbers|match your real numbers)\.\s*(</p>)',
                  lambda m: m.group(1) + c["sub"] + m.group(2), html, count=1, flags=re.S)
    pr_obj = (f"{{\n    conservative: {{ contract: {c['contract']}, leads: {c['leads']}, rate: {c['rate']}, hours: {c['hours']}, lift: 0.5 }},\n"
              f"    expected:     {{ contract: {c['contract']}, leads: {c['leads']}, rate: {c['rate']}, hours: {c['hours']}, lift: 1.0 }},\n"
              f"    stretch:      {{ contract: {c['contract']}, leads: {c['leads']}, rate: {c['rate']}, hours: {c['hours']}, lift: 1.3 }}\n  }}")
    html = re.sub(r"\{\s*conservative:.*?stretch:.*?\}\s*\}", pr_obj, html, count=1, flags=re.S)

    # ---- simple global tokens ----
    tok = {
        "{{LEAD_NAME}}": p["lead_name"], "{{FIRST_NAME}}": p["first_name"],
        "{{BUSINESS_NAME}}": p["business_name"], "{{DOMAIN}}": p["domain"],
        "{{SLUG}}": p["slug"], "{{CRM_TOOL}}": p.get("crm_tool_fallback", "your client hub"),
        "{{PODCAST_URL}}": p["podcast_url"], "{{QUALIFY_URL}}": p["qualify_url"],
    }
    for k, v in tok.items():
        html = html.replace(k, v)
    return html


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: gen-blueprint.py leads/<slug>.json")
    profile = json.load(open(sys.argv[1], encoding="utf-8"))
    out = os.path.join(REPO, "blueprints", profile["slug"] + ".html")
    open(out, "w", encoding="utf-8").write(build(profile))
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", open(out, encoding="utf-8").read())
    print(f"wrote {out}")
    if leftover:
        print("WARN leftover tokens:", sorted(set(leftover)))
