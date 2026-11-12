# Implementation choices and supporting-code interfaces

This project uses the certified Satellite collection for supported content
operations and built-in Ansible modules for orchestration, identity/service
checks and reboot handling. The following small helpers address specific gaps;
none is a replacement automation framework or a request to add a collection.

## Validation filters

`filter_plugins/content.py` and `filter_plugins/sniper.py` keep structured
validation, deduplication, date arithmetic and exact RPM identities out of long
Jinja expressions. Built-in filters cover simple selection, but do not provide
these project ownership/recovery contracts, complete per-CVE resolution or
unambiguous repository epoch joins. The helpers use controller Python, stdlib
and Ansible; they make no network calls and perform no writes. Offline tests
exercise invalid, missing, foreign and ambiguous data and synthetic real-Ansible
boundary fixtures. Expected malformed inputs raise actionable errors.

### Public filter interfaces

| Filter | Input and additional arguments | Result / important rejection |
|---|---|---|
| `sniper_one` | Resource list; optional label | The sole row; rejects empty/multiple/non-list data. |
| `sniper_owned` | Rows, exact marker, optional label | Rows after exact ownership-description validation. |
| `sniper_task_ids` | Incremental API task object/list | Identifiable task UUID list; rejects incomplete replies. |
| `sniper_repo_options` | Exact RHSM label list | Sorted `--disablerepo=*` and enable arguments; rejects globs/unsafe labels. |
| `sniper_initial_baseline` | Version history | Unambiguous initial baseline; does not guess among histories. |
| `sniper_baseline_ids` | Host advisory rows | Deduplicated outstanding RHSA IDs; rejects an empty demo set. |
| `sniper_baseline_searches` | RHSA ID list | Bounded exact advisory searches. |
| `sniper_baseline_plan` | Selected RHSA IDs, repository advisory details, optional cutoff, optional existing version list | Selected advisory set, earliest issue date and a valid preceding cutoff. |
| `sniper_update_cutoff` | Date cap, current advisory rows | Canonical cap or explicit empty latest mode; rejects removal of already serving advisory content. |
| `sniper_verify_cutoff` | Published advisory rows, cap | True only when every advisory has a usable issue date within the cap. |
| `sniper_minor_candidate` | Version history, baseline, CV ID, description, Library environment ID, current Library rows | Zero or one safe recoverable candidate; rejects foreign lineage, competing history or unsafe exposure. |
| `sniper_minor_library_safe` | Current Library rows, baseline, candidate, CV ID | True after validating Library identity; refuses conflicting content. |
| `sniper_patch_id` | One ID string | Canonical RHSA/CVE; rejects expressions or malformed IDs. |
| `sniper_patch_ids` | Survey text | One RHSA or up to 50 distinct CVEs; rejects mixed input. |
| `sniper_resolve_queries` | Repository/input query results, requested IDs | Deduplicated advisories plus complete per-input mapping. |
| `sniper_validate_resolution` | Per-input mapping, full advisory details | Mapping after validating each CVE against actual advisory metadata. |
| `sniper_package_searches` | Full advisory details | Bounded exact package-identity searches. |
| `sniper_package_requirements` | Full advisory details, authoritative repository package rows | Binary fix requirements with explicit epochs; rejects missing, conflicting or ambiguous metadata. |
| `sniper_package_delta` | Before/after RPM inventory text or lines | Changed names, including valid signing-key records; does not infer upgrade direction. |

Examples use synthetic data:

```yaml
- name: Validate one exact resource
  ansible.builtin.set_fact:
    selected: "{{ [{'id': 1}] | sniper_one('example resource') }}"

- name: Normalize a single advisory
  ansible.builtin.set_fact:
    requested: "{{ 'rhsa-2025:1234' | sniper_patch_ids }}"
```

The functions are project-local filters, not collection plugins with a separate
release/API package. Their exported names are retained for current playbooks
and tests. Full reST packaging, wholesale type annotations or a pytest migration
would add work without a demonstrated consumer benefit; revisit if they become
shared collection interfaces.

## Native RPM proof

`files/rpm_proof.py` runs on the client using its existing OS Python and native
RPM bindings. Package facts alone do not compare epochs with RPM's own rules,
prove all installed architectures, associate each requested CVE with live
advisories, or confirm that a fixed kernel is running. `rpm.labelCompare` avoids
lexical-version mistakes. The selected certified collection reads Satellite
metadata; it does not independently inspect the guest RPM database.

The JSON CLI accepts fixed package requirements and optional request/advisory
mapping options. It emits detailed JSON. An unverified fix returns process code
0 so callers can inspect pre-update state; **callers must assert `verified`**.
Malformed input or unavailable RPM facilities return code 2. It installs nothing
and writes nothing. Python 2.7 compatibility is retained for RHEL 7 clients.
Tests cover epochs, multilib, missing components, per-CVE proof and kernel state;
mock comparisons are distinct from actual native-RPM AAP evidence. Supported
kernel coverage is limited as described in [operations](operations.md).

## Runtime inspection

`files/runtime_probe.py` uses the selected EE's own `ansible-galaxy`,
`ansible-doc` and syntax-check commands. Built-in facts do not expose all these
installed-content interfaces in one report. Its subprocess calls never install
content or execute the demonstration stages. Dependencies are the existing
Ansible/Python/PyYAML runtime. The read-only playbook also queries Satellite
organizations with certificate verification. Unit tests and a local synthetic
Ansible check-mode regression exercise the report and caller behavior.

## Native host commands

The selected Core modules can request security updates generally, but do not
provide this demo's exact advisory-set plus repository allow-list behavior.
One argv-based yum/dnf transaction therefore applies the explicitly resolved
advisories, or the explicitly requested full scope. Built-in reboot and service
facts handle their native operations. No shell evaluation is used.

`subscription-manager identity` ties SSH access to the exact Satellite consumer.
`rpm -qa` snapshots provide all installed EVRs and signing-key changes for honest
change reporting. `needs-restarting -r` and its process scan provide OS reboot
and stale-binary evidence unavailable through a generic package fact. The process
scan can expose full command lines, so its task uses `no_log` while its registered
result remains usable for the reboot decision. A synthetic verbose-Ansible test
confirms both redaction and that internal decision data survives.

A full update finishes with fresh selected-repository `check-update`; rc 0 is
complete, rc 100 means updates remain, and other statuses are errors. These
commands require existing host tools and SSH/become. They do not install
prerequisites. Actual package deltas and proof determine results; masking the
package command's changed flag is not the idempotency claim.

## Incremental update API

The installed `redhat.satellite` 3.14.0 `content_view_version` module supports
publication/promotion but does not expose true incremental update. Its inspected
source provides the basis for the single `ansible.builtin.uri` POST. It uses
verified HTTPS, refuses redirects/netrc, omits host patching and automatic
consumer promotion, and waits for actual task completion. Content is validated
before normal Library/Test promotion; Prod reuses the exact checked Test minor.
There is no blind POST retry. Synthetic actual-Ansible recovery fixtures cover
the boundary; live acceptance must still use the exact corrected source.

## Synthetic test modules

The Python snippets in the boundary tests implement deliberately small local
Satellite fixtures. Native mocks alone cannot demonstrate actual Ansible
include/condition/templating flow. These fixtures let the real playbooks run
against predictable local state without production credentials or host changes.
They are test-only, depend on the existing local Ansible/Python/PyYAML tools and
are not a job-time dependency installer or a second runtime API client. They do
not establish vendor-module or real-environment behavior by themselves.

## Source and caller inventory

The dispositions below follow inspection of the implementations and their
callers. **Retain** means the existing code has a concrete purpose within this
scope; it is not a claim that no alternative could ever be built. No custom
runtime module, role, action/lookup/inventory/callback plugin, shell script,
PowerShell or JavaScript is authored in this repository.

| Source and actual caller | Contract, context and effects | Alternatives and disposition |
|---|---|---|
| `filter_plugins/content.py`; called by preparation, minor/full publication, promotion and shared context/connect tasks | Controller-only structured Satellite rows/IDs/dates to exact ownership, baseline/cutoff and recovery decisions. Pure stdlib/Ansible transformations; malformed/ambiguous data raises `AnsibleFilterError`. No network/filesystem mutation or secret output. | Satellite `resource_info` supplies rows; its 3.14.0 modules do not implement project-specific provenance/recovery contracts. Built-in Jinja covers elementary selection, not this complete decision. **Retain** cohesive tested filters instead of long duplicated YAML expressions. |
| `filter_plugins/sniper.py`; called by `tasks/resolve.yml`, `tasks/host_context.yml` and `patch_hosts.yml` | Controller-only survey text/query results/package catalogs/RPM snapshots to validated ID mappings, exact EVRs and changed package names. Pure Python; invalid, unresolved or ambiguous input raises an error. No writes/network. | Certified Satellite reads advisory/package metadata; built-in filters cannot supply authoritative epoch joins or complete per-input validation alone. **Retain** bounded pure transformations and public interfaces. |
| `files/rpm_proof.py`; loaded as Python `-c` by `tasks/proof.yml`, imported from both host patching and read-only verification | Runs on the exact client with existing OS Python/native RPM bindings. Structured requirements/request mapping to installed-EVR, architecture and running-kernel JSON proof. Reads RPM/kernel state, writes nothing. Returns 2 for malformed/runtime error; callers assert `verified` after successful execution. | `ansible.builtin.package_facts` provides inventory; Satellite metadata is not native guest proof. Neither supplies the complete librpm comparison/kernel/request contract. **Retain** this small proof. Copying it to disk or converting it to a custom module would add packaging/state without removing the comparison logic. Python 2.7 syntax is intentional. |
| `files/runtime_probe.py`; called by `check_runtime.yml` | Controller/EE read-only list/docs/syntax subprocesses and YAML interface inspection; directory input to JSON report of versions, missing modules/arguments and syntax failures. Existing Ansible/Python/PyYAML only. Commands may use Ansible's temporary files, but never run the demonstration or install dependencies. Caller asserts the report and Satellite read. | `setup` facts do not expose installed collection interfaces. A long YAML loop could invoke the same three CLIs and parse the same structures with less readable validation. **Retain** one cohesive diagnostic. |
| `ansible.builtin.command` argv tasks in `tasks/host_preflight.yml`, `tasks/proof.yml`, `tasks/check_final.yml`, `patch_hosts.yml` and `check_runtime.yml` | Native identity, RPM inventory/proof, reboot detection and selected-repository update/completion commands. Host checks are reads; yum/dnf updates RPMs only in the explicit patching job. Expected rc sets are bounded; invalid identities/proofs fail. Full stale-process argv is protected by `no_log`. No shell evaluation or generated shell program. | Use native `reboot` and `service_facts` where suitable. Core's yum/dnf modules provide broad security/repository options, but not this exact advisory-set minimal transaction plus completion contract. **Retain** the exact targeted command; keep full-update behavior consistent with its existing verified transaction/proof path. No new installer or service. |
| `ansible.builtin.uri` in `create_minor_update.yml` | Controller POST of validated missing advisory IDs to the protected Satellite endpoint; creates an asynchronous incremental version, waits and validates before promotion. No consumer update and no blind POST retry. TLS, no redirects/netrc and `no_log` protect authentication. | Inspected certified collection 3.14.0 `content_view_version` supports publish/promote, without the incremental action. **Retain** this single documented API gap; reconsider if the selected collection gains the action. |
| `tests/test_baseline.py`, `test_content.py`, `test_epochs.py`, `test_multi_ids.py`, `test_runtime.py`, `test_sniper.py`; invoked by unittest discovery | Controller-local synthetic inputs exercise filters, real Ansible templating, proof contracts and runtime argument inspection. Fake RPM comparisons do not establish native-RPM correctness. No live credentials/targets or package changes. Assertions make failures explicit. | Vendor modules cannot test this project's invalid-input/proof contracts. **Retain** stdlib unittest with existing Ansible/PyYAML; no new framework or exhaustive platform matrix. |
| `tests/test_preparation.py`, `test_minor_recovery.py`, `test_full_publication.py`, `test_dynamic_resolution.py`; unittest discovery generates `MODULE` fixtures and invokes real local Ansible | Temporary synthetic Satellite modules/state exercise ownership, interrupted-minor recovery, cutoff/content retention, retries and dynamic CVE mapping. Each fixture has explicit mocked operations; mutations are local temporary JSON only. No Satellite connection, AAP launch or dependency installer. Failures are asserted; temporary contexts clean up owned files. | Pure mocks cannot verify the actual import/condition/template flow. Live certified modules cannot provide deterministic local failure states without a real Satellite. **Retain** the small test-only modules; replacing them with declarative tasks would lose the simulated API boundary. |
| `tests/test_review_regressions.py`; unittest discovery generates a synthetic argv command, runtime JSON emitter and `resource_info` module | Real local Ansible tests output redaction/retained reboot evidence and diagnostic `--check` flow. Synthetic-only sensitive marker and credentials; temporary owned files, bounded subprocesses, explicit pass/fail. No remote target. | A source-text assertion would not prove redaction or command execution. **Retain** these two behavior regressions; generated snippets are fixtures rather than a new runtime client. |

Source evidence for the selected alternatives includes
[Satellite 3.14.0 publication/promotion module](https://github.com/RedHatSatellite/satellite-ansible-collection/blob/3.14.0/plugins/modules/content_view_version.py),
[Core 2.15.11 yum module](https://github.com/ansible/ansible/blob/v2.15.11/lib/ansible/modules/yum.py),
[Core package facts](https://github.com/ansible/ansible/blob/v2.15.11/lib/ansible/modules/package_facts.py)
and [Core command module](https://github.com/ansible/ansible/blob/v2.15.11/lib/ansible/modules/command.py).
These native modules and the previously selected certified Satellite release
were assessed before retaining custom behavior. A source checkout or converted
analysis wheel does not prove certified binary provenance. Exact target-image
and entitled collection-artifact provenance remain review evidence gaps.
