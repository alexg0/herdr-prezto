# Packaging and dotfiles migration

This package has two independent entrypoints:

- `herdr/init.zsh`: Prezto loads module `herdr` from the repository root listed
  in `pmodule-dirs`. Runtime files are entirely inside `herdr/`.
- `herdr-plugin.toml` plus `native/setup-check.sh`: optional native Herdr
  diagnostics. Native registration does not install shell configuration.

A dotfiles manager should reference one stable checkout, such as
`~/.local/share/herdr-prezto`. It should not copy the module into dotfiles or
make a native plugin installation a prerequisite for completion. Consume an
approved commit/release only after standalone readiness is confirmed.

Merge this pattern into your existing `.zpreztorc` (keep your other directories
and your full module list):

```zsh
local herdr_root="$HOME/.local/share/herdr-prezto"
local -a extra_module_dirs selected_modules
zstyle -a ':prezto:load' pmodule-dirs extra_module_dirs
selected_modules=(environment terminal editor completion)
if [[ -r "$herdr_root/herdr/init.zsh" ]]; then
  extra_module_dirs+=("$herdr_root")
  selected_modules+=(herdr)
fi
selected_modules+=(history prompt)
zstyle ':prezto:load' pmodule-dirs "${extra_module_dirs[@]}"
zstyle ':prezto:load' pmodule "${selected_modules[@]}"
```

For an existing configuration with a variable module list, inserting `'herdr'`
explicitly after `'completion'` is often clearer than array manipulation. The
required invariants are an absent-safe directory check, exactly one module root,
and exactly one completion generation path.

Migration checklist:

1. Back up the existing `.zpreztorc`, `.zshrc`, and dotfiles-owned
   `zprezto-contrib/herdr` module/link. Record the approved standalone revision.
2. Verify the new checkout with the root README's one-command verification.
3. Replace the old `pmodule-dirs` entry with the standalone root. If the old
   directory supplies other modules, retain it and remove only its `herdr` module.
4. Remove the separate `herdr completion zsh` / `herdr completions zsh` generation
   block from `.zshrc` once this module is selected. Keep unrelated Herdr tab
   `zshexit` hooks and unrelated shell setup.
5. Open an isolated new shell: verify CLI present and absent behavior, completion
   registration, exactly one generation, unchanged multiplexer defaults, and no
   lifecycle calls. Check that `hreload` is no longer offered by the old module.
6. Remove the old managed module and its installed link only after verification.
   Ensure the dotfiles install manager will not recreate them.

Rollback: restore the backed-up dotfiles module and configuration, remove this
checkout's module entry, and open a new shell. Keep only one provider active.
This repository never performs that migration automatically.
