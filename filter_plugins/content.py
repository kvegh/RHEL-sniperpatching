"""Small, pure validation helpers for Satellite content operations."""

import re
from datetime import date, timedelta
from ansible.errors import AnsibleFilterError


def one(rows, label="resource"):
    if not isinstance(rows, list) or len(rows) != 1:
        raise AnsibleFilterError(
            "Expected exactly one %s; got %s"
            % (label, len(rows) if isinstance(rows, list) else type(rows).__name__)
        )
    return rows[0]


def owned(rows, marker, label="resource"):
    for row in rows:
        if row.get("description") != marker:
            raise AnsibleFilterError(
                "Refusing to change an existing %s without the exact project ownership description"
                % label
            )
    return rows


def task_ids(response):
    rows = response if isinstance(response, list) else [response]
    ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if (
        not ids
        or len(ids) != len(rows)
        or any(
            not isinstance(x, str) or not re.fullmatch(r"[a-fA-F0-9-]{36}", x)
            for x in ids
        )
    ):
        raise AnsibleFilterError(
            "Incremental API did not return identifiable tasks; inspect Satellite before retrying"
        )
    return ids


def repo_options(labels):
    if not labels or any(
        not isinstance(x, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", x)
        for x in labels
    ):
        raise AnsibleFilterError(
            "Every selected repository must have an exact RHSM content label; globs are refused"
        )
    return ["--disablerepo=*"] + ["--enablerepo=" + x for x in sorted(set(labels))]


def initial_baseline(versions):
    version = one(versions, "recoverable initial baseline")
    if not (version.get("description") or "").startswith(
        "Initial demonstration baseline; cutoff="
    ):
        raise AnsibleFilterError(
            "Refusing to guess which version should initialize an empty environment"
        )
    return version


def baseline_ids(rows):
    """Union the outstanding security advisories reported by the explicit hosts."""
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise AnsibleFilterError("Expected host errata metadata")
    ids = set()
    for row in rows:
        ident = row.get("errata_id")
        if not isinstance(ident, str):
            raise AnsibleFilterError("Host erratum is missing its identifier")
        if ident.startswith("RHSA-"):
            if not re.fullmatch(r"RHSA-[0-9]{4}:[0-9]{4,}", ident):
                raise AnsibleFilterError("Invalid security advisory identifier")
            ids.add(ident)
    if not ids:
        raise AnsibleFilterError(
            "No outstanding security RHSAs on the selected hosts; cannot choose a demo baseline"
        )
    return sorted(ids)


def baseline_searches(ids):
    if not isinstance(ids, list):
        raise AnsibleFilterError("Expected security advisory identifiers")
    ids = baseline_ids([{"errata_id": ident} for ident in ids])
    return [
        " or ".join('errata_id = "%s"' % ident for ident in ids[start:start + 50])
        for start in range(0, len(ids), 50)
    ]


def _baseline_date(value, label, timestamp=False):
    if not isinstance(value, str):
        raise AnsibleFilterError("Missing or invalid " + label)
    text = value
    if timestamp and len(text) > 10 and text[10] == "T":
        text = text[:10]
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        raise AnsibleFilterError("Missing or invalid " + label)
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise AnsibleFilterError("Missing or invalid " + label) from exc


def baseline_plan(ids, repository_errata, requested_cutoff="", existing_versions=None):
    """Choose a frozen cutoff strictly before every selected security RHSA."""
    baseline_searches(ids)
    if not isinstance(repository_errata, list):
        raise AnsibleFilterError("Expected selected-repository errata metadata")
    dates = {ident: set() for ident in ids}
    for row in repository_errata:
        if not isinstance(row, dict):
            raise AnsibleFilterError("Expected selected-repository erratum details")
        if row.get("errata_id") in dates:
            dates[row["errata_id"]].add(
                _baseline_date(row.get("issued"), "advisory issue date", timestamp=True)
            )
    if any(len(values) != 1 for values in dates.values()):
        raise AnsibleFilterError(
            "A selected RHSA is unavailable in the selected repositories or has ambiguous issue dates"
        )
    earliest = min(next(iter(values)) for values in dates.values())
    explicit = (
        _baseline_date(requested_cutoff, "baseline cutoff")
        if requested_cutoff != "" else None
    )
    if existing_versions:
        recorded = initial_baseline(existing_versions)
        cutoff = _baseline_date(
            recorded["description"].split("cutoff=", 1)[1], "recorded baseline cutoff"
        )
        if explicit is not None and explicit != cutoff:
            raise AnsibleFilterError(
                "Cannot change a published baseline cutoff; use a separate namespace"
            )
    else:
        cutoff = explicit if explicit is not None else earliest - timedelta(days=1)
    if cutoff >= earliest:
        raise AnsibleFilterError(
            "Baseline cutoff must precede the earliest selected RHSA issue date"
        )
    return {
        "advisories": sorted(set(ids)),
        "earliest_issue_date": earliest.isoformat(),
        "cutoff": cutoff.isoformat(),
    }


def verify_cutoff(errata, cutoff):
    """Require every published advisory to have an issue date within the cap."""
    limit = _baseline_date(cutoff, "update cutoff")
    if not isinstance(errata, list):
        raise AnsibleFilterError("Expected published advisory metadata")
    for row in errata:
        if not isinstance(row, dict) or not row.get("errata_id"):
            raise AnsibleFilterError("Missing published advisory identifier")
        issued = _baseline_date(row.get("issued"), "advisory issue date", timestamp=True)
        if issued > limit:
            raise AnsibleFilterError(
                "Content contains an advisory issued after the requested cutoff: "
                + row["errata_id"]
            )
    return True


def update_cutoff(cutoff, baseline_errata):
    """Validate a date cap before synchronization or filter changes."""
    if cutoff == "":
        return ""
    canonical = _baseline_date(cutoff, "update cutoff").isoformat()
    verify_cutoff(baseline_errata, canonical)
    return canonical


class FilterModule:
    def filters(self):
        return {
            "sniper_one": one,
            "sniper_owned": owned,
            "sniper_task_ids": task_ids,
            "sniper_repo_options": repo_options,
            "sniper_initial_baseline": initial_baseline,
            "sniper_baseline_ids": baseline_ids,
            "sniper_baseline_searches": baseline_searches,
            "sniper_baseline_plan": baseline_plan,
            "sniper_update_cutoff": update_cutoff,
            "sniper_verify_cutoff": verify_cutoff,
        }
