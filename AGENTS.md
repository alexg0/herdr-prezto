# Project agent memory

- Runtime behavior lives in `herdr/init.zsh`; installation, guards, cache behavior,
  and helper settings are documented in `README.md`.
- Run `python3 tests/verify.py --prezto-dir /path/to/prezto` for portable verification.
  Tests use private homes and stubs; native registry validation is separate.
- `native/setup-check.sh` must remain read-only: no shell configuration edits,
  Herdr calls, or session lifecycle operations.
- Native plugin registration is user-wide. See `docs/publication.md` for the
  isolation requirement and outstanding native validation gate.
- The public package is `alexg0/herdr-prezto`; its Prezto module remains `herdr`.
- Preserve `LICENSE` (MIT), upstream notices in `licenses/`, and `NOTICE.md`.
  `hreload` is intentionally omitted.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
