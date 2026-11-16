# NEW content-first RHEL 9.4 baseline

This source prepares the frozen baseline before either client is
registered. The owner selected direct registration to that served content,
without temporary registration to Library. This sequence has offline fixture
coverage; live publication, registration and the complete NEW demo remain
unverified. OLD retains its existing host-derived preparation.

## Sequence and inputs

1. Complete the separately authorized foundation and proactive full repository
   synchronization. Confirm exact repository bindings and sufficient storage
   first. Filtering a CV does not reduce the source Library download footprint.
   This playbook does not enable or synchronize repositories.
2. Launch `playbooks/new/prepare_demo.yml` with the protected Satellite inputs,
   explicit repository/product mappings, namespace and exact intended host names.
   Set the Boolean `sniper_prepare_content_only: true`. The baseline cutoff is
   explicitly `sniper_baseline_end_date: "2024-04-30"`; another value is refused.
3. Require successful publication, actual-content verification and promotion of
   the same original version to both owned Test and Prod environments. This
   invocation makes no host or host-errata API requests, assigns no hosts,
   creates no activation keys, and performs no registration or RPM update.
4. Launch `playbooks/new/register_demo_clients.yml` with the same protected
   scope, approved public CA and original two-client inventory metadata. It
   verifies already-serving GA content and registers directly to dedicated
   Test/Prod activation keys. Registration does not publish content. Keep the
   job limit empty so localhost and both original clients can run.
5. Launch the same preparation playbook with `sniper_prepare_content_only: false`
   (the default). It requires an already-serving content path, reads the exact
   registered pair, rechecks the original baseline when it is the only version,
   and verifies/assigns only that pair. It cannot publish a missing baseline.
6. Complete the normal NEW runtime and client acceptance checks before beginning
   the agreed chronological CVE demonstrations. Publishing or assigning content
   does not install it.

The content-only phase retains the normal input validation of both intended
host names. Those configured names do not require existing Satellite host rows.
The shared `surveys/preparation.json` and empty cutoff in `examples/demo-vars.yml`
describe OLD. Keep that automatic/empty cutoff survey off the NEW setup template
or supply the explicit GA value; an empty override is intentionally refused.

Existing SATELLITE_* credentials, strict HTTPS validation and forced job-local
CA cleanup are unchanged. No new authentication or transport is introduced.

## Selected demonstration window

The selected client-content interval is RHEL 9.4 GA (`2024-04-30`) through
RHSA-2024:8446 (`2024-10-24`), the final selected advisory. No RHEL 9.5 content
is required for this demonstration. NEW defaults `sniper_update_end_date` to
`2024-10-24`, using the existing bounded full-publication path and its actual
advisory-date verification. Earlier per-cycle cutoff dates remain explicit
presenter inputs where needed for the chronological demonstrations.

The private caller must pin the selected date and avoid an empty survey override.
An explicitly empty cutoff still selects the existing unbounded/latest route,
which removes both owned inclusion filters and can expose later content. Shared
OLD survey/default behavior is unchanged. The client-content cutoff does not
limit Library synchronization or establish its storage requirement. Pre-sync
date-bounded downloads are not implemented; source repository/capacity choices
remain separate owner decisions before any synchronization.

## What the baseline proves

The checked-in [ten-CVE catalog](rhel94-cve-candidates.json) supplies the selected
RHSAs and observed original affected-package NEVRAs. Preparation resolves the
RHSAs and their issue dates in the actual CV repositories, with no `host_errata`
bootstrap dependency. The GA cutoff must precede every selected RHSA. Patching
still resolves requested CVEs dynamically through the existing live workflow;
this catalog is the approved baseline acceptance set, not a replacement CVE
resolver.

The existing original-packages and issue-date filters remain separate. Before
consumer promotion, certified `resource_info` reads the published version's
actual errata and latest affected packages, using `packages_restrict_latest`
after a name-only search scoped to that exact CV version. Do not filter the
query by an original filename/version: that could hide a newer build before
latest selection. Native latest selection compares EVR within each name/arch
group ([upstream controller](https://github.com/Katello/katello/blob/master/app/controllers/katello/api/v2/packages_controller.rb),
[RPM latest selection](https://github.com/Katello/katello/blob/master/app/models/katello/rpm.rb)).
An original GA identity must therefore be the latest offered build for its
architecture. All advisory dates must fall within the
cutoff, every selected RHSA and first-fixed NEVRA must be absent, and all six
original affected builds must be available. Package metadata needs an explicit
usable epoch; missing or conflicting identities fail closed. The live 6.19 API
schema confirms `packages.index` supports `content_view_version_id`. Its actual
package response shape remains an acceptance check after synchronization.

`original_packages` means packages without errata; it does **not** mean GA
packages. Date filters plus these selected-package checks do not prove exact
full-ISO equivalence, dependency installability or advisory applicability on a
registered client. The report therefore records `exact_iso_equivalence:
unverified`. In particular, other packages without errata and modular content
are not covered by the six affected-package identities. See Red Hat's
[content-view filter semantics](https://docs.redhat.com/en/documentation/red_hat_satellite/6.19/html/managing_content/managing-content-views-and-content-view-environments).

## Retry and refusal behavior

A new version is published in Library first and inspected before promotion.
Interrupted initial publication can reuse only the one identifiable original
version with the recorded GA cutoff. Published versions and their filters are
never rewritten. Missing original builds, selected fixed RPMs without an
erratum, selected RHSAs, later advisory dates, any later affected build, ambiguous package epochs or
conflicting history stop before promotion/host assignment. An invalid retained
candidate requires investigation or an explicitly selected new namespace;
preparation does not delete or repair its contents.

A content-only retry rechecks the original version and promotes only empty
destinations. It refuses established multi-version history. The normal
registered-host invocation preserves established later serving versions and
cannot reset installed RPMs. Neither invocation patches a client.

## Offline verification

The existing `tests/test_preparation.py` fixture runs the real playbook against
synthetic local Satellite modules. NEW coverage includes absent/unregistered
host rows, content publication before any host API access, a subsequent direct
registered-host phase without publication, cutoff and RHSA/fixed-RPM
contamination refusal (including later-than-first-fixed RPMs), missing originals, retained-version recovery and
established-history preservation. The existing pure validation filter also
checks explicit/ambiguous RPM epochs. These tests perform no live API calls and
do not replace final AAP end-to-end acceptance.

## Direct registration implementation

The NEW registration stage uses certified `redhat.satellite.activation_key`
with modern `content_view_environments`, and `registration_command` for native
Global Registration. CoP 1.5.0’s activation-key dispatcher forwards legacy fields;
using the certified 6.0.0 module directly avoids changing the shared collection
or selecting a downgrade. Exact returned CV/environment labels, project
ownership, the two selected repository labels and release 9.4 bind the keys.
The sole original GA version must already serve both destinations.

The protected inventory supplies each original client’s existing address,
`sniper_ssh_host_key`, `sniper_expected_product_uuid` and
`sniper_expected_machine_id`. The existing non-root Machine credential and sudo
are reused. Strict host-key pinning precedes facts and any guest connection.
The approved public Satellite CA is supplied through native guest trust,
preserving a conflicting pre-existing anchor rather than replacing it. This
follows [Red Hat’s secure Global Registration procedure](https://docs.redhat.com/en/documentation/red_hat_satellite/6.19/html-single/managing_hosts/index).

The certified registration module returns a native pipeline rather than
executing it on the guest. One protected `ansible.builtin.shell` task executes
that exact command, as documented by the module; no custom registration script,
download service or deprecated consumer RPM is added. API and initial curl
certificate verification remain enabled. The short-lived registration command
and token are never printed. Package updating, Insights, remote execution and
container-certificate setup are explicitly disabled. Existing native template
parameters must also leave optional host packages/tools disabled; explicit
command switches alone do not prove that operator templates add nothing.

`subscription-manager identity` joins the actual guest consumer to its exact
Satellite row and served CV/environment. An existing matching consumer is
verified without forced registration; a conflicting or stale registration
stops. Native full `rpm -qa` snapshots before and after, including failed
attempts, enforce preservation of the installed baseline. Final per-client
assertions prevent an excluded or skipped host from producing a successful
job. Execution-local public CA and host-key files are removed. These commands
use existing RHEL tools and require no added runtime package.

Focused synthetic local-Ansible fixtures verify registration control flow and
refusals. They cannot establish actual client connectivity, native registration
or DNF dependency resolution. Run the normal AAP GA, registration, registered
preparation and Test-to-Prod procedure against the original pair for acceptance.
Do not treat a source check or CaC import as completion of that procedure.

### Repository copies during registration

A published version has archived, Library and promoted repository copies.
Registration reads repositories with both `content_view_version_id` and the
selected `environment_id` through the certified resource-info module, then
requires the exact two protected repositories, products and RHSM labels. A
version-only query can return eight copies for this two-repository setup; it
must not be deduplicated to hide an ambiguous serving destination.

### Native calendar cutoff input

AAP/YAML can supply a real calendar date even when its stored survey value is
ISO text. The date validator accepts that calendar type and `YYYY-MM-DD` text,
normalizing the former with `isoformat()` before the same format/calendar and
advisory-retention checks. Datetime timestamps, arbitrary objects and invalid
dates remain rejected. This normalization does not change the selected date,
the explicit empty/latest mode or the published-content cutoff boundary.
