# Advaita AI — Launch Funnel

**Live URL:** https://bennett-maxwell.github.io/fki-preview/advaita/
**Target launch:** 7am MDT 2026-05-11
**Owner:** Bennett Maxwell

## What this is

A static 3-page funnel:
1. `index.html` — Hero + 3 outcomes + testimonial + podcast strip + waitlist form
2. `quiz.html` — 10-question AI Readiness Quiz (JS, no backend)
3. `result.html` — Score reveal + $-leakage moment + 3 CTAs (Calendly / Podcast / Waitlist)

Plus:
- `style.css` — Apple-light design tokens
- `quiz.js` — quiz logic + scoring + localStorage
- `nurture-emails.md` — 5-email GHL sequence draft
- `launch.sh` — one-command deploy

## Deploy

```bash
bash /Users/temp/Desktop/advaita-launch-2026-05-10/funnel/launch.sh
```

Steps:
1. Clones `bennett-maxwell/fki-preview` to `~/code/` if missing
2. Copies `funnel/*` to `~/code/fki-preview/advaita/`
3. `git add . && git commit -m "Advaita launch 2026-05-11" && git push`
4. Waits 30s for GitHub Pages, curls live URL, confirms 200

## Kill switch (rollback)

```bash
cd ~/code/fki-preview && rm -rf advaita/ && git add . && git commit -m "Rollback Advaita" && git push
```

Site is gone in ~60s.

## Gates (waiting on Bennett)

- **G_GHL_WEBHOOK** — Waitlist form `action=` URL placeholder `https://services.leadconnectorhq.com/hooks/TBD`. Need real hook ID from GHL.
- **G_PODCAST_URLS** — Spotify / Apple / YouTube links currently `#`. Need live show URLs once published.
- **G_TESTIMONIAL** — Hero testimonial is placeholder. Need real founder quote + attribution.
- **G_NURTURE_INSTALL** — `nurture-emails.md` drafted but not installed in GHL workflow.

## Diamond 3-check

1. **HTTP 200 on live URL** — verified by `launch.sh` curl step
2. **Quiz submits with score in URL** — JS routes to `result.html?score=X&band=Y&rev=Z`
3. **All result-page CTAs have valid hrefs** — Calendly (real), Spotify (placeholder but non-empty), Waitlist form (placeholder action)

## Architecture notes

- 100% static. No build step. Works file:// for local preview.
- Quiz state persists to `localStorage` so refresh doesn't lose progress.
- $-leakage formula (Hormozi pattern): `gap * monthly_rev * 0.02` where `gap = 100 - score`.
- Result copy is empowering (Robbins lens), never shaming. 4 score bands with tailored plans.
- Mobile-first responsive. Tested at 375px / 768px / 1440px breakpoints.
- Brand: white #FFFFFF, ink #1D1D1F, accent #0066FF (Advaita blue), muted #86868B.
