# Publication and native validation

Repository: [alexg0/herdr-prezto](https://github.com/alexg0/herdr-prezto).
License: [MIT](../LICENSE), with upstream notices preserved in
[NOTICE.md](../NOTICE.md) and `licenses/`.
Native plugin ID: `herdr-prezto`; version: `0.1.0`.
Prezto module name: `herdr`.

The owner approved the public repository name and MIT publication on 2026-09-21.
Portable tests and real Prezto startup checks pass. Native Herdr installation
and action execution remain **unverified**, and Linux has not yet been tested.
Publication of the source does not establish either result.

## Marketplace metadata

Description: **Herdr completions, command notifications, and pane helpers for
Prezto, with a read-only setup/check action whose native installation is unverified.**

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
after native validation. This publication does not claim marketplace listing.

## Native validation boundary

Portable tests parse the manifest and execute the exact action script with
present/missing prerequisites. They check that it writes no files or invokes
Herdr and that printed paths are safely quoted. These checks do not prove that
Herdr accepts the manifest or executes the action.

An initial private-HOME/XDG test could not establish the required live default
session baseline; its lab helper refused provisioning before any plugin link.
The investigation then checked the official Herdr 0.9.1 implementation:

- [`config_dir()`](https://github.com/herdrdev/herdr/blob/v0.9.1/src/config/io.rs#L30)
  resolves from `XDG_CONFIG_HOME` or HOME. `HERDR_CONFIG_PATH` changes only the
  TOML file path, not that directory.
- [Plugin registry and lock paths](https://github.com/herdrdev/herdr/blob/v0.9.1/src/persist/plugin_registry.rs#L11)
  derive from the same config directory as
  [session discovery and sockets](https://github.com/herdrdev/herdr/blob/v0.9.1/src/session.rs#L157).
- `XDG_STATE_HOME` relocates plugin state but not the registry/config.
  Explicit `--session` takes precedence over `HERDR_SOCKET_PATH`.
- The [plugin CLI](https://github.com/herdrdev/herdr/blob/v0.9.1/src/cli/plugin.rs#L19)
  provides no read-only manifest validator; linking updates a registry.

No supported storage-only override was found that preserves the required
session/socket discovery namespace. The actual user plugin registry was not
used as a fallback. This is a limitation of the tested Herdr version and lab
contract, not a claim that safe native validation is impossible elsewhere.

## Remaining native release checks

Use an environment where both plugin storage and lifecycle isolation can be
proved. A named session alone does not isolate the user-wide registry.

1. Confirm private registry/config/state paths, an initially empty registry,
   and lifecycle operations constrained to the owned non-default session.
2. Link this tree, enumerate `herdr-prezto.setup-check`, and invoke it.
3. Read its command log; verify successful diagnostics and installation
   instructions, then exercise missing prerequisites.
4. Unlink only the test registration and safely tear down the owned session;
   confirm the user's registry and default session are unchanged.
5. Verify the minimum supported Herdr version and test Linux before describing
   either as tested native compatibility.
6. After those checks, add the discovery topic when authorized and verify the
   marketplace metadata and `herdr plugin install alexg0/herdr-prezto` path.

Do not relax isolation guards to complete these checks. The Prezto module can
be installed directly without native plugin registration.
