# Blueprint AI Skill Patch Packet — Conveyor 30 + Email Visual Gate — 2026-06-04

## Required permanent Blueprint AI skill change
Blueprint AI must no longer run as one broad task. It must run as a 30-step conveyor where each step has a worker output, an auditor/gate, and a receipt.

## Greenlight rule
- Steps 01-28 must be GREEN before Bennett sees approval preview.
- Step 29 is Bennett-only preview send and must prove the preview receipt email SHA matches the current customer-view delivery email artifact.
- Step 30 is external/customer send and remains LOCKED_HUMAN_GATE until Bennett approval plus a Gatekeeper token with `external_send`.

## New critical step
Step 23: Delivery email visual format.
This is now a hard gate. It must prove:
- customer-view subject/body,
- no internal proof/Codex/Gatekeeper language,
- `<!DOCTYPE html>` at top with no metadata comments before it,
- card styling with border/depth,
- button styling,
- exactly one qualify CTA,
- Q7 agents context,
- render/screenshot receipt when available.

## Repo implementation
Current repo: `/Users/temp/fki-preview`

New files:
- `docs/BLUEPRINT_CONVEYOR_30_20260604.md`
- `scripts/blueprint_conveyor_30.py`
- `scripts/blueprint_email_visual_gate.py`

Updated files:
- `templates/delivery-email-template.html`
- `scripts/build-delivery-email.sh`
- `scripts/blueprint_gatekeeper_100.py`
- `scripts/blueprint_factory_manifest.py`

## Current proof
Mike Norton / Origins conveyor result:
- Steps 01-29 GREEN
- Step 30 LOCKED_HUMAN_GATE
- Red 0
- Corrected Bennett-only preview Gmail thread/message `19e9360eef345ae4`
- Email visual screenshot SHA `a2ad605d81a283e653d271640e13975f552bc4fea0b71207a4d5aede5e8b4420`

## Boundary
This is a patch packet. Do not claim the canonical Drive `blueprint-ai-skill/SKILL.md` is fully replaced until the Drive SKILL.md is replaced and fetched back.
