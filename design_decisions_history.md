# Design decisions history

## 2026-11-04 — Publish the configured stage surveys

The five remaining demo Job Templates were created with the existing runtime,
inventory and credentials. Saved input and survey readbacks passed, launch
prerequisites were satisfied, and all pre-existing template definitions,
credential associations and surveys were preserved. No demo launch was made
as part of this configuration step.

The public repository now includes the same generic survey definitions.
Protected organization, host, repository and credential bindings stay outside
public source. Cutoff publication saves Test explicitly; its survey asks only
for the date. No test mirrors these reversible data definitions; schema and
actual Controller readbacks were reviewed.

Implementation commit: `17593e593744984fd0baef8d0bad4a0dcc87ce11`.

## 2026-11-04 — Bound repository updates between RHSA demonstrations

The owner requested one RHSA at a time followed by a repository cutoff
halfway before the next advisory. Full publication now accepts an optional
issue-date cap, preserves the serving advisory set, verifies actual content
in Library, and promotes only the exact checked candidate to Test. The public
survey requires a cutoff for this demonstration; empty playbook input retains
the separate latest-content mode. Same-day advisories cannot be separated by
an intervening calendar date. Full host patching still requires an independent
strictly higher-EVR witness.

The owner also selected the existing private encrypted CaC companion schema;
public playbooks and generic surveys remain in this repository. Configuration
capture and live execution are separate verification steps.

Validation: all 81 existing regression tests passed; all 8 new cutoff tests
passed after fixture-only corrections. Seven entrypoint syntax checks and
production lint passed with the existing local collection. No live publication,
host patching or reboot was performed by this implementation.

Implementation commit: `59e9e8ca9c13be05e9c7bd780ba249d7a3e0667a`.

## Accept multiple survey CVEs with live per-ID resolution — 2026-11-04

Implementation commit: `01aa887aee80156ac2feb59f8f255a7fa606bfa8` (version 0.4.0).

The user requested multiple CVE IDs in the JT survey and explicitly required
dynamic mapping. The required textarea accepts one RHSA or up to fifty CVEs
separated by commas, spaces or newlines. IDs are normalized and deduplicated.
Every CVE is queried separately against live Satellite metadata in the selected
repositories, complete advisory details must confirm each association, and
an unresolved input stops the run. The advisory union is deduplicated before
incremental creation. The README catalog is never read for runtime mapping.

Native RPM proof now retains the per-input advisory associations and requires
installed affected-component proof for each requested CVE. One passing CVE
cannot conceal an absent or vulnerable component for another. Existing
single-RHSA behavior and epoch validation are preserved. Job reports include
the requested IDs and their dynamically resolved advisory mapping.

The reusable survey definition contains a free-text ID field and explicit
Test/Prod selection, without fixed CVE choices or a mapping table. The relevant
minor-update JT can use it without changing the independent demonstration gates.
All 81 tests pass, including actual Ansible resolver executions where identical
survey input produces changed results after the synthetic server metadata
changes. Missing-CVE failures, overlaps, per-CVE proof and baseline preservation
are covered. Seven syntax checks, production lint, legacy host-Python grammar
and a publication privacy scan pass. A read-only live Satellite probe resolved
two CVEs to three unique RHSAs and rejected an unmatched additional CVE.
No actual preparation, Content View update, patching, reboot or snapshot ran.

## Document demonstration advisories and CVE selection — 2026-11-04

Documentation commit: `8d4e25540361f90b494b9bbb4d7af90cc4e66042`. Runtime version remains 0.3.0.

The user requested the usable RHSA list and an easy CVE mapping. The README
now lists all fourteen demonstration candidates with issue date, component,
severity, associated CVEs and links to Red Hat's public advisories. Its forty-one
CVE/advisory associations cover forty distinct CVEs. Only public advisory
metadata is included; no environment identity or per-host vulnerability state
is recorded.

The examples explain that one CVE can resolve to several RHSAs in the selected
repositories and that an RHSA selects one advisory. A direct read-only Satellite
lookup of CVE-2023-40217 returned the two documented Python advisories, matching
their public Red Hat pages. The catalog also explains the earliest issue date
and automatically derived baseline cutoff. Catalog completeness and exact
CVE associations were checked against the captured advisory metadata, and the
staged documentation passed whitespace review. No runtime code changed and no
preparation, patching or reboot ran.

## Prepare a cutoff baseline before the full security advisory set — 2026-11-04

Implementation commit: `7a0a2fdd15d55c25b57eaeaad581b00e7080b2c1` (version 0.3.0).

The user requested this behavior in the preparation playbook. Prep now reads
outstanding security RHSAs from the explicit host pair, resolves their issue
dates only in the selected repositories, and chooses the day before the earliest
one. An explicit date must precede every selected RHSA. Missing or ambiguous
metadata stops preparation before publication.

Publication now creates the baseline in Library first. Prep reads its actual
advisories and requires the selected set to be absent before promotion and host
reassignment. The same validated version initializes the dedicated Test/Prod
path. Interrupted publication is revalidated before promotion into empty
destinations, using the recorded cutoff. Established later versions are
preserved on reruns. The preparation report includes the cutoff and excluded set.

All 67 tests pass, including five real Ansible executions against synthetic
local Satellite modules covering fresh preparation, contaminated content,
invalid cutoffs, interrupted publication and established newer versions.
All seven playbook syntax checks and production-profile lint pass. The cutoff
calculation was also checked against the prior protected fourteen-advisory
capture. No live preparation, publication, promotion, host reassignment,
patching, reboot or snapshot was executed for this change.

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
