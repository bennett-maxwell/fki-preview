#!/usr/bin/env python3
"""
Blueprint AI Pipeline — Stage 4: Podcast Generation
Generates NotebookLM podcast from Blueprint HTML content.

Usage:
  Single lead:  python3 generate-podcast.py <lead-profile.json> [--output-dir ~/Desktop]
  Batch mode:   python3 generate-podcast.py --batch <dir-or-glob> [--output-dir ~/Desktop]

Flags:
  --delay SECONDS        Delay between notebook creations (default: 60)
  --max-concurrent N     Max concurrent generations (default: 1 = sequential)
  --batch <path>         Process multiple lead-profile.json files from a directory
  --output-dir DIR       Where to save outputs (default: ~/Desktop)

Requires: pip3 install notebooklm
Auth: Run notebooklm-py auth flow once first (stores in ~/.notebooklm/)
"""

import argparse
import asyncio
import glob
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime

PODCAST_TEMPLATE = """# {business_name} — AI Blueprint Audio Walkthrough

## About This Business
{business_name} is a {industry} company led by {lead_name}. They currently use {tools} and serve {market}.

## The 6 AI Agents Built for {business_name}

### Agent 1: Speed-to-Lead Response Agent
Handles every inbound inquiry within 60 seconds. For {industry}, this means {speed_to_lead_context}. Studies show 78% of customers buy from the first responder (Harvard Business Review, 2023).

### Agent 2: Smart Scheduling and Routing Agent
Routes {service_type} requests to the right team member based on availability, expertise, and location. Eliminates the back-and-forth that costs {industry} businesses 5-8 hours per week.

### Agent 3: Proposal and Quote Draft Agent
Generates professional {service_type} proposals in under 2 minutes using the business's actual pricing, past projects, and industry benchmarks. Each proposal is customized to the prospect's specific needs.

### Agent 4: Follow-Up Nurture Agent
Maintains contact with leads who aren't ready to buy yet. Sends personalized follow-ups based on their specific interests and timeline — not generic drip campaigns.

### Agent 5: Review and Reputation Agent
Automatically requests reviews from satisfied customers at the optimal moment. Monitors and alerts on new reviews across Google, Yelp, and industry-specific platforms.

### Agent 6: Analytics and Reporting Agent
Provides a single dashboard showing leads, conversions, revenue attribution, and AI agent performance. {lead_name} sees exactly what's working without pulling reports manually.

## Implementation Timeline
- Days 1-3: AI agents are configured and connected to {business_name}'s existing tools
- Days 4-7: Agents are live and handling real inquiries, with human oversight
- By Day 30: Fully trained system running autonomously, saving an estimated 20+ hours per week

## Objection Handling

### "Is this going to replace my team?"
No. These agents handle the repetitive tasks your team shouldn't be doing — data entry, initial responses, follow-up sequences. Your team focuses on the high-value work: closing deals, building relationships, delivering great {service_type}.

### "What about the learning curve?"
The 3/7/30 timeline is designed for zero disruption. By day 3, you'll see the agents working. By day 7, your team will wonder how they worked without them.

### "How is this different from other AI tools?"
These aren't generic chatbots. Every agent is built specifically for {industry} — using your actual services, your pricing, your brand voice. They integrate with {tools}, not replace them.

## What To Do Next
If what you've heard resonates, reply to the email that brought you here. Tell Bennett what excited you most, and he'll walk you through exactly how this would work for {business_name}.
"""

# ---------------------------------------------------------------------------
# Rate-limit helpers
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 30

def _ts():
    """Compact timestamp for log lines."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _log(msg: str):
    """Log to stderr with timestamp."""
    print(f"[{_ts()}] {msg}", file=sys.stderr)

def _is_rate_limit_error(exc: Exception) -> bool:
    """Detect rate-limit (HTTP 429) or quota errors from the API."""
    exc_str = str(exc).lower()
    # Check for common rate-limit signals
    if '429' in exc_str:
        return True
    if 'rate' in exc_str and 'limit' in exc_str:
        return True
    if 'quota' in exc_str:
        return True
    if 'too many requests' in exc_str:
        return True
    # Check for an HTTP status attribute (requests / httpx style)
    status = getattr(exc, 'status_code', None) or getattr(exc, 'status', None)
    if status == 429:
        return True
    return False


async def _retry_async(coro_factory, description: str = "API call"):
    """
    Call *coro_factory()* (which must return a new awaitable each time) with
    exponential-backoff retry on rate-limit errors.

    Returns the result on success; raises the last exception on exhaustion.
    """
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            _log(f"Attempt {attempt}/{MAX_RETRIES} — {description}")
            result = await coro_factory()
            return result
        except Exception as exc:
            last_exc = exc
            if _is_rate_limit_error(exc) and attempt < MAX_RETRIES:
                wait = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))
                _log(f"Rate-limited on '{description}': {exc}. "
                     f"Retrying in {wait}s (attempt {attempt}/{MAX_RETRIES})...")
                await asyncio.sleep(wait)
            else:
                raise
    raise last_exc  # should not reach here, but safety net


# ---------------------------------------------------------------------------
# Core generation logic
# ---------------------------------------------------------------------------

async def generate_podcast(profile_path: str, output_dir: str = None):
    """Generate a NotebookLM podcast from lead profile."""

    # Load profile
    with open(profile_path) as f:
        profile = json.load(f)

    lead_name = profile.get('lead_name', 'Unknown')
    business_name = profile.get('business_name', 'Unknown Business')
    slug = profile.get('slug', lead_name.lower().replace(' ', '-'))
    industry = profile.get('industry', 'business services')
    tools = profile.get('tools', 'standard business tools')
    market = profile.get('market', 'local and regional customers')
    service_type = profile.get('service_type', 'professional services')
    speed_to_lead_context = profile.get('speed_to_lead_context',
        f'capturing every {industry} inquiry before competitors respond')

    if output_dir is None:
        output_dir = os.path.expanduser('~/Desktop')

    # Generate source doc from template
    source_content = PODCAST_TEMPLATE.format(
        business_name=business_name,
        lead_name=lead_name,
        industry=industry,
        tools=tools,
        market=market,
        service_type=service_type,
        speed_to_lead_context=speed_to_lead_context,
    )

    # Save source doc
    source_path = os.path.join(output_dir, f'{slug}-podcast-source.md')
    with open(source_path, 'w') as f:
        f.write(source_content)
    print(f"Source doc: {source_path} ({len(source_content)} chars)")

    # NotebookLM generation
    try:
        from notebooklm import NotebookLMClient

        client = await NotebookLMClient.from_storage()
        async with client:
            # Create notebook (with retry)
            notebook = await _retry_async(
                lambda: client.notebooks.create(
                    title=f"{business_name} AI Blueprint Podcast"
                ),
                description=f"create notebook for {business_name}",
            )
            nb_id = notebook.id
            _log(f"Notebook created: {nb_id}")

            # Add source (with retry)
            await _retry_async(
                lambda: client.sources.add_text(
                    nb_id,
                    f"{business_name} AI Blueprint",
                    source_content,
                    wait=True,
                ),
                description=f"add source to {nb_id}",
            )
            _log("Source added")

            # Generate audio (with retry)
            await _retry_async(
                lambda: client.artifacts.generate_audio(nb_id),
                description=f"generate audio for {nb_id}",
            )
            _log("Audio generation started...")

            # Poll for completion (max 5 min)
            for i in range(30):
                await asyncio.sleep(10)
                artifacts = await client.artifacts.list_audio(nb_id)
                for art in artifacts:
                    if art.status == 3:  # COMPLETED
                        _log(f"Audio ready! Artifact: {art.id}")
                        # Download
                        output_path = os.path.join(output_dir, f'{slug}-blueprint-podcast.mp4')
                        await client.artifacts.download_audio(nb_id, output_path)
                        size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        print(f"Downloaded: {output_path} ({size_mb:.1f}MB)")
                        return {
                            'notebook_id': nb_id,
                            'artifact_id': art.id,
                            'output_path': output_path,
                            'size_mb': round(size_mb, 1),
                            'source_path': source_path,
                        }
                _log(f"  Polling {i+1}/30...")

            _log("WARNING: Audio generation timed out after 5 min")
            return {
                'notebook_id': nb_id,
                'status': 'timeout',
                'source_path': source_path,
            }

    except ImportError:
        print("ERROR: notebooklm not installed. Run: pip3 install notebooklm")
        return {'error': 'notebooklm not installed', 'source_path': source_path}
    except Exception as e:
        _log(f"ERROR: {e}")
        return {'error': str(e), 'source_path': source_path}


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

async def _batch_worker(semaphore: asyncio.Semaphore, profile_path: str,
                        output_dir: str, delay: float, results: list, index: int):
    """Process a single profile inside the batch, respecting concurrency."""
    async with semaphore:
        _log(f"[{index}] Starting: {profile_path}")
        result = await generate_podcast(profile_path, output_dir)
        result['profile_path'] = profile_path
        results.append(result)
        _log(f"[{index}] Finished: {profile_path} -> "
             f"{'OK' if 'error' not in result else result['error']}")
        # Inter-creation delay (rate-limit courtesy pause)
        if delay > 0:
            _log(f"[{index}] Waiting {delay}s before next creation...")
            await asyncio.sleep(delay)


async def run_batch(profile_paths: list, output_dir: str,
                    delay: float, max_concurrent: int):
    """Process multiple lead profiles with concurrency control and delays."""
    _log(f"Batch mode: {len(profile_paths)} profiles, "
         f"delay={delay}s, max_concurrent={max_concurrent}")

    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    if max_concurrent == 1:
        # Sequential — simple loop so delays happen in order
        for i, path in enumerate(profile_paths, 1):
            await _batch_worker(semaphore, path, output_dir, delay, results, i)
    else:
        # Concurrent — launch tasks, semaphore limits parallelism
        tasks = []
        for i, path in enumerate(profile_paths, 1):
            task = asyncio.create_task(
                _batch_worker(semaphore, path, output_dir, delay, results, i)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

    _log(f"Batch complete: {len(results)}/{len(profile_paths)} processed")
    successes = [r for r in results if 'error' not in r]
    failures = [r for r in results if 'error' in r]
    _log(f"  Successes: {len(successes)}, Failures: {len(failures)}")
    return results


def _collect_profiles(batch_path: str) -> list:
    """
    Resolve batch_path to a list of lead-profile.json files.
    Accepts: a directory, a glob pattern, or a text file with one path per line.
    """
    p = Path(batch_path)

    # Directory — find all lead-profile.json inside
    if p.is_dir():
        found = sorted(p.rglob('lead-profile.json'))
        if not found:
            # Fallback: any .json file
            found = sorted(p.rglob('*.json'))
        return [str(f) for f in found]

    # Text file listing paths
    if p.is_file() and p.suffix in ('.txt', '.list'):
        with open(p) as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        return lines

    # Glob pattern
    found = sorted(glob.glob(batch_path, recursive=True))
    return found


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate NotebookLM podcasts from lead profiles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single lead
  python3 generate-podcast.py lead-profile.json

  # Batch — directory of profiles
  python3 generate-podcast.py --batch ./leads/ --delay 90

  # Batch — glob pattern, 2 concurrent
  python3 generate-podcast.py --batch './leads/*/lead-profile.json' --max-concurrent 2
""",
    )

    parser.add_argument('profile', nargs='?', default=None,
                        help='Path to a single lead-profile.json')
    parser.add_argument('--batch', type=str, default=None,
                        help='Directory, glob, or list file of lead-profile.json files')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Output directory (default: ~/Desktop)')
    parser.add_argument('--delay', type=float, default=60,
                        help='Seconds to wait between notebook creations (default: 60)')
    parser.add_argument('--max-concurrent', type=int, default=1,
                        help='Max concurrent generations (default: 1 = sequential)')

    args = parser.parse_args()

    # Validate: need either a single profile or --batch
    if args.profile is None and args.batch is None:
        parser.print_help()
        print("\nExample lead-profile.json:")
        print(json.dumps({
            "lead_name": "Jane Smith",
            "business_name": "Smith Plumbing",
            "slug": "smith-plumbing",
            "industry": "plumbing and HVAC",
            "tools": "ServiceTitan, QuickBooks",
            "market": "residential homeowners in Denver metro",
            "service_type": "plumbing and HVAC services",
            "speed_to_lead_context": "responding to emergency plumbing calls before competitors"
        }, indent=2))
        sys.exit(1)

    output_dir = args.output_dir

    # --- Batch mode ---
    if args.batch is not None:
        profile_paths = _collect_profiles(args.batch)
        if not profile_paths:
            print(f"ERROR: No profile files found at: {args.batch}", file=sys.stderr)
            sys.exit(1)
        _log(f"Found {len(profile_paths)} profile(s)")
        for pp in profile_paths:
            _log(f"  -> {pp}")

        results = asyncio.run(
            run_batch(profile_paths, output_dir, args.delay, args.max_concurrent)
        )
        print(f"\nBatch results: {json.dumps(results, indent=2)}")
        sys.exit(0)

    # --- Single-lead mode ---
    result = asyncio.run(generate_podcast(args.profile, output_dir))
    print(f"\nResult: {json.dumps(result, indent=2)}")


if __name__ == '__main__':
    main()
