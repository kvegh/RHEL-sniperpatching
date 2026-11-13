"""Verify the NEW preparation guard uses native RPM ordering and the running kernel."""
import contextlib
import io
import json
from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'playbooks/new/files/new_kernel_check.py'


class NewKernelProof(unittest.TestCase):
    def run_probe(self, running, rows):
        comparisons = []
        def compare(left, right):
            comparisons.append((left, right))
            return (left > right) - (left < right)
        fake = SimpleNamespace(TransactionSet=lambda: SimpleNamespace(dbMatch=lambda *_: rows),
                               labelCompare=compare)
        out = io.StringIO()
        with patch.dict('sys.modules', {'rpm': fake}), patch('os.uname', return_value=SimpleNamespace(release=running)), patch('platform.machine', return_value='x86_64'):
            with contextlib.redirect_stdout(out):
                runpy.run_path(str(SCRIPT))
        return json.loads(out.getvalue()), comparisons

    def test_old_running_kernel_is_not_accepted(self):
        rows = [{'epoch': 0, 'version': '5.14.0', 'release': '400', 'arch': 'x86_64'},
                {'epoch': 0, 'version': '5.14.0', 'release': '500', 'arch': 'x86_64'}]
        data, comparisons = self.run_probe('5.14.0-400.x86_64', rows)
        self.assertFalse(data['running_latest_kernel'])
        self.assertTrue(comparisons)
        self.assertEqual(data['latest_kernel'], '5.14.0-500.x86_64')

    def test_newest_running_kernel_and_native_epoch_are_used(self):
        rows = [{'epoch': 1, 'version': '5.14.0', 'release': '400', 'arch': 'x86_64'},
                {'epoch': 0, 'version': '5.14.0', 'release': '500', 'arch': 'x86_64'},
                {'epoch': 8, 'version': '9.0.0', 'release': '900', 'arch': 'aarch64'}]
        data, _ = self.run_probe('5.14.0-400.x86_64', rows)
        self.assertTrue(data['running_latest_kernel'])

    def test_missing_native_kernel_fails_without_a_success_report(self):
        with self.assertRaises(SystemExit):
            self.run_probe('5.14.0-400.x86_64', [])


if __name__ == '__main__':
    unittest.main()
