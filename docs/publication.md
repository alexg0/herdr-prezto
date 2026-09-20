# Proposed publication and marketplace listing

This document is a review draft. No repository creation, push, topic change,
marketplace submission, user-wide plugin registration, or publication is
part of the local extraction delivery.

Proposed repository: **alexg0/prezto-herdr**, public, non-fork, not archived.
Proposed description: **Herdr completions, command notifications, and pane
helpers for Prezto, with a read-only Herdr setup/check action.**
Proposed native id: `prezto-herdr`; version: `0.1.0`.

## Discovery requirements

The [official marketplace documentation](https://herdr.dev/docs/marketplace/)
was checked on 2026-09-20. Discovery requires a public, non-fork, non-archived
GitHub repository with topic `herdr-plugin`, and a `herdr-plugin.toml` at the
root or in a subdirectory on its default branch. Required metadata must parse.
The index refreshes every 30 minutes and rescans when the default-branch head
changes. A repository gets one card; each valid manifest is separately
installable. This is automatic discovery, not Herdr review or endorsement;
no manual catalog submission is documented.

The [official plugin reference](https://herdr.dev/docs/plugins/) requires `id`,
`name`, `version`, and `min_herdr_version`. Our manifest also declares a
truthful description, Unix platforms, and one executable setup/check action.
There are no automatic hooks or build steps. Installing it does not activate
Prezto. The action's output explains that manual step.

## Native validation boundary

Portable tests validate TOML shape and execute the exact action script with
present/missing prerequisites, check that it writes no files or invokes Herdr,
and verify safe quoting of paths containing spaces and shell metacharacters.
These tests do not prove that Herdr accepts the manifest or runs the action.

Native validation was attempted with a scaffold helper, a generated non-default
session name, and isolated HOME/XDG storage. The helper refused provisioning:

```text
fleet-state tripwire requires exactly one running default session
```

Under the private environment it could not establish the required live-default
baseline. Teardown then refused destructive calls because no tripwire existed.
No plugin link or action invocation followed. Native acceptance remains
unverified; user-wide registration was not used as a fallback.

Before release, use an isolated Herdr environment whose session routing **and**
plugin registry storage can both be proven. A session name alone does not isolate
the user-wide plugin registry. The test must:

1. Confirm registry/config/state paths are private, the registry starts empty,
   and all lifecycle operations are constrained to the owned non-default session.
2. Link this exact tree, enumerate `prezto-herdr.setup-check`, and invoke it.
3. Read the plugin command log and verify successful prerequisite diagnostics
   and installation instructions; exercise missing prerequisites too.
4. Unlink only the test registration and safely tear down the owned session.
   Verify the user's default session and plugin registry were unchanged.

Do not relax a helper's safety gate to complete that check.

## Owner approval checklist

- [ ] Confirm rights and adopt an effective license from `LICENSE.proposed`,
  retaining `NOTICE.md` and both upstream notices.
- [ ] Complete isolated native validation; verify the minimum supported Herdr
  release and test Linux before calling it a tested platform.
- [ ] Review module behavior, packaging, description, public documentation, and
  the portable verification result.
- [ ] Authorize creation of the proposed public non-fork repository and publication
  of the approved branch to its default branch.
- [ ] Authorize adding the `herdr-plugin` topic after the valid manifest lands.
- [ ] After the index refresh, verify the card, metadata and root install command:
  `herdr plugin install alexg0/prezto-herdr`.

Update the README's prepublication status only when the relevant steps are
actually complete. Marketplace eligibility is prepared; listing and native
compatibility are not claimed as verified.
