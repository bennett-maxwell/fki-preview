# Blueprint AI 14-Day Revenue Validation

Created: 20260527T224740Z

## Validation Question

Does the fixed Blueprint AI funnel create revenue behavior, not activity?

## Required Live Metrics

| Metric | Target | Proof source |
|---|---:|---|
| Blueprints delivered to real prospects | 12 | Delivery log / Gmail / Notion |
| Qualifier submissions tied to same GHL contact | 8 | GHL contact notes/tags |
| Qualified bookings | 4 | GHL calendar appointments |
| Showed calls | 3 | Calendar/GHL outcome |
| Revenue-stage opportunities | 1 | GHL pipeline |
| Duplicate contacts caused by the funnel | 0 | GHL duplicate audit |

## Daily Check

Run:

```bash
./scripts/blueprint-funnel-monitor.sh
./scripts/blueprint-release-gate.sh --allow-dirty
./scripts/blueprint-link-audit.sh
./scripts/blueprint-funnel-dashboard.sh
```

## Decision Rule

- Persevere if tracking is clean and at least 4 qualified bookings appear from 12 delivered blueprints.
- Fix/pause if duplicates, untracked qualifier submits, or unattached appointments appear.
- Pivot offer or audience only after tracking is clean and conversion is still below target.
