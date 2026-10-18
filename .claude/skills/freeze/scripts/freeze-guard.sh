#!/bin/bash
# usage: freeze-guard.sh arm <dir> | disarm | status | write <path>... | hook  (exit 0 allow, 2 block, 64 usage)
set -u

STATE_ROOT="${FREEZE_STATE_DIR:-$HOME/.agents/state/freeze}"
ROOT=""
GROK=0
REASON=""

usage() {
  printf 'usage: freeze-guard.sh arm <dir> | disarm | status | write <path>... | hook\n' >&2
  exit 64
}

state_key() {
  printf '%s' "$1" | sed 's|/|%|g'
}

state_file() {
  printf '%s/%s\n' "$STATE_ROOT" "$(state_key "$1")"
}

physical() {
  _p="$1"
  case "$_p" in
    /*) ;;
    *) _p="$(pwd -P)/$_p" ;;
  esac
  while [ "$_p" != "/" ] && [ "${_p%/}" != "$_p" ]; do
    _p="${_p%/}"
  done
  _rest=""
  _cur="$_p"
  while [ "$_cur" != "/" ] && [ ! -e "$_cur" ]; do
    _base="${_cur##*/}"
    _rest="/$_base$_rest"
    _cur="${_cur%/*}"
    [ -z "$_cur" ] && _cur="/"
  done
  if [ -d "$_cur" ]; then
    _real=$(cd -P "$_cur" 2>/dev/null && pwd -P)
  else
    _dir="${_cur%/*}"
    [ -z "$_dir" ] && _dir="/"
    _real="$(physical "$_dir")/${_cur##*/}"
  fi
  [ -n "$_real" ] || _real="$_cur"
  printf '%s%s\n' "$_real" "$_rest"
}

key_for_cwd() {
  _c="$1"
  if [ -n "$_c" ]; then
    _pc=$(cd -P "$_c" 2>/dev/null && pwd -P)
    [ -n "$_pc" ] && { printf '%s\n' "$_pc"; return; }
  fi
  pwd -P
}

load_root() {
  _f=$(state_file "$1")
  [ -r "$_f" ] || return 1
  _c=$(cat "$_f" 2>/dev/null)
  [ -n "$_c" ] || return 1
  printf '%s\n' "$_c"
}

frozen_target() {
  _t=$(physical "$1")
  case "$_t" in
    "$ROOT"/*) return 0 ;;
  esac
  REASON="freeze: '$1' resolves to '$_t', outside the frozen dir '$ROOT'"
  return 1
}

emit() {
  _t="$1"
  [ -n "$_t" ] || return 0
  case "$_t" in
    \&*) return 0 ;;
    /dev/*) return 0 ;;
    *[!0-9]*) ;;
    *) return 0 ;;
  esac
  printf '%s\n' "$_t"
}

command_writes() {
  _cmd="$1"
  printf '%s\n' "$_cmd" | awk '
    /^[*][*][*] (Add|Update|Delete) File: / {
      sub(/^[*][*][*] (Add|Update|Delete) File: /, "")
      sub(/[[:space:]]+$/, "")
      if (length($0) > 0) print
    }
  '
  _norm=$(printf '%s' "$_cmd" | awk '{gsub(/&>>|&>|2>>|2>|>>|>/, " & "); gsub(/\|/, " | "); print}')
  set -f
  # shellcheck disable=SC2086
  set -- $_norm
  set +f
  _tee=0
  _sed=0
  _sed_i=0
  _sed_script=0
  while [ $# -gt 0 ]; do
    _tok="$1"
    shift
    case "$_tok" in
      '>'|'>>'|'2>'|'2>>'|'&>'|'&>>')
        [ $# -gt 0 ] || break
        emit "$1"
        shift
        continue
        ;;
      '|'|';')
        _tee=0
        _sed=0
        continue
        ;;
      'sed')
        _sed=1
        _sed_i=0
        _sed_script=0
        continue
        ;;
      'tee')
        _tee=1
        continue
        ;;
    esac
    if [ "$_tee" = 1 ]; then
      case "$_tok" in
        -*) ;;
        *) emit "$_tok" ;;
      esac
      continue
    fi
    if [ "$_sed" = 1 ]; then
      case "$_tok" in
        -i|-i*) _sed_i=1; continue ;;
        -*) continue ;;
      esac
      if [ "$_sed_i" = 1 ]; then
        if [ "$_sed_script" = 0 ]; then
          _sed_script=1
        else
          emit "$_tok"
        fi
      fi
    fi
  done
}

block() {
  if [ "$GROK" = 1 ]; then
    jq -n --arg r "$REASON" '{decision:"deny",reason:$r}'
  fi
  printf '%s\n' "$REASON" >&2
  exit 2
}

json_str() {
  jq -r "$1" 2>/dev/null
}

cmd="${1:-}"
case "$cmd" in
  arm)
    [ $# -eq 2 ] || usage
    _dir=$(physical "$2")
    case "$_dir" in
      /*) ;;
      *) printf 'freeze: cannot resolve %s\n' "$2" >&2; exit 64 ;;
    esac
    mkdir -p "$STATE_ROOT" || exit 1
    printf '%s\n' "$_dir" >"$(state_file "$(pwd -P)")"
    ;;
  disarm)
    [ $# -eq 1 ] || usage
    rm -f "$(state_file "$(pwd -P)")"
    ;;
  status)
    [ $# -eq 1 ] || usage
    _r=$(load_root "$(pwd -P)") || exit 0
    printf '%s\n' "$_r"
    ;;
  write)
    [ $# -ge 2 ] || usage
    ROOT=$(load_root "$(pwd -P)") || exit 0
    shift
    for _p in "$@"; do
      frozen_target "$_p" || block
    done
    ;;
  hook)
    [ $# -eq 1 ] || usage
    PAYLOAD=$(cat)
    command -v jq >/dev/null 2>&1 || {
      printf 'freeze: jq not found, hook checks skipped\n' >&2
      exit 0
    }
    jq -e 'has("toolName") or has("hookEventName")' >/dev/null 2>&1 <<EOF && GROK=1
$PAYLOAD
EOF
    _cwd=$(json_str '(.cwd? // empty) | select(type=="string")' <<EOF
$PAYLOAD
EOF
)
    _sf=$(state_file "$(key_for_cwd "$_cwd")")
    if [ -r "$_sf" ] && [ -s "$_sf" ]; then
      ROOT=$(load_root "$(key_for_cwd "$_cwd")") || exit 0
    else
      exit 0
    fi
    _tool=$(json_str '(.tool_name? // .toolName? // empty) | select(type=="string")' <<EOF
$PAYLOAD
EOF
)
    case "$(printf '%s' "$_tool" | tr 'A-Z' 'a-z')" in
      read|read_file|readfile|grep|glob|list_dir|listdir|ls|web_search|websearch|webfetch|web_fetch)
        exit 0
        ;;
    esac
    _targets=$(json_str '[(.tool_input.file_path? // empty),(.toolInput.file_path? // empty),(.tool_input.path? // empty),(.toolInput.path? // empty),(.tool_input.file? // empty),(.toolInput.file? // empty),(.tool_input.paths[]? // empty),(.toolInput.paths[]? // empty)] | .[]' <<EOF
$PAYLOAD
EOF
)
    while IFS= read -r _t; do
      [ -n "$_t" ] || continue
      frozen_target "$_t" || block
    done <<EOF
$_targets
EOF
    _command=$(json_str '(.tool_input.command? // .toolInput.command? // empty) | select(type=="string")' <<EOF
$PAYLOAD
EOF
)
    if [ -n "$_command" ]; then
      while IFS= read -r _t; do
        [ -n "$_t" ] || continue
        frozen_target "$_t" || block
      done <<EOF
$(command_writes "$_command")
EOF
    fi
    ;;
  *)
    usage
    ;;
esac

exit 0
