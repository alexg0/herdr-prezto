"""Herdr completion checks use private homes and never control a live session."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ZSH = shutil.which('zsh')
MODULE = ROOT / 'herdr/init.zsh'


class HerdrCompletion(unittest.TestCase):
    def setUp(self):
        (ROOT / 'tmp').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'tmp')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.bin = self.home / 'bin'
        self.bin.mkdir()
        self.log = self.home / 'calls'
        self.env = dict(HOME=str(self.home), ZDOTDIR=str(self.home),
                        PATH=str(self.bin), MODULE=str(MODULE),
                        ROOT=str(ROOT), CALLS=str(self.log), TERM='dumb')

    def shell(self, code):
        # Exclude machine-installed completions and dangling site symlinks.
        code = 'fpath=(${fpath:#*site-functions*})\n' + code
        result = subprocess.run([ZSH, '-dfc', code], env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, '')
        return result.stdout.strip()

    def stub(self, body=None):
        binary = self.bin / 'herdr'
        binary.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\n' +
                          (body or '''[ "$*" = 'completion zsh' ] || exit 99
printf '%s\n' '_herdr() { :; }' 'compdef _herdr herdr'
'''))
        binary.chmod(0o755)

    def test_present_registers_once(self):
        self.stub()
        self.assertEqual(self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
source "$MODULE" || exit 2
[[ -n $functions[_herdr] ]] || exit 3
print -r -- $_comps[herdr]
'''), '_herdr')
        self.assertEqual(self.log.read_text(), 'completion zsh\n')

    def test_absent_and_missing_compinit_are_safe(self):
        self.shell('source "$MODULE" && exit 1; [[ ! -n ${_comps[herdr]-} ]]')
        self.stub()
        self.shell('source "$MODULE" && exit 1; (( ! $+functions[_herdr] && ! $+functions[_herdr_prezto_preexec] ))')
        self.assertFalse(self.log.exists())

    def test_existing_registration_is_preserved(self):
        self.stub()
        self.shell('''autoload -Uz compinit; compinit -u -D
compdef _existing herdr
source "$MODULE" || exit 1
[[ $_comps[herdr] = _existing ]]
''')
        self.assertFalse(self.log.exists())

    def test_failed_generator_does_not_evaluate_partial_output(self):
        self.stub("printf '%s\\n' 'typeset -g partial_output_executed=yes'; exit 1\n")
        self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" && exit 1
[[ -z ${partial_output_executed-} && -z ${_comps[herdr]-} ]]
''')

    def test_cache_fallback_refreshes_once(self):
        self.stub()
        cache = self.home / 'cache'
        (cache / 'completions').mkdir(parents=True)
        self.env['ZSH_CACHE_DIR'] = str(cache)
        self.assertEqual(self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
source "$MODULE" || exit 4
[[ $_comps[herdr] = _herdr ]] || exit 2
/bin/sleep 1
[[ -s "$ZSH_CACHE_DIR/completions/_herdr" ]] || exit 3
'''), '')
        self.assertEqual(self.log.read_text(), 'completion zsh\n')

    def test_pane_features_are_gated_and_report(self):
        self.stub()
        self.env.update(HERDR_ENV='1', HERDR_PANE_ID='w1:p1',
                        HERDR_OMZ_THRESHOLD='0', HERDR_OMZ_NOTIFY='false')
        self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
(( $+functions[hsplit] && $+functions[htab] && $+functions[hagent] &&
   $+functions[hworktree] )) || exit 2
_herdr_prezto_preexec 'sleep 1' 'sleep 1'
_herdr_prezto_precmd
''')
        calls = self.log.read_text()
        self.assertIn('pane report-agent w1:p1', calls)


    def test_existing_completion_does_not_disable_pane_helpers(self):
        self.stub()
        self.env.update(HERDR_ENV='1', HERDR_PANE_ID='w1:p1')
        self.shell('''autoload -Uz compinit; compinit -u -D
compdef _existing herdr
source "$MODULE" || exit 1
(( $+functions[hsplit] )) || exit 2
[[ $_comps[herdr] = _existing ]]
''')

    def test_cache_is_usable_without_external_fpath_setup(self):
        self.stub()
        cache = self.home / 'cache'
        (cache / 'completions').mkdir(parents=True)
        (cache / 'completions/_herdr').write_text('#compdef herdr\nreturn 0\n')
        self.env['ZSH_CACHE_DIR'] = str(cache)
        self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
[[ $_comps[herdr] = _herdr ]] || exit 2
[[ ${fpath[(Ie)$ZSH_CACHE_DIR/completions]} -gt 0 ]] || exit 3
_herdr || exit 4
/bin/sleep 0.2
''')

    def test_empty_generator_does_not_register(self):
        self.stub('exit 0\n')
        self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" && exit 1
[[ -z ${_comps[herdr]-} ]]
''')

    def test_each_pane_guard_is_required(self):
        self.stub()
        for env in ({}, {'HERDR_ENV': '1'}, {'HERDR_PANE_ID': 'w1:p1'},
                    {'HERDR_ENV': '0', 'HERDR_PANE_ID': 'w1:p1'}):
            with self.subTest(env=env):
                self.env.pop('HERDR_ENV', None)
                self.env.pop('HERDR_PANE_ID', None)
                self.env.update(env)
                self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
(( ! $+functions[hsplit] && ! $+functions[_herdr_prezto_preexec] ))
''')
        self.assertEqual(self.log.read_text(), 'completion zsh\n' * 4)

    def test_pane_state_survives_repeated_source(self):
        self.stub()
        self.env.update(HERDR_ENV='1', HERDR_PANE_ID='w1:p1')
        self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
_herdr_prezto_label=test-command
_herdr_prezto_registered=1
source "$MODULE" || exit 2
[[ $_herdr_prezto_registered = 1 && $_herdr_prezto_label = test-command ]] || exit 3
[[ ${(M)#precmd_functions:#_herdr_prezto_precmd} = 1 ]] || exit 4
(( ! $+functions[hreload] )) || exit 5
_herdr_prezto_registered=0
''')
        self.assertEqual(self.log.read_text(), 'completion zsh\n')

    def test_failed_cache_refresh_preserves_old_completion(self):
        self.stub("printf '%s\\n' partial; exit 1\n")
        cache = self.home / 'cache'
        (cache / 'completions').mkdir(parents=True)
        target = cache / 'completions/_herdr'
        target.write_text('#compdef herdr\nreturn 0\n')
        self.env['ZSH_CACHE_DIR'] = str(cache)
        self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
source "$MODULE" || exit 2
/bin/sleep 0.3
''')
        self.assertEqual(target.read_text(), '#compdef herdr\nreturn 0\n')
        self.assertEqual(list(target.parent.iterdir()), [target])
        self.assertEqual(self.log.read_text(), 'completion zsh\n')

    def test_helpers_use_explicit_current_pane_and_arguments(self):
        self.stub('''case "$*" in
  'completion zsh') printf '%s\\n' '_herdr() { :; }' 'compdef _herdr herdr' ;;
  'pane split '*) printf '%s\\n' '{"result":{"pane":{"pane_id":"w1:p2"}}}' ;;
esac
''')
        self.env.update(HERDR_ENV='1', HERDR_PANE_ID='w1:p1')
        self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
hsplit down 'echo hello' || exit 2
htab build || exit 3
hagent reviewer codex -- --help || exit 4
hworktree feature main || exit 5
''')
        calls = self.log.read_text()
        self.assertIn('pane split --current --direction down --cwd ', calls)
        self.assertIn('pane run w1:p2 echo hello', calls)
        self.assertIn('agent start reviewer --kind codex --pane w1:p2 -- --help', calls)
        self.assertIn('worktree create --branch feature --cwd ', calls)
        self.assertIn('--base main', calls)

    def test_notifications_and_ignored_commands(self):
        self.stub('''case "$*" in
  'completion zsh') printf '%s\\n' '_herdr() { :; }' 'compdef _herdr herdr' ;;
  'pane current --current') printf '%s\\n' '{"focused":false}' ;;
esac
''')
        self.env.update(HERDR_ENV='1', HERDR_PANE_ID='w1:p1',
                        HERDR_OMZ_REPORT='false', HERDR_OMZ_THRESHOLD='0')
        self.shell('''autoload -Uz compinit; compinit -u -D
source "$MODULE" || exit 1
_herdr_prezto_preexec 'codex' 'codex'
(( _herdr_prezto_start == 0 )) || exit 2
_herdr_prezto_preexec 'make build' 'make build'
false
_herdr_prezto_precmd
''')
        calls = self.log.read_text()
        self.assertIn('notification show Failed: make build --body exit 1, took ', calls)
        self.assertNotIn('pane report-agent', calls)


if __name__ == '__main__':
    unittest.main()
