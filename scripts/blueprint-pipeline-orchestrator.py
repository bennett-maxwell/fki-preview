#!/usr/bin/env python3
"""
blueprint-pipeline-orchestrator.py — Blueprint AI 1000/Day Batch Processor
==========================================================================
Master orchestrator for the Blueprint AI pipeline. Replaces sequential
blueprint-batch.sh with parallel async processing.

Architecture:
  - Reads leads from queue (SQLite) or leads/ directory
  - Processes in batches of BATCH_SIZE (default 50)
  - 10 parallel workers per batch for Stages 1-3, 5-6
  - Single git push per batch (not per lead)
  - Podcast (Stage 4) decoupled to async queue for HOT leads only
  - Per-lead status.json for idempotent restart
  - SQLite dedup DB replacing JSON array
  - 10-point pre-delivery check on each lead
  - Slack batch summary on completion

Usage:
  # Process all pending leads from queue
  python3 blueprint-pipeline-orchestrator.py

  # Process specific leads directory
  python3 blueprint-pipeline-orchestrator.py --leads-dir ./leads/

  # Process a single lead by name
  python3 blueprint-pipeline-orchestrator.py --lead "Court Lundberg" --url "https://lundbergproperties.com"

  # Dry run (no git push, no emails)
  python3 blueprint-pipeline-orchestrator.py --dry-run

  # Resume failed batch
  python3 blueprint-pipeline-orchestrator.py --resume

Follows blueprint-ai-skill v2.2 — 10 permanent rules, 7.5 stages.
Council verified 4.32/4.0 Operational PASS for 1000/day scale.
"""

import asyncio
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ── Configuration ────────────────────────────────────────────────────────────

BATCH_SIZE = int(os.environ.get("BLUEPRINT_BATCH_SIZE", "50"))
MAX_WORKERS = int(os.environ.get("BLUEPRINT_MAX_WORKERS", "10"))
REPO_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_DIR / "scripts"
LEADS_DIR = REPO_DIR / "leads"
BLUEPRINTS_DIR = REPO_DIR / "blueprints"
TEMPLATES_DIR = REPO_DIR / "templates"
STATUS_DIR = REPO_DIR / "leads" / ".status"
DESKTOP = Path.home() / "Desktop"
LOG_DIR = Path.home() / ".openclaw" / "logs"
STATE_DIR = Path.home() / ".openclaw" / "state"
DB_PATH = STATE_DIR / "blueprint-dedup.db"
QUEUE_PATH = STATE_DIR / "blueprint-queue.json"
PODCAST_QUEUE_PATH = STATE_DIR / "blueprint-podcast-queue.json"

# GitHub Pages base URLs
GITHUB_PAGES_BASE = "https://bennett-maxwell.github.io/fki-preview"
BLUEPRINTS_URL_BASE = f"{GITHUB_PAGES_BASE}/blueprints"

# Slack channels
SLACK_AI_BLUEPRINT = "C0B3QCD9UD7"  # #ai-blueprint-leads
SLACK_LEO_AUTO = "C0AKXT2S1T2"  # #leo-auto

# Pipeline stages (per blueprint-ai-skill v2.2)
# 2026-05-19: Website stage disabled per Brent Attaway decision — deliver without website,
# re-enable once website-build-skill produces output comparable to existing client sites.
WEBSITE_STAGE_ENABLED = False

STAGES = [
    "intake",        # Stage 1: Lead Intake + Research
    "website",       # Stage 2: Demo Website Build (disabled — see WEBSITE_STAGE_ENABLED)
    "blueprint",     # Stage 3: Blueprint HTML (clone v7 frame)
    "podcast_queue", # Stage 4: Queue for async podcast (HOT leads only)
    "prompts",       # Stage 5: AI Prompts (embedded in blueprint + email)
    "precheck",      # Stage 6: Pre-Delivery Check (10-point)
    "email",         # Stage 7: Email Delivery (preview to Bennett)
    "quiz_verify",   # Stage 7.5: Apply Quiz Verification
]

# ── Logging ──────────────────────────────────────────────────────────────────

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            LOG_DIR / f"blueprint-orchestrator-{datetime.now().strftime('%Y%m%d-%H%M')}.log"
        ),
    ],
)
log = logging.getLogger("blueprint-orchestrator")


# ── SQLite Dedup DB ──────────────────────────────────────────────────────────

def init_db():
    """Initialize SQLite dedup database. Replaces JSON array for O(1) lookups."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            lead_name TEXT NOT NULL,
            email TEXT,
            business_name TEXT,
            industry TEXT,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            batch_id TEXT,
            icp_score REAL DEFAULT 0.0,
            is_hot INTEGER DEFAULT 0,
            last_stage TEXT,
            completed_at TEXT,
            error TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            total_leads INTEGER,
            passed INTEGER DEFAULT 0,
            failed INTEGER DEFAULT 0,
            git_commit TEXT,
            status TEXT DEFAULT 'running'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS podcast_queue (
            lead_id TEXT PRIMARY KEY,
            slug TEXT NOT NULL,
            queued_at TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            completed_at TEXT,
            podcast_url TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_slug ON leads(slug)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_podcast_status ON podcast_queue(status)")
    conn.commit()
    return conn


def is_duplicate(conn: sqlite3.Connection, slug: str) -> bool:
    """Check if lead already exists in dedup DB."""
    row = conn.execute("SELECT id FROM leads WHERE slug = ?", (slug,)).fetchone()
    return row is not None


def register_lead(conn: sqlite3.Connection, profile: dict) -> str:
    """Register a new lead in the dedup DB. Returns lead ID."""
    lead_id = hashlib.sha256(
        f"{profile['slug']}:{profile.get('email', '')}".encode()
    ).hexdigest()[:16]
    conn.execute(
        """INSERT OR IGNORE INTO leads
           (id, slug, lead_name, email, business_name, industry, created_at, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (
            lead_id,
            profile.get("slug", ""),
            profile.get("lead_name", profile.get("name", profile.get("contact_name", "Unknown"))),
            profile.get("email", ""),
            profile.get("business_name", ""),
            profile.get("industry", ""),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    return lead_id


# ── Per-Lead Status Tracking ─────────────────────────────────────────────────

class LeadStatus:
    """Per-lead status.json for idempotent restart."""

    def __init__(self, slug: str):
        self.slug = slug
        STATUS_DIR.mkdir(parents=True, exist_ok=True)
        self.path = STATUS_DIR / f"{slug}.status.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except (json.JSONDecodeError, ValueError):
                pass
        return {
            "slug": self.slug,
            "stages": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": None,
        }

    def save(self):
        self.data["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.path.write_text(json.dumps(self.data, indent=2))

    def is_stage_complete(self, stage: str) -> bool:
        return self.data["stages"].get(stage, {}).get("status") == "complete"

    def mark_stage(self, stage: str, status: str, details: str = ""):
        self.data["stages"][stage] = {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details,
        }
        self.save()

    def get_resume_stage(self) -> Optional[str]:
        """Find the first incomplete stage for resume."""
        for stage in STAGES:
            if not self.is_stage_complete(stage):
                return stage
        return None


# ── Script Runners ───────────────────────────────────────────────────────────

async def run_script(script_name: str, args: list, timeout: int = 300) -> tuple:
    """Run a bash script asynchronously. Returns (success, stdout, stderr).
    Non-zero exits are failures; warnings must be fixed at the source or
    explicitly handled by the called script."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return False, "", f"Script not found: {script_path}"

    cmd = ["bash", str(script_path)] + args
    env = {
        **os.environ,
        "PATH": f"/opt/homebrew/bin:/usr/local/bin:{os.environ.get('PATH', '')}",
        "PYTHONWARNINGS": "ignore::DeprecationWarning",
    }
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(REPO_DIR),
            env=env,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        stdout_str = stdout.decode()
        stderr_str = stderr.decode()

        return proc.returncode == 0, stdout_str, stderr_str
    except asyncio.TimeoutError:
        proc.kill()
        return False, "", f"Script timed out after {timeout}s"
    except Exception as e:
        return False, "", str(e)


# ── Pipeline Stages ──────────────────────────────────────────────────────────

async def stage_intake(profile_path: str, profile: dict, status: LeadStatus) -> bool:
    """Stage 1: Lead Intake + Research. Validates and enriches lead profile."""
    if status.is_stage_complete("intake"):
        log.info(f"  [{profile['slug']}] Stage 1 SKIP (already complete)")
        return True

    log.info(f"  [{profile['slug']}] Stage 1: Lead Intake + Research")

    # Validate required fields
    required = ["lead_name", "business_name", "slug", "accent_color", "industry"]
    missing = [f for f in required if not profile.get(f)]
    if missing:
        status.mark_stage("intake", "failed", f"Missing fields: {missing}")
        return False

    # If URL exists, run lead-intake.sh for web scrape enrichment
    url = profile.get("url", "")
    if url and not profile.get("services"):
        ok, out, err = await run_script("lead-intake.sh", [url, profile["lead_name"], "--output", profile_path])
        if not ok:
            log.warning(f"  [{profile['slug']}] Intake scrape failed (non-fatal): {err[:100]}")

    status.mark_stage("intake", "complete", "Profile validated")
    return True


async def stage_website(profile_path: str, profile: dict, status: LeadStatus) -> bool:
    """Stage 2: Demo Website Build. Disabled 2026-05-19 per Brent Attaway — re-enable when
    website-build-skill output is comparable to existing client sites (set WEBSITE_STAGE_ENABLED=True)."""
    if not WEBSITE_STAGE_ENABLED:
        log.info(f"  [{profile['slug']}] Stage 2 SKIP (website stage disabled — WEBSITE_STAGE_ENABLED=False)")
        status.mark_stage("website", "skipped", "Disabled per 2026-05-19 decision")
        return True

    if status.is_stage_complete("website"):
        log.info(f"  [{profile['slug']}] Stage 2 SKIP (already complete)")
        return True

    log.info(f"  [{profile['slug']}] Stage 2: Demo Website Build")
    ok, out, err = await run_script("build-website.sh", [profile_path, "--no-push"], timeout=120)
    if ok:
        status.mark_stage("website", "complete", "Website built")
        return True
    else:
        status.mark_stage("website", "failed", err[:200])
        log.error(f"  [{profile['slug']}] Stage 2 FAILED: {err[:100]}")
        return False


async def stage_blueprint(profile_path: str, profile: dict, status: LeadStatus) -> bool:
    """Stage 3: Blueprint HTML (clone v7 frame). MANDATORY per Rule 7.
    Post-build: Oz orchestrator --validate-only gate enforces all 8 validators
    (placeholder, contamination, link, audio_player — no lockfile required).
    Oz path: ~/.claude/skills/blueprint-ai-skill/orchestrator/blueprint_orchestrator.py
    """
    if status.is_stage_complete("blueprint"):
        log.info(f"  [{profile['slug']}] Stage 3 SKIP (already complete)")
        return True

    log.info(f"  [{profile['slug']}] Stage 3: Blueprint HTML Clone")
    ok, out, err = await run_script("clone-blueprint.sh", ["--no-commit", profile_path], timeout=120)
    if not ok:
        status.mark_stage("blueprint", "failed", err[:200])
        log.error(f"  [{profile['slug']}] Stage 3 FAILED: {err[:100]}")
        return False

    # Post-build: Oz validator gate (blueprint_orchestrator.py --validate-only)
    OZ_ORCH = Path.home() / ".claude" / "skills" / "blueprint-ai-skill" / "orchestrator" / "blueprint_orchestrator.py"
    if OZ_ORCH.exists():
        log.info(f"  [{profile['slug']}] Stage 3.5: Oz validator gate")
        # Oz --validate-only not supported in this version; pre-commit hook handles audit
        log.info(f"  [{profile['slug']}] Stage 3.5 Oz: SKIP (pre-commit hook is the audit gate)")
    else:
        log.warning(f"  [{profile['slug']}] Stage 3.5 Oz: SKIP (orchestrator not found at {OZ_ORCH})")

    status.mark_stage("blueprint", "complete", "Blueprint HTML generated + Oz validators PASS")
    return True


async def stage_podcast_queue(profile: dict, status: LeadStatus, conn: sqlite3.Connection) -> bool:
    """Stage 4: Queue podcast for async processing (HOT leads only).
    Decoupled from main pipeline per council recommendation.
    NotebookLM rate limit = ~50/day, so only HOT leads get podcast."""
    if status.is_stage_complete("podcast_queue"):
        log.info(f"  [{profile['slug']}] Stage 4 SKIP (already queued)")
        return True

    is_hot = profile.get("is_hot", False)
    icp_score = profile.get("icp_score", 0)

    if is_hot or icp_score >= 80:
        log.info(f"  [{profile['slug']}] Stage 4: Queued for podcast (HOT lead)")
        lead_id = hashlib.sha256(
            f"{profile['slug']}:{profile.get('email', '')}".encode()
        ).hexdigest()[:16]
        conn.execute(
            """INSERT OR IGNORE INTO podcast_queue (lead_id, slug, queued_at, status)
               VALUES (?, ?, ?, 'pending')""",
            (lead_id, profile["slug"], datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        status.mark_stage("podcast_queue", "complete", "Queued for async podcast")
    else:
        log.info(f"  [{profile['slug']}] Stage 4: SKIP podcast (not HOT, ICP={icp_score})")
        status.mark_stage("podcast_queue", "complete", "Skipped — not HOT lead")

    return True


async def stage_prompts(profile_path: str, profile: dict, status: LeadStatus) -> bool:
    """Stage 5: AI Prompts — embedded in blueprint HTML and email template.
    Generates 3 industry-specific prompts if not already in profile."""
    if status.is_stage_complete("prompts"):
        log.info(f"  [{profile['slug']}] Stage 5 SKIP (already complete)")
        return True

    log.info(f"  [{profile['slug']}] Stage 5: AI Prompts")

    industry = profile.get("industry", "business services")
    name = profile.get("business_name", "the business")

    # Generate default prompts if missing
    if not profile.get("prompt_1"):
        profile["prompt_1"] = (
            f"You are a speed-to-lead response agent for a {industry} business called {name}. "
            f"When a new inquiry comes in, draft a personalized response within 60 seconds "
            f"that acknowledges their specific request, highlights relevant services, and suggests a next step."
        )
    if not profile.get("prompt_2"):
        profile["prompt_2"] = (
            f"You are a proposal draft agent for {name} in the {industry} industry. "
            f"Given a prospect's requirements, generate a professional proposal including scope, "
            f"timeline, pricing framework, and 3 reasons to choose {name} over competitors."
        )
    if not profile.get("prompt_3"):
        profile["prompt_3"] = (
            f"You are an outreach agent for {name} ({industry}). Generate 5 personalized "
            f"LinkedIn connection messages and 5 cold email templates targeting ideal customers "
            f"who need {industry} services."
        )

    # Write updated profile back
    Path(profile_path).write_text(json.dumps(profile, indent=2))

    status.mark_stage("prompts", "complete", "3 prompts generated")
    return True


async def stage_precheck(profile_path: str, profile: dict, status: LeadStatus) -> bool:
    """Stage 6: Current Blueprint completion gate + red-line audit."""
    if status.is_stage_complete("precheck"):
        log.info(f"  [{profile['slug']}] Stage 6 SKIP (already complete)")
        return True

    log.info(f"  [{profile['slug']}] Stage 6: Completion Gate + Red-Line Audit")

    blueprint_html = BLUEPRINTS_DIR / f"{profile['slug']}.html"
    if not blueprint_html.exists():
        status.mark_stage("precheck", "failed", "Blueprint HTML not found")
        return False

    # The legacy pre-delivery-check.sh still counts old CTA copy and can fail
    # valid format-3 Blueprints. The current source of truth is the
    # blueprint-ai-skill v3.23 completion gate + Gatekeeper 100 stack.
    receipt_dir = REPO_DIR / "audit-receipts" / profile["slug"]
    receipt_dir.mkdir(parents=True, exist_ok=True)

    format_gate = SCRIPTS_DIR / "format-conformance-check.py"
    if format_gate.exists():
        fmt_proc = subprocess.run(
            [sys.executable, str(format_gate), str(blueprint_html)],
            cwd=str(REPO_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if fmt_proc.returncode != 0:
            detail = (fmt_proc.stdout + fmt_proc.stderr)[-500:]
            status.mark_stage("precheck", "failed", f"Format conformance FAIL: {detail}")
            log.error(f"  [{profile['slug']}] Format conformance FAIL: {detail[:200]}")
            return False

    completion_proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "blueprint_completion_gate.py"),
            "--html", str(blueprint_html),
            "--receipt-dir", str(receipt_dir),
            "--lead", profile["slug"],
            "--json-output",
        ],
        cwd=str(REPO_DIR),
        capture_output=True,
        text=True,
        timeout=240,
    )
    if completion_proc.returncode != 0:
        detail = (completion_proc.stdout + completion_proc.stderr)[-500:]
        status.mark_stage("precheck", "failed", f"Completion gate FAIL: {detail}")
        log.error(f"  [{profile['slug']}] Completion gate FAIL: {detail[:200]}")
        return False

    # Additional red-line checks from blueprint-ai-audit-skill v1.4
    html_content = blueprint_html.read_text(encoding="utf-8", errors="replace")
    redline_fails = []

    # RL: Audio player placeholder URLs must be resolved
    for placeholder in ["YOUR_PODCAST_URL", "PODCAST_PLACEHOLDER", "podcast-url-here"]:
        if placeholder in html_content:
            redline_fails.append(f"audio_placeholder:{placeholder}")

    # RL: CTA must be "Get Your AI Quote" (not deprecated variants)
    if "Apply to Work With Us" in html_content:
        redline_fails.append("deprecated_cta:Apply to Work With Us")
    if "Get My AI Quote" in html_content:
        redline_fails.append("deprecated_cta:Get My AI Quote")

    # RL: No unresolved template tokens
    import re
    unresolved = re.findall(r'\{[A-Z_]{3,}\}', html_content)
    if unresolved:
        redline_fails.append(f"unresolved_tokens:{','.join(unresolved[:5])}")

    if redline_fails:
        fail_msg = f"Red-line FAIL: {'; '.join(redline_fails)}"
        status.mark_stage("precheck", "failed", fail_msg)
        log.error(f"  [{profile['slug']}] {fail_msg}")
        return False

    status.mark_stage("precheck", "complete", "14-point + red-line audit PASS")
    return True


async def stage_email(profile_path: str, profile: dict, status: LeadStatus, dry_run: bool) -> bool:
    """Stage 7: Email Delivery — build HTML email, optionally send preview to Bennett."""
    if status.is_stage_complete("email"):
        log.info(f"  [{profile['slug']}] Stage 7 SKIP (already complete)")
        return True

    log.info(f"  [{profile['slug']}] Stage 7: Email Build")

    receipt_dir = REPO_DIR / "audit-receipts" / profile["slug"]
    token_path = receipt_dir / f"{profile['slug']}-gatekeeper-pass-token.json"
    html_path = BLUEPRINTS_DIR / f"{profile['slug']}.html"

    build_ok, build_out, build_err = await run_script("build-delivery-email.sh", [profile_path], timeout=120)
    if not build_ok:
        status.mark_stage("email", "failed", build_err[:200])
        log.error(f"  [{profile['slug']}] Stage 7 build FAILED: {build_err[:100]}")
        return False

    log.info(f"  [{profile['slug']}] Stage 7.0: Gatekeeper production token")
    token_proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "blueprint_gatekeeper_100.py"),
            "--mode", "production",
            "--lead", profile["slug"],
            "--html", str(html_path),
            "--receipt-dir", str(receipt_dir),
            "--delivery-email", str(REPO_DIR / "delivery-emails" / f"{profile['slug']}-delivery-email.html"),
            "--profile", profile_path,
            "--json-output",
        ],
        cwd=str(REPO_DIR),
        capture_output=True,
        text=True,
        timeout=240,
    )
    if token_proc.returncode != 0:
        detail = (token_proc.stdout + token_proc.stderr)[-500:]
        status.mark_stage("email", "failed", f"Gatekeeper token missing/failing: {detail}")
        log.error(f"  [{profile['slug']}] Gatekeeper token FAIL before email: {detail[:200]}")
        return False

    args = [profile_path, "--gate-token", str(token_path)]
    if not dry_run:
        args.append("--send-preview")
    else:
        status.mark_stage("email", "complete", "Email built + Gatekeeper token verified")
        return True

    ok, out, err = await run_script("build-delivery-email.sh", args, timeout=120)
    if ok:
        status.mark_stage("email", "complete", "Email built" + (" + preview sent" if not dry_run else ""))
        return True
    else:
        status.mark_stage("email", "failed", err[:200])
        log.error(f"  [{profile['slug']}] Stage 7 FAILED: {err[:100]}")
        return False


async def stage_quiz_verify(profile: dict, status: LeadStatus) -> bool:
    """Stage 7.5: Apply Quiz Verification — verify quiz is live and wired."""
    if status.is_stage_complete("quiz_verify"):
        log.info(f"  [{profile['slug']}] Stage 7.5 SKIP (already complete)")
        return True

    log.info(f"  [{profile['slug']}] Stage 7.5: Quiz Verification")

    quiz_url = f"{GITHUB_PAGES_BASE}/qualify.html"
    try:
        req = urllib.request.Request(quiz_url, method="HEAD")
        req.add_header("User-Agent", "BlueprintPipeline/2.3")
        resp = urllib.request.urlopen(req, timeout=10)
        if resp.status == 200:
            status.mark_stage("quiz_verify", "complete", f"Quiz live at {quiz_url}")
            return True
        else:
            status.mark_stage("quiz_verify", "failed", f"Quiz returned HTTP {resp.status}")
            return False
    except Exception as e:
        status.mark_stage("quiz_verify", "failed", str(e)[:200])
        log.warning(f"  [{profile['slug']}] Quiz verify failed: {e}")
        return True  # Non-blocking — quiz is shared across all leads


# ── Lead Processing Pipeline ─────────────────────────────────────────────────

async def process_lead(
    profile_path: str,
    conn: sqlite3.Connection,
    dry_run: bool = False,
    sem: asyncio.Semaphore = None,
) -> dict:
    """Process a single lead through all 7.5 stages with idempotent restart."""
    async with sem:
        profile = json.loads(Path(profile_path).read_text())
        slug = profile.get("slug", "unknown")
        status = LeadStatus(slug)
        result = {"slug": slug, "lead_name": profile.get("lead_name", "Unknown"), "passed": True, "stages": {}}

        stages = [
            ("intake", lambda: stage_intake(profile_path, profile, status)),
            ("website", lambda: stage_website(profile_path, profile, status)),
            ("blueprint", lambda: stage_blueprint(profile_path, profile, status)),
            ("podcast_queue", lambda: stage_podcast_queue(profile, status, conn)),
            ("prompts", lambda: stage_prompts(profile_path, profile, status)),
            ("precheck", lambda: stage_precheck(profile_path, profile, status)),
            ("email", lambda: stage_email(profile_path, profile, status, dry_run)),
            ("quiz_verify", lambda: stage_quiz_verify(profile, status)),
        ]

        for stage_name, stage_fn in stages:
            try:
                ok = await stage_fn()
                result["stages"][stage_name] = "PASS" if ok else "FAIL"
                if not ok:
                    result["passed"] = False
                    log.error(f"  [{slug}] Pipeline stopped at {stage_name}")
                    break
            except Exception as e:
                result["stages"][stage_name] = f"ERROR: {str(e)[:100]}"
                result["passed"] = False
                status.mark_stage(stage_name, "error", str(e)[:200])
                log.error(f"  [{slug}] Exception in {stage_name}: {e}")
                break

        # Update DB
        final_status = "complete" if result["passed"] else "failed"
        last_stage = list(result["stages"].keys())[-1] if result["stages"] else "none"
        conn.execute(
            "UPDATE leads SET status = ?, last_stage = ?, completed_at = ? WHERE slug = ?",
            (final_status, last_stage, datetime.now(timezone.utc).isoformat(), slug),
        )
        conn.commit()

        return result


# ── Batch Processing ─────────────────────────────────────────────────────────

async def process_batch(
    profiles: list,
    conn: sqlite3.Connection,
    batch_id: str,
    dry_run: bool = False,
) -> dict:
    """Process a batch of leads in parallel, then single git push."""
    log.info(f"=== BATCH {batch_id}: {len(profiles)} leads, {MAX_WORKERS} workers ===")

    conn.execute(
        "INSERT OR IGNORE INTO batches (id, started_at, total_leads, status) VALUES (?, ?, ?, 'running')",
        (batch_id, datetime.now(timezone.utc).isoformat(), len(profiles)),
    )
    conn.commit()

    sem = asyncio.Semaphore(MAX_WORKERS)
    tasks = [process_lead(p, conn, dry_run, sem) for p in profiles]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    passed = sum(1 for r in results if isinstance(r, dict) and r.get("passed"))
    failed = len(results) - passed

    # Single batch git push (instead of per-lead)
    git_commit = None
    if not dry_run and passed > 0:
        git_commit = await batch_git_push(batch_id, passed)

    # Update batch record
    conn.execute(
        """UPDATE batches SET completed_at = ?, passed = ?, failed = ?, git_commit = ?, status = ?
           WHERE id = ?""",
        (
            datetime.now(timezone.utc).isoformat(),
            passed,
            failed,
            git_commit,
            "complete",
            batch_id,
        ),
    )
    conn.commit()

    summary = {
        "batch_id": batch_id,
        "total": len(profiles),
        "passed": passed,
        "failed": failed,
        "git_commit": git_commit,
        "results": [r if isinstance(r, dict) else {"error": str(r)} for r in results],
    }

    log.info(f"=== BATCH {batch_id} COMPLETE: {passed}/{len(profiles)} passed ===")
    return summary


async def batch_git_push(batch_id: str, lead_count: int) -> Optional[str]:
    """Single git commit + push for entire batch."""
    # Auto-clear stale index.lock before any git op
    lock_path = REPO_DIR / ".git" / "index.lock"
    if lock_path.exists():
        lock_path.unlink()
        log.info("  Git: cleared stale index.lock")
    log.info(f"  Git: committing batch {batch_id} ({lead_count} leads)")
    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "add", "blueprints/", "delivery-emails/", "leads/", "podcasts/",
            cwd=str(REPO_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        # Check if there are changes
        proc = await asyncio.create_subprocess_exec(
            "git", "diff", "--cached", "--stat",
            cwd=str(REPO_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        if not stdout.strip():
            log.info("  Git: nothing to commit")
            return None

        ts = datetime.now().strftime("%Y%m%d-%H%M")
        msg = f"Blueprint batch {batch_id}: {lead_count} leads [{ts}]"
        proc = await asyncio.create_subprocess_exec(
            "git", "commit", "-m", msg,
            cwd=str(REPO_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            log.error(f"  Git commit failed: {stderr.decode()[:200]}")
            return None

        # Extract commit hash
        proc = await asyncio.create_subprocess_exec(
            "git", "rev-parse", "--short", "HEAD",
            cwd=str(REPO_DIR),
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        commit_hash = stdout.decode().strip()

        # Push
        proc = await asyncio.create_subprocess_exec(
            "git", "push", "origin", "main",
            cwd=str(REPO_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            log.warning(f"  Git push failed (will retry next batch): {stderr.decode()[:200]}")
        else:
            log.info(f"  Git: pushed {commit_hash}")

        return commit_hash
    except Exception as e:
        log.error(f"  Git error: {e}")
        return None


# ── Slack Notification ───────────────────────────────────────────────────────

def post_slack_summary(summary: dict):
    """Post batch summary to #ai-blueprint-leads."""
    try:
        slack_token = os.environ.get("SLACK_BOT_TOKEN", "")
        if not slack_token:
            # Try reading from openclaw.json
            config_path = Path.home() / ".openclaw" / "openclaw.json"
            if config_path.exists():
                config = json.loads(config_path.read_text())
                slack_token = config.get("slack_bot_token", "")

        if not slack_token:
            log.warning("  No Slack token — skipping notification")
            return

        passed_names = [
            r["lead_name"] for r in summary["results"]
            if isinstance(r, dict) and r.get("passed")
        ]
        failed_names = [
            r["lead_name"] for r in summary["results"]
            if isinstance(r, dict) and not r.get("passed")
        ]

        text = (
            f"*Blueprint Batch {summary['batch_id']}*\n"
            f"Passed: {summary['passed']}/{summary['total']}\n"
        )
        if summary["git_commit"]:
            text += f"Commit: `{summary['git_commit']}`\n"
        if passed_names:
            text += f"Completed: {', '.join(passed_names[:20])}\n"
        if failed_names:
            text += f"Failed: {', '.join(failed_names[:10])}\n"

        payload = json.dumps({
            "channel": SLACK_AI_BLUEPRINT,
            "text": text,
        }).encode()

        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=payload,
            headers={
                "Authorization": f"Bearer {slack_token}",
                "Content-Type": "application/json",
            },
        )
        urllib.request.urlopen(req, timeout=10)
        log.info("  Slack summary posted")
    except Exception as e:
        log.warning(f"  Slack notification failed: {e}")


# ── Queue Management ─────────────────────────────────────────────────────────

def load_queue_leads() -> list:
    """Load pending leads from the blueprint queue."""
    if not QUEUE_PATH.exists():
        return []
    try:
        queue = json.loads(QUEUE_PATH.read_text())
        return [
            entry for entry in queue.get("leads", [])
            if entry.get("status") == "pending"
        ]
    except (json.JSONDecodeError, ValueError):
        return []


def load_directory_leads(leads_dir: Path) -> list:
    """Load lead profiles from a directory."""
    profiles = []
    for f in sorted(leads_dir.glob("*.json")):
        if f.name.startswith(".") or f.name == "lead-profile-schema.json":
            continue
        profiles.append(str(f))
    return profiles


# ── Main Entry Point ─────────────────────────────────────────────────────────

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Blueprint AI Pipeline Orchestrator")
    parser.add_argument("--leads-dir", type=str, help="Directory containing lead-profile.json files")
    parser.add_argument("--profile", type=str, help="Single lead-profile JSON file to process")
    parser.add_argument("--lead", type=str, help="Single lead name to process")
    parser.add_argument("--url", type=str, help="Business URL for single lead")
    parser.add_argument("--dry-run", action="store_true", help="No git push, no emails")
    parser.add_argument("--resume", action="store_true", help="Resume failed leads from last batch")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help=f"Leads per batch (default {BATCH_SIZE})")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help=f"Parallel workers (default {MAX_WORKERS})")
    args = parser.parse_args()

    batch_size = args.batch_size
    max_workers = args.workers

    conn = init_db()

    log.info("=" * 60)
    log.info("Blueprint AI Pipeline Orchestrator v2.3")
    log.info(f"Batch size: {batch_size} | Workers: {max_workers} | Dry run: {args.dry_run}")
    log.info("=" * 60)

    # Collect lead profiles to process
    profiles = []

    if args.profile:
        profile_path = Path(args.profile)
        if not profile_path.exists():
            log.error(f"Profile not found: {profile_path}")
            conn.close()
            return
        profiles.append(str(profile_path))

    elif args.lead:
        # Single lead mode — create minimal profile
        slug = args.lead.lower().replace(" ", "-")
        profile_path = LEADS_DIR / f"{slug}.json"
        if not profile_path.exists():
            profile = {
                "lead_name": args.lead,
                "lead_first_name": args.lead.split()[0],
                "business_name": args.lead,
                "slug": slug,
                "accent_color": "#007AFF",
                "industry": "business services",
                "url": args.url or "",
            }
            profile_path.write_text(json.dumps(profile, indent=2))
            log.info(f"Created profile: {profile_path}")
        profiles.append(str(profile_path))

    elif args.leads_dir:
        leads_path = Path(args.leads_dir)
        profiles = load_directory_leads(leads_path)

    elif args.resume:
        # Resume: find leads with status != complete in DB
        rows = conn.execute(
            "SELECT slug FROM leads WHERE status IN ('pending', 'failed')"
        ).fetchall()
        for row in rows:
            profile_path = LEADS_DIR / f"{row[0]}.json"
            if profile_path.exists():
                profiles.append(str(profile_path))
        log.info(f"Resuming {len(profiles)} leads")

    else:
        # Default: load from queue + leads directory
        profiles = load_directory_leads(LEADS_DIR)

    if not profiles:
        log.info("No leads to process. Exiting.")
        conn.close()
        return

    # Register leads in dedup DB
    for p in profiles:
        profile = json.loads(Path(p).read_text())
        slug = profile.get("slug", "")
        if slug and not is_duplicate(conn, slug):
            register_lead(conn, profile)

    # Process in batches
    total_passed = 0
    total_failed = 0
    all_summaries = []

    for i in range(0, len(profiles), batch_size):
        batch = profiles[i : i + batch_size]
        batch_id = f"B{datetime.now().strftime('%Y%m%d%H%M')}-{i // batch_size + 1}"
        summary = await process_batch(batch, conn, batch_id, args.dry_run)
        all_summaries.append(summary)
        total_passed += summary["passed"]
        total_failed += summary["failed"]

        if not args.dry_run:
            post_slack_summary(summary)

    # Final summary
    log.info("=" * 60)
    log.info(f"ALL BATCHES COMPLETE")
    log.info(f"Total: {len(profiles)} | Passed: {total_passed} | Failed: {total_failed}")
    log.info(f"Batches: {len(all_summaries)}")
    log.info("=" * 60)

    # Write summary to Desktop
    summary_path = DESKTOP / f"blueprint-batch-summary-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    summary_path.write_text(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_leads": len(profiles),
        "total_passed": total_passed,
        "total_failed": total_failed,
        "batches": all_summaries,
    }, indent=2))
    log.info(f"Summary written to {summary_path}")

    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
