# Rare Breed Plumbing — Bountiful redesign (preview)

**Source URL audited:** https://www.callrarebreed.com/plumbing-services-bountiful-ut  
**Site type:** LOCAL_SERVICE  
**Status:** Local preview only · `noindex` · forms are inert (no production CRM)

## Open the site
```bash
cd ~/Desktop/rare-breed-bountiful-website
python3 -m http.server 8765
# then open http://127.0.0.1:8765/
```
Or open `index.html` directly in a browser.

## Pages
- `index.html` — Bountiful plumbing landing
- `services.html` — full service menu
- `about.html` — why Rare Breed
- `contact.html` — request form + NAP

## Brand lock
Colors from logo SVG + live CSS: navy `#001538`/`#002B4E`, blue `#007FA9`, cyan `#23B8E0`, orange `#F5821F`.  
Fonts: Teko + Inria Sans (live site).

## Audit / build receipts
- `receipts/audit.json` — website-audit-skill DEEP package
- `receipts/benchmark_matrix.json` — 20 analogs
- `receipts/csll-ledger.jsonl` — 10 CL rounds
- `receipts/visual-economy-canary.txt` — PASS
- `receipts/color-diamond-report.json`

## Protected / human open
- Production publish / DNS
- Wire form to live webhook + SMS opt-in legal copy
- Confirm Google review aggregate before star badge
