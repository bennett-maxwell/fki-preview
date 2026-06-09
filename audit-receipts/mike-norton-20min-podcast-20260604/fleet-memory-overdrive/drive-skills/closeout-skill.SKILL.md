---
name: closeout-skill
drive_file_id: 1udXAN7CVGspKw3OIEfSdz9ZZpT_6BuGy
description: >
  Closes out the current work thread with a Diamond-certified summary.
  TRIGGER: "close out", "close this thread", "wrap up", "end of thread".
  DO NOT TRIGGER for: mid-session status checks.
version: 18
deps:
  - name: diamond-skill
    fileId: 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT
  - name: memory-skill
    fileId: 11N3WxEHenqDoidLawqfh1m-AfeU0G8Pu
  - name: fleet-memory-skill
    fileId: 1kE1web8T1HKD-M7u8OirfxhGPduOU002
  - name: handoff-skill
    fileId: 11HJUvXAmWscPRZin3e2Zezfa0JuEYEmq
  - name: recap-skill
    fileId: 1e9nw03yKQ9tjD4k3zEBAhQsEnH0qZWe6
  - name: council-skill
    fileId: 18edfLllHikArUABu7l_feBxFWfiLncAY
  - name: troubleshoot-skill
    fileId: 1I13dA9Tcn-N0ETowd6dhZG46F5Wu3krK
  - name: strike-skill
    fileId: 1mBRI0RKEuuvLF5Oh3Gdrl-BLhGrsZhix
---

## Dependencies
Preload in parallel via mcp__claude_ai_Google_Drive__read_file_content:
- diamond-skill (fileId: 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT)
- memory-skill (fileId: 11N3WxEHenqDoidLawqfh1m-AfeU0G8Pu)
- handoff-skill (fileId: 11HJUvXAmWscPRZin3e2Zezfa0JuEYEmq)
- recap-skill (fileId: 1e9nw03yKQ9tjD4k3zEBAhQsEnH0qZWe6)
- council-skill (fileId: 18edfLllHikArUABu7l_feBxFWfiLncAY)
- troubleshoot-skill (fileId: 1I13dA9Tcn-N0ETowd6dhZG46F5Wu3krK)
- strike-skill (fileId: 1mBRI0RKEuuvLF5Oh3Gdrl-BLhGrsZhix)
Execute their workflows in full when referenced below.

# Close Thread Skill v16

## North Star
Succeeds when > Closes out the current work thread with a Diamond-certified summary.


> ⚠️ **TERMINAL STEP — NEVER CHAIN ANYTHING AFTER**
> closeout-skill is the **last** step in any autonomy loop. It writes the final state file, posts the final receipt, and closes the thread.
>
> Already invoked as the final step inside ship-it-skill (Step 6), overdrive-skill (Step 7), full-cycle-skill (when built). **Never call closeout-skill twice on the same cycle** — second invocation rewrites state file with stale data and corrupts resume logic.
>
> If you want to keep working after a closeout, that's a NEW cycle — start fresh with ship-it / overdrive / autopilot. Don't chain extra-push or council AFTER closeout.
>
> Patched 2026-05-09 per Council v16 verdict 4.24/4.0 — same double-stack rule shipped to ship-it/overdrive/autopilot.


> v18 changelog (2026-06-04): NO-EARLY-STOP CLOSEOUT BLOCKER. Closeout cannot finalize when Yellow/partial/AI OPEN contains a safe AI-owned next action. The agent must execute the next reversible no-send/no-delete/no-secret blocker-clearing action, fetch back proof, and rerun the relevant verifier before closeout. Only true human/protected/platform blockers or bounded continuation receipts may remain. Also corrects this root-folder SKILL.md frontmatter drive_file_id to the canonical file in the closeout-skill folder.
> v16 changelog (2026-05-14): Step 2.5 added — mandatory Notion Project Sub-Page update (BLOCKING). Sprint board row (Step 2) captures status; Step 2.5 captures the full session artifact record as a sub-page linked to that row. Root cause: session artifacts (Drive IDs, proof URLs, carry-forward) were not persisted in Notion, making retrospective review impossible.
> v15 changelog (2026-05-13): blocker-verify-skill gate added before Step 6.6 Bennett-gate classification. Before classifying any open item as a BENNETT gate, blocker-verify-skill must be executed. Only items with status=verified_down or human_only may be escalated.
> v14 changelog (2026-05-13): Step 2 is now a **BLOCKING gate** with mandatory Notion write + verified page ID receipt. Previously soft ("Find or create Notion page") — root cause of 6 live projects with zero Notion pages this session. Closeout CANNOT complete without a confirmed Notion page ID. Red Line added. Patched by Mack per Bennett directive #leo-coaches 2026-05-13 14:40.
> v13 changelog (2026-05-09): Step 0 now writes `~/.openclaw/state/recap-cycle-trigger.txt` before invoking recap-skill, wiring v3.5's end-of-thread council-execute loop. Without this, v3.5's auto-loop never fires from closeout (Skill() can't pass CLI args).
> v11 changelog (2026-05-09): Refactored per Skill Reference Refactor Audit. Inlined memory-skill content removed from Step 5. Step 1 Diamond reference + Step 4 Drive-architecture prose replaced with `→ Execute` references. Dependency block hoisted to top of body.
> v10 changelog (2026-05-04): Added Step 6.6 "Open Item DIY Resolution Loop (BLOCKING)" + Red Line forbidding lazy "leftover" listings.

Category: Session Management

## Purpose
Verified close-out of the current work session. Everything logged and Diamond-stress-tested before thread ends. Proof links required.

## Trigger Phrases
- "close out" / "close this thread" / "wrap up" / "end of thread"

## Workflow

### Step -1: Sync Verification Gate (BLOCKING — runs FIRST)

Before any closeout work begins, verify local copies of the chained skills (see ## Dependencies above) match Drive canonical. Drive Desktop sync is unreliable; this gate catches drift.

**Two-tier check (PRIMARY: Drive MCP, FALLBACK: gog CLI). Use whichever is available.**

#### PRIMARY — Drive MCP (works on every agent: Ivan, Mack, Leo, Tiffany)

For each chained skill in the Dependencies block, call `mcp__claude_ai_Google_Drive__get_file_metadata` and compare `modifiedTime` against local file mtime. If drift > 1h → force-pull via `read_file_content` and Write to local `~/.claude/skills/<name>/SKILL.md`.

#### FALLBACK — gog CLI (Ivan only, requires GOG_KEYRING_PASSWORD)

```bash
PW=$(grep '^export GOG_KEYRING_PASSWORD=' ~/.zshrc | sed 's/^export GOG_KEYRING_PASSWORD=//' | tr -d '"' | tr -d "'")
GOG_KEYRING_PASSWORD="$PW" gog -a bennett@franchiseki.com download <drive_file_id> --out=~/.claude/skills/<skill-name>/SKILL.md
```

#### Environment-aware behavior

- **Ivan (hostname starts with `Ivan` or path `/Users/openclaw/`)**: full local-vs-Drive mtime check. Force-pull writes to local SKILL.md.
- **Mack (hostname `Macbook` or path `/Users/temp/`)**: skip local stat (no local skills file); confirm Drive MCP read works. Treat any successful MCP fetch as PASS.
- **Leo (cloud)**: Drive MCP only — confirm MCP fetch returns valid frontmatter.

If ALL tiers fail OR a chained skill is stale and force-pull does not recover it, **AUTO-CHAIN** instead of aborting silently:

1. → Execute troubleshoot-skill with the failure context (which skill, drift duration, last-attempted recovery).
2. troubleshoot-skill's Block 6 will name a strike level and auto-chain to strike-skill (Level 2 = council-skill).
3. → Execute council-skill — returns ranked fixes with 0/N Bennett gates.
4. Execute the council's #1 fix via diy-skill.
5. Diamond-verify and resume closeout.

This auto-chain rule applies to **every BLOCKING gate in this skill** (Step -1, Step 4 PATCH gate, Step 4.5 Diamond gate). No human re-trigger needed — detection IS the trigger.

### Phase-State Schema Validator (NEW 2026-05-11)

Runs immediately before Step 0. **Non-blocking** — failures promote to recap slot 1 rather than halting closeout.

**Inputs:** `~/Desktop/<project>-<date>/phase-state.json` (if a cycle artifact exists for this thread). Skip silently if no artifact found.

**Required keys:**
- `project_slug` (string, non-empty)
- `current_phase` (integer, 0-13 inclusive)
- `phase_N_receipt` (one per completed phase, each must be an existing path on disk)
- `shipped_items_cumulative` (array, non-empty)
- For each item in `shipped_items_cumulative`: a `diamond_stamp` object with keys `logic`, `proof`, `reversible`, `verified_iso`

**Validator reference impl (bash, safe to inline):**
```bash
ART_DIR=$(ls -dt ~/Desktop/*-2026-* 2>/dev/null | head -1)
PS="$ART_DIR/phase-state.json"
if [ -f "$PS" ]; then
  python3 - "$PS" <<'PY'
import json, os, sys, datetime
p = sys.argv[1]
fail = []
try:
  d = json.load(open(p))
except Exception as e:
  fail.append(f"parse:{e}")
  d = {}
for k in ("project_slug","current_phase","shipped_items_cumulative"):
  if not d.get(k): fail.append(f"missing:{k}")
cp = d.get("current_phase")
if isinstance(cp,int) and not (0 <= cp <= 13): fail.append("current_phase_out_of_range")
for k,v in d.items():
  if k.startswith("phase_") and k.endswith("_receipt"):
    if not (isinstance(v,str) and os.path.exists(os.path.expanduser(v))):
      fail.append(f"missing_receipt:{k}")
missing_stamps = 0
for it in (d.get("shipped_items_cumulative") or []):
  ds = (it or {}).get("diamond_stamp") or {}
  if not all(ds.get(x) for x in ("logic","proof","reversible","verified_iso")):
    missing_stamps += 1
ts = datetime.datetime.utcnow().isoformat()+"Z"
if fail or missing_stamps:
  os.makedirs(os.path.expanduser("~/.openclaw/logs"), exist_ok=True)
  rec = {"ts":ts,"file":p,"fail":fail,"missing_stamps":missing_stamps}
  open(os.path.expanduser("~/.openclaw/logs/closeout-validation-failures.jsonl"),"a").write(json.dumps(rec)+"\n")
  print(f"VALIDATION FAIL: {fail} missing_stamps={missing_stamps}")
  open(os.path.expanduser("~/.openclaw/state/closeout-validation-promote.txt"),"w").write(
    f"Run diamond-skill backfill on {missing_stamps} items missing stamps" if missing_stamps else "Fix phase-state.json: "+",".join(fail))
else:
  json.dump({"ts":ts,"file":p,"status":"PASS"}, open(os.path.expanduser(os.path.dirname(p)+"/closeout-validation-pass.json"),"w"))
  print("VALIDATION PASS")
PY
fi
```

**On FAIL:** print `VALIDATION FAIL` with the missing-key list, append a JSON line to `~/.openclaw/logs/closeout-validation-failures.jsonl`. Do **NOT** block closeout. Write the promotion string to `~/.openclaw/state/closeout-validation-promote.txt`; recap-skill Step 0 must read that file and use its contents as recap **slot 1** (e.g., "Run diamond-skill backfill on N items missing stamps").

**On PASS:** write `closeout-validation-pass.json` next to the phase-state file with `{ts, file, status:"PASS"}`.

### Step 0: Recap (footer mode)

**v13 wiring (NEW 2026-05-09):** Before invoking recap-skill, write the end-of-thread trigger so v3.5's 2-round council-execute loop fires:

```bash
mkdir -p ~/.openclaw/state && date +%s > ~/.openclaw/state/recap-cycle-trigger.txt
```

recap-skill v3.5 detects mtime <60s and fires the loop on Mack/Ivan only (Leo identity gate skips). Recursion lock at `~/.openclaw/state/recap-cycle.lock` prevents re-entry. The loop runs synchronously inside this Skill call — Steps 1-7 only proceed after the loop completes, so the loop summary is available for inclusion in the closeout report (per recap-skill v3.5 POST-LOOP step 8).

→ Execute recap-skill. Its Mode 1 footer (Prompt Trail + THREAD + 5 options) IS the recap — do NOT inline a separate `## 🔁 Recap` block here. The Mode 2 5-bullet format was deleted in recap-skill v3.0 (it caused duplicate recaps when both closeout and recap-skill emitted it).

Caveman-skill governs voice in everything below.

### Step 1: Diamond Table — Everything Worked On
| Task | Status | Diamond | Proof |
|------|--------|---------|-------|

- 💎 Diamond / ✅ Done / 🟡 In Progress / 🔴 Blocked
- Diamond column: `3/3` ✅, `2/3` 🟡, `1/3` 🟡, `0/3` ❌, `n/a` (only for trivial status checks where stress-testing isn't meaningful — must justify)
- → Execute diamond-skill to verify any 💎 or ✅ task before marking done.

### Step 2: Notion Project Update (BLOCKING — v14)

**This step is BLOCKING. Closeout cannot proceed to Step 3 without a confirmed Notion page ID.**

Root cause fixed (2026-05-13): prior versions were soft — agents completed work, wrote memory, sent CEO email, but did NOT write to Notion. Found 6 live projects with zero Notion pages. This gate closes that gap permanently.

**Mandatory actions (in order):**

1. **Infer project title** — 3-5 word Title Case from this session's work.

2. **Find or create Notion Sprint Board row** at https://www.notion.so/335cf5514fd3813488dec82a68622d7b
   - Search first: `notion-search(query="[project title]", data_source_url="collection://335cf5514fd3813488dec82a68622d7b")`
   - If found: update existing page
   - If not found: create new page via `notion-create-pages`

3. **Write required fields** to the Notion page:
   - What was done (bulleted list of shipped items)
   - What changed (systems, configs, files modified)
   - What's open (Bennett gates + AI-blocked items)
   - Session date + agent identity
   - Link to CEO email msgId (if sent this session)

4. **Capture page ID** from the Notion response. This is your receipt.

5. **Post Notion link** in closeout report Step 7.

**Verification check:**
```
✅ NOTION WRITE CONFIRMED
Page ID: [notion_page_id]
URL: https://www.notion.so/[page_id_formatted]
Fields written: shipped_items | open_items | session_date | agent
```

**On failure:** If Notion MCP fails → retry once. If second attempt fails → post error + page ID attempt to #leo-auto, then continue closeout (non-blocking fallback only after 2 confirmed failures). Log failure to `~/.openclaw/logs/closeout-notion-failures.jsonl`.

**Anti-pattern:** Skipping this step because "memory-skill already logged it" — memory and Notion are separate targets. Memory is agent-internal. Notion Sprint Board is team-visible. Both must be written.



## Step -0.5: No-Early-Stop Gate (BLOCKING — v18)

Before any closeout or final response, scan the current status for Yellow, partial, AI OPEN, or blockers.

- If any remaining item is AI-owned and has a safe reversible path, execute it now, up to 3 safe attempts before requiring a bounded continuation receipt. Safe means no external send, no delete, no money/trade, no legal/FDD/customer document movement, no credential value exposure, and no protected identity action.
- After execution, fetch back/read back canonical Drive/Notion proof and rerun gatekeeper, memory-sync, manifest, recap checker, or the relevant verifier.
- Do not move the item to Open Items and do not close the thread merely because the verifier returned Yellow. Yellow is the next execution queue.
- Closeout may proceed only if all AI-owned safe actions are cleared, the remaining blocker is true human/protected/platform-limited with probe proof, or a bounded continuation receipt exists.

Required receipt line:
```
NO_EARLY_STOP_GATE: pass|blocked owner=<ai|human|platform> next_action=<executed|protected|continuation> proof=<path_or_url>
```

### Step 2.5: Notion Project Sub-Page Update (BLOCKING — v16)

**This step is BLOCKING. Closeout cannot proceed to Step 3 without a confirmed sub-page URL.**

**Why:** Step 2 writes status-level fields to the Sprint Board row (shipped, open, session date). Step 2.5 writes the full artifact record to a dedicated sub-page linked to that row. These are separate Notion objects — both required.

**Mandatory actions (in order):**

1. **Use the Notion page ID captured in Step 2** as the parent.

2. **Create or update a sub-page** titled `Session Log — <YYYY-MM-DD>` under the Sprint Board row:
   - Use `notion-create-pages` with `parent_id=<step2_page_id>`
   - If a sub-page with today's date already exists → update it via `notion-update-page`

3. **Write the following sections to the sub-page body:**

   ```
   ## Artifacts
   [Table: Title | Type | Drive ID / URL | Status]
   — One row per shipped item, Drive file, or live URL created this session

   ## Session Stats
   - Agent: Ivan CC (claude-sonnet-4-6) | Date: YYYY-MM-DD
   - Items shipped: N | T1 direct: X | T2 dispatched: Y | T3 bennett-mode: Z
   - Self-heals: H | Skill patches: P | Process improvements: I
   - CEO email: sent ✅ / not sent ❌

   ## Carry-Forward
   [Bulleted list of open items with tier, SLA, and blocker reason]

   ## Process Improvements This Session
   [Bulleted list from ~/.openclaw/workspace/process-improvements.jsonl entries written this session]
   ```

4. **Capture sub-page URL** from Notion response.

**Verification check:**
```
✅ NOTION SUB-PAGE CONFIRMED (v16)
Parent Sprint Row ID: [step2_page_id]
Sub-Page URL: https://www.notion.so/[sub_page_id]
Sections written: artifacts | session_stats | carry_forward | process_improvements
```

**On failure:** If Notion MCP fails → retry once. If second attempt fails → write the sub-page content to `~/.openclaw/logs/closeout-notion-subpage-fallback-<date>.md`, log to `~/.openclaw/logs/closeout-notion-failures.jsonl`, and continue closeout.

**Anti-pattern:** Writing the artifact record only to memory-skill and skipping the Notion sub-page. Memory is agent-internal ephemeral state. Notion sub-pages are the persistent, team-visible artifact record.

### Step 3: Master Prompt Check
Read https://www.notion.so/33dcf5514fd3816fbd57e5c1fdc0a3fd. Anything new (Red Lines, model rules, channel IDs)? Report.

### Step 4: Skills Used / Edited / Deleted (BLOCKING)

**Skill edit discipline (Bennett 2026-04-28):** When a skill needs improvement, the default action is **EDIT the existing SKILL.md and PATCH to Drive**, NOT create a new skill file. Creating a new skill is reserved for genuinely new capabilities not covered by any existing skill.

→ Execute memory-skill for the canonical Drive storage rules and PATCH protocol. Then run the manifest validator:
```bash
python3 ~/.openclaw/scripts/validate_skill_manifest.py
```
Exit 0 = clean, proceed. Exit 1 = problems printed to stderr; resolve each before continuing closeout.

**Then produce two tables — every closeout must show both, even if empty.**

**Table A — Skills USED in this session (read or invoked, not edited):**
| Skill | Drive fileId | Storage location confirmed? |
|---|---|---|

**Table B — Skills EDITED, CREATED, or DELETED this session:**
| Skill | Action | Drive PATCH confirmed? | Was a new file created? (justify if yes) |
|---|---|---|---|

Action = `Edited` / `Created` / `Deleted` / `Renamed`. For EVERY new file, justify in plain English why an edit to an existing skill couldn't have done the job. If no justification exists → revert and edit the existing skill instead.

**Auto-chain on failure:** If a PATCH attempt fails (auth error, fileId mismatch, network), → Execute troubleshoot-skill per Step -1's auto-chain rule.

### Step 4.5: Diamond Verification (BLOCKING — self-service)

**Every task in Step 1's Diamond Table marked ✅ Done or 💎 must run diamond-skill BEFORE closing.** The agent who did the work runs the verification on their own work — no routing to Leo or Cody.

→ Execute diamond-skill on each completed task. Deliver its 3-test pass/fail block per task.

**Self-verify rule:** Any agent (Mack, Ivan, Leo, Tiffany, Cody) runs diamond-skill on their own work. We're using the same skill. No "send it to Cody to verify" — that creates routing overhead and stalls.

**Diamond column scoring in Step 1 table:**
- `3/3` 💎 — all 3 tests pass with evidence inline
- `2/3` 🟡 — partial; explain which test failed in the row notes
- `1/3` or `0/3` ❌ — task is NOT done; move to Step 7 Open Items
- `n/a` — only for trivial status checks; must justify

**No closing the thread if any ✅ Done task lacks a Diamond score.**

### Step 5: Memory Update Report

→ Execute memory-skill. Deliver its required Memory Updates report block verbatim, covering CLAUDE.md, Ivan project memory, and Mack auto-memory targets.

### Step 5b: bennett-rules.md Cross-Cutting Audit (Drive-canonical v10)

bennett-rules.md is auto-injected at SessionStart on Mack + Ivan via `inject-bennett-rules.sh`, which `gog drive download`s the canonical Drive file at every session boot. Hard cap 1000 chars.

**CANONICAL: Drive fileId `1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui` (Leo AI/docs/bennett-rules.md). Local files are ephemeral caches — never edit them, they overwrite from Drive on next session.**

Closeout MUST audit:
1. Scan every new/changed `feedback_*.md` file written this session (Mack auto-memory + Ivan memory dirs).
2. For each: is the rule cross-cutting (applies all sessions, not project-specific)? If YES and not already in bennett-rules.md → promote it.
3. Edit happens ONLY on Drive: download via `gog drive download 1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui` → edit → `gog upload --replace=1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui`. Do NOT touch local caches.
4. If file exceeds 1000 chars after promotion: prune the OLDEST line on Drive.
5. → Execute memory-skill contradiction detector. If conflict found → STOP, alert Bennett.

Report block:
```
bennett-rules.md audit (Drive-canonical):
- Promoted: [N rules — list each]
- Pruned: [N old rules]
- Final size: [X / 1000 chars]
- Contradictions: [pass / N flagged]
- Drive PATCH: [✅ replaced=true,preservedFileId=true / ❌ ...]
- Caches: [Mack + Ivan auto-refresh on next SessionStart — no manual sync]
```

**Architecture reference:** Leo AI/docs/cross-memory-architecture.md (Drive `1mh7bfiWZz_5C4cAv9lgkpqxFcrCnPL4_`).

### Step 6: Post to #leo-auto
Concise close to C0AKXT2S1T2: recap-skill block, Notion link, open items.

### Step 6.5: Post AI-Blocked Items to #leo-coaches (MANDATORY)

After building the Open Items list, scan each item:
- **Human gate** (requires Bennett/biometric/financial/external) → human-gates-log.md + Bennett DM only. Do NOT post to #leo-coaches.
- **AI-blocked** (another AI agent needs to pick it up) → post to #leo-coaches (C0AQ4KB1SA0).

Format for each AI-blocked item:
```
🤖 PICKUP AVAILABLE — [task name]
Task: [one sentence]
Abilities needed: [e.g. Drive MCP, Notion MCP, Bash/CLI, Slack MCP, GHL MCP]
Context: [one sentence — what's done, what's needed next]
```

No agent name required. Any AI reading #leo-coaches can claim it.
Post all AI-blocked items in a single message if there are multiple.
If no AI-blocked items: skip this step silently.

### Step 6.6: Open Item DIY Resolution Loop (BLOCKING — added v10)

**The closeout cannot complete with non-empty Open Items unless every item has proven DIY exhaustion.**

Before classifying any blocker as BENNETT gate: → Execute blocker-verify-skill (blocker_id, type, url). Only escalate if status=verified_down or human_only.

Before listing ANYTHING in Open Items, run this loop on each candidate:

1. **Council pass** — → Execute council-skill (compressed mode, single round) with the item + the full DIY tool inventory. Ask: "Is this resolvable end-to-end with the agent's current tool surface?"

2. **If council says YES** (any tool path exists): **execute it now.** Don't surface as Open. Repeat until done or council says NO.

3. **If council says NO**, generate the DIY-exhaustion log:
   ```
   OPEN ITEM: [name]
   DIY ATTEMPTS:
   - [tool 1]: [what was tried, exact failure mode]
   - [tool 2]: [what was tried, exact failure mode]
   - [tool 3]: [what was tried, exact failure mode]
   COUNCIL VERDICT: NOT RESOLVABLE BY AGENT (≥3 proven blockers above)
   BENNETT-GATE JUSTIFICATION: [biometric / financial / identity / legal / external-irreversible / hardware-physical-access]
   ```

4. **Only items with a complete log AND a valid Bennett-gate category** may appear in Open Items. Anything else: resolve before closing.

**Anti-pattern (Bennett 2026-05-04):** Listing "leftover housekeeping" or "should be cleaned up next pass" without a DIY attempt = lazy closeout = INCOMPLETE. Closeout must re-fire until the list is either empty or every entry has the proof block above.

### Step 6.7: Artifact Registry Bulk-Registration (notion-artifact-skill v1.0 — 2026-05-21)

**Non-blocking.** Failures do NOT halt closeout — log and continue to Step 7.

Before the final report, ensure every Drive artifact created this session has a Notion row in the FKI AI Artifact Registry — Universal.

**Scan sources (in order):**
1. `~/.claude/artifact-queue.jsonl` — PostToolUse hook queue from this session
2. Any Drive link mentioned in this session's THREAD rows or Step 1 Diamond table
3. Any file created via `mcp__claude_ai_Google_Drive__create_file` or `copy_file` this session

**For each artifact without a Notion registry row:**
→ Execute notion-artifact-skill REAL-TIME MODE with the artifact metadata (name, type, drive_file_id, agent, project, date).

**Coverage check:**
```
✅ ARTIFACT REGISTRY SWEEP (Step 6.7)
Artifacts found this session: N
Already registered: M
Registered this step: K
Coverage: (M+K)/N = X%
```

**Queue drain (Bash):**
```bash
QUEUE=~/.claude/artifact-queue.jsonl
[ -f "$QUEUE" ] && wc -l < "$QUEUE" || echo "0"
```
If queue non-empty: process each entry via notion-artifact-skill, then truncate queue.

**Universal DB:** https://www.notion.so/11944015a0b5468587dd66dc148ac606
**Collection ID:** `2501fb25-637e-44fb-a4ff-2235e04863c3`

### Step 7: Deliver Close-Out Report

**Always start with recap-skill block (Step 0). Then:**
```
## 📦 Thread Closed — [Date]

### 🔄 Sync Gate
[Step -1 result: pass / N skills force-pulled]

### ✅ What Was Done
[Diamond table with status + Diamond column + proof]

### 🎯 Net Effect
**Today:** [one sentence]
**Going forward:** [one sentence]

### 📋 Notion
✅ Updated: [link]
Sprint Board: [link]

### 🧠 Master Prompt
[Updated / Not needed] — [details]

### 💾 Memory
- CLAUDE.md / Ivan / Mack: status
- bennett-rules.md: [N promoted, N pruned, X/500 chars]

### 💎 Diamond Verification Summary
N tasks at 3/3 | M at partial | K blocked | All self-verified by [agent]

### 🛠 Skills (this session only)
- **Used:** [comma list with drive_file_id confirmed]
- **Edited:** [list, with `gog --replace` confirmation]
- **Created:** [list, each with one-line justification why an edit wouldn't suffice]
- **Deleted:** [list]
- All canonical files live in Google Drive folder `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY`

### 🔴 Open Items (THIS THREAD ONLY — strict scoping)
**SCOPING RULE (Bennett 2026-04-28):** Open Items lists ONLY items that originated from work performed in THIS closeout thread. Do NOT propagate pre-existing Bennett-gates from earlier handoffs.

Format: `[Blocked items + owner + next action, or "None"]`

After listing, apply Step 6.5 rule: AI-blocked → #leo-coaches pickup post. Human-gated → human-gates-log only.
```

## Red Lines
- NEVER skip Step -1 sync gate — closeout from a stale skill chain produces wrong outputs
- NEVER skip the recap-skill block at top — first thing Bennett reads
- NEVER mark a task ✅ Done in the Diamond Table without a Diamond score
- NEVER route Diamond verification to another agent — self-verify is mandatory
- NEVER skip the Master Prompt check
- NEVER skip Step 5b bennett-rules.md cross-cutting audit
- NEVER mark a skill update Done without confirmed Drive PATCH (gog upload --replace)
- NEVER ask Bennett for the project title — infer it
- Net Effect MUST be plain English from Bennett's perspective
- NEVER create a new SKILL.md when an edit to an existing skill would do the job
- NEVER include Open Items from earlier handoffs or ambient blockers
- NEVER skip Step 6.5 AI pickup post
- NEVER list an Open Item without the Step 6.6 DIY-exhaustion log + Bennett-gate justification
- NEVER inline content from other skills — always reference via → Execute
- **NEVER skip Step 2 Notion write — a closeout without a confirmed Notion page ID is INCOMPLETE (v14)**
- **NEVER classify a blocker as BENNETT gate without first running blocker-verify-skill — only escalate if status=verified_down or human_only (v15)**
- NEVER treat memory-skill write as a substitute for Notion Sprint Board write
