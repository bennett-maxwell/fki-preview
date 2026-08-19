#!/usr/bin/env python3
"""
Subset of research-blueprint-ai-skill scripts/research_packet_gate.py for the magnet.

Full gate wants >=14 evidence rows, identity lock, founder URLs, send_blocked.
Magnet lite: >=4 evidence rows, 3-6 AI Employees with finding+workflow+loop,
no invented founder trail, send_blocked true, soft claims allowed if labeled.

Usage:
  python3 api/research_packet_lite_gate.py            # self-test
  python3 api/research_packet_lite_gate.py packet.json
Exit 0 = PASS, 1 = FAIL.
"""
import json
import sys
from pathlib import Path

VALID_CONF = {"high", "medium", "low"}


def gate_lite(packet):
    if not isinstance(packet, dict):
        return False, "packet", "packet is not an object"
    if packet.get("send_blocked") is not True:
        return False, "send_block", "send_blocked must be true on the magnet lite packet"
    if packet.get("bennett_approval_token") not in (None, ""):
        return False, "send_block", "approval_token must be empty until Bennett approves a full send"

    el = packet.get("evidence_ledger") or []
    if len(el) < 4:
        return False, "evidence_floor_lite", f"evidence_ledger has {len(el)} rows, lite floor is 4"

    for row in el:
        conf = row.get("confidence")
        if conf is not None and conf not in VALID_CONF:
            return False, "confidence", f"ledger confidence '{conf}' not in {VALID_CONF}"

    profiler = packet.get("profiler") or {}
    employees = profiler.get("employees") or packet.get("ai_employees_initial") or []
    if not (3 <= len(employees) <= 6):
        return False, "ai_employees", f"need 3-6 AI Employees, got {len(employees)}"
    for emp in employees:
        if not emp.get("finding") or not emp.get("workflow") or not emp.get("loop"):
            return False, "ai_employees", "employee missing finding, workflow, or measurable loop"
        if not emp.get("name"):
            return False, "ai_employees", "employee missing name"

    founder = packet.get("founder") or {}
    if founder.get("career_trail") and not founder.get("thin_record"):
        return False, "founder", "lite packet must not ship an unsourced founder career trail"

    analyst = packet.get("analyst") or {}
    if not analyst.get("industry"):
        return False, "industry", "analyst.industry missing"
    if not (analyst.get("demographic") or []):
        return False, "demographic", "analyst.demographic missing"
    if not (analyst.get("competitors") or []):
        return False, "competitors", "industry AI Employee patterns missing"

    scout = packet.get("scout") or {}
    if not scout.get("host") and not scout.get("site"):
        return False, "scout", "scout host/site missing"

    return True, None, "lite gates passed"


def _good():
    return {
        "send_blocked": True,
        "bennett_approval_token": None,
        "scout": {"host": "recruiting4parents.com", "site": "https://recruiting4parents.com"},
        "analyst": {
            "industry": "High-school / youth sports recruiting",
            "demographic": [{"claim": "Parents of high-school athletes", "label": "homepage-inferred"}],
            "competitors": [{"claim": "Speed-to-lead on parent forms", "label": "industry pattern"}],
        },
        "profiler": {
            "employees": [
                {"name": "Speed-to-Lead Employee", "finding": "f", "workflow": "w", "loop": "l"},
                {"name": "Booking Employee", "finding": "f", "workflow": "w", "loop": "l"},
                {"name": "Parent Qualification Employee", "finding": "f", "workflow": "w", "loop": "l"},
            ]
        },
        "evidence_ledger": [
            {"id": "E-001", "claim": "headline", "confidence": "high"},
            {"id": "E-002", "claim": "wix", "confidence": "medium"},
            {"id": "E-003", "claim": "icp", "confidence": "medium"},
            {"id": "E-004", "claim": "leak", "confidence": "medium"},
        ],
        "founder": {"thin_record": True},
    }


def _bad_floor():
    p = _good()
    p["evidence_ledger"] = p["evidence_ledger"][:2]
    return p


def main():
    if len(sys.argv) == 1:
        ok, dim, reason = gate_lite(_good())
        if not ok:
            print("SELFTEST FAIL good packet", dim, reason)
            return 1
        bad, bdim, _ = gate_lite(_bad_floor())
        if bad:
            print("SELFTEST FAIL negative packet should fail")
            return 1
        print("GATE-LITE-PASS self-test")
        print("negative_hit", bdim)
        return 0
    path = Path(sys.argv[1])
    packet = json.loads(path.read_text())
    if "profiler" not in packet and "packet" in packet:
        packet = packet["packet"]
    ok, dim, reason = gate_lite(packet)
    print("GATE-LITE-PASS" if ok else "GATE-LITE-FAIL", dim or "", reason)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
