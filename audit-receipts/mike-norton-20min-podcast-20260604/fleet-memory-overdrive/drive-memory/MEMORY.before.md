# Memory Index — Unified (auto-rebuilt by memory-hygiene.py v2)
# Durable-first (feedback/reference/user), then recent projects. Detail lives in topic files; keep hooks one line.
# bennett-rules.md / agents-roster.md / core-protocols.md are PROTECTED — not listed, never archived.

# Rebuilt 2026-06-04T09:20:47 · 771 active rows

- [stage-transition-plist-env-vars](feedback_stage_transition_plist_env_vars.md) — stage-transition-detector.py plist had no EnvironmentVariables block and used /usr/bin/python3 — fixed 2026-06-04
- [ghl-unassigned-leads-pipeline-level](feedback_ghl_unassigned_leads_pipeline_level.md) — GHL "unassigned leads" stat refers to pipeline-opportunity level, not contact.assignedTo — use per-stage GET endpoints to count
- [GHL /opportunities/search 422 fleet bug](feedback_ghl_opp_search_422_fleet.md) — GHL opportunities search endpoint returns 422 on all calls — use ghl_search_contacts instead
- [meta-spend-new-campaigns-day1](feedback_meta_spend_new_campaigns_day1.md) — Meta $0 spend report from polling file is NOT an outage if campaigns were created yesterday — confirmed 2026-06-04
- [blueprint-poller-sprint-board-fix](feedback_blueprint_poller_sprint_board_fix.md) — Blueprint batch-approve poller was querying deleted Notion DB (08c0525b) — fixed to Sprint Board (335cf551) with Status filter
- [feedback_qb_oauth_not_a_kay_gate_20260604](feedback_qb_oauth_not_a_kay_gate_20260604.md) — [REDACTED]
- [Pulse heartbeat timestamp format fix — no seconds in NOW_LABEL](feedback_pulse_heartbeat_fix_seconds.md) — pulse-ci-loop.sh NOW_LABEL had %S (seconds) causing gateway strptime failures; fixed 2026-06-03
- [feedback_recap_4_loops_end_of_thread](feedback_recap_4_loops_end_of_thread.md) — recap-skill 4 autonomous council loops fire END-OF-THREAD ONLY — not every response; 5-option footer fires every response
- [extra-push-recap-architecture](feedback_extra_push_recap_architecture.md) — Extra-push and recap 4-round council loops are sequential, not competing — canonical autonomy chain order
- [email-send-scrubber-data-attr-fix](feedback_email_send_scrubber_data_attr.md) — email-send.sh jargon scrubber was clobbering data-kpi HTML attributes, breaking Gate 8.
- [feedback_context_ceiling_v4_fix](feedback_context_ceiling_v4_fix.md) — Context ceiling crash root cause — threshold was 150K, sessions hit 260K and crashed. Fixed to 80K warn / 110K block with decision:block output and HANDOFF fla…
- [email-triage-launchagent-required](feedback_email_triage_launchagent_required.md) — email-triage.py had no LaunchAgent — was dark 7 days (May 27 to June 3, 2026). Root cause: script built but plist never created.
- [desktop-organizer-30min-sweep](feedback_desktop_organizer_root_cause.md) — desktop-organizer.sh runs every 30min via com.fki.desktop-cleanup-interval plist — sweeps AI-generated files to ~/Desktop/"Mack Claude Code"/
- [feedback_council_50_50_gating](feedback_council_50_50_gating.md) — council-skill 50/50 expand+break is gated on high-stakes questions only — not all council calls
- [FLEET-CONTEXT.md Mack DIY write via Ivan gog](feedback_fleet_context_mack_diy_write.md) — Mack can write FLEET-CONTEXT.md via Ivan SSH + gog when Leo is unresponsive >5min (autopilot HARD RULE 2)
- [gog-drive-mcp-pagesize-fix](gog_drive_mcp_fix.md) — MCP gdrive tools inject --page-size flag that gog v0.13.0 doesn't support; workaround is direct bash calls
- [feedback_diamond_manual_only](feedback_diamond_manual_only.md) — diamond-skill T1-T8 is manual invocation only — no stop-hook or auto-fire; recap-skill ledger check is the only enforcement layer
- [desktop-copy-ephemeral](feedback_desktop_copy_ephemeral.md) — Desktop files copied successfully (COPIED_OK + ls verified) then missing 7-14min later — subagent false-done detection caught this
- [gog drive upload --replace flag for in-place Drive file updates](feedback_gog_drive_replace_flag.md) — gog v0.12.0 supports --replace=<fileId> on upload to patch existing Drive files in-place
- [chrome-managed-policy-correct-fix](feedback_chrome_managed_policy_correct_fix.md) — Chrome camera/mic fix = Chrome Managed Policy JSON, NOT LaunchAgent. LaunchAgents create daemon bloat Bennett explicitly rejected.
- [autohandoff-circuit-breaker](feedback_autohandoff_circuit_breaker.md) — At 80% context (160K tokens), context-ceiling-guard.sh v2.0 forces handoff-skill + Slack DM to Bennett. Gatekeeper-verified 2026-06-02.
- [no-per-turn-context-injection](feedback_no_per_turn_context_injection.md) — Context injection hooks that fire on every turn (even at thresholds) are BANNED — they increase token burn and were explicitly removed. Bennett directive confi…
- [heygen-api-credits-zero-2026-06-02](feedback_heygen_api_credits_zero.md) — HeyGen API credits at $0 — renders fail with MOVIO_PAYMENT_INSUFFICIENT_CREDIT
- [charles-giunta-ic-prospect](feedback_charles_giunta_ic.md) — Charles Giunta IC prospect key facts for Call #2 prep
- [creatify-api-video-endpoint-broken](feedback_creatify_api_broken.md) — Creatify video creation API returns 404 — only personas endpoint works
- [GHL Mack PIT token scope limitation — opportunities/users 422](feedback_ghl_mack_pit_scope_422.md) — Mack's GHL PIT token cannot access opportunities/search or users/search endpoints (422 on all attempts). Only contacts/ and opportunities/pipelines work.
- [ic-franchise-overview-link-bug](feedback_ic_franchise_overview_link.md) — indyclover.franchiseki.com redirects to a calendar booking page — never use as franchise overview link. Use www.indyclover.com/franchising instead.
- [recap-skill-v9-council-enforce](feedback_recap_v9_council_enforce.md) — recap-skill v9.0 — mechanical council-execute enforcement (2026-06-02); self-audit threshold change
- [context-ceiling-prevention](feedback_context_ceiling_prevention.md) — Council-approved (4.15/5) prevention system for "Usage credits required for 1M context" freeze — 5 hooks/LaunchAgent built 2026-06-02
- [feedback_recap_inline_violation](feedback_recap_inline_violation.md) — recap-skill must always fire via Skill() tool — never write an inline recap block as a substitute. Stop hook enforces this mechanically.
- [remotion-fki-roi-dist-missing](feedback_remotion_fki_roi_dist_missing.md) — Remotion fki-roi-20260602 project renders fail — dist/cjs/index.js missing from node_modules
- [rustdesk-suppress-launchagent-pattern](feedback_rustdesk_suppress_launchagent_pattern.md) — How to permanently stop macOS apps (RustDesk, etc.) from auto-relaunching and popping up on close/minimize
- [chrome-site-permissions-meet](feedback_chrome_site_permissions_meet.md) — Chrome site permissions for camera/mic must be set at the Chrome level — macOS TCC ALLOW is not sufficient
- [overdrive-fast-path-rule](feedback_overdrive_fast_path_rule.md) — Overdrive must check state age before running full 30-item chain — fast-path if <2h old
- [feedback_synthflow_not_in_use](feedback_synthflow_not_in_use.md) — Synthflow is NOT in use at FKI — never surface as gate, task, or recommendation
- [meeting-runner-exists-on-mack](feedback_meeting_runner_exists_on_mack.md) — meeting-completion-runner.py EXISTS on Mack (skill v4.0 "MISSING" warning is stale); tracker DB 56574049 writable via gateway NOTION_TOKEN raw REST.
- [podcast-speed-control-player-permanent](feedback_podcast_speed_control_player_permanent.md) — Every team/training podcast must ship as a hosted speed-control player (1x/1.25x/1.5x/2x + resume) like the blueprint podcast — not just an MP3.
- [feedback_self_audit_catches_own_cycle_violations](feedback_self_audit_catches_own_cycle_violations.md) — "Self-audit caught revenue/automation declaration blocks missing from the same cycle that added the mandate — meta-violation caught in real time."
- [legal-session-gmail-evidence-pattern](feedback_legal_session_gmail_evidence.md) — Legal session meeting-completion should include Gmail evidence search — permanent pattern 2026-06-01
- [notebooklm-chrome-profile-fix](feedback_notebooklm_chrome_profile_fix.md) — NotebookLM cookie_bridge must use "Profile 1" not profile 4 — Profile 4 doesn't exist on Mack
- [team-podcast-cadence-daily](feedback_team_podcast_cadence_daily.md) — Team AI training podcast cadence — Monday long ~20min, Tue-Fri short 9-13min daily delta, auto-sent to the team via Mack LaunchAgent.
- [feedback-human-gate-cc-kay](feedback_human_gate_cc_kay.md) — Human gate briefing emails must CC kay@franchiseki.com — she needs visibility on all Bennett action items
- [feedback_mrr_tracker_log_bleed_fix](feedback_mrr_tracker_log_bleed_fix.md) — log() in bash subshells must redirect to stderr to avoid contaminating captured stdout variable values
- [gdrive-mirror-tcc-after-os-update](feedback_gdrive_mirror_tcc_after_os_update.md) — GDrive "synced folder is missing" (Downloads) after macOS 26.5 = lost FileProvider registration on Downloads. Real fix = Drive Prefs uncheck/recheck Downloads…
- [feedback_codex_documents_tcc](feedback_codex_documents_tcc.md) — Codex CLI app-server cannot read files from ~/Documents due to macOS TCC — fix is to move .codex-guard to home
- [feedback_blueprint_g28_href_before_percent](feedback_blueprint_g28_href_before_percent.md) — G28 gate bug — original pattern checked % then href, missed href-then-% format. Fixed 2026-05-28 in html-content-check.sh.
- [dq-stage-transition-dry-run-fix](feedback_dq_stage_transition_dry_run.md) — DQ automation and stage-transition both stuck in DRY-RUN since May 28 — fix is DRY_RUN=false env var in LaunchAgent plist
- [blueprint-generator-template-canonical](feedback_blueprint_generator_template_canonical.md) — blueprint-auto-generator.sh was using Brittney (wrong) as template — corrected to melissa-tash-srp.html (v2.3 canonical)
- [blueprint-pipeline-poller-is-dupe-engine-ungated](feedback_blueprint_pipeline_poller_is_dupe_engine_ungated.md) — com.advaita.blueprint-pipeline LaunchAgent fires every 15min and commits via git — it is the divergent-dupe engine. The pre-commit FLEET-GATE was non-functiona…
- [openclaw-config-canonical-clobber-archive](feedback_openclaw_config_canonical_clobber_archive.md) — Canonical openclaw config is /Users/temp/.openclaw/openclaw.json. ~80 stale backup/clobbered copies were archived 2026-05-30; .clobbered.* files prove a prior…
- [Apollo API Key + Instantly Mailbox — SUPERSEDED 2026-05-30](feedback_apollo_instantly_resolved.md) — SUPERSEDED — Apollo + Instantly keys are NOT resolved. Vault (canonical) shows Apollo STALE (Bennett gate) + Instantly EXPIRED (Kay gate). Do not claim outreac…
- [blueprint-send-ghl-token-export-fix](feedback_blueprint_send_ghl_token_export_fix.md) — FIXED 2026-05-30 — blueprint-send.sh line 16 now `export GHL_TOKEN=...`. Unexported var was empty in any child process/sub-script, silently blocking prospect d…
- [blueprint-5-delivered-rows-unverified-reconciliation](feedback_blueprint_5_delivered_rows_unverified_reconciliation.md) — One-time reconciliation — 5 blueprint-delivery-tracker rows marked 'delivered'/'sent' are UNVERIFIED; relabeled to 'sent_unverified' pending two-path receipt (…
- ["[SUPERSEDED 2026-05-13] gog-keyring password (Mack)"](feedback_gog_keyring_password.md) — "SUPERSEDED 2026-05-13 by feedback_gog_send_no_keyring_env.md. Do NOT set GOG_KEYRING_PASSWORD — it makes gog gmail send hang silently. Retained for history on…
- [angie-cron-missed-days](feedback_angie_cron_missed_days.md) — Angie audit cron missed 2+ days as of 2026-05-19. angie-audit-rate.json never initialized. Advaita Improvement Rate unmeasured.
- [blueprint-send-bug1-resolved](feedback_blueprint_send_bug1_unresolved.md) — RESOLVED 2026-05-22 — blueprint-send.sh BUG-001 (echo-only curl) fixed; real urllib POST now at lines 176-188. Delivery-to-prospect verification is a SEPARATE…
- [feedback_blueprint_12_permanent_fixes_20260528](feedback_blueprint_12_permanent_fixes_20260528.md) — 12 council-approved permanent fixes to Blueprint AI pipeline (2026-05-28, score 4.18/5.0). Any agent must apply these before building or shipping any Blueprint.
- [Cross-Session State Must Be Notion or Drive](feedback_cross_session_state_notion_drive_only.md) — Any state that must survive across sessions/machines/accounts = Notion or Drive ONLY. Local files die on handoff.
- [Blueprint delivery owned by Mack + Ivan, not Hyperagent](feedback_blueprint_delivery_mack_ivan.md) — Bennett correction 2026-05-18 — Hyperagent will NOT handle Blueprint delivery. Mack and Ivan own the full pipeline (generation, NotebookLM, email send).
- [Never hallucinate business data in Blueprints](feedback_never_hallucinate_business_data.md) — Bennett directive — never fabricate years in business, event counts, revenue ranges, locations, or specialties. Use only verified data from the lead or omit en…
- [Codi + Brent own lead flow](feedback_cody_brent_lead_flow_owners.md) — Cody Johnson and Brent own the current GHL lead assignment/qualification flow. Always communicate before changing lead automation. All changes must be non-dest…
- [Question Format for Bennett](feedback_question_format.md) — How to ask Bennett clarification questions — inline, plain language, no jargon, no toggle UI
- [Legal Gate Aging — Immediate DM to Bennett](feedback_legal_gate_aging_immediate_dm.md) — Legal gates that are PAST DUE require immediate DM to Bennett, not just digest entry
- [GHL 401 Self-Heal — Search Slack and Gmail First](feedback_ghl_401_self_heal_slack_gmail.md) — When GHL returns 401, search Slack and Gmail for Kay's latest pit- token before doing anything else. Never ask Bennett.
- [Calendly Booking — Use Google Calendar Direct](feedback_calendly_booking_pattern.md) — When asked to book via a Calendly link, use Google Calendar directly if Chrome MCP unavailable
- [feedback-angie-audit-30min-self-improve](feedback_angie_audit_30min_self_improve.md) — Angie must audit + self-improve every 30min via Pulse Trigger 24, not standalone crons
- [Cron rewriter on Mack — use LaunchAgents](feedback_cron_rewriter_use_launchd.md) — Mack crontab is managed by some external process; ad-hoc cron adds get reverted. Use LaunchAgents for new persistent ops.
- [Dashboard Cardinal Rule — click-throughs, not info](feedback_dashboard_cardinal_rule.md) — Bennett's design constraint for ALL dashboard/command-center work. Main pages stay minimal; details live behind clicks/expandables.
- [Legal Case 250905143 — personal, do not surface](feedback_legal_case_personal.md) — Bennett's personal legal matter. Never escalate, post, or share with any agent or board.
- [Cloudflare + GHL Domain Rule](reference_cloudflare_ghl_domain_rule.md) — DNS/domain management lives inside GHL — Cloudflare is transparent infrastructure Brent manages. FKI never touches CF directly.
- [state file domain-namespacing](feedback_state_file_domain_namespacing.md) — Autonomy-cycle state writes must go through ~/.openclaw/scripts/write-overdrive-state.sh to prevent parallel-session clobber
- [Human Gate False Gate Removals — Standard Pattern](feedback_human_gate_false_gate_removals.md) — Meta token, CMO Option A silence=approve, and auto-retry scheduled items are always false gates — never surface as human gates
- [blueprint-r23-delivery-unverifiable](feedback_blueprint_r23_delivery_unverifiable.md) — Court/Melissa R23 delivery receipts are unverifiable. GHL msgId cyjdYGn1WtEXL40YzgbI returns 400 Bad Request. Deliveries likely never occurred.
- [state-file-pattern](feedback_state_file_pattern.md) — Autonomy-loop skills (overdrive, ship-it, future) persist cycle state to ~/.openclaw/state/ and resume on next run. Pattern unlocks compounding autonomy.
- [feedback_sudo_command_newline_split](feedback_sudo_command_newline_split.md) — sudo commands with a newline in the middle split into two zsh commands — path becomes a separate command and fails with "permission denied"
- [Self-audit before business-audit](feedback_audit_order_self_before_business.md) — self-audit FIRST, business-audit SECOND. Wired into overdrive v3.3.
- [feedback_delivery_email_podcast_first](feedback_delivery_email_podcast_first.md) — "Delivery email: podcast FIRST (top), playbook second. Label = 'Your Personalized Podcast' + 'Listen to Your Personalized Podcast' button. Bennett directive 20…
- [CC click-through expansion rule](feedback_cc_clickthrough_only.md) — Bennett CC design constraint — no new content on main pages, only click-through expansions
- [Gates should use browser control not escalate](feedback_gates_use_browser_control.md) — UI-only GHL tasks and token re-auth are NOT Bennett gates — use Chrome MCP / browser control + DIY skill
- [LinkedIn li_at Cookie Expiry = Kay Task](feedback_linkedin_li_at_cookie_kay_task.md) — When LinkedIn LaunchAgents exit code 1 with "li_at expired (redirect loop)" — Chrome Profile 2 cookie refresh needed. Kay task, not GHL token issue.
- [gog gmail send has no --draft flag](feedback_gog_no_draft_flag.md) — gog gmail send does not support --draft; HUMAN-APPROVAL-SEND emails go to Desktop as HTML
- [feedback-never-ask-want-me-to](feedback_never_ask_want_me_to.md) — PERMANENT — Never ask "Want me to X?" when X is implied by prior directive. Execute immediately.
- [friction-reduction-pattern](feedback_friction_reduction_pattern.md) — Bennett-facing friction (Touch ID spam, Apple notification badges, login nags) gets fixed at the source + auto-runs at login via LaunchAgent. Never one-shot ma…
- [Skills are ONLY edited on Google Drive — never local cache](feedback_skills_always_drive.md) — Mandatory rule — all skill edits must happen on the Drive canonical path. Symlink fix permanently implemented 2026-04-24.
- [blueprint-stage0-ghl-field-fix](feedback_blueprint_stage0_ghl_field_fix.md) — Blueprint AI Stage 0 used invented GHL field names — fixed with real field IDs verified from location 14RD8KklxR9G4e0Rf7v2
- [GHL token mismatch — ghl.env stale vs gateway.env active](feedback_ghl_401_token_mismatch_pit82b3c74c.md) — ghl.env had [REDACTED] (stale), active token is [REDACTED] — caused all 6 LaunchAgents to 401
- [feedback_intake_form_additive_only](feedback_intake_form_additive_only.md) — Intake form changes must be additive only — Bennett "don't take away anything" directive
- [feedback_podcast_source_doc_format](feedback_podcast_source_doc_format.md) — Blueprint podcast source docs — Court+Melissa 5-7 section format is canonical, not a defect
- [Pre-delivery check apply grep must match button text](feedback_predelivery_check_apply_grep.md) — build-delivery-email.sh checks grep 'apply' but CTA must explicitly contain "apply" — verify button text matches before building
- [feedback-troubleshoot-first-then-diy](feedback_troubleshoot_first_then_diy.md) — Bennett rule — use troubleshoot-skill BEFORE any work, then DIY-skill, then council if routing unclear
- [blueprint-form-gate-required](feedback_blueprint_form_gate_required.md) — No blueprint work until lead fills out Blueprint AI intake form at blueprint.meetadvaita.com/apply
- [Tailscale preflight before any Ivan SSH](feedback_tailscale_preflight_before_ivan_ssh.md) — Before ANY SSH or Tailscale-IP operation to Ivan, check Tailscale status first. Never dispatch to Leo for tasks blocked only because Tailscale is stopped.
- [Cloudflare managed through GHL only](feedback_cloudflare_ghl_only.md) — FKI never logs into Cloudflare directly — all DNS/domain management is inside GHL which uses Cloudflare as backend infrastructure
- [Recap skill at end of every response](feedback_recap_at_end_of_every_response.md) — Bennett wants recap-skill output at the end of every response, not just at session close
- [Desktop Organization Policy (2026-05-16)](feedback_desktop_archive_policy.md) — Agent outputs go to ~/Desktop with date in filename. Auto-cleanup archives daily at 6am.
- [hyperagent-setup-skill is canonical source for employee CLAUDE.md](feedback_hyperagent_setup_skill_is_claude_md_source.md) — Employee Claude Code CLAUDE.md template lives in hyperagent-setup-skill Section B on Drive
- [blueprint-no-drive-links](feedback_blueprint_no_drive_links.md) — No drive.google.com links in Blueprint HTML or delivery emails — GitHub Pages only
- [Blueprint email requires podcast complete first](feedback_blueprint_no_email_before_podcast.md) — NEVER send blueprint delivery email to a lead until the podcast is already done and verified. Both deliverables must be ready before any email goes out.
- [iOS settings — verify path before directing Bennett](feedback_ios_settings_verify_before_directing.md) — Never give an iOS Settings path without confirming it exists on his iOS version first
- [Frozen Claude Code terminal cleanup pattern](feedback_frozen_terminal_cleanup_pattern.md) — How to identify and kill frozen Claude Code sessions — 0% CPU + high RAM = timed-out session
- [False Human Gate Pattern — Browser + API First](feedback_false_gate_pattern.md) — CRITICAL: Most gates labeled Bennett/Brent/Kay are FALSE gates. Exhaust 5-step waterfall before declaring any human gate. Root cause was diy-skill v2 staging n…
- [Blueprint self-audit 95% before delivery](feedback_blueprint_self_audit_95_before_delivery.md) — Self-audit score must be 95%+ before sending any Blueprint to Bennett for final delivery
- [Never Remind About Google Ads Billing](feedback_google_ads_billing.md) — Bennett explicitly said he will not act on Google Ads billing reminders — never surface this again
- [Chrome kill via workspace/scripts/machine-health.sh](feedback_chrome_kill_workspace_scripts.md) — workspace/scripts/machine-health.sh has a live Chrome tab killer that does NOT have the if-false guard. Caused Chrome to be killed every 5 min.
- [GHL Python urllib must include User-Agent header](feedback_ghl_python_user_agent.md) — Any Python urllib.request to services.leadconnectorhq.com that omits User-Agent gets silent 403 Forbidden. mapki_tag_router.py was missing UA on ghl_get/ghl_pu…
- [Onboarding docs — no cross-section step references](feedback_onboarding_doc_no_cross_references.md) — Never write "see Jenn's steps above" in Keith's section — breaks when read in isolation
- [Tiffany online — IP drift caveat](feedback_tiffany_offline.md) — Tiffany IS up (16 models). Stale memory said offline. Always use current Tailscale IP — MagicDNS hostname fails from curl.
- [Audit effectiveness depends on work-completion stage](feedback_audit_effectiveness_by_completion.md) — website-audit-skill outperforms when work <70% complete; self-audit-skill outperforms when work >70%. Use both, but expect different signal quality at each rou…
- [blueprint-website-section-removed](feedback_blueprint_must_include_website.md) — "SUPERSEDED 2026-05-22 — website/demo site section REMOVED from Blueprint pipeline per Bennett directive"
- [state writer uname guard for non-macOS port](feedback_state_writer_uname_guard.md) — write-overdrive-state.sh uses macOS-portable mkdir-lock; if ever ported to Linux/Windows, add uname guard
- [Bennett gate waterfall — exhaust AI before surfacing](feedback_bennett_gate_waterfall.md) — CRITICAL: Must try API → Chrome MCP → Playwright → Leo dispatch before any Bennett gate. Slack messages pre-authorized. Web UI forms are NOT Rule 2.
- [Advaita Rubric v2 Proactivity Tier Split](feedback_advaita_rubric_v2_proactivity.md) — Rubric Q6 NEW capability gate. Overdrive tier-split: ≥10 NEW / ≤15 MAINTAIN / ≤5 SUPPRESS.

# … +659 more memories on disk (not indexed; use mem-search). Index capped at 23KB (112 of 771 rows shown, durable-first).


## Blueprint AI v3.27 scale conveyor memory — 2026-06-04

- Canonical Drive `blueprint-ai-skill/SKILL.md` is now version `3.27`; file ID `1IzE-seDDaB1Tciik9mwBVrgQcb7FP7eH`; fetchback SHA `02de3ec9ca92ae25852db50670a4b148aaa3a8495aa560ee7ff67d049a6a6f30`.
- v3.27 requires Blueprint Scale Conveyor smoke proof before any agent claims Blueprint AI is production-scale or ready for 1000/day throughput.
- Required synthetic fixture is Billy Bob / Billy Bob Electric, electrician/electrical contractor, average customer value `$1000`, annual revenue `$2,000,000`, no external/customer send.
- Billy Bob scale-smoke result: Blueprint audit PASS `15/15`; completion gate PASS `36/36 applicable`; Gatekeeper local PASS score `100`; delivery email visual gate PASS; qualifier/Q7 context PASS with six actual electrical contractor agents; Conveyor 30 pre-Bennett PASS with `28 GREEN, 2 LOCKED_HUMAN_GATE, 0 RED`.
- Permanent repo fixes from the scale run: `scripts/blueprint_conveyor_30.py` now supports `scale_fixture=true` no-send receipts, `blueprints/TEMPLATE.html` fixed malformed top-nav `href=\"#apply\"`, and `scripts/roi-industry-config.json` maps `billy-bob-electric-20260604` to `home_services` so `$1000` is financially checked.
- External/customer sends remain blocked until Bennett approval plus an `external_send` Gatekeeper token; synthetic scale-smoke never counts as customer delivery.
- Proof row: `https://app.notion.com/p/374cf5514fd38116a10af88c504def54`; repo receipt folder: `/Users/temp/fki-preview/audit-receipts/blueprint-scale-permanent-20260604/`.

## Blueprint AI v3.27 Billy Bob final clean proof — 2026-06-04

The first Billy Bob v3.27 scale-smoke run passed structure but later CI/audit review found stale SaaS/CRM customer-view copy and a `$2,388` ROI value in the HTML. Final electrician-clean artifact corrected Billy Bob Electric to electrician/electrical contractor with `$1,000` average customer value and `$2,000,000` annual revenue.

Final receipt set in `/Users/temp/fki-preview`:
- `audit-receipts/billy-bob-electric-20260604/billy-bob-electric-20260604-run-audit.final-v327-electrician-clean2.txt` = PASS 15/15.
- `audit-receipts/billy-bob-electric-20260604/billy-bob-electric-20260604-financial-realism.final-v327-corrected.txt` = Billy Bob PASS with default 1000.
- `audit-receipts/billy-bob-electric-20260604/billy-bob-electric-20260604-completion-gate.final-v327-electrician-clean.json` = PASS 37/37 applicable.
- `audit-receipts/billy-bob-electric-20260604/billy-bob-electric-20260604-gatekeeper-local.final-v327-electrician-clean.json` = PASS score 100.
- `audit-receipts/billy-bob-electric-20260604/billy-bob-electric-20260604-conveyor-30-pre-bennett.final-v327-electrician-clean.json` = 28 GREEN, 2 LOCKED_HUMAN_GATE, 0 RED.

Permanent lesson: Blueprint AI v3.27 scale-smoke must include a visible customer-view stale-copy grep for wrong industry, wrong ACV, stale SaaS/CRM language, and Q7/agent tailoring before claiming green.
