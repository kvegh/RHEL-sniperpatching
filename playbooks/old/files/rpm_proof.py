#!/usr/bin/env python
"""Read-only fix proof with native RPM comparison; Python 2.7/3 compatible.

argv[1] is fixed-package JSON. Optional argv[2] is JSON with requested_id and
advisory_map (live per-CVE Satellite resolution). requested_id accepts one RHSA
or comma/whitespace-separated CVEs.
An unverified fix emits JSON and exits 0 so callers can inspect pre-patch state.
Malformed metadata or unavailable native RPM bindings/database exit 2. Callers
must assert verified after patching/reboot. Nothing is written to disk.
"""
# Reason and interface: ../docs/implementation.md#native-rpm-proof


from __future__ import print_function
import json
import platform
import re
import sys

try:
    STRING_TYPES = (basestring,)
except NameError:
    STRING_TYPES = (str,)

_ADVISORY = re.compile(r"RHSA-[0-9]{4}:[0-9]{4,}\Z")
_CVE = re.compile(r"CVE-[0-9]{4}-[0-9]{4,}\Z")
_NAME = re.compile(r"[A-Za-z0-9_+][A-Za-z0-9_.+\-]*\Z")
_EVR = re.compile(r"[A-Za-z0-9_+.~^]+\Z")
_ARCH = re.compile(r"[A-Za-z0-9_]+\Z")
_RUNTIME_KERNELS = frozenset(
    (
        "kernel",
        "kernel-core",
        "kernel-rt",
        "kernel-rt-core",
        "kernel-debug",
        "kernel-debug-core",
        "kernel-PAE",
        "kernel-smp",
        "kernel-xen",
    )
)


def _package(item):
    if not isinstance(item, dict):
        raise ValueError("Each fixed package requirement must be a dictionary")
    entry = {}
    for key, pattern in (
        ("name", _NAME),
        ("version", _EVR),
        ("release", _EVR),
        ("arch", _ARCH),
    ):
        value = item.get(key)
        if (
            not isinstance(value, STRING_TYPES)
            or len(value) > 512
            or not pattern.match(value)
        ):
            raise ValueError("Invalid package field: " + key)
        entry[key] = value
    if "epoch" not in item:
        raise ValueError("Fixed package requirement lacks an authoritative RPM epoch")
    epoch = item["epoch"]
    if isinstance(epoch, bool) or not re.match(r"[0-9]+\Z", str(epoch)):
        raise ValueError("Invalid package epoch")
    entry["epoch"] = str(int(epoch))
    if entry["arch"] in ("src", "nosrc"):
        raise ValueError("Source packages cannot prove an installed binary fix")
    return entry


def _validated(requirements):
    if not isinstance(requirements, list) or not requirements:
        raise ValueError("Nonempty fixed package requirements are required")
    result = []
    for item in requirements:
        entry = _package(item)
        advisory = item.get("advisory")
        if not isinstance(advisory, STRING_TYPES) or not _ADVISORY.match(advisory):
            raise ValueError("Invalid RHSA identifier in fixed package requirements")
        entry["advisory"] = advisory
        result.append(entry)
    return result


def _evr(package):
    epoch = package["epoch"]
    return (
        str(epoch if epoch is not None else 0),
        str(package["version"]),
        str(package["release"]),
    )


def _display(evr):
    return "%s:%s-%s" % evr


def _newest(packages, rpm_module):
    result = packages[0]
    for package in packages[1:]:
        if rpm_module.labelCompare(_evr(package), _evr(result)) > 0:
            result = package
    return result


def _headers(transaction, name):
    return [
        dict(
            (key, header[key])
            for key in ("name", "epoch", "version", "release", "arch")
        )
        for header in transaction.dbMatch("name", name)
    ]


def _requests(options, requirements):
    value = options.get("requested_id")
    if value is None:
        return [], {}, False
    if not isinstance(value, STRING_TYPES) or len(value) > 4096:
        raise ValueError("Invalid requested patch identifiers")
    ids = sorted(set(re.split(r"[\s,]+", value.strip())))
    if not ids or len(ids) > 50 or any(
        not (_CVE.match(ident) or _ADVISORY.match(ident)) for ident in ids
    ):
        raise ValueError("Invalid requested patch identifiers")
    available = set(item["advisory"] for item in requirements)
    if len(ids) == 1 and _ADVISORY.match(ids[0]):
        if available != set(ids):
            raise ValueError("Fixed package metadata does not match requested RHSA")
        return ids, {ids[0]: ids}, False
    if any(not _CVE.match(ident) for ident in ids):
        raise ValueError("Supply one RHSA or a list of CVEs")
    mapping = options.get("advisory_map")
    if not isinstance(mapping, dict) or set(mapping) != set(ids):
        raise ValueError("Every CVE requires its live Satellite advisory mapping")
    covered = set()
    for ident, advisories in mapping.items():
        if not isinstance(advisories, list) or not advisories or any(
            not isinstance(a, STRING_TYPES) or not _ADVISORY.match(a)
            or a not in available for a in advisories
        ):
            raise ValueError("Invalid or incomplete CVE advisory mapping")
        covered.update(advisories)
    if covered != available:
        raise ValueError("CVE mapping does not match fixed package metadata")
    return ids, mapping, True


def verify(requirements, rpm_module=None, running_release=None, options=None):
    requirements = _validated(requirements)
    options = {} if options is None else options
    if not isinstance(options, dict):
        raise ValueError("Proof options must be a dictionary")
    requested_ids, advisory_map, cve_mode = _requests(options, requirements)
    if rpm_module is None:
        import rpm as rpm_module
    if running_release is None:
        running_release = platform.release()
    transaction = rpm_module.TransactionSet()
    cache, by_advisory = {}, {}
    for item in requirements:
        by_advisory.setdefault(item["advisory"], {}).setdefault(
            item["name"], []
        ).append(item)
    records, mismatches, advisories = [], [], {}
    kernel_checks, kernel_reboots = [], []
    for advisory, names in sorted(by_advisory.items()):
        advisory_records, advisory_mismatches = [], []
        affected_present = False
        for name, fixed_packages in sorted(names.items()):
            if name not in cache:
                cache[name] = _headers(transaction, name)
            installed = cache[name]
            affected_present = affected_present or bool(installed)
            for arch in sorted(set(package["arch"] for package in installed)):
                installed_arch = [
                    package for package in installed if package["arch"] == arch
                ]
                fixed_arch = [
                    package for package in fixed_packages if package["arch"] == arch
                ]
                if not fixed_arch:
                    advisory_mismatches.append(
                        {
                            "advisory": advisory,
                            "name": name,
                            "arch": arch,
                            "reason": "installed_architecture_missing_fixed_metadata",
                        }
                    )
                    continue
                threshold = _newest(fixed_arch, rpm_module)
                newest = _newest(installed_arch, rpm_module)
                newest_fixed = (
                    rpm_module.labelCompare(_evr(newest), _evr(threshold)) >= 0
                )
                installonly = name in _RUNTIME_KERNELS or (
                    name.startswith("kernel") and name.endswith("-devel")
                )
                installed_fixed = (
                    newest_fixed
                    if installonly
                    else all(
                        rpm_module.labelCompare(_evr(package), _evr(threshold)) >= 0
                        for package in installed_arch
                    )
                )
                record = {
                    "advisory": advisory,
                    "name": name,
                    "arch": arch,
                    "installed": [
                        _display(_evr(package)) for package in installed_arch
                    ],
                    "fixed": _display(_evr(threshold)),
                    "verified": installed_fixed,
                }
                if name in _RUNTIME_KERNELS:
                    running = [
                        package
                        for package in installed_arch
                        if "%s-%s.%s"
                        % (package["version"], package["release"], package["arch"])
                        == running_release
                    ]
                    running_fixed = bool(running) and any(
                        rpm_module.labelCompare(_evr(package), _evr(threshold)) >= 0
                        for package in running
                    )
                    record["running_kernel_fixed"] = running_fixed
                    kernel_checks.append(running_fixed)
                    kernel_reboots.append(newest_fixed and not running_fixed)
                    record["verified"] = installed_fixed and running_fixed
                    if installed_fixed and not running_fixed:
                        advisory_mismatches.append(
                            {
                                "advisory": advisory,
                                "name": name,
                                "arch": arch,
                                "reason": "fixed_kernel_not_running",
                                "running_release": running_release,
                            }
                        )
                advisory_records.append(record)
                if not installed_fixed:
                    advisory_mismatches.append(
                        {
                            "advisory": advisory,
                            "name": name,
                            "arch": arch,
                            "reason": "installed_version_below_fix",
                            "fixed": record["fixed"],
                            "installed": record["installed"],
                        }
                    )
        not_applicable = cve_mode and not affected_present
        if not advisory_records and not not_applicable and not advisory_mismatches:
            advisory_mismatches.append(
                {"advisory": advisory, "reason": "no_affected_installed_packages"}
            )
        advisories[advisory] = {
            "verified": bool(advisory_records) and not advisory_mismatches,
            "not_applicable": not_applicable,
            "affected_installed": affected_present,
            "affected_packages": advisory_records,
            "mismatches": advisory_mismatches,
        }
        records.extend(advisory_records)
        mismatches.extend(advisory_mismatches)
    applicable = [value for value in advisories.values() if not value["not_applicable"]]
    requested = {}
    for ident in requested_ids:
        covered = [advisories[a] for a in advisory_map[ident]]
        active = [value for value in covered if value["affected_installed"]] if cve_mode else covered
        requested[ident] = {
            "advisories": advisory_map[ident],
            "verified": bool(active) and all(value["verified"] for value in active),
        }
        if cve_mode and not active:
            mismatches.append(
                {
                    "requested_id": ident,
                    "reason": "no_affected_installed_packages_for_cve",
                }
            )
    affected_names = sorted(set(record["name"] for record in records))
    result = {
        "verified": bool(records)
        and bool(applicable)
        and all(value["verified"] for value in applicable)
        and all(value["verified"] for value in requested.values()),
        "affected_packages": records,
        "affected_names": affected_names,
        "mismatches": mismatches,
        "advisories": advisories,
        "requested": requested,
        "requested_ids": requested_ids,
        "running_kernel_fixed": all(kernel_checks) if kernel_checks else None,
        "requires_kernel_reboot": any(kernel_reboots),
    }
    return result


def main(argv=None):
    argv = sys.argv if argv is None else argv
    try:
        if len(argv) not in (2, 3):
            raise ValueError(
                "Supply JSON fixed package requirements and optional proof options"
            )
        options = json.loads(argv[2]) if len(argv) == 3 else {}
        proof = verify(json.loads(argv[1]), options=options)
        print(json.dumps(proof, sort_keys=True))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {"verified": False, "error": "%s: %s" % (type(exc).__name__, exc)},
                sort_keys=True,
            )
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
