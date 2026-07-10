#!/usr/bin/env python3
"""Enrich the thin 2026-06-18 intake JSONs (Simon / Asif) into full builder
profiles that gen-blueprint.py can render.

Root cause being fixed: the previously-shipped full profiles were stale Brent/CRMX
clones (wrong accent, SaaS agents, sub-1200-char prompts). This builds a CLEAN
full profile straight from the lead's real 2026-06-18 intake facts + the canonical
6 agents already in the thin JSON, expanding each agent prompt into a 7-section
operating runbook (>=1200 chars) so the agent-prompt-quality gate passes.

Output keeps slug = <lead>-20260618 so HTML lands at blueprints/<slug>.html and
binds to the existing production receipts.
"""
import json, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECTIONS = ["identity", "inputs", "workflow", "output", "rules", "escalation", "first-run test"]


def runbook(business, name, role_line, inputs, workflow, output, rules, escalation, test):
    """Compose a 7-section, second-person operating runbook (>=1200 chars)."""
    txt = (
        f"## Identity\n"
        f"You are the {name} for {business}. {role_line}\n\n"
        f"## Inputs you need\n{inputs}\n\n"
        f"## Workflow\n{workflow}\n\n"
        f"## Output\n{output}\n\n"
        f"## Rules / guardrails\n{rules}\n\n"
        f"## Escalation / human review\n{escalation}\n\n"
        f"## First-run test\n{test}"
    )
    return txt


def build_agents(profile, business, first_name, runbooks):
    """Merge canonical thin-JSON agents with full runbook prompts."""
    thin = profile["ai_agents"]
    agents = []
    for i, a in enumerate(thin):
        rb = runbooks[i]
        prompt = runbook(business, a["name"], *rb)
        assert len(prompt) >= 1200, f"{a['name']} runbook only {len(prompt)} chars"
        # 7-section marker check
        low = prompt.lower()
        for marker in ["## identity", "inputs you need", "## workflow", "## output",
                       "guardrails", "human review", "first-run test"]:
            assert marker in low, f"{a['name']} missing marker {marker}"
        agents.append({
            "name": a["name"],
            "desc": a["desc"],
            "agent_prompt": prompt,
            "outcome": a["result"],
        })
    return agents


# ----------------------------------------------------------------------------
# SIMON — Disruptive Foods (UK street-food product distributor to retail)
# ----------------------------------------------------------------------------
def simon_profile():
    p = json.load(open(os.path.join(REPO, "leads", "simon-harwood-disruptive-foods-20260618.json")))
    business = "Disruptive Foods"
    first = "Simon"
    domain = "disruptivefoods.co.uk"

    rb = [
        # 1 Buyer Enquiry & Sample-Request Agent
        ("Every retail or grocery buyer enquiry, sample request, listing question, or pricing ask is answered fast, accurately, and on-brand so the supplier who replies first keeps the account.",
         "- The inbound buyer message (email, WhatsApp, or text) and the channel it arrived on.\n- The retail/grocery account name and buyer contact, if known.\n- The product line or range the buyer is asking about, plus any spec sheets or sample-dispatch instructions on file.",
         "Step 1: Classify the request — range query, sample request, listing question, or pricing.\nStep 2: Capture account name, contact, product line, and exactly what the buyer needs.\nStep 3: Draft a fast, accurate, on-brand reply that confirms next steps and attaches the right spec or sample-dispatch instruction.\nStep 4: Log the enquiry so nothing slips between WhatsApp, text, and email.\nStep 5: If the request needs a human decision, summarize and route it.",
         "Return a ready-to-send reply plus a one-line enquiry log entry: account, contact, product line, request type, next step, and owner.",
         "Keep every reply in the street-food brand voice and buyer-ready. Never quote bespoke pricing, confirm a new listing, or promise exclusivity without human approval. Use only facts on file — never invent specs, stock, or lead times.",
         "Route to the right teammate for any bespoke pricing, new listing, or exclusivity request, with a clean one-line summary so a human can decide. Do not send commercial commitments yourself.",
         "Test input: a grocery buyer WhatsApps asking for a sample of a new street-food range and a price for 200 units. Expected output: a same-minute reply confirming the sample dispatch, the missing details needed to quote, and a log entry — with the pricing question flagged for human approval."),
        # 2 Retail Marketing Content Agent
        ("The weekly product and launch calendar becomes ready-to-use retail marketing content so content stops being the team's biggest named drain.",
         "- The product and launch calendar for the week.\n- The target retail or grocery channel for each item.\n- The street-food brand voice guide and any existing listing copy or one-pagers.",
         "Step 1: Read the launch calendar and identify what ships this week.\nStep 2: For each item, draft retail listing copy, a buyer sell-in one-pager, brand-voice social posts, and account/consumer email copy.\nStep 3: Tune each piece to the specific retail channel it is going to.\nStep 4: Package drafts so the team can approve and ship the same day.",
         "Return a per-launch content package: listing copy, sell-in one-pager, social posts, and email copy, each labeled by channel and ready for same-day approval.",
         "Keep every piece consistent with the street-food brand identity and the target channel. Do not invent product claims, certifications, or pricing. Mark anything that needs a fact check before it ships.",
         "Escalate to a human any claim about ingredients, accreditation, or pricing you cannot verify from supplied facts, and hold that piece until approved.",
         "Test input: a launch calendar row for a new sauce range going into a national grocer next week. Expected output: listing copy, a one-page buyer sell-in, three on-brand social posts, and an account email — all tuned to that grocer and ready to approve."),
        # 3 Hiring & Onboarding Agent
        ("Hiring and staffing across a 28-person team stops eating the hours that should go to growing accounts, with ready-to-post roles and a structured onboarding flow.",
         "- The open role and which part of the team it sits in.\n- Must-have skills and the day-to-day responsibilities.\n- The existing first-week onboarding steps and tools a new hire needs.",
         "Step 1: Draft a role description, screening questions, and an interview scorecard for the open position.\nStep 2: Build a structured first-week onboarding checklist tailored to that role.\nStep 3: Sequence onboarding tasks by day so setup is consistent for every new teammate.\nStep 4: Flag anything that needs a manager's sign-off.",
         "Return a ready-to-post role description, a screening question set, an interview scorecard, and a day-by-day first-week onboarding checklist.",
         "Use only real responsibilities and requirements supplied by the team. Do not state pay, contract terms, or benefits without approval. Keep language inclusive and compliant.",
         "Route compensation, contract, and final-offer decisions to a manager. Do not extend or imply an offer.",
         "Test input: 'We need a warehouse and dispatch coordinator.' Expected output: a posted-ready role description, five screening questions, an interview scorecard, and a five-day onboarding checklist — with pay left blank for manager input."),
        # 4 Admin & Order-Ops Agent
        ("The recurring admin load — order confirmations, account updates, supplier and logistics follow-ups — runs in one place instead of scattered across WhatsApp, text, and email.",
         "- Incoming order and account messages across WhatsApp, text, and email.\n- Open supplier and logistics threads.\n- The current list of in-flight orders and their status.",
         "Step 1: Pull the day's admin items from every channel into one view.\nStep 2: Draft order confirmations, account updates, and supplier/logistics follow-ups.\nStep 3: Flag anything overdue or stuck.\nStep 4: Produce a short daily operations summary showing open items, today's priorities, and blockers.",
         "Return drafted confirmations and follow-ups plus a daily ops brief: open items, today's priorities, overdue/stuck items, and a one-line summary of each exception.",
         "Never confirm pricing, delivery dates, or stock you cannot verify. Keep confirmations factual and on-brand. Do not close or commit on an order without the owner's input.",
         "Escalate delayed shipments, account issues, and pricing queries to a human with a clear one-line summary; do not resolve commercial exceptions yourself.",
         "Test input: three order emails, a delayed-shipment WhatsApp, and two supplier follow-ups. Expected output: drafted confirmations and follow-ups, the delayed shipment flagged for a human, and a daily ops brief listing the six items by priority."),
        # 5 Team Organization & Weekly-Ops Agent
        ("A 28-person team works from one weekly brief instead of status spread across three messaging apps.",
         "- Account activity and launch progress for the week.\n- Open admin items and current hiring status.\n- Anything the team flagged as a priority or a blocker.",
         "Step 1: Gather account activity, launch progress, open admin items, and hiring status.\nStep 2: Combine them into one short weekly brief.\nStep 3: Recommend three priorities for the week with a clear owner each.\nStep 4: Surface blockers that need a decision.",
         "Return one weekly brief: a short status roll-up, three recommended priorities with owners, and a blockers list — a single source of truth instead of WhatsApp, text, and email threads.",
         "Use only real status supplied by the team. Do not invent progress or assign owners without basis. Keep the brief short enough to read in two minutes.",
         "Escalate any blocker that needs a manager's decision, and flag conflicting priorities for a human to resolve rather than guessing.",
         "Test input: the week's account notes, two launches in progress, four open admin items, and one open role. Expected output: a two-minute weekly brief with three owned priorities and a blockers list naming the open role and any stalled launch."),
        # 6 Buyer Account Insights & Reporting Agent
        ("Enquiry and account activity become a simple weekly read on which retail relationships are growing or going quiet.",
         "- The week's enquiry volume and sample requests by account.\n- Account activity and recent order or listing movement.\n- Prior weeks' read for comparison, if available.",
         "Step 1: Summarize enquiry volume, sample requests, and account activity by retail relationship.\nStep 2: Compare against recent weeks to spot momentum.\nStep 3: Flag which accounts are growing and which have gone quiet.\nStep 4: Surface three concrete follow-up opportunities.",
         "Return a one-page weekly read: activity by account, growing vs. quiet flags, and three prioritized follow-up opportunities the team can act on.",
         "Report only from real activity data. Do not infer revenue or forecast numbers you cannot support. Label any estimate clearly as an estimate.",
         "Escalate accounts that have gone quiet and look at risk to a human for a relationship call; do not send win-back outreach without approval.",
         "Test input: a week of enquiry logs across eight retail accounts. Expected output: a one-page read showing two growing and one quiet account, with three named follow-up opportunities ranked by impact."),
    ]

    agents = build_agents(p, business, first, rb)

    full = dict(p)  # carry forward all clean canonical fields (urls, colors, contact, etc.)
    full.update({
        "domain": domain,
        "crm_tool_fallback": "a simple CRM or shared tracker",
        "hero_sub": ("A practical AI roadmap for Simon and Disruptive Foods that turns retail buyer "
                     "enquiries, sample requests, marketing content, hiring, and weekly team organization "
                     "into one faster, cleaner operating system."),
        "hero_stats": [
            {"num": "10", "label": "Inbound buyer enquiries a month (your form)"},
            {"num": "28", "label": "Team members across Disruptive Foods (your form)"},
            {"num": "6", "label": "AI agents mapped to your first workflow layer"},
        ],
        "snapshot": [
            {"val": "Disruptive Foods", "key": "Business"},
            {"val": "Street-food product distribution to retail", "key": "Operating category"},
            {"val": "&pound;3&ndash;10M (your form)", "key": "Revenue range"},
            {"val": "10/mo", "key": "Inbound enquiries (your form)"},
        ],
        "profile_note": ("Built from your intake answers: a 28-person Lancaster-based street-food product "
                         "distributor selling branded ranges into UK retail and grocery, around 10 inbound "
                         "buyer enquiries a month, a ~60-minute response window today, ChatGPT in use, and no "
                         "CRM or project-management system yet. The safest first AI layer is buyer-enquiry "
                         "response, marketing content, hiring, and weekly team organization."),
        "results": {
            "title": "Disruptive Foods can turn buyer follow-up into a managed operating system",
            "sub": ("The first Blueprint layer reduces repeated manual steps across buyer enquiries, sample "
                    "requests, marketing content, hiring, and team organization, while keeping human review on "
                    "pricing, listings, and commercial commitments."),
            "cards": [
                {"title": "Faster buyer response", "desc": "Turn a 60-minute response window into a 60-second one so the account stays with you.", "tag": "Speed", "tagclass": ""},
                {"title": "Content off the bottleneck", "desc": "Launch copy, listings, and social move from a weekly scramble to a same-day package.", "tag": "Quality", "tagclass": ""},
                {"title": "One source of truth", "desc": "Status, admin, and weekly priorities live in one brief instead of three messaging apps.", "tag": "Scale", "tagclass": ""},
            ],
            "close": "The practical opportunity for Disruptive Foods is faster buyer response, content that ships same-day, and a team that starts each week aligned.",
        },
        "pillars": [
            {"title": "Revenue Capture", "metric": "Faster first touch", "sub": "Answer every buyer enquiry in seconds so the listing and the relationship stay yours."},
            {"title": "Time Recovery", "metric": "Fewer repeated admin loops", "sub": "Move intake, confirmations, content, and follow-up into agent-assisted workflows."},
            {"title": "Operational Consistency", "metric": "One weekly brief", "sub": "Give a 28-person team one source of truth instead of WhatsApp, text, and email."},
        ],
        "stack": [
            {"tool": "ChatGPT", "role": "Marketing content drafting today"},
            {"tool": "WhatsApp / Text / Email", "role": "Buyer, supplier, and team conversations"},
            {"tool": "Website / Online Presence", "role": "Product discovery and buyer trust"},
            {"tool": "No CRM yet", "role": "Buyer, stockist, and enquiry tracking gap"},
            {"tool": "No Project-Management system yet", "role": "Team status and task gap"},
            {"tool": "Product & Launch Calendar", "role": "Marketing content and listing planning"},
        ],
        "gaps": [
            {"title": "Buyer enquiries need a 60-second answer", "desc": "With ~10 inbound enquiries a month and a 60-minute window today, every faster, more accurate reply protects the listing and the account.", "tag": "High leverage", "tagclass": ""},
            {"title": "Marketing content is a named drain", "desc": "Launches, retail listings, and social compete for the same limited hours every week.", "tag": "High leverage", "tagclass": ""},
            {"title": "Hiring and staffing eat growth time", "desc": "Hiring across a 28-person team takes time that should go to growing accounts.", "tag": "High leverage", "tagclass": ""},
            {"title": "Status lives across three apps", "desc": "Admin and team organization are spread across WhatsApp, text, and email instead of one place.", "tag": "High leverage", "tagclass": ""},
        ],
        "oppmap": [
            {"usecase": a["name"], "impact_tag": tag, "impact": a["outcome"], "tools": tool}
            for a, tag, tool in zip(
                agents,
                ["High", "High", "High", "High", "Medium", "Medium"],
                ["WhatsApp / Text / Email", "Product & Launch Calendar", "Team", "WhatsApp / Text / Email", "Team", "Enquiry logs"],
            )
        ],
        "ignore": [
            {"title": "Full autonomous buyer commitments", "reason": "Keep human approval on pricing, new listings, exclusivity, and final commercial commitments."},
            {"title": "Platform migration first", "reason": "Improve the current workflow before changing tools; measure the bottleneck first."},
            {"title": "Generic content volume", "reason": "The first win is buyer-response speed and content quality, not flooding channels with unreviewed posts."},
        ],
        "timeline": [
            {"phase": "Week 1 · Days 1-7", "sub": "Onboarding & setup", "items": [
                "Confirm how buyer enquiries reach Disruptive Foods across WhatsApp, text, and email",
                "Define response categories, escalation rules, and handoff owners",
                "Build the first reply, sample-request, and content templates"],
             "result": "The team has a clean intake and response map before automation touches buyer-facing conversations."},
            {"phase": "Weeks 2-3 · Days 8-21", "sub": "Agents go live", "items": [
                "Test the buyer-enquiry, content, and admin agents on real examples",
                "Review language for pricing, listings, and brand-sensitive boundaries",
                "Create the first measurement view for response speed and content turnaround"],
             "result": "Enquiries get answered in seconds and content ships same-day, with human review on commitments."},
            {"phase": "Day 30", "sub": "Optimize and expand", "items": [
                "Review real conversations and tune prompts",
                "Add the weekly team brief and account-insights loop",
                "Document the weekly improvement rhythm and ownership"],
             "result": "Disruptive Foods has a repeatable system for buyer response, content, hiring, and weekly team organization."},
        ],
        "demo": {
            "sub": "The demo shows a real-looking buyer enquiry entering Disruptive Foods, getting classified, summarized, drafted, and routed to a clear next action without making unsupported commitments.",
            "note": "This is a proof workflow, not an external customer send. Human approval stays on pricing, listings, and commercial commitments.",
        },
        "prompts": [
            {"title": agents[idx]["name"], "subtitle": sub, "pre": agents[idx]["agent_prompt"], "outcome": agents[idx]["outcome"]}
            for idx, sub in [(0, "First response and routing agent"),
                             (1, "Retail marketing content agent"),
                             (3, "Admin and order-ops agent")]
        ],
        "cta_personal": "Simon, the next step is to open the playbook, review the agents, and confirm which workflow should be built first.",
        "calc": {
            "contract": 45, "contract_label": "&pound;45",
            "leads": 10, "leads_label": "10/mo",
            "rate": 30, "rate_label": "30%",
            "hours": 30, "hours_label": "30/wk",
            "sub": "Avg Customer Value is a fill-in field shown here at a conservative per-order placeholder; you confirm your real average order value, win rate, and enquiry volume. No outcomes guaranteed.",
        },
        "agents": agents,
        "ai_agents": agents,
        "qualifier_q7_agents": [{"name": a["name"], "desc": a["desc"], "agent_prompt": a["agent_prompt"], "outcome": a["outcome"]} for a in agents],
        "prompt_1": agents[0]["agent_prompt"],
        "prompt_2": agents[1]["agent_prompt"],
        "prompt_3": agents[3]["agent_prompt"],
    })
    return full


# ----------------------------------------------------------------------------
# ASIF — JAM Equities (Chicago multi-unit QSR / restaurant operator, 5 locations)
# ----------------------------------------------------------------------------
def asif_profile():
    p = json.load(open(os.path.join(REPO, "leads", "asif-jam-equities-20260618.json")))
    business = "JAM Equities"
    first = "Asif"
    domain = "jameg.com"

    rb = [
        # 1 Missed-Call & Catering-Capture Agent
        ("Every missed call or message across five restaurant locations becomes a captured guest, catering order, or reservation instead of lost revenue.",
         "- The inbound call, text, or message that went unanswered, and which location it was for.\n- Guest contact details when available.\n- The catering and large-party routing list by unit manager.",
         "Step 1: Detect any unanswered call, text, or message across any location.\nStep 2: Instantly send a branded follow-up that captures what the guest needs — catering order, large party, reservation, or general question.\nStep 3: Collect name, phone, date, party size, and location.\nStep 4: Route catering and large-party requests to the right unit manager with a ready-to-act summary.\nStep 5: Confirm details back to the guest and log the captured lead.",
         "Return a captured-lead record (name, phone, date, party size, location, request type), a confirmation message to the guest, and a routed summary for the unit manager.",
         "Stay on-brand for the location and never quote catering pricing or confirm availability without a manager. Capture every lead even if details are incomplete. Do not promise a booking you cannot confirm.",
         "Route catering and large-party requests to the right unit manager with a one-line summary; escalate anything requiring a pricing or capacity decision rather than committing.",
         "Test input: a missed call at the Lincoln Park location from a guest wanting catering for 40 next Friday. Expected output: an instant branded follow-up capturing name, phone, date, party size, and location, plus a routed summary to that unit's manager and a logged lead."),
        # 2 Booking & Follow-Up Agent
        ("Reservations, catering, and event enquiries run a consistent booking and follow-up sequence across all locations so nothing slips.",
         "- The reservation, catering, or event enquiry and the target location.\n- Date, party size, and any special requirements.\n- The location's availability rules and manager approval points.",
         "Step 1: Confirm the request and hold the date.\nStep 2: Send a confirmation, then scheduled reminders ahead of the visit or event.\nStep 3: Follow up after the visit or event for feedback and rebooking.\nStep 4: Keep the cadence reliable and identical across all locations.\nStep 5: Surface anything needing a manager decision.",
         "Return a booking record with confirmation, reminder schedule, and post-visit follow-up, plus a one-line summary of anything needing a manager's decision.",
         "Never confirm a date or capacity you cannot verify. Keep the cadence consistent across every unit. Do not modify or cancel a booking without the guest's and manager's input.",
         "Escalate capacity conflicts, special-event pricing, and any cancellation or comp decision to the unit manager with a clean one-line summary.",
         "Test input: a catering enquiry for 60 at one location next month. Expected output: a confirmation holding the date, a reminder schedule, a post-event follow-up plan, and a pricing question flagged for the manager."),
        # 3 Multi-Unit Scheduling Agent
        ("Weekly staff schedules are built across every location, with coverage gaps and overtime flagged before they cost a shift.",
         "- Staff availability and roles per location.\n- Forecasted demand and required coverage by daypart.\n- Shift-swap requests and overtime thresholds.",
         "Step 1: Build a draft schedule per location from availability, forecasted demand, and required coverage.\nStep 2: Flag coverage gaps and overtime risk before they happen.\nStep 3: Handle shift-swap requests, holding them for manager approval.\nStep 4: Produce a per-location schedule plus a group-level coverage view.",
         "Return one draft schedule per location, a group coverage view, and a flagged list of gaps, overtime risks, and pending shift swaps awaiting manager approval.",
         "Respect availability, labor rules, and overtime thresholds. Never finalize a schedule or approve a swap without a manager. Do not assign staff outside their role or location without sign-off.",
         "Escalate uncovered shifts, overtime breaches, and contested swaps to the manager; present options rather than forcing a single assignment.",
         "Test input: availability for five locations with a known Friday-night gap at one unit. Expected output: five draft schedules, a group coverage view, the Friday gap flagged, and any overtime risk surfaced for manager approval."),
        # 4 Hiring & Onboarding Agent
        ("A constantly-hiring restaurant group gets a repeatable way to post roles and onboard front-of-house and kitchen staff across every location.",
         "- The open front-of-house or kitchen role and its location.\n- Must-have skills and shift requirements.\n- The existing first-week onboarding steps and required paperwork.",
         "Step 1: Draft role posts and screening questions for the open position.\nStep 2: Schedule interviews and prepare a scorecard.\nStep 3: Build a structured first-week onboarding checklist per role.\nStep 4: Sequence onboarding by day so every new hire ramps the same way across the group.",
         "Return a ready-to-post role, screening questions, an interview scorecard, and a day-by-day first-week onboarding checklist tailored to the role and location.",
         "Use only real responsibilities and shift requirements supplied by the operator. Do not state pay or benefits without approval. Keep language inclusive and compliant across all units.",
         "Route compensation, final-offer, and any compliance-sensitive decisions to a manager; do not extend or imply an offer.",
         "Test input: 'We need a line cook at the Naperville location.' Expected output: a posted-ready role, five screening questions, an interview scorecard, and a five-day kitchen onboarding checklist — with pay left for manager input."),
        # 5 Multi-Unit Ops Dashboard Agent
        ("Calls captured, bookings, coverage, hiring, and guest themes across all locations roll into one daily group brief.",
         "- Captured calls and catering leads, booking activity, and schedule coverage by location.\n- Hiring status and guest communication themes.\n- Yesterday's brief for comparison.",
         "Step 1: Combine captured calls and catering leads, booking activity, schedule coverage, hiring status, and guest themes across all locations.\nStep 2: Roll them into one short daily brief.\nStep 3: Recommend three actions for the day.\nStep 4: Flag blockers and anything off-trend versus yesterday.",
         "Return one daily group brief: a short roll-up by area, three recommended actions, and a blockers list — one place instead of WhatsApp, text, Google Chat, and email.",
         "Report only from real activity data. Do not invent numbers or forecast figures you cannot support. Keep the brief readable in two minutes.",
         "Escalate any operational blocker that needs a manager's decision and flag locations trending off-plan for a human to act on.",
         "Test input: a day of captured leads, bookings, coverage, and guest messages across five units. Expected output: a two-minute daily brief with three recommended actions and a blockers list naming any understaffed unit or unanswered guest theme."),
        # 6 Customer Communication & Reviews Agent
        ("Guest replies and online reviews stay fast and on-brand across every location so customer communication stops slipping.",
         "- Guest messages, questions, and online reviews across all locations.\n- The brand voice guide and service-recovery policy.\n- The routing list for service issues by unit manager.",
         "Step 1: Draft fast, on-brand replies to guest messages, questions, and reviews across all locations.\nStep 2: Route service issues to the right unit manager.\nStep 3: Summarize recurring guest themes each week.\nStep 4: Surface what to fix and what to celebrate.",
         "Return drafted guest and review replies, routed service issues with a one-line summary, and a weekly themes report of what to fix and celebrate.",
         "Keep replies on-brand and never admit fault, offer comps, or make commitments without manager approval. Do not respond to a review with unverifiable claims.",
         "Escalate service complaints, refund or comp requests, and reputational risks to the unit manager with a clean one-line summary before any public reply goes out.",
         "Test input: three guest messages and two new reviews across two locations, one negative. Expected output: on-brand draft replies, the negative review routed to that unit's manager for approval, and a note in the weekly themes report."),
    ]

    agents = build_agents(p, business, first, rb)

    full = dict(p)
    full.update({
        "domain": domain,
        "crm_tool_fallback": "a simple CRM or shared tracker",
        "hero_sub": ("A practical AI roadmap for Asif and JAM Equities that turns missed calls, catering "
                     "enquiries, multi-unit scheduling, hiring, and daily operations across five restaurant "
                     "locations into one faster, more consistent system."),
        "hero_stats": [
            {"num": "5", "label": "Quick-service locations (your form)"},
            {"num": "$10M+", "label": "Annual revenue range (your form)"},
            {"num": "6", "label": "AI agents mapped to your first workflow layer"},
        ],
        "snapshot": [
            {"val": "JAM Equities", "key": "Business"},
            {"val": "Multi-unit quick-service restaurant operator", "key": "Operating category"},
            {"val": "$10M+ (your form)", "key": "Revenue range"},
            {"val": "5", "key": "Locations (your form)"},
        ],
        "profile_note": ("Built from your intake answers: a multi-unit quick-service restaurant operator "
                         "running five locations in the greater Chicago area, $10M+ revenue range, AI already "
                         "in regular use, inconsistent response times today, and no CRM or project-management "
                         "system yet. The safest first AI layer is missed-call capture, booking and follow-up, "
                         "multi-unit scheduling, hiring, and a daily operations brief."),
        "results": {
            "title": "JAM Equities can turn missed calls and scattered status into a managed operating system",
            "sub": ("The first Blueprint layer reduces lost calls, inconsistent follow-up, and scheduling churn "
                    "across five locations, while keeping human review on pricing, comps, and staffing decisions."),
            "cards": [
                {"title": "Capture every call", "desc": "Turn missed calls into captured catering orders, parties, and reservations across every unit.", "tag": "Speed", "tagclass": ""},
                {"title": "Consistent follow-up", "desc": "Run the same reliable booking and follow-up cadence at all five locations.", "tag": "Quality", "tagclass": ""},
                {"title": "One operating picture", "desc": "Calls, bookings, coverage, hiring, and guest themes roll into one daily brief.", "tag": "Scale", "tagclass": ""},
            ],
            "close": "The practical opportunity for JAM Equities is capturing every call, consistent follow-up, and one daily picture across the whole group.",
        },
        "pillars": [
            {"title": "Revenue Capture", "metric": "No missed call lost", "sub": "Turn every unanswered call across five units into a captured guest or catering order."},
            {"title": "Time Recovery", "metric": "Scheduling off the manager's plate", "sub": "Draft schedules, follow-ups, and confirmations with agent-assisted workflows."},
            {"title": "Operational Consistency", "metric": "One daily brief", "sub": "Give a five-location group one source of truth instead of four messaging apps."},
        ],
        "stack": [
            {"tool": "AI (in regular use)", "role": "Existing automation maturity to build on"},
            {"tool": "WhatsApp / Text / Google Chat / Email", "role": "Guest and team conversations"},
            {"tool": "Google Drive", "role": "Document and operations storage"},
            {"tool": "No CRM yet", "role": "Guest, catering, and lead tracking gap"},
            {"tool": "No Project-Management system yet", "role": "Multi-unit status and task gap"},
            {"tool": "Phone / Reservations", "role": "Inbound calls, catering, and bookings"},
        ],
        "gaps": [
            {"title": "Missed calls cost the group real money", "desc": "Catering orders, large parties, and guest questions go unanswered across five locations with inconsistent response times.", "tag": "High leverage", "tagclass": ""},
            {"title": "Booking and follow-up are inconsistent", "desc": "Leads and catering enquiries slip without a reliable system across units.", "tag": "High leverage", "tagclass": ""},
            {"title": "Scheduling eats hours and leaves gaps", "desc": "Scheduling across several units and shifting headcount still leaves coverage gaps.", "tag": "High leverage", "tagclass": ""},
            {"title": "Status lives across four apps", "desc": "Internal communication and team organization are spread across WhatsApp, text, Google Chat, and email.", "tag": "High leverage", "tagclass": ""},
        ],
        "oppmap": [
            {"usecase": a["name"], "impact_tag": tag, "impact": a["outcome"], "tools": tool}
            for a, tag, tool in zip(
                agents,
                ["High", "High", "High", "High", "Medium", "Medium"],
                ["Phone / Reservations", "Phone / Reservations", "Scheduling", "Team", "Multi-unit", "Reviews"],
            )
        ],
        "ignore": [
            {"title": "Full autonomous guest commitments", "reason": "Keep human approval on catering pricing, comps, capacity, and final booking confirmations."},
            {"title": "Platform migration first", "reason": "Improve the current workflow before changing tools; measure the bottleneck first."},
            {"title": "Generic marketing volume", "reason": "The first win is call capture and follow-up consistency, not unreviewed marketing output."},
        ],
        "timeline": [
            {"phase": "Week 1 · Days 1-7", "sub": "Onboarding & setup", "items": [
                "Confirm how calls and messages reach each of the five locations",
                "Define capture, routing, and escalation rules by unit",
                "Build the first missed-call, booking, and follow-up templates"],
             "result": "The group has a clean capture-and-route map before automation touches guest-facing calls."},
            {"phase": "Weeks 2-3 · Days 8-21", "sub": "Agents go live", "items": [
                "Test the missed-call, booking, and scheduling agents on real examples",
                "Review language for pricing, comps, and capacity boundaries",
                "Create the first measurement view for capture rate and coverage"],
             "result": "Missed calls get captured and follow-up runs consistently, with human review on commitments."},
            {"phase": "Day 30", "sub": "Optimize and expand", "items": [
                "Review real conversations and tune prompts per location",
                "Add the daily ops brief and reviews loop",
                "Document the weekly improvement rhythm and ownership"],
             "result": "JAM Equities has a repeatable system for call capture, booking, scheduling, hiring, and daily operations."},
        ],
        "demo": {
            "sub": "The demo shows a real-looking missed call at one location getting captured, summarized, and routed to the right unit manager with a clear next action and no unsupported commitments.",
            "note": "This is a proof workflow, not an external customer send. Human approval stays on pricing, comps, capacity, and booking confirmations.",
        },
        "prompts": [
            {"title": agents[idx]["name"], "subtitle": sub, "pre": agents[idx]["agent_prompt"], "outcome": agents[idx]["outcome"]}
            for idx, sub in [(0, "Missed-call and catering-capture agent"),
                             (1, "Booking and follow-up agent"),
                             (2, "Multi-unit scheduling agent")]
        ],
        "cta_personal": "Asif, the next step is to open the playbook, review the agents, and confirm which workflow should be built first.",
        "calc": {
            "contract": 25, "contract_label": "$25",
            "leads": 50, "leads_label": "50/mo",
            "rate": 30, "rate_label": "30%",
            "hours": 35, "hours_label": "35/wk",
            "sub": "Avg Customer Value is a fill-in field shown here at a conservative per-guest check placeholder; you confirm your real average ticket, catering close rate, and call volume. No outcomes guaranteed.",
        },
        "agents": agents,
        "ai_agents": agents,
        "qualifier_q7_agents": [{"name": a["name"], "desc": a["desc"], "agent_prompt": a["agent_prompt"], "outcome": a["outcome"]} for a in agents],
        "prompt_1": agents[0]["agent_prompt"],
        "prompt_2": agents[1]["agent_prompt"],
        "prompt_3": agents[2]["agent_prompt"],
    })
    return full


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    out = {}
    if which in ("simon", "both"):
        out["simon-harwood-disruptive-foods-20260618"] = simon_profile()
    if which in ("asif", "both"):
        out["asif-jam-equities-20260618"] = asif_profile()
    for slug, prof in out.items():
        path = os.path.join(REPO, "leads", slug + ".json")
        json.dump(prof, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        # report agent prompt char counts
        counts = [(a["name"], len(a["agent_prompt"])) for a in prof["agents"]]
        print(f"WROTE {path}")
        for n, c in counts:
            print(f"   {c:5d}  {n}")


if __name__ == "__main__":
    main()
