# Design decisions history

## 2026-11-12 — Protect process diagnostics and preserve read-only check mode

Implementation: `7fd172ac84871ad7c08ca81a1d660e1be8badae6`, version **0.5.8**.

The user requested review and focused fixes before the next AAP re-test, using
Agent_generated_code_review. Two real local Ansible regressions reproduced
unprotected stale-process command arguments and a runtime probe skipped during
check mode. The corrections protect that process output while retaining its
registered reboot evidence, and execute only the read-only probe in check mode.
No other functional behavior or Python helper implementation changed.

The review added linked supporting-code rationale, all nineteen filter
interfaces, source/caller/alternative dispositions, inputs/output/recovery
instructions, a TLDR, a manual process diagram and reproducible checks. The
existing read-only Check patch job is documented as a repeatable deployed
functional test. The retained standard RHEL 7.9 kernel scope and existing manual
Test-before-Prod stages are explicit; no new EE, workflow or platform support.

All 98 local tests and the six stage interfaces/syntax plus diagnostic syntax
passed under both Core 2.16.19 and isolated Core 2.15.11, using supplemental
Python 3.12.14. Strict production lint passed. Both behavioral regressions failed
before the fixes and passed afterward. Current-source, baseline-history and
exact staged-patch Gitleaks checks reported no leaks. Independent content and
host assessments found no further worthwhile functional defect.

The owner approved an isolated local APME service and analysis dependencies.
Public Galaxy could not supply the pinned Satellite collection; its existing
3.14.0 source was imported only for supplemental analysis. All six validators
returned, and 237 leads were dispositioned without applying generated changes.
Two internal coverage failures, upstream analysis dependency advisories and
actual vendor-image/CaC provenance remain explicit gaps. No remote jobs or host
changes occurred. The temporary service is separate from AAP and other reviews.

The [dated evidence](docs/review-2026-11-12.md) and
[directive matrix](docs/review-coverage.md) preserve exact policy revisions,
accepted deviations, contradictions and limitations. This is a completed focused
fix batch, **not full review acceptance**. Required tool/security evidence and the
subsequent complete AAP end-to-end re-test remain outstanding; no successful
Code_Review report is claimed.

## 2026-11-11 — Record a handover without claiming full policy review

Documentation commit: `9143b410bec8713744c000e97b06d82d5459773f`.

The user requested a Git handover before continuing in another chat and asked
about the shared review guideline. The handover links that policy and records
that no completed full-policy acceptance report exists. It distinguishes the
two recorded successful demo cycles from a complete review, and the already
resolved epoch defect from stale pending messages. Private environment evidence
and credentials remain outside public source. Functional version 0.5.7 and its
code are unchanged; validation covers the document links, staged content and
whitespace rather than new runtime acceptance.

## 2026-11-05 — Verify the first patch interval and tolerate transient reads

The real production branch fixture confirms reuse of the exact Test minor
without another incremental request. Live Test and Prod package commands and
independent fix checks passed for the same selected RHSA.

A cutoff candidate was published but its advisory inspection received a
truncated JSON reply. A fresh complete read succeeded. Only that read-only
inspection now makes up to three attempts; publication and promotion are not
retried by this control. Nine focused publication tests passed, including
transient recovery and exhaustion without repeated mutations. The live retry
then verified all serving advisories and the date cap before promoting its
exact candidate to Test. The earlier fix remains present and the next RHSA is
excluded. The failed earlier candidate was retained without consumer promotion.

The receiving AAP configuration import, object readback and read-only runtime
diagnostic also passed. Its existing Machine credential binding does not prove
SSH-key equivalence. The first cutoff has no independent extra package upgrade;
full host-upgrade handling for that no-update case remains a separate decision.

Production reuse/documentation implementation: `b0cd683a0dc43a8d5e300a825b75f3708046d4d6`.
Read-retry implementation: `fc6106fc00b1b0a2a9b33c662d14ebecc75e00fe`.

## 2026-11-05 — Preserve RPM signing-key records during host reporting

The first targeted host command succeeded, but change reporting then rejected
legitimate RPM signing-key records whose architecture is recorded as (none).
The inventory parser now retains only that narrowly validated database shape,
including its actual missing architecture. Signing-key changes remain visible;
software package and advisory validation are unchanged.

All 35 metadata and native-RPM proof tests passed, including three regressions
for valid keys, changed keys and malformed or unrelated missing architectures.
The actual before/after snapshots now parse successfully and show only the two
expected package names changed. Live fix/reboot completion remains pending.

Implementation commit: `c23a34482d1764587867deafdc58a06e71ddb263`.

## 2026-11-05 — Recover validated minor updates through Library

A live incremental update created the correct minor but normal Test promotion
failed because it had not first entered Library. The playbook now validates
actual content before promoting through Library and then Test, with force
disabled. A controlled retry can reuse one matching orphan or Library-only
minor; ambiguous history, unrelated newer content, exposed candidates and
changes to Library during validation stop the operation. Production continues
to reuse the exact tested minor.

All 95 regression tests passed, including real Ansible boundary fixtures for
fresh creation, interrupted retries, invalid content and competing Library
changes. Seven entrypoint syntax checks and production lint passed. Live
acceptance of the corrected promotion remains separate.

Implementation commit: `49585292ec5cc226c1f51a192005565712fd3900`.

## 2026-11-04 — Correct the filter type for original packages

The first live preparation failed because Satellite rejects original_packages
on an erratum filter. Preparation and bounded publication now use a separate
owned RPM inclusion filter for packages without errata, while the erratum filter
retains the issue-date cap. The package filter suppresses the older collection's
default package-name rule. Explicit latest publication removes both owned
inclusion filters so it cannot remain accidentally limited to original packages.

Actual readback after the failed attempt confirmed only the owned Content View
and lifecycle path existed: no versions or filters were published and the
selected hosts retained their original assignments. No cleanup was required.

All 89 regression tests passed, including real preparation/publication fixtures
that reject the unsupported argument and accidental RPM name rules. Seven
entrypoint syntax checks and production lint passed. The corrected live retry
remains a separate acceptance step.

Implementation commit: `7d5f77a442210af21c924db9fc9edf7f4c462c29`.

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

## 2026-11-05 — Deliver the lean end-to-end demo

Implementation `2be30c742f946b6f9c1ad93a9b7efbe14e230953` removes the artificial
upgrade witness and duplicate middle RPM proof, narrows host advisory reads, and
shortens the run/reset guide. Observed-failure protections remain. One complete
RHSA then cutoff full-update cycle passed on Test and Prod, including exact
version promotion and final verification; unchanged full runs passed only after
the package manager confirmed no pending updates.

## 2026-11-05 — Explain the human-led demonstration

Automation implementation: `2be30c742f946b6f9c1ad93a9b7efbe14e230953` (0.5.7).
The user requested a presenter sequence with exact existing Job Template names,
survey inputs, visible results and explicit pause points. The README now follows
one advisory through Test/Prod targeted patching, date-bounded full Test update,
exact-version promotion, full Prod update and a final read-only check. It uses
reported version numbers and distinguishes content promotion from installed RPMs.
Two completed cycles are documented, including the second cycle's microcode_ctl
full upgrade. Continuation from CV4.0 uses a clearly untested next kernel example;
preparation is not a reset. A read-only CVE example shows the dynamic mapping
without publishing additional content. No automation, surveys or live systems
changed, and no patching jobs were launched for this documentation request.

The requested catalog table retains all 14 advisories and their CVEs, adds
midpoint cutoff inputs and distinguishes used dates from proposed ones. It flags
same-day advisories and the final missing successor rather than inventing a
separating date. Demo ratings distinguish package proof from kernel reboot and
hardware/boot/service-dependent effects; only the Python cycles are live-proven.

## 2026-11-05 — Compact issue labels and visible cutoff dates

Implementation: `880e524261b631677ad58bcd932294f6bd0c9867`.

The user requested a more readable advisory catalog with a short issue
description rather than component names alone, and visible cutoff dates.
GitHub controls the repository page width and fonts, so the catalog now uses
five compact columns, short advisory link labels and meaningful issue summaries.
Long CVE lists and full demonstration notes remain available in an expandable
section. Existing cutoff dates are prominent; verified and proposed dates stay
distinct, with same-day and final-entry exceptions preserved.

All14 advisory mappings,40 unique CVEs,12 cutoff dates/statuses and the complete
demonstration notes were checked against the previous README. Issue summaries
were checked against the linked Red Hat advisories; multi-CVE rows are explicitly
summaries of several flaws. GitHub-flavored Markdown parsing confirms both
catalog/detail tables have14 data rows and the expected column counts. Whitespace
checks pass; interactive GitHub rendering was not verified. This is a
documentation-only change: runtime version0.5.7, automation and live systems are
unchanged, and no patching job was launched.

## 2026-11-09 — Introduce the project before its procedure

README implementation: `372da7e7511ce90c15bd9599e6c9c10da7f5915d`. The user asked for an
explanation suitable for readers unfamiliar with the project. The opening now
explains the need for targeted one-off advisory deployment, required package
dependencies, dynamic CVE resolution and the later broader update. It introduces
Content Views and separates content promotion from host patch installation.

The environment section describes the recorded RHEL 7.9 workshop host runs and
their execution runtime, separately from receiving-AAP configuration/runtime
verification. Results are dated rather than presented as a fresh live check.
Prerequisites and the human-led procedure precede reference material. The compact
advisory catalog, CVE details and cutoff qualifications are unchanged.

Focused documentation checks preserved all 14 advisories, 40 distinct CVEs,
ten procedure steps, survey labels and local links; independent review and
whitespace checks passed. Only documentation changed; automation stays at 0.5.7,
and this work launched no jobs or deployments.

## 2026-11-12 — Use native project requirements with the official Core 2.20 EE

Implementation `06066d831bf5405992ea8d73b9f71edb87bdc1b0` (0.5.9) exposes the existing Satellite 3.14.0 pin
through the standard collections requirements file used by AAP project updates.
The configured certified Hub source and existing use-case prerequisite route
supply that same version; no alternate source, credential or custom image is
introduced. This follows the owner's decision to use the official unmodified
Core 2.20 EE with runtime collection mapping.

All 98 offline tests passed inside the actual official Core 2.20.10 EE. Test
fixtures mark only repository-owned expressions as trusted through Ansible's
native API, retaining legacy-Core compatibility and untrusted synthetic inputs.
Live Satellite access, runtime readiness and host patching remain separate
acceptance checks. Version 0.5.10 records this implementation decision.

## 2026-11-13 — Preserve independent OLD and NEW demo tracks

Implementation: `1353b73ed7c8a535bb205cf67165cf737ce804b5` (0.6.0).
The user requested both environments remain available in separate directories,
with public automation and matching private CaC maintained together. Each tree
now contains seven entry points and its own unchanged runtime tasks, variables,
filters and helpers. Root forwarding playbooks were not added. Generic surveys
remain shared; tests choose a tree explicitly. Native AAP project requirements
retain the reviewed Satellite collection pin.

Existing private CaC template paths were updated in companion implementation
`8a6a77e577f6665630bc2ec30652cdce6bd6e61a`; all other logical protected values
and literal tags were preserved. Existing names and environment/runtime bindings
were retained. New-environment templates will be configured with their own
protected inputs during setup; the copied NEW tree is not deployment acceptance.

OLD passed all98 synthetic tests on supplemental Core2.16.19 in170.393s. NEW
passed all98 in the actual cached official Core2.20.10 image in246.280s, offline
without image changes. Fourteen entry-point syntax checks and all nine Satellite
module interfaces passed using installed3.14.0. Production lint passed both
trees; four existing Jinja inspection exceptions for runtime-only inputs were
reported and were not suppressed. Runtime file bytes, local Markdown targets
and whitespace checks passed. These checks do not establish a new live OLD
re-test, NEW Satellite installation or resolution of broader review gaps.

The new installation sequence references Red Hat's6.19 connected guide and
requires correct hostname/forward/reverseDNS and a RHEL package upgrade before
Satellite installation, including required reboot and subsequent verification.
No host, live template, patching, reboot, installation or CaC import ran for
this repository reorganization.

## 2026-11-13 — Add NEW DNS and RHEL host-preparation stages

Implementation: `c15fb7f61671411ea506a2753538524e4adb1130` (0.7.0). The user fixed OLD to the remote
Satellite and its own remote AAP, and NEW to the local Satellite and selected
current production AAP. The NEW setup stages therefore use their own inventory,
protected SSH identities and exact VM ownership, without changing OLD runtime.

DNS preparation validates both native scopes before additive DHCP/DNS updates;
it does not restart the shared network or overwrite conflicting resources.
Host preparation refuses installed Satellite packages, configures the documented
repositories, upgrades installed RHEL packages, reboots as required, and verifies
native RPM/running-kernel, FQDN/DNS, swap, SELinux, time and remaining updates.
The NEW SSH pins explicitly enable per-host checking rather than inheriting a
controller-wide disabled setting. No persistent trust or credential source changes.

Fourteen focused tests, two syntax checks, sixteen builtin interfaces, a real
Ansible repository-expression fixture and SSH option checks passed in the
unchanged cached official Core2.20.10 EE with networking disabled. Production
lint passed with zero findings. The offline checker initially misclassified
set_fact's documented open keys; that check was corrected and the actual
expressions were exercised. A test-harness string-escaping defect was fixed;
these failures did not execute live operations. Local links and whitespace pass.

Companion implementation `e00bd02abbb49e6d5039059fd841e40b30dbace9` defines NEW setup only,
preserving the preceding OLD ciphertext byte-for-byte in a separate encrypted
archive. The existing shared importer contract/counts, protected input source,
and literal-template roundtrip passed. No new importer or wrapper was added.

No live import, setup, DNS/swap change, RHEL update or Satellite application
installation was performed. Production is absent from the importer's current
destination inventory and token store; the existing registered AAP is a different
installation. Registry presence was checked against the live credential hash
without printing tokens. Adding production's API access to the shared store
requires a separate explicit decision. Satellite application setup, dedicated
NEW demo EE and full NEW end-to-end acceptance remain unfinished.

## 2026-11-14 — Keep collection selection in each track's EE

Implementation `80b785e1066daef32d1a7c57f721115235103b45` (0.7.1)
removes the shared root collection requirement. AAP project content takes
precedence over EE collections regardless of version, so the inherited shared
Satellite pin could replace NEW's selected version. Each track retains its
own dependency manifest and must use an explicitly selected immutable EE.
OLD's source tree and runtime are unchanged. Built-in DNS/RHEL preparation
can run in the existing Core 2.20 management EE before the dedicated NEW demo
runtime is qualified. Both existing track-manifest checks and whitespace
validation passed. Live import and host preparation remain separate outcomes.
The owner subsequently selected the certified Satellite operations installer
role where compatible with the target; its release qualification and actual
installation are unfinished.

## 2026-11-14 — Install NEW Satellite packages after live prerequisite verification

Implementation: `a2db9865072902304a60636d3b8583eba73e8ff9`, version **0.8.0**.

The user requires an updated RHEL9 host with final hostname/DNS before
Satellite6.19 installation and selects the certified installer collection.
Add a separate package stage that rechecks exact guest identity, resources,
DNS, SELinux, synchronized time, documented repositories, newest running
kernel and zero pending RHEL updates before installing the satellite package.
Its result explicitly distinguishes packages from configured application.
Actual cached Core2.20.10 passed seven builtin interfaces and playbook syntax.

The separate installer EE recipe preserves the official digest-pinned
Core2.20.10 base and adds only the SHA256-verified certified operations4.0.0
collection. The local image, vendor layer/runtime preservation and installer
role syntax passed. Publication awaits an established protected registry login;
no credential changes or installer execution are implied. OLD is unchanged.

## 2026-11-14 — Configure NEW Satellite with certified operations and current API content

Implementation: `a62db6b5cdf193deb358d2245040ccc46bcd2035`, version **0.9.0**.

Run the certified installer after the verified NEW package stage. Validate
the installed native scenario, answer mapping and Puppet parameter definitions
before writing only the initial administrator fields as root0600. Preserve all
other answers and refuse a different existing credential. Credentials come
from the existing native project pattern and never enter command arguments.
The role uses the exact verified setup EE; final service and authenticated
HTTPS checks require the installed native CA with certificate validation.
Fourteen builtin interfaces, syntax and seven real Ansible preservation,
idempotence, redaction and refusal fixtures passed on Core2.20.10. Installed
package/schema evidence is verified; live application configuration is pending.

NEW pins certified redhat.satellite6.0.0 and follows its filter-only API.
Remove three obsolete rule_state arguments while retaining explicit rule tasks.
The certified source establishes this behavior since4.0.0. Twenty-four NEW
fixtures, nine installed module interfaces and six stage syntaxes passed on
Core2.20.10; the same24 shared regressions passed on OLD Core2.15.11. OLD source
and3.14.0 pin are unchanged. Full demo EE and live acceptance remain separate.

## 2026-11-14 — Qualify the separate NEW demo execution environment

Implementation: `248bddca7597169a5c762c0b1fe888c957e1eeb2`, version **0.10.0**.

The user requires current certified Satellite content on NEW Core 2.20 and
explicit per-track execution environments. Add a separate demo EE recipe with
the exact certified Satellite 6.0.0 archive on the unchanged official Core
2.20.10 base. The mandatory requests/PyYAML dependencies already belong to the
vendor base, and the collection vendors its API utility. No additional package
or unrelated runtime change is needed. OLD source and its legacy pin remain
unchanged; the separate operations installer EE is preserved.

The actual built demo image passed its vendored API import, twelve NEW fixtures,
nine collection interfaces and six stage syntax checks. Python/RPM inventories,
runtime configuration and the original base-layer prefix match the vendor base.
Publication passed an uncached manifest, configuration and every-blob SHA-256
and size check. Public source contains generic build provenance; receiving-Hub
references and credentials remain in protected configuration. Private demo
bindings and full patching acceptance are separate unfinished steps.

The NEW Satellite 6.19.6 installation also passed all four AAP setup stages,
including native service health and authenticated HTTPS with certificate
validation. Documentation now distinguishes that verified installation from
unfinished application CaC, client registration and the NEW patching demo.
It preserves the pending operator review of the normal-client deployment mode
rather than treating successful VM creation as approval. Version 0.10.1 records
this decision and the current handover checkpoint.

## 2026-11-14 — Qualify NEW Satellite HTTPS through both API clients

Implementation: `4f88a64c3a70107f12019f572018b33f681cc62c`, version **0.11.0**.

The installed NEW Satellite uses its native CA. Capture that public certificate
through the existing verified guest connection and retain populated values in
private Vault data. The existing project credential can inject it as a temporary
file through `SATELLITE_CA_PATH`, which certified collection 6.0.0 supports
directly. The incremental-update URI now uses the same optional path. Empty
input preserves default trust and certificate validation remains enabled.

The read-only runtime check verifies authenticated collection and native URI
requests because the demo uses both HTTP implementations. It does not contact
managed clients or change content. The existing image is unchanged. Thirteen
focused NEW fixtures, nine collection interfaces, six stage syntaxes and the
runtime syntax passed on actual Core 2.20.10 with networking disabled. Offline
production lint passed with zero findings; an existing dynamic survey-input
inspection exception remains visible. OLD source and its runtime are unchanged.

Companion implementation `bd79637ac501007e066e5015ba5532bdf33a89ff` extends the
same credential type with an optional CA field and adds the normal read-only
runtime template, retaining all existing usernames, passwords and setup bindings.
Protected inverse comparison and native Vault/import checks passed. Publication
is separate from live import and AAP-to-Satellite runtime acceptance. Version
0.11.1 records this implementation decision.
