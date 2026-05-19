#!/usr/bin/env bash
set -euo pipefail
# batch-pre-delivery.sh — Run pre-delivery checks on all Blueprints in blueprints/ dir
# Usage: ./batch-pre-delivery.sh [--leads "Name One,Name Two"] [--dir path/to/blueprints]
# Output: Summary table to stdout; full JSON in /tmp/blueprint-check-results/
# Compatible with bash 3.2+ (macOS default)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER="$SCRIPT_DIR/pre-delivery-check.sh"

# ── Defaults ──────────────────────────────────────────────────────────────────
BLUEPRINTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/blueprints"
LEADS_ARG=""
OUTPUT_DIR="/tmp/blueprint-check-results"

# ── Parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --leads)
      LEADS_ARG="$2"
      shift 2
      ;;
    --dir)
      BLUEPRINTS_DIR="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--leads \"Name One,Name Two\"] [--dir path/to/blueprints]"
      echo ""
      echo "Runs pre-delivery-check.sh on every .html file in the blueprints/ directory."
      echo "Outputs a summary table to stdout and full JSON per file to $OUTPUT_DIR/."
      exit 0
      ;;
    *)
      shift
      ;;
  esac
done

# ── Validate prerequisites ────────────────────────────────────────────────────
if [[ ! -f "$CHECKER" ]]; then
  echo "ERROR: pre-delivery-check.sh not found at $CHECKER"
  exit 1
fi

if [[ ! -d "$BLUEPRINTS_DIR" ]]; then
  echo "ERROR: Blueprints directory not found: $BLUEPRINTS_DIR"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# ── Discover HTML files (bash 3.2 compatible — no mapfile) ────────────────────
HTML_FILES=()
while IFS= read -r f; do
  HTML_FILES+=("$f")
done < <(find "$BLUEPRINTS_DIR" -maxdepth 1 -name "*.html" | sort)

if [[ ${#HTML_FILES[@]} -eq 0 ]]; then
  echo "No HTML files found in $BLUEPRINTS_DIR"
  exit 0
fi

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
TOTAL=${#HTML_FILES[@]}
PASS_COUNT=0
FAIL_COUNT=0

# Column widths
COL_FILE=32
COL_CHECK=5

# ── Table header ─────────────────────────────────────────────────────────────
echo ""
echo "Blueprint AI v2.0 — Pre-Delivery Batch Check"
echo "Run at: $TIMESTAMP"
echo "Directory: $BLUEPRINTS_DIR"
echo ""

# Abbreviated column headers matching check order
printf "%-${COL_FILE}s  " "FILE"
for h in "book" "disc" "90dy" "emoj" "aply" "cad3" "cal" "xcon" "urls" "size"; do
  printf "%-${COL_CHECK}s " "$h"
done
printf "%s\n" "RESULT"

# Separator line
sep_file=$(printf '%*s' "$COL_FILE" '' | tr ' ' '-')
sep_check=$(printf '%*s' "$COL_CHECK" '' | tr ' ' '-')
printf "%s  " "$sep_file"
for i in 1 2 3 4 5 6 7 8 9 10; do
  printf "%s " "$sep_check"
done
printf "%s\n" "--------"

# ── Tracking arrays (bash 3.2: use parallel indexed arrays instead of assoc) ──
FAIL_KEYS=()
FAIL_MSGS=()

# ── Process each file ─────────────────────────────────────────────────────────
for html_file in "${HTML_FILES[@]}"; do
  basename_file="$(basename "$html_file" .html)"
  short_name="${basename_file:0:$COL_FILE}"

  # Build checker args
  checker_args=("$html_file")
  if [[ -n "$LEADS_ARG" ]]; then
    checker_args+=("--leads" "$LEADS_ARG")
  fi

  # Run check, capture JSON (never fail the batch on individual errors)
  json_out=$("$CHECKER" "${checker_args[@]}" 2>/dev/null || printf '{"error":"checker_failed","overall":"FAIL","failures":["checker script error"],"checks":{}}')

  # Save full JSON
  echo "$json_out" > "$OUTPUT_DIR/${basename_file}.json"

  # Parse pass/fail per check using python3 — reliable JSON parsing
  check_results=$(python3 - "$json_out" <<'PYEOF'
import sys, json

try:
    data = json.loads(sys.argv[1])
    checks = data.get("checks", {})
    order = [
        "booking_urls", "discovery_call", "90day_timeline", "emojis",
        "apply_cta", "cadence_3730", "calendar_links", "cross_contamination",
        "all_urls_200", "file_size"
    ]
    results = []
    for key in order:
        c = checks.get(key, {})
        passed = c.get("pass", False)
        results.append("PASS" if passed else "FAIL")
    overall = data.get("overall", "FAIL")
    results.append(overall)
    failures = data.get("failures", [])
    # Print results on line 1, failures on line 2 (pipe-separated)
    print(" ".join(results))
    print("|".join(failures))
except Exception as e:
    print("FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL")
    print(str(e))
PYEOF
  )

  # Split into results line and failures line
  results_line=$(echo "$check_results" | head -1)
  failures_line=$(echo "$check_results" | tail -1)

  # Parse results array (indices 0-9 = checks, 10 = overall)
  read -ra results_arr <<< "$results_line"
  overall="${results_arr[10]:-FAIL}"

  if [[ "$overall" == "PASS" ]]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    verdict_display="PASS"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    verdict_display="FAIL"
    FAIL_KEYS+=("$basename_file")
    FAIL_MSGS+=("$failures_line")
  fi

  # Print row
  printf "%-${COL_FILE}s  " "$short_name"
  for i in 0 1 2 3 4 5 6 7 8 9; do
    cell="${results_arr[$i]:-FAIL}"
    printf "%-${COL_CHECK}s " "$cell"
  done
  printf "%s\n" "$verdict_display"

done

# ── Footer ────────────────────────────────────────────────────────────────────
echo ""
sep_file=$(printf '%*s' "$COL_FILE" '' | tr ' ' '-')
sep_check=$(printf '%*s' "$COL_CHECK" '' | tr ' ' '-')
printf "%s  " "$sep_file"
for i in 1 2 3 4 5 6 7 8 9 10; do
  printf "%s " "$sep_check"
done
printf "%s\n" "--------"

echo ""
echo "SUMMARY: $TOTAL files checked — $PASS_COUNT PASS / $FAIL_COUNT FAIL"
echo ""

# ── Failure detail section ────────────────────────────────────────────────────
if [[ ${#FAIL_KEYS[@]} -gt 0 ]]; then
  echo "FAILURES:"
  for i in "${!FAIL_KEYS[@]}"; do
    echo "  ${FAIL_KEYS[$i]}:"
    # Replace pipe separators with newline+indent for readability
    printf '%s\n' "${FAIL_MSGS[$i]}" | tr '|' '\n' | while IFS= read -r line; do
      [[ -n "$line" ]] && echo "    - $line"
    done
  done
  echo ""
fi

echo "Full JSON results: $OUTPUT_DIR/"
echo ""

# ── Aggregate JSON summary ────────────────────────────────────────────────────
python3 - "$OUTPUT_DIR" "$TOTAL" "$PASS_COUNT" "$FAIL_COUNT" "$TIMESTAMP" <<'PYEOF'
import sys, json, os, glob

results_dir, total, passed, failed, ts = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]

files_results = []
for jf in sorted(glob.glob(os.path.join(results_dir, "*.json"))):
    if os.path.basename(jf).startswith("_"):
        continue
    try:
        with open(jf) as f:
            files_results.append(json.load(f))
    except Exception:
        pass

summary = {
    "batch_timestamp": ts,
    "total": total,
    "pass": passed,
    "fail": failed,
    "pass_rate": f"{round(passed/total*100, 1)}%" if total > 0 else "0%",
    "files": files_results
}

out_path = os.path.join(results_dir, "_batch-summary.json")
with open(out_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"Aggregate JSON: {out_path}")
PYEOF

# Exit 1 if any failures
[[ "$FAIL_COUNT" -gt 0 ]] && exit 1
exit 0
