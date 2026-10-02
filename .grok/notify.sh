#!/usr/bin/env bash
input="$(cat)"
fields=()
while IFS= read -r field; do
  fields+=("$field")
done < <(printf '%s' "$input" | jq -r '
  def text: if type == "string" then gsub("[\u0000-\u001f\u007f]"; " ") else "" end;
  select(type == "object") |
  select((.hookEventName // .hook_event_name) == "notification" or
         (.hookEventName // .hook_event_name) == "Notification") |
  select([.subagentType, .subagent_type, .subagentId, .subagent_id] | all(. == null or . == "")) |
  [ (if .notificationType == "idle_prompt" then "Grok: Ready for input"
     elif .notificationType == "permission_prompt" then "Grok: Approval needed"
     else empty end),
    (((.cwd | text | select(. != "")) // (.workspaceRoot | text)) |
     split("/") | map(select(. != "")) | last // "")
  ] | select(length == 2) | .[]' 2>/dev/null)
[[ -n "${fields[0]}" ]] || exit 0

case "$(uname -s 2>/dev/null)" in
  Linux)
    if command -v notify-send >/dev/null 2>&1; then
      notify-send -- "${fields[0]}" "${fields[1]}" >/dev/null 2>&1 && exit 0
    fi
    ;;
  Darwin)
    if command -v osascript >/dev/null 2>&1; then
      # Pass text as arguments, not as AppleScript source.
      osascript - "${fields[0]}" "${fields[1]}" >/dev/null 2>&1 <<'APPLESCRIPT' && exit 0
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
APPLESCRIPT
    fi
    ;;
esac
{ printf '\a' > /dev/tty; } 2>/dev/null
exit 0
