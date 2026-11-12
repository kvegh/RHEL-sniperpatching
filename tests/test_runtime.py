"""Catch module interface differences that syntax checks cannot detect."""
# Reason and test scope: ../docs/implementation.md#source-and-caller-inventory

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime_probe", ROOT / "files/runtime_probe.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RuntimeArguments(unittest.TestCase):
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
