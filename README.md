# RHEL-sniperpatching

Version **0.5.1**. Independently launched Ansible stages for demonstrating a
CVE-list or single-RHSA update followed by a cutoff or latest repository update, using Red Hat
Satellite and AAP. This project is a submodule of
[AAP Advanced Features](https://github.com/kvegh/AAP-advanced-features).

## Playbooks

| Entry point | Result |
|---|---|
| `check_runtime.yml` | Read-only diagnostic of the selected existing EE: reports installed Ansible/Python/Satellite collection versions, parses all six stages, checks their Satellite module arguments, and queries Satellite organizations with verified HTTPS. No dependency installation or host contact. |
| `prepare_demo.yml` | Creates a dedicated Content View and `Library -> RHEL-sniperpatching_Test -> RHEL-sniperpatching_Prod` path, publishes the initial baseline to both stages, then moves only the explicitly supplied test/prod host pair. No host patching. |
| `create_minor_update.yml` | Resolves one RHSA or multiple CVEs dynamically in the selected repositories. In Test, creates a real incremental minor from the serving baseline, validates the content delta, and promotes it to Test. In Prod, validates and promotes the exact Test minor. No host patching. |
| `patch_hosts.yml` | Patches only the selected host, checks whether reboot is necessary, reboots and reconnects as needed, proves the fix from installed RPM versions and the running kernel, then runs smoke tests. Supports targeted and full update scopes. |
| `publish_full_update.yml` | Synchronizes selected Library repositories, publishes through an optional issue-date cutoff (or latest), verifies actual advisory content in Library, then promotes the exact checked major version to Test. No host patching. |
| `promote_content_view.yml` | Promotes an explicitly supplied version currently serving Test to Prod through the normal path. No host patching. |
| `check_patch.yml` | Read-only host identity, installed-fix, running-kernel, pending-reboot and smoke checks. It never installs packages or reboots. |

Generic AAP surveys are available under [surveys/](surveys/): preparation,
patch selection, host patching, cutoff publication, exact-version production
promotion and read-only fix verification. The seven dedicated runtime/demo
templates have been configured and read back on the selected Controller with
the existing EE and credentials; no demo stage has been launched yet.

Save sniper_environment=test on the cutoff publication template, whose survey
asks only for the date. Patch/check templates prompt explicitly for Test or Prod.
Keep organization, exact host pair and preparation repository/product names in
protected saved inputs. Patch and check need both Satellite and Machine
credentials; local-only content operations need Satellite access. Limit and
arbitrary variable prompting remain disabled.

Each invocation is a separate AAP launch. Production never starts automatically.
The full-update promotion is a manual demonstration gate: run the Test host
patch and its checks successfully before launching production promotion.

## Inputs and access

The generic example is [inventory/example.ini](inventory/example.ini); INI keeps
AAP from listing an inventory example as a runnable playbook.

Use an inventory containing the two existing Satellite host names, their SSH
connection values and appropriate privilege escalation. Keep the AAP job limit empty: the bootstrap and final proof plays require
`localhost` as well as the selected client. A limit excluding all controller
plays can make Ansible skip the whole run; later Job Templates should leave
limit prompting disabled. The host-patching stage
checks the system's actual subscription-manager consumer UUID against Satellite
before modifying packages. Only the selected existing inventory host is used.

Supply `SATELLITE_SERVER_URL`, `SATELLITE_USERNAME`, `SATELLITE_PASSWORD` and
`SATELLITE_ORGANIZATION` through protected job inputs/environment. Variables
`sniper_server_url`, `sniper_username`, `sniper_password` and
`sniper_organization` can also be supplied through protected Ansible inputs.
HTTPS certificate verification is always enabled; redirects are refused for
explicit API requests. Satellite access alone does not provide host SSH access.

Copy [examples/demo-vars.yml](examples/demo-vars.yml) to a location **outside the
repository** and replace the synthetic organization, repository/product names
and host pair. Keep passwords out of that file and out of command arguments.
The selected test and prod hosts are mandatory, distinct and never inferred.
The optional namespace must begin with `RHEL-sniperpatching`; it determines the
separate Content View and Test/Prod environment names.

Preparation refuses same-name resources without this project's exact ownership
description. It does not edit another Content View, filter, lifecycle path,
activation key, organization or global setting. Existing published project
baselines and newer serving versions are preserved on retries. If initial
publication succeeded but promotion was interrupted, a retry can promote the
single recognizable initial baseline into only the empty destinations. It
refuses ambiguous histories rather than guessing. Existing credentials and
activation keys are not changed by host reassignment.

### Choosing the initial baseline

Preparation reads outstanding errata for the explicit Test/Prod host pair,
collects their complete security RHSA set and resolves those advisories in the
selected repositories. With an empty `sniper_baseline_end_date`, it chooses the
day before the earliest issue date. An explicit cutoff must be earlier than
every selected RHSA. Missing advisories or invalid/ambiguous dates stop
preparation before publication.

The inclusion filter retains security, bugfix and enhancement errata through
that date, plus original RPMs without errata. The baseline is published in
Library first. Prep reads its actual advisory content and requires all selected
RHSAs to be absent before promoting the same baseline to Test and Prod and
reassigning the host pair. This leaves every selected fix available for a later,
separate minor-update launch.

A retry preserves established serving versions. If publication succeeded but a
promotion was interrupted, prep validates the recorded cutoff and actual content
again before promoting that single initial version into empty destinations.
It never rebuilds a published baseline or resets a later demonstration version.
Historical availability still depends on the selected repositories; a date
filter cannot recreate packages removed upstream. The check concerns published
content; it does not downgrade installed RPMs.

Use RHEL content matching the hosts' installed OS. This implementation does not
perform OS conversion, major-version upgrades, application installation or
module-stream switching. Modular-only advisory metadata is refused explicitly;
the initial demonstration targets non-modular RHEL RPM advisories.

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

### Choosing a CVE or an RHSA

`sniper_patch_id` accepts one RHSA or up to 50 CVEs, separated by commas, spaces
or newlines. For example:

```yaml
sniper_patch_id: "CVE-2024-32487, CVE-2023-40217"
```

In this catalog, `CVE-2024-32487` maps to `RHSA-2024:3669` for `less`. The playbook
resolves CVEs through Satellite, restricted to the selected Content View's
repositories. A CVE can select several RHSAs: `CVE-2023-40217` maps to
both `RHSA-2023:6823` (`python3`) and `RHSA-2023:6885` (`python`).
Every submitted CVE is queried separately against live Satellite metadata on
each launch. Complete advisory details must confirm every CVE/RHSA association.
Any unresolved CVE fails the run; overlapping advisories are deduplicated before
the minor update. Installed-fix verification reports each requested CVE
separately and requires affected installed components for every CVE. This
documentation table is a reference and is never used for runtime resolution.
To select exactly one advisory, supply its RHSA ID.

Use [surveys/patch-selection.json](surveys/patch-selection.json) for the
minor-update JT survey. Its required textarea accepts the same comma, space or
newline separators, and the lifecycle selector chooses Test or Prod. No CVE
choices or CVE-to-RHSA mappings are stored in the survey.

The earliest candidate above is `RHSA-2023:6823`, issued on 2023-11-08.
For this complete set, automatic preparation therefore chooses a cutoff of
2023-11-07. The date is calculated from discovered issue dates rather than
hardcoded into the playbook.

## Demonstration sequence

In AAP, select the relevant playbook and supply the stage inputs below. The
minor-update JT uses the patch-selection survey above. Reproducible CaC for the
full set of stage Job Templates remains separate work.
Equivalent CLI launches are shown for clarity. `demo.yml` and the inventory
below are private operator files outside the repository.

```bash
# 1. New isolated path/view and explicit host assignments.
ansible-playbook -i /path/to/inventory.yml prepare_demo.yml -e @/path/to/demo.yml

# 2. Add the selected fix to the Test content baseline.
ansible-playbook -i /path/to/inventory.yml create_minor_update.yml -e @/path/to/demo.yml -e sniper_environment=test -e sniper_patch_id=RHSA-2024:1234

# 3. Patch Test, reboot if needed, and prove the fix.
ansible-playbook -i /path/to/inventory.yml patch_hosts.yml -e @/path/to/demo.yml -e sniper_environment=test -e sniper_patch_id=RHSA-2024:1234

# 4. Promote the same validated minor to Prod, then patch Prod separately.
ansible-playbook -i /path/to/inventory.yml create_minor_update.yml -e @/path/to/demo.yml -e sniper_environment=prod -e sniper_patch_id=RHSA-2024:1234
ansible-playbook -i /path/to/inventory.yml patch_hosts.yml -e @/path/to/demo.yml -e sniper_environment=prod -e sniper_patch_id=RHSA-2024:1234

# 5. Publish all current selected repository content to Test.
ansible-playbook -i /path/to/inventory.yml publish_full_update.yml -e @/path/to/demo.yml -e sniper_environment=test

# 6. Upgrade Test fully, proving the original fix and another installed package upgrade.
ansible-playbook -i /path/to/inventory.yml patch_hosts.yml -e @/path/to/demo.yml -e sniper_environment=test -e sniper_patch_scope=full -e sniper_patch_id=RHSA-2024:1234 -e sniper_upgrade_witness=example-tools

# 7. After Test succeeds, promote its exact reported version and upgrade Prod.
ansible-playbook -i /path/to/inventory.yml promote_content_view.yml -e @/path/to/demo.yml -e sniper_environment=prod -e sniper_version=2.0
ansible-playbook -i /path/to/inventory.yml patch_hosts.yml -e @/path/to/demo.yml -e sniper_environment=prod -e sniper_patch_scope=full -e sniper_patch_id=RHSA-2024:1234 -e sniper_upgrade_witness=example-tools

# Read-only verification, independently at either stage.
ansible-playbook -i /path/to/inventory.yml check_patch.yml -e @/path/to/demo.yml -e sniper_environment=test -e sniper_patch_id=RHSA-2024:1234
```

The advisory and package names above are synthetic examples. Replace them with
a fix relevant to the chosen repositories/installed software and an independent
installed package with an actual available upgrade. `sniper_patch_id` accepts
one RHSA or a list of CVEs. Every CVE resolves dynamically to security advisories
in the selected repository set; proof requires affected installed components
for each requested CVE.
A single RHSA with no affected installed package fails instead of reporting
success. An already-fixed affected package is valid evidence, including a newer
superseding RPM version. Merely seeing no applicable update is never evidence.

The full-update witness must already be installed and have a strictly higher
RPM EVR afterwards, using native RPM comparison. It must be independent of the
requested fix. Additions, removals, downgrades and a no-op full rerun do not count
as proof of that separate upgrade. Both hosts need a suitable witness package;
the witness can be chosen independently for each launch.

## Content and host verification

The certified `redhat.satellite` collection handles discovery, lifecycle paths,
Content Views, host reassignment, synchronization, publication, promotion and
waiting for asynchronous tasks. Its version module does not expose true
incremental updates. Only that operation uses `ansible.builtin.uri` against
`POST /katello/api/content_view_versions/incremental_update`.

Incremental creation is submitted once, with host patching and automatic
promotion omitted. The playbook waits for Satellite task success, identifies
one new minor from the exact baseline, checks that all baseline RPMs and errata
remain, and rejects advisory additions outside the requested resolved set.
Satellite resolves required package dependencies; the new version stays in
Library if content validation fails. Production reuses the exact Test minor and
validates its delta against the production baseline. If Test and Prod have
diverged in unrelated content, promotion is refused; no lifecycle force option
is used. Inspect Satellite before retrying a timed-out POST, because the server
may have accepted it even if the response was lost.

Full publication synchronizes the explicitly selected **shared Library
repositories**. This does not alter any colleague's frozen Content View version,
but newer Library content becomes available to their future publications.
No other project's filters are removed. A later full publication creates a new
major version, so repeat launches deliberately create new snapshots.

For repeated single-RHSA demonstrations, set `sniper_update_end_date` to a
day strictly between the selected RHSA's issue date and the next RHSA's issue
date. For example, after RHSA-2023:6823 (2023-11-08), use 2023-11-10 before
RHSA-2023:6885 (2023-11-13). This includes all advisory types through the cutoff
and preserves the next security fix for its own incremental launch. The
[cutoff publication survey](surveys/full-update.json) requires that date.
Two RHSAs issued on the same day have no intervening calendar day; do not
pretend that a date filter separates them.

A nonempty date retains and advances this project's filter. An empty value
retains the separate publish-latest behavior and removes that filter. Dates
that would exclude a currently serving advisory are refused before
synchronization or filter changes. The new version is first published in
Library; the playbook reads its actual errata, requires preservation of the
serving advisory set, and, for a cutoff, rejects any missing/invalid issue
date or advisory issued later. Only that exact verified version is promoted
to Test. A verification failure leaves Test unchanged.

A cutoff publication does not prove that an independent installed package has
a newer version available in that interval. The full host-patch stage still
requires its strictly higher-EVR witness; an interval without one must be
reported instead of claiming a separate upgrade succeeded.

Package commands enable only the Content View's exact RHSM repository labels.
Targeted mode uses `yum`/`dnf upgrade-minimal --advisory`; full mode uses `upgrade`.
Read-only RPM proof uses the operating system's Python RPM bindings and native
`rpm.labelCompare`, including architecture and epoch. Satellite advisory package
filenames can omit the epoch. The resolver queries their exact filenames only
in the selected repositories and uses the structured package epoch; an explicit
null epoch means zero. Missing, ambiguous or conflicting epochs fail verification
instead of assuming zero. The host proof also rejects requirements without an
epoch. Old install-only kernels
can remain installed, but a kernel fix must be present in the **running kernel**.

Reboot decisions combine `needs-restarting -r`, stale running processes,
advisory reboot hints, changed core packages, and installed-versus-running kernel
proof. A required reboot must finish, fix proof must pass again, and no reboot
may remain pending before success. The default smoke test checks `sshd`; add
application service names to `sniper_smoke_services` and HTTPS/HTTP endpoint
checks to `sniper_smoke_urls` (each `{url, status}`). Without these additions,
there is no claim of application-level functional coverage.

## Execution requirements and validation

Run `check_runtime.yml` with the existing Satellite credential and candidate EE
before preparation. It needs no demonstration host pair, organization selection,
patch ID or SSH credential. It reports missing required modules and individual
stage syntax errors and unsupported Satellite module arguments before requiring
a successful read-only collection query.
It never executes the six demonstration stages. An installed collection version
and successful read access establish runtime evidence; a successful diagnostic
does not prove live publication, host reassignment or package changes.

- Reuse a compatible existing execution environment. A live read-only AAP
  diagnostic passed with `ansible-core` **2.15.11**, Python **3.9.19** and the
  already installed `redhat.satellite` **3.14.0** on 2026-11-04. All nine required
  modules were present, all six demo stages parsed, and the collection read
  Satellite organizations with certificate verification enabled. No EE rebuild
  or dependency installation was needed. The manifest now declares 3.14.0 to
  match that verified runtime. For RHEL 7 targets, retain an Ansible version
  supporting their Python. This is a deliberate trial of the existing runtime;
  collection 3.14.0 was released in September 2023. Publication and host patching
  have not yet been run, and read access alone does not establish vendor support.
  The older filter module uses `filter_state`, which these playbooks now supply;
  the diagnostic also checks argument names against the installed module docs.
- Target hosts need working subscription-manager, yum/dnf, native Python RPM
  bindings, SSH/become access and the existing `needs-restarting` utility
  (`yum-utils` or the platform's equivalent). Missing prerequisites fail before
  package changes; the playbooks do not install diagnostic dependencies.
- The explicit collection manifest is
  [dependencies/satellite.yml](dependencies/satellite.yml). AAP automatically
  processes root `requirements.yml` as well as role/collection requirement paths;
  this project keeps its declaration in an explicit location so SCM refresh
  does not install dependencies. The tested existing EE already provides the
  declared collection. On another instance, run the diagnostic before deciding
  whether additional content is needed; installing certified content requires
  an appropriately configured source. A successful SCM refresh alone does not
  prove runtime dependencies are present.
- Keep real inventories, credentials and job output outside this public repo.
  AAP CaC belongs in the private `RHEL-sniperpatching-secrets` companion as
  whole-file Ansible Vault ciphertext at
  `vaults/cac/RHEL-sniperpatching-cac-vault.yml`, using the `cac` identity.
  Generic survey definitions stay here; repository read tokens and Vault
  password sources remain outside Git. Capturing configuration does not run
  application jobs or establish restore/deployment success.
  No license has been selected for this project.

Local validation uses the available tools and a checkout of the official 3.14.0
collection source; it does not install dependencies or execute remote jobs:

```bash
python3.12 -B -m unittest discover -s tests -v
ansible-playbook --syntax-check check_runtime.yml
ansible-playbook --syntax-check prepare_demo.yml
ansible-playbook --syntax-check create_minor_update.yml
ansible-playbook --syntax-check patch_hosts.yml
ansible-playbook --syntax-check publish_full_update.yml
ansible-playbook --syntax-check promote_content_view.yml
ansible-playbook --syntax-check check_patch.yml
```

The runtime diagnostic has also passed in AAP as described above. A live
end-to-end demonstration, actual patch installation, reboots and later AAP CaC
deployment are separate
validation steps. Implementation decisions and commit references are recorded
in [design_decisions_history.md](design_decisions_history.md).
