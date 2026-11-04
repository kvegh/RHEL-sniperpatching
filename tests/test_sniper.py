"""Offline contracts for metadata parsing and native-RPM proof decisions."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


filters = load("sniper_filters", ROOT / "filter_plugins/sniper.py")
proof = load("rpm_proof", ROOT / "files/rpm_proof.py")
ADVISORY = "RHSA-2026:12345"
OTHER = "RHSA-2026:12346"
CVE = "CVE-2026-12345"


def fixed(
    name="demo",
    version="2.0",
    release="1.el7",
    epoch="0",
    arch="x86_64",
    advisory=ADVISORY,
):
    return dict(
        advisory=advisory,
        name=name,
        epoch=epoch,
        version=version,
        release=release,
        arch=arch,
    )


def installed(name="demo", version="2.0", release="1.el7", epoch=None, arch="x86_64"):
    return dict(name=name, epoch=epoch, version=version, release=release, arch=arch)


class FakeRPM:
    """Numeric fixture ranks only; production comparison always calls librpm."""

    def __init__(self, packages):
        self.packages = packages
        self.comparisons = []

    def TransactionSet(self):
        return self

    def dbMatch(self, tag, name):
        if tag != "name":
            raise AssertionError("Proof must query exact package name")
        return [p for p in self.packages if p["name"] == name]

    def labelCompare(self, left, right):
        self.comparisons.append((left, right))

        def rank(label):
            return (
                int(label[0]),
                tuple(map(int, re.findall(r"[0-9]+", label[1]))),
                tuple(map(int, re.findall(r"[0-9]+", label[2]))),
            )

        return (rank(left) > rank(right)) - (rank(left) < rank(right))


class MetadataTests(unittest.TestCase):
    def test_normalizes_single_identifier(self):
        self.assertEqual(filters.sniper_patch_id(" rhsa-2026:12345 "), ADVISORY)
        self.assertEqual(filters.sniper_patch_id("cve-2026-12345"), CVE)

    def test_rejects_identifiers_that_are_expressions_or_commands(self):
        for value in [
            None,
            1,
            True,
            "",
            "RHSA-2026:12345;id",
            "CVE-2026-12345 or id=1",
            "RHSA-2026:12345\nRHSA-2026:12346",
            "RHBA-2026:12345",
            "CVE-26-12345",
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                filters.sniper_patch_id(value)

    def test_structured_satellite_package_and_epoch(self):
        detail = {"errata_id": ADVISORY, "packages": [installed(epoch="2")]}
        self.assertEqual(
            filters.sniper_package_requirements(detail), [fixed(epoch="2")]
        )

    def test_nevra_and_filename_metadata(self):
        rows = filters.sniper_package_requirements(
            [
                {
                    "uuid": ADVISORY,
                    "packages": [
                        "demo-tools-2:3.0-4.el7.x86_64.rpm",
                        {"nvra": "demo-libs-3.0-4.el7.i686", "epoch": 2},
                        {"filename": "demo-doc-3.0-4.el7.noarch.rpm"},
                    ],
                }
            ],
            [installed("demo-doc", "3.0", "4.el7", epoch=None, arch="noarch")],
        )
        self.assertEqual(rows[0], fixed("demo-tools", "3.0", "4.el7", "2"))
        self.assertEqual(rows[1], fixed("demo-libs", "3.0", "4.el7", "2", "i686"))
        self.assertEqual(rows[2], fixed("demo-doc", "3.0", "4.el7", "0", "noarch"))

    def test_deduplicates_binary_metadata_and_ignores_source(self):
        d = {
            "errata_id": ADVISORY,
            "packages": [
                "demo-0:2.0-1.el7.x86_64.rpm",
                "demo-0:2.0-1.el7.x86_64.rpm",
                "demo-2.0-1.el7.src.rpm",
            ],
        }
        self.assertEqual(
            filters.sniper_package_requirements({"results": [d]}), [fixed()]
        )

    def test_retains_advisory_identity_for_same_package(self):
        rows = filters.sniper_package_requirements(
            [
                {"errata_id": a, "packages": ["demo-0:2.0-1.el7.x86_64"]}
                for a in [ADVISORY, OTHER]
            ]
        )
        self.assertEqual({x["advisory"] for x in rows}, {ADVISORY, OTHER})

    def test_missing_empty_source_only_and_modular_metadata_fail(self):
        for d in [
            [],
            {},
            {"errata_id": ADVISORY},
            {"errata_id": ADVISORY, "packages": []},
            {"errata_id": ADVISORY, "packages": ["demo-2.0-1.el7.src"]},
            {
                "errata_id": ADVISORY,
                "packages": [],
                "module_streams": [{"name": "demo"}],
            },
        ]:
            with self.subTest(detail=d), self.assertRaises(ValueError):
                filters.sniper_package_requirements(d)

    def test_rejects_unsafe_package_fields_and_paths(self):
        for package in [
            "demo-2.0-1.el7.x86_64;id",
            "/tmp/demo-2.0-1.el7.x86_64.rpm",
            "demo-2.0-1.el7.x86_64\n",
            {
                "name": "demo;id",
                "epoch": 0,
                "version": "2",
                "release": "1",
                "arch": "x86_64",
            },
        ]:
            with self.subTest(package=package), self.assertRaises(ValueError):
                filters.sniper_package_requirements(
                    {"errata_id": ADVISORY, "packages": [package]}
                )

    def test_inventory_delta_reports_changes_without_claiming_direction(self):
        before = ["demo|0|1.0|1.el7|x86_64", "gone|0|1.0|1.el7|x86_64"]
        after = ["demo|0|2.0|1.el7|x86_64", "added|0|1.0|1.el7|noarch"]
        self.assertEqual(
            filters.sniper_package_delta(before, after), ["added", "demo", "gone"]
        )
        self.assertEqual(
            filters.sniper_package_delta(after, "\n".join(reversed(after))), []
        )

    def test_invalid_inventory_fails(self):
        with self.assertRaises(ValueError):
            filters.sniper_package_delta(["not-a-valid-snapshot"], [])


class ProofTests(unittest.TestCase):
    def check(
        self, requirements, packages, running="3.10.0-2.el7.x86_64", options=None
    ):
        rpm = FakeRPM(packages)
        return (
            proof.verify(
                requirements, rpm_module=rpm, running_release=running, options=options
            ),
            rpm,
        )

    def test_exact_fixed_and_superseded_versions_pass(self):
        for version in ["2.0", "3.0"]:
            r, rpm = self.check([fixed()], [installed(version=version)])
            self.assertTrue(r["verified"])
            self.assertEqual(r["affected_names"], ["demo"])
            self.assertTrue(rpm.comparisons)

    def test_epoch_precedence_uses_native_rpm_comparison(self):
        r, rpm = self.check(
            [fixed(version="99.0")], [installed(version="1.0", epoch=1)]
        )
        self.assertTrue(r["verified"])
        self.assertTrue(any(a[0] == "1" and b[0] == "0" for a, b in rpm.comparisons))

    def test_vulnerable_installed_version_fails(self):
        r, _ = self.check([fixed()], [installed(version="1.0")])
        self.assertFalse(r["verified"])
        self.assertEqual(r["mismatches"][0]["reason"], "installed_version_below_fix")

    def test_absent_rhsa_is_not_an_empty_success(self):
        r, _ = self.check([fixed()], [], options={"requested_id": ADVISORY})
        self.assertFalse(r["verified"])
        self.assertEqual(r["mismatches"][0]["reason"], "no_affected_installed_packages")

    def test_uninstalled_optional_packages_are_not_required(self):
        r, _ = self.check([fixed(), fixed("demo-devel")], [installed()])
        self.assertTrue(r["verified"])

    def test_all_installed_multilib_architectures_must_be_fixed(self):
        r, _ = self.check(
            [fixed(), fixed(arch="i686")],
            [installed(), installed(version="1.0", arch="i686")],
        )
        self.assertFalse(r["verified"])

    def test_unknown_installed_architecture_fails_closed(self):
        r, _ = self.check([fixed()], [installed(arch="i686")])
        self.assertFalse(r["verified"])
        self.assertEqual(
            r["mismatches"][0]["reason"],
            "installed_architecture_missing_fixed_metadata",
        )

    def test_duplicate_vulnerable_non_kernel_version_does_not_pass(self):
        r, _ = self.check([fixed()], [installed(version="1.0"), installed()])
        self.assertFalse(r["verified"])

    def test_old_installonly_kernels_do_not_fail_fixed_running_kernel(self):
        r, _ = self.check(
            [fixed("kernel", "3.10.0", "2.el7")],
            [
                installed("kernel", "3.10.0", "1.el7"),
                installed("kernel", "3.10.0", "2.el7"),
            ],
        )
        self.assertTrue(r["verified"])
        self.assertTrue(r["running_kernel_fixed"])
        self.assertFalse(r["requires_kernel_reboot"])

    def test_fixed_kernel_installed_but_old_running_kernel_requires_reboot(self):
        r, _ = self.check(
            [fixed("kernel", "3.10.0", "2.el7")],
            [
                installed("kernel", "3.10.0", "1.el7"),
                installed("kernel", "3.10.0", "2.el7"),
            ],
            running="3.10.0-1.el7.x86_64",
        )
        self.assertFalse(r["verified"])
        self.assertFalse(r["running_kernel_fixed"])
        self.assertTrue(r["requires_kernel_reboot"])

    def test_missing_fixed_kernel_needs_patch_before_reboot(self):
        r, _ = self.check(
            [fixed("kernel", "3.10.0", "2.el7")],
            [installed("kernel", "3.10.0", "1.el7")],
            running="3.10.0-1.el7.x86_64",
        )
        self.assertFalse(r["verified"])
        self.assertFalse(r["requires_kernel_reboot"])

    def test_cve_ignores_absent_components_and_marks_not_applicable(self):
        r, _ = self.check(
            [fixed(), fixed("other", advisory=OTHER)],
            [installed()],
            options={"requested_id": CVE, "advisory_map": {CVE: [ADVISORY, OTHER]}},
        )
        self.assertTrue(r["verified"])
        self.assertTrue(r["advisories"][OTHER]["not_applicable"])
        self.assertEqual(r["advisories"][OTHER]["mismatches"], [])

    def test_cve_all_absent_fails(self):
        r, _ = self.check(
            [fixed(), fixed("other", advisory=OTHER)], [], options={"requested_id": CVE, "advisory_map": {CVE: [ADVISORY, OTHER]}}
        )
        self.assertFalse(r["verified"])
        self.assertTrue(all(x["not_applicable"] for x in r["advisories"].values()))

    def test_cve_other_installed_vulnerable_component_fails(self):
        r, _ = self.check(
            [fixed(), fixed("other", advisory=OTHER)],
            [installed(), installed("other", version="1.0")],
            options={"requested_id": CVE, "advisory_map": {CVE: [ADVISORY, OTHER]}},
        )
        self.assertFalse(r["verified"])
        self.assertFalse(r["advisories"][OTHER]["verified"])

    def test_invalid_or_mismatched_requested_id_fails(self):
        for requested in ["bad-id", OTHER]:
            with self.subTest(requested=requested), self.assertRaises(ValueError):
                self.check(
                    [fixed()], [installed()], options={"requested_id": requested}
                )

    def test_malformed_requirements_fail_before_rpm_queries(self):
        for reqs in [
            [],
            {},
            [dict(fixed(), name="demo;id")],
            [dict(fixed(), epoch=-1)],
        ]:
            with self.subTest(requirements=reqs), self.assertRaises(ValueError):
                self.check(reqs, [])

    def test_independent_witness_uses_matching_preexisting_arch(self):
        r, _ = self.check(
            [fixed()],
            [installed(), installed("other", version="2.0")],
            options={
                "requested_id": ADVISORY,
                "name": "other",
                "before": ["other|0|1.0|1.el7|x86_64"],
            },
        )
        self.assertTrue(r["verified"])
        self.assertTrue(r["upgrade_witness"]["upgraded"])
        self.assertTrue(r["upgrade_witness"]["independent"])

    def test_witness_rejects_addition_removal_downgrade_arch_switch(self):
        cases = [
            ([], [installed("other")]),
            (["other|0|1.0|1.el7|x86_64"], []),
            (["other|0|3.0|1.el7|x86_64"], [installed("other", version="2.0")]),
            (
                ["other|0|1.0|1.el7|x86_64"],
                [installed("other", version="2.0", arch="i686")],
            ),
        ]
        for before, packages in cases:
            with self.subTest(before=before, packages=packages):
                r, _ = self.check(
                    [fixed()],
                    [installed()] + packages,
                    options={"name": "other", "before": before},
                )
                self.assertTrue(r["verified"])
                self.assertFalse(r["upgrade_witness"]["upgraded"])

    def test_target_fix_cannot_be_independent_witness(self):
        r, _ = self.check(
            [fixed()],
            [installed()],
            options={"name": "demo", "before": ["demo|0|1.0|1.el7|x86_64"]},
        )
        self.assertTrue(r["verified"])
        self.assertFalse(r["upgrade_witness"]["upgraded"])
        self.assertFalse(r["upgrade_witness"]["independent"])

    def test_invalid_witness_snapshot_fails(self):
        with self.assertRaises(ValueError):
            self.check(
                [fixed()], [installed()], options={"name": "other", "before": ["bad"]}
            )

    def test_command_entrypoint_returns_json(self):
        out = io.StringIO()
        with patch.dict(
            sys.modules, {"rpm": FakeRPM([installed()])}
        ), contextlib.redirect_stdout(out):
            status = proof.main(
                [
                    "rpm_proof.py",
                    json.dumps([fixed()]),
                    json.dumps({"requested_id": ADVISORY}),
                ]
            )
        self.assertEqual(status, 0)
        self.assertTrue(json.loads(out.getvalue())["verified"])

    def test_command_entrypoint_bad_metadata_fails(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = proof.main(["rpm_proof.py", "[]"])
        self.assertEqual(status, 2)
        self.assertFalse(json.loads(out.getvalue())["verified"])


if __name__ == "__main__":
    unittest.main()
