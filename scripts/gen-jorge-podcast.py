#!/usr/bin/env python3
"""One-off: generate Jorge / Capones USA blueprint podcast from the enriched,
sanitized, direct-address source doc (>=18KB). Mirrors blueprint-podcast-worker
pipeline (create -> add source -> generate SHORT -> wait 1200s -> download)."""
import asyncio, sys
from pathlib import Path

SLUG = "jorge-capones-usa"
FIRST = "Jorge"
BIZ = "Capones USA"
SRC = Path.home() / "Desktop" / f"{SLUG}-notebooklm-source-v2.md"
OUT = str(Path.home() / "Desktop" / "fki-preview" / "podcasts" / f"{SLUG}.mp3")

async def main():
    source_text = SRC.read_text(encoding="utf-8")
    b = len(source_text.encode())
    print(f"[{SLUG}] source bytes: {b}", flush=True)
    if b < 18_432:
        print("SOURCE TOO SMALL", flush=True); sys.exit(2)
    from notebooklm import NotebookLMClient, AudioLength
    client = await NotebookLMClient.from_storage()
    async with client:
        title = f"Blueprint AI — {BIZ} ({FIRST})"
        print(f"[{SLUG}] creating notebook: {title}", flush=True)
        notebook = await client.notebooks.create(title=title)
        print(f"[{SLUG}] notebook id {notebook.id}", flush=True)
        source = await client.sources.add_text(
            notebook.id, f"{BIZ} AI Roadmap", source_text,
            wait=True, wait_timeout=120.0,
        )
        print(f"[{SLUG}] source added {source.id}", flush=True)
        instructions = (
            f"Two hosts walk {FIRST} through this AI Advantage Roadmap built specifically "
            f"for {FIRST} and for {BIZ}, a premium men's grooming and fragrance brand. "
            f"Open by greeting {FIRST} by name and saying this walkthrough was built for "
            f"{FIRST} and {BIZ}. Speak directly to {FIRST} using you and your throughout. "
            f"Do NOT refer to a source document, brief, article, or analysis. Do not analyze "
            f"{FIRST} in the third person. Keep it warm, practical, and specific to a "
            f"consumer grooming and fragrance brand: faster inquiry response, easier "
            f"appointment booking, more leads captured, consistent follow-up. Never promise "
            f"pricing or fulfillment. Conversational and encouraging, about 9 to 12 minutes."
        )
        gen = await client.artifacts.generate_audio(
            notebook.id, source_ids=[source.id], instructions=instructions,
            audio_length=AudioLength.SHORT,
        )
        print(f"[{SLUG}] generating, task {gen.task_id}", flush=True)
        result = await client.artifacts.wait_for_completion(
            notebook.id, gen.task_id, timeout=1200.0,
        )
        print(f"[{SLUG}] status: {result.status}", flush=True)
        if result.status != "completed":
            print(f"[{SLUG}] FAILED: {getattr(result,'error',None)}", flush=True); sys.exit(3)
        await client.artifacts.download_audio(notebook.id, OUT)
        print(f"[{SLUG}] DOWNLOADED {OUT}", flush=True)
        print(f"[{SLUG}] NOTEBOOK {notebook.id}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
