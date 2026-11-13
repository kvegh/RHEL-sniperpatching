"""Prevent advisory NVRA strings from silently inventing epoch zero."""
# Reason and test scope: ../docs/implementation.md#source-and-caller-inventory

import unittest
from pathlib import Path
from track_paths import TRACK_ROOT
import yaml
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.loader import filter_loader
from ansible.template import Templar

# Trust only expressions read from repository task YAML, never fixture data.
try:
    from ansible.template import trust_as_template
except ImportError:  # Core 2.16 predates explicit template trust.
    def trust_as_template(value):
        return value
from test_sniper import ADVISORY, FakeRPM, filters, fixed, installed, proof


class AdvisoryEpochs(unittest.TestCase):
    def detail(self, package="demo-2.0-1.el7.x86_64"):
        return {"errata_id": ADVISORY, "packages": [package]}

    def test_omitted_epoch_needs_exact_repository_metadata(self):
        for package in (
            "demo-2.0-1.el7.x86_64",
            {"filename": "demo-2.0-1.el7.x86_64.rpm"},
            {k: v for k, v in installed().items() if k != "epoch"},
        ):
            with self.subTest(package=package), self.assertRaisesRegex(
                ValueError, "authoritative RPM epoch"
            ):
                filters.sniper_package_requirements(self.detail(package))

    def test_explicit_null_epoch_is_authoritative_zero(self):
        self.assertEqual(
            filters.sniper_package_requirements(self.detail(), [installed(epoch=None)]),
            [fixed()],
        )

    def test_higher_installed_epoch_cannot_hide_an_old_release(self):
        for epoch in (1, 12, 32):
            with self.subTest(epoch=epoch):
                rpm = FakeRPM([installed(version="1.0", epoch=epoch)])
                requirements = filters.sniper_package_requirements(
                    self.detail(), [installed(epoch=epoch)]
                )
                self.assertEqual(requirements[0]["epoch"], str(epoch))
                result = proof.verify(
                    requirements, rpm_module=rpm, running_release="irrelevant"
                )
                self.assertFalse(result["verified"])
                self.assertTrue(all(a[0] == b[0] for a, b in rpm.comparisons))

    def test_unrelated_package_identity_does_not_supply_epoch(self):
        for key, value in (
            ("version", "3.0"),
            ("release", "2.el7"),
            ("arch", "i686"),
            ("name", "other"),
        ):
            row = dict(installed(epoch=1), **{key: value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                filters.sniper_package_requirements(self.detail(), [row])

    def test_duplicate_matches_are_ok_but_conflicting_epochs_fail(self):
        row = installed(epoch=1)
        self.assertEqual(
            filters.sniper_package_requirements(self.detail(), [row, row]),
            [fixed(epoch="1")],
        )
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            filters.sniper_package_requirements(
                self.detail(), [row, installed(epoch=2)]
            )

    def test_missing_catalogue_epoch_and_conflicting_explicit_epoch_fail(self):
        row = installed(epoch=1)
        del row["epoch"]
        with self.assertRaisesRegex(ValueError, "explicit RPM epoch"):
            filters.sniper_package_requirements(self.detail(), [row])
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            filters.sniper_package_requirements(
                self.detail("demo-1:2.0-1.el7.x86_64"), [installed(epoch=2)]
            )

    def test_host_proof_refuses_requirements_without_epoch(self):
        requirement = fixed()
        del requirement["epoch"]
        with self.assertRaisesRegex(ValueError, "authoritative RPM epoch"):
            proof.verify([requirement], rpm_module=FakeRPM([installed()]))

    def test_filename_searches_are_exact_deduplicated_and_bounded(self):
        details = self.detail()
        details["packages"] = [
            "demo%s-1:2.0-1.el7.x86_64" % i for i in range(100)
        ]
        queries = filters.sniper_package_searches([details, details])
        self.assertGreater(len(queries), 1)
        self.assertTrue(all(len(q) <= 2000 for q in queries))
        self.assertEqual(sum(q.count("filename = ") for q in queries), 100)
        self.assertTrue(all(":2.0" not in q and ".rpm" in q for q in queries))


    def test_resolver_templates_query_each_repository_and_use_its_results(self):
        root = TRACK_ROOT
        tasks = yaml.safe_load((root / "tasks/resolve.yml").read_text())
        filter_loader.add_directory(str(root / "filter_plugins"))
        variables = {
            "sniper_advisory_details": [self.detail()],
            "sniper_repo_details": [{"id": 7, "name": "alpha"}, {"id": 8, "name": "beta"}],
            "sniper_organization": "Example",
            "sniper_package_queries": {
                "results": [{"resources": [installed(epoch=1)]}, {"resources": []}]
            },
        }
        templar = Templar(loader=DataLoader(), variables=variables)
        search = next(
            t for t in tasks
            if t["name"] == "Build bounded exact package searches"
        )
        variables["sniper_package_searches"] = templar.template(
            trust_as_template(search["ansible.builtin.set_fact"]["sniper_package_searches"])
        )
        templar = Templar(loader=DataLoader(), variables=variables)
        query = next(
            t for t in tasks if "redhat.satellite.resource_info" in t
            and t["redhat.satellite.resource_info"]["resource"] == "packages"
        )
        pairs = templar.template(trust_as_template(query["loop"]))
        self.assertEqual([pair[0]["id"] for pair in pairs], [7, 8])
        for pair in pairs:
            rendered = Templar(
                loader=DataLoader(), variables=dict(variables, item=pair)
            ).template({
                **query["redhat.satellite.resource_info"],
                "params": {key: trust_as_template(value)
                           for key, value in query["redhat.satellite.resource_info"]["params"].items()},
                "search": trust_as_template(query["redhat.satellite.resource_info"]["search"]),
                "organization": trust_as_template(query["redhat.satellite.resource_info"]["organization"]),
            })
            self.assertEqual(int(rendered["params"]["repository_id"]), pair[0]["id"])
            self.assertEqual(
                rendered["search"], 'filename = "demo-2.0-1.el7.x86_64.rpm"'
            )
        expression = tasks[-1]["ansible.builtin.set_fact"]["sniper_requirements"]
        self.assertEqual(templar.template(trust_as_template(expression)), [fixed(epoch="1")])

    def test_empty_and_contradictory_embedded_epochs_fail(self):
        for package in (
            dict(installed(), epoch=""),
            {"nevra": "demo-1:2.0-1.el7.x86_64", "epoch": 2},
        ):
            with self.subTest(package=package), self.assertRaises(ValueError):
                filters.sniper_package_requirements(self.detail(package))


if __name__ == "__main__":
    unittest.main()
