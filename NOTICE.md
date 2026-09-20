# Code provenance and retained notices

`herdr/init.zsh` was extracted from the dotfiles module
`zprezto-contrib/herdr/init.zsh` at commit
`9fad49587bdb716eba40bd53ccc2ae05e8b811db`. The combined implementation entered
that history at `9978a6a`, authored by Alexander Goldstein. That source tree had
no license file and the module had no license header. Extraction does not
establish permission to publish newly authored portions.

The pane hooks, notification logic, helpers, and background completion-cache
pattern are adapted from Robby Russell's
[herdr-ohmyzsh](https://github.com/robbyrussell/herdr-ohmyzsh/tree/bbc072ada531e6306276900a866a4b44a9b92e74).
The upstream implementation and MIT license at that pinned revision were reviewed
against the extracted code. Its complete copyright and permission notice is
preserved verbatim in [licenses/herdr-ohmyzsh-MIT.txt](licenses/herdr-ohmyzsh-MIT.txt):
Copyright (c) 2026 Robby Russell. That upstream grant remains applicable to its
covered portions regardless of the proposed owner license.

The requirement guard and module-loading conventions follow
[Prezto](https://github.com/sorin-ionescu/prezto/tree/cff2d01871425b1b80710f8ec6a475c5a53145b4).
Its full MIT notice is also preserved in
[licenses/prezto-MIT.txt](licenses/prezto-MIT.txt), including Robby Russell and
contributors (2009–2011) and Sorin Ionescu and contributors (2011–2017).
No Prezto distribution is bundled; verification uses a supplied checkout.

Extraction changes add portable tests and documentation, a native read-only
setup action, correct Prezto cache lookup/registration, preserve pane features
with existing completers, and make pane initialization repeat-safe.

## Omitted reload helper

The source `zprezto-contrib/herdr/bin/reload-all` at dotfiles commit
`9fad49587bdb716eba40bd53ccc2ae05e8b811db` is preserved in that source history.
It invokes `omz reload`; its public upstream counterpart is
[bin/reload-all](https://github.com/robbyrussell/herdr-ohmyzsh/blob/bbc072ada531e6306276900a866a4b44a9b92e74/bin/reload-all).
Neither it nor the `hreload` wrapper is shipped here. This prevents advertising
an Oh My Zsh operation as working Prezto support. No real reload-all invocation
was used for extraction or verification.

## Proposed owner license

[LICENSE.proposed](LICENSE.proposed) contains an MIT proposal for owner review.
It is deliberately not named `LICENSE`, and is not yet an effective grant for
new code. Before publication, the owner must confirm authorship/rights and the
copyright line, approve a license, and retain the upstream notices above.
No license approval or publication authority is inferred from this draft.
