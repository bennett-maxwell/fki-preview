---
name: notebooklm-blueprint-ai-skill
aliases:
  - blueprint-podcast-framework-skill
  - blueprint-ai-podcast
  - notebook-blueprint
  - podcast-skill
  - blueprint-podcast
  - notebooklm-blueprint-ai-skill
version: 1.8
drive_file_id: 1_MIDfkQK7vaIUvY0QnSzBIRvuLFgfCxP
last_updated: 2026-05-26
council_verified: 4.81/5.0 (v1.5 base) + 5/5 direct-address fix (v1.6)
description: "Blueprint AI podcast generation — v1.6 direct-address hard gate. Section 1 = transcript-style 'Hi {first_name}...' monologue. Validator regex-blocks any source doc without owner's first name + ≥3 you/your refs in Section 1 + zero third-person phrasing. NotebookLM TTS reads body opening louder than directive blocks — must address owner in the first 100 words of body."
scope: Mack, Ivan-CC
---

# Blueprint Podcast Framework Skill v1.6 — Podcast Generation SOP

**version:** 1.6 | **created:** 2026-05-19 | **updated:** 2026-05-23 | **council:** 4.81/5.0 base + direct-address fix
**scope:** Mack + Ivan-CC

## RULE #1 — RED LINE (v1.6) — DIRECT ADDRESS IS NON-NEGOTIABLE
Every podcast MUST address the owner directly in the first 100 words of body audio.
NotebookLM TTS reads body opening louder than directive blocks — appendix instructions
alone are unreliable (Branson worked by luck; Brent + Brittney spoke 3rd-person
with same template). Section 1 opening MUST start "Hi {first_name}…" and contain
≥3 you/your refs + zero third-person phrasing. Validator regex-blocks violators
BEFORE NotebookLM upload. Whisper post-check transcribes first 30s of every MP3
and rejects any that don't speak the owner's first name in opening line.

## TRIGGER
"generate podcast" / "build podcast for [name]" / "podcast segment" / "NotebookLM source" / any Blueprint AI podcast work

## PRE-FLIGHT CHECKS
- [ ] blueprint-lead-intake-skill run on this lead (profile card exists)
- [ ] Industry confirmed (never "other")
- [ ] Industry top 10 list generated
- [ ] ROI calculated from form answers only
- [ ] BIL filter applied to all customer-facing language
- [ ] **Source doc ≥18KB** — verify with `wc -c source-doc.md` before NotebookLM upload. If <18KB, expand sections 3-4-5 with more specifics. Melissa Tash self-audit (3.94/5) root cause was 3KB generic doc.

## PERMANENT RULES (council-locked 2026-05-19)
1. **No agent names.** Say "an AI agent" or "your AI agent." Never Piper, Sam, Reed, Leo, etc.
2. **No calendar booking CTA.** Application prompt only.
3. **ROI from their numbers only.** Locked formula: 35% lift floor, $150/hr, 4.3 weeks/month.
4. **All customer-facing language through BIL.**
5. **Simplicity pitch in Segment 5:** "Once set up, this runs itself."
6. **Frame as ideas, not prescriptions:** "These are just ideas. Customize however you want."
7. **Quality and reliability over speed.**
8. **Assume business excellence.** Never imply the prospect's business is struggling, falling behind, or a mess. Frame AI as amplifying what they already do well. Gaps = "time recovery opportunities." (Rule 12)
9. **Brand voice is instant, not learned.** Built BEFORE launch via intelligence skill audits (email patterns, WhatsApp, marketing). Every client gets a brand guide. Bot launches at 90%+ accuracy. Tweaks = calibration, not learning. (Rule 13)

## 7-SEGMENT STRUCTURE (~20 min)

### Segment 1 — This Is Your Business (0:00-1:30)
Open with name, company, real form data. Describe their current world using their tools + pain points. Close: "Here's what your AI gave us back instantly based on what you told us."

### Segment 2 — Where You Are With AI + Industry Top 10 (1:30-4:00)
AI maturity from form. Top 5-10 industry AI use cases. Then 3-5 that apply to them specifically based on tool stack + pain points.

### Segment 3 — The Gaps We Found (4:00-8:00)
3-4 gaps mapped to stated stresses. Each: [gap] -> [cost: reliability/predictability/quality] -> [what AI agent does instead]. ROI from their own numbers.

### Segment 4 — What Your Business Looks Like Running This (8:00-12:00)
"Here's what's already been built." Day in the Life specific to their industry/tools/team. No agent names. Close: "You could try to replicate this yourself, or ask us to build it and maintain it."

### Segment 5 — Your Tech Stack, Already Connected (12:00-14:30)
Map each tool to specific AI action (table format). No CRM = Priority Gap #1. Close with simplicity pitch.

### Segment 6 — The Timeline (14:30-17:30)
Verbatim language:
- Days 1-3: Onboarding. 12-month email audit. Brand voice profile. Full ops map. We listen.
- Days 4-10: Auto-correcting, calibrating, first automations live. SOPs become agent skills.
- Day 30: System runs your business rhythm. Compounds, never forgets.
- Months 2-3: Light calibration, minimal manual input.
- After Month 3: System and team integrated. World-class employee, 24/7, fully autonomous.

### Segment 7 — What To Do Next (17:30-20:00)
Restate "ideas from your answers." If any gap resonated -> apply. Application CTA only. No pressure, no pitch.

## NOTEBOOKLM SOURCE DOC FORMAT (12-Section Template — canonical)

Every source doc MUST have these 12 sections in this order. ~196 lines. Use Court Lundberg + Melissa Tash source docs as canonical examples.

**HEADER:** Title block — "NOTEBOOKLM SOURCE DOCUMENT / AI Roadmap for [Name] — [Company] / Prepared by Franchise Ki | bennett@franchiseki.com"

**Section 1 — About [Person] and [Company]:** Narrative bio, what they do, scale, location, vision. 3-5 paragraphs. Source: website + form answers. NO fabricated data.

**Section 2 — Current Tool Stack:** "WHERE [COMPANY] IS TODAY" — exactly 6 tools they currently use with descriptions. Source: form answers only.

**Section 3 — 3 Biggest AI Opportunity Gaps:** Each gap = [problem] → [cost in reliability/speed/quality] → [what AI agent does instead] + ROI using ONLY their numbers (35% lift floor, $150/hr, 4.3 weeks/month formula). Each gap MUST cite published research with URL (HBR, McKinsey, SBA, BrightLocal).

**Section 4 — The N AI Agents Built for [Company]:** Usually 6 agents. Each = Agent name + what it monitors/does + specific outcome sentence. NO agent brand names (never Piper, Sam, Reed, Leo). Say "your AI agent."

**Section 5 — What [Company]'s Reviews Tell Us:** Pull 3-5 themes from Google reviews or website testimonials. Anchor social proof.

**Section 6 — 30-Day Onboarding Timeline:** VERBATIM language only:
- Days 1-3: Onboarding. [industry] audit. Brand voice profile. Full ops map. We listen.
- Days 4-7/10: Auto-correcting, calibrating, first automations live. SOPs become agent skills.
- Day 30: System runs your business rhythm. Compounds, never forgets.
- Months 2-3: Light calibration, minimal manual input.
- After Month 3: System and team integrated. World-class employee, 24/7, fully autonomous.

**Section 7 — Three Prompts — Start Today Without Waiting:** 3 copy-paste prompts for ChatGPT/Claude they can run themselves. NOT full code. Each prompt is 2-4 sentences with specific inputs (name, invoice #, job type). DIY entry point.

**Section 8 — Two Paths Forward:** DIY Path (use prompts, see results in days) + Partner Path (FKI builds full system). Partner CTA: bennett-maxwell.github.io/fki-preview/apply/ — application only, NO calendar booking.

**Section 9 — The ROI Picture:** Industry benchmark numbers from published research applied to THEIR business profile (from form). Use their actual job value, volume, close rate, admin hours. End with disclaimer: "These are industry benchmarks. Results vary by business. No outcomes are guaranteed."

**Section 10 — Common Objections — And Honest Answers:** Exactly 4 objections. Honest, non-salesy responses. Use objections specific to their industry.

**Section 11 — Sources and Citations:** Clickable URLs for EVERY stat cited. Format: [N] Publication — "Title" (year) — metric. URL. Minimum 4 sources.

**Section 12 — About Franchise Ki:** 2 sentences. Apply CTA: bennett-maxwell.github.io/fki-preview/apply/. Contact: bennett@franchiseki.com.

---
**Upload:** Primary source = this .txt file. Second source = their website URL. Generate Audio Overview in NotebookLM.
**HARD RULES:** No emojis. No fabricated data. ROI from their numbers ONLY. Application CTA only. BIL voice pass before uploading.

## OUTPUT CHECKLIST
- [ ] 7-segment outline with their specific data
- [ ] Industry top 10 list (5-10 items)
- [ ] 3-5 recommended starters highlighted
- [ ] ROI figure with formula visible
- [ ] Tech stack table
- [ ] Timeline language (verbatim)
- [ ] BIL pass complete
- [ ] No agent names anywhere
- [ ] CTA is application, not calendar
- [ ] "These are ideas" in Seg 1 + Seg 7
- [ ] Simplicity pitch in Seg 5

## ANTI-PATTERNS
- Building podcast without intake skill run first
- Fabricating ROI numbers
- Including calendar booking link
- Naming agents in output
- Skipping BIL voice check
- Using generic industry instead of confirmed specific

---

## AUDIO PLAYER STANDARD v1.0 (Council-certified 2026-05-21)

Every Blueprint AI HTML deliverable MUST embed the standard audio player (not a Drive link). The player uses pure HTML/CSS/JS with zero external dependencies. Source: `blueprint-podcast-framework-skill-SKILL.md` Audio Player section.

### Audio Player Placeholders (2 required per Blueprint HTML)
- `PODCAST_MP3_URL_PLACEHOLDER` → replace with GitHub Pages URL: `https://bennett-maxwell.github.io/fki-preview/podcasts/[slug].mp3` (Rule 8: ZERO Drive links in client-facing HTML)
- `PODCAST_DRIVE_URL_PLACEHOLDER` → replace with GitHub Pages URL (same pattern) for the Download MP3 button + error fallback. Drive links are BANNED per Rule 8.

### localStorage Key Convention
`bpod_[lead_slug]` — e.g. `bpod_melissa_tash` — stores resume position in seconds

### Chapter Timestamps (7-segment, percentage of total duration)
| Seg | Start % | Label |
|-----|---------|-------|
| 1 | 0% | This Is Your Business |
| 2 | 7.5% | Where You Are With AI |
| 3 | 20% | The Gaps We Found |
| 4 | 40% | Running This |
| 5 | 60% | Your Tech Stack |
| 6 | 72.5% | The Timeline |
| 7 | 82.5% | What To Do Next |

### 34-Feature Audio Player Checklist (Council v19 — ALL required)

**Core Playback (8)**
- [ ] 1. Large play/pause button — min 56px touch target on mobile, 64px on desktop
- [ ] 2. Visual progress bar — full-width, seekable
- [ ] 3. Progress fill — animates in real time as audio plays
- [ ] 4. Drag thumb — movable thumb indicator showing current position
- [ ] 5. Elapsed time display — MM:SS format, left-aligned below bar
- [ ] 6. Total duration display — MM:SS format, right-aligned below bar (populated on `loadedmetadata`)
- [ ] 7. Skip back 15 seconds button — labeled "15s", with backward-arrow icon
- [ ] 8. Skip forward 30 seconds button — labeled "30s", with forward-arrow icon

**Mobile UX (6)**
- [ ] 9. Touch-drag scrubbing — `touchstart`/`touchmove`/`touchend` listeners on progress track
- [ ] 10. `touch-action: none` on progress track to prevent scroll conflicts
- [ ] 11. All tap targets ≥ 44px — no hover-only interactions
- [ ] 12. Full-width progress bar (100% of container) — easy thumb hit on small screens
- [ ] 13. Responsive layout — controls stack cleanly at ≤640px
- [ ] 14. Font size ≥ 14px for all time/chapter labels (no tiny text)

**Visual / Engagement (7)**
- [ ] 15. Animated equalizer bars (5 bars, CSS `@keyframes eqBounce`) — shown when playing, hidden when paused
- [ ] 16. Buffering-friendly — player renders immediately, `preload="metadata"` on `<audio>`
- [ ] 17. Progress bar color matches lead brand accent (`var(--brand-light)`)
- [ ] 18. Player card uses brand gradient header (`var(--brand-dark)` → `var(--brand)`)
- [ ] 19. Lead name + company in subtitle field — always personalized, never generic
- [ ] 20. Dynamic badge — shows "Ready to play", "Now Playing", "Paused", or "Resume from MM:SS"
- [ ] 21. Mute/unmute toggle — icon switches between volume-on and volume-off SVG

**Navigation (4)**
- [ ] 22. Chapter pip markers — 6 pips at segment boundaries on progress bar
- [ ] 23. Current chapter name — displayed above progress bar, updates in real time as position changes
- [ ] 24. Chapter label live-region — `aria-live="polite"` on chapter name element
- [ ] 25. Playback speed selector — 0.75×, 1×, 1.25×, 1.5×, 2× options

**Persistence / Smart Behavior (5)**
- [ ] 26. Resume from last position — `localStorage.getItem(STORAGE_KEY)` on `loadedmetadata`; only restore if > 0 and < duration - 5s
- [ ] 27. Auto-save position — `localStorage.setItem` on every `timeupdate`
- [ ] 28. Auto-pause on tab hidden — `visibilitychange` event listener
- [ ] 29. Global keyboard shortcuts — Space = play/pause, Left arrow = back 15s, Right arrow = forward 30s (skips if `INPUT`/`SELECT`/`TEXTAREA` focused)
- [ ] 30. Progress bar keyboard control — `keydown` on track element for Left/Right arrows (ARIA slider)

**Accessibility (2)**
- [ ] 31. ARIA labels on all controls — play button `aria-label` updates to "Play"/"Pause" dynamically
- [ ] 32. Progress track as ARIA slider — `role="slider"`, `aria-valuemin="0"`, `aria-valuemax="100"`, `aria-valuenow` updated on `timeupdate`

**Fallback / Error (2)**
- [ ] 33. Error state shown on `<audio>` error event — displays "Open in Google Drive instead" with fallback link
- [ ] 34. Download MP3 button — links to `PODCAST_DRIVE_URL_PLACEHOLDER` for offline listening

**Bonus / Stickiness (2)**
- [ ] 35. Sticky mini-player — appears fixed at bottom when player scrolled out of view and audio is playing; auto-hides on pause
- [ ] 36. Mini-player shows lead name + current time + play/pause button

### Pre-Delivery Audio Player Check (runs inside Stage 6 blueprint-ai-skill)
```
POD-CHECK 1: PODCAST_MP3_URL_PLACEHOLDER replaced with real Drive URL (grep for PLACEHOLDER)
POD-CHECK 2: PODCAST_DRIVE_URL_PLACEHOLDER replaced in download link + error fallback
POD-CHECK 3: localStorage key uses lead slug (no generic default)
POD-CHECK 4: Lead name appears in player subtitle (no "Melissa Tash" or generic text)
POD-CHECK 5: <audio preload="metadata"> present (not preload="auto" or missing)
POD-CHECK 6: All 7 chapter pips present in DOM
```

### Branded Player CSS Variable Map
```
Player background header: linear-gradient(160deg, var(--brand-dark) 0%, var(--brand) 100%)
Progress fill color:       var(--brand-light)
Thumb color:               #ffffff
Body overlay:              rgba(0,0,0,0.28)
Chapter pip:               rgba(255,255,255,0.55)
Time text:                 rgba(255,255,255,0.55)
Chapter name:              var(--brand-light)
```
All colors auto-inherit from the Blueprint HTML `:root` block — no hardcoded hex in player CSS.

---

## HARD OPERATIONAL GATES (v1.7 — verified in production 2026-05-26)

### GATE A — `podcast_queue: PASS` IS A FALSE GATE
`batch_summary.json` reporting `podcast_queue: PASS` ONLY means the NotebookLM notebook was created.
It does NOT mean sources were uploaded, processed, or audio was generated.
**Real PASS requires ALL 4:**
1. `notebooklm source list --notebook $NB_ID` → ≥1 source with `status: READY`
2. `notebooklm artifact list --notebook $NB_ID` → ≥1 artifact with `status: completed`
3. MP3 file exists on disk (`ls -lh $PATH/*.mp3`) and is ≥5MB
4. `source src="..."` in blueprint HTML points to a real accessible URL (not PLACEHOLDER)

### GATE B — NotebookLM create JSON parse pattern
`notebooklm create "Title" --json` returns:
```json
{"notebook": {"id": "abc123-..."}}
```
Parse as `d['notebook']['id']` — NOT `d['id']`. `d['id']` throws KeyError.

### GATE C — Auth expires during batch runs (~every 5 leads)
Run `python3 ~/.openclaw/bin/notebooklm-cookie-refresh.py` between leads when:
- Any notebooklm command returns an authentication redirect URL
- Any command output includes "Authentication expired or invalid"
Expected output: `Authentication is valid.`

### GATE D — Download filename collision
`notebooklm download audio /path/to/file.mp3 -a $ART -n $NB` saves as `file (2).mp3`
if `file.mp3` already exists. Always force-overwrite:
```bash
notebooklm download audio /tmp/new.mp3 -a $ART -n $NB
mv "/tmp/new (2).mp3" /tmp/new.mp3 2>/dev/null || true
```
Or download to a temp path first, then `mv` to the target.

### GATE E — GitHub Pages audio URL canonical pattern
All podcast MP3s for Blueprint AI leads live at:
`https://bennett-maxwell.github.io/fki-preview/podcasts/[slug].mp3`
Where `[slug]` must exactly match the `source src` value in the blueprint HTML.
Check current HTML source first: `grep 'source src' blueprints/[slug].html`
Rename downloaded files to match — never assume the slug.

### GATE F — Lost lead recovery
A lead is "lost" when they filled the intake quiz (GHL tag `ai blueprint opt-in`) but have no:
- blueprint HTML at `fki-preview/blueprints/[slug].html`
- delivery email sent
To find lost leads: query GHL `/contacts/?tag=ai blueprint opt-in` and diff against `ls blueprints/`.
4 lost leads discovered 2026-05-26 (Alex Ramos, Rush Evans, Jaden Mecham, Austin Iron Horse).

---

## CHANGELOG
- v1.8 (2026-05-26): **72hr error audit hardening.** Fixed: (1) Audio player placeholder URLs changed from Drive download to GitHub Pages pattern (Rule 8 compliance — Drive links BANNED). (2) Section 8+12 apply CTA from blueprint.meetadvaita.com/apply to bennett-maxwell.github.io/fki-preview/apply/. (3) Self-audit checklist expanded to verify Gate A-F. All fixes prevent 3 recurring delivery failures: Drive links in client HTML, wrong apply URL, and false podcast PASS.
- v1.7 (2026-05-26): **Operational Gates A-F added** — learnings from production rebuild of all 14 Blueprint AI leads. Root cause: batch pipeline was creating empty notebook shells and reporting PASS. All 6 false-gate patterns now codified: (A) podcast_queue PASS is false, (B) create JSON parse pattern, (C) auth expiry cadence, (D) download filename collision, (E) GitHub Pages URL matching, (F) lost lead recovery via GHL tag diff. Memory: feedback_blueprint_pipeline_false_pass.md.
- v1.6 (2026-05-23): **Direct-Address Hard Gate** — Brent + Brittney podcasts spoke 3rd-person despite v1.5 HOST DIRECTIVE because NotebookLM TTS reads body opening louder than directive blocks. v1.6 fixes:
  (1) Section 1 rewritten as transcript-style "Hi {first_name}, welcome..." monologue (direct address in first 100 words).
  (2) Directive block compressed to 3 hard rules at top (RULE #1 RED LINE = direct address).
  (3) Validator regex gate: Section 1 must contain `Hi {first_name}` + ≥3 you/your refs + zero third-person phrases (he/she/they/this business/the owner). Hard-blocks upload to NotebookLM.
  (4) Version stamp `<!-- v1.6 -->` on every source doc + validator rejects missing stamp.
  (5) podcast-batch-v15.sh auto-runs `--rebuild-sources` before batch — no more stale docs.
  (6) Whisper first-30s post-check: transcribes opening, rejects MP3 missing owner's first name. Re-runs failures.
  Root cause memory: feedback_podcast_third_person_root_cause.md.
- v1.5 (2026-05-23): Council v19 — 10 improvements applied. generate-podcast.py rewritten:
  (1) Inject prompt_1/2/3 — personalized AI tools are now the core of Section 4.
  (2) 12-section SOURCE_DOC_TEMPLATE replaces 40-line generic template (3KB→18KB+).
  (3) HOST DIRECTIVE block forces NotebookLM hosts to address owner directly by name.
  (4) All body text rewritten in second person ("you/your" throughout).
  (5) File-existence + ≥5MB size gate after download — no silent failures.
  (6) MP4→MP3 extension fixed — audio player was receiving wrong format.
  (7) Hard 18KB gate BEFORE NotebookLM upload — blocks junk source docs.
  (8) Batch "done" = file-on-disk proof (timeout no longer counts as success).
  (9) All 18 profile fields extracted (services, url, team_size, pain_points, roi, etc.).
  (10) Batch manifest JSON written after every run — delivery gated on manifest.
  All 10 source docs rebuilt and validated. Zach source doc: 3.4KB→18.2KB. Council 4.81/5.0.
- v1.3 (2026-05-22): TONE + BRAND VOICE FIX — "learning" → "calibrating" in Segment 6 + Section 6 (4 lines each). "gets better every week" → "fully autonomous." "System knows your business" → "System runs your business rhythm." Added Rules 8 (assume excellence) + 9 (brand voice instant). Added 6 aliases. Restored from archive to active subdirectory. Bennett directive 2026-05-22.
- v1.2 (2026-05-21): Audio Player Standard v1.0 added — 34-feature mobile-first HTML5 player spec, chapter pip system, localStorage resume, sticky mini-player, pre-delivery POD-CHECKs 1-6, CSS variable map. Council directive: Bennett 2026-05-21 "can't see how far into it, can't rewind, can't fast-forward." All new blueprints must embed player, not Drive link.
- v1.1 (2026-05-21): Renamed to notebooklm-blueprint-ai-skill. Alias: blueprint-podcast-framework-skill. Source doc template gap documented — 12-section format required (see Court/Melissa canonical examples). For NotebookLM API tool → see notebooklm-skill.
- v1.0 (2026-05-19): Initial. 7-segment framework proven on 7 leads (Dave, Paul, Chris, Zachary, Branson, Brittney, Court). Council 4.62/4.5.

## Self-Audit Checklist (used by angie-weekly-audit-skill v8+)

Angie uses this checklist as the SOP rubric when auditing this business area.

1. [ ] Skill was invoked successfully in the last 30 days (or manually reviewed as active)
2. [ ] SKILL.md has valid frontmatter with name, description, version, and drive_file_id
3. [ ] All trigger phrases route correctly to this skill
4. [ ] Gate A verified: podcast_queue PASS requires all 4 checks (source READY, artifact completed, MP3 >=5MB, real URL in HTML)
5. [ ] Gate B verified: NotebookLM create JSON parsed as d['notebook']['id'] not d['id']
6. [ ] Gate C verified: auth refresh runs between leads during batch
7. [ ] Gate D verified: download filename collision handled (mv pattern)
8. [ ] Gate E verified: GitHub Pages URL matches slug in blueprint HTML source src
9. [ ] Gate F verified: lost lead recovery via GHL tag diff runs after batch
10. [ ] Zero Drive links in audio player placeholder instructions (Rule 8)
11. [ ] Apply CTA uses GitHub Pages URL, not blueprint.meetadvaita.com

## Cron Bindings

None — manually invoked. No scheduled LaunchAgent or cron job owns this skill.
