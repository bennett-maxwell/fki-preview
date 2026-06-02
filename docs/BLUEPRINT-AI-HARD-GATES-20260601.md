# Blueprint AI Hard Gates - 2026-06-01

This file is the local repeatability receipt for the Blueprint AI output Bennett approved.
It does not replace the Drive skill. It records the repo gates that currently make the
output reproducible for every AI that works from this repository.

## Required Output Shape

Every new customer blueprint must use the Format-3 dense-scroll structure:

- exactly these sections, in order: `hero`, `profile`, `results`, `pillars`, `stack`, `gaps`, `oppmap`, `ignore`, `agents`, `timeline`, `calculator`, `prompts`, `demo`, `listen`, `sources`, `apply`
- top navigation links on the right, not a centered tab strip
- one custom chaptered podcast player only
- one `id="listen"` only
- all player IDs required by `scripts/format-conformance-check.py`
- no old tab CSS or JavaScript such as `.tab-nav`, `.tab-panel`, or `switchTab`

Mechanical gate:

```bash
python3 scripts/format-conformance-check.py blueprints/<slug>.html --podcast podcasts/<slug>.mp3
```

## Required Podcast Behavior

Every podcast must address the prospect directly by first name in the opening.
The source document and the audio must not frame the episode as an analysis of
source material.

Required opening family:

```text
Hi <first>, welcome. This walkthrough was built for you and <Business>, from what you told us.
```

Accepted variants include `Hello <first>` and `<first>, welcome` because speech recognition
sometimes drops the greeting.

Mechanical gates:

```bash
python3 scripts/podcast_direct_address_audit.py \
  --audio podcasts/<slug>.mp3 \
  --first-name "<First>" \
  --lead-name "<Full Name>" \
  --business-name "<Business>" \
  --lead <slug> \
  --seconds 180 \
  --receipt audit-receipts/<slug>/<slug>-production-47.json \
  --json-output

python3 run-audit.py --lead <slug>
```

Production public URL proof is enforced by `blueprint_completion_gate.py --require-production`
receipt #47, not by local pre-commit. This lets a new page deploy once, then verifies public
HTTP 200 after GitHub Pages serves it.

## Industry Drift Gates

The audit blocks common cross-industry failures:

- home-services pages cannot contain SaaS/client-success/proposal-demo leftovers
- restaurant, QSR, fast-casual, food-franchise, and food-chain pages cannot contain plumber, SaaS demo, support-ticket, or onboarding leftovers
- restaurant pages must contain restaurant language such as order, catering, guest, loyalty, rewards, location, restaurant, pickup, delivery, crew, or store

Mechanical gate:

```bash
python3 run-audit.py --lead <slug>
```

## Financial Realism Gates

The ROI calculator must match the lead's industry and intake values.
For food-franchise/restaurant leads, the transaction-value slider is a per-ticket range:

```text
min 8, max 60, unit ticket
```

Restaurant and other non-B2B leads must not show the LinkedIn lead-gen ROI lever.

Mechanical gate:

```bash
python3 financial-realism-check.py --file blueprints/<slug>.html
```

## Gatekeeper Closeout

Before any Bennett-facing or customer-facing send:

```bash
python3 scripts/blueprint_gatekeeper_100.py \
  --mode production \
  --lead <slug> \
  --html blueprints/<slug>.html \
  --receipt-dir audit-receipts/<slug> \
  --delivery-email delivery-emails/<slug>-delivery-email.html \
  --profile leads/<slug>.json
```

No email send is allowed without a production Gatekeeper pass token.
For customer send, receipt #48 must explicitly approve external customer delivery.

## Current Save Locations

- Repo audit code: `run-audit.py`
- Format gate: `scripts/format-conformance-check.py`
- Direct podcast gate: `scripts/podcast_direct_address_audit.py`
- Regression lock: `tests/test_blueprint_regressions.py`
- Canonical hook installer: `scripts/hooks/install-hooks.sh`
- Active Notion task: `https://www.notion.so/372cf5514fd38101ab1cd61446517f8e`

## Drive Skill Gap

As of 2026-06-01, the Drive `blueprint-ai-audit-skill` still contains the older audit
framework plus patch docs. These new Format-3/direct-audio/restaurant-drift rules are
repo-enforced and documented here. The next Drive skill update should merge this file's
rules into the canonical Drive `SKILL.md` in place, without creating a duplicate skill file.
