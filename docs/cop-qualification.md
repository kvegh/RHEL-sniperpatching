# Scoped CoP configuration qualification

This is a development candidate, not complete NEW demo acceptance. It retains
certified Satellite collection **6.0.0**, CoP Satellite Configuration **1.5.0**,
and official AAP Core **2.20.10**. The running NEW environment remains unchanged.

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
unpublished. Initial client registration and baseline ordering remain a recorded
setup choice; no activation-key/registration phase has been selected by this draft.

CoP's separate top-level filter dispatcher can forward legacy rule fields to the
filter module. The native 6.0 content-view role already separates filter and rule
calls; the existing NEW demo playbooks do so too. Avoid that incompatible legacy
path. Automatic version cleanup, full dispatch, export/reconciliation, identity
management, provisioning and Convert2RHEL are outside this foundation scope.

## Live read-only repository preflight

Authenticated strict-TLS API reads on 15 November 2026 confirmed both explicit
minor variants, 9.4 and 9.5, for the two fixed-x86_64 repository labels. All four
were offered and disabled. The API did not advertise full-content size, so
storage fit remains unverified before proactive synchronization.

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

The unchanged released CoP archive also completed its normal private-Hub
import and matched the original SHA-256. It remains in staging. The existing
access received HTTP 403 on approval-endpoint metadata; no promotion was
attempted, and the administrator action is pending. The combined EE remains
unbuilt and cannot yet be described as published or live-accepted.

## Remaining acceptance

The CoP-inclusive EE recipe is prepared but unbuilt and unpublished. Qualify the
actual combined image and its selected normal AAP template before claiming
server compatibility. Verify ownership refusal, exact repository bindings,
actual task completion, CA cleanup, repeated apply/idempotency and preservation
of unrelated objects. Then verify registered client baselines and the complete
patching workflow through AAP. No live behavior, sync, promotion, host assignment
or complete review is established by the offline checks above.
