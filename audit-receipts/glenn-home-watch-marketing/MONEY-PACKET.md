# Blueprint money packet — Glenn / Home Watch Marketing

who: Glenn Sojourner (Home Watch Marketing) | brand: Advaita/Blueprint | $impact_proxy: $5K setup + $2K/mo Advaita AI band (canonical pricing) — 1 qualified Blueprint prospect | metric_lever: delivered Blueprint -> tracked qualifier completion -> booked call | next_3_actions: (1) Madison runs `! notebooklm login` (2) podcast renders + attaches, audit -> 20/20 (3) Gmail draft built from Drive Stage-7 design, Madison approves send | delivery_state: staged_for_approval | fdd_claims_status: n/a (not a franchise offer)

## State

| Artifact | State | Proof |
|---|---|---|
| GHL lead verified real (cf=13) | DONE | contact `POCGQAr5YGFKNrWTmtXb`, Advaita `GPCi3FrWJCyevcGzZgTT` |
| Lead profile | DONE | `leads/glenn-home-watch-marketing.json` |
| Blueprint HTML built | DONE | `blueprints/glenn-home-watch-marketing.html`, commit `febdbb046` |
| Page live HTTP 200 | PENDING | GitHub Pages deploy in flight |
| Podcast | **BLOCKED** | NotebookLM auth expired — needs interactive Google OAuth |
| Audit | 16/20 | 4 podcast red-lines only; all page-side checks PASS |
| Delivery email draft | **HELD** | RL-DE4 bans building the draft before the podcast is live |

## The single blocker

`notebooklm login` requires an interactive Google sign-in in a browser plus an ENTER
keypress in the terminal. It cannot be completed headlessly. `notebooklm auth check`
and `notebooklm profile list` both report "authenticated" — that is a **false green**;
they read the local cookie file, while every real API call redirects to
`accounts.google.com/v3/signin`. Do not trust those two commands as auth proof again.

**Unblock:** Madison runs `! notebooklm login` in this session, completes the Google
login in the browser window, then presses ENTER.

Everything downstream is already staged and resumes automatically from
`scratchpad/glenn-podcast.sh`.

## Why the draft is held rather than written

`blueprint-ai-audit-skill` v2.29 **RL-DE4** (Madison directive 2026-07-17, which
post-dates the v2.27 podcast/send decouple of 2026-07-07):

> "The personalized podcast must exist and be live (public HTTP 200, in-window per
> D3-03) BEFORE any delivery-email draft is built or sent. No draft, no send without
> a live podcast = FAIL."

Building the draft now would violate the newest governing directive and would ship a
page whose Listen player 404s — the exact `william-diggers-catch` defect from 2026-07-30.

## Expansion seeds (next artifacts, owner-bound)

1. **Home Watch niche lookalike list** — Glenn's clients are Home Watch owners; the same
   ICP is a repeatable Advaita segment. next_artifact: Apollo pull of Home Watch operators |
   owner: Madison | success_metric: 25 net-new contacts | revenue_link: new Blueprint leads.
2. **Agency-as-client angle** — Glenn is an agency that sells AI and still has an ops gap.
   That is a reusable narrative for other agency leads. next_artifact: outreach angle doc |
   owner: Madison | success_metric: 3 agency prospects opened | revenue_link: pipeline.
3. **NotebookLM auth watchdog** — this false-green cost a full render cycle. next_artifact:
   pre-flight probe that makes a real API call, not `auth check` | owner: Madison |
   success_metric: 0 silent auth failures | revenue_link: no missed 24h deliveries.
4. **Listen-section pending state** — page shipped pointing at a 404 mp3. next_artifact:
   auto "finalizing" placeholder when `podcast_status != ready` | owner: Madison |
   success_metric: no page live with a 404 player | revenue_link: delivery quality.
5. **Booking-warning false positive** — `clone-blueprint.sh` flags any "booking" string,
   including agent names. next_artifact: tighten to URL-context match | owner: Madison |
   success_metric: no false warnings | revenue_link: gate credibility (a gate that cries
   wolf gets ignored — the skill's own stated defect class).
