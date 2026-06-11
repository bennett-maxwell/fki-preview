# Blueprint AI — Handoff to Kay/Jenn (2026-06-11, Madison out 6/12)

Prepared by Madison CC. Receipts referenced below live in this repo. Skill basis: blueprint-ai-skill v3.32 + audit v2.12 (Drive canonical, folder-scan verified).

## DONE TODAY (no action needed)
- **Melissa Tash (SRP)**: podcast re-cut via NotebookLM (11:43, direct-address PASS), live + sha-verified, production audit 16/16 = 100%. Gmail draft `r2659230966132308744` staged in Madison's inbox (To melissa@spoiledrottenphotography.com, cc Bennett). **Madison decides send vs reply-in-thread** (Melissa replied 6/09 to the 6/05 follow-up).
- **Mike Norton (Origins)**: verified clean — current live audio is NotebookLM-origin, PASS receipt, local-TTS file remains quarantined. No action.
- **CI**: blueprint-audit workflow green again (sky-bme-llc D10-05 classifier fix, commit 9663da26).
- **Pages built from real GHL form submissions** (contact customFields, never guessed): garlon-maxwell (Diamond Road), mark-bustamonte (Upfinity Consulting), sky-bme-llc (rebuilt — old page only had 3 agents and played MELISSA's podcast; never delivered to anyone). All three live, page audits 13/16 (only podcast gates pending).

## IN FLIGHT (check before touching)
- **Podcasts rendering serially via NotebookLM** (file upload broken — use LIVE PAGE URL as source, .md/.txt sources all error):
  - sky-bme-llc: cut 1 FAILED audit (hosts said "the source" / "we're analyzing") — re-cut queued with hardened steering. Notebook `10197a85-c84c-4d20-af9f-ac3243725318`.
  - garlon-maxwell: rendering (notebook `cfb2bd21-35e9-4e7f-a6cd-0b5363b55604`, task `32add378`).
  - mark-bustamonte: queued (notebook `813c8ef3-604d-4fb6-9d7b-b552e2204483`, source ready `01f13371`).
- Per-cut procedure (NEVER weaken a gate; re-cut instead): download → `ffmpeg -codec:a libmp3lame -b:a 128k` (NotebookLM m4a ~2x size) → `python3 scripts/podcast_direct_address_audit.py --audio <f> --first-name X --lead-name "X Y" --business-name "Z" --lead <slug>` → full-file transcript scan for third-person → if PASS: copy to `podcasts/<slug>.mp3`, commit, push, wait Pages deploy, `BLUEPRINT_REQUIRE_PUBLIC_AUDIO=1 python3 run-audit.py --lead <slug>` (re-run auditor with `--public-url` to mint http_code into the receipt), `bash scripts/mark-audit-complete.sh <slug> 100 16 16` → stage delivery email (draft only — Bennett "confirmed {slug}" or Madison send gate applies).
- Steering that PASSES first try (Melissa proof): ban list spelled out — never "the/this business/company/owner", never "source/sources/analyzing/looking at", exact opening line "Hi {First}, welcome. This walkthrough was built for you and {Biz}, from what you told us.", target 12-15 min.

## NOT DONE — needs Kay/Jenn (GHL admin)
- **GHL Blueprint AI follow-up campaign is NOT ACTIVE.** Receipt: `audit-receipts/_location/ghl-followup-campaign-readback-20260611.json`. Campaigns list = empty; across 8 sampled tagged contacts, 100% of outbound is source=app (manual). Required build: workflow triggered on tag `ai blueprint opt-in` (or delivery tag), steps at **4h / 24h / 3d / 7d** post-delivery, enroll the ~14 real tagged leads (list in the receipt). Per skill v3.32 §v3.25 item 7 this routes to GHL admin (Kay/Jenn), not Bennett.
- **Garlon Maxwell is tagged `blueprint-queued-pending-approve`** — once his podcast passes and the package is 100%, his delivery email needs the approval flow (he's also Bennett's father — flag to Bennett before sending).

## KNOWN TRAPS
- NotebookLM: generate ONE at a time (concurrent = auth churn); duration window 6-20 min target 12-18; >20MB mp3 = too long.
- GHL tag search: POST /contacts/search filters with operator "eq" (the `tags` query param 422s; "contains" returns 0).
- The fleet GHL key pit-65e5c066 is REVOKED — use the key in `~/.claude/.env` (pit-c4b3d077…).
- gen-blueprint.py now emits the D2-02 agent-prompt blocks itself; profiles need `ai_agents[].agent_prompt` (≥200 chars).
