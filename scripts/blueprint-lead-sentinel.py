#!/usr/bin/env python3
"""
blueprint-lead-sentinel.py — BULLETPROOF Blueprint new-lead + delay + heartbeat watcher
========================================================================================
ONE always-on process that makes SILENCE impossible. Replaces the fragile
combo of n1-new-lead-watcher.py + blueprint-delay-watchdog.py, both of which
(a) only ran when a Claude session happened to invoke them, and (b) keyed on a
SINGLE `source` string so a lead with a different source/tag was silently missed.

ROOT CAUSE THIS FIXES (Josh Jackson, josh@exaltlife.co, 2026-06-30):
  Josh landed in the MAIN FKI account (14RD8KklxR9G4e0Rf7v2) with
  tags=['blueprint ai lead', ...] and source="Bennett Call 2026-06-30".
  - The old n1 watcher matched source.startswith("blueprint_ai") -> MISS.
  - The old delay-watchdog matched the same source prefix -> MISS.
  - The GHL->Slack workflow (Brent's ":fire: New Lead" posts) keyed on the
    Advaita form and stopped firing after ~6/23 -> MISS.
  - Nothing ran either script on a schedule -> nothing fired for ~24h.

MULTI-SIGNAL DETECTION (a lead matches if ANY of these is true, on EITHER account):
  1. source starts with "blueprint_ai"        (legacy main-FKI qualifier/apply)
  2. source == "external_form"                 (Advaita live form)
  3. any tag in TAG_SIGNALS                     (e.g. "blueprint ai lead",
       "ai-blueprint-opt-in", "blueprint_ai_apply", "blueprint ai opt-in")
  4. contact sits in a pipeline stage named like "Blueprint Requested"/"Blueprint"
  A single missing tag OR a changed source can no longer silently hide a lead.

WHAT IT DOES ON A NEW LEAD (idempotent, once per contact id):
  (a) writes it to a durable OUTBOX (JSON) + appends to the repo-tracked event log
  (b) posts to #ai-blueprint-leads (C0B3QCD9UD7) + DMs Madison + Cody
      -> requires SLACK_BOT_TOKEN. If absent, the notification is queued in the
         outbox with delivered=false and the Gmail-draft + SMS fallbacks still fire,
         so the lead is NEVER lost; a live Claude session drains the outbox.
  (c) best-effort SMS to Madison (Messages.app) — works headless if Automation is granted
  (d) starts the build clock for the 1-hour delivery-delay alarm
  (e) kicks the build pipeline (orchestrator --lead --url) unless --no-build

DELAY ALARM: any detected lead not marked delivered within DELAY_THRESHOLD_MIN
(default 60) raises a PRODUCTION DELAY alert (once per state).

DELIVERY DETECTION: a lead is "delivered" when it gets a "Blueprint Sent" tag in GHL
OR a <slug>.approved token exists OR sentinel is told via --delivered <id>.

HEARTBEAT / DEAD-MAN'S-SWITCH: every run stamps state/sentinel-heartbeat.json with
last_run + lead counts. Once/day it emits a heartbeat notification
("Sentinel alive — N leads seen, M delivered, K pending") so SILENCE itself becomes
an alarm. A separate check (--check-alive) fails loudly if last_run is stale, which a
tiny cron/launchd companion or an external uptime monitor can page on.

STATE (durable, mirrored into the repo under ops/state/ so it survives + is visible
to other agents; NOT local-only ~/.openclaw which dies on handoff):
  repo/ops/state/sentinel-seen.json        seen contact ids + metadata + clocks
  repo/ops/state/sentinel-outbox.json       pending + delivered notifications
  repo/ops/state/sentinel-heartbeat.json    liveness stamp
  repo/ops/logs/sentinel-events.jsonl        append-only audit trail

USAGE
  blueprint-lead-sentinel.py                 scan+notify+delay+heartbeat (the scheduled run)
  blueprint-lead-sentinel.py --baseline      record current leads as seen, notify nothing
  blueprint-lead-sentinel.py --once --dry-run print what it WOULD do, touch nothing external
  blueprint-lead-sentinel.py --delivered ID  mark a lead delivered (stops its delay clock)
  blueprint-lead-sentinel.py --drain          (for a live Claude session) print undelivered
                                              outbox items as JSON so the session posts them
  blueprint-lead-sentinel.py --mark-delivered-notif ID   mark an outbox item posted to Slack
  blueprint-lead-sentinel.py --check-alive   exit 0 if heartbeat fresh, 2 if stale
  blueprint-lead-sentinel.py --self-test EMAIL  inject a fake lead row for the live E2E test
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error

HOME = os.path.expanduser("~")
ENV_FILE = os.path.join(HOME, ".claude", ".env")
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(REPO_DIR, "ops", "state")
LOGS_DIR = os.path.join(REPO_DIR, "ops", "logs")
SEEN_FILE = os.path.join(STATE_DIR, "sentinel-seen.json")
OUTBOX_FILE = os.path.join(STATE_DIR, "sentinel-outbox.json")
HEARTBEAT_FILE = os.path.join(STATE_DIR, "sentinel-heartbeat.json")
EVENT_LOG = os.path.join(LOGS_DIR, "sentinel-events.jsonl")
APPROVE_DIR = os.path.join(HOME, ".openclaw", "state", "blueprint-approvals")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
GHL_BASE = "https://services.leadconnectorhq.com"
GHL_VER = "2021-07-28"
MAX_SCAN = 100

DELAY_THRESHOLD_MIN = int(os.environ.get("BP_DELAY_THRESHOLD_MIN", "60"))
HEARTBEAT_EVERY_HOURS = int(os.environ.get("BP_HEARTBEAT_HOURS", "24"))
ALIVE_STALE_MIN = int(os.environ.get("BP_ALIVE_STALE_MIN", "45"))  # scan every ~10m; 45m = missed >=4 runs

# ---- notification targets ----
SLACK_LEADS_CHANNEL = "C0B3QCD9UD7"      # #ai-blueprint-leads
MADISON_SLACK_ID = "U08H07FMDFA"
CODY_SLACK_ID = "U0AE3SP690D"
MADISON_TAG = f"<@{MADISON_SLACK_ID}>"
CODY_TAG = f"<@{CODY_SLACK_ID}>"
SMS_TO = "+12142153719"
SMS_SCRIPT = os.path.join(HOME, ".openclaw", "scripts", "notify-sms.sh")

# ---- detection signals ----
SOURCE_PREFIXES = ("blueprint_ai",)
SOURCE_EXACT = ("external_form",)
TAG_SIGNALS = {
    "blueprint ai lead", "blueprint_ai_apply", "blueprint_ai_qualifier",
    "ai-blueprint-opt-in", "ai blueprint opt-in", "blueprint ai opt-in",
    "blueprint-ai-opt-in", "blueprint ai apply",
}
PIPELINE_NAME_HINTS = ("blueprint",)  # a stage/pipeline whose name contains this
DELIVERED_TAGS = {"blueprint sent", "blueprint delivered", "blueprint_sent"}

# Poll BOTH accounts. loc_default lets it work even if the loc env var is absent.
ACCOUNTS = [
    {"name": "main-fki", "key_env": "GHL_API_KEY", "loc_env": "GHL_LOCATION_ID",
     "loc_default": "14RD8KklxR9G4e0Rf7v2"},
    {"name": "advaita", "key_env": "ADVAITA_GHL_PIT", "loc_env": "ADVAITA_GHL_LOCATION_ID",
     "loc_default": "GPCi3FrWJCyevcGzZgTT"},
]

# Test/QA leads never post to the real channel (memory: delay-watchdog-test-leads).
TEST_SLUG_PREFIXES = ("test-", "blueprint-repeat", "zztest", "zz-test")
TEST_EMAIL_MARKERS = ("test+", "formtest", "notif-test", "sentinel-selftest")


# ─────────────────────────── infra helpers ───────────────────────────
def _utcnow():
    return datetime.datetime.utcnow()


def _iso(dt=None):
    return (dt or _utcnow()).replace(microsecond=0).isoformat() + "Z"


def _parse_iso(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "").split(".")[0])
    except Exception:
        return None


def _load(path, default):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return default
    return default


def _save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _log_event(kind, payload):
    os.makedirs(LOGS_DIR, exist_ok=True)
    rec = {"ts": _iso(), "kind": kind, **payload}
    with open(EVENT_LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")


def load_env():
    env = dict(os.environ)
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env.setdefault(k.strip(), v.strip())
    return env


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").strip().lower())
    return s.strip("-")


def is_test_lead(lead):
    slug = lead.get("slug", "")
    email = (lead.get("email") or "").lower()
    if any(slug.startswith(p) for p in TEST_SLUG_PREFIXES):
        return True
    if any(m in email for m in TEST_EMAIL_MARKERS):
        return True
    return False


# ─────────────────────────── GHL ───────────────────────────
def ghl_get(url, key):
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {key}", "Version": GHL_VER, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def matches_signals(contact):
    """Return list of the detection signals this contact fires (empty = no match)."""
    signals = []
    src = (contact.get("source") or "").lower()
    if any(src.startswith(p) for p in SOURCE_PREFIXES):
        signals.append(f"source:{src}")
    if src in SOURCE_EXACT:
        signals.append(f"source:{src}")
    tags = [t.lower() for t in (contact.get("tags") or [])]
    for t in tags:
        if t in TAG_SIGNALS:
            signals.append(f"tag:{t}")
    return signals


def is_delivered_contact(contact):
    tags = [t.lower() for t in (contact.get("tags") or [])]
    return any(t in DELIVERED_TAGS for t in tags)


def fetch_leads(env):
    """Poll both accounts, return matched leads + a list of transport errors."""
    out, seen_ids, errors = [], set(), []
    for acct in ACCOUNTS:
        key = env.get(acct["key_env"])
        loc = env.get(acct["loc_env"], acct["loc_default"])
        if not key:
            errors.append(f"{acct['name']}: {acct['key_env']} missing from ~/.claude/.env")
            continue
        url = f"{GHL_BASE}/contacts/?locationId={loc}&limit={MAX_SCAN}"
        try:
            d = ghl_get(url, key)
        except Exception as e:  # one account down must not blind the other
            errors.append(f"{acct['name']}: {e}")
            continue
        for c in d.get("contacts", []):
            signals = matches_signals(c)
            if not signals:
                continue
            cid = c.get("id")
            if cid in seen_ids:
                continue
            seen_ids.add(cid)
            name = (c.get("contactName")
                    or ((c.get("firstName") or "") + " " + (c.get("lastName") or "")).strip()
                    or "(no name)")
            out.append({
                "id": cid, "name": name, "slug": slugify(name),
                "email": c.get("email") or "(no email)",
                "phone": c.get("phone") or "(no phone)",
                "source": c.get("source"), "tags": c.get("tags") or [],
                "dateAdded": c.get("dateAdded"), "account": acct["name"],
                "signals": signals, "delivered_in_ghl": is_delivered_contact(c),
            })
    return out, errors


# ─────────────────────────── notification transports ───────────────────────────
def slack_post(env, channel_id, text):
    """Post to Slack via bot token. Returns ts on success else None (never raises)."""
    token = env.get("SLACK_BOT_TOKEN")
    if not token:
        return None
    try:
        body = json.dumps({"channel": channel_id, "text": text}).encode()
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage", data=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        return d.get("ts") if d.get("ok") else None
    except Exception:
        return None


def sms(env, msg):
    if not os.path.exists(SMS_SCRIPT):
        return False
    try:
        return subprocess.run([SMS_SCRIPT, msg, SMS_TO], timeout=30).returncode == 0
    except Exception:
        return False


def kick_build(lead, dry_run):
    """Auto-start the build pipeline for a real lead. Best-effort, non-blocking."""
    if dry_run or is_test_lead(lead):
        return {"kicked": False, "reason": "dry_run_or_test"}
    orch = os.path.join(REPO_DIR, "scripts", "blueprint-pipeline-orchestrator.py")
    if not os.path.exists(orch):
        return {"kicked": False, "reason": "orchestrator_missing"}
    # Website URL is not always on the contact; orchestrator can research from name.
    try:
        p = subprocess.Popen(
            [sys.executable, orch, "--lead", lead["name"]],
            cwd=REPO_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"kicked": True, "pid": p.pid}
    except Exception as e:
        return {"kicked": False, "reason": str(e)}


# ─────────────────────────── notification composition ───────────────────────────
def new_lead_slack_text(lead):
    return (f":fire: *NEW BLUEPRINT LEAD* — {lead['name']} "
            f"({lead['email']} / {lead['phone']}) just came in. Build starting. "
            f"{MADISON_TAG} {CODY_TAG}\n"
            f"> account: `{lead['account']}` | source: `{lead['source']}` | "
            f"signals: {', '.join(lead['signals'])} | GHL id: `{lead['id']}`")


def delay_slack_text(lead, age_min):
    return (f":warning: *PRODUCTION DELAY* — {lead['name']} ({lead['slug']}) {MADISON_TAG} "
            f"has been in production {age_min} min with no delivery. "
            f"[signals: {', '.join(lead.get('signals', []))}] Needs attention.")


def heartbeat_text(counts):
    return (f":green_heart: Blueprint Sentinel alive @ {_iso()} — "
            f"{counts['seen']} leads seen, {counts['delivered']} delivered, "
            f"{counts['pending']} pending. (If this stops posting daily, the watcher is DOWN.)")


def enqueue(outbox, kind, lead, text, extra=None):
    key = f"{kind}:{lead['id']}" + (f":{extra}" if extra else "")
    if key in outbox["items"] and outbox["items"][key].get("slack_delivered"):
        return None
    outbox["items"][key] = {
        "kind": kind, "id": lead["id"], "name": lead["name"], "slug": lead["slug"],
        "email": lead["email"], "text": text, "queued_at": _iso(),
        "channel_id": SLACK_LEADS_CHANNEL, "slack_delivered": False, "slack_ts": None,
        "is_test": is_test_lead(lead),
    }
    return key


# ─────────────────────────── main scan ───────────────────────────
def deliver_item(env, item):
    """Try to actually push a queued notification through every available transport."""
    result = {"slack_ts": None, "sms": False}
    # Slack (only for non-test leads to the real channel; test leads go to Madison DM)
    if item.get("is_test"):
        result["slack_ts"] = slack_post(env, MADISON_SLACK_ID, "[TEST] " + item["text"])
    else:
        result["slack_ts"] = slack_post(env, item["channel_id"], item["text"])
    # SMS fallback (headless-capable, no Slack token needed) for new-lead + delay
    if item["kind"] in ("new_lead", "delay"):
        result["sms"] = sms(env, re.sub(r"[*_>`]", "", item["text"])[:300])
    return result


def scan(args):
    env = load_env()
    now = _utcnow()
    seen = _load(SEEN_FILE, None)
    outbox = _load(OUTBOX_FILE, {"items": {}})
    leads, errors = fetch_leads(env)

    # transport failure must be loud, not silent "no leads"
    if errors and not leads and seen is not None:
        _log_event("fetch_error", {"errors": errors})

    # ---------- baseline ----------
    if seen is None or args.baseline:
        seen = {"baselined_at": _iso(now), "leads": {}}
        for l in leads:
            seen["leads"][l["id"]] = {
                "slug": l["slug"], "name": l["name"], "email": l["email"],
                "source": l["source"], "signals": l["signals"], "account": l["account"],
                "first_seen": _iso(now), "delivered": l["delivered_in_ghl"],
                "delivered_at": _iso(now) if l["delivered_in_ghl"] else None,
            }
        _save(SEEN_FILE, seen)
        _save(OUTBOX_FILE, outbox)
        _log_event("baseline", {"count": len(leads)})
        stamp_heartbeat(seen, force=False)
        print(json.dumps({"baselined": len(seen["leads"]), "errors": errors}, indent=2))
        return

    known = seen.setdefault("leads", {})
    new_ids = []

    # ---------- detect NEW leads ----------
    for l in leads:
        if l["id"] not in known:
            known[l["id"]] = {
                "slug": l["slug"], "name": l["name"], "email": l["email"],
                "source": l["source"], "signals": l["signals"], "account": l["account"],
                "first_seen": _iso(now), "delivered": l["delivered_in_ghl"],
                "delivered_at": _iso(now) if l["delivered_in_ghl"] else None,
            }
            new_ids.append(l["id"])
            key = enqueue(outbox, "new_lead", l, new_lead_slack_text(l))
            _log_event("new_lead_detected", {"id": l["id"], "name": l["name"],
                                             "signals": l["signals"], "account": l["account"]})
            if not args.no_build:
                kb = kick_build(l, args.dry_run)
                _log_event("build_kick", {"id": l["id"], **kb})

    # ---------- refresh delivery status from GHL (Blueprint Sent tag) ----------
    live_by_id = {l["id"]: l for l in leads}
    for cid, rec in known.items():
        if rec.get("delivered"):
            continue
        # delivered if GHL now shows a delivered tag OR an approval token exists
        deliv = False
        if cid in live_by_id and live_by_id[cid]["delivered_in_ghl"]:
            deliv = True
        elif os.path.exists(os.path.join(APPROVE_DIR, rec["slug"] + ".approved")):
            deliv = True
        if deliv:
            rec["delivered"] = True
            rec["delivered_at"] = _iso(now)
            _log_event("delivered", {"id": cid, "name": rec["name"]})

    # ---------- DELAY alarm: undelivered past threshold ----------
    for cid, rec in known.items():
        if rec.get("delivered"):
            continue
        fs = _parse_iso(rec.get("first_seen"))
        age_min = int((now - fs).total_seconds() // 60) if fs else 0
        if age_min >= DELAY_THRESHOLD_MIN:
            lead = {"id": cid, "name": rec["name"], "slug": rec["slug"],
                    "email": rec["email"], "signals": rec.get("signals", [])}
            state = f"{(age_min // DELAY_THRESHOLD_MIN) * DELAY_THRESHOLD_MIN}min"
            key = enqueue(outbox, "delay", lead, delay_slack_text(lead, age_min), extra=state)
            if key:
                _log_event("delay_detected", {"id": cid, "age_min": age_min})

    # ---------- deliver everything queued (best-effort through all transports) ----------
    delivered_now = []
    for key, item in outbox["items"].items():
        if item.get("slack_delivered"):
            continue
        res = deliver_item(env, item)
        if res["slack_ts"]:
            item["slack_delivered"] = True
            item["slack_ts"] = res["slack_ts"]
            delivered_now.append(key)
        item["last_attempt"] = _iso(now)
        item["sms_ok"] = item.get("sms_ok") or res["sms"]

    _save(SEEN_FILE, seen)
    _save(OUTBOX_FILE, outbox)
    stamp_heartbeat(seen, force=False, env=env)

    counts = _counts(seen)
    pending = [k for k, v in outbox["items"].items() if not v.get("slack_delivered")]
    print(json.dumps({
        "new_leads": new_ids, "delivered_notifs_now": delivered_now,
        "undelivered_notifs": pending, "counts": counts,
        "slack_token_present": bool(env.get("SLACK_BOT_TOKEN")), "errors": errors,
    }, indent=2))


def _counts(seen):
    leads = seen.get("leads", {})
    delivered = sum(1 for r in leads.values() if r.get("delivered"))
    return {"seen": len(leads), "delivered": delivered, "pending": len(leads) - delivered}


def stamp_heartbeat(seen, force, env=None):
    hb = _load(HEARTBEAT_FILE, {})
    now = _utcnow()
    hb["last_run"] = _iso(now)
    counts = _counts(seen)
    hb["counts"] = counts
    last_beat = _parse_iso(hb.get("last_heartbeat_notif"))
    due = force or last_beat is None or \
        (now - last_beat).total_seconds() >= HEARTBEAT_EVERY_HOURS * 3600
    if due and env is not None:
        ts = slack_post(env, SLACK_LEADS_CHANNEL, heartbeat_text(counts))
        if ts:
            hb["last_heartbeat_notif"] = _iso(now)
            hb["last_heartbeat_ts"] = ts
    _save(HEARTBEAT_FILE, hb)


# ─────────────────────────── auxiliary modes ───────────────────────────
def mark_delivered(ids):
    seen = _load(SEEN_FILE, {"leads": {}})
    for cid in ids:
        if cid in seen.get("leads", {}):
            seen["leads"][cid]["delivered"] = True
            seen["leads"][cid]["delivered_at"] = _iso()
    _save(SEEN_FILE, seen)
    _log_event("manual_delivered", {"ids": ids})
    print(json.dumps({"marked_delivered": ids}))


def drain():
    """For a live Claude session: print undelivered outbox items to post via Slack MCP."""
    outbox = _load(OUTBOX_FILE, {"items": {}})
    pending = {k: v for k, v in outbox["items"].items() if not v.get("slack_delivered")}
    print(json.dumps({"pending": pending}, indent=2))


def mark_delivered_notif(keys):
    outbox = _load(OUTBOX_FILE, {"items": {}})
    for k in keys:
        if k in outbox["items"]:
            outbox["items"][k]["slack_delivered"] = True
            outbox["items"][k]["slack_ts"] = "posted-by-session"
    _save(OUTBOX_FILE, outbox)
    print(json.dumps({"marked": keys}))


def check_alive():
    hb = _load(HEARTBEAT_FILE, {})
    last = _parse_iso(hb.get("last_run"))
    if last is None:
        print(json.dumps({"alive": False, "reason": "never ran"}))
        sys.exit(2)
    age = int((_utcnow() - last).total_seconds() // 60)
    alive = age <= ALIVE_STALE_MIN
    print(json.dumps({"alive": alive, "last_run": hb.get("last_run"),
                      "age_min": age, "stale_threshold_min": ALIVE_STALE_MIN,
                      "counts": hb.get("counts")}))
    sys.exit(0 if alive else 2)


def self_test(email):
    """Inject a fake matched lead directly into the seen-diff path for the E2E test,
    by writing it into a scratch file the caller can point --self-test-from at.
    Simpler: we just push a synthetic 'new_lead' into the outbox and deliver it."""
    env = load_env()
    outbox = _load(OUTBOX_FILE, {"items": {}})
    lead = {"id": f"SELFTEST-{int(_utcnow().timestamp())}", "name": "Sentinel Selftest",
            "slug": "sentinel-selftest", "email": email, "phone": "+10000000000",
            "source": "self_test", "account": "self-test", "signals": ["self_test"]}
    key = enqueue(outbox, "new_lead", lead,
                  f":test_tube: SENTINEL SELF-TEST — {lead['name']} ({email}) "
                  f"synthetic lead to prove the alert path fires. {MADISON_TAG}")
    res = deliver_item(env, outbox["items"][key])
    if res["slack_ts"]:
        outbox["items"][key]["slack_delivered"] = True
        outbox["items"][key]["slack_ts"] = res["slack_ts"]
    _save(OUTBOX_FILE, outbox)
    print(json.dumps({"self_test": True, "key": key, "result": res,
                      "slack_token_present": bool(env.get("SLACK_BOT_TOKEN"))}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--once", action="store_true")  # accepted, scan is single-shot anyway
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--delivered", nargs="+")
    ap.add_argument("--drain", action="store_true")
    ap.add_argument("--mark-delivered-notif", nargs="+")
    ap.add_argument("--check-alive", action="store_true")
    ap.add_argument("--self-test")
    args = ap.parse_args()

    if args.delivered:
        return mark_delivered(args.delivered)
    if args.drain:
        return drain()
    if args.mark_delivered_notif:
        return mark_delivered_notif(args.mark_delivered_notif)
    if args.check_alive:
        return check_alive()
    if args.self_test:
        return self_test(args.self_test)
    scan(args)


if __name__ == "__main__":
    main()
