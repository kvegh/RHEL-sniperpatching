# NEW Satellite installer execution environment

This setup EE adds certified `redhat.satellite_operations` **4.0.0** to the
unchanged official Red Hat Core **2.20.10** minimal image. It is for the NEW
Satellite installation job. The later NEW demo EE and its `redhat.satellite`
management collection have separate qualification requirements. OLD keeps its
existing runtime and collection pins.

| Input | Exact identity |
|---|---|
| Base | `registry.redhat.io/ansible-automation-platform-27/ee-minimal-rhel9@sha256:aea45867ebbfcb57bba69b3b6e33542dbbe95f237dfdf35e8b68773b4f3268f8` |
| Base image ID | `6ac3ae57346f0900fab85077798225c3498793084662a3a9ee2a14dd5f0dc3a6` |
| Certified archive | `redhat-satellite_operations-4.0.0.tar.gz` |
| Archive bytes | `26716` |
| Archive SHA-256 | `9595ac584856ac67ac1f93c97fb1169ac333e8be011727436f87871be299bc4a` |

Obtain this exact archive from the receiving private Automation Hub's certified
content, synchronized from Red Hat Automation Hub. Verify both size and SHA-256
before extracting. Do not build a replacement archive from GitHub source.

Use a temporary build context outside the checkout. Copy `Containerfile` there
and install the verified local archive into its `collections/` directory with
native `ansible-galaxy collection install --no-deps -p`. Keep Ansible's cache in
the same temporary workspace. Build with the cached pinned base, native Podman,
`--pull=never` and `--network=none`. No Python or RPM package installation is part
of this collection-only recipe.

Publish a new versioned image through the operator's existing native registry
credentials with TLS validation. Never copy credentials, authentication files,
archives or populated target configuration into this repository or image. Do
not overwrite an existing tag identifying different inputs. Bind the resulting
immutable receiving-Hub digest explicitly in the NEW installer job's private
CaC; publication alone does not update a live template or install Satellite.

Check the actual Core and collection versions and parse the certified installer
role in the resulting image. Preserve the base entrypoint, command, user,
environment, working directory and every original image layer. Live Satellite
6.19/RHEL 9 installation acceptance is separate from these image checks.
