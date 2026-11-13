# Current checkpoint — 2026-11-13

Version0.6.0 separates `playbooks/old/` and `playbooks/new/`; see the current
[README](README.md#old-and-new-tracks). Both preserve the reviewed runtime logic.
The replacement OLD environment completed three Test-to-Prod cycles on0.5.8;
full policy/tooling/provenance acceptance remains separate and incomplete.
The directory reorganization passed98 local synthetic tests per track, fourteen
syntax checks and production lint. The private companion updates the seven
existing CaC paths to OLD. No live template update or import was performed.

The new VM and read-only prerequisite checks are complete. New Satellite
installation, its own protected AAP configuration and complete NEW demo remain
pending. Follow the [documented installation sequence](docs/new-satellite.md),
including correct forward/reverseDNS and RHEL update before installation.

The earlier handover below is historical; its pending functional re-test and
next-cycle statements are superseded by this checkpoint.

---

# Current status for handover

> Later work: the [12 November review evidence](docs/review-2026-11-12.md)
> records the subsequent review/fix phase. This file remains the earlier checkpoint.

Updated **2026-11-11**. This is a documentation checkpoint, not a fresh check of
running systems. Beads remains the task tracker. No execution or code review
was started while preparing this handover.

## Project and source

- Public project: [RHEL-sniperpatching](https://github.com/kvegh/RHEL-sniperpatching),
  a submodule of [AAP Advanced Features](https://github.com/kvegh/AAP-advanced-features).
- Current demo version: **0.5.7**. Functional implementation: `2be30c7`.
  Source before this documentation checkpoint: `87a518f29245fc0c90a5c5ac4cf7ebe94bb3196e`.
  Changes after the functional implementation were README and decision-history updates.
- Environment inputs and AAP configuration belong to the private,
  Vault-encrypted `RHEL-sniperpatching-secrets` companion. This public file
  contains no endpoints, credentials, inventory bindings or raw job output.
- The unrelated Command Center application is outside this project's scope.

## Implemented and previously verified

The project provides independently launched preparation, incremental Content
View publication, host patching, date-bounded full publication, explicit
production promotion and read-only patch verification, plus an EE diagnostic.
Production reuses the exact tested content version. Host checks include native
RPM epoch/version/release comparison, running-kernel checks where applicable,
reboots when required and smoke checks. Full mode verifies the selected fix and
that no approved repository updates remain; an already-current host is valid.
The former artificial independent-package witness requirement was removed.

The demonstrated runtime uses RHEL 7.9 clients, Ansible Core **2.15.11**, Python
**3.9.19** and `redhat.satellite` **3.14.0** in the existing workshop EE. The user
explicitly selected that runtime. Do not substitute collection 6.0.0 into it:
6.0.0 requires Core 2.16 or newer. A new runtime needs its own compatibility and
acceptance evidence.

Two complete targeted/full-update cycles were recorded as successful on
**2026-11-05**, using the established Test/Prod pair and normal AAP Job Templates:

| Cycle | Targeted advisory | Full-content issue-date cutoff | Recorded outcome |
|---|---|---|---|
| First | RHSA-2023:6823, Python 3 | 2023-11-10 | Both hosts passed targeted verification and the bounded full-update checks; full runs were already current. |
| Second | RHSA-2023:6885, Python | 2023-11-17 | Both hosts updated Python packages; the full stage updated microcode_ctl, and final verification passed. |

The last recorded Content View version serving both stages was **4.0**.
Twelve original advisory candidates had not been exercised by the demo; the
next was RHSA-2023:7423. These are historical results, not today's host state.
Publishing an older Content View does not downgrade installed RPMs.

AAP configuration-as-code import and the imported runtime diagnostic also
passed on a separate receiving AAP. Host SSH access from that receiving AAP was
not verified; successful import alone does not establish patching readiness.

## Corrections already completed

Earlier conversation messages describing an unfinished RPM epoch fix are stale.
Satellite's advisory package names omit epochs; authoritative epochs are now
resolved from repository package metadata. Missing or ambiguous metadata fails
instead of silently assuming zero. That correction was implemented in
`9199670`, published and verified by a corrected read-only check.

Other recorded repairs cover original-package filters, normal promotion through
Library before Test, bounded recovery of interrupted minors, RPM signing-key
inventory entries and transient read-only response retries. See
[design_decisions_history.md](design_decisions_history.md) for their commits and
individual validation records. Preserve the resource, host-identity and
repository restrictions when reviewing or changing the code.

## Code-review status

The authoritative shared guideline is
[Agent_generated_code_review](https://github.com/kvegh/Agent_generated_code_review).
The local policy examined for this handover was revision
`e45b49b0de5231fbb580d828f2247161a7787863`. Read its full
[README](https://github.com/kvegh/Agent_generated_code_review/blob/e45b49b0de5231fbb580d828f2247161a7787863/README.md)
and [TLDR](https://github.com/kvegh/Agent_generated_code_review/blob/e45b49b0de5231fbb580d828f2247161a7787863/TLDR.md).

Targeted code assessments, regression tests, syntax checks, production-profile
lint and live end-to-end results are recorded. **No completed review against the
full shared guideline was found for this repository.** In particular, there is
no root `Code_Review_YYYY-MM-DD.md` acceptance report. Do not describe the project
as fully reviewed or infer full policy compliance from the successful demo.
This absence is a review-evidence gap, not a newly established code defect.

A future authorized review must define the exact source, CaC, runtime and test
scope; cover the complete CoP guide and policy directives; establish strict
lint/APME and other required tool coverage; assess readability, security,
idempotency, recovery, documentation and timing; and finish with the required
complete AAP end-to-end test. Record findings and proportionate accepted
deviations honestly. Obtain approval before installing missing tools or making
material architecture, access or runtime changes. Check the current policy
revision at review start rather than treating this handover's revision as final.

## Continuation and durable task references

The user requested a handover to another chat and asked for fresh approval after
sessions became tangled. This document is context, not execution authorization;
do not replay old queued approvals or uncertain tool calls. Confirm the intended
next activity with the user before starting a review or another demo cycle.
Use protected access inputs rather than copying secrets into a new chat or Git.

| Beads record | Last verified status and scope |
|---|---|
| `bead-wd-hwf2` | Tracks this requested handover and review-status documentation. |
| `bead-wd-0fv`, `bead-wd-0fv.1` | Closed: original direct host verification and authoritative epoch correction. |
| `bead-wd-j0g`, `bead-wd-j0g.13` | Closed: delivery of the demo/CaC and the second complete cycle. |
| `bead-wd-v2w7` | Open future work: refresh the demonstration with current 2026 advisories and verify suitable hosts/content. It was not resumed here. |
| `bead-wd-lz8` | Deferred: VM snapshotting and rollback. Do not resume without an explicit user request. |

No formal policy review, fresh remote environment checks, code fixes, package
installation, Content View changes or snapshot operations were performed during
this documentation checkpoint. No active child agents were found. Old pending
host-verification messages have been superseded by the completed task records.
