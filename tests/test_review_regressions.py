"""Exercise output protection and check-mode behavior with local Ansible."""

# Reason and test scope: ../docs/implementation.md#synthetic-test-modules


from copy import deepcopy
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


def nested_tasks(tasks):
    """Find a behavior task regardless of the surrounding cleanup block."""
    for task in tasks:
        yield task
        for section in ("block", "rescue", "always"):
            yield from nested_tasks(task.get(section, []))


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
            for task in nested_tasks(plays[1]["tasks"])
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

    def test_new_host_pins_precede_facts_and_are_removed_on_every_outcome(self):
        new_root = Path(__file__).resolve().parents[1] / "playbooks/new"
        for stage in ("patch_hosts.yml", "check_patch.yml"):
            for outcome in ("success", "missing_key", "facts_failure", "work_failure"):
                with self.subTest(stage=stage, outcome=outcome):
                    self.check_new_host_trust(new_root, stage, outcome)

    def check_new_host_trust(self, new_root, stage, outcome):
        """Run the real pin/facts/cleanup lifecycle around synthetic target work."""
        play = deepcopy(yaml.safe_load((new_root / stage).read_text())[1])
        lifecycle = next(task for task in play["tasks"] if "block" in task)
        pin, facts = deepcopy(lifecycle["block"][:2])
        if outcome == "facts_failure":
            facts["ansible.builtin.setup"] = {"unsupported_fixture_argument": True}
        else:
            facts["ansible.builtin.setup"] = {"filter": ["ansible_system"]}
        synthetic_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFixtureOnly"
        inspect_pin = {
            "name": "Require the prepared pin during target work",
            "ansible.builtin.assert": {
                "that": [
                    "lookup('ansible.builtin.file', sniper_new_trust_file.path) == "
                    + repr("127.0.0.1 " + synthetic_key),
                    "'-o StrictHostKeyChecking=yes' in ansible_ssh_common_args",
                    "'-o GlobalKnownHostsFile=/dev/null' in ansible_ssh_common_args",
                    "'-o UpdateHostKeys=no' in ansible_ssh_common_args",
                    "sniper_new_trust_file.path in ansible_ssh_common_args",
                ]
            },
        }
        lifecycle["block"] = [pin, facts, inspect_pin]
        if outcome == "work_failure":
            lifecycle["block"].append(
                {
                    "name": "Fail synthetic target work after pin preparation",
                    "ansible.builtin.fail": {"msg": "synthetic-target-work-failed"},
                }
            )
        with tempfile.TemporaryDirectory(prefix="sniper-client-trust-") as directory:
            folder = Path(directory)
            (folder / "tasks").mkdir()
            (folder / "pins").mkdir()
            shutil.copy2(new_root / "tasks/ssh_pin.yml", folder / "tasks")
            play.update(
                hosts="localhost",
                connection="local",
                vars_files=[],
                tasks=[lifecycle],
                environment={"TMPDIR": str(folder / "pins")},
                vars={
                    "ansible_host": "127.0.0.1",
                    "ansible_become": False,
                    "ansible_python_interpreter": sys.executable,
                    "sniper_ssh_host_key": synthetic_key,
                },
            )
            if outcome == "missing_key":
                del play["vars"]["sniper_ssh_host_key"]
            # Observe the actual source cleanup; never replace it with a fixture.
            lifecycle["always"].insert(
                0,
                {
                    "name": "Observe the allocated pin before source cleanup",
                    "ansible.builtin.stat": {"path": "{{ sniper_new_trust_file.path }}"},
                    "when": "sniper_new_trust_file.path is defined",
                    "register": "fixture_pin",
                    "delegate_to": "localhost",
                    "become": False,
                },
            )
            lifecycle["always"].append(
                {
                    "name": "Record synthetic lifecycle observations",
                    "ansible.builtin.copy": {
                        "dest": str(folder / "observed.json"),
                        "mode": "0600",
                        "content": "{{ {'trust_file': sniper_new_trust_file.path | default(''), "
                        "'existed': fixture_pin.stat.exists | default(false)} | to_json }}",
                    },
                    "delegate_to": "localhost",
                    "become": False,
                }
            )
            (folder / "trust.yml").write_text(yaml.safe_dump([play], sort_keys=False))
            result = self.run_playbook(folder, "trust.yml")
            output = result.stdout + result.stderr
            observed_path = folder / "observed.json"
            self.assertTrue(observed_path.exists(), output)
            observed = json.loads(observed_path.read_text())
            self.assertEqual(result.returncode == 0, outcome == "success", output)
            self.assertNotIn("TASK [Gathering Facts]", output)
            self.assertNotIn("error while evaluating conditional", output.lower())
            if outcome == "missing_key":
                self.assertFalse(observed["existed"], output)
                self.assertEqual(observed["trust_file"], "", output)
            else:
                self.assertTrue(observed["existed"], output)
                self.assertFalse(Path(observed["trust_file"]).exists(), output)
                self.assertLess(
                    output.index("Write only the verified target public key"),
                    output.index("Gather facts only after preparing strict SSH trust"),
                )
            if outcome == "work_failure":
                self.assertIn("synthetic-target-work-failed", output)
            self.assertEqual(list((folder / "pins").iterdir()), [], output)

    def test_runtime_diagnostic_collects_its_report_in_check_mode(self):
        with tempfile.TemporaryDirectory(
            prefix="sniper-review-check-mode-"
        ) as directory:
            folder = Path(directory)
            for name in ["vars", "tasks", "files"]:
                (folder / name).mkdir()
            shutil.copy2(ROOT / "check_runtime.yml", folder)
            shutil.copy2(ROOT / "tasks/runtime_satellite.yml", folder / "tasks")
            for include in ("api_ca.yml", "api_ca_cleanup.yml"):
                if (ROOT / "tasks" / include).exists():
                    shutil.copy2(ROOT / "tasks" / include, folder / "tasks")
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
