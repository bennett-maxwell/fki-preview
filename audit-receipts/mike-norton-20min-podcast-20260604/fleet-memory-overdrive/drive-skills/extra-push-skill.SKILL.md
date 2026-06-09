---
name: extra-push-skill
drive_file_id: 16pUBt5cfyyMStxlGD5sC2Mm_MULzAvW3
version: 2.4
last_updated: 2026-05-30
council_verified: 4.4/5
description: "20-item minimum autonomous execution sprint through a C-suite lens. Renamed from push-harder-skill. Fires at the end of every autonomy loop (proactive-autonomy-skill, idea-to-completion-skill, troubleshoot chain). Never fires standalone without closeout after it. Trigger: 'extra push', 'give it an extra push', 'extra-push-skill', 'push harder' (legacy)."
north_star: "Full autonomy — Bennett closes deals, everything else runs itself 24/7."
chains_after: closeout-skill v10
---

# Extra Push Skill v1

## North Star
Full autonomy = Bennett shows up, takes calls, closes deals. Everything else runs itself.

## Purpose
After main execution completes, run one final autonomous sprint to squeeze out 15-25 more improvements. Every item must answer: "What would the CEO, CMO, or CFO do next if they were running this business?" No busywork. Only actions that move the 5 Advaita domains forward.

Minimum: 20 items. Target: 25+. No ceiling if critical issues found.

---

## Trigger Phrases
- "extra push"
- "give it an extra push"
- "extra-push-skill"
- "push harder" (legacy trigger — maps to this skill)
- "one more pass"
- "keep going"

---

## SAFETY GATE (runs before Step 1)

Tag every item REVERSIBLE or IRREVERSIBLE before execution.
IRREVERSIBLE items go to daily-digest.md only. Never auto-execute.

---

### Advaita Delta Tracking (added 2026-05-25 — IMP-014 propagation)
After every extra-push cycle, append to **`~/.openclaw/logs/council-telemetry.log`** (canonical cross-fleet path):
"EXTRA-PUSH | <ISO> | domain=<slug> | items_revised=<N> | items_passed=<N> | advaita_delta=+<X>%"
This feeds the council-skill Step 6 Advaita delta calculation automatically.
NOTE: `~/.openclaw/logs/council-telemetry.log` is machine-local. For cross-session/cross-agent durability, also append the same line to the Drive council-telemetry doc (ask gog or Drive MCP for the file if ID unknown).

---
## Loop-Consolidation Hook (v2.2 — 2026-05-27 — Bennett "most important thing of the business")
This skill does NOT carry its own deliverable-grading or self-improvement loop. That lives in ONE canonical engine: **self-audit-skill** (cycle scope). At cycle end — after the 20-item sprint is produced, BEFORE closeout — do exactly this:

1. **→ Execute self-audit-skill** on this cycle's deliverable. It owns the full loop:
   initial grade → REAL council on gaps → **Step 3.6 SAME-PATTERN-TWICE** (if a gap hash recurs ≥2× in 14d → PERMANENT-FIX: patch the owning **SKILL.md via `gog --replace`**, not just this deliverable) → **Step 5.5 inner improvement loop** (re-dispatch fixes, max 3 rounds, advance-gate = `score_delta ≥ 0.5` OR `fixes_executed ≥ 2`).
2. **Round-delta logging (fix #4):** append per improvement round to the Drive extra-push-history log (fetch ID via gog drive search "extra-push-history"). Do NOT write only to `~/.openclaw/state/extra-push-history.jsonl` — that path is machine-local and dies on agent handoff (STATE RULE). Machine-local write is acceptable as a secondary cache only.
   Format: `{"round":N,"score_before":x,"score_after":y,"council_directives":[...],"fixes_executed":k}`.
   `rounds>1` with an empty `round_deltas[]` is INVALID (mirrors gatekeeper-ledger rule) — proves the loop *lifts* score, not just churns.
3. **NEVER reimplement grading/council/redo logic inline.** The existing 1-revision council loop is superseded by self-audit's inner loop. (Consolidation 2026-05-27: 4 wrappers → 1 canonical cycle engine.)
4. **BOUNDED-ITERATION GUARD (v2.3, mirrors gatekeeper #17):** cap residual-revision at self-audit's max-3 rounds; a single-round score jump >2 triggers an independent re-score (anti reward-hacking).
---

## Hard Rules
1. NEVER ask Bennett questions. Make the call.
2. NEVER declare blocked without (a) browser attempt, then (b) diy-skill Steps 1-8.
3. NEVER stop at a plan. Execute in the same session.
4. NEVER ship fewer than 3 Diamond-verified artifacts per push.
5. Council approves the 20-item plan before wave execution — zero exceptions.
6. NEVER call closeout-skill with less than 3 artifacts produced — re-execute first.
7. Post #leo-auto receipt after every wave.
8. NEVER allow open items at closeout. Zero-Open-Items Gate (Step 4.5) is BLOCKING.
9. Diamond items execute in Wave A-1 — first, not last.
10. Wave A MUST dispatch all items as a parallel batch — no sequential execution.
11. IRREVERSIBLE items go to daily digest, never auto-execute.
12. Every item must answer "what would the C-suite do next?" If it can't, drop it.

---

## The 5 C-Suite Categories (20-item allocation)

| Category | C-Suite Lens | Items | Priority |
|---|---|---|---|
| Diamond Verification | All | 4 | PRIMARY — executes first |
| Operations / Vision | CEO | 4 | What's stalling the business? |
| Leads / Content / Brand | CMO | 4 | What's hurting acquisition or brand? |
| Financial Control / Spend | CFO | 4 | What's bleeding money or untracked? |
| Capabilities / Memory | CTO | 4 | What's broken, stale, or missing? |
| Flex | Any | +1-5 | Goes to highest-priority category if critical issue found |

Minimum: 20 items. Add flex items freely if critical issues found. No busywork — drop any item that doesn't answer the C-suite question.

---

## Execution Sequence (mandatory)

### Step 0 — THREAD CONTEXT + COST INIT
Capture last 5 user messages + any in-progress work as INPUT CANDIDATES.
Cost tracker init: session_spend = $0.00. Update after each wave.

### Step 1 — 20-ITEM CATEGORY SCAN (mandatory, no bypass)

For each category, find items that answer "what would the C-suite do next?"

Step 1a — Diamond Verification (4 items): Identify 4 critical live systems. Run 3-check: Source Lock + Receipt + Three-Line Proof. Candidate systems: Leo heartbeat, GHL>Meta CAPI pipeline, LinkedIn>GHL pipeline, legal dashboard cron, mapki/dashboard uptime, email triage cron.

Step 1b — CEO / Operations / Vision (4 items): Scan Sprint Board red/yellow rows, Vision Gap Analysis red items, any red>yellow or yellow>green domain moves available.

Step 1c — CMO / Leads / Content / Brand (4 items): Scan GHL unassigned leads (Location 14RD8KklxR9G4e0Rf7v2), ad attribution gaps, LinkedIn/Meta performance, content calendar gaps, 506 unassigned leads status.

Step 1d — CFO / Financial Control (4 items): Scan QB spend vs budget, Meta/Google ad spend vs targets, credit card utilization (Amex 74%, PCE 80% flagged), any spend anomaly >$500 from last 7 days.

Step 1e — CTO / Capabilities / Memory (4 items): Scan Drive skills folder (1qdUEbUb) for skills with modifiedTime >30 days, stale MEMORY.md entries >14 days, broken tool integrations, AGENT-MEMORY.md parity.

Step 1f — Flex (+1-5 items): If any category scan finds critical items beyond its 4-item quota, add flex items. No ceiling for critical issues.

Step 1g — Council Approval (BLOCKING): Run council-skill on assembled plan. Threshold 4.25. One revision loop. Post to #leo-auto (C0AKXT2S1T2). If #leo-auto returns channel_not_found or error, fall back to #leo-coaches (C0AQ4KB1SA0) — log the fallback in the report header:
```
EXTRA PUSH v1 [HH:MM MDT] — [N]-item sprint planned
Diamond (4): [systems]
CEO (4): [items]
CMO (4): [items]
CFO (4): [items]
CTO (4): [items]
Council: [score] pass/fail
Session spend: $0.00
[Slack channel: #leo-auto | fallback: #leo-coaches if leo-auto unavailable]
```

### Step 2 — WAVE EXECUTION

Wave A-1 — Diamond Verification (first, parallel): Run 4 Diamond checks simultaneously. Post result immediately. Any fail = add to Zero-Open-Items Gate.

Wave A-2+ — SANDBOX + BROWSER (parallel batch): Fire ALL Wave A-2+ items simultaneously. Notion, Drive, Slack, browser clicks. Never leave a UI item for Wave C if browser can click it now.

Wave B — CLI items: ON_IMAC = execute directly. SANDBOX = dispatch to Leo via #leo-auto (C0AKXT2S1T2); if #leo-auto is unavailable fall back to #leo-coaches (C0AQ4KB1SA0) with identical message.

Wave C — Leo dispatch: Send @Leo #leo-auto with exact task. Record ts. Advance — do NOT wait.

Wave D — Verify + Scope Expansion: 3-check on all completed items. Any fail = troubleshoot > re-execute. If time permits and 2+ items passed, expand to next Sprint Board item.

Wave E — New Assets: Upload new skill files or artifacts to Drive. Update SKILLS_MANIFEST if new skill deployed.

### Step 3 — ARTIFACT GATE (BLOCKING)
Count committed artifacts. If less than 3: return to Step 2. If 3 or more: proceed.

### Step 3.5 (NEW): False-Gate Auditor (mandatory pre-queue)

Before queueing ANY item to Bennett-digest as IRREVERSIBLE / Bennett-only, run the False-Gate Auditor — for each candidate gate, verify in order:

1. **SQUIRREL API path** — Is there an MCP tool (Notion/Drive/Gmail/QB/Meta/LinkedIn/GitHub) that resolves this? If yes → execute, do NOT queue.
2. **SQUIRREL Browser path** — Can BrowserSession/BrowserAction resolve? If yes → execute.
3. **CLI-DIRECT path** — Can Ivan/Mack bash, gog, curl, or composio SDK resolve? If yes → execute.
4. **Vendor-auth check** — Is the apparent "Bennett gate" actually a token re-expired? Check ~/.zshrc + workspace/config/.env first; if just-stale, escalate to credential-keyholder (Kay for GHL/QB), not Bennett.
5. **Token-aged-out detection** — If the gate cites a token blocker that's >24h old, re-test the token before propagating. Tokens auto-refresh on some flows.

Only after ALL 5 checks fail AND the gate truly fits biometric/legal/financial>$1K/identity → mark BENNETT-ONLY and queue.

Log each false-gate caught to `~/.openclaw/logs/false-gates-caught.jsonl` so we can prove the value of the auditor over time. Council v18 verdict 2026-05-10, sourced from memory-sweep cycle that found 5 false-gates of 9 candidates (55% false-gate rate).

### Step 4 — ZERO-OPEN-ITEMS GATE (BLOCKING)
For each open item, attempt in order:
1. SANDBOX API direct call
2. Browser control (BrowserSession > navigate > BrowserAction)
3. Madison delegation — FIRST load contacts-skill (Drive: 1HKaQUKXI6Y35cjaYTPnA-ROwkvXN9Dk-) to verify current email/Slack before sending. Never hardcode madison@franchiseki.com without contacts-skill confirm.
4. Leo CLI dispatch (@Leo #leo-auto C0AKXT2S1T2, or fallback #leo-coaches C0AQ4KB1SA0; record ts)
5. Kay delegation — FIRST load contacts-skill to verify current email/Slack before sending.
6. True BENNETT gate (only if ALL 5 paths exhausted — document which failed + why)

Max 1 True BENNETT gate per push. If more than 1 remains: re-execute targeting those items.

### Step 5 — C-SUITE REPORT (post to #leo-auto before closeout)

```
EXTRA PUSH v1 REPORT [HH:MM MDT]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Diamond Verification (CEO/CMO/CFO/CTO):
 • [system1]: PASS/FAIL — [proof]
 • [system2]: PASS/FAIL — [proof]
 • [system3]: PASS/FAIL — [proof]
 • [system4]: PASS/FAIL — [proof]

CEO / Operations:
 • [item]: [what was fixed] > [proof]

CMO / Leads/Content:
 • [item]: [what was fixed] > [proof]

CFO / Financial:
 • [item]: [what was fixed] > [proof]

CTO / Capabilities:
 • [item]: [what was fixed] > [proof]

Total: [N]/[N] items completed
Artifacts: [N]
IRREVERSIBLE queued for digest: [N]
BENNETT gates: [N]
Session spend: ~$X.XX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 6 — CLOSEOUT (mandatory — fires automatically)
Run closeout-skill (1F9OEFprvRhltoPmST7_zdlPEPH38MykJ) in full. Cannot skip. Cannot defer.

---

## Anti-Patterns (-2 each)
- Stopping at a plan without execution
- Skipping Step 1 category scan
- Skipping council approval before wave execution
- Running Diamond verification in Wave D instead of Wave A-1
- Surfacing BENNETT gates without trying browser + DIY waterfall
- Claiming Diamond without proof link
- Calling closeout-skill with less than 3 artifacts
- Skipping #leo-auto receipts between waves
- Running Wave A sequentially instead of parallel batch
- Items that don't answer the C-suite question (busywork): -1 each
- IRREVERSIBLE action executed without digest queuing: -5
- Skipping Zero-Open-Items Gate: -3

## Changelog
- v2.4 (2026-05-30): Permanent audit fixes — (1) council-telemetry.log path made canonical (~/.openclaw/logs/ + Drive dual-write); (2) extra-push-history.jsonl round-delta logging redirected to Drive primary (machine-local is cache-only, STATE RULE compliance); (3) Step 1g and Wave B #leo-auto fallback to #leo-coaches added; (4) Step 4 delegation now requires contacts-skill pre-load before emailing Madison or Kay; (5) Self-Audit Checklist expanded from 3 to 12 items; (6) Changelog backfilled with v2.2 and v2.3 missing entries.
- v2.3 (2026-05-27): Bounded-iteration guard — cap residual-revision at self-audit max-3 rounds; single-round score jump >2 triggers independent re-score (anti reward-hacking). Mirrors gatekeeper rule #17.
- v2.2 (2026-05-27): Loop-consolidation hook — skill no longer carries its own grading/council/redo logic; delegates to self-audit-skill as canonical cycle engine (4 wrappers → 1). Bennett directive: "most important thing of the business."
- v2.1 (2026-05-10): False-Gate Auditor mandatory pre-queue step — applies 5-tier check before any Bennett-digest add. Reduces false-gate rate proven 55% in memory-sweep cycle 2026-05-10.
- v2.0 (2026-05-07): Renamed from push-harder-skill. C-suite 20-item framework.

## Output Minimum
- 20+ line items in Step 5 report
- 4 Diamond-verified systems with pass/fail + proof
- 3+ committed artifacts
- Zero truly open items (or documented True BENNETT gates with DIY exhaustion log)
- #leo-auto receipts after each wave
- 1 closeout receipt with all destination URLs

## Self-Audit Checklist (used by angie-weekly-audit-skill v8+)

Angie uses this checklist as the SOP rubric when auditing this business area.

1. [ ] Skill was invoked successfully in the last 30 days (or manually reviewed as active)
2. [ ] SKILL.md has valid frontmatter with name, description, version, and drive_file_id
3. [ ] All trigger phrases route correctly to this skill ("extra push", "push harder", "one more pass", "keep going")
4. [ ] IRREVERSIBLE items are NOT auto-executed — they land in daily-digest.md only
5. [ ] Zero-Open-Items Gate (Step 4) is enforced before closeout-skill fires
6. [ ] Council approval threshold 4.25 verified before wave execution — not bypassed
7. [ ] At least 3 Diamond-verified artifacts produced before closeout-skill is called
8. [ ] #leo-auto Slack post sent after each wave (or #leo-coaches fallback logged)
9. [ ] contacts-skill loaded before any delegation to Madison or Kay (no hardcoded emails)
10. [ ] Round-delta log written to Drive (not only ~/.openclaw/ machine-local path)
11. [ ] Advaita delta appended to council-telemetry.log at cycle end
12. [ ] Changelog reflects latest version with date and patch summary

## Cron Bindings

None — manually invoked. No scheduled LaunchAgent or cron job owns this skill.
