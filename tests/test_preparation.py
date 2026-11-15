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

from track_paths import TRACK, TRACK_ROOT

ROOT = TRACK_ROOT
TEST = "RHEL-sniperpatching_Test"
PROD = "RHEL-sniperpatching_Prod"
NEW = TRACK == "new"
CATALOG = json.loads((ROOT.parents[1] / "docs/rhel94-cve-candidates.json").read_text())
CUTOFF = "2024-04-30" if NEW else "2025-02-28"
ADVISORIES = [dict(errata_id=row["advisory"], issued=row["fix_date"])
              for row in CATALOG["candidates"]] if NEW else [
    {"errata_id": "RHSA-2025:1234", "issued": "2025-03-01"},
    {"errata_id": "RHSA-2025:1235", "issued": "2025-05-01"},
]
ORIGINALS = list({json.dumps(row["baseline_package"], sort_keys=True): row["baseline_package"]
                  for row in CATALOG["candidates"]}.values())
FIXED = [dict(row["baseline_package"],
              version=row["fixed_package_evr"].rsplit("-", 1)[0],
              release=row["fixed_package_evr"].rsplit("-", 1)[1])
         for row in CATALOG["candidates"]]
FIRST = ADVISORIES[0]["errata_id"]
SECOND = ADVISORIES[1]["errata_id"]
MODULES = (
    "resource_info", "lifecycle_environment", "content_view",
    "content_view_filter", "content_view_filter_rule", "content_view_version", "host",
)
MODULE = r"""
import json, os
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
NAME = __MODULE__
SPLIT_FILTER_RULES = __SPLIT_FILTER_RULES__
spec = {}
for key in ("server_url", "username", "password", "organization", "name", "search",
            "resource", "prior", "description", "state", "filter_type", "filter_state", "rule_state",
            "content_view", "content_view_filter", "end_date", "date_type",
            "version", "lifecycle_environment"):
    spec[key] = {"type": "str"}
if SPLIT_FILTER_RULES:
    spec.pop("rule_state")
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
if NAME == "content_view_filter" and p["filter_type"] == "rpm" and p["filter_state"] == "present" and not SPLIT_FILTER_RULES and p.get("rule_state") != "absent":
    module.fail_json(msg="The original-only RPM filter must not create a package-name rule")
state["calls"].append({
    "module": NAME, "resource": p.get("resource"), "params": p["params"],
    "phase": state.get("phase", "initial"), "search": p.get("search"),
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
advisories = __ADVISORIES__
originals = __ORIGINALS__
fixed = __FIXED__
if NAME == "resource_info":
    resource = p["resource"]
    params = p["params"]
    if resource == "organizations":
        rows = [{"id": 1, "name": "Example Organization"}]
    elif resource == "hosts":
        if not state.get("registered", True):
            module.fail_json(msg="Unregistered fixture: content-only phase must not read hosts")
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
    elif resource == "packages":
        if params.get("packages_restrict_latest") is not True:
            module.fail_json(msg="Published baseline must inspect native latest-only packages")
        if "filename" in p["search"] or "version" in p["search"] or "release" in p["search"]:
            module.fail_json(msg="Latest query cannot hide later builds behind an exact original search")
        rows = originals[1:] if state.get("missing_original") else list(originals)
        # Underlying CV still has GA plus the later RPM; emulate native name/arch latest selection.
        contamination = None
        if state.get("fixed_contaminated"):
            contamination = fixed[0]
        if state.get("newer_contaminated"):
            contamination = dict(next(row for row in originals if row["name"] == "kernel"),
                                 release="427.42.1.el9_4")
        if contamination:
            rows = [row for row in rows if (row["name"], row["arch"]) !=
                    (contamination["name"], contamination["arch"])] + [contamination]
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
    def run_prep(self, scenario="fresh", cutoff=None, contaminated=False,
                 content_only=None, follow_with_hosts=False, fixed_contaminated=False,
                 missing_original=False, newer_contaminated=False):
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
                    MODULE.replace("__MODULE__", repr(name)).replace(
                        "__SPLIT_FILTER_RULES__", repr(NEW)).replace(
                        "__ADVISORIES__", repr(ADVISORIES)).replace(
                        "__ORIGINALS__", repr(ORIGINALS)).replace(
                        "__FIXED__", repr(FIXED))
                )
            state = {"view": False, "environments": [], "versions": [],
                     "serving": {}, "placements": {}, "calls": [],
                     "contaminated": contaminated, "fixed_contaminated": fixed_contaminated,
                     "missing_original": missing_original, "newer_contaminated": newer_contaminated,
                     "registered": not NEW or scenario == "established" or content_only is False}
            if scenario != "fresh":
                state["view"] = True
                state["environments"] = [TEST, PROD]
                state["versions"] = [{
                    "id": 40, "version": "1.0",
                    "description": "Initial demonstration baseline; cutoff=" + CUTOFF,
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
                "sniper_baseline_end_date": (CUTOFF if NEW else "") if cutoff is None else cutoff,
                "sniper_prepare_content_only": (NEW and scenario != "established") if content_only is None else content_only,
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
            if follow_with_hosts and result.returncode == 0:
                after = json.loads(state_file.read_text())
                after.update(registered=True, phase="registered")
                state_file.write_text(json.dumps(after))
                variables["sniper_prepare_content_only"] = False
                variables_file.write_text(json.dumps(variables))
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
                         "Initial demonstration baseline; cutoff=" + CUTOFF)
        self.assertEqual(state["serving"], {TEST: 40, PROD: 40})
        calls = state["calls"]
        original = [c for c in calls if c["module"] == "content_view_filter" and c["filter_type"] == "rpm"]
        self.assertEqual(len(original), 1)
        self.assertTrue(original[0]["original_packages"])
        self.assertEqual(original[0]["rule_state"], None if TRACK == "new" else "absent")
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
        if NEW:
            self.assertEqual(assignments, [])
            self.assertFalse(any(c["resource"] in {"hosts", "host_errata"} for c in calls))
        else:
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


    @unittest.skipUnless(NEW, "NEW-only direct registration sequence")
    def test_registered_phase_reuses_the_served_baseline_without_publication(self):
        result, state = self.run_prep(follow_with_hosts=True)
        self.assert_success(result)
        self.assertEqual(state["placements"], {
            "test-client.example.test": TEST, "prod-client.example.test": PROD,
        })
        initial = [c for c in state["calls"] if c["phase"] == "initial"]
        later = [c for c in state["calls"] if c["phase"] == "registered"]
        self.assertFalse(any(c["resource"] in {"hosts", "host_errata"} or
                             c["module"] == "host" for c in initial))
        self.assertTrue(any(c["module"] == "host" for c in later))
        self.assertFalse(any(c["module"] in {"content_view_filter", "content_view_filter_rule",
                                             "content_view_version"} for c in later))
        self.assertEqual(len(state["versions"]), 1)

    @unittest.skipUnless(NEW, "NEW-only original-build protection")
    def test_fixed_rpm_without_erratum_is_refused_before_promotion(self):
        result, state = self.run_prep(fixed_contaminated=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(state["versions"]), 1)
        self.assertEqual(state["serving"], {})
        self.assertEqual(state["placements"], {})

    @unittest.skipUnless(NEW, "NEW-only later-build protection")
    def test_newer_fixed_build_cannot_hide_beside_original_ga(self):
        result, state = self.run_prep(newer_contaminated=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(state["versions"]), 1)
        self.assertEqual(state["serving"], {})
        self.assertEqual(state["placements"], {})
        queries = [c for c in state["calls"] if c["resource"] == "packages"]
        self.assertTrue(queries)
        self.assertTrue(all(c["params"]["packages_restrict_latest"] is True for c in queries))
        self.assertIn("original affected build", result.stdout + result.stderr)

    @unittest.skipUnless(NEW, "NEW-only original-build protection")
    def test_missing_original_build_is_refused_before_promotion(self):
        result, state = self.run_prep(missing_original=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(state["serving"], {})

    @unittest.skipUnless(NEW, "NEW-only established history protection")
    def test_content_only_cannot_replace_established_versions(self):
        result, state = self.run_prep(scenario="established", content_only=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(state["serving"], {TEST: 41, PROD: 41})
        self.assertEqual(len(state["versions"]), 2)
        self.assertFalse(any(c["module"] in {"content_view_filter", "content_view_filter_rule",
                                           "content_view_version", "host"} for c in state["calls"]))

    @unittest.skipUnless(NEW, "NEW-only content-first prerequisite")
    def test_registered_phase_cannot_publish_a_missing_baseline(self):
        result, state = self.run_prep(content_only=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(state["versions"], [])
        self.assertFalse(any(c["module"] == "content_view_version" for c in state["calls"]))


if __name__ == "__main__":
    unittest.main()
