#!/usr/bin/env python3
"""convert-research-profile.py — map a research-rich lead profile (Brad/melissa
schema: ai_agents + prompt_1..3 + form facts) into the gen-blueprint.py schema
(billy-bob fixture shape: hero_stats/snapshot/results/pillars/stack/gaps/oppmap/
ignore/agents/timeline/demo/prompts/calc/qualifier_q7_agents).

All substantive copy comes from the researched profile; only structural glue is
templated. Form-verbatim numbers (monthly_leads) are asserted, never derived.

Usage: python3 scripts/convert-research-profile.py <slug>
Rewrites leads/<slug>.json in place (keeps original research keys alongside).
"""
import json, re, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
slug = sys.argv[1]
path = os.path.join(REPO, "leads", f"{slug}.json")
p = json.load(open(path, encoding="utf-8"))

first = p.get("lead_first_name") or p.get("first_name") or p["lead_name"].split()[0]
biz = p["business_name"]
ai = p["ai_agents"][:6]
assert len(ai) == 6, "need exactly 6 researched agents"
stresses = [re.sub(r"<[^>]+>", "", s) for s in (p.get("operational_stresses") or [])]
tools_str = p.get("tools") or ""
leads_n = int(str(p.get("monthly_leads")).replace(",", ""))
contract = int(str(p.get("avg_job_value")).replace("$", "").replace(",", ""))
rate = int(float(p.get("close_rate") or 10))
hours = int(p.get("company_hours") or p.get("roi_hours_saved") or 30)
rev = p.get("annual_revenue_range") or ""
rev_short = rev.split("(")[0].strip() or rev

def first_sentence(t, fallback=""):
    t = re.sub(r"<[^>]+>", "", t or "").strip()
    m = re.match(r"(.{20,180}?[.!?])\s", t + " ")
    return (m.group(1) if m else (t[:160] or fallback)).strip()

def outcome_for(a):
    if a.get("outcome"):
        return a["outcome"]
    sents = re.findall(r"[^.!?]{15,}[.!?]", re.sub(r"<[^>]+>", "", a["desc"]))
    return (sents[-1].strip() if sents else f"{a['name']} working inside your existing stack.")

# stack: parse "Tool (role), Tool (role)" plus trailing slot
stack = []
for m in re.finditer(r"([A-Za-z0-9@.\- ]+?)\s*\(([^)]+)\)", tools_str):
    stack.append({"tool": m.group(1).strip(" ,"), "role": m.group(2).strip().capitalize()})
if not stack:
    for t in re.split(r",\s*", tools_str):
        if t.strip():
            stack.append({"tool": t.strip(), "role": "Current workflow tool"})
stack = stack[:5]
stack.append({"tool": "No AI Layer Yet", "role": "Where the 6 agents slot in — on top of your stack, replacing nothing"})

gap_tags = ["High leverage", "Quick win", "High leverage", "Compounding"]
gaps = [{"title": first_sentence(s).rstrip("."), "desc": re.sub(r"<[^>]+>", "", s), "tag": gap_tags[i % 4], "tagclass": ""}
        for i, s in enumerate(stresses[:4])]
while len(gaps) < 4:
    gaps.append({"title": "Manual admin work absorbs selling hours",
                 "desc": f"Hours that should go to customers go to coordination instead — the agents hand that back to you.",
                 "tag": "Quick win", "tagclass": ""})

oppmap = [{"usecase": a["name"], "impact_tag": "High" if i < 3 else "Medium",
           "impact": first_sentence(a["desc"]),
           "tools": ", ".join(s["tool"] for s in stack[:3])} for i, a in enumerate(ai)]

agents = [{"name": a["name"], "desc": re.sub(r"<[^>]+>", "", a["desc"]),
           "outcome": outcome_for(a), "agent_prompt": re.sub(r"<[^>]+>", "", a.get("agent_prompt", ""))}
          for a in ai]

prompts = []
for i in (1, 2, 3):
    label = p.get(f"prompt_{i}_label") or agents[i - 1]["name"]
    body = p.get(f"prompt_{i}") or ""
    prompts.append({"title": label,
                    "subtitle": first_sentence(body.split("##")[0], f"Copy-paste system prompt for {label}") if body else f"Copy-paste system prompt for {label}",
                    "pre": body,
                    "outcome": outcome_for({"name": label, "desc": agents[i - 1]["desc"]})})

calc_sub = (f"Use these numbers as the {biz} baseline: ${contract:,} average value, {leads_n} monthly leads "
            f"(your form), {rate}% close rate, and {hours} weekly admin hours.")

p.update({
    "domain": p.get("domain") or (p.get("website_url") or p.get("url") or "").replace("https://", "").replace("http://", "").strip("/") or biz,
    "hero_sub": p.get("hero_sub") or f"A practical AI roadmap for {biz} — built from what you told us: {first_sentence(stresses[0]) if stresses else 'protect response speed and reclaim admin hours'} Six agents, your existing tools, no rip-and-replace.",
    "profile_note": p.get("profile_note") or f"{biz} is already operating with enough lead volume ({leads_n}/month, your form) and value per win for AI to pay for itself quickly. The fastest gains are response speed, follow-up, and admin recovery.",
    "cta_personal": p.get("cta_personal") or f"{first}, your best first move is not a giant AI overhaul. It is a focused system that answers new inquiries fast, follows up on every open quote, and gives your week back.",
    "crm_tool_fallback": p.get("crm_tool_fallback") or (stack[0]["tool"] if stack else "your CRM"),
    "hero_stats": p.get("hero_stats") or [
        {"num": str(leads_n), "label": "Monthly leads (your form)"},
        {"num": rev_short or "—", "label": "Annual revenue range (your form)"},
        {"num": "6", "label": f"AI agents designed for {biz}"},
    ],
    "snapshot": p.get("snapshot") or [
        {"val": rev_short or "—", "key": "Annual Revenue (form)"},
        {"val": str(leads_n), "key": "Monthly Leads (form)"},
        {"val": f"${contract:,}", "key": "Avg Value (industry-typical)"},
        {"val": str(p.get("response_speed_label") or "Slow first reply"), "key": "Today's Response Gap"},
    ],
    "results": p.get("results") or {
        "title": f"Operators like you are using automation to protect response time and win-rate.",
        "sub": "The biggest wins are not abstract AI projects. They are practical fixes around the exact stresses your form named.",
        "cards": [{"title": g["title"], "desc": g["desc"], "tag": g["tag"], "tagclass": ""} for g in gaps[:4]],
        "close": f"For {biz}, the fastest path is not replacing your team. It is giving your team an instant first response, systematic follow-up, and fewer admin hours.",
    },
    "pillars": p.get("pillars") or [
        {"title": "Capture", "metric": "Instant first response", "sub": "Every inquiry gets answered and qualified fast."},
        {"title": "Convert", "metric": "No quote goes quiet", "sub": "Follow-up and reactivation run on a system, not memory."},
        {"title": "Operate", "metric": f"~{hours} hrs/week back", "sub": "Admin, scheduling, and reporting move to the agents."},
    ],
    "stack": p.get("stack") or stack,
    "gaps": p.get("gaps") or gaps,
    "oppmap": p.get("oppmap") or oppmap,
    "ignore": p.get("ignore") or [
        {"title": "Fully autonomous pricing or bidding", "reason": "Keep pricing human-approved until your job-type data is clean."},
        {"title": "Big-bang platform migration", "reason": "The agents sit on top of the tools you already run — no rip-and-replace."},
        {"title": "Generic AI chatbot on the website", "reason": "A novelty bot without your workflows behind it creates work instead of removing it."},
    ],
    "agents": p.get("agents") or agents,
    "timeline": p.get("timeline") or [
        {"phase": "Week 1", "sub": "Foundation", "items": ["Lock intake fields and inquiry categories", "Connect the agents to your existing tools", "Approve voice and response templates"], "result": "A usable lead and follow-up workflow."},
        {"phase": "Weeks 2-3", "sub": "Agents live", "items": ["Speed-to-lead and follow-up agents take the front door", "Scheduling and admin routing turn on", "Weekly report lands automatically"], "result": "The response gap closes; nothing goes quiet."},
        {"phase": "Week 4", "sub": "Optimize", "items": ["Tune thresholds from real conversations", "Expand reactivation list", "Review the first ROI numbers together"], "result": "A system you own, with proof behind it."},
    ],
    "demo": p.get("demo") or {
        "sub": re.sub(r"<[^>]+>", "", p.get("speed_to_lead_context") or f"A real inquiry comes in to {biz}: the agent answers in seconds, collects what's missing, and routes it to you."),
        "note": f"The point is not a chatbot novelty. It is a faster front door for the work {biz} already wins.",
    },
    "prompts": p.get("prompts") or prompts,
    "calc": p.get("calc") or {
        "contract": contract, "contract_label": f"${contract:,}",
        "leads": leads_n, "leads_label": str(leads_n),
        "rate": rate, "rate_label": f"{rate}%",
        "hours": hours, "hours_label": f"{hours} hrs",
        "sub": calc_sub,
    },
    "qualifier_q7_agents": p.get("qualifier_q7_agents") or [a["name"] for a in agents],
})

json.dump(p, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"converted {path}: {len(p)} keys")
