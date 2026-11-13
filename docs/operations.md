# Inputs, validation and recovery

## Data ownership and inputs

Protected AAP inventory/credentials and the private Vault companion define the
authorized target and desired operator inputs. Satellite supplies current
Content View, lifecycle, repository and advisory metadata; installed RPMs and
the running kernel are read directly from the selected client. Neither source
alone proves the complete outcome. Privileged extra variables are trusted
configuration, not a security sandbox against an authorized AAP administrator.

| Input | Meaning and default |
|---|---|
| `sniper_server_url`, `sniper_username`, `sniper_password` | Protected connection inputs; default to `SATELLITE_SERVER_URL`, `SATELLITE_USERNAME`, `SATELLITE_PASSWORD`. HTTPS verification is required. Use credentials/Vault; no plaintext command-line passwords. |
| `sniper_organization` | Required organization; defaults to `SATELLITE_ORGANIZATION`. |
| `sniper_test_host`, `sniper_prod_host` | Required, distinct exact Satellite/inventory names. Never inferred. |
| `sniper_repositories` | Required for preparation: explicit repository/product mappings; later stages inspect the dedicated CV. |
| `sniper_namespace` | Defaults to `RHEL-sniperpatching`; may use the validated project suffix convention. |
| `sniper_owner`, `sniper_content_view`, `sniper_test_environment`, `sniper_prod_environment` | Ownership marker and namespace-derived names. Existing foreign objects are refused. Keep the approved defaults. |
| `sniper_environment` | Explicit `test` or `prod`; no implicit production rollout. |
| `sniper_patch_id` | One RHSA or up to 50 CVEs as comma/space/newline-separated text. Each CVE must resolve live; an RHSA cannot be mixed with CVEs. |
| `sniper_patch_scope` | `targeted` by default; `full` explicitly updates all available content in the selected CV repositories. |
| `sniper_baseline_end_date` | Empty selects the day before the earliest outstanding RHSA on the fresh pair; an explicit date must precede the selected advisory set. Established baselines are preserved. |
| `sniper_update_end_date` | Explicit `YYYY-MM-DD` issue-date cap for the normal demonstration. Empty playbook input is the separate latest-content mode. |
| `sniper_baseline_filter`, `sniper_original_filter` | Namespace-derived filter names owned only by this project. |
| `sniper_version` | Required exact Test version for explicit production promotion. |
| `sniper_task_timeout`, `sniper_reboot_timeout` | Default 1800 and 900 seconds. |
| `sniper_rpm_python` | Optional trusted override for the operating-system Python with native RPM bindings. Normally inferred for the declared OS. |
| `sniper_smoke_services`, `sniper_smoke_urls` | Defaults are `[sshd]` and `[]`. Add application service names and `{url, status}` checks when meaningful; the default does not establish application-level coverage. |

Track defaults live in each `playbooks/<track>/vars/main.yml`. Runtime facts are derived separately;
protected AAP extra variables can override play defaults. Do not place secrets
in public examples, survey defaults, inventory files or logged URLs. The full
survey JSON files are under `surveys/`; real credential bindings stay private.

## Outputs and execution checks

Content stages report exact versions, resolved advisories and the next manual
step. Host patching jobs expose `sniper_result` with the request-to-advisory mapping,
selected stage/version, native package proof, and changed package names.
Read-only check jobs report the request mapping, stage/version and native proof;
they do not report a package-change delta. Full patching jobs additionally report `updated` or `already_current` and the completed
repository-update check. A missing/skipped selected-host proof fails the final
controller assertion. Keep the job Limit empty so both controller and client
plays run.

`playbooks/old/check_runtime.yml` reads installed versions/module interfaces and Satellite
organizations. Its probe is read-only and also runs under `--check`.
`playbooks/old/check_patch.yml` performs real identity/RPM/reboot/service reads and optional
HTTP GET smoke requests, including in check mode. It never installs or reboots.
Preparation, minor creation, host patching and full publication are not simulated
planning interfaces: they refuse mutation in check mode. Use explicit read-only
checks and Satellite inspection to plan changes; promotion is accepted only
when actual readback shows the requested version.

The declared acceptance scope is the tested standard RHEL 7.9 kernel on the
workshop pair. RHEL 8/9 branches, debug/realtime/other kernel variants, modular
content, major OS upgrades and application-specific mitigation are not newly
verified support. In particular, debug-kernel release suffixes need separate
proof logic and tests before that variant is accepted. This is not a claim that
all other platforms are incompatible.

## Recovery and repeat behavior

| Stage or failure | Operator action |
|---|---|
| Preparation repeated | Existing owned baseline and later serving versions are preserved. Only an unambiguous initial publication may repair an empty destination. Preparation is not a downgrade/reset operation. |
| Incremental request timeout | Inspect Satellite tasks and the retained candidate before retrying. The POST may have been accepted. There is no blind mutation retry. |
| Minor promotion interrupted | A later launch may reuse one matching orphan/Library-only candidate after the lineage, ownership, content and current-Library checks. Ambiguity or unrelated newer content requires inspection. |
| Content validation fails | The candidate remains available for investigation without consumer promotion. Do not delete or force-promote it to make the next stage pass. |
| Full publication repeated | Publication deliberately creates another major snapshot. This release action is not an idempotent desired-state assertion. Read-only transient reply retries do not repeat publication or promotion. |
| Host update repeated | Already-fixed targeted work can be skipped. Full mode still performs the approved update/check; success requires fix proof, no pending reboot, smoke checks and no remaining selected-repository updates. |
| Package update/reboot fails | Stop before the next environment. Inspect the actual host and serving CV, then rerun the same stage only after understanding partial completion. No automatic package rollback is provided. |
| Source or CaC revision reverted | This does not restore guest disk contents or undo installed RPMs, CV publication or promotion. Recovery needs an explicit operator decision. |

The private companion and shared importer reproduce AAP configuration; an
import must not implicitly launch the demo. Before using a receiving instance,
verify credential bindings, inventory, Limit behavior, installed EE runtime and
client SSH/become access. The earlier import/runtime check is not evidence of
receiving-client connectivity or repeated-apply idempotency.

Credential rotation/revocation, AAP service-account permissions, registry/image
security and review cadence belong to the environment owner. Update protected
sources and their bindings together, validate read-only access after rotation,
and keep secrets/raw diagnostics outside this repository. This review does not
change RBAC, credentials, subscriptions or schedules, or certify CIS compliance.

Return to [README](../README.md) or [TLDR](../TLDR.md).
