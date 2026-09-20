#!/bin/sh
# Read-only: no shell config writes, Herdr invocations, or session operations.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
prezto=${PREZTO_DIR:-${ZDOTDIR:-$HOME}/.zprezto}
missing=0
printf '%s\n' 'Herdr for Prezto — setup check' ''
if command -v zsh >/dev/null 2>&1; then
  printf '%s\n' 'OK: zsh is on PATH.'
else
  printf '%s\n' 'MISSING: install Zsh and add it to PATH.'
  missing=1
fi
if command -v "${HERDR_BIN_PATH:-herdr}" >/dev/null 2>&1; then
  printf '%s\n' 'OK: Herdr executable is available (version not checked).'
else
  printf '%s\n' 'MISSING: install Herdr 0.9.1 or newer and add it to PATH.'
  missing=1
fi
if [ -r "$prezto/init.zsh" ] && [ -r "$prezto/modules/completion/init.zsh" ]; then
  printf '%s\n' 'OK: Prezto and its completion module were found.'
else
  printf '%s\n' 'MISSING: Prezto with its completion module; set PREZTO_DIR for a custom checkout.'
  missing=1
fi
if [ -r "$root/herdr/init.zsh" ]; then
  printf '%s\n' 'OK: herdr/init.zsh is packaged.'
else
  printf '%s\n' 'MISSING: herdr/init.zsh; restore the complete plugin checkout.'
  missing=1
fi
printf '\n%s\n' 'Manual setup in .zpreztorc (preserve your existing module directories):'
# Quote a literal path for Zsh, including spaces, quotes and shell metacharacters.
quoted_root=$(printf '%s' "$root" | sed "s/'/'\\\\''/g")
printf "  zstyle ':prezto:load' pmodule-dirs '%s'\n" "$quoted_root"
printf '%s\n' \
  "  # Add 'herdr' immediately after 'completion' in your existing pmodule list." \
  "  # For example: zstyle ':prezto:load' pmodule 'completion' 'herdr'" \
  '' \
  'Keep Herdr on the interactive shell PATH even when HERDR_BIN_PATH is set.' \
  'Open a new shell; do not reload all panes.' \
  'In that shell, verify: print -r -- ${_comps[herdr]-missing}' \
  'This process cannot verify the completion registration in another shell.' \
  'No configuration was edited and no sessions were started or stopped.'
exit "$missing"
