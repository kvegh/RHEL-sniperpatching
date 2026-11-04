"""Validate cutoff selection from the entire host-pair security advisory set."""

import importlib.util
from pathlib import Path
import unittest
from ansible.errors import AnsibleFilterError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("baseline_content", ROOT / "filter_plugins/content.py")
content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content)
FIRST = "RHSA-2025:1234"
SECOND = "RHSA-2025:1235"


def rows():
    return [
        {"errata_id": FIRST, "issued": "2025-03-01", "updated": "2025-12-01"},
        {"errata_id": SECOND, "issued": "2025-05-01"},
    ]


class BaselineCutoff(unittest.TestCase):
    def test_pair_union_uses_issue_dates_and_ignores_non_security_errata(self):
        candidates = rows() + [rows()[0], {"errata_id": "RHBA-2025:1234"}]
        ids = content.baseline_ids(candidates)
        self.assertEqual(ids, [FIRST, SECOND])
        plan = content.baseline_plan(ids, rows())
        self.assertEqual(plan["cutoff"], "2025-02-28")
        self.assertEqual(plan["advisories"], [FIRST, SECOND])

    def test_leap_year_and_iso_timestamp(self):
        plan = content.baseline_plan(
            [FIRST], [{"errata_id": FIRST, "issued": "2024-03-01T00:00:00Z"}]
        )
        self.assertEqual(plan["cutoff"], "2024-02-29")

    def test_explicit_cutoff_must_precede_every_selected_advisory(self):
        self.assertEqual(
            content.baseline_plan([FIRST, SECOND], rows(), "2025-01-01")["cutoff"],
            "2025-01-01",
        )
        for cutoff in ("2025-03-01", "2025-04-01", "2025-02-30", "today", None):
            with self.subTest(cutoff=cutoff), self.assertRaises(AnsibleFilterError):
                content.baseline_plan([FIRST, SECOND], rows(), cutoff)

    def test_unavailable_or_ambiguous_advisory_metadata_stops_selection(self):
        for details in (
            rows()[1:],
            rows() + [{"errata_id": FIRST, "issued": "2025-03-02"}],
            [{"errata_id": FIRST, "updated": "2025-03-01"}],
        ):
            with self.subTest(details=details), self.assertRaises(AnsibleFilterError):
                content.baseline_plan([FIRST, SECOND], details)

    def test_recovery_keeps_the_recorded_cutoff(self):
        version = {"version": "1.0", "description":
                   "Initial demonstration baseline; cutoff=2025-01-01"}
        plan = content.baseline_plan([FIRST, SECOND], rows(), "", [version])
        self.assertEqual(plan["cutoff"], "2025-01-01")
        with self.assertRaisesRegex(AnsibleFilterError, "Cannot change"):
            content.baseline_plan([FIRST, SECOND], rows(), "2024-12-01", [version])

    def test_recovery_refuses_unidentifiable_or_unsafe_baselines(self):
        for versions in (
            [{"version": "1.0", "description": "foreign"}],
            [{"version": "1.0", "description": "Initial demonstration baseline; cutoff=none"}],
            [{"version": "1.0", "description": "Initial demonstration baseline; cutoff=2025-03-01"}],
            [{"version": "1.0"}, {"version": "2.0"}],
        ):
            with self.subTest(versions=versions), self.assertRaises(AnsibleFilterError):
                content.baseline_plan([FIRST, SECOND], rows(), "", versions)

    def test_empty_or_invalid_host_metadata_is_rejected(self):
        for value in ([], {}, [{"errata_id": "RHBA-2025:1234"}],
                      [{"errata_id": "RHSA-2025:1234;id"}], [{}]):
            with self.subTest(value=value), self.assertRaises(AnsibleFilterError):
                content.baseline_ids(value)

    def test_repository_queries_are_exact_bounded_and_deduplicated(self):
        ids = ["RHSA-2025:%04d" % i for i in range(1000, 1120)]
        searches = content.baseline_searches(ids + ids)
        self.assertEqual(len(searches), 3)
        self.assertTrue(all(len(q) < 2000 for q in searches))
        self.assertEqual(sum(q.count("errata_id = ") for q in searches), 120)


if __name__ == "__main__":
    unittest.main()
