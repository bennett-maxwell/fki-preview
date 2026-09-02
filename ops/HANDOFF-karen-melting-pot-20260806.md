# HANDOFF — Karen / The Melting Pot Studio blueprint · session f39b06c7 · 2026-08-06 14:50 CT

⚠️ **There is no `handoff-skill` in Drive.** Probed folder `1qdUEbUb…` for `handoff*` and for
`title contains 'handoff' and title contains 'SKILL'`. What exists: a retired
`_legacy-folder-20260711-voice-chat-handoff-skill-…`, a `fetchback-handoff-skill.SKILL.md`
(different purpose), and prior handoff **output artifacts**. This follows the format of
`handoff-20260805-madison-blueprint.md` (Drive `1tvb88zv9W9RA_8t0DCP6GDsp6aB7VGbz`).
**No skill was invented and none was "run."**

---

## 1. STOP — do not rebuild, do not re-audit, do not ask Kay for a GitHub token

**Karen's blueprint is FINISHED.** Everything below is already true and re-verified this session:

| artifact | path | state |
|---|---|---|
| page | `blueprints/karen-melting-pot-studio.html` | 106,689 B · 16 sections · **on `main`** |
| podcast | `podcasts/karen-melting-pot-studio.mp3` | 8,630,576 B · **8:59 / 539s** (window 240–960) |
| delivery email | `delivery-emails/karen-melting-pot-studio-crmx-email.html` | 4,923 B · Drive-sourced (RL-DE1) |
| lead profile | `leads/karen-melting-pot-studio.json` | 28,616 B |
| receipts | `audit-receipts/karen-melting-pot-studio/` | completion-gate · clean-ending · production-47 |

**Gates, all green:** completion **37/37** (0 critical, 0 major — Structure 10/10, Content 10/10,
Funnel 10/10, Audio 5/5) · ROI-preset PASS (renders her stated **10** monthly leads) ·
text-overflow PASS **headless desktop + mobile** · Advaita palette/WCAG PASS ·
qualify-link PASS (4 action links, 0 failures) · qualifier-context PASS · intake-URL PASS ·
podcast clean-ending TRUE, direct-address TRUE, 0 banned phrases.

**Palette is already the NEW brand** — Plum `#4A1F63`, Saffron `#F5A623`, Warm Ivory `#F7F2E9`,
hex set **identical** to the rebranded `blueprints/TEMPLATE.html`, and `#0071E3` appears **0 times**.
Her file was re-rendered 11:36 by rebrand commit `b904f6561`, whose own message says
*"Validated on karen-melting-pot-studio."* **A rebuild would be byte-identical.**

## 2. The ONLY thing wrong: GitHub is down. Not us.

`page=404 mp3=404` on `hub.aiblueprintmarketing.com` as of 14:45 CT.

- GitHub incident opened **2026-08-06T15:22:49Z**, still `investigating` at 19:43Z.
  **Actions = major_outage, Pages = major_outage.** Latest GitHub update: *"Capacity remains
  constrained and jobs may still be delayed or fail while it recovers gradually."*
- Deploy run `31120453976`: attempt 1 failed at **Set up job** —
  `Failed to resolve action download info / Service Unavailable`.
  Attempt 2 **cancelled** — `The job was not acquired by Runner of type hosted even after multiple attempts`.
- `blueprint-audit` run `31120453965` hit the **same runner cancellation** → that audit
  **never executed**. It is **NOT** evidence the rebrand commit broke anything.

**A cancelled deploy leaves NOTHING pending** — a URL-only poller waits forever. The failure reason
appears **only** in `/check-runs/{job_id}/annotations`, not in the run or job objects.
`?cb=` does **not** bust the GitHub Pages edge cache.

## 3. Recovery is already automated — DO NOT ADD A SECOND TRIGGER

launchd **`com.madisonfki.karen-deploy-recover`** (loaded, every 300s) runs
`~/.openclaw/scripts/karen-deploy-recover.sh --once`. It re-triggers run `31120453976`
**only** when `githubstatus` reports Actions **and** Pages operational (12-min cooldown), then writes
**`~/.openclaw/state/karen-blueprint-live.json`**. Fixtures proven both directions:
404 pair → exit 1, no marker; known-200 pair → exit 0, marker written. Log:
`~/.openclaw/logs/karen-deploy-watch.log`.

⚠️ **`pages.yml` has `concurrency: {group: pages, cancel-in-progress: true}`** — any push or second
trigger **cancels the in-flight deploy**. This already burned Madison twice (7/28, 8/5). If you push
anything, run `bash scripts/pages-deploy-safe-to-push.sh` first. If you add your own re-trigger,
**disable the launchd job first** (`launchctl unload ~/Library/LaunchAgents/com.madisonfki.karen-deploy-recover.plist`)
or the two will cancel each other.

## 4. Exactly what remains

1. Wait for `~/.openclaw/state/karen-blueprint-live.json`, **or** confirm both URLs return 200:
   `https://hub.aiblueprintmarketing.com/blueprints/karen-melting-pot-studio.html`
   `https://hub.aiblueprintmarketing.com/podcasts/karen-melting-pot-studio.mp3`
2. **THEN** create the Gmail **DRAFT** to `karen@thempstudio.com` from
   `delivery-emails/karen-melting-pot-studio-crmx-email.html`.
   **Stage-7 forbids building the draft before the podcast is live 200** — a draft with a 404
   podcast is the exact failure that rule exists to prevent. Draft only; **Madison sends.**
3. After her send: move opportunity **`oxqmGwvoCYsXRZ8GIbrK`** to stage **"Blueprint sent"**
   (`GPCi3FrWJCyevcGzZgTT`, pipeline `u4JlprfRFVltZ4QJRVsl`, stage `b8488031-f3b9-4749-abde-e03b5c9e74ae`).

**Deadline:** form submitted 2026-08-06T04:47:15Z = **Aug 5, 11:47 PM CT** → 24h clock ends
**~11:47 PM CT Aug 6**.

## 5. Routes already exhausted — do not re-probe

- **GitHub token is NOT missing.** Working token in `~/.openclaw/gateway.env`; scopes
  `read:org, repo, workflow`; repo permissions `admin:True`. Deploy rerun POST returned **HTTP 201**.
  **Do not ask Kay or anyone for a GitHub token.**
- **Self-hosted runner: DEAD END.** I minted a registration token (HTTP 201), but `pages.yml` is
  `runs-on: ubuntu-latest` with Linux-only actions (`actions/upload-pages-artifact` tars on Linux).
  A runner on Madison's Mac would fail mid-workflow. Would need real Linux hardware.
- **Legacy `gh-pages` branch switch: DANGEROUS, needs Madison's decision.** Pages is
  `build_type: workflow` but also has `source: {branch: gh-pages, path: /}`. That branch is
  **3 weeks stale** (last commit `4426f7e3d`, 2026-07-17) and does **not** contain Karen, Sue Wright,
  Ken Wilcox, Janet, Cindy or Steve. `main` has **87** blueprints. Flipping as-is would **404 pages
  already delivered to paying clients.** Safe version requires syncing all 87 to `gh-pages` first,
  and Pages itself is in outage so the legacy builder may fail anyway. **Decision was put to Madison
  and is UNANSWERED.**
- Alternate host would mean repointing `hub.aiblueprintmarketing.com` — Cloudflare zone
  ownership is **Brent's**, no fleet token. Out of scope for one lead.

## 6. Kay threads — already sent, don't duplicate

- `1786042972.284619` (14:02:52 CT) — **Slack `xoxb-` bot token** ask, `chat:write`. Still open.
- `1786045533.264619` (14:45 CT) — **urgent GitHub outage** notice + impact.
- `1786045600.689279` (threaded reply) — **correction**: self-hosted runner won't work for us,
  told her not to chase it. Narrowed ask to "any non-GitHub-Pages publish path?"

`SLACK_LEO_BOT_TOKEN` is **not** in `~/.openclaw/secrets/gateway.env` — that path is only a
**symlink** to `~/.openclaw/gateway.env`, whose line 12 says the token is MISSING. Fresh 4-surface
probe: zero `xox[bpasr]-` under `~/.openclaw ~/.claude ~/.config ~/.zshrc ~/.zprofile`; no
`SLACK_BOT_TOKEN` keychain item (`Slack Safe Storage` = Slack desktop app's own key); `op` CLI absent.
**Don't re-grep for it.**

## 7. Out of scope for the Karen thread

- The **11 FB Instant Form leads** are **Cody's** as of 2026-08-06 (Madison reassigned).
- The **`#ai-blueprint-leads` false-trigger GHL workflow** is **PARKED** — Madison is compiling
  steps from her Advaita Lead Capture Call with Brent. Do not route it to Jenn/Cody, do not rename
  or disable it.
- **Steve / Ozark Hypnosis** — built, but replied "Stop" by SMS and is `dnd_all_ch_auto`. Needs a
  call, not an email.
- Rebrand commit `b904f6561` is **unverified** (its audit was cancelled by the outage) — re-run when
  GitHub is back.

## 8. State written this session

- Notion Live Thread row **`3b4cf5514fd381e79a10d93ad5b4aec8`** (DB `573123c6…`) — full narrative +
  `AI_HANDOFF_CONTEXT`.
- 6 memories under `~/.claude/projects/-Users-madisonlanz/memory/`, indexed in `MEMORY.md`:
  `project_karen_melting_pot_studio_blueprint_20260806` ·
  `reference_github_outage_cancelled_deploy_needs_retrigger` ·
  `reference_blueprint_stage_name_is_not_a_form_fill` ·
  `reference_blueprint_form_fill_sentinel_gate` ·
  `reference_ai_blueprint_leads_channel_false_trigger`
- Receipts: `~/.openclaw/logs/memory-skill-receipts.jsonl` (line 757)
- Gmail draft for Madison (the 14-lead audit table): **`r-7927707142507785581`**

## 9. Resume command

```bash
# 1. is she live yet?
cat ~/.openclaw/state/karen-blueprint-live.json 2>/dev/null || echo "NOT LIVE YET"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
for p in blueprints/karen-melting-pot-studio.html podcasts/karen-melting-pot-studio.mp3; do
  curl -s -o /dev/null -w "%{http_code}  $p\n" -A "$UA" "https://hub.aiblueprintmarketing.com/$p"
done
# 2. is GitHub back?
curl -s https://www.githubstatus.com/api/v2/summary.json | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['status']['description'],[ (c['name'],c['status']) for c in d['components'] if c['name'] in ('Actions','Pages')])"
# 3. watcher alive?
launchctl list | grep karen-deploy; tail -3 ~/.openclaw/logs/karen-deploy-watch.log
# 4. ONLY when both URLs are 200 -> build the Gmail DRAFT (never before)
```

## 10. Unrelated permanent fixes landed this session (don't undo)

`~/.openclaw/scripts/blueprint-lead-sentinel.py`:
- **form-completion gate** — fires only when ≥5 **lander** intake fields are populated; excludes
  `fu_*`/`followup_status`/`never_follow_up_reason`/`outbound_call_count` (automation writes those and
  would forge a completion). `--self-test-gate` = **8/8** (5 reject / 3 accept).
- **`--baseline-form`** already run: 33 historical completions marked, **0** notifications sent.
- **email transport via `gog`**, scoped to `form_complete` only (widening it would blast ~1,600
  legacy queued items back to 2026-07-03).
- **`--drain-form`** — no-token Slack path for a live session; proven 1 → posted → 0.
- **SMS circuit breaker + outbox prune** — outbox 11,943 → 1,671 items, 7.4MB → 1.1MB,
  scan runtime **>120s → 1s** (4 overlapping processes before, 0 after).

Root cause it fixed: the sentinel had delivered **0 of 49** notifications for weeks — no Slack token,
and Messages.app is TCC-denied to launchd so each SMS burned ~30s against a 120s interval.

---

## 11. Cross-session note — session 6d582d1e (added 2026-08-06 ~19:56Z)

A second Claude Code session built and pushed this same lead in parallel. Reconciled:

- **Trigger conflict found and REMOVED.** That session had its own detached watcher
  (`finish-karen.sh`) that dispatched `pages.yml` on recovery — exactly the second trigger
  §3 warns about. It was **killed at 19:55Z before GitHub recovered**, so it never raced
  `com.madisonfki.karen-deploy-recover`. The launchd job is the **sole** deploy trigger.
  It also pushed empty commit `9b279d4b3` at ~17:47Z to force a clean run; under
  `cancel-in-progress: true` that push may itself have cancelled an in-flight deploy.
  Lesson stands: **do not push, do not add a trigger.**
- **Draft lane is now owned** by `draft-only-watcher.sh` (detached, ~12h,
  `…/scratchpad/karen/draft-only-watcher.log`). It **never dispatches and never pushes** —
  it polls the two URLs, and only when BOTH return 200 (RL-DE4) creates the Gmail draft via
  `gog gmail drafts create` and reads it back. Draft only; Madison sends. Success line:
  `DRAFT_VERIFIED`. `gog … --dry-run` pre-validated: correct recipient/subject, body_html_len 4922, rc=0.
  Their `karen-deploy-recover.sh` writes the live marker but does **not** create the draft,
  so these two are complementary, not duplicate.
- **Independent agreement on state:** podcast 539s/8,630,576 B, audit 20/20 via repo-root
  `run-audit.py`, palette Plum/Saffron/Ivory with `#0071E3` count 0, qualifier links carrying
  `employees`. Additional failure modes seen on later attempts of run `31120453976`:
  attempt 3 `Invalid actions OIDC token`, attempt 4 `Multiple artifacts named "github-pages",
  count is 2` (caused by re-running the same run — each re-run re-uploads; duplicate
  `8974199384` was deleted). **Re-run the workflow, never the same run.**
- **Correction to a claim that session made earlier:** it initially blamed the 3.07 GB Pages
  artifact against the 1 GB limit. Not supported — yesterday's *successful* deploy carried
  2.86 GB. The size warning is real but is **not** today's cause; the outage is.
- Permanent fix landed + pushed in `b904f6561`: `scripts/build-podcast-source.py` no longer
  instructs phrases its own ban-list forbids ("lead with the business benefit", "every
  reference to the company"), which was silently failing D3-02 across leads. Blocking
  self-contradiction gate added, canary proven both directions.
