---
name: recap-skill
version: 8.9
drive_file_id: 1e9nw03yKQ9tjD4k3zEBAhQsEnH0qZWe6
last_updated: 2026-06-01
lss_score: 96
v8_9_codex_render_gate: "2026-06-01 — Bennett correction: measurement fields alone are still not enough if the response does not render the recap footer. Codex must render the locked footer shape: PROJECT, ORIGINAL, THREAD, MEMORY, AI OPEN, HUMAN OPEN, exactly five numbered options with one starred recommendation, Reason, self-audit, response_score, METRICS, recap-skill version, CONTEXT, receipt_path, draft_sha256, and recap_fire_rate_last20."
v8_8_revenue_automation_declarations: "2026-06-01 — Bennett carry-forward: REVENUE_DECLARATION + AUTOMATION_DECLARATION blocks added to deliverable-type responses (prompt keyword: build/create/deploy/send/run/email/blueprint). REVENUE_DECLARATION = $ pipeline | leads affected | campaign/source. AUTOMATION_DECLARATION = skills csv | model id | agent | cycle type | ISO ts. Added to footer LOCKED LAYOUT + FRC-7 required markers. Enables accountability tracing across all shipped deliverables. leo_wo_count=0."
v8_7_codex_measurement_gate: "2026-06-01 — Bennett correction: a Codex fallback one-line recap label is not enough. Non-hook seats must measure recap-fire from the ledger, include response_score, draft_sha256, current receipt_path, recap_fire_rate_last20, and the required footer markers in the final response. If these are missing, recap is NOT counted as fired."
v8_6_codex_fallback: "2026-06-01 — Added mandatory Codex/ChatGPT non-hook fallback. When Skill(\"recap-skill\") and Claude Stop hooks are unavailable, the agent must load this canonical SKILL.md, write a workspace recap receipt, append recap-fire-ledger.jsonl, label any Notion/Drive side-effect as partial, and include a recap-skill closeout line in the final response. This closes the Codex surface gap from claude-md-skill v9.3."
monitor_tables_v8_2: "2026-05-29 — Bennett directive: replaced the single 🔁 LOOP RESULTS line + single self-audit: line with TWO monitor tables rendered ABOVE the 🧵 PROJECT name so self-learning + autonomous work is the FIRST thing he sees. (1) 🔁 AUTONOMOUS LOOPS table — 4 council rounds × [✅ approved · 🔧 permanent change · 👀 you'll notice]. (2) 🪞 SELF-AUDIT table — [📉 score before · ⚠️ issues · 🔧 what fixed+rule · 📈 score after]. Self-audit now carries the 🪞 emoji marker (Bennett: 'use an emoji not number 5'). Both [OPTIONAL] — render only when end-of-thread loop fired (lean per SKILL-SLIM). Every cell computed from recap-loop.jsonl / false-done-corrections.jsonl / self-audit MICRO_RESPONSE — never asserted. Council 4.1/5 (threshold 3.5). recap-skill-tests.sh hardened v8.0 (version + marker assertions de-staled)."
v8_5_audit_2026_05_30: "2026-05-30 — Permanent-fix audit (5 fixes): (1) Self-Audit Checklist item 2 force-pull threshold updated 8.1→8.4 to match current version so Angie doesn't false-flag v8.2/v8.3 skills; (2) #leo-auto (broken C0AKXT2S1T2) replaced with #leo-coaches (C0AQ4KB1SA0) in POST-LOOP 7/7.5 and Notion Auto-Create; (3) FD-4 escalation trigger aligned — checklist item 30 'count≥3' corrected to match FD-4 body '≥2 same claim_type in 7d' (proof_failure still first-occurrence); (4) memory-hygiene.py --apply '(Mack)' annotation removed — capability-symmetry fix (Ivan agents were skipping OVER_CAP rebuild thinking it was Mack-only); (5) fd-pattern-log.json given canonical path ~/.openclaw/state/fd-pattern-log.json so agents on both machines create/read it consistently."
v8_4_crossagent_fix: "2026-05-29 — Self-audit round (Bennett: 'update 2-3 times'). 4 real defects fixed: (1) byte-guard + per-response write paths were hardcoded /Users/temp (Mack-only) → portable ~/.claude/projects/-Users-$(whoami)/memory/ so 🧠 GREEN computes on Ivan too (was silently failing — dir doesn't exist on Ivan, CAPABILITY-SYMMETRY violation); (2) 🔁 table header hardcoded '(4 rounds)' contradicted the fewer-rows-is-normal rule → 'up to 4 rounds; render only the rounds that ran'; (3) ➡️ TOTAL line was prose-only → now in the render template; (4) trend arrow ↑/↓/→ was prose-only → now shown in template Score After cell. recap-skill-tests.sh 13/13."
memory_readiness_v8_1: "2026-05-29 — Redefined 🧠 MEMORY footer line from a v8.0 'wrote-to-Notion-this-turn' activity flag into a CLOSE-OUT READINESS gauge (🟢 synced·safe-to-close / 🟡 minor pending / 🔴 NOT synced). ⚪ removed. Computed each fire from 6 probed sub-conditions (a)–(f); unknown→🟡 never 🟢. New BLOCK 4 #6 writes ~/.openclaw/state/memory-readiness.json as single source; lite footer renders the glyph too. Council Permanent-Fix 4.4/5 (threshold 4.25). Purpose: 🟢 = no need to run closeout-skill or handoff-skill for memory."
slimmed_v8_0: "2026-05-29 — Runtime/changelog split (council 4.31/5, rec 1). Moved ~600 lines of per-version changelog + BLOCK 3 improvement registry + Version History to recap-skill-CHANGELOG.md (NOT loaded at runtime). ZERO executable gates removed — verified by recap-skill-tests.sh (8/8) + gate-preservation diff (HARD GATE 15, FD-0..5, FRC-1..7, Lite FORCE-FULL 5, vault, identity, recursion lock, three-metric engine all preserved). Token cost per response cut ~65%. Full history: recap-skill-CHANGELOG.md."
description: "Called at the END OF EVERY RESPONSE on Ivan CC + Mack, with a mandatory Codex/ChatGPT fallback when the Claude hook/tool is unavailable. Q&A roll-up header + locked footer + per-response memory/self-audit + end-of-thread 4-round council loop. Completion words (fixed/done/verified/saved/updated/patched/replaced/PASS) require a Claim Ledger + proof + final_response_marker_check. Trigger phrases: recap-skill, end of response, footer, session summary. Full version history in recap-skill-CHANGELOG.md."
---

# Recap Skill v8.9 (runtime). Version history → recap-skill-CHANGELOG.md

## ⛔ BLOCK 0 — MANDATORY EXECUTION CONTRACT

**Call `Skill("recap-skill")` at the END OF EVERY RESPONSE.** The Stop hook (`auto-closeout-gate.sh` v2.0 + `inject-recap-reminder.sh` v1.3) mechanically blocks a response that skips it; after 2 blocks → escape + log to `recap-enforcement.log` for Angie.

**Codex/ChatGPT fallback:** if this surface cannot call `Skill("recap-skill")` or use the Claude Stop hook, the agent must manually execute the recap contract before the final response. Required proof: load this canonical Drive `SKILL.md` and record `drive_file_id` + `version`; write a workspace recap receipt with task, artifacts, proof, AI open, human open, self-audit, and memory/Notion status; append `~/.openclaw/state/recap-fire-ledger.jsonl`; label any missing Drive/Notion side effect as `recap partial:<blocker>`; include a final `recap-skill:` closeout line naming the receipt path. A Codex response without that fallback receipt is incomplete.

**Codex measurement gate (HARD):** a one-line `recap-skill:` label is NOT enough. Before sending, Codex must compute and print: `draft_sha256`, `response_score`, `recap_fire_rate_last20`, `receipt_path`, and `self-audit` status. The final response must include the footer markers `PROJECT`, `MEMORY`, `AI OPEN`, `HUMAN OPEN`, `METRICS`, and `CONTEXT`. Count the current response as recap-fired only if the current receipt path is in `recap-fire-ledger.jsonl` and the final response visibly includes those measurement fields. Missing measurement = `recap partial:measurement_missing`, not pass.

**Codex render gate (HARD):** measurement fields are still NOT enough unless the response renders the locked recap footer shape. After the direct answer, the response must contain: `PROJECT`, `ORIGINAL`, `THREAD`, `MEMORY`, `AI OPEN`, `HUMAN OPEN`, exactly five numbered option lines (`1.` through `5.`) with exactly one `⭐`, `Reason:`, `self-audit:`, `response_score:`, `METRICS`, `recap-skill v`, `CONTEXT`, `receipt_path:`, `draft_sha256:`, and `recap_fire_rate_last20:`. If any marker is missing or the options are not exactly five, do not count recap as fired; write `recap partial:render_missing`.

Three jobs every non-lite response, in order, BEFORE the footer prints:

**① MEMORY + PROJECTS** — Notion Live Thread row created/updated; per-response memory scan + receipt (POST-LOOP 4.6); credential VALUES → Notion Vault (4.55); Drive skill canonical pushed if a skill was patched; Sprint Board updated on task-state change.
**② SELF-AUDIT + SELF-IMPROVING** — `self-audit-skill MICRO_RESPONSE_MODE` fires before the footer. Low defect = log; medium = fix this response; high/repeated/false-done = `council-skill` Permanent Fix Approval Mode. Footer MUST carry `self-audit: pass | corrected | escalated | partial:<blocker>`.
**③ AUTONOMY** — 4-round council loop at END-OF-THREAD ONLY (see firing rule). Each round regenerates fresh options; autopilot dispatches EXECUTE items; ≤4/round; 5-min cap/round.

---

## ⚡ Lite Mode Gate (evaluate FIRST)

**LITE = true** when ANY: prompt starts `/q `; OR ≤20 words AND a question; OR pure status-check, no execution requested.
**LITE = false** when: a file was written/edited; a skill was dispatched; a bash state-change ran; or the prompt is an action directive (build/fix/run/deploy/create/update/patch/go).

**FORCE-FULL OVERRIDE (HARD)** — never lite when prompt contains:
- **Correction markers:** wrong / no (standalone) / actually / didn't work / broke(n) / again / still / I told you / I asked / stop / you keep / every time.
- **Recap/proof markers (v5.3):** recap / footer / every response / handoff / closeout / Diamond / self-audit / audit your work / permanent / why aren't you / why didn't you / prove / proof.
- **Credential pattern (v4.7):** `pit-` · `sk-`/`sk_` · `Bearer ` · `api_key` · `token=`/`_TOKEN`/`_KEY` · `GHL_`/`META_`/`ANTHROPIC_`/`SLACK_`/`GITHUB_`/`NOTION_` · any 40+ char high-entropy string · "here's the token / new key / regenerated / rotated / PIT token". On a credential pattern, force full AND run Capture-to-Vault (4.55) even on a ≤20-word message. NEVER lite-skip a token.

**When LITE=true** skip Q&A header, council loop, Notion create/update, memory scan/receipt, terminal title, task ledger. Print only (the 🧠 glyph is a cheap one-line read of `~/.openclaw/state/memory-readiness.json` `.status` — NO recompute; if file absent or its `ts` >2h → print 🟡):
```
🧵 [project ≤20 chars]
🧠 [🟢/🟡/🔴]  (close-out readiness — read from memory-readiness.json)
🟢 📊 CONTEXT Xk → N%
```

---

## ⛔ PRE-SEND FALSE-DONE GATE (runs BEFORE any response text is composed)

Trigger: every non-lite response where a Bash/MCP/Write tool was called this turn. Damage from a false claim is done once Bennett reads it — so this fires PRE-SEND, scanning tool-call OUTPUTS, not the draft.

- **FD-0 Claim inventory** (10s wall-clock cap; on timeout log `FD-SCAN TIMEOUT` + proceed): after each tool call, scan output for completion signals (`replaced: true`, `msgId`, `HTTP 200`, Notion page ID, Write success+path, `verified: true`, gog `replaced:true`+size>0). Build `claims[]` with `session_id`.
  - **BENNETT-QUESTION GATE (H02):** if the draft contains a `?` to Bennett AND no council ran this turn → STOP, run council-skill; surface to Bennett only if council returns `BENNETT_REQUIRED`.
- **FD-1 Proof gate:** each claim needs its proof signal IN THE SAME TOOL OUTPUT (table: Drive push=`replaced:true`; file=Write success+path; email=msgId; HTTP=`200`; Notion=page ID; skill patch=gog `replaced:true`+gog-pull size>0; memory=receipt <60s). Exclusions (no proof needed): conversational "done with topic", "good to go" in planning, anything trailed by "pending/next step/will do", or a response that IS a correction. Skill-patch claim also triggers self-audit on the patch (<3.0 = unproven).
- **FD-2 Auto-correct before writing:** unproven claim → write 🟡 + `(proof pending: run <tool>)`, never ✅/💎.
- **FD-3 Log + fleet notify:** append `~/.openclaw/logs/false-done-corrections.jsonl` `{ts,session_id,claims_total,corrections,detail}`; if corrections>0 notify #leo-coaches.
- **FD-4 Pattern escalation** (cross-session only, ≥2 same `claim_type` in 7d via `~/.openclaw/state/fd-pattern-log.json` — create on first write if absent): write `feedback_fd_pattern_<ctype>_<date>.md` to memory + notify #leo-coaches (`C0AQ4KB1SA0`) + set `PERMANENT_FIX_APPROVAL_MODE=true` (council before any Drive patch). `proof_failure` escalates at first occurrence (no 7d grace). Taxonomy: proof_failure/score_anomaly/missed_skill/false_done/handoff_gap/tool_failure/gate_misclassification.
- **FD-5 Self-verify:** never write "0 corrections" without reading the log tail and confirming no entry <60s. "0 corrections" is itself a claim requiring proof.

Hard rules: never run FD in POST-LOOP; never skip on "I'm confident"; never ✅ without same-turn proof; never ask Bennett a `?` without council first; never claim 0 corrections without file read; never mark skill_patched proven without gog-pull size check.

---

## FINAL RESPONSE COMPLIANCE GATE (runs after FD, before final text)

- **FRC-1 Drive loader proof:** for each named skill — Drive fullText search by name, filter by frontmatter `name`, newest modifiedTime = canonical; record `skill_name, drive_file_id, version, modifiedTime`. A mere mention ≠ proof.
- **FRC-2 Required-step ledger:** before `ran/executed/completed/verified/Diamond`, extract mandatory steps from the canonical SKILL.md, mark each executed/blocked/skipped-by-rule/N-A with proof. Any unproven mandatory step → only `loaded`/`reviewed`/`partially applied` allowed.
- **FRC-2.5 Named-skill orchestration ledger:** when Bennett names multiple skills, table: Order · Skill · Canonical proof · Required-step source · Executed proof · Blocker/skips · Allowed claim. Preserve his order; CEO email proof = Gmail msgId/draftId; handoff proof = Drive/Notion id or receipt path.
- **FRC-3 Recap partial labels:** if a recap side effect can't complete, label it (`recap partial: Notion unavailable`, etc.) — never hide a skipped side effect.
- **FRC-4 State ownership:** project state lands in Notion/Drive before "closed"; local/`~/.openclaw`/`/tmp` are mirrors → if Notion/Drive down, write local receipt + `reconciliation open`.
- **FRC-5 Diamond handoff:** any persistent write/skill patch/Drive replace/cron change → diamond-skill T7 persisted-write + skill-execution proof.
- **FRC-6 Existing-skill fix rule:** enforce via recap → diamond → council → closeout → gatekeeper before proposing any new skill.
- **FRC-7 Final-answer hard stop (v5.3+v5.8):** before sending non-lite, the exact draft must contain footer markers PROJECT · ORIGINAL/THREAD · MEMORY · AI OPEN · HUMAN OPEN · REVENUE_DECLARATION · AUTOMATION_DECLARATION (deliverable responses only) · five numbered options (one starred `N. ⭐`) · CONTEXT. If completion wording present, also require a `Claim Ledger`, `final_response_marker_check: PASS`, `draft_sha256`, and ≥1 concrete proof per claim (Drive id/hash, Notion url/id, receipt path, checker output, msgId, deploy url, API id, or explicit `partial:<blocker>`). Missing marker → add it or label `recap partial: <blocker>`, re-check after edits. A checker PASS proves only what it inspected.

---

## Q&A Roll-Up Header (every non-lite response, TOP)
```
# Questions and Answers — simplified
1. **[≤10-word condense of ask]**
   [≤25-word caveman answer, result first, bold 1-3 terms]
… up to 8; if more, last 6 + "…+N earlier"
```
Required every non-lite response; caveman-skill governs voice; ≤25 lines; no Q:/A: prefixes.

---

## The Footer — LOCKED LAYOUT (every response)

**THE TWO MONITOR TABLES (v8.2) render ABOVE the 🧵 PROJECT line so Bennett sees self-learning + autonomous work FIRST.** Both are `[OPTIONAL]` — they print only when the end-of-thread council-execute loop fired this response (keeps every-response footer lean per SKILL-SLIM). When the loop did NOT fire, skip straight to 🧵 PROJECT.

```
[OPTIONAL — only if the end-of-thread council-execute loop fired this response]
═════════════════════════════════════════════
🔁 AUTONOMOUS LOOPS — what ran itself this thread (up to 4 rounds; render only the rounds that ran)
| # | ✅ Council Approved | 🔧 Permanent Change | 👀 You'll Notice |
|---|---|---|---|
| 1 | [≤6-word what council OK'd] | [≤6-word rule/file changed] | [≤8-word day-to-day diff] |
| 2 | … | … | … |
   (0-EXECUTE round → one row "No-op · nothing changed · —"; every cell filled, never blank)
   ➡️ TOTAL: <K> permanent changes shipped this thread   (K = rows whose 🔧 cell ≠ — / No-op; must reconcile with overdrive-last-cycle.json shipped_verified[])
═════════════════════════════════════════════
🪞 SELF-AUDIT — defects I caught + permanently fixed on my OWN work
| 📉 Score Before | ⚠️ Issues Found | 🔧 What I Fixed (rule changed) | 📈 Score After |
|---|---|---|---|
| X/10 | [≤8-word defect] | [≤8-word permanent fix + which rule/skill] | Y/10 ↑ |
   (no defect this thread → single row: "10/10 · none · clean pass · 10/10 →"; arrow ↑/↓/→ vs prior thread's score)
═════════════════════════════════════════════
[OPTIONAL — only if a Bennett-ask exists this response]
🟣 BENNETT ASK [full question/blocker ≤18 words]
═════════════════════════════════════════════
🧵 PROJECT [Notion Live Thread row name] [emoji]
═════════════════════════════════════════════
   💬 ORIGINAL [first prompt ≤14 words] [emoji]
   🧵 THREAD #N [follow-up ≤12 words] [emoji]
─────────────────────────────────────────────
   🧠 MEMORY [🟢 synced · safe to close out / 🟡 minor pending / 🔴 NOT synced — don't close] (reason; +🔑 Vault if credential captured)
   🤖 AI OPEN [count · what's running, or "none"]
   🟣 HUMAN OPEN [count · what waits on Bennett, or "none"]
═════════════════════════════════════════════

1. ⭐ [highest Advaita Vision baseline gap] (domain +X%)
2. [AI-executable next action]
3. [AI-executable next action — highest Advaita impact, tag (domain +X%)]
4. [maintenance / observability]
5. [zoom-out AI action] OR 🟣 See above ↑ (if BENNETT ASK present)
Reason: [one sentence — why the starred option is best]

   🪞 self-audit: pass | corrected | escalated | partial:<blocker>   (machine-readable status — the human 🪞 SELF-AUDIT table above is its full render when the loop fired)
   response_score: X/10  [memory+2 · self-audit+2 · baseline-options+2 · no-FD-corrections+2 · Notion-row+2]
   📈 METRICS  Memory <M>%  ·  Recap-fire <R>%  ·  Self-improve <S>%
   recap-skill v8.9
   🟢 📊 CONTEXT Xk → N%   [🟡 ≥80k slot1=handoff prep · 🔴 ≥160k slot1=run closeout NOW]
```

**Two monitor-table fill rules (v8.2, HARD — anti-vibes, every cell computed not asserted):**
- **🔁 AUTONOMOUS LOOPS table** — one row per council round actually run this thread (read `recap-loop.jsonl` tail for THIS session_id; 4 rows max). `✅ Council Approved` = the EXECUTE verdict text from that round's council JSON. `🔧 Permanent Change` = the canonical artifact that changed (Drive fileId/skill name/rule line) with a real receipt — if none changed, write the literal `—`. `👀 You'll Notice` = the day-to-day behavior diff in plain words. A round with 0 EXECUTE → the row reads `No-op · nothing changed · —`. NEVER fabricate a row for a round that did not run; render fewer rows instead.
- **🪞 SELF-AUDIT table** — `📉 Score Before` + `📈 Score After` come from `self-audit-skill MICRO_RESPONSE_MODE` (the same run that sets the `🪞 self-audit:` status line). `⚠️ Issues Found` = the defect(s) it flagged this thread (read `false-done-corrections.jsonl` tail for this session_id; 0 corrections → `none`). `🔧 What I Fixed` = the permanent fix + which rule/skill/file changed, with proof — NOT "will fix". If `📈 Score After` ≤ `📉 Score Before`, the fix is unproven → label it `partial:<blocker>`, never claim improvement without a re-score receipt.
- Both tables inherit the PRE-SEND FALSE-DONE GATE: any cell asserting a completion (`fixed`, `replaced`, `approved`) needs its proof signal in a tool output THIS thread, else the cell carries `(proof pending)`.

**v8.3 hardening (council 4.2/5 — 20 improvements, runtime-relevant subset; full list in CHANGELOG):**
- **TOTAL line** under the 🔁 table: `   ➡️ TOTAL: <K> permanent changes shipped this thread` — Bennett's one-number takeaway. `<K>` = count of rows whose 🔧 cell is not `—`/`No-op`. Must reconcile with `overdrive-last-cycle.json shipped_verified[]` length (anti-drift, handoff Step 1.5 rule); mismatch → append `(⚠️ reconcile: state=N)`.
- **Defer-only round** (council DEFERRED to a Bennett gate, 0 EXECUTE) → that row's 🔧 cell = `🟣 Bennett gate` not a fake change; 👀 cell names the blocker.
- **Trend arrow** on the 🪞 table 📈 cell: `Y/10 ↑` / `↓` / `→` vs the prior thread's score read from `~/.openclaw/state/recap-selfaudit-prior.json` (write this thread's after-score there at close). At-a-glance learning direction.
- **False-done cross-check (HARD):** if `false-done-corrections.jsonl` has ≥1 entry for this session_id, 📈 Score After CANNOT be 10/10 and ⚠️ Issues Found CANNOT be `none` — they must name the correction. A clean 10/10 with corrections on file = a false self-audit (self-audit defect, logs to itself).
- **Fewer than 4 loop rows** is normal (cap hit / all-defer) — never pad to 4. If a cap terminated the loop, the last row's 👀 cell ends `· (cap hit, carried fwd)` so Bennett knows it stopped deliberately, not broke.
- **Lite mode never renders these tables** (already `[OPTIONAL]` end-of-thread-gated; restated so lite stays one-glyph cheap).

**5-option rules (render-safe, HARD):** exactly five consecutive lines each flush-left `N. `; the recommended slot is `N. ⭐ …` (star AFTER the number — `⭐ N.` breaks the markdown list and renumbers). Never print both `N.` and `N. ⭐` for one number; never repeat the starred text elsewhere; `Reason:` only after option 5; no A/B/C, no bullets, no 6th line. Slots 1–4 = actions Mack/Ivan executes itself (forbidden: "open/review/click/approve/read"). Slot 5 = Bennett-unblock or zoom-out.

**Option sources (anti-vibes):** A = Advaita baseline gap (`~/.openclaw/state/advaita-autonomy-baseline.json`, 105-pt rubric) — slots 1 & 3 MUST tag `(domain +X%)`; B = self-audit output; C = POST-LOOP cleanup; D = Bennett-explicit. Baseline stale >24h → run auto-sprint-creator-skill first.

**🧠 MEMORY = CLOSE-OUT READINESS GAUGE (v8.1).** It answers exactly ONE question and nothing else: *"Is all memory synced — am I safe to close out WITHOUT running closeout-skill or handoff-skill?"* It is NOT an "I wrote to Notion this turn" activity flag (that was the v8.0 meaning — now retired). Three states only — ⚪/"nothing-needed" is REMOVED. Every state is **computed from concrete probes each fire, never asserted.** Unknown / unprobed condition → 🟡, NEVER 🟢.

- **🟢 GREEN — synced · safe to close out.** Closing out now (or running handoff/closeout) would save **nothing additional**. Requires ALL true, each with proof this turn:
  (a) `memory-skill-receipts.jsonl` tail `ts` <120s AND its `under_cap:true` (per-response write 4.6 ran);
  (b) byte-guard pass: `wc -c < ~/.claude/projects/-Users-$(whoami)/memory/MEMORY.md` <24000;
  (c) Notion Live Thread row write returned HTTP 200 this turn **OR** this was a pure status-check that touched no syncable state AND no prior-turn unsynced state is outstanding;
  (d) stale-memory reconciliation (4.5) contradictions = 0;
  (e) every credential value seen this thread has a confirmed Vault write (`vault_write` receipt + token-probe 200);
  (f) every skill patched this thread shows gog `replaced:true`+size>0 (Drive canonical synced).
- **🟡 YELLOW — minor pending; closing loses a little / a sync is staged but unconfirmed.** ANY: a memory write is queued or `proof pending`; reconciliation open but a LOCAL receipt was written (FRC-4 mirror, Notion/Drive temporarily down); baseline >24h stale; Notion row updated but a non-blocking side effect deferred (Sprint Board / Task Ledger); a memory side effect carries a `partial:` label; readiness probe could not confirm one GREEN sub-condition.
- **🔴 RED — NOT synced; do NOT close out.** ANY: no fresh receipt (>120s, or 4.6 did not run); MEMORY.md `OVER_CAP`; Notion write errored (`NOTION_UPDATE_FAIL`); an uncaptured credential value; reconciliation contradictions >0 with NO local receipt; a skill was patched but the Drive push failed.

Append `(reason)` after the glyph; `+🔑 Vault` if a credential was captured. HARD: never 🟢 without a fresh `memory-skill-receipts.jsonl` entry (≤120s) AND under-cap. GREEN is the green light to close — if you cannot prove all six (a)–(f), it is not GREEN.

**GATE-VERIFY before any HUMAN OPEN / BENNETT ASK (v5.6):** credential gate → `token-probe.sh <service>` (200=not a gate, execute; 401=human gate; 403=fix-call; 429=wait); Vault check `notion-fetch 341cf5514fd381fe993de8add7eb265e`; never trust a prior-session "401"; true human gates only = biometric/legal/>$1K/identity/external-contract. No live receipt = SUSPECTED, stays AI OPEN.

**GATEKEEPER-SKILL GATE (v6.1 — Bennett directive 2026-06-01):** Before any non-lite response that dispatched ≥2 skills OR produced a multi-step deliverable (email/blueprint/report/HTML/automation) → gatekeeper-skill MUST have run this response. If it did not, label the response `gatekeeper_partial: not run` and add slot 1 action: "Run gatekeeper-skill on this deliverable." This prevents shipping incomplete work. Deliverable types: any response where Bennett asked to "build", "create", "deploy", "send", or "run [skill chain]". No exceptions — gatekeeper is NOT optional for deliverables.

**APPROVAL-SKILL AUTO-INVOKE (v6.0 — Bennett directive 2026-06-01):** When HUMAN OPEN > 0, BEFORE composing the Q&A header, invoke `approval-skill` v2.0 (Drive `1qWwyNolv8mvnZ5FmSZDj3luvKnbc87Um`, local `/Users/temp/.claude/skills/approval-skill-SKILL.md`) for EACH open gate. Render the complete `[FOR APPROVAL]` decision package — context (what/why/live-numbers/trade-offs/reversibility/cost-of-inaction) + council ranked rec (🥇/🥈/🥉) + ≥5 numbered options — at the VERY TOP of the response, before the Q&A header and before any other content. Format: `## 🟣 FOR APPROVAL — [Gate Title]` block per gate. Never list a gate as `HUMAN OPEN: N` without rendering its full decision package above. ALSO: when `~/.openclaw/state/pending-approvals.jsonl` shows `council_pick` exists AND action is reversible AND NOT classified as spend >$1K or biometric/legal/identity/external-contract → execute the council pick DIRECTLY without re-presenting as a new approval request. Mark ledger `approved_council_auto`.

**Status emoji:** 💎 Diamond · 🟢 done-not-Diamond · 🟡 in-progress · 🔴 blocked · 🟣 waiting-on-Bennett.

---

## ⚡ BLOCK 4 — THREE-METRIC ENGINE (the 3 things Bennett measures; all 5 run before the footer)

1. **Memory perfect** · 2. **Recap fires every message (measured)** · 3. **Permanent self-improvement.**

- **#1 Hard memory byte-guard:** never hand-edit MEMORY.md; run `python3 ~/.openclaw/bin/memory-hygiene.py --apply` (runs on both Mack and Ivan — not Mack-only). Probe before 🧠🟢: `B=$(wc -c < ~/.claude/projects/-Users-$(whoami)/memory/MEMORY.md); [ "$B" -lt 24000 ] && echo YES || echo OVER_CAP`. OVER_CAP → rebuild, re-probe. Never 🧠🟢 over cap.
- **#2 Memory-delta receipt every fire:** append one line to `memory-skill-receipts.jsonl` even when nothing written (`{ts,agent,scanned,written[],skipped[{item,reason}],memory_bytes,under_cap}`). 🧠🟢 only if tail ts <120s.
- **#3 Stale-memory reconciliation:** if this response touched a system a memory note describes, re-verify the note vs live state and correct contradictions THIS turn; log as `reason:"stale-reconciled:<slug>"`.
- **#4 Recap-fire ledger + miss-detector:** every fire appends `recap-fire-ledger.jsonl` `{ts,session_id,agent,draft_sha256,fired:true,lite}`. Next turn: if prior `turn-start-<sid>` has no newer ledger line → log `RECAP_MISSED` + footer slot 1. (The ledger is recap's OWN fire-rate proof — query fired÷total.)
- **#5 Three-metric strip + rollup:** footer prints `📈 METRICS Memory M% · Recap-fire R% · Self-improve S%` (Memory%=100 if under_cap+fresh receipt+0 pending reconciles, else −34 each; Recap-fire%=fired÷total over last 20 ledger lines; Self-improve%=BLOCK 1 Cat3). Then write `echo '{...}' > ~/.openclaw/state/advaita-three-metrics.json` — the ONE source pulse+angie+Bennett read. **NEVER seed this file with assumed numbers; it is computed from the logs each fire.** Absent on a non-lite response = self-audit defect.
- **#6 Close-out readiness compute + write (drives the 🧠 MEMORY glyph):** after #1–#5, evaluate the GREEN sub-conditions (a)–(f) from the "🧠 MEMORY = CLOSE-OUT READINESS GAUGE" rubric using THIS turn's probes (receipt tail ts + `under_cap`, MEMORY.md byte-guard, Notion row HTTP code, reconciliation count, Vault receipt, gog `replaced` on any skill patch). Map: all six provable → `green`; any RED trigger → `red`; otherwise → `yellow` (default-to-degraded — an unprovable sub-condition is yellow, never green). Then write the ONE source the footer + lite mode + pulse + Angie all read: `echo '{"ts":"<iso>","status":"green|yellow|red","reasons":[...],"pending":[...],"agent":"<mack|ivan>"}' > ~/.openclaw/state/memory-readiness.json`. The non-lite footer 🧠 line and the lite 🧠 glyph BOTH render from this file's `.status` — they must never disagree. **NEVER seed with an assumed status; it is computed from the same receipts every fire.** GREEN here is a promise: closeout-skill / handoff-skill would persist nothing this turn did not.

---

## ⚡ BLOCK 1 — RECAP SELF-AUDIT MODE (trigger: "audit recap-skill" / "recap score" / "recap health check")
Run live bash probes, output 3 category scores 0–100 + overall + top fix, log to `response-scores.jsonl`.
- **Cat 1 Autonomy:** loop fired <24h · last loop ≥1 EXECUTE/round · 4 rounds no CAP_HIT · option_hashes unique. (tails of `recap-loop.jsonl`)
- **Cat 2 Memory:** receipt <2h · MEMORY.md <190 lines · active Notion row · 0 stale files >30d.
- **Cat 3 Self-learning:** response-scores ≥3 entries · trend up · self-audit invoked this session (`ls ~/.claude/.session-state/skill-ran-self-audit-skill-*`) · pattern-escalation log active.
Output the boxed REPORT + append `{ts,cat1,cat2,cat3,score,top_fix}` to `response-scores.jsonl`.

## ⚡ BLOCK 2 — FAILURE-MODE PROBES (each probeable <5s; full root-cause notes in CHANGELOG.md)
- **F1-1** stale `recap-cycle.lock` >300s → post #leo-coaches before removing. **F1-2** round-1 0-EXECUTE → warn #leo-coaches (rounds 2-4 may legitimately be 0). **F1-3** recycled options (dup `option_hashes`) → force regenerate. **F1-4** any `CAP_HIT` → #leo-coaches with round + what was cut. **F1-5** identity gate: `whoami` PRIMARY, hostname fallback.
- **F2-1** MEMORY.md ≥190 lines → archive oldest 20 before write (HARD). **F2-2** no receipt <7200s → 🔴 not 🟢 (HARD). **F2-3** notion-search before notion-create; match → update only. **F2-4** Sprint Board = real `notion-update-page` call. **F2-5** Read-before-Write; append, never overwrite (+ `.bak`).
- **F3-1** `self-audit: pass` forbidden without a `skill-ran-self-audit-skill-*` marker this session → else `partial:not-invoked` (HARD). **F3-2** Permanent Fix Approval Mode = council v28 (threshold ≥4.0). **F3-3** never "permanent" without gog `replaced:true`+size>0 (HARD). **F3-4** Angie daily 3-category probe. **F3-5** FD-4 escalation writes a real feedback .md (no `pass` no-op).

---

## End-of-Thread Council Loop (Mack + Ivan ONLY — never Leo, never intermediate responses)

**Identity gate (HARD):** `whoami` primary — `temp`→mack, `openclaw`→ivan, else hostname fallback (`macbook`→mack, `imac`→ivan), else leo → `exit 0` (loop never fires on Leo).

**FIRING RULE:** Footer 5 options print on EVERY Mack/Ivan response (cheap). The expensive 4-round council-execute loop fires at **END-OF-THREAD ONLY** = ANY of: (1) closeout/handoff ran this turn (they write `recap-cycle-trigger.txt`); (2) context ≥120k; (3) Bennett end-of-thread signal (close / close out / wrap up / end of thread / handoff / done for now). None true → write footer, SKIP loop, log `{event:"loop_skipped",reason}`.

**Recursion guard (Python lock, 600s TTL):** `~/.openclaw/state/recap-cycle.lock` — exists & <600s → skip; stale → remove + proceed; always release in `finally`.

**Loop body — exactly 4 rounds, hard-stop after 4.** Each round regenerates fresh 5 options from post-prior-round state (never recycle — dedup via session `option_hash_registry`, real MD5 of sorted option text[:30]). Per round: read options → dispatch council-skill ("score each EXECUTE/SKIP/DEFER; EXECUTE only if reversible, Mack/Ivan-capable, <5min; DEFER if Bennett gate; SKIP if irrelevant"; JSON output) → autopilot each EXECUTE one-at-a-time, log `tool_call_id` → print `ROUND N: x EXECUTE · y SKIP · z DEFER · r receipts`. Round 1 0-EXECUTE → #leo-coaches DEFER-ALL warning. Rounds 2-4 prepend prior round's deferred items (carry-forward, min 2 EXECUTE/round gate). Round 4 writes unresolved defers to `active-thread.json.last_session_deferred_items`. Per-round caps: 5 min · 50k in+out tokens · ≤4 EXECUTE → cap hit = terminate gracefully + log `CAP_HIT`.

**POST-LOOP (every non-lite response, not just when loop fired):**
- **4.5** memory-sync-skill `--mode=L7` (<30s); contradictions → HUMAN OPEN, >3 → BENNETT ASK.
- **4.55 Credential→Vault (HARD if a credential pattern seen):** detect value → `notion-update-page` Vault `341cf5514fd381fe993de8add7eb265e` (value+last_verified, canonical var names) → `token-probe.sh` confirm 200 → mirror gateway.env/secrets/1Password → receipt `vault_write` → footer `+🔑 Vault`. Raw values go to the Vault row ONLY, never a .md or page body.
- **4.6 Per-response memory write (HARD GATE):** scan 4 categories (FEEDBACK/PROJECT/REFERENCE/USER) + 5th=CREDENTIAL via 4.55. Read-before-Write (`.bak` first, append never overwrite, conflict-merge across agent prefixes). Write `{type}_{slug}.md` to `~/.claude/projects/-Users-$(whoami)/memory/` (portable — resolves to -Users-openclaw on Ivan, -Users-temp on Mack) + add MEMORY.md index line. Log receipt. **Step E response-score (MANDATORY):** schema-validate (response_score float 0-10, self_audit_score int 0-100 or null), idempotency key MD5(session_id+score), append `response-scores.jsonl`; done-claim hard gate (no score → no receipt); 7-session trend alert if current < avg−0.5; `session_health_score = memory*.33+self_learn*.33+autonomy*.34`. Never 🧠🟢 without receipt.
- **4.62 Fix-ledger (HARD if a Drive skill/tool was patched this response):** after a confirmed `gog --replace` (`replaced:true` + gog-pull size>0), call `fix-ledger.sh --fix <what> --session <id> --file-id <driveId> --marker <ascii-regex> --domain <d>` — logs the fix and canonical-readback-verifies it (`verified:true` only on PASS). This is the MAKE-TIME half of keep-fixed; closeout-skill Step 11 re-proves all ledger entries at close (the KEEP-FIXED half). Use ASCII-only markers (no em-dash) so the audit round-trips cleanly. Auto-bootstraps from Drive `1fke8EYFQg2-5hHPVal8ZeKgak_LrPd8h` if absent.
- **4.65 Rotate/regenerate auto-close:** before creating any "rotate/regenerate/expired token" task → Vault + `token-probe.sh`; 200 = auto-close (don't ask Bennett); 401 = keep+route to owner; 403 = fix-call note.
- **4.7** auto-populate project Task Ledger (dedupe ≥90%; non-blocking).
- **5** compute LOOP RESULTS + autonomy_score = `(rounds≥2exec/total)*40 + (carried_closed/carried)*30 + (unique_hashes/options)*30`; write `last-loop-results.json`.
- **6 / 6.5** append `recap-loop.jsonl` (`option_hashes, rounds_completed, cap_hit, deferred_to_next_session, tool_call_ids, autonomy_score`); receipt-completeness check (10 required fields) → else `RECEIPT_INCOMPLETE`.
- **7 / 7.5** update Notion Live Thread row (verify HTTP 200, retry once, else `NOTION_UPDATE_FAIL`); Drive-fail fallback → Notion All-Tasks page + #leo-coaches (`C0AQ4KB1SA0`). (#leo-auto C0AKXT2S1T2 is broken — never use it; canonical fallback is #leo-coaches.)
- **9.5** write `recap-audit-snapshot.json` for Angie daily. **10** release lock.

---

## Notion Auto-Create (every response)
Read `active-thread.json`. NEW THREAD if: absent OR `started_at` >24h OR `closed_at` present. Write `closed_at` at stop hook FIRST on close. NEW → create row in Live Thread Projects DB (`3e11936b-ac59-4104-a842-144c94754698`), prepend prior `last_session_deferred_items`, write `session_delta.json` + #leo-coaches (`C0AQ4KB1SA0`) delta line. (#leo-auto is broken — do not use.) CONTINUING → increment prompt_count, append inquiry, update status. Notion failures log to `notion-thread-errors.jsonl`, never block. Live tab title → `$PWD/.terminal_title`.

## Canonical IDs
- Live Thread Projects DB: `573123c63332433d89aebefbfeb05e5e` · data source `3e11936b-ac59-4104-a842-144c94754698`
- Credential Vault page: `341cf5514fd381fe993de8add7eb265e`
- Drive skills folder: `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY` · recap drive_file_id `1e9nw03yKQ9tjD4k3zEBAhQsEnH0qZWe6`
- #leo-coaches `C0AQ4KB1SA0`

---

## Anti-Patterns (condensed; full list in CHANGELOG.md)
❌ Skip the footer · combine ORIGINAL+follow-ups on one line · 🧠🟢 without a fresh receipt · skip Notion row · skip `.terminal_title` · <5 options or slot 3 without `(domain +X%)` · duplicate/out-of-order option numbers · `⭐ N.` before the number · `Reason:` before option 5 · fire loop on Leo / on intermediate response / NOT at end-of-thread · >4 rounds · skip recursion lock · recycle options across rounds · lite-skip a credential pattern · save a credential as a "location" note instead of Vault value · write a raw credential into a .md or page body · compose before FD-0 completes · ask Bennett a `?` without council first · claim "0 corrections" without file read · mark skill_patched proven without gog-pull size>0 · say fixed/done/verified/saved/updated/patched/replaced/PASS without Claim Ledger + final_response_marker_check + draft_sha256 · seed `advaita-three-metrics.json` with assumed numbers · use the retired v8.0 "🧠🟢 = wrote to Notion this turn" meaning (🧠 is now a close-out READINESS gauge) · print 🧠🟢 when any GREEN sub-condition (a)–(f) is unproven (unknown → 🟡, never 🟢) · use ⚪/"nothing-needed" for 🧠 (removed in v8.1) · let the lite 🧠 glyph and the non-lite 🧠 line disagree (both read `memory-readiness.json` `.status`) · seed `memory-readiness.json` with an assumed status.

## Self-Audit Checklist (angie-weekly-audit-skill SOP rubric)
1. Invoked in last 30d. 2. Frontmatter valid (name, version=8.9, drive_file_id) — <8.4 = force-pull. 3. Footer on every sampled response. 4. No 🧠🟢 without receipt. 4b. 🧠 line = close-out readiness (3 states, no ⚪); footer `.status` matches `memory-readiness.json` and was computed not assumed; no 🧠🟢 with any unproven (a)–(f) sub-condition. 5. Credential FORCE-FULL fired on every credential-bearing message. 6. Every credential value in last 7d has a Vault write. 7. No raw credential in .md/page body. 8. Rotate tasks all have a probe receipt; valid ones auto-closed. 9. Loop never fired on Leo. 10. FD gate fired on every non-lite tool-using response. 11. No Bennett-directed `?` sent without council same turn. 12-20 (skill-loader proof, required-step ledgers, partial labels, diamond handoff, orchestration ledger, permanent-fix table, CEO/handoff IDs). 21. FRC-7 markers present before send. 25. MICRO_RESPONSE_MODE ran or labeled partial. 28. recap-loop.jsonl has option_hashes. 29. MEMORY.md <190 lines. 30. FD-4 writes real feedback .md at ≥2 same claim_type in 7d (proof_failure = first occurrence); feedback .md must be a real file write, not a pass no-op. 31. response_score on every non-lite footer.
32. MEMORY: memory-readiness.json written and <2h old; memory-skill-receipts.jsonl tail ts <120s; MEMORY.md <190 lines (wc -c <24000); no stale memory files >30d; per-response memory write (4.6) fired or labeled partial.
33. AUTONOMY: end-of-thread council loop fired ≥1 EXECUTE/round (check recap-loop.jsonl, last 7 sessions); option_hashes unique (no recycled across rounds); autonomy_score computed and written to last-loop-results.json; FRC-7 five-option render present; Bennett questions blocked by council gate (no bare ? without council).
34. SELF-LEARNING: self-audit MICRO_RESPONSE_MODE ran or labeled partial (F3-1 hard gate); response_score trend up over last 7 sessions (response-scores.jsonl); FD-4 pattern escalation fired at least once in last 30d (false-done-corrections.jsonl); false-done correction rate trending down session over session; BLOCK 3 improvement registry has ≥1 entry from last 30d.
35. skill_identity revenue + automation declarations:
    ```yaml
    skill_identity:
      revenue_declaration:
        expected_revenue_impact_usd: 30000
        measurement_window_days: 30
        measurement_method: "False-done prevention × avg cost per error × response count. Every prevented false-done claim protects revenue at-risk from a broken system. Permanent self-improvement compounds each session."
        ground_truth_artifact: "false-done-corrections.jsonl correction count (trending down = revenue protected); response-scores.jsonl trend (up = compound improvement)"
      automation_declaration:
        is_self_running: true
        trigger_mechanism: "stop_hook"
        trigger_ref: "auto-closeout-gate.sh v2.0 + inject-recap-reminder.sh v1.3 — fires on EVERY Claude Code response; mechanically blocks skip after 2 misses"
        trigger_verified_at: "2026-06-01 (v8.9 render gate verified, 13/13 recap-skill-tests.sh PASS)"
        human_touches_per_week: 0
        failure_alert_destination: "#leo-coaches C0AQ4KB1SA0 (recap-enforcement.log → Angie)"
    ```

## Governance
Canonical = Drive folder `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY` / recap-skill/SKILL.md. Edit on Drive canonical only. Run `bash ~/.openclaw/scripts/recap-skill-tests.sh` (must pass) before any Drive upload. Full per-version changelog + BLOCK 3 improvement registry + Version History → **recap-skill-CHANGELOG.md** (same folder; not loaded at runtime).

## Bennett Memory Status Color Rule — added 2026-06-02

In every Bennett-facing recap, the MEMORY section must distinguish shared/fleet memory from project-state saves:

- `🧠 MEMORY: 🟢 Green` means shared/fleet memory was actually saved, with a proof artifact such as a memory note path, memory tool receipt, or explicit closeout memory proof.
- `🧠 MEMORY: 🟡 Yellow` means Notion, Drive, Gmail, or local receipts may have been updated, but shared/fleet memory itself was not saved yet.
- Never imply memory is complete merely because Notion or Drive were updated. Use: `Project state saved; shared memory not saved yet.`
- This status tells Bennett whether the thread can be closed or whether closeout/memory skill still needs to run.

