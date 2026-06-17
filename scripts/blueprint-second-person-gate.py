#!/usr/bin/env python3
"""
blueprint-second-person-gate.py — PERMANENT GATE for GHL-form-driven builds.

Root cause it guards (garlon-maxwell + mark-bustamonte, 2026-06-16): when a lead
profile is authored from a GHL AI_Advantage_blueprint form submission, the copy was
narrated in THIRD PERSON about the owner ("his form says...", "both named on his
form", "his #1 goal") and shipped to the CUSTOMER-FACING page. The blueprint is
addressed TO the prospect — every customer-visible field must be SECOND PERSON
("your form", "you named", "your #1 goal"). It also caught an unsanitized GHL
revenue option value concatenated with its label ("u250k - under $250K").

Since every future Blueprint lead comes through the GHL form gate, this runs as a
hard check so a third-person / raw-value page can never ship again.

Usage:
  python3 scripts/blueprint-second-person-gate.py leads/<slug>.json          # check (exit 1 on fail)
  python3 scripts/blueprint-second-person-gate.py leads/<slug>.json --fix     # auto-rewrite + save
"""
import json, re, sys

# Customer-VISIBLE fields rendered onto the blueprint page (gen-blueprint.py).
# agent_prompt / lead_source / *_basis / *_declaration are internal-only -> skipped.
CUSTOMER_FIELDS = ["hero_sub", "profile_note", "results", "gaps", "oppmap",
                   "pillars", "stack", "ignore", "timeline", "demo",
                   "snapshot", "hero_stats", "calc", "cta_personal",
                   "agents.name", "agents.desc", "agents.outcome",
                   "prompts.title", "prompts.subtitle", "prompts.outcome"]

# Owner third-person -> second person. Order matters (longest first).
THIRD_PERSON = [
    (r"\bon his form\b", "on your form"), (r"\bon her form\b", "on your form"),
    (r"\bhis form\b", "your form"), (r"\bher form\b", "your form"),
    (r"\bhis business\b", "your business"), (r"\bher business\b", "your business"),
    (r"\bhis #(\d)\b", r"your #\1"), (r"\bher #(\d)\b", r"your #\1"),
    (r"\bhe named\b", "you named"), (r"\bshe named\b", "you named"),
    (r"\bhe flagged\b", "you flagged"), (r"\bshe flagged\b", "you flagged"),
    (r"\bhe told us\b", "you told us"), (r"\bshe told us\b", "you told us"),
    (r"\bhis stated\b", "your stated"), (r"\bher stated\b", "your stated"),
    (r"\bhis\b", "your"), (r"\bher\b", "your"),   # remaining owner-referring
]
# Detection pattern: any owner third-person pronoun in customer copy.
DETECT = re.compile(r"\b(his|her|he|she)\b", re.I)
# Malformed revenue/value: raw-code + " - " + label, e.g. "u250k - under $250K".
BADVAL = re.compile(r"^[a-z]?[a-z0-9]{2,8}\s*-\s*(.+)$")


def fields_of(profile, fix=False):
    """Yield (container, key) for every customer-visible string slot."""
    for spec in CUSTOMER_FIELDS:
        if "." in spec:
            parent, child = spec.split(".", 1)
            for item in (profile.get(parent) or []):
                if isinstance(item, dict) and child in item:
                    yield item, child
        else:
            node = profile.get(spec)
            if isinstance(node, str):
                yield profile, spec
            elif isinstance(node, dict):
                for k, v in node.items():
                    if isinstance(v, str): yield node, k
                    elif isinstance(v, list):
                        for it in v:
                            if isinstance(it, dict):
                                for kk, vv in it.items():
                                    if isinstance(vv, str): yield it, kk
            elif isinstance(node, list):
                for it in node:
                    if isinstance(it, dict):
                        for kk, vv in it.items():
                            if isinstance(vv, str): yield it, kk


def run(path, fix=False):
    prof = json.load(open(path, encoding="utf-8"))
    tp_hits, val_hits = [], []
    for cont, key in fields_of(prof):
        val = cont[key]
        # value-style fields (num/val) get the revenue sanitizer
        if key in ("num", "val"):
            m = BADVAL.match(val.strip())
            if m and ("$" in val or "under" in val.lower() or "over" in val.lower()):
                clean = m.group(1).strip()
                clean = clean[:1].upper() + clean[1:]
                val_hits.append((val, clean))
                if fix: cont[key] = clean; continue
        if DETECT.search(val):
            # report the ORIGINAL third-person (this is a gate, not residual-only)
            tp_hits.append((cont.get("title") or key, val[:120]))
            if fix:
                new = val
                for pat, rep in THIRD_PERSON:
                    new = re.sub(pat, rep, new)
                new = re.sub(r"\bHis form\b", "Your form", new)
                new = re.sub(r"\bHer form\b", "Your form", new)
                if new != val:
                    cont[key] = new
    if fix:
        json.dump(prof, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return tp_hits, val_hits


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: blueprint-second-person-gate.py leads/<slug>.json [--fix]")
    path = sys.argv[1]; fix = "--fix" in sys.argv[2:]
    tp, vh = run(path, fix=fix)
    if fix:
        print(f"[fixed] {path}: rewrote third-person + sanitized {len(vh)} value(s)")
        # re-scan after fix
        tp2, vh2 = run(path, fix=False)
        if tp2 or vh2:
            print("  REMAINING third-person:", tp2); print("  REMAINING bad values:", vh2)
            sys.exit(1)
        print("  clean after fix ✓"); sys.exit(0)
    fail = bool(tp or vh)
    print(f"[{'FAIL' if fail else 'PASS'}] second-person gate: {path}")
    for where, txt in tp: print(f"  ✗ THIRD-PERSON [{where}]: {txt}")
    for raw, clean in vh: print(f"  ✗ RAW VALUE: {raw!r} -> should be {clean!r}")
    sys.exit(1 if fail else 0)
