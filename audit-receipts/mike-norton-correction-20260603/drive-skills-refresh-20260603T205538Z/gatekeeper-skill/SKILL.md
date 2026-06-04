---
name: gatekeeper-skill
description: "Default quality orchestrator for ALL tasks (not just deliverables). Checks 98% registry first; exempt tasks skip. All others: spawn workers, spawn a SEPARATE auditor, loop through council improvement until score ≥ threshold, then ship. v12: ALL-tasks default, 98% registry gate, file-handoff enforcement, 50-failure-mode hardening. v11: model routing (Sonnet spine, Haiku trivial, Opus hard). v6: 10 verified-delivery invariants: hard ship-gate (shipped⇒pass+diamond), Sentinel monitor, Bennett-delivery pass-token gate, auditor independence, mandatory fan-out, two-key external-send, ledger integrity, KPI, repeat-leak self-heal."
version: 9.2
status: ACTIVE
drive_file_id: 17FTNm951jvei-_wphCyL9HrCwVF93Zdw
patched_v9_2: "2026-06-03 — PERMANENT FIX: batch_pass_threshold raised 0.80→0.90 per Bennett directive '90-95% certainty before shipping'. Output-type tiering added: external-facing=0.90, internal=0.85. Council 3.69/5 CONDITIONAL approved with tiering as council Seat 2 mitigation. Fleet-wide: Mack, Ivan-CC, Leo, Henry, all employee CCs. Staged rollout: council-skill first, recap-skill second, gatekeeper-skill last."
lss_score: TBD
lss_audited: 2026-05-27
patched: 2026-06-02-v12.1-automation-decl-perm-fix
---

# Gatekeeper Skill v12

## v12 — ALL-TASKS DEFAULT + 98% REGISTRY + FILE-HANDOFF + 50-FAILURE-MODE HARDENING (NEW 2026-06-02)

> **Bennett directive 2026-06-02:** *"Why do we want to limit this to human facing? Even if it's AI facing it needs to be verified. Any task — don't give it back until you spawn a sub agent, verify with diamond skill, unless we have a 98% success rate on that task type. I don't care if it's Sonnet or Opus that is the orchestrator — that is whatever the human uses. Then you judge what they're asking you to do. I'm always after productivity over token efficiency."*

### The All-Tasks Default (HARD RULE — v12)
Gatekeeper fires on **ALL tasks** by default — not just human-facing or deliverable-class tasks. AI-facing tasks with downstream actions are equally subject to quality gates. The only exception: tasks with a tracked ≥98% success rate in `~/.openclaw/state/task-confidence-registry.json`.

**Remove the old qualifier.** Prior versions said "Does NOT apply to: Pure analysis/status checks · Planning docs · Code edits." That qualifier is RETIRED. The gate is now: **check the registry. If exempt → skip. Otherwise → mandatory.**

### Stage 0.05 — 98% Registry Check (HARD GATE — runs BEFORE Stage 0)

```bash
REGISTRY=~/.openclaw/state/task-confidence-registry.json
TASK_TYPE="${task_type}"

# Fail-safe: if registry absent, treat as REQUIRED
if [ ! -f "$REGISTRY" ]; then
  echo "REGISTRY_MISSING: defaulting to REQUIRED"
  EXEMPT="REQUIRED"
else
  EXEMPT=$(python3 -c "
import json, sys
try:
  reg = json.load(open('$REGISTRY'))
  exempt = reg.get('exempt_tasks', {}).get('$TASK_TYPE', {})
  rate = exempt.get('success_rate', 0)
  # Also check non_exempt_always list
  never_exempt = reg.get('non_exempt_always_gatekeeper', [])
  if '$TASK_TYPE' in never_exempt:
    print('REQUIRED')
  elif rate >= 0.98:
    print('EXEMPT')
  else:
    print('REQUIRED')
except Exception as e:
  print('REQUIRED')  # fail-safe
" 2>/dev/null || echo "REQUIRED")
fi

if [ "$EXEMPT" = "EXEMPT" ]; then
  echo "98% REGISTRY: $TASK_TYPE exempt (≥98% tracked success rate) — skipping gatekeeper"
  # Write minimal ledger line for tracking
  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"task_type\":\"$TASK_TYPE\",\"registry_exempt\":true,\"shipped\":true}" >> ~/.openclaw/state/gatekeeper-ledger.jsonl
  exit 0
fi
echo "98% REGISTRY: $TASK_TYPE not exempt — gatekeeper REQUIRED"
```

**Registry rules (HARD):**
- `~/.openclaw/state/task-confidence-registry.json` is **READ-ONLY to all agents**
- Only Angie writes it, from `response-scores.jsonl` outcome data (automated — no agent ever writes this file directly)
- Task type not in registry → automatically REQUIRED (default to gatekeeper)
- Task type in `non_exempt_always_gatekeeper` list → REQUIRED regardless of success rate
- Registry file absent → REQUIRED (fail-safe, never skip)
- Task type partially matching (e.g. "email_compose" vs "email_send") → REQUIRED (exact match only)

**Circular dependency guard (FM-3 fix):**
```bash
# At gatekeeper entry — prevents gatekeeper calling gatekeeper
if [ "${GATEKEEPER_ACTIVE}" = "1" ]; then
  echo "GATEKEEPER_ACTIVE: circular skip — returning caller's artifact directly"
  exit 0
fi
export GATEKEEPER_ACTIVE=1
# ... run gatekeeper ...
unset GATEKEEPER_ACTIVE  # at exit
```

### File Handoff Enforcement (HARD RULE — v12)

**Skills NEVER share a context window.** Skills communicate ONLY through files. This is the root-cause fix for multi-step skill chain failures (god-function anti-pattern).

**Standard path:** `/tmp/gk-<task_slug>-<step_number>-<role>-output.<ext>`
- Role = `worker` | `auditor` | `council` | `sentinel`
- ext = `json` (scorecards) or `md`/`html` (artifacts)
- Example: `/tmp/gk-blueprint-melissa-01-worker-output.json`

**Enforcement at every handoff:**
```bash
HANDOFF="/tmp/gk-${task_slug}-${step}-${role}-output.json"
if [ ! -f "$HANDOFF" ] || [ ! -s "$HANDOFF" ]; then
  echo "FILE_HANDOFF_FAIL: $HANDOFF missing or empty"
  failure_class="QUALITY_FAIL"
  # Do NOT proceed — treat as a round failure, council will fix
  exit 1
fi
echo "FILE_HANDOFF_OK: $HANDOFF ($(wc -c < "$HANDOFF") bytes)"
```

**Worker prompt addition (v12):** Worker prompt MUST include the exact output path: "Write your artifact to `/tmp/gk-<task_slug>-<step>-worker-output.json`. This path WILL be verified before auditor runs."

**Max skill chain depth = 1 (HARD).** Gatekeeper may call ONE skill (the owning skill) as worker. That skill NEVER calls another skill internally. If owning skill needs multiple steps: gatekeeper orchestrates them as SEPARATE sub-agents with file handoffs between each. Never more than 1 skill deep in any one sub-agent's context.

### 50-Failure-Mode Hardening (v12 — council-verified fixes)

Council analysis of 50 failure modes. Critical/High fixes embedded as hard rules:

**FM-3: Circular dependency** → GATEKEEPER_ACTIVE env guard (see Stage 0.05 above). Self-referential loop prevention.

**FM-6: Empty artifact accepted as PASS** → Auditor rubric MUST include `artifact_non_empty` as a required domain check (weight: 20/100). Empty/null artifact = score 0 on this domain = QUALITY_FAIL regardless of other scores.

**FM-7: Trivial task token burn** → Registry check (Stage 0.05) handles this. status_check / planning / quick_qa task types are in the exempt registry by default.

**FM-9: Ledger write silent failure** → `gk-ledger-write.sh` exits code 1 on write failure AND posts alert to `#leo-coaches`. Gatekeeper treats ledger write failure as HALT — run is NOT marked complete.
```bash
# In gk-ledger-write.sh
echo "$LEDGER_LINE" >> ~/.openclaw/state/gatekeeper-ledger.jsonl || {
  echo "LEDGER_WRITE_FAIL: alerting #leo-coaches"
  # post slack alert
  exit 1
}
```

**FM-13: File handoff path mismatch** → Standard path enforced (see File Handoff above). Worker prompt includes exact output path. Gatekeeper verifies existence before passing to auditor.

**FM-16: Sentinel crashes silently** → Sentinel writes heartbeat every 30min to `~/.openclaw/state/sentinel-<task_slug>.heartbeat`. Main loop checks heartbeat age; if >60min stale → re-spawn sentinel. Non-blocking re-spawn, not a halt.

**FM-25: Banned model Opus 4.7 slips through** → `gk-ledger-write.sh` HARD REJECTS any line with `model_id` matching `4-7`. Worker/auditor prompts add: "HARD: Never use claude-opus-4-7. Resolve 'opus' → claude-opus-4-8 only."

**FM-27: False human gate (no probe)** → Existing STAGE 0 check-before-ask handles. v12 adds: any `HUMAN_GATE_BLOCKED` entry MUST carry `token_probe_receipt` in ledger. Bare gate without receipt → reclassified as `SUSPECTED`, counted as `false_escalation_count`.

**FM-37: Vague improvement directives** → Council improvement prompt updated: "REJECT: 'improve', 'enhance', 'better', 'consider'. EVERY directive must be: action verb + location + specific value. Example: 'Replace {{COMPANY_NAME}} on line 47 with Mahana Fresh'. Vague directive = rejected, return SPECIFIC_DIRECTIVE_REQUIRED."

**FM-38: Worker runs delivery stages** → Worker prompt add: "DELIVERY-FAIL if your output contains any of: sent email / posted to Slack / wrote to Notion / pushed to GHL / deployed. WORKER PRODUCES ONLY. Auditor checks for delivery artifacts and fails the run if found."

**FM-39: No rubric = vibes scoring** → Stage 0 HALTS if `audit_rubric_id` is blank or Drive metadata fetch fails. No rubric = no run. Non-negotiable.

**FM-46: File handoff not standardized** → Standard schema for all handoff JSON files:
```json
{
  "task_slug": "<slug>",
  "step": "<step_number>",
  "role": "worker|auditor|council",
  "ts_iso": "<ISO timestamp>",
  "artifact_path": "<path to artifact file>",
  "score": 0,
  "status": "PASS|QUALITY_FAIL|INFRA_FAIL|HUMAN_GATE_BLOCKED",
  "scorecard": {}
}
```

**FM-50: FLEET-CONTEXT stale** → Session start: gog pull of FLEET-CONTEXT.md `1kr0e__MUhAZWfzTCps4hd2-gLbVNUvu1`. If local copy >1h old → force pull before any agent work. Stale fleet context = all agents operating on old rules.

**Other FM fixes (medium severity):**
- FM-11 (auditor returns prose): Auditor prompt: "Return ONLY valid JSON. No prose. Any non-JSON response = automatic QUALITY_FAIL rescore."
- FM-22 (batch scope collision): Scope claim logged BEFORE worker spawn (already in v3). v12 adds: scope claim file `/tmp/gk-<task_slug>-scope-claims.json` verified unique before each spawn.
- FM-24 (score normalization drift): Auditor prompt: "ALL scores /100. If you compute /10 or /5, multiply before returning. gk-ledger-write.sh REJECTS any score field > 100."
- FM-30 (anti-reward hack): REWARD-HACK GUARD already in v7.1. v12 adds: if round-over-round score delta > 20 on a single quality factor → force fresh independent auditor re-score before accepting.
- FM-34 (concurrent state collision): State file uses `flock` before write: `flock -x ~/.openclaw/state/gatekeeper-<task_slug>.lock gk-state-write.sh`
- FM-40 (threshold confusion): Threshold explicitly tagged in ledger: `threshold_type: single|batch`. Single default = 95. Batch default = 80. Mismatch between task_scope and threshold_type = HALT.
- FM-43 (producer == auditor): v+1 independence invariant (already in skill). v12 reminder: producer_agent_id assigned from session sub-agent spawn receipt, NOT self-reported.

---

## v11 — MODEL-ROUTING LAYER · "Sonnet is the spine; it spawns the right brain per task" (2026-06-01)

> **Bennett directive 2026-06-01:** *"I always value productivity and effectiveness and accuracy over cost. Optimize cost but NEVER to the detriment of any of those. Sonnet is the spine — it must know when to spawn Haiku (trivial) and when to spawn Opus 4.8 (hard / quality-critical). We NEVER use Opus 4.7."*

> **v12 clarification (2026-06-02):** *"I don't care if it's Sonnet or Opus that is the orchestrator — that is whatever the human uses. Then you have to judge what they're asking you to do."* The orchestrator = whatever model the human chose for their session. Don't override it. What matters is: judge complexity of the TASK, then spawn sub-agents at the right tier. The router is about sub-agent spawning decisions, not overriding the session model.

### The spine rule (HARD)
- **Orchestrator = whatever the human is running.** Bennett runs Sonnet 4.6; that's the orchestrator. Don't switch it. Don't escalate the orchestrator.
- **Sub-agent tier = task complexity.** The sub-agent spawning model is determined by gatekeeper's complexity classifier, not the orchestrator's tier.
- **Quality beats cost at every fork.** When a sub-task could plausibly sit in two tiers, pick the HIGHER one. "Saved tokens but the artifact was weaker" = a FAIL.
- **`claude-opus-4-7` is BANNED everywhere.** `model:"opus"` resolves to Opus 4.8 (`claude-opus-4-8`). Never pass 4-7 to any sub-agent.

### Complexity classifier → model tier (assign BEFORE every spawn)
| Tier | Model (`Agent` `model:` param) | Use for | Examples |
|---|---|---|---|
| **TRIVIAL** | `haiku` → `claude-haiku-4-5-20251001` | Mechanical, deterministic, low-judgment. No reasoning a checklist couldn't do. | file moves/renames, format conversion, grep/extract, boilerplate fill, single-field lookup, link-liveness check, data reshaping, the Sentinel monitor |
| **STANDARD** | `sonnet` → `claude-sonnet-4-6` | The DEFAULT for anything not clearly trivial or clearly hard. Most workers, most auditors. | report/email/copy production, internal docs, batch infra workers, routine audits |
| **HARD / QUALITY-CRITICAL** | `opus` → `claude-opus-4-8` (NEVER 4-7) | Accuracy/effectiveness-critical, customer- or Bennett-facing, ambiguous multi-constraint reasoning, novel strategy/architecture. Escalate GENEROUSLY here. | Blueprint final synthesis, customer-facing copy, legal/compliance-sensitive text, financial-realism reasoning, the AUDITOR on any Bennett/customer-facing deliverable |

### Routing rules (enforced at spawn)
1. **Orchestrator/coordinator → whatever human chose.** Never override.
2. **Worker model = the deliverable's complexity tier.** Blueprint/customer copy → Opus worker. Standard report/email → Sonnet worker. Mechanical batch sub-task → Haiku worker.
3. **Auditor on a Bennett-facing or customer-facing deliverable → Opus 4.8.** The audit is the last line of defense before Bennett sees it — quality-critical by definition. Auditors on internal/batch infra → Sonnet. (Auditor still MUST be a different agent than the worker — v6 #5 / v+1 independence unchanged.)
4. **Tie → higher tier.** Ambiguity resolves UP, per the quality-first directive.
5. **In-loop MODEL ESCALATION:** if a Sonnet worker's artifact fails the auditor through round 2 (still < threshold), the round-3 worker is RE-SPAWNED on **Opus 4.8** — escalate the brain, not just the directive list. Log `model_escalated:"sonnet→opus"`. This is the structural cure for "looped 3 times on the same model and never cleared the bar."
6. **Sentinel monitor → Haiku** (cheap mechanical watch of state file + ledger).
7. **Never downgrade a customer/Bennett-facing FINAL synthesis below Opus** to save cost. Drafts/sections may be Sonnet; the final assembled artifact that reaches a human gets an Opus pass (worker or auditor).

### Ledger additions (per sub-agent line)
```json
{"role":"worker|auditor|sentinel","model_tier":"trivial|standard|hard","model_id":"claude-haiku-4-5-20251001|claude-sonnet-4-6|claude-opus-4-8","model_escalated":"none|sonnet→opus"}
```
`gk-ledger-write.sh` REJECTS any line whose `model_id` contains `4-7` (banned). A Bennett/customer-facing `shipped:true` line whose final auditor `model_tier` is not `hard` is SUSPECT → flag for review.

---

## v9/v10 — PLAN-FIRST · TEMPLATE-THEN-FANOUT · COVERAGE · PROPAGATE · MAX-SCOPE (v10 NEW 2026-05-30)

> **Council 5-advisor APPROVED (avg 4.4–4.6).** Bennett directive 2026-05-29: *"whatever you do once for one project, do it N times with the same workflow — use better structures and sub-agents — and make gatekeeper itself tell you to plan better and use sub-agents so you never bounce a decision back to me."*

1. **PLAN-FIRST GATE** — Before spawning any worker, emit a written plan artifact: the **target list**, the ONE **reference template**, and the **verification method** per target. No plan artifact ⇒ HALT.

2. **TEMPLATE-THEN-FANOUT** — If a deliverable repeats across **N ≥ 2** targets: build ONE reference, **verify it** (separate auditor + receipt), THEN fan out across **ALL N** via sub-agents. Never hand-build bespoke per target.

3. **COVERAGE GATE** — `done` = every target processed **OR** explicitly reported `blocked-with-reason`. Silent truncation = **hard FAIL** at ledger-write. Ledger line MUST carry `targets_total`, `targets_done`, `targets_blocked[]`.

4. **PROPAGATE-INTO-SKILL GATE** — A fix/improvement is **NOT "done"** until written into the canonical `SKILL.md` on **Drive** AND verified by readback. Fix in memory = `fix-pending-propagation` (partial), never `fixed`.

5. **MAX-SCOPE / PLUS-MORE GATE (v10)** — Do ALL N targets, never a reduced subset. Propose AND execute the bigger adjacent scope. "Which one?" / "should I do fewer?" scope question to Bennett = HARD FAIL.

**NO-BOUNCE COROLLARY:** Never return a scope question to Bennett when the structure resolves it. The ONLY exits to Bennett: (a) existing council `BENNETT_REQUIRED` token and (b) the red-line set — biometric · legal · >$1K spend · external/customer send · credential · protected-file.

---

## v6 — VERIFIED-DELIVERY INVARIANTS + ALWAYS-ON MONITOR (NEW 2026-05-27)

> **Codified from a real Angie audit of `gatekeeper-ledger.jsonl` (122 runs):** 106 prevented-ships (KPI working), but **1 leak** and **13/14 multi-round runs left `round_deltas` empty**. Bennett directive: "only verified delivered outcomes reach me; AI always does sub-agents + monitoring first."

The 10 improvements:

| # | Improvement | Ties into |
|---|---|---|
| 1 | **HARD SHIP-GATE INVARIANT** — `shipped:true` is ILLEGAL unless `pass:true` AND `final_score >= threshold` AND `diamond:"PASS"`. Enforced at ledger-write. | diamond-skill |
| 2 | **ALWAYS-ON MONITOR (Sentinel sub-agent)** — standing monitor for the whole cycle (Stage 0.7). Tails ledger + watches in-flight runs; any ship attempt without pass+diamond+token → BLOCK + alert #leo-auto. Sentinel ≠ worker ≠ auditor. | pulse-skill |
| 3 | **BENNETT-DELIVERY PASS-TOKEN GATE** — nothing reaches Bennett without a `gatekeeper_pass_token {ledger_line_id, score, diamond:PASS, ts}`. | recap-skill, ceo-email-skill |
| 4 | **ENFORCED ROUND-DELTA** — `rounds>1` with empty `round_deltas[]` is REJECTED at ledger-write. | council-skill |
| 5 | **AUDITOR-INDEPENDENCE PROOF (logged)** — ledger line MUST carry `auditor_id` + `worker_ids[]`; write REJECTED if `auditor_id ∈ worker_ids`. | diamond-skill |
| 6 | **MANDATORY SUB-AGENT FAN-OUT** — gatekeeper NEVER builds the artifact in the main thread. Pre-flight HALT if no worker sub-agent spawned. | autopilot-skill |
| 7 | **TWO-KEY EXTERNAL-SEND INSPECTION** — any external/customer send needs TWO independent auditor passes + per-lead Bennett confirm. Logged `external_two_key:true`. | "no external comms w/o approval" red line |
| 8 | **LEDGER INTEGRITY VALIDATOR + daily cron** — `gk-ledger-audit.py` scans for leaks, bypass_writes; posts alert to #leo-auto. LIVE: `0 6 * * *` on Ivan. | angie-audit-skill |
| 9 | **KPI SURFACED TO BENNETT** — `prevented_ship_count`, `avg_round_lift`, `shipped_below_threshold` (must be 0) surfaced in CEO email + Pulse. | ceo-email-skill |
| 10 | **REPEAT-LEAK SELF-HEAL** — `shipped_below_threshold > 0` in any 7-day window → auto-escalate council + freeze ships in that `task_type` until diamond-verified. | council-skill |

### Ledger-write contract (v6 — ENFORCED)
All ledger writes go through `~/.openclaw/bin/gk-ledger-write.sh`, which REJECTS any line failing:
```
REQUIRE pass == true WHEN shipped == true
REQUIRE final_score >= threshold WHEN shipped == true
REQUIRE diamond == "PASS" WHEN shipped == true (diamond may be "n/a" only when shipped == false)
REQUIRE round_deltas non-empty WHEN rounds > 1
REQUIRE auditor_id present AND auditor_id NOT IN worker_ids
REQUIRE pass_token present WHEN bennett_facing == true
REQUIRE ledger_written_ts present ALWAYS
REQUIRE council_session_id present OR null ALWAYS
REQUIRE model_id NOT matching "4-7" ALWAYS (v12 — Opus 4.7 banned)
REQUIRE token_probe_receipt present WHEN failure_class == HUMAN_GATE_BLOCKED (v12)
REQUIRE score <= 100 ALWAYS (v12 — normalization enforcement)
```
A rejected write logs `status:"halted"` + reason and posts #leo-auto.

### Stage 0.7 — SPAWN SENTINEL (before Stage 1)
Spawn ONE Monitor sub-agent (Haiku) for the cycle. On any `shipped:true` attempt lacking pass+diamond+token → block + alert #leo-auto. Heartbeat every 30 min to `~/.openclaw/state/sentinel-<task_slug>.heartbeat`. If heartbeat >60min stale → main loop re-spawns sentinel (FM-16 fix). Sentinel ≠ worker ≠ auditor — three distinct roles.

### Stage 4.6 — BENNETT-DELIVERY GATE (before anything reaches Bennett)
Before any artifact is surfaced to Bennett, the surfacing skill calls `gk-verify-token <ledger_line_id>`:
- valid (score≥threshold + diamond PASS) → deliver.
- missing/invalid → DO NOT deliver; route back into the loop.

---

## Purpose

Gatekeeper is the **default quality orchestrator** for ALL tasks (v12 — not just deliverables). It never builds the deliverable itself. It:

1. Checks 98% registry (Stage 0.05) — exempt tasks skip with a minimal ledger line
2. Dispatches worker sub-agents to produce artifacts (file handoff enforced)
3. Dispatches a SEPARATE auditor sub-agent to score (JSON only — never the same agent)
4. If score < threshold: invokes council-skill for SPECIFIC improvement delta, re-dispatches workers
5. Ships only when score ≥ threshold (max 3 loops, then escalate)

**Canonical Loop-Engine Map:** deliverable → gatekeeper · one cycle → self-audit-skill · cross-project → full-autonomy-loop-skill. Other skills CALL these; never reimplement the loop.

---

## v5.1 Patch — `proposal_only` Scope

When invoked for an audit rerun, gap scan, A-Z skill scan, or preclaim check, use `task_scope=proposal_only`.

In `proposal_only` scope:
- Stage 4 is a proposal gate, not a ship gate.
- Do not deliver, send, post, mutate Notion/GHL/QB/Meta/Drive canonical skills, deploy, delete, change credentials, touch payroll/legal, or change ad spend.
- Append a ledger line with `shipped:false`, `mutations_performed:0`, `external_sends_performed:0`.

---

## v5 RUN LEDGER + EFFECTIVENESS (HARD RULE)

> **HARD RULE:** A gatekeeper run is **not complete** until one JSON line is appended to `~/.openclaw/state/gatekeeper-ledger.jsonl`. Session markers and in-memory results do not count. recap-skill verifies the ledger line exists before logging the run as closed.

**State file (per run):** `~/.openclaw/state/gatekeeper-<task_slug>-<YYYYMMDD>.json` (deterministic — no random suffix).

**Ledger line (per run — v12 additions bolded):**
```json
{"ts":"<ISO>","task_slug":"<slug>","task_type":"<type>","task_scope":"single|batch","rounds":2,"r1_score":71,"final_score":87,"threshold":95,"threshold_type":"single|batch","pass":true,"shipped":true,"msgId_or_url":"<...>","prevented_ship":true,"workers":3,"human_gates":[],"infra_fails":[],"council_session_id":"<id OR null>","ledger_written_ts":"<ISO>","self_audit_score":<float>,"self_audit_defects_found":<int>,"self_audit_corrections_applied":<int>,"diamond_result":"PASS"|"FAIL","diamond_failed_steps":[],"producer_agent_id":"<id>","auditor_agent_id":"<id>","auditor_independent":true,"model_tier":"standard","model_id":"claude-sonnet-4-6","model_escalated":"none|sonnet→opus","registry_exempt":false,"file_handoff_verified":true,"token_probe_receipt":"<receipt OR null>"}
```

**Effectiveness rollup:**
```
prevented_ship_count = count(ledger where prevented_ship == true)
avg_round_lift = mean(final_score - r1_score) over runs with rounds>1
false_escalation_count = count(human_gates where token_probe_receipt is null) # v12
shipped_below_threshold = count(shipped==true AND final_score < threshold) # MUST be 0
```

---

### GATE-VERIFY-REQUIRED (fleet-wide protocol)
Before ANY item is classified as a human gate:
1. `~/.openclaw/bin/token-probe.sh <service>`. HTTP 200=NOT a gate. 401=human gate confirmed. 403=fix-call. 429=wait.
2. Vault check: `notion-fetch 341cf5514fd381fe993de8add7eb265e`.
3. Prior session docs? → NEVER trust. Re-probe live.
4. True human gates (no probe needed): biometric · legal · >$1K · identity · external contract.

HARD RULE: gate with no live probe receipt = SUSPECTED. In v12: `HUMAN_GATE_BLOCKED` without `token_probe_receipt` in ledger → classified as false_escalation, NOT a real gate.

---

## STAGE 0 — CHECK-BEFORE-ASK (v4 — runs before any HALT or escalation)

> **HARD RULE:** Gatekeeper must NOT HALT-on-missing-input before trying to recover from canonical stores AND proving absence with a live probe.

| Missing input type | Recovery procedure |
|---|---|
| **Credential / API key / token** | 1. `notion-fetch` Credential Vault `341cf5514fd381fe993de8add7eb265e`. 2. `token-probe.sh <service>`. 3. 200 → RECOVERED, proceed. 4. 403 → fix-call. 5. 401 / absent → escalate with proof. |
| **Known config / ID** | Check secrets-index-skill + memory-skill + Vault before asking. |
| **Lead data / rubric Drive ID** | Check task's Notion page + memory references first. |

**Recover-from-Vault-then-escalate:**
```
ON missing-credential or missing-known-input:
  1. RECOVER: query Vault + secrets-index + memory-skill
  2. PROBE: token-probe.sh <service> (<15min receipt)
  3. IF recovered/valid → write into run context, log "RECOVERED from Vault", CONTINUE
  4. ELSE → escalate as HUMAN_GATE_BLOCKED with PROOF (probe receipt + Vault-miss note)
```

---

## Task Scope Types

| `task_scope` | Use case | Workers | Auditor |
|---|---|---|---|
| `single` | One artifact | 1-2 workers | 1 auditor on the artifact |
| `batch` | N artifacts | N workers (parallel) | 1 auditor per worker artifact, aggregate gate |

**Batch mode gate:** `batch_pass = passing_workers / total_workers >= batch_pass_threshold`. **Default raised to 0.90** per Bennett directive 2026-06-03 ("90-95% certainty before shipping"). Output-type tiering: external-facing outputs (prospect emails, franchise docs, contracts) = 0.90; internal outputs (recaps Bennett skims, status updates) = 0.85. Tag `output_facing: external|internal` in the ledger to apply correct threshold. `threshold_type` tagged in ledger (FM-40 fix). [PERMANENT FIX 2026-06-03: batch default raised 0.80→0.90. Council 3.69/5 CONDITIONAL approved with output-type tiering as mitigation for token waste on low-leverage internal outputs.]

---

## Failure Classification (HARD RULE)

| Class | Definition | Gate action |
|---|---|---|
| `QUALITY_FAIL` | Artifact produced but auditor score < threshold | Loop: council improvement delta → re-run worker |
| `INFRA_FAIL` | MCP error (Cloudflare, Notion timeout, 429, 401 on service key) | Fallback chain |
| `HUMAN_GATE_BLOCKED` | Blocked on a gate only a human can resolve (after Vault recovery failed + probe receipt present) | Surface to Bennett/Kay with proof |
| `PASS` | Auditor score ≥ threshold | Proceed to Stage 4 |

**INFRA_FAIL fallback chain:**
1. `create_file` Cloudflare block → try `copy_file`
2. Notion MCP timeout → retry 1x after 30s; 2nd timeout → Leo WO
3. GHL 429 → wait 60 min + retry (token is fine — do NOT escalate as missing)
4. SSH down → check Tailscale first
5. **401 on a service key → STAGE 0 recover-from-Vault FIRST**
6. All fallbacks exhausted → log `INFRA_FAIL`, skip worker, continue batch

---

## When It Fires (v12 — ALL Tasks, not just deliverables)

**ALWAYS applies to:** Blueprint builds · Email drafts · Copy generation · Reports · HTML/document deliverables · Multi-page CC improvements (batch) · **AI-facing deliverables with downstream actions** · **Any task type NOT in the 98% exempt registry**

**98% EXEMPT (registry-controlled, Angie-maintained):** memory_receipt_write · recap_footer_render · bash_status_check · (others Angie adds from outcome data)

**NEVER exempt (always gatekeeper regardless of success rate):** email_send · blueprint_delivery · ic_demographic_report · post_call_summary · ghl_contact_note · slack_message · notion_page_write · any_human_facing_deliverable · any_ai_facing_deliverable_with_downstream_action

---

## Step-by-Step Walk-Through (Every Run)

```
STAGE 0.05 — 98% REGISTRY CHECK (v12 — FIRST GATE, before everything)
 ├── Read ~/.openclaw/state/task-confidence-registry.json
 ├── If task_type in exempt_tasks with success_rate >= 0.98
 │    AND NOT in non_exempt_always_gatekeeper list
 │   → Write minimal ledger line {registry_exempt:true, shipped:true}
 │   → EXIT (skip all remaining stages)
 ├── If registry file absent → treat as REQUIRED (fail-safe)
 └── Otherwise → REQUIRED: proceed to Stage 0

STAGE 0 — PRE-FLIGHT (v4 check-before-ask + v5 ledger init + v12 hardening)
 ├── CIRCULAR GUARD: if GATEKEEPER_ACTIVE=1 → exit immediately (FM-3 fix)
 ├── Set GATEKEEPER_ACTIVE=1
 ├── Detect task_scope: single | batch
 ├── Verify owning skill exists in Drive (HALT if not found)
 ├── Load audit rubric (Drive file ID) — HALT if rubric_id blank or Drive fetch fails (FM-39 fix)
 ├── Initialize state: round=0, best_score=0, artifacts={}, round_deltas=[], threshold_type=single|batch
 ├── Write state to: ~/.openclaw/state/gatekeeper-<task_slug>-<YYYYMMDD>.json
 ├── [batch] Assign non-overlapping scope; log to /tmp/gk-<task_slug>-scope-claims.json (verify unique — FM-22 fix)
 ├── MISSING-INPUT CHECK (v4): run recover-from-Vault-then-escalate for any missing credential/ID
 └── HALT ONLY IF: owning skill missing | rubric unloadable | input GENUINELY absent after recovery+probe

STAGE 0.7 — SPAWN SENTINEL (before Stage 1)
 ├── Spawn Monitor sub-agent (Haiku) — record sentinel_id in state
 ├── Sentinel watches state file + ledger; blocks ship-without-pass; heartbeat every 30min
 └── Heartbeat check in main loop: if >60min stale → re-spawn sentinel (FM-16 fix)

STAGE 1 — WORKER DISPATCH
 ├── Classify complexity → assign model tier (trivial/standard/hard) per complexity classifier
 ├── Spawn worker(s) with routed model tier
 ├── Worker prompt INCLUDES: exact output file path /tmp/gk-<task_slug>-<step>-worker-output.json
 ├── Worker prompt INCLUDES: "DELIVERY-FAIL if output contains sent/posted/deployed"
 ├── Worker prompt INCLUDES: "NEVER use claude-opus-4-7"
 ├── Worker runs full owning-skill pipeline (SKIP delivery stages)
 ├── Worker writes artifact to /tmp/gk-<task_slug>-<step>-worker-output.json
 └── FILE HANDOFF VERIFY: check file exists and is non-empty (FM-13 fix). If missing → QUALITY_FAIL

STAGE 1.5 — FAILURE CLASSIFICATION
 ├── Classify each: PASS | QUALITY_FAIL | INFRA_FAIL | HUMAN_GATE_BLOCKED
 ├── HUMAN_GATE_BLOCKED → run STAGE 0 recover-from-Vault FIRST
 │    → Must include token_probe_receipt. Bare gate without receipt = false_escalation (FM-27 fix)
 ├── INFRA_FAIL → fallback chain
 └── Check auditor rubric includes artifact_non_empty domain (FM-6 fix)

STAGE 2 — AUDITOR (HARD GATE: different agent from worker)
 ├── Assign model tier: Opus for Bennett/customer-facing; Sonnet for internal/batch
 ├── Spawn auditor — MUST be a DIFFERENT agent than any worker (FM-43 fix: distinct agent receipt)
 ├── Auditor reads from /tmp/gk-<task_slug>-<step>-worker-output.json (file handoff)
 ├── FILE HANDOFF VERIFY: auditor confirms it can read the handoff file before scoring
 ├── [batch] Auditor scores each artifact separately, returns aggregate
 └── Returns ONLY JSON (Standard Scorecard Schema) — any prose = automatic QUALITY_FAIL rescore (FM-11 fix)

STAGE 3 — GATE CHECK
 ├── [single] score ≥ threshold → STAGE 4
 ├── [batch] batch_pass_rate ≥ batch_pass_threshold → STAGE 4
 ├── below threshold AND round < max_rounds:
 │   └── QUALITY_FAIL only → council improvement delta
 │       Council prompt: REJECT vague directives ('improve'/'enhance'/'consider') (FM-37 fix)
 │       Each directive must be: action verb + location + specific value
 │   └── APPEND to round_deltas[]: {round, score, directives_applied, score_delta_from_prev}
 │   └── Check REWARD-HACK: if score delta > 20 in one round → fresh independent auditor re-score
 │   └── Round 3: if worker model was Sonnet and score still < threshold → re-spawn on Opus (model escalation)
 │   └── Increment round → update state → back to STAGE 1 with delta
 └── round = max_rounds AND still below → HALT + escalate + write ledger line (shipped:false)

STAGE 4 — PRE-SHIP SELF-AUDIT IMPROVEMENT LOOP (v8)
 ├── Invoke self-audit-skill in MICRO_RESPONSE_MODE
 ├── Capture: self_audit_score (0–5), self_audit_defects_found[], self_audit_corrections_applied[]
 ├── If self_audit_score < 3.5 OR any HIGH severity defect found:
 │   ├── Apply top improvement directive immediately
 │   └── Re-run self-audit-skill once (one retry maximum)
 │   └── If score still < 3.5 after retry → set shipped=false, HALT, manual review required
 └── self_audit_score ≥ 3.5 AND no unresolved HIGH defects → proceed to Stage 5

**Loop-Closure Gate (v12.2 — 2026-06-03):** Before shipping, verify prior fixes are holding:
```bash
bash ~/.openclaw/scripts/loop-closure-gate.sh || { echo "LOOP-CLOSURE GATE FAIL — fixes reverting; BLOCK ship"; }
```
If gate fails: do NOT ship; surface to council for FIX STRATEGY.

STAGE 5 — SHIP GATE (score ≥ threshold AND Stage 4 self-audit passed)
 ├── AUTOMATION_DECLARATION CHECK (v12.1 perm-fix — 2026-06-02, picked up from Mack handoff)
 │   Grep artifact for 'automation_declaration' block. If MISSING:
 │   → Force automation_dimension_score = 1.0/5 in auditor scorecard
 │   → Prepend to gap list: severity=HIGH, affected=automation_declaration, root_cause=missing block
 │   → Block ship if automation_dimension_score < 3.0 (unless task_type in registry exempt list)
 │   Bash: grep -q 'automation_declaration' "$ARTIFACT_PATH" || echo "AUTOMATION_DECL_MISSING"
 ├── Run diamond-skill T1–T7 IN FULL
 │   T1: Factual accuracy — no hallucinated contact IDs, URLs, or scores
 │   T2: Logic consistency — no contradictions between rounds or ledger entries
 │   T3: Implementation proof — receipts (HTTP 200, msgId, Notion page ID) for all claims
 │   T4: Gate lifecycle — all human_gates have owner + proof_needed + deadline
 │   T5: No false-done claims — no ✅ without same-turn proof signal
 │   T6: Canonical state written — Drive or Notion (not ~/.openclaw/ or /tmp/ only)
 │   T7: Persisted write confirmed — gog-pull size > 0 OR Notion MCP readback matches
 ├── diamond FAIL (any T-step fails) → treat as round N+1, escalate; do NOT set shipped=true
 ├── diamond PASS → execute delivery
 ├── LEDGER WRITE via gk-ledger-write.sh (HARD — if write fails → HALT, alert #leo-coaches) (FM-9 fix)
 │   Required fields: all v12 additions (file_handoff_verified, registry_exempt, token_probe_receipt, threshold_type)
 │   Validator REJECTs: model_id with "4-7" | score>100 | shipped:true without probe for HUMAN_GATE
 └── recap-skill logs: {task, rounds, r1_score, final_score, prevented_ship, status: "🚀 SHIPPED"}
     recap verifies the ledger line exists before marking the run closed

UNSET GATEKEEPER_ACTIVE  # at exit (FM-3 circular guard cleanup)
```

---

## Standard Scorecard Schema (ALL workers and auditors MUST use this)

```json
{
  "sub_agent": "<name>",
  "task_scope": "single | batch",
  "round": 1,
  "artifacts_attempted": ["<list>"],
  "artifacts_delivered": ["<list>"],
  "artifact_non_empty": true,
  "failure_class": "PASS | QUALITY_FAIL | INFRA_FAIL | HUMAN_GATE_BLOCKED",
  "infra_failures": ["<tool, error, fallback taken>"],
  "human_gates": ["<what needs who — AND vault_check result + probe receipt>"],
  "token_probe_receipts": {},
  "score": 0,
  "score_max": 100,
  "threshold": 95,
  "pass": false,
  "domain_scores": {
    "artifact_non_empty": {"score": 0, "max": 20, "required": true},
    "<other_domain>": { "score": 0, "max": 0, "checks_passed": 0, "checks_total": 0 }
  },
  "blockers": [
    { "domain": "<domain>", "check": "<id>", "issue": "<what failed>", "severity": "critical|major|minor", "failure_class": "QUALITY_FAIL | INFRA_FAIL | HUMAN_GATE_BLOCKED" }
  ],
  "round_deltas": [
    { "round": 1, "score": 0, "directives_applied": [], "score_delta_from_prev": null }
  ],
  "critical_count": 0,
  "major_count": 0,
  "file_handoff_path": "/tmp/gk-<task_slug>-<step>-worker-output.json",
  "file_handoff_verified": true
}
```

**Score normalization (HARD RULE):** All scores /100. Other denominators REJECTED. gk-ledger-write.sh REJECTS score > 100 (FM-24 fix).

**v12 artifact_non_empty domain:** Required domain on ALL scorecards. Max 20 points. Score 0 if artifact is empty/null/missing. Empty artifact = QUALITY_FAIL regardless of other scores (FM-6 fix).

---

## Inputs

| Field | Required | Description |
|-------|----------|-------------|
| `task_type` | ✅ | Type used to check 98% registry (e.g., `blueprint`, `email_send`, `ic_demographic_report`) |
| `task_scope` | ✅ | `single` (default) or `batch` |
| `owning_skill` | ✅ | Skill that owns the deliverable |
| `lead_data` | ✅ for blueprint/email | Lead context or Notion page ID |
| `audit_rubric_id` | ✅ | Drive file ID of audit rubric — HALT if blank |
| `threshold` | Optional | Default 95 (single deliverables), 80 (CC/infra batch) |
| `max_rounds` | Optional | Default 3 |
| `worker_count` | Optional | Default 1 (single), N (batch) |
| `batch_pass_threshold` | Optional (batch) | Default 0.80 |
| `output_path_prefix` | Optional | Default `/tmp/gk-<task_slug>` — base for file handoff paths |

---

## Worker Sub-Agent Prompt Template

> **Spawn with the routed model (v11/v12):** set the `Agent` `model:` param from the complexity classifier — `haiku` (trivial), `sonnet` (standard default), `opus` (hard / customer- or Bennett-facing; resolves to claude-opus-4-8, NEVER 4-7). Tie → higher tier. Round-3 re-spawn of a twice-failed Sonnet worker uses `model:"opus"`.

```
WORKER MODE — PRODUCE ONLY. DO NOT SHIP. DO NOT SEND EMAIL. DO NOT POST TO SLACK.
Model tier: {model_tier} ({model_id}) # v11 — assigned by complexity classifier
HARD: Never use claude-opus-4-7. Resolve 'opus' → claude-opus-4-8 only.

Task: {task_description}
Owning skill: {owning_skill}
Scope: {scope_assignment}
Lead/context: {lead_data}
Round: {round} of {max_rounds}
[Round 2+ only]
Improvement delta from auditor (round {round-1}, score {last_score}/100):
{improvement_delta}
Apply EVERY item — mandatory fixes. Directives are specific (action + location + value).

Output file: Write artifact to: {output_file_path}
(This path is verified by gatekeeper before auditor runs. If you skip writing to this path,
your run will be classified QUALITY_FAIL regardless of artifact quality.)

Execute {owning_skill} in WORKER MODE:
- Run all production stages (research, content, HTML/artifact build)
- SKIP all delivery stages
- DELIVERY-FAIL if your output contains: sent email / posted Slack / wrote to Notion / pushed GHL / deployed
- Return: artifact written to output file + Standard Scorecard JSON. No prose.

CREDENTIAL/INPUT recovery (v4): if a required credential appears missing:
- notion-fetch Credential Vault 341cf5514fd381fe993de8add7eb265e + run token-probe.sh <service>
- recover if valid; only set HUMAN_GATE_BLOCKED if genuinely absent (include probe receipt in human_gates[])

Output: Standard Scorecard JSON FIRST (to stdout), THEN write artifact to {output_file_path}.
Include file_handoff_path and file_handoff_verified:true in scorecard.
```

---

## Auditor Sub-Agent Prompt Template

> **Auditor model (v11/v12):** Opus for any Bennett-facing or customer-facing deliverable. Sonnet for internal/batch-infra. Still a DIFFERENT agent than the worker.

```
AUDITOR MODE — SCORE ONLY. DIFFERENT AGENT FROM WORKER. DO NOT MODIFY. DO NOT SHIP.

[HARD GATE: If you produced any of these artifacts, REFUSE. Reply: "AUDITOR CONFLICT — I produced this artifact. Spawn a different auditor."]

Read artifact from: {worker_output_file_path}
(Verify this file exists and is non-empty before scoring. If missing or empty → score artifact_non_empty domain = 0/20, QUALITY_FAIL.)

Load audit rubric from Drive: {audit_rubric_id}
Score every domain including required artifact_non_empty (max 20 pts).
Normalize ALL scores to /100. Any score field > 100 is INVALID.
Return ONLY valid JSON (Standard Scorecard Schema) — any prose = automatic disqualification.
For each blocker, classify: QUALITY_FAIL | INFRA_FAIL | HUMAN_GATE_BLOCKED.
HUMAN_GATE_BLOCKED ONLY valid when worker's scorecard includes token_probe_receipt proving absence.
Improvement directives (when score < threshold):
  - REJECT vague directives: 'improve', 'enhance', 'better', 'consider'
  - EVERY directive: action verb + specific location + specific value
  - Example: "Replace {{COMPANY_NAME}} on line 47 with 'Mahana Fresh'"
```

---

## Council-Skill Improvement Prompt Template

```
IMPROVEMENT MODE — specific fix directives required.

Current score: {score}/100 (threshold: {threshold})
QUALITY_FAIL blockers only (INFRA_FAIL and HUMAN_GATE_BLOCKED excluded):
Critical: {critical_list}
Major: {major_list}

Return ordered list of SPECIFIC directives.
REJECT: 'improve', 'enhance', 'better', 'consider'. These are not directives.
REQUIRE: action verb + specific location + specific value.
Example: "1. Replace {{COMPANY_NAME}} placeholder with 'Mahana Fresh' on line 47."
Each directive must be AI-actionable without human input.
These directives are recorded verbatim into round_deltas[].directives_applied.
```

---

## Escalation (Round 3 Fail / INFRA_FAIL unresolved / genuinely-absent input)

```
POST to #leo-coaches:
⛔ GATEKEEPER HALT — {task_type} for {lead_name}
Round {round} score: {score}/100 (threshold: {threshold})
QUALITY failures: {critical_count} critical / {major_count} major
INFRA failures: {infra_fail_list}
HUMAN gates (post-recovery, with probe receipts): {human_gate_list}
Action: Bennett review → manual override OR discard
```

---

## Round State Object

State file: `~/.openclaw/state/gatekeeper-<task_slug>-<YYYYMMDD>.json`
Write with `flock -x ~/.openclaw/state/gatekeeper-<task_slug>.lock` (FM-34 concurrent collision fix)

```json
{
  "task_type": "blueprint",
  "task_scope": "single",
  "owning_skill": "blueprint-ai-skill",
  "threshold": 95,
  "threshold_type": "single",
  "batch_pass_threshold": null,
  "max_rounds": 3,
  "registry_exempt": false,
  "workers": [
    { "name": "Worker-1", "scope": "full blueprint", "model_tier": "hard", "model_id": "claude-opus-4-8", "score": 90, "failure_class": "PASS", "output_file": "/tmp/gk-blueprint-melissa-01-worker-output.json" }
  ],
  "human_gates": [],
  "recovered_from_vault": ["NOTION_API_KEY (probe 200)"],
  "round_deltas": [
    { "round": 1, "score": 71, "directives_applied": [], "score_delta_from_prev": null },
    { "round": 2, "score": 87, "directives_applied": ["Replace {{COMPANY_NAME}} with Mahana Fresh on line 47"], "score_delta_from_prev": 16 }
  ],
  "current_round": 2,
  "sentinel_id": "sentinel-heartbeat-<task_slug>",
  "file_handoffs_verified": true,
  "status": "looping | passed | halted"
}
```

---

## Integration Map

| Skill | Change Needed |
|-------|--------------|
| **audit-skill** | None |
| **blueprint-ai-skill** | WORKER MODE wired in v3.14-runtime. Never calls another skill internally (max depth 1 rule). |
| **council-skill** | None |
| **diamond-skill** | None |
| **recap-skill** | v5 — verifies gatekeeper-ledger.jsonl line exists before marking a run closed |
| **batch-overdrive-skill** | Gatekeeper wraps batch-overdrive for infra improvement cycles |
| **secrets-index-skill** | STAGE 0 recover-from-Vault reads canonical Vault + key map |
| **memory-skill** | STAGE 0 checks memory-skill for known IDs/config |
| **autopilot-skill** | CALLER — routes deliverable-class tasks through gatekeeper |
| **angie-weekly-audit-skill** | Reads gatekeeper-ledger.jsonl; computes prevented_ship_count, avg_round_lift, shipped_below_threshold |
| **task-confidence-registry.json** | v12 — Angie maintains; Stage 0.05 reads. Agents READ-ONLY. |

---

## Cron Bindings
None — fires per Rule 16 on all tasks. No scheduled cron.

---

## Self-Audit Checklist (used by angie-weekly-audit-skill)

1. [ ] No deliverable shipped in last 14 days with audit score < 95 (Sprint Board)
2. [ ] SKILL.md frontmatter: name=gatekeeper-skill, version=9.0, drive_file_id valid
3. [ ] Worker prompt includes "DO NOT SHIP" and "DELIVERY-FAIL if contains sent/posted/deployed"
4. [ ] Auditor prompt includes "AUDITOR CONFLICT" self-check
5. [ ] council-skill invoked on QUALITY_FAIL only
6. [ ] Escalation fires on round 3 fail → #leo-coaches
7. [ ] recap-skill called after each round
8. [ ] Rule 16 confirmed present
9. [ ] All scorecards /100 normalized; gk-ledger-write.sh rejects score > 100
10. [ ] State file written after each round (deterministic path) with flock
11. [ ] No worker audited its own artifact in last 14 days
12. [ ] batch_pass_threshold 0.90 (external-facing) / 0.85 (internal) — tag output_facing in ledger; threshold_type tagged in ledger [RAISED 2026-06-03]
13. [ ] v4: every credential HALT has STAGE 0 recover-from-Vault attempt + probe receipt
14. [ ] v4: zero false escalations — no Bennett/Kay credential ask where Vault value was valid
15. [ ] v4: secrets-index-skill + memory-skill present in Integration Map
16. [ ] v5: every run has a gatekeeper-ledger.jsonl line
17. [ ] v5: shipped_below_threshold == 0
18. [ ] v5: every multi-round run has populated round_deltas[]
19. [ ] v6: every shipped:true line satisfies pass==true AND final_score>=threshold AND diamond=="PASS"
20. [ ] v6: Sentinel monitor spawned (Stage 0.7) for every multi-step cycle
21. [ ] v6: every Bennett-facing artifact carries valid gatekeeper_pass_token
22. [ ] v6: no ledger line has auditor_id ∈ worker_ids
23. [ ] v6: every external/customer send logged external_two_key:true + per-lead Bennett confirm
24. [ ] v7: gk-ledger-audit.py cron running daily on Ivan (0 6 * * *) — zero bypass_writes
25. [ ] v8: every shipped:true line carries self_audit_score ≥ 3.5
26. [ ] v8: every shipped:true line carries diamond_result=="PASS" with diamond_failed_steps==[]
27. [ ] v8: gk-ledger-write.sh rejects shipped=true when self_audit_score absent OR diamond_result≠"PASS"
28. [ ] v+1: every shipped/pass line carries distinct producer_agent_id and auditor_agent_id
29. [ ] v+1: every auditor_independent:true backed by id pair + cross-reference
30. [ ] v12: Stage 0.05 registry check runs before every task
31. [ ] v12: No gatekeeper-on-gatekeeper (GATEKEEPER_ACTIVE guard present and cleared at exit)
32. [ ] v12: All file handoffs use /tmp/gk-<task_slug>-<step>-<role>-output.<ext> — verified non-empty
33. [ ] v12: Empty artifact = hard QUALITY_FAIL (artifact_non_empty domain in rubric, max 20pts)
34. [ ] v12: All HUMAN_GATE_BLOCKED entries carry token_probe_receipt — bare gates = false_escalation counted
35. [ ] v12: gk-ledger-write.sh rejects model_id matching "4-7" (Opus 4.7 banned)
36. [ ] v12: gk-ledger-write.sh rejects score > 100 (normalization enforcement)
37. [ ] v12: flock used on state file writes (concurrent collision prevention)
38. [ ] v12: No skill chain > 1 deep in any worker sub-agent (max depth 1 rule)

---

## Changelog
- **v12 / frontmatter 9.0 (2026-06-02 — Bennett "any task, not just human-facing; 98% registry; judge complexity for model; productivity over token efficiency"):**
  - **ALL-TASKS DEFAULT:** Removed "human-facing only" qualifier. Gatekeeper fires on ALL tasks unless task_type is in the 98% exempt registry. AI-facing tasks with downstream actions explicitly added to non-exempt list.
  - **Stage 0.05 — 98% REGISTRY CHECK:** New pre-flight gate. Reads `~/.openclaw/state/task-confidence-registry.json` (Angie-maintained, agents READ-ONLY). Exempt (≥98% success) tasks skip gatekeeper with a minimal ledger line. Non-exempt or non_exempt_always tasks proceed. Registry absent = REQUIRED (fail-safe).
  - **PRODUCTIVITY-FIRST MODEL SELECTION clarification:** Orchestrator = whatever the human chose (don't override). Sub-agent model = complexity of the task. Tie → escalate UP. This refines v11 to match Bennett's exact directive (v11 said "Orchestrator = Sonnet 4.6, always" — corrected to "whatever human runs").
  - **FILE HANDOFF ENFORCEMENT:** Standardized path `/tmp/gk-<task_slug>-<step>-<role>-output.<ext>`. Worker prompt includes exact output path. Gatekeeper verifies existence before proceeding. Empty file = QUALITY_FAIL. Max skill chain depth = 1 (root cause fix for multi-step skill chain failures).
  - **50-FAILURE-MODE HARDENING (council-verified):** 14 critical/high/medium fixes embedded: FM-3 circular guard, FM-6 artifact_non_empty domain, FM-9 ledger write fail-alert, FM-11 prose auditor = disqualify, FM-13 path mismatch, FM-16 sentinel re-spawn, FM-22 scope collision flock, FM-24 score normalization, FM-25 Opus 4.7 banned in ledger-write, FM-27 false gate = false_escalation, FM-34 state file flock, FM-37 vague directives rejected, FM-38 worker delivery-fail, FM-39 rubric required.
  - **Ledger schema:** Added `registry_exempt`, `file_handoff_verified`, `token_probe_receipt`, `threshold_type` to all ledger lines.
  - **gk-ledger-write.sh contract:** Adds REJECT rules for model_id with "4-7", score > 100, HUMAN_GATE_BLOCKED without probe receipt.
  - **Self-audit checklist:** Items 30-38 added (v12 checks).
  - **When It Fires:** Updated to ALL tasks. Explicit exempt and never-exempt lists.

- **v11 / frontmatter 8.5 (2026-06-01):** Added MODEL-ROUTING LAYER. Sonnet = permanent orchestrator/spine; 3-tier complexity classifier for sub-agents. Opus 4.7 banned. Model escalation in round 3. Auditor on Bennett/customer-facing = Opus.
- **v10 / frontmatter 8.4 (2026-05-30):** Added Gate 5 MAX-SCOPE / PLUS-MORE. Do ALL N targets, propose+execute bigger adjacent scope.
- **v9 / 2026-05-29:** PLAN-FIRST · TEMPLATE-THEN-FANOUT · COVERAGE · PROPAGATE gates.
- **v8.2 / 2026-05-28:** Mechanical 3-round enforcement loop. Council MUST run on QUALITY_FAIL. round_deltas enforced.
- **v8 / 2026-05-27:** Stage 4 self-audit loop (self-audit-skill MICRO_RESPONSE_MODE, ≥3.5 required). Diamond T1–T7 (expanded from T1–T3). gk-ledger-write.sh rejects shipped=true when self_audit_score absent or diamond≠PASS.
- **v7 / 2026-05-27:** Bypass detection. council_session_id + ledger_written_ts in schema. Daily audit cron.
- **v6 / 2026-05-27:** 10 verified-delivery invariants from 122-run Angie audit. Hard ship-gate, Sentinel, Bennett pass-token, enforced round-delta, auditor independence, mandatory fan-out, two-key external, ledger integrity, KPI, repeat-leak self-heal.
- **v5.1 / 2026-05-27:** proposal_only scope.
- **v5 / 2026-05-26:** Mandatory run ledger. Round-delta capture. prevented_ship_count KPI.
- **v4 / 2026-05-26:** STAGE 0 check-before-ask — recover from Vault before any HALT.
- **v3 / 2026-05-26:** Batch mode. INFRA_FAIL vs QUALITY_FAIL. Auditor separation. Score /100.
- **v2 / 2026-05-26:** Original. Single-artifact loop. Rule 16.

---

## v8.2 — MECHANICAL 3-ROUND ENFORCEMENT LOOP (2026-05-28)

**Root cause fixed:** After Round 1, the loop was advisory — wrote `round_2_needed` to state but never actually ran council or re-dispatched workers. v8.2 makes it a hard `while` block.

```python
# Gatekeeper 3-round enforcement loop — v8.2
TARGET = 0.95  # 95% — Bennett directive
MAX_ROUNDS = 3
round_scores = []
current_round = 1
batch_score = initial_batch_score  # from Round 1

while batch_score < TARGET and current_round <= MAX_ROUNDS:
    quality_fails = [w for w in workers if w.score < (threshold*100) and w.failure_class == "QUALITY_FAIL"]
    infra_fails = [w for w in workers if w.failure_class == "INFRA_FAIL"]
    human_gates = [w for w in workers if w.failure_class == "HUMAN_GATE_BLOCKED"]
    if not quality_fails:
        break  # remaining failures are INFRA/HUMAN gates — not council-fixable
    directives = invoke_council_skill(build_directive_request(quality_fails, batch_score, TARGET))
    fixes_applied = execute_directives(directives)  # AI-executable <5min, no Bennett-gate actions
    for worker in quality_fails:
        new_result = run_worker(rerun_prompt(worker, directives), worker.name)
        worker.update_score(new_result.score, directives.get(worker.name, []))
    new_batch_score = len([w for w in workers if w.score >= threshold*100]) / len(workers)
    round_scores.append({"round": current_round, "score_before": batch_score,
                          "score_after": new_batch_score, "delta": new_batch_score - batch_score,
                          "directives_applied": directives, "fixes_executed": fixes_applied})
    batch_score = new_batch_score
    current_round += 1
```

### Per-Round Report Format (mandatory)
```
GATEKEEPER BATCH — [task_slug]
Round 1: XX% batch pass (N/M workers)
Round 2: XX% → XX% (delta: +X%) | Council directives applied: N
Round 3: XX% → XX% (delta: +X%) | Council directives applied: N
Final: XX% | [PASS/FAIL] | Target 95%: [REACHED / 3 rounds exhausted]
```

---

## v+1 PATCH — PROVABLE AUDITOR INDEPENDENCE (2026-05-31)

At ledger-write, record BOTH `producer_agent_id` and `auditor_agent_id` (distinct sub-agent run IDs / receipt-file paths). The ledger validator MUST assert `producer_agent_id != auditor_agent_id` AND that the auditor receipt references the producer's artifact ID it did NOT create. `auditor_independent:true` is INVALID unless both IDs are present and differ.

**Ledger-write contract additions:**
```
REQUIRE producer_agent_id present ALWAYS
REQUIRE auditor_agent_id present ALWAYS
REQUIRE producer_agent_id != auditor_agent_id
REQUIRE auditor receipt references >=1 producer artifact_id NOT created by auditor_agent_id
REJECT auditor_independent==true WHEN (producer_agent_id absent OR auditor_agent_id absent OR equal)
ON independence FAIL → shipped stays false, status="halted" (reason "INDEPENDENCE_FAIL_v+1"),
  loop back to spawn a SEPARATE auditor sub-agent
```

---

## v+1 PATCH — HUMAN-GATE OWNER ENVELOPE (2026-05-31)

A human gate may be addressed ONLY to: **Bennett** (U08H07DMNTS) [biometric/legal/>$1K/identity/external-contract] OR **Kay** (GHL-UI / platform config / token rotation). Every human-gate briefing email CCs kay@franchiseki.com.

HARD BLOCK: Brent and Cody are operational lead-flow owners, NEVER gate owners. If a gate's computed owner resolves to Brent/Cody/anyone-not-{Bennett,Kay}: STOP, re-classify (it is almost certainly a false gate or a Kay platform task), log `GATE OWNER MIS-ROUTE AVERTED -> reclassified`. One consolidated gate envelope per cycle. Any gate with no probe receipt = SUSPECTED, not shippable as a real gate.
