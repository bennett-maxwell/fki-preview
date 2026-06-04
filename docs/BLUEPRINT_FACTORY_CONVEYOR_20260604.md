# Blueprint AI Factory Conveyor — No-Bypass Operating Spec

Purpose: make every Blueprint AI package repeatable at scale without letting a wrong, stale, or unaudited artifact reach Bennett or a prospect.

## Non-negotiable send locks

- Builder agents may generate artifacts only. They do not audit, preview, or send.
- Auditor agents read builder outputs and write receipts. They do not edit deliverables.
- Gatekeeper is the only lane that can mint a pass token.
- Bennett preview is blocked until Blueprint audit PASS, completion gate PASS, public readback PASS, and Gatekeeper score 100/Diamond PASS.
- External/customer send is blocked until a current Bennett approval receipt exists and the Gatekeeper token includes `external_send`.

## Stage conveyor

| Stage | Lane | Required receipt | Next-stage condition |
|---|---|---|---|
| 0 | Skill/control | `manifest.json.skills` | Drive skill IDs and modified times recorded |
| 1 | Intake | `input_snapshot` | identity, slug, business, email/contact source locked |
| 2 | Build | blueprint/email/podcast artifact paths | files exist, hashes recorded |
| 3 | Blueprint audit | `run_audit` | PASS, 100% |
| 4 | Public readback | `public_readback` | public URL 200 and public SHA equals local SHA |
| 5 | Production completion | `completion_gate` | PASS, 44/44 applicable or current total |
| 6 | Gatekeeper | `gatekeeper` + pass token | score 100, Diamond PASS, token verifies against exact hashes |
| 7 | Bennett preview | Gmail proof | to `bennett@franchiseki.com`, preview-only, no customer send |
| 8 | External send | approval receipt + external token | current Bennett approval + token includes `external_send` |
| 9 | Post-send | delivery integrity receipt | GHL/Gmail message readback and funnel proof |

## Sub-agent split

- Intake worker: source data only.
- Build worker: HTML/email/audio only.
- Audit worker A: format/content/D9 checks.
- Audit worker B: financial/numeric/checksum checks.
- Release auditor: public readback and cache-bust proof.
- CRM auditor: identity and repeat-submit proof, synthetic lane only unless approved.
- Gatekeeper auditor: final token and send-lock state.
- Approval lane: Bennett inbox only.

## 1000/day rule

Scale by batching deterministic local/public checks and queueing slow lanes separately. Do not scale by weakening gates. Failed packages recycle to the exact failed stage, not the whole workflow.
