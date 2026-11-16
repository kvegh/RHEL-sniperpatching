# Interactive RHEL sniperpatching mockup

[Open the visualization](https://kvegh.github.io/RHEL-sniperpatching/).

Version **0.17.1**. This browser-only explanation is for security staff, Linux
administrators and AAP administrators. It follows the checked-in NEW architecture
while grouping tasks and shortening operations for presentation. It is an
explanatory mockup: statuses, CV numbers and outcomes are illustrative. No host,
Satellite or AAP connection is made. Live automation acceptance remains documented
separately in the project README and handover.

## Present it

Use **Next**, **Back**, **Restart**, or select one of the **seven scenes**.
Run 01 and Run 02 open their healthy baseline before introducing a new CVE.
The examples and dates are fixed; there are no presenter-entered values.
The scene counter remains at 5 or 7 while the rollout's action counter advances.
At production checkpoints, **Approve Prod** continues to exact-version promotion.
Right-arrow navigation pauses there; Enter/Space on the button also approves.
The real automation still uses separately launched AAP stages rather than an
automatic approval node. Scene links are educational navigation, not access controls.

| Scene | What changes |
| --- | --- |
| 1. All systems up to date | Test and Prod meet the same defined baseline, with green checks. No future CVE appears. |
| 2. CVE announced | A named alert reaches AAP; Satellite resolves its security advisory. Only announced issues affect host status. |
| 3. Ensure fix content is available | A small selected-fix/dependency flow arrives from Red Hat content to Satellite. |
| 4. Publish targeted CV | Add the selected fix and required dependencies to the baseline minor; Test availability changes before installation. |
| 5. Apply selected fix | Check the selected pair, patch/reboot/verify Test, approve, promote the exact minor, then patch/reboot/verify Prod. |
| 6. Routine patch window | Time passes; many security, bug-fix and enhancement updates arrive, retaining the already-applied fix in a broader CV. |
| 7. Apply broader updates | Fully update and verify Test, approve, promote its exact major, update/verify Prod and finish green. |

The compact status box sits beside the Red Hat software repositories on wider
screens, saving vertical space. The two panels stack on screens up to 640px.
The Red Hat source lane delivers content to Satellite. One selected fix and its
dependencies are visually distinct from the later batch of maintenance updates.
Arrival animations are finite and respect **Motion off** and reduced-motion
preferences. The page makes no actual download or API request.

The content-availability scene explains the content prerequisite: the targeted
playbook reads already synchronized repositories and does not launch a per-CVE
synchronization job. The full-publication playbook explicitly synchronizes the
selected repositories. Applicability checks apply to the configured Test/Prod
pair; the page does not claim implemented fleet-wide discovery. These details
are available beside the source-linked condensed code.

Both AAP and Satellite retain light-blue headers. The removed architecture
heading and Resolve/Patch/Verify badges stay absent. Green host checks indicate
baseline compliance or verified fixes; red identifies an announced outstanding
issue, and amber identifies verification or routine updates available. Previously
verified CVEs remain Fixed throughout a later maintenance update. Available CV
content and installed packages remain separate; promotion does not install RPMs.

Two fixed user-selected stories run in chronological order:

| Story | CVE / RHSA | Illustrative full-update cutoff |
| --- | --- | --- |
| Python malicious package download | CVE-2024-6345 / RHSA-2024:5534 | 2024-08-23 |
| Network Privilege Escalation | CVE-2024-36883 / RHSA-2024:6567 | 2024-09-13 |

The first cutoff leaves the second advisory outstanding. Kernel installation,
reboot and effective verification are separate rollout actions. Technical detail
identifies a local-user Linux networking flaw. The second run retains the first
run's fixed packages and starts from its completed baseline. The illustrative
CV sequence is 1.0 → 1.1 → 2.0 → 2.1 → 3.0; actual jobs return their own versions.
Grouped full-update actions include any required reboot and independent final
checks. Forty presenter-controlled actions unfold within the seven scenes per
run; there is no autoplay or artificial waiting period.

**Technical detail** shows condensed code and a source-pinned repository link.
Existing links such as `#step=run-2-input` still work; `#step=run-2-baseline`
opens the second run before its alert. On small screens, the narrative stacks
above the diagram. Browser layout remains separately unverified.

## Implementation

### Supporting code

`src/scenario.js` models the fixed story and deterministic states. `src/app.js`
uses native browser DOM APIs for rendering and controls; `src/styles.css` handles
presentation and motion. Native Ansible modules and certified Satellite content
implement the underlying automation, but cannot render an interactive browser
walkthrough. Small browser scripts are sufficient; no framework, dependency,
package manager, external CDN/font, analytics, API service or build is required.
Node built-ins provide the model, interaction and deployed-asset tests.

### Implementation and source mapping

All source links pin NEW code revision
`2fe10cd27c874691780c72eb66105f87cd5c12fa`, separate from visualization publication.

| Visual action | Implementing source |
| --- | --- |
| Controlled baseline | `playbooks/new/prepare_demo.yml` |
| CVE to RHSA resolution and synchronized-content lookup | `playbooks/new/tasks/resolve.yml`, `playbooks/new/create_minor_update.yml` |
| Explicit host scope and applicability guards | `playbooks/new/tasks/host_context.yml`, `playbooks/new/tasks/host_preflight.yml` |
| Minor CV and reuse of Test's exact version | `playbooks/new/create_minor_update.yml` |
| Targeted/full transactions and reboot | `playbooks/new/patch_hosts.yml` |
| Effective fix and service checks | `playbooks/new/tasks/check_final.yml` |
| Broader cutoff CV | `playbooks/new/publish_full_update.yml` |
| Exact major promotion | `playbooks/new/promote_content_view.yml` |
| Independent read-only verification | `playbooks/new/check_patch.yml` |

Snippet variables can be condensed explanatory examples rather than complete
ready-to-run playbooks. Consult the linked implementation for actual inputs,
repository/identity guards and returned evidence. This frontend does not change
automation or qualify a new AAP release.

## Verification

Prerequisites: existing Node.js 18+; no package installation. Local checks:

```sh
node --check demo/src/scenario.js
node --check demo/src/app.js
node --test demo/tests/*.test.cjs
git diff --check
```

Tests cover seven-scene navigation, green baseline and announcement timing,
targeted/bulk content, maintenance state, fixed catalog mapping, chronological
cutoffs, availability versus
installation, exact promotions, approval checkpoints, reboot/verification,
cumulative fixes, rewind/reset, real navigation handlers, deep links, motion and
source details. Interaction checks load actual HTML and execute its model and
handlers using a small DOM substitute. They do not establish real-browser
rendering, accessibility conformance or mobile layout. No browser executable was
available for this first implementation; no browser/tool was installed.

After publication, run the repeatable functional command against the actual site:

```sh
node demo/tests/live.cjs https://kvegh.github.io/RHEL-sniperpatching/
```

It downloads the four deployed assets with size/time limits, compares their bytes
with this checkout, and exercises the deployed scripts through the interaction
suite. It exits nonzero on missing/drifted assets or failed interactions. It uses
owned temporary files and cleans them afterward; no credentials, protected
inputs, test servers or live AAP state are used. This verifies deployed
JavaScript behavior, with the browser-rendering limits above.

For local browser review, open `demo/index.html` or serve the frontend with an
existing Python: `python3 -m http.server 8000 --directory demo`.

## GitHub Pages

`.github/workflows/deploy-demo.yml` uses GitHub Pages Actions, matching the other
demo repositories. Main pushes affecting the frontend run syntax/model/interaction
checks, then deploy only `index.html`, `src/scenario.js`, `src/app.js` and
`src/styles.css`, plus `.nojekyll`. Pull requests run checks only. Tests, playbooks,
documentation, inventories and protected files are excluded from the artifact.
The repository Pages source must be GitHub Actions. A successful push alone is
not a verified deployment; inspect the workflow and run the functional command.

Return to the [project README](../README.md) or [process diagram](../docs/process.md).
