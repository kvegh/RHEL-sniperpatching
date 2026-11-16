# Scoped CoP configuration qualification

This is a scoped qualification record, not complete NEW demo acceptance. It retains
certified Satellite collection **6.0.0**, CoP Satellite Configuration **1.5.0**,
and official AAP Core **2.20.10**. The combined EE is now adopted and its normal
AAP runtime check passed. The first scoped foundation apply and a repeated
apply with exact configuration and client preservation have passed; complete NEW
patching and full formal review remain separate.

## Why qualification is scoped

CoP declares Satellite 5.8.0. That metadata pin does not establish that every
call fails with 6.0.0. Keep the upstream package unchanged and qualify only the
repository, lifecycle, content-view and activation-key paths the project uses.
This does not claim compliance with the declared dependency combination or
qualification of all CoP features.

The CoP source revision is `4e504141d91c492f70ff59f9d38ae7d770ff75ec`.
The official immutable 1.5.0 release artifact has SHA-256
`aafc8d7c5021b1f07764b1f27b0944c0592c209507e0b3dc0e1c494a5d662901`;
all 264 declared packaged files matched the reviewed source. The certified
Satellite archive has SHA-256
`67847d52685e27f3220b1e641f8294f221e341bfddca439172c4e9b88407fb2d`.
Consume released artifacts through the existing private Automation Hub path;
do not vendor them here, repackage them or fetch Git source during a job.

## Completed offline checks

Checks ran on 15 November 2026 in the pinned official Core 2.20.10 image,
with networking disabled, a read-only container root and private temporary
fixtures. They did not contact or change Satellite.

| Check | Observed outcome |
|---|---|
| Four native Ansible syntax checks | Lifecycle role, content-view role, its explicitly loaded dynamic tasks and selected CoP dispatch tasks passed. |
| Four native templating groups | Lifecycle ordering/credentials, separate filters/rules, exact repository variants and activation-key bindings passed. |
| Ten actual module-constructor calls | Rendered arguments were accepted before an enforced API-entry barrier. |
| Legacy-filter negative check | The filter module rejected rule-only fields as expected. |
| Source resolution | The inspected modules resolved to exact certified 6.0.0 content. |

The module checks cover repository-set enablement, product creation, selected
repository sync, explicit CV publication, activation keys, lifecycle environments,
content views, and filter/rule calls. Passing an interface check does not imply
that the foundation stage uses every tested operation.

Early helper runs failed because of a moved Ansible helper, native input
serialization and untrusted synthetic template expressions. Only the test
scaffolding changed; those attempts are not evidence of CoP incompatibility.
The corrected module run completed at 14:10:49 UTC and the final independent
native-templating run at 14:11:09 UTC. Successful syntax checks were retained
from 14:08:52–14:08:59 UTC rather than rerun without a reason.

## Foundation boundary

The candidate `playbooks/new/configure_satellite_content.yml` targets the exact
RHEL 9 x86_64 BaseOS/AppStream repository variants, the existing organization,
and the owned project lifecycle path and content view. It reuses the job-local
CA and existing protected credential inputs with certificate validation enabled.
No additional connection, credential or importer is introduced.

The owner selected proactive full synchronization using the `immediate`
download policy. On-demand downloads are excluded. Limit source repository
variants explicitly to RHEL 9.4 and, only if selected, 9.5; do not select the
rolling `9` stream or a later minor. The first compatibility fixtures used a
synthetic release `9` input to check module interfaces; that is not the selected
live repository scope. Current source guard checks cover the narrowed minor list.

Verify that the subscribed CDN exposes each exact selected variant and assess
fresh target capacity before synchronization. Do not assume that two complete
minor-release repository pairs fit the provisioned demo disk. No synchronization
has run as part of this source preparation.

The existing `prepare_demo.yml` owns the first filtered baseline publication.
Publishing an unfiltered version into Test/Prod first can bypass its initial
baseline path. Therefore the foundation must leave a newly created content view
unpublished. The owner subsequently selected [content-first GA preparation](new-baseline.md):
prepare_demo verifies and serves the original baseline before direct client
registration to Test/Prod, then verifies/assigns the registered pair. The foundation
still creates no activation keys and performs no registration.

CoP's separate top-level filter dispatcher can forward legacy rule fields to the
filter module. The native 6.0 content-view role already separates filter and rule
calls; the existing NEW demo playbooks do so too. Avoid that incompatible legacy
path. Automatic version cleanup, full dispatch, export/reconciliation, identity
management, provisioning and Convert2RHEL are outside this foundation scope.

## Live read-only repository preflight

Authenticated strict-TLS API reads on 15 November 2026 confirmed both explicit
minor variants, 9.4 and 9.5, for the two fixed-x86_64 repository labels. All four
were offered and disabled at that initial read. The API did not advertise
full-content size; storage fit was unverified at this early API-only preflight.
Later storage readiness and synchronization results are recorded below.

The actual content URLs already contain literal x86_64. Their native repository
substitutions contain only `releasever`. The original draft also supplied
`basearch`, which the certified selector would reject because it compares the
complete substitutions dictionary. The correction removes that extra key while
preserving the fixed architecture labels and every minor/ownership/binding guard.

Final-source syntax passed on Core 2.20.10. The actual source builders for 9.4
and 9.4 plus 9.5, followed by four native-selector comparisons against captured
API-shaped rows, passed offline. The old extra-key shape matched no variants;
the corrected shape selected exactly the requested minors. An initial fixture
copy failed because its remote temporary directory was read-only; using the
container-local temporary directory corrected only that fixture. No live
repository enablement or sync occurred.

The unchanged released CoP archive completed its normal private-Hub import.
After the owner approved publication, the supported native move task completed;
published inventory contained this version and staging no longer did. A complete
receiving-Hub download matched the original 190727-byte SHA-256 above. Earlier
HTTP 403 on OPTIONS metadata did not establish that the actual publication
operation was denied. Existing authentication and permissions were unchanged.
The combined EE 0.2.0 is built and offline-qualified. All packaged collection
files match the two original archives, with no overlays or added dependencies.
Publication is verified by fresh immutable manifest/configuration/blob readback.
Normal AAP binding is verified through the existing CaC importer and fresh
immutable-image readback. The normal runtime template passed with actual
Core 2.20.10, Python 3.12.15 and certified Satellite 6.0.0, six stage syntaxes,
module interfaces and both authenticated strict-TLS API paths. These checks
do not execute the CoP configuration roles or establish complete NEW acceptance.

The selected BaseOS repository subsequently completed proactive Immediate sync.
Its actual content includes all nine selected RHSAs, all ten first-fixed checks
and the original affected builds. This is repository availability; client-side
applicability and dependency installability still require registered-host checks.
The later storage-readiness result and normal foundation progress are recorded
in the dated checkpoint below; they do not establish completed remaining syncs.

## Dated live foundation checkpoint

At **2026-11-15 20:17 UTC**, the approved storage-readiness work had completed.
Guest filesystem growth, preservation of identities and unrelated VM states,
service health and authenticated strict-TLS Satellite/Pulp API checks passed.
This cleared the readiness gate for the selected normal foundation launch.
It does not replace capacity checks for subsequent work.

A normal AAP run of `playbooks/new/configure_satellite_content.yml` from source
checkpoint `24f5bb3` had passed selected CoP repository enablement, exact member
bindings and Immediate-policy guards, then entered sequential certified
repository synchronization. One selected repository item had returned.
AppStream completion, the owned lifecycle path/content-view result, final CA
cleanup and repeated-apply acceptance were not yet verified. This records the
observed stage at that time; later execution results and full CoP acceptance
require separate verification.

The implementation records remain `8fb9753` for foundation/EE work and
`a5403bd` for GA-before-registration sequencing. The first GA baseline still
belongs to preparation; this foundation run does not establish publication,
activation keys, registration or client patching.

## Completed live foundation and repeated apply

The first normal foundation run completed both full proactive regular RHEL 9.4
mirrors and verified the owned lifecycle path and exact content-view bindings.
GA publication, direct registration and the first paired targeted fix then passed
through their separate AAP stages.

At **2026-11-16 00:15 UTC**, one normal foundation repeat from source `22b21e5`
had succeeded in **38.116 seconds**. Both selected native repository syncs
completed successfully. Pre/post checks verified unchanged material CV history,
serving 1.1, filters/rules/timestamps/IDs, activation keys, consumer mappings and
repository bindings, Immediate policies and counts. Both complete 443-RPM client
arrays, identities, consumers, running kernels and twenty package-witness rows
were unchanged; temporary trust was removed.

The native recap was 37 ok / 4 changed / 0 failed / 0 unreachable / 1 skipped.
Changes were
allocation/copy/cleanup of the execution-local public CA and one repository-sync
loop with two changed items. This proves desired-state preservation with expected
sync/local-file actions, not zero reported changes. Only the two human-relative
age display fields in nested filter responses were excluded from material
comparison; raw pre/post snapshots and exact exclusions remain encrypted.

## Remaining acceptance

The bounded evidence above qualifies the foundation paths actually used with
the unchanged CoP 1.5.0 archive and certified Satellite 6.0.0. It does not establish
compatibility with every CoP feature or compliance with its declared 5.8.0
metadata dependency. Live foreign-resource failure/recovery scenarios were not
exercised; that coverage gap remains separate from the verified first and
repeated application to the owned demo resources.

Complete the NEW Test/Prod full-update workflow and chronological CVE cycles
through AAP. The native calendar-date cutoff correction has passed targeted and
actual-data offline checks; its live full-publication acceptance remains pending.
Full formal review is separate and remains unfinished.
