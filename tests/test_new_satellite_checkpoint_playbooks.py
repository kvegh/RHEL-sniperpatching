"""Real Ansible checkpoint orchestration with synthetic VM, guest and API I/O.

Only boundary modules are replaced. Source guards, includes, check mode,
temporary trust files, failure cleanup and multi-play ordering still execute.
See docs/implementation.md#synthetic-test-modules.
"""
import hashlib
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
CA = "-----BEGIN CERTIFICATE-----\nsynthetic-public-ca\n-----END CERTIFICATE-----\n"
UUID = "11111111-1111-4111-8111-111111111111"
MACHINE_ID = "1" * 32
PASSWORD = "synthetic-secret-never-display"
BOUNDARY = r'''
import base64
import json
import os
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule

m = AnsibleModule(argument_spec={
    "kind": {"type": "str", "required": True},
    "arguments": {"type": "dict", "required": True},
    "pin": {"type": "str", "default": ""},
    "ssh": {"type": "str", "default": ""},
}, supports_check_mode=True)
path = Path(os.environ["SNIPER_CHECKPOINT_STATE"])
s = json.loads(path.read_text())
p = m.params
args, kind = p["arguments"], p["kind"]
s["calls"].append({"kind": kind, "arguments": args, "pin": p["pin"]})
def done(**values):
    path.write_text(json.dumps(s))
    m.exit_json(**values)
def fail(message):
    path.write_text(json.dumps(s))
    m.fail_json(msg=message)
if kind != "uri" and kind != "content":
    if not p["pin"] or not Path(p["pin"]).is_file() or "StrictHostKeyChecking=yes" not in p["ssh"]:
        fail("Boundary reached before strict SSH pinning")
if kind == "helper":
    value = json.loads(args["stdin"])
    if set(value) != {"op", "vm_name", "uuid", "mac", "network", "ca_sha256",
                      "installed_verified", "pre_sync_verified", "check"}:
        fail("Wrong native helper interface")
    if value["op"] == "verify" and not s.get("exists", False):
        fail("Checkpoint is absent")
    if s.get("foreign"):
        fail("Checkpoint belongs to another installation")
    if value["op"] == "create":
        if m.check_mode or value["check"] or not value["installed_verified"] or not value["pre_sync_verified"]:
            fail("Unsafe capture invocation")
        if s.get("malformed") or s.get("malformed_zero"):
            done(rc=0 if s.get("malformed_zero") else 1, stdout="", changed=False)
        if s.get("unknown"):
            done(rc=1, stdout=json.dumps({"result": "failed", "outcome": "unknown"}), changed=False)
    done(rc=0, stdout=json.dumps({
        "name": "post-satellite-install", "operation": value["op"],
        "exists": s.get("exists", False) or value["op"] == "create",
        "cold_verified": s.get("exists", False) or value["op"] == "create",
        "vm_running": not s.get("stopped", False), "changed": value["op"] == "create",
        "check_mode": value["check"], "reused": s.get("exists", False), "recovered_start": False,
    }), changed=False)
elif kind == "uri":
    if not args["validate_certs"] or args["follow_redirects"] != "none":
        fail("TLS or redirect protections changed")
    if args["ca_path"] != "/etc/pki/katello/certs/katello-server-ca.crt" and not Path(args["ca_path"]).is_file():
        fail("Job-local public CA is missing")
    if "/api/organizations" in args["url"]:
        done(status=200)
    if "/api/ping" in args["url"]:
        # The real server has no root status. Only the native nested shape is valid.
        done(status=200, json={"results": {"katello": {"status": "error" if s.get("unready") else "ok"}}})
    key = "repositories" if "/katello/api/repositories?" in args["url"] else "syncs"
    count = s.get(key, 0)
    done(status=200, json={"total": 99, "subtotal": count, "results": [] if count == 0 else [{}]})
elif kind == "setup":
    done(ansible_facts={"product_uuid": "wrong" if s.get("wrong_uuid") else __UUID__,
                       "machine_id": "wrong" if s.get("wrong_machine") else __MACHINE_ID__})
elif kind == "stat":
    done(stat={"isreg": True, "islnk": False, "uid": 0, "size": 200})
elif kind == "slurp":
    if args["src"].endswith("satellite-answers.yaml"):
        value = "foreman:\n  server_ssl_ca: /etc/pki/katello/certs/katello-server-ca.crt\n"
    else:
        value = "different-ca" if s.get("wrong_ca") else __CA__
    done(content=base64.b64encode(value.encode()).decode())
elif kind == "command":
    done(rc=0, stdout="healthy")
elif kind == "content":
    done(changed=True)
else:
    fail("Unexpected boundary")
'''


class CheckpointPlaybooks(unittest.TestCase):
    def run_play(self, entry="create_satellite_checkpoint.yml", *, check=False,
                 missing_install=False, limit=None, **scenario):
        with tempfile.TemporaryDirectory(prefix="sniper-checkpoint-fixture-") as tmp:
            folder = Path(tmp)
            source = folder / "new"
            shutil.copytree(NEW, source, ignore=shutil.ignore_patterns("__pycache__"))
            library = source / "library"
            library.mkdir(exist_ok=True)
            code = BOUNDARY.replace("__UUID__", repr(UUID)).replace("__MACHINE_ID__", repr(MACHINE_ID)).replace("__CA__", repr(CA))
            (library / "checkpoint_boundary.py").write_text(code)

            def replace(tasks):
                for task in tasks:
                    for branch in ("block", "always", "rescue"):
                        replace(task.get(branch, []))
                    for kind in ("command", "uri", "setup", "stat", "slurp"):
                        key = "ansible.builtin." + kind
                        if key not in task:
                            continue
                        args = task.pop(key) or {}
                        boundary = "helper" if kind == "command" and "stdin" in args else kind
                        task["checkpoint_boundary"] = {
                            "kind": boundary, "arguments": args,
                            "pin": "{{ sniper_new_trust_file.path | default('') }}",
                            "ssh": "{{ ansible_ssh_common_args | default('') }}",
                        }
                        if kind == "uri" and "/api/ping" in args.get("url", ""):
                            if "retries" in task:
                                task.update(retries=1, delay=0)
            for relative in ("tasks/satellite_checkpoint_inspect.yml", "tasks/satellite_health.yml", entry):
                file = source / relative
                data = yaml.safe_load(file.read_text())
                if relative == entry:
                    for play in data:
                        play["become"] = False
                        for branch in ("pre_tasks", "tasks", "post_tasks"):
                            replace(play.get(branch, []))
                    if entry == "configure_satellite_content.yml":
                        # Exercise the actual cross-play gate before a synthetic first write.
                        # Other content orchestration has its own tests and selected-EE syntax.
                        data[1]["tasks"] = data[1]["tasks"][:1] + [{
                            "name": "Synthetic first content write after the actual gate",
                            "checkpoint_boundary": {"kind": "content", "arguments": {}},
                        }]
                        data[1].pop("module_defaults", None)
                else:
                    replace(data)
                file.write_text(yaml.safe_dump(data, sort_keys=False))

            variables = {
                "sniper_server_url": "https://satellite.example.test",
                "sniper_username": "fixture", "sniper_password": PASSWORD,
                "sniper_satellite_fqdn": "satellite.example.test",
                "sniper_satellite_ca_pem": CA, "sniper_new_vm_name": "new-satellite",
                "sniper_new_vm_uuid": UUID, "sniper_new_vm_mac": "52:54:00:12:34:56",
                "sniper_new_vm_network": "fixture-network",
                "sniper_new_installation_vm_uuid": UUID,
                "sniper_new_installation_machine_id": MACHINE_ID,
                "sniper_new_installation_ca_sha256": hashlib.sha256("".join(CA.split()).encode()).hexdigest(),
                "sniper_new_installation_result": {"satellite_configured": True, "native_services_healthy": True,
                                                   "authenticated_https_verified": True},
                "sniper_new_checkpoint_result": {"name": "post-satellite-install", "cold_verified": True, "vm_running": True},
            }
            variables.update(
                sniper_new_checkpoint_installation_verified=True,
                sniper_new_checkpoint_verified_vm_uuid=UUID,
                sniper_new_checkpoint_verified_ca_sha256=variables["sniper_new_installation_ca_sha256"])
            if missing_install:
                variables.pop("sniper_new_installation_result")
            if scenario.pop("missing_final", False):
                variables.pop("sniper_new_checkpoint_installation_verified")
            if scenario.pop("wrong_final_uuid", False):
                variables["sniper_new_checkpoint_verified_vm_uuid"] = "wrong"
            if scenario.pop("wrong_final_ca", False):
                variables["sniper_new_checkpoint_verified_ca_sha256"] = "0" * 64
            if scenario.pop("wrong_install", False):
                variables["sniper_new_installation_vm_uuid"] = "wrong"
            inventory = {"all": {"hosts": {host: {
                "ansible_connection": "local", "ansible_host": host + ".example.test",
                "ansible_python_interpreter": sys.executable,
                "sniper_ssh_host_key": "ssh-ed25519 Zml4dHVyZS1wdWJsaWMta2V5",
            } for host in ("sniper_satellite_hypervisor", "sniper_satellite_new")}}}
            (folder / "inventory.yml").write_text(yaml.safe_dump(inventory))
            (folder / "vars.json").write_text(json.dumps(variables))
            state_path = folder / "state.json"
            state_path.write_text(json.dumps(dict(calls=[], **scenario)))
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                               ANSIBLE_NOCOLOR="1", ANSIBLE_FORCE_COLOR="0",
                               ANSIBLE_LOCAL_TEMP=str(folder / "local"),
                               ANSIBLE_REMOTE_TEMP=str(folder / "remote"),
                               SNIPER_CHECKPOINT_STATE=str(state_path),
                               SATELLITE_USERNAME="fixture", SATELLITE_PASSWORD=PASSWORD,
                               SATELLITE_SERVER_URL=variables["sniper_server_url"])
            command = ["ansible-playbook", "-i", str(folder / "inventory.yml"), str(source / entry),
                       "-e", "@" + str(folder / "vars.json"), "-vv"]
            if check:
                command.append("--check")
            if limit:
                command += ["--limit", limit]
            result = subprocess.run(command, cwd=source, env=environment, text=True, capture_output=True, timeout=180)
            state = json.loads(state_path.read_text())
            state["remaining_pins"] = [call["pin"] for call in state["calls"]
                                       if call.get("pin") and Path(call["pin"]).exists()]
            state["remaining_cas"] = list((folder / "local").rglob("*-sniper-satellite-ca.pem"))
            return result, state

    def check_result(self, result, state, success):
        self.assertEqual(result.returncode == 0, success, (result.stdout + result.stderr)[-14000:])
        self.assertNotIn(PASSWORD, result.stdout + result.stderr)
        self.assertEqual(state["remaining_pins"], [])
        self.assertEqual(state["remaining_cas"], [])

    @staticmethod
    def operations(state):
        return [json.loads(c["arguments"]["stdin"])["op"] for c in state["calls"] if c["kind"] == "helper"]

    def test_pristine_capture_orders_freshness_before_capture_and_readiness(self):
        result, state = self.run_play()
        self.check_result(result, state, True)
        self.assertEqual(self.operations(state), ["inspect", "create"])
        self.assertEqual([c["kind"] for c in state["calls"]], ["helper", "uri", "uri", "helper", "uri"])
        self.assertIn("sniper_new_checkpoint_result", result.stdout)

    def test_valid_owned_checkpoint_reuse_needs_no_new_installation_or_freshness_claim(self):
        result, state = self.run_play(exists=True, missing_install=True, repositories=2, syncs=23)
        self.check_result(result, state, True)
        self.assertEqual(self.operations(state), ["inspect", "create"])
        self.assertEqual(sum(c["kind"] == "uri" for c in state["calls"]), 1)

    def test_dirty_ambiguous_or_foreign_state_stops_before_capture(self):
        for scenario in ({"repositories": 2}, {"syncs": 23}, {"repositories": "0"}, {"foreign": True}):
            with self.subTest(scenario=scenario):
                result, state = self.run_play(**scenario)
                self.check_result(result, state, False)
                self.assertEqual(self.operations(state), ["inspect"])

    def test_installation_proof_is_required_for_new_capture(self):
        for scenario in ({"missing_install": True}, {"wrong_install": True}):
            with self.subTest(scenario=scenario):
                result, state = self.run_play(**scenario)
                self.check_result(result, state, False)
                self.assertEqual(self.operations(state), ["inspect"])

    def test_check_mode_reads_freshness_and_cleans_trust_without_capture(self):
        result, state = self.run_play(check=True, missing_install=True)
        self.check_result(result, state, True)
        self.assertEqual(self.operations(state), ["inspect"])
        self.assertIn("sniper_new_checkpoint_preflight", result.stdout)
        self.assertNotIn("sniper_new_checkpoint_result", result.stdout)

    def test_unknown_capture_is_visible_and_never_retried_or_followed_by_api(self):
        for scenario in ({"unknown": True}, {"malformed": True}, {"malformed_zero": True}):
            with self.subTest(scenario=scenario):
                result, state = self.run_play(**scenario)
                self.check_result(result, state, False)
                self.assertEqual(self.operations(state), ["inspect", "create"])
                self.assertIn("outcome is UNKNOWN", result.stdout)
                self.assertEqual(sum(c["kind"] == "uri" for c in state["calls"]), 2)

    def test_unready_restart_cannot_report_success(self):
        result, state = self.run_play(unready=True)
        self.check_result(result, state, False)
        self.assertNotIn('"sniper_new_checkpoint_result":', result.stdout)

    def test_final_guest_identity_and_trust_are_bound_to_the_installation(self):
        for scenario in ({}, {"wrong_uuid": True}, {"wrong_machine": True}, {"wrong_ca": True}):
            with self.subTest(scenario=scenario):
                result, state = self.run_play("verify_satellite_checkpoint.yml", **scenario)
                self.check_result(result, state, not scenario)
                if not scenario:
                    self.assertIn("sniper_new_checkpoint_installation_verified", result.stdout)

    def test_initial_content_requires_this_execution_native_checkpoint_gate(self):
        for scenario in ({"exists": True}, {}, {"exists": True, "stopped": True}, {"exists": True, "foreign": True}):
            with self.subTest(scenario=scenario):
                result, state = self.run_play("configure_satellite_content.yml", **scenario)
                success = scenario == {"exists": True}
                self.check_result(result, state, success)
                self.assertEqual(any(c["kind"] == "content" for c in state["calls"]), success)
                self.assertNotIn("create", self.operations(state))

    def test_missing_or_mismatched_final_guest_verification_blocks_content(self):
        for scenario in ({"missing_final": True}, {"wrong_final_uuid": True}, {"wrong_final_ca": True}):
            with self.subTest(scenario=scenario):
                result, state = self.run_play("configure_satellite_content.yml", exists=True, **scenario)
                self.check_result(result, state, False)
                self.assertFalse(any(c["kind"] == "content" for c in state["calls"]))
                self.assertEqual(self.operations(state), ["verify"])

    def test_excluding_hypervisor_cannot_bypass_the_content_gate(self):
        result, state = self.run_play("configure_satellite_content.yml", limit="localhost", exists=True)
        self.check_result(result, state, False)
        self.assertEqual(state["calls"], [])


if __name__ == "__main__":
    unittest.main()
