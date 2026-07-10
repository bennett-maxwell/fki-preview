# OVERRIDE — D2-02 (inline agent-card prompts) retired

**Date:** 2026-06-26
**Authorized by:** Madison Lanz ("Override now, I own it")
**Executed by:** Madison CC (Claude Code)
**Overrides:** Bennett Maxwell rule **D2-02** (2026-06-09) — "every agent card ships a copy-paste starter prompt >= ~900 chars."

## What changed
1. `scripts/gen-blueprint.py` — `_agent_prompt()` now returns `''`. The 6 agent
   squares are condensed to **icon + name + desc + outcome**. No inline prompt.
2. `scripts/blueprint_agent_prompt_quality_gate.py` — removed the hard
   requirement of **>= 6 inline `agent-prompt` cards**. Inline prompts are now
   optional (validated if present, not required).

## What did NOT change
- The **3 ready-to-use bot dropdown cards** (`prompt-card`) still ship the full
  operating prompts and are still required (>= 3, >= 1200 chars each).
- The canonical Drive template `brent-attaway-crmx.html` was already condensed
  (0 inline prompts) — no edit needed there.

## Rationale
Madison ruled the inline >=900-char prompt inside every square looks bad and
duplicates the 3 dropdown bots. Product intent: 6 condensed recommendation
squares + 3 ready-to-use bots (full prompt in the blue dropdown).

## Open item for Bennett
This reverses your 2026-06-09 D2-02 rule fleet-wide. If you want it reinstated,
restore the inline block in `_agent_prompt()` and the `< 6` check in the gate
(both marked with `OVERRIDE 2026-06-26` comments).

## Separate pre-existing issue (NOT addressed here)
The 3 dropdown prompts on Garlon/Sky fail the gate for missing `output` /
`first_run_test` sections — a profile-content problem (tied to the production-47
false-pass), independent of this override.
