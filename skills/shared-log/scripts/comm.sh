#!/bin/sh
# Helper for the shared-log skill. See ../SKILL.md.
#
#   comm.sh join "<what you're working on>"   prints your joined line; your ID is field 3
#   comm.sh say <id> "<statement>"
#   comm.sh read [after]
set -eu

# Use the log of the project in the current directory. In a git repository
# that's the main checkout's log, so agents in worktrees share it.
if common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null); then
  dir="$(dirname "$common")/.agents/communication"
else
  dir="$PWD/.agents/communication"
fi
log="${AGENT_COMM_LOG:-$dir/statements.log}"
lock="$log.lock"

usage() {
  sed -n '4,6s/^#   //p' "$0" >&2
  exit 2
}

append() {
  mkdir -p "$(dirname "$log")"
  tries=0
  until mkdir "$lock" 2>/dev/null; do
    tries=$((tries + 1))
    if [ "$tries" -ge 100 ]; then
      echo "comm.sh: $lock has been held for 10s. If no agent is writing, ask the user to remove it." >&2
      exit 1
    fi
    sleep 0.1
  done
  trap 'rmdir "$lock"' EXIT
  last=$(tail -n 1 "$log" 2>/dev/null | cut -d' ' -f1)
  line="$((${last:-0} + 1)) $(date -u +%Y-%m-%dT%H:%M:%SZ) $1 $(printf '%s' "$2" | tr '\n' ' ')"
  printf '%s\n' "$line" >>"$log"
  rmdir "$lock"
  trap - EXIT
  printf '%s\n' "$line"
}

case "${1:-}" in
  join)
    [ $# -eq 2 ] || usage
    append "$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')" "joined: $2"
    ;;
  say)
    [ $# -eq 3 ] || usage
    if ! grep -q "^[0-9]* [^ ]* $2 joined:" "$log" 2>/dev/null; then
      echo "comm.sh: $2 has not joined" >&2
      exit 1
    fi
    append "$2" "$3"
    ;;
  read)
    [ $# -le 2 ] || usage
    if [ -f "$log" ]; then
      awk -v after="${2:-0}" '$1 > after' "$log"
    fi
    ;;
  *)
    usage
    ;;
esac
