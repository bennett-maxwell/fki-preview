---
name: handoff-skill
drive_file_id: 11HJUvXAmWscPRZin3e2Zezfa0JuEYEmq
description: >
  Creates a compact handoff summary for continuing work in a new thread.
  TRIGGER when: user says "give me a handoff prompt", "handoff prompt",
  "new thread handoff", "continue in new thread", or "handoff".
  Automatically runs closeout-skill first, then builds the compact summary.
  v9.3 adds self-improving-loop handoff proof: every handoff after skill patches or audits must preserve the micro-audit result, permanent-fix ledger, Drive readback proof, and remaining Angie/business follow-up.
  v9.2 adds recap-final proof: handoff output must carry recap-skill proof, visible recap footer markers, and an explicit partial label if any closeout/Slack/Notion side effect cannot be proven.
  DO NOT TRIGGER for: mid-session status checks.
version: 9.7
last_updated: 2026-05-30
patched_v9_3: "2026-05-27 — Adds Self-Improving Loop Handoff Proof for recap/self-audit/overdrive/council/business/Angie/lean skill changes."
patched_v9_4: "2026-05-27 — GATE-VERIFY-REQUIRED: all human gates must be live-probe verified before appearing in handoff. Handoff docs/prior sessions are NOT proof. Added Step 1.6."
patched_v9_5: "2026-05-27 — Correction Final Verifier Gate. Handoffs after false-fix, self-audit, recap, task-review, overdrive, or skill-compliance corrections must preserve `tools/fki_correction_final_verify.py` proof and the 20-breakpoint result."
patched_v9_6: "2026-05-30 — Six permanent fixes: (1) state file field map corrected to actual overdrive-last-cycle.json + handoff-latest.json schema; (2) recap-skill version stale ref updated to v8.5; (3) verifier-script missing-path fallback added; (4) billing/model guard added to Step 3; (5) STATE RULE cross-session write requirement added; (6) programmatic-invocation read-only trigger added."
deps:
  - name: closeout-skill
    fileId: 1IfdB8YM-F9GzPHka44uE199NqPFAI4gB
  - name: recap-skill
    fileId: 1e9nw03yKQ9tjD4k3zEBAhQsEnH0qZWe6
  - name: handoff
    fileId: 15PoPnDwMdduVWDfabjXeq0fR_2NInKoC
---
## North Star
Succeeds when all open items are saved to memory and Notion, the handoff is posted to #leo-coaches so any agent can pick it up instantly, recap-skill fires as the final action with proof, the final answer still contains visible recap footer markers, AND the handoff numbers reconcile against the canonical state file (no drift).

---

# Handoff Skill v9.5

## v9.5 Patch — Correction Final Verifier Proof

Any handoff following a correction/failure-chain audit must include:
- strict verifier command used;
- verifier pass/fail result;
- draft hash;
- open Yellow items;
- exact blocker for any skipped closeout, Slack, Notion, memory, or Diamond step.

**v9.6 VERIFIER PATH GUARD:** The script `tools/fki_correction_final_verify.py` references `~/tools/` which does NOT exist on FKI machines as of 2026-05-30. Before running the verifier:
1. Check `~/tools/fki_correction_final_verify.py` — if missing, search Drive for the file ID referenced in gatekeeper state or in `~/.openclaw/state/gatekeeper-ledger.jsonl`.
2. If not found on Drive, emit `verifier: UNAVAILABLE — ~/tools/ missing, Drive search negative` and proceed with the manual 20-breakpoint checklist instead (list each breakpoint with pass/fail inline). Do NOT silently skip the v9.5 gate; replace with the manual checklist as the fallback proof.

Category: Session Management

## Purpose
Close the current thread cleanly and produce a compact handoff for the next session. The Notion page IS the handoff — it holds all context. The compact block is the on-ramp.

**v8 fix:** Step 1.5 (NEW) reads `~/.openclaw/state/overdrive-last-cycle.json` and reconciles handoff numbers against it. Prevents the drift that caused 22-shipped/capi-pending text while state showed 150-shipped/capi-LIVE (incident 2026-05-08).

## v9.1 Patch — Read-Only Handoff Mode

When invoked by a no-send/no-mutate audit, A-Z rerun, Gatekeeper proposal, Batch Overdrive gap scan, or any parent task that is not Diamond, use `handoff_read_only=true`.

In `handoff_read_only=true`:
- Skip closeout-skill mutation steps.
- Skip `#leo-coaches` posting.
- Skip Notion mutation.
- Skip recap trigger-file writes.
- Emit local handoff text and proof paths only.
- State the parent verdict honestly as Yellow/Red if any Advaita, credential, finance, legal, production, or external-send gate remains open.
- Do not send email, Slack, GHL, Gmail, Notion updates, Drive replacements, deploys, deletes, credential changes, legal documents, payroll, or ad-spend actions.

## v9.2 Patch — Recap-Final Proof Gate

When handoff-skill is invoked after a recap, self-audit, closeout, permanent-fix, or skill-compliance correction:
- Load the current Drive `recap-skill` and record file ID, version, and modifiedTime/hash in the handoff proof line.
- The handoff text must include a visible recap footer marker set: PROJECT, ORIGINAL/THREAD, MEMORY, AI OPEN, HUMAN OPEN, five options with one starred recommendation, and CONTEXT.
- The final ChatGPT/Codex answer must include the handoff proof block before the recap footer.
- If #leo-coaches posting, Notion mutation, memory logging, or closeout is skipped or unavailable, write `handoff partial: <exact blocker>` and `recap partial: <exact blocker>`.
- Never treat a local handoff note as complete unless the parent task explicitly required read-only mode.

## v9.3 Patch — Self-Improving Loop Handoff Proof

When handoff-skill follows an overdrive, self-audit, skill patch, permanent-fix, or recap correction, the handoff must include a `SELF-IMPROVING LOOP LEDGER`.

Required fields:
```yaml
self_improving_loop_ledger:
  micro_audit_result: pass | corrected | escalated | partial:<blocker>
  permanent_fixes_applied: []
  drive_readback_proof: []
  council_permanent_fix_verdict: approve | reject | partial | not_required
  heavy_scope_transfers:
    business_audit: []
    angie_audit: []
    lean_startup: []
  next_replay_test: <how the next agent verifies the fix held>
```

Do not collapse the ledger into prose. If a field cannot be proven, keep the field and label the blocker.

## Trigger Phrases
- "give me a handoff prompt" / "handoff prompt" / "new thread handoff" / "continue in new thread" / "handoff"
- **Programmatic invocation** (called by another skill without a human phrase): check the caller context.
  - If caller is an audit, gatekeeper, batch-overdrive, A-Z rerun, or gap-scan → auto-set `handoff_read_only=true` (v9.1 mode).
  - If caller is an overdrive, closeout, or session-end → run full mode.
  - If caller context is ambiguous → default to `handoff_read_only=true` and emit `INVOCATION MODE: read-only (ambiguous caller)` in output so the agent can override explicitly.

## Workflow

### Step 1: Run closeout-skill First
Execute the full closeout-skill v9+ (Step -1 sync gate, recap-skill at Step 0, Diamond verification at Step 4.5, Step 5b bennett-rules audit). The Notion page it creates IS the handoff document. If Step -1 sync gate fails AND skills can't be force-pulled, ABORT — do not produce a handoff from a stale chain.

### Step 1.5: STATE-FILE RECONCILE (v8 — BLOCKING; field map corrected v9.6)
Read BOTH state files if they exist:

**Primary:** `~/.openclaw/state/handoff-latest.json` — actual schema:
- `diamonds_shipped` → use as "shipped today" count (NOT `cumulative_shipped`)
- `advaita_after` → Advaita % post-session (NOT `advaita_vision_pct_estimate`)
- `open_gates[]` → gate objects with `gate`, `type`, `artifact` keys
- `carry_forward[]` → string list of next-session queue items
- `cycle` → session/cycle label

**Secondary:** `~/.openclaw/state/overdrive-last-cycle.json` — actual schema:
- `cycle_id` → cycle identifier
- `opts_shipped[]` → shipped items list
- `shipped_verified[]` → verified deliverables
- `true_bennett_gates` → count of real human gates
- `false_gates_reconfirmed[]` → services confirmed NOT gated

NOTE: The legacy field names `cumulative_shipped`, `cycle_count_today`, `capi_status`, and `advaita_vision_pct_estimate` do NOT exist in current state files. Do not look for them. If reading a state file and finding none of these fields, switch to the corrected schema above rather than emitting "STATE FILE MISSING."

If the recap text in Step 4 disagrees with state file → state file wins, recap is rewritten. NEVER ship a handoff whose numbers contradict state. If BOTH state files are missing or older than 24h, flag explicitly: "STATE FILE MISSING/STALE — handoff numbers are conversation-only."

### Step 1.6: GATE-VERIFY-REQUIRED (NEW v9.4 — BLOCKING before any gate enters handoff)

Before any item from `open_gates[]`, state file, prior session doc, or conversation is included in the handoff as a human gate:

**GV-1: Gate type** — is this biometric/legal/financial>$1K/external contract? → TRUE human gate (list it). All others proceed to GV-2.

**GV-2: Credential/API gates** — run live probe:
```bash
~/.openclaw/bin/token-probe.sh <service>
```
- HTTP 200 → **NOT a human gate**. Token valid. Execute directly. REMOVE from gate list.
- HTTP 401 → expired → HUMAN GATE confirmed (route to rotation_owner per Vault).
- HTTP 403 → wrong ID/scope → fix-call (not rotation). **NOT a human gate.**
- HTTP 429 → rate limit → wait 60min. **NOT a human gate.**

**GV-3: UI/platform gates** → attempt GHL API or BrowserSession first. Only gate if documented automated failure.

**GV-4: Prior session / handoff doc status** → **NEVER trust**. "Prior session said 401" is NOT proof. Re-probe live. Any gate sourced from a doc >1hr old requires re-verification before listing.

**OUTPUT:** Handoff gate list must include `probe_receipt: <ts|"true_human_gate">` per row. Gate with no receipt = `gate_status: suspected` (not listed as confirmed human gate).

### Step 2: ✓ Apply recap-skill at the top
→ Execute recap-skill (current version: v8.5, Drive ID: 1e9nw03yKQ9tjD4k3zEBAhQsEnH0qZWe6). Its Mode 1 footer is the recap — do NOT inline a separate `## 📋 Recap` 5-bullet block (removed in recap-skill v3.0 to stop duplicate recaps; current v8.5 behavior is unchanged on this). Numbers in the footer MUST match Step 1.5 reconcile.

NOTE on trigger file (v9.6 correction): The trigger file mechanism `~/.openclaw/state/recap-cycle-trigger.txt` references "recap-skill v3.5" in its original description. recap-skill is now at v8.5. The trigger-file mechanism and mtime-detection still apply — the version reference was stale. Write the trigger file as documented; v8.5 detects it identically.

### Step 3: Model Recommendation (Opus / Sonnet / Haiku)
**Opus** — novel architecture, high-stakes reasoning, cross-system strategy.
**Sonnet** — multi-file code, live system changes, state verification.
**Haiku** — well-defined tasks, routing, status checks, simple writes.

**BILLING GUARD (v9.6 — non-negotiable):** NEVER recommend any model with "(1M context)", "1M ctx", or similar extended-context label. These variants bill to API credits and are forbidden per CLAUDE.md billing rule. Only subscription-billed variants: `claude-sonnet-4-6`, `claude-opus-4-7` (standard), `claude-haiku-4-5-20251001`. If you are unsure whether a variant is subscription-billed, default to `claude-sonnet-4-6`.

State clearly:
```
MODEL: [Primary] | Fallback: [Fallback]
Reason: [1 sentence]
```

### Step 4: Build the Compact Handoff

```
[recap-skill Mode 1 footer goes here — emitted by recap-skill, not inlined]

[HANDOFF] [Project Title]
🔗 [Notion URL] · State: ~/.openclaw/state/overdrive-last-cycle.json (cycle N, X shipped)
MODEL: [Primary] | Fallback: [Fallback]
Reason: [1 sentence]
```

### Step 5: Post to #leo-coaches
Post the recap + on-ramp block above to #leo-coaches (C0AQ4KB1SA0). Nothing else.

### Step 5.5: Final-Answer Recap Verification (v9.2)
Before the user-facing final answer, verify:
1. Handoff proof includes Notion URL or local receipt path plus Slack link/draft status when applicable.
2. Recap proof includes Drive recap-skill file ID and version/modifiedTime/hash.
3. Final answer contains recap footer markers from recap-skill FRC-7.
4. Any missing side effect is labeled `handoff partial` and `recap partial`.

## Red Lines
- NEVER skip closeout-skill — Notion page (with Diamond verification) must exist before handoff is built
- NEVER skip Step 1.5 state-file reconcile — drift caused 2026-05-08 incident
- NEVER skip the recap-skill block at top — first thing Bennett reads
- NEVER finish handoff without a recap-skill proof line and final-answer footer marker check
- NEVER ship handoff numbers that contradict state file — state wins
- Output is recap + on-ramp + Notion link — nothing else
- The #leo-coaches post IS the handoff output
- Skills are ONLY edited at Drive folder 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY. Use `gog upload --replace=<id>` to PATCH this file.
- STATE RULE (v9.6): Local `~/.openclaw/state/` files are machine-local and invisible to other agents picking up the handoff. Any open_gates, carry_forward items, or session state read from local files MUST also be written to the Notion closeout page (closeout-skill handles this) AND posted in the #leo-coaches message so any agent on any machine can resume without reading local disk. Never rely solely on local state for cross-session continuity.

## Final Steps (MANDATORY ORDER)
1. Post to #leo-coaches (`C0AQ4KB1SA0`) with Notion sprint link:
   `HANDOFF READY: [session title] | Notion: [sprint URL] | Open items: [N] | State: cycle [N], [X] shipped | Any agent can pick up`
2. Write end-of-thread trigger file so recap-skill v3.5 fires its 2-round council-execute loop:
   ```bash
   mkdir -p ~/.openclaw/state && date +%s > ~/.openclaw/state/recap-cycle-trigger.txt
   ```
   (recap-skill v3.5 detects the file's mtime <60s and fires the loop on Mack/Ivan only — Leo identity gate skips. Recursion lock at `~/.openclaw/state/recap-cycle.lock` prevents re-entry. Step 2 line 53 recap call is NOT affected — that's the top-of-handoff emit, no trigger written there.)
3. Verify the user-facing final answer contains recap-skill FRC-7 markers and a recap proof line.
4. Call `Skill("recap-skill")` as the absolute last action.

## Changelog
- v9.6 (2026-05-30): Six permanent fixes from self-audit: (1) State file field map corrected — overdrive-last-cycle.json fields are `cycle_id/opts_shipped/shipped_verified`, NOT `cumulative_shipped/capi_status/advaita_vision_pct_estimate`; handoff-latest.json is primary source for `diamonds_shipped/open_gates/carry_forward`. (2) recap-skill version ref updated from stale "v3.5/v3.0" to current v8.5 throughout. (3) Verifier script fallback added — `~/tools/fki_correction_final_verify.py` path does not exist; manual 20-breakpoint checklist is now the documented fallback. (4) Billing guard added to Step 3 model recommendation — prohibits 1M-context variants. (5) STATE RULE compliance added to Red Lines — local state must be mirrored to Notion/leo-coaches for cross-agent pickup. (6) Programmatic-invocation read-only trigger added to Trigger Phrases for non-human callers.
- v9.5 (2026-05-27): Correction Final Verifier Gate — preserve fki_correction_final_verify.py proof and 20-breakpoint result.
- v9.4 (2026-05-27): GATE-VERIFY-REQUIRED — all human gates must be live-probe verified. Added Step 1.6.
- v9.3 (2026-05-27): Added Self-Improving Loop Handoff Proof ledger so every audit/overdrive/skill-patch handoff preserves micro-audit status, durable fixes, Drive readback proof, and Angie/business/lean follow-up.
- v9.2 (2026-05-27): Added recap-final proof gate, final-answer marker check, handoff/recap partial labels, and proof-line requirement after recap/compliance corrections.
- v9 (2026-05-09): Added Step 2 trigger-file writer to wire recap-skill end-of-thread council-execute loop.
- v8 (2026-05-09): Added Step 1.5 state-file reconcile. Fixes drift incident where handoff text said "22 shipped/CAPI pending" while state showed "150 shipped/CAPI LIVE."
- v7 (prior): Initial closeout + recap pipeline.


## v9.7 PATCH — Memory Hard Gate for Handoff (2026-06-03)

Trigger: any `handoff`, `handoff-skill`, or handoff-style continuation prompt.

Rule: `handoff_read_only` may skip Slack, Notion mutation, and recap trigger writes when protected or unavailable, but it may **not** silently skip memory. Before the final answer, run `memory-skill` or create a canonical memory receipt. A handoff final answer must include one of:

1. `memory saved` proof: memory-skill receipt path, Codex ad_hoc memory note path, or canonical Drive memory file ID plus readback; or
2. `memory partial:<exact blocker>` plus local reconciliation receipt path and an AI-open item to reconcile it.

Never output only "shared/fleet memory not saved" after a handoff without also creating the reconciliation receipt and making memory reconciliation the first AI-open item.

## v9.8 PATCH — Session Memory Lock for Handoff (2026-06-04)

Trigger: any `handoff`, `handoff-skill`, or handoff-ready close.

Rule: a handoff cannot close on recap text alone. Before the final answer:

1. run `memory-skill`;
2. ensure `~/.openclaw/state/memory-skill-receipts.jsonl` contains a receipt keyed by the current `session_id` or `thread`;
3. only then render the handoff footer.

If no durable memory changed, the memory-skill no-op scan still needs a session-scoped receipt with `written: []` and `skipped` reasons. If canonical memory write is blocked, label `memory partial:<exact blocker>` and create a reconciliation receipt. Do not call handoff complete without one of those two proofs.
