# Blueprint batch money packet — Glenn · Jim · Butch · Jaye (2026-08-10)

who: Glenn Sojourner (Home Watch Marketing) · Jim (Speedy Freight Greenville) · Butch (Threadgill's Roofing) · Jaye (Haven Partners Group) | brand: Advaita/Blueprint | $impact_proxy: 4 × ($5K setup + $2K/mo Advaita AI band) = up to $20K setup + $8K/mo if all four convert; Butch is the highest-revenue prospect ($1M–$3M band) | metric_lever: delivered Blueprint → tracked qualifier completion → booked call | next_3_actions: (1) Pages deploy lands the 4 mp3s (in flight, no further pushes) (2) populate 4 delivery emails + create Gmail drafts (3) Madison approves → canonical CRMX-API send | delivery_state: staged_for_approval | fdd_claims_status: n/a

## All four at 20/20 (100%)

| Lead | Business | Page | Podcast | Audit |
|---|---|---|---|---|
| Glenn Sojourner | Home Watch Marketing | live 200 | 387.3s (6:27) | **20/20** |
| Jim | Speedy Freight Greenville | live 200 | 314.0s (5:14) | **20/20** |
| Butch | Threadgill's Roofing | live 200 | 287.2s (4:47) | **20/20** |
| Jaye | Haven Partners Group | built + pushed | 366.1s (6:06) | **20/20** |

Every podcast is a native NotebookLM `AudioLength.SHORT` render inside the 240–960s window with a
clean native ending — no `ffmpeg -t` trim, no TTS bookend, no tempo patch. D3-05 clean-ending and
D3-02 direct-address gates PASS on all four.

## What unblocked this (no human action required)

The auth gate I twice escalated to Madison was self-healable the whole time — the canonical
`notebooklm` skill v6 says so in bold: *"NEVER gate on Bennett for auth recovery."* Three real
defects were behind it:

1. **`cookie_bridge.py` did not exist on this seat.** The skill documents it at
   `~/.openclaw/bin/cookie_bridge.py`, but it only ever existed on Mack. Written here now, and it
   **discovers** the Chrome profile instead of hardcoding Mack's `Profile 1` (which does not exist
   on this Mac). Cookie count alone is not a valid selector — several profiles score 9/9 on Google
   auth cookies but are the wrong account; `Profile 29` is the NotebookLM-owning one.
2. **`notebooklm-py` was 0.4.1 against PyPI 0.8.0.** Source uploads landed as
   `SourceType.UNKNOWN → status: error`, which surfaced downstream as a bogus
   `GENERATION_FAILED — no artifact_id returned`. Upgrading fixed it outright.
3. **My own runner logged the source failure and kept going**, manufacturing that misleading
   error. It now hard-aborts unless the source reaches `ready`.

Permanent fix landed in the shared fleet brain: notebooklm `SKILL.md` patched same-ID on Drive
(`19S4Iawtu3aPSTezinYMbye7AFpCol05K`), fetchback SHA `228ca532…` matched, marker
`NLM-AUTH-SELFHEAL-PORTABLE-v2-20260810`.

## Per-lead commercial angle

- **Butch — highest revenue, highest pain.** $1M–$3M, team of **1**, no CRM/PM/storage, nothing
  documented, thirteen stress areas, stated goal "less chaos." Guardrails ban advising on insurance
  claims (unlicensed **public adjusting** in Texas) and any deductible waiver (**insurance fraud**).
- **Jaye — sells speed, answers next-day.** 50 inquiries/month across four channels with no CRM,
  selling regulatory assurance to fund managers who buy on turnaround. Guardrails ban legal advice,
  interpreting any securities regulation, declaring anything compliant, and touching LP PII.
- **Jim — throughput, not demand.** 50 quote requests/month against 3 people at ~60-min response;
  in freight the first accurate quote usually wins. Rate/transit/capacity claims all banned.
- **Glenn — AI-native operator.** Runs his own AI assistant and sells AI-visibility; the build never
  explains AI and frames the gap as purely operational.

## Expansion seeds

1. **Home Watch niche list** — Glenn's ICP is a repeatable Advaita segment. next_artifact: Apollo pull | owner: Madison | success_metric: 25 net-new | revenue_link: new Blueprint leads.
2. **DFW storm/hail roofing list** — Butch's segment; same solo-operator overload. next_artifact: Apollo pull | owner: Madison | success_metric: 25 net-new | revenue_link: new leads.
3. **Fund-services / regtech segment** — Jaye's ICP; high ACV, compliance-driven. next_artifact: Apollo pull | owner: Madison | success_metric: 15 net-new | revenue_link: pipeline quality.
4. **"You sell speed and answer next-day" hook** — Jaye's own contradiction, generalizes to most service businesses. next_artifact: outreach hook doc | owner: Madison | success_metric: 3 replies | revenue_link: pipeline.
5. **Reusable industry guardrail blocks** — insurance-restoration (public adjusting + deductible) and securities-compliance (no legal advice / no compliance declaration) blocks should attach by industry automatically. next_artifact: same-ID skill patch | owner: Madison | success_metric: auto-applied | revenue_link: claim safety.
6. **Deploy discipline fix** — pushing each podcast separately cancelled its own deploy three times. next_artifact: batch-push rule in clone-blueprint + a `--no-push` flag | owner: Madison | success_metric: one deploy per batch | revenue_link: delivery latency.
