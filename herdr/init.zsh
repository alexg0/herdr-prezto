# Loads Herdr completions everywhere, and optional reporting/helpers in a pane.
# Adapted from Robby Russell's herdr-ohmyzsh (MIT); see ../NOTICE.md.

# Prezto loads this after completion, so compdef is the intentional boundary.
if (( ! $+commands[herdr] || ! $+functions[compdef] )); then
  return 1
fi

typeset -g _herdr_prezto_bin="${HERDR_BIN_PATH:-herdr}"
typeset -g _herdr_prezto_root="${0:A:h}"

# Prefer a compinit-managed cache when configured. A missing cache gets an
# autoloadable fallback immediately; refresh is silent and backgrounded.
if [[ -n ${ZSH_CACHE_DIR-} ]]; then
  # Prezto does not manage the Oh My Zsh completion cache path for us.
  (( ${fpath[(Ie)$ZSH_CACHE_DIR/completions]} )) ||
    fpath=("$ZSH_CACHE_DIR/completions" $fpath)
  if [[ -z ${_comps[herdr]-} ]]; then
    typeset -g -A _comps
    autoload -Uz _herdr
    _comps[herdr]=_herdr
  fi
  if [[ -z ${_herdr_prezto_completion_refresh-} ]]; then
    typeset -g _herdr_prezto_completion_refresh=1
    zmodload -F zsh/files b:zf_mv b:zf_mkdir b:zf_rm
    () {
      zf_mkdir -p "$ZSH_CACHE_DIR/completions"
      local tmp="$ZSH_CACHE_DIR/completions/_herdr.$$.$RANDOM"
      if "$_herdr_prezto_bin" completion zsh >| "$tmp" 2>/dev/null && [[ -s "$tmp" ]]; then
        zf_mv -f -- "$tmp" "$ZSH_CACHE_DIR/completions/_herdr"
      else
        zf_rm -f -- "$tmp"
      fi
    } >/dev/null 2>&1 &|
  fi
elif [[ -z ${_comps[herdr]-} ]]; then
  # Without a cache directory, retain the original in-memory behavior.
  function {
    local completion
    completion="$("$_herdr_prezto_bin" completion zsh)" || return 1
    [[ -n $completion ]] || return 1
    eval "$completion"
  } || return 1
fi

# Everything below needs a live Herdr pane. Loading the module elsewhere must
# not add hooks, helpers, socket calls, or other startup behavior.
[[ "$HERDR_ENV" == 1 && -n "$HERDR_PANE_ID" ]] || return 0
[[ -n ${_herdr_prezto_pane_loaded-} ]] && return 0
typeset -g _herdr_prezto_pane_loaded=1

zmodload zsh/datetime
autoload -Uz add-zsh-hook
: ${HERDR_OMZ_THRESHOLD:=10}
: ${HERDR_OMZ_REPORT:=true}
: ${HERDR_OMZ_NOTIFY:=true}
: ${HERDR_OMZ_NOTIFY_FOCUSED:=false}
: ${HERDR_OMZ_DEFAULT_AGENT:=claude}

typeset -ga HERDR_OMZ_IGNORE
(( ${#HERDR_OMZ_IGNORE} )) || HERDR_OMZ_IGNORE=(
  pi claude codex gemini cursor devin agy cline omp mastracode opencode copilot
  kimi kiro droid amp grok hermes kilo qodercli maki
  vim vi nvim emacs nano less more man ssh mosh tmux screen zellij htop top btop
  lazygit tig fzf python python3 irb pry node psql mysql sqlite3 herdr
)
typeset -g _herdr_prezto_cmd=
typeset -g _herdr_prezto_label=
typeset -gF _herdr_prezto_start=0
typeset -gi _herdr_prezto_watcher=0
typeset -gi _herdr_prezto_registered=0

function _herdr_prezto_seq {
  REPLY=$(( EPOCHREALTIME * 1000000 ))
  REPLY=${REPLY%.*}
}

function _herdr_prezto_call {
  "$_herdr_prezto_bin" "$@" >/dev/null 2>&1
  return 0
}

function _herdr_prezto_program {
  local -a words
  local w
  words=(${(z)1})
  for w in $words; do
    case "$w" in
      *=*) continue ;;
      sudo|doas|command|builtin|exec|nohup|time|nice|env|caffeinate) continue ;;
      -*) continue ;;
      *) REPLY="${w:t}"; return 0 ;;
    esac
  done
  return 1
}

function _herdr_prezto_sanitize {
  local l="${(L)1}"
  l="${l//[^a-z0-9_-]/-}"
  [[ "$l" == [a-z]* ]] || l=shell
  REPLY="${l[1,32]}"
}

function _herdr_prezto_human {
  local -i s=$1
  if (( s < 60 )); then
    REPLY="${s}s"
  elif (( s < 3600 )); then
    REPLY="$(( s / 60 ))m $(( s % 60 ))s"
  else
    REPLY="$(( s / 3600 ))h $(( (s % 3600) / 60 ))m"
  fi
}

function _herdr_prezto_kill_watcher {
  (( _herdr_prezto_watcher )) || return 0
  kill -TERM -- -$_herdr_prezto_watcher 2>/dev/null || kill -TERM $_herdr_prezto_watcher 2>/dev/null
  _herdr_prezto_watcher=0
}

function _herdr_prezto_release {
  (( _herdr_prezto_registered )) || return 0
  local REPLY
  _herdr_prezto_seq
  _herdr_prezto_call pane release-agent "$HERDR_PANE_ID" \
    --source prezto --agent "$_herdr_prezto_label" --seq $REPLY
  _herdr_prezto_registered=0
}

function _herdr_prezto_preexec {
  local cmd="${2:-$1}"
  local REPLY
  _herdr_prezto_release
  _herdr_prezto_cmd=
  _herdr_prezto_start=0
  _herdr_prezto_program "$cmd" || return 0
  (( ${HERDR_OMZ_IGNORE[(Ie)$REPLY]} )) && return 0
  _herdr_prezto_sanitize "$REPLY"
  _herdr_prezto_label="$REPLY"
  _herdr_prezto_cmd="$cmd"
  _herdr_prezto_start=$EPOCHREALTIME
  [[ "$HERDR_OMZ_REPORT" == true ]] || return 0
  _herdr_prezto_seq
  local seq=$REPLY
  local -i cs=$(( HERDR_OMZ_THRESHOLD * 100 ))
  (
    zmodload zsh/zselect 2>/dev/null && zselect -t $cs
    "$_herdr_prezto_bin" pane report-agent "$HERDR_PANE_ID" \
      --source prezto --agent "$_herdr_prezto_label" --state working \
      --message "$cmd" --seq $seq
  ) >/dev/null 2>&1 &!
  _herdr_prezto_watcher=$!
}

function _herdr_prezto_precmd {
  local -i code=$?
  (( _herdr_prezto_start )) || return 0
  local -F elapsed=$(( EPOCHREALTIME - _herdr_prezto_start ))
  local cmd="$_herdr_prezto_cmd" label="$_herdr_prezto_label"
  local REPLY
  _herdr_prezto_cmd=
  _herdr_prezto_start=0
  _herdr_prezto_kill_watcher
  (( elapsed >= HERDR_OMZ_THRESHOLD )) || return 0
  _herdr_prezto_human ${elapsed%.*}
  local summary="exit $code, took $REPLY"
  if [[ "$HERDR_OMZ_REPORT" == true ]]; then
    _herdr_prezto_seq
    _herdr_prezto_call pane report-agent "$HERDR_PANE_ID" \
      --source prezto --agent "$label" --state idle \
      --message "$cmd ($summary)" --seq $REPLY
    _herdr_prezto_registered=1
  fi
  if [[ "$HERDR_OMZ_NOTIFY" == true ]]; then
    _herdr_prezto_focused && return 0
    local title="Finished: $cmd" sound=done
    if (( code != 0 )); then
      title="Failed: $cmd"
      sound=request
    fi
    _herdr_prezto_call notification show "${title[1,80]}" --body "$summary" --sound $sound
  fi
  return 0
}

function _herdr_prezto_focused {
  [[ "$HERDR_OMZ_NOTIFY_FOCUSED" == true ]] && return 1
  local json
  json="$("$_herdr_prezto_bin" pane current --current 2>/dev/null)" || return 1
  [[ "$json" == *'"focused":true'* ]]
}

function _herdr_prezto_zshexit {
  _herdr_prezto_kill_watcher
  _herdr_prezto_release
}

add-zsh-hook preexec _herdr_prezto_preexec
add-zsh-hook precmd _herdr_prezto_precmd
add-zsh-hook zshexit _herdr_prezto_zshexit

function _herdr_prezto_pane_id {
  [[ "$1" =~ '"pane_id":"([^"]+)"' ]] || return 1
  REPLY="$match[1]"
}

function hsplit {
  local direction=right REPLY out
  case "$1" in right|down) direction=$1; shift ;; esac
  out="$("$_herdr_prezto_bin" pane split --current --direction $direction --cwd "$PWD" --focus)" || return 1
  (( $# )) || return 0
  _herdr_prezto_pane_id "$out" || { print -u2 'hsplit: could not read the new pane id'; return 1; }
  "$_herdr_prezto_bin" pane run "$REPLY" "$@" >/dev/null
}

function htab {
  local -a args=(--cwd "$PWD" --focus)
  [[ -n "$1" ]] && args+=(--label "$1")
  "$_herdr_prezto_bin" tab create "${args[@]}" >/dev/null
}

function hagent {
  local name="$1" kind="$HERDR_OMZ_DEFAULT_AGENT" REPLY out
  local -a extra
  [[ -n "$name" ]] || { print -u2 'usage: hagent NAME [KIND] [-- AGENT_ARGS...]'; return 1; }
  shift
  if [[ -n "$1" && "$1" != -- ]]; then kind="$1"; shift; fi
  [[ "$1" == -- ]] && shift
  (( $# )) && extra=(-- "$@")
  out="$("$_herdr_prezto_bin" pane split --current --direction right --cwd "$PWD" --no-focus)" || return 1
  _herdr_prezto_pane_id "$out" || { print -u2 'hagent: could not read the new pane id'; return 1; }
  "$_herdr_prezto_bin" agent start "$name" --kind "$kind" --pane "$REPLY" "${extra[@]}" >/dev/null &&
    print "hagent: $kind started as '$name' in pane $REPLY"
}

function hworktree {
  local -a args
  [[ -n "$1" ]] || { print -u2 'usage: hworktree BRANCH [BASE]'; return 1; }
  args=(--branch "$1" --cwd "$PWD" --focus)
  [[ -n "$2" ]] && args+=(--base "$2")
  "$_herdr_prezto_bin" worktree create "${args[@]}" >/dev/null
}

function hreload {
  local reload="$_herdr_prezto_root/bin/reload-all"
  [[ -x "$reload" ]] || return 1
  zsh "$reload" "$@"
}
