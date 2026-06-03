# Blueprint AI Pipeline — fki-preview

[![blueprint-audit](https://github.com/bennett-maxwell/fki-preview/actions/workflows/blueprint-audit.yml/badge.svg)](https://github.com/bennett-maxwell/fki-preview/actions/workflows/blueprint-audit.yml)

Personalized AI transformation blueprints for Advaita lead acquisition.

## Live Assets
- **Pipeline Status**: https://bennett-maxwell.github.io/fki-preview/pipeline-status.html
- **Apply Quiz**: https://bennett-maxwell.github.io/fki-preview/apply/
- **Blueprints**: `blueprints/<slug>.html` — 10 leads, all live

## Architecture

```
GHL Form Submit
      ↓
Webhook → Ivan :8080 (openclaws-imac.tail503ee0.ts.net)
      ↓
lead-intake.sh → scrape website → generate blueprint HTML
      ↓
generate podcast via NotebookLM → push MP3 to podcasts/
      ↓
git push → GitHub Pages (auto-deploy)
      ↓
build-delivery-email.sh → send preview to bennett@franchiseki.com
      ↓
Bennett APPROVE → send-approved.sh --all --bennett-approved → GHL delivery
```

## Scripts
| Script | Purpose |
|---|---|
| `lead-intake.sh` | Full pipeline for a new lead |
| `blueprint-batch.sh` | Batch process multiple leads |
| `validate-delivery-ready.sh` | Pre-delivery checks (podcast, CTA, apply_url) |
| `send-approved.sh` | Batch deliver after Bennett approval |
| `gen-paul-muus-podcast.sh` | One-click Paul Muus podcast |
| `nightly-podcast-health-check.sh` | 2AM health check (LaunchAgent) |

## Quality Gates
The blueprint grader (`run-audit.py`) is protected by a layered tripwire system:
- **Regression suite** — `tests/test_blueprint_regressions.py` (17 stdlib-only invariants). Each pins a real fixed defect, including the 0/0-false-PASS resolver killer (#16) and the audit_lead non-zero-check-count guard (#17). Run: `python3 tests/test_blueprint_regressions.py`.
- **CI gate** — `.github/workflows/blueprint-audit.yml` runs the suite on every push to `main` + PRs touching `blueprints/`, `run-audit.py`, `scripts/`, or `tests/`. Status badge is at the top of this README.
- **Nightly health** — `~/.openclaw/bin/blueprint-daily-health.sh` (LaunchAgent `com.fki.blueprint-daily-health`, 8am) runs the suite locally to catch out-of-git drift CI can't see, then posts a PASS/FAIL receipt to Slack `#leo-coaches` (`C0AQ4KB1SA0`).

## Key Rules
- CTA text MUST be "Apply to Work With Us" (not "Get Your AI Quote")
- Never send to leads without `--bennett-approved` flag
- Podcast must return HTTP 200 before delivery gate passes
- All podcast URLs → GitHub Pages (not Google Drive)
