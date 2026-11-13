"""Exercise output protection and check-mode behavior with local Ansible."""

# Reason and test scope: ../docs/implementation.md#synthetic-test-modules


import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

from track_paths import TRACK_ROOT

ROOT = TRACK_ROOT


class ReviewRegressions(unittest.TestCase):
    def run_playbook(self, folder, name, check=False, collections=None, verbose=False):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        environment["ANSIBLE_LOCAL_TEMP"] = str(folder / "local")
        environment["ANSIBLE_REMOTE_TEMP"] = str(folder / "remote")
        if collections:
            environment["ANSIBLE_COLLECTIONS_PATH"] = str(collections)
        command = ["ansible-playbook", "-i", "localhost,", str(folder / name)]
        if check:
            command.append("--check")
        if verbose:
            command.append("-vv")
        return subprocess.run(
            command,
            cwd=folder,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_sensitive_process_arguments_are_hidden_but_reboot_detection_still_works(
        self,
    ):
        plays = yaml.safe_load((ROOT / "patch_hosts.yml").read_text())
        diagnostic = next(
            task
            for task in plays[1]["tasks"]
            if task["name"] == "Detect running processes still using replaced binaries"
        )
        marker = "synthetic-sensitive-process-argument"
        diagnostic["ansible.builtin.command"]["argv"] = [
            sys.executable,
            "-c",
            "print('123 : example --token=' + " + repr(marker) + ")",
        ]
        assertion = {
            "name": "Require the actual registered output to remain usable",
            "ansible.builtin.assert": {
                "that": [
                    "sniper_stale_processes.stdout_lines | select('match', '^[0-9]+\\s*:') | list | length == 1"
                ],
                "quiet": True,
            },
        }
        with tempfile.TemporaryDirectory(prefix="sniper-review-output-") as directory:
            folder = Path(directory)
            (folder / "check.yml").write_text(
                yaml.safe_dump(
                    [
                        {
                            "name": "Check process diagnostics",
                            "hosts": "localhost",
                            "connection": "local",
                            "gather_facts": False,
                            "tasks": [diagnostic, assertion],
                        }
                    ]
                )
            )
            result = self.run_playbook(folder, "check.yml", verbose=True)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertNotIn(marker, output)

    def test_runtime_diagnostic_collects_its_report_in_check_mode(self):
        with tempfile.TemporaryDirectory(
            prefix="sniper-review-check-mode-"
        ) as directory:
            folder = Path(directory)
            for name in ["vars", "tasks", "files"]:
                (folder / name).mkdir()
            shutil.copy2(ROOT / "check_runtime.yml", folder)
            shutil.copy2(ROOT / "tasks/runtime_satellite.yml", folder / "tasks")
            (folder / "vars/main.yml").write_text(
                yaml.safe_dump(
                    {
                        "sniper_server_url": "https://satellite.example.test",
                        "sniper_username": "fixture-user",
                        "sniper_password": "fixture-only",
                    }
                )
            )
            report = {
                "ansible_core": "fixture",
                "python": "fixture",
                "satellite_collections": {},
                "modules": ["redhat.satellite.resource_info"],
                "missing_modules": [],
                "module_argument_failures": [],
                "syntax_failures": {},
                "syntax_checked": ["fixture.yml"],
            }
            (folder / "files/runtime_probe.py").write_text(
                "import json\nprint(json.dumps(" + repr(report) + "))\n"
            )
            collections = folder / "collections"
            collection = collections / "ansible_collections/redhat/satellite"
            modules = collection / "plugins/modules"
            modules.mkdir(parents=True)
            (collection / "galaxy.yml").write_text(
                "namespace: redhat\nname: satellite\nversion: 3.14.0\n"
            )
            (modules / "resource_info.py").write_text(
                "from ansible.module_utils.basic import AnsibleModule\n"
                "spec = {key: {'type': 'str'} for key in "
                "('server_url', 'username', 'resource')}\n"
                "spec['password'] = {'type': 'str', 'no_log': True}\n"
                "spec['validate_certs'] = {'type': 'bool'}\n"
                "module = AnsibleModule(argument_spec=spec, supports_check_mode=True)\n"
                "module.exit_json(changed=False, resources=[{'id': 1}])\n"
            )
            result = self.run_playbook(
                folder, "check_runtime.yml", check=True, collections=collections
            )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("Record read-only runtime verification", output)


if __name__ == "__main__":
    unittest.main()
