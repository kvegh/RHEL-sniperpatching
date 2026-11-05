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


def _minor_identity(row, content_view_id):
    if not isinstance(row, dict) or row.get("content_view_id") != content_view_id:
        raise AnsibleFilterError("Minor history contains a foreign Content View version")
    if (any(type(row.get(key)) is not int or row[key] < 0
            for key in ("id", "major", "minor")) or row["id"] == 0):
        raise AnsibleFilterError("Minor history has invalid version identifiers")
    if row.get("version") != "%s.%s" % (row["major"], row["minor"]):
        raise AnsibleFilterError("Minor history has inconsistent version numbers")
    environments = row.get("environments")
    if (not isinstance(environments, list)
            or any(not isinstance(env, dict) or type(env.get("id")) is not int
                   or env["id"] <= 0 for env in environments)):
        raise AnsibleFilterError("Minor history has incomplete environment metadata")
    ids = [env["id"] for env in environments]
    if len(ids) != len(set(ids)):
        raise AnsibleFilterError("Minor history has duplicate environment metadata")
    return row["id"], row["major"], row["minor"], set(ids)


def minor_library_safe(rows, baseline, candidate, content_view_id):
    if (not isinstance(rows, list) or len(rows) != 1
            or not isinstance(candidate, dict)):
        raise AnsibleFilterError("Require one current Library version before changing content")
    base_id = _minor_identity(baseline, content_view_id)[0]
    allowed = {base_id}
    if candidate:
        allowed.add(_minor_identity(candidate, content_view_id)[0])
    if _minor_identity(rows[0], content_view_id)[0] not in allowed:
        raise AnsibleFilterError("Library contains unrelated content; refusing to replace it")
    return True


def minor_candidate(versions, baseline, content_view_id, description,
                    library_id, library_versions):
    if (not isinstance(versions, list) or type(content_view_id) is not int
            or content_view_id <= 0 or type(library_id) is not int
            or library_id <= 0 or not isinstance(description, str) or not description):
        raise AnsibleFilterError("Require explicit minor provenance and Library identity")
    base_id, major, minor, _ = _minor_identity(baseline, content_view_id)
    candidates = []
    seen = set()
    for version in versions:
        ident, version_major, version_minor, environments = _minor_identity(version, content_view_id)
        if ident in seen:
            raise AnsibleFilterError("Minor history has duplicate version identifiers")
        seen.add(ident)
        if ident == base_id:
            if (version_major, version_minor) != (major, minor):
                raise AnsibleFilterError("The serving baseline changed while planning a minor")
            continue
        if version.get("description") == description:
            if (version_major != major or version_minor <= minor
                    or not environments.issubset({library_id})):
                raise AnsibleFilterError("Refusing a candidate with foreign lineage or consumer environments")
            candidates.append(version)
        elif (version_major, version_minor) > (major, minor):
            raise AnsibleFilterError("Refusing unrelated newer minor history; inspect it before retrying")
    if base_id not in seen or len(candidates) > 1:
        raise AnsibleFilterError("Require the serving baseline and at most one recoverable minor")
    candidate = candidates[0] if candidates else {}
    minor_library_safe(library_versions, baseline, candidate, content_view_id)
    return candidate


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
            "sniper_minor_candidate": minor_candidate,
            "sniper_minor_library_safe": minor_library_safe,
        }
