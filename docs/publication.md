# Publication and native validation

Repository: [alexg0/herdr-prezto](https://github.com/alexg0/herdr-prezto).
License: [MIT](../LICENSE), with upstream notices preserved in
[NOTICE.md](../NOTICE.md) and `licenses/`.
Native plugin ID: `herdr-prezto`; version: `0.1.0`.
Prezto module name: `herdr`.

The owner approved the public repository name and MIT publication on 2026-09-21.
Portable tests and real Prezto startup checks pass. Installation from GitHub
through Herdr and direct execution of the installed setup/check script were
verified on macOS with Herdr 0.9.3 on 2026-10-06. Live-session action invocation
and Linux have not been tested.

## Marketplace metadata

The manifest describes Prezto completions and pane helpers with read-only setup
diagnostics and notes that live-session action invocation remains untested,
matching the installation check below.

The [official marketplace documentation](https://herdr.dev/docs/marketplace/)
requires a public, non-fork, non-archived GitHub repository with topic
`herdr-plugin`, plus a parseable `herdr-plugin.toml` on its default branch at the
root or in a subdirectory. The index refreshes every 30 minutes and rescans when
the default-branch head changes. It is automatic discovery, not Herdr review or
endorsement; no separate catalog submission is documented.

The [official plugin reference](https://herdr.dev/docs/plugins/) requires `id`,
`name`, `version`, and `min_herdr_version`. This package declares those fields,
Unix platforms, and one executable setup/check action. Installing it does not
activate the Prezto module: the action prints the manual configuration steps.
There are no automatic build, startup, or event hooks.

The manifest and description prepare the package for discovery. Adding the
`herdr-plugin` topic and verifying a marketplace card remain separate steps
after the installation validation below and a green delivery PR. This
publication does not claim marketplace listing.

## Native validation boundary

Portable tests parse the manifest and execute the exact action script with
present/missing prerequisites. They check that it writes no files or invokes
Herdr and that printed paths are safely quoted. These checks do not prove that
Herdr accepts the manifest or executes the action.

## Verified installation path

```sh
herdr plugin install alexg0/herdr-prezto --ref main -y
```

Herdr 0.9.3 installed the public GitHub repository at default-branch commit
`982026c6c52d154eb4016ddd4b174e059379ea3b`, accepted its manifest, and persisted
an enabled `herdr-prezto` registration with the `setup-check` action and GitHub
source metadata. `-y` permits noninteractive installation; interactive users
can omit it and `--ref main`.

Verification used a short private `XDG_CONFIG_HOME`, private `XDG_STATE_HOME`,
and an explicit unused non-default lab `--session` on every Herdr command.
No server was provisioned. Herdr's offline installation fallback used only
private plugin storage, including the registry, lock, and managed checkout. The installed manifest and
registry action command were checked, and `sh native/setup-check.sh`, executed
from the installed checkout, exited 0 with successful prerequisite diagnostics
and manual Prezto configuration instructions. SHA-256 hashes of the live
registry and lock files and the live session-list output matched before and
after the check. No live session was contacted for plugin installation.

A short private path matters: the first attempt exceeded the Unix socket path
length limit before registration; retrying under a short temporary directory
succeeded without changing the package.

The isolation boundary remains relevant on Herdr 0.9.3:

- [`config_dir()`](https://github.com/herdrdev/herdr/blob/v0.9.3/src/config/io.rs#L30)
  resolves from `XDG_CONFIG_HOME` or HOME.
- [Plugin registry and lock paths](https://github.com/herdrdev/herdr/blob/v0.9.3/src/persist/plugin_registry.rs#L10)
  and [session/socket discovery](https://github.com/herdrdev/herdr/blob/v0.9.3/src/session.rs#L161)
  share that config directory. A named session alone does not isolate registration.
- Explicit `--session` takes precedence over `HERDR_SOCKET_PATH`.
- The [plugin CLI](https://github.com/herdrdev/herdr/blob/v0.9.3/src/cli/plugin.rs#L196)
  supports installation without a running server through its offline fallback.

## Remaining checks

The store installation gate is satisfied by the offline check above. It does
not establish live-session action invocation or plugin command-log behavior.
Those checks require an environment with private plugin storage and an owned
running session, without relaxing lifecycle isolation guards. Linux and the
manifest's minimum Herdr version, 0.9.1, remain untested for native installation.

After the delivery PR is green, add the authorized `herdr-plugin` discovery
topic and verify marketplace discovery separately. Source installation does
not itself prove that a marketplace card has appeared. Installing the native
companion still requires manual Prezto configuration; it never edits shell
startup files.
