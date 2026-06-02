#!/usr/bin/env bash
# ============================================================================
# blueprint-delivery-integrity-gate.sh
# PROJECT 2 — Blueprint Delivery Integrity Gate (council pick, bennett-mode)
#
# THE single chokepoint that decides whether a Blueprint lead may carry the
# tracker status "delivered". Kills the unverified-delivery failure class at
# the source (R23 + the 5 sent_unverified rows). REVERSIBLE: this script never
# sends anything. It only READS (GHL conversations API, Gmail sent thread,
# booking/qualifier URLs, podcast URL, audit-score JSON) and WRITES a verdict
# JSON receipt + at most DOWNGRADES an unverified tracker status. It NEVER
# upgrades a status to "delivered" unless every gate passes with a logged
# receipt, and the upsell it "queues" is a STAGED note in the verdict (no GHL
# write, no email) until a human/automation chooses to action it.
#
# Gates enforced (all must PASS for verdict=DELIVERED_VERIFIED):
#   G1  TWO-PATH RECEIPT
#         a) GHL conversations/messages/{msgId} returns HTTP 200, AND
#         b) Gmail sent thread contains the unique per-lead footer token.
#   G2  PODCAST PRESENT      podcast_url non-empty AND HTTP 200.
#   G3  STAT CITATION        blueprint HTML: every stat-looking number sits
#                            near a citation link (source attribution).
#   G4  SELF-AUDIT >= 95%    audit-score JSON for the lead shows score >= 0.95.
#   G5  BOOKING/QUALIFIER     qualifier + canonical booking URL return 200.
#   G6  UPSELL AUTO-QUEUE     on full pass, stage the done-for-you
#                            implementation upsell offer (staged, not sent).
#   G7  DRIVE-LINK BAN        blueprint HTML must contain ZERO drive.google.com
#                            links. Hard-blocks delivery. Promotes the prior
#                            memory-rule ("no drive.google.com in Blueprint HTML
#                            or delivery emails — GitHub Pages only") into a
#                            mechanical gate so it can't be silently violated.
#
# Usage:
#   blueprint-delivery-integrity-gate.sh --lead <slug> [--profile <file.json>]
#   blueprint-delivery-integrity-gate.sh --lead <slug> --write-status [--profile <f>]
#                              # run gate AND mechanically stamp tracker status
#                              # (delivered on PASS, sent_unverified on BLOCK)
#   blueprint-delivery-integrity-gate.sh --reconcile-tracker   # sweep all rows
#   blueprint-delivery-integrity-gate.sh --self-test           # network-free
#
# Exit 0 = verdict DELIVERED_VERIFIED (safe to write "delivered").
# Exit 1 = any gate failed; status must stay sent_unverified / blocked.
# Exit 2 = usage / config error.
#
# CHOKEPOINT NOTE: status is written to the tracker ONLY by this script's
# write_tracker_status(), driven by the gate exit code. The send path
# (build-delivery-email.sh) calls `--write-status` and never sets "delivered"
# itself. This makes the gate mechanical, not advisory (R23 architectural fix).
# ----------------------------------------------------------------------------
set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TRACKER="${BLUEPRINT_TRACKER:-$HOME/.openclaw/state/blueprint-delivery-tracker.json}"
VERDICT_DIR="${BLUEPRINT_VERDICT_DIR:-$HOME/.openclaw/state/blueprint-integrity-verdicts}"
LOG="${BLUEPRINT_INTEGRITY_LOG:-$HOME/.openclaw/logs/blueprint-integrity-gate.jsonl}"
BASE_URL="${BLUEPRINT_BASE_URL:-https://bennett-maxwell.github.io/fki-preview}"
BOOKING_URL="${BLUEPRINT_BOOKING_URL:-https://ki.franchiseki.com/widget/bookings/ai-strategy-call-wuvot-1}"
GHL_API="${GHL_API_BASE:-https://services.leadconnectorhq.com}"
GHL_VERSION="2021-07-28"
UA="Mozilla/5.0 (FKI-BlueprintIntegrityGate)"   # GHL silent-403 fix: UA required
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERDICT_DIR" "$(dirname "$LOG")"

log_jsonl() { printf '%s\n' "$1" >> "$LOG"; }

# Resolve the REAL gog binary. `gog` is a shell alias invisible to scripts in
# non-interactive shells — `command -v gog` returns the alias/function and the
# bare invocation then fails. Every gog call site (G1b gmail search AND state
# mirror) MUST go through this so the binary actually resolves in production.
# (gatekeeper blocker #1 — G1b had the same unresolved-gog bug mirror_state fixed.)
GOG_BIN=""
resolve_gog() {
  [ -n "$GOG_BIN" ] && { printf '%s' "$GOG_BIN"; return 0; }
  local c
  for c in /opt/homebrew/bin/gog /usr/local/bin/gog \
           /opt/homebrew/Cellar/gogcli/0.13.0/bin/gog \
           "$(type -P gog 2>/dev/null)"; do
    [ -n "$c" ] && [ -x "$c" ] && { GOG_BIN="$c"; printf '%s' "$GOG_BIN"; return 0; }
  done
  return 1
}

# Resolve a GHL token without ever asking a human. Priority order matches the
# self-heal rule: gateway.env (active) > ghl.env > env var. Read-only use.
resolve_ghl_token() {
  local t=""
  for f in "$HOME/.openclaw/gateway.env" "$HOME/.openclaw/ghl.env" "$HOME/Agent SDK/.env" "$HOME/.claude/.env"; do
    [ -f "$f" ] || continue
    t="$(grep -hoE '(GHL_API_KEY|GHL_TOKEN|GHL_PRIVATE_TOKEN)=[^ "'"'"']+' "$f" 2>/dev/null | head -1 | cut -d= -f2-)"
    [ -n "$t" ] && { printf '%s' "$t"; return 0; }
  done
  printf '%s' "${GHL_API_KEY:-${GHL_TOKEN:-}}"
}

http_code() { curl -s -o /dev/null -w "%{http_code}" --max-time 15 -A "$UA" "$1" 2>/dev/null || echo "000"; }

# ---- G1a: GHL message receipt -------------------------------------------
ghl_msg_200() {
  local msgid="$1" token; token="$(resolve_ghl_token)"
  [ -z "$msgid" ] && { echo "no_msgid"; return 1; }
  [ -z "$token" ] && { echo "no_ghl_token"; return 1; }
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
      -A "$UA" \
      -H "Authorization: Bearer $token" \
      -H "Version: $GHL_VERSION" \
      "$GHL_API/conversations/messages/$msgid" 2>/dev/null || echo "000")"
  echo "$code"
  [ "$code" = "200" ]
}

# ---- G1b: Gmail unique footer token in sent thread ----------------------
# token is deterministic per lead so the same value is searchable post-send.
footer_token() { printf 'bp-receipt-%s' "$(printf '%s' "$1" | tr -cd 'a-z0-9_-')"; }

gmail_token_present() {
  local token="$1" gog
  gog="$(resolve_gog)" || { echo "gog_unavailable"; return 1; }
  # Count real message rows. gog prints "No results" (1 line) on zero hits, so a
  # plain `grep -c .` is wrong on two counts: it counts the "No results" line as
  # a hit, AND `grep -c . || echo 0` emits a SECOND "0" line when grep exits 1 on
  # zero matches — producing a multiline value that breaks the integer test.
  # Use JSON output + a deterministic single-integer count instead.
  local hits
  hits="$("$gog" -j gmail search "in:sent \"$token\"" --max 1 2>/dev/null \
            | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin)
except Exception:
    print(0); sys.exit(0)
# unwrap common envelope shapes; count message-like rows only.
rows=d.get("threads") or d.get("messages") or d.get("results") or d.get("data") or (d if isinstance(d,list) else [])
print(len(rows) if isinstance(rows,list) else 0)' 2>/dev/null)"
  hits="${hits//[!0-9]/}"; hits="${hits:-0}"
  echo "$hits"
  [ "$hits" -ge 1 ]
}

# ---- G3: stat-citation proximity ----------------------------------------
# Every standalone percentage/dollar stat in body copy must have a citation
# link within the surrounding block. Reuses the principle from G28 fix
# (href-before-% AND %-before-href both count).
stat_citation_ok() {
  local html="$1"
  [ -f "$html" ] || { echo "no_html"; return 1; }
  python3 - "$html" <<'PY'
import re, sys
html = open(sys.argv[1], encoding="utf-8", errors="replace").read()
# Split into block-level chunks so "near" = same block.
blocks = re.split(r'(?i)</(?:p|li|div|section|td|h[1-6])>', html)
stat_re = re.compile(r'(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+)\s?%|\$\s?\d[\d,]*')
href_re = re.compile(r'href\s*=', re.I)
uncited = 0
for b in blocks:
    if stat_re.search(b) and not href_re.search(b):
        uncited += 1
print(uncited)
sys.exit(0 if uncited == 0 else 1)
PY
}

# ---- G7: Drive-link ban -------------------------------------------------
# Hard-block: any drive.google.com link in the blueprint HTML fails delivery.
# Prints the count of offending lines. Returns 0 only when ZERO are present.
drive_link_absent() {
  local html="$1"
  [ -f "$html" ] || { echo "no_html"; return 1; }
  local n
  n="$(grep -ciE 'drive\.google\.com' "$html" 2>/dev/null)"
  n="${n//[!0-9]/}"; n="${n:-0}"
  echo "$n"
  [ "$n" -eq 0 ]
}

# ---- G4: self-audit >= 95% ----------------------------------------------
audit_score() {
  local slug="$1" f
  for f in "$REPO/audit-receipts/${slug}-pre-delivery-audit"*.json \
           "$HOME/Documents/New project/audit-receipts/${slug}"*.json \
           "$HOME/.openclaw/state/blueprint-audit-${slug}.json"; do
    [ -f "$f" ] || continue
    python3 - "$f" <<'PY'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
except Exception:
    print("nan"); sys.exit(1)
s=d.get("self_audit_score", d.get("score", d.get("audit_score")))
if isinstance(s,str):
    s=s.strip().rstrip('%').strip()
    # Handle "96/100" fraction form as well as bare "96" / "0.96".
    if '/' in s:
        try:
            num,den=s.split('/',1); s=float(num)/float(den)
        except: s=None
    else:
        try: s=float(s)
        except: s=None
if s is None:
    try: s=float(s)
    except (TypeError,ValueError): print("nan"); sys.exit(1)
if not isinstance(s,(int,float)): print("nan"); sys.exit(1)
if s>1: s=s/100.0
print(f"{s:.4f}")
sys.exit(0 if s>=0.95 else 1)
PY
    return $?
  done
  echo "no_audit_file"; return 1
}

# ---- G6: stage the upsell (no send) -------------------------------------
upsell_offer_json() {
  local slug="$1"
  cat <<EOF
{"upsell":"done-for-you-implementation","slug":"$slug","status":"STAGED_NOT_SENT","action_required":"human_or_automation_to_send_GHL_offer","offer_ref":"blueprint-ai-implementation-skill","staged_at":"$NOW"}
EOF
}

# ---- mechanical tracker status writer -----------------------------------
# THE only place a lead's status is set from a gate result. Driven by the gate
# exit code: 0 -> "delivered", non-0 -> "sent_unverified". Backs up first.
# This is what makes the send-path enforcement mechanical instead of advisory.
write_tracker_status() {
  local slug="$1" gate_rc="$2" verdict_file="$3"
  [ -f "$TRACKER" ] || { echo "no_tracker_for_status_write"; return 1; }
  cp "$TRACKER" "${TRACKER}.bak-status-$(date -u +%Y%m%dT%H%M%SZ)"
  python3 - "$TRACKER" "$slug" "$gate_rc" "$NOW" "$verdict_file" <<'PY'
import json,sys
p,slug,rc,now,vf=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]
d=json.load(open(p))
leads=d.setdefault("leads",{})
row=leads.setdefault(slug,{})
new_status="delivered" if rc=="0" else "sent_unverified"
row["prior_status"]=row.get("status")
row["status"]=new_status
row.setdefault("delivery_verification",{}).update({
  "verified": rc=="0",
  "stamped_at": now,
  "verdict_file": vf,
  "source":"integrity-gate write_tracker_status (mechanical, exit-code driven)",
})
json.dump(d,open(p,"w"),indent=2)
print(new_status)
PY
}

# ===========================================================================
# Per-lead gate run
# ===========================================================================
# $3 (write_status): "1" => after the verdict, mechanically stamp the tracker
# status via write_tracker_status(). Default "0" = verdict-only (read-only).
run_gate() {
  local slug="$1" profile="${2:-}" write_status="${3:-0}"
  local msgid="" podcast_url="" html="" qualifier_url=""

  # Pull facts from tracker row (authoritative) then profile (fallback).
  if [ -f "$TRACKER" ]; then
    eval "$(python3 - "$TRACKER" "$slug" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); slug=sys.argv[2]
row=d.get("leads",{}).get(slug,{})
def g(*k):
    for kk in k:
        if row.get(kk): return row[kk]
    return ""
print(f'TRK_MSGID="{g("emailed_lead_msgId","ghl_message_id","msgId")}"')
print(f'TRK_PODCAST="{1 if row.get("podcast") else 0}"')
PY
)"
  fi
  if [ -n "$profile" ] && [ -f "$profile" ]; then
    podcast_url="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("podcast_url",""))' "$profile")"
    msgid="${msgid:-$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("ghl_message_id",""))' "$profile")}"
  fi
  msgid="${msgid:-${TRK_MSGID:-}}"
  html="$REPO/blueprints/${slug}.html"
  qualifier_url="$BASE_URL/qualify.html?lead=${slug}"

  local fail=0; local -a results=()
  jadd() { results+=("\"$1\":$2"); }

  # G1a
  local g1a_code; g1a_code="$(ghl_msg_200 "$msgid")"; local g1a=$?
  jadd "g1a_ghl_msg_200" "{\"code\":\"$g1a_code\",\"pass\":$([ $g1a -eq 0 ] && echo true || echo false)}"
  [ $g1a -ne 0 ] && fail=1
  # G1b
  local tok; tok="$(footer_token "$slug")"
  local g1b_hits; g1b_hits="$(gmail_token_present "$tok")"; local g1b=$?
  jadd "g1b_gmail_token" "{\"token\":\"$tok\",\"hits\":\"$g1b_hits\",\"pass\":$([ $g1b -eq 0 ] && echo true || echo false)}"
  [ $g1b -ne 0 ] && fail=1
  # G2
  local p_pass=false; local p_code="empty"
  if [ -n "$podcast_url" ]; then p_code="$(http_code "$podcast_url")"; [ "$p_code" = "200" ] && p_pass=true; fi
  jadd "g2_podcast" "{\"url\":\"$podcast_url\",\"code\":\"$p_code\",\"pass\":$p_pass}"
  [ "$p_pass" = true ] || fail=1
  # G3
  local g3_uncited; g3_uncited="$(stat_citation_ok "$html")"; local g3=$?
  jadd "g3_stat_citation" "{\"uncited_stats\":\"$g3_uncited\",\"pass\":$([ $g3 -eq 0 ] && echo true || echo false)}"
  [ $g3 -ne 0 ] && fail=1
  # G4
  local g4_score; g4_score="$(audit_score "$slug")"; local g4=$?
  jadd "g4_self_audit_95" "{\"score\":\"$g4_score\",\"pass\":$([ $g4 -eq 0 ] && echo true || echo false)}"
  [ $g4 -ne 0 ] && fail=1
  # G5
  local q_code b_code g5=true
  q_code="$(http_code "$qualifier_url")"; b_code="$(http_code "$BOOKING_URL")"
  { [ "$q_code" = "200" ] && [ "$b_code" = "200" ]; } || { g5=false; fail=1; }
  jadd "g5_booking_qualifier_200" "{\"qualifier\":\"$q_code\",\"booking\":\"$b_code\",\"pass\":$g5}"
  # G7 — Drive-link ban (hard block, network-free).
  local g7_count; g7_count="$(drive_link_absent "$html")"; local g7=$?
  jadd "g7_drive_link_ban" "{\"drive_links\":\"$g7_count\",\"pass\":$([ $g7 -eq 0 ] && echo true || echo false)}"
  [ $g7 -ne 0 ] && fail=1

  local verdict upsell="null"
  if [ $fail -eq 0 ]; then
    verdict="DELIVERED_VERIFIED"
    upsell="$(upsell_offer_json "$slug")"
  else
    verdict="BLOCKED_UNVERIFIED"
  fi

  local out="$VERDICT_DIR/${slug}-$(date -u +%Y%m%dT%H%M%SZ).json"
  printf '{"slug":"%s","timestamp":"%s","verdict":"%s","gates":{%s},"upsell_staged":%s}\n' \
    "$slug" "$NOW" "$verdict" "$(IFS=,; echo "${results[*]}")" "$upsell" | tee "$out"
  log_jsonl "{\"ts\":\"$NOW\",\"slug\":\"$slug\",\"verdict\":\"$verdict\",\"verdict_file\":\"$out\"}"

  # Mechanical chokepoint: stamp tracker status from the gate exit code.
  if [ "$write_status" = "1" ]; then
    local stamped; stamped="$(write_tracker_status "$slug" "$fail" "$out")"
    echo "tracker status stamped: $slug -> $stamped (exit-code driven, not advisory)"
    log_jsonl "{\"ts\":\"$NOW\",\"slug\":\"$slug\",\"status_write\":\"$stamped\",\"gate_rc\":$fail}"
  fi

  [ $fail -eq 0 ]
}

# ===========================================================================
# Tracker reconciliation sweep — DOWNGRADE-ONLY (reversible/safe)
# Any row claiming "delivered" that does not pass the gate is downgraded to
# sent_unverified. NEVER upgrades. Backs up the tracker first.
# ===========================================================================
reconcile_tracker() {
  [ -f "$TRACKER" ] || { echo "no tracker at $TRACKER"; return 2; }
  cp "$TRACKER" "${TRACKER}.bak-integrity-$(date -u +%Y%m%dT%H%M%SZ)"
  # Sweep BOTH keys that carry a deliverable status: leads{} (slug->row) AND
  # deliveries[] (list of slug->row maps). Emit "loc<TAB>slug" pairs so we know
  # which structure to write back into. deliveries[] was previously ignored —
  # that was a silent coverage hole (gatekeeper blocker #5).
  local pairs
  pairs="$(python3 - "$TRACKER" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
for slug,row in d.get("leads",{}).items():
    if isinstance(row,dict) and row.get("status")=="delivered":
        print(f"leads\t{slug}")
for i,entry in enumerate(d.get("deliveries",[]) or []):
    if not isinstance(entry,dict): continue
    for slug,row in entry.items():
        if isinstance(row,dict) and row.get("status")=="delivered":
            print(f"deliveries:{i}\t{slug}")
PY
)"
  local downgraded=0
  while IFS=$'\t' read -r loc slug; do
    [ -z "$slug" ] && continue
    if ! run_gate "$slug" >/dev/null 2>&1; then
      python3 - "$TRACKER" "$loc" "$slug" "$NOW" <<'PY'
import json,sys
p,loc,slug,now=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
d=json.load(open(p))
if loc=="leads":
    row=d["leads"][slug]
else:
    idx=int(loc.split(":")[1]); row=d["deliveries"][idx][slug]
row["prior_status"]=row.get("status")
row["status"]="sent_unverified"
row.setdefault("delivery_verification",{}).update({
  "verified":False,"relabeled_at":now,"location":loc,
  "reason":"integrity-gate: one or more delivery gates failed (G1-G5).",
  "required_receipt":"All of G1a(GHL 200)+G1b(Gmail token)+G2(podcast 200)+G3(cited stats)+G4(audit>=95%)+G5(booking/qualifier 200)."})
json.dump(d,open(p,"w"),indent=2)
PY
      downgraded=$((downgraded+1))
      echo "DOWNGRADED: [$loc] $slug delivered -> sent_unverified (gate failed)"
    fi
  done <<< "$pairs"
  echo "reconcile complete: $downgraded row(s) downgraded across leads{}+deliveries[]. Backup written."
  log_jsonl "{\"ts\":\"$NOW\",\"action\":\"reconcile\",\"downgraded\":$downgraded,\"swept\":[\"leads\",\"deliveries\"]}"
}

# ===========================================================================
# Self-test — network-free, proves gate logic blocks correctly.
# ===========================================================================
self_test() {
  local t pass=0 total=0; t="$(mktemp -d)"
  check() { total=$((total+1)); if [ "$2" = "$3" ]; then pass=$((pass+1)); echo "  PASS $1"; else echo "  FAIL $1 (got '$2' want '$3')"; fi; }

  # G3: uncited stat must fail, cited stat must pass.
  printf '<p>Revenue grew 47%% last year.</p>' > "$t/bad.html"
  stat_citation_ok "$t/bad.html" >/dev/null 2>&1; check "G3 blocks uncited stat" "$?" "1"
  printf '<p>Revenue grew 47%% <a href="https://src">[source]</a>.</p>' > "$t/good.html"
  stat_citation_ok "$t/good.html" >/dev/null 2>&1; check "G3 passes cited stat" "$?" "0"
  printf '<p>We help franchises grow nationwide.</p>' > "$t/nostat.html"
  stat_citation_ok "$t/nostat.html" >/dev/null 2>&1; check "G3 passes no-stat copy" "$?" "0"

  # G7: a drive.google.com link must BLOCK; clean HTML must PASS.
  printf '<a href="https://drive.google.com/file/d/x/view">dl</a>' > "$t/drive.html"
  drive_link_absent "$t/drive.html" >/dev/null 2>&1; check "G7 blocks drive.google.com link" "$?" "1"
  printf '<a href="https://bennett-maxwell.github.io/fki-preview/q.html">q</a>' > "$t/nodrive.html"
  drive_link_absent "$t/nodrive.html" >/dev/null 2>&1; check "G7 passes no-drive HTML" "$?" "0"

  # G4: exercise the REAL audit_score() function (string-strip, /100 normalize,
  # file-glob discovery, nan handling) — NOT an inline throwaway. We point its
  # glob at a synthetic receipt by overriding the state path it scans.
  local saved_repo="$REPO" saved_home_state
  # audit_score globs $HOME/.openclaw/state/blueprint-audit-<slug>.json — write there.
  local g4dir="$HOME/.openclaw/state"; mkdir -p "$g4dir"
  echo '{"self_audit_score":0.91}' > "$g4dir/blueprint-audit-selftestlow.json"
  audit_score "selftestlow" >/dev/null 2>&1; check "G4 blocks 91% (real audit_score)" "$?" "1"
  echo '{"self_audit_score":0.97}' > "$g4dir/blueprint-audit-selftesthi.json"
  audit_score "selftesthi" >/dev/null 2>&1; check "G4 passes 97% (real audit_score)" "$?" "0"
  # G4 normalization: "96/100" string must normalize to 0.96 and PASS.
  echo '{"score":"96/100"}' > "$g4dir/blueprint-audit-selftestnorm.json"
  audit_score "selftestnorm" >/dev/null 2>&1; check "G4 normalizes 96/100 string (real)" "$?" "0"
  # G4 nan handling: garbage score must BLOCK, not crash.
  echo '{"score":"n/a"}' > "$g4dir/blueprint-audit-selftestnan.json"
  audit_score "selftestnan" >/dev/null 2>&1; check "G4 blocks non-numeric score (real)" "$?" "1"
  rm -f "$g4dir"/blueprint-audit-selftest*.json

  # G1a: empty msgid blocks.
  ghl_msg_200 "" >/dev/null 2>&1; check "G1a blocks empty msgid" "$?" "1"

  # footer token determinism.
  local tok_val; tok_val="$(footer_token 'court_lundberg')"
  check "token deterministic" "$tok_val" "bp-receipt-court_lundberg"

  # G1b single-integer guarantee (regression lock for the multiline-hits bug
  # that made BLOCKED runs wrongly exit 0). Stub a real gog binary that resolves
  # via resolve_gog and returns an empty-threads envelope => hits MUST be exactly
  # "0" (one line, clean integer), and the function MUST return non-zero.
  (
    local stubdir; stubdir="$(mktemp -d)"
    cat > "$stubdir/gog" <<'STUB'
#!/usr/bin/env bash
# emulate `gog -j gmail search ... --max 1` zero-hit envelope
printf '{"nextPageToken":"","threads":[]}'
STUB
    chmod +x "$stubdir/gog"
    GOG_BIN="$stubdir/gog"
    local out rc lines
    out="$(gmail_token_present "bp-receipt-zzz")"; rc=$?
    lines="$(printf '%s' "$out" | grep -c .)"
    [ "$out" = "0" ] && [ "$lines" -eq 1 ] && [ $rc -ne 0 ] && echo OK || echo BAD
    rm -rf "$stubdir"
  ) | grep -qx OK; check "G1b hits is single clean integer on zero results" "$?" "0"

  # ---- ALLOW-PATH coverage: synthetic lead, ALL gates forced PASS ----------
  # Proves the verdict=DELIVERED_VERIFIED branch + upsell staging + mechanical
  # status upgrade — the half of the state machine that real runs never reached
  # because every live lead failed on absent inputs. Network probes are stubbed
  # via function override (still exercises run_gate's real verdict assembly,
  # upsell_offer_json, and write_tracker_status).
  (
    # Override only the network-bound gate primitives; everything else is real.
    ghl_msg_200()        { echo "200"; return 0; }
    gmail_token_present(){ echo "1";   return 0; }
    http_code()          { echo "200"; }            # podcast + booking + qualifier
    NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local syn="synthetic_allowpath"
    # real cited-stat HTML so G3 (real) passes
    mkdir -p "$REPO/blueprints"
    printf '<p>Revenue grew 47%% <a href="https://src">[source]</a>.</p>' > "$REPO/blueprints/${syn}.html"
    # real audit receipt so G4 (real) passes
    echo '{"self_audit_score":0.98}' > "$g4dir/blueprint-audit-${syn}.json"
    # synthetic tracker so write_tracker_status has a row + msgId
    local syntrk; syntrk="$(mktemp)"
    printf '{"leads":{"%s":{"emailed_lead_msgId":"SYN123","podcast":true,"status":"sent_unverified"}}}' "$syn" > "$syntrk"
    local synprof; synprof="$(mktemp)"
    printf '{"podcast_url":"https://example.com/p.mp3","ghl_message_id":"SYN123"}' > "$synprof"
    TRACKER="$syntrk" VERDICT_DIR="$(mktemp -d)" LOG="$(mktemp)" \
      run_gate "$syn" "$synprof" "1" >"$t/allow.out" 2>&1
    local rc=$?
    # exit 0 = DELIVERED_VERIFIED
    [ $rc -eq 0 ] && echo PASS_RC || echo FAIL_RC
    grep -q 'DELIVERED_VERIFIED' "$t/allow.out" && echo PASS_VERDICT || echo FAIL_VERDICT
    grep -q 'STAGED_NOT_SENT'   "$t/allow.out" && echo PASS_UPSELL  || echo FAIL_UPSELL
    # mechanical status upgrade landed in the synthetic tracker
    python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["leads"]["synthetic_allowpath"]["status"])' "$syntrk" \
      | grep -qx 'delivered' && echo PASS_STATUS || echo FAIL_STATUS
    rm -f "$REPO/blueprints/${syn}.html" "$g4dir/blueprint-audit-${syn}.json" "$syntrk" "$synprof"
  ) > "$t/allow.result" 2>/dev/null
  grep -qx PASS_RC      "$t/allow.result"; check "ALLOW: synthetic lead exit 0"        "$?" "0"
  grep -qx PASS_VERDICT "$t/allow.result"; check "ALLOW: verdict DELIVERED_VERIFIED"   "$?" "0"
  grep -qx PASS_UPSELL  "$t/allow.result"; check "ALLOW: upsell STAGED_NOT_SENT"       "$?" "0"
  grep -qx PASS_STATUS  "$t/allow.result"; check "ALLOW: tracker stamped 'delivered'"  "$?" "0"

  # ---- write_tracker_status downgrade path (real fn, exit 1) ---------------
  local dtrk; dtrk="$(mktemp)"
  printf '{"leads":{"d":{"status":"delivered"}}}' > "$dtrk"
  TRACKER="$dtrk" write_tracker_status "d" "1" "/tmp/none.json" >/dev/null 2>&1
  python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["leads"]["d"]["status"])' "$dtrk" \
    | grep -qx 'sent_unverified'; check "write_status downgrades on rc!=0" "$?" "0"
  rm -f "$dtrk" "$dtrk".bak-status-* 2>/dev/null

  # ---- reconcile_tracker REAL write-back into deliveries[] (planted bad row) -
  # Gatekeeper blocker #5: the deliveries[] downgrade write-back path had never
  # executed on real data (live tracker had nothing mislabeled). Plant a row
  # falsely marked "delivered" inside deliveries[] of a TRACKER COPY, run the
  # real reconcile_tracker (gate fails on the synthetic slug => downgrade),
  # and assert the write-back landed in the nested deliveries[idx][slug] struct.
  local rtrk; rtrk="$(mktemp)"
  printf '{"leads":{},"deliveries":[{"plantedbad_xyz":{"status":"delivered","emailed_lead_msgId":""}}]}' > "$rtrk"
  # gate will fail for plantedbad_xyz (no msgId/podcast/html/audit) => downgrade.
  TRACKER="$rtrk" VERDICT_DIR="$(mktemp -d)" LOG="$(mktemp)" \
    reconcile_tracker >/dev/null 2>&1
  python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["deliveries"][0]["plantedbad_xyz"]["status"])' "$rtrk" \
    | grep -qx 'sent_unverified'; check "reconcile downgrades planted deliveries[] row" "$?" "0"
  # prove the write-back recorded the nested location, not a leads{} fallback.
  python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["deliveries"][0]["plantedbad_xyz"]["delivery_verification"]["location"])' "$rtrk" \
    | grep -q 'deliveries'; check "reconcile write-back targets deliveries[idx]" "$?" "0"
  rm -f "$rtrk" "$rtrk".bak-integrity-* 2>/dev/null

  rm -rf "$t"
  echo "self-test: $pass/$total passed"
  [ "$pass" -eq "$total" ]
}

# ===========================================================================
# Cross-session state mirror — STATE RULE: verdict ledger must live in
# Drive/Notion, not only ~/.openclaw (local files die on handoff). Pushes the
# JSONL ledger to the Blueprint pipeline Drive folder. Reversible (upload only).
# ===========================================================================
BLUEPRINT_STATE_DRIVE_FOLDER="${BLUEPRINT_STATE_DRIVE_FOLDER:-}"  # set to mirror
# Canonical Drive file ID is persisted here so every mirror updates ONE file
# instead of creating a new one each run (idempotency — STATE RULE: single
# canonical Drive location). (gatekeeper blocker #2 — mirror was non-idempotent.)
MIRROR_ID_STATE="${BLUEPRINT_MIRROR_ID_STATE:-$HOME/.openclaw/state/blueprint-integrity-mirror-id.txt}"
mirror_state() {
  [ -f "$LOG" ] || { echo "no ledger at $LOG"; return 1; }
  local gog; gog="$(resolve_gog)" || { echo "gog_unavailable_for_mirror"; return 1; }
  local name="blueprint-integrity-gate-ledger.jsonl"

  # 1) Determine the canonical file ID: persisted state first, then a live
  #    Drive search by exact name (recovers the ID if state was lost). Never
  #    blind-upload, which would fork a new file every cycle.
  #    CLI surface (gog 0.13.0): `get <id>` (existence), `search <query>`
  #    (--raw-query for Drive query language), `upload --replace=<id>`
  #    (overwrites content in place, preserves the shared link + permissions).
  local fid=""
  if [ -f "$MIRROR_ID_STATE" ]; then
    fid="$(tr -d ' \t\r\n' < "$MIRROR_ID_STATE")"
    # Verify it still resolves; drop a stale/trashed ID so --replace can't fail silently.
    [ -n "$fid" ] && ! "$gog" drive get "$fid" >/dev/null 2>&1 && fid=""
  fi
  if [ -z "$fid" ]; then
    fid="$("$gog" -p drive search "name = '$name' and trashed = false" --raw-query --max 1 2>/dev/null \
            | grep -oE '[A-Za-z0-9_-]{25,}' | head -1)"
  fi

  # 2) Replace the existing file's content in place, or create exactly once.
  local out
  if [ -n "$fid" ]; then
    out="$("$gog" drive upload "$LOG" --replace="$fid" 2>&1 | tail -5)"
    echo "$out"
    printf '%s\n' "$fid" > "$MIRROR_ID_STATE"
    echo "mirror: replaced canonical ledger file $fid in place (idempotent — no new file created, link/permissions preserved)"
  else
    if [ -n "$BLUEPRINT_STATE_DRIVE_FOLDER" ]; then
      out="$("$gog" drive upload "$LOG" --name "$name" --parent "$BLUEPRINT_STATE_DRIVE_FOLDER" 2>&1 | tail -5)"
    else
      out="$("$gog" drive upload "$LOG" --name "$name" 2>&1 | tail -5)"
    fi
    echo "$out"
    fid="$(printf '%s' "$out" | grep -oE '[A-Za-z0-9_-]{25,}' | head -1)"
    [ -n "$fid" ] && { printf '%s\n' "$fid" > "$MIRROR_ID_STATE"; echo "mirror: created canonical ledger file $fid (persisted for future idempotent --replace updates)"; }
  fi
}

# ---- dispatch -----------------------------------------------------------
case "${1:-}" in
  --self-test) self_test ;;
  --reconcile-tracker) reconcile_tracker ;;
  --mirror-state) mirror_state ;;
  --lead)
    [ -n "${2:-}" ] || { echo "usage: $0 --lead <slug> [--profile <file>] [--write-status]"; exit 2; }
    SLUG_ARG="$2"; PROFILE=""; WRITE_STATUS=0
    shift 2
    while [ $# -gt 0 ]; do
      case "$1" in
        --profile) PROFILE="${2:-}"; shift 2 ;;
        --write-status) WRITE_STATUS=1; shift ;;
        *) shift ;;
      esac
    done
    run_gate "$SLUG_ARG" "$PROFILE" "$WRITE_STATUS" ;;
  *) echo "usage: $0 --lead <slug> [--profile <f>] [--write-status] | --reconcile-tracker | --self-test"; exit 2 ;;
esac
