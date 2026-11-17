# Interactive RHEL sniperpatching mockup

[Open the visualization](https://kvegh.github.io/RHEL-sniperpatching/).

Version **0.19.20**. This browser-only explanation is for security staff, Linux
administrators and AAP administrators. It follows the checked-in NEW architecture
while grouping tasks and shortening operations for presentation. It is an
explanatory mockup: statuses, CV numbers and outcomes are illustrative. No host,
Satellite or AAP connection is made. Live automation acceptance remains documented
separately in the project README and handover.

## Present it

Scene and optional action progress share one line: **SCENE 4 OF 7: Action 2 of 2**.
Single-action scenes show only the scene indicator, with no trailing separator.
The sidebar has a fixed responsive height: its explanation and scene list scroll
above a separate bottom control section. Back/Next are the lowest row, below
Restart/Motion, so changing text cannot shift them. No content is clipped; short
viewports may still require page scrolling. The redundant summary footnote is absent.
Both broader-update history entries read **All updates until date cutoff**;
the fixed scenario cutoff dates remain available in the technical explanation.

Use **Next**, **Back**, **Restart**, or select one of the **seven scenes**.
Run 01 and Run 02 open their healthy baseline before introducing a new CVE.
The examples and dates are fixed; there are no presenter-entered values.
The CVE is announced directly at the query action with a larger bold alert
heading. The alert copy simply identifies the CVE announced to AAP.
All six current CV readouts use a 650ms mechanical counter: the new version
descends from above as the old version exits below. Only actual value changes
animate; first render and unchanged values stay still. Motion off and reduced
motion show the latest value immediately. The visual old value is hidden from
assistive technology. Separate announcement and selected-pair-check stops are omitted;
publication leads directly to Test Server deployment.
The scene counter remains at 5 or 7 while the rollout's action counter advances.
At production checkpoints, **Approve Prod Server** continues to exact-version promotion.
Right-arrow navigation pauses there; Enter/Space on the button also approves.
The real automation still uses separately launched AAP stages rather than an
automatic approval node. Scene links are educational navigation, not access controls.

| Scene | What changes |
| --- | --- |
| 1. All systems up to date | Test Server and Prod Server meet the same defined baseline, with green checks. No future CVE appears. |
| 2. CVE announced | A named alert reaches AAP; Satellite resolves its security advisory. Only announced issues affect host status. |
| 3. Ensure fix content is available | AAP triggers the repository update, then one connected Download fix arrow delivers the selected fix/dependencies to Satellite. |
| 4. Publish targeted CV | AAP triggers CV composition and the baseline + fix equation appears. A separate publication action makes the minor available to Test Server without installing it. |
| 5. Apply selected fix | AAP launches CVE-scoped deployment; the host requests packages and Satellite responds. Test Server installs/reboots/verifies first, then approval and exact promotion precede the same Prod Server exchange. |
| 6. Routine patch window | Time passes; many security, bug-fix and enhancement updates arrive, retaining the already-applied fix in a broader CV. |
| 7. Apply broader updates | Fully update and verify Test Server, approve, promote its exact major, update/verify Prod Server and finish green. |

The compact status box sits beside the Red Hat software repositories on wider
screens, aligned with the workflow panel’s top edge and saving vertical space.
The minimum content-arrival reserve above AAP/Satellite is 24px. Red Hat
is shifted left by half the horizontal gap to the status box on wide screens.
Its single download arrow exits the right side and enters Satellite's top; native
rendered bounds and resize observation keep the endpoints attached as cards wrap.
The generic host-content caption reads **Satellite provides updates**.
The phase appears in the left workflow panel; the duplicate footer badge and
separate content-availability reminder are removed. Compact AAP and Satellite cards
are centered in equal halves. The latest refinement makes the server cards 20%
narrower with tighter padding and enlarges Satellite and Red Hat another 10%.
Narrow screens retain readable card widths; the Red Hat source stays above
Satellite with one continuous arrow. The top status/source panels stack on
screens up to 640px. The AAP-to-Satellite API arrow spans the gap between the
cards, carrying the current action label only when a named query/repository/CV
action applies. The generic HTTPS API label and arrow are absent. AAP is another
20% wider than the preceding revision; the connector fits its new gap. Solid
arrowheads use a narrower angle and stronger visibility while shafts stay
continuous throughout the animation. Arrow
labels are larger and bold across AAP, download and host routes. Generic Red Hat
content labels/arrows stay hidden when no download is happening. All action
connectors follow the Content View update arrow style: rounded
continuous shafts, matching solid acute heads and a same-color capsule highlight
without glow, blur or halo. All passes use the same one-second linear pace.
The API capsule is 18px long; SVG highlight length scales with its route. Every
animated arrow makes exactly three passes per activation, then its highlight
stops. This includes AAP actions, Red Hat downloads and host execution/content
routes in both directions. The API restarts for each named query/trigger action. Motion off and reduced motion hide highlights while retaining the shafts
and heads. API captions sit above the shaft; host captions wrap within the middle
half of the diagram, at least 8px above their horizontal lanes and away from
vertical stems. The route area is 96px high above 1100px viewport width,
128px through 1100px, and 168px through 540px. Its horizontal lanes sit at 36%
and 80%, with captions still 8px above the shafts. Platform padding, Satellite
content margins and host CV/fix/check gaps are tighter without reducing text size.
Platform footers stay at the bottom of their cards. The fixed-location refinement
reserves two sidebar title lines and a 225px narrative region, while preserving
the sidebar width. Hidden CV composition/publication details keep their layout
slots through visibility:hidden, without revealing future state. Server cards keep a fixed height while their fix list can scroll; baseline
content stays at the top. A
permanent vertical scrollbar gutter keeps the centered page origin steady. Approval controls reserve two text lines and stay in a separate bottom footer.
History uses fixed responsive slots; the normal-flow download fallback reserves
its largest list even when hidden. Existing checks cover behavior and source
consistency; browser-rendered positions and visual acceptance remain unverified.
The user declined browser installation. The page header now occupies the left grid column above the unchanged workflow
panel. The redundant product-name eyebrow is removed. The title and subtitle are
left-aligned as one block shifted left toward the page padding, with a single-line
subtitle on desktop. Small screens retain natural wrapping. On desktop the colored
status panel is centered horizontally in the left half
of the diagram, with a maximum width of 572px (30% wider than 440px) and a fixed 118px
height on wide screens; longer messages scroll inside it. Its distance from the site top equals its gap above AAP: the
centered margin box reserves the same 28px as the page's top inset and shares
additional row space equally. Width is capped to fit its half of the diagram.
Red Hat is centered over Satellite again, with room for its rightward
arrow exit and header links above. At widths through 850px the header, workflow
and architecture stack normally, and the status/source offsets reset. The
existing narrower top-row stacking is retained. Category labels form a vertical stack beside the download arrow in the gutter
outside Satellite, so they do not expand the architecture's source row. The
broader list keeps the green earlier-fix chip and five blue categories: Security
updates, Bug fixes, Enhancements, Libraries and Drivers. Targeted content keeps
its green selected-fix and purple dependency chips. On very narrow layouts the
list and Red Hat share a row in separate columns; where no side gutter fits,
the arrow clears that normal-flow list. The existing colors and motion controls
are retained. Download captions sit beside the
route, above the package list.
Host arrows show the client pulling from Satellite; package return and installation
share that action. The moving highlight reverses for a client request.
The Red Hat source lane delivers content to Satellite. One selected fix and its
dependencies are visually distinct from the later batch of maintenance updates.
Arrow highlights stop after three passes; category arrivals remain finite.
Both respect **Motion off** and reduced-motion preferences. The page makes no actual download or API request.

Satellite includes a visible definition: a Content View (CV) version is a
predefined snapshot of selected software repositories. This explains why the
same tested version can be promoted without changing its package contents.

The explicit AAP arrow labels are **Query: fix available?**, **Trigger software
repository update**, **Trigger Content View update**, and **Trigger publishing
updated Content View**. The equation **CV 1.0 + fix == CV 1.1** appears at CV
composition; only the next publication action highlights Test Server's newly available
CV. Installed packages and Prod Server availability stay unchanged at publication.
The second cycle uses the corresponding 2.0/2.1 equation. The deployment trigger does not install packages. The following client pull
and apply action combines the DNF request, Satellite response and installation
of selected advisory packages/dependencies; it has no separate return step. Intermediate kernel-installed/reboot-pending
and fixed-kernel-running stops are omitted.

These composition/publication actions and the repository trigger are explanatory
presentation stops rather than additional implemented AAP jobs or separate API
calls. The content-availability scene explains the content prerequisite: the targeted
playbook reads already synchronized repositories and does not launch a per-CVE
synchronization job. The full-publication playbook explicitly synchronizes the
selected repositories. Applicability checks apply to the configured Test Server/Prod Server
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

The first cutoff leaves the second advisory outstanding. Kernel updates include any required reboot in the same action; effective
verification follows separately. Technical detail
identifies a local-user Linux networking flaw. The second run retains the first
run's fixed packages and starts from its completed baseline. The illustrative
CV sequence is 1.0 → 1.1 → 2.0 → 2.1 → 3.0; actual jobs return their own versions.
Grouped full-update actions include any required reboot and independent final
checks. Forty-two presenter-controlled actions unfold within the seven scenes per
run; there is no autoplay or artificial waiting period.

**Technical detail** shows condensed code and a source-pinned repository link.
Legacy `#step=run-2-input` links open the query/announcement action; removed
`#step=run-2-host-scope` links open Test Server deployment; removed request
links open the combined pull-and-apply action; `#step=run-2-baseline`
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

### Fixed presentation geometry

Version 0.19.20 replaces minimum-only card reserves with fixed responsive heights.
Wide layouts use 224px AAP/Satellite cards and 282px server cards, using the user's
expanded-state screenshot as the size reference. Through the existing narrower
breakpoints the cards use larger fixed heights (300/340px and 400/440px), so text
can wrap. Platform bodies, status messages and host-fix lists scroll internally
when needed; headers, footers and host checks stay outside those scrollers.
The sidebar uses a viewport-based height clamped to 720–960px on desktop and
620–800px in the stacked layout. Minimum heights can exceed short viewports. Its content can scroll while footer controls remain at
the panel bottom. These are source-checked sizes, not browser-measured pixels;
rendered geometry and visual acceptance remain unverified. No browser is installed.
