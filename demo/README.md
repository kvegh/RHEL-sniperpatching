# Interactive RHEL sniperpatching mockup

[Open the visualization](https://kvegh.github.io/RHEL-sniperpatching/).

Version **0.15.3**. This browser-only explanation is for security staff, Linux
administrators and AAP administrators. It follows the checked-in NEW architecture
while grouping tasks and shortening operations for presentation. It is an
explanatory mockup: statuses, CV numbers and outcomes are illustrative. No host,
Satellite or AAP connection is made. Live automation acceptance remains documented
separately in the project README and handover.

## Present it

Use **Next**, **Back**, **Restart**, or select a workflow step. The two story
buttons open their fixed cycles; no CVE/date data entry is needed. At each
production checkpoint, **Approve Prod** advances to exact-version promotion.
The real playbooks still run as separately launched AAP stages; this page does
not add an automatic AAP approval node. Arrow keys navigate outside focused
controls; the right arrow stops at approval. R restarts. Workflow selection and
direct links are presentation navigation rather than security controls.

The architecture keeps AAP, Satellite, Test and Prod visible. Both platform
headers use a softer light blue with dark text; the redundant architecture
heading is removed, keeping the current phase indicator. The AAP card shows
its current action without the redundant Resolve/Patch/Verify badge row. Satellite serves
available CV content; separate AAP host jobs install and verify packages.
Purple identifies content, blue host execution and amber approval. Hosts pull
repository content from Satellite; content-flow arrows show package direction.
Promotion reuses the exact tested version and does not install packages.

Two user-selected stories run in chronological order:

| Story | CVE / RHSA | Illustrative full-update cutoff |
| --- | --- | --- |
| Python malicious package download | CVE-2024-6345 / RHSA-2024:5534 | 2024-08-23 |
| Network Privilege Escalation | CVE-2024-36883 / RHSA-2024:6567 | 2024-09-13 |

The first cutoff precedes the second advisory so the kernel example stays
outstanding. Kernel installation, reboot and effective verification are separate
stops; technical detail states that this is a local-user networking flaw.
Both cycles include targeted Test/Prod work, a broader cutoff publication,
full Test/Prod updates and an independent final check. Earlier fixes persist.
The illustrative CV sequence is 1.0 → 1.1 → 2.0 → 2.1 → 3.0; real jobs return
actual versions. Grouped full-update stops include any required reboot checks.

**Technical detail** shows condensed code and a source-pinned repository link.
URL fragments such as `#step=run-2-input` restore the matching state. Motion is
finite and can be disabled; reduced-motion preferences are respected. On small
screens the narrative stacks above the architecture and the host cards remain
side by side. Browser layout still requires visual verification.

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
| CVE to RHSA resolution | `playbooks/new/tasks/resolve.yml` |
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

Tests cover fixed catalog mapping, chronological cutoffs, availability versus
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
