---
name: fleet-memory-skill
drive_file_id: 1kE1web8T1HKD-M7u8OirfxhGPduOU002
version: 2.3
---

# fleet-memory-skill
**Version:** 2.3 | **Updated:** 2026-06-04 | **Owner:** Bennett Maxwell
**Drive folder ID:** 1ONFawFvQpitk8xWsYZvSyPNEFZe17TqH
**Drive file ID:** 1kE1web8T1HKD-M7u8OirfxhGPduOU002
**Employee template v2.0:** 18VdhJbKQgLgvY17rB1t0NFXbdAxfl9Qb
**Notion Credential Vault:** 341cf5514fd381fe993de8add7eb265e

---

## PURPOSE
Teaches any AI agent how to bootstrap a brand-new machine's memory, CLAUDE.md, skills
structure, and Drive connections, from scratch. Use whenever onboarding a new employee
machine, recovering a crashed agent, or syncing a machine that's been offline.

**v2.1 update (2026-05-26):** CREDENTIAL CARVE-OUT. The general rule "memory is NOT
automatically shared" is now OVERRIDDEN for credentials. Every agent reads the ONE
Notion Credential Vault (341cf5514fd381fe993de8add7eb265e) as the live shared credential
object via Notion MCP. Bootstrap now loads the Vault. Source: memory-skill audit,
Bennett-approved 2026-05-26.

**v2.0 update (2026-05-21):** Added the RULES.md boot step, the critical missing piece
that caused employee agents to behave differently from Bennett's agents. All employee
CLAUDE.md files must load RULES.md (Drive: 1L02oYv0aipmIV-7vYcwxzSYCFUka96kB) at boot
Step 2. This is what gives employees 100% identical behavioral functionality.

---


## NO-EARLY-STOP FLEET BEHAVIOR (v2.3 — HARD RULE)

Every employee agent, Claude Code seat, Hyperagent seat, and Codex/Chad surface must follow this behavior:

1. Yellow, partial, AI OPEN, or blocker status is an execution queue, not an ending.
2. Before finalizing, identify the next blocker-clearing action.
3. If the action is safe and reversible and does not send externally, delete, spend, expose secrets, change credentials, or move legal/financial documents, execute it now. Repeat for up to 3 safe attempts before requiring a bounded continuation receipt.
4. After execution, fetch/read back the canonical Drive/Notion proof and rerun gatekeeper, memory-sync, manifest, or the relevant verifier.
5. Stop only when the blocker is cleared, the remaining gate is truly human/protected/platform-limited, or a bounded continuation receipt exists.
6. Never use local memory, local receipts, local skills, or chat wording as proof of a fleet behavior change. Drive/Notion canon plus fetchback is required.

Canary: If an agent says “Yellow because X is missing” and X can be fixed by patching a Drive skill or Notion row safely, the correct next move is to patch/fetchback/rerun, not report Yellow and end.

## THE TWO-LAYER ARCHITECTURE (why it works)

Layer 1, CLAUDE.md (50 lines or fewer, identity plus boot pointers only)
 - Who am I
 - 5 hardcoded red lines (minimum always-remember set)
 - Boot sequence with explicit Drive/Notion URLs

Layer 2, RULES.md (Drive: 1L02oYv0aipmIV-7vYcwxzSYCFUka96kB)
 - ALL behavioral rules (15-plus)
 - Model assignments
 - Memory routing
 - Slack UIDs
 - Google Doc share rule
 - Agent routing hierarchy
 - Security governance

**Result:** Update RULES.md once, ALL agents (Bennett plus all employees) get the change
automatically on next boot. No drift. No per-file maintenance.

---

## WHAT "FLEET MEMORY" MEANS (v2.2 — CAPABILITY SYMMETRY)

**The brain is centralized in Google Drive. Every agent points at the same Drive, so every agent
has the EXACT SAME capabilities.** Skills, rules (RULES.md + bennett-rules.md), and credentials
(the Notion Credential Vault) are ONE shared object the whole fleet reads. No agent is more capable
than another. Nobody waits on Mack. Nobody waits on Ivan. The only thing that differs per machine is
*identity* (name, role, hostname) — never *capability.*

What IS shared fleet-wide, live (the actual brain):
- **Skills** — one canonical SKILL.md per skill in Drive folder `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY`.
  Every agent loads the same skill. A skill improvement is inherited by all agents on next load.
- **Rules** — RULES.md (`1L02oYv0aipmIV-7vYcwxzSYCFUka96kB`) + bennett-rules.md
  (`1OPx_UM1oOpGz3xxPAEy1wOxTuFQAT6ui`). Update once → all agents get it on next boot.
- **Credentials** — the ONE Notion Credential Vault (`341cf5514fd381fe993de8add7eb265e`). Every
  agent reads/writes the same Vault via Notion MCP; gateway.env on each machine is only a mirror
  refreshed from the Vault. No private credential copies.
- **Project state** — Notion + Drive (never local `~/.openclaw/`, `/tmp/`, or local files).
- **No-early-stop behavior** — Drive-canonical memory/governance rule v2.3. Yellow/partial with a safe AI-owned next step must execute before closeout.

The ONLY thing that is per-machine is the **local `MEMORY.md` cache** — and that is a *mirror, not a
source of truth.* Durable memory belongs in Drive/Notion (where every agent can read it), exactly so
that capability never silos. A local cache going stale must never make one agent "know" something
another can't; if it does, that's a bug to fix by pushing the memory to Drive, not an accepted state.

(Prior versions of this skill said "general memory is NOT automatically shared." That framing was
retired in v2.2 because it implied accepted capability asymmetry. Corrected per Bennett directive
2026-05-29: agents are capability-symmetric; the local cache is just a mirror of the Drive brain.)

To bring a new machine into the fleet with full operational context:

1. **Install Claude Code** (get the binary running)
2. **Write CLAUDE.md v2.0** (agent identity plus Drive pointers plus RULES.md boot step)
3. **Mirror the skills structure** (local stub pointing to Drive)
4. **Bootstrap memory** (copy key memories from Ivan's memory store)
5. **Load the Credential Vault** (Notion MCP read of 341cf5514fd381fe993de8add7eb265e) — v2.1 NEW
6. **Verify Drive connections** (Google Drive MCP access)
7. **Test fleet connectivity** (Tailscale plus SSH)

---

## STEP-BY-STEP: ONBOARDING A NEW EMPLOYEE MACHINE

### Phase 1, Prerequisites (on new machine)
```
1. Tailscale installed and connected to Bennett's tailnet
2. Claude Code CLI installed:
   - macOS: npm install -g @anthropic-ai/claude-code
   - Windows: npm install -g @anthropic-ai/claude-code (after Node.js install)
3. Git installed (required for Claude Code)
4. SSH enabled (for Ivan to push files)
```

**For Windows machines:** Run jen-windows-bootstrap.ps1 (on Desktop of Ivan) as
Administrator. Handles steps 2-4 plus CLAUDE.md creation.

### Phase 2, Write CLAUDE.md v2.0

Fetch the template from Drive: **18VdhJbKQgLgvY17rB1t0NFXbdAxfl9Qb**

Replace all placeholders:
- AI_NAME, e.g. "Christelle CC", "Chad CC", "Jade"
- EMPLOYEE_NAME, Full name
- ROLE, Job title
- EMAIL, firstname@franchiseki.com
- PLATFORM, "Claude Code (terminal)" or "Hyperagent (browser)"
- PROJECT_HUB_URL, Their Notion project hub page
- PROJECT_TABLE, Their project table (name, link, role, status)

**Known AI identities:**
| Employee | Machine | AI Name | Platform |
|---|---|---|---|
| Bennett | iMac (Ivan) | Ivan CC | Claude Code |
| Bennett | MacBook (Mack) | Mack | Claude Code |
| Kay | MacBook Air | Kay CC | Claude Code |
| Jenn Penas | Windows PC | Jade | Hyperagent |
| Christelle | TBD | Christelle CC | Hyperagent |
| George | TBD | George CC | Hyperagent |
| Madison | TBD | Madison CC | Hyperagent |
| Cody Johnson | TBD | Cody CC | Hyperagent |
| Stephen | TBD | Stephen CC | Hyperagent |
| Bailey | TBD | Bailey CC | Hyperagent |

### Phase 3, Create .claude Directory Structure

**macOS:**
```bash
mkdir -p ~/.claude/skills
mkdir -p ~/.claude/projects/$(echo ~/ | sed 's|/||g')/memory
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\skills" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\projects\-Users-jenn\memory" -Force
```

### Phase 4, Mirror Skills Structure

```
~/.claude/skills/
  machines-skill/
    SKILL.md (stub with Drive ID 1FQ6c_xnxPSEsVPRQ7mxaHpwyqHxBqmxk)
  tailscale-skill/
    SKILL.md (stub with Drive ID 1luc4dqIE2hPpTKMyR32dvTgcqgyB1U9S)
  fleet-memory-skill/
    SKILL.md (stub with Drive ID 1ONFawFvQpitk8xWsYZvSyPNEFZe17TqH)
```

**Ivan can push these via SSH after bootstrap:**
```bash
NEW_MACHINE="employee@100.x.x.x"
ssh $NEW_MACHINE "mkdir -p ~/.claude/skills/machines-skill"
scp ~/.claude/skills/machines-skill/SKILL.md $NEW_MACHINE:~/.claude/skills/machines-skill/SKILL.md
```

### Phase 5, Bootstrap Key Memories

```bash
# From Ivan, after SSH is working
NEW_MACHINE="employee@100.x.x.x"
MEMORY_PATH="~/.claude/projects/-Users-employee/memory"

scp ~/.claude/projects/-Users-openclaw/memory/MEMORY.md \
    $NEW_MACHINE:$MEMORY_PATH/MEMORY.md
```

**Key memories to bootstrap on every new machine:**
1. feedback_recap_every_response.md, recap-skill rule
2. feedback_token_rotation_ai_owned.md, never surface tokens as gates
3. reference_ghl_oauth_pattern.md, GHL token refresh pattern
4. Machine-specific: tailscale-skill reference, machines reference

### Phase 5.5, Load the Credential Vault (v2.1 NEW)

The new agent MUST be able to read the ONE Notion Credential Vault. This replaces any
per-machine private credential store. Bootstrap step:
1. Confirm Notion MCP is configured on the new agent.
2. Read the Vault: notion-fetch 341cf5514fd381fe993de8add7eb265e.
3. Confirm the agent can see the compact credential manifest (service, status, last_verified).
4. The agent's gateway.env is a MIRROR only, refreshed from the Vault at SessionStart, never
   the source of truth.
5. HARD RULE (matches memory-skill v9): no agent claims a credential expired/missing without
   a Vault read plus a token-probe receipt under 15 min old. GHL probe is location-scoped
   (canonical var GHL_PIT_TOKEN), never users/me.

### Phase 6, Verify Drive Access

Agent must confirm Google Drive MCP configured and can read RULES.md:
Drive ID to test: 1L02oYv0aipmIV-7vYcwxzSYCFUka96kB

### Phase 7, Test Fleet Connectivity

```bash
# From Ivan
tailscale status | grep <new_hostname>
ssh <user>@<tailscale_ip>
ssh <user>@<tailscale_ip> "claude --version"
```

---

## RECOVERY: AGENT CRASHED / MEMORY LOST

1. SSH from Ivan: ssh <user>@<tailscale_ip>
2. Restore CLAUDE.md from Drive template: 18VdhJbKQgLgvY17rB1t0NFXbdAxfl9Qb
3. Restore MEMORY.md from Ivan's copy
4. Re-load the Credential Vault (notion-fetch 341cf5514fd381fe993de8add7eb265e) — credentials
   survive the crash because they live in the Vault, not the lost local cache.
5. Run claude --resume to pick up last session if JSONL exists

---

## CLAUDE CODE SETTINGS.JSON PUSH

Ivan's settings.json contains MCP server configs (Drive, Gmail, Slack, Notion, etc.):
```bash
NEW_MACHINE="employee@100.x.x.x"
scp ~/.claude/settings.json $NEW_MACHINE:"~/.claude/settings.json"
# NOTE: Push only over Tailscale, settings.json contains real API tokens
```

---

## KEY DRIVE / NOTION IDs, ALL AGENTS MUST KNOW

| Resource | ID |
|---|---|
| Notion Credential Vault (ALL credentials) | 341cf5514fd381fe993de8add7eb265e |
| Skills folder | 1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY |
| RULES.md (behavioral kernel) | 1L02oYv0aipmIV-7vYcwxzSYCFUka96kB |
| Employee CLAUDE.md v2.0 | 18VdhJbKQgLgvY17rB1t0NFXbdAxfl9Qb |
| machines-skill | 1FQ6c_xnxPSEsVPRQ7mxaHpwyqHxBqmxk |
| tailscale-skill | 1luc4dqIE2hPpTKMyR32dvTgcqgyB1U9S |
| fleet-memory-skill folder | 1ONFawFvQpitk8xWsYZvSyPNEFZe17TqH |
| council-skill | 18edfLllHikArUABu7l_feBxFWfiLncAY |
| recap-skill | 1e9nw03yKQ9tjD4k3zEBAhQsEnH0qZWe6 |

---

## QUICK REFERENCE: FLEET ONBOARDING CHECKLIST

```
[ ] Tailscale connected (verify: tailscale status from Ivan)
[ ] SSH enabled plus Ivan's pub key in authorized_keys
[ ] Git installed
[ ] Node.js installed
[ ] Claude Code CLI installed
[ ] claude login completed (Anthropic API auth)
[ ] CLAUDE.md v2.0 written, identity plus RULES.md boot step confirmed
[ ] RULES.md boot verified (agent can read Drive ID 1L02oYv0aipmIV-7vYcwxzSYCFUka96kB)
[ ] Credential Vault verified (agent can notion-fetch 341cf5514fd381fe993de8add7eb265e)
[ ] .claude/skills/ directory exists
[ ] Key skill stubs created (machines, tailscale, fleet-memory)
[ ] MEMORY.md bootstrapped with fleet-wide memories
[ ] settings.json pushed (includes Drive/Slack/Gmail/Notion MCPs)
[ ] Drive MCP verified working (read RULES.md as test)
[ ] Claude Code session launched, agent replies correctly with name plus task count
[ ] Entry added to machines-skill Drive doc
[ ] Entry added to tailscale-skill fleet table
[ ] Slack post to #leo-auto confirming new agent online
[ ] Angie recurring audit added for this employee (Sunday 23:00 MDT)
```

---

## WHEN TO UPDATE RULES.md vs CLAUDE.md vs CREDENTIAL VAULT

Update RULES.md (Drive: 1L02oYv0aipmIV-7vYcwxzSYCFUka96kB) when:
- Adding/changing a behavioral rule for ALL agents
- Updating Slack UIDs
- Changing model assignments
- Updating memory routing

Update CLAUDE.md template (Drive: 18VdhJbKQgLgvY17rB1t0NFXbdAxfl9Qb) when:
- Changing the boot sequence itself
- Changing the hardcoded top-5 red lines
- Changing session close steps

Update the Notion Credential Vault (341cf5514fd381fe993de8add7eb265e) when:
- Any API key, token, password, or OAuth value changes or rotates
- A token probe confirms a new last_verified date
- A new service is added to the fleet
- NEVER store a credential value anywhere else, not in a skill, not in MEMORY.md, not in a
  per-machine file. gateway.env is a mirror only.

Update individual employee CLAUDE.md when:
- Their name, role, email, or projects change
- NEVER for behavioral rules, those go in RULES.md, NEVER for credentials, those go in the Vault

---

## Changelog
- v2.1 (2026-05-26): Credential carve-out, the "memory is NOT automatically shared" rule is overridden for credentials. All agents read the ONE Notion Credential Vault as the live shared credential object. Added Phase 5.5 Vault bootstrap, Vault in onboarding checklist, recovery step 4, and update-routing guidance. Source: memory-skill audit, Bennett-approved.
- v2.3 (2026-06-04): No-early-stop fleet behavior. Yellow/partial/AI-open becomes the next execution queue when a safe reversible tool path remains; closeout allowed only after proof, true human/protected/platform blocker, or bounded continuation.
- v2.0 (2026-05-21): RULES.md boot step.
- v1.x: Initial fleet onboarding architecture.

---

## Self-Audit Checklist

Binary checks an auditor (Angie) can run to verify fleet-memory-skill is healthy:

- [ ] **RULES.md readable** — `mcp__claude_ai_Google_Drive__read_file_content(1L02oYv0aipmIV-7vYcwxzSYCFUka96kB)` returns content with ≥10 behavioral rules; confirms the fleet behavioral kernel is accessible.
- [ ] **Employee CLAUDE.md template readable** — Drive file `18VdhJbKQgLgvY17rB1t0NFXbdAxfl9Qb` returns content containing `AI_NAME` placeholder; confirms the onboarding template is intact and not overwritten with a real identity.
- [ ] **Notion Credential Vault reachable** — `notion-fetch 341cf5514fd381fe993de8add7eb265e` returns a page with at least one credential row; confirms every agent can load the shared credential object at boot.
- [ ] **Skills folder accessible** — Drive folder `1qdUEbUb_BpkVBt_YCX686nnu-O7lW0pY` lists ≥10 skill subdirectories; confirms the canonical skill library is mounted and not empty.
- [ ] **This skill's Drive file matches local** — Drive file `1kE1web8T1HKD-M7u8OirfxhGPduOU002` content matches the local `SKILL.md` version string (`v2.2`); confirms the local stub is not stale/diverged from Drive.
- [ ] **Fleet onboarding checklist is complete for all known agents** — each agent listed in the Known AI Identities table has a corresponding entry in machines-skill Drive doc (`1FQ6c_xnxPSEsVPRQ7mxaHpwyqHxBqmxk`); confirms no machine was bootstrapped without being registered.
- [ ] **No per-machine credential copies** — grep of gateway.env on Ivan and Mack contains no hardcoded token values that are NOT also present in the Notion Credential Vault; confirms the Vault-as-source-of-truth rule is enforced.
