"""Execute real resolver tasks against changing synthetic Satellite responses."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CVE1 = "CVE-2050-1000"
CVE2 = "CVE-2050-1001"
A = "RHSA-2050:1000"
B = "RHSA-2050:1001"
C = "RHSA-2050:1002"
MODULE = r"""
import json, os
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
module = AnsibleModule(argument_spec={
    "resource": {"type": "str", "required": True},
    "organization": {"type": "str"},
    "search": {"type": "str"},
    "params": {"type": "dict", "default": {}},
})
p = module.params
path = Path(os.environ["SNIPER_RESOLUTION_TEST_STATE"])
state = json.loads(path.read_text())
state["calls"].append({"resource": p["resource"], "params": p["params"], "search": p["search"]})
advisories = ["RHSA-2050:1000", "RHSA-2050:1001", "RHSA-2050:1002"]
details = {}
packages = []
for i, ident in enumerate(advisories):
    package = {"name": "demo-" + str(i), "epoch": "0", "version": "2.0",
               "release": "1.el7", "arch": "x86_64"}
    packages.append(package)
    details[ident] = {
        "id": i + 101, "errata_id": ident, "packages": [package],
        "cves": [{"cve_id": cve} for cve, matches in state["mapping"].items() if ident in matches],
    }
params = p["params"]
if p["resource"] == "errata":
    if "id" in params:
        rows = [next(row for row in details.values() if row["id"] == int(params["id"]))]
    elif int(params["repository_id"]) != 7:
        rows = []
    else:
        ids = state["mapping"].get(params.get("cve"), [])
        rows = [{"id": details[ident]["id"], "errata_id": ident} for ident in ids]
elif p["resource"] == "packages":
    rows = [row for row in packages
            if "%s-%s-%s.%s.rpm" % tuple(row[k] for k in ("name", "version", "release", "arch"))
            in p["search"]]
else:
    module.fail_json(msg="Unexpected resource " + p["resource"])
path.write_text(json.dumps(state))
module.exit_json(changed=False, resources=rows)
"""


class DynamicResolution(unittest.TestCase):
    def resolve(self, mapping):
        with tempfile.TemporaryDirectory(prefix="sniper-resolution-test-") as directory:
            base = Path(directory)
            collection = base / "collections/ansible_collections/redhat/satellite"
            modules = collection / "plugins/modules"
            modules.mkdir(parents=True)
            (modules / "resource_info.py").write_text(MODULE)
            state_file = base / "state.json"
            state_file.write_text(json.dumps({"mapping": mapping, "calls": []}))
            result_file = base / "result.json"
            play = [{
                "name": "Resolve submitted survey IDs", "hosts": "localhost",
                "connection": "local", "gather_facts": False,
                "vars": {
                    "ansible_python_interpreter": sys.executable,
                    "sniper_patch_id": CVE1 + ",\n" + CVE2 + " " + CVE1,
                    "sniper_repo_details": [{"id": 7, "name": "alpha"},
                                            {"id": 8, "name": "beta"}],
                    "sniper_organization": "Example", "sniper_org": {"id": 1},
                },
                "tasks": [
                    {"ansible.builtin.import_tasks": str(ROOT / "tasks/resolve.yml")},
                    {"ansible.builtin.copy": {
                        "dest": str(result_file), "mode": "0600",
                        "content": "{{ {'ids': sniper_ids, 'map': sniper_advisory_map, "
                                   "'requirements': sniper_requirements} | to_json }}",
                    }},
                ],
            }]
            playbook = base / "resolve.yml"
            playbook.write_text(yaml.safe_dump(play, sort_keys=False))
            env = dict(os.environ,
                       ANSIBLE_COLLECTIONS_PATH=str(base / "collections"),
                       ANSIBLE_FILTER_PLUGINS=str(ROOT / "filter_plugins"),
                       ANSIBLE_LOCAL_TEMP=str(base / "local"),
                       ANSIBLE_NOCOLOR="1", ANSIBLE_FORCE_COLOR="0",
                       SNIPER_RESOLUTION_TEST_STATE=str(state_file),
                       PYTHONDONTWRITEBYTECODE="1")
            env.pop("ANSIBLE_COLLECTIONS_PATHS", None)
            run = subprocess.run(["ansible-playbook", "-i", "localhost,", str(playbook)],
                                 cwd=ROOT, env=env, text=True, capture_output=True, timeout=120)
            result = json.loads(result_file.read_text()) if result_file.exists() else None
            return run, result, json.loads(state_file.read_text())["calls"]

    def test_new_launch_uses_changed_satellite_data_with_the_same_survey_input(self):
        for target in (B, C):
            run, result, calls = self.resolve({CVE1: [A, B], CVE2: [target]})
            self.assertEqual(run.returncode, 0, (run.stdout + run.stderr)[-8000:])
            self.assertEqual(result["ids"], [CVE1, CVE2])
            self.assertEqual(result["map"], {CVE1: [A, B], CVE2: [target]})
            queries = [c for c in calls if "cve" in c["params"]]
            self.assertEqual({(int(c["params"]["repository_id"]), c["params"]["cve"])
                              for c in queries},
                             {(repo, ident) for repo in (7, 8) for ident in (CVE1, CVE2)})
            self.assertEqual({r["advisory"] for r in result["requirements"]}, {A, B, target})
            self.assertEqual(len(result["requirements"]), len({A, B, target}))

    def test_an_unresolved_second_cve_stops_before_package_queries(self):
        run, result, calls = self.resolve({CVE1: [A], CVE2: []})
        self.assertNotEqual(run.returncode, 0)
        self.assertIsNone(result)
        self.assertIn(CVE2, run.stdout)
        self.assertFalse(any(c["resource"] == "packages" for c in calls))


if __name__ == "__main__":
    unittest.main()
