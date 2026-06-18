#!/usr/bin/env python3
"""
create-crmx-email-draft.py — Stage 7 CRMX/GHL blueprint-delivery email DRAFT creator.

Spec: docs/crmx-blueprint-delivery-and-automation.md §2.
Builds a blueprint delivery email from the ONE canonical template
(templates/delivery-email-template.html — never a fork), injects the real lead
tokens, runs scripts/email-design-conformance.py on the resolved HTML and REQUIRES
PASS, then records the email into CRMX as a DRAFT attached to the contact.

SAFETY / NEVER-SEND DESIGN (hard requirement of the pipeline):
  - This script NEVER calls any send / outbound-message / scheduled endpoint.
  - The CRMX-side artifact is a CONTACT NOTE (GHL /contacts/{id}/notes), which has
    ZERO delivery capability — it is reviewable in CRMX but cannot reach the prospect.
    Madison opens the contact in CRMX, reviews the drafted email + links, and is the
    one who actually composes/sends the email. Status is therefore "draft" by
    construction (a recorded note is never an outbound email).
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


def load_env():
    d = {}
    p = os.path.expanduser("~/.claude/.env")
    for line in open(p):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def api(method, path, body=None):
    env = load_env()
    headers = {"Authorization": f"Bearer {env['GHL_API_KEY']}", "Version": "2021-07-28",
               "Accept": "application/json", "Content-Type": "application/json", "User-Agent": UA}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.getcode(), json.loads(r.read().decode() or "{}")


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
    ap.add_argument("--commit", action="store_true", help="write the CRMX draft note (else dry-run)")
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

    cid = prof.get("ghl_contact_id")
    subject = f"Your AI Blueprint is Ready — {vals['BUSINESS_NAME']}"
    note_body = (
        f"[BLUEPRINT DELIVERY EMAIL — DRAFT, NOT SENT]\n"
        f"Channel: CRMX (review + send manually). Status: DRAFT.\n"
        f"To: {prof.get('email','')}  |  Contact: {cid}\n"
        f"Subject: {subject}\n\n"
        f"Blueprint: {vals['BLUEPRINT_URL']}\n"
        f"Podcast:   {vals['PODCAST_URL']}\n"
        f"Qualify:   {vals['QUALIFY_URL']}\n\n"
        f"Resolved, conformance-PASSED email HTML staged at: delivery-emails/{slug}-crmx-email.html\n"
        f"Paste that HTML into a CRMX Email > Custom HTML/Code element to review, then send.\n"
        f"(This note is a non-sending draft record; it does not deliver any email.)\n"
        f"Generated {datetime.datetime.now(datetime.timezone.utc).isoformat()} by create-crmx-email-draft.py"
    )

    result = {"slug": slug, "contact_id": cid, "subject": subject,
              "email_html": f"delivery-emails/{slug}-crmx-email.html",
              "mode": "commit" if args.commit else "dry-run", "status": "draft", "sent": False}

    if not args.commit:
        print("[dry-run] NOT writing to GHL. Re-run with --commit to create the CRMX draft note.")
        print(json.dumps(result, indent=2))
        return

    # COMMIT: create a non-sending CONTACT NOTE (zero delivery capability)
    code, resp = api("POST", f"/contacts/{cid}/notes", {"body": note_body})
    note_id = (resp.get("note") or {}).get("id") or resp.get("id")
    result["crmx_note_id"] = note_id
    result["crmx_draft_url"] = f"https://app.gohighlevel.com/v2/location/{load_env()['GHL_LOCATION_ID']}/contacts/detail/{cid}"
    result["http_code"] = code
    # Save a receipt
    rec_dir = os.path.join(REPO, "audit-receipts", slug)
    os.makedirs(rec_dir, exist_ok=True)
    open(os.path.join(rec_dir, f"{slug}-crmx-email-draft.json"), "w").write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"[done] CRMX draft note created (id={note_id}, http {code}) — NOT sent.")


if __name__ == "__main__":
    main()
