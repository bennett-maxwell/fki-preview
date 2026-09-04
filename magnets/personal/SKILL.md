# lead-magnet-personal-skill v1.0

Generate a personalized lead magnet page for a Blueprint AI / Advaita prospect in
**under 30 minutes**, from **their website + LinkedIn/social only**. No intake form
required. Replaces the long-form blueprint as the default first-touch deliverable
(see `AUDIT-why-29-blueprints-did-not-book.md` for why).

## The product in one sentence

A ~600-word page that proves we already understand their business, hands them one
piece of work we already did for them, and gives them three ways to book — readable
top to bottom in 3 minutes on a phone.

## Hard rules (locked)

- **Noun:** "AI Employees" — never agents.
- **Offer lock:** $5,000 setup + $1,000/mo. Live in 14 days. Month-to-month.
- **Booking doors (all three, top AND bottom):**
  1. GHL widget `https://api.leadconnectorhq.com/widget/booking/CWLlHSfE2585XWo3VWpT`
  2. Call/text **(801) 980-0308**
  3. Intake form `https://blueprint.meetadvaita.com/` (the ONLY intake URL — marker BLUEPRINT-INTAKE-URL-CANONICAL-20260805)
  - **NEVER** paste `calendly.com/franchiseki/blueprint-ai` — it is HTTP 404.
- **Proof line (only proof allowed):** Anthony's AI hire paid for itself in under
  30 days — one sale through the ad employee and lead employee covered it.
- **Brand:** Advaita palette only — Plum `#4A1F63`, Saffron `#F5A623`, Warm Ivory
  `#F7F2E9`, Ink Plum `#17111F`, Mauve Mist `#EADFF0`, text-light `#7C5E8D`.
  Space Grotesk (display) + Inter (body). **Never blue** (`#0071E3` is retired).
  Saffron for accents on plum backgrounds (plum-on-plum is invisible — 1.0:1).

## Banned (these are what killed the 29)

- Industry statistics, citations, McKinsey/HBR anything
- Roadmaps, week-by-week plans, ROI calculators, prompt libraries
- The 6-AI-Employees grid, podcasts, "What your industry is already doing"
- Any sentence that could be pasted into another prospect's page unchanged
- More than 800 words of readable copy (the done-for-you asset text is exempt)
- A second form between them and booking

## Pipeline

### 1. Research — 15 minutes, website + social only

Open their website and note (quote exact wording where possible):

- [ ] Owner name, business name, city/service area
- [ ] Services offered; is pricing visible anywhere?
- [ ] **The contact path**: phone only? form? online booking? chat? What happens
      after hours? Any response-time promise ("we'll call you back within…")?
- [ ] Reviews/testimonials: how many, how old, is anyone replying to them?
- [ ] Anything promised on the site that has no visible mechanism behind it
- [ ] What's missing that a customer would want (booking, financing, pricing, FAQ)

Open LinkedIn / Facebook / Instagram and note:

- [ ] Owner's name, how they talk (formal? blunt? folksy?) — this calibrates voice
- [ ] Last post date; are they posting at all?
- [ ] Team size signals, hiring posts, busy-season complaints

If an intake form exists for this lead, use it as bonus color — but the page must
work without it.

### 2. Pick the 3 findings — 5 minutes

Each finding must pass this test: **it names something observable on their site or
profile** ("your contact form is the only way in after 5pm", "your last Google
review reply was 14 months ago"), states what it costs in **honest, labeled math
from their own numbers or one conservative stated assumption** — never industry
stats — and gives the fix in one sentence.

Rank by dollars. Cut anything generic. Three maximum.

### 3. Build the done-for-you asset — 5 minutes

Do finding #1's fix *for them*, in their voice, ready to use today with zero new
software. Good assets:

- The missed-call text-back message + first-reply email for a new inquiry
- A 3-touch estimate/quote follow-up sequence (day 2 / day 7 / day 14)
- Reply drafts for their 3 most recent unanswered Google reviews
- A seasonal reactivation message for past customers

Write it so they could copy-paste it in 10 minutes. Say explicitly: *"Use it today,
keep it forever — it's yours either way."*

### 4. Fill `TEMPLATE.html` — 5 minutes

Replace every `{{PLACEHOLDER}}`. Save as
`magnets/personal/<first-name>-<business-slug>.html`.

### 5. QA gates — do not send without all five

1. Zero `{{` remaining: `grep -c '{{' page.html` → 0
2. Readable copy ≤ 800 words
3. No retired blue, no Calendly, noun check: `grep -ciE '0071E3|calendly|AI agent'` → 0
4. Read the whole page aloud — under 3 minutes, and every paragraph contains at
   least one fact that is only true of THIS business
5. Contrast: run `scripts/advaita-palette-gate.sh` if available (no plum-on-plum)

## Delivery email (4 sentences, plain text)

> Subject: {{FirstName}} — we did your first hour of AI work for you
>
> {{FirstName}} — we looked at {{website}} and noticed {{finding #1, one clause}}.
> So we fixed part of it for you: {{link}} has the exact {{asset name}} written for
> {{Business}}, ready to copy-paste today — free, no strings.
> If you want the rest running for you, grab 15 minutes on the page or call/text
> (801) 980-0308.
> — Bennett

No attachments, no bullets, no "I hope this finds you well."
