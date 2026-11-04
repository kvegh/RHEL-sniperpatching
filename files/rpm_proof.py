#!/usr/bin/env python
"""Read-only fix proof with native RPM comparison; Python 2.7/3 compatible.

argv[1] is fixed-package JSON. Optional argv[2] is JSON with requested_id and,
for full-update proof, name/before for an independent package-upgrade witness.
An unverified fix emits JSON and exits 0 so callers can inspect pre-patch state.
Malformed metadata or unavailable native RPM bindings/database exit 2. Callers
must assert verified after patching/reboot and upgrade_witness.upgraded in full
mode. Nothing is written to disk.
"""

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
    epoch = item.get("epoch", "0")
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


def _upgrade_witness(options, transaction, rpm_module, affected_names):
    name = options.get("name")
    if not name:
        return None
    if not isinstance(name, STRING_TYPES) or not _NAME.match(name):
        raise ValueError("Invalid upgrade witness package name")
    before = options.get("before")
    if isinstance(before, STRING_TYPES):
        before = before.splitlines()
    if not isinstance(before, list):
        raise ValueError("Upgrade witness requires its pre-update RPM snapshot")
    previous = []
    for line in before:
        if not isinstance(line, STRING_TYPES):
            raise ValueError("RPM snapshot lines must be strings")
        if not line.strip():
            continue
        fields = line.split("|")
        if len(fields) != 5:
            raise ValueError(
                "RPM snapshot must contain NAME|EPOCHNUM|VERSION|RELEASE|ARCH"
            )
        package = _package(
            dict(zip(("name", "epoch", "version", "release", "arch"), fields))
        )
        if package["name"] == name:
            previous.append(package)
    current = _headers(transaction, name)
    comparisons = []
    for arch in sorted(set(package["arch"] for package in previous)):
        old = [package for package in previous if package["arch"] == arch]
        new = [package for package in current if package["arch"] == arch]
        if new:
            old_evr, new_evr = _evr(_newest(old, rpm_module)), _evr(
                _newest(new, rpm_module)
            )
            comparisons.append(
                {
                    "arch": arch,
                    "before": _display(old_evr),
                    "after": _display(new_evr),
                    "upgraded": rpm_module.labelCompare(new_evr, old_evr) > 0,
                }
            )
    independent = name not in affected_names
    return {
        "name": name,
        "independent": independent,
        "upgraded": independent and any(value["upgraded"] for value in comparisons),
        "comparisons": comparisons,
        "reason": (
            "target_fix_package_is_not_independent"
            if not independent
            else (
                "compared_existing_name_and_arch"
                if comparisons
                else "no_matching_preexisting_name_and_arch"
            )
        ),
    }


def verify(requirements, rpm_module=None, running_release=None, options=None):
    requirements = _validated(requirements)
    options = {} if options is None else options
    if not isinstance(options, dict):
        raise ValueError("Proof options must be a dictionary")
    requested_id = options.get("requested_id")
    if requested_id is not None:
        if not isinstance(requested_id, STRING_TYPES) or not (
            _CVE.match(requested_id) or _ADVISORY.match(requested_id)
        ):
            raise ValueError("Invalid requested patch identifier")
        if _ADVISORY.match(requested_id) and set(
            item["advisory"] for item in requirements
        ) != set([requested_id]):
            raise ValueError("Fixed package metadata does not match requested RHSA")
    cve_mode = bool(requested_id and _CVE.match(requested_id))
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
            "affected_packages": advisory_records,
            "mismatches": advisory_mismatches,
        }
        records.extend(advisory_records)
        mismatches.extend(advisory_mismatches)
    applicable = [value for value in advisories.values() if not value["not_applicable"]]
    if cve_mode and not applicable:
        mismatches.append(
            {
                "requested_id": requested_id,
                "reason": "no_affected_installed_packages_for_cve",
            }
        )
    affected_names = sorted(set(record["name"] for record in records))
    result = {
        "verified": bool(records)
        and bool(applicable)
        and all(value["verified"] for value in applicable),
        "affected_packages": records,
        "affected_names": affected_names,
        "mismatches": mismatches,
        "advisories": advisories,
        "running_kernel_fixed": all(kernel_checks) if kernel_checks else None,
        "requires_kernel_reboot": any(kernel_reboots),
    }
    witness = _upgrade_witness(options, transaction, rpm_module, affected_names)
    if witness is not None:
        result["upgrade_witness"] = witness
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
