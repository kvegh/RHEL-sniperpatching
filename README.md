# RHEL-sniperpatching

**Demo project version: 0.7.2.**

See [current handover status](current_status_for_handover.md) for recorded
validation, review status and continuation boundaries.

[Quick guide](TLDR.md) · [Process diagram](docs/process.md) ·
[Inputs and recovery](docs/operations.md) · [Implementation rationale](docs/implementation.md) ·
[Review evidence](docs/review-2026-11-12.md)

## OLD and NEW tracks

Both tracks remain available in this public repository:

| Directory | Purpose | Verification |
|---|---|---|
| `playbooks/old/` | Remote demo Satellite and its own remote AAP, with the tested runtime helpers. | Three Test-to-Prod cycles passed before this path-only reorganization. |
| `playbooks/new/` | Our local Satellite and up-to-date production AAP; includes separate NEW setup stages. | Copied from the same reviewed logic; new-environment installation and end-to-end acceptance remain pending. |

Each directory contains all seven demo entry points, tasks, variables, filter plugins,
native RPM/runtime helpers, synthetic inventory and collection declarations.
Surveys remain shared generic input definitions under `surveys/`. AAP Job
Templates must save the full path for their selected track. OLD always runs
through the remote environment's own AAP. NEW runs through our production AAP.
The current private CaC describes NEW setup only; the historical OLD capture is
preserved separately and must never be imported into the NEW controller.

NEW adds `configure_satellite_dns.yml` and `prepare_satellite_host.yml`. Their
[documented sequence](docs/new-satellite.md) includes strict SSH identity, exact
VM ownership, RHEL update/reboot/kernel proof, matching FQDN/DNS and swap.
Satellite package installation/configuration and the new demo EE remain pending.

There are no root-level forwarding playbooks. Update a template's playbook path
and synchronize the matching source revision together. The private companion
keeps populated environment inputs and CaC encrypted; no live import, patching
or Satellite installation is performed by this repository reorganization.

For the new Satellite build, follow [the installation sequence](docs/new-satellite.md):
finalize the FQDN and forward/reverse DNS, update RHEL and reboot as required,
verify prerequisites, and only then install Satellite.

## What this project does

RHEL-sniperpatching is a working demonstration of targeted security patching for
Red Hat Enterprise Linux (RHEL), using Red Hat Satellite and Ansible Automation
Platform (AAP). It shows how an operator can select one security advisory, test
its fix on a Test host, deploy the same tested content to a Prod host, and later
bring both hosts up to a broader, date-bounded repository update.

The repository provides the Ansible playbooks and AAP survey definitions for
that sequence. Satellite controls which packages are available; AAP runs the
host updates, handles required reboots, and verifies the installed result.
Each stage is launched explicitly by the person leading the demonstration.
Test and Prod are the two stages of this dedicated demo environment.

## Why deploy a single security fix?

An urgent vulnerability can need attention while a wider operating-system update
is still being tested or waiting for a maintenance window. For example, a team
may need to fix a TLS vulnerability in Python while keeping unrelated package
changes for its next regular patch cycle. A focused update gives the team a
smaller change to review, test and explain before applying it to the next stage.

Here, **sniper**, **one-off** and **single-patch** deployment mean selecting a
specific Red Hat Security Advisory (**RHSA**). An advisory can update several RPM
packages and require dependencies, so a focused deployment can change more than
one package. A **CVE** identifies a vulnerability; the same CVE can map to several
RHSAs. The playbooks resolve CVE input dynamically through Satellite. Use an
explicit RHSA when the demonstration must select exactly one advisory.

Targeted patching fits between broader maintenance updates. This demo therefore
shows both parts: first the selected security fix, then all updates available
through a chosen cutoff date. Choosing a cutoff between consecutive demo
advisories leaves the following fix available for another demonstration cycle.

A Satellite **Content View (CV)** is the versioned set of repository content made
available to hosts. The demo adds the selected advisory to a minor CV version,
then promotes that same version through Test and Prod. A later major CV version
contains the broader cutoff content. Publishing or promoting a CV changes
available content; the separate host-patching job installs and verifies it.

## Environment this was built and demonstrated in

The end-to-end demo was built and exercised in an existing Satellite/AAP workshop
environment. Its recorded functional runs used the following setup:

| Part | Demonstrated setup |
|---|---|
| Managed hosts | Two RHEL 7.9 clients registered to Satellite, one assigned to Test and one to Prod. |
| Content management | Red Hat Satellite, with a dedicated Content View and Library → Test → Prod lifecycle path. |
| Repository content | Selected non-modular RHEL 7 base/extras RPM repositories, with historical 2023–2024 advisories for the staged demo. |
| Automation | Existing AAP workshop controller and its execution environment; separate Job Templates for content changes, host patching and verification. |
| Execution runtime | Ansible Core 2.15.11, Python 3.9.19 and the redhat.satellite collection 3.14.0. |
| Host access | Satellite API credentials plus Machine SSH/become access to the selected pair; connection details stay in protected inputs. |

The historical advisory catalog is the content available for this demonstration.
It is not a current list of all RHEL vulnerabilities or a claim that other RHEL
versions have been tested. The live results below were recorded on **2026-11-05**:
two complete targeted/full-update cycles passed on both hosts.

The AAP configuration-as-code (**CaC**) deployment was also verified on a separate
AAP 2.7 receiving instance, including its imported read-only runtime diagnostic.
The host-patching runs were performed through the original workshop controller;
SSH access from the receiving instance still needs verification before using it
for the host demo. Public playbooks live here, while populated environment
settings and credentials remain in the private Vault-encrypted companion.

## Prerequisites

- Two existing RHEL hosts registered to Satellite, an explicit Test/Prod pair, and matching non-modular RPM repositories. The catalog below is for RHEL 7.
- A compatible EE for the selected track. OLD was exercised with Core 2.15.11; NEW targets Core 2.20. Both starting trees pin redhat.satellite 3.14.0. Run the selected track's full `check_runtime.yml` path before its demonstration.
- Protected Satellite credentials, verified HTTPS and Machine SSH/become access. Save the organization, repositories and exact host pair in protected inputs; see [demo variables](examples/demo-vars.yml) and [inventory](playbooks/old/inventory/example.ini).
- Hosts already have subscription-manager, yum/dnf, native Python RPM bindings and needs-restarting. Allow a reboot when required.
- Keep the AAP job limit empty so localhost and the selected host both run. Each stage is launched separately.

The shared project deliberately has no root `collections/requirements.yml`.
AAP gives project-installed collections precedence over EE content, even when
the project's collection is older. A shared Satellite pin would therefore
silently replace the selected track's EE version. Keep exact collection
requirements in each track's `dependencies/satellite.yml` and build its own EE;
bind each demo job template explicitly to that EE's immutable image.
See [Red Hat's collection precedence documentation](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.7/develop-ref_projects_collections_support).

OLD retains its verified Core 2.15.11/Satellite collection 3.14.0 baseline.
NEW must resolve and qualify the current certified release from Red Hat
Automation Hub, then pin that exact version in its Core 2.20 EE. Its inherited
manifest is pending that update; do not treat it as current-release acceptance.
The two NEW DNS/RHEL preparation templates use built-in modules and the existing
Core 2.20 management EE. They do not require a Satellite collection to bootstrap
the server. The historical OLD runs remain separate from NEW acceptance.

All 98 offline tests passed inside the official unmodified Core 2.20.10 EE.
These checks do not establish fresh Satellite access or live patching acceptance.

## How to demonstrate the functionality

Launch each stage manually in AAP. Wait for its successful result before starting
another stage. Keep the same selected RHSA throughout the cycle. The names below
are the existing Job Template names; numeric template IDs vary between AAPs.

### Before the audience arrives

Use the prepared demo controller, its dedicated Content View and its explicit
Test/Prod host pair. Confirm Machine SSH/become access and the runtime prerequisite
check have passed. A successful CaC import alone does not prove host access.
Leave the job Limit empty and keep the saved protected connection settings.
Have AAP Jobs and the Satellite Content View/host pages open in separate tabs.

For a **fresh, unpatched pair**, first launch **RHEL-sniperpatching - Prepare demo**
with **Baseline issue-date cutoff (optional)** empty. Verify the dedicated
Library → Test → Prod path, baseline and host assignments. Start with the earliest
outstanding RHSA and choose a later cutoff before the following RHSA. Preparation
is setup, not an RPM rollback; do not rerun it to reset an already-patched pair.

At the **last verified run**, two cycles had passed and both demo environments
served **CV 4.0**. The next planned example is **RHSA-2023:7423** (kernel, issued
2023-11-21), followed by cutoff **2023-11-24**, halfway to RHSA-2023:7513
(2023-11-27). Confirm that advisory is still outstanding before presenting.
This third cycle has not been run; the two verified examples are listed below.

Allow roughly **35–45 minutes** plus presenter pauses for a complete cycle;
a kernel reboot may take longer. In the second verified run, Test minor creation took about nine minutes, Prod minor reuse five,
and cutoff publication eight; host updates took about two to three minutes each.
Satellite operations are asynchronous. Use the wait to explain what is changing;
do not launch the same stage again while its job is running.

### Presenter sequence

In the steps below, enter your chosen RHSA in **CVE ID(s) or one RHSA** wherever
that field appears. For the next planned example, enter **RHSA-2023:7423** and
use **2023-11-24** as the cutoff. Use the actual returned CV versions, even if
they differ from the expected next minor/major. Explicitly choose **prod** on
every Prod launch: the Test default does not remember the preceding job.

1. **Show the starting state in Satellite.** Open the dedicated CV and both demo
   hosts. Show that Test and Prod use the same starting version and the selected
   security advisory is outstanding. Say: “We will expose one security advisory,
   patch Test, and then move the same tested content to Prod.”

2. **Create the RHSA-only content for Test.** Launch
   **RHEL-sniperpatching - Create minor update** with **Lifecycle stage: test**
   and the chosen RHSA. In the successful output, show the resolved advisory,
   selected version and `already_available` result. Note the version as **MINOR**
   (normally 4.1 when starting from 4.0). In Satellite, show Test on MINOR and
   Prod still on the starting version. Say: “The old content is preserved and
   only the selected advisory is added. Publishing content has not patched a host.”

3. **Apply the selected fix to Test.** Launch **RHEL-sniperpatching - Patch hosts**
   with **Lifecycle stage: test**, the same RHSA and **Patch scope: targeted**.
   Show `sniper_result`: the requested ID, environment, MINOR version,
   `changed_packages` and `proof.verified: true`. Wait through any required reboot
   and smoke checks. For a kernel advisory, show the running-kernel verification.
   Say: “The installed system has been checked, not just the repository metadata.”

4. **Move the same minor content to Prod.** Launch
   **RHEL-sniperpatching - Create minor update** with **Lifecycle stage: prod**
   and the same RHSA. Show that its reported version is the exact **MINOR**
   tested in step 3. Say: “We reuse the tested minor; we do not build another
   version for Prod.” Do this before publishing the full cutoff version.

5. **Apply the selected fix to Prod.** Launch **RHEL-sniperpatching - Patch hosts**
   with **Lifecycle stage: prod**, the same RHSA and **Patch scope: targeted**.
   Show the package changes, successful native proof and completed reboot/smoke
   checks. Both hosts now have the selected fix using the same MINOR content.

6. **Publish the full repository content through the cutoff.** Launch
   **RHEL-sniperpatching - Publish full update**. Enter the chosen date in
   **Repository cutoff (YYYY-MM-DD)**; use **2023-11-24** for the planned kernel
   example. Show the successful report's `test_version` and `cutoff`; note that
   version as **FULL** (normally 5.0 after 4.1). In Satellite, show Test on FULL
   while Prod remains on MINOR. Say: “Now Test can receive all repository updates
   through this date, including non-security updates. The following RHSA is beyond
   the cutoff.” The cutoff is entered explicitly, not calculated by the job.

7. **Apply the full update to Test.** Launch **RHEL-sniperpatching - Patch hosts**
   with **Lifecycle stage: test**, the original RHSA and **Patch scope: full**.
   Show FULL, `changed_packages`, `update_result`, `proof.verified: true` and
   `full_repository_verified: true`. Explain that `updated` means packages changed;
   `already_current` means the update actually ran and verified no pending updates.

8. **Promote the exact fully tested version.** Launch
   **RHEL-sniperpatching - Promote Content View** with **Destination stage: prod**
   and **Exact tested Content View version: FULL**, copied from step 6. Show that
   Prod now serves that same version. Say: “Promotion follows the successful Test
   update; it does not update Prod's installed packages by itself.”

9. **Apply the full update to Prod.** Launch **RHEL-sniperpatching - Patch hosts**
   with **Lifecycle stage: prod**, the original RHSA and **Patch scope: full**.
   Show FULL, the actual package changes, successful proof and
   `full_repository_verified: true`. Both hosts have now completed the targeted
   and full stages using the same tested content versions.

10. **Close with an independent read-only result.** Launch
    **RHEL-sniperpatching - Check patch** with **Lifecycle stage: prod** and the
    same RHSA. Show `proof.verified: true` and FULL. In Satellite, show Test and
    Prod on the same FULL version. Summarize: “One selected security fix first;
    then all updates through a date between that advisory and the next.”

If a stage fails, stop there and inspect its failed task before proceeding.
Do not advance Prod or blindly repeat a publication: an interrupted job may have
retained a candidate, so always read the actual returned version after recovery.

### Optional read-only CVE input demonstration

After the two verified Python cycles, launch **RHEL-sniperpatching - Check patch**
with **Lifecycle stage: prod** and **CVE ID(s) or one RHSA: CVE-2023-40217**.
Show `sniper_result.advisory_map` and `proof.verified: true`: Satellite resolves
that CVE dynamically to both RHSA-2023:6823 and RHSA-2023:6885, whose fixes are
already installed. This check does not publish content or patch a host.

The field also accepts up to 50 CVEs separated by commas, spaces or newlines.
For a separately planned multi-CVE run, show the resolved mapping for every
entered ID; a CVE may select multiple RHSAs. The live mapping comes from
Satellite, not a static file or this README. Keep using an explicit RHSA for the
strictly one-advisory sequence above, so CVE expansion does not consume future
demo fixes unexpectedly.

### What has already been demonstrated

| Selected RHSA | Full cutoff | Targeted result on both hosts | Full-update result on both hosts |
|---|---|---|---|
| RHSA-2023:6823 | 2023-11-10 | python3 and python3-libs fixed, CV 1.1 | CV 3.0, verified already_current |
| RHSA-2023:6885 | 2023-11-17 | python and python-libs upgraded, CV 3.1 | CV 4.0, microcode_ctl upgraded |

Both cycles passed exact-version promotion and final verification. The first
full version was 3.0 because a failed earlier publication candidate remained
retained; version numbers must come from job output. Replaying these advisories
on the current pair may change no packages. Continue with the next outstanding
advisory for a visible upgrade; an identical replay requires an independently
reset host state, and snapshot/rollback automation remains on hold.

## Expected result and repeat runs

Test and Prod use the same checked content. Native RPM comparison, including epoch and running-kernel checks where relevant, verifies the installed fix. Required reboots and smoke checks finish before success.

Full scope runs yum/dnf upgrade against only the selected CV repositories. It verifies the fix and refreshes metadata to require no pending updates. An unchanged RPM snapshot succeeds as **already_current**; changes report **updated**.

**Resetting a Content View does not downgrade installed RPMs.** Preparation preserves established later versions. For another visible package-change cycle, select the next still-unpatched RHSA. Repeating an already-fixed RHSA is valid and may change no packages. VM snapshot/rollback work remains on hold.

## Six stages

| Stage | Playbook | Purpose |
|---|---|---|
| Prepare | prepare_demo.yml | Creates the dedicated CV and Library → Test → Prod path, verifies the baseline and assigns only the chosen pair. |
| Minor update | create_minor_update.yml | Creates the selected fix in Test; the Prod invocation reuses the exact tested minor. |
| Patch host | patch_hosts.yml | Updates one host with targeted or full scope, reboots if needed and verifies its installed fix. |
| Publish cutoff | publish_full_update.yml | Publishes repository content through the selected date and promotes the checked major version to Test. |
| Promote | promote_content_view.yml | Promotes the explicitly supplied Test version to Prod. |
| Check | check_patch.yml | Independently checks identity, fix, kernel, reboot and smoke-test results without changing the host. |

Generic AAP surveys are in [surveys](surveys/). Content jobs need Satellite access; patch/check jobs also need Machine access. Only the dedicated CV, lifecycle path and selected pair belong to this demo.

## Choose the fix and cutoff

`sniper_patch_id` accepts **one RHSA** or **up to 50 CVEs**, separated by commas, spaces or newlines. CVEs resolve dynamically through Satellite on each run; unresolved IDs fail. One CVE can select multiple RHSAs. For exactly the first advisory use RHSA-2023:6823.

With `sniper_baseline_end_date` empty, preparation selects the day before the earliest outstanding security advisory on the pair: **2023-11-07** for the catalog above. An explicit baseline date must precede all selected advisories.

Enter `sniper_update_end_date` explicitly. After RHSA-2023:6823 (November 8), use **2023-11-10**, before RHSA-2023:6885 (November 13). The cutoff includes all advisory types through that date. It is not calculated automatically. Same-day advisories cannot be separated by a calendar-date cutoff.

## Demonstration RHSA and CVE catalog

These RHEL 7 security advisories are demonstration candidates, ordered by
issue date. Each RHSA links to Red Hat's public advisory with its CVE list.
Preparation discovers the current security advisory set from the explicit
host pair; repository availability and installed-package proof are checked
during the relevant stages.

Dates are **RHSA issue dates**, not individual CVE disclosure dates. A cutoff
means all configured repository content through that date; it is not another
advisory date. Only the first two cutoffs have been executed. Later dates below
are **proposed presenter inputs**, not saved defaults or completed runs.

Issue labels summarize Red Hat's linked advisories; multi-CVE rows can contain
several different flaws. Full CVE lists and demonstration notes are expandable
below. **Cutoff** is the full-update date **after this RHSA and before the next**:
**✓ verified**, **\* proposed**. The **Demo** column rates the ease of showing an
installed-package fix; expand the notes for reboot, service and hardware caveats.
DoS means denial of service.

| Issued | RHSA | Component — issue | Cutoff | Demo |
|---|---|---|---|---|
| 2023-11-08 | [2023:6823](https://access.redhat.com/errata/RHSA-2023:6823) | python3 — TLS handshake bypass | **2023-11-10** ✓ | Easy ✓ |
| 2023-11-13 | [2023:6885](https://access.redhat.com/errata/RHSA-2023:6885) | python — TLS handshake bypass | **2023-11-17** ✓ | Easy ✓ |
| 2023-11-21 | [2023:7423](https://access.redhat.com/errata/RHSA-2023:7423) | kernel — Network flaws / CPU leaks | **2023-11-24** * | Moderate |
| 2023-11-27 | [2023:7513](https://access.redhat.com/errata/RHSA-2023:7513) | linux-firmware — AMD data leaks | **2023-12-04** * | Limited |
| 2023-12-12 | [2023:7743](https://access.redhat.com/errata/RHSA-2023:7743) | curl — Proxy use-after-free | **2024-01-02** * | Easy |
| 2024-01-23 | [2024:0346](https://access.redhat.com/errata/RHSA-2024:0346) | kernel — Netfilter out-of-bounds access | **2024-01-31** * | Moderate |
| 2024-02-08 | [2024:0753](https://access.redhat.com/errata/RHSA-2024:0753) | linux-firmware — SEV-ES memory-integrity loss | **2024-02-24** * | Limited |
| 2024-03-12 | [2024:1249](https://access.redhat.com/errata/RHSA-2024:1249) | kernel — Memory corruption / DoS | **2024-04-02** * | Moderate |
| 2024-04-23 | [2024:2002](https://access.redhat.com/errata/RHSA-2024:2002) | grub2 — Font buffer overflow | Shared below | Limited |
| 2024-04-23 | [2024:2004](https://access.redhat.com/errata/RHSA-2024:2004) | kernel — Memory / access-control flaws | **2024-05-14** * | Moderate |
| 2024-06-04 | [2024:3588](https://access.redhat.com/errata/RHSA-2024:3588) | glibc — iconv / netgroup memory flaws | **2024-06-05** * | Easy |
| 2024-06-06 | [2024:3669](https://access.redhat.com/errata/RHSA-2024:3669) | less — Shell command injection | **2024-06-08** * | Easy |
| 2024-06-10 | [2024:3741](https://access.redhat.com/errata/RHSA-2024:3741) | BIND / DHCP — DNS CPU exhaustion | **2024-06-13** * | Moderate |
| 2024-06-17 | [2024:3939](https://access.redhat.com/errata/RHSA-2024:3939) | linux-firmware — Wi-Fi access / validation flaws | Not defined | Limited |

<details>
<summary>Full CVE lists and demonstration notes (14 advisories)</summary>

| RHSA | Component | CVEs | Demonstration notes |
|---|---|---|---|
| [2023:6823](https://access.redhat.com/errata/RHSA-2023:6823) | python3 | CVE-2023-40217 | Easy — verified RPM proof for python3/python3-libs; already fixed on the current pair. |
| [2023:6885](https://access.redhat.com/errata/RHSA-2023:6885) | python | CVE-2023-40217 | Easy — verified python/python-libs upgrade; already fixed on the current pair. |
| [2023:7423](https://access.redhat.com/errata/RHSA-2023:7423) | kernel | CVE-2022-40982, CVE-2023-31436, CVE-2023-3611, CVE-2023-3776, CVE-2023-4128, CVE-2023-4206, CVE-2023-4207, CVE-2023-4208 | Moderate — installed and running-kernel proof, with reboot when required; untested next cycle. |
| [2023:7513](https://access.redhat.com/errata/RHSA-2023:7513) | linux-firmware | CVE-2023-20569, CVE-2023-20593 | Limited security effect in a VM — package proof is straightforward; firmware mitigation needs relevant hardware. Untested. |
| [2023:7743](https://access.redhat.com/errata/RHSA-2023:7743) | curl | CVE-2022-43552 | Easy package/version proof for curl; vulnerability reproduction is not prepared. Untested. |
| [2024:0346](https://access.redhat.com/errata/RHSA-2024:0346) | kernel | CVE-2023-42753 | Moderate — installed and running-kernel proof, with reboot when required. Untested. |
| [2024:0753](https://access.redhat.com/errata/RHSA-2024:0753) | linux-firmware | CVE-2023-20592 | Limited security effect in a VM — package proof is straightforward; firmware mitigation needs relevant hardware. Untested. |
| [2024:1249](https://access.redhat.com/errata/RHSA-2024:1249) | kernel | CVE-2022-42896, CVE-2023-38409, CVE-2023-45871, CVE-2023-4921, CVE-2024-1086, CVE-2024-26602 | Moderate — installed and running-kernel proof, with reboot when required. Untested. |
| [2024:2002](https://access.redhat.com/errata/RHSA-2024:2002) | grub2 | CVE-2022-2601 | Limited security effect — GRUB package proof; boot-security demonstration needs the applicable boot/firmware setup. Untested. |
| [2024:2004](https://access.redhat.com/errata/RHSA-2024:2004) | kernel | CVE-2020-36558, CVE-2023-2002, CVE-2023-25775, CVE-2023-4622, CVE-2023-4623 | Moderate — installed and running-kernel proof; shares its issue date with the GRUB advisory. Untested. |
| [2024:3588](https://access.redhat.com/errata/RHSA-2024:3588) | glibc | CVE-2024-2961, CVE-2024-33599, CVE-2024-33600, CVE-2024-33601, CVE-2024-33602 | Easy package/version proof for glibc; allow required service restart/reboot handling. Untested. |
| [2024:3669](https://access.redhat.com/errata/RHSA-2024:3669) | less | CVE-2024-32487 | Easy package/version proof for the less command; vulnerability reproduction is not prepared. Untested. |
| [2024:3741](https://access.redhat.com/errata/RHSA-2024:3741) | bind, bind-dyndb-ldap, and dhcp | CVE-2023-4408, CVE-2023-50387, CVE-2023-50868 | Moderate — proof covers installed bind/DHCP components; a functional service demonstration needs those services configured. Untested. |
| [2024:3939](https://access.redhat.com/errata/RHSA-2024:3939) | linux-firmware | CVE-2022-27635, CVE-2022-36351, CVE-2022-38076, CVE-2022-40964, CVE-2022-46329 | Limited security effect in a VM — firmware package proof, with hardware-dependent mitigation. Untested. |

</details>

The proposed cutoff is the midpoint before the next catalog advisory, rounded to
the earlier day when necessary. Enter it manually in the Publish full update
survey. The two April 23 advisories cannot have separate date-bounded full cycles:
a full cutoff after April 23 can include both. To show both targeted fixes
separately, finish both targeted Test/Prod sequences before their shared full
update, or choose a different demo advisory. May 14 is the midpoint after that
same-day group. No midpoint is defined after the final entry until a following
advisory is selected from the live catalog.

“Easy” rates an observable **installed-package fix**, not a working exploit or
proof of hardware mitigation. The two Python rows are live-verified; ratings for
the other rows are estimates based on their components and the existing proof
checks. Kernel rows need running-kernel verification; firmware and boot security
effects may not be visible in this VM environment. Satellite remains the dynamic
source for actual CVE mappings, affected installed packages and available content.

## Configuration and checks

Public playbooks and surveys stay here. Protected AAP configuration is whole-file Vault ciphertext in the private RHEL-sniperpatching-secrets companion. Deploy RHEL Sniperpatching CaC uses the shared importer and an explicit destination. Its configuration import and receiving-runtime diagnostic have passed; the selected Machine credential still needs suitable SSH access to the clients.

The observed-failure protections remain: compatible original-package filters, normal Library → Test promotion, bounded reuse of an interrupted minor, signing-key inventory handling, authoritative RPM epochs and bounded transient read retries. Host/CV ownership, consumer UUID, repository restrictions, cutoff checks and final host completion assertions remain enforced.

Use focused checks for changed behavior and a real Test/Prod run. Historical decisions remain in [design_decisions_history.md](design_decisions_history.md).


## Naming and validation

Project variables and public filters use the `sniper_` prefix and descriptive
`snake_case`. Existing playbooks use `action_noun.yml`; task names use imperative
verbs. Shared task files represent reusable components of the independently
launched stages. The owner-selected repository name and published input/playbook
names are retained; cosmetic renaming would break callers without a practical
benefit. [Input precedence, check mode and repeat behavior](docs/operations.md)
are explicit project interfaces.

Use the existing local Python/Ansible tooling for focused regressions and
`ansible-lint --profile production --strict`; all entry-point syntax and module
interfaces must also pass in the selected EE. Offline fixture results on a
newer local runtime supplement, rather than replace, the actual AAP baseline.
The current review/fix batch is **not accepted yet**: mandatory APME coverage and
the final corrected-source AAP end-to-end re-test remain pending. See the
[dated evidence](docs/review-2026-11-12.md) for exact results and limitations.


### Reproduce local validation

Use an existing Python with Ansible and PyYAML, the selected Satellite 3.14.0
collection on its search path, and matching Ansible CLI programs on `PATH`.
Do not install or upgrade content as part of a normal demonstration job.

```sh
SNIPER_TRACK=old python3 -B -m unittest discover -s tests -v
SNIPER_TRACK=new python3 -B -m unittest discover -s tests -v
ansible-lint --profile production --strict playbooks/old playbooks/new
python3 playbooks/old/files/runtime_probe.py playbooks/old
python3 playbooks/new/files/runtime_probe.py playbooks/new
ansible-playbook --syntax-check playbooks/old/check_runtime.yml
ansible-playbook --syntax-check playbooks/new/check_runtime.yml
```

The runtime probe checks all six demonstration entry points and their Satellite
module arguments without executing the stages. The local unit/boundary fixtures
use synthetic data and temporary files; they do not contact or patch clients.
Record the actual interpreter/core/collection versions alongside results.

### Repeatable functional test of a deployed client

Use the existing **RHEL-sniperpatching - Check patch** Job Template
(`playbooks/old/check_patch.yml`). Select `test` or `prod` and the same already-applied RHSA/CVE
input; retain the protected inventory, credential and exact authorized pair.
Keep Limit empty and require existing SSH/become, native RPM/reboot tools and
Satellite read access. The job checks current CV/consumer binding, every requested
fix using native RPM/kernel proof, no pending reboot and configured smoke tests.
Expected result: a successful AAP job with `sniper_result.proof.verified: true`.
An assertion failure is a failed functional test. Defaults prove SSH service
health; add application smoke services/URLs for application-level coverage.

This check is safe to repeat on the owned pair: it creates no test resources,
installs nothing and requires no cleanup. Run it after patching and as the final
independent presenter check. It supplements the complete Test/Prod publication,
patching, reboot and full-update acceptance sequence; it does not replace it.
The corrected revision has not yet passed that AAP acceptance sequence.
