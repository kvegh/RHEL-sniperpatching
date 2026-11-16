# Design decisions history

## 2026-11-16 — Verify the imported native checkpoint configuration

Functional implementation: 339009520fd20b7eb431f719ca25764d0755d37e
(feature 0.16.0). The later 0.17.0 visualization is preserved byte-for-byte;
checkpoint automation is unchanged.

The approved encrypted declarations were published through the existing private
route after explicit publication approval. The normal shared CaC recovery import
succeeded, and read-only acceptance matched all sixteen NEW templates, saved
playbooks/credentials/EEs/inventory/extra-vars, the exact three success-only nodes,
the single required first-sync JSON survey and protected inventory/four hosts.
Launch inspection required the handoff without requesting a new secret.
The workflow and two new jobs had zero executions at acceptance.

Retain the first failed import: it never started because its shared-source
Galaxy collection download failed checksum validation. The exact rejected bytes
and digest were absent from available API evidence. A fresh complete read matched
current metadata; one normal recovery passed with integrity/TLS controls unchanged.
The shared-source revision also advanced, so no root-cause or causal-fix claim is
made. Existing shared integrity investigation and unrelated holds remain intact.

This is recovered configuration acceptance plus 35 focused synthetic tests, not a
real fresh installation, cold capture or live survey handoff. Those checks await
the next genuine authorized pre-sync boundary. No current populated VM was
stopped, reset or snapshotted, and no broader rollback scope was resumed.


## 2026-11-16 — Wire the approved native checkpoint workflow and bounded handoff

Implementation: 339009520fd20b7eb431f719ca25764d0755d37e, version0.16.0.
The user selected the native three-job AAP workflow. Use success-only
installation, cold checkpoint and original-guest verification nodes, each with
its saved existing credentials. Keep content synchronization separately
operator-launched; the existing shared CaC importer owns all definitions.

Native ancestor artifacts connect the three jobs. The final verification exports
one JSON string containing only completion, checkpoint, original VM and public CA.
The foundation's one required native textarea survey accepts that declared key
while arbitrary-variable prompting stays disabled. Parse it strictly as data,
reject unexpected fields/types, missing/failed proof and wrong VM/CA, then check
native cold metadata and API readiness before writes. Remove the stale saved
foundation CA. This is an operator-mediated copy of the actual successful final
artifact, without authenticated originating-job provenance or a new service.

The selected Core 2.20.10 EE passed35 focused tests in166.904s, including an actual
final-job serialized export into the separately launched foundation fixture.
Earlier11related CA/installer tests remain valid;20existing frontend tests passed
after only the displayed version was synchronized. The public main0.15.3
presentation changes were preserved while rebasing unpublished work. Bounded
review found no concrete defect in this source or the exact encrypted candidate:
16JTs, one3-node workflow, saved credentials unchanged,13unrelated JTs unchanged,
no workload/schedule definitions and no static success/CA override. Fresh live
workflow execution, survey transport and cold capture remain unverified; no
formal acceptance or current-VM snapshot is claimed.

The independent approved case-two archive was published first at private
1bbec39a1ed632b02d793e17d42889ef3d7857e0:14encrypted receipts plus README0.14.13,
with canonical configuration unchanged. No later-cycle evidence was added.


## 2026-11-16 — Guard a future NEW Satellite cold installation checkpoint

Implementation: 3931027601c3ad4492d9a4c5e6094bde4f4380fd, working version
0.16.0 (unpublished). The user explicitly selected a cold checkpoint named
post-satellite-install after successful installation and before the first sync.

Keep the existing certified installer, native Machine/API credentials and private
whole-file Vault configuration. Separate guest and hypervisor jobs retain their
own credentials. The selected libvirt module exposes no snapshot-create action;
the existing AAP helper has AAP-only ownership constraints. Add a NEW-only
standard-library virsh/qemu-img helper with exact identity/storage/provenance
guards, a per-VM native lock, bounded ACPI shutdown, verified cold readback and
restart. Refuse foreign snapshots and unsupported storage; preserve uncertain
capture outcomes without automatic retry or restart.

Share native service/TLS verification with the installer. Bind successful final
guest verification to its original VM UUID and public CA. Initial content setup
requires that result plus the owned cold checkpoint before any content write.
An integration review identified the missing final-result dependency; the
implemented correction and negative regressions close that gap. Read-only
preflight never claims capture, and temporary SSH/CA files are cleaned up.

The selected Core2.20.10 EE passed 33 focused helper/orchestration tests; related
CA/installer checks passed 11 tests. Four playbook syntax checks passed before
the final artifact-binding addition, which is covered by the focused suite.
The helper also passed its 22 focused tests under Python3.12 and3.9. These are
synthetic/local results, not fresh live capture or formal acceptance. Review of
the final trailing-blank-line correction found no behavior change.

Native AAP workflow versus separate manual-job sequencing is awaiting the
existing user choice; new template/CaC wiring and publication remain pending.
The current Satellite already has synchronized content and was not stopped,
reset, reinstalled or snapshotted. Preserve completed nine-cycle evidence and
all separate private-publication, held image/rollback and OLD/review boundaries.


## 2026-11-16 — Record all nine chronological NEW procedures

Automation correction: implementation
61ba62232e425a1a7497cd0813c8249976325e43 (0.14.11). Final-cycle executable source:
28ab1a5da4984da5e9c768d3704a61720788d086 (public 0.15.2), with the qualified
automation tree unchanged by the intervening presentation updates.

Finish the agreed ten-CVE catalog on the original pair without resetting or
recreating clients. All nine advisory cycles and 81 distinct successful normal
stages passed. Both clients reached full 10.0 through October 24, stayed on
RHEL 9.4 and ran kernel 5.14.0-427.40.1.el9_4. Final native evidence verifies
all ten selected CVEs, including the running kernel for four CVEs and all
installed witness builds for six userspace CVEs. Preserve the five earlier
failed attempts and the correctly already_current fourth-case Test recovery.

Update current summaries and add a sanitized acceptance table; retain raw
events, identities and hash-linked receipts under the existing whole-file
Vault mechanism. This records actual runtime evidence, with no new executable
or infrastructure behavior and no full formal-review, exploitability,
installation-ISO equivalence or latest-source full-suite claim. The separately
requested pre-sync Satellite snapshot and its pending power-cycle choice remain
outside this acceptance; existing held and OLD scopes are preserved.

## 2026-11-16 — Include standard versioned modules in NEW running-kernel proof

Implementation: `61ba62232e425a1a7497cd0813c8249976325e43`, version **0.14.11**.
The fourth targeted Test kernel update installed and booted the fixed build,
then failed verification because older retained `kernel-modules` and
`kernel-modules-core` RPMs were treated as ordinary userspace duplicates. Add
only those two names to the existing NEW runtime-kernel allowlist; keep exact
running version-release.arch matching and native fixed-EVR comparison. Older
fallback builds stay visible in proof. Userspace, tools, unknown names and
installed-architecture checks remain strict; OLD source is unchanged. This is a
focused correction within the authorized procedure testing, with no package
removal, content rebuild, runtime/dependency or architecture change.

The before-fix positive regression failed as intended. Existing selected-EE
qualification passed 38 NEW tests in 0.013 seconds and 31 OLD tests in 0.004
seconds, with seven NEW-only skips under OLD. Seven new methods cover 22
scenarios. A replay of the actual failed package snapshot with native RPM
4.16.1.3 passes after the correction, while old or unmatched running-release
and missing-matching-module controls fail. The EE tests use synthetic RPM
fixtures; its Python lacks native RPM bindings, so the native comparator replay
is recorded separately. Independent scoped source review found no concrete
defect. Raw failures and complete qualification output remain whole-file Vault
evidence. Matching-EE strict lint and full formal review remain unperformed.

The first three complete chronological cases passed on both original RHEL 9.4
clients. Corrected fourth-case live recovery is still pending: retry only Test
against its existing immutable 4.1, verify the original Prod baseline before
exact promotion, then complete Prod and the August 15 bounded full update. An
already-current retry must retain the original transaction/reboot failure
history rather than claiming an uninterrupted case. Keep remaining cutoffs,
OLD boundaries and shared/image holds intact.


## 2026-11-16 — Record first complete NEW acceptance and catalog validation

Documentation/catalog-status checkpoint: `273d423a0f9ccf97f699b61a3eb07e2bbd2edeeb`,
version **0.14.10**. Executable automation is unchanged from the qualified/live
0.14.9 prefix correction. Catalog candidates, fixed builds, dates and sources
are unchanged; only its previously unverified applicability status is updated.

The first RHSA-2024:3339 case completed targeted Test/Prod minor 1.1 and bounded
full version 2.0 through May 23, with actual reboots, native fix/smoke and no
pending-update/reboot checks. Independent Prod verification and a fresh native
matrix confirm original identities/consumers, 447 RPMs and kernel
5.14.0-427.18.1.el9_4 on both clients. The first selected witness is fixed and the
remaining nine witnesses are below their first-fixed builds. Earlier failures
and the multiple actual stage-source revisions remain preserved in private Vault
evidence; this is not an uninterrupted first-run or full formal-review claim.

Close only the achieved NEW procedure and list-validation tasks. Preserve the
broader deployment parent's blocked OLD child and held image/generic work; use
specific completed NEW prerequisite records rather than force-closing unrelated
work. The next chronological case started on prior immutable source 9a162e3.
Remaining eight RHSA/nine-CVE cycles retain per-cycle cutoffs and separate actual
outcomes. No guest reset, reinstall, new instance or OLD action was performed.


## 2026-11-16 — Preserve exact NEW version digits through AAP transport

Implementation: `d7e14bb2b67254ebbbcf6ba6580d0ec24ee251c3`, version **0.14.9**.
Controlled diagnostics proved a native float request against a string Test
version, while the lifecycle path was correct. The unchanged selected Core 2.20
runtime reproduces float/date re-resolution of quoted and unquoted `!unsafe`
scalars from the upstream AWX string-writer pattern. The exact deployed writer
was not directly read; source behavior and local reproduction match both live
failures. Never reconstruct a version from a float because 2.10 becomes 2.1.

Require text and an optional single `v` prefix, remove only that prefix into a
fresh string, then compare/promote/read back the exact remaining version. Keep
numeric/Boolean/list rejection, normal lifecycle and no-force guards. Add a
NEW-only survey prescribing v2.0/v2.10; retain the OLD source/shared survey.
No controller trust setting, runtime, credential or architecture change is made.

All seven regression methods are covered by six confirmed original-method
passes plus a focused final-method recovery in 9.312 seconds. The original
suite final output/end time/duration were lost and remain unknown. The recovery
captured output/result/timing inside whole-file Vault evidence before returning.
Independent scoped static review found no concrete defect. Matching-EE strict
lint remains unavailable; no tool was installed or full formal review claimed.
Publish and import/read back the protected survey-only change normally, then
verify the actual prefixed promotion/Prod update before first-cycle acceptance.


## 2026-11-16 — Diagnose exact-version equality before Prod promotion

Implementation: `4a50e1af12f1dc0c888eb48371f7002d641074e0`, version **0.14.8**.
The bounded May 23 publication and Test full update passed on 0.14.7; the next
Prod promotion stopped before mutation at exact-version equality. Actual saved
input and the returned Test row pass the unchanged guard offline. A numeric
control fails but does not establish the failed live job's runtime type.

Add only types, guarded string lengths and comparison results to that existing
failure message. Do not coerce numeric versions: for example, 2.10 cannot safely
be recovered from 2.1. Preserve the exact Test-version comparison, normal prior
environment, no-force promotion and exact final readback. Five regression methods
with nine real local playbook invocations passed in 42.850 seconds in the
unchanged selected EE, covering legitimate 2.0/2.10 strings, wrong versions/path,
non-string controls and wrong final readback. Standalone host strict lint cannot
resolve the qualified collection; the matching EE has no installed linter.
No tools/dependencies were installed and no full formal review is claimed.

Run one normal controlled promotion on this source and inspect actual bounded
diagnostics before changing semantics or proceeding to the Prod host update.
Keep the original failure as private whole-file Vault evidence, preserve held/
shared/OLD scopes and distinguish this diagnostic checkpoint from a completed
first full cycle or all-CVE acceptance.


## 2026-11-16 — Normalize the native calendar date proven by AAP

Implementation: `63fe436499d7a19b8dd6ac84db3ff99f777f60ba`, version **0.14.7**.
The follow-up documentation commit records this actual implementation ID without
changing that tested executable version.

The controlled live retry identified `_AnsibleTaggedDate` at the publication
guard. Its stored cutoff was the intended ISO text, but the validator received a
native calendar object. The runner's conversion point remains unknown. Both
failed attempts stopped before repository sync, filters or publication, so the
same tested 1.1 content remained serving and no new content version was created.

Normalize only native calendar dates with `isoformat()` before the same strict
text/calendar and advisory-retention validation. Exclude datetime timestamps and
retain rejection of arbitrary objects rather than coercing their string forms.
Empty/latest semantics and all content ownership/promotion boundaries remain
unchanged. The actual native-date regression failed before the correction and
passed afterward. All fifteen publication tests passed in 82.908 seconds; saved
actual inputs and all 4,456 immutable advisories passed through both JSON text
and native YAML calendar types in the unchanged selected EE.

The separate scoped CoP repeat also passed on source `22b21e5`, preserving all
material content and both full 443-RPM client inventories, identities, consumers
and kernels. Native repository syncs and execution-local CA-file handling explain
reported changes; no zero-change or full CoP-feature compatibility is claimed.
Corrected full publication and complete NEW/CVE acceptance still require their
normal AAP execution; full formal review and held/OLD work remain separate.


## 2026-11-16 — Diagnose the live cutoff rejection without disclosing its value

Implementation: `cde7988fafce8416ca22e470093aa1d033f64daf`, version **0.14.5**.
This **0.14.6** documentation checkpoint records its actual commit; executable
content and runtime dependencies remain unchanged.

The first real targeted Test/Prod sequence passed on an identical minor,
including actual reboots and native fix/smoke proof. The following full-update
job supplied the intended May 23 cutoff but rejected it before any repository
sync, filter change or publication. Independent native reads confirmed the
existing serving versions remained unchanged. The same saved variables and
all 4,456 actual published advisory rows pass unchanged validation offline in
the selected EE, through JSON and safe YAML transport. Native unquoted YAML
dates are a reproducing negative control, not proof of the live input's type.
The original cause remains unproven; do not change the cutoff or claim a fix.

Add only sanitized date-error diagnostics: reason, runtime class and string
length. Keep accepted types, exact format, valid-calendar and advisory-retention
checks unchanged; omit values/repr and suppress the calendar exception context.
Eight affected tests passed in 21.307 seconds in the unchanged selected EE,
including real native templating, malformed/non-string rejection, value
suppression and publication/preservation boundaries. Actual-data replays also
passed. Raw inputs, outputs, immutable runtime provenance and unknown test-start
timing remain accurately labeled in private Vault evidence.

After the separately scoped CoP repeat/preservation check is terminal, run one
controlled normal publication with the same explicit cutoff and inspect the
actual diagnostic result. No full-update, complete NEW or formal review
acceptance is implied by these diagnostics or offline checks. OLD source and
all existing holds remain unchanged.


## 2026-11-15 — Select the repository copies serving each registration destination

Implementation: `01f476240c0ef45fa2bbd7f21d6ac2273380d6a3`, version **0.14.3**.
This **0.14.4** documentation checkpoint adds the actual implementation ID;
executable content and runtime dependencies are unchanged.

The normal direct-registration run stopped before guest access because its
published-version query returned eight archived/Library/Test/Prod repository
copies. The native API supports intersecting that version with the selected
lifecycle environment. The certified resource-info call now supplies both IDs;
live read-only checks returned exactly the two serving repositories for each
destination. Existing ownership, exact-pair, product, RHSM-label and GA-baseline
guards remain unchanged; no deduplication or broader access was introduced.

Three affected regression methods passed in the selected unchanged EE in
127.392 seconds: normal registration ordering/preservation, repeat/idempotency,
and destination selection with refusal of an unexpectedly unscoped response.
These checks supplement the earlier full 140-test checkpoint; they do not
establish corrected live registration or full NEW acceptance. The next test is
the normal AAP registration job, followed by registered-host applicability and
the authorized chronological nine-advisory/ten-CVE procedure.

Full proactive regular RHEL 9.4 BaseOS/AppStream synchronization and the frozen
GA publication/promotions have now completed through AAP. Independent actual
serving-version checks confirmed the GA advisory boundary, selected-fix
exclusions and original latest affected builds in Test and Prod. Full ISO
identity and complete NEW/CVE patching acceptance remain unverified. Earlier
entries below retain their original historical state.


## 2026-11-15 — Register the original NEW pair directly to served GA content

Implementation: `388fdc58fecc7c77fd139a3fd6f8f01290340841`, version **0.14.0**.

The owner requested testing the procedure on the two original clients, fixing
playbooks where necessary and then demonstrating the selected CVEs in order.
The new registration stage verifies the already-serving original GA content,
uses certified modern activation-key bindings and native Global Registration,
and refuses a foreign consumer or changed RPM baseline. It reuses the selected
public CA and Machine/API credentials, with package updates and unrelated
integrations disabled. Temporary API trust has independent controller/client
lifetimes; strict guest SSH pins precede facts and are removed on task exits.
Existing equal CA anchors are preserved; conflicting anchors stop. No missing
content is published and no temporary Library registration is introduced.

NEW patch/check also establish their existing strict SSH trust before facts,
with guarded cleanup. Their original target task dictionaries and both
localhost plays remain unchanged apart from nesting. OLD has no source delta.
The runtime probe covers the new stage and certified registration arguments.
The public catalog now supplies nine exact chronological RHSA/cutoff inputs for
ten CVEs; shared/cumulative fixes remain distinct from independent transactions.

The final registration fixtures passed eight tests in the selected unmodified
demo EE with networking disabled. Three focused SSH/redaction/runtime tests,
including eight pin lifecycle cases, and the two changed host-playbook syntaxes
also passed in that EE. Independent integration review found and corrected
inventory scope, API-CA lifetime and pin-fixture coverage issues before any
client operation. Supplemental strict lint on Core 2.16.19 with verified
Satellite 6.0.0 returned zero rule findings, but an ignored Jinja-rule exception
limits that coverage. This is not full policy acceptance: actual registration,
registered-host/DNF applicability and the full corrected AAP procedure remain
unverified.

The initial broader candidate ran 140 tests: 138 passed and two source-inspection
fixtures still assumed flat patch tasks. Version **0.14.1** reuses recursive
traversal without weakening their assertions. All ten content-boundary tests
then passed; actual Core 2.20.10 / Python 3.12.15 / Satellite 6.0.0 inspection
confirmed eleven module interfaces and seven stage syntaxes. The read-only
local verification harness needed a temporary Galaxy-cache directory; the
selected image and deployed runtime were unchanged. The final source rerun
passed all **140 tests in 623.437 seconds**, with the tested runtime
source matching the frozen checkpoint. Source-inspection fixture
correction implementation is `06a56567e1bd9bd4ebfd50c6b671859cc35732c4`.

Normal CaC import/readback matched fourteen templates and four declared hosts,
including protected variables, credentials, surveys and launch controls. The
normal AAP runtime check passed on that same published executable checkpoint,
proving actual Core 2.20.10, Python 3.12.15, Satellite 6.0.0, all seven syntaxes
and strict-TLS collection/native URI reads. This **0.14.2** documentation
checkpoint changes no executable content. Real GA publication, direct client
registration, DNF applicability and complete NEW/CVE patching acceptance remain
unfinished.

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

## 2026-11-14 — Preserve in-use credential schemas during CA delivery

Correction: `260f94c286ff094a57ffc5db5a58fbc32c1a2868`, version **0.11.2**.

The initial live import failed at the credential-type update; its existing input
schema and API credential remained unchanged. The upstream Controller API blocks
input changes for a type already used by a credential. Keep that schema and
the existing credential intact. Supply the public CA through the already chosen
private project-configuration path instead of extending a native input schema.

Standard Ansible tasks create a mode0600 CA file in a private native temporary
directory and pass its path explicitly to the certified collection and native
URI. A forced handler removes the file after success or failure. Existing
environment-provided paths and default trust remain supported. This adds no
credential type, credential, image change, global trust update or authentication
source. Private correction `6d3178885ba55f97b2f73926b3df1cec35146b69` restores
the original type/credential inputs and supplies only public CA configuration
to the new read-only runtime template; all passwords and other values remain.

Fourteen focused fixtures passed on the unchanged NEW Core2.20.10 EE, including
real Ansible file permissions and cleanup on both success and deliberate failure.
Nine collection interfaces, six stage syntaxes and runtime syntax passed.
Production lint passed on19files with zero findings and two existing dynamic
inspection exceptions. OLD is unchanged. Live import and runtime acceptance
remain separate. Version0.11.3 records the correction.

Live follow-up: the corrected normal CaC import and read-only runtime job both
succeeded on 14 November2026. Actual Core2.20.10/Python3.12.15/Satellite6.0.0,
six stage syntaxes, module interfaces and both verified authenticated HTTPS
paths passed, including CA-file cleanup. No clients or content were changed.
Version0.11.4 records this acceptance of implementation260f94c; the complete
NEW patching demo and remaining stage bindings are still unfinished.


## 2026-11-15 — Qualify only the selected CoP content paths

Recorded 2026-11-15T14:41:43.264287+00:00. Implementation
`8fb97532b32df1c7e8f3892f71c99aab2a636c92` (candidate 0.12.0) prepares
the NEW content foundation, combined EE recipe and RHEL 9.4 CVE catalog.

The owner challenged an indefinite hold based solely on CoP’s declared
Satellite 5.8.0 dependency and accepted focused qualification with the selected
certified 6.0.0 collection. The unchanged CoP 1.5.0 release matched its official
asset digest and all 264 reviewed files. Four native syntaxes, four rendering
groups and ten actual module-constructor acceptances passed on Core 2.20.10;
a negative control correctly rejected legacy rule fields in the filter module.
This establishes the selected offline interfaces, not blanket or live support.

The owner explicitly selected proactive immediate synchronization and bounded
content to 9.4 and at most 9.5. The foundation requires an explicit minor list,
refuses rolling/later versions and on-demand downloads, verifies exact repository
bindings and ownership, and preserves an existing content view. Its final source
passed native syntax plus nine focused policy/minor/binding guard cases.

The existing preparation playbook must own the first filtered-baseline
publication. Publishing an unfiltered initial version would bypass that path.
The foundation therefore leaves a new CV unpublished and performs no activation
key creation, registration, publication, promotion or client patching. Initial
registration order, actual minor availability and sufficient full-sync capacity
remain unresolved deployment prerequisites. No live foundation change occurred.

Primary Red Hat research found ten CVSS 7-or-higher RHEL 9.4 candidates fixed
before 9.5 GA: four Important and six Moderate, grouped into nine RHSAs. Actual
client package/configuration applicability remains unverified. The catalog
explains cumulative kernel/OpenSSH fixes, component prerequisites and excluded
already-fixed or unsuitable examples. A minor jump is not needed merely to
obtain ten candidate IDs; it may not provide ten independent patch cycles.

Candidate 0.12.1 records the real implementation ID. Source publication is
separate from building/publishing the combined image, current CaC adoption,
server idempotency and final AAP patching acceptance. Existing OLD scope and
independent deployment feature freeze remain preserved.


## 2026-11-15 — Validate and demonstrate the agreed CVE catalog

Recorded 2026-11-15T14:53:48.454373+00:00. Documentation candidate **0.12.2** records the
owner's explicit selection of the existing ten-CVE tables and subsequent request:
validate the list, then cycle through its entries once the NEW implementation
works. The original catalog was implemented in
`8fb97532b32df1c7e8f3892f71c99aab2a636c92`.

The authorization establishes the demonstration goal and ordering prerequisite,
not evidence that every package or advisory applies to the clients. Validate
the actual installed baseline and synchronized fixed builds first. Keep
chronological package updates and separate per-CVE results, including the pair
sharing one RHSA. Guest recreation, baseline restoration and replacement CVEs
are not silently selected. No patch cycle has started. Existing proactive
9.4/9.5-only content policy, pending initial-registration choice, OLD boundaries
and independent shared-deployment hold remain intact.


## 2026-11-15 — Correct repository variants from actual API evidence

Recorded 2026-11-15T15:07:54.609547+00:00. Implementation
`06732373582985dbf0d08f2975d502a9fb02a006`, candidate **0.12.3**,
corrects one repository-variant builder after bounded authenticated API reads.
Both 9.4 and 9.5 were offered for the selected BaseOS/AppStream labels, all
disabled. Their URLs fix x86_64, so native substitutions must contain only
releasever. Supplying basearch also caused the certified selector to find no
match. The correction preserves all other policy, ownership and CV-binding
tasks. Actual-source syntax and affected offline builders/selectors passed.
An initial fixture-copy temporary-directory failure was corrected in the
fixture; a parent verification also corrected its own guessed task index.
Neither failure was a live repository operation or a product runtime failure.

Both original NEW clients separately passed fresh identity and unchanged full
package-baseline checks. Twenty native RPM comparisons found all ten candidate
CVEs below their first fixed EVR on both clients, including the required glibc
conversion component and setuptools. This is package screening; application
conditions and synchronized Satellite advisory availability remain unverified.
Clients remain unregistered; no package or configuration change occurred.

The exact unchanged released CoP collection completed private-Hub import and
its stored artifact digest matched upstream. It remains staged after the
existing access received HTTP 403 on approval-endpoint metadata. No promotion
was attempted; the native administrator action is pending. Preserve current
permissions rather than choose another credential or bypass the approval
pipeline. The combined EE is still unbuilt. Full-sync storage fit is unknown
because the API did not advertise content size. The independent initial
Library registration choice remains unanswered.

Candidate **0.12.4** records the actual correction commit and observed limits.
No current-main merge, content sync, client patch or full NEW acceptance is
claimed by this checkpoint.


## 2026-11-15 — Publish NEW GA-cutoff content before registration

Working candidate **0.13.0** implements the selected sequence. The owner selected a frozen
RHEL 9.4 baseline CV before direct Test/Prod registration, removing the proposed
temporary Library registration step. NEW prepare_demo remains the sole initial
publisher, with an explicit content-only mode and the approved catalog plus
2024-04-30 cutoff. Its later normal mode requires served content before selected
registered-host verification/assignment. OLD behavior is unchanged.

Date filtering and original_packages alone do not prove GA/ISO content. Actual
published metadata must exclude selected RHSAs/fixed NEVRAs and retain the
observed original affected builds before promotion. A small existing-filter
extension compares exact package identities and epochs using certified scoped
reads. It adds no runtime helper, credential, transport or service. Published
baseline contents are not rewritten; retained originals are reverified and
established later histories remain protected.

Implementation commit: `a5403bd822b8f4a23443d418259c8ee3ff0be994`.
Eleven real-playbook preparation fixtures, 21 affected metadata/epoch checks,
nine certified module interfaces, six NEW syntax checks and five OLD preparation
regressions passed. The existing full-publication path also passed its selected
default-cutoff fixture; production lint reported zero warnings or failures.
Live synchronization, publication, direct registration, dependency/DNF
applicability and complete AAP patching acceptance remain unverified.

The owner subsequently bounded demonstration content to GA through the final
selected RHSA-2024:8446 on 2024-10-24, without a 9.5 requirement. Set only NEW
sniper_update_end_date to that date and reuse the existing bounded publication
path. An explicit empty override remains latest mode; private callers must pin
the date. No pre-sync date filter, mirror helper or Library-size reduction is
claimed, and source repository/capacity selection remains separately owned.

Candidate **0.13.1** records the actual implementation and verification above.
The owner chose standard proactive RHEL 9.4 mirroring while client views remain
bounded to the selected window, and retained the existing disk capacity. Start
only safely fitting repository work, verify actual space, and gate later syncs
on sufficient capacity. No 9.5 sync, disk growth, custom mirror or complete live
acceptance is implied by this documentation checkpoint.

## 2026-11-15 — Preserve the main-only workflow

The owner reaffirmed that development/publication must use main, without feature
branches. Publishing candidate work on a temporary branch was a workflow mistake.
Reconcile the verified commits with current main, publish without force-updating
main, and remove only the temporary branch after independent main readback.
Implementation remains a5403bd822b8f4a23443d418259c8ee3ff0be994; its
verification checkpoint is f1e68ea32c902ea4294aeac3748afd6d8f9c6d5e.

Version **0.13.2** also records the baked EE 0.2.0 offline result: certified
Satellite 6.0.0 and unmodified CoP 1.5.0 packaged files match the official
archives, and selected role rendering/syntax, module arguments and current
project runtime paths passed. Registry publication, normal AAP binding and
complete NEW acceptance remain separate unfinished work.

## 2026-11-15 — Verify publication of the combined demo EE

Version **0.13.3** records completed publication of EE 0.2.0. The receiving
immutable manifest, configuration and all layers matched a fresh uncached
download, and existing authentication files were preserved. The underlying
recipe/foundation implementation is 8fb97532b32df1c7e8f3892f71c99aab2a636c92;
baseline sequencing is a5403bd822b8f4a23443d418259c8ee3ff0be994.
Normal AAP template binding, CoP server acceptance and complete patching
acceptance remain separate unfinished work. Continue directly on main.

## 2026-11-15 — Verify the adopted combined runtime and selected BaseOS content

Version **0.13.4** records successful normal CaC application of the published
combined EE and its dedicated AAP runtime check. Actual Core 2.20.10, Python
3.12.15, Satellite 6.0.0, all six stage syntaxes and authenticated strict-TLS
collection/native URI reads passed. CoP’s unchanged archive provenance remains
separate from its still-pending live configuration-role acceptance.

The selected BaseOS repository completed Immediate sync. All agreed RHSAs,
first-fixed checks and original affected builds are present. Repository
availability is not registered-host applicability or DNF dependency validation.
The foundation recipe implementation remains
8fb97532b32df1c7e8f3892f71c99aab2a636c92 and baseline sequencing remains
a5403bd822b8f4a23443d418259c8ee3ff0be994. Further content follows the current
capacity gate; direct registration and full NEW acceptance remain unfinished.


## 2026-11-15 — Record storage readiness and dated normal foundation progress

Version **0.13.5** records the evidence available at 20:17 UTC, following public
checkpoint `24f5bb31520aacb92684b4425bf156ea18d2d1d7`. The owner-approved
storage-readiness procedure completed guest filesystem growth while preserving
existing identities and unrelated VM states. Service health and authenticated
strict-TLS Satellite/Pulp API verification passed before the normal foundation
launch. Operational identities, measurements and raw receipts remain private.

The normal AAP foundation run had passed the selected CoP repository-enablement,
exact-binding and Immediate-policy guards and entered sequential certified
repository synchronization. One selected item had returned at the checkpoint;
AppStream completion, owned lifecycle/content-view readback, final cleanup and
repeated-apply acceptance were not yet verified. Date this observation instead
of presenting a transient running state as a permanent result.

Underlying implementation records remain
`8fb97532b32df1c7e8f3892f71c99aab2a636c92` for foundation/EE work and
`a5403bd822b8f4a23443d418259c8ee3ff0be994` for GA-first sequencing. This change
updates documentation and VERSION only. GA publication, direct registration,
host applicability/dependencies, complete NEW patching acceptance and the
agreed CVE cycles remain pending. No complete CoP or full-review acceptance is
claimed. Development and publication remain on existing main.
## 2026-11-15 15:14 EST — Publish the CVE/RHSA patching cycle visualization

The user explicitly requested publishing the conversation's visualization in
the public RHEL-sniperpatching repository. Update the existing docs/process.md
and README links rather than introduce a second diagram, website or rendering
dependency. The diagram follows CVE/RHSA input through a minor CV, Test patching
and verification, an operator decision and exact-version production promotion;
it then shows the later date-bounded full update and repeating advisory cycle.
Retain the independent read-only fix check and failure/recovery guidance.

The approval gates describe human decisions between existing separate AAP stage
launches. They do not claim implemented automatic approval prompts, schedules
or new live acceptance. No playbook, infrastructure or runtime behavior changes.
The code release remains 0.13.4 because this change updates documentation only.
The alternative of adding automated approval nodes or scheduling would change
execution behavior and is outside this publication request.

This initial static documentation proposal was superseded by the interactive
publication requirement below before any commit or publication.


## 2026-11-15/16 — Build and publish the first explanatory interactive mockup

The user requested a dynamic interactive visualization in this public repository
and GitHub Pages, using the Windows disconnected, AAP AutoDeploy and AIOps pages
as presentation references. The audience is security staff, Linux administrators
and AAP administrators. Architecture is central, with workflow and Content View
versions also visible. The user clarified that the page follows the code's core
architecture and responsibilities while grouping tasks and simplifying timings
for explanation. This supersedes the initial static-diagram-only proposal.

The user selected two fixed stories with no presenter-entered data: “Python
malicious package download” (setuptools, CVE-2024-6345, RHSA-2024:5534) and
“Network Privilege Escalation” (kernel, CVE-2024-36883, RHSA-2024:6567). Technical
detail identifies the latter as a local-user kernel networking flaw. Illustrative
cutoff dates leave the second advisory outstanding after the first broader update.
The presentation retains already installed fixes across both cycles.

On the subsequent instruction to create and publish the first version, adopt the
previously proposed reference pattern: browser-local HTML/CSS/JavaScript, fixed
Next/Previous/Restart navigation and explicit operator approval checkpoints before
Prod. The user did not separately choose playback preferences; these first-version
defaults were stated before implementation. The actual playbooks still use
separate manual launches; the page adds no AAP approval node or runtime scheduler.

No framework, package installation, frontend API access or live infrastructure
operation is needed. Native Ansible/Satellite content cannot render an interactive
browser explanation; small browser scripts and Node built-in checks follow the
existing reference sites. GitHub Pages Actions publishes an explicit allowlist
of four frontend files from main. Source links pin the current NEW playbooks,
separate from the mockup's own version. The code feature version is 0.15.0.
Implementation and verification references follow after the implementation commit.


### First publication and observed verification — 2026-11-16 UTC

Implementation commit: `45f2d6835446213c5c1075d17d3fed2267242937` (0.15.0).
The normal GitHub Pages workflow completed successfully at 05:01:29 UTC,
run `43807520254`; its check job took 5 seconds and publication took 15 seconds.
The site is public with HTTPS enforced. The repeatable deployed functional
command retrieved four exact matching assets and passed all six real-handler
interaction checks. Fourteen local story-model tests, JavaScript syntax checks,
HTML asset/ID checks and whitespace validation also passed. Two independent
source reviews found one fallback-link defect, corrected before the first push.
No real browser rendering, screenshot or mobile-layout check was performed;
no browser executable was available and none was installed. This is development
verification of the frontend, not formal acceptance of the automation project.

The successful deployment reported Node20 deprecations in the inherited Pages
action versions. Update only those official action versions after checking
current upstream metadata. The newer releases preserve the publication model;
no new service, tool installation or infrastructure execution is introduced.


### Publishing compatibility correction — 2026-11-16 UTC

Version 0.15.1 replaces the reference workflow's deprecated action runtimes with
official configure-pages6.0.0, upload-pages-artifact5.0.0 and deploy-pages5.0.1.
A separate read-only check inspected each exact upstream action.yml and the
artifact action's pinned upload-artifact7.0.0: executable runtimes use Node24,
existing inputs/page_url and required Pages permissions remain compatible.
Explicit hidden-file inclusion retains only the staged .nojekyll marker alongside
the four allowlisted frontend files. The first-version interaction behavior is
unchanged. The correction commit and resulting deployment are recorded below
after they exist; browser-rendering verification remains outstanding.


### Corrected Pages publication — 2026-11-16 05:04 UTC

Correction commit: `cc30e8406cbb6b9d1b410dcf559848508ecb8249` (0.15.1).
GitHub Pages run `43807803364` completed successfully at 05:04:14 UTC; check took
4 seconds and publication 13 seconds. The Node20 deprecation warning is gone.
The four deployed frontend assets again matched this checkout, and the deployed
HTML/model/handlers passed all six functional interaction checks. The content
and interaction behavior remains the reviewed first version. Real-browser visual
review remains a disclosed gap; the public page is ready for the user's review.
The first warning-bearing deployment ended at 05:01:29 UTC, so the bounded
compatibility correction through final deployment took 2 minutes 45 seconds of
wall time. Active effort versus approval/CI waiting was not measured separately.
No automation job, host or Satellite content was changed by this frontend work.


## 2026-11-16 05:51 UTC — Simplify the visualization canvas

The user requested removal of “THE PATCHING ARCHITECTURE / One tested version.
Two environments.” and friendlier, lighter-blue AAP and Satellite headers.
Version 0.15.2 removes that heading and its unused styles, retains the compact
current-phase indicator, and gives both platform headers a light blue with dark
text. This is a focused presentation correction; interaction behavior, source
mapping and automation architecture are unchanged. No new components or tools
are needed. Implementation commit: `e2e0fc80ec424503ff786af9831069b63cc5f152`.
The existing six interaction checks passed locally and against the deployed
page. GitHub Pages run `43813046943` succeeded; all four public assets matched
the checkout. Header text contrast is 9.39:1 and 5.22:1 against the new light
blue. Browser visual/mobile rendering remains unverified.


## 2026-11-16 08:20 UTC — Remove redundant AAP capability badges

The user requested removing Resolve/Patch/Verify from the AAP card. Version
0.15.3 deletes that static badge row and its unused desktop/mobile styles,
retaining the current action and existing presentation behavior. No new code
path, dependency or architecture change is needed. Implementation commit:
`70d517f58089ca1375f07b1bcc35638922fda656`. Pages run `43830568573`
completed successfully. All four deployed assets matched the checkout and all
six existing interaction checks passed locally and against the deployed page.
Browser rendering remains unverified; no new tools or tests were introduced.


## 2026-11-16 10:33 UTC — Adopt the approved seven-scene story

The user proposed seven states and explicitly accepted the reviewed adjustments
with “agree, do it”. Version 0.17.0 uses those seven main scenes for both fixed
CVE stories: green baseline, new alert, Red Hat fix content, targeted minor CV,
controlled rollout, later patch window/bulk content, and broader rollout. Scenes
5 and 7 retain visible Test proof/reboot, operator approval, exact-version Prod
promotion and final checks as substages. Forty actions support the seven-scene
navigation; no new runtime jobs or orchestration are introduced.

The previous mechanics-first list exposed future CVEs too early. Each run now
starts green, reveals only announced CVEs, retains earlier fixes and preserves
separate available/installed CV states. Red Hat content is a labelled source to
Satellite, with finite targeted-versus-bulk package animation and reduced motion.
The existing light-blue headers and earlier label removals remain unchanged.

Technical detail distinguishes already synchronized targeted content from the
full-publication repository sync and limits host applicability to the existing
explicit Test/Prod pair. The mockup does not claim per-CVE sync, dynamic fleet
discovery or an implemented AAP approval node. Plain browser APIs, the four-file
Pages artifact and existing Node tests remain sufficient; no dependency or
service is added. The authoritative full review-policy blob was rechecked as
f73e491fb6f25f57daa6903746414b2db29ce056, matching the already-read full source.
Implementation commit and deployment evidence follow after they exist.

The concurrent cold-checkpoint source reached main as 0.16.0 before this
frontend push. Preserve that work and advance this feature to 0.17.0; only
the overlapping release and handover introductions required reconciliation.


## 2026-11-16 10:40 UTC — Publish and verify the seven-scene walkthrough

Implementation `da35b9fd15ed3b7f3401a3b2d2882ba801d2481e` publishes version
0.17.0 on main, preserving concurrent checkpoint implementation 89426ac.
[Pages run 43850827769](https://github.com/kvegh/RHEL-sniperpatching/actions/runs/43850827769)
succeeded (created 10:39:33 UTC, last updated 10:40:02 UTC). The repeatable live
check downloaded all four public assets, confirmed exact checkout equality and
passed all ten actual model/UI-handler interaction checks across both cycles.
Local model checks passed all nineteen cases, and syntax/whitespace checks passed.
Independent integration review found no remaining concrete issue after the
skip-link state-reset regression was fixed. These checks do not establish
real-browser layout; no browser or browser automation package was installed.
No AAP/Satellite configuration, automation job or client state was changed by
this frontend release. Active effort and approval/CI waiting were not separately
measured.


## 2026-11-16 16:53 UTC — Compact the status and repository row

The user requested a narrower green baseline box with Red Hat software
repositories alongside it to save space. Version 0.17.1 groups the existing
status and source panels in a two-column row, shortens the baseline copy and
stacks the panels on screens up to 640px. Existing source delivery and presenter
controls remain in place. Native HTML/CSS is sufficient; no dependency or
architectural change is needed. Implementation and publication evidence follow
after verification. Browser rendering is not established by the existing Node
interaction checks.

Implementation: `2da296becc0e4e788904e77c78e4f6ff3975841f` (0.17.1).
[Pages run 43912832338](https://github.com/kvegh/RHEL-sniperpatching/actions/runs/43912832338)
succeeded. All four live assets match; all ten existing deployed HTML/script
interaction checks pass. Local interaction, syntax, markup, shared-row and
version checks also pass. Real-browser layout remains unverified; no browser
tool was available or installed. No automation or infrastructure was changed.


## 2026-11-16 17:30 UTC — Align the top panels

The user requested aligning the green status and Red Hat boxes with the top
of the workflow panel. Version 0.17.2 moves the secondary phase badge from
its separate top row into the existing footer, removes the obsolete offset
styles and top-aligns the source content. This preserves the badge and
walkthrough behavior while bringing the requested panels to the same top edge.
No new component or dependency is needed. Implementation and publication
references follow after verification; real-browser layout remains unverified.

Implementation: `8895e950f025fda8dfc0e4a1ceae964c9f4fd289` (0.17.2).
[Pages run 43919181329](https://github.com/kvegh/RHEL-sniperpatching/actions/runs/43919181329)
succeeded. All four public assets match source and all ten deployed
HTML/script interaction checks pass. Local interaction, markup and whitespace
checks passed. These checks preserve behavior but do not verify browser layout.


## 2026-11-16 18:28 UTC — Make AAP orchestration explicit

Recorded at this time after the user's successive requirements: center AAP and
Satellite in their own halves at least 40% narrower, enlarge the Red Hat source
by about 30%, and show AAP orchestrating the full sequence. Version 0.18.0 uses
separate query, repository-update, CV-composition and publication actions. The
baseline + fix equation appears during composition; Test availability changes
only at publication, while installed packages and Prod remain unchanged.

One continuous Red Hat-to-Satellite arrow says Download fix. AAP then launches
the CVE-scoped job, the client requests packages and Satellite returns selected
advisory packages/dependencies. The same sequence follows Test verification,
operator approval and exact-version promotion for Prod. Two fixed runs retain
seven scenes each and now contain 52 actions. Native HTML/CSS and existing
browser APIs suffice; no dependency, service or automation change is introduced.

These explicit triggers are explanatory subdivisions. The real targeted path
consumes synchronized content; full publication explicitly synchronizes repos.
CV composition/publication remain grouped by the checked-in implementation.
Source-linked detail preserves these boundaries. The work was split into a
scoped card-CSS stream and model stream, with root integrating labels, connected
arrows, availability state and regressions. Implementation and live publication
references follow after verification. Browser rendering remains unverified.


Implementation: `cd3d9a42770569715fba604d489a77738bb7f0bd` (0.18.0).
[Pages run 43929434866](https://github.com/kvegh/RHEL-sniperpatching/actions/runs/43929434866)
succeeded. All four public assets match source and all twelve deployed
HTML/script interaction checks pass, including both complete orchestration
sequences and client request/response exchanges. Nineteen local model checks,
syntax, markup, version and whitespace checks pass. Independent read-only
integration review found no concrete issue in the inspected CSS/markup/state
changes; it verified the matching column math, reverse request marker and motion
controls by source inspection. This is not formal project-review acceptance or
browser rendering verification. No browser tooling was installed and no AAP,
Satellite or client runtime was changed.


## 2026-11-16 19:29 UTC — Refine card balance and arrow styling

Recorded after the user requested server nodes 20% smaller, Satellite and Red
Hat another 10% larger, a long AAP-to-Satellite arrow, and more elegant technical
connectors with visible but lighter animation. Version 0.18.1 narrows centered
server cards and tightens padding, enlarges Satellite's existing width and the
Red Hat source dimensions, and preserves readable narrow-screen card widths.
The API connector spans the gap between cards with its existing action label.
All routes use thinner rounded strokes, small open heads and finer, slower
finite flow dashes. Motion-off and reduced-motion preferences remain effective;
client request/response direction and all orchestration behavior are preserved.
Native CSS and SVG are sufficient. No dependency or runtime changes are made.
Implementation and publication evidence follow after verification. Browser
layout and perceived animation quality remain unverified by the Node checks.


Implementation: `4110a83d850aa119a03103b7bec569f77b960188` (0.18.1).
[Pages run 43939993694](https://github.com/kvegh/RHEL-sniperpatching/actions/runs/43939993694)
succeeded. Four public assets match source and all twelve deployed interaction
checks pass. Local interaction, markup, version and whitespace checks passed.
Independent source review confirmed the resized-gap geometry, open arrowheads,
flow directions and motion-control coverage, finding no concrete issue in the
inspected scope. Browser appearance, text wrapping and perceived animation
quality remain unverified; no browser or dependency was installed.


## 2026-11-16 19:35 UTC — Remove the generic connector and clarify arrowheads

The user requested removing the HTTPS API text/arrow, clearer arrowheads and
another 20% larger AAP card. Version 0.18.2 hides the connector whenever no named
orchestration action applies, preserving the previously requested query,
repository-update, CV-update and publication arrows. AAP stays centered with a
refitted connector gap. Open arrowheads are larger and stronger while shafts
remain thin, addressing the user's reported visibility problem. Existing native
CSS/SVG and the same interaction checks suffice; no dependency or architecture
change is needed. Implementation and publication evidence follow verification.
Browser appearance remains unverified by the automated Node checks.


Before publication, the user also removed the separate announcement and selected
Test/Prod-pair check stops, requested a larger bold CVE ANNOUNCED alert and arrow
labels, and removed the generic inactive Red Hat content connector. These
refinements remain in 0.18.2. Announcement/risk transition now occurs at query;
publication leads directly to deployment. Actual scoped-host checks remain in
technical detail. The two stories now contain 48 actions; legacy input and
host-scope links resolve to query and Test deployment respectively. Generic
connectors are hidden, while named orchestration and real download/response
arrows remain visible at their corresponding actions.


## 2026-11-16 19:45 UTC — Add mechanical CV counters and streamline delivery

Recorded after the user's further refinements: animate every current CV change
like a mechanical counter, merge the separate package-return stop into the host
pull-and-apply action, and use Test Server/Prod Server throughout the visible
copy. All six current CV readouts retain their exact current values; a new value
descends while the previous value exits below. Only changes animate; old visual
values are hidden from assistive technology and motion preferences show the
latest value immediately. Native CSS and the existing render functions suffice.

The two stories now contain 44 actions. Earlier input, selected-pair and request
links resolve to their replacement actions. The combined feature release is
0.19.0, superseding the uncommitted/unpublished 0.18.2 draft described above;
there was no separate 0.18.2 publication. Preserve historical source snippets
and actual environment names; the server naming change affects presentation.
No automation or infrastructure change is introduced. Implementation and live
verification evidence follow after publication; actual browser animation
appearance remains unverified by Node tests.


The user then removed the kernel-installed/reboot-pending and fixed-kernel-running
intermediate stops. Required kernel reboots are included in the pull-and-apply
action; effective verification still follows. The final combined 0.19.0 story
contains 42 actions, 21 per fixed run. Removed reboot links open the corresponding
combined kernel update. This supersedes the earlier draft action counts without
changing actual automation or discarding the implementation's reboot checks.


The user also requested a plain-language explanation of CVs. Satellite's visible
controls now define a Content View (CV) version as a predefined snapshot of
selected software repositories, explaining the reusable tested snapshot without
confusing the CV definition with its published version. During final source
review, an equal-specificity mobile label rule was found to override counter
text to 8px. Strengthening the two counter typography selectors preserves the
surrounding CV font on narrow screens. This focused correction does not change
states or animation timing; browser rendering remains unverified.


Implementation: `08ef2338c35617a606d41528eceae2790cab50d4` (0.19.0).
[Pages run 43943781452](https://github.com/kvegh/RHEL-sniperpatching/actions/runs/43943781452)
succeeded. Four public assets match source and all thirteen deployed HTML/script
interaction checks pass, including every current CV field across both cycles,
motion-off behavior, full server names, direct publication-to-deployment and
combined kernel reboot/verification behavior. Nineteen model checks and local
syntax/markup/version/whitespace checks pass. The stale skip-link expectation
was updated for the removed action; the mobile counter inheritance finding was
fixed and confirmed in source review. Actual browser appearance, text wrapping
and animation perception remain unverified. No browser tooling was installed;
no AAP/Satellite/client runtime or infrastructure was changed.


## 2026-11-16 20:13 UTC — Tighten upstream spacing and reroute downloads

Recorded while implementing the user's requests to halve the upper gap, shift
Red Hat left by half the horizontal gap, route its arrow from the right side
into Satellite's top, and rename the generic host caption Satellite provides
updates. Version 0.19.1 reduces the reserved upstream minimum from 90px to45px;
content can still use the room needed for readable labels. The source moves
within the existing wide-screen grid, with a mobile reset.

A single native SVG path uses rendered source/right and destination/top bounds,
with a viewport/ResizeObserver update, to remain connected after text wrapping
and resizing. This small renderer addition replaces the fixed CSS shaft; it adds
no dependency or architectural component. A focused interaction check verifies
both endpoints, an outward elbow, resize updates and inactive visibility. An
initial test expectation used a20px elbow although the implementation used18px;
the corrected assertion checks the requested geometry rather than that incidental
waypoint. All original story/model behavior is preserved. Implementation and
publication evidence follow verification; actual browser appearance remains
unverified by the Node DOM checks.


Final source review identified a narrow-screen edge case: a full-width Red Hat
source could end at the canvas edge, so the bounded elbow would turn left into
it. A 24px mobile source gutter now preserves the requested rightward exit.
The geometry regression includes that narrow layout in addition to the desktop
and resize cases. This fixes the concrete reviewed edge case; browser rendering
remains unverified.


Implementation: `df9f8352d5e08db4f41f0ba278437052667f3527` (0.19.1).
[Pages run 43948699552](https://github.com/kvegh/RHEL-sniperpatching/actions/runs/43948699552)
succeeded. All four public assets match source and all fourteen deployed
HTML/script interaction checks pass, including desktop/narrow connector
endpoints, resize updates and inactive visibility. Source review confirmed the
24px gutter correction; local syntax, markup, version and whitespace checks
passed. Browser appearance remains unverified. No dependency, automation or
infrastructure change was made.


## 2026-11-16 20:32 UTC — Keep arrows solid and move a highlight along them

The user reported the repository-update trigger arrow was hard to see, requested
an alternative to dashed lines, and specified solid heads with half the previous
wide angle. Version 0.19.2 retains continuous visible shafts and overlays a short
cyan/purple moving highlight, with request direction reversed where appropriate.
Solid triangular SVG heads narrow from about67degrees to33degrees; the API head
uses the same acute shape. The API highlight restarts at every distinct named
query/trigger, including consecutive AAP-to-Satellite actions.

Native SVG paths reuse the base route geometry; CSS handles the finite highlight
animation. Motion-off and reduced-motion hide highlights while leaving the solid
line/head visible. The existing story, CV counters, labels, card sizes and layout
are preserved. No dependency or runtime change is introduced. Implementation and
publication references follow verification; browser appearance remains unverified.
