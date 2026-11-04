"""Inspect installed Ansible content and parse stages; never install or run them."""

import json
import platform
from pathlib import Path
import subprocess
import sys

import ansible
import yaml

MODULES = [
    "redhat.satellite." + name
    for name in (
        "resource_info",
        "lifecycle_environment",
        "content_view",
        "content_view_filter",
        "content_view_filter_rule",
        "content_view_version",
        "repository_sync",
        "host",
        "wait_for_task",
    )
]
STAGES = (
    "prepare_demo.yml",
    "create_minor_update.yml",
    "patch_hosts.yml",
    "publish_full_update.yml",
    "promote_content_view.yml",
    "check_patch.yml",
)


def run(arguments, root):
    return subprocess.run(
        arguments, cwd=str(root), capture_output=True, text=True, timeout=120
    )


def check_arguments(value, documented, filename):
    """Check nested task arguments against the installed modules' merged docs."""
    failures = []
    if isinstance(value, dict):
        for key, entry in value.items():
            if key in documented and documented[key] and isinstance(entry, dict):
                options = documented[key]["doc"]["options"]
                allowed = set(options)
                for option in options.values():
                    allowed.update(option.get("aliases", []))
                unsupported = sorted(set(entry) - allowed)
                if unsupported:
                    failures.append(
                        {
                            "file": filename,
                            "module": key,
                            "unsupported_arguments": unsupported,
                        }
                    )
            failures.extend(check_arguments(entry, documented, filename))
    elif isinstance(value, list):
        for entry in value:
            failures.extend(check_arguments(entry, documented, filename))
    return failures


def main():
    root = Path(sys.argv[1]).resolve()
    galaxy = run(
        [
            "ansible-galaxy",
            "collection",
            "list",
            "redhat.satellite",
            "--format",
            "json",
        ],
        root,
    )
    collections = json.loads(galaxy.stdout) if galaxy.returncode == 0 else {}
    docs = run(["ansible-doc", "--json"] + MODULES, root)
    documented = json.loads(docs.stdout) if docs.stdout.strip() else {}
    available = [name for name in MODULES if documented.get(name)]
    argument_failures = []
    paths = sorted(root.glob("*.yml")) + sorted((root / "tasks").glob("*.yml"))
    for path in paths:
        argument_failures.extend(
            check_arguments(
                yaml.safe_load(path.read_text()),
                documented,
                str(path.relative_to(root)),
            )
        )
    checked = []
    failures = {}
    for stage in STAGES:
        result = run(
            [
                "ansible-playbook",
                "--syntax-check",
                "--inventory",
                str(root / "inventory/example.ini"),
                str(root / stage),
            ],
            root,
        )
        if result.returncode:
            failures[stage] = (result.stderr + result.stdout).strip()
        else:
            checked.append(stage)
    print(
        json.dumps(
            {
                "ansible_core": ansible.__version__,
                "python": platform.python_version(),
                "satellite_collections": collections,
                "collection_list_error": (
                    galaxy.stderr.strip() if galaxy.returncode else ""
                ),
                "modules": available,
                "missing_modules": sorted(set(MODULES) - set(available)),
                "module_argument_failures": argument_failures,
                "syntax_checked": checked,
                "syntax_failures": failures,
            }
        )
    )


if __name__ == "__main__":
    main()
