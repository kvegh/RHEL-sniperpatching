"""Catch module interface differences that syntax checks cannot detect."""
# Reason and test scope: ../docs/implementation.md#source-and-caller-inventory

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import os
import json
import subprocess
import tempfile
import yaml
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.loader import init_plugin_loader
from ansible.template import Templar

try:
    from ansible.template import trust_as_template
except ImportError:
    def trust_as_template(value):
        return value

from track_paths import TRACK, TRACK_ROOT

ROOT = TRACK_ROOT
spec = importlib.util.spec_from_file_location(
    "runtime_probe", ROOT / "files/runtime_probe.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RuntimeArguments(unittest.TestCase):
    @unittest.skipUnless(TRACK == "new", "Job-local CA support belongs to NEW.")
    def test_public_ca_file_is_private_and_cleaned_after_success_or_failure(self):
        with tempfile.TemporaryDirectory(prefix="sniper-ca-test-") as directory:
            root = Path(directory)
            for provided, fail in ((False, False), (True, False), (True, True)):
                report = root / "report.json"
                tasks = [{"ansible.builtin.include_tasks": str(ROOT / "tasks/api_ca.yml")}]
                if provided:
                    tasks.extend([
                        {"ansible.builtin.stat": {"path": "{{ sniper_satellite_ca_path }}"}, "register": "ca_stat"},
                        {"ansible.builtin.slurp": {"src": "{{ sniper_satellite_ca_path }}"}, "register": "ca_content"},
                        {"ansible.builtin.stat": {"path": "{{ sniper_satellite_ca_path | dirname }}"}, "register": "ca_dir_stat"},
                        {"ansible.builtin.assert": {"that": [
                            "ca_stat.stat.mode == '0600'",
                            "ca_content.content | b64decode == sniper_satellite_ca_pem",
                            "ca_dir_stat.stat.mode == '0700'",
                            "ca_dir_stat.stat.isdir",
                        ]}},
                        {"ansible.builtin.copy": {
                            "content": "{{ {'path': sniper_satellite_ca_path} | to_json }}",
                            "dest": str(report), "mode": "0600",
                        }},
                    ])
                else:
                    tasks.append({"ansible.builtin.assert": {"that": [
                        "sniper_satellite_job_ca.skipped | default(false)",
                        "sniper_satellite_job_ca.path is not defined",
                    ]}})
                if fail:
                    tasks.append({"ansible.builtin.fail": {"msg": "Expected fixture failure after CA preparation"}})
                runtime = yaml.safe_load((ROOT / "check_runtime.yml").read_text())[0]
                handlers = runtime["handlers"]
                for handler in handlers:
                    handler["ansible.builtin.include_tasks"] = str(ROOT / handler["ansible.builtin.include_tasks"])
                play = [{"name": "Exercise native public CA lifetime", "hosts": "localhost", "connection": "local",
                         "gather_facts": False, "vars": {"sniper_satellite_ca_pem": "synthetic-public-ca\n" if provided else ""},
                         "force_handlers": runtime["force_handlers"], "handlers": handlers, "tasks": tasks}]
                fixture = root / "play.yml"
                fixture.write_text(yaml.safe_dump(play, sort_keys=False))
                result = subprocess.run(["ansible-playbook", "-i", "localhost,", str(fixture)],
                                        capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 2 if fail else 0, result.stdout + result.stderr)
                if provided:
                    self.assertFalse(Path(json.loads(report.read_text())["path"]).exists())

    @unittest.skipUnless(TRACK == "new", "Job-local CA support belongs to NEW.")
    def test_satellite_uri_trust_uses_provided_ca_and_preserves_default_trust(self):
        init_plugin_loader()
        def uri_arguments(value):
            if isinstance(value, dict):
                if "ansible.builtin.uri" in value:
                    yield value["ansible.builtin.uri"]
                for entry in value.values():
                    yield from uri_arguments(entry)
            elif isinstance(value, list):
                for entry in value:
                    yield from uri_arguments(entry)

        for name in ("create_minor_update.yml", "tasks/runtime_satellite.yml"):
            calls = list(uri_arguments(yaml.safe_load((ROOT / name).read_text())))
            self.assertEqual(len(calls), 1)
            call = calls[0]
            self.assertTrue(call["validate_certs"])
            self.assertEqual(call["follow_redirects"], "none")
            for value in ("", "/runner/env/synthetic-satellite-ca.pem"):
                with self.subTest(file=name, ca_provided=bool(value)):
                    with patch.dict(os.environ, {"SATELLITE_CA_PATH": value}):
                        actual = Templar(
                            loader=DataLoader(), variables={
                                "omit": "__omit_ca__",
                                "sniper_satellite_ca_path": trust_as_template(
                                    yaml.safe_load((ROOT / "vars/main.yml").read_text())["sniper_satellite_ca_path"]
                                ),
                            }
                        ).template(trust_as_template(call["ca_path"]))
                    self.assertEqual(actual, value or "__omit_ca__")

    def test_unsupported_argument_in_nested_task_is_reported(self):
        docs = {"redhat.satellite.example": {"doc": {"options": {"filter_state": {}}}}}
        tasks = [{"block": [{"redhat.satellite.example": {"state": "absent"}}]}]
        self.assertEqual(
            m.check_arguments(tasks, docs, "stage.yml"),
            [
                {
                    "file": "stage.yml",
                    "module": "redhat.satellite.example",
                    "unsupported_arguments": ["state"],
                }
            ],
        )

    def test_documented_alias_is_accepted_and_builtins_are_ignored(self):
        docs = {
            "redhat.satellite.example": {
                "doc": {"options": {"name": {"aliases": ["label"]}}}
            }
        }
        tasks = [
            {"redhat.satellite.example": {"label": "demo"}},
            {"ansible.builtin.debug": {"msg": "demo"}},
        ]
        self.assertEqual(m.check_arguments(tasks, docs, "stage.yml"), [])


if __name__ == "__main__":
    unittest.main()
