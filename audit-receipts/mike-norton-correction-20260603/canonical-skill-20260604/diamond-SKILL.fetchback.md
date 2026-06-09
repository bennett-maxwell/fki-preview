---
name: diamond-skill
version: 2.6
drive_file_id: 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT
description: "This skill should be used when verifying any completed deliverable passes quality gates. v2.6 fixes #leo-auto stale channel ref, clarifies T4-T8 mandatory scope, adds T6 failure surfacing, expands trigger phrases and Self-Audit Checklist. Trigger phrases: diamond-skill, run diamond, verify diamond, diamond gate, diamond check, is this diamond, T7 write verification, T8 drive verification, skill-execution claim, proof-receipt check, artifact registry check"
---

# Diamond Gate Skill v2.6 — CANONICAL (last updated 2026-05-30 by Chad)

## Patch History
| Version | Date | Author | Summary |
|---|---|---|---|
| 2.5 | 2026-05-27 | Chad | T8 skill-patch Drive verification added |
| 2.6 | 2026-05-30 | Chad | Audit fixes: #leo-auto→#leo-coaches, T4-T8 mandatory scope clarified in Workflow, T6 failure surfacing in output, trigger phrase expansion, Self-Audit Checklist T4-T8 coverage |

## North Star
Succeeds when a completed deliverable passes 5 independent stress tests with logged evidence — covering root cause, failure modes, execution stack, edge cases, and regression — and has zero known break paths.

---

Category: Quality Assurance

## Purpose

No task is Done until it is Diamond. Diamond means 3 independent stress tests passed with evidence. No self-reported passes. No exceptions.

Any agent runs this skill on their own work — Mack, Ivan-CC, Squirrel, or any other agent. No handoff required. Follow this skill, run the tests, capture evidence, report the result.

## Skill Execution Claim Verification (v2.5 — Bennett permanent-fix directive)

Use this addendum whenever the deliverable includes a claim that a skill was `ran`, `executed`, `completed`, `closed out`, `verified`, or `Diamond`.

A skill-execution claim can be Diamond only when all are true:
1. Canonical Drive loader proof exists: skill frontmatter `name`, `version`, `drive_file_id`, and modifiedTime.
2. The agent extracted mandatory workflow/red-line/final-step requirements from the canonical `SKILL.md`.
3. A required-step ledger exists with every mandatory row marked `executed`, `blocked`, `skipped by explicit rule`, or `not applicable`.
4. Every `executed` row has evidence: Drive file ID, Notion page ID, Slack ts, command output, receipt path, byte count, grep marker, validator output, or equivalent proof.
5. Blocked or skipped rows are named in the final answer and cannot be hidden behind a green/Diamond status.

**Hard rule:** loading, reading, summarizing, or partially applying a skill is not a full skill execution. If the ledger is incomplete, final status is Yellow and wording must be `loaded`, `reviewed`, or `partially applied`.

### Skill-Claim Diamond Tests

When verifying a skill-execution claim, adapt the 3 stress tests as follows:

**Test 1: Required-Step Coverage**
- Compare the required-step ledger against the canonical `SKILL.md`.
- PASS: every mandatory step is represented with a status and proof/blocker.
- FAIL: any required step is missing, inferred, or hidden.

**Test 2: Proof-Receipt Recovery**
- Re-open at least one claimed proof artifact from outside the original tool output.
- PASS: proof is independently reachable and matches the claim.
- FAIL: proof is missing, local-only when Drive/Notion was required, or cannot be reopened.

**Test 3: Claim-Language Boundary**
- Scan the final response/receipt for `ran`, `executed`, `completed`, `closed out`, `verified`, `Diamond`, and equivalent terms.
- PASS: each strong claim maps to proof; partial work uses partial wording.
- FAIL: any strong claim lacks proof from the same run.

## Two Types of Diamond â Do Not Confuse

| Diamond Type | When | Owned By | Source |
|---|---|---|---|
| Diamond Gate (this skill) | After a task is built â verifies it actually works | Any agent, on their own work | diamond-skill v2 |
| Diamond Stress Test (council Step 5.5) | Before execution â stress-tests the PLAN | council-skill v12, Step 5.5 | council-skill SKILL.md |

This skill = post-build QA. Council Step 5.5 = pre-execution plan validation. Both are mandatory. They are not interchangeable.

## Status Ladder

| Status | Meaning |
|---|---|
| Red | Broken. Test failed or task not started. |
| Yellow | Fix attempted. Not all 3 tests passed yet. |
| Green | Task complete. Stress tests not yet run. |
| Diamond | All 3 tests passed with evidence. Fully confirmed. |

## The 3 Stress Tests

Every task needs all 3 adapted to what it actually does.

### Test 1: Adversarial Input

Feed bad/unexpected/invalid input and verify no crash, no silent failure.

- Examples: empty payload, missing fields, malformed JSON, emoji-only input, 10K character blob, Unicode edge cases
- Pass: Handled gracefully â processed or rejected with error log
- Fail: Crash, hang, or silent corruption

SANDBOX adaptation (Squirrel/cloud agents): Submit a deliberately bad API call (wrong field type, missing required param, malformed ID). Verify the integration returns a structured error and Squirrel logs it â not a silent pass or unhandled exception.

### Test 2: Failure Recovery

Force a failure mid-process and verify clean recovery.

CLI agents (Ivan-CC, Mack): Kill the process, mock an API timeout, cut network mid-run, restart dependency service. Pass: recovers within expected time, no messages lost, no duplicates, no partial outputs.

SANDBOX adaptation (Squirrel/cloud agents): Cannot kill processes directly. Instead: (1) Send a valid request to a broken endpoint or with a revoked credential, (2) verify graceful error handling â no partial writes, (3) re-run the task from scratch and confirm idempotent (no duplicate Notion rows, no duplicate Slack messages, no duplicate GitHub commits). Pass: clean error + clean retry. Fail: silent partial write, or duplicate output on retry.

### Test 3: Boundary Condition

Push to the extreme edge of normal operation.

- Examples: concurrent runs, exact timing boundaries, max payload size, rapid re-execution (3x in 30s), simultaneous triggers
- Pass: Idempotent, no race conditions, no off-by-one errors
- Fail: Duplicate output, race condition, state corruption

SANDBOX adaptation (Squirrel/cloud agents): Run the same SANDBOX task 3x in rapid succession. Verify: only 1 result exists (idempotent), or exactly 3 distinct results (intentionally repeated). No phantom duplicates. No silent failures on repeat.

## Workflow

1. Identify what the task actually does (file write, API call, cron, Slack msg, Drive write, GitHub commit, etc.)
2. Classify: CLI or SANDBOX? Pick the right test adaptation above.
3. Run Test 1 (Adversarial Input), capture evidence
4. Run Test 2 (Failure Recovery), capture evidence
5. Run Test 3 (Boundary Condition), capture evidence
6. Run T4 (Edge Case Coverage) — always required unless explicitly scoped out
7. Run T5 (Regression Check) — always required unless explicitly scoped out
8. Run T6 (Artifact Registry Check) — required for any deliverable with a Drive file ID; see T6 section for AUTO-FIX and FAIL handling. Any T6 FAIL must be surfaced in the final output, not silently logged.
9. Run T7 (Persisted-Write Verification) — required for ANY claimed file/skill write
10. Run T8 (Skill Patch Drive Verification) — required when a SKILL.md is written back to Drive
11. All applicable tests pass = Diamond. Any fail = back to Yellow, fix, retest all applicable tests.

**Mandatory vs. Optional scope:**
- T1, T2, T3: always required
- T4, T5: required unless deliverable scope explicitly excludes them (e.g., pure Slack-only or one-shot research with no persistent state)
- T6: required for any deliverable with a Drive file ID; skip only for planning docs and one-shot research
- T7: required for any claimed file write; skip only for Slack/research outputs with no persistent file
- T8: required only when a SKILL.md is written back to Drive
- T4-Council: required only for council deliverables

## Output Format

Diamond Test -- [Task Name] -- [Date]

Test 1: Adversarial Input
What we did: [exact call or action]
Evidence: [paste response or describe observed behavior]
Result: PASS / FAIL

Test 2: Failure Recovery
What we did: [exact call or action]
Evidence: [paste response or describe observed behavior]
Result: PASS / FAIL

Test 3: Boundary Condition
What we did: [exact call or action]
Evidence: [paste response or describe observed behavior]
Result: PASS / FAIL

FINAL STATUS: Diamond / Yellow ([how many passed]/3)

## Rules

- NEVER self-report a pass â evidence required or it did not happen
- NEVER skip a test â if one cannot be run, explain why and mark Yellow
- Any FAIL = task goes back to Yellow, fix, retest all 3
- Diamond can only be claimed after all 3 pass in the same test run
- ANY agent runs their own diamond tests â no handoff to Cody required
- Post Diamond results to #leo-coaches (C0AQ4KB1SA0) when complete — NOTE: #leo-auto (C0AKXT2S1T2) is broken as of 2026-05-30; use #leo-coaches as permanent fallback
- SANDBOX agents: use the SANDBOX adaptations above â do not attempt CLI steps
- **Rule 4 (v2.3, 2026-05-25) T2 FALSE-PASS GUARD:** If T1=PASS AND T2 has a 100% failure pattern (e.g. all message-fetch returns HTTP 400 fleet-wide) then verdict MUST be YELLOW, not DIAMOND, even if T1+T3 pass. T2 100%-fail is a correctness defect that must surface. Cycle scripts MUST: (a) first attempt T2 fall-through to v2 endpoint `services.leadconnectorhq.com/conversations/messages/{id}` with `Version: 2021-04-15` header; (b) if still 100% fail, mark verdict YELLOW + log to Sprint Board as defect. Triggered by self-audit G2+G6 (2026-05-25). Reference: `~/Desktop/audit-2026-05-25/self-audit.json`.

## When to Invoke

- After any Sprint Board row is created and work begins â run Diamond before claiming done
- After any skill update (SKILL.md written to Drive) â Diamond the write
- After any cron/automation deployment â Diamond the live system
- After any integration setup (OAuth, Composio, GHL webhook) â Diamond the connection
- Do NOT diamond planning docs, Slack messages, or one-shot research outputs â only systems and persistent changes

## T4: Edge Case Coverage
What happens with bad input, missing data, empty responses, or partial failures? The fix must handle these without crashing or silently failing.

## T5: Regression Check
Does this fix break anything that was already working? Test at least 2 adjacent functions/workflows that touch the same code path.

## T6: Artifact Registry Check (v2.2 — 2026-05-21)
Every Diamond-qualified deliverable with a Drive file ID must have a corresponding row in the FKI AI Artifact Registry — Universal Notion DB.

- **DB:** https://www.notion.so/11944015a0b5468587dd66dc148ac606 (collection `2501fb25-637e-44fb-a4ff-2235e04863c3`)
- **Check:** Search Notion for `drive_file_id = <artifact_drive_id>` in the universal DB.
- **PASS:** Row found with Drive File ID + Agent + Project + Date populated.
- **AUTO-FIX (not a fail):** No row found → call `notion-artifact-skill REAL-TIME MODE` to register it on the spot. Mark T6 PASS after successful registration.
- **FAIL:** Row not found AND notion-artifact-skill registration failed after 3 retries — log to `~/.openclaw/logs/artifact-registry-failures.jsonl` AND surface explicitly in the final Diamond output (T6: FAIL — registry write failed after 3 retries, logged). A T6 FAIL downgrades final status to Yellow. Do NOT silently log and claim Diamond.
- **Scope:** Applies ONLY to deliverables with a Drive File ID (Blueprint HTML, podcast, report, skill file, handoff doc). Skip for planning docs, Slack messages, one-shot research outputs.

## T7: Persisted-Write Verification (v2.4 — 2026-05-26, Bennett directive)

**MANDATORY for any deliverable that claims a file/skill was written or edited.** Tool-reported "updated successfully" is NOT proof of a write — on Mack the Edit/Write tools were observed reporting success while the file on disk was UNCHANGED (mtime, byte count, and grep all proved zero writes). This is a likely fleet-wide root cause of false "done" / false "skill patched to vX" claims.

**The check (run for EVERY claimed write):**
1. `wc -c <file>` — byte count changed vs. pre-edit? (capture before + after)
2. `grep -c "<unique marker from the new content>" <file>` — returns ≥1?
3. `stat -f %m <file>` (macOS) — mtime newer than edit start?
4. If a Drive canonical exists: verify the synced copy byte-count matches local.

**PASS:** all markers present, bytes grew/changed, mtime fresh, Drive copy matches.
**FAIL (auto-Yellow):** tool said success but bytes/grep/mtime unchanged → the write did NOT persist. Re-apply via Bash (`python3` string-replace or `printf`), then re-verify. NEVER claim Diamond on Edit/Write tool success alone.

**Scope:** every file write, skill patch, config edit, dashboard build. Skip only for pure Slack/research outputs (no persistent file).

## T8: Skill Patch Drive Verification (v2.5 — 2026-05-27)

**MANDATORY when a `SKILL.md` is written back to Drive.** T7 proves the local file changed; T8 proves the Drive canonical changed.

**The check:**
1. Capture pre-edit local byte count and version.
2. Apply the patch locally.
3. Verify local byte count changed and unique marker grep returns at least 1.
4. Upload/replace the canonical Drive file.
5. Download the same Drive file ID to a fresh path.
6. Verify downloaded byte count, frontmatter version, and unique marker match the patched local file.

**PASS:** local patched file and fresh Drive download both contain the new version and unique marker.
**FAIL (auto-Yellow):** upload output exists but fresh Drive download lacks the marker/version, byte count is zero, or the file ID changed unexpectedly.

## T4-Council — Gate Lifecycle Audit (council deliverables only, v2.3 2026-05-25)

**T4 — Gate Lifecycle Audit (council deliverables only)**
Check: every BENNETT-classified gate in the council artifact has (1) gate_id populated, (2) same_gate_count fetched from council-log.json, (3) permanent_fix_deadline set.
T4 PASS = all fields present on all BENNETT gates.
T4 FAIL = any gate missing fields → flag INCOMPLETE_GATE_TEMPLATE.
T4 is SKIPPED (mark n/a) for non-council Diamond verification (broker scripts, dashboards, etc.)

## Self-Audit Checklist (used by angie-weekly-audit-skill v8+)

Angie uses this checklist as the SOP rubric when auditing this business area.

1. [ ] Skill was invoked successfully in the last 30 days (or manually reviewed as active)
2. [ ] SKILL.md has valid frontmatter with name, description, version, and drive_file_id
3. [ ] All trigger phrases route correctly to this skill (including T7/T8/skill-execution/proof-receipt variants added in v2.6)
4. [ ] Skill-execution claims have canonical Drive loader proof
5. [ ] Required-step ledger exists for every claimed skill execution
6. [ ] Strong claim language maps to proof from the same run
7. [ ] Skill patches pass T7 local write verification and T8 Drive verification
8. [ ] Partial skill work remains Yellow and is described as partial, not complete
9. [ ] T4 (Edge Case) and T5 (Regression) were run or explicitly scoped out with documented reason
10. [ ] T6 (Artifact Registry) failures were surfaced in the final output, not silently logged
11. [ ] T4-Council gate lifecycle audit was run (or marked n/a) for any council deliverable
12. [ ] #leo-coaches (C0AQ4KB1SA0) was used for result posting — NOT the deprecated #leo-auto channel
13. [ ] Workflow mandatory-vs-optional T4-T8 scope table was followed; no tests skipped without documented reason

## Cron Bindings

None — manually invoked. No scheduled LaunchAgent or cron job owns this skill.
