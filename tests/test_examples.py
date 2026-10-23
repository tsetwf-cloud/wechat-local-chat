"""Reader example regression; synthetic data, never accesses WeChat."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
DEMO = PACKAGE / 'examples' / 'run_demo.py'


@unittest.skipIf(sys.platform == 'win32', 'Example runner is documented for Linux/WSL')
class ExampleTests(unittest.TestCase):
    def test_documented_demo_runs_real_cli_with_scoped_citations(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'demo'
            run = subprocess.run([sys.executable, str(DEMO), '--output', str(output)],
                                 cwd=directory, capture_output=True, text=True,
                                 encoding='utf-8', timeout=30)
            self.assertEqual(0, run.returncode, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(3, result['selected_messages'])
            self.assertEqual(1, result['keyword_matches'])
            self.assertEqual(3, result['cited_messages'])
            self.assertEqual('saved-snapshot', result['source_mode'])
            self.assertFalse(result['wal_included'])
            self.assertFalse(result['model_called'])
            self.assertEqual(2, result['excluded_controls'])
            report = Path(result['report_path'])
            text = report.read_text(encoding='utf-8')
            self.assertIn('Prewritten synthetic demonstration', text)
            self.assertIn('Room booking is still unconfirmed', text)
            self.assertNotIn('OUTSIDE_SELECTED_SCOPE', text)
            self.assertEqual(hashlib.sha256(report.read_bytes()).hexdigest(), result['report_sha256'])
            meta = json.loads(report.with_suffix('.json').read_text())
            self.assertEqual(3, len(meta['cited_message_ids']))
            self.assertEqual(result['report_sha256'], meta['report_sha256'])
            self.assertEqual('prewritten synthetic fixture; no model called', meta['generated_by'])
            second = subprocess.run([sys.executable, str(DEMO), '--output', str(output)],
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(0, second.returncode)
            self.assertIn('already exists', second.stderr)
            self.assertEqual(result['report_sha256'], hashlib.sha256(report.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
