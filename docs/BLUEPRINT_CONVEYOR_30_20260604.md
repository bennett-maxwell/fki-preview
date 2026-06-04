# Blueprint AI Conveyor 30 — Permanent Small-Step Factory

Purpose: stop one giant Blueprint AI task from hiding defects. Every Blueprint package must move through 30 small steps. Each step has a worker output, an auditor check, and a receipt. A later step cannot run if an earlier required step is red.

## Greenlight model
- **Steps 01-28:** must be green before Bennett sees approval preview.
- **Step 29:** Bennett approval preview send; green only after Bennett-only preview is sent and receipt exists.
- **Step 30:** external/customer send; locked until Bennett explicitly approves and Gatekeeper token allows `external_send`.

## Subagent model
Use bounded subagents only for isolated steps. Each subagent returns a JSON receipt and no prose-only pass claims.

| Step | Name | Worker output | Auditor / gate | Green condition |
|---:|---|---|---|---|
| 01 | Intake identity lock | lead profile JSON | identity auditor | canonical name, email/phone/contact ID, business, slug |
| 02 | Source-of-truth bundle | source URLs/files | source auditor | source list exists, no fabricated facts |
| 03 | Brand/business classification | industry + business model | classification auditor | industry and revenue model match source |
| 04 | Tool stack extraction | tools list | stack auditor | CRM/site/calendar/tools mapped or marked unknown |
| 05 | GHL/contact readback | CRM receipt | CRM auditor | exact contact found or explicit no-contact proof |
| 06 | Opportunity map | prioritized use cases | strategy auditor | P1-P6 tied to actual business |
| 07 | Agent list | 6 actual agents | agent auditor | agent names/descriptions match Blueprint recommendations |
| 08 | Prompt pack | 3 prompts | prompt auditor | prompts are customer-specific, not generic |
| 09 | Financial inputs | ROI variables | finance auditor | intake/source-backed, no cross-industry clone |
| 10 | Blueprint HTML render | `blueprints/<slug>.html` | render auditor | required sections render, no template leaks |
| 11 | Blueprint copy QA | customer-facing copy | copy auditor | no wrong industry, no stale customer names |
| 12 | CTA/link QA | public action links | link gate | `qualify.html` only, carries lead/biz/src/agents, HTTP 200 |
| 13 | Qualifier required fields | `qualify.html` | qualifier required-field gate | identity + all 8 answers required |
| 14 | Q7 tailoring | Q7 context | qualifier-context gate | Q7 options overlap actual agents/recommendations |
| 15 | Lead relay/GHL payload | relay payload proof | relay auditor | no public PIT token, tracked submit payload valid |
| 16 | Repeat submit/idempotency | repeat receipt | CRM duplicate auditor | five submits update one contact, no duplicate |
| 17 | Calendar routing | booking proof | calendar auditor | booking path opens only after tracked submit |
| 18 | Audio script | script text | direct-address text auditor | direct address, source-specific, no banned phrases |
| 19 | Audio render | MP3 | audio size/duration auditor | 6-20 min, readable, correct file |
| 20 | Audio transcript/readback | ASR/public receipt | audio content auditor | direct-address ASR PASS + public SHA match |
| 21 | Delivery email data | populated fields | email data auditor | correct lead/business/industry/URLs |
| 22 | Delivery email HTML | customer-view HTML | email technical gate | inline-safe, one qualify CTA, no tokens |
| 23 | Delivery email visual format | rendered preview/screenshot | email visual-format gate | approved subject/body/cards/buttons/signature; no proof memo |
| 24 | Bennett approval packet | Bennett-only preview | approval packet auditor | preview email is customer-view, internal proof separate |
| 25 | Blueprint audit | audit receipt | `run-audit.py` | 100% for current lead |
| 26 | Completion gate | completion receipt | completion gate | all required categories green |
| 27 | Gatekeeper token | token receipt | Gatekeeper | token bound to exact artifacts, preview-only unless approved |
| 28 | Public readback | public HTML/email/audio receipts | public auditor | deployed bytes and public links match intended artifacts |
| 29 | Bennett preview send | Gmail receipt | send auditor | sent to `bennett@franchiseki.com`, customer not sent |
| 30 | External/customer send | GHL/Gmail receipt | external-send auditor | only after Bennett approval + `external_send` token |

## Permanent rule
Final audit must output all 30 steps with `GREEN`, `RED`, or `LOCKED_HUMAN_GATE`. Bennett approval preview is not allowed until steps 01-28 are GREEN. External send is not allowed until steps 01-29 are GREEN and step 30 is explicitly unlocked by Bennett approval.
