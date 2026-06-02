# AI Advantage Blueprint — Claude Code, Claude Code Agency

## Business Overview

Claude Code Agency is a 2-year-old AI agent development and automation consultancy that builds custom AI systems for SMBs and franchise operators. Founded by a former software engineer turned AI automation specialist, the agency sells fixed-price $5,000 contracts that deliver a complete, calibrated AI agent stack in 30 days.

Current state:
- Monthly leads: 25
- Close rate: ~20% (5 contracts/month)
- Average contract value: $5,000
- Monthly revenue: ~$40,000–$42,000
- Team size: 4 people
- Annual revenue: ~$500,000

The agency has product-market fit — clients see clear results from AI agents. The constraint is delivery capacity. One human can properly onboard 3 clients per month. The goal is 10+.

## The Core Problem

Claude Code Agency sells better than it delivers. Here's the breakdown:

1. **Manual onboarding**: Each new client requires 8 hours of back-and-forth to gather credentials, map workflows, and understand their tech stack. There is no repeatable intake system.

2. **Custom from scratch**: Every project starts from zero. There is no reusable agent framework — each client gets a bespoke configuration. This makes delivery slow and the founder the only person who can do it.

3. **No follow-up automation**: After a discovery call, if a prospect doesn't reply, they fall through. No automated re-engagement sequence means roughly 25–30% of warm leads are lost unnecessarily.

4. **Sales depends on the founder**: Only the founder can close. There is no scalable sales process — no automated proposals, no AI-driven qualification, no systematic discovery prep.

5. **Zero referral system**: Satisfied clients at the 30-day milestone are a goldmine for referrals, but there is no automated process to ask at the right moment.

## The AI Opportunity

The greatest irony in the AI consulting industry: agencies that build AI for clients often haven't deployed AI in their own operations. Claude Code Agency is at that inflection point. The same systems they build for clients are exactly what they need internally.

Here's where AI creates the most leverage:

### 1. Client Onboarding Agent — Turn 8 Hours into 45 Minutes

Every new client engagement starts with an intake process that currently takes 8 hours across multiple back-and-forth exchanges. An AI onboarding agent sends a structured intake form immediately after contract signing, collects credentials, maps top 3 automation priorities, identifies tech stack, and packages everything into a project brief — automatically.

The delivery team walks into every kickoff with complete information instead of missing pieces. Onboarding capacity goes from 3 clients per month to effectively unlimited at the intake stage.

**What other AI agencies are already doing:** AI-native consulting firms like Gradient Works and Relevance AI have deployed intake agents that cut their discovery process from days to hours — one team reported reducing sales-to-kickoff time from 14 days to 3 days after deploying an intake agent.

**How it helps them:** They onboard more clients without hiring, maintain delivery quality at scale, and free senior consultants to focus on strategy instead of information gathering.

**How Bennett delivers it for Claude Code Agency:** A Claude Code CLI-powered intake agent wired to GoHighLevel that collects everything, builds the brief, and routes it to the delivery team in Slack — before the first human call.

### 2. Lead Follow-Up Agent — Recover 20-30% of Warm Leads

After a discovery call, if a prospect doesn't reply within 5 days, the odds of closing drop significantly. Currently, Claude Code Agency has no systematic follow-up. A lead who attended a demo and went quiet is effectively lost.

An AI follow-up agent checks for non-replies at day 5, pulls the specific pain point mentioned in the call from GHL notes, and sends a personalized follow-up that references exactly what they talked about — not a generic "just checking in."

This alone could recover 1-2 additional closed contracts per month at $5K each — $5,000–$10,000 in monthly revenue with no additional marketing spend.

### 3. Delivery Scope Agent — End Scope Creep Before It Starts

Every week 3 on a project, the same conversation happens: the client asks for something outside the original scope, and the team scrambles to decide what's included. This costs time, strains the relationship, and compresses margins.

A Delivery Scope Agent converts completed intake data into a formal 30-day delivery plan — deliverables list, explicit out-of-scope list, milestone table, success criteria, and change request protocol — within minutes of intake completion. The client approves in writing before a single line of code is written.

Scope creep conversations drop from weekly to monthly.

### 4. Referral & Review Agent — Turn Day-30 Clients into a Sales Channel

At the 30-day milestone, clients have seen results. They are at peak satisfaction. This is the exact right moment to ask for a referral and a Google review — but most agencies miss the window because there is no automated system to catch it.

A Referral Agent fires automatically when GHL tags a client with "milestone-30d-complete." It sends a warm, specific message that references their actual outcome (not a generic "loved working with you"), asks for a Google review with a direct link, and asks if they know any other business operators who are still doing things manually.

At 5 closed clients per month, with a 30% referral yield, this adds 1-2 referred leads per month. Referred leads close at 3-4x the rate of cold leads.

### 5. Inbound Content Agent — Thought Leadership Without Writing

LinkedIn posts from real client wins drive inbound leads for AI agencies. But writing two posts per week while running delivery is not realistic for a 4-person team.

An Inbound Content Agent fires every Monday, reviews completed milestones from the previous week, and drafts two LinkedIn posts and one case study snippet per client win — formatted for direct publishing, routed to Notion for approval. The founder never writes a cold draft again.

Two posts per week for 50 weeks = 100 organic LinkedIn touchpoints per year. At even a 1% conversion to discovery calls, that is 1 additional qualified call per week.

### 6. Tech Stack Audit Agent — Stop Mid-Project Surprises

The most expensive problem in AI consulting is discovering an integration doesn't work at week 3. APIs change, plan tiers have rate limits, legacy tools have no API at all. A Tech Stack Audit Agent reviews every client's reported tools immediately after intake, risk-rates each integration (Low/Medium/High), flags any blockers before scoping begins, and documents exactly what credentials are needed for Day 1.

Projects that start with a completed tech audit have near-zero integration surprises. Projects that skip it frequently hit 1-2 week delays.

## Three Prompts to Use Today

### Prompt 1: Client Onboarding Agent
This prompt handles the entire intake process from signed contract to project brief without a human touching it.

You are the Client Onboarding Agent for Claude Code Agency, an AI agent development firm. When a new client contract is signed, immediately send a structured intake form collecting: business name, current CRM, top 3 automation priorities in priority order, API credentials available, team size, people who will interact with agents daily, and any past automation attempts. Package the completed intake into a project brief JSON, tag the GHL contact "onboarding-intake-complete," route the brief to the delivery team Slack with a summary, create a Notion project page, and confirm the kickoff date. Never start delivery work without a complete intake. If the client is unresponsive after 48 hours, send one gentle follow-up. If they say "just call me," book a 20-minute intake call instead.

### Prompt 2: Lead Follow-Up Agent
This prompt re-engages warm leads before they go cold permanently.

You are the Lead Follow-Up Agent for Claude Code Agency. For any prospect who attended a discovery call but has not replied in 5 days, pull their specific pain point from the GHL call notes and send a follow-up under 120 words that opens with that pain point specifically (never "just checking in"), offers one concrete value point — a relevant stat, case study, or quick win they can use today — and closes with two specific calendar times for a 15-minute call. Tag GHL "follow-up-sent-day-5." If no reply after 3 more days, send one shorter follow-up with only the two calendar slots. After a second non-reply, tag "follow-up-exhausted" and route to the sales team. If they reply positively, tag "re-engaged" and notify the sales team in Slack immediately.

### Prompt 3: Delivery Scope Agent
This prompt converts intake data into a signed scope plan before delivery begins.

You are the Project Scope Agent for Claude Code Agency. After the client intake is complete, generate a 30-day delivery plan that includes: a 3-sentence executive summary of what gets built for whom by when, a numbered deliverables list (only what is explicitly in the $5K contract), an explicit out-of-scope list to prevent scope creep conversations, a milestone table for Days 1-3, 4-7, 8-14, and 15-30, written success criteria both sides agree on, and a change request protocol explaining that any post-approval requests become a separate contract. Create this as a Notion page, email it to the client with a 48-hour approval deadline, and tag GHL "scope-plan-sent." If no approval in 48 hours, send one reminder and pause delivery until the client approves in writing.

## The DIY Path vs. The Partner Path

**DIY (Start This Week):**
Use the three prompts above in Claude Code CLI or the Anthropic API. Wire them to your GoHighLevel instance with webhooks. Expected time to first working agent: 3-5 days. Time savings at full implementation: 8-12 hours per week. This path requires your team to configure, test, and maintain the agents.

**Partner Path (30-Day Full Deployment):**
Claude Code Agency already runs on these exact agent systems. Bennett's team builds, calibrates, and connects all 6 agents to your GoHighLevel and Notion in 30 days — and trains your team to maintain them. The agents are running at 90%+ accuracy from Day 1, not learning over time. Fixed $5K contract, no surprises, no scope creep.

The question is whether you want to build it yourself (months) or have a team that has done this exact project before do it in 30 days.

## What to Ignore Right Now

Not every AI opportunity is worth chasing in the first 30 days. Here are the ones to skip for now — and why:

**Fully autonomous pricing decisions:** AI can model pricing scenarios and recommend changes based on market data — and eventually run A/B tests automatically. For now, keep the contract pricing decisions with leadership. This is a future-phase capability, not a Day 1 priority.

**AI-generated proposals:** Automated proposal generation is powerful once you have 50+ past proposals to train on. At your current scale, the founder's custom proposals close better. Build the intake and follow-up agents first, then layer in proposal automation.

**AI-driven hiring:** Screening and interviewing automation works well at scale. At a 4-person team, you hire rarely enough that the manual process is fine. Focus on revenue-generating agents first.

**Full social media automation:** AI can draft content, but publishing autonomously without review creates reputational risk for a consulting firm. The Inbound Content Agent should route to Notion for approval, not post directly.

## Sources and Benchmarks

1. Speed-to-lead research: Harvard Business Review (2011) — companies that contact prospects within 1 hour are 7x more likely to qualify the lead. The same pattern holds in AI consulting — first agency with a concrete plan typically wins the deal.

2. Follow-up recovery rates: Salesforce State of Sales research — 44% of sales reps give up after one follow-up. Agencies with automated 5-day follow-up sequences recover 20-30% of initial non-responders.

3. Referral conversion rates: Nielsen Trust in Advertising report — referrals convert at 3-5x the rate of cold outbound. For a $5K contract, one referred lead per month adds $5K in monthly revenue at near-zero acquisition cost.

4. Onboarding time reduction: Relevance AI 2024 case studies — AI intake agents reduced onboarding back-and-forth from 8-12 hours to under 1 hour for professional services firms.

5. Scope creep cost: Project Management Institute (PMI) Pulse of the Profession — 52% of projects experience scope creep; projects with a written scope agreement at kickoff have 40% fewer scope disputes.

## Call to Action

The agents described in this blueprint are not theoretical. They run in GoHighLevel + Claude Code CLI on real client accounts today.

The question is whether Claude Code Agency has them running for itself — or is still delivering AI for everyone else while doing its own operations manually.

If you want to talk through the 30-day deployment plan for these 6 agents specifically for Claude Code Agency's workflow, click "See If You Qualify" and fill out the 8-question qualifier. If it's a fit, the team will reach out within 48 hours with a call to review your numbers.
