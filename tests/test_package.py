"""Portable CLI tests; synthetic/offline, never reads WeChat."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
CLI = PACKAGE / 'scripts' / 'chat.py'


class PackageTests(unittest.TestCase):
    def test_collect_refuses_private_state_inside_installed_skill(self):
        sys.path.insert(0,str(PACKAGE/'scripts'))
        import business
        with self.assertRaisesRegex(ValueError,'outside'):
            business.collect(PACKAGE/'private',name='Fixture Peer',start='2024-01-01',end='2024-01-01',snapshot='unused')

    def test_test_runner_can_list_suite_without_running_private_capture(self):
        run=subprocess.run([sys.executable,str(PACKAGE/'scripts'/'test.py'),'--list'],capture_output=True,text=True,timeout=15)
        self.assertEqual(0,run.returncode,run.stderr)
        self.assertIn('BusinessTests',run.stdout)

    def test_bootstrap_exposes_a_separate_check_without_installing(self):
        with tempfile.TemporaryDirectory() as folder:
            run=subprocess.run([sys.executable,str(PACKAGE/'scripts'/'bootstrap.py'),'--root',folder,'--check'],
                               capture_output=True,text=True,timeout=15)
            self.assertEqual(0,run.returncode,run.stderr)
            self.assertFalse(json.loads(run.stdout)['ready'])
            self.assertFalse(Path(json.loads(run.stdout)['python']).is_relative_to(Path(folder)))
            self.assertEqual([],list(Path(folder).iterdir()))

    def test_local_only_state_is_never_a_default_inside_the_skill(self):
        import ast
        forbidden = ['/home/' + 'wts/', 'Administrator', '吉' + '长美']
        for path in (PACKAGE / 'scripts').glob('*.py'):
            text = path.read_text(encoding='utf-8')
            for token in forbidden:
                self.assertNotIn(token, text, str(path))

    def test_exclusive_lock_supports_windows_without_importing_fcntl(self):
        text = (PACKAGE / 'scripts' / 'workflow.py').read_text(encoding='utf-8')
        self.assertIn('msvcrt', text)
        self.assertNotIn('\nimport fcntl\n', text)

    def test_help_works_outside_repository_without_personal_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            run = subprocess.run([sys.executable, str(CLI), '--help'], cwd=folder,
                                 capture_output=True, text=True, timeout=15)
        self.assertEqual(0, run.returncode, run.stderr)
        for command in ['init', 'doctor', 'build', 'collect', 'context', 'save-analysis']:
            self.assertIn(command, run.stdout)


if __name__ == '__main__':
    unittest.main()
