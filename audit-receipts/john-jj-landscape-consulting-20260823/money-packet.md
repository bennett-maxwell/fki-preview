who: John — JJ Landscape Consulting (GHL XISYqIALiQNCN5ALbDFf, Advaita loc GPCi3FrWJCyevcGzZgTT)
brand: Blueprint
$impact_proxy: pipeline — 1 inbound Blueprint form-fill (30 leads/mo, $1M–$3M revenue band, team 5)
metric_lever: Blueprint delivered -> tracked qualifier completion -> booked call
next_3_actions: (1) Madison decides duplicate-send question vs 8/16 delivery; (2) audit-gate 100% + mint send token; (3) Gmail draft to johnj@jjlandscapeconsulting.com for her review+send
delivery_state: draft_only
fdd_claims_status: safe

## What shipped
- Page: blueprints/john-jj-landscape-consulting-20260823.html (commit 48036d4b0, pushed to main)
- Profile: leads/john-jj-landscape-consulting-20260823.json (13/13 form fields, zero invented values)
- Podcast: NotebookLM nb b18eb35e / artifact 7a4ab3db (native SHORT, rendering)

## Duplicate-business flag (human decision)
Contact AGnfKf0wM1sDrFBBq14S (John Joestgen, same company JJLC, same domain) was
blueprint-delivered 2026-08-16 with materially different answers (Jobber/50 leads/team 30/
efficiency vs ServiceTitan/30 leads/team 5/scale). CRMX strict dedupe does not block, because
this is a different contact id. Second delivery to the same business is a send decision.

## Expansion seeds (5)
1. next_artifact: CRMX dedupe-by-business rule (match on companyName+domain, not contact id) | owner_agent: Madison CC | success_metric: zero duplicate blueprint sends to one business | revenue_link: protects sender reputation on warm inbound
2. next_artifact: stale-Pages-deploy alarm (corky 8/17 page 404s on hub today) | owner_agent: Madison CC | success_metric: every delivered blueprint URL 200 within 15m of push | revenue_link: a 404 blueprint kills the qualifier funnel silently
3. next_artifact: same-ID Drive patch to blueprint-ai-skill Stage 6.5 replacing gatekeeper-100 with audit-gate.sh | owner_agent: Madison CC | success_metric: build skill and audit skill agree on the send token | revenue_link: removes an unpassable gate that already got routed around
4. next_artifact: form-refill detector — alert when a known business re-submits with changed answers | owner_agent: Madison CC | success_metric: refills surfaced same-day with a diff | revenue_link: a refill is a buying signal, not a duplicate
5. next_artifact: 401/private-domain pre-check wired into intake (dig+fetch before build) | owner_agent: Madison CC | success_metric: zero pages claiming review of an unreadable site | revenue_link: prevents a credibility-killing false claim to a prospect
