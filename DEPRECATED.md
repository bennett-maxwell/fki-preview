# ⛔ DEPRECATED — DO NOT USE THIS PIPELINE (retired 2026-06-03)

This `fki-gen` repo was a **homegrown reimplementation** of Bennett's Blueprint AI pipeline.
It diverged from the canonical `blueprint-ai-skill` (Drive `15hlMdkl…`, v3.16) and on 2026-06-02
shipped a **non-standard delivery-email template** (podcast-first, table buttons, parameterized
links) to customers — different from what Bennett's skill produces. Madison caught it only because
Bennett emailed her his version of Austin/Iron Horse.

## Use the real skill instead
- Canonical skill: `~/.claude/skills/blueprint-ai-skill/` (SKILL.md + MANIFEST.json) → Drive `15hlMdkl…`.
- Page base: `brent-attaway-crmx.html` (Drive `1z5A_8Ol…`), NOT `blueprints/TEMPLATE.html`.
- Audit: `run-audit.py v2.2.1` (Drive `1tWH9z…`) + audit skill v2.3.0.
- A `UserPromptSubmit` hook (`~/.claude/hooks/blueprint-skill-freshness.sh`) now forces a
  Drive freshness check before any blueprint work.

Artifacts here (lead JSONs, podcasts, the reusable `ghl-pull-contact.py`) may still be referenced,
but **do not run `gen-blueprint.py` / `build-delivery-email.sh` to ship to customers.** Build through
the skill so output matches Bennett's standard.
