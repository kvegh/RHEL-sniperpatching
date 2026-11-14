"""Catch module interface differences that syntax checks cannot detect."""
# Reason and test scope: ../docs/implementation.md#source-and-caller-inventory

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import os
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
                            loader=DataLoader(), variables={"omit": "__omit_ca__"}
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
