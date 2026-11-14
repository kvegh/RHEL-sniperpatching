# NEW Satellite demo execution environment

This demo EE adds certified `redhat.satellite` **6.0.0** to the unchanged official
Red Hat Core **2.20.10** minimal image. Use the same immutable NEW image for its
NEW targets and the later compatibility test against OLD Satellite/RHEL hosts.
The original OLD AAP keeps its existing legacy runtime; the separate NEW
Satellite setup EE remains unchanged.

| Input | Exact identity |
|---|---|
| Base | `registry.redhat.io/ansible-automation-platform-27/ee-minimal-rhel9@sha256:aea45867ebbfcb57bba69b3b6e33542dbbe95f237dfdf35e8b68773b4f3268f8` |
| Base image ID | `6ac3ae57346f0900fab85077798225c3498793084662a3a9ee2a14dd5f0dc3a6` |
| Certified archive | `redhat-satellite-6.0.0.tar.gz` |
| Archive bytes | `514153` |
| Archive SHA-256 | `67847d52685e27f3220b1e641f8294f221e341bfddca439172c4e9b88407fb2d` |

Obtain the exact certified archive through the existing authenticated Hub and
verify its size and SHA-256. Do not rebuild a substitute from GitHub source.
Use a temporary build context outside the checkout: copy `Containerfile` and
install the verified local archive under `collections/` using native
`ansible-galaxy collection install --no-deps -p`. Build with the pinned cached
base, `--pull=never` and `--network=none`.

## Runtime dependencies

The certified archive declares `requests>=2.4.2` and `PyYAML`. The pinned base
already supplies requests **2.34.2** and PyYAML **6.0.1**. Collection 6.0.0 vendors
its own `_apypie.py`; an external apypie package is unnecessary. Optional GSSAPI,
Kerberos and OAuth adapters are not required by this demo's username/password
API authentication. No Python packages, RPMs or unrelated tools are added by
this recipe, and the complete base Python distribution inventory is preserved.

The collection's platform bindep includes `python3-rpm`. Its only RPM-binding
import is the optional `content_upload` module; that module also accepts the
vendor base's existing `/usr/bin/rpm` CLI. This scoped demo does not upload RPMs.
Python RPM bindings are not added, and no claim that every optional collection
feature is qualified is made. Native package proof runs on managed RHEL hosts
using their own RPM bindings, independently of this controller EE.

Check the built image's actual Core, collection, vendored API and dependency
imports. Exercise the NEW content/runtime fixtures, nine module interfaces and
six demo stage syntax checks against this exact collection. Publish a new
versioned tag through existing protected native Hub authentication and verify
its immutable manifest/configuration/blobs. Bind that receiving-Hub digest
explicitly on NEW job templates through private CaC. Keep target addresses,
credentials, authentication files and generated evidence outside public source.

Image qualification and publication do not establish live Satellite API access,
managed-host reachability or end-to-end patching acceptance. Those remain
separate normal AAP checks after configuration.
