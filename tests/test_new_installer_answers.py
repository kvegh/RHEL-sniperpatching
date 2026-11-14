"""Exercise private native-answer updates and refusal boundaries with real Ansible."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
ANSWERS_TASKS = ROOT / 'playbooks/new/tasks/satellite_installer_answers.yml'
PLAYBOOK = ROOT / 'playbooks/new/configure_satellite.yml'
PASSWORD = 'synthetic-only-credential-0000000001'
PARAMETERS = 'class foreman(\n  $initial_admin_username = undef,\n  $initial_admin_password = undef,\n) {'


@unittest.skipUnless(os.geteuid() == 0, "Run root-ownership fixtures inside the verified installer EE.")
class NativeInstallerAnswers(unittest.TestCase):
    def run_case(self, original, *, password=PASSWORD, username='fixture-admin', parameters=PARAMETERS):
        with tempfile.TemporaryDirectory(prefix='sniper-installer-fixture-') as directory:
            work = Path(directory)
            target = work / 'answers.yaml'
            before = yaml.safe_dump(original, sort_keys=False)
            target.write_text(before)
            target.chmod(0o600)
            play = [{'name': 'Exercise only private native answer handling', 'hosts': 'localhost',
                     'connection': 'local', 'gather_facts': False,
                     'vars': {'sniper_installer_original_answers': original,
                              'sniper_installer_username': username,
                              'sniper_installer_password': password,
                              'sniper_installer_parameter_source': parameters,
                              'sniper_installer_answers_file': str(target)},
                     'tasks': [{'name': 'Run the production answer tasks',
                                'ansible.builtin.include_tasks': str(ANSWERS_TASKS)}]}]
            fixture = work / 'fixture.yml'
            fixture.write_text(yaml.safe_dump(play, sort_keys=False))
            result = subprocess.run(['ansible-playbook', '-i', 'localhost,', str(fixture)],
                                    capture_output=True, text=True, timeout=40)
            after = target.read_text()
            self.assertNotIn(password, result.stdout + result.stderr)
            if result.returncode == 0:
                again = subprocess.run(['ansible-playbook', '-i', 'localhost,', str(fixture)],
                                       capture_output=True, text=True, timeout=40)
                self.assertEqual(again.returncode, 0, again.stderr)
                self.assertRegex(again.stdout, r'changed=0\s')
                self.assertEqual(target.read_text(), after)
                self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            return result.returncode, before, after

    def test_fresh_seed_preserves_other_answers_and_is_idempotent(self):
        original = {'foreman': {'server_ssl_ca': '/etc/pki/katello/certs/katello-default-ca.crt',
                                'initial_organization': 'Fixture organization'},
                    'katello': {'enable_ostree': False}, 'puppet': False}
        code, unused, output = self.run_case(original)
        self.assertEqual(code, 0)
        expected = {**original, 'foreman': {**original['foreman'],
                    'initial_admin_username': 'fixture-admin', 'initial_admin_password': PASSWORD}}
        self.assertEqual(yaml.safe_load(output), expected)

    def test_existing_matching_secret_is_preserved(self):
        original = {'foreman': {'initial_admin_username': 'fixture-admin',
                               'initial_admin_password': PASSWORD, 'other_answer': 'keep'}}
        code, unused, output = self.run_case(original)
        self.assertEqual(code, 0)
        self.assertEqual(yaml.safe_load(output), original)

    def test_existing_different_secret_refuses_without_write(self):
        code, before, after = self.run_case({'foreman': {'initial_admin_password': 'existing-secret-do-not-replace'}})
        self.assertNotEqual(code, 0)
        self.assertEqual(before, after)

    def test_existing_different_username_refuses_without_write(self):
        code, before, after = self.run_case({'foreman': {'initial_admin_username': 'other-operator'}})
        self.assertNotEqual(code, 0)
        self.assertEqual(before, after)

    def test_unsupported_native_parameter_refuses_without_write(self):
        code, before, after = self.run_case({'foreman': {}}, parameters='class foreman() {')
        self.assertNotEqual(code, 0)
        self.assertEqual(before, after)

    def test_nonmapping_foreman_refuses_without_write(self):
        code, before, after = self.run_case({'foreman': True})
        self.assertNotEqual(code, 0)
        self.assertEqual(before, after)

    def test_newline_credential_refuses_without_write(self):
        code, before, after = self.run_case({'foreman': {}}, password=PASSWORD + '\nunsafe')
        self.assertNotEqual(code, 0)
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
