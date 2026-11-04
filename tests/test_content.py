"""Validate content-operation boundaries and actual command rendering."""

import importlib.util
from pathlib import Path
import unittest
import yaml
from ansible.errors import AnsibleFilterError
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "content_filters", ROOT / "filter_plugins/content.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ContentBoundaries(unittest.TestCase):
    def test_unique_resource_required(self):
        for rows in ([], [{}, {}], None):
            with self.assertRaises(AnsibleFilterError):
                m.one(rows)
        self.assertEqual(m.one([{"id": 2}])["id"], 2)

    def test_foreign_objects_are_refused(self):
        for row in ({"description": None}, {"description": "Someone else"}, {}):
            with self.assertRaises(AnsibleFilterError):
                m.owned([row], "owner")
        self.assertEqual(
            m.owned([{"description": "owner"}], "owner"), [{"description": "owner"}]
        )

    def test_only_exact_repository_labels(self):
        self.assertEqual(
            m.repo_options(["repo-b", "repo-a", "repo-a"]),
            ["--disablerepo=*", "--enablerepo=repo-a", "--enablerepo=repo-b"],
        )
        for labels in ([], ["*"], ["repo,other"], ["../bad"], ["repo --bad"]):
            with self.assertRaises(AnsibleFilterError):
                m.repo_options(labels)

    def test_task_payload_validation(self):
        tid = "01234567-0123-4567-89ab-0123456789ab"
        self.assertEqual(m.task_ids({"id": tid}), [tid])
        self.assertEqual(m.task_ids([{"id": tid}]), [tid])
        for response in ({}, [], [{"id": tid}, {}], {"id": "../../escape"}):
            with self.assertRaises(AnsibleFilterError):
                m.task_ids(response)

    def test_targeted_command_has_exact_advisory_arguments(self):
        plays = yaml.safe_load((ROOT / "patch_hosts.yml").read_text())
        task = next(x for x in plays[1]["tasks"] if x["name"].startswith("Patch only"))
        variables = {
            "ansible_facts": {"distribution_major_version": "7"},
            "sniper_patch_scope": "targeted",
            "hostvars": {
                "localhost": {
                    "sniper_repo_args": m.repo_options(["repo-a"]),
                    "sniper_resolved_ids": ["RHSA-2024:1234", "RHSA-2024:5678"],
                }
            },
        }
        rendered = Templar(loader=DataLoader(), variables=variables).template(
            task["ansible.builtin.command"]["argv"]
        )
        self.assertEqual(
            rendered,
            [
                "yum",
                "-y",
                "--disablerepo=*",
                "--enablerepo=repo-a",
                "upgrade-minimal",
                "--advisory=RHSA-2024:1234",
                "--advisory=RHSA-2024:5678",
            ],
        )
        variables["sniper_patch_scope"] = "full"
        variables["ansible_facts"]["distribution_major_version"] = "8"
        rendered = Templar(loader=DataLoader(), variables=variables).template(
            task["ansible.builtin.command"]["argv"]
        )
        self.assertEqual(
            rendered, ["dnf", "-y", "--disablerepo=*", "--enablerepo=repo-a", "upgrade"]
        )

    def test_incremental_request_cannot_patch_or_promote_hosts(self):
        plays = yaml.safe_load((ROOT / "create_minor_update.yml").read_text())
        block = next(x["block"] for x in plays[0]["tasks"] if "block" in x)
        creation = next(
            x["block"] for x in block if x.get("when") == "sniper_environment == 'test'"
        )
        request = next(
            x["ansible.builtin.uri"] for x in creation if "ansible.builtin.uri" in x
        )
        self.assertNotIn("update_hosts", request["body"])
        self.assertEqual(
            request["body"]["content_view_version_environments"][0]["environment_ids"],
            [],
        )
        self.assertFalse(request["body"]["propagate_all_composites"])
        self.assertEqual(request["follow_redirects"], "none")
        self.assertTrue(request["validate_certs"])

    def test_partial_prep_recovery_is_unambiguous(self):
        initial = {
            "version": "1.0",
            "description": "Initial demonstration baseline; cutoff=2023-12-01",
        }
        self.assertEqual(m.initial_baseline([initial])["version"], "1.0")
        for versions in (
            [],
            [initial, {"version": "2.0"}],
            [{"version": "1.0", "description": "foreign"}],
        ):
            with self.assertRaises(AnsibleFilterError):
                m.initial_baseline(versions)

    def test_production_minor_reuses_test_without_new_post(self):
        plays = yaml.safe_load((ROOT / "create_minor_update.yml").read_text())
        block = next(x["block"] for x in plays[0]["tasks"] if "block" in x)
        production = next(
            x["block"] for x in block if x.get("when") == "sniper_environment == 'prod'"
        )
        self.assertFalse(any("ansible.builtin.uri" in task for task in production))
        self.assertTrue(
            any(
                "sniper_new_version" in task.get("ansible.builtin.set_fact", {})
                for task in production
            )
        )

    def test_rpm_snapshot_format_contains_one_rpm_newline_escape(self):
        plays = yaml.safe_load((ROOT / "patch_hosts.yml").read_text())
        snapshots = [
            task
            for task in plays[1]["tasks"]
            if task["name"].startswith("Snapshot installed RPM")
        ]
        self.assertEqual(len(snapshots), 2)
        expected = "%{NAME}|%{EPOCHNUM}|%{VERSION}|%{RELEASE}|%{ARCH}" + chr(92) + "n"
        for task in snapshots:
            self.assertEqual(task["ansible.builtin.command"]["argv"][-1], expected)


if __name__ == "__main__":
    unittest.main()
