# RHEL-sniperpatching

Version **0.1.2**. Independently launched Ansible stages for demonstrating a
single CVE/RHSA update followed by a full repository update, using Red Hat
Satellite and AAP. This project is a submodule of
[AAP Advanced Features](https://github.com/kvegh/AAP-advanced-features).

## Playbooks

| Entry point | Result |
|---|---|
| `prepare_demo.yml` | Creates a dedicated Content View and `Library -> RHEL-sniperpatching_Test -> RHEL-sniperpatching_Prod` path, publishes the initial baseline to both stages, then moves only the explicitly supplied test/prod host pair. No host patching. |
| `create_minor_update.yml` | Resolves one CVE/RHSA in the selected repositories. In Test, creates a real incremental minor from the serving baseline, validates the content delta, and promotes it to Test. In Prod, validates and promotes the exact Test minor. No host patching. |
| `patch_hosts.yml` | Patches only the selected host, checks whether reboot is necessary, reboots and reconnects as needed, proves the fix from installed RPM versions and the running kernel, then runs smoke tests. Supports targeted and full update scopes. |
| `publish_full_update.yml` | Synchronizes the selected Library repositories, removes only this project's initial cutoff filter, publishes full current content and promotes it to Test. No host patching. |
| `promote_content_view.yml` | Promotes an explicitly supplied version currently serving Test to Prod through the normal path. No host patching. |
| `check_patch.yml` | Read-only host identity, installed-fix, running-kernel, pending-reboot and smoke checks. It never installs packages or reboots. |

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

Choose `sniper_baseline_end_date` before the demonstration advisory's issue date.
Preparation uses an inclusion filter for security, bugfix and enhancement errata
through that date, retaining RPMs without errata. This filter belongs only to the
new Content View. Omit the date to snapshot all currently synchronized content;
then an advisory already present in that baseline needs no minor update and is
reported as already available. Historical package availability depends on the
selected Library repositories; a date filter cannot recreate packages already
removed upstream. Set the baseline inputs before the first publication: reruns
do not rebuild or roll back an established baseline.

Use RHEL content matching the hosts' installed OS. This implementation does not
perform OS conversion, major-version upgrades, application installation or
module-stream switching. Modular-only advisory metadata is refused explicitly;
the initial demonstration targets non-modular RHEL RPM advisories.

## Demonstration sequence

In AAP, select the relevant playbook and supply the stage inputs below. Later CaC
will provision these Job Templates; this implementation supplies their source.
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
one RHSA or CVE. A CVE resolves to security advisories in the selected repository
set; proof covers affected installed components and requires at least one.
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

Package commands enable only the Content View's exact RHSM repository labels.
Targeted mode uses `yum`/`dnf upgrade-minimal --advisory`; full mode uses `upgrade`.
Read-only RPM proof uses the operating system's Python RPM bindings and native
`rpm.labelCompare`, including architecture and epoch. Old install-only kernels
can remain installed, but a kernel fix must be present in the **running kernel**.

Reboot decisions combine `needs-restarting -r`, stale running processes,
advisory reboot hints, changed core packages, and installed-versus-running kernel
proof. A required reboot must finish, fix proof must pass again, and no reboot
may remain pending before success. The default smoke test checks `sshd`; add
application service names to `sniper_smoke_services` and HTTPS/HTTP endpoint
checks to `sniper_smoke_urls` (each `{url, status}`). Without these additions,
there is no claim of application-level functional coverage.

## Execution requirements and validation

- Use an execution environment with `ansible-core` 2.16 and the declared
  `redhat.satellite` 6.0.0 collection plus its existing Python requirements.
  For RHEL 7 targets, retain an Ansible version supporting their Python.
- Target hosts need working subscription-manager, yum/dnf, native Python RPM
  bindings, SSH/become access and the existing `needs-restarting` utility
  (`yum-utils` or the platform's equivalent). Missing prerequisites fail before
  package changes; the playbooks do not install diagnostic dependencies.
- The explicit collection manifest is
  [dependencies/satellite.yml](dependencies/satellite.yml). AAP automatically
  processes root `requirements.yml` as well as role/collection requirement paths;
  this project keeps its declaration in an explicit location so SCM refresh
  does not install dependencies. Supply the declared collection in the execution
  environment before running jobs. Its installation requires an appropriately
  configured certified content source; a successful SCM refresh alone does not
  prove runtime dependencies are present.
- Keep real inventories, credentials and job output outside this public repo.
  No license has been selected for this project.

Local validation uses the available tools and an existing checkout of the
official collection; it does not install dependencies or execute remote jobs:

```bash
python3.12 -B -m unittest discover -s tests -v
ansible-playbook --syntax-check prepare_demo.yml
ansible-playbook --syntax-check create_minor_update.yml
ansible-playbook --syntax-check patch_hosts.yml
ansible-playbook --syntax-check publish_full_update.yml
ansible-playbook --syntax-check promote_content_view.yml
ansible-playbook --syntax-check check_patch.yml
```

These are implementation/offline checks. A live end-to-end demonstration,
actual patch installation, reboots and later AAP CaC deployment are separate
validation steps. Implementation decisions and commit references are recorded
in [design_decisions_history.md](design_decisions_history.md).
