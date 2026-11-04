"""Exercise the real publication playbook with bounded local module fixtures."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml
from ansible.errors import AnsibleFilterError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cutoff_content", ROOT / "filter_plugins/content.py")
content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content)
MODULES = ("resource_info", "repository_sync", "content_view_filter",
           "content_view_filter_rule", "content_view_version")
MODULE = r"""
import json, os
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
name = __MODULE__
spec = {}
for key in ("server_url", "username", "password", "organization", "name", "search",
            "resource", "description", "state", "filter_type", "filter_state",
            "content_view", "content_view_filter", "end_date", "date_type",
            "version", "product", "repository"):
    spec[key] = {"type": "str"}
spec["password"]["no_log"] = True
for key in ("validate_certs", "full_details", "inclusion", "original_packages"):
    spec[key] = {"type": "bool"}
for key in ("types", "lifecycle_environments"):
    spec[key] = {"type": "list", "elements": "raw"}
spec["params"] = {"type": "dict", "default": {}}
m = AnsibleModule(argument_spec=spec)
p = m.params
path = Path(os.environ["SNIPER_FULL_TEST_STATE"])
s = json.loads(path.read_text())
s["calls"].append({"module": name, "resource": p.get("resource"),
                   "params": p["params"], "version": p.get("version"),
                   "destinations": p.get("lifecycle_environments"),
                   "filter_state": p.get("filter_state"), "end_date": p.get("end_date")})
owner = "Managed by RHEL-sniperpatching."
first = {"errata_id": "RHSA-2025:1234", "issued": "2025-03-01"}
later = {"errata_id": "RHSA-2025:5678", "issued": "2025-05-01"}
def done(**result):
    path.write_text(json.dumps(s))
    m.exit_json(**result)
if name == "resource_info":
    resource, params = p["resource"], p["params"]
    if resource == "organizations":
        rows = [{"id": 1}]
    elif resource == "content_views":
        rows = [{"id": 20, "description": owner, "repositories": [{"id": 7, "name": "Example RPMs"}]}]
    elif resource == "lifecycle_environments":
        rows = [{"id": 31, "description": owner}]
    elif resource == "content_view_versions":
        rows = [s["candidate"]] if s["promoted"] else [{"id": 40, "version": "1.1", "major": 1, "minor": 1}]
    elif resource == "repositories":
        rows = [{"id": 7, "name": "Example RPMs", "content_label": "example-rpms",
                 "product": {"name": "Example Product"}}]
    elif resource == "content_view_filters":
        rows = [{"name": "RHEL-sniperpatching_baseline_cutoff"}]
    elif resource == "errata":
        if int(params["content_view_version_id"]) == 40:
            rows = [first]
        elif s["lost"]:
            rows = []
        elif s["contaminated"] or s["cutoff"] == "":
            rows = [first, later]
        else:
            rows = [first]
    else:
        m.fail_json(msg="Unexpected resource " + resource)
    done(changed=False, resources=rows)
elif name == "content_view_filter_rule":
    s["cutoff"] = p["end_date"]
elif name == "content_view_filter" and p["filter_state"] == "absent":
    s["cutoff"] = ""
elif name == "content_view_version":
    if p["version"] is None:
        s["candidate"] = {"id": 41, "content_view_id": 20, "version": "2.0", "major": 2, "minor": 0}
        done(changed=True, entity={"content_view_versions": [s["candidate"]]})
    else:
        if p["version"] != s["candidate"]["version"] or p["lifecycle_environments"] != ["RHEL-sniperpatching_Test"]:
            m.fail_json(msg="Unexpected promotion")
        s["promoted"] = True
done(changed=True)
"""


class CutoffValidation(unittest.TestCase):
    def test_cutoff_uses_issue_date_inclusive_and_validates_calendar(self):
        rows = [{"errata_id": "RHSA-2024:1234", "issued": "2024-02-29T00:00:00Z"}]
        self.assertEqual(content.update_cutoff("2024-02-29", rows), "2024-02-29")
        for value in ("2023-02-29", "2024-02-30", "2024-2-29", "latest", None):
            with self.subTest(value=value), self.assertRaises(AnsibleFilterError):
                content.update_cutoff(value, rows)

    def test_later_or_unknown_issue_date_fails_closed(self):
        for row in ({"errata_id": "RHSA-2025:1234", "issued": "2025-05-01"},
                    {"errata_id": "RHSA-2025:1234", "updated": "2025-03-01"},
                    {"issued": "2025-03-01"}, None):
            with self.subTest(row=row), self.assertRaises(AnsibleFilterError):
                content.verify_cutoff([row], "2025-04-01")

    def test_empty_value_preserves_explicit_latest_mode(self):
        self.assertEqual(content.update_cutoff("", []), "")


class FullPublicationPlaybook(unittest.TestCase):
    def run_publication(self, cutoff="2025-04-01", contaminated=False, lost=False):
        with tempfile.TemporaryDirectory(prefix="sniper-full-test-") as directory:
            base = Path(directory)
            coll = base / "collections/ansible_collections/redhat/satellite"
            (coll / "plugins/modules").mkdir(parents=True)
            (coll / "meta").mkdir()
            (coll / "meta/runtime.yml").write_text(yaml.safe_dump({
                "action_groups": {"satellite": list(MODULES)}
            }))
            for name in MODULES:
                (coll / ("plugins/modules/" + name + ".py")).write_text(
                    MODULE.replace("__MODULE__", repr(name)))
            state = {"calls": [], "promoted": False, "candidate": None,
                     "cutoff": "2025-02-28", "contaminated": contaminated, "lost": lost}
            state_path = base / "state.json"
            state_path.write_text(json.dumps(state))
            variables = {
                "sniper_server_url": "https://satellite.example.test",
                "sniper_username": "example", "sniper_password": "fixture-only-password",
                "sniper_organization": "Example Organization",
                "sniper_test_host": "test-client.example.test",
                "sniper_prod_host": "prod-client.example.test",
                "sniper_environment": "test", "sniper_update_end_date": cutoff,
                "ansible_python_interpreter": sys.executable,
            }
            var_path = base / "vars.json"
            var_path.write_text(json.dumps(variables))
            env = dict(os.environ, ANSIBLE_COLLECTIONS_PATH=str(base / "collections"),
                       ANSIBLE_LOCAL_TEMP=str(base / "local"), ANSIBLE_NOCOLOR="1",
                       ANSIBLE_FORCE_COLOR="0", SNIPER_FULL_TEST_STATE=str(state_path),
                       PYTHONDONTWRITEBYTECODE="1")
            env.pop("ANSIBLE_COLLECTIONS_PATHS", None)
            result = subprocess.run(
                ["ansible-playbook", "-i", "localhost,", "publish_full_update.yml",
                 "-e", "@" + str(var_path)],
                cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
            return result, json.loads(state_path.read_text())

    def test_bounded_candidate_verified_before_exact_test_promotion(self):
        result, state = self.run_publication()
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-7000:])
        self.assertTrue(state["promoted"])
        self.assertEqual(state["cutoff"], "2025-04-01")
        calls = state["calls"]
        verification = next(i for i, c in enumerate(calls)
                            if c["resource"] == "errata"
                            and str(c["params"].get("content_view_version_id")) == "41")
        promotion = next(i for i, c in enumerate(calls) if c["version"] == "2.0")
        self.assertLess(verification, promotion)
        self.assertFalse(any(c["filter_state"] == "absent" for c in calls))

    def test_content_after_cutoff_stays_in_library(self):
        result, state = self.run_publication(contaminated=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNotNone(state["candidate"])
        self.assertFalse(state["promoted"])

    def test_cutoff_that_would_lose_existing_fix_cannot_mutate(self):
        result, state = self.run_publication(cutoff="2025-02-28")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(c["module"] != "resource_info" for c in state["calls"]))

    def test_missing_previously_serving_advisory_stays_in_library(self):
        result, state = self.run_publication(lost=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNotNone(state["candidate"])
        self.assertFalse(state["promoted"])

    def test_latest_mode_removes_only_own_filter_and_verifies_before_promotion(self):
        result, state = self.run_publication(cutoff="")
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-7000:])
        self.assertTrue(state["promoted"])
        self.assertTrue(any(c["filter_state"] == "absent" for c in state["calls"]))
        self.assertFalse(any(c["module"] == "content_view_filter_rule" for c in state["calls"]))


if __name__ == "__main__":
    unittest.main()
