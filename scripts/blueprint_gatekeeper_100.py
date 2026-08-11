#!/usr/bin/env python3
"""RETIRED — blueprint_gatekeeper_100.py is no longer the Blueprint send-token authority.

Madison directive 2026-08-11. Marker BLUEPRINT-SEND-TOKEN-AUDIT-GATE-CANONICAL-20260811.
Preimage preserved at scripts/blueprint_gatekeeper_100.py.RETIRED-20260811
(sha256 a3c5dd7361eaa1453599590b0f7ea771099ace3b1c17a633125b9ca2c8335cb8).
Rollback: cp scripts/blueprint_gatekeeper_100.py.RETIRED-20260811 scripts/blueprint_gatekeeper_100.py

WHY IT WAS RETIRED (evidence gathered 2026-08-10 while sending 4 real Blueprints):
  1. It demanded `<slug>-desktop-render.json`, `<slug>-mobile-render.json`, `<slug>-audit.json`
     and `<slug>-closeout.json` receipts that `clone-blueprint.sh` never emits — it emits
     completion-gate / clean-ending / production-47. So it could not pass on a normally-built lead.
  2. It carried a stale 480-720s podcast window while canon has been 240-960s since v3.50/v3.51,
     so it also failed every compliant native-SHORT render.
  3. Consequence: repo-wide 10 pass tokens vs 33 fail receipts, and recently-DELIVERED leads
     (sue-wright, karen-melting-pot-studio) carry NO token at all. The send path had silently
     stopped using it. A gate that cannot pass gets routed around, and a gate that gets routed
     around protects nothing — it was enforcement theatre.

WHAT REPLACED IT:
  `scripts/audit-gate.sh`, surfaced through `scripts/blueprint_send_token.py`. That is the
  hash-bound 100%-conformance token the audit skill's Hard-100 gate actually specifies, and it is
  the one the pipeline can satisfy. It binds the token to the SHA256 of the EXACT delivery-email
  bytes: edit the email after minting and the token stops authorizing it.

    python3 scripts/blueprint_send_token.py --mint   <slug>
    python3 scripts/blueprint_send_token.py --verify <slug>
    python3 scripts/blueprint_send_token.py --self-test

COVERAGE WAS TRANSFERRED, NOT DROPPED: this file was the only token-path caller of the D2-03
agent-card / ready-to-use-prompt quality gate. That gate now runs inside audit-gate.sh, verified
2026-08-11. Retiring it without moving D2-03 would have been a silent loss of coverage.

This shim FAILS CLOSED on every invocation. It never mints, never verifies, and never returns 0,
so no caller can accidentally treat it as an authorization.
"""
import sys

MSG = """
blueprint_gatekeeper_100.py is RETIRED (2026-08-11) and will never mint or verify a token.

Use the canonical send token instead:
    python3 scripts/blueprint_send_token.py --mint   <slug>    # audit-gate 100% -> hash-bound token
    python3 scripts/blueprint_send_token.py --verify <slug>    # exit 0 only if token matches bytes

Rationale + rollback are in this file's docstring.
Marker: BLUEPRINT-SEND-TOKEN-AUDIT-GATE-CANONICAL-20260811
"""


def main() -> int:
    sys.stderr.write(MSG)
    # Exit 2 (not 1) so a caller that merely checks "returncode != 0" still fails closed, while a
    # human reading logs can tell "retired tool invoked" apart from "gate legitimately failed".
    return 2


if __name__ == "__main__":
    sys.exit(main())
