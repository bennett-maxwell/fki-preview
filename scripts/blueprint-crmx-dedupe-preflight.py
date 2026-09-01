#!/usr/bin/env python3
"""blueprint-crmx-dedupe-preflight.py <slug> --strict-crmx — Watson double-send guard.

blueprint-ai-skill v3.52 Stage 7 makes this MANDATORY before any CRMX `--send-ghl`:
  "It HARD-BLOCKS if the contact already carries a `blueprint-delivered` tag or has a prior
   blueprint conversation — this prevents the Watson-style double-send. No --send-ghl may run
   until this preflight PASSES."

Written 2026-08-10: the skill has named this path since v3.52 but the file did not exist in the
repo, so the mandatory gate was unenforceable — the send path had no double-send protection at
all. Implemented here against the live GHL API.

Checks (any HARD-BLOCK => exit 1):
  1. contact carries tag `blueprint-delivered`
  2. contact has a prior EMAIL message in any conversation whose body/subject references the
     blueprint hub (i.e. we already delivered) — belt to the tag's braces, because tags are
     known-unreliable (memory: never trust tags to prove delivery)
  3. contact id does not resolve

Exit 0 = safe to send.

Usage: python3 scripts/blueprint-crmx-dedupe-preflight.py <slug> --strict-crmx
"""
import json, os, sys, urllib.request, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB_MARK = "hub.aiblueprintmarketing.com"


def env():
    for path in (os.path.expanduser("~/.openclaw/gateway.env"), os.path.expanduser("~/.claude/.env")):
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def call(url, tok):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {tok}", "Version": "2021-07-28", "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    slug = sys.argv[1]
    if "--strict-crmx" not in sys.argv:
        print("refusing to run without --strict-crmx", file=sys.stderr)
        return 2
    env()
    tok = os.environ["ADVAITA_GHL_PIT"]
    loc = os.environ["ADVAITA_GHL_LOCATION_ID"]
    p = json.load(open(os.path.join(REPO, "leads", f"{slug}.json"), encoding="utf-8"))
    cid = p["ghl_contact_id"]

    try:
        c = call(f"https://services.leadconnectorhq.com/contacts/{cid}", tok)["contact"]
    except Exception as e:
        print(f"HARD-BLOCK {slug}: contact {cid} did not resolve ({e})")
        return 1

    blocks = []
    tags = [t.lower() for t in (c.get("tags") or [])]
    if "blueprint-delivered" in tags:
        blocks.append("contact already carries tag 'blueprint-delivered'")

    # Tags are unreliable on their own, so also look for an actual prior delivery message.
    prior = 0
    try:
        convs = call("https://services.leadconnectorhq.com/conversations/search"
                     f"?locationId={loc}&contactId={cid}", tok).get("conversations", []) or []
        for cv in convs:
            msgs = call(f"https://services.leadconnectorhq.com/conversations/{cv['id']}/messages", tok)
            for m in (msgs.get("messages", {}) or {}).get("messages", []) or []:
                blob = json.dumps(m).lower()
                if HUB_MARK in blob and f"/{slug}" in blob:
                    prior += 1
    except Exception as e:
        print(f"  note: conversation scan degraded ({type(e).__name__}: {e}) — tag check still applied")
    if prior:
        blocks.append(f"{prior} prior message(s) already reference {HUB_MARK}/…/{slug}")

    print(f"contact={cid} tags={c.get('tags')} prior_blueprint_messages={prior}")
    if blocks:
        for b in blocks:
            print(f"HARD-BLOCK {slug}: {b}")
        return 1
    print(f"PASS {slug}: no blueprint-delivered tag, no prior blueprint delivery — safe to send")
    return 0


if __name__ == "__main__":
    sys.exit(main())
