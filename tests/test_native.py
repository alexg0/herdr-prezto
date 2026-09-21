"""Action contract and behavior without any real Herdr invocation or registry."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SetupAction(unittest.TestCase):
    def setUp(self):
        (ROOT / 'tmp').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'tmp')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.bin = self.home / 'bin'
        self.bin.mkdir()
        for name in ('dirname', 'sed'):
            (self.bin / name).symlink_to(shutil.which(name))
        self.env = dict(HOME=str(self.home), PATH=str(self.bin))

    def test_manifest_has_only_one_read_only_action(self):
        manifest = tomllib.loads((ROOT / 'herdr-plugin.toml').read_text())
        self.assertEqual(manifest['id'], 'herdr-prezto')
        self.assertEqual(manifest['platforms'], ['linux', 'macos'])
        self.assertEqual(len(manifest['actions']), 1)
        self.assertEqual(manifest['actions'][0]['command'], ['sh', 'native/setup-check.sh'])
        for key in ('build', 'startup', 'events', 'panes', 'link_handlers'):
            self.assertNotIn(key, manifest)

    def run_action(self, root=ROOT):
        before = {p.relative_to(self.home): p.read_bytes()
                  for p in self.home.rglob('*') if p.is_file() and not p.is_symlink()}
        result = subprocess.run(['/bin/sh', str(root / 'native/setup-check.sh')],
                                env=self.env, capture_output=True, text=True, timeout=10)
        after = {p.relative_to(self.home): p.read_bytes()
                 for p in self.home.rglob('*') if p.is_file() and not p.is_symlink()}
        self.assertEqual(before, after, 'The action changed files')
        self.assertEqual(result.stderr, '')
        return result

    def test_missing_prerequisites_are_actionable(self):
        result = self.run_action()
        self.assertEqual(result.returncode, 1)
        for text in ('MISSING: install Zsh', 'MISSING: install Herdr', 'MISSING: Prezto',
                     'pmodule-dirs', "immediately after 'completion'"):
            self.assertIn(text, result.stdout)

    def test_present_prerequisites_are_not_executed(self):
        (self.bin / 'zsh').symlink_to(shutil.which('zsh'))
        herdr = self.bin / 'herdr'
        herdr.write_text('#!/bin/sh\n: > "$HOME/UNEXPECTED-HERDR-CALL"\nexit 99\n')
        herdr.chmod(0o755)
        prezto = self.home / '.zprezto'
        (prezto / 'modules/completion').mkdir(parents=True)
        (prezto / 'init.zsh').touch()
        (prezto / 'modules/completion/init.zsh').touch()
        result = self.run_action()
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('MISSING:', result.stdout)
        self.assertIn('version not checked', result.stdout)

    def test_printed_path_is_a_safe_zsh_literal(self):
        root = self.home / "plugin ' space $(touch INJECTED)"
        (root / 'native').mkdir(parents=True)
        (root / 'herdr').mkdir()
        shutil.copy2(ROOT / 'native/setup-check.sh', root / 'native/setup-check.sh')
        (root / 'herdr/init.zsh').touch()
        result = self.run_action(root)
        line = next(line for line in result.stdout.splitlines() if line.startswith('  zstyle'))
        code = line + "\nzstyle -a ':prezto:load' pmodule-dirs dirs\nprint -r -- $dirs"
        check = subprocess.run([shutil.which('zsh'), '-dfc', code], env=self.env,
                               cwd=self.home, text=True, capture_output=True, timeout=10)
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertEqual(check.stdout.strip(), str(root))
        self.assertFalse((self.home / 'INJECTED').exists())
