#!/usr/bin/env bash
input="$(cat)"
fields=()
# One sanitized field per line keeps absent fields in their original positions.
while IFS= read -r field; do
  fields+=("$field")
done < <(printf '%s' "$input" | jq -r '
  def text: if type == "string" then gsub("[\u0000-\u001f\u007f]"; " ") else "" end;
  def name: text | split("/") | map(select(. != "")) | last // "";
  select(type == "object") |
  [ ((.model.display_name? // null | text | select(. != "")) // (.model.id? // null | text)),
    (.effort.level? // null | text),
    (((.workspace.current_dir? // null | text | select(. != "")) // (.cwd? | text)) | name),
    (.workspace.branch? // null | text),
    (.context_window.used_percentage? // null | if type == "number" and . >= 0 and . <= 100 then . else "" end),
    (.cost.total_cost_usd? // null | if type == "number" and . > 0 then . else "" end)
  ] | .[]' 2>/dev/null)

segments=()
for index in 0 1 2 3; do
  [[ -z "${fields[$index]}" ]] || segments+=("${fields[$index]}")
done
[[ -z "${fields[4]}" ]] || segments+=("$(awk -v p="${fields[4]}" 'BEGIN { printf "%.0f%% ctx", p }')")
[[ -z "${fields[5]}" ]] || segments+=("$(awk -v c="${fields[5]}" 'BEGIN { if (c < 0.0005) printf "$<0.001"; else printf "$%.3f", c }')")

out=""
for segment in "${segments[@]}"; do
  [[ -z "$out" ]] || out+=" · "
  out+="$segment"
done
printf '%s' "$out"
