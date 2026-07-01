# Blueprint Lead Sentinel

Always-on watcher that makes a missed Blueprint lead impossible.
Canonical source: `scripts/blueprint-lead-sentinel.py` (this repo).
Runtime copy (launchd cannot read ~/Desktop due to macOS TCC): `~/.openclaw/scripts/blueprint-lead-sentinel.py`.
Scheduler: `~/Library/LaunchAgents/com.madisonfki.blueprint-lead-sentinel.plist` (StartInterval **120s** + RunAtLoad; plist mirrored to `ops/launchd/`).

## Two-layer architecture (2026-07-01)
- **Layer 1 (real-time, server-side, primary):** form → Slack the instant a lead is created,
  no Mac needed. NOT YET LIVE — grant-gated. See `ops/relay-slack-patch.md`. Blocked because
  (a) the live form bypasses the relay and posts external-tracking directly to Advaita, and
  (b) the relay routes to MAIN + GHL workflow actions can't be edited via API. Needs a Slack
  Incoming Webhook + a decision on canonical ingestion path + GHL workflow-edit UI access.
- **Layer 2 (backstop, this Sentinel):** near-real-time poll (every 120s) of BOTH GHL accounts,
  multi-signal detection, durable outbox, 60-min delay alarm, daily heartbeat. WORKING.
  PROVEN end-to-end 2026-07-01: relay test lead (contactId Ymzvi5H8mOviUFWbostJ) submitted
  21:42:38Z → detected + queued 21:43:22Z (~44s) → posted to #ai-blueprint-leads
  (https://franchiseki.slack.com/archives/C0B3QCD9UD7/p1782942232167569) → 60-min clock armed
  → test contact deleted + verified gone (GET 400).

## Why it exists (Josh Jackson failure, 2026-06-30)
Josh (josh@exaltlife.co) landed in MAIN GHL with source="Bennett Call" + tag="blueprint ai lead".
The old n1 watcher + delay-watchdog keyed ONLY on source.startswith("blueprint_ai") -> missed him.
The GHL->Slack workflow keyed on the Advaita form -> stopped ~6/23. Nothing ran on a schedule.
Result: ~24h of total silence for a paying-pipeline lead.

## Detection (multi-signal, both accounts)
A contact matches if ANY: source startswith "blueprint_ai" | source == "external_form" |
any tag in TAG_SIGNALS (incl "blueprint ai lead") . Polls MAIN (14RD8...) + Advaita (GPCi3...).

## On a new lead
1. durable outbox + append-only event log  2. Slack #ai-blueprint-leads + DM Madison & Cody
3. best-effort SMS  4. start 60-min delivery-delay clock  5. kick build orchestrator.

## Delay + heartbeat
- Undelivered > 60 min -> PRODUCTION DELAY alert (once per state).
- Daily heartbeat "alive, N seen" -> silence == alarm. `--check-alive` exits 2 if stale.

## KNOWN BLOCKER (route to Kay/Ivan)
Headless autonomous Slack posting needs `SLACK_BOT_TOKEN` (MISSING from gateway.env).
Until granted, the launchd run DETECTS + queues the alert in the outbox durably, and a live
Claude session drains it (`--drain` -> post via Slack MCP -> `--mark-delivered-notif KEY`).
SMS also needs macOS Automation permission for the launchd context (currently -1743).
Gmail-draft + outbox + event-log fallbacks always fire, so a lead is never lost.
