# NEW chronological cycle acceptance

Evidence checkpoint: **16 November 2026, 07:36:25 UTC**. All nine agreed
chronological Test/Prod cycles passed on the same two original RHEL 9.4 x86_64
clients. All ten selected CVEs are at or above their first-fixed package builds
on both clients, with the additional running-kernel and installed-userspace
checks described below.

The [ten-CVE catalog](rhel94-cve-candidates.md) spans nine security advisories.
RHSA-2024:5928 fixes two selected CVEs in one package-update step. The nine
completed advisory cycles fix ten selected CVEs; the shared advisory does not
provide a separate transaction for each CVE. Cumulative package updates retain
earlier fixes.

## Completed procedure and results

Each completed row passed the normal nine stages: create and validate the Test
minor; patch Test with that advisory; promote the exact tested minor; patch
Prod; publish the bounded full update to Test; patch Test fully; promote that
exact full version; patch Prod fully; and run the independent Prod check.
Native verification covered the requested fix, the running kernel where
relevant, required reboots, smoke checks and no outstanding reboot. Both full
updates also passed their no-pending-repository-update checks. Fresh read-only
Satellite and native package snapshots preserved original host and consumer
identities and recorded all twenty selected package witnesses. All nine pinned
cycle aggregates were checked: they contain **81 distinct successful normal-stage
jobs**. Preserved failed attempts remain separate from that count.

The cutoff is inclusive. Each row's package count and running kernel are the
post-full-update values on **each** original client; both clients matched.

| Cycle | Advisory | Tested minor | Full version | Full cutoff | RPMs per client | Running kernel | Selected CVEs fixed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | RHSA-2024:3339 | 1.1 | 2.0 | 2024-05-23 | 447 | 5.14.0-427.18.1.el9_4.x86_64 | 1 of 10 |
| 2 | RHSA-2024:4312 | 2.1 | 3.0 | 2024-07-03 | 456 | 5.14.0-427.22.1.el9_4.x86_64 | 2 of 10 |
| 3 | RHSA-2024:4457 | 3.1 | 4.0 | 2024-07-10 | 456 | 5.14.0-427.24.1.el9_4.x86_64 | 3 of 10 |
| 4 | RHSA-2024:5363 | 4.1 | 5.0 | 2024-08-15 | 456 | 5.14.0-427.31.1.el9_4.x86_64 | 4 of 10 |
| 5 | RHSA-2024:5534 | 5.1 | 6.0 | 2024-08-19 | 456 | 5.14.0-427.31.1.el9_4.x86_64 | 5 of 10 |
| 6 | RHSA-2024:5928 | 6.1 | 7.0 | 2024-08-28 | 456 | 5.14.0-427.33.1.el9_4.x86_64 | 7 of 10 |
| 7 | RHSA-2024:6567 | 7.1 | 8.0 | 2024-09-11 | 456 | 5.14.0-427.35.1.el9_4.x86_64 | 8 of 10 |
| 8 | RHSA-2024:6754 | 8.1 | 9.0 | 2024-09-18 | 456 | 5.14.0-427.35.1.el9_4.x86_64 | 9 of 10 |
| 9 | RHSA-2024:8446 | 9.1 | 10.0 | 2024-10-24 | 456 | 5.14.0-427.40.1.el9_4.x86_64 | 10 of 10 |

At this checkpoint, both clients used full **10.0**, bounded inclusively through
**2024-10-24**. Native RPM snapshots explicitly verified `redhat-release` EVR
`0:9.4-0.5.el9`: the clients remain on RHEL 9.4. All ten witnesses per client were
at or above their first-fixed builds. Both final full updates changed fifteen
package names and passed the full fix, reboot, smoke and no-pending-update checks.
The Prod full update passed **07:29:59–07:34:12 UTC**; the independent final check
finished **07:35:57 UTC**.

Final acceptance additionally bound all four selected kernel CVEs to the actual
running kernel **5.14.0-427.40.1.el9_4.x86_64**. Native EVR comparison showed that
running build above each first-fixed build. For the six selected userspace CVEs,
every installed build of each recorded witness package met its first-fixed EVR.
Existing native snapshots supplied these cross-CVE checks. Older installed kernel
fallbacks remain visible and are not used as running-kernel evidence. Installed
package and running-kernel proof remain distinct from exploitability testing.

## Corrected kernel-module proof passed live

The fourth targeted Test run installed and booted its fixed kernel, then failed
the final fix guard at **03:19:02 UTC**. Retained older `kernel-modules` and
`kernel-modules-core` builds had been classified as ordinary userspace
duplicates. The focused NEW correction in implementation
`61ba62232e425a1a7497cd0813c8249976325e43` (0.14.11) applies the existing exact
running-release and native fixed-EVR checks to those two standard module names.
Userspace and unknown package names retain their strict checks; OLD is unchanged.

The normal Test recovery passed **03:31:20–03:32:04 UTC** against the same minor
**4.1**, reporting `already_current` and no package changes because the earlier
run had performed the transaction and reboot. Prod then passed its actual
targeted update and reboot. Both full **5.0** updates and the independent final
check passed before the fifth cycle began. The initial failure remains in the
sealed acceptance record; this was a recovered procedure, not an uninterrupted
first attempt. No minor rebuild, package-backup removal or client reset was used.

Earlier first-cycle calendar-cutoff and exact-version promotion failures also
remain in the protected acceptance evidence. Those issues were corrected before
the paired procedure was accepted. The table records the completed procedures
without erasing their failed attempts or presenting the successful-stage count
as an uninterrupted run.

## Source provenance and scope

Executable source revisions are recorded separately for every stage. The
fourth minor predates the module-proof correction; its successful recovery and
later stages use the corrected implementation. During cycles six and seven,
public presentation changes advanced the source through `7667ca7`, `e2e0fc8`
and `28ab1a5` (public version 0.15.2). Exact Git-tree comparisons verified the
same 99 entries across `playbooks`, `surveys`, `tests`,
`docs/rhel94-cve-candidates.json` and `ansible.cfg` for the applicable
presentation-only revisions and their qualified automation baseline. Each
cycle's protected aggregate retains its actual stage revisions and equivalence
proof; a single uniform source revision is not claimed for these mixed runs.
All eighteen normal stages of cycles eight and nine used `28ab1a5`, with that
same qualified automation tree. The interactive mockup's publication and browser
checks have separate evidence.

Raw job events, native package snapshots, original identity bindings, failure
records and hash-linked aggregates remain protected with the existing whole-file
Vault mechanism outside this public document. This sanitized summary publishes
no credentials, environment addresses, host identities or encrypted payloads.
Local sealed evidence and publication of that evidence to a private companion
are separate outcomes.

This acceptance covers the selected standard RHEL 9.4 pair and demonstrated
workflow. It does not establish exploitability, equivalence to a full
installation ISO, support for other kernel variants, a major OS upgrade or
universal CoP compatibility. No clients were recreated, reinstalled, restored
from snapshots or upgraded to RHEL 9.5. Full formal review, matching-EE strict
lint, OLD runtime/compatibility qualification and held shared/image work remain
separate. Earlier focused test results are not a latest-source full-suite rerun.
