# Code provenance and retained notices

`herdr/init.zsh` was extracted from the dotfiles module
`zprezto-contrib/herdr/init.zsh` at commit
`9fad49587bdb716eba40bd53ccc2ae05e8b811db`. The combined implementation entered
that history at `9978a6a`, authored by Alexander Goldstein. That source tree had
no license file and the module had no license header. The owner subsequently
approved publication of this standalone package under the MIT License on
2026-09-21; the effective grant is in [LICENSE](LICENSE).

The pane hooks, notification logic, helpers, and background completion-cache
pattern are adapted from Robby Russell's
[herdr-ohmyzsh](https://github.com/robbyrussell/herdr-ohmyzsh/tree/bbc072ada531e6306276900a866a4b44a9b92e74).
The upstream implementation and MIT license at that pinned revision were reviewed
against the extracted code. Its complete copyright and permission notice is
preserved verbatim in [licenses/herdr-ohmyzsh-MIT.txt](licenses/herdr-ohmyzsh-MIT.txt):
Copyright (c) 2026 Robby Russell. That upstream grant remains applicable to its
covered portions alongside the project license.

The requirement guard and module-loading conventions follow
[Prezto](https://github.com/sorin-ionescu/prezto/tree/cff2d01871425b1b80710f8ec6a475c5a53145b4).
Its full MIT notice is also preserved in
[licenses/prezto-MIT.txt](licenses/prezto-MIT.txt), including Robby Russell and
contributors (2009–2011) and Sorin Ionescu and contributors (2011–2017).
No Prezto distribution is bundled; verification uses a supplied checkout.

Extraction changes add portable tests and documentation, a native read-only
setup action, correct Prezto cache lookup/registration, preserve pane features
with existing completers, and make pane initialization repeat-safe.

## Reload helper

The source `zprezto-contrib/herdr/bin/reload-all` at dotfiles commit
`9fad49587bdb716eba40bd53ccc2ae05e8b811db` is preserved in that source history.
It invokes `omz reload`; its public upstream counterpart is
[bin/reload-all](https://github.com/robbyrussell/herdr-ohmyzsh/blob/bbc072ada531e6306276900a866a4b44a9b92e74/bin/reload-all).
The packaged `herdr/bin/reload-all` and `hreload` wrapper adapt that source for
Prezto by sending `exec zsh` instead of `omz reload`. Verification uses private
homes and a stub Herdr executable; no live reload-all invocation is used.

## Project license

[LICENSE](LICENSE) contains the owner-approved MIT license for this package,
with copyright 2026 Alexander Goldstein. Preserve it together with both upstream
notices when redistributing the relevant code. The source-history attribution
above was verified before adopting the license.
