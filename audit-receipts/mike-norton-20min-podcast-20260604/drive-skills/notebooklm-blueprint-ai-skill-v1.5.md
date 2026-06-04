---
name: notebooklm-blueprint-ai-skill
alias: blueprint-podcast-framework-skill
version: 1.5
last_updated: 2026-05-25
base_versions: 1.4 (drive_id 10WIk9v_Ng8jLEm2sOuvGpYNdww9XkHvD, modifiedTime 2026-05-23T02:39:29.178Z) + 1.4.1 micro-patch (drive_id 1RkGa4xZK_nFZ4D0QvGHnYe8qXYjIAzMA, modifiedTime 2026-05-23T04:48:38.615Z)
author_agent: mack-agent-a (Bennett autopilot directive 2026-05-25 19:19 MDT)
description: >
  Blueprint AI podcast generation. v1.5 adds AUDIO-OUTPUT VERIFICATION —
  prevents the failure mode where a podcast `.md` source doc URL ships in place
  of the `.mp3` audio file (the Alex/DePuy near-miss 2026-05-26 when Ivan-CC SSH
  was down >24h). Every podcast deliverable must satisfy a Content-Type =
  `audio/mpeg` HEAD probe before the skill marks done.
scope: Mack, Ivan-CC
---

# notebooklm-blueprint-ai-skill v1.5 — Audio-Output Verification

## What changed in v1.5

- **NEW Rule 15** — AUDIO-OUTPUT VERIFICATION. Before any podcast deliverable is marked `podcast_status: ready`, the final URL must return HTTP 200 AND `Content-Type: audio/mpeg`. A `.md` source doc URL is NEVER an acceptable substitute.
- **NEW pre-completion HEAD probe** added between the GitHub Pages upload step and the "send podcast links to bennett@ + madison@" step (existing Rule 13).
- **NEW failure-mode block**: if Ivan-CC is down and audio cannot be generated, the skill HALTs and posts to #leo-bennett rather than allowing source-doc fallback. Source doc is for internal review only; never shipped to lead.
- **Rules 1–14 from v1.4 unchanged.** Rule 12 retains the v1.4.1 micro-patch (1x · 1.25x · 1.5x speed buttons minimum).

---

## NEW Rule 15 — Audio-Output Verification (Bennett directive 2026-05-25)

> Every podcast deliverable URL MUST pass this probe before the skill returns `podcast_status: ready`:
>
> ```bash
> RESP=$(curl -sI -X HEAD "$PODCAST_URL")
> STATUS=$(echo "$RESP" | head -1 | awk '{print $2}')
> CTYPE=$(echo "$RESP" | grep -i '^content-type:' | awk '{print $2}' | tr -d '\r\n;')
>
> if [ "$STATUS" != "200" ] || [ "$CTYPE" != "audio/mpeg" ]; then
>   echo "FAIL: status=$STATUS content_type=$CTYPE"
>   exit 1
> fi
> ```
>
> Acceptable Content-Type values: `audio/mpeg` ONLY.
> Rejected: `text/markdown` (source doc), `text/html` (placeholder page), `application/octet-stream` (raw bytes — likely upload misconfigured), anything else.
>
> Failure path:
> 1. HALT — do NOT mark podcast_status: ready
> 2. Do NOT send podcast links to bennett@ + madison@ (Rule 13 is conditional on Rule 15 PASS)
> 3. Post to #leo-bennett (C0APWHBBHLP): "Podcast audio FAIL for [slug] — status=[X] content-type=[Y]. Source doc fallback NOT permitted for lead delivery."
> 4. If Ivan-CC SSH is the blocker: fall back to NotebookLM web UI via Chrome (Mack-driven, ~30 min), OR re-classify the entire Blueprint package as INTERNAL APPROVAL ONLY (forces blueprint-ai-skill v3.11 Stage 5.5 halt path b).

This rule eliminates the failure mode from past-blueprint-failures-2026-05-25.md Pattern 2 (podcast source doc linked in place of MP3 audio).

---

## NEW pre-completion HEAD probe (sequence)

The skill's completion sequence is now:

```
1. Generate audio via notebooklm-py OR NotebookLM web UI fallback
2. Verify local file size > 29MB (existing check)
3. Upload to bennett-maxwell.github.io/fki-preview/blueprints/podcasts/[slug].mp3
4. Verify HTTP 200 (existing Rule 10)
5. [NEW] Run Rule 15 HEAD probe → must return audio/mpeg
6. [NEW] If Rule 15 PASS: continue. If FAIL: HALT per failure path above.
7. E2E inbox test (existing Rule 11)
8. Send podcast links to bennett@ + madison@ (existing Rule 13)
9. Mark podcast_status: ready
```

---

## Audio-output receipt schema (logged to ~/.openclaw/logs/podcast-audio-verify.jsonl)

```json
{
  "slug": "[lead-slug]",
  "timestamp": "[ISO 8601 UTC]",
  "url": "https://bennett-maxwell.github.io/fki-preview/blueprints/podcasts/[slug].mp3",
  "http_status": 200,
  "content_type": "audio/mpeg",
  "content_length_bytes": 30412345,
  "rule_15_verdict": "PASS | FAIL",
  "fallback_used": "none | notebooklm_web_ui | internal_approval_only",
  "ivan_cc_status_at_attempt": "up | down"
}
```

---

## Rules 1–14 (unchanged)

1. No agent names.
2. No calendar booking CTA.
3. ROI from their numbers only.
4. All customer-facing language through BIL.
5. Simplicity pitch in Segment 5.
6. Frame as ideas, not prescriptions.
7. Quality and reliability over speed.
8. Brand voice is built BEFORE launch — not learned over time.
9. Assume business excellence — always.
10. (v1.4) Podcast audio files = GitHub Pages ONLY.
11. (v1.4) E2E inbox click test required before delivery.
12. (v1.4.1) Podcast player speed controls — **1x · 1.25x · 1.5x** minimum (Bennett listens at 1.5x).
13. (v1.4) Send podcast links to bennett@ + madison@ after generation — **now conditional on Rule 15 PASS**.
14. (v1.4) This skill owns the segment structure.

---

## Anti-Patterns added in v1.5

- **Shipping a `.md` source doc URL as the Listen-tab href because Ivan-CC SSH is down** (-5) — fallback is NotebookLM web UI or INTERNAL APPROVAL ONLY, never source doc to lead.
- **Marking podcast_status: ready without Rule 15 HEAD probe receipt** (-5)
- **Linking a Drive-view URL for the podcast** (-5) — Rule 10 (GitHub Pages only) carries forward and is reinforced by Rule 15.

---

## Coordination with blueprint-ai-skill v3.11

Stage 5.5 of master skill v3.11 checks `bennett-maxwell.github.io/fki-preview/blueprints/podcasts/[slug].mp3` HTTP 200 + Content-Type `audio/mpeg`. This skill's Rule 15 enforces the same at podcast-completion time. Defense in depth — both must pass before customer email ships.

---

## Version History

- **v1.5 (2026-05-25)**: Rule 15 added — audio-output verification (HEAD probe → audio/mpeg required). Source-doc fallback to lead permanently banned. Authored by Mack agent-A under Bennett autopilot directive 2026-05-25 19:19 MDT.
- v1.4.1 (2026-05-23): Rule 12 updated — 1.5x speed button required.
- v1.4 (2026-05-22): Segment structure unified, Rules 10–14 added.
- v1.3 (2026-05-19): 7-segment framework.

---

## Related artifacts (same-session)

- past-blueprint-failures-2026-05-25.md — Drive id `13wMuzgZQwD_LJpBJzTzv1w3fuKOu-loc`
- blueprint-ai-audit-SKILL-v1.7.md — Drive id `1A-9yQnn7ThFiEk5tXUA6LcLPPCqeV4VK` (Domain 10 D10-3 enforces the same at audit time)
- blueprint-ai-SKILL-v3.11.md — Drive id `1sjH46Xs5pmsAS1qEklqJVnD0li2CVnJW` (Stage 5.5 enforces the same at orchestration time)
