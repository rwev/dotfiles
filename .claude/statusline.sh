#!/usr/bin/env bash
# =============================================================================
# Claude Code status line
# Reads the session JSON from stdin and prints a one-line footer:
#   <model> · <dir> · <git branch> · $<session cost> · +<added>/-<removed>
# Dependency-light: uses jq if present, else python3, else degrades gracefully.
# =============================================================================
input="$(cat)"

model="" dir="" cost="" added="" removed="" limit_pct="" limit_resets="" ctx_pct=""

if command -v jq &>/dev/null; then
  IFS=$'\t' read -r model dir cost added removed limit_pct limit_resets ctx_pct <<<"$(
    printf '%s' "$input" | jq -r '
      [ (.model.display_name // ""),
        (.workspace.current_dir // .cwd // ""),
        (.cost.total_cost_usd // 0),
        (.cost.total_lines_added // 0),
        (.cost.total_lines_removed // 0),
        (.rate_limits.five_hour.used_percentage // ""),
        (.rate_limits.five_hour.resets_at // ""),
        (.context_window.used_percentage // "")
      ] | @tsv' 2>/dev/null
  )"
elif command -v python3 &>/dev/null; then
  IFS=$'\t' read -r model dir cost added removed limit_pct limit_resets ctx_pct <<<"$(
    printf '%s' "$input" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
m = (d.get("model") or {}).get("display_name", "")
ws = d.get("workspace") or {}
cwd = ws.get("current_dir") or d.get("cwd") or ""
c = d.get("cost") or {}
fh = ((d.get("rate_limits") or {}).get("five_hour") or {})
cw = d.get("context_window") or {}
print("\t".join(str(x) for x in (
    m, cwd, c.get("total_cost_usd", 0),
    c.get("total_lines_added", 0), c.get("total_lines_removed", 0),
    fh.get("used_percentage", ""), fh.get("resets_at", ""),
    cw.get("used_percentage", ""),
)))
' 2>/dev/null
  )"
fi

# Fallbacks when no parser is available or fields are missing.
[[ -z "$dir" ]] && dir="$PWD"
added="${added:-0}" removed="${removed:-0}"

dir_name="$(basename "${dir/#$HOME/\~}")"

branch=""
if git -C "$dir" rev-parse --is-inside-work-tree &>/dev/null; then
  branch="$(git -C "$dir" branch --show-current 2>/dev/null)"
fi

# Format cost only when it's a positive number.
cost_fmt="$(awk -v c="$cost" 'BEGIN { if (c+0 > 0) printf "$%.3f", c }')"

lines_fmt=""
[[ "$added" != "0" || "$removed" != "0" ]] && lines_fmt="+${added}/-${removed}"

# 5-hour session rate limit (absent for API-key/non-plan sessions).
limit_fmt=""
[[ -n "$limit_pct" ]] && limit_fmt="$(awk -v p="$limit_pct" 'BEGIN { printf "%.0f%% session", p }')"

ctx_fmt=""
[[ -n "$ctx_pct" ]] && ctx_fmt="$(awk -v p="$ctx_pct" 'BEGIN { printf "%.0f%% ctx", p }')"

resets_fmt=""
if [[ -n "$limit_resets" ]]; then
  resets_fmt="$(awk -v r="$limit_resets" -v now="$(date +%s)" '
    BEGIN {
      d = r - now
      if (d > 0) {
        h = int(d / 3600)
        m = int((d % 3600) / 60)
        if (h > 0) printf "resets %dh%dm", h, m
        else printf "resets %dm", m
      }
    }')"
fi

# Assemble, skipping empty segments.
segments=()
[[ -n "$model" ]]      && segments+=("$model")
[[ -n "$dir_name" ]]   && segments+=("$dir_name")
[[ -n "$branch" ]]     && segments+=("$branch")
[[ -n "$cost_fmt" ]]   && segments+=("$cost_fmt")
[[ -n "$lines_fmt" ]]  && segments+=("$lines_fmt")
[[ -n "$ctx_fmt" ]]    && segments+=("$ctx_fmt")
[[ -n "$limit_fmt" ]]  && segments+=("$limit_fmt")
[[ -n "$resets_fmt" ]] && segments+=("$resets_fmt")

out=""
for seg in "${segments[@]}"; do
  [[ -n "$out" ]] && out+=" · "
  out+="$seg"
done

printf '%s' "$out"
