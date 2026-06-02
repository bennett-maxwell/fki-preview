# Council 50/50 Receipt

Scope: Blueprint AI Costa Vida synthetic A-Z test.
Mode: AUDIT_ONLY for protected actions. Reversible local fixes only.
Verdict: NO-GO for external send. Continue local hardening only.

## Council Options 1-5

1. Contrarian: 2.1/5. Main risk: local pass being mistaken for production pass.
2. Financial/ROI: 2.0/5. Main risk: synthetic ROI copy sounding like real Costa Vida data.
3. Automation/Technical: 3.2/5. Main risk: GHL, Drive, repeat-submit, and mobile proof gaps.
4. Customer/UX: 3.1/5. Main risk: internal test language and repeated copy weakening trust.
5. Executor/Ops: 2.6/5. Main risk: handoff, proof link, and dirty git staging errors.

## Top 10 Council Fixes Applied

1. Added `scripts/blueprint_production_summary.py`.
2. Added `strict_production_ready`, `external_send_allowed`, and `no_send` split.
3. Added schema validators for Drive registry, HighLevel readback, and repeat-submit.
4. Saved refreshed production summary receipt.
5. Added regression test for the no-send production summary guard.
6. Removed internal/synthetic page labels from the Costa Vida blueprint.
7. Replaced internal agent chips with prospect-safe labels.
8. Corrected delivery email language around editable assumptions.
9. Cleaned the podcast source brief so it no longer includes customer-send approval language.
10. Hardened podcast audit banned patterns for internal approval and Gatekeeper language.

## 50 Expansion Ideas

1. Add one production-readiness receipt index per lead.
2. Add a per-lead public URL health receipt.
3. Add mobile screenshot proof as a required artifact.
4. Add Drive registry readback proof with artifact hashes.
5. Add HighLevel contact exact-count proof.
6. Add repeat-submit duplicate-prevention proof.
7. Add instant-response conversation proof.
8. Add email click-through proof for every CTA.
9. Add podcast direct-address proof for the first 3 minutes.
10. Add full-transcript internal-language proof before customer send.
11. Add customer-facing copy scan for internal terms.
12. Add synthetic-data disclaimer enforcement for test leads.
13. Add real-data-only copy enforcement for live leads.
14. Add industry drift scan for plumber, SaaS, and home-service leftovers.
15. Add food-franchise vocabulary threshold for restaurant leads.
16. Add Format-3 exact-section-order proof.
17. Add top-right navigation proof.
18. Add no old tab CSS proof.
19. Add no unresolved template token proof.
20. Add no Drive or Notion customer-facing URL proof.
21. Add proof that qualification links preserve lead, biz, and source query params.
22. Add proof that the qualifier form asks no redundant questions.
23. Add proof that qualifying ROI threshold shows Bennett booking only after fit.
24. Add proof that booking link does not bypass qualification.
25. Add a production-ready field that is false by default.
26. Add explicit no-send status in every handoff.
27. Add exact next physical action per external blocker.
28. Add an artifact hash table per handoff.
29. Add a Notion proof link property update at closeout.
30. Add a local receipt when Notion property updates are blocked.
31. Add commit-scoped staging instructions for dirty worktrees.
32. Add a guard against broad `git add -A` during Blueprint closeout.
33. Add lead profile/source hash into the Gatekeeper token.
34. Add delivery email hash into the Gatekeeper token.
35. Add podcast MP3 hash into the Gatekeeper token.
36. Add public URL hash/size readback for podcast.
37. Add player UX checks for chapter count and speed controls.
38. Add audio banned-phrase checks beyond NotebookLM source framing.
39. Add "Bennett preview only" versus "external send approved" split.
40. Add CEO email draft only when production is blocked.
41. Add Q&A decision row only when Bennett input is truly required.
42. Add regression test for local versus production status separation.
43. Add overdrive receipt that lists reversible actions only.
44. Add business-audit receipt that separates revenue, automation, and consolidation.
45. Add lean-startup receipt with exactly 5 next actions.
46. Add autonomous-loop receipt with 10 concrete improvements per round.
47. Add a customer-facing copy de-duplication pass.
48. Add a public proof dashboard for passed versus blocked gates.
49. Add Drive canonical skill pointer to repo-local hard gates.
50. Add a scale-readiness checklist before running the next 1000 leads.

## 50 Premortem Failure Modes

1. Agent claims local 100% while production Gatekeeper is failing.
2. Agent sends customer email before strict production proof exists.
3. Agent mistakes Bennett preview approval for customer-send approval.
4. Agent treats relay HTTP 200 as HighLevel CRM proof.
5. Agent does not verify exact contact count in HighLevel.
6. Agent creates duplicate contacts on repeat submit.
7. Agent misses missing conversation or instant response proof.
8. Agent skips Drive artifact registry readback.
9. Agent records a Drive registry file name without verified=true.
10. Agent skips mobile render proof.
11. Agent treats D9 mobile CSS as a real mobile screenshot.
12. Agent says podcast works while source-material framing is present.
13. Agent says podcast works while internal approval language is spoken.
14. Agent leaves "Bennett preview" visible to the prospect.
15. Agent leaves "synthetic fresh run" visible to the prospect.
16. Agent says "real numbers" for a synthetic test.
17. Agent says "actual business" without verified customer data.
18. Agent reintroduces old middle tabs or tab panels.
19. Agent reintroduces Format-4 or Format-5 references.
20. Agent reintroduces plumber or SaaS workflows for a restaurant lead.
21. Agent leaves IN, OUT, or T chips visible as internal labels.
22. Agent repeats long generic paragraphs to inflate density.
23. Agent uses a public Drive or Notion URL in customer-facing HTML.
24. Agent leaves unresolved `{{token}}` fields.
25. Agent leaves dead nav anchors.
26. Agent lets the Apply CTA bypass the qualifier.
27. Agent loses lead, business, or source query params.
28. Agent changes qualification questions without retesting CRM payload.
29. Agent sends CEO closeout as customer delivery email.
30. Agent sends customer email with CEO email design.
31. Agent writes a polished handoff that hides blockers.
32. Agent sets Notion status Green while proof link is blank.
33. Agent commits unrelated plumber or Brent changes.
34. Agent reverts user changes while trying to clean the tree.
35. Agent reruns generation and overwrites approved Format-3 styling.
36. Agent changes the MP3 without updating hash receipts.
37. Agent changes HTML after completion receipt and does not rerun gates.
38. Agent changes email after click test and does not retest links.
39. Agent accepts skipped rows as pass rows.
40. Agent counts planned fixes as completed proof.
41. Agent records a production token when blocker receipts are still blocked.
42. Agent fails to separate public preview from external delivery.
43. Agent uses broad cleanup or delete operations without Bennett approval.
44. Agent relies on stale memory over Drive skill instructions.
45. Agent ignores Notion project state for multi-step work.
46. Agent fails to update the handoff after new blockers appear.
47. Agent does not cite exact file paths for future pickup.
48. Agent lets synthetic assumptions become ROI claims.
49. Agent scales to batch work before the first A-Z run is production-clean.
50. Agent closes the thread without a no-send or blocker receipt.
