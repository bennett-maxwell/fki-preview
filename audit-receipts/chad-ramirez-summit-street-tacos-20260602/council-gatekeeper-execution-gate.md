# Council + Gatekeeper execution gate
- created_at_utc: 2026-06-02T15:11:33Z

Council average: 4.6 / 5
Council decision: APPROVED_TO_EXECUTE_WITH_GATES
Gatekeeper status: YELLOW_UNTIL_PREFLIGHT_FIXED
Gatekeeper decision: PROCEED_TO_FIX_PREFLIGHT_ONLY

## Advisor scores
- Funnel QA: 4.7 — Approve with mandatory local and public preflight before customer-path submission. Fix apply redirect and restore qualify webhook first.
- CRM/GHL Integrity: 4.4 — Approve, but mark CRM proof partial until HighLevel auth returns or a safe authenticated readback script proves exact one contact.
- Blueprint Quality/Audit: 4.6 — Approve only if no Bennett preview is sent until blueprint-audit 100/100 plus podcast direct-address receipts pass.
- Skill Repeatability: 4.5 — Approve. Patch runbook after execution proof; if Drive replace/fetchback is unavailable, produce patch proposal and label Drive partial.
- Protected Sends/Legal: 4.8 — Approve internal Bennett preview only; external fake-prospect/customer send remains blocked without separate Bennett approval.

## Red lines
- Public secrets: must pass grep/no direct GHL token before publish
- Customer path: apply must redirect to thank-you-apply; qualify must post before booking
- GHL identity: same Chad email/phone, exact contact count 1 if GHL auth available
- Podcast: direct-address opening to Chad/Summit, no source-material framing, speed controls
- Send boundary: Bennett preview only after 100 gate; external sends blocked
- Skill patch: Drive patch requires fetchback; otherwise patch proposal only