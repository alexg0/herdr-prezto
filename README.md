# herdr-prezto — Herdr for Prezto

Herdr CLI completion for [Prezto](https://github.com/sorin-ionescu/prezto),
plus slow-command reporting, notifications, and pane helpers inside
[Herdr](https://herdr.dev). The repository also contains a native Herdr
**setup/check action** that diagnoses prerequisites and prints manual installation
instructions. Installing that action does not load the module into Zsh.

[`alexg0/herdr-prezto`](https://github.com/alexg0/herdr-prezto) is MIT licensed.
The Prezto module passes portable and real-Prezto startup tests. Installation
from GitHub through Herdr and direct execution of the installed
setup/check script were verified on macOS with Herdr 0.9.3. Invocation through
a live Herdr session was not exercised; see the [validation boundary](docs/publication.md).
Install the Prezto module using the manual configuration instructions below.

## Requirements

- Zsh 5.9 or newer, with Prezto and its `completion` module.
- Herdr on your interactive shell's `PATH`. The package targets Herdr 0.9.1
  or newer; older versions have not been verified.
- macOS or Linux. The implementation uses Zsh and POSIX shell tools; current
  verification was on macOS with Zsh 5.9.2, Herdr 0.9.1, and Prezto
  `cff2d01871425b1b80710f8ec6a475c5a53145b4`. Linux is intended but not yet tested.
- For tests only: Python 3.11+ and an existing Prezto checkout. No Python
  package installation is needed.

The native action uses `sh`, `dirname`, and `sed`. It can report a missing Zsh
installation without requiring Zsh to start. Herdr's manifest version guard
requires 0.9.1; the action itself checks executable presence, not versions.

## Install the Prezto module

Use a checkout of this repository, for example at
`~/.local/share/herdr-prezto`:

```sh
git clone https://github.com/alexg0/herdr-prezto.git ~/.local/share/herdr-prezto
```

In `${ZDOTDIR:-$HOME}/.zpreztorc`, add the **repository root** to
`pmodule-dirs`. Preserve any directories you already have:

```zsh
zstyle ':prezto:load' pmodule-dirs \
  "$HOME/.local/share/herdr-prezto"
```

Add `herdr` immediately after `completion` in your existing `pmodule` list.
For example, a small configuration is:

```zsh
zstyle ':prezto:load' pmodule \
  'environment' \
  'terminal' \
  'editor' \
  'completion' \
  'herdr' \
  'history' \
  'prompt'
```

Keep your other modules. If you use `screen` or `tmux`, put `herdr` before them;
this package does not enable their auto-start options. Do not point
`pmodule-dirs` at the `herdr/` subdirectory or source `init.zsh` a second time.
Open a new shell and check:

```zsh
print -r -- ${_comps[herdr]-missing}
# Expected: _herdr (or a completer you deliberately registered earlier).
```

For a checkout that may be absent on some machines, use the guarded configuration
in [migration and packaging](docs/migration.md).

## What happens at startup

Without the Herdr executable or `compdef`, the module returns unloaded, as other
optional Prezto modules do. It never starts or attaches a Herdr session.
Completion works outside Herdr. Pane features require **both** `HERDR_ENV=1`
and a nonempty `HERDR_PANE_ID`; normal terminals get no hooks or helpers.

Without `ZSH_CACHE_DIR`, the module runs `herdr completion zsh` synchronously,
captures successful nonempty output, and evaluates it once. Failed output is
never evaluated. Existing completion registrations are preserved and do not
prevent pane helpers from loading. `HERDR_BIN_PATH` can select the executable,
but a `herdr` executable on PATH is still required by the Prezto module guard.

### Optional completion cache

Set a cache before Prezto loads, for example in `.zshrc` above its Prezto source:

```zsh
export ZSH_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/zsh"
```

The module adds `$ZSH_CACHE_DIR/completions` to `fpath`, registers an autoloadable
`_herdr` when no completer exists, and refreshes `_herdr` once per shell in a
silent background job. Successful, nonempty output replaces the old file with
a same-directory rename. Failed/empty output leaves the old cache intact.
Repeated sourcing does not schedule another refresh. This is separate from
Prezto's `zcompdump` cache; `ZSH_CACHE_DIR` is optional, not a Prezto default.

On the first cache-enabled shell there may be no file until the background job
finishes, so very early completion can be unavailable. The refreshed file is
used when `_herdr` is next autoloaded; a function already loaded in the current
shell remains unchanged. Open a new shell after upgrading Herdr. If refresh
fails with no previous file, fix the CLI or unset `ZSH_CACHE_DIR` before opening
a new shell. Cache files are executable shell code: use a directory you own.

## Pane reporting, notifications, and helpers

Commands taking at least ten seconds are reported as working, then idle, and
produce a completion notification unless the pane is focused. The command text,
exit status and elapsed time are included. Known agents and interactive tools
are ignored because Herdr tracks them separately. Hook communication failures
are suppressed so a missing socket does not break the prompt.

Settings retain their upstream `HERDR_OMZ_*` names for migration compatibility;
Oh My Zsh is not required. Set them before Prezto loads:

| Variable | Default | Meaning |
| --- | --- | --- |
| `HERDR_OMZ_THRESHOLD` | `10` | Nonnegative integer seconds before reporting |
| `HERDR_OMZ_REPORT` | `true` | Send slow-command state to Herdr |
| `HERDR_OMZ_NOTIFY` | `true` | Notify when a slow command finishes |
| `HERDR_OMZ_NOTIFY_FOCUSED` | `false` | Also notify for the focused pane |
| `HERDR_OMZ_DEFAULT_AGENT` | `claude` | Default kind for `hagent` |
| `HERDR_OMZ_IGNORE` | See `herdr/init.zsh` | Zsh array of programs to ignore |

For example, disable command-text reporting and notifications with:

```zsh
HERDR_OMZ_REPORT=false
HERDR_OMZ_NOTIFY=false
```

The following helpers act only when explicitly invoked inside a Herdr pane.
They use the calling pane/current directory and propagate command failures:

| Helper | Example | Effect |
| --- | --- | --- |
| `hsplit [right\|down] [COMMAND...]` | `hsplit down 'make test'` | Focus a new pane; optionally run a command |
| `htab [LABEL]` | `htab build` | Create and focus a tab in the current directory |
| `hagent NAME [KIND] [-- ARGS...]` | `hagent reviewer codex -- --help` | Split without focus and start an agent |
| `hworktree BRANCH [BASE]` | `hworktree feature main` | Create a Herdr worktree and focus it |
| `hreload [--dry-run]` | `hreload --dry-run` | Reload idle Zsh panes, or preview without sending commands |

`hreload` runs the packaged `herdr/bin/reload-all`. It skips panes with agents,
busy shells, unreadable process information, or shells other than Zsh. Eligible
panes receive `exec zsh` to load their shell configuration again; unexported shell
state is lost. `--dry-run` only reads pane information and prints the result,
without sending pane commands or notifications. See [provenance](NOTICE.md).

## Native Herdr setup/check action

The root [`herdr-plugin.toml`](herdr-plugin.toml) declares one useful action:
`herdr-prezto.setup-check`. It checks Zsh, the Herdr executable, a Prezto checkout,
and the packaged module, then prints a shell-quoted install path and module-order
instructions. It exits 1 if prerequisites are missing, 0 if found. It cannot
inspect the active completion state of a different shell. `PREZTO_DIR` selects
a custom Prezto checkout for the check.

Run the exact action script directly without registering a plugin:

```sh
sh native/setup-check.sh
```

Install the native companion from GitHub:

```sh
herdr plugin install alexg0/herdr-prezto
```

For noninteractive installation, use `-y`; `--ref main` selects the default
branch explicitly. On macOS with Herdr 0.9.3, the verified command was
`herdr plugin install alexg0/herdr-prezto --ref main -y`, with a private
`XDG_CONFIG_HOME`, a private `XDG_STATE_HOME`, and an explicit unused lab
`--session`. Herdr installed and registered the manifest without a running
server. Running `sh native/setup-check.sh` from that installed checkout passed.
The live plugin registry/lock hashes and session list were unchanged.

To invoke the action in your own running Herdr session:

```sh
herdr plugin action invoke herdr-prezto.setup-check
herdr plugin log list --plugin herdr-prezto
```

Live-session action invocation and plugin command logs were not exercised in
this validation. Herdr plugin registration is user-wide; a named session alone
does not isolate the registry. The package has no build command, startup hook,
event hook, keybinding, or automatic shell installer. The action does not invoke
Herdr or edit configuration. See the [validation details and remaining
checks](docs/publication.md).

## Verify

From the checkout root:

```sh
python3 tests/verify.py --prezto-dir "${PREZTO_DIR:-$HOME/.zprezto}"
```

This runs shell syntax checks, focused Python unit tests, manifest contract
checks, and real Prezto startup in private homes with Herdr present/absent and
with the module checkout absent. Stub commands reject lifecycle calls and count
exactly one completion generation. It checks completion functions, pane gates,
helpers, notifications, cache failure behavior, safe setup output, unchanged
PATH/SSH socket, and tmux/screen aliases. It never registers a native plugin.

To exercise real CLI output without live calls during tests, capture it
separately in an approved isolated environment and pass
`--completion-file /path/to/herdr-completion.zsh` to the same command.
Native manifest linking and action execution are a separate release check.

## Diagnostics

- **`missing` completion:** check `command -v herdr`, ensure `completion` precedes
  `herdr`, and run `whence -w compdef` in the affected shell.
- **Conflicting module locations:** remove the old dotfiles module from Prezto's
  search path; keep exactly one `herdr/` module.
- **Cached `_herdr` unavailable:** inspect `$ZSH_CACHE_DIR/completions/_herdr` and
  directory permissions. A new shell retries refresh; no cache is needed.
- **Helpers absent:** check `${HERDR_ENV:-0}` and `${HERDR_PANE_ID:-missing}`.
  Both pane guards must pass; do not forge them outside Herdr.
- **Native check cannot find Prezto:** set `PREZTO_DIR` for the action, or run
  `PREZTO_DIR=/path/to/prezto sh native/setup-check.sh` directly.
- **No slow-command notification:** check the threshold, ignore list, notification
  switches and whether the pane is focused. Hook failures are deliberately quiet.

## Uninstall and migration

Remove `herdr` from `pmodule` and this checkout from `pmodule-dirs`, preserving
other entries. Open a new shell to drop the old functions/hooks before deleting
the checkout. If used, remove only this module's `_herdr` cache file and refresh
Prezto's completion dump as needed; do not delete shared cache directories.

If you registered the native companion, unlink a local link with
`herdr plugin unlink herdr-prezto`, or uninstall a managed installation with
`herdr plugin uninstall herdr-prezto`. First remove any shell configuration that
points at that managed checkout. Native removal does not edit shell startup
files or affect existing shell functions. Herdr retains plugin config/state.

For a dotfiles-owned module, follow [the migration checklist](docs/migration.md)
to retain separate exit hooks and eliminate duplicate generation.

## License and attribution

The module adapts [robbyrussell/herdr-ohmyzsh](https://github.com/robbyrussell/herdr-ohmyzsh)
by Robby Russell and follows Prezto module conventions. Required upstream MIT
notices are retained under [`licenses/`](licenses/); see [NOTICE.md](NOTICE.md).
The project is distributed under the [MIT License](LICENSE), copyright 2026
Alexander Goldstein. The retained upstream notices also apply to their respective
portions.
