# Blueprint Podcast Generation — Troubleshooting Runbook
_Authored 2026-06-30 from the Divya / Adam / Shivangi rebuild. Goal: faster, predictable podcast generation that passes the audit on the first or second try. Fold into the canonical blueprint-ai-skill podcast section on Drive (route to Ivan)._

## The reliable end-to-end recipe (do this, in order)
1. `python3 ~/.notebooklm/refresh_auth.py`  ← IMMEDIATELY before every NotebookLM call
2. Get the FULL notebook id: `notebooklm list --json` (never the truncated table id)
3. Ensure a source doc exists: `podcasts/<slug>-podcast-source.md` with the verbatim opening line (see #5). Audit D4-09 requires this file.
4. Generate: `notebooklm generate audio -n <FULL_ID> --length default --json "<instruction>"` (see instruction template #5/#6)
5. Poll until `status_id==3`, then `notebooklm download audio -n <FULL_ID> --latest --force /tmp/<slug>-full.mp3`
6. Transcode + trim in ONE step: `ffmpeg -y -i /tmp/<slug>-full.mp3 -t 900 -c:a libmp3lame -b:a 128k podcasts/<slug>.mp3`
7. `rm -f audit-receipts/<slug>/<slug>-production-47.json` then `python3 run-audit.py --lead <slug>`
8. Commit page + mp3 + source doc + receipt; push; wait for the **Actions** "Deploy static site to Pages" run + live mp3 HTTP 200.

## Errors hit & fixes (root-caused)
1. **Auth rotates within minutes.** `list` works right after refresh, then `artifact list`/`generate` 401/redirect a few minutes later (Google SID rotation on this seat). → Refresh right before EACH op; never rely on the morning refresh.
2. **Truncated notebook IDs.** The `list` table prints `abc123…`; using that → `RPC GET_NOTEBOOK null / account-routing mismatch (authuser index 0)`. → Always pull full UUIDs with `list --json`.
3. **Length is bimodal, NOT prompt-controlled.** `--length default` → ~15–21 min; `--length short` → ~6 min. "Target 9–13 minutes" in the prompt is ignored for length. → Use `--length default` then ffmpeg-trim to 15:00. `short` undershoots the 7-min floor (Shivangi short = 6:10, failed).
4. **Download is AAC/m4a despite the .mp3 name.** `ffmpeg -c copy → .mp3` fails: "Exactly one MP3 audio stream is required." → Always transcode with `-c:a libmp3lame -b:a 128k` (also guarantees the ≥5 MB audit floor).
5. **Direct-address opening (D3-02) not honored from the prompt alone.** NotebookLM's two-host format opens in third person. → (a) Put the verbatim opening in the SOURCE doc: `Open the audio with EXACTLY these words: "Hi <First>, welcome. This walkthrough was built for you and <Business>, from what you told us."` (b) Repeat it in the generate instruction. Audit opening check is lenient — it just needs `Hi <First>, welcome` in the first 500 chars + "you/your" ≥5 + first name ≥1.
6. **The word "sources" fails the audio (D3-02 banned phrase).** Hosts say "based on the sources…". → Generate instruction MUST forbid: "source", "sources", "source material", "this document", "the report"; substitute "what you told us" / "your answers". (This was the single blocker that held Divya at 94%.)
7. **Receipt race.** Two `run-audit.py` runs on the same slug race on `<slug>-production-47.json`. → Audit sequentially; `rm` the receipt before re-audit so the transcriber re-runs after any audio change.
8. **GitHub Pages: dead Jekyll builder + slow Actions deploy.** `/pages/builds/latest` shows "errored since 2026-06-09" (legacy Jekyll, ignore it). Real deploys = the GitHub **Actions** "Deploy static site to Pages" workflow, which takes several minutes (re-uploads all site mp3s). → Verify via the Actions run conclusion + live mp3 HTTP 200, not the Jekyll builds API. HTML can 200 from CDN cache while new files still 404 — don't trust HTML 200 alone.
9. **Audit non-podcast gotchas seen this run:** `D1-01_name_in_title` (put the lead's FIRST name in `<title>`), `D10-05` financial "industry unclassified" (add slug→industry in `financial-realism-check.py LEAD_INDUSTRY`), `D7-02` cloned ROI value (personalize `sl-contract value=` per lead, in-band), `D4-09` missing source doc.

## Duration gate
`run-audit.py podcast_duration_gate` MIN_SEC/MAX_SEC. Changed 8–12 → **7–16** on 2026-06-30 (Madison). Pending review of the 6-min cut → may widen to **6–16**. The canonical Drive `blueprint-ai-audit-skill` SKILL.md must be bumped to match (TODO — route to Ivan).
