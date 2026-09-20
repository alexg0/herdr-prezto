"""Real Prezto in private homes; fake CLI accepts completion generation only."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def check(prezto_dir, completion_file=None):
    upstream = prezto_dir.resolve()
    if not (upstream / 'init.zsh').is_file():
        raise SystemExit('Supply an existing Prezto checkout with --prezto-dir')
    completion = (completion_file.read_text() if completion_file else
                  '#compdef herdr\n_herdr() { :; }\ncompdef _herdr herdr\n')
    results = {}
    (ROOT / 'tmp').mkdir(exist_ok=True)
    for mode in ('baseline', 'absent', 'present', 'missing-module'):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as directory:
            home = Path(directory)
            binary = home / 'bin'
            binary.mkdir()
            for name in ('tmux', 'screen'):
                p = binary / name
                p.write_text('#!/bin/sh\necho forbidden >> "$HOME/lifecycle"\nexit 99\n')
                p.chmod(0o755)
            if mode == 'present':
                (home / 'completion.zsh').write_text(completion)
                p = binary / 'herdr'
                p.write_text('''#!/bin/sh
printf '%s\\n' "$*" >> "$HOME/calls"
[ "$*" = 'completion zsh' ] || exit 99
exec /bin/cat "$HOME/completion.zsh"
''')
                p.chmod(0o755)
            (home / '.zprezto').symlink_to(upstream)
            module_root = ROOT if mode != 'missing-module' else home / 'not-installed'
            config = '''
zstyle ':prezto:load' pmodule 'completion' 'screen' 'tmux'
if [[ -r "$MODULE_ROOT/herdr/init.zsh" && "$MODE" != baseline ]]; then
  zstyle ':prezto:load' pmodule-dirs "$MODULE_ROOT"
  zstyle ':prezto:load' pmodule 'completion' 'herdr' 'screen' 'tmux'
fi
'''
            (home / '.zpreztorc').write_text(config)
            (home / '.zshrc').write_text('''
fpath=(${fpath:#*site-functions*})
source "$HOME/.zprezto/init.zsh"
''')
            env = dict(HOME=str(home), ZDOTDIR=str(home), MODE=mode,
                       MODULE_ROOT=str(module_root), TERM='xterm-256color',
                       XDG_CACHE_HOME=str(home / 'cache'),
                       PATH=str(binary) + ':/usr/bin:/bin',
                       SSH_TTY='/dev/test', SSH_AUTH_SOCK='/test/inherited')
            code = '''
print -r -- "completion=${_comps[herdr]-none}"
if [[ "$MODE" == present ]]; then
  (( $+functions[_herdr] )) || exit 20
  pmodload herdr
  source "$MODULE_ROOT/herdr/init.zsh" || exit 21
fi
(( ! $+functions[hsplit] && ! $+functions[_herdr_prezto_preexec] )) || exit 22
for name in herdr tmux screen; do
  for location in local remote; do
    zstyle -t ":prezto:module:$name:auto-start" "$location" && exit 23
  done
done
print -r -- "path=$PATH sock=$SSH_AUTH_SOCK"
print -r -- "tmuxa=$aliases[tmuxa] scr=$aliases[scr]"
'''
            p = subprocess.run([shutil.which('zsh'), '-d', '-i', '-c', code], env=env,
                               text=True, capture_output=True, timeout=30)
            assert p.returncode == 0 and not p.stderr, (mode, p.stdout, p.stderr)
            assert not (home / 'lifecycle').exists(), mode
            if mode == 'present':
                assert 'completion=_herdr' in p.stdout, p.stdout
                assert (home / 'calls').read_text() == 'completion zsh\n'
            else:
                assert 'completion=none' in p.stdout, p.stdout
                assert not (home / 'calls').exists()
            results[mode] = '\n'.join(p.stdout.splitlines()[1:]).replace(str(home), '<HOME>')
            print(f'{mode}: real Prezto startup passed; no lifecycle calls')
    assert len(set(results.values())) == 1, results
    print('Exactly one generation; PATH, SSH_AUTH_SOCK and tmux/screen aliases unchanged')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prezto-dir', type=Path, required=True)
    parser.add_argument('--completion-file', type=Path,
                        help='Previously captured real Herdr output (no live CLI calls)')
    args = parser.parse_args()
    check(args.prezto_dir, args.completion_file)
