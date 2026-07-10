# Layer 1 (real-time, server-side) — Vercel relay Slack patch

**Goal:** the instant a Blueprint form lead is created server-side, post to Slack
`#ai-blueprint-leads` (C0B3QCD9UD7) — with ZERO dependence on Madison's Mac.

## Where this goes
Repo: **blueprint-ghl-relay** (Vercel project `blueprint-ghl-relay.vercel.app`).
Source is NOT on Madison's machine (it lives at `/Users/temp/blueprint-ghl-relay` on
Bennett's machine per session brief). Whoever holds it applies this patch.

Handler file: `api/blueprint-lead.(js|ts)` — the function that today creates the GHL
contact and returns `{ok:true, mode:"created", contactId}`.

## The patch (Node/Vercel serverless)
Immediately AFTER the GHL contact create succeeds, before `res.json(...)`, add:

```js
// --- Layer 1: real-time Slack alert to #ai-blueprint-leads ---
const SLACK_WEBHOOK = process.env.SLACK_LEADS_WEBHOOK_URL; // Incoming Webhook for #ai-blueprint-leads
if (SLACK_WEBHOOK) {
  const name = [body.firstName, body.lastName].filter(Boolean).join(" ") || "(no name)";
  const text =
    `:fire: *NEW BLUEPRINT LEAD* — ${name} (${body.email || "?"} / ${body.phone || "?"}) ` +
    `just submitted the form. Build starting. <@U08H07FMDFA> <@U0AE3SP690D>\n` +
    `> business: ${body.businessName || "?"} | source: \`${body.source || "external_form"}\` | ` +
    `GHL id: \`${contactId}\``;
  try {
    await fetch(SLACK_WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
  } catch (e) { console.error("slack alert failed (lead still saved):", e); }
}
```

Fire-and-forget: a Slack failure must NEVER block the contact create.

## Required grant (route to Kay/Ivan — Slack admin)
- A Slack **Incoming Webhook URL** bound to `#ai-blueprint-leads`, set as Vercel env var
  `SLACK_LEADS_WEBHOOK_URL` on the `blueprint-ghl-relay` project (Production).
- Redeploy the relay.

## IMPORTANT ROUTING BUG found 2026-07-01 (fix while you're in here)
The live relay **ignores the `locationId` in the POST body and writes every contact to
MAIN FKI (14RD8KklxR9G4e0Rf7v2)**, even when `locationId=GPCi3FrWJCyevcGzZgTT` (Advaita)
is passed. Meanwhile the **live form** (`blueprint.meetadvaita.com`) no longer uses the
relay at all — it POSTs directly to GHL `backend.leadconnectorhq.com/external-tracking/events`
with `type:external_form_submission`, `trackingId:tk_34be577ca301462ca99e00b50c5ae72d`,
`locationId:GPCi3FrWJCyevcGzZgTT` → lands in **Advaita** with `source=external_form`, no tags.

So there are TWO divergent ingestion paths. Decide the canonical one:
- If the form should route through the relay again → point the SPA's submit `fetch` at
  `https://blueprint-ghl-relay.vercel.app/api/blueprint-lead` (edit the Vibe page bundle),
  and make the relay honor `body.locationId`.
- If the form keeps posting external-tracking directly to Advaita → the relay Slack patch
  is moot for real leads; instead Layer 1 must be a **GHL workflow in the Advaita account**
  triggered on Contact Created (or source=external_form) with a Slack/webhook step. That
  workflow slot already exists published ("Blueprint AI Contact Alerts - ML",
  a2331d2c-4a87-4811-b974-700abfb204b4) but its trigger/step must be re-pointed — this
  needs GHL **workflow-edit UI access** (Madison/Bennett/Jenn); the GHL API cannot edit
  workflow actions (GET /workflows/:id returns 404; list is read-only).

Until Layer 1 is chosen + wired, **Layer 2 (the Sentinel) is the working guarantee.**
