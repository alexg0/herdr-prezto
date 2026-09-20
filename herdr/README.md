# Herdr Prezto module

Add the parent repository directory to Prezto's `pmodule-dirs`, then load `herdr`
after `completion`. `init.zsh` registers Herdr completion when Herdr and `compdef`
are available. Only Herdr panes get reporting hooks, notifications, and the
`hsplit`, `htab`, `hagent`, and `hworktree` helpers.

See the [installation and behavior guide](../README.md) for requirements, cache
behavior, configuration, diagnostics, verification, and uninstall instructions.
`hreload` is omitted because the inherited helper sends an Oh My Zsh command.
Upstream notices and the proposed owner license are explained in
[NOTICE.md](../NOTICE.md).
