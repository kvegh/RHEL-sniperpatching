"""Exercise minor creation/recovery and normal Library to Test promotion."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
A = "RHSA-2050:1000"
DESCRIPTION = "RHEL-sniperpatching requested " + A + " from 1.0"
MODULES = ("resource_info", "wait_for_task", "content_view_version", "fixture_incremental")
MODULE = r'''
import json, os
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
name = __MODULE__
spec = {key: {"type": "str"} for key in (
    "server_url", "username", "password", "organization", "name", "search",
    "resource", "content_view", "version", "task", "url", "method",
    "url_username", "url_password", "body_format", "follow_redirects")}
for key in ("password", "url_password"):
    spec[key]["no_log"] = True
for key in ("validate_certs", "full_details", "force_basic_auth", "use_netrc"):
    spec[key] = {"type": "bool"}
spec["force_promote"] = {"type": "bool", "default": False}
spec["timeout"] = {"type": "int"}
spec["status_code"] = {"type": "list", "elements": "int"}
spec["lifecycle_environments"] = {"type": "list", "elements": "str"}
for key in ("params", "body"):
    spec[key] = {"type": "dict", "default": {}}
m = AnsibleModule(argument_spec=spec)
p = m.params
path = Path(os.environ["SNIPER_MINOR_TEST_STATE"])
s = json.loads(path.read_text())
s["calls"].append({"module": name, "resource": p.get("resource"),
    "params": p["params"], "destinations": p.get("lifecycle_environments")})
owner = "Managed by RHEL-sniperpatching."
requested = "RHSA-2050:1000"
base_rpm = {"id": "base-rpm", "name": "base", "epoch": "0", "version": "1.0", "release": "1.el7", "arch": "x86_64"}
fixed_rpm = {"id": "fixed-rpm", "name": "demo", "epoch": "0", "version": "2.0", "release": "1.el7", "arch": "x86_64"}
old = {"id": 100, "errata_id": "RHSA-2049:9999", "type": "security"}
fix = {"id": 101, "errata_id": requested, "type": "security",
       "packages": [fixed_rpm], "cves": [], "reboot_suggested": False, "module_streams": []}
labels = {1: "Library", 31: "RHEL-sniperpatching_Test", 32: "RHEL-sniperpatching_Prod"}
def done(changed=False, **result):
    path.write_text(json.dumps(s))
    m.exit_json(changed=changed, **result)
def fail(message):
    path.write_text(json.dumps(s))
    m.fail_json(msg=message)
def version(ident, minor, description, environments, major=1):
    return {"id": ident, "content_view_id": 20, "major": major, "minor": minor,
        "version": "%s.%s" % (major, minor), "description": description,
        "environments": [{"id": eid, "name": labels[eid]} for eid in environments]}
if name == "fixture_incremental":
    body = p["body"]
    entries = body.get("content_view_version_environments", [])
    if (p["method"] != "POST" or not p["validate_certs"] or p["follow_redirects"] != "none"
            or p["use_netrc"] or "update_hosts" in body or body["propagate_all_composites"]
            or len(entries) != 1 or int(entries[0]["content_view_version_id"]) != 40
            or entries[0]["environment_ids"] != []
            or body["add_content"]["errata_ids"] != [requested]):
        fail("Unsafe incremental API request")
    s["uri_count"] += 1
    if "41" in s["versions"]:
        fail("An existing orphan must not cause another incremental request")
    s["versions"]["41"] = version(41, 1, body["description"], [])
    done(changed=True, status=202, json={"id": "01234567-0123-4567-89ab-0123456789ab"})
elif name == "wait_for_task":
    done(task={"state": "stopped", "result": "success"})
elif name == "resource_info":
    resource, params = p["resource"], p["params"]
    if resource == "organizations":
        rows = [{"id": 1}]
    elif resource == "content_views":
        rows = [{"id": 20, "description": owner, "repositories": [{"id": 7, "name": "Example RPMs"}]}]
    elif resource == "lifecycle_environments":
        eid = 1 if "Library" in (p["search"] or "") else 32 if "_Prod" in (p["search"] or "") else 31
        rows = [{"id": eid, "name": labels[eid], "description": owner,
                 "library": eid == 1, "prior": None if eid == 1 else {"id": 1 if eid == 31 else 31}}]
    elif resource == "content_view_versions":
        if "environment_id" in params:
            rows = [s["versions"][str(s["serving"][str(params["environment_id"])])]]
        else:
            rows = list(s["versions"].values())
    elif resource == "repositories":
        rows = [{"id": 7, "name": "Example RPMs", "content_label": "example-rpms", "product": {"name": "Example Product"}}]
    elif resource == "errata":
        if "content_view_version_id" not in params:
            rows = [fix]
        elif int(params["content_view_version_id"]) == 40:
            rows = [old]
        else:
            rows = [old, fix]
            if s["contaminated"]:
                rows.append({"id": 102, "errata_id": "RHSA-2050:2000", "type": "security"})
    elif resource == "packages":
        if "repository_id" in params:
            rows = [fixed_rpm]
        elif int(params["content_view_version_id"]) == 40:
            rows = [base_rpm]
        else:
            rows = [base_rpm, fixed_rpm]
            if s["race"] and not s.get("race_done"):
                s["versions"]["42"] = version(42, 0, "Unrelated newer Library content", [1], major=2)
                s["serving"]["1"] = 42
                s["race_done"] = True
    else:
        fail("Unexpected resource " + resource)
    done(resources=rows)
elif name == "content_view_version":
    if p["force_promote"]:
        fail("Force promotion is forbidden")
    rows = [v for v in s["versions"].values() if v["version"] == p["version"]]
    if len(rows) != 1 or len(p["lifecycle_environments"] or []) != 1:
        fail("Ambiguous promotion")
    row = rows[0]
    destination = p["lifecycle_environments"][0]
    eid = next((ident for ident, label in labels.items() if label == destination), None)
    environments = {e["id"] for e in row["environments"]}
    if eid in environments:
        done(entity={"content_view_versions": [row]})
    if not ((eid == 1 and not environments) or (eid == 31 and 1 in environments)
            or (eid == 32 and 31 in environments)):
        fail("Cannot promote environment out of sequence")
    for other in s["versions"].values():
        other["environments"] = [e for e in other["environments"] if e["id"] != eid]
    row["environments"].append({"id": eid, "name": destination})
    s["serving"][str(eid)] = row["id"]
    s["promotions"].append(destination)
    done(changed=True, entity={"content_view_versions": [row]})
else:
    fail("Unexpected module")
'''


def version(ident, minor=0, description="Baseline", environments=(1, 31, 32), major=1):
    labels = {1: "Library", 31: "RHEL-sniperpatching_Test", 32: "RHEL-sniperpatching_Prod"}
    return {"id": ident, "content_view_id": 20, "major": major, "minor": minor,
            "version": "%s.%s" % (major, minor), "description": description,
            "environments": [{"id": eid, "name": labels[eid]} for eid in environments]}


class MinorRecoveryPlaybook(unittest.TestCase):
    def run_minor(self, mode="fresh", contaminated=False, race=False):
        with tempfile.TemporaryDirectory(prefix="sniper-minor-test-") as directory:
            base = Path(directory)
            collection = base / "collections/ansible_collections/redhat/satellite"
            (collection / "plugins/modules").mkdir(parents=True)
            (collection / "meta").mkdir()
            (collection / "meta/runtime.yml").write_text(yaml.safe_dump({"action_groups": {
                "satellite": [name for name in MODULES if name != "fixture_incremental"]}}))
            for name in MODULES:
                (collection / ("plugins/modules/" + name + ".py")).write_text(MODULE.replace("__MODULE__", repr(name)))
            state = {"versions": {"40": version(40)}, "serving": {"1": 40, "31": 40, "32": 40},
                     "calls": [], "promotions": [], "uri_count": 0, "contaminated": contaminated, "race": race}
            if mode != "fresh":
                state["versions"]["41"] = version(41, 1, DESCRIPTION, ())
            if mode == "library":
                state["versions"]["40"]["environments"] = [{"id": 31}, {"id": 32}]
                state["versions"]["41"]["environments"] = [{"id": 1}]
                state["serving"]["1"] = 41
            elif mode == "ambiguous":
                state["versions"]["42"] = version(42, 2, DESCRIPTION, ())
            elif mode == "foreign":
                state["versions"]["41"]["description"] = "Another operation"
            elif mode == "foreign_cv":
                state["versions"]["41"]["content_view_id"] = 99
            elif mode == "newer_library":
                state["versions"].pop("41")
                state["versions"]["42"] = version(42, 0, "Unrelated newer Library content", (1,), major=2)
                state["serving"]["1"] = 42
            elif mode == "consumer":
                state["versions"]["40"]["environments"] = [{"id": 31}]
                state["versions"]["41"]["environments"] = [{"id": 1}, {"id": 32}]
                state["serving"]["1"] = 41
                state["serving"]["32"] = 41
            path = base / "state.json"
            path.write_text(json.dumps(state))
            play = yaml.safe_load((ROOT / "create_minor_update.yml").read_text())
            replacements = []

            def prepare(nodes):
                for task in nodes:
                    if "ansible.builtin.uri" in task:
                        task["redhat.satellite.fixture_incremental"] = task.pop("ansible.builtin.uri")
                        replacements.append(task["name"])
                    if "ansible.builtin.import_tasks" in task:
                        task["ansible.builtin.import_tasks"] = str(ROOT / task["ansible.builtin.import_tasks"])
                    for key in ("block", "rescue", "always"):
                        prepare(task.get(key, []))

            prepare(play[0]["tasks"])
            self.assertEqual(len(replacements), 1)
            play[0]["vars_files"] = [str(ROOT / "vars/main.yml")]
            playbook = base / "minor.yml"
            playbook.write_text(yaml.safe_dump(play, sort_keys=False))
            variables = {"sniper_server_url": "https://satellite.example.test", "sniper_username": "example",
                "sniper_password": "fixture-minor-password-canary", "sniper_organization": "Example Organization",
                "sniper_test_host": "test-client.example.test", "sniper_prod_host": "prod-client.example.test",
                "sniper_environment": "test", "sniper_patch_id": A, "ansible_python_interpreter": sys.executable}
            var_path = base / "vars.json"
            var_path.write_text(json.dumps(variables))
            env = dict(os.environ, ANSIBLE_COLLECTIONS_PATH=str(base / "collections"),
                       ANSIBLE_FILTER_PLUGINS=str(ROOT / "filter_plugins"), ANSIBLE_LOCAL_TEMP=str(base / "local"),
                       ANSIBLE_REMOTE_TEMP=str(base / "remote"), ANSIBLE_NOCOLOR="1", ANSIBLE_FORCE_COLOR="0",
                       PYTHONDONTWRITEBYTECODE="1", SNIPER_MINOR_TEST_STATE=str(path))
            env.pop("ANSIBLE_COLLECTIONS_PATHS", None)
            result = subprocess.run(["ansible-playbook", "-i", "localhost,", str(playbook), "-e", "@" + str(var_path)],
                                    cwd=ROOT, env=env, text=True, capture_output=True, timeout=180)
            self.assertNotIn("fixture-minor-password-canary", result.stdout + result.stderr)
            return result, json.loads(path.read_text())

    def test_fresh_minor_is_validated_then_staged_through_library_before_test(self):
        result, state = self.run_minor()
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-8000:])
        self.assertEqual(state["uri_count"], 1)
        self.assertEqual(state["promotions"], ["Library", "RHEL-sniperpatching_Test"])
        self.assertEqual(state["serving"], {"1": 41, "31": 41, "32": 40})
        self.assertEqual(set(state["versions"]), {"40", "41"})
        first_promotion = next(i for i, c in enumerate(state["calls"]) if c["module"] == "content_view_version")
        for resource in ("errata", "packages"):
            proof = next(i for i, c in enumerate(state["calls"]) if c["resource"] == resource
                         and str(c["params"].get("content_view_version_id")) == "41")
            self.assertLess(proof, first_promotion)

    def test_orphan_is_reused_without_incremental_post(self):
        result, state = self.run_minor("orphan")
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-8000:])
        self.assertEqual(state["uri_count"], 0)
        self.assertEqual(state["promotions"], ["Library", "RHEL-sniperpatching_Test"])
        self.assertEqual(set(state["versions"]), {"40", "41"})
        self.assertEqual(state["serving"]["32"], 40)

    def test_library_candidate_is_reused_without_post_or_library_mutation(self):
        result, state = self.run_minor("library")
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-8000:])
        self.assertEqual(state["uri_count"], 0)
        self.assertEqual(state["promotions"], ["RHEL-sniperpatching_Test"])
        self.assertEqual(state["serving"], {"1": 41, "31": 41, "32": 40})

    def test_ambiguous_foreign_or_newer_library_history_cannot_mutate(self):
        for mode in ("ambiguous", "foreign", "foreign_cv", "newer_library", "consumer"):
            with self.subTest(mode=mode):
                result, state = self.run_minor(mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(state["uri_count"], 0)
                self.assertEqual(state["promotions"], [])
                self.assertEqual(state["serving"]["31"], 40)
                self.assertEqual(state["serving"]["32"], 41 if mode == "consumer" else 40)
                self.assertEqual(state["serving"]["1"], 42 if mode == "newer_library" else 41 if mode == "consumer" else 40)

    def test_contaminated_orphan_stays_unpromoted(self):
        result, state = self.run_minor("orphan", contaminated=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(state["uri_count"], 0)
        self.assertEqual(state["promotions"], [])
        self.assertIn("The generated version has an unexpected content delta", result.stdout)
        self.assertEqual(state["versions"]["41"]["environments"], [])
        self.assertEqual(state["serving"], {"1": 40, "31": 40, "32": 40})

    def test_library_change_during_content_validation_is_refused(self):
        result, state = self.run_minor("orphan", race=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(state["uri_count"], 0)
        self.assertEqual(state["promotions"], [])
        self.assertTrue(state.get("race_done"))
        self.assertIn("Library contains unrelated content", result.stdout)
        self.assertEqual(state["serving"], {"1": 42, "31": 40, "32": 40})


if __name__ == "__main__":
    unittest.main()
