#!/usr/bin/env python3
"""
blueprint-podcast-worker.py — Async Podcast Generation Worker
=============================================================
Processes HOT leads from the podcast_queue SQLite table.
Generates NotebookLM source docs and queues for podcast generation.
Rate-limited to ~50/day (NotebookLM unofficial API constraint).

Runs via LaunchAgent every 30 minutes. Processes up to 5 leads per run.

Usage:
  python3 blueprint-podcast-worker.py
  python3 blueprint-podcast-worker.py --max 10
  python3 blueprint-podcast-worker.py --dry-run
"""

import asyncio
import json
import logging
import importlib.util
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".openclaw" / "state"
DB_PATH = STATE_DIR / "blueprint-dedup.db"
REPO_DIR = Path(__file__).resolve().parent.parent
LEADS_DIR = REPO_DIR / "leads"
PODCASTS_DIR = REPO_DIR / "podcasts"
DESKTOP = Path.home() / "Desktop"
LOG_DIR = Path.home() / ".openclaw" / "logs"
MAX_PER_RUN = int(os.environ.get("PODCAST_MAX_PER_RUN", "5"))

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "blueprint-podcast-worker.log"),
    ],
)
log = logging.getLogger("podcast-worker")


def _load_canonical_podcast_module():
    """Load generate-podcast.py even though the filename is not importable."""
    path = REPO_DIR / "scripts" / "generate-podcast.py"
    spec = importlib.util.spec_from_file_location("blueprint_generate_podcast", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load canonical podcast generator: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generate_source_doc(profile: dict) -> str:
    """Generate the canonical NotebookLM direct-address source doc.
    Returns path to the generated markdown file."""
    podcast_mod = _load_canonical_podcast_module()
    slug = profile["slug"]
    doc = podcast_mod.build_source_doc(profile)
    lead_name = profile.get("lead_name", "Business Owner")
    lead_first = profile.get("lead_first_name", lead_name.split()[0])
    podcast_mod.validate_source_doc(doc, lead_name, lead_first)

    output_path = PODCASTS_DIR / f"{slug}-podcast-source.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(doc)
    log.info(f"  Source doc written: {output_path}")
    return str(output_path), doc


async def generate_podcast_audio(slug: str, source_text: str) -> str | None:
    """Run the canonical NotebookLM generator and return the verified MP3 path."""
    try:
        podcast_mod = _load_canonical_podcast_module()
        result = await podcast_mod.generate_podcast(
            str(LEADS_DIR / f"{slug}.json"),
            str(PODCASTS_DIR),
            source_only=False,
        )
        if result.get("status") != "VERIFIED" or not result.get("output_path"):
            log.error(f"  [{slug}] Canonical podcast generation failed: {result}")
            return None
        log.info(f"  [{slug}] Canonical podcast verified: {result['output_path']}")
        return result["output_path"]

    except Exception as e:
        log.error(f"  [{slug}] Canonical podcast generation failed: {e}")
        return None


async def process_lead(conn: sqlite3.Connection, lead_id: str, slug: str, dry_run: bool) -> None:
    """Process a single lead: generate source doc + podcast audio."""
    profile_path = LEADS_DIR / f"{slug}.json"
    if not profile_path.exists():
        log.warning(f"  [{slug}] Profile not found — skipping")
        conn.execute("UPDATE podcast_queue SET status = 'failed' WHERE lead_id = ?", (lead_id,))
        return

    profile = json.loads(profile_path.read_text())
    log.info(f"  [{slug}] Generating NotebookLM source doc")

    try:
        source_path, source_text = generate_source_doc(profile)
        log.info(f"  [{slug}] Source doc ready at {source_path}")

        if dry_run:
            conn.execute(
                "UPDATE podcast_queue SET status = 'source_ready', completed_at = ? WHERE lead_id = ?",
                (datetime.now(timezone.utc).isoformat(), lead_id),
            )
            log.info(f"  [{slug}] Dry-run — skipping audio generation")
            return

        mp3_path = await generate_podcast_audio(slug, source_text)

        if mp3_path:
            conn.execute(
                "UPDATE podcast_queue SET status = 'completed', completed_at = ? WHERE lead_id = ?",
                (datetime.now(timezone.utc).isoformat(), lead_id),
            )
            # Update lead profile with podcast path
            profile["podcast_mp3"] = mp3_path
            profile["podcast_ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            profile_path.write_text(json.dumps(profile, indent=2))
            log.info(f"  [{slug}] Full podcast pipeline complete")
        else:
            conn.execute(
                "UPDATE podcast_queue SET status = 'source_ready', completed_at = ? WHERE lead_id = ?",
                (datetime.now(timezone.utc).isoformat(), lead_id),
            )
            log.info(f"  [{slug}] Source doc done; audio generation unavailable or failed")

    except Exception as e:
        log.error(f"  [{slug}] Failed: {e}")
        conn.execute("UPDATE podcast_queue SET status = 'failed' WHERE lead_id = ?", (lead_id,))


async def async_main():
    import argparse
    parser = argparse.ArgumentParser(description="Blueprint Podcast Worker")
    parser.add_argument("--max", type=int, default=MAX_PER_RUN)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not DB_PATH.exists():
        log.info("No dedup DB found — nothing to process")
        return

    conn = sqlite3.connect(str(DB_PATH))
    pending = conn.execute(
        "SELECT lead_id, slug FROM podcast_queue WHERE status = 'pending' ORDER BY queued_at LIMIT ?",
        (args.max,),
    ).fetchall()

    if not pending:
        log.info("No pending podcasts in queue")
        conn.close()
        return

    log.info(f"Processing {len(pending)} podcast leads")

    # Process sequentially to respect NotebookLM rate limits
    for lead_id, slug in pending:
        await process_lead(conn, lead_id, slug, args.dry_run)
        # Rate-limit delay between leads (NotebookLM ~50/day)
        if len(pending) > 1:
            time.sleep(2)

    conn.commit()
    conn.close()
    log.info("Podcast worker complete")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
