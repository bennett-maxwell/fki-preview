#!/usr/bin/env python3
"""Blueprint agent prompt quality gate.

Blocks Blueprint pages where the advertised "production-ready" agents are only
short prompt starters. The gate checks both visible copy-paste prompt cards in
the HTML and, when provided, the lead profile's agent_prompt fields.
"""

import argparse
import html as html_lib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_MARKERS = {
    "identity": ["## identity", "identity"],
    "inputs": ["## inputs", "inputs you need", "input contract", "required inputs"],
    "workflow": ["## workflow", "## structure", "step 1", "operating loop"],
    "output": ["## output", "output schema", "return this", "deliverables"],
    "rules": ["## rules", "safety rules", "guardrails"],
    "escalation": ["escalat", "human review", "route to", "do not send"],
    "first_run_test": ["first-run test", "test input", "example input", "acceptance test"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def strip_tags(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</(?:p|div|li|h[1-6]|pre)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html_lib.unescape(text).strip()


def extract_pre_prompts(html: str) -> List[Dict[str, str]]:
    prompts = []
    for match in re.finditer(r'<pre\b[^>]*class=["\'][^"\']*prompt-pre[^"\']*["\'][^>]*>(.*?)</pre>', html, re.I | re.S):
        block = match.group(0)
        id_match = re.search(r'\bid=["\']([^"\']+)["\']', block, re.I)
        prompts.append({
            "label": id_match.group(1) if id_match else f"prompt_pre_{len(prompts) + 1}",
            "text": strip_tags(match.group(1)),
        })
    return prompts


def extract_agent_prompts(html: str) -> List[Dict[str, str]]:
    prompts = []
    for match in re.finditer(r'<div\b[^>]*class=["\'][^"\']*agent-prompt[^"\']*["\'][^>]*>(.*?)</div>', html, re.I | re.S):
        prompts.append({
            "label": f"agent_prompt_html_{len(prompts) + 1}",
            "text": strip_tags(match.group(1)).replace("Copy-paste prompt:", "").strip(),
        })
    return prompts


def extract_agent_cards(html: str) -> List[str]:
    """Return the raw HTML of each visible AI-agent square (.agent-card).

    v3.42 (Madison 2026-07-01): the 6 agent squares must be CONDENSED and
    outcome-first. They must NEVER carry a raw copy-paste operating prompt —
    that reads as a lazy paste and Madison ruled it out. We scan the raw card
    HTML (not stripped) so the check catches the boilerplate wherever it sits.
    """
    cards = []
    for match in re.finditer(
        r'<div\b[^>]*class=["\'][^"\']*\bagent-card\b[^"\']*["\'][^>]*>(.*?)</div>\s*</div>',
        html, re.I | re.S,
    ):
        cards.append(match.group(1))
    return cards


# Boilerplate that must NEVER appear inside an agent card (case-insensitive).
CARD_BANNED_SUBSTRINGS = [
    "you are an ai agent",   # raw copy-paste operating prompt leaked into the card
    "copy-paste prompt",     # the "Copy-paste prompt:" label
]


def check_agent_cards_no_boilerplate(html: str) -> List[str]:
    """v3.42 red-line: no agent card may contain a boilerplate copy-paste prompt."""
    failures = []
    cards = extract_agent_cards(html)
    for idx, card in enumerate(cards, start=1):
        low = card.lower()
        for banned in CARD_BANNED_SUBSTRINGS:
            if banned in low:
                failures.append(
                    f"agent card {idx}: contains banned boilerplate '{banned}' — "
                    "agent squares must be condensed outcome cards, never a raw copy-paste prompt"
                )
    return failures


def validate_prompt(text: str, label: str, min_chars: int) -> List[str]:
    failures = []
    raw = str(text or "").strip()
    low = raw.lower()
    if len(raw) < min_chars:
        failures.append(f"{label}: only {len(raw)} chars; need >= {min_chars}")
    for marker, needles in REQUIRED_MARKERS.items():
        if not any(needle in low for needle in needles):
            failures.append(f"{label}: missing {marker}")
    if re.search(r"\b(?:you are an ai agent for|create a response for|draft a message for)\b.{0,120}$", low, re.S):
        failures.append(f"{label}: appears to be a starter prompt, not an operating runbook")
    # v3.42: length + markers alone are not enough. A prompt that is only a bare
    # "You are an AI agent…" opener with no real body is a stub even if padded to
    # length. Require the structure markers (checked above) AND that the prompt is
    # not dominated by the boilerplate opener.
    if low.startswith("you are an ai agent") and len(raw) < min_chars * 1.5 and low.count("##") < 3:
        # short-ish, opener-led, and lacking multiple structured sections → filler risk
        if "## " not in low:
            failures.append(f"{label}: reads as a boilerplate starter (no structured sections), not a bulletproof runbook")
    return failures


def profile_prompts(profile_path: Path) -> List[Dict[str, str]]:
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    prompts = []
    for i, agent in enumerate(data.get("agents", []) or [], start=1):
        if not isinstance(agent, dict):
            continue
        text = agent.get("agent_prompt") or agent.get("prompt") or ""
        label = agent.get("name") or agent.get("title") or f"profile_agent_{i}"
        prompts.append({"label": f"profile agent {i} ({label})", "text": text})
    for i, prompt in enumerate(data.get("prompts", []) or [], start=1):
        if not isinstance(prompt, dict):
            continue
        text = prompt.get("pre") or prompt.get("prompt") or ""
        label = prompt.get("title") or prompt.get("h") or f"profile_visible_prompt_{i}"
        prompts.append({"label": f"profile visible prompt {i} ({label})", "text": text})
    return prompts


def write_receipt(path: Path, receipt: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", required=True, help="Blueprint HTML path")
    parser.add_argument("--profile", help="Lead profile JSON path")
    parser.add_argument("--receipt", help="Optional JSON receipt path")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()

    html_path = Path(args.html).resolve()
    html = html_path.read_text(encoding="utf-8", errors="replace")
    visible_prompts = extract_pre_prompts(html)
    html_agent_prompts = extract_agent_prompts(html)

    failures = []
    # v3.42 (Madison 2026-07-01) HARD RED-LINE: no agent square may contain a raw
    # copy-paste operating prompt / "You are an AI agent…" boilerplate / "Copy-paste
    # prompt:" label. Agent cards must be condensed, outcome-first squares.
    failures.extend(check_agent_cards_no_boilerplate(html))
    if len(visible_prompts) < 3:
        failures.append(f"visible prompt cards: found {len(visible_prompts)}; need at least 3")
    # OVERRIDE 2026-06-26 (Madison Lanz, "I own it"): D2-02 retired.
    # The 6 agent squares are now condensed and no longer carry an inline
    # copy-paste prompt, so we no longer require >=6 inline agent-prompt cards.
    # Full operating prompts are still required in the 3 visible dropdown cards
    # (checked above + below). Restore the >=6 inline check if Bennett reinstates D2-02.

    checked = []
    # The 3 ready-to-use dropdown prompts (prompt-pre) are the ONLY place full
    # operating runbooks live — each must be lead-specific and structurally
    # bulletproof (role/context/steps/guardrails/output + first-run test), not
    # just long. (v3.42)
    for prompt in visible_prompts[:3]:
        checked.append({"source": "html_visible_prompt", "label": prompt["label"], "chars": len(prompt["text"])})
        failures.extend(validate_prompt(prompt["text"], f"HTML visible prompt {prompt['label']}", 1200))
    # Inline agent-prompt cards are CONDENSED benefit/outcome teasers under v3.42 —
    # they are NOT full runbooks, so we do NOT re-validate them for length/markers.
    # Their only hard requirement is the boilerplate ban, enforced above via
    # check_agent_cards_no_boilerplate(). Record them for the receipt only.
    for prompt in html_agent_prompts:
        checked.append({"source": "html_agent_prompt", "label": prompt["label"], "chars": len(prompt["text"])})

    if args.profile:
        for prompt in profile_prompts(Path(args.profile).resolve()):
            checked.append({"source": "profile", "label": prompt["label"], "chars": len(prompt["text"])})
            if "visible prompt" in prompt["label"]:
                # Profile-side ready-to-use dropdown prompt → full runbook required.
                failures.extend(validate_prompt(prompt["text"], prompt["label"], 1200))
            else:
                # Profile-side agent card → condensed teaser; only ban boilerplate,
                # do not demand a full runbook (empty is fine, HTML renders outcome).
                low = str(prompt["text"] or "").lower()
                for banned in CARD_BANNED_SUBSTRINGS:
                    if banned in low:
                        failures.append(f"{prompt['label']}: contains banned boilerplate '{banned}' (agent cards must be condensed outcome teasers, not copy-paste prompts)")

    receipt = {
        "status": "PASS" if not failures else "FAIL",
        "pass": not failures,
        "ts": utc_now(),
        "html": str(html_path),
        "profile": str(Path(args.profile).resolve()) if args.profile else None,
        "checked": checked,
        "failures": failures,
        "required_markers": sorted(REQUIRED_MARKERS.keys()),
    }
    if args.receipt:
        write_receipt(Path(args.receipt), receipt)

    if args.json_output:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"Blueprint agent prompt quality gate: {receipt['status']}")
        for failure in failures[:20]:
            print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
