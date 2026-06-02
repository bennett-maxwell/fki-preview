# Task review local mistake/source ledger

- created_at_utc: 2026-06-02T15:11:03Z
- Mode: local repo/receipts scan before mutation; Notion search separately recorded in run log.

## podcast direct address — audit-receipts/autonomous-loop-20260602/avery-production-summary.json
- modified: 2026-06-02T14:10:07Z
- snippet: false, "path": "audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-production-46.json", "status": "BLOCKED" }, "production_47_podcast": { "detail": "PASS", "exists": true, "pass": true, "path": "audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-production-47.json", "status": "PASS" }, "production_48

## GHL repeat submit — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-closeout.json
- modified: 2026-06-02T14:10:07Z
- snippet: { "blocker": "Production closeout cannot pass until Drive registry, HighLevel readback, repeat-submit proof, and mobile render are verified.", "lead": "avery-martinez-costa-vida-20260601", "pass": false, "status": "BLOCKED", "ts": "2026-06-01T23:41:13.576230+00:00" }

## podcast direct address — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-gatekeeper-fail.json
- modified: 2026-06-02T14:55:56Z
- snippet: { "detail": "avery-martinez-costa-vida-20260601.mp3 10534182 bytes within window", "name": "production_audio_size", "pass": true }, { "detail": "direct-address audio receipt passed", "name": "production_audio_direct_address", "pass": true } ], "diamond": "FAIL", "failures": [ "visible_html_surface: ambiguous CTA copy: Apply", "completion_gate failed", "run-audit.

## gatekeeper failures — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-gatekeeper-local-output.json
- modified: 2026-06-02T14:10:07Z
- snippet: " [PASS] D9-18 tables border-collapse (or N/A)", " [PASS] D9-19 max-width container", " [PASS] D9-20 [RL] no off-brand accent leak", "", "FAILED: 0" ] } ], "diamond": "PASS", "failures": [], "html_path": "/Users/openclaw/fki-preview/blueprints/avery-martinez-costa-vida-20260601.html", "lead": "avery-martinez-costa-vida-20260601", "mode": "local", "receipt_di

## gatekeeper failures — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-gatekeeper-local.json
- modified: 2026-06-02T14:10:07Z
- snippet: " [PASS] D9-18 tables border-collapse (or N/A)", " [PASS] D9-19 max-width container", " [PASS] D9-20 [RL] no off-brand accent leak", "", "FAILED: 0" ] } ], "diamond": "PASS", "failures": [], "html_path": "/Users/openclaw/fki-preview/blueprints/avery-martinez-costa-vida-20260601.html", "lead": "avery-martinez-costa-vida-20260601", "mode": "local", "receipt_di

## podcast direct address — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-gatekeeper-production-output.json
- modified: 2026-06-02T14:10:07Z
- snippet: { "detail": "avery-martinez-costa-vida-20260601.mp3 10534182 bytes within window", "name": "production_audio_size", "pass": true }, { "detail": "direct-address audio receipt passed", "name": "production_audio_direct_address", "pass": true } ], "diamond": "FAIL", "failures": [ "completion_gate failed", "proof receipt missing or failing: avery-martinez-costa-vida-20260

## gatekeeper failures — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-mobile-render.json
- modified: 2026-06-02T14:10:07Z
- snippet: local Playwright is not installed and the browser wrapper did not expose a mobile viewport setter.", "lead": "avery-martinez-costa-vida-20260601", "pass": false, "status": "BLOCKED", "ts": "2026-06-01T23:41:13.576230+00:00" }

## gatekeeper failures — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-production-43.json
- modified: 2026-06-02T14:10:07Z
- snippet: safe replace-in-place or registry update tool was available in this thread.", "lead": "avery-martinez-costa-vida-20260601", "pass": false, "registry_file": "", "status": "BLOCKED", "ts": "2026-06-01T23:40:31.754254+00:00", "verified": false }

## gatekeeper failures — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-production-45.json
- modified: 2026-06-02T14:10:07Z
- snippet: rify exact contact or instant response.", "contact": {}, "conversation": {}, "exact_contact_count": null, "instant_response_verified": false, "pass": false, "status": "BLOCKED", "ts": "2026-06-01T23:31:30.443807+00:00" }

## GHL repeat submit — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-production-46.json
- modified: 2026-06-02T14:10:07Z
- snippet: { "blocker": "Repeat-submit same-contact proof requires authenticated HighLevel readback; connector returned 401 Reauthentication required.", "pass": false, "status": "BLOCKED", "ts": "2026-06-01T23:31:30.443807+00:00" }

## qualifier webhook/base64 — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-completion-gate.json
- modified: 2026-06-02T14:55:56Z
- snippet: : "10/10 (100%)", "pass": true, "failures": [] }, "Funnel": { "score": "9/10 (90%)", "pass": false, "failures": [ "#27: CTA points to qualify.html and avoids banned or ambiguous apply copy \u2014 Ambiguous CTA copy found: Apply" ] }, "Audio": { "score": "5/5 (100%)", "pass": true, "failures": [] }, "Proof": { "score": "N/A", "pass":

## qualifier webhook/base64 — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-completion-local-output.json
- modified: 2026-06-02T14:10:07Z
- snippet: not cited as new-lead proof", "pass": true, "severity": "warning", "detail": "OK" }, "26": { "desc": "Query params (lead=, biz=, src=) preserved in qualify.html CTAs", "pass": true, "severity": "major", "detail": "OK" }, "27": { "desc": "CTA points to qualify.html and avoids banned or ambiguous apply copy", "pass": true, "severity": "critical", "de

## qualifier webhook/base64 — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-email-click-test.json
- modified: 2026-06-02T14:10:07Z
- snippet: 260601.mp3", "http_code": 200, "pass": true }, { "content_type": "text/html; charset=utf-8", "href": "https://bennett-maxwell.github.io/fki-preview/qualify.html?lead=Avery+Martinez&biz=Costa+Vida&src=avery-martinez-costa-vida-20260601&utm_source=blueprint_email&utm_medium=email&utm_campaign=blueprint_delivery", "http_code": 200, "pass": true } ], "lead": "avery-martinez-costa-v

## podcast direct address — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-production-47.json
- modified: 2026-06-02T14:10:07Z
- snippet: { "audio": "podcasts/avery-martinez-costa-vida-20260601.mp3", "audio_sha256": "f13ab455538a5b49006e4e4a289a5decf8ff442191958664e74d9b146a3ffb31", "audio_size_bytes": 10534182, "banned_audio_phrases_found": [], "business_present": true, "content_type

## podcast direct address — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-public-http.json
- modified: 2026-06-02T14:10:07Z
- snippet: tes": 1024, "http_code": 200, "url": "https://bennett-maxwell.github.io/fki-preview/delivery-emails/avery-martinez-costa-vida-20260601-delivery-email.html" }, "podcast": { "content_length": "10534182", "content_type": "audio/mp3", "first_bytes": 1, "http_code": 200, "url": "https://bennett-maxwell.github.io/fki-preview/podcasts/avery-martinez-costa-vida-20260601.mp3" }

## public token — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-qualifier-flow.json
- modified: 2026-06-02T14:10:07Z
- snippet: gin could type text fields and click chips, but range controls did not move through the limited wrapper. Direct relay payload used the same form schema and returned HTTP 200.", "ghl_readback_blocker": "HighLevel connector returned 401 Reauthentication required.", "ghl_readback_verified": false, "lead": "avery-martinez-costa-vida-20260601", "pass": true, "public_qualify_http_200": true, "relay_mode": "created

## qualifier webhook/base64 — audit-receipts/avery-martinez-costa-vida-20260601/avery-martinez-costa-vida-20260601-qualifier-submit.json
- modified: 2026-06-02T14:10:07Z
- snippet: -test-20260601@franchiseki.com", "event_name": "blueprint_qualifier_submit", "firstName": "Avery", "first_deploy": "crm-auto", "form_version": "2026-05-27-identity-webhook-v1", "lastName": "Martinez", "lead_session_id": "advaita-codex-costa-vida-20260601-51fc75d1", "leads_per_sale": 4, "locationId": "14RD8KklxR9G4e0Rf7v2", "monthly_ad_spend": 12000, "monthly_leads": 2200, "note":

## qualifier webhook/base64 — audit-receipts/brent-attaway/brent-attaway-completion-gate.json
- modified: 2026-06-02T15:11:02Z
- snippet: not cited as new-lead proof", "pass": true, "severity": "warning", "detail": "OK" }, "26": { "desc": "Query params (lead=, biz=, src=) preserved in qualify.html CTAs", "pass": true, "severity": "major", "detail": "OK" }, "27": { "desc": "CTA points to qualify.html and avoids banned or ambiguous apply copy", "pass": true, "severity": "critical", "de

## qualifier webhook/base64 — audit-receipts/brent-attaway/brent-attaway-gatekeeper-fail.json
- modified: 2026-06-02T15:11:03Z
- snippet: INDUSTRY DEFAULT JS RESULT", "------------------------------------------------------------------------------", "brent-attaway crm_software 2388 0 PASS", "------------------------------------------------------------------------------", "FINANCIAL-REALISM: 1/1 pass red-line financial checks" ] }, { "name": "d9_render_inte

## podcast direct address — audit-receipts/brent-attaway/brent-attaway-production-47.json
- modified: 2026-06-02T14:10:32Z
- snippet: { "audio": "/Users/temp/fki-preview/podcasts/brent-attaway.mp3", "audio_sha256": "8cd000c03e27fadb2456c3a45093c5daa78870ced543f3e50869e20ddc875dc0", "audio_size_bytes": 14773949, "direct_address_audio_verified": false, "error": "speech_recognition unavailable: No module name

## qualifier webhook/base64 — audit-receipts/dave-wood/dave-wood-completion-gate.json
- modified: 2026-06-02T14:55:56Z
- snippet: : "10/10 (100%)", "pass": true, "failures": [] }, "Funnel": { "score": "9/10 (90%)", "pass": false, "failures": [ "#27: CTA points to qualify.html and avoids banned or ambiguous apply copy \u2014 Ambiguous CTA copy found: Apply" ] }, "Audio": { "score": "5/5 (100%)", "pass": true, "failures": [] }, "Proof": { "score": "N/A", "pass":

## podcast direct address — audit-receipts/dave-wood/dave-wood-gatekeeper-fail.json
- modified: 2026-06-02T14:55:56Z
- snippet: pass": false, "returncode": 1, "stderr_tail": [], "stdout_tail": [ "[FAIL] dave-wood: 8/14 (57%) RED-LINE FAIL: ['PF0-5_format3_dense_scroll_RL', 'D3-02_podcast_audio_direct_address_RL', 'D10-23_restaurant_copy_clean_RL', 'D4-09_podcast_source_funnel_clean_RL', 'D10-01_financial_realism_RL'] (FINANCIAL-REALISM: 0/1 pass red-line financial checks)", "", "Audit complete. History: /Us

## podcast direct address — audit-receipts/dave-wood/dave-wood-production-47.json
- modified: 2026-06-02T14:10:32Z
- snippet: { "audio": "/Users/temp/fki-preview/podcasts/dave-wood.mp3", "audio_sha256": "691094fc09f6b5a6cf36a1cab635b43d46a6c51be84d4a20c92058e0ac3d3a44", "audio_size_bytes": 20587970, "direct_address_audio_verified": false, "error": "speech_recognition unavailable: No module named 's

## qualifier webhook/base64 — audit-receipts/plumber-test-business-20260601/plumber-test-business-20260601-completion-gate.json
- modified: 2026-06-02T14:55:57Z
- snippet: not cited as new-lead proof", "pass": true, "severity": "warning", "detail": "OK" }, "26": { "desc": "Query params (lead=, biz=, src=) preserved in qualify.html CTAs", "pass": true, "severity": "major", "detail": "OK" }, "27": { "desc": "CTA points to qualify.html and avoids banned or ambiguous apply copy", "pass": true, "severity": "critical", "de

## podcast direct address — audit-receipts/plumber-test-business-20260601/plumber-test-business-20260601-gatekeeper-fail.json
- modified: 2026-06-02T14:55:57Z
- snippet: eturncode": 1, "stderr_tail": [], "stdout_tail": [ "[FAIL] plumber-test-business-20260601: 11/14 (79%) RED-LINE FAIL: ['PF0-5_format3_dense_scroll_RL', 'D3-02_podcast_audio_direct_address_RL', 'D10-22_home_services_copy_clean_RL'] (FINANCIAL-REALISM: 1/1 pass red-line financial checks)", "", "Audit complete. History: /Users/temp/.openclaw/logs/blueprint-audit-history.jsonl", "VER

## podcast direct address — audit-receipts/plumber-test-business-20260601/plumber-test-business-20260601-production-47.json
- modified: 2026-06-02T14:10:34Z
- snippet: { "audio": "/Users/temp/fki-preview/podcasts/plumber-test-business-20260601.mp3", "audio_sha256": "a301b0ae161c4651d01cdb7cc4c0cfee020f2f96fea2fc43adbf4f33cf478ccf", "audio_size_bytes": 14784931, "direct_address_audio_verified": false, "error": "speech_recognition unavailabl

## podcast direct address — audit-receipts/autonomous-loop-20260602/audit-stack-report.md
- modified: 2026-06-02T14:10:07Z
- snippet: ive Revenue declaration: The Costa Vida test can only support synthetic ROI modeling until verified customer data replaces assumptions. Automation declaration: Local page, email, podcast, qualifier relay, and audit gates work. CRM readback and repeat-submit automation remain blocked by HighLevel auth. Completion declaration: Not complete for production. Local preview only. ## Self-Audit Initial score: 2.4/5. Reason: the

## podcast direct address — audit-receipts/autonomous-loop-20260602/autonomous-loop-rounds.md
- modified: 2026-06-02T14:10:07Z
- snippet: ion claim, no pass token until #43, #45, #46, mobile render, closeout, and production Gatekeeper pass. ## Round 2 - Customer-Facing Cleanup Status: completed for page and email. Podcast MP3 regeneration remains blocked until production rerun. 1. Removed synthetic wording from blueprint meta description. 2. Replaced hero badge with customer-safe operating-plan wording. 3. Replaced hero paragraph with prospect-safe workflo

## gatekeeper failures — audit-receipts/autonomous-loop-20260602/ceo-email-draft.html
- modified: 2026-06-02T14:10:07Z
- snippet: t-weight:500;">(+2.6)</span></h1> <p style="margin:0;font-size:14px;color:#6E6E73;line-height:1.5;">Costa Vida local preview was hardened, but strict production send remains blocked.</p> </div> <div style="padding:24px 32px;background:#FFFFFF;border-top:1px solid #E5E5EA;"> <p style="margin:0 0 12px;font-size:11px;font-weight:700;color:#A1A1A6;letter-spacing:2px;text-transform:uppercase;">What got done</

## qualifier webhook/base64 — audit-receipts/autonomous-loop-20260602/council-50-50.md
- modified: 2026-06-02T14:10:07Z
- snippet: 3. Add mobile screenshot proof as a required artifact. 4. Add Drive registry readback proof with artifact hashes. 5. Add HighLevel contact exact-count proof. 6. Add repeat-submit duplicate-prevention proof. 7. Add instant-response conversation proof. 8. Add email click-through proof for every CTA. 9. Add podcast direct-address proof for the first 3 minutes. 10. Add full-transcript internal-language proof before customer send

## GHL repeat submit — audit-receipts/autonomous-loop-20260602/skill-inventory.json
- modified: 2026-06-02T14:10:07Z
- snippet: .notion.so/372cf5514fd38101ab1cd61446517f8e", "no_send_gate": { "active": true, "reason": "Strict production Gatekeeper is FAIL until Drive registry, HighLevel readback, repeat-submit, mobile render, and closeout are all verified." } }

## apply thank-you redirect — audit-receipts/chad-ramirez-summit-street-tacos-20260602/pre-mutation-repo-state.json
- modified: 2026-06-02T15:10:31Z
- snippet: "has_webhook": false, "contains_thank_you_apply": false, "contains_thank_you_blueprint": false, "looks_base64_start": true, "title": null }, "thank-you-apply.html": { "exists": true, "size": 16169, "sha256": "0dc7a26df66dae7bad19000751cb13f02de1bf7d5b54e93287c71ae2badaa4d1", "has_fetch": false, "has_webhook": false, "contains_thank_you_apply": false, "c

## apply thank-you redirect — audit-receipts/chad-ramirez-summit-street-tacos-20260602/pre-mutation-repo-state.md
- modified: 2026-06-02T15:10:31Z
- snippet: nt=True title=Get Your AI Blueprint — Advaita AI for Business - qualify.html: size=25896 base64=True fetch=False webhook=False thank_apply=False thank_blueprint=False title=None - thank-you-apply.html: size=16169 base64=False fetch=False webhook=False thank_apply=False thank_blueprint=False title=Application Received — Advaita AI Team Review · Franchise KI - thank-you-blueprint.html: size=3557 base64=False fetch=False webhook=False

## qualifier webhook/base64 — docs/BLUEPRINT-AI-HARD-GATES-20260601.md
- modified: 2026-06-02T14:10:07Z
- snippet: rant-drift rules are repo-enforced and documented here. The next Drive skill update should merge this file's rules into the canonical Drive `SKILL.md` in place, without creating a duplicate skill file.

## qualifier webhook/base64 — docs/BLUEPRINT-DELIVERY-RUNBOOK.md
- modified: 2026-05-30T18:26:32Z
- snippet: "/"money"/"autonomy"/"memory"), subject 10–120 chars with a number or action verb, plain English (no jargon: no LaunchAgent/plist/SSH/Diamond/ gatekeeper/UUID/msgId/token), no duplicate subject within 1h. - Send only after §4 passes for all 15 (pre-delivery 15/15, D9 15/15, live URLs 30/30 = 200). A gatekeeper run is not complete until a line is appended to `~/.openclaw/state/gatekeeper-ledger.jsonl`. `shipped:true` is i
