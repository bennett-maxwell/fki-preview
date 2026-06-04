# Blueprint Hosting — GHL/Cloudflare Migration Note — 2026-06-04

## Current state
- Blueprint deliverables in this repo are currently published from GitHub Pages at `https://bennett-maxwell.github.io/fki-preview/`.
- The current Drive `blueprint-ai-skill` and repo scripts still hardcode GitHub Pages in generation, delivery, and proof commands.
- The qualifier itself posts into GHL through the relay at `https://blueprint-ghl-relay.vercel.app/api/blueprint-lead`; the static page host is separate from GHL CRM submission.

## Why Mike Norton was not on GHL/Cloudflare
- The pipeline inherited the GitHub Pages host from the existing Blueprint system.
- No GHL website/page publish API was available in this Codex session: the HighLevel connector returned `401 reauthentication required`.
- No Cloudflare/Wrangler config or CLI exists in `/Users/temp/fki-preview`, so there is no current Cloudflare Pages project to deploy this static package from this repo.

## Required migration gate
Before claiming a Blueprint is hosted on GHL/Cloudflare:
1. Reauthenticate HighLevel or provide the exact GHL Site/Funnel/Page target.
2. Decide canonical host: GHL Site/Funnel path, Cloudflare Pages, or GHL custom domain behind Cloudflare.
3. Replace hardcoded `https://bennett-maxwell.github.io/fki-preview` in generator/profile/delivery scripts with a single configurable `BLUEPRINT_BASE_URL`.
4. Run `blueprint_qualify_link_gate.py --check-http` against the final public host.
5. Run Gatekeeper 100 and factory manifest after the final host is live.

## Current status
`GHL partial`: GitHub Pages copy is fixed and verified; GHL/Cloudflare production hosting cannot be claimed until HighLevel auth/target and Cloudflare deployment config are available.
