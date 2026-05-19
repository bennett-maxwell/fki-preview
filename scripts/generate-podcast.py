#!/usr/bin/env python3
"""
Blueprint AI Pipeline — Stage 4: Podcast Generation
Generates NotebookLM podcast from Blueprint HTML content.

Usage: python3 generate-podcast.py <lead-profile.json> [--output-dir ~/Desktop]

Requires: pip3 install notebooklm
Auth: Run notebooklm-py auth flow once first (stores in ~/.notebooklm/)
"""

import asyncio
import json
import sys
import os
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
            # Create notebook
            notebook = await client.notebooks.create(
                title=f"{business_name} AI Blueprint Podcast"
            )
            nb_id = notebook.id
            print(f"Notebook created: {nb_id}")

            # Add source
            await client.sources.add_text(
                nb_id,
                f"{business_name} AI Blueprint",
                source_content,
                wait=True
            )
            print("Source added")

            # Generate audio
            await client.artifacts.generate_audio(nb_id)
            print("Audio generation started...")

            # Poll for completion (max 5 min)
            for i in range(30):
                await asyncio.sleep(10)
                artifacts = await client.artifacts.list_audio(nb_id)
                for art in artifacts:
                    if art.status == 3:  # COMPLETED
                        print(f"Audio ready! Artifact: {art.id}")
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
                print(f"  Polling {i+1}/30...")

            print("WARNING: Audio generation timed out after 5 min")
            return {
                'notebook_id': nb_id,
                'status': 'timeout',
                'source_path': source_path,
            }

    except ImportError:
        print("ERROR: notebooklm not installed. Run: pip3 install notebooklm")
        return {'error': 'notebooklm not installed', 'source_path': source_path}
    except Exception as e:
        print(f"ERROR: {e}")
        return {'error': str(e), 'source_path': source_path}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 generate-podcast.py <lead-profile.json> [--output-dir DIR]")
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

    profile_path = sys.argv[1]
    output_dir = None
    if '--output-dir' in sys.argv:
        idx = sys.argv.index('--output-dir')
        output_dir = sys.argv[idx + 1]

    result = asyncio.run(generate_podcast(profile_path, output_dir))
    print(f"\nResult: {json.dumps(result, indent=2)}")
