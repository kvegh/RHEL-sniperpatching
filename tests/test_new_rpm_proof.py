"""NEW-only regressions for retained standard-kernel module builds.

The RPM database/comparator are synthetic here. The production helper still uses
native librpm and records every installed EVR, including retained fallback builds.
Reason and test scope: ../docs/implementation.md#native-rpm-proof
"""

import unittest

from track_paths import TRACK
from test_sniper import ADVISORY, FakeRPM, fixed, installed, proof


MODULE_NAMES = ("kernel-modules", "kernel-modules-core")
KERNEL_NAMES = ("kernel", "kernel-core") + MODULE_NAMES
VERSION = "5.14.0"
OLD_RELEASE = "427.22.1.el9_4"
PREVIOUS_RELEASE = "427.24.1.el9_4"
FIXED_RELEASE = "427.31.1.el9_4"
NEWER_RELEASE = "427.32.1.el9_4"


def kernel_fixed(name, **fields):
    return fixed(name, VERSION, FIXED_RELEASE, **fields)


def kernel_installed(name, release=FIXED_RELEASE, **fields):
    return installed(name, VERSION, release, **fields)


@unittest.skipUnless(TRACK == "new", "NEW-only standard kernel-module proof")
class KernelModuleProofTests(unittest.TestCase):
    def check(self, requirements, packages, release=FIXED_RELEASE):
        return proof.verify(
            requirements, rpm_module=FakeRPM(packages),
            running_release=VERSION + "-" + release + ".x86_64",
            options={"requested_id": ADVISORY},
        )

    def test_fixed_running_kernel_and_modules_keep_old_fallback_rpms(self):
        requirements = [kernel_fixed(name) for name in KERNEL_NAMES]
        packages = [
            kernel_installed(name, release)
            for name in KERNEL_NAMES
            for release in (OLD_RELEASE, PREVIOUS_RELEASE, FIXED_RELEASE)
        ]
        result = self.check(requirements, packages)
        self.assertTrue(result["verified"])
        self.assertTrue(result["requested"][ADVISORY]["verified"])
        self.assertTrue(result["running_kernel_fixed"])
        self.assertFalse(result["requires_kernel_reboot"])
        self.assertEqual(result["mismatches"], [])
        for record in result["affected_packages"]:
            self.assertTrue(record["running_kernel_fixed"])
            self.assertEqual(len(record["installed"]), 3)
            self.assertIn("0:" + VERSION + "-" + OLD_RELEASE, record["installed"])
            self.assertIn("0:" + VERSION + "-" + PREVIOUS_RELEASE, record["installed"])

    def test_newer_fixed_module_does_not_fix_an_old_or_unmatched_running_release(self):
        for name in MODULE_NAMES:
            for running in (PREVIOUS_RELEASE, NEWER_RELEASE):
                with self.subTest(name=name, running=running):
                    result = self.check(
                        [kernel_fixed(name)],
                        [kernel_installed(name, PREVIOUS_RELEASE), kernel_installed(name)],
                        release=running,
                    )
                    self.assertFalse(result["verified"])
                    self.assertFalse(result["running_kernel_fixed"])
                    self.assertTrue(result["requires_kernel_reboot"])
                    self.assertIn("fixed_kernel_not_running",
                                  [item["reason"] for item in result["mismatches"]])

    def test_fixed_kernel_cannot_substitute_for_missing_matching_module_build(self):
        for missing in MODULE_NAMES:
            with self.subTest(missing=missing):
                packages = [kernel_installed(name) for name in KERNEL_NAMES if name != missing]
                packages += [kernel_installed(missing, PREVIOUS_RELEASE),
                             kernel_installed(missing, NEWER_RELEASE)]
                result = self.check([kernel_fixed(name) for name in KERNEL_NAMES], packages)
                self.assertFalse(result["verified"])
                record = next(row for row in result["affected_packages"] if row["name"] == missing)
                self.assertFalse(record["verified"])
                self.assertFalse(record["running_kernel_fixed"])
                self.assertTrue(result["requires_kernel_reboot"])

    def test_module_matching_release_must_also_pass_rpm_epoch_comparison(self):
        for name in MODULE_NAMES:
            with self.subTest(name=name):
                result = self.check([kernel_fixed(name, epoch="1")], [kernel_installed(name)])
                self.assertFalse(result["verified"])
                self.assertFalse(result["running_kernel_fixed"])
                self.assertFalse(result["requires_kernel_reboot"])
                self.assertIn("installed_version_below_fix",
                              [item["reason"] for item in result["mismatches"]])

    def test_missing_fixed_module_requires_package_fix_before_reboot(self):
        for name in MODULE_NAMES:
            with self.subTest(name=name):
                result = self.check([kernel_fixed(name)], [kernel_installed(name, PREVIOUS_RELEASE)])
                self.assertFalse(result["verified"])
                self.assertFalse(result["requires_kernel_reboot"])
                self.assertIn("installed_version_below_fix",
                              [item["reason"] for item in result["mismatches"]])

    def test_userspace_tools_and_unlisted_kernel_names_remain_all_version_strict(self):
        for name in ("demo", "kernel-tools", "kernel-tools-libs", "kernel-headers",
                     "kernel-modules-extra", "kernel-modules-unknown", "kernel-custom-modules"):
            with self.subTest(name=name):
                result = self.check(
                    [kernel_fixed(name)],
                    [kernel_installed(name, PREVIOUS_RELEASE), kernel_installed(name)],
                )
                self.assertFalse(result["verified"])
                self.assertIn("installed_version_below_fix",
                              [item["reason"] for item in result["mismatches"]])
                self.assertNotIn("running_kernel_fixed", result["affected_packages"][0])

    def test_additional_installed_module_architectures_are_never_ignored(self):
        for name in MODULE_NAMES:
            for include_fixed_metadata in (False, True):
                with self.subTest(name=name, include_fixed_metadata=include_fixed_metadata):
                    requirements = [kernel_fixed(name)]
                    if include_fixed_metadata:
                        requirements.append(kernel_fixed(name, arch="i686"))
                    packages = [kernel_installed(name),
                                kernel_installed(name, PREVIOUS_RELEASE, arch="i686")]
                    result = self.check(requirements, packages)
                    self.assertFalse(result["verified"])
                    reason = ("installed_version_below_fix" if include_fixed_metadata
                              else "installed_architecture_missing_fixed_metadata")
                    self.assertIn(reason, [item["reason"] for item in result["mismatches"]])


if __name__ == "__main__":
    unittest.main()
