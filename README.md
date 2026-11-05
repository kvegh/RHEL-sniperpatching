# RHEL-sniperpatching

Version **0.5.7**. A Satellite/AAP demo: apply one selected security fix, test it, move the same content to Prod, then perform a date-bounded full update.

## Prerequisites

- Two existing RHEL hosts registered to Satellite, an explicit Test/Prod pair, and matching non-modular RPM repositories. The catalog below is for RHEL 7.
- An existing execution environment with redhat.satellite. Run check_runtime.yml after selecting it. The demonstrated runtime uses Ansible 2.15.11, Python 3.9.19 and Satellite collection 3.14.0.
- Protected Satellite credentials, verified HTTPS and Machine SSH/become access. Save the organization, repositories and exact host pair in protected inputs; see [demo variables](examples/demo-vars.yml) and [inventory](inventory/example.ini).
- Hosts already have subscription-manager, yum/dnf, native Python RPM bindings and needs-restarting. Allow a reboot when required.
- Keep the AAP job limit empty so localhost and the selected host both run. Each stage is launched separately.

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

## Demonstration RHSA and CVE catalog

These RHEL 7 security advisories are demonstration candidates, ordered by
issue date. Each RHSA links to Red Hat's public advisory with its CVE list.
Preparation discovers the current security advisory set from the explicit
host pair; repository availability and installed-package proof are checked
during the relevant stages.

| Issued | RHSA | Component | Severity | CVEs |
|---|---|---|---|---|
| 2023-11-08 | [RHSA-2023:6823](https://access.redhat.com/errata/RHSA-2023:6823) | python3 | Important | CVE-2023-40217 |
| 2023-11-13 | [RHSA-2023:6885](https://access.redhat.com/errata/RHSA-2023:6885) | python | Important | CVE-2023-40217 |
| 2023-11-21 | [RHSA-2023:7423](https://access.redhat.com/errata/RHSA-2023:7423) | kernel | Important | CVE-2022-40982, CVE-2023-31436, CVE-2023-3611, CVE-2023-3776, CVE-2023-4128, CVE-2023-4206, CVE-2023-4207, CVE-2023-4208 |
| 2023-11-27 | [RHSA-2023:7513](https://access.redhat.com/errata/RHSA-2023:7513) | linux-firmware | Moderate | CVE-2023-20569, CVE-2023-20593 |
| 2023-12-12 | [RHSA-2023:7743](https://access.redhat.com/errata/RHSA-2023:7743) | curl | Low | CVE-2022-43552 |
| 2024-01-23 | [RHSA-2024:0346](https://access.redhat.com/errata/RHSA-2024:0346) | kernel | Important | CVE-2023-42753 |
| 2024-02-08 | [RHSA-2024:0753](https://access.redhat.com/errata/RHSA-2024:0753) | linux-firmware | Moderate | CVE-2023-20592 |
| 2024-03-12 | [RHSA-2024:1249](https://access.redhat.com/errata/RHSA-2024:1249) | kernel | Important | CVE-2022-42896, CVE-2023-38409, CVE-2023-45871, CVE-2023-4921, CVE-2024-1086, CVE-2024-26602 |
| 2024-04-23 | [RHSA-2024:2002](https://access.redhat.com/errata/RHSA-2024:2002) | grub2 | Moderate | CVE-2022-2601 |
| 2024-04-23 | [RHSA-2024:2004](https://access.redhat.com/errata/RHSA-2024:2004) | kernel | Important | CVE-2020-36558, CVE-2023-2002, CVE-2023-25775, CVE-2023-4622, CVE-2023-4623 |
| 2024-06-04 | [RHSA-2024:3588](https://access.redhat.com/errata/RHSA-2024:3588) | glibc | Important | CVE-2024-2961, CVE-2024-33599, CVE-2024-33600, CVE-2024-33601, CVE-2024-33602 |
| 2024-06-06 | [RHSA-2024:3669](https://access.redhat.com/errata/RHSA-2024:3669) | less | Important | CVE-2024-32487 |
| 2024-06-10 | [RHSA-2024:3741](https://access.redhat.com/errata/RHSA-2024:3741) | bind, bind-dyndb-ldap, and dhcp | Important | CVE-2023-4408, CVE-2023-50387, CVE-2023-50868 |
| 2024-06-17 | [RHSA-2024:3939](https://access.redhat.com/errata/RHSA-2024:3939) | linux-firmware | Important | CVE-2022-27635, CVE-2022-36351, CVE-2022-38076, CVE-2022-40964, CVE-2022-46329 |

## Choose the fix and cutoff

`sniper_patch_id` accepts **one RHSA** or **up to 50 CVEs**, separated by commas, spaces or newlines. CVEs resolve dynamically through Satellite on each run; unresolved IDs fail. One CVE can select multiple RHSAs. For exactly the first advisory use RHSA-2023:6823.

With `sniper_baseline_end_date` empty, preparation selects the day before the earliest outstanding security advisory on the pair: **2023-11-07** for the catalog above. An explicit baseline date must precede all selected advisories.

Enter `sniper_update_end_date` explicitly. After RHSA-2023:6823 (November 8), use **2023-11-10**, before RHSA-2023:6885 (November 13). The cutoff includes all advisory types through that date. It is not calculated automatically. Same-day advisories cannot be separated by a calendar-date cutoff.

## Run the demo

1. Launch **Prepare** once with the protected inputs and automatic baseline.
2. Launch **Minor update** for Test with the chosen ID(s), **Patch host** with targeted scope. After success, repeat for Prod; its minor invocation reuses the Test version.
3. Launch **Publish cutoff** for Test with the date. Note the returned version.
4. Launch **Patch host** for Test with full scope and the original ID(s).
5. Launch **Promote** for Prod with that exact version, then **Patch host** with full scope.

Patch host already performs final fix and smoke checks. Use **Check** for a separate read-only confirmation when needed.

One live cycle has passed for RHSA-2023:6823 followed by the 2023-11-10 cutoff: Test and Prod completed both targeted and full stages, exact-version promotion and the final check. Both full stages correctly reported `already_current`; no additional packages were available in that interval.

Production starts only when explicitly launched. Keep the same selected fix throughout a cycle. Use the reported version rather than assuming a version number; failed publication candidates can remain retained.

## Expected result and repeat runs

Test and Prod use the same checked content. Native RPM comparison, including epoch and running-kernel checks where relevant, verifies the installed fix. Required reboots and smoke checks finish before success.

Full scope runs yum/dnf upgrade against only the selected CV repositories. It verifies the fix and refreshes metadata to require no pending updates. An unchanged RPM snapshot succeeds as **already_current**; changes report **updated**.

**Resetting a Content View does not downgrade installed RPMs.** Preparation preserves established later versions. For another visible package-change cycle, select the next still-unpatched RHSA. Repeating an already-fixed RHSA is valid and may change no packages. VM snapshot/rollback work remains on hold.

## Configuration and checks

Public playbooks and surveys stay here. Protected AAP configuration is whole-file Vault ciphertext in the private RHEL-sniperpatching-secrets companion. Deploy RHEL Sniperpatching CaC uses the shared importer and an explicit destination. Its configuration import and receiving-runtime diagnostic have passed; the selected Machine credential still needs suitable SSH access to the clients.

The observed-failure protections remain: compatible original-package filters, normal Library → Test promotion, bounded reuse of an interrupted minor, signing-key inventory handling, authoritative RPM epochs and bounded transient read retries. Host/CV ownership, consumer UUID, repository restrictions, cutoff checks and final host completion assertions remain enforced.

Use focused checks for changed behavior and a real Test/Prod run. Historical decisions remain in [design_decisions_history.md](design_decisions_history.md).
