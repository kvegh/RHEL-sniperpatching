"""Exercise NEW exact-version promotion and failure diagnostics with local Ansible.

Only Satellite I/O is synthetic. Real playbook guards, input typing, context,
version comparison and final readback checks run without any network operation.
Reason and scope: ../docs/implementation.md#synthetic-test-modules
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

from track_paths import TRACK

ROOT = Path(__file__).resolve().parents[1] / "playbooks/new"
MODULES = ("resource_info", "content_view_version")


class SafeStringDumper(yaml.SafeDumper):
    """Match AWX's survey extra-vars writer, including explicit !unsafe scalars."""

    def represent_data(self, value):
        if isinstance(value, str):
            return self.represent_scalar("!unsafe", value)
        return super().represent_data(value)


MODULE = r'''
import json
import os
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
NAME = __MODULE__
spec = {key: {"type": "str"} for key in (
    "server_url", "username", "password", "ca_path", "organization", "resource", "search", "content_view", "version")}
spec["password"]["no_log"] = True
spec.update({"validate_certs": {"type": "bool"}, "full_details": {"type": "bool"},
             "params": {"type": "dict", "default": {}},
             "lifecycle_environments": {"type": "list", "elements": "str"},
             "force_promote": {"type": "bool", "default": False}})
m = AnsibleModule(argument_spec=spec)
p = m.params
path = Path(os.environ["SNIPER_PROMOTION_STATE"])
s = json.loads(path.read_text())
s["calls"].append({"module": NAME, "resource": p["resource"], "params": p["params"],
                   "version": p["version"], "force_promote": p["force_promote"]})
def done(**result):
    path.write_text(json.dumps(s))
    m.exit_json(**result)
if NAME == "resource_info":
    resource, params = p["resource"], p["params"]
    if resource == "organizations":
        rows = [{"id": 1}]
    elif resource == "content_views":
        rows = [{"id": 20, "description": "Managed by RHEL-sniperpatching.",
                 "repositories": [{"id": 7, "name": "Example RPMs"}]}]
    elif resource == "lifecycle_environments":
        is_test = "_Test" in p["search"]
        rows = [{"id": 30 if is_test else 31, "description": "Managed by RHEL-sniperpatching.",
                 "prior": {"id": 1 if is_test else (999 if s["wrong_prior"] else 30)}}]
    elif resource == "content_view_versions":
        if int(params["environment_id"]) == 30:
            rows = [{"id": 4, "version": s["test_version"]}]
        elif s["promoted"]:
            rows = [{"id": 4, "version": "9.9" if s["bad_readback"] else s["test_version"]}]
        else:
            rows = [{"id": 3, "version": "1.1"}]
    elif resource == "repositories":
        rows = [{"id": 7, "name": "Example RPMs", "content_label": "example-rpms",
                 "product": {"name": "Example Product"}}]
    else:
        m.fail_json(msg="Unexpected fixture resource")
    done(changed=False, resources=rows)
else:
    if p["force_promote"] or p["version"] != s["test_version"] or p["lifecycle_environments"] != ["RHEL-sniperpatching_Prod"]:
        m.fail_json(msg="Unexpected or forced promotion")
    s["promoted"] = True
    done(changed=True)
'''


@unittest.skipUnless(TRACK == "new", "NEW-only exact-version promotion")
class PromotionPlaybook(unittest.TestCase):
    def run_promotion(self, requested="2.0", test_version="2.0", wrong_prior=False,
                      bad_readback=False, unsafe_transport=False):
        with tempfile.TemporaryDirectory(prefix="sniper-promotion-") as directory:
            base = Path(directory)
            collection = base / "collections/ansible_collections/redhat/satellite"
            modules = collection / "plugins/modules"
            modules.mkdir(parents=True)
            (collection / "meta").mkdir()
            (collection / "meta/runtime.yml").write_text(yaml.safe_dump({
                "action_groups": {"satellite": list(MODULES)}
            }))
            for name in MODULES:
                (modules / (name + ".py")).write_text(MODULE.replace("__MODULE__", repr(name)))
            state = {"calls": [], "promoted": False, "test_version": test_version,
                     "wrong_prior": wrong_prior, "bad_readback": bad_readback}
            state_path = base / "state.json"
            state_path.write_text(json.dumps(state))
            variables = {
                "sniper_server_url": "https://satellite.example.test",
                "sniper_username": "fixture", "sniper_password": "fixture-only-password",
                "sniper_organization": "Example Organization",
                "sniper_test_host": "test-client.example.test", "sniper_prod_host": "prod-client.example.test",
                "sniper_environment": "prod", "sniper_version": requested,
                "ansible_python_interpreter": sys.executable,
            }
            var_path = base / "extravars"
            var_path.write_text(yaml.dump(variables, Dumper=SafeStringDumper, default_flow_style=False)
                                if unsafe_transport else json.dumps(variables))
            environment = dict(os.environ, ANSIBLE_COLLECTIONS_PATH=str(base / "collections"),
                               ANSIBLE_LOCAL_TEMP=str(base / "local"), ANSIBLE_REMOTE_TEMP=str(base / "remote"),
                               ANSIBLE_NOCOLOR="1", ANSIBLE_FORCE_COLOR="0", PYTHONDONTWRITEBYTECODE="1",
                               SNIPER_PROMOTION_STATE=str(state_path))
            environment.pop("ANSIBLE_COLLECTIONS_PATHS", None)
            result = subprocess.run(
                ["ansible-playbook", "-u", "root", "--forks=1", "-i", "localhost,", "promote_content_view.yml",
                 "-e", "@" + str(var_path)], cwd=ROOT, env=environment, text=True, capture_output=True, timeout=90)
            return result, json.loads(state_path.read_text())

    def assert_not_promoted(self, result, state):
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(state["promoted"])
        self.assertFalse(any(call["module"] == "content_view_version" for call in state["calls"]))

    def test_exact_version_strings_preserve_minor_digits_and_confirm_readback(self):
        for version in ("2.0", "2.10"):
            with self.subTest(version=version):
                result, state = self.run_promotion(requested=version, test_version=version)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                promotions = [call for call in state["calls"] if call["module"] == "content_view_version"]
                self.assertEqual(len(promotions), 1)
                self.assertEqual(promotions[0]["version"], version)
                self.assertFalse(promotions[0]["force_promote"])
                self.assertTrue(state["promoted"])

    def test_awx_unsafe_prefixed_strings_preserve_minor_digits(self):
        for version in ("2.0", "2.10"):
            with self.subTest(version=version):
                result, state = self.run_promotion(requested="v" + version, test_version=version,
                                                   unsafe_transport=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                promotions = [call for call in state["calls"] if call["module"] == "content_view_version"]
                self.assertEqual(len(promotions), 1)
                self.assertEqual(promotions[0]["version"], version)
                self.assertFalse(promotions[0]["force_promote"])

    def test_bare_unsafe_version_cannot_select_a_different_minor(self):
        result, state = self.run_promotion(requested="2.10", test_version="2.1", unsafe_transport=True)
        self.assert_not_promoted(result, state)
        output = result.stdout + result.stderr
        self.assertIn("Use v2.0", output)
        self.assertIn("requested_type=float", output)
        self.assertFalse(any(call["params"].get("environment_id") == 30 for call in state["calls"]))

    def test_wrong_version_fails_before_promotion_with_bounded_diagnostics(self):
        for requested, unsafe_transport in (("2.10", False), ("v2.10", True)):
            with self.subTest(unsafe_transport=unsafe_transport):
                result, state = self.run_promotion(requested=requested, unsafe_transport=unsafe_transport)
                self.assert_not_promoted(result, state)
                output = result.stdout + result.stderr
                self.assertIn("requested_type=str", output)
                self.assertIn("requested_length=" + str(len(requested)), output)
                self.assertIn("normalized_type=str", output)
                self.assertIn("normalized_length=4", output)
                self.assertIn("test_type=str", output)
                self.assertIn("test_length=3", output)
                self.assertIn("version_equal=False", output)
                self.assertIn("path_equal=True", output)
                self.assertNotIn("requested_value", output)

    def test_wrong_predecessor_remains_blocked(self):
        for requested, unsafe_transport in (("2.0", False), ("v2.0", True)):
            with self.subTest(unsafe_transport=unsafe_transport):
                result, state = self.run_promotion(requested=requested, wrong_prior=True,
                                                   unsafe_transport=unsafe_transport)
                self.assert_not_promoted(result, state)
                output = result.stdout + result.stderr
                self.assertIn("version_equal=True", output)
                self.assertIn("path_equal=False", output)

    def test_bool_list_and_numeric_versions_never_promote(self):
        marker = "synthetic-private-version-marker"
        for value, test_version in ((True, "2.0"), ([marker], "2.0"), (2.0, "2.0"), (2.1, "2.10")):
            with self.subTest(input_type=type(value).__name__, test_version=test_version):
                result, state = self.run_promotion(requested=value, test_version=test_version)
                self.assert_not_promoted(result, state)
                output = result.stdout + result.stderr
                self.assertNotIn(marker, output)
                if isinstance(value, float):
                    self.assertIn("requested_type=float", output)
                    self.assertIn("requested_length=unavailable", output)
                    self.assertIn("Use v2.0", output)

    def test_final_readback_must_still_match_exact_requested_version(self):
        result, state = self.run_promotion(requested="v2.0", bad_readback=True, unsafe_transport=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(state["promoted"])
        self.assertIn("Confirm production serves the selected version", result.stdout)


if __name__ == "__main__":
    unittest.main()
