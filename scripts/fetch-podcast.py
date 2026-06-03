#!/usr/bin/env python3
"""
fetch-podcast.py — long-poll + download a NotebookLM audio artifact to the
canonical podcasts/<slug>.mp3 path. Fixes two issues with generate-podcast.py for
our flow: (1) its 5-min poll often expires while NotebookLM is still rendering, and
(2) it writes <slug>-blueprint-podcast.mp3, but the audit + blueprint expect <slug>.mp3.

Modes:
  # attach to an already-rendering notebook (no new generation):
  python3 scripts/fetch-podcast.py --slug britt-warnick --notebook <NB_ID>
  # create a fresh notebook from a prebuilt source doc, then wait + download:
  python3 scripts/fetch-podcast.py --slug watson-kamoto --source podcasts/watson-kamoto-podcast-source.md
"""
import argparse, asyncio, importlib.util, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PODCASTS = os.path.join(REPO, "podcasts")

# Reuse the validated _ensure_real_mp3 from generate-podcast.py (hyphenated filename).
_spec = importlib.util.spec_from_file_location("genpod", os.path.join(REPO, "scripts", "generate-podcast.py"))
_genpod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_genpod)
_ensure_real_mp3 = _genpod._ensure_real_mp3


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def steering(first, business):
    """NotebookLM `instructions` steering — the only reliable lever to control the
    hosts' opening line and tone (the source-doc directive alone is ignored). Forces
    the exact on-brand opening, strict second-person, and positive (never-negative)
    framing — fixes the audit's D3-02 direct-address gate + the 'assume excellence' rule."""
    f = first or (business or "there")
    return (
        f'OPENING LINE MUST BE EXACTLY: "Hi {f}, welcome. This walkthrough was built for you and '
        f'{business}, from what you told us." Then proceed. '
        f'THROUGHOUT: speak DIRECTLY to {f} in second person using "you" and "your" — NEVER refer to {f} in the '
        f'third person, NEVER say "this business," "the owner," or "they." {f} is listening; speak TO {f}, not ABOUT {f}. '
        f'Tone: warm, personal, genuinely excited about what AI unlocks. The business is THRIVING — frame every '
        f'opportunity as an AI amplification, NEVER as a flaw, problem, chaos, or something broken. Do NOT open with a '
        f'negative hook. BANNED ANALYST FRAMING: never say "we are looking at", "we\'re looking at", "we are analyzing", '
        f'"let\'s look at", or otherwise narrate as outside analysts observing the business. Always speak directly to {f} '
        f'about what the system does FOR them — say "this gives you", "you\'ll get", "for you and {business}", not "we\'re looking at". '
        f'LENGTH IS REQUIRED: cover ALL 12 sections in real depth — aim for about 18 minutes of '
        f'conversation. Do NOT wrap up early, do NOT rush or summarize; give each of the 12 sections its own '
        f'substantive back-and-forth. ABSOLUTE HARD CEILING: never exceed 20 minutes — if in doubt, err shorter (17-18 min). '
        f'Close with the application CTA — never mention scheduling a call.'
    )


async def main(slug, notebook_id, source_path, business_name, first_name, timeout):
    from notebooklm import NotebookLMClient
    out = os.path.join(PODCASTS, f"{slug}.mp3")
    client = await NotebookLMClient.from_storage()
    async with client:
        if not notebook_id:
            content = open(source_path, encoding="utf-8").read()
            nb = await client.notebooks.create(title=f"{business_name or slug} AI Blueprint Podcast")
            notebook_id = nb.id
            log(f"notebook created: {notebook_id}")
            await client.sources.add_text(notebook_id, f"{business_name or slug} AI Blueprint", content, wait=True)
            log("source added")
            steer = steering(first_name, business_name)
            await client.artifacts.generate_audio(notebook_id, instructions=steer)
            log(f"audio generation requested (steered, {len(steer)} chars)")
        else:
            log(f"attaching to existing notebook: {notebook_id}")

        deadline = time.time() + timeout
        while time.time() < deadline:
            arts = await client.artifacts.list_audio(notebook_id)
            done = [a for a in arts if getattr(a, "status", None) == 3]
            if done:
                log(f"audio ready — artifact {done[0].id}")
                await client.artifacts.download_audio(notebook_id, out)
                if not os.path.exists(out):
                    raise RuntimeError(f"download reported ok but missing: {out}")
                out2 = _ensure_real_mp3(out)
                size_mb = os.path.getsize(out2) / (1024 * 1024)
                log(f"DOWNLOADED {out2} ({size_mb:.1f}MB)")
                print(f"RESULT_OK {out2} {size_mb:.1f}MB notebook={notebook_id}")
                return
            log("still rendering...")
            await asyncio.sleep(15)
        print(f"RESULT_TIMEOUT notebook={notebook_id} after {timeout}s")
        sys.exit(2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--notebook", default=None)
    ap.add_argument("--source", default=None)
    ap.add_argument("--business-name", default="")
    ap.add_argument("--first-name", default="")
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()
    if not a.notebook and not a.source:
        sys.exit("need --notebook (existing) or --source (create new)")
    asyncio.run(main(a.slug, a.notebook, a.source, a.business_name, a.first_name, a.timeout))
