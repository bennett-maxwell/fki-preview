#!/usr/bin/env python3
"""
create-crmx-email-draft.py — Stage 7 CRMX/GHL blueprint-delivery email DRAFT creator.

Spec: docs/crmx-blueprint-delivery-and-automation.md §2.
Builds a blueprint delivery email from the ONE canonical template
(templates/delivery-email-template.html — never a fork), injects the real lead
tokens, runs scripts/email-design-conformance.py on the resolved HTML and REQUIRES
PASS, then creates the email in CRMX as a SENDABLE custom-HTML email
template/builder (the exact resolved HTML, NOT a rebuilt drag-drop layout).

HOW THE SENDABLE DRAFT IS MADE (verified on location 14RD8KklxR9G4e0Rf7v2):
  Two-step GHL Emails API:
    1) POST /emails/builder
         {locationId, title, type:"html", updatedBy}            -> returns template {id}
    2) POST /emails/builder/data
         {locationId, templateId, html, editorType:"html", updatedBy}
                                                                 -> injects EXACT raw HTML
  The result is a custom-code email template in CRMX (Marketing > Emails > Templates).
  Madison opens it, clicks "Send" / uses it in a campaign, and is the one who sends.
  This is a real sendable object (unlike the old contact-note, which could not send).

SAFETY / NEVER-SEND DESIGN (hard requirement of the pipeline):
  - This script NEVER calls any send / outbound-message / campaign-execute /
    scheduled-send endpoint. It only creates a TEMPLATE. Creating a template does
    NOT address a recipient and does NOT trigger delivery — a human must open it in
    CRMX and click Send. Status is therefore "draft/template, unsent" by construction.
  - HARD never-send guard: the only POST paths allowed are /emails/builder and
    /emails/builder/data. Any path containing send/outbound/schedule/execute is
    refused in code (assert_never_send).
  - Default mode is DRY-RUN. Nothing is written to GHL unless --commit is passed.
  - Pre-send gates: (a) session audit 100/100 this session, (b) email conformance PASS.

Usage:
  python3 scripts/create-crmx-email-draft.py <slug>            # dry-run (resolve + conformance only)
  python3 scripts/create-crmx-email-draft.py <slug> --commit   # also write the CRMX draft note
"""
import os, sys, json, re, subprocess, argparse, datetime
import urllib.request, urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, "templates", "delivery-email-template.html")
OUT_DIR = os.path.join(REPO, "delivery-emails")
STATE_DIR = os.path.expanduser("~/.openclaw/state")
BASE = "https://services.leadconnectorhq.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

TOKENS = ["LEAD_FIRST_NAME", "BUSINESS_NAME", "INDUSTRY", "ACCENT_COLOR",
          "BLUEPRINT_URL", "PODCAST_URL", "QUALIFY_URL"]


# Per-run credential override, populated once the lead's own sub-account is resolved.
# api() re-reads the env file on every call, so without this the Advaita PIT selected
# below would be silently discarded and every request would fall back to FKI main.
_ENV_OVERRIDE = {}


def load_env():
    d = {}
    p = os.path.expanduser("~/.claude/.env")
    for line in open(p):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    d.update(_ENV_OVERRIDE)
    return d


SEND_TOKENS = ("send", "outbound", "schedule", "execute", "campaign", "message", "/sms")


def assert_never_send(path):
    """Hard guard: refuse any path that could deliver a message to the prospect."""
    low = path.lower()
    for tok in SEND_TOKENS:
        if tok in low:
            raise SystemExit(
                f"NEVER-SEND GUARD TRIPPED: refusing API path containing '{tok}': {path}. "
                f"This script only creates an unsent CRMX email template.")


def api(method, path, body=None):
    if method.upper() in ("POST", "PUT", "PATCH", "DELETE"):
        assert_never_send(path)
    env = load_env()
    headers = {"Authorization": f"Bearer {env['GHL_API_KEY']}", "Version": "2021-07-28",
               "Accept": "application/json", "Content-Type": "application/json", "User-Agent": UA}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.getcode(), json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, {"_error": e.read().decode()[:1500]}


def session_audit_ok(slug):
    p = os.path.join(STATE_DIR, f"session-audit-ts-{slug}.json")
    if not os.path.exists(p):
        return False, f"missing {p}"
    d = json.load(open(p))
    score = d.get("score")
    ts = d.get("ts") or d.get("timestamp")
    if score != 100:
        return False, f"score={score} (need 100)"
    # ts freshness within 3600s. Canonical writer (mark-audit-complete.sh) emits epoch seconds.
    try:
        if isinstance(ts, (int, float)) or str(ts).isdigit():
            t = datetime.datetime.fromtimestamp(float(ts), datetime.timezone.utc)
        else:
            t = datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        age = (datetime.datetime.now(datetime.timezone.utc) - t).total_seconds()
        if age > 3600:
            return False, f"audit ts age {int(age)}s > 3600s"
    except Exception as e:
        return False, f"bad ts {ts}: {e}"
    return True, "audit 100/100 this session"


def resolve(slug):
    prof = json.load(open(os.path.join(REPO, "leads", f"{slug}.json")))
    html = open(TEMPLATE, encoding="utf-8").read()
    vals = {
        "LEAD_FIRST_NAME": prof.get("lead_first_name") or prof.get("first_name") or "",
        "BUSINESS_NAME": prof.get("business_name", ""),
        "INDUSTRY": prof.get("industry", ""),
        "ACCENT_COLOR": prof.get("accent_color", "#0071E3"),
        "BLUEPRINT_URL": prof.get("blueprint_url", ""),
        "PODCAST_URL": prof.get("podcast_url", ""),
        "QUALIFY_URL": prof.get("qualify_url") or prof.get("apply_url", ""),
    }
    for t in TOKENS:
        html = html.replace("{{" + t + "}}", str(vals[t]))
    left = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if left:
        raise SystemExit(f"FAIL: unresolved tokens remain: {sorted(set(left))}")
    return prof, html, vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--title", help="CRMX email template title (default: 'Blueprint — <name> / <business>')")
    ap.add_argument("--commit", action="store_true", help="create the sendable CRMX email template (else dry-run)")
    args = ap.parse_args()
    slug = args.slug

    # GATE 1: session audit 100/100 this session
    ok, why = session_audit_ok(slug)
    if not ok:
        raise SystemExit(f"BLOCKED: session audit gate not satisfied — {why}. Run the audit to 100 first.")
    print(f"[gate] session audit: PASS ({why})")

    # Resolve canonical template
    prof, html, vals = resolve(slug)
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{slug}-crmx-email.html")
    open(out_path, "w", encoding="utf-8").write(html)
    print(f"[resolve] wrote {out_path} ({len(html)} bytes)")

    # GATE 2: email design conformance MUST pass
    r = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "email-design-conformance.py"), out_path],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        raise SystemExit(f"BLOCKED: email-design-conformance FAIL\n{r.stderr.strip()}")
    print("[gate] email conformance: PASS")

    env = load_env()
    # PERMANENT FIX 2026-07-28 (marker BLUEPRINT-CRMX-DRAFT-WRONG-SUBACCOUNT-20260728):
    # this used env["GHL_LOCATION_ID"] unconditionally — that is FKI main
    # (14RD8KklxR9G4e0Rf7v2). Every Advaita blueprint lead lives in the Advaita
    # sub-account (GPCi3FrWJCyevcGzZgTT) with its own PIT. So the delivery draft was
    # created in a sub-account where the prospect's contact DOES NOT EXIST — Madison
    # opens CRMX, cannot send it to the lead, and any send would go from the wrong
    # brand. Caught on bri-fresh (contact BJp1MNYhfCqJjM3LATeJ in GPCi3) after the
    # draft landed in 14RD8K. The lead profile is the authority on its own location.
    loc = prof.get("ghl_location_id") or env["GHL_LOCATION_ID"]
    if loc == env.get("ADVAITA_GHL_LOCATION_ID") and env.get("ADVAITA_GHL_PIT"):
        env["GHL_API_KEY"] = env["ADVAITA_GHL_PIT"]
        print(f"[creds] Advaita sub-account {loc} -> using ADVAITA_GHL_PIT")
    else:
        print(f"[creds] location {loc} -> using default GHL_API_KEY")
    if loc != env.get("GHL_LOCATION_ID") and loc != env.get("ADVAITA_GHL_LOCATION_ID"):
        raise SystemExit(
            f"BLOCKED: lead location {loc} matches no known credential set. Refusing to "
            f"create a draft in an unverified sub-account.")
    _ENV_OVERRIDE.update(env)
    cid = prof.get("ghl_contact_id")
    subject = f"Your AI Blueprint is Ready — {vals['BUSINESS_NAME']}"
    title = args.title or f"Blueprint — {prof.get('lead_name') or vals['LEAD_FIRST_NAME']} / {vals['BUSINESS_NAME']}"

    result = {"slug": slug, "contact_id": cid, "subject": subject, "template_title": title,
              "email_html": f"delivery-emails/{slug}-crmx-email.html",
              "mode": "commit" if args.commit else "dry-run", "status": "draft/template", "sent": False}

    if not args.commit:
        print("[dry-run] NOT writing to GHL. Re-run with --commit to create the sendable CRMX email template.")
        print(json.dumps(result, indent=2))
        return

    # COMMIT — STEP 1: create the email template/builder shell (no recipient, cannot send)
    code1, r1 = api("POST", "/emails/builder",
                    {"locationId": loc, "title": title, "type": "html",
                     "updatedBy": "madison@franchiseki.com"})
    template_id = r1.get("id") or r1.get("redirect")
    if code1 != 201 or not template_id:
        raise SystemExit(f"FAIL creating builder shell [{code1}]: {r1}")
    print(f"[step1] builder shell created id={template_id} [{code1}]")

    # COMMIT — STEP 2: inject the EXACT resolved HTML as custom code (editorType=html)
    code2, r2 = api("POST", "/emails/builder/data",
                    {"locationId": loc, "templateId": template_id, "html": html,
                     "editorType": "html", "updatedBy": "madison@franchiseki.com"})
    if code2 not in (200, 201) or not r2.get("ok"):
        raise SystemExit(f"FAIL injecting HTML into builder [{code2}]: {r2}")
    preview_url = r2.get("previewUrl")
    print(f"[step2] HTML injected (versionId={r2.get('versionId')}) [{code2}]")

    # VERIFY — fetch the builder back, confirm it exists as a template and the HTML round-trips
    cv, rv = api("GET", f"/emails/builder?locationId={loc}&limit=200")
    builders = rv.get("builders", []) if isinstance(rv, dict) else []
    mine = next((b for b in builders if b.get("id") == template_id), None)
    verified = mine is not None
    html_roundtrip = None
    if preview_url:
        try:
            vreq = urllib.request.Request(preview_url, headers={"User-Agent": UA})
            with urllib.request.urlopen(vreq, timeout=40) as vr:
                fetched = vr.read().decode()
            # sentinel: the business name must appear in the stored HTML
            html_roundtrip = vals["BUSINESS_NAME"] in fetched
        except Exception as e:
            html_roundtrip = f"fetch-error: {e}"

    crmx_url = f"https://app.gohighlevel.com/v2/location/{loc}/emails/templates?templateId={template_id}"
    result.update({
        "crmx_template_id": template_id,
        "crmx_template_url": crmx_url,
        "preview_url": preview_url,
        "http_create": code1, "http_inject": code2,
        "verified_in_list": verified,
        "verified_template_type": (mine or {}).get("templateType"),
        "html_roundtrip_ok": html_roundtrip,
        "is_plain_text": (mine or {}).get("isPlainText"),
        "sent": False, "status": "draft/template (unsent)",
    })

    rec_dir = os.path.join(REPO, "audit-receipts", slug)
    os.makedirs(rec_dir, exist_ok=True)
    open(os.path.join(rec_dir, f"{slug}-crmx-email-draft.json"), "w").write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"[done] CRMX sendable email TEMPLATE created (id={template_id}) — verified unsent. "
          f"Open in CRMX: {crmx_url}")


if __name__ == "__main__":
    main()
