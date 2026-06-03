---
name: lean-startup-skill
aliases:
 - peter-thiel-skill
 - ycombinator-skill
 - startup-audit-skill
 - vc-lens-skill
display_name: Lean Startup Skill
version: 2.4
status: ACTIVE
created: 2026-05-20
updated: 2026-05-30
drive_file_id: 1kFiJLtk2MMekWr8uI0Ftsg_hoPU-0Jfh
author: Mack
patched_v2_4: "2026-05-30 — Audit r1: fix version header mismatch (title now v2.4), add conversion/booking-funnel trigger phrases, add Done= proof-link definition to ACTION OUTPUT FORMAT, add LSS Score Tracker Drive ID + Notion fallback, add Section 9 scoring rubric (___/10), add council-skill Drive ID to MODE D trigger."
patched_v2_3: "2026-05-27 — Adds Conversion Proof Over Activity Proof for Blueprint/revenue funnels: requires contact-attached conversion metrics, vanity-metric rejection, MVP tracking minimum, external friction score, proof velocity, and 14-day re-audit when booking/duplicate rates are unknown."
patched_v2_2: "2026-05-27 — Adds SELF_IMPROVEMENT_LOOP_SCORE for internal skills/systems: validated learning, response friction reduction, permanent fix durability, revenue/autonomy impact, and proof velocity."
description: >
  Master startup audit + creation benchmark skill for FKI and Advaita.
  Applies the combined frameworks of Eric Ries (Lean Startup), Peter Thiel
  (Zero to One), Paul Graham / Y Combinator, and 2026 VC investment
  criteria to score any FKI project, skill, system, or company initiative
  on a 0-100 scale. Produces a scored gap report, pivot/persevere verdict,
  and ranked action list. Four modes: AUDIT (score existing), CREATE (template
  new), INTERNAL TOOL (non-revenue systems), ADVERSARIAL (MODE D challenge).
  v2.2 adds SELF_IMPROVEMENT_LOOP_SCORE for per-response improvement loops.
  v2.1 adds: MODE D adversarial audit protocol, Revenue Attribution section
  (direct tie to deal decisions, $12,200 ROI / 24x), External Validation
  Template (5-step process any agent can run).

when_to_use: >
  Trigger phrases: "lean startup audit", "thiel audit", "startup audit",
  "vc lens", "ycombinator check", "audit this project", "is this lean",
  "score this skill", "what would a VC say", "peter thiel this",
  "are we building right", "validate this idea", "pivot or persevere",
  "what does success look like", "benchmark this", "startup score",
  "mode d audit", "adversarial audit", "challenge this assumption",
  "conversion audit", "booking funnel audit", "is this a vanity metric",
  "blueprint funnel audit", "check booking funnel", "are we tracking the right metrics",
  "funnel conversion check", "revenue experiment", "mvp check"
---

# Lean Startup Skill v2.4 — Master Protocol

## v2.3 Patch — Conversion Proof Over Activity Proof

When auditing Blueprint AI, qualifying forms, booking funnels, or any MVP intended to create sales calls, score conversion proof above activity proof.

### Required revenue experiment statement
```yaml
revenue_experiment:
  hypothesis: "We believe <prospect segment> will book a call with Bennett after <trigger> because <reason>."
  primary_conversion: <sent blueprint -> qualifier submit -> booked call -> held call -> closed revenue>
  actionable_metrics: []
  vanity_metrics_rejected: []
  minimum_tracking_standard_met: true|false
  next_experiment_window_days: <int>
```

### Scoring rules
1. **Conversion beats activity:** Calculator views, score completions, anonymous form fills, and modal opens are vanity unless tied to a known CRM contact and next action.
2. **Minimum viable tracking:** Before scaling traffic, the funnel must track sent blueprint, qualifier submit, booked call, appointment contact ID, held call, and closed revenue or mark each unknown.
3. **Learning loop:** Every experiment must answer what was learned from CRM data, not just whether the page worked technically.
4. **External friction score:** Captcha, calendar parsing, login walls, appointment attachment, and deploy-health issues reduce Build-Measure-Learn and Distribution scores.
5. **Proof velocity:** A future agent must be able to verify the experiment from one receipt/dashboard without rerunning the whole funnel.
6. **Pivot/persevere rule:** Persevere only if the next experiment is conversion-based. If only activity is measurable, verdict is Pause or Conditional.
7. **14-day re-audit:** If booking attach rate, duplicate rate, or held-call conversion is unknown, set a re-audit deadline within 14 days.
8. **Real revenue boundary:** A test booking validates mechanics, not willingness to buy. Do not call revenue validated until real prospects book/hold calls or pay.
9. **North Star filter:** Any added workflow that increases Bennett's operational load without increasing qualified booked calls is Red.
10. **Dashboard requirement:** A project cannot score 90+ unless the actionable metrics are visible in a dashboard, sheet, CRM report, or receipt with an owner.

If conversion data is not yet available, output PERSEVERE/CONDITIONAL only when the next experiment will collect it.

## NORTH STAR ANCHOR (Always Apply First)
FKI North Star: "Bennett takes calls and closes deals. Everything else runs itself."
Every score and verdict must be filtered through this. If a project moves
Bennett away from calls/deals or adds human ops load, flag it RED regardless
of other scores.

## v2.2 Patch — SELF_IMPROVEMENT_LOOP_SCORE

Use this add-on when auditing recap/self-audit/Angie/overdrive/handoff loops or any internal self-improving system.

Score 0-100 across five 20-point sections:
1. **Validated learning:** Does each defect become a testable hypothesis with a replay check?
2. **Response friction reduction:** Did it reduce Bennett repeats, corrections, waiting, or decision load?
3. **Permanent fix durability:** Is the canonical source changed, read back, and rollback-safe?
4. **Revenue/autonomy impact:** Does it advance revenue-driving autonomy or one Advaita domain?
5. **Proof velocity:** Can future agents verify the result quickly from receipts/logs without redoing the work?

Verdict:
- 85-100: keep and scale.
- 70-84: keep, but Angie tracks next regression.
- 50-69: revise before system-wide rollout.
- <50: reject or send through council Permanent Fix Approval Mode.

---

## FOUR MODES

### MODE A: AUDIT (external/revenue projects)
Input: Project name / skill name / system description + any known metrics
Output: Full 9-section scored report + Strategic Leverage + Decay Rate

### MODE B: CREATE
Input: Idea or problem statement
Output: Lean-validated project charter with hypothesis, MVP definition,
success metrics, and first experiment date

### MODE C: INTERNAL TOOL (v2.0)
Input: Internal system, agent, skill, or daemon
Output: 5-section scored report focused on time saved, bottleneck removed,
North Star proximity. Revenue/VC sections SKIPPED. Strategic Leverage
multiplier still applies.

MODE C scoring sections: (1) Problem Solved, (2) Bottleneck Removed,
(3) North Star Alignment, (4) Self-Improving, (5) Team Completeness.
Scale: 90-100=Critical infrastructure. 70-89=Strong. 50-69=Conditional.
Below 50=Question existence.

### MODE D: ADVERSARIAL AUDIT (v2.1 NEW)
Input: Project name + current LSS score + 3 strongest assumptions
Output: 3 adversarial challenges + refutation evidence requirements + score adjustment

MODE D process:
1. State the project's core thesis (1 sentence)
2. For each of the 3 core assumptions, build the strongest-possible counter-argument
3. State what evidence would refute each counter-argument
4. Assign risk level: HIGH (>50% probability assumption is wrong) / MED (20-50%) / LOW (<20%)
5. Apply score adjustment: HIGH = -3 pts, MED = -2 pts, LOW = -1 pt per challenge
6. Verdict: Does the MODE D-adjusted score change the PERSEVERE/PIVOT/KILL verdict?

MODE D rules:
- The adversarial position must be the STRONGEST possible counterargument, not a straw man
- At least 1 of the 3 challenges must attack the revenue/impact assumption directly
- If MODE D reduces score below 60, mandatory council review triggered — invoke council-skill (Drive: 1MpUHqm5dMHY1dF_kqm88pVCj7FT49ZYr) with MODE D output as input; do NOT ask Bennett to route this
- MODE D does NOT replace MODE A/C — it supplements the final score

---

## AUDIT TEMPLATE — FULL (MODE A)

### SECTION 0 — SCORE HEADER (v2.0)
Before scoring, declare:
- BLOCKED_SCORE: score as-of-today with all blockers in place
- POTENTIAL_SCORE: score if all Purple/blocker items resolved
- DECAY_RATE: "drops ~X pts/week if nothing happens" (estimate velocity)
- STRATEGIC_LEVERAGE: Does this project unblock 3+ other projects? YES/NO
  If YES: add +10 to final score (Strategic Leverage multiplier)

### SECTION 1 — REVENUE HYPOTHESIS
State the testable claim:
"We believe [customer] will pay [price] for [thing] because [reason]."
Status: VALIDATED / UNVALIDATED / PARTIALLY VALIDATED

### SECTION 2 — PROBLEM/MARKET FIT (Paul Graham / YC)
- Is this a real, urgent, demanded problem? (1-10)
- Do we have evidence people WANT this (not just think they do)?
- What is the customer archetype? (specific, named role/persona)
- "Do things that don't scale" check (v2.0 4-POINT SCALE):
  1 = Fully manual, correctly manual (pre-validation)
  2 = Manual but ready to automate (validation done)
  3 = Over-automated pre-validation (RED FLAG)
  4 = Correctly automated post-validation (IDEAL)
Score: ___/10

### SECTION 3 — ZERO TO ONE (Peter Thiel)
- Are we creating something genuinely NEW, not incremental? (0to1 vs 1ton)
- What is our contrarian secret?
- 4-Moat Score: Network effects ___/10 | Scale ___/10 | Proprietary tech ___/10 | Brand ___/10
- Are we building for last-mover advantage?
- What are we 10x better at than the nearest substitute?
Score: ___/10

### SECTION 4 — BUILD-MEASURE-LEARN (Eric Ries)
- What is the current MVP?
- What is the Build-Measure-Learn cycle time?
- Current VANITY metrics (list and eliminate)
- Replacement ACTIONABLE metrics (list)
- Growth engine (v2.0 STAGE-APPROPRIATE CHECK):
  Seed stage: STICKY or VIRAL only. PAID only if CAC is proven.
  Growth stage: all three valid.
  Declare: [Viral / Sticky / Paid] — Stage: [Seed/Growth/Scale] — Appropriate? YES/NO
Score: ___/10

### SECTION 5 — 2026 VC CRITERIA
- External paying customers: YES/NO
- LTV/CAC ratio: ___x (target 3x+)
- Gross margin estimate: ___% (target 70-80%)
- Capital efficiency: revenue per $1 AI infrastructure spend
- Regulatory risk: LOW / MEDIUM / HIGH
- Pilot to contract conversion rate (target 47%+)
Score: ___/10

### SECTION 6 — DISTRIBUTION AUDIT
- How does the product reach customers?
- Is the GTM motion validated or assumed?
- Who owns distribution?
- Time to first paying external customer: ___ days
- COMPETITIVE BASELINE (v2.0): What does the average competitor do here?
  Are we above / at / below industry baseline?
Score: ___/10

### SECTION 7 — ASSUMPTION MAP (v2.0 WITH KILL PROBABILITY)
Top 5 unvalidated assumptions + Kill Probability per assumption:
1. [Assumption] — Kill Probability: HIGH / MED / LOW
2. [Assumption] — Kill Probability: HIGH / MED / LOW
3. [Assumption] — Kill Probability: HIGH / MED / LOW
4. [Assumption] — Kill Probability: HIGH / MED / LOW
5. [Assumption] — Kill Probability: HIGH / MED / LOW

Risk Score: Count of HIGH kills. >=3 HIGH = project is HIGH RISK regardless of total score.

### SECTION 8 — PRE-MORTEM (v2.0 WITH KILL PROBABILITY %)
Top 3 kill scenarios + probability:
1. [Scenario] — Kill Probability: HIGH (>50%) / MED (20-50%) / LOW (<20%)
   Early warning signal: [specific observable indicator]
2. [Scenario] — Kill Probability: HIGH / MED / LOW
   Early warning signal: [specific observable indicator]
3. [Scenario] — Kill Probability: HIGH / MED / LOW
   Early warning signal: [specific observable indicator]

### SECTION 9 — TEAM COMPLETENESS
- Who owns this? (named human or agent)
- What skill/role is missing that could be fatal?
- North Star compatibility: moves Bennett toward calls/deals or away?

**Scoring rubric (v2.4):**
- 9-10: Named owner, no fatal gaps, fully North-Star-aligned
- 7-8: Named owner, minor skill gap, does not increase Bennett ops load
- 5-6: Owner unclear OR one fatal role gap OR marginally increases Bennett load
- 3-4: No clear owner OR multiple fatal gaps
- 0-2: No owner, pulls Bennett into ops, unworkable as-is
Score: ___/10

---

## SCORING RUBRIC

90-100: Ship it. This is the company.
75-89: Strong. Fix 2-3 gaps. Don't stall.
60-74: Conditional. Validate assumption map before scaling.
40-59: Caution. Major pivot candidate. Run Three-Brain.
Below 40: STOP. Fundamental PMF problem. Council required.

**Strategic Leverage Multiplier (v2.0):** +10 if project unblocks 3+ other projects.
Applied AFTER base score. Max 100.

**RE-AUDIT TRIGGER (v2.0 MANDATORY):**
Any project scoring below 60 → mandatory re-audit within 14 days.
Score is stamped with date. If no re-audit by deadline → post alert to Slack #leo-coaches (C0AQ4KB1SA0):
"[project] LSS score <60 re-audit overdue — stamped [date] — 14-day window expired. Action required."
Do NOT ask Bennett to send the message — post it directly via slack-comms-skill or gog Slack.

---

## PIVOT OR PERSEVERE VERDICT
Required output at end of every audit:
PERSEVERE / PIVOT / KILL / PAUSE — with 1-sentence reason.

---

## DUAL SCORE OUTPUT (v2.0)
Always report:
- BLOCKED SCORE: X/100 (today, with all current blockers)
- POTENTIAL SCORE: X/100 (if Purple/blockers resolved)
- DECAY RATE: X pts/week if stagnant

---

## ACTION OUTPUT FORMAT
Every audit produces exactly 5 actions:
| # | Action | Owner | Deadline | Done = |

**Done = definition (v2.4):** A verifiable proof artifact — HTTP 200 URL, GHL stage ID, Notion page link, Drive file ID, or CRM-attached evidence. "Done" is NEVER claimed without a proof link. If the action is not yet complete, Done = must contain the expected proof type (e.g., "GHL stage advance confirmed" or "Notion page ID"). Vague statements ("completed", "fixed") are not accepted.

---

## FINAL VERDICT SENTENCE
"Based on this audit, FKI/[project] should _____ by _____."

---

## REVENUE ATTRIBUTION SECTION (v2.1 NEW)

Every audit must include a Revenue Attribution assessment:

### RAI Score (Revenue Attribution Instances)
- Confirmed RAIs: [count] (rep cited this project's output in a deal action)
- Candidate RAIs: [count] (correlation found, causation not confirmed)
- RAI collection method: [interview / GHL stage correlation / Bennett citation]

### Dollar Attribution
- Direct revenue attributed: $___
- Waste avoided: $___ (projects killed before over-investment)
- Pipeline velocity improvement: ___% faster stage advance (if measurable)

### FKI Baseline Reference
- LSS portfolio audit is a named Advaita DFY deliverable ($25-50K tier)
- Each full portfolio audit = ~$12,200 value to client / 24x ROI on AI runtime cost
- Use this as floor for any internal tool audit ROI estimate

### Attribution Rules
- NEVER fabricate RAI counts. If 0 confirmed RAIs, state 0.
- Candidate RAIs require: signal timestamp + action timestamp + outcome evidence
- RAI confirmation requires all 4: (1) Reed/system output, (2) rep review, (3) action taken, (4) deal impact

---

## EXTERNAL VALIDATION TEMPLATE (v2.1 NEW)

Any agent can run this 5-step process to get external validation evidence:

### Step 1 — Define the One Assumption to Validate
Write: "We believe [customer segment] will [behavior] because [reason]."
Rules: One assumption. Falsifiable. Named customer segment.

### Step 2 — Select Validation Method (Match to Stage)
| Stage | Best Methods |
|---|---|
| Pre-launch | 5 customer interviews, landing page CTA, fake door test |
| Early (1-10 users) | Usage analytics, support tickets, NPS |
| Growth (10+) | Cohort retention, referral rate, LTV:CAC |
| Scale | A/B tests, pricing sensitivity, churn |

### Step 3 — Execute Minimum Viable Experiment
- Minimum sample: 5 for directional, 30 for statistical significance
- Time-box: max 14 days
- Document RAW data (not summaries)
- For FKI: GHL stage advancement = weak validation. Closed deal = strong.

### Step 4 — Score Against Falsification Criteria
- >=70% support assumption: VALIDATED (provisionally)
- 40-69% support: PARTIALLY VALIDATED
- <40% support: INVALIDATED (pivot/kill trigger)
- <5 data points: INCONCLUSIVE (continue)

### Step 5 — Update LSS Score
- Update BLOCKED score if assumption validated
- Add to Notion Sprint Board project row: "External Validation: [Method] | [Date] | [Status] | [Evidence]"
  (Sprint Board: https://www.notion.so/335cf5514fd3813488dec82a68622d7b — update project header field)
- LSS Score Tracker: search Drive folder 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY for "lss-score-tracker";
  if not found, create a Drive Sheet named "LSS-Score-Tracker" and log: project, score, date, status, evidence link.
- If INVALIDATED: mandatory council-skill review within 48h (council-skill Drive: 1MpUHqm5dMHY1dF_kqm88pVCj7FT49ZYr)

---

## INTEGRATION RULES
1. Any new skill via skill-creator-skill → must pass lean-startup-skill audit before ACTIVE status
2. Any new Notion project via notion-master-project-skill → lean-startup-skill score embedded in project header
3. North Star review → quarterly lean-startup-skill audit of entire company
4. Any project scoring below 60 → automatic Three-Brain flagged to Bennett
5. Skill scores tracked over time → delta shows movement toward or away from 100%
6. (v2.0) Projects with 3+ HIGH kill assumptions → auto-council flag regardless of total score
7. (v2.0) Re-audit deadline tracked in Notion project header alongside score + date
8. (v2.1) MODE D adversarial audit required for any project BLOCKED score >=65 before promoting to POTENTIAL
9. (v2.1) Revenue Attribution section required in all MODE A and MODE C audits
10. (v2.1) External Validation template must be cited when Section 2/5/6 score is assumed (not measured)

---

## CHANGELOG
- v2.4 (2026-05-30): Audit r1 — 6 permanent fixes: (1) version header corrected from v2.2→v2.4;
  (2) 8 conversion/booking-funnel trigger phrases added to when_to_use;
  (3) ACTION OUTPUT FORMAT "Done =" defined with proof-link requirement;
  (4) External Validation Step 5 — LSS Score Tracker given Drive folder ID + Notion Sprint Board URL;
  (5) Section 9 Team Completeness given 0-10 scoring rubric matching other sections;
  (6) MODE D council trigger given council-skill Drive ID + autonomy instruction;
  (7) Re-audit escalation replaced vague "Bennett DM" with #leo-coaches Slack post + skill path.
- v2.3 (2026-05-27): Conversion Proof Over Activity Proof patch for Blueprint/revenue funnels.
- v2.2 (2026-05-27): SELF_IMPROVEMENT_LOOP_SCORE add-on for internal self-improving systems.
- v2.1 (2026-05-21): R20 Agent 1 patch. MODE D adversarial audit protocol added (formally documented).
  Revenue Attribution section added (RAI tracking, $12,200/24x baseline, attribution rules).
  External Validation Template added (5-step, stage-appropriate, VALIDATED/INVALIDATED thresholds).
- v2.0 (2026-05-21): 10 improvements applied from R14 self-audit. MODE C added.
  Strategic Leverage +10 multiplier. Blocked/Potential dual scores. Decay Rate.
  Kill Probability per assumption. Competitive Baseline in S6. 4-point DTS scale.
  Kill Probability % per pre-mortem. Stage-appropriate engine check. Re-audit trigger.
- v1.0 (2026-05-20): Initial ship. 9-section audit, 2 modes, scoring rubric.

## ALIASES
lean-startup-skill = peter-thiel-skill = ycombinator-skill = startup-audit-skill = vc-lens-skill
All trigger the same protocol.
