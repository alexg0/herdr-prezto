#!/usr/bin/env python3
"""One-command portable checks; never starts or controls a live Herdr session."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from check_herdr_startup import check

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--prezto-dir', type=Path,
                    default=Path(os.environ.get('PREZTO_DIR', '~/.zprezto')).expanduser())
parser.add_argument('--completion-file', type=Path)
args = parser.parse_args()
if not shutil.which('zsh'):
    parser.error('zsh is required')
for interpreter, filename in [('zsh', 'herdr/init.zsh'), ('sh', 'native/setup-check.sh')]:
    subprocess.run([interpreter, '-n', str(ROOT / filename)], check=True)
suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
    sys.exit(1)
check(args.prezto_dir, args.completion_file)
print('Portable verification passed (native Herdr validation is separate).')
