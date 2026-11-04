"""Pure data filters for patch IDs, Satellite metadata, and RPM inventories."""

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


def _text(value, pattern, label):
    if not isinstance(value, str) or len(value) > 512 or not pattern.fullmatch(value):
        raise ValueError("Invalid RPM " + label)
    return value


def _epoch(value):
    if value in (None, "", "(none)"):
        return "0"
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise ValueError("Invalid RPM epoch")
    return str(int(value))


def _package(value):
    original = value
    if isinstance(value, dict):
        if all(k in value for k in ("name", "version", "release", "arch")):
            result = {k: value[k] for k in ("name", "version", "release", "arch")}
            result["epoch"] = _epoch(value.get("epoch"))
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
                result["epoch"] = _epoch(original["epoch"])
            return result
    elif isinstance(value, str):
        value = value[:-4] if value.endswith(".rpm") else value
        try:
            nvr, arch = value.rsplit(".", 1)
            name, version, release = nvr.rsplit("-", 2)
        except ValueError as exc:
            raise ValueError("Invalid RPM NEVRA") from exc
        epoch = "0"
        if ":" in version:
            epoch, version = version.split(":", 1)
        result = {
            "name": name,
            "epoch": _epoch(epoch),
            "version": version,
            "release": release,
            "arch": arch,
        }
    else:
        raise ValueError(
            "Satellite package metadata must be a dictionary or NEVRA string"
        )
    result["name"] = _text(result["name"], _NAME, "name")
    result["epoch"] = _epoch(result["epoch"])
    result["version"] = _text(result["version"], _EVR, "version")
    result["release"] = _text(result["release"], _EVR, "release")
    result["arch"] = _text(result["arch"], _ARCH, "architecture")
    return result


def sniper_package_requirements(errata_details):
    """Retain per-advisory EVRs; never guess modular-stream policy."""
    if isinstance(errata_details, dict):
        errata_details = errata_details.get("results", [errata_details])
    if not isinstance(errata_details, list) or not errata_details:
        raise ValueError("At least one resolved RHSA detail is required")
    result, seen = [], set()
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
            identity = tuple(
                item[k]
                for k in ("advisory", "name", "epoch", "version", "release", "arch")
            )
            if identity not in seen:
                result.append(item)
                seen.add(identity)
        if not found:
            raise ValueError("Resolved RHSA has no binary fixed package metadata")
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
        package = _package(
            dict(zip(("name", "epoch", "version", "release", "arch"), fields))
        )
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
            "sniper_package_requirements": sniper_package_requirements,
            "sniper_package_delta": sniper_package_delta,
        }
