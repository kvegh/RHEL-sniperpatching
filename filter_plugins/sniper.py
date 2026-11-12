"""Pure data filters for patch IDs, Satellite metadata, and RPM inventories."""
# Reason and interface: ../docs/implementation.md#validation-filters


import re

_PATCH = re.compile(r"(?:CVE-[0-9]{4}-[0-9]{4,}|RHSA-[0-9]{4}:[0-9]{4,})\Z")
_NAME = re.compile(r"[A-Za-z0-9_+][A-Za-z0-9_.+\-]*\Z")
_EVR = re.compile(r"[A-Za-z0-9_+.~^]+\Z")
_ARCH = re.compile(r"[A-Za-z0-9_]+\Z")


def sniper_patch_id(value):
    if not isinstance(value, str):
        raise ValueError("Patch ID must be one CVE or RHSA string")
    value = value.strip().upper()
    if len(value) > 96 or not _PATCH.fullmatch(value):
        raise ValueError("Patch ID must be CVE-YYYY-NNNN or RHSA-YYYY:NNNN")
    return value


def sniper_patch_ids(value):
    """Survey text: one RHSA or up to fifty CVEs; no expressions."""
    if not isinstance(value, str) or len(value) > 4096:
        raise ValueError("Enter one RHSA or up to 50 CVEs as survey text")
    ids = sorted({sniper_patch_id(item) for item in re.split(r"[\s,]+", value.strip())})
    if len(ids) > 50 or (len(ids) > 1 and any(not x.startswith("CVE-") for x in ids)):
        raise ValueError("Enter one RHSA or up to 50 CVEs; do not mix RHSA and CVE IDs")
    return ids


def sniper_resolve_queries(queries, requested_ids):
    """Retain the live per-input resolution, refusing any unresolved input."""
    requested_ids = sniper_patch_ids(" ".join(requested_ids))
    mapping = {ident: set() for ident in requested_ids}
    advisories = {}
    if not isinstance(queries, list):
        raise ValueError("Expected live Satellite query results")
    for query in queries:
        pair = query.get("item") if isinstance(query, dict) else None
        rows = query.get("resources") if isinstance(query, dict) else None
        if not isinstance(pair, (list, tuple)) or len(pair) != 2 or pair[1] not in mapping:
            raise ValueError("Satellite query result lacks its requested ID")
        if not isinstance(rows, list):
            raise ValueError("Satellite query result lacks advisory resources")
        requested = pair[1]
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("Invalid Satellite advisory result")
            advisory = sniper_patch_id(row.get("errata_id"))
            if not advisory.startswith("RHSA-"):
                raise ValueError("Requested ID resolved outside security advisories")
            if requested.startswith("RHSA-") and advisory != requested:
                raise ValueError("Satellite returned a different RHSA than requested")
            mapping[requested].add(advisory)
            advisories[advisory] = row
    unresolved = [ident for ident, values in mapping.items() if not values]
    if unresolved:
        raise ValueError("No RHSA in the selected repositories for: " + ", ".join(unresolved))
    return {
        "by_input": {ident: sorted(values) for ident, values in mapping.items()},
        "advisories": [advisories[ident] for ident in sorted(advisories)],
    }


def sniper_validate_resolution(mapping, details):
    """Confirm live CVE membership from complete Satellite advisory details."""
    if not isinstance(mapping, dict) or not isinstance(details, list):
        raise ValueError("Expected live per-ID resolution and advisory details")
    ids = sniper_patch_ids(" ".join(mapping))
    by_id = {}
    for detail in details:
        ident = sniper_patch_id(detail.get("errata_id"))
        if not ident.startswith("RHSA-"):
            raise ValueError("Resolved detail is not an RHSA")
        by_id[ident] = detail
    result = {}
    for requested in ids:
        values = mapping[requested]
        if not isinstance(values, list) or not values or any(x not in by_id for x in values):
            raise ValueError("Incomplete Satellite advisory resolution")
        if requested.startswith("RHSA-"):
            if values != [requested]:
                raise ValueError("RHSA resolution must identify that exact advisory")
        else:
            for advisory in values:
                cves = by_id[advisory].get("cves")
                if not isinstance(cves, list) or requested not in {
                    row.get("cve_id") for row in cves if isinstance(row, dict)
                }:
                    raise ValueError(
                        "Satellite advisory details do not confirm " + requested + " in " + advisory
                    )
        result[requested] = sorted(set(values))
    if {value for values in result.values() for value in values} != set(by_id):
        raise ValueError("Advisory details do not match the requested resolution")
    return result


def _text(value, pattern, label):
    if not isinstance(value, str) or len(value) > 512 or not pattern.fullmatch(value):
        raise ValueError("Invalid RPM " + label)
    return value


def _epoch(value):
    if value in (None, "(none)"):
        return "0"
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise ValueError("Invalid RPM epoch")
    return str(int(value))


def _package(value):
    original = value
    if isinstance(value, dict):
        if all(k in value for k in ("name", "version", "release", "arch")):
            result = {k: value[k] for k in ("name", "version", "release", "arch")}
            result["epoch"] = _epoch(value["epoch"]) if "epoch" in value else None
        else:
            value = next(
                (value.get(k) for k in ("nevra", "nvra", "filename") if value.get(k)),
                None,
            )
            if not value:
                raise ValueError(
                    "Satellite package metadata lacks structured NEVRA or a package filename"
                )
            result = _package(value)
            if "epoch" in original:
                epoch = _epoch(original["epoch"])
                if result["epoch"] is not None and result["epoch"] != epoch:
                    raise ValueError("Conflicting RPM epoch in package metadata")
                result["epoch"] = epoch
            return result
    elif isinstance(value, str):
        value = value[:-4] if value.endswith(".rpm") else value
        try:
            nvr, arch = value.rsplit(".", 1)
            name, version, release = nvr.rsplit("-", 2)
        except ValueError as exc:
            raise ValueError("Invalid RPM NEVRA") from exc
        epoch = None
        if ":" in version:
            epoch, version = version.split(":", 1)
        result = {
            "name": name,
            "epoch": _epoch(epoch) if epoch is not None else None,
            "version": version,
            "release": release,
            "arch": arch,
        }
    else:
        raise ValueError(
            "Satellite package metadata must be a dictionary or NEVRA string"
        )
    result["name"] = _text(result["name"], _NAME, "name")
    if result["epoch"] is not None:
        result["epoch"] = _epoch(result["epoch"])
    result["version"] = _text(result["version"], _EVR, "version")
    result["release"] = _text(result["release"], _EVR, "release")
    result["arch"] = _text(result["arch"], _ARCH, "architecture")
    return result


def _advisory_packages(errata_details):
    """Parse advisory package identity without inventing an omitted epoch."""
    if isinstance(errata_details, dict):
        errata_details = errata_details.get("results", [errata_details])
    if not isinstance(errata_details, list) or not errata_details:
        raise ValueError("At least one resolved RHSA detail is required")
    result = []
    for detail in errata_details:
        if not isinstance(detail, dict):
            raise ValueError("Erratum detail must be a dictionary")
        advisory = sniper_patch_id(
            detail.get("errata_id") or detail.get("uuid") or detail.get("pulp_id")
        )
        if not advisory.startswith("RHSA-"):
            raise ValueError("Resolved advisory must be an RHSA")
        packages = detail.get("packages")
        if not isinstance(packages, list) or not packages:
            if detail.get("module_streams"):
                raise ValueError(
                    "Modular-only advisory requires an explicit supported module-stream policy"
                )
            raise ValueError("Resolved RHSA has no fixed package metadata")
        found = False
        for raw in packages:
            package = _package(raw)
            if package["arch"] in ("src", "nosrc"):
                continue
            found = True
            item = {"advisory": advisory, **package}
            result.append(item)
        if not found:
            raise ValueError("Resolved RHSA has no binary fixed package metadata")
    return result


def _nvra(package):
    return tuple(package[key] for key in ("name", "version", "release", "arch"))


def sniper_package_searches(errata_details):
    """Bound exact filename queries; RPM filenames themselves omit epochs."""
    terms = sorted(
        {
            'filename = "%s-%s-%s.%s.rpm"' % _nvra(package)
            for package in _advisory_packages(errata_details)
        }
    )
    queries, current = [], ""
    for term in terms:
        if len(term) > 2000:
            raise ValueError("RPM filename is too long for a bounded package query")
        combined = current + " or " + term if current else term
        if len(combined) > 2000:
            queries.append(current)
            current = term
        else:
            current = combined
    if current:
        queries.append(current)
    return queries


def sniper_package_requirements(errata_details, package_catalog=None):
    """Resolve omitted epochs from exact packages in the selected repositories."""
    catalogue = {}
    if package_catalog is not None:
        if isinstance(package_catalog, dict):
            package_catalog = package_catalog.get("results")
        if not isinstance(package_catalog, list):
            raise ValueError("Package catalogue must contain structured package rows")
        for raw in package_catalog:
            if not isinstance(raw, dict) or "epoch" not in raw:
                raise ValueError("Package catalogue must include an explicit RPM epoch")
            package = _package(raw)
            catalogue.setdefault(_nvra(package), set()).add(package["epoch"])
    result, seen = [], set()
    for package in _advisory_packages(errata_details):
        epochs = catalogue.get(_nvra(package), set())
        if package["epoch"] is None:
            if len(epochs) != 1:
                raise ValueError(
                    "Missing or ambiguous authoritative RPM epoch for "
                    + package["name"]
                )
            package["epoch"] = next(iter(epochs))
        elif epochs and epochs != {package["epoch"]}:
            raise ValueError("Conflicting RPM epoch metadata for " + package["name"])
        identity = tuple(
            package[key]
            for key in ("advisory", "name", "epoch", "version", "release", "arch")
        )
        if identity not in seen:
            result.append(package)
            seen.add(identity)
    return result


def _inventory(value):
    if isinstance(value, str):
        value = value.splitlines()
    if not isinstance(value, list):
        raise ValueError("RPM inventory must be text or a list of lines")
    result = {}
    for line in value:
        if not isinstance(line, str):
            raise ValueError("RPM inventory lines must be strings")
        if not line.strip():
            continue
        fields = line.split("|")
        if len(fields) != 5:
            raise ValueError(
                "RPM inventory must contain NAME|EPOCHNUM|VERSION|RELEASE|ARCH"
            )
        raw = dict(zip(("name", "epoch", "version", "release", "arch"), fields))
        if raw["name"] == "gpg-pubkey" and raw["arch"] == "(none)":
            # RPM stores imported signing keys as database records without an
            # architecture. Keep their real identity in inventory deltas only.
            if (raw["epoch"] not in ("0", "(none)")
                    or any(not re.fullmatch(r"[0-9a-fA-F]{8}", raw[key])
                           for key in ("version", "release"))):
                raise ValueError("Invalid RPM signing-key database record")
            package = dict(raw, epoch="0")
        else:
            package = _package(raw)
        result.setdefault(package["name"], set()).add(
            tuple(package[k] for k in ("epoch", "version", "release", "arch"))
        )
    return result


def sniper_package_delta(before_rpm_lines, after_rpm_lines):
    """Changed RPM names only; direction must be proven with native RPM."""
    before, after = _inventory(before_rpm_lines), _inventory(after_rpm_lines)
    return sorted(
        name for name in set(before) | set(after) if before.get(name) != after.get(name)
    )


class FilterModule:
    def filters(self):
        return {
            "sniper_patch_id": sniper_patch_id,
            "sniper_patch_ids": sniper_patch_ids,
            "sniper_resolve_queries": sniper_resolve_queries,
            "sniper_validate_resolution": sniper_validate_resolution,
            "sniper_package_requirements": sniper_package_requirements,
            "sniper_package_searches": sniper_package_searches,
            "sniper_package_delta": sniper_package_delta,
        }
