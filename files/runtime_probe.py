"""Inspect installed Ansible content and parse stages; never install or run them."""

import json
import platform
from pathlib import Path
import subprocess
import sys

import ansible

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
                "syntax_checked": checked,
                "syntax_failures": failures,
            }
        )
    )


if __name__ == "__main__":
    main()
