---
name: business-audit-skill
description: >
  FKI Business Audit Skill v2 — 36-dimension CFO-level audit framework + shared 8-dim audit-core rubric. Run for complete snapshot of FKI's financial health, pipeline, marketing, operations, legal, and tech, mapped to Project Advaita's 5 autonomy domains. Bennett reviews as CFO. Outputs prioritized needle-mover plan where every needle-mover declares revenue impact + automation posture + consolidation status.
  Cohort-aware: cloud routes restricted tools (GHL/Meta unverified) to Leo WO; CLI executes direct.
type: business-audit
applies-to: FKI company-scope
drive_folder_id: 1xlcN-2VIGgRGMLGYdJ4NUFBblCooFlsW
drive_file_id: 1ChehVt8OMh7_L5Y3tZGioS9ynx4IRp7y
skills_root_mirror_id: 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY
version: 2.5
last_updated: 2026-05-27  # v2.5: Blueprint revenue-control and funnel observability gates
council_verified: 4.46
patched_v2_5: "2026-05-27 — Adds Blueprint revenue-control and funnel observability gates: apply/qualifier/booking metrics, same-contact attach rate, duplicate contact rate, high-intent action attachment, historical lead reconciliation, external widget risk, monitoring owner/cadence, and revenue attribution blockers."
patched_v2_4: "2026-05-27 — Adds Heavy Self-Audit Business Coverage so self-audit-skill can stay small. Business audit now owns revenue, pipeline, operations, finance, automation ROI, and Advaita-domain business impact analysis transferred from per-response self-audits."
patched: "2026-05-15 v2 — Bennett directive 'permanently make those skills better.' Adopts shared 8-dimension audit-core rubric (Revenue/Automation/Consolidation are universal completion gates). Adds REAL council auto-fire after Step 4 (was: missing entirely). Adds diamond gate Step 7 (was: missing). Adds before/after delta tracking vs prior business audit (was: one-shot). Adds cohort_routing block (cloud GHL/Meta → Leo WO). Cleans mojibake from v1. drive_file_id auto-populates. Adopts fleet loader contract (name + modifiedTime desc). Council v20 4.46/4.0 PASS."
created_by: Ivan-CC (v1, 2026-05-04) + Hyperagent (v2, 2026-05-15)
trigger:
  - "business audit"
  - "run business audit"
  - "business-audit-skill"
  - "CEO day audit"
  - "CFO review"
  - "company health check"
  - "full Advaita system status"
  - "FKI monthly audit"
council_verdict: "v2 council 2026-05-15 21:45 MDT — Operational pass 4.46/4.0. 5 advisors, 0 dissents, 1 Bennett gate (irreversible archive of v1 file)."
---

# FKI Business Audit Skill v2.4

## v2.5 Patch — Blueprint Revenue-Control And Funnel Observability

When auditing Blueprint AI, AI qualifying forms, CRM lead capture, or any lead-to-call funnel, add this required subsection under Lead Acquisition, Lead Processing, Sales Intelligence, Operations, and Financial Control.

### Required funnel metrics
```yaml
blueprint_funnel_metrics:
  public_page_build_status: <pass|fail|stale|unknown>
  apply_submits: <count or source>
  qualifier_submits: <count or source>
  booking_modal_opens: <count or source>
  confirmed_appointments: <count or source>
  same_contact_attach_rate: <percent>
  duplicate_contact_rate: <percent>
  appointment_attach_rate: <percent>
  source_tag_coverage: <percent>
  monitor_last_passed_at: <timestamp|none>
```

### Business gates
1. **Leads captured before qualification:** Every high-intent funnel must capture or recover first name, last name, email, phone, and business before scoring/booking.
2. **High-intent action attached:** Qualifier submit and calendar booking must attach to the same CRM contact, not an anonymous event.
3. **No duplicate contacts:** Repeat submits from the same email/phone must update one CRM contact. Duplicate rate above 0% is Yellow/Red depending on volume.
4. **Historical lead reconciliation:** Named lead checks must report contact found, tags found, notes found, appointments found, and gaps separately.
5. **External widget risk:** Calendar/form widgets are scored as dependencies. Known parsing/captcha/attachment failures must cap Operations and Financial Control.
6. **Monitoring owner and cadence:** A revenue funnel cannot score 5/5 in Operations unless a monitor exists with owner, cadence, alert destination, and last-run proof.
7. **Revenue attribution:** Financial Control cannot score 5/5 until booked calls can be connected to held calls and closed revenue, or the missing attribution is explicitly open.
8. **Deploy health:** Public build/deployment health must be part of the funnel score, separate from code correctness.
9. **Alert hygiene:** Internal alerts must fire only on real submissions or failures, not anonymous calculator activity.
10. **Test-data policy:** Live proof contacts/appointments must be tagged and must not be deleted/cancelled without Bennett approval.

If any business gate is unknown, mark the domain Yellow. Do not call the business system 100% until all controllable gates have current proof.

## North Star (v2 — codifies Bennett directive 2026-05-15)

Succeeds when Bennett has a 36-dimension company audit AND every surfaced needle-mover declares (a) revenue impact, (b) automation posture, (c) consolidation status. The headline is: **"Here are the N things your AI workforce can fix this week — each ≥$X revenue, each self-running, each consolidates rather than fans out."**

The audit itself must survive an audit. No PLACEHOLDER drive_file_ids. No tools the cohort can't reach. No "PASS" verdict on the audit run if Reds went unactioned.

Covers: revenue vs target, pipeline velocity, CPL, ROAS, unassigned leads, GHL automation health, email deliverability, content calendar, cash runway, credit utilization, QB reconciliation, legal deadlines, FDD pipeline, agent uptime, cron health, skill gaps, memory freshness, known issues backlog, brand consistency, autonomy % by domain, Advaita AI capability vs gap analysis.

## Purpose
Full 36-dimension CFO-level audit of FKI's business health. Run monthly minimum or on-demand before major decisions. Output: prioritized needle-mover plan tied to Project Advaita's 5 autonomy domains, gated on revenue + automation + consolidation.

## Dependencies (load by NAME + modifiedTime desc — fleet loader contract v1.5)
- company-context-skill — FKI ICP, brand roster, sales motion
- check-in-skill — machine + daemon health
- memory-skill — recent context
- diy-skill — available tool stack
- council-skill — Step 5 mandatory auto-fire
- diamond-skill — Step 7 gate
- autopilot-skill — Step 6 dispatch
- caveman-skill — voice
- bennett-mode-skill — Step 8 CEO email

## Project Advaita Alignment

| Domain | Audit Sections |
|--------|---------------|
| Lead Acquisition | §3 Marketing (dims 17-22) |
| Lead Processing | §2 Sales Pipeline (dims 9-16) |
| Sales Intelligence | §2 + §5 Operations (dims 9-16, 27) |
| Operations | §4 AI Workforce (dims 23-28) |
| Financial Control | §1 Financial (dims 1-8) |

## v2.2 Patch — Advaita Metric Source-Of-Truth + No-False-100 Gate

When the business audit is asked to score "Advaita 100" or "full system status", it MUST read the metric source-of-truth before any 100% claim:

1. Local CLI source: `~/.openclaw/state/advaita-metric-source-of-truth-YYYYMMDD.json`.
2. Ivan source: `/Users/openclaw/.openclaw/state/advaita-autonomy-baseline.json`.
3. Supporting gate source: `~/.openclaw/state/advaita-gates-check.json`.

Rules:
- Do not collapse `vision_page_metric`, `autonomy_baseline`, and `honest_105pt_rubric` into one number.
- A 100% claim is blocked unless the named metric is 100, every active credential gate is green, gatekeeper has zero shipped-below-threshold leaks, and proof pass rate is 100.
- If any gated action remains (legal, finance, external send, GHL mutation, ad spend, admin credential change), the audit status is Yellow or Red, never Diamond.
- CEO email is a draft-only closeout unless the audit's Diamond criteria are met and the requested send is internal to Bennett at `bennett@franchiseki.com`.
- Current known source-of-truth receipt: `advaita-metric-source-of-truth-20260527.json` blocks 100% with operational baseline 61.9% local / 63.3% Ivan.

## v2.3 Patch — Audit-Only / No-Send Rerun Guard

When invoked by Gatekeeper, Batch Overdrive, Self Audit, Angie Audit, or any "rerun/gap scan/A-Z audit" context, business-audit-skill runs in `AUDIT_ONLY` mode unless the caller explicitly supplies a separate delivery approval.

Rules:
- Do not send CEO email, Gmail, GHL, Slack, or other external messages.
- Do not mutate Notion rows, GHL, QB, Meta, Drive canonical skills, deployments, DNS, credentials, payroll, legal documents, or ad spend.
- Produce proposal-only findings, patch plans, and local receipts.
- If Advaita status is requested, read the current `advaita-metric-source-of-truth-YYYYMMDD.json` and `advaita-gates-check.json` first.
- If `advaita_100_claim_pass != true`, output Yellow/Red only and block Diamond/100 wording.
- CEO email closeout is draft-only while any legal, finance, production, credential, external-send, or Advaita 100 gate remains open.

## v2.4 Patch — Heavy Self-Audit Business Coverage

When `self-audit-skill` MICRO_RESPONSE_MODE transfers a heavy business finding here, business-audit-skill must preserve the coverage instead of sending it back to the per-response audit.

### Added coverage
- **Self-Improvement ROI:** Estimate the dollar value, time saved, or risk reduced by the proposed permanent fix.
- **Friction-to-business impact:** Classify repeated Bennett frustration as lost CEO time, missed lead follow-up, slower sales intelligence, operational drag, or financial-control risk.
- **Advaita domain mapping:** Every transferred finding maps to Lead Acquisition, Lead Processing, Sales Intelligence, Operations, or Financial Control.
- **Permanent-fix ranking:** Rank fixes by revenue impact, autonomy gain, proof availability, reversibility, and time-to-verify.
- **No boomerang rule:** Do not force company-scope checks back into `self-audit-skill`; return only a one-line status summary for recap.

### Transferred-finding schema
```yaml
self_audit_transfer:
  source: self-audit-skill MICRO_RESPONSE_MODE
  pattern: <stable defect name>
  business_impact: <lost revenue | time loss | risk | operational drag>
  advaita_domain: <domain>
  suggested_permanent_fix: <skill/process/system patch>
  measurement_method: <how success is verified>
```

## v2 Patches (post-council, 2026-05-15)

### PI-BA-NS-1 (HIGH) — Shared 8-dim audit-core rubric on the audit itself
Every business-audit RUN is also self-graded against the 8-dim audit-core rubric (Completeness, Correctness, Constraints, Revenue, Automation, Consolidation, Cleanup, Scope Discipline). The audit cycle's OWN diamond gate uses this rubric — not a vibes-pass on "did we score 36 dimensions."

### PI-BA-NS-2 (HIGH) — Revenue floor per needle-mover
Each Top-5 needle-mover MUST declare:
```
revenue_declaration:
  expected_revenue_impact_usd: <int ≥ 1000>   # default floor; override per cycle config
  measurement_window_days: <int>              # typically 30/60/90
  measurement_method: <string>                # e.g. "Meta CAPI conversions", "GHL booked-call count", "QB commission revenue"
  ground_truth_artifact: <url>                # dashboard/sheet/report
```
Needle-movers below floor drop out of Top-5 even if their dimension is 🔴. Cycle digest reports total projected revenue across the 5 picks.

### PI-BA-NS-3 (HIGH) — Automation posture per needle-mover
Each Top-5 needle-mover MUST declare:
```
automation_declaration:
  is_self_running: true | false
  trigger_mechanism: <cron | webhook | scheduled_workflow | external_event>
  trigger_ref: <string>
  human_touches_per_week: <int target 0>
  failure_alert_destination: <slack_channel | email>
```
Needle-movers with `is_self_running: false` get flagged as Yellow recommendations (require ongoing human babysitting) — preference to Top-5 goes to self-running fixes.

### PI-BA-NS-4 (HIGH) — Consolidation status per needle-mover
Each Top-5 needle-mover MUST declare:
```
consolidation_status:
  reduces_notion_sprawl: true | false
  consolidates_existing_rows: <list of row IDs being merged | "none">
  creates_new_top_level_row: true | false   # default false; true = Bennett gate
```
Needle-movers that create new top-level Sprint Board rows trigger Bennett 1-click (anchor-to-existing-rows HARD RULE).

### PI-BA-NS-5 (HIGH) — REAL council auto-fire post-Step 4
After Step 4 (Sprint Board updates), MUST invoke council-skill on the Top-5 needle-mover ranking:
```
QUESTION: Are these the right Top-5 needle-movers given current FKI state?
NEEDLE-MOVERS: <verbatim ranked list with revenue/automation/consolidation declarations>
36-DIM SCORES: <green/yellow/red/black counts per section>
STAKES: Operational (4.0+ threshold) — these will be sprint-actioned this week
ASK: Validate ranking, surface missed items, ranked dispatch list
```
Council artifact saved to Drive `1dikjqZvnsWbbvVjNupiCWC-qN3fWfesV` as `council-business-audit-<YYYY-MM-DD>.md`.

### PI-BA-NS-6 (HIGH) — Diamond gate (Step 7 NEW)
After Step 4 + Step 5 council + Step 6 autopilot dispatch, invoke diamond-skill T1/T2/T3 on the audit artifact + Sprint Board state.
- T1 Adversarial: "Could we have missed a 🔴 in §1-§6 by looking at the wrong source?"
- T2 Recovery: "If today's Sprint Board fails, do we have the audit's gap-list readable to rebuild?"
- T3 Boundary: "Are the Top-5 needle-movers actually executable by the AI workforce this week, or did we surface fantasy?"
Diamond fail → block Bennett digest send + escalate to council reverse-audit-the-audit.

### PI-BA-NS-7 (MEDIUM) — Before/after delta (was: one-shot)
Step 8 output includes delta-vs-prior-audit table:
- Find latest prior business-audit artifact in Drive folder `1xlcN-2VIGgRGMLGYdJ4NUFBblCooFlsW` OR skills root
- Compare per-dimension scores (🟢🟡🔴⚫ counts)
- List dimensions that flipped from prior + flipped from green→red (regression flags)
- Compute total Advaita autonomy delta (105-pt rubric via self-audit-skill standalone Advaita-100 mode)

### PI-BA-NS-8 (HIGH) — Cohort routing block
```yaml
cohort_routing:
  cloud:
    detect: HOSTNAME contains "hyperagent" OR "madison"
    output_path: drive_skills_root + drive_folder
    output_method: SaveFile → PublishFilePublicly → GOOGLEDRIVE_UPLOAD_FROM_URL (parent = 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY)
    restricted_tools_check: SearchIntegrations({query: "highlevel"}) AND ({query: "meta ads"}) BEFORE any pull on these dimensions
    restricted_tools_if_unavailable: dispatch_to_leo_wo with payload (dims to refresh + 90-min SLA)
    leo_wo_destination: C0AKXT2S1T2, mention @U0AG6G4BEM9
    council_invocation: inline_5_advisor_synthesis
    council_artifact_dest: 1dikjqZvnsWbbvVjNupiCWC-qN3fWfesV
    state_path: brain.md cycle section + latest business-audit artifact in skills root
  cli:
    detect: presence of ~/.openclaw/state/
    output_path: ~/Desktop/audits/ + Drive backup
    output_method: write + rsync to Drive
    restricted_tools_check: skip (Ivan/Mack have direct API + browser_cookie3 + op CLI)
    council_invocation: real_council_skill_subprocess
    council_artifact_dest: ~/Desktop/audits/council/ + Drive folder
    state_path: ~/.openclaw/state/business-audit-last-cycle.json
```

### PI-BA-NS-9 (MEDIUM) — drive_file_id auto-populate
On first upload, scan YAML for `AUTO_POPULATED_ON_UPLOAD` → replace with the returned fileId → re-upload (replace=). Hard fail Cleanup dimension if PLACEHOLDER left in shipped file.

### PI-BA-NS-10 (LOW) — Mojibake fix
v1 contained Â§ / Ã encoding from broken UTF-8 round-trip. v2 rewrites from clean UTF-8 (§ characters explicit, em-dashes proper).

## Hard Rules (v2)
1. NEVER ask Bennett operational questions. Pull from QB / GHL / Meta / Notion / Drive.
2. NEVER attempt restricted tools without cohort_routing pre-check.
3. NEVER ship audit verdict without Step 5 REAL council + Step 7 diamond gate.
4. NEVER ship Top-5 needle-mover without revenue + automation + consolidation declarations.
5. NEVER leave drive_file_id = PLACEHOLDER / AUTO_POPULATED_ON_UPLOAD after upload.
6. NEVER write to ~/Desktop when cohort=cloud.
7. NEVER hardcode dependency fileIds — load by name + modifiedTime desc only.
8. NEVER skip before/after delta vs prior business-audit.
9. NEVER report a number without live source pull (QB=revenue, Meta API=spend, GHL=leads — when cohort can reach them).
10. NEVER suppress 🔴 / ⚫ items from Bennett digest because they're inconvenient.

---

## §1 FINANCIAL — 8 Dimensions

### Dim 1: Revenue Run Rate
**Source:** QuickBooks P&L (last 30 days) + GHL closed opportunities
**Metric:** Monthly commission revenue (target: $50K+/month for June 2026 Northstar)
**Pull:** QB MCP profit-loss-generator (cohort=cloud: direct; cohort=cli: direct)
**Red flag:** <$20K/month or >20% MoM decline
**Restricted-tool routing:** none (QB cloud-available)

### Dim 2: COGS & Gross Margin
**Source:** QB P&L — operating expenses vs revenue
**Metric:** Gross margin % (target: >70% after ad spend, tools, contractors)
**Red flag:** Margin <50% or tools/SaaS >$5K/month

### Dim 3: CAC per Channel
**Source:** Meta Ads MCP (spend) + GHL pipeline (leads by source)
**Metric:** Cost-per-acquisition by channel (Meta / broker / direct / organic)
**Formula:** Total ad spend per channel ÷ closed deals from that channel (last 90d)
**Red flag:** Meta CAC >$3K per closed deal, broker CAC >$500 per referral
**Restricted-tool routing:** if cohort=cloud AND METAADS connection=false → dispatch Leo WO for Meta refresh

### Dim 4: LTV vs CAC Ratio
**Source:** Calculated from Dims 1 + 3
**Metric:** LTV:CAC (target: >5:1)
**Red flag:** <3:1

### Dim 5: Cash Runway
**Source:** QB Balance Sheet (checking account ONLY — cash position rule)
**Metric:** Months of runway at current burn
**Red flag:** <2 months

### Dim 6: P&L vs Budget Variance
**Source:** QB P&L vs prior month and prior year
**Metric:** Line-by-line variance on top 5 expense categories
**Red flag:** Any category >30% over budget. **v2 update:** ad spend cap is now $400/day (brain v33+) — flag >$15K/month against $400/day envelope, not $500/day legacy.

### Dim 7: AR Aging (Commissions Owed)
**Source:** QB Accounts Receivable
**Metric:** Total commissions earned but not collected, aged by bucket
**Red flag:** Any commission >60d unpaid without documented dispute

### Dim 8: Ad Spend ROAS by Brand
**Source:** Meta Ads MCP (spend, CPL, leads) + GHL (deals closed by brand)
**Metric:** ROAS = commission revenue from brand ÷ ad spend
**Red flag:** ROAS <1.0x
**Known issue (2026-05-04, monitor):** SH ROAS 0.84x, FKI 2nd Opinion 15x
**Restricted-tool routing:** see Dim 3

---

## §2 SALES PIPELINE — 8 Dimensions

### Dim 9: Active Leads by Stage
**Source:** GHL pipeline (00-Sales pipeline BkDsA5sIzgsEon9ikJVW)
**Metric:** Count by stage
**Pull:** GHL MCP list_opportunities (cohort=cli direct; cohort=cloud → Leo WO)
**Red flag:** >200 leads in stage 1 no movement, >50 stale >14d
**Restricted-tool routing:** if cohort=cloud → dispatch Leo WO for §2 dim 9-16 pull (single WO covers all GHL dims)

### Dim 10: Conversion Rate (Funnel)
**Metric:** % conversion at each stage gate (target: 30% lead→discovery, 50% discovery→brand match, 20% brand match→FA)
**Red flag:** Lead→discovery <15%, brand match→FA <10%

### Dim 11: Avg Days Per Stage (Velocity)
**Metric:** Avg days each stage (target: discovery <3d from lead, FA <90d from discovery)
**Red flag:** Any stage >14d avg without strike trigger

### Dim 12: Leads by Source
**Source:** GHL UTM attribution (custom field mQiY5BHHi9gWVFHOTgQP)
**Metric:** % leads from Meta / broker / organic / direct
**Red flag:** Single source >80% of leads (concentration risk)

### Dim 13: Stale Pipeline Value at Risk
**Source:** GHL opportunities >30d no movement
**Metric:** Total deal value + count
**Red flag:** >$100K in stale pipeline without re-engagement plan

### Dim 14: Close Rate
**Metric:** FA signed ÷ discovery-done leads (last 90d)
**Target:** >15% post-discovery close
**Red flag:** <8%

### Dim 15: Revenue per Qualified Lead
**Metric:** Total commission ÷ total discovery-done leads
**Target:** >$3K

### Dim 16: Discovery-to-Close Cycle Time
**Metric:** Avg days from discovery-done to FA-signed (target: <90d)
**Red flag:** >120d

---

## §3 MARKETING — 6 Dimensions

### Dim 17: CPL by Campaign
**Source:** Meta Ads MCP
**Target:** <$150 CPL for FKI, <$75 for IC
**Red flag:** CPL >$300 on any campaign running >7d
**Restricted-tool routing:** Leo WO if cloud + Meta unverified

### Dim 18: ROAS by Brand
**Source:** Meta Ads + GHL
**Critical (monitor):** SH = 0.84x watch, FKI/2nd Opinion = 15x scale

### Dim 19: Ad Creative Performance
**Metric:** Top 3 vs bottom 3 by CPL + ROAS, creative type breakdown
**Red flag:** No creative refresh in >30d, bottom 3 CTR <0.5%

### Dim 20: Content Output Rate
**Source:** Slack #leo-auto + social analytics
**Metric:** Posts per week per brand (target: 5+ for active brands)
**Red flag:** <2 posts/week, no UGC in >14d

### Dim 21: Organic Reach Trend
**Source:** Metricool + MapKI Vercel analytics
**Metric:** Social follower growth, MapKI monthly visitors
**Red flag:** Flat/declining follower count over 30d

### Dim 22: Email/SMS Performance
**Source:** GHL campaign stats
**Metric:** Open rate (target: >25%), reply rate (>5%), unsubscribe (<1%)
**Red flag:** Open rate <15%, unsubscribe >2%

---

## §4 AI WORKFORCE / OPERATIONS — 6 Dimensions

### Dim 23: Agent Uptime
**Source:** Leo heartbeat (~/.openclaw/state/leo-heartbeat), launchctl
**Pull:** cohort=cli direct; cohort=cloud → query #leo-auto for last leo-heartbeat post + dispatch WO if stale
**Red flag:** Heartbeat >10 min old, bridge not in launchctl list

### Dim 24: Sprint Board Health
**Source:** Notion Sprint Board (335cf551-4fd3-8134-88de-c82a68622d7b)
**Metric:** Diamond rate this week, avg hours RED before resolution
**Red flag:** Diamond rate <60%, any task RED >24h without escalation

### Dim 25: Task Completion Rate
**Source:** Notion Sprint Board status counts this week
**Target:** (Diamond + Green) ÷ total rows >80%

### Dim 26: Skill Coverage vs Gaps
**Source:** SKILLS_MANIFEST.json (latest via fleet loader contract) vs Project Advaita domain needs
**Metric:** Skills per domain, gaps
**v2 update:** Use manifest-rebuild-skill output (canonical fileId resolved at audit time)
**Red flag:** Any Advaita domain with <3 active skills

### Dim 27: Bennett Time Audit
**Source:** Google Calendar API + Slack API
**Pull (v2.1 — concrete methodology):**
- Google Calendar: `list events for past 7 days (primary calendar), categorize by event title keyword:` sales-call keywords ["discovery", "brand match", "FA", "franchise agreement", "candidate"] → sales; admin keywords ["admin", "review", "1:1", "team", "sync"] → admin; remaining → deep-work/other. Sum hours per category.
- Slack: count messages authored by Bennett across all channels in last 7 days (Slack API `users.getPresence` + `search.messages?query=from:@bennett`). Flag if >30% messages in non-sales channels.
- cohort=cli: pull via Google Calendar MCP + Slack API directly. cohort=cloud: dispatch Leo WO for Calendar + Slack pull if restricted.
**Target by June 2026:** <5 hours total non-sales, >80% on sales calls
**Red flag:** >10 hours/week non-sales, >30% of all events are admin, <2 sales calls in 7 days

### Dim 28: Team Productivity Signals
**Source:** Slack #leo-auto posts (AI output volume), Notion task velocity
**Red flag:** Any employee channel with <2 AI interactions per week, task intake lag >1h

---

## §5 LEGAL / COMPLIANCE — 4 Dimensions

### Dim 29: Open Legal Cases
**Source:** Notion legal project (349cf551-4fd3-8180-9b69-d45bb530a2a8)
**Metric:** Count of open cases, nearest deadline
**Critical (monitor):** Default Cert case 250905143 — May 27 2026 filing deadline. BENNETT gate.
**Red flag:** Any case deadline <30d without active counsel engagement

### Dim 30: Contract Pipeline
**Source:** Notion + SignWell
**Metric:** Pending FAs waiting for Bennett signature, broker MOUs expiring in 90d
**Red flag:** Any FA sitting unsigned >5 business days

### Dim 31: IP & Trademark Status
**Source:** Notion / legal docs
**Red flag:** Any trademark lapse or active claim

### Dim 32: Compliance Gaps
**Source:** FDD Item 5/6/7 per brand, state franchise registration status
**Red flag:** Any state where FKI is soliciting leads without valid registration

---

## §6 TECHNOLOGY / INFRASTRUCTURE — 4 Dimensions

### Dim 33: Machine Health
**Source:** computer-health-skill latest (load by name)
**Pull:** cohort=cli direct via ~/.openclaw/workspace/scripts/machine-health.sh; cohort=cloud → query #leo-auto for last machine-health post
**Red flag:** Any red threshold, Tiffany unreachable, >2 Claude Code processes

### Dim 34: API Key / Secret Rotation Status
**Source:** 1Password FKI-Production vault, ~/.openclaw/secrets/
**Metric:** Age of each active API key vs 90-day rotation policy
**Red flag:** Any key >90d, any plaintext secret in Slack logs (auto-rotate immediately)

### Dim 35: Daily AI Cost Tracking
**Source:** ~/.openclaw/workspace/data/cost-tracking.db (Fred monitor)
**Metric:** Daily AI spend vs $20 autonomous cap (cohort=cli) / $30 thread cap (cohort=cloud)
**Red flag:** Any day >$15 (Tier 1 alert)

### Dim 36: Data Backup Status
**Source:** Google Drive, Notion, GitHub
**Red flag:** Any critical file not in Drive within 7 days, no GitHub commit in >14d

---

## AUDIT EXECUTION PROTOCOL (v2 — 8 steps)

### Step 0 — Cohort detect + dependency load + state pull
1. Detect cohort (cloud vs cli) per cohort_routing block.
2. Load dependencies by name + modifiedTime desc.
3. Pull latest prior business-audit artifact for delta comparison (Step 7).
4. Run pre-flight restricted_tools_check: SearchIntegrations({query: "highlevel"}) + ({query: "meta ads"}) — note has_active_connection state.

### Step 1 — Data Pull (parallel, ~10 min)
Pull all 36 dimensions in parallel. Restricted dimensions (cloud + tool unavailable) get queued for Step 1.5 Leo WO.

### Step 1.5 — Leo WO dispatch (cloud cohort only, when restricted)
If any restricted dim couldn't pull locally:
- Dispatch single Leo WO to #leo-auto (`C0AKXT2S1T2`, mention `@U0AG6G4BEM9`)
- Payload: list of dims needing refresh + 90-min SLA + handoff prompt for re-merging results
- Mark dims as "⏳ PENDING Leo WO ts=<ts>" in Step 2 scoring (NOT scored 🔴 just because we couldn't pull — pending != fail)
- **SLA enforcement (v2.1 NEW):** Record the WO dispatch timestamp. At Step 3 Needle-Mover Synthesis, re-check each ⏳ dim:
  - If Leo WO returned: merge results → score normally
  - If 90 min elapsed without return: re-classify dim as `⚪ UNAVAILABLE (Leo WO timeout ts=<ts>)` — NOT 🔴, NOT blocked. Log to #leo-coaches `C0AQ4KB1SA0`: "Business audit Step 1.5 timeout — dims [list] unavailable. WO ts=<ts>." Allow audit to proceed.
  - Diamond gate Step 7 MUST note any ⚪ UNAVAILABLE dims as a partial-coverage flag. Audit can still reach Diamond if ≤4 dims are UNAVAILABLE and all others scored.

### Step 2 — Score Each Dimension
For each of 36 dims:
- 🟢 Green — on target, no action
- 🟡 Yellow — mild concern, monitor or tweak
- 🔴 Red — action required this week
- ⚫ Black — critical, blocks Advaita or revenue
- ⏳ Pending — Leo WO outstanding (cloud cohort only)

### Step 3 — Needle-Mover Synthesis (Top 5)
Identify top 5 items by: (Advaita-domain impact) × (urgency) × (Bennett time freed) × (revenue floor pass). Each needle-mover MUST attach:
- `revenue_declaration` block (PI-BA-NS-2)
- `automation_declaration` block (PI-BA-NS-3)
- `consolidation_status` block (PI-BA-NS-4)

**v2.1 ADD — Sprint Board pre-search (anchor-to-existing-rows):** For each candidate needle-mover BEFORE scoring, run:
`NOTION_QUERY_DATABASE({database_id: "335cf551-4fd3-8134-88de-c82a68622d7b", filter: {property: "Name", text: {contains: <needle_mover_keyword>}}})`
Record any matching existing row IDs. Set `consolidation_status.consolidates_existing_rows = [<id list>]`. This ensures Step 4 Sprint Board updates anchor to existing rows rather than creating new ones.

Drop candidates failing any gate (revenue <$1K, manual-only, creates new top-level row without Bennett 1-click).

### Step 4 — Update Sprint Board
For each Top-5 needle-mover with clear AI-executable action:
- Anchor to EXISTING Sprint Board row where possible (per anchor-to-existing-rows HARD RULE)
- If no existing row → surface Bennett 1-click for new row creation (never auto-create)
- Update via NOTION_UPDATE_ROW_DATABASE only (NEVER NOTION_UPSERT_ROW_DATABASE on existing rows)

### Step 5 — REAL Council on Top-5 (v2 MANDATORY)
Invoke council-skill on Top-5 ranking. See PI-BA-NS-5 above for council input template. Council artifact saved to Drive `1dikjqZvnsWbbvVjNupiCWC-qN3fWfesV`.

### Step 6 — Autopilot Dispatch
For each council-validated needle-mover that's AI-executable, dispatch autopilot-skill. Track WO IDs in audit artifact.

### Step 7 — Diamond Gate (v2 NEW)
Invoke diamond-skill T1/T2/T3 on the audit artifact + Sprint Board state. Fail → block Bennett digest + escalate to reverse-audit-the-audit via council.

### Step 8 — Post Digest to #leo-auto + Bennett CEO Email + Save Artifact
```
🐿️ FKI BUSINESS AUDIT [YYYY-MM-DD]
Cohort: [cloud|cli]
🟢 X green | 🟡 Y yellow | 🔴 Z red | ⚫ N black | ⏳ P pending
Top 5 needle-movers (each: revenue $X · automation true/false · consolidates row IDs):
  1. ...
  2. ...
Sprint rows updated: N (anchor-to-existing)
Total projected revenue across Top-5: $X
Automation rate across Top-5: Y%
Bennett gates: [list | 0]
Council: <link to artifact>
Diamond gate: PASS/FAIL
Delta vs prior audit (<YYYY-MM-DD>): green +N, red -M, autonomy +X/105
```

Send Bennett CEO email via bennett-mode-skill v2.1+ (10-card format).

Save artifact:
- cloud: SaveFile → PublishFilePublicly → GOOGLEDRIVE_UPLOAD_FROM_URL to skills root + folder mirror with name `business-audit-<YYYY-MM-DD>.md`
- cli: write `~/Desktop/audits/business-audit-YYYY-MM-DD.md` + rsync to Drive

### Step 8.5 — Diamond Criteria for the audit RUN itself (v2)
The audit cycle is Diamond when:
1. All 36 dimensions scored OR ⏳ Pending with Leo WO dispatched
2. Top 5 needle-movers identified with revenue/automation/consolidation declarations
3. Step 5 REAL council artifact saved + council score ≥4.0
4. Step 7 diamond gate PASS
5. Step 8 digest posted + Bennett email sent (Gmail msgId logged)
6. Any ⚫ items have immediate triage started
7. Sprint Board updated (anchor-to-existing) with WO IDs
8. drive_file_id of v2 artifact NOT containing PLACEHOLDER text

## 🔴 CLOSING HARDGATE (v3 — Bennett directive 2026-05-22)

**Audit ≠ plan. Audit = fix.** See memory: `feedback_audit_plan_never_fixed_loop`.

Before declaring "business audit complete":
1. Every finding scored by council-skill → EXECUTE / SKIP / DEFER (council labels, does NOT gate)
2. EVERY EXECUTE → dispatch to autopilot-skill, capture receipt in `~/.openclaw/logs/autopilot-receipts.jsonl`
3. EVERY DEFER → create Notion WO under Sprint Board row, never silently drop
4. Verify: receipts_count_in_last_5min ≥ execute_count, else SKILL FAILED → reopen cycle
5. NEVER leave `## Priority Actions` / `## Recommendations` as final output. Either fixed, WO'd, or explicitly SKIP'd with reason
6. NEVER ask Bennett "want me to fix these?" — fix is implicit when audit invoked (see `feedback_never_ask_after_fix_directive`)

## Anti-Patterns (v2)

- ❌ NEW v3: Ending audit with unactioned `## Priority Actions` list (-5 — Bennett 2026-05-22)
- ❌ NEW v3: Asking re-approval after audit before dispatching fixes (-5)
- ❌ Skipping Step 5 REAL council (-5 — audit theater)
- ❌ Skipping Step 7 diamond gate (-3)
- ❌ Shipping Top-5 without revenue/automation/consolidation declarations (-3 each)
- ❌ Creating new top-level Sprint rows without Bennett 1-click (-5 — anchor-to-existing-rows HARD RULE)
- ❌ Using NOTION_UPSERT_ROW_DATABASE on existing rows (-5)
- ❌ Attempting GHL/Meta pulls on cloud cohort without restricted_tools_check (-3)
- ❌ Suppressing 🔴/⚫ items from Bennett digest (-5)
- ❌ Reporting numbers without live source pull (-3 — brain hard rule)
- ❌ Saving to ~/Desktop on cloud cohort (-3)
- ❌ Hardcoding dependency fileIds (-2)
- ❌ PLACEHOLDER drive_file_id remaining after upload (-3)
- ❌ Mojibake or broken encoding in shipped artifact (-2)

## Output JSON addition (v2)

```json
{
  "audit_run_id": "<uuid>",
  "timestamp": "<ISO>",
  "cohort": "cloud|cli",
  "leo_wo_ts": "<ts | null>",
  "scores": {"green": N, "yellow": N, "red": N, "black": N, "pending": N},
  "needle_movers": [
    {
      "name": "...",
      "advaita_domain": "...",
      "revenue_declaration": {...},
      "automation_declaration": {...},
      "consolidation_status": {...},
      "sprint_row_id": "...",
      "autopilot_wo_id": "..."
    }
  ],
  "council_artifact_id": "<drive_file_id>",
  "council_score": 4.46,
  "diamond_gate": "PASS|FAIL",
  "delta_vs_prior": {"prior_audit_date": "...", "green_delta": N, "red_delta": N, "autonomy_delta": N},
  "audit_self_grade": {"completeness": X, "correctness": X, "constraints": X, "revenue": X, "automation": X, "consolidation": X, "cleanup": X, "scope_discipline": X, "final": X.X},
  "bennett_email_msg_id": "<gmail msgId>",
  "drive_artifact_id": "<id — populated post-upload>"
}
```

## Cohort routing block (NEW v2)
```yaml
cohort_routing:
  cloud:
    detect: HOSTNAME contains "hyperagent" OR "madison"
    output_path: drive_skills_root + drive_folder
    output_method: SaveFile → PublishFilePublicly → GOOGLEDRIVE_UPLOAD_FROM_URL (parent = 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY)
    restricted_tools_check: SearchIntegrations({query: "highlevel"}) AND ({query: "meta ads"})
    restricted_tools_if_unavailable: dispatch_to_leo_wo
    leo_wo_destination: C0AKXT2S1T2, mention @U0AG6G4BEM9
    council_invocation: inline_5_advisor_synthesis
    council_artifact_dest: 1dikjqZvnsWbbvVjNupiCWC-qN3fWfesV
    state_path: brain.md cycle section + latest business-audit artifact in skills root
  cli:
    detect: presence of ~/.openclaw/state/
    output_path: ~/Desktop/audits/ + Drive backup
    output_method: write + rsync to Drive
    restricted_tools_check: skip
    council_invocation: real_council_skill_subprocess
    council_artifact_dest: ~/Desktop/audits/council/ + Drive folder
    state_path: ~/.openclaw/state/business-audit-last-cycle.json
```

## Self-Audit Checklist
<!-- Added 2026-05-28 — gatekeeper R2 directive: business-audit must have own checklist -->
1. [ ] SKILL.md frontmatter complete: name/version/drive_file_id/skills_root_mirror_id (no AUTO_POPULATED placeholder)
2. [ ] drive_file_id is non-empty and not placeholder: `1ChehVt8OMh7_L5Y3tZGioS9ynx4IRp7y`
3. [ ] Council verification ≥4.0: current council_verified = 4.46 ✓
4. [ ] Before/after delta tracking: business-audit-last-cycle.json exists at `~/.openclaw/state/`
5. [ ] Diamond gate (Step 7) included in each run — diamond-skill called with T7 receipt
6. [ ] Revenue gates included: apply/qualifier/booking metrics, attach rate, duplicate contact rate present in run output
7. [ ] LaunchAgent or cron wired for scheduled runs — or explicit `trigger: manual-only` in frontmatter

## Governance
- Canonical: Drive folder `1xlcN-2VIGgRGMLGYdJ4NUFBblCooFlsW` / SKILL.md
- Skills-root mirror: `business-audit-SKILL-v2.md`
- Edit pattern: SaveFile → PublishFilePublicly → GOOGLEDRIVE_UPLOAD_FROM_URL
- **v2 loader contract:** load by `name='SKILL.md' and parents contains '1xlcN-2VIGgRGMLGYdJ4NUFBblCooFlsW'` → sort modifiedTime desc → top 1.

## Version History
- **v1 (2026-05-04)** — Initial 36-dim audit by Ivan-CC. drive_file_id PLACEHOLDER (never populated). Mojibake from UTF-8 round-trip.
- **v2 (2026-05-15)** — Shared 8-dim audit-core rubric. Revenue/Automation/Consolidation gates on needle-movers. REAL council auto-fire. Diamond gate. Before/after delta. Cohort routing. Fleet loader contract. drive_file_id auto-populate. Mojibake cleaned. Council v20 4.46/4.0 PASS.

---

> **See also:** `self-audit-skill v1.5+` (shared rubric), `council-skill v20+` (Step 5), `diamond-skill v2.1+` (Step 7), `autopilot-skill v12+` (Step 6), `bennett-mode-skill v2.1+` (Step 8), `batch-overdrive-skill v1.2+` (Universal Completion Gates source).
