# NEW Satellite demo execution environment

This demo EE recipe combines certified `redhat.satellite` **6.0.0** and unmodified
CoP `infra.satellite_configuration` **1.5.0** on the unchanged official Red Hat
Core **2.20.10** minimal image. The earlier published image contains Satellite
6.0.0 only; CoP-containing EE 0.2.0 is now built and offline-qualified, but is not yet
published or bound to AAP. Use the same immutable NEW image for its
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
| CoP released archive | `infra-satellite_configuration-1.5.0.tar.gz` |
| CoP archive bytes | `190727` |
| CoP archive SHA-256 | `aafc8d7c5021b1f07764b1f27b0944c0592c209507e0b3dc0e1c494a5d662901` |

Obtain the exact certified archive through the existing authenticated Hub and
verify its size and SHA-256. Do not rebuild a substitute from GitHub source.
Use a temporary build context outside the checkout: copy `Containerfile` and
install the two verified local archives under `collections/` using native
`ansible-galaxy collection install --no-deps -p`, explicitly supplying both
archive paths. Build with the pinned cached base, `--pull=never` and
`--network=none`. Preserve the approved private Automation Hub distribution
path; do not download Git source or install dependencies during a job.

## Scoped CoP dependency qualification

CoP 1.5.0 declares Satellite 5.8.0. That declaration remains unchanged in its
upstream package. This recipe deliberately retains the selected certified 6.0.0
artifact instead of resolving CoP's dependency to 5.8.0. The released CoP archive
has an authoritative release-asset digest; its manifest/file inventory and all
264 packaged file hashes matched the exact reviewed source revision
`4e504141d91c492f70ff59f9d38ae7d770ff75ec`. Do not repackage the collection or
silently describe this as compliance with its declared dependency combination.

Offline checks on Core 2.20.10 passed four native syntax checks, four synthetic
rendering groups, and ten actual module-constructor argument checks. An
additional negative check confirmed rejection of legacy filter-rule fields by
the filter module. The tests stopped before API entry with container networking
disabled. They establish bounded loading, templating and argument compatibility;
real API behavior, idempotency and end-to-end acceptance remain unverified.

Limit configuration to the selected repository, lifecycle, content-view and
activation-key paths. The native content-view role separates filters and rules;
do not pass rule fields through CoP's separate legacy filter dispatcher. Do not
invoke full dispatch, automatic content-view version cleanup, exports,
reconciliation, provisioning or identity management to configure this demo.
Keep the existing targeted/full patching stages separate from foundation setup.
The NEW content plan uses proactive `immediate` synchronization, explicitly
bounded to the selected RHEL 9.4/9.5 variants. It must not switch to on-demand
downloads or a rolling/newer minor to work around capacity or applicability.


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
