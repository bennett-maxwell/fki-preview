---
name: blueprint-ai-audit-skill
version: 2.11
last_updated: 2026-06-02
changelog_v2.11: >
  GATE-MISCLASSIFICATION + EMAIL-CONFORMANCE LESSONS (2026-06-02, from two
  fki-preview feedback memories). (1) home_services_content_gate (D10-22) added a
  SaaS/software/crm/platform/b2b/tech-company exclusion that runs BEFORE the
  home-services term match — a SaaS vendor whose target market is "for home
  service businesses" (CRMX/brent-attaway) is NOT a home-services operator and
  must not be subjected to the operator-copy gate. Permanent lesson: when a
  content red-line fires on a B2B/SaaS lead, fix the gate's classifier, never
  rewrite correct copy. (2) Email Design Conformance D5-17 reconciled to the real
  Madison send TEMPLATE (white #FFFFFF OR legacy #F5F5F7 bg; injected bgcolor
  accent OK); added D5-22 (no flexbox — Outlook strips it) and D5-23 (no <style>
  block — inline-only) as red-lines; documented that the send path is the
  TEMPLATE (templates/delivery-email-template.html), never the output files, and
  the generator sed_esc() &-escaping fix caught by the HARD conformance gate.
changelog_v2.10: >
  CONTRACT-FIELD FILL-IN ALIGNMENT (Bennett directive 2026-06-02, companion to
  blueprint-ai-skill v3.21). D10-01/02/04 reworded from "ROI slider" to the
  Avg-Customer-Value fill-in: D10-01 checks the typed value="" default on
  <input type="number" id="sl-contract"> against the industry band; D10-02
  (min-max range overlap) is now flagged legacy-slider-only / N/A for a fill-in
  (no max attr); D10-04 fingerprint covers fill-in (min+default) or legacy
  slider (min/max/default). Backed by financial-realism-check.py which was
  patched to actually match id=sl-contract (was a dead id=slider-contract regex
  that silently fail-open-skipped these contract-band red-lines) and to exempt
  the fill-in's intentional "|| 0" empty-sentinel from the D7-17 band check.
changelog_v2.9: >
  REPEATABILITY HARDENING (Bennett directive 2026-06-01). Format-3 is the only
  approved Blueprint surface. Added direct-address podcast gate: audio must open
  by speaking to the prospect by first name, must say the walkthrough was built
  for them and their business, must avoid "source material/document/brief"
  framing, must avoid third-person analysis of the prospect, and must include
  >=5 "you/your" references in the audited opening. Added restaurant/QSR drift
  gate for food franchise leads: no plumber/home-services/SaaS/onboarding copy
  can ship, and restaurant vocabulary must be present. Added local-first public
  audio rule: local audit may pass before first deploy when the MP3 is hash-bound
  and direct-address verified; production audit still requires public HTTP 200,
  public size window, hash match, and the same direct-address receipt.
changelog_v2.8: >
  HARD 100% GATE (Bennett directive 2026-06-01). Removed the ≥90/110 partial-pass
  threshold — the ONLY passing state is total_score == total_possible (100%) AND all
  red-lines green AND a hash-bound approval token minted by passing 100%. Added Email
  Design Conformance checks D5-16..D5-21 (all [RL], enforced by scripts/email-design-conformance.py):
  build-script provenance marker, Advaita palette, "See If You Qualify"→qualify.html CTA,
  zero-emoji, no unrendered tokens, single CTA. Reconciled D5-11 to qualify.html (was "apply quiz",
  which contradicted the CTA-ban rule and made 100% unreachable). Send path (build-delivery-email.sh)
  now calls scripts/audit-gate.sh which mints the token ONLY at 100% conformance, bound to the exact
  email bytes — editing after audit invalidates the token. Mechanically impossible to send below 100%.
council_verified_v13: 4.60 / 5.0 PASS (overdrive cycle 1, council v24)
council_verified: 4.66 / 5.0 PASS (council v24, 2026-05-21)
drive_file_id: 1Wp7zzDlp4uzeEX8vTIQv0_RsJp70ORLM
description: >
  Blocking pre-delivery audit gate for the Blueprint AI pipeline.
  Must PASS before Stage 7 (email delivery) executes.
  149 binary checks across 10 domains (22 red-line). Red-line checks = instant FAIL.
  Draws from all known failure patterns: Melissa Tash, Chris Phillips,
  unauthorized sends, color defaults, hallucinated data, broken podcast,
  missing demo site, wrong CTAs, cross-contamination, 90-day plans.
  No Blueprint ships without a PASS report on file.
triggers:
  - "run blueprint audit"
  - "audit this blueprint"
  - "pre-delivery check"
  - "check this blueprint"
  - "blueprint check"
  - "before delivery"
  - "stage 6 audit"
  - "blueprint gate"
  - "run audit gate"
  - called automatically by blueprint-ai-skill v2.3 Stage 6
owner: Mack (claude.ai) — strategy + audit. Ivan (iMac CLI) — file/curl checks.
---

# Blueprint AI Audit Skill v2.9 — 149-Point Blocking Gate (22 Red-Lines) + Pre-Flight Format-3 Conformance

## North Star
Every Blueprint that ships to a prospect has been machine-verified against
149 binary checks (canonical count as of v2.5). If any RED-LINE check fails,
delivery stops immediately. There are 22 red-line checks — failing even one halts
the pipeline regardless of overall score.
If score < 100% of applicable checks, auto-fix loops run (max 3), then flag to Bennett — a single missed point blocks the send. The ONLY passing state is 100% with every red-line green and a hash-bound approval token minted by that 100% pass (see Scoring — Hard 100% Gate).
No exceptions. No partial credit. No ≥90 shortcut.

---

## How It Works

1. Load this skill before Stage 7 of blueprint-ai-skill v2.3.
2. Run all checks against the deliverable package (Blueprint HTML, demo site, podcast, email draft).
3. Generate AUDIT_REPORT.json: domain scores + total + PASS/FAIL per check.
4. If RED_LINE_FAIL_COUNT > 0 → HALT. Post to #leo-coaches. Flag Bennett.
5. If total_score < total_possible → auto-fix loop (max 3 rounds). Re-run audit after each fix.
6. PASS requires ALL THREE: total_score == total_possible (100%), red_line_pass == true, AND approval_token present (see Hard 100% Gate). Anything less → FAIL.
7. Save AUDIT_REPORT.json to Drive + log row in Notion Lead Tracker.

---

## Scoring — HARD 100% GATE (Bennett directive 2026-06-01)

| Threshold | Result |
|-----------|--------|
| Any RED-LINE check fails | Instant FAIL — do not proceed |
| total_score < total_possible (i.e. < 100%) | FAIL — auto-fix + re-audit (max 3x) |
| total_score == total_possible AND all red-lines pass AND approval_token present | PASS — proceed to Stage 7 |

**There is no longer a ≥90 partial pass. The ONLY passing state is 100% of total_possible with every red-line green AND a valid approval token.** A single missed check (1 point) = FAIL = send blocked. This is a hard gate, not a quality target. The old ≥90/110 threshold REWARDED shipping ~18% defective; it is removed permanently.

Red-line checks are marked [RL] below. Failing even one = FAIL regardless of score on every other check.

### Hard 100% Gate — mechanical enforcement
The send path (`scripts/build-delivery-email.sh`) calls `scripts/audit-gate.sh <slug> <email_html>` before ANY send. That script:
1. Runs every deterministic enforcer (email-design-conformance.py, plus format/financial/d9 when a blueprint HTML is present) — ALL must exit 0.
2. Computes `sha256(email_html)`.
3. ONLY if every enforcer exits 0 does it MINT the approval token at `~/.openclaw/state/blueprint-approvals/<slug>.approved` containing `approved_html_sha256 = sha256(email_html)` + `score=100`.
4. The send step re-reads the token and re-hashes the exact HTML it is about to send; mismatch (any byte changed after minting) OR missing token = ABORT.
5. Net effect: the token can ONLY come into existence at 100% conformance, and it only authorizes the exact bytes that were audited. "this is all approved" == "the audit minted a hash-bound 100% token for these exact bytes." Edit the email after audit → hash changes → token invalid → send blocked. There is no path to send below 100%.

---

## PRE-FLIGHT GATE 0 — Artifact Integrity (BLOCKING, runs before all domains) — added 2026-05-26

Runs FIRST. Any failure = instant FAIL, audit does not proceed. Root cause: pipeline reported PASS/"done" on empty shells, divergent duplicates, and Notion-link-only deliveries (Bennett 4 angry replies 2026-05-26).

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| PF0-1 | The lead's Blueprint HTML file EXISTS and is ≥ 40 KB | `[ $(wc -c < <slug>.html) -ge 40000 ]` — Notion-link-only or missing file = FAIL | [RL] |
| PF0-2 | EXACTLY ONE HTML file exists for this lead slug — no divergent versions | `ls blueprints/ \| grep -i <lead-key>` returns 1 file. >1 (e.g. rey.html + rey-31consulting.html + rey-31-consulting.html) = FAIL until consolidated | [RL] |
| PF0-3 | The delivered URL/email body links to the HTML Blueprint, NOT just a Notion page | grep delivery body for `.html`; if only `notion.so` present = FAIL | [RL] |
| PF0-4 | Zero unresolved template tokens (mirror of D1-19, run early). **STRIP `<pre>` blocks first** — AI agent prompt templates inside `<pre>` tags use bracket placeholders (`[INPUTS NEEDED]`, `[FOLLOW-UP NEEDED]`) as intentional instructions for the lead; these are NOT unfilled tokens. Pattern: strip `<pre>.*?</pre>` (DOTALL), THEN run `grep -oE '[A-Z_]*PLACEHOLDER[A-Z_]*|\{\{[A-Za-z_]+\}\}|\[[A-Z_]{3,}\]'` on remaining HTML; count must == 0. VERIFIED 2026-05-26: FAILs raw-template shells (chris/melissa/zak = 85 tokens), PASSes real blueprints (court/dave/branson = 0). Patched 2026-05-26 (16-round batch): pre-block exclusion prevents false positives on alex-ramos + jaden-mecham prompt templates. | pre-stripped token grep == 0 | [RL] |
| PF0-5 | **Format-3 structural conformance** (added 2026-06-01 — the reproducibility guarantee Bennett asked for: "every time I ask for the blueprint AI audit/task/skill I get this exact same output, but with another company's information"). The deliverable must match the format-3 gold signature — 16 named sections in exact order, custom chaptered podcast player (21 signature IDs each present exactly once, single `id="listen"`), component DNA at gold density, `--brand` Advaita-blue accent. Mechanically the generator clones `blueprints/TEMPLATE.html` (which IS tokenized format-3, pre-commit FORMAT-3 LOCKed), so any conformant clone passes and any drift HALTs. Method: `python3 scripts/format-conformance-check.py <slug>.html` — exit 0 required. PROVEN 2026-06-01 to PASS format-3 and HALT the old 21-section template (3 red-line fails) + the 3 drift classes (missing player-id, scrambled section order, duplicate listen-section/the original button bug). | conformance exit 0 | [RL] |

**Why a pre-flight gate, not just domain checks:** domain checks scored CONTENT inside one assumed-good file. They never asserted the file existed, was unique, was actually what got sent, **or reproduced the format-3 gold structure**. The false-PASS lived in that gap.

### Format-3 Only Rule (2026-06-01)

The only approved Blueprint structure is the dense-scroll Format-3 surface:
`hero`, `profile`, `results`, `pillars`, `stack`, `gaps`, `oppmap`, `ignore`,
`agents`, `timeline`, `calculator`, `prompts`, `demo`, `listen`, `sources`,
`apply`.

The old centered-tab design, the "Command Center" tab, `tab-nav`, `tab-panel`,
`switchTab`, Playfair styling, and any alternate format reference are revoked.
Tabs/nav belong at the top right of the sticky header. The primary CTA copy is
"See If You Qualify" or a direct approved qualify variation. Visible "Apply",
"Apply to work with Bennett", and "Apply to Work With Us" are banned.

### Direct-Address Podcast Gate (2026-06-01)

Every podcast must be addressed to the prospect by name, not framed as an
analysis of source material. The opening must be equivalent to:

`Hi <First>, welcome. This walkthrough was built for you and <Business>, from what you told us.`

The production receipt for check #47 must prove:
- `direct_address_audio_verified=true`
- `opening_direct_address_verified=true`
- `opening_exact_or_close=true`
- no "source material", "source document", "this document", "this brief",
  "the materials", "we are analyzing", or similar narrator-risk framing
- no third-person patterns such as "the company", "the owner", "they have",
  or `<Business> has/is/needs/wants`
- `you_your_count >= 5`
- `audio_sha256` matches the current MP3

Local audit can pass before first deploy when the local MP3 is hash-bound and
direct-address verified. Production audit still requires public HTTP 200, public
download size in the 6-20 MB window, direct-address receipt, and hash match.

### Industry Drift Gate (2026-06-01)

Food franchise, restaurant, QSR, fast-casual, catering, and food-chain leads must
pass the restaurant/QSR drift gate. Plumber, home-services, SaaS, onboarding,
support-ticket, login, demo-request, proposal-specialist, and product-launch copy
is a red-line failure for those leads. Restaurant vocabulary such as order,
catering, guest, loyalty, rewards, location, pickup, delivery, crew, store, and
restaurant must be present in the client-facing body.

Home-services leads must pass the home-services drift gate. Restaurant, SaaS,
photography, design-agency, onboarding, support-ticket, login, demo-request,
proposal-specialist, product-launch, and unrelated franchise copy is a red-line
failure for those leads.

**SaaS-vendor exclusion (2026-06-02 — gate-misclassification fix).** The
home-services content gate (`run-audit.py` `home_services_content_gate`) keyed
on the substring "home service" inside the lead's industry/market blob. A
software vendor that merely SELLS TO home-services operators — e.g. CRMX, whose
industry is "SaaS CRM for home service businesses" — contains that substring but
is NOT a home-services operator, so its (correct) SaaS copy ("churn risk",
"recurring revenue locked in", "plan tier", "675+ accounts") was wrongly gated
(brent-attaway D10-22 false positive). FIX: the gate now excludes any blob
containing `saas / software / crm / platform / b2b / tech company` BEFORE the
home-services term match. Verified both directions — CRMX/claude-code/B2B
consulting pass; a real plumber using the same SaaS churn copy still gates.
Permanent lesson: when a content red-line fires on a B2B/SaaS lead, check
whether the gate is keying on a substring of the lead's *target market*
("for X businesses") rather than the lead's *own* business type — fix the gate's
classifier, never rewrite correct copy.

## Domain 1 — Identity & Personalization (20 checks)

These verify the Blueprint is actually built for this lead, not cloned from another.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D1-01 | Lead's full name appears in Blueprint HTML title tag | grep `<title>` for lead name | |
| D1-02 | Lead's first name used in hero headline | grep hero section | |
| D1-03 | Lead's business name appears ≥ 5 times in HTML | grep -c "business_name" | |
| D1-04 | No other lead's name appears anywhere in HTML | grep for all known prior lead names | [RL] |
| D1-05 | Business type matches lead's intake form (e.g. "franchise", "school photography") | string match | |
| D1-06 | Revenue band matches intake (e.g. "$3M–$10M") | string match | |
| D1-07 | CRM listed matches lead's actual CRM (e.g. "GoHighLevel") | string match | |
| D1-08 | Tool stack section lists lead's real tools only — no placeholder "Trello" or "Asana" if lead doesn't use them | manual review or grep vs lead-profile.json | |
| D1-09 | AI agents are named and described for lead's specific industry | review 6 agent cards | |
| D1-10 | Agent descriptions do NOT contain generic phrases like "your business" without lead name | grep for unresolved `{lead}` or `[NAME]` tokens | [RL] |
| D1-11 | Pain points listed match lead's intake answers | compare vs lead-profile.json | |
| D1-12 | Industry-specific statistics cited (not generic "small business") | review stats section | |
| D1-13 | ROI calculator default values match lead's business numbers from intake | check JS default values | |
| D1-14 | Opportunity gaps section lists ≥ 3 gaps specific to lead's industry | review gaps section | |
| D1-15 | Website audit section scores are for lead's domain, not a placeholder | verify domain in audit section matches lead-profile.json domain | |
| D1-16 | Proposal/pitch language references lead's specific customer type (e.g. "school districts" not "clients") | grep | |
| D1-17 | Meta description tag contains lead's name and business | grep `<meta name="description"` | |
| D1-18 | OG title and OG description contain lead's name | grep og:title, og:description | |
| D1-19 | No unresolved template tokens in client-facing HTML. VERIFIED pattern (zero false positives — does NOT match legit lowercase `placeholder=` attrs): `grep -oE '[A-Z_]*PLACEHOLDER[A-Z_]*\|\{\{[A-Za-z_]+\}\}\|\[[A-Z_]{3,}\]' file.html \| wc -l` must == 0. Catches `_URL_PLACEHOLDER`, `{{LEAD_NAME}}`, `{{BIZ_NAME}}`, `[NAME]`. (Root cause 2026-05-26: old check matched only `[PLACEHOLDER]` bracketed → raw template shells chris/melissa/zak shipped with 85 unfilled `{{TOKEN}}` each.) | uppercase-token grep, count == 0 | [RL] |
| D1-20 | Filename/slug matches lead (e.g. melissa-tash-srp.html, not brittney-warnick.html) | check filename | |

---

## Domain 2 — Content Rules (25 checks)

These verify all 10 Permanent Rules plus Bennett directives are enforced.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D2-01 | Zero emojis in any client-facing section of Blueprint HTML | grep Unicode emoji ranges U+1F300–U+1FAFF | [RL] |
| D2-02 | Zero emojis in email draft | grep email HTML | [RL] |
| D2-03 | No booking/calendar URLs (Calendly, cal.com, leadconnectorhq widget/booking) | Pattern: `grep -oE 'calendly\.com\|(?<![a-z])cal\.com\|leadconnectorhq\.com/(widgets/booking\|calendar)' file.html` — use negative lookbehind so `brightlocal.com`, `toplocal.com`, `rocalhost` do NOT match. Confirmed false-positive fix 2026-05-26: `brightlocal.com` contains `cal.com` as substring. Only match `cal.com` at word boundary or after `://`. | [RL] |
| D2-04 | No "discovery call" language | grep "discovery call" | |
| D2-05 | No 90-day plan language | grep "90.day\|phase 2\|phase 3\|12.week\|quarter 2" | |
| D2-06 | Onboarding timeline = 3/7/30 days (not 90) | grep "day.*1-3\|day.*4-7\|day.*30" ≥ 3 | |
| D2-07 | No hardcoded ROI dollar amounts (e.g. "you'll make $50,000") | grep "\$[0-9,]+.*per month\|\$[0-9,]+.*revenue" in prediction context | [RL] |
| D2-08 | ROI calculator exists and is interactive (JS sliders/inputs present) | grep `<input\|<range\|calculator` in HTML | |
| D2-09 | Apply CTA appears ≥ 3 times | grep -ci "apply" | |
| D2-10 | All CTAs link to apply URL or qualifying quiz — NOT calendar/booking | grep all href values | |
| D2-11 | All statistics have cited sources with clickable links | review every stat claim | |
| D2-12 | No fabricated testimonials (no fake quotes attributed to real people) | grep testimonial section | |
| D2-13 | No fabricated years ("FKI has been serving clients since 2018" when false) | manual review | |
| D2-14 | No fabricated locations or offices | manual review | |
| D2-15 | No fabricated specialties or certifications | manual review | |
| D2-16 | No fabricated GHL data (if GHL pull failed, fields show [PENDING_FORM_DATA]) | verify against lead-profile.json | |
| D2-17 | Advaita brand colors used on Advaita/FKI UI elements (#1E1E3F / #00D4AA / #FAFAFA) | grep :root CSS variables | |
| D2-18 | Client brand colors used on client-facing sections (extracted from CSS, not defaults) | verify client_palette.json exists and values appear in HTML | |
| D2-19 | No black/white/gray default palette used silently (EXTRACTION_FAILED = instant fail) | check client_palette.json for EXTRACTION_FAILED flag | [RL] |
| D2-20 | Color palette documented in HTML :root block as commented hex values | grep :root | |
| D2-21 | No "excited to work with you" or generic filler opener phrases | grep "excited to\|looking forward to connecting\|hope this finds you" | |
| D2-22 | All active voice — no passive constructions in hero or agent descriptions | spot check | |
| D2-23 | BIL three-pillar check — each agent card maps to at least one of [$in] [$out] [T] | review agent cards | |
| D2-24 | No pricing tables, price ranges, or investment tiers in Blueprint HTML | grep "\$[0-9].*package\|investment.*tier\|pricing.*table" | [RL] |
| D2-25 | CTA uses "See If You Qualify" or approved variation — HARD REJECT if "Apply to Work with Bennett" or "Apply to work with Bennett" appears ANYWHERE in HTML. Banned phrase — Bennett directive permanent 2026-05-27. Check: `grep -i "apply to work with bennett" file.html` must return 0. Then: `grep -i "See If You Qualify\|qualify" file.html` must return >= 1. | [RL] |

---

## Domain 3 — Podcast / Audio (15 checks)

Melissa Tash failure domain. Every check here came from a real incident.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D3-01 | Podcast file exists and is HTTP 200 | curl -sI podcast_url | [RL] |
| D3-02 | Podcast URL slug matches lead (e.g. /melissa-tash-srp.mp3, not advaita-ep01.wav) | string match | [RL] |
| D3-03 | Podcast is NOT advaita-ep01.wav or advaita-ep02.wav (generic episodes banned) | grep "advaita-ep01\|advaita-ep02" | [RL] |
| D3-04 | Podcast was generated via notebooklm-py pipeline (generation receipt exists in Drive) | check Drive for podcast-receipt-{lead-slug}.json | |
| D3-05 | Podcast source doc followed 7-segment framework (check source doc word count ≥ 18KB) | check source doc file size | |
| D3-06 | Podcast audio player is embedded and functional (not broken iframe) | load page, check player renders | |
| D3-07 | Podcast Drive fallback link is also present and HTTP 200 | curl fallback URL | |
| D3-08 | Podcast title shown in player matches lead name | check player UI text | |
| D3-09 | If podcast generation failed, page shows "GENERATING" placeholder — NOT silence or broken player | check for broken audio element | |
| D3-10 | Podcast duration > 5 minutes (under 5 = likely truncated/failed generation) | check audio metadata | |
| D3-11 | Podcast source doc references lead's specific pain points (not generic) | review source doc text | |
| D3-12 | Podcast CTA in audio references apply URL, not calendar | review source doc segment 7 | |
| D3-13 | No competitor's podcast embedded (cross-contamination check) | grep audio src for other lead slugs | |
| D3-14 | Download link for podcast present and functional | curl download href | |
| D3-15 | Podcast generation timestamp logged in Notion Lead Tracker | check Notion row | |
| D3-16 | Podcast is featured at the forefront — a prominent callout/banner linking to #listen appears within the first 4 sections (immediately visible on page load, before any agent/ROI content). Check: podcast callout div exists before 5th `<section` tag in document order. | `awk '/class.*pod-hero-callout|href="#listen"/{found=1} /<section/{sec++; if(found && sec<=4) pass=1} END{exit !pass}' file.html` or grep for podcast-forefront div in first 3000 chars | [RL] |
| D3-17 | All podcast-related href links are absolute URLs (no `qualify.html` or relative paths). `grep 'href="[^h][^t]' file.html` in podcast/CTA sections returns 0. | grep for relative hrefs | |

---

## Domain 4 — Interactive Demo: Command Center + Podcast (10 checks)

**RECONCILED 2026-05-26 (Bennett directive).** The standalone demo website was REMOVED from the
Blueprint spec and replaced by the in-page interactive **Command Center** section plus the
personalized **podcast**. The 10 website-specific checks (old D4-04, D4-06, D4-07, D4-10, D4-11,
D4-12, D4-16, D4-17, D4-18, D4-19) are **RETIRED — N/A** (they tested a separate site that no longer
ships). The 3 red-lines re-map to Command Center presence + interactivity + the live podcast asset,
all of which ARE part of the current Blueprint spec. Domain 4 applicable checks: 20 → 10.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D4-01 | In-page Command Center interactive demo section exists in Blueprint HTML | grep -i "command center\|command-center" ≥ 1 | [RL] |
| D4-02 | Command Center is interactive (tabs / buttons / JS toggles — not a static image) | grep `onclick\|data-tab\|<button\|addEventListener` | [RL] |
| D4-03 | Personalized podcast (the live demo asset) is HTTP 200 | curl -sI podcast_url | [RL] |
| D4-05 | Page uses lead's extracted brand colors (not black/white/gray defaults) | grep :root CSS variables | |
| D4-08 | Command Center / hero CTA = Apply — NOT calendar/booking | grep CTA href routes to apply/qualify | |
| D4-09 | No fake testimonials anywhere in Blueprint | review testimonial section | |
| D4-13 | Before/after comparison OR "audit scores" / snapshot section present | grep audit scores / snapshot / comparison | |
| D4-14 | A "View / Listen" button links to Command Center anchor or podcast (in-page) | verify href = `#command-center`/`#listen` or podcast url | |
| D4-15 | Blueprint is NOT a clone of a prior lead (no other lead business names) | grep HTML for prior lead names | |
| D4-20 | No pricing tables or ROI dollar predictions | grep pricing / `$X guaranteed` | |

*RETIRED (N/A — standalone site removed 2026-05-26): old D4-04, D4-06, D4-07, D4-10, D4-11, D4-12, D4-16, D4-17, D4-18, D4-19.*

---

## Domain 5 — Delivery & Pipeline Integrity (15 checks)

Prevents unauthorized sends and pipeline shortcuts.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D5-01 | Bennett preview email has NOT been sent yet (delivery paused here) | check Gmail sent for prior preview to same lead | |
| D5-02 | No prior unresolved Bennett preview sitting in inbox (must pull back first) | check Gmail inbox | [RL] |
| D5-03 | All Stage 1-6 tasks completed (Notion row has all stage receipts) | check Notion row fields | |
| D5-04 | Blueprint HTML pushed to GitHub Pages and HTTP 200 | curl blueprint_url | |
| D5-05 | Blueprint HTML file size > 50KB | wc -c | |
| D5-06 | Apply quiz URL (fki-preview/apply/) is HTTP 200 | curl quiz_url | |
| D5-07 | Apply quiz GHL webhook is wired (no REPLACE_WITH_WEBHOOK_ID tokens) | grep quiz HTML | |
| D5-08 | Email draft CC = bennett@franchiseki.com | check email draft headers | |
| D5-09 | Email draft BCC = brent@franchiseki.com, madison@franchiseki.com | check email draft headers | |
| D5-10 | Email draft TO = lead's email from GHL (not a placeholder) | check email draft TO field | |
| D5-11 | Email CTA links to qualify.html, not a calendar/booking URL (bennett-rule CTA-ban: qualify.html ONLY) | grep email HTML | |
| D5-12 | No external send executed by AI without human approval (HUMAN-APPROVAL-SEND tier) | verify email is in draft/staged state only | [RL] |
| D5-13 | Notion Lead Tracker row created for this lead | check Notion DB | |
| D5-14 | All Blueprint URLs in email are HTTP 200 | curl each href in email | |
| D5-15 | Self-audit score ≥ 4.0/5 documented (if council ran during build) | check council artifact | |

### Email Design Conformance (added 2026-06-01 — Bennett directive, all [RL], enforced by `scripts/email-design-conformance.py`)

The email must match the approved Advaita delivery design. A hand-rolled / drifted / raw-`gog`-sent email FAILS these and therefore cannot mint the 100% token. Run `python3 scripts/email-design-conformance.py <email_html>` → exit 0 required.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D5-16 | Built by `build-delivery-email.sh` (carries `<!-- BLUEPRINT-DELIVERY-EMAIL v2 -->` provenance marker) — NOT hand-rolled | grep marker | [RL] |
| D5-17 | Advaita palette: `-apple-system` font + `#1D1D1F` text required; bg may be legacy `#F5F5F7` OR the Madison-blessed white `#FFFFFF` send template; accent may be `#0071E3` OR an injected `bgcolor="#…"` CTA. (Reconciled 2026-06-02 — the gate was false-failing the real white-bg template that is actually SENT.) | grep tokens | [RL] |
| D5-18 | CTA text is exactly "See If You Qualify" and href ends `/qualify.html` (banned: "Get Your AI Quote", "APPLY TO WORK", apply_url) | grep CTA + href | [RL] |
| D5-19 | Zero emoji in the email body (Advaita design is emoji-free) | unicode-emoji scan | [RL] |
| D5-20 | No unrendered `{{TOKEN}}` placeholders remain | grep `{{` | [RL] |
| D5-21 | Exactly one CTA anchor (no competing booking/calendar/apply links) | count anchors to action URLs | [RL] |
| D5-22 | No flexbox (`display:flex`) — Outlook's Word engine silently strips it and collapses the card; tables only. `display:inline-block` on the CTA `<a>` is fine. | grep `display:flex` | [RL] |
| D5-23 | No `<style>` block — Gmail/Outlook honor `<style>` inconsistently; email-safe styling is inline only. A `<style>` tag means the email was hand-rolled off-template. | grep `<style` | [RL] |

**Send path is the TEMPLATE, never the output files (2026-06-02).** The real
send path is `templates/delivery-email-template.html` (Madison-blessed, white
`#ffffff` bg, `{{ACCENT_COLOR}}` injected, flex=0, no `<style>` — already
Outlook-safe). `delivery-emails/*.html` are disposable OUTPUT artifacts —
fix at the template/generator layer, never by hand-editing outputs (they get
regenerated). The conformance check in `build-delivery-email.sh` is **HARD
(exit 1) on the fresh-template path, WARN on idempotent reuse**: the canonical
template passes all 8 so legit fresh builds never block, while reuse stays WARN
so already-approved re-sends aren't blocked.

**Generator `&`-escaping (2026-06-02 — caught by the HARD gate).** In a `sed`
replacement RHS the bare `&` is the whole-match operator, so a free-text token
value containing `&` (e.g. rush-evans industry "Photography & Video") expanded
`&` back into its own `{{INDUSTRY}}` token and left it UNRENDERED (D5-20 fail).
FIX: `build-delivery-email.sh` defines `sed_esc(){ printf '%s' "$1" | sed 's/&/\\&/g'; }`
and applies it to EVERY free-text token replacement (not just QUALIFY_URL).
Pinned by regression check `DELIVERY_EMAIL_ESCAPES_AMPERSAND_TOKENS` in
`tests/test_blueprint_regressions.py`.

---

## Domain 6 — Research Integrity (15 checks)

Hallucination prevention. Every fact must be traceable to a source.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D6-01 | Every statistic has a cited source with clickable link | review all stat claims | [RL] |
| D6-02 | No citation points to a 404 page | curl each citation URL | |
| D6-03 | No citation to "FKI internal data" or "Advaita research" unless real document exists | grep citation text | |
| D6-04 | HubSpot, McKinsey, HBR citations link to real pages (not fabricated URLs) | curl each | |
| D6-05 | Lead's website audit scores are real (generated by website-audit-skill, not invented) | check audit receipt in Drive | |
| D6-06 | Competitor analysis data is from web research (search receipts in Drive) | check research log | |
| D6-07 | Lead's pain points sourced from GHL intake form or explicit conversation (not assumed) | compare vs lead-profile.json | |
| D6-08 | Lead's revenue band sourced from intake (not assumed from business type) | compare vs lead-profile.json | |
| D6-09 | Agent capability claims are real (no "AI can do X" without implementation path) | manual review | |
| D6-10 | ROI benchmarks (close rate lift %, admin time reduction %) sourced to published research | verify all % claims | |
| D6-11 | No fabricated quotes from Bennett | grep for unattributed Bennett quotes | |
| D6-12 | No fabricated case studies (e.g. "a client like you saw X result") | grep case study section | |
| D6-13 | Tool stack for lead sourced from intake or website scrape — not assumed | compare vs lead-profile.json | |
| D6-14 | Web audit scores (brand consistency, SEO etc.) match what website-audit-skill returned | compare scores vs audit receipt | |
| D6-15 | All images/logos in Blueprint are real URLs that resolve — no placeholder image.png | curl all img src attributes | |

---

## Auto-Fix Protocol

On any FAIL (non-red-line):

1. Identify the check ID and domain.
2. Attempt programmatic fix (e.g. replace broken URL, re-run color extraction, update CTA link).
3. Re-run the failed check only.
4. If PASS: continue audit.
5. If FAIL after 3 attempts: log as UNRESOLVED, flag to Bennett in #leo-coaches.

On any RED-LINE FAIL:

1. HALT immediately.
2. Post to #leo-coaches: "BLUEPRINT AUDIT FAIL [RL] — Check {ID}: {description}. Blueprint for {lead} BLOCKED."
3. Tag `<@U0AG6G4BEM9>`.
4. Do NOT proceed to Stage 7 under any circumstance.
5. Bennett decision required.

---


### Council Fix-Loop Prompt Template (v1.3 — use verbatim for each failed check)

```
"Blueprint audit check {check_id} FAILED for lead {lead_slug}.

Check description: {check_description}
What was found: {actual_value}
What was expected: {expected_value}
File/location: {check_location}

You are advising on a single specific fix. Rules:
- Fix must be executable by Mack (Drive/Notion/GitHub) or Ivan (CLI/bash)
- Fix must be reversible (no permanent deletes, no external sends)
- Fix must complete in under 3 minutes
- Do NOT suggest 'rebuild from scratch' or 're-run the whole pipeline'
- Do NOT suggest anything requiring Bennett input

Output ONLY this JSON:
{
  'fix_action': 'exact command or instruction',
  'executor': 'mack|ivan',
  'confidence': 0.0-1.0,
  'reversible': true|false,
  'estimated_seconds': N
}

If no fix is possible without Bennett: output confidence: 0.0 and fix_action: 'NEEDS_HUMAN: {reason}'"
```

Execute fix if confidence >= 0.7 AND reversible = true.
Log to ~/.openclaw/state/blueprint-audit-loops.jsonl regardless of outcome.
**STATE RULE:** ~/.openclaw/logs/ is local-only and invisible to fleet agents on handoff.
Use ~/.openclaw/state/ (which IS synced) as the canonical fix-loop log path.
If Drive upload receipt is needed for cross-agent visibility: `gog drive upload blueprint-audit-loops.jsonl`.

---

## AUDIT_REPORT.json Schema

```json
{
  "lead_name": "Melissa Tash",
  "lead_slug": "melissa-tash-srp",
  "audit_timestamp": "2026-05-21T22:00:00Z",
  "skill_version": "1.0",
  "domain_scores": {
    "D1_identity": { "passed": 19, "total": 20, "score": 0.95 },
    "D2_content": { "passed": 24, "total": 25, "score": 0.96 },
    "D3_podcast": { "passed": 15, "total": 17, "score": 0.88 },
    "D4_command_center_podcast": { "passed": 10, "total": 10, "score": 1.0 },
    "D5_delivery": { "passed": 15, "total": 15, "score": 1.0 },
    "D6_research": { "passed": 15, "total": 15, "score": 1.0 },
    "D7_post_delivery": { "passed": 1, "total": 1, "score": 1.0 },
    "D8_landing_page": { "passed": 8, "total": 8, "score": 1.0 },
    "D9_formatting_render": { "passed": 20, "total": 20, "score": 1.0 },
    "D10_financial_numeric": { "passed": 20, "total": 20, "score": 1.0 }
  },
  "total_score": 147,
  "total_possible": 151,
  "red_line_checks": {
    "total": 22,
    "passed": 12,
    "failed": 0,
    "failed_ids": []
  },
  "non_red_line_failed": ["D1-09", "D2-21"],
  "auto_fix_attempted": ["D1-09", "D2-21"],
  "auto_fix_resolved": ["D1-09"],
  "unresolved_flags": ["D2-21"],
  "verdict": "PASS",
  "proceed_to_stage_7": true,
  "drive_receipt_id": "",
  "notion_row_updated": true,
  "audit_history_fields": {
    "notion_artifact_registry_db": "328a4ee00ca84c9b8e8134067fa04609",
    "fields_to_add": {
      "Audit Score": "number — score out of 111",
      "Audit Version": "text — e.g. v1.3",
      "Audit Timestamp": "date",
      "Audit Checks Failed": "text — comma-separated failed check IDs",
      "Fix Loops Run": "number — 0, 1, 2, or 3",
      "Audit Status": "select — PASS | FAIL | BLOCKED"
    },
    "note": "Each re-audit appends a new row for diff history"
  },
}
```

---

## Known Failure Patterns (Reference Library)

Every check above traces to at least one of these real incidents.

| Incident | Checks It Spawned |
|----------|------------------|
| Melissa Tash — podcast broken (mp3 dead) | D3-01, D3-06, D3-09 |
| Melissa Tash — audio uses generic advaita-ep01 | D3-02, D3-03 |
| Melissa Tash — no demo website section | D4-01, D4-02, D4-13, D4-14 |
| Melissa Tash — notebooklm not in pipeline | D3-04, D3-05 |
| Chris Phillips — unauthorized send without Bennett approval | D5-12, D5-01 |
| Chris Phillips — prior unresolved preview in inbox | D5-02 |
| Color extraction silent failure — black/white default shipped | D2-19, D4-05 |
| Unresolved tokens shipped ({variable}, [NAME]) | D1-10, D1-19 |
| Cross-contamination — wrong lead's name in HTML | D1-04, D4-15, D3-13 |
| 90-day plan shipped instead of 30-day | D2-05, D2-06 |
| Booking/calendar URL in CTA | D2-03, D4-08, D5-11, D2-25 |
| Hardcoded ROI predictions ($X revenue guaranteed) | D2-07, D4-20 |
| Fabricated testimonials | D2-12, D4-09 |
| Fabricated statistics without sources | D6-01, D2-11 |
| Generic agent descriptions not customized to lead | D1-09, D1-10 |
| Wrong tool stack (Trello listed, lead uses Asana) | D1-08, D6-13 |
| Emojis shipped in client-facing HTML | D2-01, D2-02 |
| Pricing tables in Blueprint | D2-24, D4-20 |
| Broken demo site URL | D4-03, D4-02 |
| Apply quiz GHL webhook unwired | D5-07 |
| Fabricated HubSpot citation (404 URL) | D6-02, D6-04 |
| Lead email set to placeholder not real address | D5-10 |
| Demo site is clone of prior lead | D4-15 |
| Bennett BCC/CC missing from delivery email | D5-08, D5-09 |

---

## Cron Bindings

None — this skill runs on-demand as a blocking gate, not on a schedule.
Triggered by blueprint-ai-skill v2.3 Stage 6 automatically.

---

## Self-Audit Checklist (for Angie weekly audit)

1. Does every check have a programmatic method (grep/curl/compare) — not "manual feels right"?
2. Are all 22 red-line checks still present and marked [RL]? (North Star + domain sub-sections must agree on count.)
3. Is the AUDIT_REPORT.json schema complete and saving to Drive on every run?
4. Is this skill referenced in blueprint-ai-skill v2.3 Stage 6 by Drive ID?
5. Have any new Blueprint failures occurred since last audit? If yes, new checks added?
6. Is the Known Failure Patterns table current with all real incidents?
7. Is the auto-fix protocol producing fix attempts (not just flagging)?
8. Are Notion Lead Tracker rows being updated on every audit run?
9. Does the AUDIT_REPORT.json schema `total_possible` match the grand total check count at the bottom of the skill? (Version drift causes schema to stale — verify numerically.)
10. Is `financial-realism-check.py` present at `fki-preview/financial-realism-check.py`? If missing, Domain 10 red-lines cannot run — log BLOCKED status and post to #leo-coaches immediately rather than falsely PASSing.
11. Does the fix-loop log path point to `~/.openclaw/state/blueprint-audit-loops.jsonl`? (Not logs/ — local-only path breaks fleet handoff.)
12. Are all AUDIT_REPORT.json domain_scores keys current? (`D4_demo_website` is a retired name — correct key is `D4_command_center_podcast`.)
13. Are all trigger phrases in the skill header covering how agents actually invoke this? Review any recent "skill not found" audit failures.

---

## Domain 7 — Post-Delivery Verification (1 check)

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D7-13 | CEO results email sent to bennett@franchiseki.com after delivery (Stage 7.75 receipt exists) | check ~/.openclaw/logs/ceo-emails.jsonl for entry with lead_slug and timestamp < 1h ago | |

**Domain 7 total: 1 check. Updated overall total: 111 checks.**

---

## Domain 8 — Landing Page (8 checks, 4 red-line)

Gates the FKI AI qualifier landing page (fki-preview/index.html) per blueprint-ai-landing-page-skill v2 canonical recipe. Auto-fires when any landing page commit lands or on every Angie weekly sweep.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D8-1 | No gold palette — #F8B552 / #d4a857 / rgba(248,181,82,…) absent from fki-preview/*.html | `grep -E '#F8B552\|#d4a857\|rgba\(248,181,82' fki-preview/*.html` returns empty | 🔴 |
| D8-2 | FAQ accordion single-handler — NEVER inline `onclick=` AND `addEventListener` both bound to FAQ items | grep both patterns; only one allowed per FAQ block | 🔴 |
| D8-3 | No fabricated testimonials / fake reviews — proof section uses only Bennett-approved real wins | manual review against testimonials-allowlist.json (or absence of proof-section) | 🔴 |
| D8-4 | No "No email required" claim anywhere in funnel HTML | `grep -i 'no email required' fki-preview/*.html` returns empty | 🔴 |
| D8-5 | All CTAs route to qualify.html (zero calendar/booking URLs in index.html) | grep `href=` in CTA buttons; allow only `qualify.html`, anchors `#`, or `privacy.html`/`terms.html` in footer | |
| D8-6 | Sticky mobile CTA bar present — fixed-bottom, visible at viewport ≤860px | grep for `.sticky-cta` class + `@media (max-width: 860px)` block | |
| D8-7 | Mobile breakpoints present — both `max-width: 480px` AND `max-width: 360px` media queries in index.html | grep both queries | |
| D8-8 | privacy.html email = contact@franchiseki.com (NOT bennett@) | `grep 'contact@franchiseki.com' fki-preview/privacy.html` returns ≥1 AND `grep 'bennett@franchiseki.com' fki-preview/privacy.html` returns 0 | |

**Domain 8 total: 8 checks (4 red-line). Updated overall total: 109 checks (16 red-line).**

---

## Domain 10 — Financial & Numeric Credibility (20 checks, 5 red-line) — added 2026-05-29

> **NUMBERING NOTE (2026-05-29 collision fix):** This domain was briefly authored as a SECOND
> "Domain 9", colliding with the existing Domain 9 (Formatting & Render Integrity, v2.2.0). Both
> used `D9-XX` prefixes — an invalid duplicate. Permanently renumbered to **Domain 10 / `D10-XX`**.
> Formatting & Render Integrity keeps Domain 9. Always check existing domain numbers before adding one.

**Root cause (Bennett 2026-05-29):** Court Lundberg / Rare Breed Plumbing (a residential
home-services company) shipped with a `$45,000 "average contract value"` default and a
`$25K–$120K` ROI slider — generic franchise-consulting numbers **cloned onto every business
regardless of industry**. The prior audit "passed 100%" because the only financial checks were
D1-13 (manual review) and an orphaned D3-27 grep that was never wired. There was **no machine
gate** on whether the money math fit the lead's industry. Domain 10 closes that gap.

**Enforcement is real, not manual review:** these are gated by
`fki-preview/financial-realism-check.py` (INDUSTRY_BANDS + LEAD_INDUSTRY map). The audit runs
`python3 financial-realism-check.py --all`; exit 0 is required for the financial red-lines to pass.

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D10-01 | ROI contract/deal-value fill-in DEFAULT (the typed `value="…"` on `<input type="number" id="sl-contract">`) sits inside the lead's industry band (home_services $300–$20k, photography $250–$8k, medspa $150–$6k, food_franchise $8–$60, consulting $3k–$150k, medical_devices $5k–$500k, etc.) — a plumbing job is NOT a $45,000 contract | `financial-realism-check.py` D7-01 | [RL] |
| D10-02 | Contract field min–max RANGE overlaps the industry band — applies to a legacy bounded slider only; the fill-in has no `max` so this check is N/A for fill-in blueprints | `financial-realism-check.py` D7-03 | [RL] |
| D10-03 | JS fallback for the contract input is inside band — not a generic `\|\| 45000` and not `\|\| 0` (which renders a $0/NaN ROI) | `financial-realism-check.py` D7-17 | [RL] |
| D10-04 | ROI contract-field fingerprint (the numbers present — fill-in min+default, or legacy slider min/max/default) is NOT identical across ≥3 blueprints spanning ≥2 industries — cross-industry clone detection | `financial-realism-check.py` D7-02 | [RL] |
| D10-05 | Lead's industry IS classified (no `unknown` band shipping unverified financials) | `financial-realism-check.py` D7-11 / LEAD_INDUSTRY map | [RL] |
| D10-06 | Transaction NOUN matches the industry — "job/ticket" (plumbing), "session/package" (photography), "treatment" (medspa), "contract" (devices) — not a blanket "Average Contract Value" | D7-10 label check | |
| D10-07 | No hardcoded large $ figure (≥$10k) in client-facing copy unless it traces to intake / a cited source | D7-04 body grep (script/input stripped) | |
| D10-08 | EVERY $ figure in the blueprint traces to lead-profile.json / intake / a cited source — zero invented revenue numbers | compare all `$` matches vs lead-profile.json | |
| D10-09 | Revenue band displayed matches the intake revenue band (no silent upgrade/downgrade) | string match vs lead-profile.json | |
| D10-10 | ROI math is internally consistent: leads × close-rate × deal-value = the displayed projection (no contradiction between slider state and headline number) | evaluate calc JS against displayed default | |
| D10-11 | No guaranteed/fabricated ROI dollar prediction in copy ("you'll make $X/mo") — numeric scan, mirrors D2-07 | grep `$[0-9,]+ .*(per month\|/mo\|revenue)` in prediction context | |
| D10-12 | Percentage claims are plausible & sourced (close-rate lift, time saved ≤100%, no "300% close rate") | scan all `%` claims vs cited source | |
| D10-13 | Default lead-VOLUME slider value is plausible for the industry (a solo photographer is not "500 leads/mo") | check slider-leads default vs industry | |
| D10-14 | No pricing tables / investment tiers (numeric scan for "$X/mo package", "tier") — mirrors D2-24 | grep tiers/packages | |
| D10-15 | Currency + number formatting consistent — all USD, no mixed symbols, no malformed `$45,00` | regex format scan | |
| D10-16 | ROI calculator returns a sensible NON-zero output at default state (not $0, not NaN) — a $0 default makes the whole tool look broken | evaluate calc at load | |
| D10-17 | No OTHER lead's business numbers leak in (financial cross-contamination) | grep prior-lead default values | |
| D10-18 | Annualized vs per-deal figures are labeled correctly (a per-job number is never labeled "annual") | label vs magnitude check | |
| D10-19 | The INDUSTRY_BANDS table itself is sourced/reviewed (provenance note present) — bands are not themselves invented | check financial-realism-check.py header provenance | |
| D10-20 | `financial-realism-check.py --all` exits 0 for the full batch — the whole domain is machine-gated and BLOCKING before any send | run the script, assert exit 0 | [RL] |

**Domain 10 total: 20 checks (5 red-line: D10-01..D10-05 + D10-20 blocking). Enforcer: `fki-preview/financial-realism-check.py`.**

**ERROR RECOVERY — script missing:** If `financial-realism-check.py` is not found at `fki-preview/`, Domain 10 cannot be machine-gated. DO NOT assume PASS. Steps:
1. Check Drive for the latest version: search `financial-realism-check.py` in Drive Skills folder.
2. If found: download to `fki-preview/` and re-run.
3. If not found: set all D10 red-line checks to BLOCKED (not PASS). Post to #leo-coaches: "BLUEPRINT AUDIT — Domain 10 enforcer script MISSING. Blueprint for {lead} BLOCKED until script restored." Tag Leo. Do NOT proceed to Stage 7.

> **CURRENT STATE 2026-05-29 (verified):** Domain 10 = **15/15 blueprints pass** (`FINANCIAL-REALISM: 15/15`).
> The per-industry slider min/max/default + correct transaction noun were injected into the build
> template keyed off LEAD_INDUSTRY (consistency-template rebuild earlier today). Court Lundberg now
> defaults to $300 (home_services), not $45,000; all 15 leads sit inside their industry bands and the
> cross-industry clone check passes. This domain is GREEN and BLOCKING before any blueprint ships.

---

## Domain 9 — Formatting & Render Integrity (20 checks, 1 red-line) — NEW v2.2.0

**Built 2026-05-26 (Bennett directive).** dave-wood + brittney shipped at audit-100% but rendered
**unstyled** — the body used class names (`profile-grid`, `gap`, `agent`, `ignore`, `stack-item`)
that had **no matching CSS rule** in the `<style>` block, so whole sections rendered as flat text
instead of styled card grids. Every prior domain checked *content*, never *whether the markup is
actually styled*. Domain 9 closes that. The runner is `run-audit.py` (stdlib + curl).

| ID | Check | Method | Red Line |
|----|-------|--------|----------|
| D9-01 | Zero orphan CSS classes — every class used in the body has a CSS rule (or inline style) | parse `class=""` tokens vs `.rules` in `<style>`; inline-styled classes exempt | [RL] |
| D9-02 | No undefined CSS variables — every `var(--x)` is declared | compare used vs `:root`/declared vars | |
| D9-03 | Snapshot/profile section is a styled grid (grid/flex), not a bare stack | `.snapshot-grid`/`.profile-grid` rule contains `grid` or `flex` | |
| D9-04 | At least one `@media` query (responsive) | grep `@media` | |
| D9-05 | Mobile breakpoint ≤480px present | grep `max-width:4[0-8]\dpx` | |
| D9-06 | Viewport meta present | grep `viewport` | |
| D9-07 | No leftover template blue (#1D6FDB / #4A90E2 / rgba(29,111,219)) | grep | |
| D9-08 | Section count ≥ 8 (full template) | count `<section` | |
| D9-09 | Every `<section>` has an id (anchor nav works) | count ids vs sections | |
| D9-10 | No dead in-page anchors — every `href="#x"` resolves to an element id | set diff | |
| D9-11 | No empty headings `<hN></hN>` | regex | |
| D9-12 | No double-encoded entities (`&amp;mdash;`) | grep | |
| D9-13 | No broken possessive — `Biz'` with apostrophe not followed by `s` | regex on business name | |
| D9-14 | No literal `undefined` / `NaN` / `null` in body text | regex | |
| D9-15 | font-family defined AND applied to `body` | grep style block | |
| D9-16 | Hero has background/gradient (not bare) | `.hero` rule has `background`/`gradient` | |
| D9-17 | Primary CTA button is styled (`.cta-btn`/`.btn` defined) | class defined | |
| D9-18 | Tables styled (`border-collapse`) if any `<table>` present | grep | |
| D9-19 | Content width capped (`max-width` container) | grep | |
| D9-20 | No off-brand accent leak (lime #bbff01 / navy #000321 from old template) | grep | |

**Domain 9 total: 20 checks (1 red-line).**

**GRAND TOTAL (canonical, v2.5): 149 checks, 22 red-line.** = Domain 9 Formatting (20/1RL) + Domain 10 Financial (20/5RL) added on top of the prior 129/17RL baseline (129 already included Domain 9 Formatting; Domain 10's +20 checks and +5 red-line bring it to 149/22RL). This is the authoritative count — supersedes the scattered per-domain "updated overall total" lines above, which were snapshots at the time each domain was added and were never reconciled after Domain 10.

Auto-Fix Protocol for Domain 9: D9-01 RED LINE failure → either rename body classes to the
stylesheet's defined vocabulary (e.g. `profile-grid`→`snapshot-grid`) OR add the missing CSS rules.
Non-red-line → autopilot patches additively (add `@media`, fix possessive, add section id, swap
off-brand hex for the lead's extracted palette). Always re-screenshot after a Domain 9 fix —
a green D9 score must be backed by a visual proof capture.

Auto-Fix Protocol for Domain 8: any RED LINE failure → block ship + open Notion row referencing blueprint-ai-landing-page-skill v2 quality gates. Non-red-line failures → autopilot patches additively (never rebuilds).

---

## Related Skills

| Skill | Drive ID | Purpose |
|-------|----------|---------|
| blueprint-ai-skill v2.3 | 1qFMLDeI__RifRAcZ3PNaWwWJoYWcoFoj | Master orchestrator — calls this skill in Stage 6 |
| notebooklm-skill | 1ceOsmptwxso0P0MCPC9xJa3mvPRgf55q | Podcast generation |
| website-build-skill v3 | (load by name) | Demo website build |
| website-audit-skill v5 | (load by name) | Website audit scores |
| diamond-skill v2.1 | 1CVpWQLYHUlfnJroKtcpamM7SZSNdtvPT | Post-build QA (runs after this audit) |
| apply-scoring-skill v2.0 | 13VzcQnt0kS_YsbZSlFRFG9BZSzxtm6Nj | Apply quiz verification |

---

## Version History
- v2.7 (2026-06-01, Bennett reproducibility directive): **PRE-FLIGHT GATE 0 gains PF0-5 — Format-3 structural conformance [RL].** Root cause Bennett asked to close: *"how do you GUARANTEE that every time I ask for the blueprint AI audit/task/skill, I get this exact same output, but with another company's information?"* The audit now mechanically enforces it. PF0-5 runs `python3 scripts/format-conformance-check.py <slug>.html` (exit 0 required) so every deliverable must match the format-3 gold signature: 16 named sections in exact order, custom chaptered podcast player (21 signature IDs each exactly once, single `id="listen"`), component DNA at gold density, `--brand` Advaita-blue accent. The generator clones `blueprints/TEMPLATE.html` (now tokenized format-3, pre-commit FORMAT-3 LOCKed), so a conformant clone passes and any drift HALTs. PROVEN 2026-06-01 (diamond-skill 6/6 + gatekeeper ledger ACCEPTED 100/95): PASSes format-3, HALTs the old 21-section template (3 RL fails) and 3 drift classes (missing player-id, scrambled section order, duplicate listen-section — the original broken-button bug). PF0-5 is a pre-flight red-line, separate from the 149 domain checks; domain totals unchanged. Also bumped `html-content-check.sh` token check to skip TEMPLATE.html (scaffolds legitimately hold {{TOKENS}}).
- v2.6 (2026-05-30, permanent-self-improvement audit): Six genuine fixes applied. (1) **North Star stale counts corrected**: was "110 checks / 12 red-lines", now reflects canonical v2.5 totals of 149 checks / 22 red-lines — mismatched counts caused agent confusion about gate thresholds. (2) **Trigger phrase expansion**: added 5 missing phrases ("check this blueprint", "blueprint check", "before delivery", "stage 6 audit", "blueprint gate", "run audit gate") — sparse trigger set caused skill-not-found misses. (3) **Fix-loop log path corrected**: was `~/.openclaw/logs/blueprint-audit-loops.jsonl` (local-only, dies on handoff), now `~/.openclaw/state/blueprint-audit-loops.jsonl` per STATE RULE. (4) **AUDIT_REPORT.json schema updated**: domain_scores key renamed from stale `D4_demo_website` to `D4_command_center_podcast`; total_possible corrected from 110→151; all 10 domain keys added (were only 6). (5) **Domain 10 error-recovery added**: no fallback existed if `financial-realism-check.py` is missing — would silently false-PASS; now BLOCKED + #leo-coaches post + Drive search before giving up. (6) **Self-Audit Checklist expanded from 8→13 items**: added guards for red-line count consistency, schema numeric drift, enforcer script presence, fix-loop log path, stale domain key names, and trigger coverage.
- v2.5 (2026-05-29, autonomous-loop Round 1 fix): **Domain numbering collision fixed.** The Financial & Numeric Credibility domain was authored as a SECOND "Domain 9" with `D9-XX` IDs, colliding with the existing Domain 9 (Formatting & Render Integrity, v2.2.0) that also uses `D9-XX`. Renumbered Financial → **Domain 10 / `D10-01..D10-20`** (5 red-line). Formatting keeps Domain 9. Also corrected the stale "0/15 blueprints pass" state note to the verified **15/15 PASS** (per-industry slider injected into the build template; Court Lundberg $45k→$300 home_services). Permanent lesson: check existing domain numbers before adding one.
- v2.4 (2026-05-29, Phase 4 hardenings): Pre-commit hook (`fki-preview/.git/hooks/pre-commit`) repointed from the broken `blueprint_orchestrator.py --validate-only` call to the authoritative `run-audit.py` gate (requires `VERDICT=PASS` per staged blueprint; G16 + `.blueprint-ci-skip` bypass preserved). Podcast regex now matches `<audio src="...mp3">` as well as `href` (was false-failing embedded players). D10 delivery-email path now falls back to the git repo root when audited from a temp copy (non-fatal). New non-red-line check **D2-27** — qualify CTA must pass `firstName`+`agents` prefill params so qualify.html prefills and Q7 renders dynamically. Overall total 80→81.

- v2.2.0 (2026-05-26, Bennett directive): **Domain 9 — Formatting & Render Integrity** added (20 checks, 1 red-line). Root cause: dave-wood + brittney passed audit-100% but rendered UNSTYLED because the body referenced class names with no CSS rule (`profile-grid`, `gap`, `agent`…). New red-line D9-01 = zero orphan classes. Also catches: undefined CSS vars, missing mobile breakpoint, dead anchors, broken possessives, off-brand hex leak, leftover template blue. Runner = `run-audit.py`. Overall total 109→129 (17 red-line). Every Domain 9 fix requires a re-screenshot proof.
- v2.1.0 (2026-05-26, Bennett directive): Domain 4 RECONCILED to current Blueprint spec. Standalone demo website was removed from blueprints and replaced by the in-page interactive Command Center + personalized podcast. 10 website-specific checks retired (N/A); 3 red-lines re-mapped to Command Center presence + interactivity + live podcast HTTP 200. Domain 4: 20→10 checks. Overall total 119→109 (16 red-line unchanged). Resolves the audit/spec drift where no current blueprint could pass 100% because the audit still required a deliverable Bennett deleted.
- v1.5 (2026-05-23): Domain 8 added — Landing Page audit (8 checks, 4 red-line) per blueprint-ai-landing-page-skill v2 canonical recipe. Gates fki-preview/index.html on every landing-page commit. 119 total checks. Bennett directive 2026-05-23.
- v1.3 (2026-05-21): Council fix-loop prompt template added to Auto-Fix Protocol. D7-13 CEO results email check added (Domain 7). Audit history fields added to Artifact Registry schema + AUDIT_REPORT.json. Version bumped from 1.0→1.3 per WO-A (overdrive cycle 1). 111 total checks.
- v1.0 (2026-05-21): Initial build. Council v24 4.66/5.0 PASS. 110 checks across 6 domains.
  12 red-line checks. Known Failure Patterns table from 30+ real incidents.
  Skill-creator-skill v10 Create mode. Bennett directive: "at least 100 different points."
