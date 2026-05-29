# Blueprint AI — Verified Delivery Runbook

Canonical, reproducible SOP for delivering Blueprint AI roadmaps + podcasts and emailing a
verified summary. Any AI agent (Ivan, Mack, Leo, or a future agent on a fresh clone) follows
this exactly. The goal: **nothing reaches a prospect or Bennett until it is 100% verified.**

Last verified end-to-end: 2026-05-29 (15-blueprint two-link delivery, gatekeeper ledger ACCEPTED).

---

## 0. First thing after a fresh clone — install the gates

The verified quality gates live in the repo at `scripts/git-hooks/` but a fresh clone's
`.git/hooks/` is empty. Install them before doing anything else:

```bash
bash scripts/hooks/install-hooks.sh
```

This deploys:
- **pre-commit** — G16 SKILL.md gate strings, orchestrator validators, completion-gate, and
  D9 render-integrity (network-free). Blocks any commit of a defective blueprint.
- **pre-push** — HTTP 200 check on every changed blueprint HTML *and* the podcast MP3 it
  references. Blocks pushing anything not actually live.

Optional secondary gates in pre-commit (auto-heal, completion-gate) point at
`~/Documents/New project/scripts/`. They are `[ -f ]`-guarded: on machines without them they
self-skip. The primary gates (G16, orchestrator, D9) are portable (`$HOME`-based) and always run.

---

## 1. The 15 canonical blueprints

```
alex-ramos        austin-iron-horse   branson-maxwell   brent-attaway   brittney-warnick
chris-lpnw        court-lundberg      dave-wood         jaden-mecham    melissa-tash-srp
paul-muus         rey-31-consulting   rush-evans        watson          zachary-oldham
```

melissa-tash-srp is the gold-standard baseline. Clone from it for new leads.

---

## 2. URL patterns (the part that bites you)

- Blueprint: `https://bennett-maxwell.github.io/fki-preview/blueprints/<slug>.html`
- Podcast:   `https://bennett-maxwell.github.io/fki-preview/podcasts/<podname>.mp3`

**Podcast filename = `<slug>.mp3` EXCEPT two overrides:**

| slug            | podcast filename          |
|-----------------|---------------------------|
| watson          | `watson-kamoto.mp3`       |
| zachary-oldham  | `zachary-red-sands.mp3`   |

Do not guess podcast URLs. The pre-push hook auto-discovers the real path by grepping the
blueprint HTML for `podcasts/<name>.mp3`, so the override is mechanically enforced at push
time — but when you *build the email* you must use the correct override or the link 404s.

---

## 3. Generate / clone a blueprint

```bash
bash scripts/clone-blueprint.sh <slug> "<Business Name>"
```

The generator's Step 4 is a **hard blocking gate** (added 2026-05-29): it runs auto-heal →
D9 audit → pre-delivery check and **exits non-zero** if any fail. This is what stops an AI
re-emit from silently regressing a previously-verified fix. Do not bypass it.

---

## 4. Verify ONE blueprint (the 100% bar)

All three must pass before a blueprint is deliverable:

```bash
# (a) Pre-delivery mechanical (10 checks). --leads = the OTHER 14 names (cross-contamination grep).
bash scripts/pre-delivery-check.sh blueprints/<slug>.html \
  --leads "<comma-separated list of the other 14 names>"
#   → expect JSON  "overall":"PASS"

# (b) D9 render-integrity (20 binary checks). Pass --business-name to run all 20;
#     without it, only the D9-13 possessive check is skipped (other 19 still run).
python3 ~/.claude/skills/blueprint-ai-audit-skill/d9-audit.py blueprints/<slug>.html \
  --business-name "<Business Name>"
#   → expect exit 0

# (c) Live HTTP 200 — blueprint AND podcast
curl -s -o /dev/null -w "%{http_code}\n" \
  https://bennett-maxwell.github.io/fki-preview/blueprints/<slug>.html
curl -s -o /dev/null -w "%{http_code}\n" -I \
  https://bennett-maxwell.github.io/fki-preview/podcasts/<podname>.mp3
#   → expect 200, 200
```

Batch helper for all 15: `scripts/batch-pre-delivery.sh`.

---

## 5. Commit + push (gates run automatically)

```bash
git add blueprints/<slug>.html
git commit -m "..."   # pre-commit gate runs: G16 + orchestrator + completion + D9
git push              # pre-push gate runs: HTTP 200 on blueprint + podcast
```

NEVER use `--no-verify` and NEVER create `.blueprint-ci-skip` files — both hide real gate
failures (the rush-evans incident). If a gate fails, fix the blueprint, don't bypass the gate.
GitHub Pages caches; after push, the live URL may serve the previous content for a few minutes.
An invisible HTML-comment-only diff that is still 200 with valid content does **not** block
delivery (the live page is the previously-verified-100% content).

---

## 6. Email the summary (only when everything is 100%)

Orchestrate through **gatekeeper-skill**: workers produce, a *separate* auditor verifies,
ship only when score ≥ threshold + diamond PASS + a `pass_token` is issued.

Hard email rules (enforced by `~/.openclaw/bin/email-send.sh`):
- Recipient: **bennett@franchiseki.com ONLY**. Never brent@ (external prospect).
- One email, each person's NAME + TWO separate links (blueprint + podcast).
- ≥1500 bytes, 4 KPI cards (data-kpi="time"/"money"/"autonomy"/"memory"), subject 10–120 chars
  with a number or action verb, plain English (no jargon: no LaunchAgent/plist/SSH/Diamond/
  gatekeeper/UUID/msgId/token), no duplicate subject within 1h.
- Send only after §4 passes for all 15 (pre-delivery 15/15, D9 15/15, live URLs 30/30 = 200).

A gatekeeper run is not complete until a line is appended to
`~/.openclaw/state/gatekeeper-ledger.jsonl`. `shipped:true` is illegal unless
`pass:true` + `final_score ≥ threshold` + `diamond:"PASS"`; `pass_token` is required because
the artifact is Bennett-facing; `auditor_id` must not be in `worker_ids`.

---

## 7. Keeping the gates honest going forward

The committed hooks in `scripts/git-hooks/` are the single source of truth. If you change a
live `.git/hooks/` hook, re-sync it so the next agent inherits the change:

```bash
cp .git/hooks/pre-commit scripts/git-hooks/pre-commit
cp .git/hooks/pre-push  scripts/git-hooks/pre-push
git add scripts/git-hooks/ && git commit -m "sync verified git hooks to canonical dir"
```

If you don't re-sync, the next clone's `install-hooks.sh` deploys a stale gate — exactly the
reproducibility bug this runbook exists to prevent.
