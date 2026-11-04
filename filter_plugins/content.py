"""Small, pure validation helpers for Satellite content operations."""

import re
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


class FilterModule:
    def filters(self):
        return {
            "sniper_one": one,
            "sniper_owned": owned,
            "sniper_task_ids": task_ids,
            "sniper_repo_options": repo_options,
            "sniper_initial_baseline": initial_baseline,
        }
