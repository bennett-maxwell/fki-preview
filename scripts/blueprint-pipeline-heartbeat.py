#!/usr/bin/env python3
"""blueprint-pipeline-heartbeat.py — DECOUPLE watchdog (2026-07-07).

Now that the customer SEND is gated on the PAGE only and the podcast is a NON-BLOCKING
async enrichment, a stalled podcast (or a stalled lead intake) is silent instead of
blocking. This heartbeat closes that gap: it runs on a schedule (launchd) and alerts
#ai-blueprint-leads (+ best-effort SMS) when the pipeline looks stuck. It ALERTS if ANY:

  1. 0 new form leads in > LEADS_STALE_HOURS (default 12h)
  2. NotebookLM auth stale (`notebooklm list` errors / non-zero exit)
  3. a lead at Stage-1 with its page NOT shipped > STAGE1_UNSHIPPED_HOURS (default 1h)
  4. a podcast pending > PODCAST_PENDING_HOURS (default 6h) for a shipped page
  5. the notification outbox has delivered=0 while work is pending

Modeled on scripts/blueprint-lead-sentinel.py (ops/state/sentinel-*.json) + the Slack
pattern in scripts/blueprint-pipeline-orchestrator.py.

Usage:
  python3 scripts/blueprint-pipeline-heartbeat.py --check            # run once, alert on issues
  python3 scripts/blueprint-pipeline-heartbeat.py --check --dry-run  # run once, print only (no send)

launchd wiring: ops/launchd/com.fki.blueprint-pipeline-heartbeat.plist runs `--check`
every 30 min. Install with:
  cp ops/launchd/com.fki.blueprint-pipeline-heartbeat.plist ~/Library/LaunchAgents/
  launchctl load ~/Library/LaunchAgents/com.fki.blueprint-pipeline-heartbeat.plist
"""
import os
import sys
import json
import time
import shutil
import argparse
import datetime
import subprocess
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(REPO, "ops", "state")
BP_DIR = os.path.join(REPO, "blueprints")
POD_DIR = os.path.join(REPO, "podcasts")
LEADS_DIR = os.path.join(REPO, "leads")
SEEN_PATH = os.path.join(STATE_DIR, "sentinel-seen.json")
OUTBOX_PATH = os.path.join(STATE_DIR, "sentinel-outbox.json")
SENTINEL_HB_PATH = os.path.join(STATE_DIR, "sentinel-heartbeat.json")
HB_STATE_PATH = os.path.join(STATE_DIR, "pipeline-heartbeat.json")

SLACK_AI_BLUEPRINT = "C0B3QCD9UD7"  # #ai-blueprint-leads

# Thresholds (env-overridable)
LEADS_STALE_HOURS = float(os.environ.get("HB_LEADS_STALE_HOURS", "12"))
STAGE1_UNSHIPPED_HOURS = float(os.environ.get("HB_STAGE1_UNSHIPPED_HOURS", "1"))
PODCAST_PENDING_HOURS = float(os.environ.get("HB_PODCAST_PENDING_HOURS", "6"))


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def hours_since(ts):
    dt = parse_ts(ts) if isinstance(ts, str) else ts
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return (now_utc() - dt).total_seconds() / 3600.0


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def is_test_slug(slug, name=""):
    blob = f"{slug} {name}".lower()
    return any(t in blob for t in ("test", "ignore", "example", "sample", "demo"))


# ── Checks ────────────────────────────────────────────────────────────────────

def check_form_leads_freshness():
    """1. 0 new form leads in > LEADS_STALE_HOURS."""
    newest = None
    seen = load_json(SEEN_PATH, {}).get("leads", {})
    for meta in seen.values():
        if is_test_slug(meta.get("slug", ""), meta.get("name", "")):
            continue
        ts = parse_ts(meta.get("first_seen"))
        if ts and (newest is None or ts > newest):
            newest = ts
    # Fallback: newest real lead JSON on disk
    try:
        for fn in os.listdir(LEADS_DIR):
            if not fn.endswith(".json") or fn.endswith(".bak") or is_test_slug(fn):
                continue
            mt = datetime.datetime.fromtimestamp(
                os.path.getmtime(os.path.join(LEADS_DIR, fn)), datetime.timezone.utc)
            if newest is None or mt > newest:
                newest = mt
    except Exception:
        pass
    if newest is None:
        return f"No form-lead intake timestamps found (seen + leads/ both empty)."
    age = hours_since(newest)
    if age is not None and age > LEADS_STALE_HOURS:
        return f"No new form leads in {age:.1f}h (threshold {LEADS_STALE_HOURS:.0f}h). Intake may be stalled."
    return None


def check_notebooklm_auth():
    """2. NotebookLM auth stale (`notebooklm list` errors)."""
    exe = shutil.which("notebooklm") or os.path.expanduser("~/.pyenv/shims/notebooklm")
    if not os.path.exists(exe):
        return None  # CLI not installed on this host — cannot assert stale, skip.
    try:
        proc = subprocess.run([exe, "list"], capture_output=True, text=True, timeout=90)
    except Exception as e:
        return f"NotebookLM auth check could not run ({e}); podcast generation may be blocked."
    out = (proc.stdout + "\n" + proc.stderr).lower()
    if proc.returncode != 0 or any(t in out for t in ("auth", "login", "expired", "unauthor", "credential", "refresh")):
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        detail = tail[-1] if tail else f"exit {proc.returncode}"
        return f"NotebookLM auth appears STALE (`notebooklm list` -> {detail}). Refresh auth; podcasts blocked."
    return None


def check_stage1_unshipped():
    """3. A lead at Stage-1 with its page not shipped > STAGE1_UNSHIPPED_HOURS."""
    seen = load_json(SEEN_PATH, {}).get("leads", {})
    stalled = []
    for meta in seen.values():
        slug = meta.get("slug", "")
        if not slug or is_test_slug(slug, meta.get("name", "")):
            continue
        if meta.get("delivered"):
            continue
        age = hours_since(meta.get("first_seen"))
        if age is None or age <= STAGE1_UNSHIPPED_HOURS:
            continue
        # "page shipped" == a blueprint HTML exists for the slug (exact or dated)
        exact = os.path.join(BP_DIR, f"{slug}.html")
        dated = [f for f in os.listdir(BP_DIR)
                 if f.startswith(slug + "-") and f.endswith(".html")] if os.path.isdir(BP_DIR) else []
        if not os.path.exists(exact) and not dated:
            stalled.append(f"{slug} ({age:.1f}h)")
    if stalled:
        return f"{len(stalled)} lead(s) at Stage-1 with NO page shipped > {STAGE1_UNSHIPPED_HOURS:.0f}h: {', '.join(stalled[:8])}"
    return None


def check_podcast_pending():
    """4. A podcast pending > PODCAST_PENDING_HOURS for a page that already shipped."""
    seen = load_json(SEEN_PATH, {}).get("leads", {})
    pending = []
    for meta in seen.values():
        slug = meta.get("slug", "")
        if not slug or is_test_slug(slug, meta.get("name", "")):
            continue
        # find the shipped page (exact or newest dated)
        candidates = []
        exact = os.path.join(BP_DIR, f"{slug}.html")
        if os.path.exists(exact):
            candidates.append(exact)
        if os.path.isdir(BP_DIR):
            candidates += [os.path.join(BP_DIR, f) for f in os.listdir(BP_DIR)
                           if f.startswith(slug + "-") and f.endswith(".html")]
        if not candidates:
            continue  # page not shipped -> that's check #3, not this one
        page = max(candidates, key=os.path.getmtime)
        page_slug = os.path.basename(page)[:-5]
        mp3 = os.path.join(POD_DIR, f"{page_slug}.mp3")
        page_age = hours_since(datetime.datetime.fromtimestamp(
            os.path.getmtime(page), datetime.timezone.utc))
        if not os.path.exists(mp3) and page_age is not None and page_age > PODCAST_PENDING_HOURS:
            pending.append(f"{page_slug} ({page_age:.1f}h)")
    if pending:
        return f"{len(pending)} podcast(s) pending > {PODCAST_PENDING_HOURS:.0f}h after page shipped: {', '.join(pending[:8])}"
    return None


def check_outbox_delivery():
    """5. Notification outbox delivered=0 while work is pending."""
    hb = load_json(SENTINEL_HB_PATH, {})
    counts = hb.get("counts", {}) if isinstance(hb, dict) else {}
    delivered = counts.get("delivered")
    pending = counts.get("pending")
    outbox = load_json(OUTBOX_PATH, {}).get("items", {})
    undelivered = sum(1 for v in outbox.values() if not v.get("slack_delivered"))
    if delivered == 0 and (pending or 0) > 0:
        return (f"Notification outbox delivered=0 with {pending} pending "
                f"({undelivered} undelivered items). Alert delivery is broken.")
    if delivered is None and undelivered > 0:
        return f"Notification outbox has {undelivered} undelivered item(s) and no delivery counter."
    return None


CHECKS = [
    ("form_leads_freshness", check_form_leads_freshness),
    ("notebooklm_auth", check_notebooklm_auth),
    ("stage1_unshipped", check_stage1_unshipped),
    ("podcast_pending", check_podcast_pending),
    ("outbox_delivery", check_outbox_delivery),
]


# ── Notifications ───────────────────────────────────────────────────────────────

def _slack_token():
    tok = os.environ.get("SLACK_BOT_TOKEN", "")
    if tok:
        return tok
    cfg = os.path.join(os.path.expanduser("~"), ".openclaw", "openclaw.json")
    if os.path.exists(cfg):
        try:
            return json.load(open(cfg)).get("slack_bot_token", "")
        except Exception:
            return ""
    return ""


def post_slack(text, channel):
    tok = _slack_token()
    if not tok:
        print("  [slack] no SLACK_BOT_TOKEN — skipped")
        return False
    try:
        payload = json.dumps({"channel": channel, "text": text}).encode()
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=payload,
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
        )
        resp = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
        if not resp.get("ok"):
            print(f"  [slack] API error: {resp.get('error')}")
            return False
        print("  [slack] posted")
        return True
    except Exception as e:
        print(f"  [slack] failed: {e}")
        return False


def send_sms(text):
    """Best-effort Twilio SMS. Silently skips unless all env vars are present."""
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth = os.environ.get("TWILIO_AUTH_TOKEN")
    frm = os.environ.get("TWILIO_FROM")
    to = os.environ.get("HB_ALERT_SMS_TO") or os.environ.get("ALERT_SMS_TO")
    if not (sid and auth and frm and to):
        print("  [sms] Twilio env not fully set — skipped (best-effort)")
        return False
    try:
        import base64
        import urllib.parse
        data = urllib.parse.urlencode({"From": frm, "To": to, "Body": text[:1400]}).encode()
        req = urllib.request.Request(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            data=data,
            headers={"Authorization": "Basic " + base64.b64encode(f"{sid}:{auth}".encode()).decode()},
        )
        urllib.request.urlopen(req, timeout=10)
        print("  [sms] sent")
        return True
    except Exception as e:
        print(f"  [sms] failed: {e}")
        return False


def write_state(alerts):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        json.dump({
            "last_run": now_utc().isoformat().replace("+00:00", "Z"),
            "alert_count": len(alerts),
            "alerts": alerts,
        }, open(HB_STATE_PATH, "w"), indent=2)
    except Exception as e:
        print(f"  [state] write failed: {e}")


def run_once(dry_run, channel):
    print(f"[heartbeat] {now_utc().isoformat()} — running {len(CHECKS)} checks (dry_run={dry_run})")
    alerts = []
    for name, fn in CHECKS:
        try:
            msg = fn()
        except Exception as e:
            msg = f"check '{name}' crashed: {e}"
        status = "ALERT" if msg else "ok"
        print(f"  - {name:22s} {status}{(': ' + msg) if msg else ''}")
        if msg:
            alerts.append(f"[{name}] {msg}")
    write_state(alerts)
    if not alerts:
        print("[heartbeat] all clear.")
        return 0
    text = ":rotating_light: *Blueprint pipeline heartbeat* — {n} issue(s):\n{body}".format(
        n=len(alerts), body="\n".join(f"• {a}" for a in alerts))
    print(f"[heartbeat] {len(alerts)} issue(s) detected.")
    if dry_run:
        print("[heartbeat] --dry-run: not sending Slack/SMS.\n---\n" + text + "\n---")
        return 0
    post_slack(text, channel)
    send_sms(f"Blueprint pipeline: {len(alerts)} issue(s). " + " | ".join(a.split('] ', 1)[-1] for a in alerts)[:1200])
    return 0


def main():
    p = argparse.ArgumentParser(description="Blueprint pipeline heartbeat watchdog")
    p.add_argument("--check", action="store_true", help="Run all checks once and alert on issues")
    p.add_argument("--dry-run", action="store_true", help="Print results only; do not send Slack/SMS")
    p.add_argument("--channel", default=SLACK_AI_BLUEPRINT, help="Slack channel id for alerts")
    args = p.parse_args()
    if not args.check:
        p.print_help()
        sys.exit(2)
    sys.exit(run_once(args.dry_run, args.channel))


if __name__ == "__main__":
    main()
