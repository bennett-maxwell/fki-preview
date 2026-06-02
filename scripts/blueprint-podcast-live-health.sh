#!/bin/bash
# blueprint-podcast-live-health.sh
# ------------------------------------------------------------------
# ADDITIVE, READ-ONLY live delivery-reachability check for Blueprint
# podcast URLs. Closes the wave152 finding: the prior nightly check
# only ever ran in dry-run/fixture mode and never wrote a durable
# live-health receipt against the ACTUAL delivered podcast URLs.
#
# What this does (READ-ONLY, NO external sends, NO API writes):
#   1. Pulls delivered podcast URLs from the Notion Blueprint DB IF a
#      NOTION_TOKEN + BLUEPRINT_DB_ID are present in the environment.
#      (Notion REST query is a READ — POST /databases/{id}/query is a
#       read operation; it does not mutate Notion.)
#   2. ALWAYS merges the canonical local source of record
#      (fki-preview/leads/*.json -> podcast_url), which is what the
#      Blueprint pipeline itself writes.
#   3. For each unique URL: curl -s -o /dev/null -w "%{http_code}"
#      (HEAD by default), records the HTTP status.
#   4. Writes a receipt to:
#        ~/.openclaw/state/blueprint-podcast-live-health.json
#   5. Exits non-zero if ANY url != 200. Slack alert ONLY fires with
#      the explicit --alert flag (default = NO SEND, fully read-only).
#
# Reversible: delete this script + its LaunchAgent to fully remove.
# Touches NO GHL, NO Notion writes, NO sends by default.
# ------------------------------------------------------------------

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LEADS_DIR="${SCRIPT_DIR%/scripts}/leads"
RECEIPT="$HOME/.openclaw/state/blueprint-podcast-live-health.json"
ALERT=0
METHOD="HEAD"   # HEAD by default; falls back to GET on a 405

while [ "$#" -gt 0 ]; do
    case "$1" in
        --alert)        ALERT=1; shift ;;
        --get)          METHOD="GET"; shift ;;
        --leads-dir)    LEADS_DIR="${2:?--leads-dir requires a path}"; shift 2 ;;
        --receipt)      RECEIPT="${2:?--receipt requires a path}"; shift 2 ;;
        *) echo "ERROR: unknown arg: $1" >&2; exit 2 ;;
    esac
done

mkdir -p "$(dirname "$RECEIPT")"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TMP_URLS="$(mktemp)"
trap 'rm -f "$TMP_URLS"' EXIT

NOTION_SOURCE="unavailable"
# ---- Optional Notion Blueprint DB read (graceful, no-credential-gate) ----
if [ -n "${NOTION_TOKEN:-}" ] && [ -n "${BLUEPRINT_DB_ID:-}" ]; then
    if curl -s -X POST \
        "https://api.notion.com/v1/databases/${BLUEPRINT_DB_ID}/query" \
        -H "Authorization: Bearer ${NOTION_TOKEN}" \
        -H "Notion-Version: 2022-06-28" \
        -H "Content-Type: application/json" \
        -H "User-Agent: fki-blueprint-podcast-live-health/1.0" \
        --max-time 20 -d '{"page_size":100}' 2>/dev/null \
      | python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
except Exception:
    sys.exit(0)
for r in d.get("results",[]):
    props=r.get("properties",{})
    for key in ("Podcast URL","podcast_url","Podcast","Podcast Link"):
        p=props.get(key)
        if not p: continue
        url=""
        if p.get("type")=="url": url=p.get("url") or ""
        elif p.get("type")=="rich_text":
            url="".join(t.get("plain_text","") for t in p.get("rich_text",[]))
        if url.strip().startswith("http"):
            print("notion\t"+url.strip())
' >>"$TMP_URLS" 2>/dev/null; then
        NOTION_SOURCE="queried"
    else
        NOTION_SOURCE="query_failed"
    fi
fi

# ---- Canonical local source of record (always) ----
if [ -d "$LEADS_DIR" ]; then
    for f in "$LEADS_DIR"/*.json; do
        [ -f "$f" ] || continue
        slug="$(basename "$f" .json)"
        url="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('podcast_url','') or '')" "$f" 2>/dev/null)"
        case "$url" in
            http*) printf 'leads:%s\t%s\n' "$slug" "$url" >>"$TMP_URLS" ;;
        esac
    done
fi

# ---- Health check each UNIQUE url (read-only) ----
RESULTS_JSON="$(
python3 - "$TMP_URLS" "$METHOD" <<'PYEOF'
import json,subprocess,sys
src=sys.argv[1]; method=sys.argv[2]
seen={}
order=[]
with open(src) as fh:
    for raw in fh:
        raw=raw.rstrip("\n")
        if not raw: continue
        if "\t" not in raw: continue
        origin,url=raw.split("\t",1)
        if url not in seen:
            seen[url]=[origin]; order.append(url)
        else:
            seen[url].append(origin)

def http_code(url, m):
    flag = "-I" if m=="HEAD" else ""
    cmd=["curl","-s","-o","/dev/null","-w","%{http_code}","--max-time","12",
         "-A","fki-blueprint-podcast-live-health/1.0"]
    if m=="HEAD": cmd.append("-I")
    cmd.append(url)
    try:
        out=subprocess.run(cmd,capture_output=True,text=True,timeout=20).stdout.strip()
        return out or "000"
    except Exception:
        return "000"

results=[]
for url in order:
    code=http_code(url, method)
    # Some static hosts reject HEAD with 403/405 -> retry GET to avoid false alert
    if method=="HEAD" and code in ("403","405","000"):
        code2=http_code(url,"GET")
        if code2 not in ("000",): code=code2
    results.append({"url":url,"origins":sorted(set(seen[url])),"http":code,"ok":code=="200"})

print(json.dumps(results))
PYEOF
)"

TOTAL="$(echo "$RESULTS_JSON" | python3 -c 'import json,sys;print(len(json.load(sys.stdin)))')"
FAILS_JSON="$(echo "$RESULTS_JSON" | python3 -c 'import json,sys;print(json.dumps([r for r in json.load(sys.stdin) if not r["ok"]]))')"
FAIL_COUNT="$(echo "$FAILS_JSON" | python3 -c 'import json,sys;print(len(json.load(sys.stdin)))')"

# ---- Write durable receipt (the first real delivery-reachability signal) ----
python3 - "$RECEIPT" "$TS" "$TOTAL" "$FAIL_COUNT" "$NOTION_SOURCE" "$RESULTS_JSON" "$FAILS_JSON" <<'PYEOF'
import json,sys
receipt,ts,total,fails,notion_src,results_json,failures_json=sys.argv[1:8]
doc={
  "artifact_type":"blueprint_podcast_live_health_receipt",
  "generated_at_utc":ts,
  "mode":"read-only/live-http-head/no-sends/no-api-writes",
  "notion_source":notion_src,
  "checked_count":int(total),
  "failure_count":int(fails),
  "all_healthy":int(fails)==0,
  "verdict":"ALL_PODCAST_URLS_REACHABLE" if int(fails)==0 else "REACHABILITY_FAILURE",
  "results":json.loads(results_json),
  "failures":json.loads(failures_json),
}
with open(receipt,"w") as fh:
    json.dump(doc,fh,indent=2,sort_keys=True)
print(receipt)
PYEOF

echo "RECEIPT: $RECEIPT  (checked=$TOTAL, failures=$FAIL_COUNT, notion=$NOTION_SOURCE)"

if [ "${FAIL_COUNT:-0}" -gt 0 ]; then
    MSG="⚠️ Blueprint podcast LIVE health: $FAIL_COUNT/$TOTAL unreachable — $(echo "$FAILS_JSON" | python3 -c 'import json,sys;print(", ".join(r["url"]+":"+r["http"] for r in json.load(sys.stdin)))')"
    if [ "$ALERT" -eq 1 ]; then
        ~/bin/slack-post.sh "#leo-auto" "$MSG" 2>/dev/null || true
    else
        echo "NO_SEND (use --alert to enable): $MSG"
    fi
    exit 1
fi

echo "All $TOTAL delivered podcast URLs reachable (200) at $TS"
exit 0
