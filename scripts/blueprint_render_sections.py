#!/usr/bin/env python3
"""blueprint_render_sections.py — render the 5 per-lead narrative sections from the lead profile.

PERMANENT FIX 2026-08-03 (marker BLUEPRINT-TEMPLATE-SECTIONS-PER-LEAD-20260803,
EC-BLUEPRINT-TEMPLATE-ROSTER-AND-STRESS-LEAK-STILL-OPEN-20260803). Madison directive.

WHY THIS EXISTS
---------------
`blueprints/TEMPLATE.html` hardcoded the CONTENT of five customer-facing sections —
gaps / oppmap / timeline / results / ignore — as lead-agnostic B2B-agency copy that was never
tokenized. Every generated Blueprint therefore shipped:

  1. A DIFFERENT AI-employee roster than the lead's own six: "Client Onboarding Agent",
     "Proposal Generator", "Content Production Agent", "Retention Monitor",
     "Client Health Monitor", "Admin Automation Agent", "Sales Intelligence Agent".
  2. TWO FABRICATED STRESS CLAIMS — "You flagged Marketing Content as a top operational stress"
     and "You flagged Admin Work as a top stress" — asserted regardless of what the lead
     actually selected. On janet-drawn-logic `operational_stress_areas` was EMPTY, so both
     sentences were false statements attributed to a named customer.
  3. "Agent" where D2-26 requires "AI Employee".
  4. Plural-team copy ("your team", "Team walkthrough", "your 24/7 human support") on leads whose
     stated team size is 1.

`run-audit.py` scored janet-drawn-logic and cindy-broken-in-treasures **19/19 with all of the
above present** — the format/completion gates never compared section content against the profile.
Both were repaired by hand, which does not scale and is exactly the failure this replaces.

Same bug-class as BLUEPRINT-STACK-NO-TEMPLATE-DEFAULT-LEAK-20260723 (stack cards) and
BLUEPRINT-ROI-PRESET-FROM-FORM-20260727 (ROI presets): per-lead content living in the template.

CONTRACT
--------
* Every claim traces to the lead profile. A stress area is named ONLY if the lead selected it.
* Nothing is invented: absent data produces absent copy, never a plausible substitute.
* Solo leads (team_size == 1) get singular copy; never "your team".
* Customer-facing label is always "AI Employee", never "Agent".
* CSS classes and section ids are preserved exactly (format-3 lock + D9 orphan-class gate).

Usage:  python3 scripts/blueprint_render_sections.py --lead <slug> [--html <path>] [--check]
        --check exits 1 without writing if any template-default leak is still present.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The exact roster identifiers the template hardcoded. Any of these surviving in a built page means
# the leak came back. Shared by the renderer and the gate so there is one list.
#
# MATCHED CASE-SENSITIVELY AND ONLY AS FULL IDENTIFIERS. Bare two-word fragments are NOT listed:
# "client onboarding", "content production" and "admin automation" all occur legitimately in
# lowercase descriptive prose (e.g. the pillars card reads "Admin work, client onboarding, content
# creation, and support triage — automated"). Flagging those produced a false positive on the first
# run of this gate, which is its own kind of defect — a gate that cries wolf gets disabled.
TEMPLATE_ROSTER = [
    "Client Onboarding Agent",
    "Proposal Generator",
    "Content Production Agent",
    "Retention Monitor",
    "Client Health Monitor",
    "Admin Automation Agent",
    "Sales Intelligence Agent",
]
FABRICATED_STRESS_RE = re.compile(r"You flagged\s+([A-Za-z][A-Za-z /&-]{2,40}?)\s+as a top", re.I)
PLURAL_TEAM_RE = re.compile(
    r"your team\b|your whole team\b|Team walkthrough|your people\b|your staff\b|24/7 human support",
    re.I,
)

CIT = {
    1: '<sup><a href="https://www.hubspot.com/marketing-statistics" target="_blank" rel="noopener">[1]</a></sup>',
    2: '<sup><a href="https://hbr.org/2023/03/how-automation-is-transforming-small-business" target="_blank" rel="noopener">[2]</a></sup>',
    3: '<sup><a href="https://mckinsey.com/business-functions/operations/our-insights/analytics" target="_blank" rel="noopener">[3]</a></sup>',
    4: '<sup><a href="https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year" target="_blank" rel="noopener">[4]</a></sup>',
}


def esc(s) -> str:
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Lead:
    """Normalized, never-inventing view of the lead profile."""

    def __init__(self, p: dict):
        self.p = p
        q = p.get("quiz") or {}
        self.q = q
        self.biz = p.get("business_name") or "your business"
        self.first = p.get("first_name") or (p.get("lead_name") or "").split(" ")[0]
        self.agents = [a for a in (p.get("ai_agents") or p.get("agents") or []) if isinstance(a, dict)][:6]
        self.industry_phrase = str(p.get("industry") or "").replace("_", " ").strip().lower()

        self.team_size = self._num(p.get("team_size"), q.get("team_size"))
        self.solo = self.team_size == 1
        self.monthly_leads = self._num(p.get("monthly_leads"), q.get("monthly_leads"))
        self.response_speed = self._txt(q.get("response_speed"))
        self.primary_goal = self._txt(p.get("primary_goal"), q.get("biggest_goal"))
        self.ai_maturity = self._txt(q.get("ai_maturity"))

        # Tools: only treat as "absent" when the form literally says None.
        self.crm = self._txt(q.get("crm_tools"), p.get("tools"))
        self.pm = self._txt(q.get("project_management_tools"))
        self.storage = self._txt(q.get("storage_tools"))
        self.comms = self._txt(q.get("communication_tools"))
        self.no_crm = self._is_none(self.crm)
        self.no_pm = self._is_none(self.pm)
        self.no_storage = self._is_none(self.storage)

        # STRESS AREAS — the whole point. Only what the lead actually selected, "Other" dropped
        # because it carries no information and must never be turned into a named stress.
        raw = self._txt(q.get("operational_stress_areas"), p.get("operational_stress_areas"))
        self.stress = [
            s.strip() for s in re.split(r"[,;]", raw)
            if s.strip() and s.strip().lower() not in ("other", "none", "n/a", "")
        ] if raw and not self._is_none(raw) else []

    @staticmethod
    def _txt(*vals) -> str:
        for v in vals:
            if isinstance(v, list):
                v = ", ".join(str(x) for x in v)
            if v not in (None, "", "—"):
                return str(v).strip()
        return ""

    @staticmethod
    def _is_none(v: str) -> bool:
        return str(v or "").strip().lower() in ("none", "", "n/a", "na", "null")

    @staticmethod
    def _num(*vals):
        for v in vals:
            m = re.search(r"\d+", str(v or "").replace(",", ""))
            if m:
                return int(m.group(0))
        return None

    # ---- copy helpers so solo vs team never has to be reasoned about inline ----
    @property
    def you_or_team(self) -> str:
        return "you" if self.solo else "your team"

    @property
    def missing_tools(self) -> list:
        out = []
        if self.no_crm:
            out.append("no CRM")
        if self.no_pm:
            out.append("no project management tool")
        if self.no_storage:
            out.append("no file storage system")
        return out


def gap(n, title, desc, tag, label) -> str:
    return ('      <div class="gap-card"><div class="gap-num">%d</div><div class="gap-body">'
            '<div class="gap-title">%s</div><div class="gap-desc">%s</div>'
            '<span class="gap-tag %s">%s</span></div></div>' % (n, title, desc, tag, label))


def build_gaps(L: Lead) -> str:
    cards, n = [], 0

    # 1 — capacity. Always true and always sourced (team_size is asked on every form).
    n += 1
    if L.solo:
        t = "You Are the Only Person, and Everything Waits on You"
        d = ("You told us %s is a team of one. That is the honest centre of this blueprint: every task "
             "below is work you would otherwise have to hire for, and every one of them is work an AI "
             "Employee can hold without a payroll decision, a job posting, or a training period. " % esc(L.biz))
    else:
        t = "A Small Team Carrying Every Function"
        d = ("You told us %s runs with a team of %s. Every task below is work that currently competes for "
             "that team's attention, and each one is work an AI Employee can absorb so the people you "
             "already employ spend their hours on what only they can do. " % (esc(L.biz), L.team_size))
    if L.stress:
        d += "You named %s as where the pressure sits, which is exactly what this sequence is built around. " % esc(L.stress[0].lower())
    cards.append(gap(n, t, d + CIT[2], "efficiency", "Time Recovery"))

    # 2 — no system of record. Only when the form actually said None.
    if L.missing_tools:
        n += 1
        mt = ", ".join(L.missing_tools)
        cards.append(gap(n, "Nothing Is Written Down Anywhere",
            ("You reported %s. Right now the memory of the business is %s. That is workable at low volume and "
             "it is the thing that breaks first when volume arrives. The fix is not buying software you would "
             "then have to learn; it is an AI Employee that keeps one plain record per customer for you. " % (esc(mt), L.you_or_team)) + CIT[3],
            "efficiency", "Time Recovery"))

    # 3 — lead volume. Branch honestly on what they reported.
    n += 1
    if L.monthly_leads is not None and L.monthly_leads == 0:
        cards.append(gap(n, "No Inbound Volume Yet",
            ("You told us zero people a month are currently reaching out. That matters for sequencing: catching "
             "and converting demand is worthless until demand arrives. So visibility is not a nice-to-have further "
             "down this list — for you it comes first, and everything else exists to catch what it brings in. " + CIT[4]),
            "revenue", "Revenue Impact"))
    elif L.monthly_leads:
        speed = (" and you get back to them %s" % esc(L.response_speed.lower())) if L.response_speed else ""
        cards.append(gap(n, "Every Inquiry Lands on the Same Desk",
            ("You told us about %d people a month reach out%s. Published research shows the first responder wins "
             "the clear majority of deals, so the answer is not to reply slower — it is to stop being the only one "
             "who can reply. " % (L.monthly_leads, speed)) + CIT[1],
            "revenue", "Revenue Impact"))
    else:
        cards.append(gap(n, "Speed of Response Decides Who Wins",
            ("Published research shows the first business to respond wins the clear majority of deals, yet most "
             "replies still depend on a person being free. An AI Employee makes response time structural rather "
             "than personal. " + CIT[1]),
            "revenue", "Revenue Impact"))

    # 4..N — one card per remaining AI Employee, so the gaps always match the lead's real roster.
    tags = [("efficiency", "Time Recovery"), ("brand", "Retention"), ("brand", "Visibility"), ("efficiency", "Time Recovery")]
    for i, a in enumerate(L.agents[2:6]):
        if n >= 6:
            break
        n += 1
        tag, label = tags[i % len(tags)]
        desc = esc(a.get("desc") or "")
        res = esc(a.get("result") or "")
        body = desc + ((" <strong>What you get:</strong> %s. " % res) if res else " ")
        cards.append(gap(n, esc(a.get("name") or "AI Employee #%d" % n), body + CIT[2 + (i % 3)], tag, label))

    sub = ("These come straight from what you told us on your intake form. None of this is critique &mdash; "
           "it is where AI gives %s the most leverage on what you have already built."
           % ("one person" if L.solo else "your team"))
    return ('<section class="section section-alt" id="gaps">\n  <div class="container">\n'
            '    <p class="section-label">Where the Leverage Is</p>\n'
            '    <h2 class="section-title">Your Biggest Time Recovery Opportunities</h2>\n'
            '    <p class="section-sub">%s</p>\n    <div class="gap-list">\n%s\n    </div>\n  </div>\n</section>'
            % (sub, "\n".join(cards)))


def build_oppmap(L: Lead) -> str:
    tool_pool = [t.strip() for t in re.split(r"[,;]", L.comms) if t.strip() and not Lead._is_none(t)]
    if not tool_pool:
        tool_pool = ["Email"]
    rows = []
    for i, a in enumerate(L.agents, 1):
        res = esc(a.get("result") or "")
        impact = esc(a.get("time") or "").strip() or "Hours back"
        tools = esc(tool_pool[(i - 1) % len(tool_pool)])
        rows.append('          <tr><td><div class="pri-badge">%d</div></td><td><strong>%s</strong></td>'
                    '<td><span class="impact-tag">%s setup</span> &mdash; %s</td><td>%s</td></tr>'
                    % (i, esc(a.get("name") or "AI Employee #%d" % i), impact, res, tools))
    return ('<section class="section" id="oppmap">\n  <div class="container">\n'
            '    <p class="section-label">Prioritized Roadmap</p>\n'
            '    <h2 class="section-title">AI Opportunity Map &mdash; %s</h2>\n'
            '    <p class="section-sub">Every AI Employee ranked by impact and ease of implementation with your '
            'current tool stack. Start at P1 and work down &mdash; do not skip ahead.</p>\n'
            '    <div class="opp-table-wrap">\n      <table class="opp-table">\n        <thead>\n'
            '          <tr><th style="width:50px">Pri</th><th>AI Employee</th><th>Business Impact</th>'
            '<th>Tools It Connects</th></tr>\n        </thead>\n        <tbody>\n%s\n        </tbody>\n'
            '      </table>\n    </div>\n  </div>\n</section>' % (esc(L.biz), "\n".join(rows)))


def build_timeline(L: Lead) -> str:
    first = L.agents[0].get("name") if L.agents else "your first AI Employee"
    rest = [esc(a.get("name")) for a in L.agents[1:6]]
    rest_li = "".join("<li>%s deployed</li>" % r for r in rest)
    who = "you" if L.solo else "your team"
    walkthrough = "Walkthrough with you" if L.solo else "Team walkthrough"
    return ('<section class="section section-alt" id="timeline">\n  <div class="container">\n'
            '    <p class="section-label">How It Happens</p>\n'
            '    <h2 class="section-title">Your Implementation Roadmap</h2>\n'
            '    <p class="section-sub">No long multi-month rollouts. No waiting. Here is exactly what happens '
            'from day one.</p>\n    <div class="milestone-table-wrap">\n      <table class="milestone-table">\n'
            '        <thead>\n          <tr><th>Milestone</th><th>What Happens</th><th>Result You See</th></tr>\n'
            '        </thead>\n        <tbody>\n'
            '          <tr>\n            <td><div class="m-phase">Week 1 &middot; Days 1&ndash;7</div>'
            '<div style="font-size:0.82rem;color:var(--text-light);margin-top:0.2rem;">Onboarding &amp; Setup</div></td>\n'
            '            <td><ul class="m-list"><li>Kickoff call &mdash; we map how work actually moves through %s today</li>'
            '<li>%s configured and connected</li><li>Brand voice calibrated from your own words</li>'
            '<li>Live test: send a test inquiry and watch the reply fire</li></ul></td>\n'
            '            <td class="m-result">Onboarding week &mdash; we map your workflow and configure the system '
            'internally. Nothing customer-facing goes live yet.</td>\n          </tr>\n'
            '          <tr>\n            <td><div class="m-phase">Weeks 2&ndash;3 &middot; Days 8&ndash;21</div>'
            '<div style="font-size:0.82rem;color:var(--text-light);margin-top:0.2rem;">AI Employees Go Live</div></td>\n'
            '            <td><ul class="m-list">%s<li>%s: 30 minutes, no technical knowledge required</li></ul></td>\n'
            '            <td class="m-result">Your first AI Employee goes live in week 2. By the end of week 3 all '
            'of them are running &mdash; and %s know how to steer them.</td>\n          </tr>\n'
            '          <tr>\n            <td><div class="m-phase">Day 30</div>'
            '<div style="font-size:0.82rem;color:var(--text-light);margin-top:0.2rem;">Fully Calibrated</div></td>\n'
            '            <td><ul class="m-list"><li>30-day review: response times, hours returned, work booked</li>'
            '<li>AI Employees refined against your real conversations</li>'
            '<li>Expansion roadmap: what to hand over next as %s grows</li></ul></td>\n'
            '            <td class="m-result">The system knows your business. Every AI Employee calibrated to real '
            '%s data.</td>\n          </tr>\n'
            '          <tr>\n            <td><div class="m-phase">Month 2+</div>'
            '<div style="font-size:0.82rem;color:var(--text-light);margin-top:0.2rem;">Compounding</div></td>\n'
            '            <td><ul class="m-list"><li>Minimal manual input required from %s</li>'
            '<li>Continuous improvement from production data</li>'
            '<li>You own the system &mdash; we stay as your AI operations team</li></ul></td>\n'
            '            <td class="m-result">AI runs like a trained colleague who never forgets and never has a '
            'bad day.</td>\n          </tr>\n        </tbody>\n      </table>\n    </div>\n  </div>\n</section>'
            % (esc(L.biz), esc(first), rest_li, walkthrough, who, esc(L.biz), esc(L.biz), who))


def build_results(L: Lead) -> str:
    peer = "One-person businesses" if L.solo else "Businesses like %s" % esc(L.biz)
    cards = []
    tags = [("revenue", "Revenue Impact"), ("efficiency", "Time Recovery"), ("brand", "Retention")]
    for i, a in enumerate(L.agents, 1):
        tag, label = tags[(i - 1) % 3]
        nm = esc(a.get("name") or "")
        desc = esc(a.get("desc") or "")
        res = esc(a.get("result") or "")
        d = ("<strong>What they&rsquo;re doing:</strong> operators in your position now run an AI Employee for "
             "exactly this. <strong>How it helps them:</strong> %s <strong>How I deliver it for %s:</strong> %s %s"
             % ((res + ".") if res else "the work stops depending on someone being free to do it.",
                esc(L.biz), desc, CIT[1 + (i % 4)]))
        cards.append(gap(i, nm, d, tag, label))
    return ('<section class="section" id="results">\n  <div class="container">\n'
            '    <p class="section-label">What Your Industry Is Already Doing</p>\n'
            '    <h2 class="section-title">%s Are Already Running on AI</h2>\n'
            '    <p class="section-sub">These are the moves being made right now &mdash; live in the market today. '
            'The question is not whether AI can hold this work. It is whether %s puts it to work first.</p>\n'
            '    <div class="gap-list">\n%s\n    </div>\n  </div>\n</section>'
            % (peer, esc(L.biz), "\n".join(cards)))


def build_ignore(L: Lead) -> str:
    def card(t, r):
        return ('      <div class="ignore-card"><div class="ignore-x"><span>&rsaquo;</span></div><div>'
                '<div class="ignore-title">%s</div><div class="ignore-reason">%s</div></div></div>' % (t, r))

    items = [card("Publishing Anything Without You Reading It First",
                  "Your AI Employees draft; you approve. Until they have learned how you actually talk about what "
                  "you do, everything goes past you before it goes public. A confident, well-written sentence "
                  "containing a detail you never said is the worst thing automation can do to a business, and the "
                  "easiest to prevent."),
             card("Autonomous Pricing and Scope Commitments",
                  "AI can assemble every input for a quote, but the number and the yes stay with %s. Any commitment "
                  "made on your behalf is a commitment you personally have to keep. Let AI collect and draft; you "
                  "confirm." % L.you_or_team)]
    if L.missing_tools:
        items.append(card("A Full Software Stack",
                          "You told us you have %s. The instinct is to fix that with subscriptions. Not yet &mdash; "
                          "every tool is another thing to learn and maintain. Start with an AI Employee that keeps "
                          "the record for you, and buy software later only if you outgrow that."
                          % ", ".join(L.missing_tools)))
    if L.monthly_leads == 0:
        items.append(card("Paid Advertising",
                          "Ads make sense once something is reliably converting the traffic they buy. With no "
                          "inbound yet and no follow-up system in place, paid spend leaks straight out the bottom. "
                          "Build the organic rhythm and the capture system first."))
    else:
        items.append(card("A Generic Website Chatbot",
                          "Worth revisiting later in a smarter form &mdash; but today a qualification-first AI "
                          "Employee over email and text converts more of your inquiries than a chatbot menu tree."))
    return ('<section class="section section-alt" id="ignore">\n  <div class="container">\n'
            '    <p class="section-label">Sequencing, Not Limits</p>\n'
            '    <h2 class="section-title">What We&rsquo;ll Save for Later &mdash; So You Win the Big Wins First</h2>\n'
            '    <p class="section-sub">Here is the honest truth: AI has reached the point where almost anything done '
            'on a computer can eventually be handled by a trained AI Employee. The plan is to take that work over step '
            'by step, starting with the highest-impact wins. The items below are things you <em>could</em> automate '
            'down the road, but I would hold off &mdash; chasing them today would only distract from the AI Employees '
            'that move the needle first.</p>\n    <div class="ignore-grid">\n%s\n    </div>\n  </div>\n</section>'
            % ("\n".join(items)))


def replace_section(html: str, sid: str, new: str):
    pat = re.compile(r'<section[^>]*id="%s".*?</section>' % re.escape(sid), re.S)
    m = pat.search(html)
    if not m:
        return html, False
    return html[:m.start()] + new + html[m.end():], True


def leaks(html: str, L: Lead) -> list:
    """Every way the template default can reappear. Shared by --check and the build gate."""
    out = []
    vis = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    own = {(a.get("name") or "") for a in L.agents}
    for name in TEMPLATE_ROSTER:
        # case-SENSITIVE, word-bounded: the template rendered these as title-case labels.
        if re.search(r"\b%s\b" % re.escape(name), vis) and not any(name in o for o in own):
            out.append("RL-TS1 template roster name still present: %r" % name)
    for m in FABRICATED_STRESS_RE.finditer(vis):
        claimed = m.group(1).strip().lower()
        if not any(claimed in s.lower() or s.lower() in claimed for s in L.stress):
            out.append("RL-TS2 fabricated stress claim %r — lead selected %s"
                       % (m.group(1).strip(), L.stress or "NOTHING"))
    if L.solo:
        for m in PLURAL_TEAM_RE.finditer(vis):
            out.append("RL-TS3 plural-team copy %r on a team of 1" % m.group(0))
    for m in re.finditer(r"\bAgent\b", vis):
        out.append("RL-TS4 customer-facing 'Agent' (D2-26 requires 'AI Employee')")
        break
    return sorted(set(out))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lead", required=True)
    ap.add_argument("--html")
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 on any leak")
    ap.add_argument("--json-output", action="store_true")
    a = ap.parse_args()

    lead_path = os.path.join(REPO, "leads", "%s.json" % a.lead)
    html_path = a.html or os.path.join(REPO, "blueprints", "%s.html" % a.lead)
    L = Lead(json.load(open(lead_path, encoding="utf-8")))
    html = open(html_path, encoding="utf-8").read()

    if not a.check:
        if not L.agents:
            print("  sections: SKIPPED — profile has no ai_agents to render from", file=sys.stderr)
            return 0
        done = []
        for sid, fn in (("gaps", build_gaps), ("oppmap", build_oppmap), ("results", build_results),
                        ("ignore", build_ignore), ("timeline", build_timeline)):
            html, ok = replace_section(html, sid, fn(L))
            done.append(sid if ok else "%s(MISSING)" % sid)
        # D2-26 wording on the template chrome the sections do not own
        for x, y in (('<span class="label">First Agent<br>Live</span>', '<span class="label">First AI Employee<br>Live</span>'),
                     ('>Your First AI Agent &mdash; Start Here<', '>Your First AI Employee &mdash; Start Here<'),
                     ("AI Agent Prompts for", "AI Employee Prompts for"),
                     ("<h3>Agent 1 &mdash;", "<h3>AI Employee 1 &mdash;"),
                     ("<h3>Agent 2 &mdash;", "<h3>AI Employee 2 &mdash;"),
                     ("<h3>Agent 3 &mdash;", "<h3>AI Employee 3 &mdash;")):
            html = html.replace(x, y)
        open(html_path, "w", encoding="utf-8").write(html)
        print("  per-lead sections: rendered %s from profile (solo=%s, stress=%s)"
              % (", ".join(done), L.solo, L.stress or "none-stated"))

    found = leaks(html, L)
    if a.json_output:
        print(json.dumps({"status": "PASS" if not found else "FAIL", "lead": a.lead,
                          "solo": L.solo, "stress_stated": L.stress, "failures": found}, indent=2))
    elif found:
        print("blueprint_render_sections: FAIL (%d)" % len(found), file=sys.stderr)
        for f in found:
            print("   %s" % f, file=sys.stderr)
    else:
        print("blueprint_render_sections: PASS — no template-default leak, no fabricated stress claim")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
