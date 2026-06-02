#!/usr/bin/env python3
"""
Chrome → NotebookLM CLI cookie bridge.
Reads Google session cookies from Chrome's SQLite DB, decrypts them using
the macOS Keychain Chrome Safe Storage key, and injects them into the
notebooklm Playwright storage_state.json so the CLI stays authenticated
as long as Chrome is logged into Google.

Run manually or via LaunchAgent every 12h.
"""

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from hashlib import pbkdf2_hmac
from pathlib import Path

from Crypto.Cipher import AES

# Profile 29 = madison@franchiseki.com — the Google account that owns the NotebookLM
# notebooks. (Was Profile 4 / madison@pulsarhalo.com, whose cookies went stale in Jul 2025
# and caused "Authentication expired" failures.)
CHROME_COOKIES = Path.home() / "Library/Application Support/Google/Chrome/Profile 29/Cookies"
NLM_STORAGE    = Path.home() / ".notebooklm/profiles/default/storage_state.json"
TMP_DB         = Path("/tmp/chrome_nlm_cookies.db")
LOG            = Path.home() / ".openclaw/logs/chrome-cookie-bridge.log"

GOOGLE_HOSTS = {
    ".google.com",
    "accounts.google.com",
    "notebooklm.google.com",
    ".notebooklm.google.com",
}

REQUIRED_COOKIE_NAMES = {"__Secure-1PSID", "__Secure-3PSID", "SID", "HSID", "SSID", "APISID", "SAPISID"}


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{stamp} {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def get_chrome_key() -> bytes:
    raw = subprocess.check_output(
        ["security", "find-generic-password", "-w", "-s", "Chrome Safe Storage"],
        stderr=subprocess.DEVNULL,
    ).strip()
    return pbkdf2_hmac("sha1", raw, b"saltysalt", 1003)[:16]


def decrypt_value(enc: bytes, key: bytes) -> str:
    if not enc:
        return ""
    if enc[:3] == b"v10":
        body = enc[3:]
        cipher = AES.new(key, AES.MODE_CBC, IV=b" " * 16)
        dec = cipher.decrypt(body)
        # Chrome prepends a 32-byte fixed header before encrypting — skip it
        dec = dec[32:]
        # Remove PKCS7 padding
        pad = dec[-1]
        if 1 <= pad <= 16:
            dec = dec[:-pad]
        try:
            result = dec.decode("utf-8")
            if all(0x20 <= ord(c) < 0x7F for c in result):
                return result
        except Exception:
            pass
        return ""
    return enc.decode("utf-8", errors="replace")


def chrome_epoch_to_unix(chrome_ts: int) -> float:
    """Chrome timestamps are microseconds since Jan 1 1601."""
    if chrome_ts == 0:
        return 0.0
    return (chrome_ts / 1_000_000) - 11644473600


def extract_cookies(key: bytes) -> list[dict]:
    if not CHROME_COOKIES.exists():
        log("ERROR: Chrome cookie DB not found")
        sys.exit(1)
    shutil.copy2(CHROME_COOKIES, TMP_DB)
    conn = sqlite3.connect(TMP_DB)
    conn.row_factory = sqlite3.Row
    # Return every column as raw bytes so a non-UTF-8 text cell can't crash fetchall();
    # we decode the genuinely-text columns ourselves and leave encrypted_value as bytes.
    conn.text_factory = bytes
    rows = conn.execute(
        "SELECT host_key, name, encrypted_value, value, path, expires_utc, "
        "is_secure, is_httponly, samesite FROM cookies "
        "WHERE host_key LIKE '%.google.com' OR host_key = 'accounts.google.com'"
    ).fetchall()
    conn.close()
    TMP_DB.unlink(missing_ok=True)

    def s(b):  # decode a text column that text_factory handed back as bytes
        return b.decode("utf-8", "replace") if isinstance(b, (bytes, bytearray)) else b

    cookies = []
    for r in rows:
        enc = r["encrypted_value"]
        val = decrypt_value(enc, key) if enc else s(r["value"])
        expires = chrome_epoch_to_unix(r["expires_utc"])
        same_site_map = {-1: "None", 0: "None", 1: "Lax", 2: "Strict"}
        cookies.append({
            "name": s(r["name"]),
            "value": val,
            "domain": s(r["host_key"]),
            "path": s(r["path"]),
            "expires": expires if expires > 0 else -1,
            "httpOnly": bool(r["is_httponly"]),
            "secure": bool(r["is_secure"]),
            "sameSite": same_site_map.get(r["samesite"], "None"),
        })
    return cookies


def build_storage_state(cookies: list[dict]) -> dict:
    return {
        "cookies": cookies,
        "origins": [],
    }


def verify_auth(cookies: list[dict]) -> bool:
    names = {c["name"] for c in cookies}
    have = REQUIRED_COOKIE_NAMES & names
    log(f"Auth cookies found: {sorted(have)}")
    return bool({"SID", "__Secure-1PSID", "__Secure-3PSID"} & names)


def main():
    log("=== chrome-cookie-bridge start ===")

    if not CHROME_COOKIES.exists():
        log("Chrome cookie DB not found — is Chrome installed?")
        sys.exit(1)

    log("Fetching Chrome Safe Storage key from Keychain...")
    try:
        key = get_chrome_key()
    except subprocess.CalledProcessError:
        log("ERROR: Could not read Chrome Safe Storage key — Chrome must be running/unlocked")
        sys.exit(1)

    log("Extracting Google cookies from Chrome...")
    cookies = extract_cookies(key)
    log(f"  {len(cookies)} Google cookies extracted")

    if not verify_auth(cookies):
        log("ERROR: Required Google session cookies missing — make sure you are logged into Chrome")
        sys.exit(1)

    NLM_STORAGE.parent.mkdir(parents=True, exist_ok=True)
    state = build_storage_state(cookies)
    NLM_STORAGE.write_text(json.dumps(state, indent=2))
    log(f"storage_state.json written to {NLM_STORAGE}")

    # Quick sanity: try notebooklm list
    log("Testing notebooklm auth...")
    nlm = shutil.which("notebooklm") or str(Path.home() / ".pyenv/versions/3.11.9/bin/notebooklm")
    result = subprocess.run([nlm, "list", "--json"], capture_output=True, text=True, timeout=30)
    if result.returncode == 0 and "error" not in result.stdout.lower():
        log("✅ notebooklm auth VALID — CLI authenticated from Chrome cookies")
    else:
        log(f"⚠️  notebooklm test returned: {result.stdout[:200]} {result.stderr[:200]}")

    log("=== chrome-cookie-bridge complete ===")


if __name__ == "__main__":
    main()
