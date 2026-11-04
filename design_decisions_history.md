# Design decisions history

## Resolve advisory epochs from selected repository packages — 2026-11-04

Implementation commit: `9199670f987932bcfec9179934da64625d3ec3e7` (version 0.2.2).

Satellite advisory NVRA strings omit the RPM epoch. Treating that omission as
zero made older installed packages with nonzero epochs appear newer than the
fixed versions. The resolver now queries exact package filenames through the
certified collection, restricted to the selected repositories, and matches the
complete name/version/release/architecture identity before using its structured
epoch. Queries are bounded. Explicit null means epoch zero; missing, ambiguous,
empty or conflicting metadata is rejected. The native host proof also refuses
requirements without an explicit epoch.

Fifty-four tests pass, including missing/ambiguous metadata, nonzero-epoch
false positives and actual Ansible task templating. All seven syntax checks,
production-profile lint and legacy host-Python grammar checks pass. Read-only
Satellite queries resolved all 151 fixed-package entries in the inspected
advisory set, including 33 nonzero epochs. Corrected native-RPM checks on both
selected RHEL 7.9 hosts confirm that all 14 reported advisories remain
outstanding; the earlier GRUB and BIND/DHCP fixed results were false positives.

No package installation, reboot, Content View change or snapshot operation ran.
Later AAP CaC and the six actual demonstration stages remain separate work.

## Reuse the existing Satellite collection after a runtime trial — 2026-11-04

Implementation commit: `524f835fb2c5a638d500cb735bca500d17edae96` (version 0.2.1).

The user chose the existing EE after its read-only diagnostic established
Ansible Core 2.15.11, Python 3.9.19 and redhat.satellite 3.14.0. This collection
was released in September 2023. The initially selected 6.0.0 requires Core 2.16+
and cannot be substituted into that EE unchanged. The explicit dependency now
matches the user's chosen existing runtime; no collection installation, EE
rebuild or shared source change was needed.

Inspection of the official 3.14.0 source found that content_view_filter uses
filter_state rather than state. Both filter calls now use that interface. The
diagnostic also compares actual task argument names with the installed module
documentation, including aliases, because syntax checks did not detect this
mismatch. Satellite's live API advertises the legacy host-assignment fields
used by this collection; assignment itself has not been executed.

All 44 offline tests, seven entry-point syntax checks and production-profile
lint pass against the official 3.14.0 source checkout. The first AAP diagnostic
read organizations successfully with verified HTTPS and zero changes. These
checks do not establish vendor support or successful live publication, host
patching or reboot behavior. Those demonstration stages remain unrun.

## Add an independently launched read-only EE diagnostic — 2026-11-04

Implementation commit: `1c9c73e0b6c1e551abdfe37738a532873555419f` (version 0.2.0).

The user requested a trial with the existing EE before considering a rebuild.
check_runtime.yml reports installed core, Python and collection versions,
checks required module availability, parses all six demonstration stages and
queries organizations using the existing Satellite credential with verified
HTTPS. Its supporting commands only inspect content and check syntax; it never
executes preparation or host-patching stages and needs no host SSH credential.

Local diagnostic syntax, production-profile lint and the six-stage inspection
passed. A separate normal AAP Job Template provides the live diagnostic without
changing the colleague's automation. Snapshot and rollback work remains on its
explicit hold.

## Show only runnable stages in AAP playbook discovery — 2026-11-04

Implementation commit: `224a8b12c9ff9474567c3491b9439c8024237a40` (version 0.1.2).

The successful external AAP source refresh also listed the YAML example
inventory as a playbook. The generic example now uses INI, with the local
ansible.cfg default and README aligned, so the project presents only its six
actual stage entry points. All six syntax checks and production-profile lint
pass after the format change; the 42 passing logic tests are unaffected.

## Keep dependency installation separate from SCM synchronization — 2026-11-04

Implementation commit: `f528087bd55a7117eb2fee86860bb2888549ad9d` (version 0.1.1).

The external AAP synchronization exposed that it also processes a root
requirements.yml, attempting to install the declared certified collection. Its
configured sources could not resolve that dependency. The explicit declaration
now lives in dependencies/satellite.yml, outside automatic discovery paths. This
keeps source synchronization separate from intentional execution-environment
preparation without changing the declared Satellite 6.0.0 runtime requirement
or controller settings. No dependency installation was completed.

A regression checks the automatic discovery paths and the retained dependency
declaration. All 42 offline tests and production-profile lint pass; the six
playbook syntax checks remain valid. Runtime dependencies must still be supplied
before executing a playbook, and successful SCM synchronization alone is not
evidence of runtime readiness.

## Build independently launched patching demonstration stages — 2026-11-03

Implementation commit: `ba33c694edd16334a29126b4684a4c3a2d26a624` (version 0.1.0).

The user requested separate preparation, incremental Content View creation,
host patching, full publication, promotion and read-only verification stages
for an external Satellite/AAP environment. Preparation creates a project-owned
Test/Prod path and Content View and moves only the explicit host pair. Existing
colleague-owned objects are protected by name and ownership checks.

The certified Satellite collection manages supported operations. Inspection of
its Python implementation confirmed no incremental-update action, so only that
operation uses Ansible uri with verified HTTPS. It waits for task success and
checks baseline preservation and advisory additions before promotion. Production
reuses the exact Test minor rather than generating an untested version or
bypassing the lifecycle path.

Host proof uses native RPM EVR comparison and the running kernel. A CVE may
resolve to multiple advisories; absent components do not create false failures,
but at least one installed affected component and all installed affected
components must verify. Reboots combine system hints, advisory hints, stale
processes and kernel state. Full updates also require a strictly newer installed
version of an independent witness package. Modular-only advisory metadata is
refused instead of guessing a module-stream policy.

Forty-one offline tests, all six Ansible syntax checks, the available
production-profile lint check, and legacy Python grammar parsing of the host
proof passed. These checks do not establish a live patching or recovery result.
The source contains synthetic inputs only; credentials and environment
configuration remain outside the public repository. No dependency installation
or remote prep, patch, reboot, snapshot or restore was performed. AAP SCM project
creation is separate from later Job Template/CaC deployment.

## Initialize the project — 2026-11-03

Implementation commit: `a3c7cdfa6ae10c97f2b637c75f5a44193248e457`.

The user requested a public repository named `RHEL-sniperpatching` and its
addition to the AAP Advanced Features collection as a Git submodule. The
initial README establishes the project and provides a commit for the parent
repository to reference. Patching scope and implementation remain undecided.
