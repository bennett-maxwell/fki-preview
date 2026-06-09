# Blueprint AI Skill Patch Packet — Q7 Tailoring + Customer-View Approval Gate — 2026-06-04

## Why this patch exists
Bennett identified two recurring false-pass failures:
1. Qualifier Question 7 existed, but could fall back to generic options instead of using the actual customer Blueprint recommendations.
2. Bennett approval emails could be internal proof/status memos instead of the exact customer-view delivery email.

## Mandatory rule to add to Blueprint AI SKILL.md
Before any Bennett approval preview, external/customer send, or Diamond/completion claim:

1. The qualifier contact fields must be required: first name, last name, business name, email, phone.
2. The qualifier CTA must stay disabled until contact identity, consent, and all 8 qualifier questions are completed.
3. Question 7 must be tailored from the actual Blueprint recommendations/agents shown to that customer. Generic options are not acceptable unless they exactly match the customer-specific Blueprint.
4. Every customer-facing `qualify.html` CTA in the Blueprint HTML and delivery email must carry `lead`, `biz`, `src`, and `agents` query context.
5. The `agents` list should be extracted from the rendered Blueprint HTML first, then profile data as fallback.
6. Bennett approval preview must be the customer-view Stage 7 email body. Internal proof memos, audit summaries, Gatekeeper language, SHA/readback receipts, thread IDs, and Codex/proof-ledger language cannot count as approval preview.
7. Gatekeeper must fail if either the qualifier-context gate or the approval-email customer-view gate fails.
8. External/customer send remains blocked until Bennett explicitly approves and Gatekeeper is rerun with `external_send` in allowed actions.

## Repo implementation proof
Current repo: `/Users/temp/fki-preview`

New/updated gates:
- `scripts/blueprint_qualifier_context_gate.py`
- `scripts/blueprint_approval_email_gate.py`
- `scripts/blueprint_q7_agents.py`
- wired into `scripts/blueprint_gatekeeper_100.py`
- wired into `scripts/blueprint_factory_manifest.py`
- email builder uses rendered Blueprint agents for Q7 context

Mike Norton / Origins validated Q7 options:
- Speed-to-Lead Agent
- Client Onboarding Agent
- Proposal Generator
- Content Production Agent
- Client Health Monitor
- Admin Automation Agent

Proof receipts:
- `/Users/temp/fki-preview/audit-receipts/mike-norton-correction-20260603/continuation-20260604/qualifier-context-gate-20260604.json`
- `/Users/temp/fki-preview/audit-receipts/mike-norton-correction-20260603/continuation-20260604/approval-email-customer-view-gate-20260604.json`
- `/Users/temp/fki-preview/audit-receipts/mike-norton-correction-20260603/continuation-20260604/gatekeeper-after-q7-email-gates-20260604.json`
- Corrected Bennett-only preview Gmail thread/message: `19e9347a66f73e1d`

## Status boundary
This patch packet is a proposed Drive-canonical skill update. Do not claim the Drive `blueprint-ai-skill/SKILL.md` is permanently patched until the exact Drive `SKILL.md` is replaced and fetched back successfully.
