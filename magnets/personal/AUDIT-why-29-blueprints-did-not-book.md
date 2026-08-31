# Why 29 sent Blueprints produced 0 bookings — audit 2026-08-31

Reviewed: all 95 generated pages in `blueprints/` (29 externally sent), `TEMPLATE.html`,
delivery emails, and the three hub magnets (/plan, /calculator, /score).

## The numbers

| Measure | Value |
|---|---|
| Median length | ~3,200 words (16+ minute read; longest 5,191 words / 26 min) |
| Vocabulary shared with TEMPLATE.html | 40–70% per page |
| First booking link position | ~78% of the way down the page (median) |
| Sections per page | 13–15 (roadmap, stats, tool stack, opportunity map, 6 AI Employees, ROI calculator, 3 prompts, demo, podcast, citations…) |
| Booking doors above the fold | 0 |

## The five reasons nobody books

1. **It's a whitepaper, not a gift.** A 16–26 minute read is a task. Prospects are the
   exact people who don't have 20 minutes — that's the problem we sell against.
   Most never reach the CTA at 78% scroll depth.

2. **The personalization is thin where it matters.** Name/business substitution plus
   intake echo ("You told us…") wrapped in 60% template prose. McKinsey/HBR 2023
   citations and "operators in your position now run an AI Employee for exactly this"
   repeated six times per page read as mail-merge, not attention.

3. **It assigns homework instead of doing work.** Roadmaps, prompt libraries, ROI
   calculators — all things the prospect must go implement. The value is theoretical
   until they act. Nothing on the page is *already done for them*.

4. **One buried, indirect door.** Single CTA to `qualify.html` (a second form) at the
   bottom. The working GHL booking widget isn't on the page. More steps, less booking.

5. **It tells instead of shows.** Six described AI Employees < one working artifact.
   The page claims AI can write in their voice — and then doesn't demonstrate it.

## What replaces it

`magnets/personal/` — a ~600-word, 3-minute personalized page built from **website +
LinkedIn/social research only** (no intake form needed):

- **3 specific findings** from *their* website — quoted, costed with honest math.
- **1 done-for-you asset** — the actual messages their business should be sending,
  written in their voice, copy-paste usable today, free, no strings.
- **Booking doors at top and bottom** — GHL widget + phone + /apply. Never Calendly.

See `SKILL.md` for the generation pipeline and QA gates, `TEMPLATE.html` for the page,
and the two rebuilt examples (`butch-threadgills-roofing.html`, `john-jj-landscape.html`).
