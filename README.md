# Blueprint AI Pipeline — fki-preview

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

## Key Rules
- CTA text MUST be "Apply to Work With Us" (not "Get Your AI Quote")
- Never send to leads without `--bennett-approved` flag
- Podcast must return HTTP 200 before delivery gate passes
- All podcast URLs → GitHub Pages (not Google Drive)
