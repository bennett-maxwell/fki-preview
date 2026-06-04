---
name: overdrive-skill
drive_file_id: 1iz45wnvX6T77JfeodpRxbIpDgd76OhnQ
version: 3.9
last_updated: 2026-05-30
council_verified: 4.62/5 (v3.6 schema-patch pass, Operational threshold)
description: "Overdrive skill — full autonomous business loop. Chain: state-resume > self-audit micro baseline > business-audit > council > gate-aging > autopilot(batches of 10) > diamond per batch > advaita-rubric-gate (once) > extra-push (EMBEDDED step 6 — extra_push_embedded: YES) > closeout. v3.7 adds Self-Improving Loop Verification Pass and corrected canonical drive_file_id. Trigger: use proactive autonomy skill, run proactive, full autonomy loop, use advaita vision as rubric, run against advaita vision."
deliverable: "30 high-leverage Diamond-verified items minimum per run, sequenced in batches of 10. Session not complete until 30 items pass all 3 diamond checks (T1/T2/T3) AND HTTP 200 Proof Link verification AND ≥1 process_improvement logged AND unified compact receipt posted to #leo-coaches (C0AQ4KB1SA0)."
north_star: "Full autonomy — Bennett closes deals, everything else runs itself 24/7."
patched_v3_6: "2026-05-14 v3.6 — EMBEDS closeout-receipt-schema-patch v1.0 (Drive 1uScideBdlllxvlxH5WuKC9Gx-__NNSoj) in Step 7 CLOSEOUT. Unified 11-field compact Slack receipt MANDATORY. HTTP 200 Proof Link verification mechanical. PROCESS_IMPROVEMENT_GATE auto-suggest if improvements_count=0. Wave-audit-skill v1.0 auto-discovers THREAD_X_COMPLETE receipts via this schema. Pattern-driven by wave-audit-skill v1.0 retroactive audit 2026-05-14 (D6=0.0 systemic, D8=4.0 inconsistent across 3 cycles)."
patched_v3_7: "2026-05-27 — Self-Improving Loop Verification Pass. Overdrive now checks recap/self-audit/council/business/Angie/lean/handoff contract drift before and after a loop; any repeated micro-audit pattern becomes a council permanent-fix candidate."
patched_v3_8: "2026-05-27 — Correction Final Verifier Gate. Overdrive outputs involving correction, recap, self-audit, task-review, handoff, or CEO email proof must pass `tools/fki_correction_final_verify.py <draft> --json` before completion wording."
patched_v3_9: "2026-05-30 — Skill audit fixes: (1) All #leo-auto posts corrected to #leo-coaches C0AQ4KB1SA0 (dead channel); (2) blocker-verify-skill Drive ID added; (3) receipt version tag corrected to overdrive@v3.9; (4) council-skill version conflict resolved (v15 call vs v28+ contract); (5) fki_correction_final_verify.py self-heal fallback added; (6) IRREVERSIBLE digest mirrored to Drive for cross-agent visibility."
patched: "2026-05-13 — v3.5: Step -1 memory-sync-gate added (PATCH 3). blocker-verify-skill gate added before BENNETT gate classification (PATCH 2). v3.4 (2026-05-10): Auto-default-Option-A rule. v3.3 (2026-05-09): Step 0.5 self-audit. v3.2: CEO HTML format. v3.1: state-resume, gate-aging, batches."
---

# Overdrive Skill v3.9

## v3.8 Patch — Correction Final Verifier Gate

When overdrive is invoked for a repeated correction/failure chain, produce a bounded hardening packet instead of claiming the full 30-item autonomy loop unless all 30 Diamond items are actually run. The final response must pass `tools/fki_correction_final_verify.py <draft> --json` before using completion language.

**SELF-HEAL if `tools/fki_correction_final_verify.py` is missing (script does not exist at `~/.claude/tools/`):**
1. Search Drive Skills folder `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY` for the script; if found, write to `~/.claude/tools/fki_correction_final_verify.py`.
2. If not found: apply manual 3-check verification gate inline — (a) is every diamond item claimed actually in `overdrive-last-cycle.json open_queue`? (b) does proof_pass_rate >= 100%? (c) is improvements_count > 0? — log outcome as `manual_verifier_gate` in `~/.openclaw/logs/correction-verify-manual.jsonl`.
3. Never block on missing script. Self-heal always. Flag gap to council for permanent fix if this path fires.

> ⚠️ **DO NOT DOUBLE-STACK**
> overdrive-skill already includes the FULL chain:
> state-resume → **self-audit (NEW v3.3)** → business-audit → council → gate-aging → autopilot(batches of 10) → diamond per batch → advaita-rubric-gate → **extra-push** (extra_push_embedded: YES — step 6 auto-fires; no manual call needed) → **closeout**
>
> Calling `extra-push-skill`, `closeout-skill`, `council-skill`, `autopilot-skill`, `business-audit-skill`, or `diamond-skill` AFTER overdrive = redundant work.
>
> If you want to **audit overdrive's output**, chain: overdrive → **self-audit-skill** (cycle-scope grade) → done.
>
> Patched 2026-05-09 per Council v16 verdict 4.24/4.0 + Bennett proactivity test.



## North Star
Full autonomy = Bennett shows up, takes calls, closes deals. Everything else runs itself.

## Purpose
AI proactively finds what to improve and executes end-to-end. Starts with business audit for context.
Use when topic is vague or you want a full business health check.

## Trigger Phrases
- "overdrive"
- "use overdrive skill"
- "use proactive autonomy skill"
- "run proactive"
- "full autonomy loop"
- "run the full loop on [area]"
- "audit and fix [area]"
- "use advaita vision as rubric"
- "run against advaita vision"

---

## SAFETY GATE (BLOCKING)

REVERSIBLE (execute immediately): Notion updates, Drive writes, Slack posts, code commits, skill edits, dashboard updates, memory writes, Sprint Board rows.

IRREVERSIBLE (daily digest ONLY — NEVER auto-execute): outbound emails to external parties, budget changes, Meta/Google ad changes, GHL contact modifications, external publishes.

Hard rule: IRREVERSIBLE actions append to ~/.openclaw/workspace/daily-digest.md with timestamp + description. Bennett reviews once daily. Zero exceptions.
**CROSS-AGENT VISIBILITY (v3.9 — mandatory):** After any IRREVERSIBLE append, also mirror the new entry to Drive Skills folder `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/overdrive-skill/state/daily-digest-mirror-<YYYY-MM-DD>.md` via Drive MCP create_file/update. Local `~/.openclaw/workspace/daily-digest.md` is machine-local and invisible to Leo, Tiffany, and cloud agents. Drive mirror is the cross-session canonical. Any agent reading the digest must check Drive first, then fall back to local.

---

## Hard Rules
1. NEVER ask Bennett questions. Make the call.
2. NEVER surface "I need a human" without documenting all 8 DIY steps first.
3. Closeout fires automatically at the end. NEVER skip it.
4. Every action tagged REVERSIBLE or IRREVERSIBLE before execution.
5. IRREVERSIBLE actions go to daily digest only.
6. Post #leo-coaches (C0AQ4KB1SA0) receipt after every skill completes. (#leo-auto is broken — never use it)
7. Council must approve plan before autopilot starts.
8. Extra-push fires before closeout — always.
9. Advaita Rubric Gate fires after all 30 Diamond-verified items, before Extra-Push — always. No skip.
10. State file writes atomically at closeout. State persists across cycles. Resume check fires at Step 0.
11. Bennett-gate-aging check (Step 1.5) fires every cycle regardless of resume — never skipped.
12. Quality > quantity: 30 high-leverage minimum, sequenced in batches of 10. Each batch closes its own Diamond loop before next batch starts.

### Auto-Default-Option-A Rule (NEW — propagated from autopilot-skill v11)

When overdrive posts an Option A/B/C ping to #leo-coaches (C0AQ4KB1SA0) requesting Bennett's pick, start a 24h timer. If Bennett has not replied at 24h:
- If option tagged IRREVERSIBLE (biometric, financial >$1K, legal, identity) → keep waiting
- Otherwise → auto-execute Option A, post receipt "AUTO-DEFAULT [HH:MM MDT] — Option A executed after 24h Bennett silence per overdrive auto-default rule"
- Log to ~/.openclaw/logs/auto-default-options.jsonl
Unblocks CMO-style 60-item-leverage gates. Council v18 verdict 2026-05-10.

## DIY / Strike / Troubleshoot Coverage
These skills are NOT directly called here — they are loaded and fired by autopilot's BLOCKER LOOP:
- diy-skill: fires on any blocker before escalation
- strike-skill: fires after diy exhausted (5-level escalation)
- troubleshoot-skill: fires via council Step -1A on any failure
No direct call needed from this skill.


---

## Execution Chain (mandatory order)

### Step -2: Self-Improving Loop Verification Pass (v3.7 — runs before Step -1)

Before a new overdrive loop, verify the self-improving loop contracts are current:
- `recap-skill` v5.4+ contains SIL-0 through SIL-4.
- `self-audit-skill` v2.1+ contains `MICRO_RESPONSE_MODE` and the 7-check rubric.
- `council-skill` v28+ contains Permanent Fix Approval Mode.
- `business-audit-skill` v2.4+ accepts heavy self-audit business transfers.
- `angie-audit-skill` v2.5+ aggregates micro-audit trends.
- `lean-startup-skill` v2.2+ contains `SELF_IMPROVEMENT_LOOP_SCORE`.
- `handoff-skill` v9.3+ preserves self-improvement proof in handoffs.

If any contract is missing, run troubleshoot → council Permanent Fix Approval Mode → DIY → patch reversible Drive skill source → readback verify. Do not start the 30-item loop with a broken improvement chain.

### Step 7.5: Post-Loop Self-Improvement Replay (v3.7)

After closeout receipts are produced, replay `self-audit-skill` MICRO_RESPONSE_MODE against the final response and write the result to the overdrive receipt. Any repeated/high defect becomes a council Permanent Fix Approval Mode candidate before the next loop.

### Step -1: Sync Verification Gate (BLOCKING — runs after Step -2)

Before any overdrive work begins, verify local copies of the chained skills match Drive canonical. Drive Desktop sync is unreliable; this gate catches drift.

**Two-tier check (PRIMARY: Drive MCP, FALLBACK: gog CLI). Use whichever is available.**

#### PRIMARY — Drive MCP (all agents: Ivan, Mack, Leo, Tiffany)
For each chained skill, call `mcp__claude_ai_Google_Drive__get_file_metadata` and compare `modifiedTime` against local file mtime. If drift > 1h → force-pull via `read_file_content` and Write to local `~/.claude/skills/<name>/SKILL.md`.

#### FALLBACK — gog CLI (Ivan only, requires GOG_KEYRING_PASSWORD)
```bash
PW=$(grep '^export GOG_KEYRING_PASSWORD=' ~/.zshrc | sed 's/^export GOG_KEYRING_PASSWORD=//' | tr -d '"' | tr -d "'")
GOG_KEYRING_PASSWORD="$PW" gog -a bennett@franchiseki.com download <drive_file_id> --out=~/.claude/skills/<skill-name>/SKILL.md
```

#### Environment-aware behavior
- **Ivan**: full local-vs-Drive mtime check. Force-pull writes to local SKILL.md.
- **Mack**: skip local stat; confirm Drive MCP read works. Treat any successful MCP fetch as PASS.
- **Leo (cloud)**: Drive MCP only — confirm MCP fetch returns valid frontmatter.

If ALL tiers fail: → Execute troubleshoot-skill → council-skill → diy-skill fix. No human re-trigger needed — detection IS the trigger.

### Step 0 — STATE RESUME CHECK + CONTEXT LOAD (parallel)
> Print on resume: `extra_push_embedded: YES | step=6 | auto-fires after advaita-rubric-gate`

**Sub-step A — State resume:**
Read `~/.openclaw/state/overdrive-last-cycle.json`. If file exists AND `last_run_iso` is <24h old AND `domain` matches current request → SKIP audit, resume from `open_queue` array. Post #leo-coaches (C0AQ4KB1SA0): "OVERDRIVE RESUME [HH:MM MDT] — last cycle [N]h ago, [N] open items, [N] stale gates. Skipping audit."
If file missing, >24h old, or domain mismatch → proceed to Step 1 (full audit).

**Sub-step B — Context load (parallel):**
Load: business-audit-skill (1w7pnvUEhmHZjRYGRCPJ643OXlFSJ-2r2), company-context-skill (1NnNpscIwJLTN4jRsFZM-bM8rZKhw4XIT).

**Sub-step C — Suppression filter (added 2026-05-09 by CMO Overnight R3 council):**
Source `~/.openclaw/scripts/load-suppression-list.sh` if present. All candidate items generated downstream MUST pipe through the loader. Suppressed items get prefix `SUPPRESS:` and are silently dropped — never surfaced to Bennett, never re-asked, never planned-around.

### Step 0.5 — SELF-AUDIT ON PRIOR CYCLE (NEW v3.3 — fires BEFORE business-audit)

**Why before business-audit:** business-audit looks OUTSIDE (FKI 36-dim company snapshot). self-audit looks INSIDE (the WORK just done). Running self FIRST surfaces blind spots before business-audit pulls the wider company picture. Mirror before window.

**When fires:**
- ALWAYS if Step 0 found `overdrive-last-cycle.json` <24h old (resume path)
- ALSO if Step 0 found a fresh ship-it / autopilot output to grade
- SKIP only if no prior cycle artifact exists at all (cold start)

**How:**
1. → Execute `self-audit-skill` (Drive `1eL25q60RSbGidFJ0F7tZXiWi1ovCKmyb`) on the prior cycle's deliverable.
2. Capture self-audit output JSON at `~/.openclaw/logs/self-audit-cycle-N.json`.
3. If self-audit `score < 4.0` → tag the cycle "SELF-AUDIT FAIL" in #leo-coaches post.
4. Append `self_audit.priors[]` to the business-audit input context (Step 1 reads them).

Post #leo-coaches (C0AQ4KB1SA0): "SELF-AUDIT [HH:MM MDT] — prior cycle scored [N.N]/5, [N] gaps surfaced, [N] priors fed to business-audit."

### Step 1 — BUSINESS AUDIT (skipped if Step 0 resumed)
Run business-audit-skill full 3-layer. Target 30+ high-leverage items. Deliverable: 30 high-leverage Diamond-verified items minimum. Tag to domain. Save to Drive.
Post #leo-coaches (C0AQ4KB1SA0): "PROACTIVE AUTONOMY [HH:MM MDT] — Audit complete. [N] high-leverage items. Proceeding to council."

> **BLOCKER-VERIFY GATE (mandatory before any BENNETT gate):** → Execute blocker-verify-skill (Drive: search Skills folder `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY` for `blocker-verify-skill`; params: blocker_id, type, url). Skip escalation if status=cached_up or not verified_down. Only escalate if status=verified_down or human_only.
> **SELF-HEAL if blocker-verify-skill not found:** → Search Skills folder Drive for `blocker-verify` → if absent, use diy-skill to run direct HTTP probe (curl -I <url>, timeout 10s) and classify result manually: 200=cached_up, non-200=verified_down.

### Step 1.5 — BENNETT-GATE-AGING ESCALATION (BLOCKING — fires every cycle)
**Always fires** — regardless of Step 0 resume. Never skipped.

Read digest in priority order: (1) Drive `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/overdrive-skill/state/daily-digest-mirror-<today>.md` via MCP (cross-agent canonical); (2) fallback to `~/.openclaw/workspace/daily-digest.md` (local, Ivan-only). Also read prior `overdrive-last-cycle.json`. For every Bennett gate (IRREVERSIBLE pending) older than 7 days:
- Tag `STALE` and surface at TOP of today's digest
- Add 1-line context: "First raised [date] — [N] days open. Blocking: [downstream items count]"
- If gate is >14 days old → also DM Bennett directly via Slack with single-line: "STALE GATE >14d: [item] — pending since [date]."

Post #leo-coaches (C0AQ4KB1SA0): "GATE AGING [HH:MM MDT] — [N] stale gates surfaced ([N] >14d direct-DM'd)."

### Step 2 — COUNCIL APPROVAL (BLOCKING)
Run council-skill v28+ (1MpUHqm5dMHY1dF_kqm88pVCj7FT49ZYr). Threshold: Operational 4.0 / Strategic 4.5 / Irreversible 4.7.
NOTE: Step -2 SIL contract requires council-skill v28+. If local SKILL.md reports v15 or earlier → force-pull from Drive before proceeding. The Drive ID is authoritative.
Queue IRREVERSIBLE items to digest before autopilot starts.
Post #leo-coaches (C0AQ4KB1SA0): "COUNCIL [HH:MM MDT] — [score]/5. [N] approved. [N] IRREVERSIBLE queued."

### Step 3 — AUTOPILOT EXECUTION (BATCHES OF 10, MIN 30 TOTAL)
Run autopilot-skill v9 (10KBx34OrzdlX0_RN9x8zqNvQEprLdQow) in **3 sequential batches of 10**.

**Loop-Closure Gate (v3.9.1 — 2026-06-03):** Before any batch starts, run:
```bash
bash ~/.openclaw/scripts/loop-closure-gate.sh || { echo "LOOP-CLOSURE GATE FAIL — prior fixes reverting; verify before new Diamonds"; }
```
If gate fails (exit 1): pause new done-claims, verify prior fixes survive (loop_closure_rate ≥ 0.5), re-run gate.

**Batch loop:**
1. Autopilot fires 10 highest-leverage items (parallel SANDBOX, dispatched CLI, IRREVERSIBLE → digest).
2. Diamond gate runs on the 10 (Step 4 below). Failures → troubleshoot → re-execute → re-verify.
3. Once 10 pass Diamond → advance to next batch of 10.
4. Repeat until 30 total Diamond-passed items.

**If a batch can't reach 10 passes after 2 troubleshoot loops:** carry the failed items forward into the open_queue (state file), and pull replacement items from audit residual to fill the batch. Cycle does not stall.

Post #leo-coaches (C0AQ4KB1SA0) receipt after each batch: "BATCH [n/3] [HH:MM MDT] — 10 items shipped, Diamond-passed."

### Step 4 — DIAMOND VERIFICATION (per batch)
Run diamond-skill v2 (1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT) **per batch of 10**, not once at end.
3-check per item: Adversarial T1 + Recovery T2 + Boundary T3.
Any failure: troubleshoot > re-execute > re-verify (max 2 loops then carry forward).
Rationale: catches failures within 10 items, not after 30. Cheap to fix mid-cycle.

### Step 4.5 — ADVAITA VISION RUBRIC GATE (BLOCKING — fires ONCE on all 30)
Fires after all 3 batches complete (30 Diamond-passed items), before Extra-Push.

Rubric Source: Load Advaita Vision FINAL May 2026 — Drive ID: 1VMmKRR1MuNc0_Z4vngFM4u-GBi0PbT-6E8rjlXDpNHY

5-Question Rubric (score each 0–2, max 10):
1. Bennett-free? Does output move without Bennett touching it? → Pass ≥1.5
2. Operational layer? Removes a human from an operational task? → Pass ≥1.5
3. North Star alignment? Moves toward: one green dashboard, laptop closed at 3pm? → Pass ≥1.5
4. May 17 readiness? Contributes to any of the 8 deployment requirements? → Pass ≥1
5. Self-improving? Makes system smarter or more autonomous next cycle? → Pass ≥1

Scoring per item:
- 8–10 → PASS — counts toward shipped
- 5–7 → REVISE — feed to Extra-Push residual queue
- 0–4 → FAIL — escalate to council, drop from shipped count

Post #leo-coaches (C0AQ4KB1SA0): "ADVAITA RUBRIC [HH:MM MDT] — 30 items graded. [N] PASS / [N] REVISE / [N] FAIL. Proceeding to Extra-Push on [N] residual."

### Step 5 — EXTRA PUSH (RESIDUAL ONLY)
Run extra-push-skill (16pUBt5cfyyMStxlGD5sC2Mm_MULzAvW3) **only on REVISE items from rubric gate** — not a fresh 20-item sprint.
C-suite lens applied to residual. Goal: lift REVISE items to PASS on re-grade. Items that still fail after push → state file `carry_forward` array.

### Step 6 — SKILL EXECUTION TABLE

| Skill | Drive fileId | Executed | Artifacts |
|---|---|---|---|
| self-audit-skill (Step 0.5) | 1eL25q60RSbGidFJ0F7tZXiWi1ovCKmyb | | |
| business-audit-skill | 1w7pnvUEhmHZjRYGRCPJ643OXlFSJ-2r2 | | |
| council-skill v28+ | 1MpUHqm5dMHY1dF_kqm88pVCj7FT49ZYr | | |
| autopilot-skill v9 (×3 batches) | 10KBx34OrzdlX0_RN9x8zqNvQEprLdQow | | |
| diamond-skill v2 (×3 batches) | 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT | | |
| Advaita Vision Rubric Gate (×1) | 1VMmKRR1MuNc0_Z4vngFM4u-GBi0PbT-6E8rjlXDpNHY | | |
| extra-push-skill v2.0 (residual) | 16pUBt5cfyyMStxlGD5sC2Mm_MULzAvW3 | | |
| closeout-skill v10 | 1F9OEFprvRhltoPmST7_zdlPEPH38MykJ | | |

### Step 6.5 — CEO EMAIL (MANDATORY — final visibility before closeout)

→ Execute `ceo-email-skill` (Drive fileId `1yKAMge08xa8gAo0RCWNhoR0Rwr5cneth`).

Pass JSON payload built from chain receipts:
- `project_name`: cycle slug
- `advaita_pct_before` / `advaita_pct_after`: from `~/.openclaw/state/advaita-autonomy-baseline.json`
- `verdict`: 1-sentence what shipped
- `bullets`: max 5, ≤25 words each
- `self_audit_score`: Step 0.5 self-audit score
- `decisions`: 0-3 Notion Q&A rows seeded for Bennett gates this cycle
- `next_topic`: next cycle topic
- `audit_artifact_url`: link to Notion sprint row

Email sent to `bennett@franchiseki.com`. Log msgId to `~/.openclaw/logs/ceo-email-sends.jsonl`.

Anti-patterns:
- ❌ Skipping CEO email (-5 penalty)
- ❌ Emailing brent@franchiseki.com

### Step 7 — CLOSEOUT + STATE PERSISTENCE + CEO HTML + UNIFIED RECEIPT (v3.6 SCHEMA EMBEDDED — never skipped)

Run closeout-skill v10 (1F9OEFprvRhltoPmST7_zdlPEPH38MykJ) WITH the v3.6 schema patch embedded below. Cannot be skipped. Cannot be deferred.

**Sub-step A — Atomic state write:**
Write `~/.openclaw/state/overdrive-last-cycle.json` (atomic: write tmp file → mv → rename). Also mirror to Drive `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/overdrive-skill/state/overdrive-last-cycle-<thread_id>.json` (CLOUD-MODE STATE PATHS rule).

**Sub-step B — HTTP 200 Diamond Proof Verification (v3.6 NEW — MECHANICAL)**

For each Diamond shipped this cycle:
```
proof_pass = 0
proof_total = 0
phantom_diamonds = []

for diamond in cycle_diamonds:
    proof_url = diamond.proof_link
    if not proof_url:
        phantom_diamonds.append({"item": diamond.id, "reason": "no_proof_link"})
        continue
    proof_total += 1
    response = curl_head(proof_url, timeout=10)
    if response.status_code == 200:
        proof_pass += 1
    else:
        phantom_diamonds.append({"item": diamond.id, "reason": f"http_{response.status_code}"})

proof_pass_rate = (proof_pass / proof_total * 100) if proof_total > 0 else 0
```

If `proof_pass_rate < 100%`:
- Log phantom-diamonds to `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/wave-audit-skill/state/phantom-diamonds-<thread_id>.jsonl`
- Auto-flip phantom rows back to 🟡 Yellow in Notion
- Reduce diamonds count in receipt by phantom count

**Sub-step C — PROCESS_IMPROVEMENT_GATE Auto-Suggest (v3.6 NEW — MECHANICAL)**
```
improvements = read_jsonl(
    "1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/improvements-log.jsonl"
).filter(thread_id=current_thread_id)

if len(improvements) == 0:
    auto = council_skill.suggest_single_improvement(
        context=current_cycle_summary,
        skills_used=current_skill_chain
    )
    write_jsonl(improvements_log_path, auto)
    improvements = [auto]
```
No human in loop. Closeout cannot exit with improvements_count=0.

**Sub-step D — CEO HTML primary output (preserved from v3.5):**
Generate `~/Desktop/overdrive-cycle-YYYY-MM-DD-HHMM.html` — single page, white background, Apple-style.

Required top table (impact-first, before shipped list):
- Time savings, $out savings, $in pipeline, Advaita delta, Diamond count, Bennett gates

Top item rule: 3-5 words minimum, verb-led, names the actual artifact — NOT a category restatement.

**Sub-step E — UNIFIED RECEIPT POST (v3.6 NEW — MANDATORY SCHEMA, REPLACES old "OVERDRIVE COMPLETE" string)**

Post to #leo-coaches (`C0AQ4KB1SA0`) ONE-LINE compact: (#leo-auto C0AKXT2S1T2 is broken — use #leo-coaches)

```
THREAD_<id>_COMPLETE wave=<label> diamonds=<K> budget=$<X>/$<cap> elapsed=<min> scan_count=N/A_overdrive improvements=<I> ride_along=<R> proof_pass_rate=<P>% public=<URL> phase_state=<DRIVE_ID> skill=overdrive@v3.9
```

**11 mandatory fields. Closeout REJECTED at post if any missing.**

| Field | Required | Sentinel allowed |
|---|---|---|
| `wave=<label>` | Yes | `wave=overdrive-<date>` if not set |
| `diamonds=<K>` | Yes | `diamonds=0` |
| `budget=$<X>/$<cap>` | Yes | `budget=N/A_cli` for CLI cycles |
| `elapsed=<min>` | Yes | never blank |
| `scan_count` | Yes | `scan_count=N/A_overdrive` (overdrive uses batches not Phase 11.5 SCAN) |
| `improvements=<I>` | Yes | NEVER 0 (Sub-step C auto-fills) |
| `ride_along=<R>` | Yes | `ride_along=0` for spec-pure cycles |
| `proof_pass_rate=<P>%` | Yes | from Sub-step B |
| `public=<URL>` | Yes | `public=none_<reason>` |
| `phase_state=<DRIVE_ID>` | Yes | Drive ID from Sub-step A |
| `skill=overdrive@v3.9` | Yes | never blank |

This unified schema is auto-discoverable by **wave-audit-skill v1.0** which auto-fires when all THREAD_X_COMPLETE receipts for a wave_label arrive.

See: `closeout-receipt-schema-patch-v1.md` (Drive `1uScideBdlllxvlxH5WuKC9Gx-__NNSoj`) for canonical schema source.

**Sub-step F — Master tracker append**
NOTION_ADD_MULTIPLE_PAGE_CONTENT to current wave's master tracker page with the same compact one-liner + public URL hyperlink.

**Legacy fallback:** If wave_label NOT set (legacy overdrive invocation outside wave context), ALSO post the human-readable line: "OVERDRIVE COMPLETE [HH:MM MDT] — N shipped, [G] gates open, Advaita +[A]pp, state saved." Both lines, in order. New unified line is canonical for wave-audit-skill consumption.

---

## Anti-Patterns
- Skipping business-audit when Step 0 did NOT resume: -3
- Skipping council: -3
- Skipping extra-push: -2
- Skipping closeout: -5
- IRREVERSIBLE auto-executed without digest: -5
- "I need a human" without 8 DIY steps: -3
- Skill table missing: -2
- Skipping Advaita Rubric Gate: -5
- Running gate without loading Drive doc: -3
- Skipping Step 1.5 gate-aging on resume: -5
- Running Diamond once at end instead of per batch: -3
- Failing to write state file at closeout: -5
- CEO HTML missing CFO Quarterly impact table at top: -3
- "Top item" being category restatement instead of verb-led 3-5 word descriptor: -2
- Padding to hit 30 with low-leverage items (rubric will fail them anyway): -3
- **(v3.6) Posting old "OVERDRIVE COMPLETE" string WITHOUT also posting unified compact receipt schema: -5** (breaks wave-audit-skill auto-discovery)
- **(v3.6) Skipping HTTP 200 Proof Link verification in Sub-step B: -5** (phantom-Diamonds enter the dataset)
- **(v3.6) Posting receipt with `improvements=0` instead of running auto-suggest in Sub-step C: -5** (PROCESS_IMPROVEMENT_GATE failure)
- **(v3.6) Receipt missing any of 11 mandatory fields: -5** (closeout REJECTED at post time)

> **See also:** `bennett-mode-skill` v2.4+ invokes this skill in its 13-phase meta-chain. `wave-audit-skill` v1.0 auto-discovers this skill's unified receipts. `closeout-receipt-schema-patch-v1.md` (Drive `1uScideBdlllxvlxH5WuKC9Gx-__NNSoj`) is the canonical receipt schema source.

---

## Self-Audit Checklist

Binary checks for Angie (or any auditor) to verify overdrive-skill health. Each item is YES/NO — no partial credit.

1. **UNIFIED RECEIPT SCHEMA COMPLETE** — Does the most recent #leo-coaches THREAD_X_COMPLETE post contain all 11 mandatory fields (`wave`, `diamonds`, `budget`, `elapsed`, `scan_count`, `improvements`, `ride_along`, `proof_pass_rate`, `public`, `phase_state`, `skill=overdrive@v3.9`)? YES / NO

2. **HTTP 200 PROOF LINKS** — Is `proof_pass_rate` in the last receipt equal to 100% (i.e., zero phantom-diamonds were logged to `phantom-diamonds-<thread_id>.jsonl`)? YES / NO

3. **IMPROVEMENTS COUNT > 0** — Does the last receipt show `improvements` ≥ 1 (Sub-step C auto-suggest fired; closeout never exited with `improvements=0`)? YES / NO

4. **STATE FILE PERSISTS** — Does `~/.openclaw/state/overdrive-last-cycle.json` exist, contain a `last_run_iso` within the last 24h, and mirror to Drive `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/overdrive-skill/state/`? YES / NO

5. **ADVAITA RUBRIC GATE FIRED** — Is there a #leo-coaches post line starting "ADVAITA RUBRIC [HH:MM MDT]" for the last cycle, with a PASS/REVISE/FAIL breakdown summing to 30 items? YES / NO

6. **DIAMOND GATE PER BATCH (NOT ONCE AT END)** — Are there exactly 3 separate "BATCH [n/3]" receipts in #leo-coaches for the last cycle (one per batch of 10), each confirming Diamond-passed before advancing? YES / NO

7. **CEO EMAIL SENT** — Does `~/.openclaw/logs/ceo-email-sends.jsonl` contain a record with a msgId for the current cycle's `project_name`, sent to `bennett@franchiseki.com`? YES / NO

8. **IRREVERSIBLE ACTIONS STAGED ONLY** — Is every IRREVERSIBLE action from the cycle present in `~/.openclaw/workspace/daily-digest.md` (and its Drive mirror) and absent from direct-execution logs? YES / NO
