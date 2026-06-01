# Blueprint AI Repeatability Save Receipt - 2026-06-01

Status: saved locally in repo code, docs, hooks, regression tests, and the local cached audit skill.

What was saved:

- Format-3 dense-scroll gate is wired as a red-line in `run-audit.py`.
- Restaurant/food-franchise drift gate is wired as a red-line in `run-audit.py`.
- Home-services drift gate now blocks SaaS/demo/proposal/onboarding leftovers.
- Podcast source generation no longer emits the old `NOTEBOOKLM SOURCE DOCUMENT`, `Source:`, `Sources and Citations`, old apply URL, or `first 90 days` language.
- Direct podcast audio audit blocks source-material framing, third-person framing, and known ASR artifacts.
- Local audio audit no longer blocks first deploy on a public URL that cannot exist until after push; production receipt #47 verifies public HTTP 200.
- Local `.git/hooks` were reinstalled from `scripts/git-hooks` via `scripts/hooks/install-hooks.sh`.
- Local cached `blueprint-ai-audit-skill/SKILL.md` is patched to v2.9 with Format-3-only, direct-address podcast, restaurant/QSR drift, and local-first/public-production audio rules.

Proof commands run:

```bash
python3 -m py_compile run-audit.py scripts/generate-podcast.py scripts/podcast_direct_address_audit.py tests/test_blueprint_regressions.py
bash scripts/hooks/install-hooks.sh
```

Drive status:

- Drive was searched first.
- Canonical Drive `blueprint-ai-audit-skill/SKILL.md` exists at file ID `1Wp7zzDlp4uzeEX8vTIQv0_RsJp70ORLM`.
- Connector metadata read succeeded. Replace-in-place did not run because the authenticated Drive CLI is not available and the connected Drive app in this thread exposes read/import tools, not safe same-file replacement.
- This receipt plus `docs/BLUEPRINT-AI-HARD-GATES-20260601.md` are the local handoff until the canonical Drive `SKILL.md` is patched in place.

Active Notion task:

https://www.notion.so/372cf5514fd38101ab1cd61446517f8e
