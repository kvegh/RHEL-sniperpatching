# RHEL sniper patching: quick guide

Select the OLD or NEW directory explicitly in each AAP template:
`playbooks/old/<stage>.yml` or `playbooks/new/<stage>.yml`. The OLD workshop
results below do not certify the pending NEW Satellite installation. See
[the two-track layout](README.md#old-and-new-tracks).

The demonstrated scope is an existing Satellite/AAP workshop and two RHEL 7.9
clients. Each stage is a separate human launch; this is not an automatic workflow.
Use the existing compatible EE, protected Satellite credentials, and Machine
SSH/become access. Keep the AAP Limit empty, verify TLS, and supply the exact
Test/Prod pair and repositories through protected inputs.

1. On a fresh, unpatched pair, prepare the dedicated Content View and lifecycle
   path once. Preparation preserves an already established baseline on retries.
2. Select one RHSA, or up to 50 CVEs resolved live through Satellite. Publish its
   minor version to Test, patch Test, and wait for fix/reboot/smoke checks.
3. Promote that exact tested minor to Prod, then patch and verify Prod separately.
4. Supply an explicit issue-date cutoff before the next demonstration advisory.
   Publish the broader major version to Test and run the full Test update.
5. Promote the exact tested major to Prod, run the full Prod update, and verify.
6. Choose the next still-unpatched advisory for another visible change cycle.

Allow required reboots. An already-current full run succeeds only after fix,
reboot, smoke and fresh repository-update checks pass. Resetting a Content View
never downgrades installed RPMs. Snapshot/rollback work remains on hold at the owner's request.

The catalog is historical 2023–2024 content. Two cycles passed in November 2026
on functional version 0.5.7; that does not certify current advisories or another
platform. The receiving AAP's configuration import/runtime check passed, but
its client SSH access remains unverified. The replacement OLD environment subsequently passed three cycles on reviewed
0.5.8. The path-only 0.6.0 reorganization has local regression checks; its new
Satellite installation and live NEW demo acceptance remain pending. Full review
tooling/provenance gaps are separate from the completed OLD functional tests.

See the [full presenter guide](README.md), [manual process diagram](docs/process.md),
[inputs and recovery](docs/operations.md), [supporting-code rationale](docs/implementation.md),
and [current review evidence](docs/review-2026-11-12.md).
