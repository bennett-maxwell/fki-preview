# Blueprint AI v3.27 scale conveyor — 2026-06-04

User explicitly requested fleet memory.

Canonical Drive `blueprint-ai-skill/SKILL.md` is now version `3.27` with Blueprint Scale Conveyor hardening for Madison/all agents.

Permanent behavior:
1. Before any agent claims Blueprint AI is production-scale, permanently fixed, or ready for high-throughput/1000-per-day operation, it must run a post-update synthetic scale-smoke fixture.
2. Required fixture: Billy Bob / Billy Bob Electric, electrician/electrical contractor, average customer value `$1000`, annual revenue `$2,000,000`, no external/customer send.
3. Required receipts: profile, Blueprint HTML, delivery email, qualifier/Q7 context, email visual gate, completion gate, Gatekeeper result, Conveyor 30 audit, self-audit/edit receipt, and memory receipt tied to Drive/Notion proof.
4. Billy Bob scale-smoke proof passed locally: Blueprint audit `15/15`; completion `36/36 applicable`; Gatekeeper local score `100`; email visual PASS; qualifier/Q7 context PASS; Conveyor 30 pre-Bennett `28 GREEN, 2 LOCKED_HUMAN_GATE, 0 RED`.
5. Step 30 remains locked until Bennett approval plus `external_send`; synthetic scale-smoke cannot be treated as customer delivery.
6. Repo fixes from the run: `scripts/blueprint_conveyor_30.py` scale fixture support, `blueprints/TEMPLATE.html` malformed top-nav href fix, and `scripts/roi-industry-config.json` mapping for Billy Bob to `home_services`.
7. Drive skill proof: file ID `1IzE-seDDaB1Tciik9mwBVrgQcb7FP7eH`, v3.27 fetchback SHA `02de3ec9ca92ae25852db50670a4b148aaa3a8495aa560ee7ff67d049a6a6f30`.
8. Drive memory proof: canonical `MEMORY.md` file ID `1RO4koS5TvZP37AvDB3y4T9I2A582q90G`, fetchback SHA `3a8ee85705178ba55ce4df310b8096991f014f3a2420194c922aea0ce52a6bcc`.
9. Active Notion row: `https://app.notion.com/p/374cf5514fd38116a10af88c504def54`.
