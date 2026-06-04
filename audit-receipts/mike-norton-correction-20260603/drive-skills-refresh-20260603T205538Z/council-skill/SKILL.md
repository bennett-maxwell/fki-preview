---
name: council-skill
drive_file_id: 18edfLllHikArUABu7l_feBxFWfiLncAY
version: 33.0
last_updated: 2026-05-30
council_verified: v32 self-test passed 2026-05-30 (sub-agent advisors + separate-auditor step-enforcement + literal-50/50 hard-on + dual-ID sync, readback verified)
patched_v33: "2026-05-30 — Bennett-directed v33 rounds: fixed wrong Bennett DM id (U0A70BQBWP6->U08H07DMNTS); added Step 6.6 Token-Effectiveness Gate; wired out-of-band fail-closed ship gate (council-run.sh+council-verify-run.sh); added Step 7.5 calibration-contingent authority; slimmed version-archaeology to CHANGELOG. All pushed permanent to Drive, anchor-guarded."
patched_v30: "2026-05-29 — Mechanical Integrity Gates (council 4.13/5, rec 4). Converts the two weakest prose 'MANDATORY' steps into executable hard gates: (G1) telemetry write fail-open-with-alert before Step 7; (G2) same-gate-twice question-hash lookup; (G3) NEW anti-rubber-stamp calibration gate — trailing-20 pass-rate >90% forces one advisor to score <=3 with written justification. Root cause: 2026-05-29 audit found 138 council 'ran' markers vs 2 telemetry lines (~2% real execution) and 100% historical pass-rate (rubber-stamp)." 
patched_v28: "2026-05-27 — Adds Permanent Fix Approval Mode for self-improving loops. Repeated/high-severity self-audit findings are scored by 5 advisors, require 4.25/5, and output a reversible patch plan, proof plan, rollback path, and protected-action boundary before any permanent fix is claimed."
patched_v29_2: "2026-05-27 — Correction Final Verifier Gate. Permanent-fix approvals for false-fix, missed-skill, recap, self-audit, task-review, handoff, overdrive, or CEO-email correction loops must require `tools/fki_correction_final_verify.py <draft> --json` as final-response proof."
patched: "2026-05-10 v19 — HARD False Gate Auditor (Bennett directive 2026-05-10 from gate-audit thread). Step 4 now requires MANDATORY probe call + browser fallback + OAuth/cookie reuse BEFORE any BENNETT classification. Same-gate-twice = auto-escalate to permanent-fix project (no third-cycle gate allowed). Every gate annotated convertible_to_permanent + 30d deadline. Mentor lens block (v18) preserved unchanged. 2026-05-10 v18 — Mentor Lens Block. 2026-05-09 v17 — Step 6.5 Council Artifact Persistence."
description: >
  Run any question through 5 AI advisors who score it 0-5, recommend improvements, then run implementation
  triage with MANDATORY autonomous dispatch. v19 ADDS HARD False Gate Auditor: probe-call mandatory,
  browser/OAuth fall-through mandatory, same-gate-twice = permanent-fix escalation. v18 mentor lens
  block preserved.
  TRIGGERS: 'council this', 'run the council', 'war room this', 'pressure-test this', 'debate this'.
---

## v32 — SUB-AGENT ORCHESTRATION + GATEKEEPER STEP-ENFORCEMENT (2026-05-30, Bennett directive)

**Root cause of skipped steps:** all "MANDATORY" steps ran as prose in ONE context window — the model skips or fakes them (~2% real execution, 100% rubber-stamp pass-rate). Fix = borrow the patterns that already work in gatekeeper-skill + blueprint-ai-skill: separate sub-agents + an independent auditor + receipts.

**1. ADVISOR SUB-AGENTS (structural anti-sycophancy).** The 5 advisor seats run as 5 SEPARATE sub-agents (Agent tool), in PARALLEL, each returning structured JSON `{seat, score_0_5, single_failure_mode, recommendation, external_data_point}`. No seat sees another's output until Chairman. This makes "no advisor sees others' scores" structural instead of honor-system, and fixes "same model plays all 5 seats -> correlated errors."

**2. SEPARATE AUDITOR SUB-AGENT (gatekeeper invariant #5: auditor != producer).** After advisors return, a DISTINCT auditor sub-agent verifies the run against the STEP-COMPLETION LEDGER below. It did NOT produce any advisor score. Output: per row `{step, status: done|skipped|n/a, proof}`.

**STEP-COMPLETION LEDGER (auditor checks every row):**
- Step 0 question quality gate (stakes set)
- Step -0.75 Expansion & Pre-Mortem 50/50 (if stakes high) — fired + picks listed
- Step -1 Exa research brief (if "what to build")
- Step -0.5 mentor lens block (Hormozi/Vee/Robbins)
- Round 1: five ISOLATED sub-agent scores present
- G1 telemetry write / G2 same-gate hash / G3 calibration
- Step 4.0 probe-call proof on EVERY Bennett gate
- Step 5.2 Fresh Eyes + 5.3 Red Team + 5.5 Diamond T4

**3. STEP RECEIPTS.** Each step appends a one-line receipt to council-log.json. The auditor reads RECEIPTS, not prose claims (blueprint sub-agent-receipt pattern). No receipt = step didn't happen.

**4. SHIP GATE (gatekeeper loop).** The Step 6 verdict CANNOT be emitted unless the auditor returns (a) all mandatory rows = done/n-a AND (b) weighted score >= threshold. Any skipped mandatory row -> loop back and run it (max 3 rounds). Round 3 still failing -> HALT + post #leo-coaches "COUNCIL INCOMPLETE: <skipped steps>". Never emit a verdict over a skipped step.

**5. COMPOSITION — gatekeeper vs council (the answer to "do we need gatekeeper?").**
- council-skill = the DECISION/scoring engine (now self-enforcing via its own auditor sub-agent).
- gatekeeper-skill = the DELIVERABLE QA wrapper (worker -> auditor -> loop -> ship).
- For a DECISION ("should we do X?") -> council directly (it now polices its own steps).
- For a DELIVERABLE (email/blueprint/report) -> gatekeeper, which CALLS council as its scoring brain.
- They compose; you do not pick one. When council runs INSIDE gatekeeper/self-audit/overdrive it inherits AUDIT_ONLY and records `auditor_independent: true`.

---

## v30 — MECHANICAL INTEGRITY GATES (rec 4, council 4.13/5, 2026-05-29)

The prior "MANDATORY" telemetry + same-gate steps were prose and ran ~2% of the time (audit: 138 "ran" markers vs 2 telemetry lines). These three gates are now executable bash, run on EVERY council invocation. A council run that skips them is INCOMPLETE.

**G1 — Telemetry write (fail-open + alert) — runs at Step 6, BEFORE Step 7:**
```bash
LOG=~/.openclaw/workspace/logs/council-telemetry.log; mkdir -p "$(dirname "$LOG")"
LINE="COUNCIL RUN | $(date -u +%FT%TZ) | domain=$DOMAIN | score=$SCORE | threshold=$THRESH | $VERDICT | gates_caught=$GC | dispatched=$DN | false_gates_rejected=$FG"
echo "$LINE" >> "$LOG" || echo "TELEMETRY_WRITE_FAIL"   # fail-OPEN: never block the verdict on a disk error
tail -1 "$LOG" | grep -q "$(date -u +%F)" && echo "G1 OK" || echo "G1 MISS -> post #leo-coaches TELEMETRY_WRITE_FAIL"
```
Fail-open is deliberate: a telemetry disk error must NOT cause a skipped council run (the old failure mode). Missing line -> alert, don't halt.

**G2 — Same-gate-twice (real hash lookup) — runs before any BENNETT classification:**
```bash
QH=$(echo "$GATE_TITLE" | tr '[:upper:]' '[:lower:]' | { md5sum 2>/dev/null || md5; } | cut -c1-8)
PRIOR=$(grep -c "\"question_hash\": *\"$QH\"" ~/.openclaw/workspace/council-log.json 2>/dev/null || echo 0)
if [ "$PRIOR" -ge 1 ]; then echo "SAME_GATE_TWICE -> auto-escalate to PERMANENT-FIX (autopilot WO), NOT a 3rd Bennett gate"; fi
```
Mechanical version of Step 4.0d — stops recurring defers (e.g. "Advaita v2", "SOUL.md model line") from re-surfacing to Bennett every cycle.

**G3 — Anti-rubber-stamp calibration gate — runs at Round 1:**
```bash
LOG=~/.openclaw/workspace/council-log.json   # unified path (was state/council-log.jsonl — drift fixed v31)
PASS=$(tail -20 "$LOG" 2>/dev/null | grep -c '"passed": *true')
TOT=$(tail -20 "$LOG" 2>/dev/null | grep -c '"passed"')
if [ "$TOT" -ge 10 ] && [ $((PASS*100/TOT)) -gt 90 ]; then
  echo "CALIBRATION: trailing pass-rate $((PASS*100/TOT))% > 90% -> at least ONE advisor MUST score <=3 this run with written justification, or Chairman documents why a near-unanimous PASS is genuinely warranted."
fi
```
Root cause: 100% historical pass-rate = rubber-stamping, not filtering. A real 5-advisor adversarial council rejects/sends-back ~20-30% on first pass. G3 forces that distribution to be earned.

**All three appear in the Step 6 Verdict footer: `Integrity gates: G1 <ok|miss> . G2 <n prior> . G3 <fired|n/a>`. Absent = INCOMPLETE run, flagged by Angie.**

---

## v26 Patch — AUDIT_ONLY Mode

When invoked by Business Audit, Angie Audit, Self Audit, Gatekeeper, Batch Overdrive, or any "A-Z rerun/gap scan" task, council-skill must default to `AUDIT_ONLY=true` unless the caller explicitly requests dispatch and the action is not protected.

In `AUDIT_ONLY=true`:
- Score, challenge, and recommend only.
- Do not post to Slack, DM Bennett, dispatch autopilot, mutate Sprint Board, mutate Drive, send email, mutate GHL/QB/Meta, deploy, delete, change credentials, touch payroll/legal documents, or change ad spend.
- If the question mentions Advaita 100, read the current metric source-of-truth and `advaita-gates-check.json`; do not report progress or Diamond unless the source proves it.
- Any protected action exits as a Yellow/Purple gate with owner, proof needed, and next safe probe.

## v28 Patch — Permanent Fix Approval Mode

Trigger when recap-skill or self-audit-skill reports a high-severity defect, repeated same-pattern defect, false-done/proof failure, missed mandatory skill, missed recap/handoff/closeout, or durable behavior change request.

Set:
```yaml
PERMANENT_FIX_APPROVAL_MODE: true
threshold: 4.25
protected_actions: still_blocked
```

Required advisor questions:
1. Is this a real repeat/system defect or a one-off?
2. What is the smallest reversible permanent fix?
3. Which canonical source must change: Drive skill, AGENTS.md, Notion SOP, script, memory, or dashboard?
4. How will the fix be verified now and replay-tested later?
5. What could this break, and what is the rollback path?

Approval output must include:
```yaml
permanent_fix_verdict: approve | reject | partial
score_avg: <0-5>
canonical_sources_to_patch: []
protected_actions_required: []
proof_required: []
rollback_path: <specific>
followup_audit_owner: angie-audit-skill | self-audit-skill | business-audit-skill
```

If score_avg <4.25, do not patch the durable source. Return the highest-confidence current-response correction only.

## v29.2 Patch — Correction Final Verifier Gate

When council approves a permanent fix for a repeated false-fix/proof failure, the proof plan must include a strict final-draft verifier command:

```text
python3 tools/fki_correction_final_verify.py <draft> --json
```

Do not approve completion wording unless the exact final answer passes that command and side-effect claims have separate receipts.

## Dependencies
Preload in parallel via mcp__claude_ai_Google_Drive__read_file_content (verify modifiedTime — flag any > 30d as STALE):
- diy-skill v3 (fileId: 19mQxNIPy-viPJYfd89QTLrpX73q_Vo8M) — capability inventory + fall-through chain
- troubleshoot-skill (fileId: 1I13dA9Tcn-N0ETowd6dhZG46F5Wu3krK) — diagnostic protocol
- company-context-skill (fileId: 1NnNpscIwJLTN4jRsFZM-bM8rZKhw4XIT) — FKI context
- agent-routing-skill (fileId: 1Px_-8sR_sfUESs2DbaSfWKXjI9ZTdv1F)
- tiffany-skill (fileId: 1H1oVidUlwoGckehSfgmI1_ozSex5-rJ9)
- slack-comms-skill (fileId: 11UEN5S1sCiGSLZeeaxKng8hUuk_SJS53) — Slack channel IDs + routing
- boot-skill (fileId: 1uSrUQcip9E4Wj6bvpDg9_6wVOuzmowGo)
- diamond-skill (fileId: 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT) — mandatory Step 5.5
- strike-skill (fileId: 1mBRI0RKEuuvLF5Oh3Gdrl-BLhGrsZhix)
- three-brain-skill (fileId: 1XExmjUTIvLwSUg2eIErgHFxDz1AMjn2j)
- six-brain-skill (fileId: 1oib7mlTETDzHW632aVdUeHK5T7bpW-Sh)

**Brain-Skill Selection (IMP-024):**
- Stakes = Operational or Revenue → three-brain-skill
- Stakes = Legal/Financial($5K+) or Irreversible → six-brain-skill (mandatory — adds Skeptic + Historian + Consequence lenses)
- Document which brain-level was used in Step 6 Verdict: "Brain level: three-brain | six-brain"
- memory-skill (fileId: 11N3WxEHenqDoidLawqfh1m-AfeU0G8Pu)
- check-in-skill (fileId: 1eGKuEsznUy9haosNex4qoCAfi1liPOmo)
- caveman-skill (fileId: 1YvK8Gi9RmbBoZjXEY6D0fV0P51Dy38bC) — voice
- autopilot-skill (fileId: 10KBx34OrzdlX0_RN9x8zqNvQEprLdQow) — Execution Boundary Gate + permanent-fix escalation
- tools-skill (fileId: 1OcbKl-E6tfMhhQMRq9h6RYaBiZIUwkPR)
- push-harder-skill v4 (fileId: 1Uyeu1F5gSn8QOarp-AzV-5PtFFZxEq6Q) — sprint dispatch
- idea-expander-skill (fileId: 1V0w5HU28-mw135p0ZCdR_u0s8OO8gTWU, folder: 18aYZCRDXg1Aqt0MqeLCSiBQVwBty2NX8) — Step -0.75 execution engine for 50-expansion + 50-pre-mortem; always-available version without stakes gate
- gate-lifecycle tracking is INLINE (v31): no separate skill required. Lifecycle fields (same_gate_count, permanent_fix_deadline) are written directly into council-log.json. The unwritten gate-lifecycle-skill.sh is OPTIONAL, never a hard dependency.
Execute their workflows in full when referenced below.

### Pre-Flight Dependency Check (MANDATORY before Step -1)
After preloading dependencies, confirm each loaded successfully. If gate-lifecycle-skill is NOT found:
1. Run: bash ~/.openclaw/scripts/gate-lifecycle-skill.sh (if it exists, proceed)
2. If script missing: create ~/.openclaw/workspace/council-log.json manually before proceeding
3. Log to #leo-coaches: 'COUNCIL PREFLIGHT: gate-lifecycle-skill missing — using fallback log'

**Version Gate (IMP-021):** Check frontmatter of loaded council-skill SKILL.md. If version < 25: STOP. Reload from Drive (fileId: 18edfLllHikArUABu7l_feBxFWfiLncAY) before proceeding. Log version mismatch to #leo-coaches: "COUNCIL VERSION STALE: loaded v<N>, required v25+. Reloaded."

## Step 0 — Question Quality Gate (IMP-029)
Before any work begins, verify the question has:
- (a) Clear success criterion: "What does DONE look like?"
- (b) Defined scope: "What's in/out of this decision?"
- (c) Identified stakes level: Operational / Revenue / Legal / Irreversible

If ANY element is missing, return:
"COUNCIL REFRAME NEEDED: [specific missing element]. Restate question with:
- Success: [what success looks like]
- Scope: [what this covers / doesn't cover]
- Stakes: [Operational | Revenue | Legal | Irreversible]"

Do NOT proceed until question passes Step 0. A well-framed question = 80% of council value.

---

## Step -0.75 — EXPANSION & PRE-MORTEM GATE (v31 — Bennett 50/50 directive 2026-05-30)

**Fires ONLY when Step 0 set stakes in {Revenue/Product, Legal/Financial, Irreversible}.** Operational / low-stakes questions SKIP this gate (fast-path — keeps trivial councils cheap). Gating is deliberate: Bennett's own prior directive was "bake it in but gate to Revenue/Irreversible, measure the delta first." An always-on 100-item sweep on every call worsens instruction-overload (the root cause of the ~2% real-execution problem).

**When fired, BEFORE Round 1 scoring, generate:**
- **EXPANSION SET** — exactly **50** distinct ways to expand / improve / 10x the idea (dedupe near-identicals).
- **PRE-MORTEM SET** — exactly **50** distinct ways the idea breaks, fails, or is terrible (dedupe near-identicals).

Then the 5 advisors **pick >=10 from EACH set** (the strongest) to implement / counteract. Those picks become:
1. the candidate **OPTION SET** Round 1 scores (fixes single-option bias — the best idea now enters the room),
2. direct seed for **Seat 1 Contrarian** (pre-mortems) and **Step 5.3 Red Team**.

Output: the full 50+50 (terse, numbered) THEN a compact decision table — **top 10 expansions to implement + top 10 pre-mortems to counteract**, one-line rationale each. Token cost is accepted; coverage > brevity here.

**MEASURE-DELTA-FIRST (Bennett prior directive, preserved):** for the first 15 high-stakes councils after v31, log `premortem_delta` to council-log.json — decisions_changed + false_gates_caught WITH vs WITHOUT this gate. This gate is HARD-ON for all high-stakes councils as of v31.1 (Bennett 2026-05-30: 'get a working system today, 50s is the way'). It DOES feed the option set + Contrarian + Red-Team and its picks must be addressed in the verdict. `premortem_delta` is still logged for tuning, but logging never downgrades the gate to optional.

---

## North Star (v19 — Bennett directive 2026-05-10 gate audit)

**Bennett's Brain replica CEO — but better, with ZERO false gates.** Combines 5 isolated advisors (the way Bennett actually thinks) with 3 mentor lenses (Alex Hormozi distribution / Gary Vee attention / Tony Robbins state-of-mind) on **EVERY** council run, PLUS a HARD False Gate Auditor that requires probe-call proof before any Bennett classification. The previous v18 auditor was a passive checklist; v19 makes it a forcing function. Same gate appearing in 2+ cycles = auto-escalate to permanent-fix project, not gate #3.

This skill is the canonical decision layer for the entire Advaita stack. Bennett sees a gate ONLY when something is genuinely biometric / legal sign-off / financial>$1K irreversible / identity / external contract — not when a token expired or a login flow needs cookie injection.

## Loop-Improvement Add-Ons (v27.1 — 2026-05-27, Tier-B #8 + #14)
- **EVAL-SET HOOK (#8 — eval-driven dev):** When council scores a recurring decision type, it MAY load a saved rubric `~/.openclaw/state/council-evalset/<decision-type>.json` (fixed criteria + prior scores) and grade against it instead of ad-hoc. If a rubric exists, cite it in the verdict; if not, the verdict's criteria seed the rubric. Anchors scoring to a fixed eval, not vibes.
- **LLM-AS-JUDGE INDEPENDENCE (#14):** When council is the *auditor* inside gatekeeper/self-audit, advisor seats MUST be distinct from the workers that produced the artifact (auditor ≠ producer). Record `auditor_independent:true`. Mirrors gatekeeper invariant #5.

---


## Corrected Capability Matrix (v14, preserved)

```
SANDBOX (Ivan/Mack execute now) (execute now, no dispatch needed):
  API: NOTION_, GOOGLEDRIVE_, GMAIL_, QUICKBOOKS_, METAADS_, LINKEDIN_, GITHUB_
  GHL API: Ivan CC direct via Bash (gateway.env token — /opportunities/search, /contacts/, /notes). GHL UI-only actions (workflow publish, pipeline renames): Kay. Do NOT route GHL API calls to Leo — Ivan CC handles these directly.
  BROWSER: BrowserSession, BrowserAction, BrowserNavigate, BrowserObserve, BrowserExtract
  RESEARCH: ExaSearch, ExaContents, ExaAnswer, ExaResearch
  MEDIA: GenerateImage, GenerateAudio, GenerateVideo
  COMMS: SlackSendMessage, SlackGetChannelHistory

CLI-DIRECT — IVAN CC or MACK (execute directly if ON_IMAC or ON_MACK, else dispatch to Leo):
  Ivan CC / Mack: Bash, Python, cron, git, SSH, Browser-Use, composio SDK, GHL API
  Both have browser_cookie3 (decrypt Chrome cookies via macOS keychain)
  Both have op CLI (1Password secret injection)

HUMAN DELEGATION (non-AI execution):
  Madison Lanz — operational workflows [FIRST HUMAN TIER]
  Kay Labang — admin UI, GHL settings, platform configs
**Madison Lanz routing criteria:** operational workflows, scheduling, document prep, follow-up tracking, calendar access, meeting coordination, anything requiring human presence in a process.
**Kay Labang routing criteria:** GHL UI actions (workflow publish, pipeline stage rename, form edits), admin platform config, account-level settings. If ambiguous: prefer Madison unless explicitly GHL-UI-specific.
  Bailey + Keith — sales rep activities
  Bennett — biometric, financial >$1K, legal, irreversible, identity ONLY [GATED HUMAN]
```

---

## Step -1 — CAPABILITY INVENTORY + RESEARCH (MANDATORY)

### Tool Registry Gate (v29 — added 2026-05-27)

If the decision involves a connector, API, CLI, Slack/Notion/Drive/Gmail/GHL/Vercel/GitHub/Cloudflare/OpenAI/Meta/QuickBooks/Apollo/ElevenLabs/Browser tool, credential, deploy, send, or cross-agent capability split, load `tools-skill` before scoring.

Council output must include:
- Which agent/tool surface can do the work.
- Whether the tool is read-only, dry-run, no-send, approved-live, or blocked.
- Credential rotation/probe requirement if relevant.
- Whether a dedicated `{connection}-skill` exists or should be created.
- Gatekeeper approval boundary for protected actions.

If `tools-skill` is unavailable, score the proposal as provisional and mark the missing registry proof as a blocker.

**Sub-step A:** → Execute diy-skill v3 — load capability inventory + fall-through chain. → Execute troubleshoot-skill if question is about a failure.

**Sub-step B: Exa Research** (mandatory for "what to build/do next" questions):
Run 3 Exa searches BEFORE Round 1.

**Exa Research Template (IMP-017 — mandatory query structure):**
Query 1: "[question topic] best practices [current year]"
Query 2: "[question topic] failure modes case studies"  
Query 3: "[question topic] competitive landscape OR alternatives"

Paste top 3 results per query into Research Brief. Minimum 1 external data point per advisor Round 1 response.
Queries that return zero results = flag RESEARCH GAP in brief.

**Sub-step C: Vision domain + stakes check.**

**Sub-step D: Context loads** (conditional).

**Sub-step E: Dependency freshness check** (>30d → STALE flag).

**Sub-step F (NEW v19): Same-Gate-Twice Check.** Read council-log.json. If question hash matches a prior council artifact's BENNETT classification in last 14 days, flag SAME-GATE-TWICE in Research Brief. Round 1 advisors must explicitly address why this is not auto-escalated to permanent-fix project.

---

## Step -0.5 — MENTOR LENS BLOCK (v18 — preserved, MANDATORY EVERY RUN)

### Mentor Lens Block (fires on EVERY council run — mandatory)
After each Round 1 advisor delivers their score, apply these 3 lenses:

| Lens | Question to ask | Focus |
|------|----------------|-------|
| Alex Hormozi (Distribution) | "What's the $100M version of this? Does this scale or does it require more humans?" | Revenue leverage, volume, irresistible offer |
| Gary Vee (Attention) | "Where is the attention? Does this put us where the audience already is? What would a $0 budget version look like?" | Organic reach, content, platform-native |
| Tony Robbins (State of Mind) | "Is the decision being made from fear or from certainty? What does the BEST version of Bennett decide here?" | Peak state, limiting beliefs, identity-level commitment |

For each lens: write 2-3 sentences applying it to the question at hand. This fires AFTER Round 1 scores are collected, BEFORE Chairman Synthesis. Tag each advisor response with the lens that most applies to their recommendation.

---

## Round 1 — ANTI-SYCOPHANCY ISOLATION PROTOCOL (v18 — preserved)

### Round 1 — Five Isolated Advisors (score 0-5, ANTI-SYCOPHANCY: no advisor sees others' scores until Step 5)

**Seat 1: The Contrarian**
Role: Challenge every assumption. Find the fastest path to failure. Assume the plan is wrong.
Scoring: 0 = obviously wrong, 5 = despite my best efforts I can't break this
Prompt: "What's the single most likely reason this fails within 90 days? What assumption is being made that no one is questioning?"

**Seat 2: The Financial Realist**
Role: Model the money. Revenue impact, cost, opportunity cost, cash timing.
Scoring: 0 = burns money, 5 = best ROI of all options on the table
Prompt: "What does this cost (time + money + attention)? What's the realistic revenue outcome in 30/90/180 days? What's the opportunity cost of NOT doing this?"

**Seat 3: The Expansionist**
Role: 10x the vision. What's the biggest version? What adjacent markets does this unlock?
Scoring: 0 = dead end, 5 = platform-level unlock
Prompt: "If this works perfectly, what does it enable that we haven't considered? How does this change what's possible in 6 months?"

**Seat 4: The Outside Expert**
Role: Domain specialist who has seen this exact problem before. Pattern match to industry best practices and known failures.
Scoring: 0 = violates basic domain principles, 5 = best-in-class execution
Prompt: "Who has solved this problem already? What do they do that we're not doing? What mistake does everyone make here?"

**Seat 5: The Executor**
Role: Operations. Implementation reality check. Dependency map. What breaks when this goes live?
Scoring: 0 = impossible to implement, 5 = clear path, right team, right tools
Prompt: "Step by step, who does what by when? What's the first thing that breaks? What do we need that we don't have?"

**Response Limits (IMP-012):**
- Each advisor: 200-word cap per Round 1 response
- Mentor lens citation: adds 50 words max
- Chairman Synthesis: 300 words max
- Total council output target: <1,500 words

**Weighted Scoring:** Contrarian × 1.2, Financial × 1.3, Expansionist × 0.9, Outside Expert × 1.1, Executor × 1.0. Sum / 5.5 = weighted council score.

### Anti-Sycophancy Hard Rule (IMP-010)
If all 5 advisors score within 0.3 points of each other AND all recommend PROCEED on the first pass: Chairman MUST flag CONSENSUS RISK and trigger a mandatory 60-second adversarial reframe.

Adversarial reframe prompt: "Assume this decision is WRONG. You have 60 seconds to find the one thing everyone missed. Go."

If adversarial reframe still finds nothing: document "CONSENSUS VERIFIED — adversarial challenge passed" in the verdict. 
Unanimous agreement without challenge = the most common signature of group-think.

---

## Round 2 — Implementation Triage + Dispatch

### GATE-VERIFY-REQUIRED (2026-05-27 — fleet-wide protocol)
Before ANY item is classified as a human gate / BENNETT / HUMAN OPEN:
1. Credential/token gate? → `~/.openclaw/bin/token-probe.sh <service>`. HTTP 200=NOT a gate. 401=human gate confirmed. 403=fix-call (not human). 429=wait.
2. Vault check first: `notion-fetch 341cf5514fd381fe993de8add7eb265e`.
3. Prior session / handoff doc? → NEVER trust. Re-probe live.
4. True human gates (no probe needed): biometric · legal · >$1K · identity · external contract.
HARD RULE: gate with no live probe receipt = SUSPECTED (not confirmed human gate).

### Step 4 — Classify each implementation step

| Tier | Examples | Agent | Action |
|------|---------|-------|--------|
| SANDBOX-API | Notion, Drive, Gmail, QB, Meta Ads, LinkedIn, GitHub | Ivan/Mack | Execute NOW |
| SANDBOX-BROWSER | Web UI click, form fill, login flow, visual check | Ivan/Mack BrowserSession | Execute NOW |
| SANDBOX-RESEARCH | Exa, ExaContents, knowledge lookup | Ivan/Mack | Execute NOW |
| CLI-DIRECT | Bash, cron, LaunchAgent, git, GHL API, SSH, browser_cookie3, op inject | Ivan/Mack direct OR Leo dispatch | Execute/Dispatch NOW |
| BENNETT | Biometric / legal sign-off / financial >$1K / irreversible / identity / external contract | Weekly digest | ONLY after Step 4.0 audit PASS |

### Step 4.0 — HARD FALSE GATE AUDITOR (NEW v19 — MANDATORY before any BENNETT classification)

Before ANY step is classified BENNETT, the advisor proposing it MUST embed proof in their recommendation:

**4.0a — Probe Call Proof (MANDATORY)**
- Execute the actual API call against current creds and paste response code (e.g. `GET /me 200 OK` or `GET /contacts 401`).
- If probe returns 200/2xx → step is NOT broken, classify as SANDBOX-API.
- If probe returns 401/403 → continue to 4.0b.
- No probe response embedded = Step REJECTED at Chairman Synthesis (Step 5).

**4.0b — Browser Fall-Through Proof (MANDATORY if 4.0a returns 401/403)**
- Attempt BrowserSession with cookie inject (Hyperagent native).
- If on Ivan/Mack: attempt browser_cookie3 to decrypt user's Chrome cookies for the target domain.
- If Composio has an existing OAuth for the target product (Google → NotebookLM/Docs/Drive, LinkedIn → Sales Nav, GitHub → API): attempt token reuse.
- Paste screenshot URL OR session ID as proof.
- All 3 browser attempts fail = continue to 4.0c.

**Financial Sub-Tiers (IMP-003):**
- $0-$999: SANDBOX-AUTO (no notification needed)
- $1K+: Bennett APPROVE required before execute (irreversible spend — matches CLAUDE.md 'spend >$1K' hard gate). NO auto-proceed on irreversible spend.
- (Reversible spend $1K-$5K with clean rollback may notify+24hr-auto per Auto-Default-Option-A; IRREVERSIBLE spend never auto-proceeds.)
Add `irreversible_impact_score: 0-3` to every gate row (0=reversible, 1=notify, 2=approve, 3=biometric).

**4.0c — Gate Justification Template (MANDATORY for BENNETT)**
```
GATE: <one-line description>
TRIGGER (pick exactly one):
  [ ] Biometric (FaceID/TouchID/Yubikey)
  [ ] Legal sign-off (FDD / contract / counsel)
  [ ] Financial irreversible >$1,000
  [ ] Identity verification (KYC / SMS code to Bennett's phone)
  [ ] External contract / NDA signature
EVIDENCE: <1-line why no other trigger applies>
PROBE_RESPONSE: <pasted from 4.0a — required>
BROWSER_FALLBACK_ATTEMPTED: <yes/no + proof URL — required>
CONVERTIBLE_TO_PERMANENT: <true/false>
PERMANENT_FIX_PROPOSAL: <one-line — required if convertible=true>
SAME_GATE_COUNT: <N from council-log lookup>
PERMANENT_FIX_DEADLINE: <creation + 30d ISO>
```
Missing any field = step REJECTED at Step 5.

**4.0d — Same-Gate-Twice Auto-Escalation (NEW v19)**
- If `SAME_GATE_COUNT >= 2`: this is NOT a BENNETT classification. Auto-classify as PERMANENT-FIX project. Dispatch to autopilot-skill via Leo WO. No third-cycle Bennett gate allowed.
- Chairman synthesis must include line: "Same-gate-twice escalation triggered for: <gate-name>. Autopilot WO dispatched."

**FALSE GATE AUDITOR (v14, deprecated by 4.0 — kept for reference only):**
~~Before any BENNETT classification, verify in order: 1. Ivan/Mack API? 2. Ivan/Mack Browser? 3. CLI-DIRECT?~~ — v18 passive checklist replaced by v19 hard auditor above.

**SCORE FLOOR GATE (mandatory before any dispatch):** If council score < 3.0: NO dispatch. Post to #leo-coaches 'COUNCIL LOW CONFIDENCE — <score>/<threshold>'. If 3.0-3.4: SANDBOX-RESEARCH dispatch only. If ≥3.5: full dispatch per routing matrix.

### Domain Score Thresholds (IMP-005 — replaces flat 4.0)
| Stakes Level | Threshold | Examples |
|---|---|---|
| Operational | 3.5 | Script fixes, report generation, dashboard updates, memory writes |
| Revenue/Product | 4.0 | GHL automation, email campaigns, funnel changes, CRM updates |
| Legal/Financial ($1-5K) | 4.5 | Contract decisions, spend increases, payment processing changes |
| Irreversible ($5K+) | 4.8 | Wire transfers, legal sign-offs, identity-level, biometric gates |
Chairman Synthesis must cite the applicable threshold row explicitly in every verdict.

### Step 4.5 — CEO Sanity Check (IMP-023, fires before SANDBOX batch)
Before firing the parallel dispatch batch, state in plain English what will happen in the next 5 minutes:
- One sentence per dispatch item: "I am about to [action] which will [result]"
- If any item sounds wrong when read aloud: PAUSE that item, flag to #leo-coaches: "SANITY CHECK PAUSE: <item> — re-verify before dispatch"
- This is the CEO gut-check that replaces micromanagement

Example: "I am about to post AI briefs to 100 GHL broker contacts, which will appear in their GHL notes visible to all team members." → Does this sound right? If yes, proceed.

### Step 4.6 — Parallel SANDBOX batch (mandatory)

Fire ALL SANDBOX items simultaneously. Not sequential. Record all IDs. → Execute slack-comms-skill to post #leo-auto receipt: SANDBOX [N] | Browser [N] | CLI [N] | Madison [N] | Kay [N] | Bennett digest [N AFTER Step 4.0 pass-rate].

**Slack Receipt Format (IMP-025 — standard for all council runs):**
`[COUNCIL] <question-slug> | SANDBOX: N | CLI: N | Madison: N | Kay: N | Bennett-REAL: N | False-gates-caught: N | Score: X.X/<threshold> | ETA: <completion time>`

Post to #leo-coaches (C0AQ4KB1SA0) after Step 6. No exceptions.

---

### Score Confidence Bands (IMP-018)
After collecting all 5 advisor scores, compute the band:
- band_width = max_score - min_score
- band_width < 1.0: HIGH CONFIDENCE → proceed to synthesis
- band_width 1.0-1.5: MODERATE CONFIDENCE → Chairman must resolve the disagreement explicitly before verdict
- band_width > 1.5: HIGH DISAGREEMENT → mandatory Red Team (Step 5.3) before synthesis
- band_width > 2.0: FORCE Red Team + flag to Bennett if stakes ≥ Revenue/Product

Include in Step 6 Verdict output: "Score: X.X ± Y.Y (band: Z.Z)"

## Step 5 — Chairman Synthesis (v19 — gate audit roll-up added)

Confidence-weighted recommendation + preserved dissents + mentor lens roll-up + **NEW v19: Gate Audit Roll-Up**:
- BENNETT classifications proposed: N
- BENNETT classifications PASSED Step 4.0 audit: M (target: M = real gates only)
- BENNETT classifications REJECTED (false gates caught): N - M
- Same-gate-twice escalations triggered: K
- Convertible-to-permanent gates: J / M

## Step 5.2 — Fresh Eyes Validation
Bring in an advisor who was NOT in Round 1. Summarize the question in ONE sentence without any prior context or scoring. Ask: "Without knowing anything else, what's your gut reaction to this?" Note any surprises — things the Fresh Eyes advisor flags that Round 1 missed. If Fresh Eyes finds a critical gap: flag to Chairman as ROUND 1 BLIND SPOT and factor into synthesis.

## Step 5.3 — Red Team Step (MANDATORY)
Assign the Contrarian advisor to attack the BEST CASE scenario. Prompt: "You are now trying to destroy the strongest argument FOR this decision. Find the one thing that makes the whole thesis fall apart." Red Team output goes directly to Chairman Synthesis as a mandatory input. Chairman must address Red Team's attack explicitly in the verdict or the verdict is incomplete.

## Step 5.5 — Diamond Stress Test (MANDATORY)
→ Execute diamond-skill. T1 / T2 / T3 + (v19) **T4 Gate Lifecycle Audit**: every BENNETT classification has all 4.0c fields filled.

**T4 Gate Lifecycle Audit (required per IMP-016):** For every BENNETT row in the verdict, verify: (1) all 4.0c fields populated (gate_id, same_gate_count, permanent_fix_deadline, convertible_to_permanent), (2) lifecycle fields written INLINE into council-log.json (no external script required — v31), (3) SAME_GATE_COUNT fetched from council-log.json. Any missing field = T4 FAIL. T4 FAIL blocks Step 6 verdict output.

## Step 5.7 — Escalation Routing
Based on weighted council score and stakes:
- Score ≥ threshold AND stakes = Operational → SANDBOX dispatch (Ivan CC executes)
- Score ≥ threshold AND stakes = Revenue/Product → CLI dispatch to Ivan CC + receipt to #leo-auto
- Score ≥ threshold AND stakes = Legal/Financial ($1K-$5K) → Bennett notify (24hr window, auto-proceed if no response)
- Score ≥ threshold AND stakes = Irreversible ($5K+, biometric, legal sign-off) → Bennett APPROVE before execute
- Score 3.0-3.49 → SANDBOX-RESEARCH only (no writes, no external calls)
- Score < 3.0 → NO dispatch. Flag COUNCIL LOW CONFIDENCE to #leo-coaches
- Any PERMANENT_FIX_REQUIRED flag from gate-lifecycle-skill → autopilot-skill intake (not Bennett)

## Step 6.0 — OUT-OF-BAND SHIP GATE (v33 — keystone; the trust boundary leaves the prompt)
The advisor isolation + separate auditor are no longer honor-system prose. The verdict is CODE-gated:
1. `council-run.sh <question-hash>` makes the run dir + idempotency lock + gold-set self-test canary.
2. The 5 advisors + independent auditor run as SEPARATE Agent sub-agents, each writing a receipt file.
3. `council-verify-run.sh <run-dir> 5` must `exit 0` (all advisor receipts + independent auditor + SELF_TEST_PASS present) BEFORE the Step 6 verdict may be emitted. Missing any => FAIL CLOSED, no verdict, post #leo-coaches.
This is what moves the ~96% rubber-stamp pass-rate toward a real ~70%. A self-narrated run with no receipts cannot ship.

## Step 6 — Verdict + Archive

```
COUNCIL v19 VERDICT [HH:MM MDT]
Score: X.X/threshold | Confidence-weighted: X.X | Stakes: [Operational/Strategic/Irreversible]
Mentor lenses fired: [N Hormozi · N Vee · N Robbins]
Gate audit (v19): [N proposed → M passed → K same-gate-twice escalated]
→ Dispatched: [N SANDBOX] [N CLI to Leo] [N Madison] [N Kay]
Top recommendation: [one sentence]
Red Team: [one sentence summary]
Dissents preserved: [Y/N — count]
Bennett digest: [M items — only Step 4.0 PASSES]
Brain level: [three-brain | six-brain]
```

**Advaita Delta Estimate (IMP-014 — required in every verdict):**
"Advaita delta: +X% (gates eliminated: N × 0.5% each | SANDBOX dispatches: M × 0.1% each | false gates rejected: K × 0.3% each)"
This feeds the autonomy baseline tracking.

### Bennett Digest Delivery SLA (IMP-007)
All BENNETT-classified items are batched into a SINGLE Slack DM to Bennett within 15 minutes of Step 6 close.

DM Format:
```
[COUNCIL DIGEST — <YYYY-MM-DD HH:MM>]
Items requiring your attention: N
Highest stakes: <1-line description of most critical item>
Drive artifact: <council artifact URL or path>

Items:
1. [GATE_TYPE] <title> — <25-word context> — Options: A=<do nothing>, B=<act now>
2. [GATE_TYPE] <title> — ...
```

If N=0: Send confirmation DM: "Zero true Bennett gates this council session — all items auto-dispatched."
DM goes to U08H07DMNTS (Bennett). NOT to #leo-coaches. NOT to #leo-auto. Direct message only.

**Canonical path:** `~/.openclaw/workspace/council-log.json`. Create-if-missing: `[ -f $LOG ] || echo '{"sessions":[],"gates":[]}' > $LOG` (gate-lifecycle-skill.sh handles this automatically).

**NOTE (council-log.json structure):** an existing council-log.json's top-level is a LIST; element [0] is the dict holding the canonical `sessions` array. Append via `d=json.load(f); d[0]['sessions'].append(rec)` — NOT `d.setdefault('sessions',...)` (the file is a list, not a dict; assuming a dict crashes with `'list' object has no attribute 'setdefault'`).

**council-log.json entry (v19 — adds gate audit fields):**
```json
{
  "timestamp": "...",
  "question_hash": "...",
  "score_raw": 4.5,
  "score_weighted": 4.52,
  "domain": "...",
  "stakes": "...",
  "threshold": 4.0,
  "passed": true,
  "dissents": 0,
  "mentor_lens_fires": {"hormozi": 3, "vee": 2, "robbins": 1},
  "gate_audit": {
    "proposed": 3,
    "passed_4_0_audit": 1,
    "rejected_false_gates": 2,
    "same_gate_twice_escalations": 0,
    "convertible_to_permanent": 1
  },
  "implementation_succeeded": null
}
```

### Step 6.5 — Council Artifact Persistence (v17 + v18 + v19 — MANDATORY)

**Artifact Naming Convention (IMP-028):**
Filename: `council-<question-slug>-<YYYY-MM-DD>-v<N>.md`
Drive folder: 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/council-artifacts/
If Drive MCP create_file fails (file >5KB): use `gog drive upload --parent=<folder_id>`
Retry max 2x. On 3rd fail: post artifact to #leo-coaches as code block with tag "DRIVE_FAIL".

Artifact format (write to council-log.json + optionally upload to Drive):
- Session timestamp, question_hash, scores (raw + weighted), domain, stakes, threshold, passed, dissents
- mentor_lens_fires: {hormozi: N, vee: N, robbins: N}
- gate_audit: {proposed, passed_4_0_audit, rejected_false_gates, same_gate_twice_escalations, convertible_to_permanent}
- implementation_succeeded: null (update within 72hr)

```markdown
### Gate Lifecycle Roll-Up (NEW v19)
Total Bennett classifications proposed in Round 1: <N>
Step 4.0 audit results:
- 4.0a probe-call passed (returned 200): <K> — auto-reclassified to SANDBOX
- 4.0a probe-call failed (401/403) but 4.0b browser/OAuth resolved: <L> — auto-reclassified to SANDBOX-BROWSER or CLI-DIRECT
- 4.0c gate justification template complete + valid trigger: <M>
- 4.0d same-gate-twice escalations: <P>

Final BENNETT digest count: <M - P>

Permanent-fix conversions triggered: <list of gate titles with autopilot WO IDs>
```

## Step 6 — Telemetry Log (IMP-030)
After every council run, append one line to ~/.openclaw/workspace/logs/council-telemetry.log:
```
COUNCIL RUN | <ISO date> | domain=<topic-slug> | score=<X.X> | threshold=<X.X> | PASS/FAIL | gates_caught=<N> | dispatched=<N> | false_gates_rejected=<N> | tokens=<N> | value_per_1k=<X.X>
```
Ivan CC writes this via bash one-liner immediately after Step 6 closes. This feeds Angie's weekly audit check #4 automatically.

**ENFORCEMENT (v27 — W22e 2026-05-27):** The telemetry write is MANDATORY and VERIFIED. Before proceeding to Step 7, confirm `council-telemetry.log` has a line with today's ISO date. If write fails (disk full, path missing), create `~/.openclaw/workspace/logs/` directory and retry. Log write failure must be posted to #leo-coaches as `TELEMETRY_WRITE_FAIL`. Log directory auto-create: `mkdir -p ~/.openclaw/workspace/logs`.

**council-step7-reminder.sh** cron runs daily at 08:00 UTC on Ivan — auto-posts to #leo-coaches listing any sessions where `implementation_succeeded=null` AND age > 72hr. This provides automated Step 7 accountability without requiring manual tracking.

## Step 6.6 — Token-Effectiveness Gate (v33 — Bennett directive 2026-05-30)
Council spawns 5-6 sub-agents + (high-stakes) a 50/50 expansion = real token cost on one Max quota. Monitor it.
After every run, append to `~/.openclaw/workspace/logs/council-token-effectiveness.log`:
`CTEFF | <ISO> | domain=<slug> | tokens=<N out-tokens or 1k*subagents proxy> | value=<decisions_changed + false_gates_caught> | note=<>`
Then compute **value_per_1k = value / (tokens/1000)**. Report it in the Step 6 verdict footer: `Token-eff: <value_per_1k>`.
**Budget gate:** if trailing-10 value_per_1k < 0.05 (lots of tokens, little decision value), the **Step -0.75 50/50 expansion and extra sub-agents are gated behind explicit high-stakes only** until efficiency recovers (ops seat token-storm fix). Run `council-token-effectiveness.sh` for the trend.

## Step 7 — Post-Implementation Review (IMP-006, mandatory)
Within 72 hours of council close, the dispatching agent MUST:
1. Run gate-lifecycle-skill.sh close <gate_id> <true|false> "<outcome note>"
2. Update council-log.json entry: implementation_succeeded = true/false, outcome_note
3. If implementation_succeeded = false: re-open gate, increment same_gate_count, check if PERMANENT_FIX_REQUIRED

If Step 7 is not completed within 72hr: next council run auto-flags this artifact as STALE in Step -1 Research Brief with message: "STALE COUNCIL: <question-slug> — outcome not updated. Was it implemented?"

Ivan CC should add a one-line reminder to the council artifact: "REMINDER: Update outcome at ~/.openclaw/workspace/council-log.json by <ISO: now+72hr>"

---

## Step 7.5 — Calibration-Contingent Authority (v33 — governance seat fix)
The council must LOSE power when it stops being right, not just log that it was wrong.
Run `council-calibration.sh` (reads `implementation_succeeded` outcomes from council-log.json).
If `realized_success_rate < 0.7` over the resolved set, council auto-dispatch authority is DOWNGRADED to
SANDBOX-RESEARCH-only until calibration recovers — the verdict says `authority: DOWNGRADED`. With <1 resolved
outcome it reads INSUFFICIENT_DATA (the honest state today; Step 7 must back-fill `implementation_succeeded`).
"100% effectiveness" is defined here as realized_success_rate, NOT a self-graded rubric.

## Anti-Patterns (v14-v18 preserved + v19 additions)

**Anti-Pattern List (v14-v18 core + v19 additions):**
- ❌ Routing to Bennett anything solvable via Ivan/Mack API, BrowserSession, or CLI-DIRECT
- ❌ Letting advisors see each other's scores before Step 5 (sycophancy chain)
- ❌ Running Round 1 without Exa research brief (Sub-step B)
- ❌ Skipping mentor lens block (Hormozi/Vee/Robbins) — it fires EVERY run
- ❌ Unanimous advisor scores without adversarial challenge (IMP-010 consensus risk)
- ❌ Verdict with no explicit threshold cited from Domain Score Thresholds table
- ❌ Step 6.5 artifact not written to council-log.json within session
- ❌ NEW v19: Classifying any step BENNETT without embedding probe-call response (Step 4.0a) in advisor recommendation
- ❌ NEW v19: Skipping browser fall-through (Step 4.0b) when API probe returns 401/403
- ❌ NEW v19: Logging same-gate-twice without triggering 4.0d auto-escalation
- ❌ NEW v19: Missing any field in 4.0c gate justification template
- ❌ NEW v19: Allowing Bennett to see a gate that has SAME_GATE_COUNT >= 2 (must auto-escalate to permanent-fix)

---

> **See also:** `bennett-mode-skill v2.1+` invokes this skill. Mentor lens source: Bennett directive 2026-05-10 gmail thread 19e141cdc25e5c98. v19 gate audit source: Bennett directive 2026-05-10 (this thread).

## Self-Audit Checklist (used by angie-weekly-audit-skill v8+)

Angie uses this checklist as the SOP rubric when auditing this business area.

1. [ ] Skill was invoked successfully in the last 30 days (or manually reviewed as active)
2. [ ] SKILL.md has valid frontmatter with name, description, version, and drive_file_id
3. [ ] All trigger phrases route correctly to this skill
4. [ ] council-log.json exists at ~/.openclaw/workspace/council-log.json with ≥1 entry written in last 30d
5. [ ] gate-lifecycle-skill.sh exists at ~/.openclaw/scripts/gate-lifecycle-skill.sh
6. [ ] No advisor content in SKILL.md reads '[preserved verbatim]' or '[v14 preserved]' (stubs must be inlined)
7. [ ] Step 6 artifact Drive upload confirmed in last 30d (Drive folder: 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/council-artifacts/)
8. [ ] Last council run: implementation_succeeded field updated within 72hr

## Cron Bindings

- `council-step7-reminder.sh` — daily 08:00 UTC on Ivan: posts to #leo-coaches any council session with implementation_succeeded=null AND age>72hr (Step 7 accountability). This is the one cron bound to this skill. Council runs themselves are manually invoked.
