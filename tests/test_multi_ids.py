"""Multiple survey CVEs must all resolve live and receive independent proof."""
# Reason and test scope: ../docs/implementation.md#source-and-caller-inventory

import json
from pathlib import Path
import unittest
from test_sniper import ADVISORY, OTHER, CVE, FakeRPM, filters, fixed, installed, proof

CVE2 = "CVE-2026-12346"


def query(ident, *advisories):
    return {"item": [{"id": 7, "name": "Example"}, ident],
            "resources": [{"id": i + 1, "errata_id": a} for i, a in enumerate(advisories)]}


class MultipleSurveyIds(unittest.TestCase):
    def test_normalizes_comma_space_newline_and_duplicate_cves(self):
        self.assertEqual(
            filters.sniper_patch_ids(" cve-2026-12346,\n" + CVE + " " + CVE),
            [CVE, CVE2],
        )
        self.assertEqual(filters.sniper_patch_ids(" " + ADVISORY.lower()), [ADVISORY])

    def test_rejects_invalid_expressions_and_unsupported_mixtures(self):
        for value in (
            None, True, 3, "", CVE + ";id", CVE + " or " + CVE2,
            ADVISORY + " " + OTHER, ADVISORY + "," + CVE, "x" * 4097,
            " ".join("CVE-2026-%04d" % i for i in range(1000, 1051)),
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                filters.sniper_patch_ids(value)

    def test_resolves_each_input_and_deduplicates_shared_advisories(self):
        result = filters.sniper_resolve_queries(
            [query(CVE, ADVISORY, OTHER), query(CVE2, OTHER), query(CVE, ADVISORY)],
            [CVE, CVE2],
        )
        self.assertEqual(result["by_input"], {CVE: [ADVISORY, OTHER], CVE2: [OTHER]})
        self.assertEqual(len(result["advisories"]), 2)

    def test_one_unresolved_cve_fails_even_when_another_resolves(self):
        with self.assertRaisesRegex(ValueError, CVE2):
            filters.sniper_resolve_queries(
                [query(CVE, ADVISORY), query(CVE2)], [CVE, CVE2]
            )

    def test_non_security_or_wrong_rhsa_results_are_refused(self):
        for result, requested in (
            (query(CVE, "RHBA-2026:12345"), [CVE]),
            (query(ADVISORY, OTHER), [ADVISORY]),
            ({"resources": []}, [CVE]),
        ):
            with self.subTest(result=result), self.assertRaises(ValueError):
                filters.sniper_resolve_queries([result], requested)

    def test_full_live_details_must_confirm_each_cve_association(self):
        mapping = {CVE: [ADVISORY], CVE2: [OTHER]}
        details = [
            {"errata_id": ADVISORY, "cves": [{"cve_id": CVE}]},
            {"errata_id": OTHER, "cves": [{"cve_id": CVE2}]},
        ]
        self.assertEqual(filters.sniper_validate_resolution(mapping, details), mapping)
        details[1]["cves"] = [{"cve_id": CVE}]
        with self.assertRaisesRegex(ValueError, "do not confirm"):
            filters.sniper_validate_resolution(mapping, details)

    def test_actual_survey_field_is_free_text_with_no_static_cve_choices(self):
        path = Path(__file__).resolve().parents[1] / "surveys/patch-selection.json"
        survey = json.loads(path.read_text())
        field = next(q for q in survey["spec"] if q["variable"] == "sniper_patch_id")
        self.assertEqual(field["type"], "textarea")
        self.assertTrue(field["required"])
        self.assertEqual(field["choices"], "")
        self.assertEqual(field["max"], 4096)
        self.assertEqual(filters.sniper_patch_ids(CVE + "\n" + CVE2), [CVE, CVE2])


class PerCveProof(unittest.TestCase):
    def verify(self, packages, mapping=None):
        requirements = [fixed(), fixed("other", advisory=OTHER)]
        return proof.verify(
            requirements, rpm_module=FakeRPM(packages), running_release="irrelevant",
            options={"requested_id": CVE + ", " + CVE2,
                     "advisory_map": mapping or {CVE: [ADVISORY], CVE2: [OTHER]}},
        )

    def test_every_requested_cve_is_proven(self):
        result = self.verify([installed(), installed("other")])
        self.assertTrue(result["verified"])
        self.assertEqual(result["requested_ids"], [CVE, CVE2])
        self.assertTrue(all(row["verified"] for row in result["requested"].values()))

    def test_one_fixed_cve_cannot_mask_an_absent_component_for_another(self):
        result = self.verify([installed()])
        self.assertFalse(result["verified"])
        self.assertTrue(result["requested"][CVE]["verified"])
        self.assertFalse(result["requested"][CVE2]["verified"])
        self.assertIn({"requested_id": CVE2, "reason": "no_affected_installed_packages_for_cve"},
                      result["mismatches"])

    def test_one_fixed_cve_cannot_mask_an_unfixed_component(self):
        result = self.verify([installed(), installed("other", version="1.0")])
        self.assertFalse(result["verified"])
        self.assertFalse(result["requested"][CVE2]["verified"])

    def test_two_cves_may_share_the_same_verified_advisory(self):
        result = proof.verify(
            [fixed()], rpm_module=FakeRPM([installed()]), running_release="irrelevant",
            options={"requested_id": CVE + " " + CVE2,
                     "advisory_map": {CVE: [ADVISORY], CVE2: [ADVISORY]}},
        )
        self.assertTrue(result["verified"])

    def test_incomplete_or_extra_live_mapping_cannot_reach_rpm_proof(self):
        for mapping in (
            None, {CVE: [ADVISORY]}, {CVE: [], CVE2: [OTHER]},
            {CVE: [ADVISORY], CVE2: ["RHSA-2026:99999"]},
            {CVE: [ADVISORY], CVE2: [ADVISORY]},
        ):
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                proof.verify(
                    [fixed(), fixed("other", advisory=OTHER)],
                    rpm_module=FakeRPM([]), running_release="irrelevant",
                    options={"requested_id": CVE + "," + CVE2, "advisory_map": mapping},
                )


if __name__ == "__main__":
    unittest.main()
