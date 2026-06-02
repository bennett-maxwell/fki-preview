#!/usr/bin/env python3
"""
blueprint_idempotency.py — Idempotency key for the Blueprint pipeline poller.
=============================================================================
PURPOSE
  The com.advaita.blueprint-pipeline LaunchAgent fires every 900s (15 min) and
  calls blueprint-pipeline-orchestrator.py with NO pending filter — it reloads
  EVERY leads/*.json each cycle and re-runs the full 7.5-stage pipeline (incl.
  git commit). Per-lead status.json makes individual STAGES restart-safe, but
  there is no guard against re-processing a lead whose INPUT CONTENT is
  unchanged. That re-processing is the divergent-dupe / wasted-cost engine.

WHAT THIS ADDS (additive, reversible, inert until imported)
  A content-addressed idempotency key. For each lead we compute a stable
  sha256 over the *semantic input fields* (not volatile timestamps). If a lead
  with the SAME slug + SAME input_hash already completed, re-running is a NO-OP.

  - compute_input_hash(profile) -> 16-hex digest over canonical input fields.
  - ensure_schema(conn)         -> adds input_hash + idempotency columns if absent
                                   (idempotent ALTER; safe to call every run).
  - should_skip(conn, profile)  -> True if this exact input already completed.
  - record_completion(conn, profile, batch_id) -> stamp hash after a real run.

REVERT
  Delete this file and remove the 3-line call sites from the orchestrator
  (see blueprint-idempotency.patch). The ALTER-added columns are harmless if
  left in place (nullable, defaulted).

DETERMINISM
  Fields are sorted and JSON-serialized with sort_keys=True so hash is stable
  across runs/machines. VOLATILE fields (any *_ts, status, completed_at,
  last_updated, batch_id) are EXCLUDED so a pure re-run does not bust the key.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone

# Fields that define the SEMANTIC INPUT of a blueprint. If any of these change,
# the lead legitimately needs regeneration and the key SHOULD bust.
INPUT_FIELDS = (
    "lead_name",
    "lead_first_name",
    "business_name",
    "slug",
    "url",
    "website_url",
    "accent_color",
    "industry",
    "services",
    "tools",
    "market",
    "service_type",
    "speed_to_lead_context",
    "phone",
    "email",
    "years_in_business",
    "key_metric",
    "key_metric_label",
    "team_size",
    "monthly_leads",
    "prompt_1",
    "prompt_2",
    "prompt_3",
    "cta_text",
)

# Fields explicitly NOT part of the key (volatile / derived). Documented so a
# future maintainer does not accidentally add a timestamp to INPUT_FIELDS.
_EXCLUDED = (
    "status", "completed_at", "last_updated", "batch_id",
    "blueprint_ts", "website_ts", "email_ts", "podcast_ts",
    "blueprint_url", "podcast_url", "podcast_drive_id", "apply_url",
)


def compute_input_hash(profile: dict) -> str:
    """Stable 16-hex content hash over canonical input fields only."""
    canonical = {k: profile.get(k, "") for k in INPUT_FIELDS}
    blob = json.dumps(canonical, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Add idempotency columns to the existing `leads` table if missing.
    Idempotent: safe to call on every poller run."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(leads)").fetchall()}
    if "input_hash" not in cols:
        conn.execute("ALTER TABLE leads ADD COLUMN input_hash TEXT")
    if "last_input_hash_completed" not in cols:
        conn.execute("ALTER TABLE leads ADD COLUMN last_input_hash_completed TEXT")
    if "idempotent_skips" not in cols:
        conn.execute("ALTER TABLE leads ADD COLUMN idempotent_skips INTEGER DEFAULT 0")
    conn.commit()


def should_skip(conn: sqlite3.Connection, profile: dict) -> bool:
    """True if this exact input (slug + input_hash) already COMPLETED.
    On a True result the caller increments the skip counter and no-ops the lead,
    eliminating duplicate generation + duplicate git churn."""
    slug = profile.get("slug")
    if not slug:
        return False
    h = compute_input_hash(profile)
    row = conn.execute(
        "SELECT status, last_input_hash_completed FROM leads WHERE slug = ?",
        (slug,),
    ).fetchone()
    if not row:
        return False
    status, last_done_hash = row[0], row[1]
    hit = status == "complete" and last_done_hash == h
    if hit:
        conn.execute(
            "UPDATE leads SET idempotent_skips = COALESCE(idempotent_skips,0)+1 WHERE slug = ?",
            (slug,),
        )
        conn.commit()
    return hit


def record_completion(conn: sqlite3.Connection, profile: dict, batch_id: str = "") -> str:
    """Stamp the completed input_hash after a REAL successful run so the next
    poller cycle treats an unchanged lead as a no-op. Returns the hash."""
    slug = profile.get("slug")
    h = compute_input_hash(profile)
    conn.execute(
        "UPDATE leads SET input_hash = ?, last_input_hash_completed = ?, "
        "completed_at = ?, batch_id = ? WHERE slug = ?",
        (h, h, datetime.now(timezone.utc).isoformat(), batch_id, slug),
    )
    conn.commit()
    return h


# ── Self-test (run directly: python3 blueprint_idempotency.py) ───────────────
if __name__ == "__main__":
    import sys, tempfile, os
    db = os.path.join(tempfile.mkdtemp(), "t.db")
    c = sqlite3.connect(db)
    c.execute("CREATE TABLE leads (id TEXT PRIMARY KEY, slug TEXT UNIQUE, "
              "lead_name TEXT, status TEXT DEFAULT 'pending', completed_at TEXT, batch_id TEXT)")
    c.execute("INSERT INTO leads (id, slug, lead_name) VALUES ('x','acme','Acme')")
    c.commit()
    ensure_schema(c)
    p = {"slug": "acme", "lead_name": "Acme", "business_name": "Acme", "industry": "hvac"}

    assert should_skip(c, p) is False, "pending lead must NOT skip"
    c.execute("UPDATE leads SET status='complete' WHERE slug='acme'")
    c.commit()
    record_completion(c, p)
    assert should_skip(c, p) is True, "unchanged completed lead MUST skip"

    p2 = dict(p, services="new service added")  # input changed
    assert should_skip(c, p2) is False, "changed input MUST bust the key"

    # volatile-only change must NOT bust
    p3 = dict(p, blueprint_ts="2026-05-31T00:00:00Z", status="whatever")
    assert compute_input_hash(p3) == compute_input_hash(p), "volatile fields must not affect hash"

    skips = c.execute("SELECT idempotent_skips FROM leads WHERE slug='acme'").fetchone()[0]
    assert skips == 1, f"skip counter should be 1, got {skips}"
    print("blueprint_idempotency self-test: ALL PASS (5 assertions)")
    sys.exit(0)
