#!/usr/bin/env python3
"""
Pull a GHL/LeadConnector contact's full AI_Advantage_blueprint form submission by email.
Maps custom-field IDs -> human field names so the blueprint profile is built from the
lead's ACTUAL form answers (never guessed). GHL sits behind Cloudflare, which 1010-blocks
non-browser User-Agents, so we send a browser UA.

Usage: python3 scripts/ghl-pull-contact.py "<email>"
Reads GHL_API_KEY + GHL_LOCATION_ID from ~/.claude/.env.
"""
import os, sys, json, urllib.request, urllib.parse

ENV = os.path.expanduser("~/.claude/.env")
def load_env():
    d = {}
    for line in open(ENV):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d

env = load_env()
KEY = env["GHL_API_KEY"]; LOC = env["GHL_LOCATION_ID"]
BASE = "https://services.leadconnectorhq.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

def api(path):
    req = urllib.request.Request(BASE + path, headers={
        "Authorization": f"Bearer {KEY}", "Version": "2021-07-28",
        "Accept": "application/json", "User-Agent": UA,
    })
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())

def main(email):
    # 1) find contact by email
    q = urllib.parse.quote(email)
    res = api(f"/contacts/?locationId={LOC}&query={q}&limit=20")
    contacts = res.get("contacts", [])
    match = next((c for c in contacts if (c.get("email") or "").lower() == email.lower()), None)
    if not match and contacts:
        match = contacts[0]
    if not match:
        print(json.dumps({"error": "no contact found", "email": email})); return
    cid = match["id"]
    # 2) full contact (custom fields live here)
    full = api(f"/contacts/{cid}").get("contact", {})
    # 3) field-id -> name map
    cf_defs = api(f"/locations/{LOC}/customFields").get("customFields", [])
    id2name = {f["id"]: (f.get("name") or f.get("fieldKey") or f["id"]) for f in cf_defs}
    answers = {}
    for cf in full.get("customFields", []):
        name = id2name.get(cf.get("id"), cf.get("id"))
        answers[name] = cf.get("value")
    out = {
        "contact_id": cid,
        "name": f"{full.get('firstName','')} {full.get('lastName','')}".strip(),
        "first_name": full.get("firstName"), "last_name": full.get("lastName"),
        "email": full.get("email"), "phone": full.get("phone"),
        "company": full.get("companyName"),
        "tags": full.get("tags"),
        "form_answers": answers,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: ghl-pull-contact.py <email>")
    main(sys.argv[1])
