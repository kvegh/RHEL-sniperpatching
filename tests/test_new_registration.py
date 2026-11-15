"""Run NEW registration orchestration locally with synthetic Satellite/guest boundaries.

Real Ansible runs the source assertions, includes, loops, failure/always paths,
SSH pin files and CA cleanup. Fixtures replace only APIs and guest operations;
no live API, SSH, guest file or package operation is performed.
Reason and scope: ../docs/implementation.md#synthetic-test-modules
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "playbooks/new"
HOSTS = ["test-client.example.test", "prod-client.example.test"]
OWNER = "Managed by RHEL-sniperpatching."
LABELS = ["rhel-9-for-x86_64-appstream-rpms", "rhel-9-for-x86_64-baseos-rpms"]
SECRET = "synthetic-registration-token-do-not-display"
MODULES = ("resource_info", "activation_key", "registration_command", "guest")

MODULE = r'''
import base64
import json
import os
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
NAME = __MODULE__
spec = {
    key: {"type": "str"} for key in (
        "server_url", "username", "password", "ca_path", "organization", "resource", "packages",
        "search", "name", "description", "release_version", "state", "kind", "target_host", "ssh_args", "pin_path")
}
spec.update({
    "validate_certs": {"type": "bool"}, "full_details": {"type": "bool"},
    "params": {"type": "dict", "default": {}}, "arguments": {"type": "dict", "default": {}},
    "content_view_environments": {"type": "list", "elements": "str"},
    "content_overrides": {"type": "list", "elements": "dict"},
    "activation_keys": {"type": "list", "elements": "str"}, "jwt_expiration": {"type": "int"},
})
for key in ("insecure", "force", "ignore_subman_errors", "update_packages", "setup_insights",
            "setup_remote_execution", "setup_remote_execution_pull", "setup_container_registry_certs"):
    spec[key] = {"type": "bool"}
m = AnsibleModule(argument_spec=spec)
p = m.params
if p.get("ca_path") and not Path(p["ca_path"]).is_file():
    m.fail_json(msg="Delegated API CA was removed before this operation")
path = Path(os.environ["SNIPER_REGISTRATION_STATE"])
s = json.loads(path.read_text())
call = dict(module=NAME, resource=p["resource"], params=p["params"], name=p["name"],
            host=p["target_host"], kind=p["kind"], pin_path=p["pin_path"])
s["calls"].append(call)
def done(**result):
    path.write_text(json.dumps(s))
    m.exit_json(**dict({"changed": False}, **result))
def fail(message):
    path.write_text(json.dumps(s))
    m.fail_json(msg=message)
def stage_of(host):
    return "test" if host.startswith("test-") else "prod"
def cve(stage):
    eid = 30 if stage == "test" else 31
    return {"id": eid + 100, "label": "RHEL_sniperpatching_" + stage.title() + "/RHEL_sniperpatching",
            "content_view": {"id": 20}, "lifecycle_environment": {"id": eid}}
def host_row(host):
    stage = stage_of(host)
    mapping = cve(stage)["id"]
    if s.get("wrong_mapping"):
        mapping = 999
    return {"id": 11 if stage == "test" else 12, "name": host, "organization_id": 1,
            "subscription_facet_attributes": {"uuid": s["consumers"][host]},
            "content_facet_attributes": {"content_view_environments": [{"id": mapping}]}}
if NAME == "resource_info":
    resource, params = p["resource"], p["params"]
    if resource == "organizations":
        rows = [{"id": 1}]
    elif resource == "content_views":
        rows = [{"id": 20, "label": "RHEL_sniperpatching", "description": s["owner"],
                 "repositories": [{"id": 50, "name": "BaseOS"}, {"id": 51, "name": "AppStream"}]}]
    elif resource == "lifecycle_environments":
        stage = "test" if "_Test" in p["search"] else "prod"
        rows = [{"id": 30 if stage == "test" else 31, "description": s["owner"],
                 "label": "RHEL_sniperpatching_" + stage.title(),
                 "prior": {"name": "Library" if stage == "test" else "RHEL-sniperpatching_Test"}}]
    elif resource == "content_view_versions":
        rows = [{"id": 40, "version": "1.0", "content_view_id": 20,
                 "description": "Initial demonstration baseline; cutoff=2024-04-30"}]
        if s.get("later_history") and "environment_id" not in params:
            rows.append(dict(rows[0], id=41, version="2.0"))
        if s.get("missing_serving") and "environment_id" in params:
            rows = []
    elif resource == "repositories":
        # Native index first filters the version, then the lifecycle environment.
        # The same two source repositories have archived and promoted copies.
        rows = [{"id": rid + offset, "name": "BaseOS" if rid == 50 else "AppStream",
                 "product": {"name": "RHEL 9"}, "content_label": __LABELS__[1 if rid == 50 else 0],
                 "library_instance_id": rid, "environment_id": environment_id,
                 "content_view_version_id": 40}
                for environment_id, offset in ((None, 0), (1, 100), (30, 200), (31, 300))
                for rid in (50, 51)]
        if "content_view_version_id" in params:
            rows = [row for row in rows if row["content_view_version_id"] == int(params["content_view_version_id"])]
        if "environment_id" in params and not s.get("unscoped_repositories"):
            rows = [row for row in rows if row["environment_id"] == int(params["environment_id"])]
        call["returned_repository_ids"] = [row["id"] for row in rows]
        call["returned_environment_ids"] = [row["environment_id"] for row in rows]
    elif resource == "errata":
        rows = [{"errata_id": "RHSA-2024:9999", "issued": "2024-05-01"}] if s.get("later_erratum") else []
    elif resource == "packages":
        rows = s["originals"]
        if s.get("wrong_packages"):
            rows = [dict(row, release="999.el9_4") for row in rows]
    elif resource == "content_view_environments":
        rows = [cve("test" if int(params["lifecycle_environment_id"]) == 30 else "prod")]
    elif resource == "activation_keys":
        rows = [{"description": "foreign"}] if s.get("foreign_key") else []
    elif resource == "hosts":
        host = p["search"].split('"')[1]
        rows = [host_row(host)] if host in s["consumers"] and not s.get("missing_host") else []
    else:
        fail("Unexpected API resource " + resource)
    done(resources=rows)
elif NAME == "activation_key":
    if p["release_version"] != "9.4" or len(p["content_view_environments"]) != 1:
        fail("Incorrect modern activation key parameters")
    if sorted(p["content_overrides"], key=lambda row: row["label"]) != [
            {"label": label, "override": "enabled"} for label in __LABELS__]:
        fail("Activation key must enable exactly the original repository pair")
    call["cve_labels"] = p["content_view_environments"]
    s["keys"].append(p["name"])
    done(changed=True)
elif NAME == "registration_command":
    for key in ("insecure", "force", "ignore_subman_errors", "update_packages", "setup_insights",
                "setup_remote_execution", "setup_remote_execution_pull", "setup_container_registry_certs"):
        if p[key] is not False:
            fail("Unsafe or omitted native registration option: " + key)
    if p["jwt_expiration"] != 1 or p["packages"] != "":
        fail("Token must be short lived and packages must be empty")
    done(registration_command="native-register " + __SECRET__)
elif NAME == "guest":
    host, kind, args = p["target_host"], p["kind"], p["arguments"]
    if not p["pin_path"] or not Path(p["pin_path"]).is_file() or "StrictHostKeyChecking=yes" not in p["ssh_args"]:
        fail("Guest operation occurred before strict public-key pinning")
    if Path(p["pin_path"]).read_text() != host + " ssh-ed25519 Zml4dHVyZS1wdWJsaWMta2V5\n":
        fail("Guest SSH pin did not contain the exact protected host/key pair")
    stage = stage_of(host)
    if kind == "setup":
        uuid = ("11111111-1111-4111-8111-111111111111" if stage == "test" else "22222222-2222-4222-8222-222222222222")
        done(ansible_facts={"distribution": "RedHat", "distribution_version": "9.4", "architecture": "x86_64",
                           "fqdn": host, "product_uuid": uuid if not s.get("wrong_guest") else "wrong",
                           "machine_id": ("1" if stage == "test" else "2") * 32})
    elif kind == "command":
        argv = args["argv"]
        if argv[0] == "rpm":
            lines = ["example|0|1.0|1.el9|x86_64", "gpg-pubkey|0|12345678|87654321|(none)"]
            if s.get("rpm_changed") and host in s["consumers"]:
                lines[0] = "example|0|2.0|1.el9|x86_64"
            done(rc=0, stdout="\n".join(lines), stdout_lines=lines, stderr="")
        elif argv == ["subscription-manager", "identity"]:
            consumer = s["consumers"].get(host)
            done(rc=0 if consumer else 1, stdout="system identity: " + consumer if consumer else "This system is not yet registered.", stderr="")
        elif argv == ["update-ca-trust", "extract"]:
            s["trust"].append(host)
            done(rc=0, stdout="", stderr="")
        else:
            fail("Unexpected guest command")
    elif kind == "stat":
        exists = host in s["anchors"]
        done(stat={"exists": exists, "isreg": True, "islnk": False})
    elif kind == "slurp":
        done(content=base64.b64encode(s["anchors"][host].encode()).decode())
    elif kind == "copy":
        created = host not in s["anchors"]
        s["anchors"].setdefault(host, args["content"])
        done(changed=created)
    elif kind == "shell":
        if host not in s["trust"] or args["cmd"] != "native-register " + __SECRET__:
            fail("Native registration ran before guest trust or with the wrong command")
        s["consumers"][host] = "aaaaaaaa-aaaa-4aaa-8aaa-" + ("1" if stage == "test" else "2") * 12
        if s.get("registration_failure"):
            fail("Synthetic uncertain registration failure")
        done(rc=0, stdout="registered", stderr="", changed=True)
    else:
        fail("Unexpected guest boundary " + kind)
'''


class NewRegistration(unittest.TestCase):
    def run_registration(self, *, repeat=False, extra_inventory=False, **scenario):
        with tempfile.TemporaryDirectory(prefix="sniper-registration-") as directory:
            folder = Path(directory)
            source = folder / "playbooks/new"
            shutil.copytree(NEW, source, ignore=shutil.ignore_patterns("__pycache__"))
            (folder / "docs").mkdir()
            catalog = json.loads((ROOT / "docs/rhel94-cve-candidates.json").read_text())
            (folder / "docs/rhel94-cve-candidates.json").write_text(json.dumps(catalog))
            collection = folder / "collections/ansible_collections/redhat/satellite"
            modules = collection / "plugins/modules"
            modules.mkdir(parents=True)
            (collection / "meta").mkdir()
            (collection / "meta/runtime.yml").write_text(yaml.safe_dump({
                "action_groups": {"satellite": list(MODULES)}
            }))
            for name in MODULES:
                (modules / (name + ".py")).write_text(MODULE.replace(
                    "__MODULE__", repr(name)).replace("__LABELS__", repr(LABELS)).replace("__SECRET__", repr(SECRET)))
            # Keep source orchestration and assertions; replace only guest I/O.
            client_path = source / "tasks/registration_client.yml"
            tasks = yaml.safe_load(client_path.read_text())

            def replace_guest_io(tasks):
                for task in tasks:
                    for branch in ("block", "always", "rescue"):
                        replace_guest_io(task.get(branch, []))
                    for kind in ("setup", "command", "stat", "slurp", "copy", "shell"):
                        key = "ansible.builtin." + kind
                        if key in task:
                            arguments = task.pop(key) or {}
                            task["redhat.satellite.guest"] = {
                                "kind": kind, "arguments": arguments,
                                "target_host": "{{ inventory_hostname }}",
                                "pin_path": "{{ sniper_new_trust_file.path | default('') }}",
                                "ssh_args": "{{ ansible_ssh_common_args | default('') }}",
                            }
            replace_guest_io(tasks)
            client_path.write_text(yaml.safe_dump(tasks, sort_keys=False))
            entry = source / "register_demo_clients.yml"
            plays = yaml.safe_load(entry.read_text())
            for play in plays:
                play["no_log"] = False  # all data here is synthetic; explicit token tasks remain protected
            plays[1]["become"] = False
            entry.write_text(yaml.safe_dump(plays, sort_keys=False))
            variables = {
                "sniper_server_url": "https://satellite.example.test",
                "sniper_username": "fixture", "sniper_password": "fixture-only",
                "sniper_organization": "Example Organization",
                "sniper_test_host": HOSTS[0], "sniper_prod_host": HOSTS[1],
                "sniper_satellite_ca_pem": "-----BEGIN CERTIFICATE-----\nfixture-public-ca\n-----END CERTIFICATE-----\n",
                "sniper_repositories": [{"name": name, "product": "RHEL 9"} for name in ("BaseOS", "AppStream")],
            }
            (folder / "vars.json").write_text(json.dumps(variables))
            hostvars = {}
            for index, host in enumerate(HOSTS, 1):
                hostvars[host] = {
                    "ansible_connection": "local", "ansible_user": "fixture-user", "ansible_host": host,
                    "ansible_python_interpreter": sys.executable,
                    "sniper_ssh_host_key": "ssh-ed25519 Zml4dHVyZS1wdWJsaWMta2V5",
                    "sniper_expected_product_uuid": str(index) * 8 + "-" + str(index) * 4 + "-4" + str(index) * 3 + "-8" + str(index) * 3 + "-" + str(index) * 12,
                    "sniper_expected_machine_id": str(index) * 32,
                }
            if extra_inventory:
                hostvars["unrelated.example.test"] = {"ansible_connection": "local"}
            (folder / "inventory.yml").write_text(yaml.safe_dump({"all": {"hosts": hostvars}}))
            state = {
                "calls": [], "keys": [], "consumers": {}, "anchors": {}, "trust": [], "owner": OWNER,
                "originals": list({json.dumps(row["baseline_package"], sort_keys=True): row["baseline_package"]
                                   for row in catalog["candidates"]}.values()),
            }
            if scenario.pop("registered", False):
                state["consumers"] = {host: "aaaaaaaa-aaaa-4aaa-8aaa-" + str(i) * 12 for i, host in enumerate(HOSTS, 1)}
            if scenario.pop("conflicting_ca", False):
                state["anchors"][HOSTS[0]] = "another-public-ca"
            if scenario.pop("matching_ca", False):
                state["anchors"][HOSTS[1]] = variables["sniper_satellite_ca_pem"]
            state.update(scenario)
            state_path = folder / "state.json"
            state_path.write_text(json.dumps(state))
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", ANSIBLE_NOCOLOR="1", ANSIBLE_FORCE_COLOR="0",
                               ANSIBLE_LOCAL_TEMP=str(folder / "local"), ANSIBLE_REMOTE_TEMP=str(folder / "remote"),
                               ANSIBLE_COLLECTIONS_PATH=str(folder / "collections"), SNIPER_REGISTRATION_STATE=str(state_path))
            environment.pop("ANSIBLE_COLLECTIONS_PATHS", None)
            command = ["ansible-playbook", "-i", str(folder / "inventory.yml"), str(entry), "-e", "@" + str(folder / "vars.json"), "-vv"]
            result = subprocess.run(command, cwd=source, env=environment, text=True, capture_output=True, timeout=180)
            if repeat and result.returncode == 0:
                state = json.loads(state_path.read_text())
                state["first_calls"] = list(state["calls"])
                state["calls"] = []
                state_path.write_text(json.dumps(state))
                result = subprocess.run(command, cwd=source, env=environment, text=True, capture_output=True, timeout=180)
            state = json.loads(state_path.read_text())
            observed_pins = {call["pin_path"] for call in state["calls"] if call.get("pin_path")}
            observed_pins.update(call["pin_path"] for call in state.get("first_calls", []) if call.get("pin_path"))
            state["remaining_pins"] = [pin for pin in observed_pins if Path(pin).exists()]
            state["remaining_cas"] = list(Path(folder / "local").rglob("*-sniper-*-ca.pem"))
            return result, state

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-12000:])
        self.assertNotIn(SECRET, result.stdout + result.stderr)

    def test_direct_registration_orders_content_trust_and_native_registration(self):
        result, state = self.run_registration(extra_inventory=True, matching_ca=True)
        self.assert_success(result)
        self.assertEqual(set(state["consumers"]), set(HOSTS))
        self.assertEqual(len(state["keys"]), 2)
        self.assertFalse(any(call["kind"] == "copy" and call["host"] == HOSTS[1] for call in state["calls"]))
        calls = state["calls"]
        first_guest = next(i for i, c in enumerate(calls) if c["module"] == "guest")
        package_reads = [i for i, c in enumerate(calls) if c["resource"] == "packages"]
        self.assertEqual(len(package_reads), 2)
        self.assertLess(max(package_reads), first_guest)
        self.assertEqual([c["cve_labels"] for c in calls if c["module"] == "activation_key"], [
            ["RHEL_sniperpatching_Test/RHEL_sniperpatching"],
            ["RHEL_sniperpatching_Prod/RHEL_sniperpatching"],
        ])
        self.assertEqual(state["remaining_pins"], [])
        self.assertEqual(state["remaining_cas"], [])
        self.assertIn("package_baseline_unchanged", result.stdout)

    def test_served_repository_query_selects_each_environment_without_deduplicating(self):
        result, state = self.run_registration()
        self.assert_success(result)
        queries = [call for call in state["calls"] if call["resource"] == "repositories"]
        self.assertEqual([call["params"] for call in queries], [
            {"content_view_version_id": 40, "environment_id": 30},
            {"content_view_version_id": 40, "environment_id": 31},
        ])
        self.assertEqual([call["returned_repository_ids"] for call in queries], [[250, 251], [350, 351]])
        self.assertEqual([call["returned_environment_ids"] for call in queries], [[30, 30], [31, 31]])

        # An unexpectedly unscoped response still fails closed, even when all
        # eight copies share the expected names, products and content labels.
        result, state = self.run_registration(unscoped_repositories=True)
        self.assertNotEqual(result.returncode, 0)
        query = next(call for call in state["calls"] if call["resource"] == "repositories")
        self.assertEqual(len(query["returned_repository_ids"]), 8)
        self.assertFalse(any(call["module"] in {"guest", "activation_key", "registration_command"}
                             for call in state["calls"]))
        self.assertEqual(state["consumers"], {})
        self.assertEqual(state["remaining_cas"], [])

    def test_repeat_skips_registration_and_all_guest_mutations(self):
        result, state = self.run_registration(repeat=True)
        self.assert_success(result)
        self.assertFalse(any(c["module"] in {"activation_key", "registration_command"} or
                             c["kind"] in {"copy", "shell", "stat", "slurp"} for c in state["calls"]))
        self.assertEqual(len(state["keys"]), 2)

    def test_missing_or_later_baseline_stops_before_guest_or_activation_key(self):
        for scenario in ("missing_serving", "later_history", "later_erratum", "wrong_packages"):
            with self.subTest(scenario=scenario):
                result, state = self.run_registration(**{scenario: True})
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(any(c["module"] in {"guest", "activation_key", "registration_command"} for c in state["calls"]))
                self.assertEqual(state["consumers"], {})

    def test_wrong_original_guest_stops_before_registration_changes(self):
        result, state = self.run_registration(wrong_guest=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(state["keys"], [])
        self.assertEqual(state["anchors"], {})
        self.assertEqual(state["remaining_pins"], [])

    def test_foreign_existing_consumer_mapping_is_preserved(self):
        result, state = self.run_registration(registered=True, wrong_mapping=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(state["consumers"]), 2)
        self.assertEqual(state["keys"], [])
        self.assertFalse(any(c["kind"] == "shell" for c in state["calls"]))
        self.assertEqual(state["remaining_pins"], [])

    def test_foreign_key_or_conflicting_ca_never_executes_registration(self):
        for scenario in ("foreign_key", "conflicting_ca"):
            with self.subTest(scenario=scenario):
                result, state = self.run_registration(**{scenario: True})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(state["consumers"], {})
                self.assertFalse(any(c["module"] == "registration_command" or c["kind"] == "shell" for c in state["calls"]))
                if scenario == "conflicting_ca":
                    self.assertEqual(state["anchors"][HOSTS[0]], "another-public-ca")
                self.assertEqual(state["remaining_pins"], [])

    def test_changed_full_rpm_inventory_fails_and_cleans_ssh_pin(self):
        result, state = self.run_registration(rpm_changed=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Registration changed the full RPM baseline", result.stdout)
        self.assertEqual(state["remaining_pins"], [])

    def test_uncertain_native_failure_is_not_retried_and_still_checks_rpms(self):
        result, state = self.run_registration(registration_failure=True)
        self.assertNotEqual(result.returncode, 0)
        shells = [i for i, c in enumerate(state["calls"]) if c["kind"] == "shell"]
        self.assertEqual(len(shells), 1)
        self.assertTrue(any(c["kind"] == "command" for c in state["calls"][shells[0] + 1:]))
        self.assertEqual(state["remaining_pins"], [])
        self.assertNotIn(SECRET, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
