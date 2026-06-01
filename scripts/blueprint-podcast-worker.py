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


def generate_source_doc(profile: dict) -> str:
    """Generate NotebookLM v2 source doc with objection handling.
    Returns path to the generated markdown file."""
    slug = profile["slug"]
    name = profile.get("lead_first_name", profile["lead_name"].split()[0])
    business = profile.get("business_name", "the business")
    industry = profile.get("industry", "business services")
    services = profile.get("services", [])
    services_str = ", ".join(services[:5]) if isinstance(services, list) else str(services)

    doc = f"""# AI Advantage Roadmap — {profile['lead_name']}, {business}

## Segment 1: The Hook
What if AI could handle the most time-consuming parts of running {business}? Not in some distant future — but starting this week, with tools that already exist?

{name}, this AI Advantage Roadmap was built specifically for your {industry} business. Every recommendation is based on your actual operations, your team size, and the tools you already use.

## Segment 2: Current State
{business} operates in the {industry} space, offering {services_str}. Like most businesses at this stage, there are predictable bottlenecks: lead response time, proposal generation, follow-up consistency, and content creation.

The gap is not effort — it is systems. The manual processes that worked at one scale become the ceiling at the next.

## Segment 3: The 6 AI Agents
Here is what changes when AI handles the repetitive work:

1. Speed-to-Lead Agent: Responds to every inquiry within 60 seconds with a personalized message.
2. Follow-Up Nurture Agent: Runs a 7-touch sequence so no warm lead falls through the cracks.
3. Proposal Draft Agent: Generates professional proposals in minutes, not hours.
4. Content Engine Agent: Turns your expertise into social posts, emails, and articles automatically.
5. Review and Reputation Agent: Solicits reviews at the right moment and responds to feedback.
6. Admin Automation Agent: Handles scheduling, data entry, and routine communications.

Each agent is configured for {industry} specifically — not generic templates.

## Segment 4: ROI Walkthrough
Rather than promise specific dollar amounts, we built an interactive calculator into your Blueprint. Plug in your real numbers — average deal size, close rate, lead volume — and see what the math says for {business} specifically.

The conservative baseline across our clients: 35% efficiency lift in the first 30 days.

## Segment 5: Objection Handling

### Objection 1: Cost and Investment
"This sounds expensive." The implementation cost is a fraction of one employee's monthly salary. Most businesses see positive ROI within the first 2 weeks because the agents work 24/7 at zero incremental cost per interaction.

### Objection 2: Past AI or Tech Failures
"We tried automation before and it did not work." Previous tools required constant management. These agents are self-running after a 3-day setup. They monitor themselves and alert you only when human judgment is actually needed.

### Objection 3: Industry-Specific Concerns
"Does this work for {industry}?" Every agent recommendation is built from {industry}-specific use cases. The Speed-to-Lead agent, for example, understands {industry} terminology and common inquiry patterns.

### Objection 4: Time and Bandwidth
"We do not have time to implement this." The onboarding timeline is 3 days to get agents live, 7 days running independently, 30 days fully trained on your business patterns. Your team's involvement drops to near-zero after week one.

## Segment 6: Implementation Timeline
Day 1-3: Core agent setup. Speed-to-Lead and Follow-Up agents go live.
Day 4-7: Proposal, Content, and Review agents activated. First automated outputs reviewed.
Day 8-30: Agents learn your patterns. Performance data feeds back into optimization.

No 90-day rollout. No phase 2 that never happens. Agents are working within 72 hours.

## Segment 7: Call to Action
{name}, your Blueprint is ready. Your rebuilt website preview is live. The interactive ROI calculator has your actual numbers.

The next step: reply to the email that brought you here and tell us what excited you most. Or use the apply link to start the conversation about implementation.

No obligation. No sales pressure. Just a real conversation about whether this is the right fit for {business}.
"""

    output_path = DESKTOP / f"{slug}-notebooklm-source-v2.md"
    output_path.write_text(doc)
    log.info(f"  Source doc written: {output_path}")
    return str(output_path), doc


async def generate_podcast_audio(slug: str, source_text: str) -> str | None:
    """blueprint_podcast_pipeline contract: size-check → create → add source → wait → generate → wait → download.
    Returns path to downloaded MP3, or None on failure."""
    # Size gate: mirrors mcp__notebooklm__blueprint_podcast_pipeline (>18KB required)
    source_bytes = len(source_text.encode("utf-8"))
    if source_bytes < 18_432:
        log.error(f"  [{slug}] Source doc too small ({source_bytes}B < 18KB) — podcast skipped")
        return None

    try:
        from notebooklm import NotebookLMClient, AudioLength
    except ImportError:
        log.warning("notebooklm-py not installed — skipping audio generation")
        return None

    try:
        client = NotebookLMClient.from_storage()
    except Exception as e:
        log.error(f"  [{slug}] NotebookLM auth failed: {e}")
        return None

    notebook = None
    try:
        title = f"Blueprint AI — {slug}"
        log.info(f"  [{slug}] Creating NotebookLM notebook: {title}")
        notebook = await asyncio.to_thread(client.notebooks.create, title)

        log.info(f"  [{slug}] Adding source text ({source_bytes}B)")
        source = await asyncio.to_thread(
            client.sources.add_text,
            notebook.id, f"{slug} AI Roadmap", source_text,
            wait=True, wait_timeout=120.0,
        )

        log.info(f"  [{slug}] Generating podcast audio...")
        gen_status = await asyncio.to_thread(
            client.artifacts.generate_audio,
            notebook.id,
            source_ids=[source.id],
            instructions=f"Create an engaging podcast about how AI can transform {slug}'s business. Two hosts discussing the AI Advantage Roadmap. Keep it conversational and exciting.",
        )

        log.info(f"  [{slug}] Waiting for audio generation (task {gen_status.task_id})...")
        result = await asyncio.to_thread(
            client.artifacts.wait_for_completion,
            notebook.id, gen_status.task_id,
            timeout=300.0,
        )

        if result.status != "completed":
            log.error(f"  [{slug}] Audio generation failed: {result.status} — {result.error}")
            return None

        output_mp3 = str(DESKTOP / f"{slug}-podcast.mp3")
        log.info(f"  [{slug}] Downloading audio to {output_mp3}")
        await asyncio.to_thread(
            client.artifacts.download_audio,
            notebook.id, output_mp3,
        )
        log.info(f"  [{slug}] Podcast MP3 saved: {output_mp3}")
        return output_mp3

    except Exception as e:
        log.error(f"  [{slug}] NotebookLM audio generation failed: {e}")
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
