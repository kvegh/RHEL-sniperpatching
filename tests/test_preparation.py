"""Run the real prep playbook against a synthetic, local Satellite module fixture."""
# Reason and test scope: ../docs/implementation.md#synthetic-test-modules


import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TEST = "RHEL-sniperpatching_Test"
PROD = "RHEL-sniperpatching_Prod"
FIRST = "RHSA-2025:1234"
SECOND = "RHSA-2025:1235"
MODULES = (
    "resource_info", "lifecycle_environment", "content_view",
    "content_view_filter", "content_view_filter_rule", "content_view_version", "host",
)
MODULE = r"""
import json, os
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
NAME = __MODULE__
spec = {}
for key in ("server_url", "username", "password", "organization", "name", "search",
            "resource", "prior", "description", "state", "filter_type", "filter_state", "rule_state",
            "content_view", "content_view_filter", "end_date", "date_type",
            "version", "lifecycle_environment"):
    spec[key] = {"type": "str"}
spec["password"]["no_log"] = True
for key in ("validate_certs", "full_details", "solve_dependencies", "inclusion", "original_packages"):
    spec[key] = {"type": "bool"}
for key in ("repositories", "types", "lifecycle_environments"):
    spec[key] = {"type": "list", "elements": "raw"}
spec["params"] = {"type": "dict", "default": {}}
module = AnsibleModule(argument_spec=spec)
p = module.params
path = Path(os.environ["SNIPER_PREP_TEST_STATE"])
state = json.loads(path.read_text())
if NAME == "content_view_filter" and p["filter_type"] == "erratum" and p["original_packages"] is not None:
    module.fail_json(msg="setting original_packages not supported for Katello::ContentViewErratumFilter")
if NAME == "content_view_filter" and p["filter_type"] == "rpm" and p["filter_state"] == "present" and p["rule_state"] != "absent":
    module.fail_json(msg="The original-only RPM filter must not create a package-name rule")
state["calls"].append({
    "module": NAME, "resource": p.get("resource"), "params": p["params"],
    "filter_type": p.get("filter_type"), "original_packages": p.get("original_packages"),
    "rule_state": p.get("rule_state"),
    "version": p.get("version"), "destinations": p.get("lifecycle_environments"),
    "end_date": p.get("end_date"),
})
def done(**result):
    path.write_text(json.dumps(state))
    module.exit_json(**result)
owner = "Managed by RHEL-sniperpatching."
test = "RHEL-sniperpatching_Test"
prod = "RHEL-sniperpatching_Prod"
hosts = {"test-client.example.test": 11, "prod-client.example.test": 12}
advisories = [
    {"errata_id": "RHSA-2025:1234", "issued": "2025-03-01"},
    {"errata_id": "RHSA-2025:1235", "issued": "2025-05-01"},
]
if NAME == "resource_info":
    resource = p["resource"]
    params = p["params"]
    if resource == "organizations":
        rows = [{"id": 1, "name": "Example Organization"}]
    elif resource == "hosts":
        host = next(name for name in hosts if name in p["search"])
        rows = [{"id": hosts[host], "name": host, "organization_id": 1,
                 "operatingsystem_name": "RedHat 7.9",
                 "content_facet_attributes": {
                     "content_view": {"id": 20},
                     "lifecycle_environment": {"name": state["placements"].get(host, "Old_Dev")},
                 }}]
    elif resource == "lifecycle_environments":
        name = next(name for name in (test, prod) if name in p["search"])
        rows = [{"id": 31 if name == test else 32, "name": name,
                 "description": owner}] if name in state["environments"] else []
    elif resource == "content_views":
        rows = [{"id": 20, "name": "RHEL-sniperpatching", "description": owner,
                 "repositories": [{"id": 7, "name": "Example RPMs"}]}] if state["view"] else []
    elif resource == "content_view_versions":
        if "environment_id" in params:
            name = test if int(params["environment_id"]) == 31 else prod
            ident = state["serving"].get(name)
            rows = [v for v in state["versions"] if v["id"] == ident]
        else:
            rows = state["versions"]
    elif resource == "host_errata":
        rows = advisories[1:] if int(params["host_id"]) == 11 else advisories
    elif resource == "errata":
        if "repository_id" in params:
            rows = advisories
        else:
            rows = [advisories[0]] if state["contaminated"] else []
    else:
        module.fail_json(msg="Unexpected resource " + resource)
    done(changed=False, resources=rows)
elif NAME == "lifecycle_environment":
    if p["name"] not in state["environments"]:
        state["environments"].append(p["name"])
elif NAME == "content_view":
    state["view"] = True
elif NAME == "content_view_version":
    if p["version"] is None:
        state["versions"].append({"id": 40, "version": "1.0", "description": p["description"]})
    else:
        version = next(v for v in state["versions"] if v["version"] == p["version"])
        for name in p["lifecycle_environments"]:
            state["serving"][name] = version["id"]
elif NAME == "host":
    state["placements"][p["name"]] = p["lifecycle_environment"]
done(changed=True)
"""


class PreparationPlaybook(unittest.TestCase):
    def run_prep(self, scenario="fresh", cutoff="", contaminated=False):
        with tempfile.TemporaryDirectory(prefix="sniper-prep-test-") as directory:
            base = Path(directory)
            collection = base / "collections/ansible_collections/redhat/satellite"
            modules = collection / "plugins/modules"
            modules.mkdir(parents=True)
            meta = collection / "meta"
            meta.mkdir()
            (meta / "runtime.yml").write_text(yaml.safe_dump({
                "action_groups": {"satellite": list(MODULES)}
            }))
            for name in MODULES:
                (modules / (name + ".py")).write_text(
                    MODULE.replace("__MODULE__", repr(name))
                )
            state = {"view": False, "environments": [], "versions": [],
                     "serving": {}, "placements": {}, "calls": [],
                     "contaminated": contaminated}
            if scenario != "fresh":
                state["view"] = True
                state["environments"] = [TEST, PROD]
                state["versions"] = [{
                    "id": 40, "version": "1.0",
                    "description": "Initial demonstration baseline; cutoff=2025-02-28",
                }]
            if scenario == "established":
                state["versions"].append({"id": 41, "version": "2.0",
                                          "description": "Full update"})
                state["serving"] = {TEST: 41, PROD: 41}
                state["placements"] = {
                    "test-client.example.test": TEST,
                    "prod-client.example.test": PROD,
                }
            state_file = base / "state.json"
            state_file.write_text(json.dumps(state))
            variables = {
                "sniper_server_url": "https://satellite.example.test",
                "sniper_username": "example", "sniper_password": "example",
                "sniper_organization": "Example Organization",
                "sniper_test_host": "test-client.example.test",
                "sniper_prod_host": "prod-client.example.test",
                "sniper_repositories": [{"name": "Example RPMs", "product": "Example"}],
                "sniper_baseline_end_date": cutoff,
                "ansible_python_interpreter": sys.executable,
            }
            variables_file = base / "vars.json"
            variables_file.write_text(json.dumps(variables))
            env = dict(os.environ,
                       ANSIBLE_COLLECTIONS_PATH=str(base / "collections"),
                       ANSIBLE_LOCAL_TEMP=str(base / "local"),
                       ANSIBLE_NOCOLOR="1", ANSIBLE_FORCE_COLOR="0",
                       SNIPER_PREP_TEST_STATE=str(state_file),
                       PYTHONDONTWRITEBYTECODE="1")
            env.pop("ANSIBLE_COLLECTIONS_PATHS", None)
            result = subprocess.run(
                ["ansible-playbook", "-i", "localhost,", "prepare_demo.yml",
                 "-e", "@" + str(variables_file)],
                cwd=ROOT, env=env, text=True, capture_output=True, timeout=180,
            )
            return result, json.loads(state_file.read_text())

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-8000:])

    def test_fresh_baseline_is_verified_before_promotion_and_host_assignment(self):
        result, state = self.run_prep()
        self.assert_success(result)
        self.assertEqual(state["versions"][0]["description"],
                         "Initial demonstration baseline; cutoff=2025-02-28")
        self.assertEqual(state["serving"], {TEST: 40, PROD: 40})
        calls = state["calls"]
        original = [c for c in calls if c["module"] == "content_view_filter" and c["filter_type"] == "rpm"]
        self.assertEqual(len(original), 1)
        self.assertTrue(original[0]["original_packages"])
        self.assertEqual(original[0]["rule_state"], "absent")
        publication = next(i for i, c in enumerate(calls)
                           if c["module"] == "content_view_version")
        verification = next(i for i, c in enumerate(calls)
                            if c["resource"] == "errata"
                            and "content_view_version_id" in c["params"])
        promotions = [i for i, c in enumerate(calls)
                      if c["module"] == "content_view_version" and c["version"]]
        assignments = [i for i, c in enumerate(calls) if c["module"] == "host"]
        self.assertLess(publication, verification)
        self.assertLess(verification, min(promotions))
        self.assertLess(max(promotions), min(assignments))

    def test_contaminated_baseline_stays_unpromoted_and_hosts_untouched(self):
        result, state = self.run_prep(contaminated=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(state["versions"]), 1)
        self.assertEqual(state["serving"], {})
        self.assertEqual(state["placements"], {})
        self.assertFalse(any(c["module"] == "host" for c in state["calls"]))

    def test_unsafe_explicit_cutoff_cannot_publish_a_baseline(self):
        result, state = self.run_prep(cutoff="2025-03-01")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(state["versions"], [])
        self.assertEqual(state["serving"], {})
        self.assertEqual(state["placements"], {})

    def test_interrupted_publication_is_reverified_before_recovery(self):
        result, state = self.run_prep(scenario="recovery")
        self.assert_success(result)
        self.assertEqual(len(state["versions"]), 1)
        self.assertEqual(state["serving"], {TEST: 40, PROD: 40})
        publications = [c for c in state["calls"]
                        if c["module"] == "content_view_version" and not c["version"]]
        self.assertEqual(publications, [])

    def test_established_newer_versions_survive_preparation_retry(self):
        result, state = self.run_prep(scenario="established")
        self.assert_success(result)
        self.assertEqual(state["serving"], {TEST: 41, PROD: 41})
        self.assertEqual(len(state["versions"]), 2)
        prohibited = {"content_view_filter", "content_view_filter_rule",
                      "content_view_version"}
        self.assertFalse(any(c["module"] in prohibited or c["resource"] == "host_errata"
                             for c in state["calls"]))


if __name__ == "__main__":
    unittest.main()
