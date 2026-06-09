---
name: memory-skill
drive_file_id: 11N3WxEHenqDoidLawqfh1m-AfeU0G8Pu
version: 9.5
last_updated: 2026-06-04
trigger: "update memory", "memory protocol", "update everything", "sync memory", "save this", "audit memory", "use the memory skill", "search for this", "remember this", "store this", "log this"
description: "Update all persistent storage when Bennett says update memory, memory protocol, update everything, sync memory, save this, audit memory, or use the memory skill. Handles cross-machine memory reads via SSH to Mack. v9.1 adds uniform agent workflow memory: Drive-skill-first, recap every response, council before strategic/permanent fixes, DIY before handoff, Diamond proof before done, and Leo only for cron/cross-machine ownership. MANDATORY TRIGGERS: update memory, memory protocol, update everything, sync memory, save this, audit memory, use the memory skill."
credential_vault_page_id: 341cf5514fd381fe993de8add7eb265e
deps:
  - name: closeout-skill
    fileId: 1IfdB8YM-F9GzPHka44uE199NqPFAI4gB
  - name: autopilot-skill
    fileId: 10KBx34OrzdlX0_RN9x8zqNvQEprLdQow
  - name: diamond-skill
    fileId: 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT
  - name: strike-skill
    fileId: 1mBRI0RKEuuvLF5Oh3Gdrl-BLhGrsZhix
  - name: machines-skill
    fileId: 1FQ6c_xnxPSEsVPRQ7mxaHpwyqHxBqmxk
  - name: tools-skill
    fileId: 1WzuzXJJT5Pei5QpVmH0H9_QMHp3p0Wzd
  - name: council-skill
    fileId: 18edfLllHikArUABu7l_feBxFWfiLncAY
  - name: bennett-intelligence-layer
    fileId: 1sxSzVTQwWNIdYdub5kV6hgLZSjPWYpDH
  - name: review
    fileId: 1iAo8F6-_xw0eEwV7DxaYQGBPlb1urZTG
zone1_hardened: true
---

# Memory Protocol Skill v9.5 (2026-06-04)
# v9.5 patch (2026-06-04): Added session-scoped receipt hard gate. Every invocation must append a receipt with `session_id` or `thread` even on no-op scans, so the stop hook can mechanically block any response that tries to close without memory-skill proof. Hard-memory prompts still require canonical Drive/Notion proof when durable state changed.
# v9.4 patch (2026-06-02): Added fail-closed source-of-truth rule. Durable cross-agent memory must live in Drive, credentials only in Notion Credential Vault, and local memory files are cache/receipt layers only. Added explicit ban on treating repo or local memory as canonical and added recovery path for accidental local writes.
# v9.3 audit patch (2026-05-30): (1) Added missing trigger phrases "search for this/remember this/store this/log this". (2) Fixed receipt schema — added required `thread` and `verified` fields per v7.1 mandate. (3) Corrected Ivan project memory path to include both -Users-openclaw/memory/ and -Users-openclaw-Ivan---Imac/memory/ dirs. (4) bennett-rules.md Tier-0 section now includes Drive fileId for gog-upload. (5) Step 0.5 Mack repeat-flags write now guarded by Tailscale liveness check. (6) bennett-rules.md cap enforcement now includes auto-prune-and-upload action when >1000 chars.
# v9.2: Step 0.6 DEDUPE-BEFORE-WRITE (memory-hygiene.py --check) — closeout-skill + all memory writers delegate here. Fixes index-bloat/stale-recall root cause.

## North Star
Succeeds when Ivan, Mack, and Leo all behave identically: every session loads memory at start and updates it at end.
When 'search for this' is invoked: search emails (all agents) plus Google Drive (all) plus Slack (all channels) plus Google Meet transcripts plus GHL contacts/notes/pipeline plus GitHub issues/PRs, using the target keyword PLUS 5-10 related keywords. Start with Notion to understand project context, then expand keyword set. Same question equals same complete answer in any session.

## Search Protocol
1. Notion first: get project context plus expand keywords
2. Parallel search: Gmail, Drive, Slack, Meet transcripts, GHL, GitHub
3. GHL deep-dive: contacts, notes, pipeline stages, workflow history, conversations
4. GitHub: code plus issues plus PRs with all keyword variants
5. Synthesize with source citations

## Tool Surfaces
- Google Drive canonical memory/skill storage
- Notion for project state and Credential Vault
- Local receipts only as temporary fallback
- `tools-skill` before connector-specific paths

## Authentication and Secret Handling
- Credentials are never stored as durable memory outside the Notion Credential Vault.
- Never print raw tokens, keys, cookies, or secret values in memory receipts.

## Protected Actions and Approval Gates
- Read/search/reconcile by default.
- Any claim of saved memory requires canonical-store proof.
- Do not treat a local write as a completed durable-memory save.

## Preflight and Smoke Tests
- Read the current canonical Drive or Notion target before writing.
- Confirm the target item ID/path and whether the write belongs in Drive or Credential Vault.

## Proof and Receipts
- Required proof: canonical store ID/path plus readback/fetchback after the write.
- Temporary local receipts must be labeled as temporary until canonical reconciliation succeeds.
- Every invocation, including no-op scans, must append a receipt line to `~/.openclaw/state/memory-skill-receipts.jsonl` with `session_id` (preferred) or `thread`, plus `verified`, `written`, and `skipped`. A response without a session-scoped memory receipt is incomplete.

## Failure Recovery and Rollback
- If Drive/Notion is unavailable, create a temporary local receipt and keep reconciliation open.
- If an accidental local-only memory write occurs, mark it non-canonical, reconcile into the canonical store, and report the drift.

## Handoff Fields
- Memory target:
- Canonical store:
- Proof:
- Blocker:
- Next action:

> v9 changelog (2026-05-26): Notion Credential Vault is now the SINGLE canonical credential store (Bennett-approved, plaintext, universally readable via Notion MCP). (a) Credential self-heal reads the Vault FIRST, Slack/Gmail only fallback. (b) SessionStart loads a compact credential manifest. (c) RECALL-GATE: no "I do not have X / X is expired" claim without a Vault read plus token-probe receipt under 15 min old. (d) GHL probe endpoint fixed to location-scoped contacts. The durable copy of any credential IS the Vault, write/read mismatch is closed.
> v9.1 changelog (2026-05-27): Uniform Agent Workflow Memory patch. Any memory update that changes agent behavior must include the five-step loop: Drive skill loader proof, council approval for strategic/permanent fixes, DIY before human/Leo escalation, Diamond proof before done, and recap closeout proof. Leo handoff is reserved for cron/LaunchAgent/cross-machine ownership or a proven unreachable machine.
> v8 changelog (2026-05-25): Added Self-Audit Checklist and Cron Bindings sections per skill-creator-skill v11 / angie-weekly-audit-skill v7 mandate.
> v7.1 changelog (2026-05-09): Live Thread Projects Notion DB added. Canonical: 573123c6-3332-433d-89ae-befbfeb05e5e (data_source 3e11936b-ac59-4104-a842-144c94754698, parent: Advaita Vision). Every memory-skill invocation MUST append a receipt to ~/.openclaw/state/memory-skill-receipts.jsonl (NOT ~/.openclaw/logs/ — that path was wrong) containing ALL of these fields: ts, agent, session_id or thread, writes, verified, written (list of files), skipped (list), memory_bytes, under_cap — so recap-skill and the stop hook can print proof-checkmark and mechanically block missing memory. Receipts missing `session_id`/`thread` or `verified` are treated as partial/skipped by recap. Note: actual receipt path is state/ not logs/.
> v7 changelog (2026-05-04): Drive-canonical architecture. All cross-machine memory lives in Google Drive Leo AI/docs/. Local files are ephemeral caches refreshed at SessionStart.

When triggered, update the canonical Drive copy of any persistent storage location and report what changed. Run the contradiction detector before writing any new rule. Diamond-verify every claimed write.

## 🚨 Source-of-Truth Red Line (v9.4)
- **Drive is the canonical home for durable cross-agent memory.**
- **Notion Credential Vault is the canonical exception for credentials only.**
- Local files, repo memory notes, local mirrors, `generated-skills/`, `~/.claude/skills/`, and temporary receipts are never canonical memory.
- Local drafts are allowed only when explicitly labeled **NON-CANONICAL** and they may never be used as routing, memory truth, or proof of save.
- If duplicates or parallel notes exist, **never assume the nearest local copy is canonical**. Verify the exact canonical Drive item ID first.
- If Drive is slow or unavailable, write a temporary local receipt only, label reconciliation as open, and do not claim memory was saved until the Drive canonical item is updated and fetched back.
- If a local memory file or local skill was updated by mistake, mark it NON-CANONICAL, reconcile the content into Drive canon if needed, then report the drift.

---

## Step 0 — EXECUTION BOUNDARY GATE (BLOCKING, runs FIRST)

Classify the memory write target by storage tier. All cross-machine tiers are Drive-canonical (v7), EXCEPT credentials which are Notion-Vault-canonical (v9). Local files equal ephemeral caches that auto-refresh at SessionStart.

| Storage Tier | Canonical store | Owner | Method | Local cache |
|---|---|---|---|---|
| Credentials (ALL services) | Notion Credential Vault 341cf5514fd381fe993de8add7eb265e | Any agent | Notion MCP notion-update-page | gateway.env equals mirror, refreshed from Vault at SessionStart |
| bennett-rules.md (Tier 0 inject) | 1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui (Leo AI/docs) | Any agent | gog upload replace 1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui | Mack plus Ivan ~/.openclaw/memory/ overwritten each SessionStart |
| Skills (any) | Leo AI/FKI AI Skills Master 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY | Any agent | gog upload replace drive_file_id (fileId-locked) | Ivan ~/.claude/skills/ closeout sync gate refreshes |
| Master Prompt | Leo AI/docs (gdoc) | Any agent | Edit gdoc directly | None |
| SOUL / Vision | Leo AI/docs (gdoc) | Any agent | Edit gdoc directly | None |
| Cross-memory architecture | 1mh7bfiWZz_5C4cAv9lgkpqxFcrCnPL4_ (Leo AI/docs) | Any agent | Edit plus gog upload replace | None |
| Sprint Board / Decisions / Sessions | Notion (memory-skill v2) | Any agent | Notion MCP | None |
| CLAUDE.md (local Red Lines) | Ivan-only ~/.claude/CLAUDE.md | Ivan-CC | bash | n/a |
| repeat-flags.md (per machine) | Per-machine local | Per machine | bash | n/a |
| GitHub archive (Sunday backup) | GitHub | Ivan-CC | git push | Never source-of-truth |

Hard rule: if writing a fact that any other agent needs to read in a future session, the canonical copy MUST live in Leo AI/docs/ on Drive. For credentials, the canonical copy MUST live in the Notion Credential Vault, never gateway.env alone, never a Drive memory blob, never a local file. Local memory paths are cache only and cannot be treated as success proof.

## Step 0.2 — Uniform Agent Workflow Memory Gate (v9.1)

When the memory update changes how agents behave, the memory entry MUST include this compact workflow contract:

1. **Drive first:** Search FKI AI Skills Master and load canonical `SKILL.md` by frontmatter `name` before answering.
2. **Council before permanence:** Strategic decisions, new permanent rules, or skill patches need council-skill approval or an explicit council-unavailable blocker.
3. **DIY before handoff:** Exhaust diy-skill and direct tool/API paths before Bennett or Leo. Leo is for cron/LaunchAgent/cross-machine ownership, not ordinary execution.
4. **Diamond before done:** Any claimed persistent write, skill execution, email send, handoff, or shipped artifact needs diamond-skill proof.
5. **Recap every response:** recap-skill owns final claim ledger, partial labels, Sprint/Drive memory proof, and closeout status.

If the memory receipt omits any row, the memory update is partial and cannot be used as a fleet-wide behavior fix.

---

## Step 0.3 — SessionStart CREDENTIAL MANIFEST LOAD (NEW v9, runs at boot)

At SessionStart, every agent loads a COMPACT credential manifest from the Notion Credential Vault (341cf5514fd381fe993de8add7eb265e) via notion-fetch. This is a one-line-per-service snapshot, NOT the full values, so the agent always knows what exists before claiming anything is missing.

Manifest line format (per service): service then status then last_probe then pointer
- status equals ok or expired or unknown (from the Vault last_verified plus taxonomy)
- last_probe equals ISO timestamp of last token-probe receipt
- pointer equals "Vault row" (the full VALUE, probe cmd, taxonomy, rotation owner live in the Vault)

Example manifest (loaded into working context):
```
GHL_PIT_TOKEN then ok then 2026-05-26T05:00Z then Vault row
META_ACCESS_TOKEN then ok(non-expiring system user) then 2026-05-26 then Vault row
GITHUB_TOKEN then ok then 2026-05-26 then Vault row
QB_OAUTH then expired then 2026-05-19 then Vault row (Kay rotation)
ANTHROPIC_API_KEY then ok then 2026-05-26 then Vault row
```

The manifest is the index. The Vault row is the durable copy. Never reconstruct a credential value from memory, re-read the Vault row.

---

## Step 0.35 — CREDENTIAL RECALL-GATE (NEW v9, BLOCKING, Tier 0)

Before ANY agent emits the words "I do not have X", "X is expired", "X is missing", "needs rotation", "token is stale", or surfaces a credential as a human gate, this gate MUST pass:

1. Vault read: notion-fetch 341cf5514fd381fe993de8add7eb265e. Does the Vault hold a current VALUE for the service? If YES and last_verified is recent, use it. The claim "I do not have X" is FALSE if the Vault has it.
2. Live probe: run ~/.openclaw/bin/token-probe.sh service and capture the receipt. Receipt MUST be under 15 min old.
3. Taxonomy classify the probe HTTP code (see Step 0.4). Only 401 equals genuinely expired. 403/429/000 are NOT expiry.
4. Only if Vault has no value AND probe returns 401 with an under-15-min receipt may the agent say "expired", and it must then self-heal per Step 6.

No Vault read plus no fresh probe receipt equals the "expired/missing" claim is BLOCKED and treated as operator error. Bennett has asked for this 10-plus times: never diagnose from stale memory.

---

## Step 0.4 — KNOWN ERRORS AND SOLUTIONS REGISTRY (v7.2, updated v9)

Purpose: When ANY agent is about to claim a service is "expired/broken/down/stale/needs rotation/401" OR Bennett says "check the memory skill", read this section FIRST, AFTER passing the Step 0.35 recall-gate.

Hard rule (Tier 0): No claim of "X expired/broken/down" without a probe receipt less than 15 min old. Run: ~/.openclaw/bin/token-probe.sh

### HTTP status taxonomy:
| Code | Status | Action |
|---|---|---|
| 200 | ok | Token valid, no action |
| 429 | throttled | Rate-limited. WAIT. Do NOT rotate. |
| 403 | wrong_id | Token valid, wrong locationId/resource. Fix the CALL, not the token. Do NOT rotate. |
| 401 | expired | Real auth fail. Rotate per service-specific solution below. |
| 000 | network | No response. Check connectivity. Do NOT rotate. |
| 404 | not-applicable | For GHL PITs, users/me ALWAYS 404, this is NOT expiry. Use the location-scoped probe below. |

### Known-error registry:
| Pattern | Real cause | Solution |
|---|---|---|
| GHL TOKEN EXPIRED from ivan-health | Daemon mislabels ALL non-200 as expired (verified 2026-05-23) | token-probe.sh location-scoped (see GHL PROBE FIX). 401 equals Vault first then Slack from Kay. 429 equals wait. 403 equals fix locationId. 404 on users/me equals NOT expiry. |
| Meta token expired | Leo Meta is SYSTEM USER token equals NON-EXPIRING | probe graph.facebook.com me endpoint, 200 equals ignore |
| GitHub token stale | Probe, usually valid | probe api.github.com user endpoint, 200 equals valid |
| QB OAuth expired over 7d | Real expiry, Kay rotation | Auto-WO Leo then DM Kay. Never Bennett. Update Vault row on recovery. |
| LinkedIn exit 1 | li_at cookie expired Chrome Profile 2 | Kay refresh cookie |
| Tailscale Ivan down | Check tailscale status first | preflight rule |
| Notion API 401 mid-session | Composio OAuth expired | Save to Drive, Leo WO refresh |
| op would like to access | TCC auth_value 5 corruption | tccutil reset SystemPolicyAppData |

### GHL PROBE FIX (v9, canonical):
GHL PITs are location-scoped. NEVER probe with users/me (always returns 404 for a PIT, this is NOT expiry and has caused false "expired" claims repeatedly). Correct probe is an authenticated GET to the contacts endpoint scoped by location:
- Endpoint: services.leadconnectorhq.com contacts, query params locationId equals GHL_LOCATION_ID and limit equals 1
- Header Authorization Bearer GHL_PIT_TOKEN
- Header Version 2021-07-28

Result codes:
- 200 equals valid
- 401 equals expired (rotate)
- 403 equals wrong locationId, fix the call, not the token
- 429 equals rate-limited, wait

Canonical variable name equals GHL_PIT_TOKEN (all skills/scripts use this name). Location id equals GHL_LOCATION_ID.

---

## Step 0.5 — Repeat-Explanation Prevention (Run on Every Trigger)

When Bennett uses phrases like "I have told you", "I have explained this", "again:", "as I mentioned":

1. Stop and search memory first: grep MEMORY.md plus all feedback_*.md plus bennett-rules.md
2. If found: Report already in memory at file:line. Then write immediately to correct tier.
3. If not found: Write it NOW before doing anything else.
4. Log to repeat-flags.md at Ivan (/Users/openclaw/.openclaw/memory/repeat-flags.md) — always reachable. For Mack (/Users/temp/.openclaw/memory/repeat-flags.md): FIRST confirm Tailscale liveness (`tailscale status | grep 100.112.24.104`). If unreachable, skip Mack write and note "Mack offline — repeat-flag write deferred" in the Ivan log entry. Never fail silently.

---

## Step 0.6 — DEDUPE-BEFORE-WRITE (v9.2, BLOCKING on any new memory .md)

Before creating ANY new memory file in the auto-memory dir (`.../projects/-Users-*/memory/`), run the hygiene check so the index does not bloat into stale recall (root cause of the 929-file / 753-line index incident, fixed 2026-05-27):

1. `python3 ~/.openclaw/bin/memory-hygiene.py --check {type}_{topic_slug}`
2. Output `EXISTING: <path>` (exit 0) → **UPDATE that file in place** (Edit/append + bump valid_as_of), do NOT create a new one.
3. Output `NONE` (exit 1) → safe to create new. Keep the index hook ≤160 chars, no credential values.
4. This is the same gate recap-skill v5.8 runs at POST-LOOP 4.6 STEP A.5. **closeout-skill and any agent writing memory delegate to this rule** — recap is the per-response writer; the WEEKLY consolidation (`--apply`: series-collapse + auto-archive + index rebuild, durable-first, credential-scrubbed) runs via Mack LaunchAgent `com.fki.memory-hygiene-weekly`. Engine reference: [[reference_memory_hygiene_engine]].

---

## The System in One Sentence

Google Drive is the single source of truth for memory and skills. The Notion Credential Vault (341cf5514fd381fe993de8add7eb265e) is the single source of truth for credentials. Skills live in FKI AI Skills Master (Drive folder ID 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY). CLAUDE.md is local Red Lines only. bennett-rules.md is the auto-load pinned file injected at every session start.

---

## Cross-Machine Memory Scope

| Machine | Agent | SSH from Ivan | Tailscale IP | iCloud |
|---|---|---|---|---|
| Ivan (iMac) | Ivan-CC | Local, no SSH | 100.103.51.12 | Sync OFF (confirmed 3x, never ask again) |
| Mack (MacBook) | Mack / Mac-CC | ssh temp at 100.112.24.104 | 100.112.24.104 | May be active at ~/Library/Mobile Documents/ |
| Tiffany (HP Omen) | Tiffany sub-agent | See machines-skill | See machines-skill | N/A |

Resolved 2026-04-26: 100.112.24.104 equals Mack-from-Ivan. 100.103.51.12 equals Ivan-from-Mack.

---

## Agent Access to Drive plus Credential Vault (and Execution Authority)

| Agent | Drive access | Credential Vault access | CLI / SSH execution |
|---|---|---|---|
| Ivan-CC (iMac) | ~/.claude/skills/ symlink, rclone-synced from Drive | Notion MCP read plus write | Full, Bash sandbox approved 2026-04-24 |
| Mack (MacBook) | Drive MCP plus SSH to Ivan via Tailscale 100.103.51.12 | Notion MCP read plus write | NONE in autopilot mode, delegates CLI via WO |
| Leo (cloud) | Drive MCP, primary bennett at franchiseki.com | Notion MCP read plus write | None, orchestrator only |

Every agent/thread reads the same one Vault. Credentials are NOT per-agent, the Vault is the live shared credential object.

---

## bennett-rules.md — Auto-Load Tier 0

- Path (Ivan): /Users/openclaw/.openclaw/memory/bennett-rules.md
- Path (Mack): /Users/temp/.openclaw/memory/bennett-rules.md
- Drive canonical: Advaita AI/docs/bennett-rules.md | Drive fileId: 1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui (use this for `gog upload replace 1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui`)
- Hard cap: 1000 characters. Dense pinned rules only. Prune oldest on overflow.
- **Cap enforcement action (NEW v9.3):** If `wc -c ~/.openclaw/memory/bennett-rules.md` > 1000, prune oldest entries until ≤1000 chars, then immediately re-upload to Drive with `gog upload replace 1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui ~/.openclaw/memory/bennett-rules.md`. Do NOT just report the violation — fix it in the same step.

---

## Storage Locations (update in this order)

### 1. bennett-rules.md, TIER 0 AUTO-LOAD
- Cap: 1000 chars. Prune oldest on overflow.

### 2. Notion Credential Vault, CANONICAL CREDENTIAL STORE (v9)
- Page: 341cf5514fd381fe993de8add7eb265e (API Keys and Credentials Index / Credential Vault).
- Holds, PER SERVICE: variable name(s), current VALUE (plaintext, Bennett-approved), probe command, 200/401/403/429 taxonomy, rotation owner, last_verified date.
- Universally readable by EVERY agent/thread via Notion MCP notion-fetch. Writable via notion-update-page.
- On ANY credential discovery/recovery: write the new value plus last_verified to the Vault FIRST, then mirror to gateway.env.

### 3. Google Drive, CANONICAL SOURCE OF TRUTH (memory plus skills)
- Advaita AI folder: ID 1e6iH9n0ZKNezYhXM4q57-SDzXLNIQiNs
- Skills folder: 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY
- Skills: edit in Drive ONLY. Use drive_file_id in frontmatter to PATCH.
- Docs folder (1Yc9J008OMtN3xkfnZJn10BJ2cyaaE2_k): Master Prompt, Advaita Vision, SOUL, bennett-rules.md.

### 4. CLAUDE.md, Rules and Red Lines ONLY
- Path: ~/.claude/CLAUDE.md. Hard cap: 3,500 characters.

### 5. Notion, Search Before Updating
- Sprint Board (335cf5514fd3813488dec82a68622d7b), session row required at close.

### 6. Memory Files, System Facts and Session Discoveries
- Ivan project memory (two active dirs — BOTH are in use):
  - `~/.claude/projects/-Users-openclaw/memory/` — primary, holds MEMORY.md and feedback/project/reference files
  - `~/.claude/projects/-Users-openclaw-Ivan---Imac/memory/` — secondary Ivan session context
  - When writing a new memory file, run `ls ~/.claude/projects/-Users-openclaw/memory/ ~/.claude/projects/-Users-openclaw-Ivan---Imac/memory/ 2>/dev/null | grep <slug>` to confirm which dir already holds a matching file before creating a new one.
- Mack memory: ~/.claude/projects/-Users-temp-OpenClaw---Macbook-/memory/
- Autopilot state file: /Users/openclaw/.openclaw/state/autopilot-state.json

### 7. Rotating Credentials, Self-Heal Protocol (v9, VAULT FIRST)
GHL PIT Token Self-Heal Protocol (canonical order):
When GHL returns 401 (after the Step 0.35 recall-gate plus location-scoped probe confirms a real 401):
1. Vault FIRST: notion-fetch 341cf5514fd381fe993de8add7eb265e. If the Vault holds a newer GHL_PIT_TOKEN than the one that just failed, use it and re-probe. Done.
2. Fallback only if Vault stale: search Slack from U08JNLSUN8P in #leo-auto pit- sort newest
3. Fallback: search Gmail from kay at franchiseki.com pit- sort newest
4. On recovery: write the new value plus last_verified to the Vault FIRST, then SSH to Ivan to mirror ~/.openclaw/gateway.env
5. Dispatch WO to Leo for openclaw.json update
6. Smoke test: location-scoped GET contacts must return HTTP 200
7. Write memory pointer: reference_ghl_pit_token_current.md (pointer to Vault row, NOT a copy of the value)

### 8. GitHub, Archive Only (not canonical)

---

## Contradiction Detector, Run Before Writing Any New Rule

1. Search existing rules for the keyword
2. If contradicting rule exists: STOP. Report both. Get clarification.
3. If near-duplicate: merge, do not duplicate.
4. Only then write.

---

## Diamond Verify, Required on Every "memory updated" / "credential updated" Claim

1. Source Lock: Did I write to the PRIMARY canonical location? (Vault for credentials, Drive for memory/skills.)
2. Receipt Required: Drive fileId, Notion MCP response (Vault page edit confirmation), Slack ack from Ivan-CC, or token-probe 200 receipt.
3. Three-Line Proof: SOURCE / CLAIM / PROOF.

Any check fails, claim is NOT done. Add to open_diamond_items in autopilot-state.json.

---

## Rules

- ALWAYS store uniform agent workflow changes in Drive-canonical memory or a Drive-canonical skill, not local-only notes
- ALWAYS include the v9.1 five-step workflow contract when saving agent-behavior memory
- ALWAYS pass the credential recall-gate (Step 0.35) before any "I do not have / expired" claim
- ALWAYS read the Notion Credential Vault FIRST for credential self-heal, Slack/Gmail are fallback only
- ALWAYS write recovered credentials to the Vault FIRST, gateway.env is a mirror
- ALWAYS run repeat-explanation check FIRST when triggered
- ALWAYS run contradiction detector before writing new rules
- ALWAYS Diamond-verify every memory/credential write before claiming done
- NEVER claim a credential is expired/missing without a Vault read plus token-probe receipt under 15 min old
- NEVER probe GHL PITs with users/me (always 404, not expired), use location-scoped contacts
- NEVER delete without replacement unless explicitly asked
- NEVER self-reference in deps frontmatter
- Drive is canonical for memory/skills, Vault is canonical for credentials, they win on conflict
- Leo handoff is not a substitute for DIY; use Leo only for cron/LaunchAgent/cross-machine ownership or proven unreachable machines
- GitHub is archive only, never source of truth
- bennett-rules.md max 1000 chars, prune oldest on overflow
- iCloud sync on Ivan is OFF, do not ask Bennett about this (confirmed 3x)
- Mack in autopilot mode does ZERO CLI, delegates via Slack WO

---

## Anti-Patterns (6)

1. Self-referencing deps: v3 listed memory-protocol as a dep of itself. v4 removes.
2. Char-cap drift: v3 said 1000 but one section still said 500. v4 unified.
3. SSH-IP swap: v3 mixed up Tailscale IPs. v4 explicit table.
4. Silent CLI attempt from Mack: Mack tries bash, no sandbox, silent failure. v4 forces WO emission.
5. Zero-receipt "memory updated": claim without fileId / Slack ack / Notion API response.
6. Write/read mismatch on credentials (v9): recovering a token to gateway.env but not the Vault, then a future session reads the Vault, sees nothing, and falsely claims "expired". The durable copy IS the Vault.

---

## Changelog

- v9.3 (2026-05-30): Skill audit patch — 6 genuine fixes: (1) Added trigger phrases "search for this/remember this/store this/log this" to frontmatter. (2) Fixed receipt schema mismatch — required fields `thread` and `verified` now documented and enforced in Self-Audit item 1. (3) Corrected receipt file path from ~/.openclaw/logs/ to ~/.openclaw/state/. (4) Expanded Step 6 memory paths to document BOTH active Ivan dirs (-Users-openclaw/ and -Users-openclaw-Ivan---Imac/). (5) Added Drive fileId (1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui) to bennett-rules.md Tier-0 section + cap-breach enforcement action. (6) Mack repeat-flags write in Step 0.5 now guarded by Tailscale liveness check — no more silent failures.
- v9.1 (2026-05-27): Added Uniform Agent Workflow Memory Gate: Drive first, council before permanence, DIY before handoff, Diamond before done, recap every response. Clarified Leo-only-for-cron/cross-machine ownership.
- v9 (2026-05-26): Notion Credential Vault equals single canonical credential store. Added Step 0.3 SessionStart credential manifest, Step 0.35 recall-gate, GHL location-scoped probe fix, GHL_PIT_TOKEN canonical name, Vault-first self-heal. Closes write/read mismatch.
- v8 (2026-05-25): Added Self-Audit Checklist plus Cron Bindings per angie-weekly-audit-skill v7 / skill-creator-skill v11 mandate. Angie W22 sweep.
- v7.2 (2026-05-23): Step 0.4 Known Errors and Solutions Registry.
- v7.1 (2026-05-09): Live Thread Projects Notion DB plus receipts protocol.
- v7 (2026-05-04): Drive-canonical architecture.
- v6 (2026-05-01): Strengthened Bennett correction: Drive first.
- v5 (2026-05-01): Canonicalized skills source wording.
- v4 (2026-04-26): Step 0 Boundary Gate, Diamond Verify, Strike escalation.
- v3 (2026-04-25): Repeat-explanation prevention, contradiction detector.
- v2: Initial Tier 0 / Drive canonical / CLAUDE.md split.

---

## Self-Audit Checklist (used by angie-weekly-audit-skill v8+)

Angie uses this checklist as the SOP rubric when auditing the memory/storage business area.

1. [ ] memory-skill-receipts.jsonl updated in last 24h at ~/.openclaw/state/memory-skill-receipts.jsonl (NOT ~/.openclaw/logs/) — tail -1 | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'thread' in d and 'verified' in d, 'SCHEMA MISSING thread/verified'"
2. [ ] repeat-flags.md exists and was reviewed in last 30 days on Ivan; Mack write only after Tailscale liveness confirmed
3. [ ] bennett-rules.md is less than or equal to 1000 chars: wc -c ~/.openclaw/memory/bennett-rules.md — if >1000, prune AND re-upload to Drive fileId 1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui immediately
4. [ ] Leo SOUL is less than or equal to 11 lines: wc -l /Users/openclaw/.openclaw/agents/leo/agent/SOUL.md
5. [ ] token-probe.sh ran in last 7 days, receipt exists at ~/.openclaw/state/token-registry.json
6. [ ] No memory file in MEMORY.md index is more than 30 days stale (stat each file, compare mtime)
7. [ ] Drive canonical copies of skills are newer than local ~/.claude/skills/ cache (spot-check 3 skills)
8. [ ] (v9) Notion Credential Vault 341cf5514fd381fe993de8add7eb265e has a last_verified date under 7 days for every service in the manifest, no skill or script reads a credential from anywhere but the Vault (or its gateway.env mirror)
9. [ ] (v9.1) Any agent-behavior memory update contains the five-step uniform workflow contract
10. [ ] (v9.1) Any Leo handoff in memory shows DIY exhausted or cron/cross-machine ownership

## Cron Bindings

None. This skill is invoked on-demand by Bennett or an upstream skill. No scheduled LaunchAgent or cron job owns this skill.
