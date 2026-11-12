# Supplemental APME results and dispositions

**Incomplete acceptance.** Scan `4d82068a-2cac-454d-afb2-e0cffa82a2a8`
completed in30.610seconds using installed APME revision
`9c4372f79a8b537865040cea17cf9db7659614ad`, upstream Core2.15.11 and
Python3.12.14. It analyzed the19 uploaded Ansible files, not every Python,
documentation or Git-history blob. Satellite3.14.0 was built from the existing
source revision `17dc64abe942270ecb4153ef80aaaa4aa17e8d35` for local analysis;
this converted wheel is not certified EE/artifact provenance. No generated
remediation diff was applied. Artifact line coordinates are normalized and can
differ from source file lines.

The first scan aborted before validation because public Galaxy could not resolve
the Satellite pin. The subsequent source import used the native authenticated
proxy in a temporary local review service. No AAP EE, host or Satellite state
was changed. Reports/raw diagnostics stay outside public Git.

## Backend completion and limitations

| Backend | Returned records | Actual coverage |
|---|---:|---|
| Native |222|Completed; manually assessed dataflow/risk/style leads below.|
| OPA |7|Completed; ordinary debug-output suggestions assessed below.|
| Ansible |0|Syntax, introspection and documented args checks completed, but L059 mocked argspec serialization failed internally. Zero returned records is not complete coverage. Separate runtime probe passed all used module arguments.|
| Gitleaks |0|Completed for uploaded Ansible files. Separate current-directory and all-ref Git-history scans also passed, including 41 commits through baseline66e9554; no leaks reported.|
| Collection Health |8|Completed vendor-source scan: six Core>=2.19 migration leads and two become records in vendor tests. No vendor source edits. Not a collection-wide security certification.|
| Dependency Audit |0|Backend returned after underlying pip-audit failed on the non-PyPI converted collection wrapper. **Incomplete, not clean.** Direct pinned-PyPI audit separately returned genuine advisories.|

## All 237 returned findings

Independent content and host reviewers inspected overlapping scopes; their
counts must not be added. The exact global counts below sum to 237 and include
eight vendor records. Classifications reflect inspected source and the retained
baseline, not a blanket ignore list. No scanner rule was disabled.

| Rule | Count | Disposition |
|---|---:|---|
|L039|101|False-positive dataflow/keyword warnings: all records inspected. Inputs/facts arise from vars/main.yml, preceding imports/registers/set_fact and branch gates; attribute is a Jinja keyword. No missing-value defect substantiated.|
|M005|30|Version-scoped migration warnings explicitly target Core >=2.19; selected runtime is2.15.11. Six are in vendor collection roles/tests. Future migration compatibility remains unverified, not proven broken or clean.|
|L049|26|Accepted naming deviation: separate flat task loops use item without demonstrated active nested-loop shadowing. Renaming all references adds churn; revisit nested includes.|
|L099|19|Readable single YAML wrappers around complete Jinja expressions preserve quoted arguments and match the CoP exception. No quoting defect; retain existing interface formatting.|
|L078|19|Accepted notation deviation: inspected fixed keys do not collide with dictionary methods. Revisit when a schema or meaningful touched code introduces ambiguity.|
|L042|8|Accepted structure deviation: counts expand shared task imports. Manual stages stay cohesive; role conversion solely to lower a count adds indirection and regression cost.|
|L067|7|Intentional visible operator output: versions, proof, package changes and next step are required demonstration results. Higher debug verbosity would hide them; sensitive stale argv is now protected.|
|L073|6|Continuation alignment inside folded Jinja scalars is not YAML structural indentation. Actual parsing/lint succeeds; no meaningful defect established.|
|L033|5|Independent entrypoints derive fresh facts; preparation intentionally refreshes ready versions after promotion. No accidental state overwrite substantiated.|
|R108|4|Two project become plays provide required package/reboot/protected-system reads on the exact selected consumer; localhost API plays are not escalated. Two records are vendor test plays outside project execution. Current actual RBAC remains unverified.|
|R101|4|Reviewed argv execution for trusted runtime/proof helpers and exact advisory/repository commands. Validated selectors and separate JSON arguments; no shell evaluation. Retain documented native gaps.|
|L060|4|Scanner-normalized scalar formatting produces long-line records; inspected affected source files contain no physical lines over160 characters. No suppression added.|
|L045|2|Only deterministic, non-secret LC_ALL:C is set for package commands. Moving one locale value to an environment file adds no meaningful benefit.|
|R105|1|Necessary protected Satellite incremental POST: exact validated IDs, verifiedTLS, no redirects/netrc, no_log, no automatic consumer update or host patching. Not unexpected exfiltration; no hardcoded environment endpoint.|
|L091|1|The preparation initialization fact is computed from Boolean comparisons; direct when use has no demonstrated string truthiness failure. A redundant cast adds no functional benefit.|

## Dependency findings and applicability

A direct audit of the actual installed PyPI package versions used
`--disable-pip --no-deps --strict` without installs/upgrades. The generated
non-PyPI collection wrapper was explicitly excluded and remains a separate
audit limitation. Duplicate distribution paths/report entries are deduplicated
for interpretation rather than counted as separate vulnerabilities.

The upstream Core2.15.11 analysis package is flagged for four unique advisories:
[CVE-2024-9902](https://access.redhat.com/security/cve/cve-2024-9902),
[CVE-2024-8775](https://access.redhat.com/security/cve/cve-2024-8775),
[CVE-2024-11079](https://access.redhat.com/security/cve/cve-2024-11079) and
[CVE-2026-11332](https://access.redhat.com/security/cve/cve-2026-11332).
The local analysis venv's bootstrap pip23.2.1 also has reported advisories.
This is not a scan of the actual Red Hat EE. Its RPM release/image digest,
backports and exploit-path applicability require separate verification; matching
an upstream version string does not prove vendor-image affectedness. No target
upgrade or security acceptance is inferred from the owner's choice to reproduce
the existing baseline. This review has not established a new project-code defect
or an exploit from these version findings.

The unused user-module/key-generation and role-install paths described by two
of those advisories are not project patching operations. That does not waive
other runtime/security findings or certify the full EE. Use the vendor advisories
and exact image/component readback before a final security disposition. Changes
to the selected AAP runtime remain an explicit owner decision.
