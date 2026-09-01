#!/usr/bin/env python3
"""blueprint_send_token.py — THE Blueprint send token surface (mint + verify).

Madison directive 2026-08-11 (marker BLUEPRINT-SEND-TOKEN-AUDIT-GATE-CANONICAL-20260811):
`blueprint_gatekeeper_100.py` is RETIRED as the send-token authority. `scripts/audit-gate.sh` is
the token, because it is the hash-bound 100%-conformance token the audit skill's Hard-100 gate
actually specifies, and it is the only one the pipeline can currently satisfy.

Why gatekeeper-100 was retired (evidence, 2026-08-10):
  - It demanded `*-desktop-render.json`, `*-mobile-render.json`, `*-audit.json` and
    `*-closeout.json` receipts that `clone-blueprint.sh` never emits (it emits completion-gate /
    clean-ending / production-47), so it could not pass on a normally-built lead.
  - Repo-wide: 10 pass tokens vs 33 fail receipts, and recently-delivered leads (sue-wright,
    karen-melting-pot-studio) carry NO token at all — the send path had silently stopped using it.
  - It also carried a stale 480-720s podcast window against canon's 240-960s.
  A gate that cannot pass gets routed around, and a gate that gets routed around protects nothing.

What this preserves — the property that actually matters:
  The token is bound to the SHA256 of the EXACT delivery-email bytes. Edit the email after minting
  and the token no longer authorizes it. "Approved" means "these exact bytes were audited at 100%".

Usage:
  python3 scripts/blueprint_send_token.py --mint   <slug>   # runs audit-gate.sh, mints token
  python3 scripts/blueprint_send_token.py --verify <slug>   # exit 0 only if token matches bytes
  python3 scripts/blueprint_send_token.py --self-test       # bad/good/tamper canaries
Optional: --email <path> --blueprint <path> (default to the conventional per-slug paths)
"""
import argparse, hashlib, json, os, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPROVE_DIR = os.path.expanduser("~/.openclaw/state/blueprint-approvals")


def email_path(slug, override=None):
    return override or os.path.join(REPO, "delivery-emails", f"{slug}-delivery-email.html")


def blueprint_path(slug, override=None):
    return override or os.path.join(REPO, "blueprints", f"{slug}.html")


def token_path(slug):
    return os.path.join(APPROVE_DIR, f"{slug}.approved")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mint(slug, email, blueprint):
    if not os.path.exists(email):
        print(f"BLOCKED {slug}: delivery email not found: {email}")
        return 1
    cmd = ["bash", os.path.join(REPO, "scripts", "audit-gate.sh"), slug, email]
    if blueprint and os.path.exists(blueprint):
        cmd.append(blueprint)
    p = subprocess.run(cmd, cwd=REPO, text=True, capture_output=True)
    tail = (p.stdout + p.stderr).strip().splitlines()[-6:]
    print("\n".join(tail))
    if p.returncode != 0:
        print(f"BLOCKED {slug}: audit-gate did not reach 100% — no token minted")
        return 1
    return verify(slug, email)


def verify(slug, email):
    tp = token_path(slug)
    if not os.path.exists(tp):
        print(f"BLOCKED {slug}: no send token at {tp} — run --mint first")
        return 1
    try:
        t = json.load(open(tp, encoding="utf-8"))
    except Exception as e:
        print(f"BLOCKED {slug}: token unreadable ({e})")
        return 1
    if t.get("score") != 100 or t.get("red_line_pass") is not True:
        print(f"BLOCKED {slug}: token is not a 100%/red-line-clean token: "
              f"score={t.get('score')} red_line_pass={t.get('red_line_pass')}")
        return 1
    if not os.path.exists(email):
        print(f"BLOCKED {slug}: delivery email not found: {email}")
        return 1
    actual = sha256_file(email)
    approved = t.get("approved_html_sha256")
    if actual != approved:
        print(f"BLOCKED {slug}: TOKEN/BYTES MISMATCH — the email changed after the token was minted.\n"
              f"  token approved sha256 = {approved}\n  current  email sha256 = {actual}\n"
              f"  Re-run --mint on the current bytes.")
        return 1
    print(f"PASS {slug}: send token valid and hash-bound to the exact email bytes "
          f"(sha256={actual[:16]}…, minted {t.get('minted_at')})")
    return 0


def self_test():
    """bad -> blocked, good -> pass, tampered -> blocked. Uses a scratch slug; touches no real lead."""
    slug = "_sendtoken_selftest"
    tp = token_path(slug)
    em = os.path.join(tempfile.gettempdir(), f"{slug}.html")
    open(em, "w").write("<html><body>canary v1</body></html>")
    fails = []
    if os.path.exists(tp):
        os.remove(tp)

    # 1. BAD: no token at all must block
    if verify(slug, em) == 0:
        fails.append("no-token did NOT block")

    # 2. GOOD: a hand-built valid token for these exact bytes must pass
    os.makedirs(APPROVE_DIR, exist_ok=True)
    json.dump({"slug": slug, "score": 100, "red_line_pass": True,
               "approved_html_sha256": sha256_file(em), "minted_at": "canary"},
              open(tp, "w"))
    if verify(slug, em) != 0:
        fails.append("valid token did NOT pass")

    # 3. TAMPER: change the email after minting -> must block (the whole point of hash-binding)
    open(em, "w").write("<html><body>canary v2 TAMPERED</body></html>")
    if verify(slug, em) == 0:
        fails.append("tampered bytes did NOT block")

    # 4. BAD: sub-100 score must block even with a matching hash
    json.dump({"slug": slug, "score": 92, "red_line_pass": True,
               "approved_html_sha256": sha256_file(em), "minted_at": "canary"},
              open(tp, "w"))
    if verify(slug, em) == 0:
        fails.append("score<100 did NOT block")

    os.remove(tp); os.remove(em)
    print("\n--- SELF-TEST ---")
    for f in fails:
        print(f"  FAIL: {f}")
    print("  4/4 canaries behaved correctly" if not fails else f"  {len(fails)} canary failure(s)")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mint", metavar="SLUG")
    ap.add_argument("--verify", metavar="SLUG")
    ap.add_argument("--email")
    ap.add_argument("--blueprint")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    slug = a.mint or a.verify
    if not slug:
        ap.error("need --mint SLUG, --verify SLUG, or --self-test")
    em = email_path(slug, a.email)
    if a.mint:
        return mint(slug, em, blueprint_path(slug, a.blueprint))
    return verify(slug, em)


if __name__ == "__main__":
    sys.exit(main())
