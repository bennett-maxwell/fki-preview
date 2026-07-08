#!/usr/bin/env python3
"""podcast_content_substance_gate.py — Red-line D3-11 (2026-07-07, Madison COO).

WHY THIS EXISTS
---------------
The Stage-4 podcast directive (blueprint-ai-skill v3.53) + the audit's D3-05 row
("Podcast source doc followed 7-segment framework") already REQUIRE the podcast to
substantively walk through the blueprint — the specific AI agents, their use-cases,
and the value AI delivers for the business — not just a generic intro/outro. But
NOTHING enforced that at the TRANSCRIPT level: D3-02 only checks the direct-address
opening (first ~180s), D3-03 checks duration, D3-05 checks a clean ending, D4-09
checks the SOURCE doc for funnel-clean framing. So a thin render that opens/closes
correctly but never actually names the lead's agents could PASS every gate.

This gate transcribes the FULL podcast (reusing the same faster-whisper path as the
direct-address / clean-ending gates) and FAILS unless the spoken content references a
threshold of the lead's ACTUAL agents (from leads/<slug>.json `agents[].name`) OR the
lead's key use-cases (from `oppmap[].usecase` / `gaps[].title`). It is a PODCAST_VERDICT
red-line only — per the 2026-07-07 DECOUPLE it gates the podcast attach/publish, NOT the
page/customer send.

PASS if:  agents_covered >= AGENT_MIN   (default 3, capped at #agents defined)
      OR  usecase_hits   >= USECASE_MIN (default 6)
N/A PASS if the lead JSON defines no agents AND no use-cases (nothing to check against).

Exit 0 = PASS/N/A; non-zero = substance FAIL (thin render — regenerate natively with a
source doc that walks each agent + the business value).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

AGENT_MIN_DEFAULT = 3       # distinct lead agents that must be referenced in the audio
USECASE_MIN_DEFAULT = 6     # alternative pass: distinct use-case keywords referenced

# Structural / generic tokens stripped from agent names before matching. Anything left
# (len >= 4) is a distinctive token; an agent is "covered" if any distinctive token is
# spoken. GENERIC_TOKENS are too common to be evidence an agent was actually discussed.
STOP_TOKENS = {
    "agent", "agents", "ai", "employee", "employees", "assistant", "bot",
    "the", "and", "for", "your", "with", "our", "a", "an", "of", "to", "on", "in",
}
GENERIC_TOKENS = {
    "local", "group", "before", "after", "content", "market", "sales", "lead",
    "leads", "customer", "customers", "business", "service", "services", "team",
    "system", "data", "time", "work", "help", "make", "need", "want", "more",
}


def run(cmd, timeout=240):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def transcribe_full(audio_path: Path) -> str:
    """Full-episode transcript. Prefers faster-whisper base.en (accurate on proper
    names); falls back to Google Web Speech in 60s chunks. Mirrors the transcription
    used by podcast_direct_address_audit.py so behavior is consistent across gates."""
    # Duration → transcribe the whole thing (not just the first 180s the other gates use).
    try:
        out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                   "-of", "csv=p=0", str(audio_path)], timeout=30).stdout.strip()
        total = int(float(out)) + 5
    except Exception:
        total = 1200
    try:
        from faster_whisper import WhisperModel
        clip = Path("/tmp") / f"pcs-{audio_path.stem}.wav"
        ff = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(audio_path),
                  "-ac", "1", "-ar", "16000", str(clip)], timeout=300)
        if ff.returncode == 0:
            model = WhisperModel("base.en", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(str(clip), beam_size=1)
            text = " ".join(s.text for s in segments).strip()
            if text:
                return text
    except Exception:
        pass
    # Fallback: Google Web Speech, full duration in 60s chunks.
    try:
        import speech_recognition as sr
    except Exception as exc:
        raise RuntimeError(f"no transcription backend available: {exc}") from exc
    tmp_root = Path("/tmp") / f"pcs-{audio_path.stem}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    recognizer = sr.Recognizer()
    chunks = []
    for start in range(0, total, 60):
        wav = tmp_root / f"chunk-{start}.wav"
        ff = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(audio_path),
                  "-ss", str(start), "-t", "60", "-ac", "1", "-ar", "16000", str(wav)], timeout=120)
        if ff.returncode != 0:
            break
        try:
            with sr.AudioFile(str(wav)) as source:
                audio = recognizer.record(source)
            chunks.append(recognizer.recognize_google(audio))
        except Exception:
            pass
    return " ".join(chunks)


AGENT_NAME_RE = re.compile(r'class="agent-name"[^>]*>(.*?)</', re.IGNORECASE | re.DOTALL)


def agents_from_html(html_path: Path):
    """Fallback agent source: extract the `<div class="agent-name">NAME</div>` labels
    from the RENDERED blueprint HTML when the lead JSON defines no agents[]. WHY: many
    form/GHL leads (e.g. mike-norton-origins) carry no `agents[]` in leads/<slug>.json —
    the 6 AI agents exist only in the generated blueprint HTML — so without this fallback
    the substance gate had nothing to check against, returned N/A, and SILENTLY PASSED a
    thin render. Reading the agent names off the page the customer actually receives makes
    the gate real for those leads instead of a no-op."""
    try:
        html = html_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    names = []
    for raw in AGENT_NAME_RE.findall(html):
        name = re.sub(r"<[^>]+>", " ", raw)          # strip any nested tags
        name = re.sub(r"&[#0-9a-zA-Z]+;", " ", name)  # strip HTML entities
        name = re.sub(r"\s+", " ", name).strip()
        if name and name not in names:
            names.append(name)
    return names


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", (text or "").lower())


def agent_tokens(name: str):
    toks = [t for t in re.split(r"[^a-z0-9]+", (name or "").lower()) if t]
    return [t for t in toks if len(t) >= 4 and t not in STOP_TOKENS]


def word_present(word: str, norm_text: str) -> bool:
    return re.search(rf"\b{re.escape(word)}", norm_text) is not None


def usecase_keywords(lead: dict):
    """Distinctive keywords drawn from the lead's use-cases / gaps / pillars."""
    blobs = []
    for u in lead.get("oppmap", []) or []:
        blobs.append(u.get("usecase", ""))
    for g in lead.get("gaps", []) or []:
        blobs.append(g.get("title", ""))
        blobs.append(g.get("desc", ""))
    for p in lead.get("pillars", []) or []:
        blobs.append(p.get("title", ""))
    words = set()
    for b in blobs:
        for t in re.split(r"[^a-z0-9]+", (b or "").lower()):
            if len(t) >= 5 and t not in GENERIC_TOKENS and t not in STOP_TOKENS:
                words.add(t)
    return sorted(words)


def evaluate(lead: dict, transcript: str, agent_min: int, usecase_min: int) -> dict:
    norm = normalize(transcript)
    agents = lead.get("agents") or lead.get("ai_agents") or []
    agent_names = [a.get("name", "") for a in agents if a.get("name")]

    covered = []
    for name in agent_names:
        toks = [t for t in agent_tokens(name) if t not in GENERIC_TOKENS] or agent_tokens(name)
        hit = [t for t in toks if word_present(t, norm)]
        if hit:
            covered.append({"agent": name, "matched_tokens": hit})

    kw = usecase_keywords(lead)
    kw_hits = [w for w in kw if word_present(w, norm)]

    n_agents = len(agent_names)
    n_usecases = len(kw)
    eff_agent_min = min(agent_min, n_agents) if n_agents else 0

    # Nothing in the lead JSON to check against → cannot enforce substance here.
    if n_agents == 0 and n_usecases == 0:
        return {
            "status": "N/A", "passed": True,
            "reason": "lead JSON defines no agents and no use-cases; transcript-substance check N/A",
            "agents_defined": 0, "agents_covered": 0, "usecase_keywords": 0, "usecase_hits": 0,
            "transcript_chars": len(transcript),
        }

    agents_ok = n_agents > 0 and len(covered) >= eff_agent_min
    usecase_ok = len(kw_hits) >= usecase_min
    passed = agents_ok or usecase_ok

    if passed:
        reason = (f"substantive: {len(covered)}/{n_agents} agents referenced"
                  f" (need {eff_agent_min}); {len(kw_hits)}/{n_usecases} use-case keywords")
    else:
        reason = (f"THIN render — only {len(covered)}/{n_agents} agents referenced"
                  f" (need {eff_agent_min}) and {len(kw_hits)}/{n_usecases} use-case keywords"
                  f" (need {usecase_min}); the podcast does not walk through the blueprint."
                  f" Regenerate natively with a source doc that covers each agent + the business value.")
    return {
        "status": "PASS" if passed else "FAIL", "passed": passed, "reason": reason,
        "agents_defined": n_agents, "agents_covered": len(covered),
        "agent_min_required": eff_agent_min, "covered_agents": covered,
        "uncovered_agents": [n for n in agent_names if n not in [c["agent"] for c in covered]],
        "usecase_keywords": n_usecases, "usecase_hits": len(kw_hits),
        "usecase_min_required": usecase_min, "matched_usecase_keywords": kw_hits[:25],
        "transcript_chars": len(transcript),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--lead-json", required=True)
    ap.add_argument("--blueprint-html", help="Rendered blueprint HTML; agent names are read "
                    "from its <div class=\"agent-name\"> labels when the lead JSON has no agents[]")
    ap.add_argument("--transcript-file", help="Use an existing transcript instead of transcribing")
    ap.add_argument("--agent-min", type=int, default=AGENT_MIN_DEFAULT)
    ap.add_argument("--usecase-min", type=int, default=USECASE_MIN_DEFAULT)
    ap.add_argument("--receipt")
    ap.add_argument("--json-output", action="store_true")
    args = ap.parse_args()

    audio_path = Path(args.audio)
    lead_path = Path(args.lead_json)
    result = {"audio": str(audio_path), "lead_json": str(lead_path)}
    try:
        lead = json.loads(lead_path.read_text(encoding="utf-8"))
    except Exception as exc:
        result.update({"status": "FAIL", "passed": False, "reason": f"lead JSON unreadable: {exc}"})
        print(json.dumps(result, indent=2)); return 1
    if not audio_path.exists():
        result.update({"status": "FAIL", "passed": False, "reason": "podcast audio missing"})
        print(json.dumps(result, indent=2)); return 1

    # HTML fallback: if the lead JSON carries no agents, pull the agent names off the
    # rendered blueprint HTML so the gate can still enforce substance (see agents_from_html).
    agents_source = "lead_json"
    existing_agents = lead.get("agents") or lead.get("ai_agents") or []
    if not existing_agents and args.blueprint_html and Path(args.blueprint_html).exists():
        html_agents = agents_from_html(Path(args.blueprint_html))
        if html_agents:
            lead["agents"] = [{"name": n} for n in html_agents]
            agents_source = "blueprint_html"
    result["agents_source"] = agents_source
    try:
        if args.transcript_file and Path(args.transcript_file).exists():
            transcript = Path(args.transcript_file).read_text(encoding="utf-8", errors="replace")
        else:
            transcript = transcribe_full(audio_path)
    except Exception as exc:
        result.update({"status": "FAIL", "passed": False, "reason": f"transcription failed: {exc}"})
        print(json.dumps(result, indent=2)); return 1

    result.update(evaluate(lead, transcript, args.agent_min, args.usecase_min))
    result["transcript_excerpt"] = transcript[:1500]

    if args.receipt:
        rp = Path(args.receipt)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"[{result['status']}] {result['reason']}")
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    sys.exit(main())
