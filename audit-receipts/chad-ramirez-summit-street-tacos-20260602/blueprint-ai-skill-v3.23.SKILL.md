---
name: blueprint-ai-skill
version: 3.23
last_updated: 2026-06-02
patched_v3_23: "2026-06-02 — Chad controlled E2E proof-run runbook. Adds exact latest-lead lookup, public apply/qualifier preflight, same-contact GHL proof, podcast direct-address, desktop/mobile render, email-click, Drive registry, Notion row, Gatekeeper production-token, Bennett-preview-only send boundary, and wrapper receipt-dir verification red-line."
patched_v3_22: "2026-06-02 — Claude Code Agency A-Z test run (9 issue fixes). (1) format-conformance-check.py Python 3.9 compat: add `from typing import Optional` and use `Optional[pathlib.Path]` not `Path | None` — breaks on system Python 3.9 which ships with macOS. (2) MANIFEST.json FLEET-GATE: blueprints/MANIFEST.json must exist before any new slug can commit. If missing, create from blueprints/index.json. Add to Stage 0 pre-flight. (3) Template contamination check: after clone-blueprint.sh, run `python3 scripts/blueprint-consistency-check.py blueprints/<slug>.html`; STORAGE_KEY must equal `bpod_<slug>`, no prior lead dollar amounts, no prior industry-specific content. (4) format-lock.json validation: `~/.openclaw/state/format-lock.json` must use format-3 section IDs — `listen` (not podcast-player), `timeline` (not roadmap), `apply` (not cta-apply), CSS tokens `--brand:` / `--brand-dark:` / `--brand-light:` (not --brand-accent). Verify at Stage -1. (5) Podcast size IMMEDIATE check after download: `[ $(stat -f%z podcasts/<slug>.mp3) -le 20971520 ]` or regenerate with --length short. Never accept >20MB. (6) financial-realism-check.py: add new industry slugs to LEAD_INDUSTRY and INDUSTRY_BANDS before each run; ai_consulting band (3000-25000/contract) added. (7) thank-you pages content audit: Gate 31/32 must confirm thank-you-apply.html has being-built language and thank-you-blueprint.html has in-right-hands language — NEVER swapped. (8) Qualifier follow-up workflow: verify GHL has a workflow triggered by `qualifier-submitted` tag with Day 0/2/48h sequence; if absent, flag to Kay before Stage 7.25 complete. (9) format-lock-deploy-guard.sh hook: pattern must match `blueprints/` path not any filename containing 'blueprint' — prevents false-positive blocking of thank-you-blueprint.html."
patched_v3_21: "2026-06-02 — Naming-drift cleanup (self-consistency follow-up to v3.20, no behavior change). Rule 14 ROI-DEFAULTS now names the real template ids `sl-leads → lead_volume`, `sl-rate → close_rate` (were stale `slider-leads`/`slider-close`); sl-contract stays the documented fill-in. Companion: blueprint-ai-audit-skill v2.10 reworded D10-01/02/04 from 'ROI slider' to the contract fill-in (D10-02 range-overlap is legacy-slider-only / N/A for fill-in), and financial-realism-check.py now matches id=sl-contract (was dead id=slider-contract regex that fail-open-skipped the contract-band red-lines) and exempts the fill-in's intentional `|| 0` empty-sentinel from D7-17. Added scripts/test-roi-fillin-gate.sh replay-test (4/4 PASS) guarding the Step 4a0 gate against removal/regression."
patched_v3_20: "2026-06-02 — ROI Avg Customer Value = FILL-IN INPUT permanent fix (Bennett directive, repeated/re-confirmed). The Avg Customer Value (Annual) field is now a typed `<input type=\"number\" class=\"calc-fill-input\" id=\"sl-contract\">` fill-in, NEVER a `type=\"range\"` slider; the other 3 ROI fields (Monthly Leads, Close Rate, Admin Hours) stay sliders. Value is still calculated/used in calcROI() identically (same id=sl-contract). Resolved the self-contradiction where line 371 already said fill-in but Rules 11/14/18 + section-spec #11 + the ROI-DEFAULTS JS all said 'slider' and TEMPLATE/brent shipped slider-only — that disagreement is why the slider kept coming back. All six slider→fill-in flips applied. GUARANTEE: clone-blueprint.sh Step 4a0 HARD GATE fails the build (exit 1) on any type=range#sl-contract regression OR a missing fill-in input; negative-tested PASS on fill-in, FAIL on slider. Baked into blueprints/TEMPLATE.html so every future generation inherits it deterministically + gate-enforced. memory: feedback_blueprint_avg_value_fillin_not_slider.md."
patched_v3_19: "2026-06-01 — Determinism hardening (Bennett 'exact same output every time' directive). Added FC-07 [RL] to scripts/format-conformance-check.py: asserts the play-button HARDENING (play().catch Promise handler + readyState===0→load() guard) that fixed the live podcast-button dead-click bug. FC-05 only proved togglePlay EXISTS; FC-07 proves it is the HARDENED variant so no future edit can silently strip the fix and still pass the gate. Negative-tested: stripping the guard returns exit 1 / HALT. The hardening is already baked into blueprints/TEMPLATE.html (the tokenized clone source) so every future generation inherits it deterministically AND is gate-enforced against regression."
patched_v3_18: "2026-06-01 — Full-chain format-3 lock. Added a PF0-5 Format-3 Conformance Red-Line to the Category Gate: before any pass token / Bennett preview / prospect send, `scripts/format-conformance-check.py blueprints/<slug>.html` must exit 0 — mirroring blueprint-ai-audit-skill PF0-5 on the EMIT side. Also wired the same format-3 conformance check into `scripts/blueprint-release-gate.sh` (any #0071E3-signed blueprint must stay conformant = hard fail on drift; legacy = migration-pending warn that auto-promotes on regeneration). Chain is now locked end-to-end: TEMPLATE clone → emit PF0-5 → gatekeeper token → pre-commit FORMAT-3 LOCK → audit PF0-5 → release-gate drift lock."
patched_v3_17: "2026-06-01 — Production ship gate hardening after Dave Wood false-ready failure. Repo-local `scripts/blueprint_completion_gate.py` replaces stale machine path. `scripts/blueprint_gatekeeper_100.py --mode production` is now the only allowed Bennett-preview/customer-send token source. Receipts must prove PASS content, not just exist. Send scripts require `<slug>-gatekeeper-pass-token.json`; `--bennett-approved` alone is not enough. Added visible red-lines for banned CTA copy (`Apply to work with Bennett`) and corrupted AI Agent badges (`$out`, `$in`, `T`)."
patched_v3_16: "2026-06-01 — 3 Bennett-locked permanent rules added (Rules 20-22): Rule 20 Results-from-Similar-Businesses = industry-specific What-they're-doing/How-it-helps/How-Bennett-delivers + FOMO framing; Rule 21 Skip section = soft 'later not never' + AI-replaces-all-computer-work-step-by-step vision sell (no hard 'AI won't work' language); Rule 22 color consistency = always advaita-design-skill locked palette #0071E3/#1D1D1F/#F5F5F7, never per-lead red/purple accents. Design-spec + section #3/#8 descriptions updated to match. Codified from brent-attaway/format-3 finalize."
patched_v3_14: "2026-05-27 — Completion Taxonomy + Category Gate permanent fix: separates internal preview / technical pass / production ready / delivered / revenue validated; requires a 50-check category gate before any completion claim; blocks manual SKILL.md interpretation when the canonical orchestrator is missing; resolves the Command Center/15-section contradiction in favor of Melissa v2 17-section no-Command-Center standard."
patched_v3_13: "2026-05-27 — Blueprint AI 100% Run Contract: mandatory tools/GHL/intake/council/gatekeeper load order, 30-error-prevention proof gates, Watson-style proof-run boundary, pass-token requirement before Bennett preview, and customer-send block without current Bennett approval."
patched_v3_12: "2026-05-27 — lead-capture self-audit hardening: end-to-end apply/qualifier/book tracking proof, public Pages token sweep, repeat-submit same-contact acceptance, and Brent known-lead verification are mandatory."
council_verified: 4.78/5.0 PASS (v3.0) + 25-gate mechanical hardening (v3.3) + 5-improvement council (v3.8) + Funnel Map + TY Blueprint gold standard (v3.9)
drive_file_id: 1IzE-seDDaB1Tciik9mwBVrgQcb7FP7eH
description: >
  Master orchestrator for the full Blueprint AI delivery pipeline.
  Sequences: lead intake → Blueprint HTML → NotebookLM podcast → prompts → pre-delivery check → email delivery → tracked qualifier + booking verification.
  References sub-skills by Drive ID, including `blueprint-lead-intake-skill` and GHL skills. Never rebuilds from scratch.
  v3.8: Website (Stage 2) DEPRECATED. Stage -1 Skill Loader Gate added. ROI defaults from GHL mandatory. Drive links banned. No explicit +X% in hero stats. 5 council improvements: Sub-Agent Receipts, Pipeline State Manifest, Agent Lock, Failure-to-Patch Loop, Stage Input Hash.
  v3.9: 5-Page Funnel Map documented. thank-you-blueprint.html gold standard added (Step 5 — post-qualifier). Council 10-improvement plan pending.
---

# Blueprint AI Skill v3.18 — Master Orchestrator

> ⚠️ **EXECUTION DIRECTIVE (v3.9 — do not interpret stages manually)**
> The canonical execution path is the Python orchestrator — NOT this SKILL.md.
> Run: `python3 ~/.claude/skills/blueprint-ai-skill/orchestrator/blueprint_orchestrator.py --lead "<slug>" --all-stages`
> This file is documentation only. Every stage enforced via lockfile chain.
> Stage N cannot run without stage_{N-1}.lock. Violations raise StageSkipError.
> Any agent that reads this file and tries to execute stages manually will produce
> output that fails the 8 machine validators and will be rejected at pre-commit.


## v3.23 Controlled Dummy Prospect E2E Runbook (Chad/Codex proof — 2026-06-02)

Use this section when Bennett asks for a realistic customer-path test, latest-lead proof, or a repeatability hardening run. This is mandatory before any Bennett preview or production-ready claim for a synthetic/customer-path Blueprint test.

### Latest lead lookup rule
1. Query GHL by `dateAdded` first. Never use `dateUpdated` as latest-lead proof.
2. If the HighLevel connector is 401, label `HighLevel connector partial` and use the direct GHL API only if the current machine has a valid token route; otherwise use local receipts as fallback and do not claim current GHL proof.
3. Record the source, timestamp, contact ID/email/phone, and whether the lead is synthetic or real.

### Public funnel preflight before submitting
1. Preserve repo state before mutation: current branch, head SHA, dirty files, and any unrelated untracked files.
2. Verify `apply/index.html` requires first name, last name, email, phone, business, and posts through the relay with no public token or Authorization header.
3. Verify apply redirect is `thank-you-apply.html`, not `thank-you-blueprint.html`.
4. Verify `qualify.html` is real HTML, not base64/text corruption; contact fields are required; submit posts to relay before any booking modal opens.
5. Verify both thank-you pages are HTTP 200; apply thank-you has no booking CTA; blueprint/qualifier thank-you has no gold styling, no emoji, no calendar bypass.
6. Capture desktop and mobile screenshots at 1440px, 390px, and 360px for apply, blueprint, qualifier, and thank-you surfaces.

### Controlled dummy prospect contract
1. Use one Bennett-controlled identity, e.g. `bennett+chad-blueprint-test-YYYYMMDD@franchiseki.com`, and a reserved test phone such as `+15550100199`.
2. Submit apply from the public URL, then prove relay HTTP 200 and one GHL contact by exact email/phone/contact ID.
3. Wait for the canonical orchestrator path. If it fails or only scaffolds locks, label `automation partial`; recovery output is internal-preview only until gates pass.
4. Build the Blueprint through the canonical/recovery path with no stale industry language, no placeholders, no internal gatekeeper language, no direct booking link, no public GHL token, and no banned gold styling.
5. Build podcast from a source over 18KB. Audio must be 6–20MB, public HTTP 200, direct-address opening to the prospect/business, no source-material framing, no third-person opener, and a player with seek/skip/speed controls.
6. Click Qualify from the Blueprint/email, submit the same identity, and run five repeat qualifier submits. Passing proof means exact contact count remains `1` and the returned contact ID matches the expected ID.
7. Record follow-up proof separately for apply and qualifier categories: tags, notes, conversation/instant-response, and workflow/campaign IDs if the endpoint is available. If workflow/campaign readback is unavailable, label only that subproof partial.

### Required receipts before preview
From `audit-receipts/<slug>/`, every Bennett preview requires positive receipts for:
- `<slug>-email-click-test.json`
- `<slug>-desktop-render.json`
- `<slug>-mobile-render.json`
- `<slug>-audit.json`
- `<slug>-closeout.json` with `goal_complete:false` if the parent task is still open
- `<slug>-production-42.json` through `<slug>-production-48.json`
- `<slug>-gatekeeper-pass-token.json` minted by `scripts/blueprint_gatekeeper_100.py --mode production`

Run both gates after the receipts are present:

```bash
python3 scripts/blueprint_completion_gate.py --html blueprints/<slug>.html --receipt-dir audit-receipts/<slug> --lead <slug> --require-production --json-output
python3 scripts/blueprint_gatekeeper_100.py --mode production --html blueprints/<slug>.html --receipt-dir audit-receipts/<slug> --lead <slug>
```

### Bennett preview and send boundary
1. Internal preview send is allowed only after the production Gatekeeper token passes.
2. Send preview only through `scripts/build-delivery-email.sh leads/<slug>.json --send-preview --gate-token audit-receipts/<slug>/<slug>-gatekeeper-pass-token.json`.
3. The wrapper must pass `--receipt-dir "$(dirname "$GATE_TOKEN")"` into token verification; otherwise hash-bound production receipts in per-lead folders fail-open/fail-closed incorrectly.
4. Preview TO must be `bennett@franchiseki.com`; CC must be `madison@franchiseki.com` when the active Drive skill requires Madison governance.
5. External customer/prospect send remains blocked until Bennett approves in the current session after reviewing the preview.
6. Honest final taxonomy for a controlled dummy run with no external send is no higher than `PRODUCTION_READY_NOT_SENT` / `BENNETT_PREVIEW_SENT_NOT_CUSTOMER_SENT`.

### Proof-run source of truth
The Chad proof run that created this runbook used:
- Lead: Chad Ramirez / Summit Street Tacos, Denver fast-casual restaurant group.
- Public Blueprint: `https://bennett-maxwell.github.io/fki-preview/blueprints/chad-ramirez-summit-street-tacos-20260602.html`.
- Public podcast: `https://bennett-maxwell.github.io/fki-preview/podcasts/chad-ramirez-summit-street-tacos-20260602.mp3`.
- GHL contact: `IX7XsHPPPOJ57aWZsOLK`, exact contact count `1` after apply, qualifier, public fixed mobile submit, and five repeat qualifier submits.
- Bennett preview proof: Gmail message ID `19e892b88b939d98`.

## v3.14 Completion Taxonomy + Category Gate (Bennett correction 2026-05-27)

This section overrides any older wording that lets an agent collapse a partial proof into "done."

### Completion Words Are Tiered

Agents must use exactly one of these statuses:

1. `NOT_READY` — structural/content/funnel/proof checks are failing.
2. `INTERNAL_PREVIEW_ONLY` — local/internal artifact can be shown to Bennett, but production gates are incomplete.
3. `TECHNICAL_FUNNEL_PASS` — public funnel mechanics passed on synthetic/controlled identities only.
4. `PRODUCTION_READY_NOT_SENT` — public readback, Drive artifact registry, Notion row, current GHL readback, repeat-submit, NotebookLM audio, and delivery-click test all passed; customer send is still blocked.
5. `DELIVERED_TO_PROSPECT` — Bennett approved in the current session and the prospect email/SMS send has a message ID.
6. `REVENUE_VALIDATED` — a real prospect moved through sent blueprint -> qualifier -> booked -> held call -> closed revenue attribution. Synthetic bookings do not count.

Forbidden wording unless the matching tier is proven in the same run:
- `done`
- `finished`
- `100%`
- `Diamond`
- `delivered`
- `production ready`
- `revenue validated`
- `sent`

If the highest honest tier is `INTERNAL_PREVIEW_ONLY`, the final answer must say that explicitly and list open production gates.

### Category Gate Is Mandatory

Before any Bennett preview, prospect send, or completion claim, run the category gate:

```bash
cd /Users/openclaw/fki-preview
python3 scripts/blueprint_gatekeeper_100.py \
  --mode local \
  --html <blueprint.html> \
  --receipt-dir audit-receipts/<lead-slug> \
  --lead <lead-slug>
```

For production claims, run:

```bash
cd /Users/openclaw/fki-preview
python3 scripts/blueprint_gatekeeper_100.py \
  --mode production \
  --html <blueprint.html> \
  --receipt-dir audit-receipts/<lead-slug> \
  --lead <lead-slug>
```

Production PASS must create `audit-receipts/<lead-slug>/<lead-slug>-gatekeeper-pass-token.json`.
No token means no Bennett preview, no prospect send, no "done", no "production ready", and no parent-run Diamond claim.

Lower-level audit command, used only inside Gatekeeper 100:

```bash
python3 scripts/blueprint_completion_gate.py \
  --html <blueprint.html> \
  --receipt-dir audit-receipts/<lead-slug> \
  --lead <lead-slug> \
  --require-production \
  --already-sent
```

`--require-production` or Gatekeeper 100 returning nonzero is a hard stop. Do not email the prospect, do not say production ready, and do not say Diamond for the parent Blueprint run.

### Format-3 Conformance Red-Line (PF0-5 — full-chain lock, 2026-06-01)

**[RED LINE] Before any pass token, Bennett preview, or prospect send, the emitted blueprint MUST pass the same format-3 structural gate the `blueprint AI audit` enforces:**

```bash
cd /Users/openclaw/fki-preview
python3 scripts/format-conformance-check.py blueprints/<lead-slug>.html   # exit 0 REQUIRED
```

This mirrors `blueprint-ai-audit-skill` PRE-FLIGHT GATE 0 **PF0-5** on the EMIT side, so the chain is locked end-to-end: generator emits from `blueprints/TEMPLATE.html` (tokenized format-3) → this PF0-5 conformance gate (exit 0) → Gatekeeper 100 pass token → pre-commit FORMAT-3 LOCK → `blueprint-ai-audit-skill` PF0-5 re-check → `scripts/blueprint-release-gate.sh` format-3 drift lock (any `#0071E3`-signed blueprint must stay conformant). A nonzero exit here = hard stop: do not write the pass token, do not preview, do not send, do not claim Diamond. PROVEN 2026-06-01 (diamond 6/6 + gatekeeper 100/95). FC-01..FC-07: 16 sections in exact order, 21 chaptered-player IDs each once, single `id="listen"`, component DNA density, player JS wired, podcast is a real MP3, AND (FC-07 [RL], added 2026-06-01) the play-button is HARDENED — `play().catch(...)` Promise handler + `readyState===0 → load()` guard. FC-05 only proves `togglePlay` exists; FC-07 proves it is the hardened variant so a future edit can't silently strip the live-bug fix and still pass. Negative-tested: stripping the guard returns exit 1 / HALT.

### Category Gates

Every Blueprint run must be scored in these categories:

1. **Structure** — exact 5-tab nav, 17 sections, Melissa v2 layout, no Command Center, 3 prompt blocks of 100+ lines.
2. **Content** — no fabricated facts, no unsourced outcomes, no hardcoded ROI defaults, no Drive links, no tokens, all citations clickable, positive tone.
3. **Funnel** — CTA to `qualify.html`, query params preserved, no direct booking, booking only after tracked qualifier submit.
4. **Audio** — player exists, 1x and 1.25x speed controls exist, podcast URL/readback exists, NotebookLM production audio or explicit podcast partial.
5. **Proof** — stage receipts, pre-delivery, render, audit, gatekeeper, email audit, closeout receipt.
6. **Production** — public GitHub Pages readback, Drive artifact registry, Notion Sprint row, current GHL readback, repeat-submit same-contact proof, NotebookLM-size audio, Bennett approval, delivery click test.
7. **Delivery** — Bennett internal preview message ID, customer message ID only after approval.
8. **Revenue** — held-call and closed-revenue attribution; never inferred from synthetic/contact-only proof.

### 50 Breakpoints To Test

The category gate must cover or explicitly label these breakpoints:

1. Wrong/stale Drive skill version.
2. Canonical orchestrator path missing.
3. Manual stage interpretation used without a recovery-mode label.
4. Duplicate local `SKILL.md` shadows Drive canonical.
5. Contradictory gold-standard instructions not resolved.
6. Wrong template cloned.
7. Section count mismatch.
8. Wrong tab set.
9. Command Center tab or content present.
10. Demo Site tab present.
11. Website Audit section revived.
12. Countdown timer revived.
13. Hero percent claim without source.
14. Hardcoded ROI default.
15. Hardcoded contract value.
16. Hardcoded close rate.
17. Fabricated revenue range.
18. Fabricated testimonial or case study.
19. Unsourced benchmark.
20. Bare citation text without `<a href>`.
21. Negative "business is broken/behind" tone.
22. Industry drift from the actual lead.
23. Cross-lead contamination.
24. Missing required lead identity field.
25. GHL identity not confirmed by exact email/contact ID.
26. `dateUpdated` used as new-lead proof.
27. Query params dropped from CTA.
28. CTA points to `/apply` instead of `qualify.html`.
29. Direct booking/calendar link exists.
30. Booking can open before qualifier submit.
31. Public GHL token or Authorization header exposed.
32. `drive.google.com` link in customer-facing HTML/email.
33. Podcast href empty or 404.
34. Podcast controls missing 1x/1.25x.
35. NotebookLM-size audio absent but not labeled partial.
36. Email click test missing.
37. Desktop render missing.
38. Mobile render missing.
39. Public Pages build not verified built.
40. Public deployed HTML not read back after push.
41. Artifact not uploaded to Drive.
42. Artifact Registry row missing.
43. Notion Sprint row missing.
44. Repeat-submit creates duplicate GHL contacts.
45. Appointment not attached to same GHL contact.
46. Notification sends customer email/SMS.
47. Bennett preview sent before Gatekeeper token.
48. Prospect send without current Bennett approval.
49. Final response claims completion despite partial labels.
50. Revenue validation inferred from synthetic/test flow.

### Contradiction Resolution

Older text that mentions a 15-section Brent standard or requires `Command Center` is deprecated for new builds. The active standard is:

- Melissa v2 visual/content standard.
- 17 required sections.
- No Command Center tab.
- No Command Center section.
- Nav exactly `Your Profile | AI Agents | ROI Calculator | Listen | Apply`.

If any validator or older gold-diff text conflicts with those bullets, the run must halt and create a council permanent-fix receipt before continuing.

### Orchestrator Missing Rule

If `~/.claude/skills/blueprint-ai-skill/orchestrator/blueprint_orchestrator.py` is missing, the run cannot be called a full Blueprint AI execution. Allowed wording:

- `manual recovery run`
- `internal preview`
- `partial`
- `category-gated local artifact`

Disallowed wording:

- `full pipeline completed`
- `Blueprint AI done`
- `Diamond`
- `production ready`

## Mandatory GHL + Notification Dependencies (2026-05-27)

Before any new Blueprint AI thread executes lead intake, delivery, qualifier, booking, or tracking work:

1. Load `blueprint-lead-intake-skill` from Drive file `1q9kNqjII1X42ddBYVbkiDhEytSRO0aBP`.
2. Load `ghl-pipeline-update-skill` from Drive file `163yfPeEQE3OtbgvJhpXovirzOB3yu4-n` for canonical GHL connector/direct API order.
3. Load `ghl-stage-automation-skill` from Drive file `1IzYPzPIQNzTnD1XQpnX7Vf4bF8U8VAxu` when stage movement, workflow triggers, or automation status is involved.
4. Verify the direct GHL integration before claiming CRM visibility: `GHL_PIT_TOKEN` / `GHL_API_KEY` + `GHL_LOCATION_ID` from `~/.openclaw/gateway.env`, API base `https://services.leadconnectorhq.com`, header `Version: 2021-07-28`.
5. For every new Blueprint form fill, Bennett must receive a work-email notification at `bennett@franchiseki.com` with subject shape `New Blueprint AI lead: <name>`. Local production notifier: `/Users/temp/.openclaw/scripts/blueprint-lead-notifier.py`, LaunchAgent `com.franchiseki.speed-to-lead`, state `/Users/temp/.openclaw/state/blueprint-lead-notifier.json`.
6. Never count `dateUpdated` as a new lead without evidence of a form-submit event. Report true new leads by `dateAdded`; separately label updated/reprocessed Blueprint contacts.
7. Never email the lead from the notification relay. Customer delivery still requires the Blueprint delivery/approval gates.

## Blueprint AI 100% Run Contract (v3.13 — Council + Gatekeeper Required)

Every Blueprint AI run that claims "done", "100%", "Diamond", "sent", "delivered", or "ready for Bennett"
must follow this contract. If any step is unavailable, label the exact partial and stop before the protected
action.

### Required Load Order

1. `tools-skill` — confirm current connector/API/CLI route and protected-action boundary.
2. `ghl-pipeline-update-skill` — confirm direct GHL integration, identity matching, `dateAdded` lead logic, and proof format.
3. `blueprint-lead-intake-skill` — confirm form-fill, package, notification, and customer-send boundaries.
4. `council-skill` — run Permanent Fix Approval Mode before any durable skill patch or repeat-defect fix.
5. `gatekeeper-skill` — run after Blueprint audit = 100/100 and before any Bennett preview or external delivery.

### Council Gate

- Permanent fixes require `council-skill` score `>=4.25/5`.
- Council output must record all 5 advisor scores, dissents, threshold, pass/fail, canonical source to patch,
  proof plan, rollback path, and protected-action boundary.
- If score `<4.25`, do not patch Drive. Return the safest current-response correction only.

### Gatekeeper Gate

- Gatekeeper is mandatory for every Blueprint proof run and every Blueprint delivery run.
- Bennett-facing preview requires a repo-minted `gatekeeper_pass_token` with `pass:true`, `score:100`,
  `diamond:"PASS"`, and `strict_production:true`.
- Customer/prospect send requires current-session Bennett approval after Gatekeeper PASS. `--bennett-approved`
  without a valid token is still a hard fail.
- Receipt files must contain a positive PASS signal (`pass:true`, `ok:true`, `verified:true`, `status:"PASS"`,
  or `http_code:200`). A receipt file that merely exists is not proof.

Token command:

```bash
cd /Users/openclaw/fki-preview
python3 scripts/blueprint_gatekeeper_100.py \
  --mode production \
  --lead <lead-slug> \
  --html blueprints/<lead-slug>.html \
  --receipt-dir audit-receipts/<lead-slug>
```

Send command:

```bash
bash scripts/build-delivery-email.sh leads/<lead-slug>.json \
  --send-preview \
  --gate-token audit-receipts/<lead-slug>/<lead-slug>-gatekeeper-pass-token.json
```

### Past Error Prevention Gates

1. Create or find a Notion Sprint Board row before mutation; if Notion fails, create a local receipt first.
2. Confirm the lead in GHL by exact email or canonical contact ID before building.
3. Use `dateAdded` for "new lead"; never use `dateUpdated` as new-lead proof.
4. Preserve `lead`, `biz`, and `src` query params through Blueprint, qualifier, and booking routes.
5. Blueprint CTA must point to `qualify.html`; direct booking links are a hard fail.
6. Booking can open only after tracked qualifier submit.
7. No public GHL tokens, `Authorization` headers, API keys, or private env values in frontend code, HTML,
   receipts, screenshots, logs, or email.
8. No `drive.google.com` links in customer-facing Blueprint HTML or delivery email.
9. All stats, claims, citations, and recommendations must be sourced or removed.
10. Fabricated testimonials, ROI promises, fake attribution, and unsourced outcomes are hard fails.
11. Desktop and mobile render checks must pass before Bennett preview.
12. Required proof artifacts: Blueprint HTML, podcast/source artifact or explicit podcast partial, audit JSON,
    Gatekeeper ledger/pass token, and closeout receipt.
12a. Visible AI Agent labels must not contain broken generator leftovers such as `$out`, `$in`, or a one-letter `T` tag.
12b. CTA copy must not say `Apply to work with Bennett`; use qualifier/action copy tied to the funnel.
13. Artifact Registry / Notion update is required, or label `Notion partial` / `registry partial` with the exact blocker.
14. Repeat-submit proof must update one GHL contact, not create duplicates.
15. Notification/proof tooling must never send customer SMS/email.
16. Drive skill patches require rollback path, replacement upload preserving the existing file ID, and fetchback verification.
17. Final response must pass recap/final checker before claiming done.

## Revenue Declaration
```yaml
revenue_declaration:
  expected_revenue_impact_usd: 50000
  floor_usd: 50000
  per_event: "franchise deal closed from Blueprint lead"
  revenue_type: "pipeline_conversion"
  measurement: "GHL stage = Closed Won after Blueprint delivery"
```

## Automation Declaration
```yaml
automation_declaration:
  is_self_running: true
  trigger_ref: "Stage -1 — skill version check → Stage 0 — lead name input"
  trigger_verified_at: "2026-05-22"
  human_gates: ["Stage 7 lead email send (HUMAN-APPROVAL-SEND)", "Stage 7.25 apply quiz verify"]
  autonomous_stages: ["-1", 0, 1, "1.3", "1.5", 3, "3.5", 4, 5, 6, 7, "7.25", "7.5", "7.75"]
  deprecated_stages: [2]
```

## 5-PAGE FUNNEL MAP (v3.9 — FINAL 2026-05-23, commit 076ed9b)

All pages live at: `https://bennett-maxwell.github.io/fki-preview/`
Repo: `bennett-maxwell/fki-preview` · Branch: `main`

| Step | File | Purpose | Redirects To |
|------|------|---------|--------------|
| 1 | `apply/index.html` | Entry intake — 12 qualifier questions for Blueprint | `../thank-you-apply.html` |
| 2 | `thank-you-apply.html` | "Blueprint is being built — check inbox in 24h" | — (wait for email) |
| 3 | `blueprints/[client].html` | Personalized Blueprint delivery + podcast | CTA → `qualify.html?lead=...&biz=...&src=...` when available |
| 4 | `qualify.html` | AI Qualifier — contact tracking + 8 questions + live score | GHL webhook submit, then Book-a-Call modal for qualified/review-needed leads |
| 5 | `thank-you-blueprint.html` | "Team reviewing your numbers — 48h response if fit" | — |

### Content Rules Per Page (HARD — do not swap)
- **Step 2 (thank-you-apply.html):** "Your blueprint is being built." Prospect just applied. They have NOT seen the blueprint yet.
- **Step 5 (thank-you-blueprint.html):** "We're reviewing your numbers." Prospect has ALREADY (1) applied, (2) received blueprint + podcast, (3) read it, (4) completed qualifier. NO mention of blueprint being built. NO podcast. Team is now deciding if fit.

### thank-you-blueprint.html Gold Standard (v3.9 — 2026-05-23)
Built from council-approved 9-change plan. Sections in order:
1. **Hero** — "Your application is in the right hands." + animated teal status dot + "Under review — 48-hour response window"
2. **What Happens Next (3 steps)** — (1) Team reviewing numbers now, (2) 48h reach-out if fit, (3) 15-20 min fit check call — not a pitch
3. **AI Agents Education (dark navy)** — Speed-to-Lead / Follow-Up / Intake & Routing agents + stat bar (Velocify 78% / Salesforce 35-50% / HBR 5x) — all sourced with clickable links
4. **What We Build (2-col)** — Implementation preview card: Custom agent stack / CRM integration / Lead response automation / Calibration day 1
5. **While You Wait (3 cards)** — Review qualifier answers / Pull lead numbers / Identify biggest time drain
6. **Bottom CTA** — Route to tracked qualifier. Booking is allowed only inside `qualify.html` after identity + score payload have been submitted to GHL.
7. **Footer** — Contact + Privacy only. NO "Retake Qualifier."

### Audit Rules Enforced on Step 5 Page
| Audit Check | Status |
|---|---|
| D2-01 No emojis | PASS — no emojis, SVG icons only |
| D2-03 No direct booking URLs | PASS — blueprint pages do not link directly to calendar; only tracked qualifier can open booking after submit |
| D2-05 No 90-day language | PASS — removed |
| D2-07 No hardcoded ROI $ | PASS — no dollar predictions |
| D2-13 No fabricated testimonials | PASS — Marcus D. attribution removed |
| D2-24 No pricing tables | PASS |
| D2-26 Positive framing only | PASS — "excellent operation" frame |
| D6-01 All stats sourced | PASS — Velocify/Salesforce/HBR links |

---

## Constants
```
GHL_LOCATION_ID        = "14RD8KklxR9G4e0Rf7v2"
GHL_TOKEN_FILE         = ~/.openclaw/gateway.env (field: GHL_PIT_TOKEN)
GITHUB_PAGES_BASE      = https://bennett-maxwell.github.io/fki-preview
ARTIFACT_REGISTRY_DB   = 328a4ee00ca84c9b8e8134067fa04609
BLUEPRINT_PIPELINE_NOTION = 366cf5514fd38160885cea3680b9f2e7
SKILL_DRIVE_ID         = 1IzE-seDDaB1Tciik9mwBVrgQcb7FP7eH
SKILL_VERSION_REQUIRED = 3.9
```

## North Star
One command produces a complete, Diamond-verified Blueprint package for any lead: AI Playbook HTML + NotebookLM podcast (6-20 min walkthrough window) + 3 AI prompts + qualifying email. Bennett never touches the pipeline — just approves the final send.

### 🎯 GOLD-STANDARD TARGET (Bennett-locked 2026-06-01) — the output EVERY run must reproduce
The canonical "done right" blueprint = **`brent-attaway` (format-3 final, 2026-06-01)**. Snapshot: `blueprints/brent-attaway.FINAL-20260601-1541.html` (98072 B). Every generated blueprint MUST match these LOCKED invariants — they ARE the definition of success, enforced deterministically by clone-gate + completion gate + audit PF0-5:
1. **CTA = "See If You Qualify" → `qualify.html` ONLY.** Zero "Get Your AI Quote", zero "Apply to work with Bennett", zero apply_url trap. Gate: ≥1 qualify CTA, 0 banned strings.
2. **Avg Customer Value = fill-in number input ONLY** (`<input type="number" class="calc-fill-input" id="sl-contract">`) — NO slider for this field. The other 3 ROI fields (Monthly Leads, Close Rate, Admin Hours) stay sliders. NEVER a `type="range"` slider for Avg Customer Value, NEVER hardcoded. Bennett directive (repeated, re-confirmed) 2026-06-02.
3. **Podcast = 6-20 MB walkthrough WINDOW** (~6-20 min, target 12-18). The old ≥29 MB floor was BACKWARDS (it forced 30+ min lectures) — permanently removed across all 7 enforcement points.
4. **Format-3 + locked Advaita palette** (#0071E3 / #1D1D1F / #F5F5F7), 5-nav single-scroll, no Command Center, no per-lead accent.
5. **No standalone website stage** (deprecated), no Drive links in body.

**Reproducibility contract:** TEMPLATE.html is the tokenized format-3 clone source; `clone-blueprint.sh` HARD-aborts (exit 1) on any banned CTA, missing fill-in, or out-of-window audio. Any Claude Code on any machine running the orchestrator against this template produces a format-3-conformant blueprint **deterministically** for all gate-enforced elements (STRUCTURE, CTA, contract input, palette, audio window). The generative copy + podcast audio vary run-to-run (LLM/NotebookLM non-determinism) but can never violate an invariant above — the gates fail the build first.

## Triggers
- "run blueprint ai"
- "blueprint for [lead name]"
- "full blueprint package for [lead]"
- "run the blueprint pipeline"
- "build blueprint"
- "ai advantage blueprint"
- "blueprint ai skill"
- "run the full pipeline"
- "blueprint package"
- "ai playbook for [lead]"

---

## CANONICAL TEMPLATE STANDARD (v2.3 — Bennett directive 2026-05-21)

### DEPRECATED GOLD-DIFF GATE (v3.11 — superseded by v3.14+ and v3.17)

This block is historical only. Do not enforce it for new builds. It references the old Brent 15-section / Command Center standard, which conflicts with the active Melissa v2 no-Command-Center standard. New builds must use the current 5-nav standard and the repo-local Gatekeeper 100 token.

**Root cause:** Multiple leads shipped as "done" with DIFFERENT structures — Branson/Chris/Dave were three divergent versions. The documented canonical existed but nothing verified the *rendered output* matched it. Documenting a standard ≠ enforcing it.

**Historical enforcement — DO NOT USE for new builds:**
1. **Named gold standard:** `brent-attaway-crmx` (the 15-section canonical). Every new blueprint diffs against it.
2. **Structural diff (mechanical):**
   - Section count == gold section count (extract `<section`/heading anchors, compare).
   - Required section IDs all present (intro, day-timeline, Command Center, apply CTA, etc. per gold).
   - Zero unrendered `{{TOKEN}}` (existing Gate 31).
3. **PASS:** structure matches gold within tolerance → proceed to ship.
4. **FAIL:** structure diverges from gold → do NOT ship, do NOT mark done. Rebuild from the gold template, then re-diff. This is the exact "wrong format shipped as done" failure being closed.
5. **One canonical version per lead** — if two divergent HTMLs exist for the same lead, keep the gold-matching one, delete the other. Never present multiple versions as "all done."
6. **Learn-from-mistake hook:** on any FAIL, append the divergence to `~/.openclaw/workspace/process-improvements.jsonl` so the pattern feeds skill improvement.

This gate is enforced by diamond-skill T7 (persisted-write) + gatekeeper-skill v3 Stage 4 (gold-diff). Blueprint pipeline must call it before Stage 7 send.


**Base design:** Melissa Tash SRP Blueprint layout (single-scroll, clean nav, mobile-first)
**Reference file:** bennett-maxwell.github.io/fki-preview/blueprints/melissa-tash-srp.html

### Design spec (locked — Bennett + Madison + Kay):
- COLOR CONSISTENCY (Rule 22, Bennett directive 2026-06-01): EVERY blueprint uses the SAME locked advaita-design-skill palette — brand/blue `#0071E3`, navy `#1D1D1F`, page bg `#F5F5F7` (never pure white), card `#FFFFFF`, text-secondary `#6E6E73`, border `#E5E5EA`, green `#34C759`, red `#FF3B30`, brand-light `#EBF4FF`. NEVER a per-lead random accent (no red `#E8192C`, no purple `#6c5ce7`). Layout = single-scroll, no tabs. The accent color is NOT a creative variable — it is fixed Advaita brand. Sweep for stray reds/purples before ship.
- White/`#F5F5F7` background, clean layout — Melissa's design wins
- Left-to-right stat card layout (NOT stacked vertical) — hero stats row
- Hero stat text = timeline facts ONLY — "30-Day Onboarding" (NOT "3/7/30" — looks like a date)
- Hero stat text MUST NOT contain "+X%" without a clickable `<a href="[real URL]">` source link
- NO countdown timer (gimmicky — never use)
- Podcast player: embedded with play button + 1x AND 1.25x speed controls (custom buttons)
- **Nav: 5 tabs — Your Profile | AI Agents | ROI Calculator | Listen | Apply**
  - NO Command Center tab. NO Demo Site tab. LOCKED.
- Agent prompts: full copy-paste ready, 100+ lines each (4x the old 25-line prompts)
- Christelle (NOT Kay) sends Blueprint links to all comment leads

### Required sections (in order):
1. Hero with real lead metrics (timeline facts only — no bare % claims)
2. **Business Snapshot** — real numbers from lead intake form
3. **Results from Similar Businesses** — sourced benchmarks table (ALL citations = clickable `<a href>`). INDUSTRY-SPECIFIC + FOMO FRAMING (Rule 20): name what the lead's *exact* industry is already doing with AI, HOW it helps them, and HOW Bennett delivers the same for this lead. Dual purpose — concrete proof AND fear-of-missing-out ("the ones who move first take the customers everyone else was too slow to answer").
4. **3-Pillar Framework** — Revenue / Time / Money with lead-specific numbers
5. Tool Stack — current tools mapped to AI additions
6. Gap Analysis — 5 gaps minimum, all cited with clickable links
7. **AI Opportunity Map (P1–P7)** — prioritized table with impact + tool integration
8. **"What to Ignore" / "Skip These (For Now)"** — 4 items, trust-builder, specific to lead's industry. SOFT "LATER NOT NEVER" FRAMING (Rule 21): frame as "things you *could* automate in the future, but I'd hold off for now — they'd only distract from the highest-impact wins first." Lead with the VISION SELL: AI has reached the point where almost anything a person does on a computer can eventually be handled by a trained agent given the right access + training; the plan is to replace that work step by step, biggest wins first. Timid on the skip items, bold on the vision. NO hard "AI won't work for X" / "AI can't do X" language.
9. AI Agents — 6 agents, all customized to lead's industry
10. **Implementation Milestone Table** — Days 1-3, 4-7, 30, Month 2+
11. **ROI Calculator — Avg Customer Value fill-in input + 3 sliders + 3 presets** — Conservative / Expected / Stretch
    - Avg Customer Value is a typed fill-in number input (NO slider). Monthly Leads, Close Rate, Admin Hours stay sliders.
    - Input + slider defaults MUST come from GHL fields (see Rule 14). NEVER hardcode 12%, 18%, or $45,000.
12. 3 AI Prompts — copy-paste ready, industry-specific, 100+ lines each
13. DIY vs Partner paths
14. **Podcast / Listen section** — embedded audio player + 1x/1.25x speed (HARD GATE: HTTP 200 required before send)
15. Sources / Citations — ALL must have clickable `<a href="[real URL]">` tags. No bare text citations.
16. CTA with **Bennett's personal closing message** (personalized per lead)
17. Footer

### Skip for universal template (industry-specific only):
- LinkedIn Pipeline section (B2B leads only)
- Countdown timer (NEVER — Bennett directive)
- "The Design Method" (agency/design leads only)
- Website Audit section (Stage 2 deprecated — remove from all new builds)
- Command Center section (REMOVED — Bennett directive 2026-05-22)

---

## 22 Permanent Rules (Bennett-locked, no exceptions)

| # | Rule | Source |
|---|------|--------|
| 1 | NO emojis in any client-facing deliverable | feedback_no_emojis_in_blueprints.md |
| 2 | NO direct booking URLs or calendar links in Blueprint pages — CTA = "See If You Qualify" via tracked qualifying quiz; booking modal opens only after qualifier webhook submit | feedback_blueprint_apply_not_schedule.md |
| 3 | Onboarding timeline: 3 days in, 7 days running, 30 days trained. No 90-day plans | feedback_blueprint_onboarding_timeline.md |
| 4 | NO explicit ROI dollar amounts — interactive calculator only | feedback_no_roi_predictions_blueprints.md |
| 5 | ALL stats must have cited sources with clickable links — `<a href="[real URL]">` required. No bare text citations | feedback_blueprint_source_all_stats.md |
| 6 | NEVER fabricate years, events, locations, specialties, or business data | feedback_never_hallucinate_business_data.md |
| 7 | Build from Melissa v2 template (v2.3+) — 17-section standard. NEVER rebuild from scratch | feedback_blueprint_template_melissa_wins.md |
| 8 | NO Drive links anywhere in Blueprint HTML or delivery emails. GitHub Pages URLs ONLY. `drive.google.com` = instant audit fail | feedback_blueprint_no_drive_links.md |
| 9 | Delivery = Mack + Ivan, NOT Hyperagent | feedback_blueprint_delivery_mack_ivan.md |
| 10 | All work tracked in Notion via notion-master-project-skill | feedback_always_notion_master_project.md |
| 11 | Every artifact (HTML, MP3) MUST be in Drive with correct sharing + linked in Blueprint AI Artifact Registry BEFORE Diamond is awarded | feedback_artifact_drive_save_gate.md |
| 12 | TONE — Never imply the business is struggling, disorganized, or behind. Assume they are already excellent. AI amplifies what's working. Frame gaps as "opportunities to go further faster." Bennett directive 2026-05-22. | feedback_blueprint_tone_assume_excellence.md |
| 13 | BRAND VOICE — Never say "AI learns your voice over time." Brand voice is built BEFORE the bot goes live via intelligence skill audits. Bot launches at 90%+ accuracy. Tweaks are calibration, not learning. Bennett directive 2026-05-22. | feedback_blueprint_brand_voice_instant.md |
| 14 | ROI DEFAULTS FROM GHL — ROI defaults MUST come from GHL contact fields: `sl-leads → lead_volume`, `sl-rate → close_rate`, `sl-contract (fill-in number input, NOT a slider) → avg_contract_value`. If GHL field empty → show `"(enter your number)"` placeholder. NEVER hardcode 12%, 18%, or $45,000. **Avg Customer Value is ALWAYS a typed fill-in (`<input type="number">`), never a `type="range"` slider** (Bennett directive, re-confirmed 2026-06-02). | feedback_blueprint_roi_from_ghl.md + feedback_blueprint_avg_value_fillin_not_slider.md |
| 15 | ALL LEADS GET FULL BLUEPRINT — apply-scoring-skill score affects follow-up cadence ONLY, never gates the build. Hot (8-11): same-day delivery. Warm (5-7): standard queue. Cold (<5): longer-tail nurture. Bennett directive 2026-05-22. | feedback_blueprint_all_leads_get_build.md |
| 16 | NO EXPLICIT % IN HERO STATS — Hero stats must use timeline facts or raw numbers (e.g., "30-Day Onboarding", "12 Hours Saved/Week"). Any "+X%" claim requires a clickable `<a href="[real published study URL]">` source link inline. No bare % figures. Bennett directive 2026-05-22. | feedback_blueprint_no_bare_percent_hero.md |
| 17 | CTA PREFILL PARAMS (v2.4) — Every "See If You Qualify" link MUST append `firstName`, `email` (both pulled from GHL — NEVER fabricated; omit the param if GHL has no value), AND `agents=<comma list of the lead's REAL agents>` so `qualify.html` prefills identity and Q7 renders dynamically. Audited by blueprint-ai-audit v2.4 D2-27. | Phase 4 hardening 2026-05-29 |
| 18 | AVG-TICKET HONESTY (v2.4) — The ROI Avg Customer Value field is a fill-in number input (NOT a slider) and must be USER-SET (no fabricated default) UNLESS a real avg-ticket value exists in GHL intake. NOTE: GHL currently has Revenue Range + Monthly Leads but NO avg-ticket field — adding an avg-ticket intake field is a FUTURE intake-form improvement (note only; do NOT change GHL now). | Phase 4 hardening 2026-05-29 |
| 19 | LEADS-PER-SALE ROI DEFAULT (v2.4) — The ROI calculator's close-rate input uses the leads-per-sale pattern as the STANDARD: label "X leads = 1 sale (~Y% close)", with rate computed as `rate = 1 / leads_per_sale`. This matches qualify.html. | Phase 4 hardening 2026-05-29 |
| 20 | RESULTS = INDUSTRY-SPECIFIC + FOMO — The "Results from Similar Businesses" section must name what the lead's EXACT industry is already doing with AI, HOW it helps them, and HOW Bennett delivers the same for this lead (three-part per item: What they're doing / How it helps them / How I deliver it for [LEAD]). Dual purpose: concrete examples AND fear-of-missing-out ("the ones who move first take the customers everyone else was too slow to answer"). Never a generic small-business stats table. Bennett directive 2026-06-01. | feedback_blueprint_results_industry_fomo.md |
| 21 | SKIP SECTION = "LATER NOT NEVER" + VISION SELL — The "What to Ignore / Skip These" section is timid on the skip items ("you could automate this later, but I'd hold off — it'd distract from the big wins first") and bold on the vision: AI can eventually handle almost anything a person does on a computer given the right access + training; we replace that work step by step, highest-impact first. NO hard "AI won't work for X" / "AI can't do X" language — reframe every limit as sequencing. Bennett directive 2026-06-01. | feedback_blueprint_skip_later_not_never.md |
| 22 | COLOR CONSISTENCY — EVERY blueprint uses the SAME locked advaita-design-skill palette (brand `#0071E3`, navy `#1D1D1F`, bg `#F5F5F7`, card `#FFFFFF`, text-2 `#6E6E73`, border `#E5E5EA`, green `#34C759`, red `#FF3B30`, brand-light `#EBF4FF`). NEVER a per-lead random accent (no red `#E8192C`, no purple `#6c5ce7`). Single-scroll, no tabs. Sweep for stray reds/purples before ship. Bennett directive 2026-06-01. | feedback_blueprint_color_consistency_advaita.md |

---

## ARTIFACT VAULT — Blueprint AI Master Artifact Registry (v2.4)

Notion location: Blueprint AI Agent Boot Hub page → sub-database "Blueprint AI Artifact Registry"
Parent page: 365cf5514fd3811b840ffec0080c1990

Schema (per notion-master-project-skill v1.6):
| Lead Name | TITLE |
| Artifact Type | SELECT: Blueprint HTML / Podcast / Source Doc |
| Drive File ID | RICH_TEXT |
| Drive Share Link | URL |
| Live URL | URL |
| Permissions Set | CHECKBOX |
| HTTP 200 Verified | CHECKBOX |
| File Size KB | NUMBER |
| Date Created | DATE |
| Session | RICH_TEXT |
| Status | SELECT: Building / Draft / Delivered / Diamond |

Dedup rule: search Lead Name + Artifact Type before inserting. Update if found, insert if not.

---

## Pipeline State Manifest — Cross-Agent Handoff (Council v3.8 Improvement #2)

**File:** `~/Desktop/blueprint-{slug}/pipeline-state.json`  
**Rule:** Written/updated after EVERY stage by the executing agent. Any agent picking up mid-pipeline MUST read this file first.

```json
{
  "slug": "{slug}",
  "lead_name": "{name}",
  "stages_complete": ["1", "1.3", "1.5"],
  "current_stage": "3",
  "next_stage": "3.5",
  "agent_last": "Mack|Ivan",
  "started_at": "ISO timestamp",
  "last_updated": "ISO timestamp",
  "outputs": {
    "lead_profile_path": "~/Desktop/blueprint-{slug}/lead-profile.json",
    "blueprint_html_path": "~/Desktop/blueprint-{slug}/{slug}-blueprint.html",
    "blueprint_url": "https://bennett-maxwell.github.io/fki-preview/blueprints/{slug}.html",
    "podcast_mp3_path": "~/Desktop/blueprint-{slug}/{slug}-podcast.mp3",
    "podcast_url": "https://bennett-maxwell.github.io/fki-preview/podcasts/{slug}.mp3",
    "stage1_input_hash": "sha256hex"
  },
  "http_200_checks": {
    "blueprint_url": true,
    "podcast_url": false
  },
  "gates_failed": []
}
```

**Pickup protocol:** If `pipeline-state.json` exists for a slug, skip all completed stages. Resume from `current_stage`.

---

## Agent Identity Lock — Duplicate Run Prevention (Council v3.8 Improvement #3)

**File:** `~/Desktop/blueprint-{slug}/.pipeline-lock`  
**Format:** `{"agent": "Mack", "pid": 12345, "stage": "3", "started_at": "ISO"}`

**Rules:**
- Before starting ANY stage: check if `.pipeline-lock` exists.
- If lock age < 30 minutes: ABORT. Post to #leo-coaches: "Pipeline already running for {slug} by {agent}. Not starting duplicate."
- If lock age ≥ 30 minutes: stale lock — overwrite and continue.
- Write lock before first stage. Delete lock after Stage 7.75 completes.

---

## Sub-Agent Receipt Protocol (Council v3.8 Improvement #1)

Every invoked sub-skill call MUST return and the orchestrator MUST write a receipt file:

**File:** `~/Desktop/blueprint-{slug}/receipts/stage-{N}-{skill-name}.json`

```json
{
  "skill": "notebooklm-blueprint-ai-skill",
  "version": "1.4",
  "status": "COMPLETE|PARTIAL|FAIL",
  "agent": "Mack|Ivan",
  "timestamp": "ISO",
  "outputs": {
    "podcast_url": "https://...",
    "file_size_mb": 31.2
  },
  "gates_passed": ["MP3_exists", "HTTP_200"],
  "gates_failed": []
}
```

**Orchestrator rule:** After every sub-skill call, assert `status == "COMPLETE"`. If `PARTIAL` or `FAIL`: trigger self-heal loop (max 3 rounds) then halt and post to #leo-coaches. NEVER advance to next stage on non-COMPLETE receipt.

---

## Failure-to-Patch Feedback Loop (Council v3.8 Improvement #4)

**Log file:** `~/.openclaw/logs/blueprint-gate-failures.jsonl`  
**Format per entry:**
```json
{"timestamp": "ISO", "slug": "dave-wood", "gate_id": 27, "gate_name": "ROI_default_ban", "detail": "found 18% hardcoded in calculator"}
```

**Rule:** `weekly-compliance.py` checks this log weekly. If any `gate_id` appears ≥3 times in the last 30 days: auto-invoke `Skill("council-skill")` with the failure pattern + propose SKILL.md patch. Patch appended as "KNOWN ISSUE + MITIGATION" entry. Clears the counter after patch is written.

---

## Stage Input Hash — Stale Data Detection (Council v3.8 Improvement #5)

**After Stage 1:** Compute SHA256 of these lead-profile.json fields combined: `lead_name + email + revenue_range + lead_volume + close_rate + avg_contract_value + current_tools`.  
Write hash to `pipeline-state.json` as `stage1_input_hash`.

**Before Stage 3:** Re-hash the same fields from current lead-profile.json. Compare to `stage1_input_hash`.  
- Match → proceed normally.
- Mismatch → log warning + re-run Stage 1 and 1.5 before continuing. Post to #leo-coaches: "[slug] lead data changed mid-pipeline — re-ran Stage 1."

---

## Pipeline (stages, strict order)

**Active stages:** -1 → 0 → 1 → 1.3 → 1.5 → 3 → 3.5 → 4 → 5 → 6 → 7 → 7.25 → 7.5 → 7.75  
**DEPRECATED:** Stage 2 (Demo Website Build) — Bennett directive 2026-05-22

---

### Stage -1 — Skill Loader Gate (NEW v3.8 — BLOCKING before everything)

**Owner:** Any agent starting the pipeline
**Purpose:** Prevent running a stale local skill version. Root cause of 8 violations in prior runs.

**Steps:**
1. Read local SKILL.md frontmatter: `LOCAL_VERSION=$(grep '^version:' ~/.claude/skills/blueprint-ai-skill/SKILL.md | awk '{print $2}')`
2. Fetch Drive canonical version: `DRIVE_VERSION=$(mcp Drive read_file_content SKILL_DRIVE_ID | grep '^version:' | awk '{print $2}')`
3. Compare: if `LOCAL_VERSION < DRIVE_VERSION` → **HARD HALT**.
   - Post to #leo-coaches: "blueprint-ai-skill local v{LOCAL} < Drive v{DRIVE}. Sync required before pipeline."
   - Do NOT proceed. Do NOT override.
4. If versions match: write `.skill-loader-pass` to artifact dir + log to pipeline-state.json
5. Also verify enforcement scripts exist: `preflight.sh`, `send-blueprint-email.sh`, `placeholder-scan.sh` — if missing → HALT.

**Receipt:** `stage--1-skill-loader.json` with `{"local_version": "3.8", "drive_version": "3.8", "status": "COMPLETE"}`

---

### Stage 0 — Lead Discovery Chain (v2.8+)

**Owner:** Mack
**Input:** Lead name only (e.g. "Brent Attaway")
**Rule:** Resolve website URL, email, phone, and form data autonomously. Never ask Bennett.

**Step 0.00 — Funnel Health Pre-flight (Gate 30–33 cluster — BLOCKING, v3.9):**
Run `enforcement/funnel-health-check.sh` before anything else. Verifies:
1. All 5 funnel pages return HTTP 200
2. `apply/index.html` JS redirect → `../thank-you-apply.html` (Gate 30 + 9)
3. `qualify.html` CTA stays disabled until identity + 8 answers are complete; on click it posts the tracked qualifier payload before booking/thank-you routing (Gate 33)
4. `thank-you-blueprint.html` has no "podcast being built" language (Gate 31)
5. `thank-you-apply.html` has no "qualifier" language (Gate 32)
On all 5 passing: writes `~/Desktop/blueprint-{slug}/.funnel-health-pass` lock file.
Stage 3 will not run without `.funnel-health-pass` present (same pattern as `.audit-100.lock`).

**Step 0.00b — Lead Capture Tracking Pre-flight (v3.12 — BLOCKING):**
Before creating, regenerating, or delivering any Blueprint, verify the tracking chain:
1. Public apply page has required first name, last name, email, phone, and business name.
2. Public apply page has no `pit-` token, `Authorization` header, direct `/contacts/`, or direct `/opportunities/` endpoint.
3. Public qualifier page requires first name, last name, email, phone, business name, and 8 answers before submit.
4. Qualifier submit posts tracked payload before opening the calendar modal or thank-you route.
5. Blueprint and delivery email CTAs point to `qualify.html`, preserve `lead`, `biz`, and `src` when known, and do not point to `/apply` or a direct calendar. (v2.4 — Rule 17) Every "See If You Qualify" CTA MUST also append `firstName`, `email` (from GHL, never fabricated — omit if absent), and `agents=<comma list of the lead's real agents>` so qualify.html prefills identity and Q7 renders dynamically. Audited by D2-27.
6. GitHub Pages build is complete before public HTML proof is accepted.
7. Repeat-submit GHL test and appointment/contact attachment are either verified or labeled `GHL partial` / `Calendar partial`.
8. Known-lead checks use verified email, phone, or contact ID; name-only GHL search cannot close a Brent-style proof gap.

**Receipt:** `stage-0-lead-capture-tracking.json` with public URLs, Pages build status, token sweep result, CTA sweep result, and GHL/Calendar proof labels.

**Step 0.0 — contacts-skill load (MANDATORY):**
Invoke `Skill("contacts-skill")` for the lead name BEFORE any GHL search.
contacts-skill returns canonical email, phone, GHL ID, and role.
Never skip — skipping = wrong email, wrong GHL record, wasted stages.

**Step 0.1 — Agent lock check (Gate Council-3):**
Check `~/Desktop/blueprint-{slug}/.pipeline-lock` before proceeding (see Agent Identity Lock section above).

**Step 0.2 — GHL token pre-flight (BLOCKING):**
```bash
LOC="14RD8KklxR9G4e0Rf7v2"
TOKEN=$(grep -o 'pit-[a-f0-9-]*' ~/.openclaw/gateway.env | head -1)
HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" -H "Version: 2021-07-28" \
  "https://services.leadconnectorhq.com/contacts/?locationId=$LOC&limit=1")
[ "$HTTP" = "200" ] || { /* self-heal: search Slack from:Kay #leo-coaches pit- newest → update gateway.env → retry */ }
```
If 401 → follow `feedback_ghl_401_self_heal_slack_gmail.md` chain before continuing.

**Step 0.3 — GHL contact search:**
```bash
curl -s "https://services.leadconnectorhq.com/contacts/?locationId=$LOC&query=LEAD+NAME&limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Version: 2021-07-28"
```
Extract: `id`, `email`, `phone`, `website`, `customFields[]`, `tags[]`

**Step 0.4 — Multi-record dedup rule:**
Prefer record with `ai blueprint opt-in` tag OR highest tag count. Skip `_test` records.

**Step 0.5 — Website URL resolution (if GHL website field is empty):**
1. Check GHL custom fields for URL-shaped value
2. Web search: `"[Lead First Last]" business site:linkedin.com OR site:[leadname].com`
3. Verify HTTP 200: `curl -sI [URL] | head -1`

**Step 0.6 — Slug generation:**
`lead-slug = lowercase(firstName + "-" + lastName)` → e.g. "brent-attaway"

**Step 0.7 — GHL form data extraction + normalization:**
Map custom field values to lead-profile.json keys:
```json
{
  "revenue_range": "$XXXk-$XXXk",
  "team_size": 50,
  "lead_volume": 50,
  "close_rate": 0.25,
  "avg_contract_value": 12000,
  "current_tools": ["Tool A", "B"],
  "tasks_to_automate": ["Admin"],
  "urgency_score": 6
}
```
`lead_volume`, `close_rate`, and `avg_contract_value` MUST be captured here — they feed ROI defaults in Stage 3 (Avg Customer Value = fill-in input default; leads & close-rate = slider defaults).

**Step 0.8 — Color extraction with Cloudflare fallback:**
Fallback chain (stop at first success):
1. `curl -sL [website] | grep -oE '#[0-9a-fA-F]{6}'`
2. CSS file direct
3. `og:image` meta → sample dominant hex
4. LinkedIn profile banner → sample dominant hex
5. Web search: `"[company name]" brand colors hex`
6. Final fallback: `#1a1a2e, #16213e, #0f3460, #e94560` (professional SaaS palette)

**Output:** Fully populated `lead-profile.json` on Desktop. Zero Bennett questions.

---

### Stage 1 — Lead Intake + Research + Registry Check
**Owner:** Mack
**Input:** Lead name, business URL, any form responses
**Actions:**
1. Scrape lead's website for: business name, services, tools used, brand colors, logo URL
2. Search GHL for contact record (contact ID, email, phone)
3. Search Notion for existing Blueprint records (dedup check)
4. Search Blueprint AI Artifact Registry for existing rows matching this lead name
   - If found: log existing Drive file IDs to lead-profile.json → skip re-uploading
   - If not found: proceed with clean slate
5. Create Notion sprint row for this lead
6. **Compute Stage 1 Input Hash** (Council v3.8 Improvement #5): SHA256 of `lead_name + email + revenue_range + lead_volume + close_rate + avg_contract_value + current_tools` → write to pipeline-state.json as `stage1_input_hash`

**Output:** `lead-profile.json` + pipeline-state.json initialized with stage 1 complete

### Stage 1.3 — Source Freshness Check (v3.5 — non-blocking)
**Owner:** Mack
**Purpose:** Ensure lead data is not stale before building.

**Rule:** If form submission timestamp is >30 days old:
1. Flag in #leo-coaches: "[lead name] form submission is [N] days old — re-confirm business still active before build"
2. Do NOT halt build automatically — flag only, continue with existing data
3. Append to lead-profile.json: `data_freshness: stale_>30d` with submission date

**Output:** `data_freshness` key in lead-profile.json (either `fresh` or `stale_>30d`)

### Stage 1.5 — Data Completeness Gate (v3.0 — BLOCKING)
**Owner:** Mack
**Rule:** Every template variable must resolve to a real value or `display:none`. Never a visible blank line.

**Required field resolution + fallback logic:**
```
{{years_in_business}} → GHL field → scrape "About" or footer copyright year → display:none
{{clients_helped}} → GHL field → website testimonials count → display:none
{{revenue_band}} → GHL custom field → industry default → "Growing business"
All {{variables}} → grep -E '\{\{[^}]+\}\}' blueprint.html must return 0 before Stage 3
```

**Auto-fix protocol:**
1. Run: `grep -E '\{\{[^}]+\}\}|: $|>\s*<' ~/Desktop/{slug}-blueprint.html`
2. For each blank/unresolved: add `style="display:none"` to parent element
3. Re-scan: must return 0 matches before advancing

**Output:** All template variables resolved or hidden. lead-profile.json has `data_completeness: verified`.

---

### Stage 2 — Demo Website Build — DEPRECATED
**Status: DEPRECATED — Bennett directive 2026-05-22. Website build removed from pipeline.**
**Do NOT run. Do NOT include website audit section in Blueprint HTML. Do NOT reference Stage 2 in orchestrator.**

---

### Stage 3 — Blueprint HTML (AI Playbook)
**Owner:** Mack
**Input:** lead-profile.json + Melissa v2 template (canonical)

**Pre-stage funnel lock check (v3.9 — BLOCKING):** Assert `~/Desktop/blueprint-{slug}/.funnel-health-pass` exists. If absent → re-run Stage 0.00 funnel health pre-flight before proceeding. Stage 3 refuses to start without this lock.

**Pre-stage hash check (Council v3.8):** Re-hash lead-profile.json key fields → compare to `stage1_input_hash`. Mismatch → re-run Stage 1 first.

**Actions:**
1. Clone Melissa v2 template — NOT Brittney v7 (archived as base)
2. Replace ALL lead-specific content: name, business, services, brand colors, agent descriptions
3. **PALETTE LOCK (v2.4 — Advaita-chrome default):** The blueprint chrome MUST use Advaita Apple-light tokens — `#0071E3` (accent/CTA), `#1D1D1F` (navy headings), `#F5F5F7` (light surface) — with the lead's brand color applied as exactly ONE `--lead-accent` variable. Do NOT build a full per-lead extracted palette and recolor the whole chrome with it. Reference advaita-design-skill + blueprint-ai-audit v2.3 checks D2-17 / D2-18 / D2-26. Write `~/.openclaw/state/palette-locks/{slug}.json` after color extraction (Advaita tokens + single `--lead-accent`). All HTML MUST use only these hex codes.
4. All sections per CANONICAL TEMPLATE STANDARD above (17 sections — no website audit, no Command Center)
5. Nav: 5 tabs — `Your Profile | AI Agents | ROI Calculator | Listen | Apply`
6. Agent prompts: 100+ lines each — full copy-paste ready
7. Hero stat text: timeline facts only — "30-Day Onboarding" (never "3/7/30", never bare "+X%")
8. Podcast player: native `<audio controls ...>` is MANDATORY (v2.4 — emits the native scrubber/seek bar) PLUS the custom 1x and 1.25x speed control buttons. Never ship an `<audio>` element without the `controls` attribute.
9. **ROI INPUT DEFAULTS (Rule 14 — HARD GATE):**
   ```javascript
   // Pull from lead-profile.json — these come from GHL custom fields
   const sliderLeads   = leadProfile.lead_volume || null;        // slider
   const sliderClose   = leadProfile.close_rate || null;         // slider
   const contractInput = leadProfile.avg_contract_value || null; // FILL-IN number input (id="sl-contract"), NOT a slider
   // Avg Customer Value renders as <input type="number" class="calc-fill-input" id="sl-contract"> — NEVER type="range"
   // If null: show "(enter your number)" placeholder, NOT a default number
   // NEVER: const sliderClose = 0.18; // BANNED
   // NEVER: const contractInput = 45000; // BANNED
   ```
   **AVG-TICKET HONESTY (Rule 18, v2.4):** The Avg Customer Value fill-in input must be USER-SET with no fabricated default UNLESS a real avg-ticket value exists in GHL intake. GHL currently has Revenue Range + Monthly Leads but NO avg-ticket field — adding one is a future intake-form improvement (note only; do not change GHL now).
   **LEADS-PER-SALE CLOSE-RATE (Rule 19, v2.4):** The close-rate input uses the leads-per-sale pattern as the standard — label "X leads = 1 sale (~Y% close)", `rate = 1 / leads_per_sale` — matching qualify.html.
10. **Drive link audit (Rule 8 — HARD GATE):** Before finalizing HTML, run:
    `grep -c 'drive.google.com' {slug}-blueprint.html` → must return 0. Any Drive link = fix immediately.
11. **Citation audit (Rule 5):** Every `<sup>` or footnote reference must have clickable `<a href="[real URL]">`.
12. Push to GitHub Pages at fki-preview/blueprints/[lead-name].html
13. Verify HTTP 200

**MOBILE STANDARD (v2.5 — HARD REQUIREMENTS):**
| Requirement | Verify |
|---|---|
| Hamburger nav | `grep "navHamburger"` |
| Font floor ≥0.78rem | `grep -E "0\.[67][0-9]rem"` = 0 |
| Table overflow | `grep "overflow-x: auto"` ≥3 |
| OG meta | `grep "og:title"` |
| Progress bar | `grep "readingProgress"` |
| Sticky mobile CTA | `grep "mobile-cta-bar"` |
| Touch targets 44px | `grep "min-height: 44px"` |

**ARTIFACT SAVE — Blueprint HTML:**
1. Upload Desktop HTML to Drive: `blueprints/{lead-slug}-blueprint.html`
2. Verify fileSize > 50KB
3. Set permissions: bennett@=Writer, bennettmaxwell35@=Writer, madison@=Writer, kay@=Reader
4. Update Blueprint AI Artifact Registry row

**Output:** Live Blueprint URL (HTTP 200) + Desktop HTML copy + pipeline-state.json updated

### Stage 3.5 — Podcast URL Gate (v3.5 — BLOCKING before Stage 4)
**Owner:** Mack
**Rule:** Before Stage 4 fires, verify the Listen section is correctly set up:
1. `grep -c 'podcasts/.*\.mp3\|podcast_status.*generating' {slug}-blueprint.html` — must return ≥1
2. If podcast not yet generated: set Listen section to placeholder state with "Generating..." text and note in lead profile: `podcast_status: pending`
3. **HARD GATE:** Never set `href=""` on the Listen button — empty href = delivery failure
4. Never set `podcast_status: ready` until GitHub Pages URL returns HTTP 200

**Why:** Every Blueprint delivered with broken Listen links was caused by wiring the href AFTER HTML was finalized.

**Output:** Listen section has real URL or explicit "Generating..." placeholder. `podcast_status` written to lead-profile.json.

### Stage 4 — NotebookLM Podcast
**Owner:** Mack (via notebooklm-py)
**Input:** Blueprint HTML content → NotebookLM source doc
**Actions:**
1. Use notebooklm-blueprint-ai-skill v1.4 (NOT generic notebooklm-skill) — Drive ID: 1zFoUSa7Wp7do8aqKDgk72U8wX6sHYxmo8fVKVdcPLqs
   - GitHub Pages-only URLs
   - e2e inbox test required
   - native `<audio controls>` (mandatory, v2.4) + 1x+1.25x speed controls
   - Send link to bennett@+madison@ after generation
   - Unified 7-segment structure
2. Generate 12-section NotebookLM source doc (18-20KB markdown with objection handling)
3. Create notebook + upload source + generate audio via notebooklm-py
4. Download podcast MP3/MP4 — WALKTHROUGH WINDOW 6-20MB (~6-20 min @128kbps). < 6MB = FAIL (too short). > 20MB = FAIL (too long, a lecture not a walkthrough) — re-generate SHORTER (target 12-18 min). The old "≥29MB" floor was BACKWARDS and forced 30+ min podcasts; it is removed.
5. Upload to GitHub Pages at fki-preview/podcasts/[slug].mp3
6. Verify HTTP 200
7. Wire podcast URL into Blueprint HTML Listen section
8. Update pipeline-state.json: `podcast_url` + `http_200_checks.podcast_url: true`

**Receipt (Council v3.8):** Write `receipts/stage-4-notebooklm.json` with status, podcast_url, file_size_mb, gates_passed.

**ARTIFACT SAVE — Podcast:**
1. Search Drive for existing podcast: title contains '{lead-slug}' + mimeType contains 'audio'
   - If found: verify fileSize is inside the 6-20MB walkthrough window, update permissions + Registry
   - If not found: upload to Drive: blueprints/podcasts/{lead-slug}-podcast.mp3
2. Verify fileSize inside 6-20MB window (< 6MB or > 20MB = re-generate; > 20MB means too long, regenerate shorter)
3. Set permissions: bennett@=Writer, bennettmaxwell35@=Writer, madison@=Writer, kay@=Reader
4. Update Blueprint AI Artifact Registry row

**Output:** Live podcast URL (HTTP 200) + Desktop file

### Stage 5 — AI Prompts
**Owner:** Mack
**Input:** lead-profile.json (industry, services, tools)
**Actions:**
1. Generate 3 industry-specific AI prompts — FULL copy-paste ready, 100+ lines each
2. Prompt structure: ## IDENTITY + ## INPUTS YOU NEED + ## STRUCTURE + ## RULES (with examples)
3. Prompt 1: Speed-to-Lead Response Agent
4. Prompt 2: Follow-up / Communication / Lifecycle Agent
5. Prompt 3: Operations / Reporting / Proposal Agent
6. Embed in Blueprint HTML under Prompts section

**Output:** 3 prompts (100+ lines each) embedded in Blueprint

### Stage 6 — Audit Gate (blueprint-ai-audit-skill v2.6 — REQUIRED SCORE: 100/100)
**Owner:** Mack
**Skill file:** `1Wp7zzDlp4uzeEX8vTIQv0_RsJp70ORLM`
**REQUIRED SCORE: 100/100. Not 90. Every check must pass.**
**Current version: v2.6.0 (149 checks across 10 domains, 22 red-line)**

**v2.2.0 additions (2026-05-26):**
- Domain 9 — Formatting & Render Integrity (20 checks, 1 red-line): catches orphan CSS classes, undefined vars, missing mobile breakpoints
- Domain 4 reconciled: standalone website retired, Command Center + podcast checks replace old website checks
- RED LINE D0-22: End-to-End Email Click Test — send preview to bennett@, open in Gmail, click every button. INSTANT FAIL if not completed.
- Slack alert if score <85 → auto-fix loop (max 3) → escalate if still <85

**v3.8 ADDITIONAL AUDIT CHECKS (Gates 26-29):**
- CHECK D3-26: `grep -c 'drive.google.com' blueprint.html` = 0 (zero Drive links)
- CHECK D3-27: `grep -cE '(12%|18%|0\.12|0\.18|45000|45,000)' blueprint.html` = 0 (no hardcoded ROI)
- CHECK D3-28: Hero section — scan for bare "+XX%" without adjacent `<a href=`. Must return 0.
- CHECK D3-29: `grep -c 'id="listen"\|podcasts/' blueprint.html` ≥ 1 (podcast section present and linked)

**v3.9 DELIVERY GATE (Gate 30 — MANDATORY — Bennett directive 2026-05-23):**
- CHECK D3-30: `grep -c 'preload="metadata"\|preload=.metadata.' blueprint.html` ≥ 1 (audio player has preload=metadata)
  - Root cause: missing preload=metadata causes silent audio failure on mobile; player appears but never loads
  - Fix: inject `preload="metadata"` on the `<audio>` tag OR hidden audio preload element
  - HARD BLOCK: Stage 7 email cannot send until this check returns ≥ 1

**Execution:**
```bash
→ Execute Skill("blueprint-ai-audit-skill") with blueprint_html_path and lead_slug
```

**Autonomous fix loop (max 3 rounds):**
1. Run audit → receive score + failed check list
2. For each failed check: load council-skill, get fix strategy, execute fix
3. Re-run audit after each fix
4. 100/100 + e2e PASS → invoke Skill("gatekeeper-skill") — see Stage 6.5 below
5. Still failing after 3 rounds → post to #leo-coaches, Ivan/Mack self-diagnose directly

**Hard rules:**
- NEVER send email before audit score = 100/100 AND e2e click test = PASS
- NEVER skip audit to "save time"
- Score <85 → Slack #leo-coaches alert required before proceeding

### Stage 6.5 — Gatekeeper Verification (MANDATORY — NEW v3.12 — baked in)
**Trigger:** After audit = 100/100. BEFORE Stage 7 email send.
**Owner:** Mack (Ivan CC)
**Purpose:** Final quality gate. Prevents shipping anything the audit-skill missed.

**Actions:**
1. Invoke Skill("gatekeeper-skill") on the blueprint HTML file
2. Gatekeeper runs: worker → auditor → council improvement loop → ledger write
3. Run repo-local Gatekeeper 100 in production mode.
4. Gatekeeper MUST score 100/100 and write `<lead-slug>-gatekeeper-pass-token.json`.
5. On FAIL: council-skill fires one improvement round → fix → re-run Gatekeeper 100 → if still failing after 3 rounds, post to #leo-coaches.

**HARD GATE:** Stage 7 email CANNOT send without `audit-receipts/<lead-slug>/<lead-slug>-gatekeeper-pass-token.json` from:

```bash
python3 scripts/blueprint_gatekeeper_100.py \
  --mode production \
  --lead <lead-slug> \
  --html blueprints/<lead-slug>.html \
  --receipt-dir audit-receipts/<lead-slug>
```

Verify the token before send:

```bash
python3 scripts/blueprint_gatekeeper_100.py \
  --verify-token \
  --mode production \
  --lead <lead-slug> \
  --token audit-receipts/<lead-slug>/<lead-slug>-gatekeeper-pass-token.json
```

**What gatekeeper catches that audit misses:**
- Podcast forefront position (D3-16) — validates callout is actually FIRST visible element
- CTA phrase exact rendering in rendered HTML (not just source)
- Email draft alignment with page content
- Link click verification (actually navigates to correct destination)
- Mobile rendering check

**Permanent rule (v3.12 — Bennett directive 2026-05-27):** Gatekeeper is NOT optional. NOT for "high-stakes" blueprints only. Runs on EVERY blueprint before Stage 7 regardless of audit score.

### Stage 7 — Email Delivery
**Owner:** Mack
**Actions:**
1. Build Apple-style HTML email with 2 deliverable blocks (Blueprint HTML + Podcast)
   - ALL URLs must be GitHub Pages URLs. ZERO Drive links in email.
2. Write HTML to `~/Desktop/[lead-slug]-delivery-email.html`
3. Send PREVIEW to Bennett only through the token-verifying wrapper:
   `bash scripts/build-delivery-email.sh leads/[lead-slug].json --send-preview --gate-token audit-receipts/[lead-slug]/[lead-slug]-gatekeeper-pass-token.json`
4. After Bennett approval → send only through:
   `bash scripts/send-approved.sh [lead-slug] --bennett-approved --gate-token-dir audit-receipts/[lead-slug]`

**DUAL-SEND RULE (v3.10 — HARD):** ALL blueprint delivery emails and CEO results emails send to `bennett@franchiseki.com` (TO) with `madison@franchiseki.com` (CC). NEVER send to brent@ — brent@ is an external prospect, NOT an internal team member. This includes preview emails, CEO results emails, and any page-delivery notifications. Root cause: R39 correction — emails were sent to brent@ instead of bennett@. (Memory: feedback_email_wrong_recipient.md)

**HARD GATE:** Podcast URL HTTP 200 is not enough. Email cannot send unless the Gatekeeper 100 production token validates. Direct `gog gmail send` is banned for Blueprint delivery.

**Bennett approval mechanism:**
Approval = ANY ONE of:
- Bennett replies "send it", "go", "approved", or "looks good" to the preview email
- Bennett adds `blueprint-approved` tag to GHL contact record
- Bennett sends Slack DM with "send [lead name] blueprint"

Poll for approval: check Gmail inbox + GHL contact tags at 5min intervals × 3 (15min max). If no response after 15min → surface in next recap-skill footer as 🟣 HUMAN OPEN.

**Madison governance:**
- Blueprint preview CC: madison@franchiseki.com (CC only — NEVER in TO field)
- Bennett approval signals required before any forward to prospect

### Stage 7.75 — CEO Results Email
**Owner:** Mack
**Trigger:** After Stage 7 delivery email is sent or staged for approval
**Recipient:** bennett@franchiseki.com (INTERNAL — auto-send via gog)
**Actions:**
Build and send plain-text results summary:
```
Subject: Blueprint Delivered: [Lead Name] — [Business] | [date]

Lead: [Name] | [Business] | [email]
Revenue range: [X] | Urgency: [X]/10 | Source: [X]

Deliverables:
✓ Blueprint HTML: [GitHub Pages URL]
✓ Podcast: [GitHub Pages URL] ([file size]MB)
✓ Delivery email: staged / sent

Pipeline stage: [GHL stage]
Drive artifacts: [count] files shared

Next: Apply quiz verification pending.
```

### Stage 7.25 — Advaita AI Application Form
**Owner:** Mack
**Skill:** → Execute `advaita-apply-skill` (Drive: `1IXQ89dYOQq_kDx4XTM6uB0oYYsLyHbA9`)
**Trigger:** Fires after Stage 7 email delivery.
**Actions:**
1. Verify `qualify.html` is live (HTTP 200)
2. Verify first name, last name, business, email, and phone are required before CTA enables
3. Verify the qualifier webhook payload includes source, lead_session_id, optional contact_id, qualification band, and all 8 answers
4. Verify GHL workflow matches/upserts by email/phone and applies the correct tags (`advaita-qualified`, `advaita-review-needed`, `advaita-not-fit`)
5. Verify Book-a-Call modal opens only after qualified/review-needed submit; not-fit routes to thank-you-blueprint.html
6. Verify Blueprint HTML and delivery email CTAs point to `qualify.html`, not `/apply`, direct calendar, or stale `blueprint.meetadvaita.com/apply`
7. Verify five repeat qualifier submits from the same test identity update one GHL contact, not duplicate contacts, or label `GHL partial`
8. Verify booked appointment attaches to the same GHL contact, or label `Calendar partial`

**7 Questions (council-locked 2026-05-21):**
1. Which AI agent first + what problem does it solve?
2. What would 10+ hrs/week back mean for your business?
3. Total monthly marketing spend including ad spend + content?
4. #1 thing holding back next revenue tier?
5. Currently using any AI tools? Which ones?
6. Urgency 1-10 for competitive edge in 60 days?
7. What would need to be true for this to be your best 2026 decision?

### Stage 7.5 — Apply Quiz Verification
**Owner:** Mack
**Actions:** Verify apply quiz live + webhook wired + scoring payload correct.

---

## Diamond Gate (runs after Stage 7.5) — 11 tests

| # | Test | What it checks |
|---|------|----------------|
| T1 | Adversarial | 10-point pre-delivery check on all deliverables |
| T2 | Failure Recovery | All files render offline, graceful font degrade |
| T3 | Boundary | NaN guards, slider safety, calculator edge cases |
| T4 | Edge Case | Cross-contamination, unique brand colors/titles per lead |
| T5 | Regression | All URLs HTTP 200, podcast live, qualifier identity capture live, email delivered |
| T6 | Artifact Registry | Blueprint HTML + Podcast have Drive File ID ≠ blank + HTTP 200=✅ + Permissions=✅ |
| T7 | Zero Drive links | `grep -c 'drive.google.com' blueprint.html` = 0 |
| T8 | ROI not hardcoded | `grep -cE '(12%\|18%\|0\.12\|0\.18\|45000)' blueprint.html` = 0 |
| T9 | Zero bare hero % | Hero section: no "+XX%" without adjacent `<a href` |
| T10 | All footnotes clickable | Every `<sup>` reference has `<a href="[real URL]">` |
| T11 | Skill loader passed | `receipts/stage--1-skill-loader.json` exists + status=COMPLETE |

T6-T11 FAIL → BLOCK Diamond.

---

## Skill Inventory (Blueprint AI ecosystem)

| Skill | Drive ID | Purpose | Status |
|-------|-------------|---------|--------|
| blueprint-ai-skill (this) | 1IzE-seDDaB1Tciik9mwBVrgQcb7FP7eH | Master orchestrator | CANONICAL v3.8 |
| notebooklm-blueprint-ai-skill | 1zFoUSa7Wp7do8aqKDgk72U8wX6sHYxmo8fVKVdcPLqs | Podcast framework v1.7 | ACTIVE v1.7 |
| blueprint-lead-intake-skill | 1e6_7KSS_KSwWJTrCdn7oDx3Fl_YmRxB3 | Lead intake + Notion row | ACTIVE |
| blueprint-ai-audit-skill | 1Wp7zzDlp4uzeEX8vTIQv0_RsJp70ORLM | Stage 6 audit 149/149 gate | ACTIVE v2.6.0 |
| advaita-apply-skill v1.0 | 1IXQ89dYOQq_kDx4XTM6uB0oYYsLyHbA9 | Stage 7.25 — 7Q apply form | ACTIVE |
| apply-scoring-skill v2.0 | 1gYaAerxXQO | Stage 7.5 — Internal scoring | ACTIVE |
| diamond-skill v2.2 | 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT | Post-build QA (11 tests v3.8) | ACTIVE |

## Related Notion Pages
| Page | URL | Purpose |
|------|-----|---------|
| Blueprint AI Agent Boot Hub | 365cf5514fd3811b840ffec0080c1990 | Boot page |
| Blueprint AI Artifact Registry | 328a4ee00ca84c9b8e8134067fa04609 | Artifact tracking |
| Blueprint AI Pipeline | 366cf5514fd38160885cea3680b9f2e7 | 10-lead status |
| Sprint Board | 335cf5514fd3813488dec82a68622d7b | Active sprint rows |

---

## Anti-Patterns

- ~~Skipping Stage 2 (website build)~~ — Stage 2 is DEPRECATED, do not run it
- Rebuilding Blueprint from scratch instead of cloning Melissa v2 template (-5)
- Hardcoding ROI dollar amounts (-3)
- Hardcoding 12%, 18%, or $45,000 in ROI calculator (-5) — HARD GATE
- Using direct booking URLs or calendar links outside the tracked qualifier submit flow (-5)
- Fabricating business data, testimonials, or stats (-5)
- Skipping pre-delivery check (-3)
- Sending to lead without Bennett preview approval (-5)
- Sending before podcast URL is HTTP 200 (-5) — HARD GATE
- Using Drive links (drive.google.com) in Blueprint HTML or delivery email (-5) — HARD GATE
- Using Hyperagent instead of Mack/Ivan for delivery (-3)
- Emojis in any client-facing deliverable (-3)
- Hero stat showing "3/7/30" — looks like a date (-2)
- Hero stat showing "+X%" without clickable source link (-4) — HARD GATE
- Bare text citation (no `<a href>`) in footnotes or stats (-4)
- Running pipeline with local skill version < Drive version (-5) — HARD GATE
- Skipping Artifact Registry update before Diamond (-5)
- Using generic notebooklm-skill instead of blueprint-podcast-framework-skill (-3)
- Command Center tab in Blueprint HTML nav (-3) — REMOVED
- Running Stage 4 before Stage 3.5 gate passes (-3)
- **Council v3.8: Advancing to next stage without writing pipeline-state.json (-3)**
- **Council v3.8: Starting pipeline for a slug that has active `.pipeline-lock` < 30min (-5)**
- **Council v3.8: Not writing sub-agent receipt after sub-skill invocation (-3)**
- Assuming prospect's business is disorganized — ALWAYS assume excellence (-5)
- Saying "AI learns your brand voice over time" — it launches at 90%+ accuracy (-3)

---

## Self-Audit Checklist (18 mechanical checks)

> **SOP-COVERAGE CONTRACT (v3.15, 2026-05-31):** angie-audit / angie-weekly executes each item *mechanically* (stat a path, grep this SKILL.md, jq a value, curl a probe). Items phrased as human-judgment questions ("Does the skill reference X?") are skipped as `HUMAN_CHECK` and do NOT count toward coverage — that is why the prior 14-question checklist scored only ~0.50. Every item below is a runnable assertion with a concrete command and a PASS condition, so coverage = 1.0. Run from the skill dir: `cd ~/.claude/skills/blueprint-ai-skill`.

1. [ ] 16 permanent rules present: `grep -cE "^(Rule |[0-9]+\. )" SKILL.md` for the permanent-rules block ≥ 16. PASS if count ≥ 16.
2. [ ] All active stages present: `for s in -1 0 1 1.3 1.5 3 3.5 4 5 6 7 7.25 7.5 7.75; do grep -q "Stage $s" SKILL.md || echo "MISSING $s"; done` → no MISSING output.
3. [ ] Stage 2 deprecated: `grep -qiE "Stage 2.*(DEPRECATED|REMOVED)" SKILL.md`. PASS = exit 0.
4. [ ] Stage 6 audit checks D3-26..D3-29: `for c in D3-26 D3-27 D3-28 D3-29; do grep -q "$c" SKILL.md || echo MISS; done` → no MISS.
5. [ ] Melissa v2 template referenced: `grep -qiE "Melissa v2.*(template|mandatory|gold standard)" SKILL.md`. PASS = exit 0.
6. [ ] Bennett-first email approval: `grep -qiE "Bennett (first|approval).*(before|prior to) (send|delivery)|approval gate" SKILL.md`. PASS = exit 0.
7. [ ] Diamond gate T6-T11 after Stage 7.5: `grep -q "Stage 7.5" SKILL.md && for t in T6 T7 T8 T9 T10 T11; do grep -q "$t" SKILL.md || echo MISS; done` → no MISS.
8. [ ] Podcast HTTP 200 hard gate: `grep -qE "curl -fsI.*PODCAST_URL.*200|probe-podcast-url.sh" SKILL.md`. PASS = exit 0.
9. [ ] 17 required Blueprint sections enumerated: `grep -cE "^\| ?[0-9]+ ?\|" SKILL.md` over the sections table ≥ 17, AND `! grep -qi "website audit\|Command Center" SKILL.md` in the sections list. PASS = both.
10. [ ] Artifact Save steps in Stages 3,4 + T6: `grep -qE "Artifact (Save|Vault).*Stage 3" SKILL.md && grep -qE "Artifact (Save|Vault).*Stage 4" SKILL.md && grep -q "T6" SKILL.md`. PASS = exit 0.
11. [ ] Stage -1 Skill Loader Gate BLOCKING: `grep -qE "Stage -1.*Skill Loader Gate" SKILL.md && grep -qiE "Stage -1.*BLOCKING|Skill Loader.*BLOCKING" SKILL.md`. PASS = exit 0.
12. [ ] ROI default rules (GHL, no hardcoded): `grep -qiE "ROI.*GHL field" SKILL.md && ! grep -qE "\\\$45K|\\b12%\\b.*hardcoded|\\b18%\\b.*hardcoded" SKILL.md`. PASS = exit 0.
13. [ ] Drive link bans enforced 4 places: `grep -cE "Drive link.*(ban|forbidden|no drive\\.google)" SKILL.md` ≥ 1 AND each of Stage 3 / Stage 6 / Stage 7 / Diamond T7 referenced near a ban line. PASS = count ≥ 1.
14. [ ] Podcast NOT banned (Stage 4 active): `! grep -qiE "Gate 29.*podcast ban.*ENFORCED|podcast.*REMOVED" SKILL.md && grep -q "Stage 4" SKILL.md`. PASS = exit 0.
15. [ ] Enforcement dir exists with gate scripts: `[ -d enforcement ] && [ $(ls enforcement/*.sh 2>/dev/null | wc -l) -ge 5 ]`. PASS = exit 0.
16. [ ] Frontmatter complete: `head -20 SKILL.md | grep -qE "^name:" && grep -qE "^version:" SKILL.md && grep -qE "^drive_file_id:" SKILL.md`. PASS = exit 0.
17. [ ] Last successful pipeline run < 14 days: `find ~/Desktop/blueprint-* -name 'stages-completed.txt' -mtime -14 2>/dev/null | head -1` non-empty, OR tag `HUMAN_CHECK` if no leads processed this window.
18. [ ] Version pin consistent: frontmatter `version:` ≥ the `SKILL_VERSION_REQUIRED` literal — `python3 -c "import re,sys;t=open('SKILL.md').read();v=re.search(r'^version:\s*([0-9.]+)',t,re.M).group(1);r=re.search(r'SKILL_VERSION_REQUIRED[^0-9]*([0-9.]+)',t);sys.exit(0 if (not r or float(v)>=float(r.group(1))) else 1)"`. PASS = exit 0.

**Coverage scoring:** Skill SOP coverage = (mechanical items that ran AND are not HUMAN_CHECK) / total items. Items 1-16,18 are pure-mechanical (always executable); item 17 degrades to HUMAN_CHECK only when no leads were processed. Target coverage ≥ 0.94.

---

## Version History

- v3.15 (2026-05-31): Self-Audit Checklist rewritten from 14 human-judgment questions to 18 MECHANICAL assertions (grep/stat/jq/curl) + SOP-COVERAGE CONTRACT note. Raises angie SOP coverage from ~0.50 (half were HUMAN_CHECK-skipped) toward ~0.94. Items 15-18 added (enforcement dir, frontmatter, last-run freshness, version-pin consistency).

- v1.3 (2026-05-17): Initial skill on Drive
- v2.0 (2026-05-19): Full orchestrator rewrite. 10 permanent rules codified.
- v2.3 (2026-05-21): Melissa layout canonical. Website Audit added.
- v2.4 (2026-05-21): Artifact Vault + Drive share per stage + T6 Diamond gate.
- v2.5 (2026-05-21): Mobile standard — hamburger nav, font floors, table overflow, OG meta.
- v2.8 (2026-05-21): Lead Discovery Chain — Stage 0 added. Never ask Bennett for URL.
- v3.0 (2026-05-21): Stage 1.5 data completeness gate. Palette lock file. Stage 6 → audit-skill 100/100.
- v3.1 (2026-05-22): Tone + Brand Voice — Rules 12+13. Assume excellence. Brand voice built before launch.
- v3.3 (2026-05-22): 25 Mechanical Gates. Enforcement scripts. Stage 4/6 cannot be skipped.
- v3.5 (2026-05-22): Stage 1.3 source freshness. Stage 3.5 podcast URL gate. Rules 14+15 (Ivan). Audit v1.4. NotebookLM v1.4.
- v3.8 (2026-05-22): WEBSITE DEPRECATED (Stage 2 removed). Stage -1 Skill Loader Gate. Rule 14=ROI from GHL, Rule 15=All leads get Blueprint, Rule 16=No bare % hero. Drive link ban (Rule 8 rewritten). Nav locked to 5 tabs. Gates 26-29 added. Diamond T7-T11 added. 5 council improvements: Sub-Agent Receipts, Pipeline State Manifest, Agent Lock, Failure-to-Patch Loop, Stage Input Hash.
- v3.10 (2026-05-26): 72hr error audit hardening. Fixed: brent@ CC→madison@ (brent is external prospect per R39). Audit skill ref v1.4→v2.2.0 (129 checks, 9 domains). Podcast skill ref v1.4→v1.7. SKILL_VERSION_REQUIRED 3.8→3.9. Dual-Send Rule corrected. All version refs synchronized.
- v3.9 (2026-05-23): 5-Page Funnel Map documented (commit 076ed9b). thank-you-blueprint.html gold standard added: 9-change council rebuild — 48h review framing, AI agents education section, no fabricated attribution, no podcast card, no booking URL, no 90-day language. All 8 audit checks documented as PASS. Council 10-improvement plan executed: Gates 30–34 added (funnel redirect chain, TY content regression guards, blueprint CTA check), Stage 0.00 Funnel Health Pre-flight added, Stage 3 funnel lock gate added, Stage 7 Dual-Send Rule documented, Notion stage-timestamp protocol added.

---

## 29 MECHANICAL GATES (v3.3 base + v3.8 additions)

**Root cause of Rey 31C failure:** Orchestrator skipped Stage 4 and Stage 6. Prose rules were ignored. v3.3 replaced prose with file-existence + exit-code gates. v3.8 adds Gates 26-29.

**Enforcement directory:** `~/.claude/skills/blueprint-ai-skill/enforcement/`
**Per-lead artifact dir:** `~/Desktop/blueprint-{slug}/`

| # | Gate | Mechanism | Where it lives |
|---|------|-----------|----------------|
| 1 | Podcast MP3 in window | `[[ -f artifacts/{slug}/podcast.mp3 && $(stat -f%z) -ge 6291456 && $(stat -f%z) -le 20971520 ]] \|\| exit 87` (6-20MB walkthrough window; old ≥29MB floor removed) | `enforcement/gate-stage4.sh` |
| 2 | Podcast HTTP 200 probe | `curl -fsI $PODCAST_URL \| grep -q "200" \|\| exit 87` | `enforcement/probe-podcast-url.sh` |
| 3 | Audit score lockfile | Stage 6 writes `.audit-100.lock` ONLY when score==100 | SKILL.md §Stage 6/§Stage 7 |
| 4 | Audit score numeric parser | `SCORE=$(jq -r .total audit.json); [[ "$SCORE" == "100" ]] \|\| exit 89` | `enforcement/parse-audit-score.sh` |
| 5 | Orchestrator stage-counter | `diff <(seq 1 6) stages-completed.txt \|\| exit 90` before email | SKILL.md §Orchestrator Entry |
| 6 | Pre-email hard-stop wrapper | Direct `gog gmail send` BANNED. All sends route through `enforcement/send-blueprint-email.sh` | SKILL.md §Stage 7 |
| 7 | "Audio pending" string ban | `grep -q "Audio pending" blueprint.html && exit 91` | `enforcement/html-content-check.sh` |
| 8 | Drive upload receipt | T6 writes `.drive-uploaded.json`; pre-email asserts IDs return 200 via Drive API | SKILL.md §T6 |
| 9 | Registry row assertion | `python3 enforcement/check-registry-row.py {slug}` queries Notion DB 328a4ee0 | pre-email wrapper |
| 10 | NotebookLM source ≠ MP3 detector | If `.md` exists but `.mp3` missing → auto-fire podcast-framework retry (3× cap) | `enforcement/stage4-self-heal.sh` |
| 11 | Stage skip detector | Orchestrator log parsed for `STAGE_SKIPPED` tokens → exit 93 + Slack | `enforcement/skip-detector.sh` |
| 12 | Placeholder scan | `grep -E "PENDING\|TBD\|TODO\|Audio pending\|placeholder" blueprint.html && exit 94` | `enforcement/placeholder-scan.sh` |
| 13 | SKILL.md version pin | Orchestrator reads `version:` from frontmatter; if `<3.8` refuses to run | SKILL.md §Orchestrator Entry |
| 14 | Stage transition manifest | Each stage emits `stage-N.done` with SHA256; Stage N+1 verifies N's manifest | `enforcement/stage-manifest.sh` |
| 15 | Draft-not-send fallback | Any gate fail → wrapper drops to `gog gmail draft` + Slack alert, never silently sends | `enforcement/send-blueprint-email.sh` |
| 16 | Pre-commit hook | `.git/hooks/pre-commit` blocks SKILL.md commits that REMOVE gate strings | skills repo |
| 17 | LaunchAgent delivery-audit (15min) | Scans last 24h Sent, re-runs all gates against delivered URL | `com.fki.blueprint.delivery-audit.plist` |
| 18 | Daily Drive-vs-delivered diff (9am) | Every emailed slug must have Drive folder with mp3 + html + audit.json | `com.fki.blueprint.drive-delivery-diff.plist` |
| 19 | Registry-vs-Sent reconciler (hourly) | Every `blueprint-delivery` tagged Sent must have Registry row | `com.fki.blueprint.registry-reconcile.plist` |
| 20 | HTTP 200 link-checker (cron) | Fetches every emailed blueprint URL, asserts mp3 src returns 200 | `enforcement/link-check-cron.sh` |
| 21 | Orchestrator pre-flight (Step 0) | Validates skill version, notebooklm creds, drive creds, registry write access, gog, jq | `enforcement/preflight.sh` |
| 22 | Self-heal retry budget | Stage 4 self-heal hard cap (3 retries, 90min) → #leo-coaches + HALT | `enforcement/stage4-self-heal.sh` |
| 23 | Email subject embeds audit score | Subject template requires `[AUDIT:100]` token — impossible to send without real score | `templates/blueprint-email-subject.tmpl` |
| 24 | Slack receipt with gate stamps | Post-delivery Slack MUST contain `mp3:OK url:OK audit:100 drive:OK registry:OK` | `enforcement/post-delivery-slack.sh` |
| 25 | Weekly compliance audit (Sun 11pm) | 100% week deliveries re-audited; <100% → autopilot council-skill to harden | `com.fki.blueprint.weekly-compliance.plist` |
| 26 | Drive link ban | `grep -c 'drive.google.com' blueprint.html` = 0; any match → exit + Slack | `enforcement/html-content-check.sh` (v3.8 ext) |
| 27 | ROI default ban | `grep -cE '(12%\|18%\|0\.12\|0\.18\|45000\|45,000)' blueprint.html` = 0 | `enforcement/html-content-check.sh` (v3.8 ext) |
| 28 | Hero % stat ban | Hero section grep: bare "+XX%" without adjacent `<a href` = 0 | `enforcement/html-content-check.sh` (v3.8 ext) |
| 29 | Podcast section present | `grep -c 'id="listen"\|podcasts/' blueprint.html` ≥ 1 | `enforcement/html-content-check.sh` (v3.8 ext) |
| 30 | Funnel redirect chain verification | `apply/index.html` JS redirect → `../thank-you-apply.html`; `qualify.html` identity + 8-answer CTA posts webhook before booking modal or thank-you redirect. Writes `.funnel-health-pass` lock. | `enforcement/funnel-health-check.sh` |
| 31 | TY-blueprint.html content regression guard | `grep -ciE "podcast being built\|blueprint being built\|check your inbox in.*24\|your podcast is being built" thank-you-blueprint.html` = 0. Prevents revert to wrong Step 5 content. | `enforcement/funnel-health-check.sh` (v3.9) |
| 32 | TY-apply.html content regression guard | `grep -ciE "qualifier\|you qualified\|application received.*team reviews" thank-you-apply.html` = 0. Prevents Step 2/5 content swap. | `enforcement/funnel-health-check.sh` (v3.9) |
| 33 | qualify.html tracked-submit gate | Confirm contact fields exist, CTA starts disabled, webhook URL is present, and booking modal exists; fail if `qualify.html` only links directly to `thank-you-blueprint.html` without a submit handler. | `enforcement/funnel-health-check.sh` |
| 34 | Blueprint CTA links to qualify.html | `grep -oP 'href="[^"]*"' blueprints/{slug}.html \| grep -q "qualify.html"` on the primary Apply CTA. HALT if missing before delivery. | `enforcement/html-content-check.sh` (v3.9 ext) |

**Orchestrator entry contract (v3.8):**
1. Check Agent Identity Lock (Council Gate Council-3) — abort if active lock < 30min
2. Source `enforcement/preflight.sh` (Gate 21) — exit if fails
3. Run Stage -1 Skill Loader Gate — write `receipts/stage--1-skill-loader.json` — exit if fails
4. Initialize `artifacts/{slug}/pipeline-state.json` + `stages-completed.txt`
5. After each stage: update pipeline-state.json + append stage number + run stage-manifest gate
6. After Stage 1: compute stage1_input_hash → write to pipeline-state.json
7. Before Stage 3: verify stage1_input_hash — re-run Stage 1 if mismatch
8. Between Stage 4 → 5: run `gate-stage4.sh` (Gates 1, 2, 7)
9. Between Stage 6 → 7: assert `.audit-100.lock` exists (Gate 3)
10. Stage 7 send: ROUTE THROUGH `send-blueprint-email.sh` ONLY (Gates 4, 6, 8, 9, 12, 15, 23)
11. Post-delivery: `post-delivery-slack.sh` (Gate 24)
12. After each sub-skill: write receipt to `receipts/` dir, assert status=COMPLETE

---

## Cron Bindings

- `com.fki.blueprint.delivery-audit` — 15min, re-runs gates on last 24h sent (Gate 17)
- `com.fki.blueprint.drive-delivery-diff` — daily 9am MDT (Gate 18)
- `com.fki.blueprint.registry-reconcile` — hourly orphan reconciler (Gate 19)
- `com.fki.blueprint.weekly-compliance` — Sun 11pm MDT, compliance audit + Failure-to-Patch check (Gate 25 + Council v3.8 Improvement #4)
