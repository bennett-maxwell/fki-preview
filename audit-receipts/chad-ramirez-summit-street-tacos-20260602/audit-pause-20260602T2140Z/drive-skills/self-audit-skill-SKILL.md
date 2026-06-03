---
name: self-audit-skill
description: >
  Cycle-scope work audit (v1.5). Grades a single autonomy-cycle deliverable (ship-it / overdrive / autopilot / batch-overdrive output) against the original spec + Bennett's universal completion gates (revenue + automation + consolidation), identifies gaps, runs a REAL council pass + autopilot pass to fix them, and outputs a before/after delta. Distinct from business-audit-skill (company-scope, 36 dimensions) and diamond-skill (pass/fail).
  Trigger phrases: "self-audit", "audit this work", "audit this cycle", "grade my work", "self-audit-skill", "audit the cycle that just ran".
type: meta-audit
applies-to: any-cycle-deliverable
drive_folder_id: 1ZBvY1JaG9u-PhZhzRDhlQO1koPVRY33l
drive_file_id: 1xCx0k6lj1y1_ni77ff0j8rrYAw2r8BMM
skills_root_mirror_id: 1xCx0k6lj1y1_ni77ff0j8rrYAw2r8BMM
version: 2.7
last_updated: 2026-06-01  # v2.7: TO-100 TARGET CONTRACT in Step 5.5 — aim 5.0/100% per dimension, council reframed to smallest-1-2-changes-per-sub-5.0-dim path-to-100, non-gameable HELD % re-measurement, aspirational (plateau/round-cap terminator, never fabricate a 5.0)
council_verified: 3.67
patched_v2_7: "2026-06-01 TO-100 TARGET CONTRACT (Bennett directive — 'every self-audit asks council how to reach 100%, makes 1-2 small fixes, re-tests, reports how many held'). Council 3.67/3.5 PASS (3 advisors, unanimous keep-council-separate per Loop-Engine Map). Step 5.5 retargets the inner loop from PASS (delta>=0.5) to aim-5.0/100%: council question reframed to 'smallest 1-2 changes per sub-5.0 dimension to reach 5.0'; adds HELD % (non-gameable: target dim held + no other dim regressed + aggregate didn't fall, recomputed from real counts not asserted); 100% is ASPIRATIONAL with plateau guard (delta<0.3 x2 OR held<50%) + round-cap — fabricating a 5.0 is a hard fail. Council amendment incorporated: kept council SEPARATE (not baked in), did NOT add a second per-round grader."
council_verified_prior: 4.46
patched_v2_4: "2026-05-27 Behavior-Delta Gate — self-audit must change the current response, not only patch documentation. Correction prompts require a root-cause answer, explicit prior failure, current behavior delta, same-defect scan, and a final-draft self-audit proof block. If the same defect remains visible, the audit status is partial and the response must be revised before sending."
patched_v2_5: "2026-05-27 Correction Final Verifier Gate — self-audit/correction finals must pass `tools/fki_correction_final_verify.py <draft> --json` before completion wording. The gate bundles recap proof, behavior-delta proof, claim ledger, and 20 failure-mode breakpoints."
patched_v2_6: "2026-05-30 5-fix audit patch — (1) SynthFlow row in Advaita checklist updated to GHL SMS+email (SynthFlow DROPPED 2026-05-30). (2) #leo-auto dispatch in Advaita standalone step 6 corrected to #leo-coaches fallback (C0AQ4KB1SA0). (3) fki_correction_final_verify.py path clarified to absolute path ~/.openclaw/bin/ with fallback skip-and-log if missing. (4) Self-Audit Checklist item 4 path corrected from ~/.openclaw/logs/ to ~/.openclaw/state/self-audit-history.jsonl. (5) v2.6 error-ledger every-cycle check wired into Step 0 as Step 0.5 with explicit error-ledger.py invocation."
patched_v2_3: "2026-05-27 Micro Response False-Done Claim Proof — restores MICRO_RESPONSE_MODE and adds 10 claim-proof checks for exact final drafts. Fixed/done/verified/saved/updated/patched/replaced/PASS claims require a proof ledger, final_response_marker_check PASS, draft_sha256, and fetchback/readback when the claim involves a skill patch."
patched_v2_2: "2026-05-27 Blueprint live-funnel proof gates — adds mandatory public browser proof, deployed HTML readback, same-contact CRM proof, repeat-submit duplicate proof, booking/appointment attach proof, identity edge-case checks, protected side-effect ledger, and final ask-to-proof map before any live revenue/Diamond claim."
patched_v2_0: "2026-05-27 W22e overdrive — 4 permanent changes: (1) REVENUE_DECLARATION HARD GATE: missing block auto-scores Revenue=1.0/5 (mechanical, not advisory). (2) AUTOMATION_DECLARATION HARD GATE: missing block auto-scores Automation=1.0/5. (3) SAME-PATTERN-TWICE auto-escalation on Revenue<3.0 in consecutive 14d audits — immediate PERMANENT-FIX dispatch. (4) Step 8 output template NOW INCLUDES mandatory revenue_declaration + automation_declaration YAML blocks so every future cycle deliverable includes them automatically — eliminating the missing-block root cause. Council 4.22/3.5 PASS."
patched_v2_1: "2026-05-27 autonomous-chain-r2 — council 3.78/3.5 PASS: (1) Step 8 PRE-FLIGHT ENFORCEMENT: Step 8 now MUST call email-send.sh --revenue-usd and --auto-trigger — script rejects sends without these flags (exit 2). (2) email-send.sh v2: injects revenue_declaration + automation_declaration as HTML comment before every CEO email send — mechanical enforcement, not documentation. (3) Red Team finding implemented: template in docs != enforcement; enforcement = script gate. Council auditor_independent:true."
patched_v1_9: "2026-05-27 W22e — HARD ENFORCE: self-audit-history.jsonl write is MANDATORY on EVERY cycle completion (not just multi-round). One entry minimum per invocation. Audit found only 1 entry despite 17 output files = 94% miss rate. Fix: Step 8 adds mandatory state-history write before any output. council-step7-reminder.sh cron deployed on Ivan (0 8 * * *) to auto-flag stale council sessions. skills_root_mirror_id PLACEHOLDER cleaned to match drive_file_id."
patched_v1_8: "2026-05-26 v1.8 — FIX-01 score_delta threshold corrected (0.5 not 5), FIX-04 defer guard, FIX-08 strike Notion routing."
patched_v1_7: "2026-05-26 v1.7 — Inner council improvement loop with gate metric. State history write to ~/.openclaw/state/self-audit-history.jsonl per round. Strike escalation after 3 rounds for unfixed gaps. Council verdict 4.07/3.5 PASS."
patched: "2026-05-15 v1.5 — Bennett directive 2026-05-15 'permanently make those skills better for all agents.' Adds shared 8-dimension audit-core rubric (Revenue/Automation/Consolidation NEW). Forces REAL council-skill invocation in Step 4 (no synthetic council). Adds Same-Pattern-Twice escalation. Adds Reverse Audit-the-Audit gate. Adds cohort_routing block (cloud vs CLI). Adopts fleet loader contract (name + modifiedTime desc, no hardcoded fileIds). drive_file_id auto-populates on upload. Council v20 4.46/4.0 PASS."
patched_v1_4: "2026-05-14 v1.4 — Severity field + AUTO-FIRE COUNCIL on HIGH. Council 4.72/5."
patched_v1_3: "2026-05-09 v1.3 — Added Scope Discipline dimension. Council v16 4.40/4.0."
patched_v1_2: "2026-05-09 v1.2 — Audit-the-Audit gate. Council v16 4.36/4.0."
patched_v1_1: "2026-05-09 v1.1 — Project Advaita 100% Autonomy Checklist (35 items × 5 domains, 0-3, max 105). Council v16 4.24/4.0."
created_by: Mack (v1.0) + Hyperagent (v1.5)
council_verdict: "v1.5 council 2026-05-15 21:45 MDT — Operational pass 4.46/4.0. 5 advisors, 0 dissents, 1 Bennett gate (irreversible archive of superseded v1.4 file)."
trigger:
  - "self-audit"
  - "audit this work"
  - "audit this cycle"
  - "grade my work"
  - "self-audit-skill"
  - "audit the cycle that just ran"
---

# Self-Audit Skill v2.5

## v2.6 — SAME-PATTERN-EVERY-CYCLE ESCALATION (NEW 2026-05-29 — council APPROVED)

Extends the v2.0 Same-Pattern-**Twice** gate: the repeat-error check now fires on **EVERY autonomous cycle**, not only at end-of-thread recap or on consecutive-14-day revenue audits. Before any cycle closeout, query `~/.openclaw/bin/error-ledger.py list --open`; any signature with `count >= ESCALATE_THRESHOLD` still `open` / `regressed` / `fix-pending-propagation` is auto-classified **PERMANENT-FIX** and dispatched immediately. A defect is accepted as resolved **only** when `error-ledger.py check <sig>` returns OK (status `fixed` AND propagated into a skill on Drive, verified by readback). This is the wiring that makes "hit an error once → fix it → never hit it again" real instead of record-only — the exact gap behind Blueprint AI never learning.

## v2.5 Patch — Mandatory Correction Final Verifier

For every correction, self-audit, false-fix, recap-compliance, task-review, or "why is it still broken" response:

1. Draft the final answer to a local file.
2. Run `python3 ~/.openclaw/bin/fki_correction_final_verify.py <draft> --json`. (Canonical path: `~/.openclaw/bin/`. If the file is absent, log `verifier-missing: skipped` in the audit JSON and continue — do NOT silently pass; the skip itself must appear in the Claim Ledger.)
3. If it fails, revise the draft and rerun before answering Bennett.
4. Do not say `fixed`, `done`, `verified`, `Diamond`, `saved`, `patched`, or `complete` unless the Claim Ledger and strict verifier pass on that exact draft.
5. Treat the verifier as current-response proof only; side effects still require Drive/Notion/Gmail/Slack/CRM/memory receipts.

## v2.4 Patch — Behavior-Delta Gate for Corrections

When Bennett says the agent has not improved, says "why", "still", "again", "you keep", "not following", or asks to fix self-audit itself, self-audit must prove behavior changed in the current response. A skill patch alone is not improvement.

### Behavior-Delta Gate

Before any final answer on a correction/self-audit prompt, the final draft must include:

1. **Root cause:** one direct sentence explaining why the prior answer failed.
2. **Prior visible defect:** the exact behavior Bennett saw, stated without defensiveness.
3. **Current behavior delta:** what this response is doing differently before it claims any patch.
4. **Same-defect scan:** a check that the final draft does not repeat the prior visible defect.
5. **Mechanism changed:** the durable artifact or checker that changed, with proof.
6. **Current-response proof:** final checker output or explicit manual audit result on the exact final draft.
7. **Allowed claim boundary:** completion words are scoped to the proven mechanism only.

If any item is missing, print `self-audit: partial:behavior-delta-missing` and revise the answer before sending. Do not say `pass`.

### "Why" Answer Rule

If Bennett asks "why", answer the why before listing proof. The answer must name the failed mechanism, not hide behind a receipt. Valid shape:

```text
Why: <mechanism failed because ...>
Changed now: <current response behavior change ...>
Proof: <artifact/checker/fetchback ...>
```

### Same-Defect Red Flag

The audit fails if the final answer:

- says the skill improved without showing how the current response changed;
- gives proof links before answering the root cause;
- claims `self-audit: pass` after making any correction in the same response;
- patches Drive but omits final-draft self-audit proof;
- says memory/closeout/Diamond/verified without a receipt.

## v2.3 Patch — MICRO_RESPONSE_MODE + False-Done Claim Proof

Use this mode for every non-lite recap/correction/permanent-fix/named-skill final response. It is intentionally small: audit the exact response being sent, not the whole company.

### MICRO_RESPONSE_MODE seven checks
1. **Recap marker check:** Final draft contains PROJECT, ORIGINAL or THREAD, MEMORY, AI OPEN, HUMAN OPEN, five numbered options with exactly one starred recommendation, Reason after option 5, and CONTEXT.
2. **Exact final draft check:** The checker ran after the last edit, and the reported `draft_sha256` corresponds to the final draft being sent.
3. **Claim-proof scan:** Completion words in the final draft (`fixed`, `done`, `complete`, `completed`, `verified`, `Diamond`, `saved`, `created`, `updated`, `patched`, `replaced`, `PASS`, `passed`) are each backed by a same-response proof ledger row or downgraded to partial.
4. **Named-skill ledger:** Every named Drive skill has file ID, version, modified time or fetchback hash, mode used, steps followed, and blocked steps.
5. **Side-effect boundary:** Drive, Notion, Slack, Gmail, CRM, calendar, memory, deploy, and automation side effects have proof IDs/paths or explicit partial labels.
6. **Regression readback:** If a skill was patched, a fresh fetchback/readback contains the newly added rule before any final says fixed.
7. **Option lock:** The footer options are exactly `1.`, `2.`, one starred `3.` or other recommended number replacing the unstarred line, `4.`, `5.`, then `Reason:`.
8. **Behavior-delta check:** On correction prompts, the final draft answers root cause first, names the prior visible defect, shows current behavior delta, and scans for the same defect before sending.

### Ten claim-proof fixes for repeated false-done failures
1. The audit must inspect the final answer text itself, not only earlier tool outputs.
2. `fixed` is forbidden until proof exists for the exact mechanism that was broken.
3. `checker PASS` proves only the rules the checker actually enforces.
4. A missing expected rule in live Drive fetchback is a regression/overwrite, not proof that the prior fix remains valid.
5. If any issue was corrected during the audit, report `self-audit: corrected`; do not report pass.
6. If any proof channel is unavailable, report `self-audit: partial:<blocker>`.
7. For skill patches, require local patch, Drive replacement, Drive fetchback, hash/readback proof, and a receipt path before claiming fixed.
8. For memory, say `not saved` unless memory-skill or a supported memory write produced a receipt tied to the active Notion row or local receipt.
9. For Notion, Drive, Gmail, Slack, CRM, calendar, and deployments, require the specific URL, ID, receipt, or API result before completion wording.
10. If Bennett reports a same-message failure, escalate through council-skill Permanent Fix Approval Mode before claiming a durable correction.

### MICRO_RESPONSE_MODE output line
Print exactly one compact line near the recap footer:

```text
self-audit: pass | corrected | escalated | partial:<blocker>
```

Use `corrected` when the final draft or artifacts were changed in this response. Use `partial:<blocker>` when any required side effect or proof path could not be proven.

## v2.2 Patch — Blueprint Live-Funnel Proof Gates

When a cycle deliverable claims a lead capture, booking, CRM, public funnel, or revenue-path fix is live, self-audit-skill must require these gates before scoring Correctness, Revenue, Automation, or Cleanup above 4.5:

1. **Public deployed HTML readback:** Fetch the public URL after deployment and prove the live HTML contains the intended endpoint, identity persistence, and CTA behavior. Source-code proof alone is not enough.
2. **Public browser proof:** Run a real browser flow from the public URL through apply/intake, qualifier, and final CTA. Save the browser receipt and screenshot when relevant.
3. **Same-contact CRM proof:** Prove apply and qualifier update the same CRM contact ID. Search by exact email/phone and report duplicate count.
4. **Repeat-submit duplicate proof:** Submit the qualifying event at least 5 times for the same test identity and prove exact CRM contact count remains 1.
5. **Booking attachment proof:** If the flow books calls, prove the calendar event or appointment is attached to the same CRM contact. Modal-open proof alone is Yellow.
6. **Identity edge-case proof:** Test email/phone preservation, including plus aliases and phone normalization. External-widget failures must be named separately.
7. **Protected side-effect ledger:** List every send, booking, CRM mutation, Notion mutation, Drive mutation, deploy, or deletion/cancellation; include proof IDs or explicit blocked labels.
8. **Test-data cleanup boundary:** Do not cancel/delete proof records without Bennett approval. If proof artifacts remain live, label them Human Open.
9. **Final ask-to-proof map:** Every original ask must map to a receipt path, CRM/Notion/Gmail/Drive ID, validator output, or blocker.
10. **Monitor requirement:** A live revenue-path fix cannot score Automation 5/5 unless a recurring monitor or alert exists and has a passing dry-run/live-run receipt.

If any required gate is missing, the audit can still pass, but the missing gate must cap the affected dimension and prevent 100%/Diamond wording.

## North Star (v1.5 — codifies Bennett directive 2026-05-15)

Succeeds when a single ship-it / overdrive / autopilot / batch-overdrive cycle deliverable has been graded against (a) its ORIGINAL ASK and (b) Bennett's UNIVERSAL COMPLETION GATES — revenue, automation, consolidation — gaps identified, REAL council-approved fixes applied via autopilot, and a clear before/after delta produced, all WITHOUT Bennett review.

A "good" cycle audit is one where the audit itself would survive an audit. No synthetic council. No padded gap lists. No ~/Desktop output on cloud. Drive canonical paths only.

## Purpose

Cycle-scope work audit. Three sibling skills:

| Skill | Scope | Output |
|---|---|---|
| business-audit-skill v2+ | Company (36 dimensions of FKI) | Strategic audit + needle-mover plan |
| diamond-skill v2.1+ | Pass/fail validation per item | Adversarial T1 + Recovery T2 + Boundary T3 |
| **self-audit-skill (this)** | **One cycle's deliverable** | **Grade + gap list + REAL council fixes + delta** |

self-audit grades THIS work product, finds gaps, fixes them via council+autopilot, and reports before/after. The missing piece between "ship-it finished" and "I trust this work."

## v1.5 Patches (post-council, 2026-05-15)

### PI-SA-NS-1 (HIGH) — Shared 8-dimension audit-core rubric

**Rule:** Every cycle audit scores 8 dimensions, not 5. Three NEW dimensions:
- **Revenue** — Does the deliverable have a revenue_declaration block? Is `expected_revenue_impact_usd ≥ revenue_floor_usd` (default $500 LIGHT / $1000 MEDIUM / $2500 FULL)?
- **Automation** — Does the deliverable have an automation_declaration block? Is `is_self_running: true` + `trigger_ref` present + `trigger_verified_at` populated?
- **Consolidation** — Did the cycle REDUCE Notion sprawl (merge duplicates pre-spawn) or fan it out? Did Step 0.5 fire on batch cycles?

These three dimensions are NON-NEGOTIABLE on customer-deliverable cycles. Infra cycles may receive a `--no-revenue-gate` flag from the invoker (Bennett-approved override only).

### PI-SA-NS-2 (HIGH) — REAL council invocation, no synthetic council

**Root cause:** v1.4 self-audit on 2026-05-15 said "Council input (synthesized — would normally invoke council-skill inline)" and proceeded with paraphrased advisor opinions. That's audit theater.

**Rule:** Step 4 MUST produce a real council-skill v20 artifact:
- Either invoke council-skill inline via the cloud cohort's actual 5-advisor protocol AND save the artifact to Drive as `council-cycle-<slug>-<ISO>.md`
- OR if council-skill is unavailable, hard-fail the audit and surface a Bennett gate

No "synthesized" / "as if council ran" / "would normally invoke" language permitted. If you cannot run council, you cannot complete the audit.

### PI-SA-NS-3 (MEDIUM) — Same-Pattern-Twice escalation

**Rule:** Before Step 4 council, hash the gap list by `<gap.severity>:<gap.affected_artifact>:<gap.root_cause>`. Query the last 14 days of self-audit artifacts in Drive. If the SAME pattern hash appears in ≥2 prior audits, auto-classify as PERMANENT-FIX project:
- Dispatch autopilot-skill via Leo WO with the pattern as the project scope
- Annotate current audit: `same_pattern_twice_escalation=true; autopilot_wo_id=<id>`
- Do NOT add the gap to the regular fix list — it's now an autopilot project, not a one-cycle patch

Pattern hash uses gap NATURE + AFFECTED COMPONENT, NOT just title (per Red Team rebuttal). 80%+ string overlap on `affected_artifact` OR identical `root_cause` = same pattern.

### PI-SA-NS-4 (MEDIUM) — Reverse Audit-the-Audit gate

**Existing Audit-the-Audit (v1.2):** fires when grade JUMP >0.5 between rounds — catches inflated gap lists.

**NEW Reverse gate:** fires when audit grade ≥4.5 AND diamond-skill T1/T2/T3 FAILS on the artifact afterwards. Triggers council with question:
> "Audit gave this artifact ≥4.5 but it failed diamond gate. What material gap did the audit miss?"

If council finds a material gap → revise audit grade down by 0.5 + annotate `reverse_audit_the_audit: <gap>`.

### PI-SA-NS-5 (HIGH) — Cohort routing block

**Rule:** Every audit cycle starts by determining cohort:

```yaml
cohort_routing:
  cloud:                          # Hyperagent / Madison
    output_path: drive_skills_root_or_subfolder
    desktop_fallback: false
    council_invocation: inline_5_advisor_synthesis
    restricted_tools: [GHL, METAADS_unverified, browser_cookie3, op_cli]
    restricted_tool_action: dispatch_to_leo_wo_in_C0AKXT2S1T2
  cli:                            # Ivan-CC / Mack
    output_path: ~/Desktop/audits/
    desktop_fallback: true
    council_invocation: real_council_skill_subprocess
    restricted_tools: []
    restricted_tool_action: direct_execution
```

Detect cohort via env: `HOSTNAME contains "hyperagent"` → cloud; presence of `~/.openclaw/state/` → cli.

### PI-SA-NS-6 (MEDIUM) — Fleet loader contract

**Rule:** When loading any dependency skill, NEVER hardcode the fileId. Always:
```
1. GOOGLEDRIVE_FIND_FILE query "name = '<skill-name>' and parents contains '<skills-root-or-folder>'"
2. Sort modifiedTime DESC, pick top 1
3. Verify modifiedTime <30d old → else flag STALE and continue
4. GOOGLEDRIVE_DOWNLOAD_FILE on that fileId
```
Old "Dependencies (fileId: ...)" lines are deprecated. New format below uses NAMES only.

### PI-SA-NS-7 (MEDIUM) — drive_file_id auto-populate

**Rule:** On every skill upload (this skill OR any audited skill), run a post-upload verify:
```python
uploaded_id = GOOGLEDRIVE_UPLOAD_FROM_URL(...).id
yaml_id = parse_yaml(file)["drive_file_id"]
if yaml_id == "AUTO_POPULATED_ON_UPLOAD" or yaml_id == "PLACEHOLDER_SET_AFTER_UPLOAD" or yaml_id != uploaded_id:
    rewrite yaml drive_file_id = uploaded_id
    re-upload (replace=uploaded_id)
```
Skill fails Cleanup dimension audit if PLACEHOLDER text remains.

## When to Invoke
- Immediately after ship-it-skill / overdrive-skill / autopilot-skill / batch-overdrive-skill completes
- After any autonomy cycle that produced a tangible deliverable
- Triggers (any of): "self-audit", "audit this work", "audit this cycle", "grade my work", "self-audit-skill", "audit the cycle that just ran"
- Auto-fire: full-cycle-skill (when built) calls this between ship-it and closeout

## Inputs (any of)
1. Artifact path (file or folder) — preferred
2. Cycle-state JSON (cli cohort: `~/.openclaw/state/[skill]-last-cycle.json`; cloud cohort: brain.md cycle section)
3. Last-N-commits diff (if cycle produced code)
4. Conversation context (last user prompt + executed actions) — fallback

## Hard Rules (v1.5)
1. NEVER ask Bennett operational questions. Pull cycle context from state files / brain / context.
2. Grade against ORIGINAL ASK **and** UNIVERSAL COMPLETION GATES (revenue + automation + consolidation).
3. Maximum 1 council+autopilot improvement loop per audit. No infinite recursion.
4. Output ALWAYS includes initial grade, final grade, and delta.
5. If grade <4.0 after fixes → escalate to extra-push-skill, not human.
6. Save artifact per cohort_routing block (cloud → Drive skills root; CLI → ~/Desktop).
7. Never overlap with diamond-skill scope. self-audit grades quality. diamond validates pass/fail.
8. **v1.5: Step 4 MUST invoke REAL council-skill v20 (artifact on Drive). No synthetic council.**
9. **v1.5: Step 3.6 same-pattern-twice escalation MUST fire when triggered.**
10. **v1.5: Step 7.5 reverse audit-the-audit MUST fire on grade ≥4.5 + diamond fail.**
11. **v1.5: Cohort routing block MUST be honored for output path + tool restrictions.**
12. **v1.5: Dependencies loaded by NAME + modifiedTime desc only — no hardcoded fileIds.**

## Execution Chain

### Step 0 — Cohort detect + dependency load
1. Detect cohort (cloud vs cli) per cohort_routing block.
2. Load council-skill latest by name → modifiedTime desc. **Version gate (v1.6 NEW):** After loading, parse the `version:` field from the SKILL.md YAML header. If `version < 20` → HALT with "Council skill stale — version X found, need ≥20. Post to #leo-coaches." Do NOT proceed to Step 1 without council v20+.
3. Load autopilot-skill latest by name → modifiedTime desc.
4. Load diamond-skill latest by name → modifiedTime desc.
5. Load caveman-skill latest by name → modifiedTime desc.
6. Load recap-skill latest by name → modifiedTime desc.
7. Verify each modifiedTime <30d → else annotate STALE_DEPS in audit output.

### Step 0.5 — Every-Cycle Error-Ledger Check (v2.6 — HARD ENFORCE)

**Fires on EVERY audit invocation before spec recall.** This is the execution wiring for the v2.6 prose section ("SAME-PATTERN-EVERY-CYCLE ESCALATION"). Without this step, that section is documentation only.

```bash
python3 ~/.openclaw/bin/error-ledger.py list --open
```

- If output is empty (no open signatures) → log `error-ledger: clean` in audit JSON and continue.
- If any signature has `count >= ESCALATE_THRESHOLD` (default: 2) with status `open` / `regressed` / `fix-pending-propagation`:
  1. Auto-classify as PERMANENT-FIX. Do NOT add to this cycle's regular gap list.
  2. Dispatch autopilot-skill via Leo WO with scope = signature + affected component.
  3. Annotate audit JSON: `error_ledger_escalations: [{sig, count, status, wo_id}]`.
  4. A signature is only accepted as resolved when `error-ledger.py check <sig>` returns `fixed` AND the fix is propagated to a Drive skill (verified by readback).
- If `error-ledger.py` is missing → log `error-ledger: tool-missing` in audit JSON, continue; flag STALE_DEPS in output.

### Step 1 — Spec Recall (BLOCKING)
Pull original ask. Sources in priority:
1. Cycle state JSON `spec` field (cli) OR brain.md cycle section (cloud)
2. Last user prompt before cycle started (parse from session log / conversation)
3. Notion sprint row linked to cycle
4. **v1.5 NEW:** Bennett's UNIVERSAL COMPLETION GATES read from latest batch-overdrive-skill SKILL.md North Star

Output: 3-5 bullet "What was asked" + 3 universal gates verbatim. **If you can't find the original ask in <30 seconds, abort and route to #leo-coaches** — auditing without spec = grading air.

### Step 2 — Initial Grade (shared 8-dim audit-core rubric, v1.5)

Score 0-5 per dimension:

| # | Dimension | What it measures | Pass |
|---|---|---|---|
| 1 | Completeness | Did we deliver what was asked? | 4.0 |
| 2 | Correctness | Does it actually work under live conditions? | 4.5 |
| 3 | Constraints | Caveman, Drive canonical, no ~/Desktop on cloud, no protected file edits, no NOTION_UPSERT on existing rows, bennett-mode-skill present where mandated | 4.5 |
| 4 | **Revenue (NEW v1.5)** | revenue_declaration present + `expected_revenue_impact_usd ≥ floor` | 4.0 |
| 5 | **Automation (NEW v1.5)** | automation_declaration present + `is_self_running: true` + verified trigger | 4.0 |
| 6 | **Consolidation (NEW v1.5)** | Did cycle REDUCE Notion sprawl or fan out? Step 0.5 fired (batch cycles)? | 4.0 |
| 7 | Cleanup | Orphans, broken refs, PLACEHOLDER_SET_AFTER_UPLOAD, stale drive_file_ids | 4.0 |
| 8 | Scope Discipline | Per v1.3 classification (ALIGNED BONUS / NEUTRAL / SCOPE CREEP) | 4.0 |
| Bonus | +0.5 cap | Aligned-and-useful additions | additive |

**Grade formula:** `avg(8 dimensions) + Bonus`. Bonus capped at +0.5.

**REVENUE_DECLARATION HARD GATE (v2.0 — council 4.22/3.5 PASS 2026-05-27):**
BEFORE computing grade, check if cycle artifact includes a `revenue_declaration` block with `expected_revenue_impact_usd` and `revenue_floor_usd`. If MISSING:
- Auto-set Revenue dimension = **1.0/5** (mechanical — not adjustable by rubric scorer)
- Prepend to Step 3 gap list: `{severity: "high", affected_artifact: "revenue_declaration", root_cause: "No revenue_declaration block in deliverable — impact unquantified", proposed_fix: "Add revenue_declaration block with expected_revenue_impact_usd and revenue_floor_usd before cycle ships"}`
This turns Revenue from advisory scoring to **mechanical enforcement**.

**AUTOMATION_DECLARATION HARD GATE (v2.0):**
BEFORE computing grade, check if cycle artifact includes an `automation_declaration` block with `is_self_running: true` + `trigger_ref` + `trigger_verified_at`. If MISSING:
- Auto-set Automation dimension = **1.0/5** (mechanical — not adjustable)
- Prepend to Step 3 gap list with severity=MEDIUM

**SAME-PATTERN-TWICE FAST-PATH (v2.0):**
If Revenue dimension < 3.0 in current audit AND any prior self-audit in last 14d also had Revenue < 3.0:
- Skip full Step 3.6 hash calculation
- Immediately auto-classify as PERMANENT-FIX project: dispatch autopilot-skill with scope "revenue_declaration block missing from cycle deliverables"
- Annotate: `revenue_same_pattern_escalation: true`

**Scope Discipline classification (preserved from v1.3):** For each unasked addition, classify ALIGNED BONUS / NEUTRAL / SCOPE CREEP. SCOPE CREEP = −0.5 per occurrence.

**Verdict table:**
| Grade | Verdict |
|---|---|
| <4.0 | REWORK — proceed to Step 3 |
| 4.0–4.5 | SHIP-WITH-FIXES — proceed to Step 3 |
| >4.5 | PASS — skip to Step 7 (post-diamond check still required for reverse-AtA) |

### Step 3 — Gap List

For each dimension scoring <4.0 (or 4.5 for Correctness/Constraints), list specific gap. Each gap MUST include:
- `severity`: high | medium | low
- `affected_artifact`: file/row/URL/skill_name
- `root_cause`: 1-2 sentences
- `proposed_fix`: 1 sentence

### Step 3.5 — AUTO-FIRE COUNCIL on HIGH severity (preserved v1.4)
Any severity=high gap → auto-invoke council-skill in Step 4. No manual user-prompt path.

### Step 3.6 — SAME-PATTERN-TWICE Check (NEW v1.5)
1. Hash each gap by `<severity>:<affected_artifact>:<root_cause>` (normalized — lowercase, stoplist removed).
2. Query Drive folder `1ZBvY1JaG9u-PhZhzRDhlQO1koPVRY33l` for `name contains 'self-audit'` with `modifiedTime` in last 14 days.
   **v1.6 ADD — First-run path:** If query returns 0 artifacts → log `"first_run=true; no prior self-audit artifacts in 14d window; same-pattern-twice check skipped"` in audit JSON. Continue to Step 3.5 / Step 4 immediately. Do NOT error or block.
3. Read each artifact's gap list section.
4. For each current gap, check if same pattern hash appears in ≥1 prior artifact (counting current = 2nd occurrence).
5. If matched:
   - Auto-classify current gap as PERMANENT-FIX project
   - Dispatch autopilot-skill via Leo WO with scope = `<root_cause>` + `<affected_artifact>` + remediation notes
   - Annotate audit JSON: `same_pattern_twice_escalation: true, autopilot_wo_id: <id>, pattern_hash: <hash>, prior_artifacts: [<list>]`
   - Remove the gap from the regular fix list

### Step 4 — REAL Council on Gaps (v1.5 — no synthetic)

**MANDATORY:** Invoke council-skill (latest, loaded in Step 0). For cloud cohort, this means executing the 5-advisor synthesis using the loaded SKILL.md protocol AND producing a real artifact `council-cycle-<slug>-<ISO>.md` saved to Drive folder `1dikjqZvnsWbbvVjNupiCWC-qN3fWfesV` (council-skill folder).

Council input:
```
QUESTION: Here are the gaps in cycle [X]. Recommend top 3 fixes.
GAPS: [list from Step 3, post Step-3.6 filtering]
ORIGINAL ASK: <verbatim>
UNIVERSAL COMPLETION GATES: revenue ≥ $<floor>, automation self-running, consolidation reduced sprawl
STAKES: Operational (4.0+ threshold)
ASK: One ranked fix list, dispatch via autopilot.
```

Council artifact MUST include:
- 5 advisor scores + recommendations
- Mentor lens roll-up (Hormozi/Vee/Robbins)
- Gate audit (Step 4.0 false-gate auditor results)
- Chairman synthesis
- Red Team rebuttal
- Diamond stress test
- council-log.json entry

**Hard fail:** if Step 4 cannot produce a real artifact (council-skill unavailable, Drive write fails), abort audit + surface Bennett gate "Council unavailable — cannot complete audit on cycle X."

### Step 5 — Autopilot Dispatch (one pass only)
Invoke autopilot-skill on council-recommended fixes. **Hard cap: 1 pass.** If autopilot can't close gap in one pass, surface as Bennett gate.

### Step 5.5 — IMPROVEMENT GATE + INNER LOOP (NEW v1.7)

#### TO-100 TARGET CONTRACT (NEW v2.7 — Bennett directive 2026-06-01, council 3.67/3.5 PASS)

**The aim of every self-audit round is 5.0/100% on EVERY dimension — not merely a PASS.** This retargets the inner loop from "good enough" to "perfect, or the honest distance from it."

1. **Council question is reframed to path-to-100.** When Step 4 invokes council, the QUESTION is NOT "recommend top 3 fixes" but: *"For each dimension scoring < 5.0, name the SMALLEST 1-2 changes that move it to 5.0. Rank by least-effort-highest-gain."* Council returns small, surgical changes — never a rewrite. The discipline is **1-2 small changes per sub-5.0 dimension per round**, so the work is bounded and re-testable.
2. **100% is ASPIRATIONAL, never a hard exit.** Do NOT loop forever chasing an unreachable 5.0. The round-cap (3) and the plateau guard below are the real terminators. At terminate, report the honest gap: `best reached X.X/5 (Y%), Z/8 dimensions at 5.0`. Fabricating a 5.0 to satisfy the aim is a hard audit failure (worse than an honest 4.3).
3. **Plateau guard (terminate early, honestly):** if `score_delta < 0.3` for 2 consecutive rounds, OR `held_pct < 50` (fixes not surviving), STOP looping and report — more rounds won't help; escalate the residual per the strike path below.
4. **HELD % (re-measurement — the metric Bennett asked for).** After Step 6 re-grade, compute and REPORT held %. A fix counts **HELD** only if ALL three are true on the re-grade (non-gameable, mirrors the line-453 anti-hardcode rule — **recomputed from real before/after counts, never asserted**):
   - (a) the dimension the fix targeted is ≥ its immediate post-fix score, AND
   - (b) NO other dimension regressed below its pre-fix baseline, AND
   - (c) the cycle aggregate (avg of 8) did not fall.
   `held_pct = (fixes meeting a+b+c) / (fixes_executed) * 100`. Print one line: `path-to-100: <N> dims < 5.0 → council named <M> changes → <K>/<M> applied → held <held_pct>% → best <X.X>/5`.

**Gate metric (FIX-01 — corrected scale):** self-audit scores 0–5 per dimension (avg = 0–5 total). After Step 5, check: `score_delta ≥ 0.5 on 0-5 scale` OR `fixes_executed ≥ 2`. Either = advance to Step 6. **NOT ≥5pts — that threshold is impossible on a 0-5 scale and was a critical bug.** (TO-100 note: the gate still governs round-advance; the 5.0 aim governs WHAT council is asked for and WHAT held% measures — the two compose, the gate is not replaced.)

**FIX-04 — 0-EXECUTE guard:** If council returns 0 EXECUTE items (all DEFER/SKIP), that round does NOT count toward the 3-round cap. Track `defer_count` separately. If `defer_count >= 2`, skip remaining rounds and go straight to strike escalation — don't waste more council calls.

**If gate FAILS (both conditions unmet):**
- If round_count < 3 AND defer_count < 2: increment round_count, go back to Step 4 (fresh council pass on REMAINING unfixed gaps only — not the full gap list)
- If round_count == 3 OR defer_count >= 2: do NOT loop again. For each unfixed gap:
  1. Write to `~/.openclaw/workspace/known-issues/<audit_slug>-<gap_slug>.md` with full gap context
  2. Post to #leo-coaches (C0AQ4KB1SA0): "🔴 SELF-AUDIT STRIKE L2: unfixed gap after 3 rounds — <gap.root_cause> | cycle <cycle_slug>"
  3. → Execute strike-skill Level 2 entry for each (session-error-capture mode — no web search needed, go straight to council input for persistent fix)
  4. Advance to Step 6 with remaining gaps carried forward in `carry_forward[]`

**State history write (every round — mandatory):**
```bash
python3 -c "
import json, datetime, os
entry = {
  'ts': datetime.datetime.utcnow().isoformat()+'Z',
  'cycle_slug': '$CYCLE_SLUG',
  'round': $ROUND_COUNT,
  'score_before': $SCORE_BEFORE,
  'score_after': $SCORE_AFTER,
  'delta': $SCORE_AFTER - $SCORE_BEFORE,
  'fixes_executed': $EXECUTE_COUNT,
  'gaps_remaining': $REMAINING_GAP_COUNT,
  'gate_passed': $GATE_PASSED
}
os.makedirs(os.path.expanduser('~/.openclaw/state'), exist_ok=True)
with open(os.path.expanduser('~/.openclaw/state/self-audit-history.jsonl'), 'a') as f:
  f.write(json.dumps(entry) + '\n')
"
```

### Canonical Loop-Engine Map (v1.8 — 2026-05-27 consolidation)
The self-improvement loop (score → council → permanent fix → redo → re-measure) lives in **3 engines by scope — never reimplemented elsewhere:**
| Scope | Canonical engine | Callers |
|---|---|---|
| One deliverable | **gatekeeper-skill** | every email/report/blueprint |
| One cycle | **self-audit-skill (this)** | overdrive, ship-it, autopilot, extra-push (via their Loop-Consolidation Hook) |
| Cross-project / meta | **full-autonomy-loop-skill** | weekly / big pushes; escalation target on same-gap-3× |

The 4 wrappers call THIS skill at cycle end instead of carrying their own partial loops. Their `round_deltas[]` use the same shape as the State-History write above. A wrapper that grades/councils inline (not via this engine) = DRIFT → log to #leo-coaches.

**FIX-08 — Strike Notion routing:** Strike entries go to sub-page of existing "Known Issues" sprint project, NOT new master Sprint Board rows. Sprint Board cap = 30 rows. Strike entries would overflow it within days.

**FIX-01 — Score scale:** Always use 0–5 scale matching self-audit dimensions. Never compare delta to "5pts" — that's the full scale maximum, not an improvement threshold.

**Anti-patterns (v1.7 council-hardened):**
- ❌ Looping more than 3 effective rounds (defer rounds don't count) (-5)
- ❌ Skipping state history write per round (-3)
- ❌ Routing strike escalation through Leo without DIY attempt (-3)
- ❌ Re-running council on already-fixed gaps (-2 — remaining gaps only)
- ❌ Using score_delta ≥ 5 as gate — scale is 0-5, use ≥ 0.5 (-5 — FIX-01 critical bug)
- ❌ Creating new Sprint Board master rows for strike entries (-3 — FIX-08)
- ❌ Continuing loop after 2 consecutive 0-EXECUTE council rounds (-3 — FIX-04)

### Step 6 — Re-Grade
Repeat Step 2 with fixes applied. Compute delta.

### Step 7 — Diamond Gate
Invoke diamond-skill on final state (post-fixes). T1 / T2 / T3 must all pass.

### Step 7.5 — REVERSE Audit-the-Audit (NEW v1.5)
**Trigger:** Final grade ≥4.5 AND diamond-skill T1/T2/T3 FAILS.

**Action:** Invoke council with prompt:
```
QUESTION: Audit gave this artifact <grade> but it failed diamond gate <T1|T2|T3 failure>. What material gap did the audit miss?
ORIGINAL ASK: <verbatim>
AUDIT GAP LIST: <verbatim>
DIAMOND FAILURE: <verbatim>
```

If council finds material gap → revise grade down 0.5 + annotate `reverse_audit_the_audit: <gap>` in output JSON.

### Step 8 — Output

**MANDATORY PRE-OUTPUT (v1.9 HARD ENFORCE):** Before any output file is written, append one line to `~/.openclaw/state/self-audit-history.jsonl`. This is NON-OPTIONAL. A self-audit that does not write to state-history = incomplete run (Angie will flag it). Root cause of 94% miss rate (1 entry for 17 output files) was this step being inside the "per-round" loop only. Now fires on EVERY invocation regardless of rounds.

```bash
python3 -c "
import json, datetime, os
entry = {
  'ts': datetime.datetime.utcnow().isoformat()+'Z',
  'cycle_slug': 'CYCLE_SLUG',
  'initial_grade': INITIAL_GRADE,
  'final_grade': FINAL_GRADE,
  'delta': FINAL_GRADE - INITIAL_GRADE,
  'fixes_executed': EXECUTE_COUNT,
  'gaps_found': GAP_COUNT,
  'gaps_remaining': REMAINING_COUNT,
  'council_score': COUNCIL_SCORE,
  'diamond_pass': DIAMOND_PASS
}
os.makedirs(os.path.expanduser('~/.openclaw/state'), exist_ok=True)
with open(os.path.expanduser('~/.openclaw/state/self-audit-history.jsonl'), 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('state-history written')
"
```

Save per cohort_routing:
- Cloud: SaveFile → PublishFilePublicly → GOOGLEDRIVE_UPLOAD_FROM_URL to skills root with name `self-audit-<cycle-slug>-YYYY-MM-DD.md`
- CLI: write to `~/Desktop/self-audit-<cycle-slug>-YYYY-MM-DD-HHMM.md`

```markdown
# Self-Audit: [Cycle Name]
Audited: [ISO] | Cycle: [skill name] | Cohort: [cloud|cli]

## What was asked
- [bullet]
## Universal completion gates
- Revenue floor: $X
- Automation required: true
- Consolidation expected: true

## Initial grade: X.X/5
| Dimension | Score | Notes |
|---|---|---|
| Completeness | ... |
| Correctness | ... |
| Constraints | ... |
| Revenue | ... |
| Automation | ... |
| Consolidation | ... |
| Cleanup | ... |
| Scope Discipline | ... |

## Gaps found
1. [severity · affected_artifact · root_cause · proposed_fix]

## Same-Pattern-Twice escalations (NEW v1.5)
- [list — empty if none]

## Council artifact
- Drive file ID: <id>
- Verdict: X.X/4.0 — PASS/FAIL
- Mentor lenses: [Hormozi/Vee/Robbins counts]

## Fixes applied (council + autopilot)
1. [fix] → [result]

## Final grade: X.X/5 (delta: +X.X)
| Dimension | Before | After |
|---|---|---|

## Diamond gate: [PASS/FAIL]
## Reverse Audit-the-Audit: [N/A | FIRED — revised grade X → Y]

## revenue_declaration (MANDATORY — v2.0 HARD GATE — every cycle output)
```yaml
revenue_declaration:
  expected_revenue_impact_usd: <int>  # 0 for pure infra cycles; must be explicit, not omitted
  revenue_floor_usd: 0                # infra default; override for customer deliverables ($500/$1000/$2500)
  measurement_window_days: 90
  measurement_method: "<quality-gate-bypass-prevention|pipeline-impact|direct-revenue>"
  ground_truth_artifact: "<gatekeeper-ledger.jsonl|notion-pipeline-id|email-msgId>"
```

## automation_declaration (MANDATORY — v2.0 HARD GATE — every cycle output)
```yaml
automation_declaration:
  is_self_running: <true|false>
  trigger_ref: "<cron-schedule|launchagent-plist|webhook-url|none-manual>"
  trigger_verified_at: "<ISO timestamp or 'not-yet-deployed'>"
  deploy_target: "<ivan-cron|mack-launchagent|leo-cron|drive-skill|none>"
```

**HARD RULE (v2.0):** If either block is ABSENT from the cycle deliverable, the self-audit
MUST auto-set that dimension to 1.0/5 (mechanical, not advisory). The blocks must be present
in the ARTIFACT, not just noted in the audit. The autopilot fix for missing blocks = add the
template above to the skill/artifact and re-run. No override, no manual waiver.

## Carry-forward
- [items not closed]
```

If chained from full-cycle-skill, emit cycle-state JSON update with `audit_grade` field.

## 🔴 CLOSING HARDGATE (v1.6 — Bennett directive 2026-05-22; cycle-state gate added v2.7)

**Audit ≠ plan. Audit = fix.** See memory: `feedback_audit_plan_never_fixed_loop`.

**CYCLE-STATE GATE (v2.7 — replaces session-digest check):**
Before any completion claim, read `~/.openclaw/state/<skill>-last-cycle.json` for the skill being audited (e.g. `~/.openclaw/state/self-audit-skill-last-cycle.json`). This is the durable cross-session record, not the in-memory session digest which dies on handoff.
```bash
python3 -c "
import json, os, sys
skill = sys.argv[1] if len(sys.argv) > 1 else 'self-audit-skill'
path = os.path.expanduser(f'~/.openclaw/state/{skill}-last-cycle.json')
if not os.path.exists(path):
    print(f'cycle-state: no prior cycle file at {path} — seeding empty record')
    with open(path, 'w') as f:
        json.dump({'cycle_slug': None, 'last_run_utc': None, 'last_grade': None, 'open_gaps': []}, f, indent=2)
else:
    d = json.load(open(path))
    print(f'cycle-state: last_run={d.get(\"last_run_utc\")}, last_grade={d.get(\"last_grade\")}, open_gaps={len(d.get(\"open_gaps\", []))}')
" self-audit-skill
```
Gate rule: if `open_gaps` from prior cycle is non-empty, those gaps MUST appear in current Step 3 gap list (carry-forward) — do not silently drop prior-cycle gaps. A session restart does not clear carry-forward.

**Defect-seed verification (run once after editing this gate to confirm it catches real gaps):**
```bash
python3 -c "
import json, os
path = os.path.expanduser('~/.openclaw/state/self-audit-skill-last-cycle.json')
# Seed a synthetic open gap
d = json.load(open(path)) if os.path.exists(path) else {}
d.setdefault('open_gaps', []).append({'sig': 'TEST-DEFECT', 'root_cause': 'gate-verification seed', 'severity': 'low'})
with open(path, 'w') as f: json.dump(d, f, indent=2)
print('defect seeded — re-run audit and confirm gap appears in Step 3 carry-forward')
"
```
Remove the seeded gap after verification by deleting the TEST-DEFECT entry from the JSON.

Before declaring "self-audit complete":
1. Read cycle-state JSON (above gate) — carry forward any prior open_gaps
2. Each gap → council scores EXECUTE / SKIP / DEFER (no gating, just labeling)
3. EVERY EXECUTE → dispatched to autopilot-skill same cycle, receipt logged
4. EVERY DEFER → Notion WO created, never silently dropped
5. Verify receipts ≥ EXECUTE count, else SKILL FAILED → reopen
6. NEVER leave `## Priority Actions` / `## Recommendations` as the final state
7. NEVER ask "want me to fix these?" — implicit fix authorization (see `feedback_never_ask_after_fix_directive`)

## Anti-Patterns

- ❌ NEW v1.6: Ending audit with unactioned `## Priority Actions` list (-5 — Bennett 2026-05-22)
- ❌ NEW v1.6: Asking re-approval after audit before dispatching fixes (-5)
- ❌ Auditing the WHOLE company → use business-audit-skill (-5)
- ❌ Pass/fail only without grading → use diamond-skill (-3)
- ❌ Looping more than 1 council+autopilot pass (-3)
- ❌ Skipping original ask recall in Step 1 (-5 — invalidates audit)
- ❌ Outputting only initial grade without final + delta (-3)
- ❌ Asking Bennett anything (-5)
- ❌ Saving to ~/Desktop on cloud cohort (-3 — cohort_routing violation)
- ❌ Skipping Step 7 Diamond gate (-3)
- ❌ **v1.5: Synthetic council in Step 4 ("would normally invoke...") (-5 — audit theater)**
- ❌ **v1.5: Skipping Step 3.6 same-pattern-twice check (-3)**
- ❌ **v1.5: Skipping Step 7.5 reverse audit-the-audit on grade ≥4.5 + diamond fail (-3)**
- ❌ **v1.5: Scoring without Revenue/Automation/Consolidation dimensions on customer-deliverable cycles (-5 — Bennett directive violation)**
- ❌ **v1.5: Hardcoded fileIds in dependency loads (-2 — loader contract violation)**
- ❌ **v1.5: Leaving drive_file_id as PLACEHOLDER / AUTO_POPULATED_ON_UPLOAD after upload (-3)**

## Dependencies (load by NAME + modifiedTime desc — NO hardcoded fileIds, v1.5)

- council-skill — Step 4 (MANDATORY real invocation)
- autopilot-skill — Step 5
- diamond-skill — Step 7
- caveman-skill — voice
- recap-skill — output formatting
- batch-overdrive-skill — read latest North Star for Universal Completion Gates (Step 1 universal-gates load)

## Project Advaita 100% Autonomy Checklist (105-point rubric, preserved v1.1)

**Standalone invocation mode.** Trigger: "advaita rubric" / "advaita 100" / "audit advaita autonomy".

The 5 Advaita Vision domains × 7 checks each = **35 items, scored 0-3, max 105 points**.

| # | Domain | Check | Max |
|---|--------|-------|-----|
| 1 | Lead Acquisition | Meta CAPI live | 3 |
| 2 | Lead Acquisition | Apollo+Instantly daily | 3 |
| 3 | Lead Acquisition | LinkedIn 8am cron | 3 |
| 4 | Lead Acquisition | Form auto-validation | 3 |
| 5 | Lead Acquisition | CPL dashboard | 3 |
| 6 | Lead Acquisition | Speed-to-lead <5min | 3 |
| 7 | Lead Acquisition | Brand auto-attribution | 3 |
| 8 | Lead Processing | GHL SMS+email no-show seq + LeadScorer (SynthFlow DROPPED 2026-05-30) | 3 |
| 9 | Lead Processing | GHL 3-touch auto-fire | 3 |
| 10 | Lead Processing | Unassigned leads = 0 | 3 |
| 11 | Lead Processing | Day-90 re-engage | 3 |
| 12 | Lead Processing | DQ reason carry-forward | 3 |
| 13 | Lead Processing | Stage transition auto | 3 |
| 14 | Lead Processing | Post-call qual report | 3 |
| 15 | Sales Intelligence | Pre-call prep PDF | 3 |
| 16 | Sales Intelligence | Post-call pipeline | 3 |
| 17 | Sales Intelligence | Coaching analyzer | 3 |
| 18 | Sales Intelligence | Weekly pipeline report | 3 |
| 19 | Sales Intelligence | Territory report <60s | 3 |
| 20 | Sales Intelligence | Battle card refresh | 3 |
| 21 | Sales Intelligence | Transcript routing 2hr | 3 |
| 22 | Operations | Bennett digest 8am | 3 |
| 23 | Operations | Sprint board auto-update | 3 |
| 24 | Operations | Notion personal block | 3 |
| 25 | Operations | Machine health widgets | 3 |
| 26 | Operations | Backup chain | 3 |
| 27 | Operations | Leo-bridge >99% 7d | 3 |
| 28 | Operations | Skill versioning | 3 |
| 29 | Financial Control | Cash runway dashboard | 3 |
| 30 | Financial Control | Budget variance alert | 3 |
| 31 | Financial Control | AR/commission Piper | 3 |
| 32 | Financial Control | Cost-per-signed-deal | 3 |
| 33 | Financial Control | CFO Quarterly QB sync | 3 |
| 34 | Financial Control | Divvy+Amex auto-import | 3 |
| 35 | Financial Control | Bennett-approval gate | 3 |

**Scoring guide:** 3 = fully automated + live in prod; 2 = deployed but partial/flaky; 1 = scripted/built but not running; 0 = missing entirely.
**Baseline file:** `~/.openclaw/state/advaita-autonomy-baseline-v2.json` (last scored 2026-05-12, 94.0/105 = 88.1%)

When invoked in standalone mode:
1. Score each of 35 checks 0-3
2. Total = current Advaita autonomy score (X/105)
3. Save to cohort-appropriate path (cloud: Drive skills root; cli: `~/.openclaw/state/advaita-autonomy-baseline.json`)
4. Output baseline markdown
5. Compare to previous baseline (delta) if file exists
6. **v1.5 ADD (v2.6 channel fix):** Items scoring ≤1 AND stable >2 weeks → auto-create autopilot WO via Leo, dispatch to **#leo-coaches (C0AQ4KB1SA0)** — #leo-auto is BROKEN (confirmed 2026-05-30; C0AKXT2S1T2 returns errors). (was: auto-create Notion sprint row; v1.5 routes via autopilot for fleet consistency)

## v1.2 + v1.3 + v1.4 features preserved verbatim
- Audit-the-Audit gate (forward, grade jump >0.5) — Step 3.5b in v1.5
- Scope Discipline classification (ALIGNED BONUS / NEUTRAL / SCOPE CREEP)
- Severity field per gap (high/medium/low)
- AUTO-FIRE COUNCIL on severity=high
- CLOUD COHORT acknowledgment (now formalized in cohort_routing block)

## Cohort routing block (NEW v1.5)

```yaml
cohort_routing:
  cloud:
    detect: HOSTNAME contains "hyperagent" OR "madison"
    output_path: drive_skills_root
    output_method: SaveFile → PublishFilePublicly → GOOGLEDRIVE_UPLOAD_FROM_URL (parent = 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY)
    desktop_fallback: false
    council_invocation: inline_5_advisor_synthesis (this thread)
    council_artifact_dest: drive_council_skill_folder (1dikjqZvnsWbbvVjNupiCWC-qN3fWfesV)
    restricted_tools: [HIGHLEVEL_*, METAADS_* if has_active_connection=false, browser_cookie3, op_cli]
    restricted_tool_action: dispatch_to_leo_wo via SlackSendMessage(C0AKXT2S1T2, @U0AG6G4BEM9)
    state_path: brain.md cycle section
  cli:
    detect: presence of ~/.openclaw/state/
    output_path: ~/Desktop/audits/
    output_method: write directly
    desktop_fallback: true
    council_invocation: real_council_skill_subprocess (~/.claude/skills/council-skill/run.sh)
    council_artifact_dest: ~/Desktop/audits/council/
    restricted_tools: []
    restricted_tool_action: direct_execution
    state_path: ~/.openclaw/state/<skill>-last-cycle.json
```

## Governance
- Canonical: Drive folder `1ZBvY1JaG9u-PhZhzRDhlQO1koPVRY33l` / SKILL.md
- Skills-root mirror: `self-audit-SKILL-v1.5.md`
- Edit pattern: SaveFile → PublishFilePublicly → GOOGLEDRIVE_UPLOAD_FROM_URL (replace existing or new)
- Web link: https://drive.google.com/drive/folders/1ZBvY1JaG9u-PhZhzRDhlQO1koPVRY33l
- **v1.5 loader contract:** load by `name='SKILL.md' and parent contains '1ZBvY1JaG9u-PhZhzRDhlQO1koPVRY33l'` → sort modifiedTime desc → top 1.

## Version History
- **v1.0 (2026-05-09)** — Initial build. Council v16 4.2/4.0.
- **v1.1 (2026-05-09)** — Advaita 100 Checklist. Council v16 4.24/4.0.
- **v1.2 (2026-05-09)** — Audit-the-Audit gate. Council v16 4.36/4.0.
- **v1.3 (2026-05-09)** — Scope Discipline dimension. Council v16 4.40/4.0.
- **v1.4 (2026-05-14)** — Severity field + AUTO-FIRE COUNCIL on HIGH. Council 4.72/5.
- **v1.5 (2026-05-15)** — Shared 8-dim audit-core rubric (Revenue/Automation/Consolidation NEW). Forces real council invocation. Same-Pattern-Twice escalation. Reverse Audit-the-Audit gate. cohort_routing block. Fleet loader contract. drive_file_id auto-populate. Council v20 4.46/4.0 PASS.

---

> **See also:** `bennett-mode-skill v2.1+`, `batch-overdrive-skill v1.2+`, `business-audit-skill v2+`, `council-skill v20+`, `autopilot-skill v12+`.

## Self-Audit Checklist (used by angie-weekly-audit-skill v8+)

Angie uses this checklist as the SOP rubric when auditing this business area.

1. [ ] Skill was invoked successfully in the last 30 days (or manually reviewed as active)
2. [ ] SKILL.md has valid frontmatter with name, description, version, and drive_file_id
3. [ ] All trigger phrases route correctly to this skill
4. [ ] self-audit-skill state written to ~/.openclaw/state/self-audit-history.jsonl (append) within 24hr of cycle completion — NOT ~/.openclaw/logs/ (that path is wrong; state lives in ~/.openclaw/state/ per Step 8)
5. [ ] Gaps flagged in output include severity (HIGH/MED/LOW) and affected domain
6. [ ] Score < 4.0 cycles flagged in #leo-coaches with "SELF-AUDIT FAIL" tag

## Cron Bindings

None — manually invoked. No scheduled LaunchAgent or cron job owns this skill.
