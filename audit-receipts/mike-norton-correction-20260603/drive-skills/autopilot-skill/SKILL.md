---
name: autopilot-skill
description: "Single-cycle autonomous execution. Each invocation = one complete cycle. External scheduler (Cowork scheduled-tasks, cron */15 * * * *) fires each cycle — no sleep/loop needed inside this skill. NEVER ask Bennett questions. NEVER fabricate data. v12 adds deep-work-mode pre-flight + LEO ALLOCATION FLIPPED enforcement. v13 — gatekeeper-skill wired as mandatory Step 0.3 (Bennett directive 2026-06-03). v13.1 — Diamond T1/T2/T4 fixes: gatekeeper unavailable/unexpected-return handling, #leo-auto→#leo-coaches, EXEMPT trust documented, gatekeeper-skill added to deps."
drive_file_id: 10KBx34OrzdlX0_RN9x8zqNvQEprLdQow
version: 13.1
architecture: scheduled-task
last_updated: 2026-06-03
deps:
  - name: diy-skill
    fileId: 19mQxNIPy-viPJYfd89QTLrpX73q_Vo8M
  - name: strike-skill
    fileId: 1mBRI0RKEuuvLF5Oh3Gdrl-BLhGrsZhix
  - name: diamond-skill
    fileId: 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT
  - name: machines-skill
    fileId: 1FQ6c_xnxPSEsVPRQ7mxaHpwyqHxBqmxk
  - name: tools-skill
    fileId: 1WzuzXJJT5Pei5QpVmH0H9_QMHp3p0Wzd
  - name: handoff-skill
    fileId: 11HJUvXAmWscPRZin3e2Zezfa0JuEYEmq
  - name: council-skill
    fileId: 18edfLllHikArUABu7l_feBxFWfiLncAY
  - name: closeout-skill
    fileId: 1IfdB8YM-F9GzPHka44uE199NqPFAI4gB
  - name: troubleshoot-skill
    fileId: 1I13dA9Tcn-N0ETowd6dhZG46F5Wu3krK
  - name: slack-comms-skill
    fileId: 11UEN5S1sCiGSLZeeaxKng8hUuk_SJS53
  - name: memory-skill
    fileId: 11N3WxEHenqDoidLawqfh1m-AfeU0G8Pu
  - name: deep-work-mode-skill
    fileId: 10-r0La0so_OGaWGoVWI-ZBRBYmL4mYex (v12 addition — to be set at upload time)
  - name: self-audit-skill
    fileId: 1xCx0k6lj1y1_ni77ff0j8rrYAw2r8BMM (referenced by v12 SELF-AUDIT+BUSINESS-AUDIT FIRST rule)
  - name: business-audit-skill
    fileId: 1ChehVt8OMh7_L5Y3tZGioS9ynx4IRp7y (referenced by v12 SELF-AUDIT+BUSINESS-AUDIT FIRST rule)
  - name: gatekeeper-skill
    fileId: 1CMnKR6t6d6iUIP4P1X3CDxmjxXAMOh53
    note: mandatory Step 0.3 pre-flight — added v13
---

## Dependencies
Preload in parallel via Drive fetch:
- diy-skill (fileId: 19mQxNIPy-viPJYfd89QTLrpX73q_Vo8M)
- strike-skill (fileId: 1mBRI0RKEuuvLF5Oh3Gdrl-BLhGrsZhix)
- diamond-skill (fileId: 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT)
- machines-skill (fileId: 1FQ6c_xnxPSEsVPRQ7mxaHpwyqHxBqmxk)
- tools-skill (fileId: 1WzuzXJJT5Pei5QpVmH0H9_QMHp3p0Wzd)
- handoff-skill (fileId: 11HJUvXAmWscPRZin3e2Zezfa0JuEYEmq)
- council-skill (fileId: 18edfLllHikArUABu7l_feBxFWfiLncAY)
- closeout-skill (fileId: 1IfdB8YM-F9GzPHka44uE199NqPFAI4gB)
- troubleshoot-skill (fileId: 1I13dA9Tcn-N0ETowd6dhZG46F5Wu3krK)
- slack-comms-skill (fileId: 11UEN5S1sCiGSLZeeaxKng8hUuk_SJS53)
- memory-skill (fileId: 11N3WxEHenqDoidLawqfh1m-AfeU0G8Pu)
- **(v12) deep-work-mode-skill** — pre-flight check before EXECUTE Step 3 (and before closeout/handoff)
- **(v12) self-audit-skill + business-audit-skill** — parallel audits before Step 3.5 VERIFY for content tasks
Execute their workflows in full when referenced below. All canonical files live in Google Drive folder `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY`.

## North Star
Succeeds when every dispatched task is confirmed complete (Notion sprint row = Diamond OR #leo-coaches (C0AQ4KB1SA0) broadcast received) — not just launched — by checking back at +60s, +120s, +300s after dispatch, then → Execute troubleshoot-skill if no signal by 300s.

---

## Architecture Note (v9 — Refactor Audit, preserved)
**The loop is EXTERNAL.** Cowork's scheduled-tasks MCP fires a new session every 15 minutes.
Each invocation of this skill executes exactly ONE cycle, then exits.
Do NOT include "wait 15 min and repeat" logic — the scheduler handles that.

> v9 changelog (2026-05-09): Refactor Audit Phase A.
> v11 changelog (2026-05-10): Auto-default-Option-A rule after 24h Bennett silence.
> **v12 changelog (2026-05-14): deep-work-mode-skill pre-flight check + LEO ALLOCATION FLIPPED enforcement in dispatch logic + SELF-AUDIT+BUSINESS-AUDIT FIRST hook in Step 3.5 + CLOUD-MODE STATE PATHS migration.**
> **v13 changelog (2026-06-03): gatekeeper-skill wired as mandatory Step 0.3 (Bennett directive 2026-06-03)**

# Autopilot Skill v13.1

> ⚠️ **DO NOT DOUBLE-INVOKE**
> autopilot-skill is a **building block** — already invoked inside ship-it-skill (Step 2), overdrive-skill (autopilot batches of 10), and full-cycle-skill (when built).
>
> Chaining autopilot-skill AFTER ship-it / overdrive = double-execute the queue. Don't.
>
> **Standalone autopilot is valid** — when the external Cowork scheduled-task cron fires it directly, OR when you explicitly want a single cycle without the full ship-it/overdrive wrapper.

## Trigger
- Cowork scheduled-task fires (cron: `*/15 * * * *`)
- "go on autopilot" / "I'm leaving" / "run autonomously" / "keep working while I'm gone"
- Any indication Bennett is unavailable for 30+ minutes

## BROWSER TOOL HIERARCHY (mandatory)
For any web/browser task: **Chrome MCP first** (`mcp__Claude_in_Chrome__*`). Lightweight, DOM-aware.
Fall back to computer-use ONLY for native desktop control (Terminal, system apps, non-browser GUIs).

## HARD RULES
1. **NEVER ask Bennett a question while in autopilot mode.** Make the call yourself via → Execute council-skill or skip.
2. **NEVER wait for Leo or any agent to respond.** If no response in 5 min, DIY and → Execute troubleshoot-skill in parallel.
3. **On any blocker → Execute BLOCKER LOOP (see Step 4).** Do not surface to Bennett until loop exhausted.
4. **Update Notion tracker after every completed item.**
5. **Post status to #leo-coaches (C0AQ4KB1SA0) every cycle** via → Execute slack-comms-skill. Compact 3-line format (see REPORT step).
6. **NEVER stop because one task is blocked.** Skip → next task → return later.
7. **END-OF-TASK: No open items allowed.** → Execute council-skill on every open item before closing.
8. **COUNCIL BEFORE ANY BENNETT — ZERO EXCEPTIONS.**
9. **(v12) LEO ALLOCATION FLIPPED — pre-flight check before ANY Slack WO to #leo-coaches (C0AQ4KB1SA0).** Default = Hyperagent cloud-native execution. Leo WO is exception. See Step 3 dispatch logic.
10. **(v12) SELF-AUDIT+BUSINESS-AUDIT FIRST — for content-generating tasks.** Run both audits in parallel before Step 3.5 VERIFY. Audit JSON IDs embed in Three-Line Proof. See Step 3.5.
11. **(v12) NO-HARDCODED-ROW-IDS — Notion rows looked up live by title.** Never embed 36-char UUIDs in this skill body.
12. **(v12) CLOUD-MODE STATE PATHS — state files in Drive, mirrored to local on CLI.** See state file references throughout.

### Auto-Default-Option-A Rule (v11, preserved)

When autopilot posts an Option A/B/C ping to #leo-coaches (C0AQ4KB1SA0) requesting Bennett's pick, start a 24h timer. If Bennett has not replied at 24h:
- If the option is tagged IRREVERSIBLE (biometric, financial >$1K, legal, identity) → keep waiting, do NOT auto-default
- Otherwise → auto-execute Option A, post receipt to #leo-coaches (C0AQ4KB1SA0) "AUTO-DEFAULT [HH:MM MDT] — Option A executed after 24h Bennett silence per autopilot-skill v11 rule"
- Log to Drive `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/autopilot-skill/state/auto-default-options.jsonl` (v12: was `~/.openclaw/logs/`)

This unblocks CMO-style 60-item-leverage gates. Bennett retains override by replying "ROLLBACK" within 24h.

## QUESTION GATE (mandatory before ANY message to Bennett)
[v11 preserved]
1. List which of the 8 DIY steps you tried + results
2. List which machines from machines-skill you attempted
3. List which tools from tools-skill you attempted
4. Confirm you ran Strike Protocol through Strike 3
5. Confirm you ran BLOCKER LOOP (Step 4) for each open item
6. Confirm council-skill was run on each specific blocker AND produced no actionable plan
7. **(v12)** Confirm self-audit-skill + business-audit-skill both ran on the question

Cannot show all 7? DELETE the draft. Go back to DIY step 1.

---

## SINGLE-CYCLE EXECUTION (run once per invocation)

### Step -1 — DIAMOND-COMPLETE GATE (BLOCKING — runs FIRST)

**(v12 CLOUD-MODE)** Read `autopilot-state.json` from Drive `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/autopilot-skill/state/autopilot-state.json` (create if missing with default `{"open_diamond_items": [], "session_id": null, "started_at": null}`). CLI agents (Leo/Ivan/Mack) mirror to `~/.openclaw/state/autopilot-state.json` on boot.

**If `open_diamond_items` is an empty list AND `session_id` is non-null:**
- Bennett triggered "autopilot until Diamond verified" and we hit the goal.
- **(v12)** → Execute deep-work-mode-skill pre-flight (Gate 1 + Gate 2). If REFUSED → continue working, do NOT closeout.
- If pre-flight PASSES: → Execute closeout-skill in full.
- After closeout success: reset state file to defaults (`session_id: null`).
- **EXIT.** No further cycles until Bennett retriggers.

**If `session_id` is null:**
- Routine cycle, not autopilot-until-Diamond. Proceed to Step 0.

**If `open_diamond_items` is non-empty:**
- Items still need verification. Proceed to Step 0 with priority bias toward closing these.

### Step 0 — OVERLAP GUARD
→ Execute slack-comms-skill to read last 5 messages from #leo-coaches (C0AQ4KB1SA0).
If an AUTOPILOT message exists from within the last 10 minutes: **EXIT immediately**.

### Step 0.3 — GATEKEEPER PRE-FLIGHT (MANDATORY)
invoke Skill("gatekeeper-skill"). 
- If gatekeeper returns BLOCKED → EXIT cycle immediately, post blocker reason to #leo-coaches (C0AQ4KB1SA0).
- If gatekeeper returns EXEMPT (98% registry hit) → log exempt_task to cycle state, continue.
- If gatekeeper returns PASS → continue to Step 0.5.
- If gatekeeper returns any other value (ERROR, TIMEOUT, UNKNOWN, or malformed) → treat as BLOCKED, EXIT cycle, post to #leo-coaches (C0AQ4KB1SA0) with value received.
- If Skill("gatekeeper-skill") invocation fails entirely (Drive fetch error, skill missing, tool error) → EXIT cycle, post "GATEKEEPER_UNAVAILABLE" to #leo-coaches (C0AQ4KB1SA0). Do NOT continue without a gate check.
Gatekeeper MUST complete before any execution work. Non-negotiable.
Note: EXEMPT is fully trusted from gatekeeper's 98% registry — no local override list exists. If you need a task to always gate regardless of registry, add it to gatekeeper-skill's non_exempt_always_gatekeeper list directly.

### Step 0.5 — SYSTEM HEALTH GATE (Ivan only — runs every cycle, CLI-DIRECT)
Kill duplicate chroma-mcp processes:
```bash
ssh openclaw@100.103.51.12 "ps aux | grep chroma-mcp | grep -v grep | awk '{print \\\$2}' | sort -n | tail -n +3 | xargs kill 2>/dev/null; true" 2>/dev/null
```
Keeps the oldest instance. Safe when count ≤2 (no-op). Backstop: `com.openclaw.chroma-cleanup` LaunchAgent runs every 15min on Ivan.

### Step 0.7 — SUPPRESSION FILTER (every cycle, fast)
**(v12 CLOUD-MODE)** Load master suppression list from Drive `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/autopilot-skill/state/master-suppression-list.yaml` (was `~/.openclaw/master-suppression-list.yaml`).

Step 1 SCAN candidates get filtered before Step 2 TRIAGE.

### Step 1 — SCAN (30 seconds)
Read current task list. Sources:
- → Execute slack-comms-skill to read last 10 messages from #leo-coaches (C0AQ4KB1SA0)
- Memory file `/sessions/*/mnt/.auto-memory/MEMORY.md` (if exists)
- Knowledge of open items from previous cycle's REPORT

**(v12 NO-HARDCODED-ROW-IDS)** When pulling Notion sprint board rows, use `NOTION_QUERY_DATABASE` filter (`Status` ∈ {🔴 Red, 🟡 Yellow}) — do NOT hardcode page IDs.

Identify all Red/Yellow status items.

### Step 2 — TRIAGE (pick ONE task)
Priority order:
1. Bennett explicitly asked for it (highest)
2. Unblocks other work
3. Can complete alone without any human (DIY)
4. Revenue-generating (ads, cold email, pipeline)

Skip: anything requiring Bennett physically present.
Skip: anything actively being worked by Leo/Ivan right now.

### Step 3 — EXECUTE (bulk of cycle, max 8 minutes)

**(v12 deep-work plan-then-execute gate)** Before dispatching ≥4 sub-tasks in a single round, → Execute deep-work-mode-skill Gate 3. Requires plan-in-Drive + council pre-flight, else REFUSED.

**(v12 LEO ALLOCATION FLIPPED dispatch logic — pre-flight check for ANY Slack WO):**

Before posting any WO to #leo-coaches (C0AQ4KB1SA0), run this check:

```
Does this STRICTLY need iMac filesystem / CLI / Browser-Use / OAuth-restricted-tool?

STRICTLY NEEDS LEO:
- Filesystem writes outside Drive (~/.openclaw/, ~/.claude/, ~/Desktop/)
- Meta Ads API (METAADS Composio has_active_connection: false in cloud)
- GHL/HighLevel API (SESSION RESTRICTED in cloud)
- Apple Notes / Reminders / iMessage
- browser_cookie3 (decrypt user's Chrome cookies)
- op CLI (1Password injection)
- macOS-only tools (Keychain, NotificationCenter, Quick Look)

DOES NOT NEED LEO (execute Hyperagent native):
- Notion writes (NOTION_*)
- Drive uploads (GOOGLEDRIVE_*)
- Gmail sends (GMAIL_*)
- Slack posts/reads (SLACK_*)
- GitHub commits (GITHUB_*)
- QuickBooks pulls (QUICKBOOKS_*)
- Generic web research (ExaSearch, WebFetch)
- Composio integrations marked has_active_connection: true
- Image/video/audio generation (GenerateImage, GenerateVideo, GenerateAudio)
- Webpage/slides publishing (PublishWebpage, PublishSlides)
```

If task fits DOES NOT NEED LEO → execute via ExecuteIntegration directly. Do NOT post Slack WO.
If task fits STRICTLY NEEDS LEO → post one focused WO via slack-comms-skill, move on.

Goal: ≤1 Leo WO per cycle average (was 5+ in Thread 7 pre-v12).

If item needs data: → Execute diy-skill (web search, Drive, Notion, Slack history).
If item needs a tool: → Execute machines-skill to identify which machine has it.

### Step 3.5 — VERIFY (on every "done" claim)

**(v12 SELF-AUDIT+BUSINESS-AUDIT FIRST — for content tasks)**

If the task generated marketing / sales / content output (email, LP, post, ad copy, pitch deck, anything customer-facing):
1. Fire `self-audit-skill` + `business-audit-skill` in parallel BEFORE the 3-check VERIFY.
2. Both audit JSON IDs (Drive) must embed in Three-Line Proof:
   - SOURCE = `audit_self=<drive_id>;audit_business=<drive_id>` + BIL section anchor + brand-guide skill ID
   - CLAIM = three-pillar tags present + audit verdict ≥ threshold
   - PROOF = pre-publish review by → Execute caveman-skill against jargon list

If either audit fails threshold → task is 🟡 not ✅, surface in REPORT for next cycle.

**Standard 3-check VERIFY (preserved from v11):**

**Check 1 — Source Lock**
Did I use the PRIMARY source? (FDD PDF in Drive, GHL API, Convex DB — not memory or web snippets)
If secondary source used → verify against primary.

**Check 2 — Receipt Required**
For delegated tasks: did the delegate actually execute?
- Slack confirmation from delegate
- File exists at expected location
- Screenshot or API response
"I sent the message" ≠ "it's done." No receipt = not done.

**Check 3 — Three-Line Proof**
For every data point reported as done, state:
- SOURCE: [where exactly — file ID, page number, API endpoint, audit JSON IDs (v12)]
- CLAIM: [specific number or fact + audit verdict]
- PROOF: [how to verify independently]

If any check fails → task is 🟡 not ✅. → Execute diamond-skill on every claimed-done task before marking 3/3.

### Step 3.6 — STATE FILE UPDATE (after VERIFY)
**(v12 CLOUD-MODE)** After Step 3.5 marks a task done (3/3 Diamond), append/remove from `open_diamond_items` in Drive `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY/autopilot-skill/state/autopilot-state.json`.

### Step 4 — BLOCKER LOOP (mandatory on ANY blocker)
[v11 BLOCKER LOOP preserved verbatim — Level 1 troubleshoot → Level 2 council → Level 3 strike → Level 4 BENNETT gate (only after Step 4.0 council audit PASS per council v19+)]

### Step 5 — OPEN ITEMS SWEEP (before REPORT — mandatory)
[v11 preserved.]

**(v12)** Set `theme_exhausted` boolean for deep-work-mode-skill Gate 1. True if all attempted items are 3/3 Diamond OR genuine BENNETT gates with no DIY path remaining.

### Step 6 — REPORT (last action before exit)
→ Execute slack-comms-skill to post #leo-coaches (C0AQ4KB1SA0) in compact format (v12 via notion-compact-skill convention):

```
AUTOPILOT [HH:MM MDT] — Cycle N
✅ <verb+object>;council=<verdict>;sla=<status>;leo_wo_count=<N v12>
⏭ <next-task-headline>
```

If nothing was actionable:
```
AUTOPILOT [HH:MM MDT] — Cycle N
⚠️ No unblocked tasks. Monitoring.
⏭ Will rescan in 15 min.
```

Update Notion tracker (compact format per v12). → Execute memory-skill if any cross-cutting state changed.

**EXIT.** Scheduler will fire next cycle in 15 minutes.

---

## EXIT CONDITIONS (for interactive/manual autopilot sessions only)
- Bennett sends a message → switch to interactive mode
- All tasks complete + theme_exhausted=true → → Execute closeout-skill (after deep-work-mode-skill pre-flight)
- Default timeout: 3 hours from activation
- Cost exceeds $10 in one session → post warning, reduce scope (v12 — but still subject to deep-work 45-min floor)
- 4 consecutive cycles with zero progress → escalate to Bennett (after council-skill audit)

## MANDATORY CLOSEOUT (interactive sessions only)
When interactive autopilot ends:
1. **(v12)** → Execute deep-work-mode-skill Gate 1 + Gate 2 pre-flight. If REFUSED → keep working.
2. → Execute closeout-skill as final action.

## Mandatory Read Before Dashboard Work
Dashboard Ownership Rule (Council v8): https://www.notion.so/350cf5514fd38145a0bbd6fd840e0fbe
Any autopilot cycle involving dashboard work MUST read this rule first.

## WHAT AUTOPILOT DOES NOT DO
- Does not make irreversible decisions (delete data, send external emails, push to production)
- Does not modify SOUL.md or any Red Line files
- Does not spend money without revenue-skill budget check
- Does not contact anyone outside FKI

## Red Lines
- NEVER ask Bennett a question while in autopilot mode (HARD RULE 1)
- NEVER skip the BLOCKER LOOP before classifying anything as a BENNETT gate
- NEVER inline content from another skill — reference via Dependencies block + `→ Execute <skill>`
- NEVER hard-code Slack channel IDs in body — route via slack-comms-skill
- NEVER auto-default an IRREVERSIBLE-tagged Option ping (v11, 2026-05-10)
- **(v12) NEVER post a Slack WO to Leo without passing the LEO ALLOCATION FLIPPED pre-flight check**
- **(v12) NEVER ship content output without self-audit + business-audit JSON IDs in the Three-Line Proof**
- **(v12) NEVER hardcode Notion row UUIDs in this skill body** — look up by title at execution time
- **(v12) NEVER reference local-disk state paths exclusively** — always cite Drive canonical + local mirror

## Changelog
- **v13.1 (2026-06-03):** Diamond T1/T2/T4 fixes — gatekeeper unavailable/unexpected-return handling, #leo-auto→#leo-coaches, EXEMPT trust documented, gatekeeper-skill added to deps.
- **v13 (2026-06-03):** gatekeeper-skill wired as mandatory Step 0.3 (Bennett directive 2026-06-03). BLOCKED → EXIT + #leo-coaches (C0AQ4KB1SA0) post. EXEMPT (98% registry hit) → log + continue. PASS → proceed to Step 0.5.
- **v12 (2026-05-14):** deep-work-mode-skill pre-flight (Gate 1+2 before closeout, Gate 3 before ≥4 sub-task dispatch). LEO ALLOCATION FLIPPED enforcement in Step 3 dispatch. SELF-AUDIT+BUSINESS-AUDIT FIRST hook in Step 3.5 for content tasks. CLOUD-MODE STATE PATHS migration (all state in Drive, CLI mirrors). NO-HARDCODED-ROW-IDS in Step 1. Compact REPORT format.
- **v11 (2026-05-10):** Auto-default-Option-A rule.
- **v9 (2026-05-09):** Refactor Audit Phase A.

> **See also:** `bennett-mode-skill` v2.2+ invokes this skill. `deep-work-mode-skill` v1+ is mandatory pre-flight.
