# Blueprint AI Skill Patch Packet — No-Bypass Conveyor — 2026-06-04

Canonical request: Bennett asked that Blueprint AI be broken into sub-agent stages so each stage is verified before moving forward, and so no package reaches human approval until Blueprint audit passes.

## Patch to apply to blueprint-ai-skill/SKILL.md

Add this as the Stage 0 / Gatekeeper section before the existing pipeline:

1. Each Blueprint run creates `audit-receipts/<slug>/<slug>-factory-manifest.json`.
2. Builder agents produce only artifacts. Builder agents cannot audit, preview, or send.
3. Auditor agents read artifacts and write receipts only. Auditor agents cannot edit deliverables.
4. Stage advancement requires a machine-readable `pass=true` receipt for the previous stage.
5. Podcast production-47 must include: `pass=true`, `http_code=200`, `size_download`, `audio_sha256`, `public_sha256`, `direct_address_audio_verified=true`, `opening_direct_address_verified=true`, `opening_exact_or_close=true`, zero banned source-material phrases, zero third-person prospect patterns, and `you_your_count>=5`.
6. Gatekeeper token must verify against exact current artifact hashes: blueprint HTML, delivery email, lead profile, and production-47.
7. Bennett preview is allowed only when the factory manifest status is `PASS_PREVIEW_ONLY` or `PASS_EXTERNAL_SEND_ALLOWED`.
8. External/customer send is allowed only when factory manifest status is `PASS_EXTERNAL_SEND_ALLOWED` and token `allowed_actions` contains `external_send`.
9. A CLI flag such as `--bennett-approved` is never approval proof. External send requires a current approval receipt: `<slug>-bennett-approval.json` with `bennett_approved=true` and `external_customer_send_approved=true`.
10. Failed packages recycle to the exact failed stage and may not continue forward.

## Local implementation committed

Repo: bennett-maxwell/fki-preview
Commit: `35ce3c12101e583ea78d3cea0374650e29e0358c`

Files:
- `/Users/temp/fki-preview/docs/BLUEPRINT_FACTORY_CONVEYOR_20260604.md`
- `/Users/temp/fki-preview/scripts/blueprint_factory_manifest.py`
- `/Users/temp/fki-preview/scripts/send-approved.sh`
- `/Users/temp/fki-preview/audit-receipts/mike-norton-origins-20260603/mike-norton-origins-20260603-factory-manifest.json`

## Mike Norton current proof

- Gmail thread: `19e8f6f7ecefefe8`
- Latest Bennett inbox packet: `19e92f5e3f446355`
- Public podcast: `https://bennett-maxwell.github.io/fki-preview/podcasts/mike-norton-origins-20260603.mp3?v=cda0fc8f`
- Public podcast SHA: `cda0fc8f11dc9381e75f1928e73d6d5293f1cec7b23829e7aa3c7944f98f7f3a`
- Factory manifest: `PASS_PREVIEW_ONLY`
- External send: locked until Bennett approval receipt + external_send token.
