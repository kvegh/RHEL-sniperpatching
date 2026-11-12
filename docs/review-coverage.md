# Baseline directive coverage and later policy additions

This is an **incomplete review inventory**, not an acceptance report. The original
static assessment below is preserved at its stated source/policy revisions.
Its baseline findings and pending-test wording are historical. See the
[current correction and verification evidence](review-2026-11-12.md),
[helper/caller inventory](implementation.md#source-and-caller-inventory) and
[APME dispositions](review-apme.md) for subsequent work. Line references in the
baseline matrix must not be treated as coordinates in the changed files.

The matrix inventories 280 directive groups, not 280 passing tests. The final
section separately accounts for 16 groups introduced by the newer policy.
Mandatory tool/runtime, private CaC and final AAP evidence remain incomplete.

## Preserved original assessment

This is a review evidence draft for the root reviewer. It is neither a task tracker nor a successful acceptance report. No final functionality confirmation is asserted.

## Baseline and evidence boundaries

- Local policy: Agent_generated_code_review revision e45b49b0de5231fbb580d828f2247161a7787863 (e45b49b), full README.md and TLDR.md.
- Upstream CoP: automation-good-practices revision fb5fcd6f03c544909dbad352a352b421c41d7203 (fb5fcd6). All thirteen section README.adoc files were read completely: 3,658 lines, including directive bullets, qualifications, rationale and examples. The upstream root introduction was also read.
- Reviewed project baseline: RHEL-sniperpatching commit 66e9554; functional version 0.5.7; functional implementation 2be30c742f946b6f9c1ad93a9b7efbe14e230953. Project line references below describe that baseline.
- Declared acceptance scope: the existing two-host RHEL 7.9 workshop pair, Ansible Core 2.15.11, Python 3.9.19 and redhat.satellite 3.14.0. Receiving AAP 2.7 evidence covers CaC import and the read-only runtime diagnostic; host SSH/patching from that receiver is not established.
- Historical results: two complete targeted/full-update cycles were recorded on 2026-11-05. They are historical evidence, not fresh checks of current host state or acceptance of later changes.
- Main-review update supplied by root: two flags have since been reproduced and corrected; 98-test validation remains pending. This reviewer has not inspected or verified those later edits. Baseline findings below must not be read as claims about the corrected artifact.
- This reviewer performed source/documentation reads only. No source, Git, Beads or remote mutations, installs or tests were performed. Writing this one draft is the sole authorized artifact mutation.
- No private Vault payloads or credential values were opened for this assessment. Actual private CaC, runtime, hosting and security evidence remains the owning reviewer's responsibility. The draft contains no endpoints, credentials or raw environment output.
- A fresh upstream-change check, exact runtime image digest, mandatory validators and final complete AAP workflow require the main reviewer's evidence. Reading a guide is not functional-test evidence.

## Status and grouping definition

Each ID below is one source-located directive group. A group may combine repeated statements, closely related bullets, rationale and examples concerning the same requirement. Separate instructions are identified within the row rather than counted as separate successful checks. Counts describe inventory groups, not independent tests, complete individual-tool coverage or a percentage compliance score.

- P — Static alignment: the read source supports the stated narrow property; execution and final acceptance are not implied.
- F — Concrete documentation gap at the reviewed baseline, suitable for a minimal correction.
- A — Accepted proportionate deviation under the local policy, subject to root recording the stated scope, rationale and remaining evidence. Acceptance of style/process deviation does not waive mandatory tests or unknown security conditions.
- N — Justified not applicable to the authored content or declared supported scope.
- E — Missing, unperformed or unavailable evidence. This is incomplete, not a clean result or an observed code defect.

For CoP rows, Source means <area>/README.adoc at fb5fcd6. Project evidence paths are relative to the reviewed repository at 66e9554. Local-policy rows refer to the policy README.md at e45b49b. F statuses are baseline findings; root must update their dispositions after validating the actual correction.

## 1. Automation structures

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| STR-01 | structures:15–34 | P/A | All Zen principles considered: Ansible is not Python; YAML/playbooks are not general programming; nonprogrammer usability; clarity, concision, simplicity, readability, useful outcomes, UX, automation, convention, declarative preference, focus, explainability and continuous improvement. Explicit stage playbooks, shared task components and pure filters are proportionate. Do not replace guarded structured filters with dense Jinja or new framework scaffolding. |
| STR-02 | structures:43 | F/A | Document the chosen responsibilities: playbook = explicitly launched operator stage; task file = shared component; filter = pure validation/transformation. README:227–238 already lists six stages. |
| STR-03 | structures:59–65,69–78,80–86 | A | The landscape/type/function/component hierarchy is an example, with reasoned exceptions expressly allowed. Independently launched workshop stages preserve owner-requested pauses. No numbered playbooks. Role conversion has no demonstrated reusable consumer. |

## 2. Naming conventions

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| NAM-01 | naming_conventions:12–13 | P/F | Descriptive sniper_* variables/filters, imperative task names, consistent action_noun.yml filenames and .yml extension are evident. The naming scheme is not documented in the baseline README. |
| NAM-02 | naming_conventions:17 | P | README:30–46 introduces RHSA, CVE and Content View concepts; standard RPM/API/AAP abbreviations are appropriate. |
| NAM-03 | naming_conventions:40 | A | Preserve owner-selected RHEL-sniperpatching. Policy:51–57 explicitly protects it; design_decisions_history.md:332 records the selection. |
| NAM-04 | naming_conventions:65 | A | Existing action-purpose filenames use underscores consistently. Preserve published playbook/CaC references rather than migrate to hyphens for a cosmetic benefit. This conflicts with coding_style:16 snake_case and :26–27 object_action guidance; record the selected action_noun convention. |
| NAM-05 | naming_conventions:66 | N | Optional pb_ prefix is unnecessary for seven clear entry points; no new prefix migration. |
| NAM-06 | naming_conventions:67 | P/A | vars/main.yml centrally holds a short project input set. Category-file splitting adds little value at this scale. |
| NAM-07 | naming_conventions:98 | E/A | Remote branch names and branch-lifetime practice are not established by local history. Do not invent hosted workflow evidence. |
| NAM-08 | naming_conventions:99 | A | Existing commit subjects are clear imperatives rather than conventional-commit prefixes. No automated changelog consumer is demonstrated; do not rewrite history. |
| NAM-09 | naming_conventions:135–136 | E/A | Existing AAP names are a documented presenter interface (README:84–86). Private CaC evidence must establish actual resource names; broad renaming risks deployed references. |
| NAM-10 | naming_conventions:140–148 | E/N/A | Account separately for organization, team, credential, project, inventory, JT, workflow, EE and schedule naming from the approved private definitions. Unused resource types are N; no resource is invented or automatically renamed. |

## 3. Roles

No roles are authored in this repository. Role-specific packaging/interface requirements are N; general safety, input validation, naming and repeat-operation expectations are separately applied to the project.

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| ROL-01 | roles:10,22,26 | N/P | No authored role functionality/interface. Equivalent stage outcomes are listed in README:229–238. |
| ROL-02 | roles:82 | N/P | No common role to create; shared tasks/context.yml, connect.yml, resolve.yml, proof.yml and other components already avoid duplication. |
| ROL-03 | roles:95 | N | Galaxy-compatible role skeleton requirement does not apply. |
| ROL-04 | roles:104–108 | N | No role distribution or Galaxy release. Project version is handled under Git coverage. |
| ROL-05 | roles:114 | N/P | No role arguments/defaults. Project names use sniper_* to isolate the public project namespace. |
| ROL-06 | roles:118 | N | No project-authored modules distributed inside roles. |
| ROL-07 | roles:120–126 | N/A | No role-local variables requiring __role_ prefix. Existing project runtime variables are intentionally read across task/play boundaries. |
| ROL-08 | roles:127 | N | No role tags. |
| ROL-09 | roles:128 | N | No authored role names; do not rename the owner-selected repository on this basis. |
| ROL-10 | roles:135–150 | N | No multi-provider role input, provider auto-detection or OS-default export. One selected Satellite/RHEL workshop is declared. |
| ROL-11 | roles:156–164 | N/A | Per-distribution/provider role vars/template layout is not applicable. Alternative OS branches do not establish tested support; do not introduce a platform matrix. |
| ROL-12 | roles:167–176 | N/A | No role collection to package. Adding collection architecture solely for this recommendation has no demonstrated distribution benefit. |
| ROL-13 | roles:182–184 | F/A | Document check-mode limitations. prepare_demo.yml:17–25, create_minor_update.yml:38–41, patch_hosts.yml:28–33 and publish_full_update.yml:17–21 reject mutation simulations. check_runtime.yml:9 skips its command under --check, leaving decoding without a report; document or safely correct that read-only path. Later root fixes are not verified here. |
| ROL-14 | roles:185–188,207 | E/A | Actual repeat-state/change evidence required where desired-state semantics apply. patch_hosts.yml:35–61 uses before/after RPM snapshots and computed package deltas; changed_when:false alone is not proof. Publication is an explicitly changing release action. |
| ROL-15 | roles:189–192 | P/F | Read-only registered host commands explicitly execute in check mode (tasks/host_preflight.yml:9–35, proof.yml:8–18, check_final.yml:10–16). Runtime-diagnostic check-mode limitation is covered above. |
| ROL-16 | roles:193–197 | N/A | No supported mutating-command dry run is offered; guards prevent simulated publication or patch success. Do not invent a dry-run guarantee. |
| ROL-17 | roles:198–201 | N/P | Native tools are prerequisites, not installed during normal jobs; README:76–79. |
| ROL-18 | roles:215–222 | N | Multiple-platform role use cases and fact-cache recommendations do not apply to the declared RHEL 7.9-only acceptance. |
| ROL-19 | roles:228–327 | N | No role platform variable fallback/loading hierarchy, deduplication or shared role-test variable interface. |
| ROL-20 | roles:333–369 | N | No first_found provider-task selection, default or skip scheme. |
| ROL-21 | roles:374–375 | N | No with_first_found usage to replace. |
| ROL-22 | roles:376–379 | N | No variable role includes requiring role_path anchoring. |
| ROL-23 | roles:380–383 | A | Existing fixed-key fact/dictionary dot access is not a demonstrated collision. Whole-tree style conversion is low value; prefer brackets for new ambiguous keys. |
| ROL-24 | roles:389–400 | N | No per-provider tasks/vars files or provider file-existence contract. |
| ROL-25 | roles:406 | N | No runtime managed configuration templates requiring ansible_managed comments. |
| ROL-26 | roles:408–409 | P/N | No changing date headers in managed configuration were observed. |
| ROL-27 | roles:410 | N | No runtime configuration-file replacement requiring unconditional backup:true. |
| ROL-28 | roles:411 | F | Document actual mutation scope and recovery limits; do not invent configuration replacement or transactional rollback claims. |
| ROL-29 | roles:413–419 | N | No nested-role variable filename lookup ambiguity. |
| ROL-30 | roles:425–426 | P/A | Static values generally centralized. Short reboot package-trigger list in patch_hosts.yml:86–88 is coherent decision logic; extracting it solely to add indirection is unnecessary. |
| ROL-31 | roles:427–429 | N/F | No role defaults interface; equivalent complete project inputs table should document vars/main.yml:1–25. |
| ROL-32 | roles:430–431 | N/A | No role-default-filter interface to migrate. Existing optional dictionary/runtime-result guards have a concrete purpose. |
| ROL-33 | roles:432–434 | P | Mandatory project inputs are empty until supplied and fail explicit assertions (tasks/connect.yml:2–22), rather than using dangerous fabricated defaults. |
| ROL-34 | roles:435–436 | N/A/F | Role vars/default precedence does not directly apply. Document central vars_files and protected/survey extra-var precedence instead of migrating architecture. |
| ROL-35 | roles:442 | N | No role examples requiring an FQ role name. |
| ROL-36 | roles:443 | P | Synthetic .example.test hosts are used; no real example endpoints are required. |
| ROL-37 | roles:451–452 | N/P | No authored role README; project README exists and explains purpose. |
| ROL-38 | roles:456–463 | N/F | Role-specific inbound/outbound args, capabilities, unit, outcome, rollback, idempotence and atomicity interface are N. Equivalent project input/output/repeat/recovery documentation is useful; do not claim atomic RPM rollback. |
| ROL-39 | roles:475 | P/N | No externally imposed role group; internal sniper_targets contains only the selected existing host (tasks/host_context.yml:36–49). |
| ROL-40 | roles:516 | A | Included-file name prefixes absent, but these are not roles; task names are descriptive and native verbose logs expose paths. Record the corresponding local naming deviation; broad cosmetic edits add churn. |
| ROL-41 | roles:538–546 | N/P | No role argument_specs. Project assertions and filters already validate mandatory inputs and metadata. |
| ROL-42 | roles:583–586 | N | Contextual references provide inspiration, not additional independent implementation directives. |

## 4. Collections

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| COL-01 | collections:8 | N | No authored collection to package at type/landscape level. |
| COL-02 | collections:17–24 | N | No implicit collection defaults or reusable role collision interface. |
| COL-03 | collections:56–59 | N | Collection README/purpose/license/runtime/library requirements are N; project documentation is assessed independently. |
| COL-04 | collections:62–63 | N/F | No generated collection doc/rst layout. User-facing local filter API documentation remains required under plugins:16. |
| COL-05 | collections:73–76 | N | No collection LICENSE/COPYING or differing-file license decision to make. Do not choose legal terms for the owner. |

## 5. Playbooks

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| PLB-01 | playbooks:6–12 | A | Shared task-file architecture is proportionate for independently launched workshop stages; no demonstrated role consumer justifies a broad conversion. |
| PLB-02 | playbooks:37–41 | P | Plays use tasks without mixed roles/tasks execution sections. |
| PLB-03 | playbooks:47,49–50,52,54 | N/P | No tags create unsupported partial/destructive combinations. Explicit stage entry points are documented in README:229–238. |
| PLB-04 | playbooks:147–151 | A | Visible outcome reports are presenter outputs and next-stage inputs, not incidental debug chatter: create_minor_update.yml:241–251, publish_full_update.yml:171–176, tasks/check_final.yml:31–39, patch_hosts.yml:116–120. |

## 6. Inventories and variables

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| INV-01 | inventories:7–11 | P/F | SSOTs are separated: protected AAP inventory/inputs for desired targeting; Satellite for current CV/repository/host/advisory metadata. Evidence: tasks/context.yml:42–58, host_context.yml:24–49, resolve.yml. Document the boundary explicitly. |
| INV-02 | inventories:19–23 | P/N | Technical Satellite source is used. No CMDB/cloud source is assumed. Static demonstration-pair selection does not justify adding a dynamic inventory system. |
| INV-03 | inventories:33–44,50–55 | P | Desired patch/cutoff/stage inputs are separate from discovered content metadata and installed proof. No as-is/to-be conflation established. |
| INV-04 | inventories:64–86 | A | A single synthetic file inside inventory/ is sufficient for two example hosts. Full host_vars/group_vars expansion adds little value now. |
| INV-05 | inventories:67–72 | N | Unused dynamic plugins/scripts and host/group var components are not requirements to implement. Do not add a legacy script merely because an example lists it. |
| INV-06 | inventories:127,135–136 | A/P | inventory/example.ini contains two synthetic rows and a generic inline ansible_user. Splitting variables offers negligible benefit at this scale; both example hosts are listed under all. |
| INV-07 | inventories:140–142 | N | No role-driven public inventory requiring role-named files or reserved ansible.yml. |
| INV-08 | inventories:166–183 | P/A | Actual patch/check work runs via native hosts:sniper_targets. Preparation's two-host Satellite assignment loop is the deliberate exact-pair safety boundary, not a generic sequential provisioning engine. |
| INV-09 | inventories:257 | N | No generic host-list provisioning workaround is needed. |
| INV-10 | inventories:264–265 | A | vars_files:vars/main.yml intentionally centralizes inputs for independent stages. Inventory-only migration risks existing interfaces/CaC for little benefit. |
| INV-11 | inventories:266–267 | P/A | Scoped/runtime values serve loops and derived metadata; set_fact supports ordered tasks and final localhost readback. |
| INV-12 | inventories:277 | N | No authored role defaults. |
| INV-13 | inventories:278–280 | P | Desired inputs and discovered facts remain distinct; no native fact-name reuse established. |
| INV-14 | inventories:281 | N/F | Role constants guidance is N; document project input/default precedence. |
| INV-15 | inventories:282–285 | A/F | Consistent sniper_* runtime/scoped names are used. Document highest-precedence protected/survey extra vars; this is not a sandbox against privileged overrides. |
| INV-16 | inventories:302–304 | A | Advisory/date/stage surveys intentionally supply per-launch operator choices; connection/pair/repository identity remains protected configuration. Inventory-only desired-state advice must not erase explicit demo controls. |
| INV-17 | inventories:311–315 | N | VM sizing, destructive-reset confirmations and no_log-uncover examples do not authorize adding reset/debug interfaces. |

## 7. Plugins

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| PLG-01 | plugins:7 | E | Applicable Ansible module/development documentation review for the exact runtime belongs to main baseline evidence; CoP reading alone does not prove that linked-document assessment. |
| PLG-02 | plugins:8 | E | Source readability is reasonable, but supporting Python checks must run before claiming comprehensive PEP8 alignment. |
| PLG-03 | plugins:9 | F | Intent docstrings exist, but supporting-code explanation links are missing from all four Python implementation headers and execution points. Add short reason/link comments. |
| PLG-04 | plugins:16 | F | Both FilterModule exports lack complete public parameter/output/example documentation: twelve content filters and seven sniper filters. Add a compact interface table and useful examples. |
| PLG-05 | plugins:25–28 | A/F | Public interface docs and non-obvious intent comments are worthwhile. Exhaustive reST boilerplate for every small private helper adds repetition; record that narrow deviation. |
| PLG-06 | plugins:50–52 | A | Host proof must preserve Python 2.7 syntax. Controller-side Python3 helpers are readable without a wholesale typing migration; revisit on substantial interface/runtime changes. |
| PLG-07 | plugins:67–70 | A | Retain stdlib unittest: ten meaningful suites already exercise contracts, invalid inputs and synthetic actual Ansible executions. Pytest migration adds churn/dependency without demonstrated functional benefit. |
| PLG-08 | plugins:107–112 | N | No runtime project-authored module argspec. Generated synthetic module argspecs are isolated test fixtures, not the supported collection API. |
| PLG-09 | plugins:125–130 | A | Cohesive 259/312-line local filters and 328-line host proof are manageable. New plugin_utils/module_utils/collection packaging would add indirection without a demonstrated shared consumer. |
| PLG-10 | plugins:138 | A | Existing small FilterModule entry points do not benefit from retrospective plugin-builder scaffolding. |
| PLG-11 | plugins:146–149 | P | Errors identify epoch ambiguity, invalid identity, foreign ownership/provenance and malformed requirements; content.py:8–41,96–107,180–240; sniper.py:98–109,226–250. |
| PLG-12 | plugins:151,155 | N/P | Extra logging is unnecessary: helpers raise actionable errors and playbooks present the outcomes. |
| PLG-13 | plugins:153 | N/P | No authored Ansible module requiring AnsibleModule helpers. Host proof is an explicit JSON CLI; malformed/runtime failure exits2 (rpm_proof.py:306–324), and callers assert verified after patching. |

## 8. Coding style

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| COD-01 | coding_style:16 | P/A/F | Variables/Python files use snake_case; document the scheme. Preserve owner repo name and existing filename convention despite contradictory generic advice. |
| COD-02 | coding_style:17 | P | Variable identifiers have no special characters; external JSON/API keys retain their real schema. |
| COD-03 | coding_style:26–28 | P/A | Names are descriptive. Existing action_noun filename order differs from object_action example; preserve interfaces and explain the choice. |
| COD-04 | coding_style:29 | P | No numbered role/playbook names. |
| COD-05 | coding_style:30 | P/E | Reviewed runtime plays/tasks/blocks have descriptive names. Main strict discovery/lint must account for complete Ansible and generated-fixture coverage. |
| COD-06 | coding_style:31 | P | Imperative task names use Validate, Read, Require, Record, Promote and Verify. |
| COD-07 | coding_style:32 | P | Standard RHSA/CVE/RPM/API/AAP abbreviations are appropriate; README introduces concepts. |
| COD-08 | coding_style:36 | P | Runtime YAML uses two-space indentation. |
| COD-09 | coding_style:37 | P/E | Lists generally follow the recommended indentation; complete lint evidence remains required. |
| COD-10 | coding_style:62 | P | Long runtime expressions are folded/wrapped for readability. |
| COD-11 | coding_style:66–68 | E | Record the actual installed lint line-length rule and findings. Historical numeric examples are not target-runtime specifications; no blanket skip is justified. |
| COD-12 | coding_style:88–90 | P | Folded expressions use >-; no accidental trailing-newline input was identified. |
| COD-13 | coding_style:94–99 | P/A | Many long conjunctions use condition lists. Short readable expressions do not need mechanical conversion. |
| COD-14 | coding_style:117 | E | Exact baseline syntax checks for all entry points remain main-review evidence. |
| COD-15 | coding_style:118 | P | Structured YAML module arguments and command argv; no key=value task bodies observed. |
| COD-16 | coding_style:140 | P | Runtime YAML uses true/false; Python booleans inside generated test code are appropriate Python. |
| COD-17 | coding_style:149–154 | P | Positive proof/flag names; no harmful double-negative interface identified. |
| COD-18 | coding_style:157–159 | P/F | Task names explain routine actions. Significant custom/command reasons require concise linked comments under the stronger local policy. |
| COD-19 | coding_style:160–162 | P | Spacing around template delimiters is consistent. |
| COD-20 | coding_style:163–164 | P | .yml is used for playbooks/tasks/vars/dependency manifests. |
| COD-21 | coding_style:165 | A | Existing readable quote mix is stylistic; mass scalar conversion provides no functional benefit. |
| COD-22 | coding_style:166–167 | A | Preserve readable user strings and keyword literals. Whole-tree quoting migration adds churn; lint findings need separate evidence. |
| COD-23 | coding_style:168–169 | P | JSON surveys are AAP's native format and a justified structured-data exception. |
| COD-24 | coding_style:170–175 | N | No lengthy Jinja configuration templates to split. |
| COD-25 | coding_style:177–183 | P | Structured parsing, epochs and provenance are handled by pure Python filters instead of dense Jinja programming. |
| COD-26 | coding_style:186–197 | N | No intentionally literal third-party {{...}} configuration requiring !unsafe was observed. Do not add tags indiscriminately to intentional expressions. |
| COD-27 | coding_style:225–234 | P/A | Task modules use FQCNs. Project-local filters use registered short names; collection migration solely to invent FQCNs is disproportionate. |
| COD-28 | coding_style:263 | E/A | Actual idempotence requires state/readback evidence. Explicit fresh CV publication is a changing release action; document its exact repeat semantics. |
| COD-29 | coding_style:264 | P/A | Lazy input evaluation retained; runtime-derived facts have concrete ordering and final-readback purposes. |
| COD-30 | coding_style:265–268 | P/A | No shell tasks observed. Commands use argv where exact native tooling is required. Document native-module gaps instead of removing commands categorically. |
| COD-31 | coding_style:269 | F | Required justification comments/links are absent at command execution points. |
| COD-32 | coding_style:270 | A | Some derived boolean facts are bare, e.g. preparation initialization. They are computed booleans; no wrong truthiness established. Record a narrow style deviation unless a targeted cheap correction is warranted. |
| COD-33 | coding_style:271–278 | P/A | Shared files split coherent concerns. Larger publish/validate/promote/recovery blocks preserve a clear lifecycle; no speculative role/framework split. |
| COD-34 | coding_style:280–286 | A | Fixed-key dictionary dot access is common; no demonstrated collision. Whole-tree rewrite has low benefit; use brackets for changed/new ambiguous keys. |
| COD-35 | coding_style:292–297 | P | No meta:end_play usage observed. |
| COD-36 | coding_style:300–310 | P/N | No observed dynamic task-name expression in the middle requiring repair; preserve useful static names. |
| COD-37 | coding_style:332 | P | Play names are static. |
| COD-38 | coding_style:333–334 | P | No observed loop-item task-name reliance; useful loop_control labels are present. |
| COD-39 | coding_style:335–341 | P | Derived runtime names preserve the input's purpose. A general dislike of set_fact is not evidence of an overwritten-input defect. |
| COD-40 | coding_style:344–346 | A | Runtime facts support subsequent tasks and cross-play completion checks (patch_hosts.yml:122–148, check_patch.yml:31–54); scoped-only migration would complicate proof readback. |
| COD-41 | coding_style:347–348 | P | No blanket ignore_errors observed; expected return codes are bounded explicitly and failures remain visible. |
| COD-42 | coding_style:349–364 | N/A | Advice targets ancient EL7 control-node Jinja. Selected AAP EE/core2.15 is not that control-node platform; managed RHEL7 does not require replacing supported equality tests with regexes. |
| COD-43 | coding_style:385 | P | Validated ID/metadata regexes are anchored; exact search terms are bounded and validated. |
| COD-44 | coding_style:388–389 | N | No when:result is changed handler chain. Immediate conditional reboot must complete before proof; no managed-config notification use case. |
| COD-45 | coding_style:390–400 | P | Native imports/includes share context/connect/resolve/proof/smoke/preflight components. |
| COD-46 | coding_style:402–403 | P | No package-per-item install loop; selected advisory set is handled in a package-manager transaction. |
| COD-47 | coding_style:404–414 | A | Generic-module preference is qualified by :452–454. Exact advisory/repository controls need chosen native tools; no new portability requirement. |
| COD-48 | coding_style:416–427 | N | No runtime lineinfile use or configuration-edit concern to repair. |
| COD-49 | coding_style:430–432 | P/N | No runtime configuration file push to convert. Synthetic test-result copy is appropriate generated data; do not template fixtures for hypothetical future use. |
| COD-50 | coding_style:433–441 | N | No authored configuration template requiring .j2. |
| COD-51 | coding_style:443–449 | N | No destination-file template hierarchy to reshape. |
| COD-52 | coding_style:452–454 | P/A | Specific yum/dnf behavior is justified by exact advisory and repository requirements. Native reboot/service_facts are used where suitable. |
| COD-53 | coding_style:456–470 | P/E | Numeric comparisons commonly cast int and flags bool; complete test/lint coverage remains main-review evidence. |
| COD-54 | coding_style:473–475 | P/E | Reviewed arithmetic/comparisons normalize inputs. No unsupported unary-arithmetic defect identified; comprehensive runtime verification remains pending. |
| COD-55 | coding_style:497–499 | P | Expressions are wrapped; conditions use native expressions without unnecessary outer template markers. |
| COD-56 | coding_style:501–503 | P | Long assignments are wrapped/moved for readability; no mechanical rewrite needed. |
| COD-57 | coding_style:505–508 | N/P | No long literal URL needing backslash escaping was identified; API URLs are intentionally composed Jinja expressions. |

## 9. AAP configuration as code

Private configuration was not opened; E must be resolved with sanitized evidence from its owner.

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| AAP-01 | aap_configuration:10 | E | Account for required organizations, teams, credentials, projects, inventories, JTs, workflows, EEs, schedules, settings and relationships using the approved companion. README:325 identifies existing shared importer/explicit destination. |
| AAP-02 | aap_configuration:11,16 | E | Source/readback alignment is required to assess drift and UI changes; import success alone does not establish it. |
| AAP-03 | aap_configuration:25 | E | Exact configuration collection version needed; illustrative2.9.0 is not a requirement to change the selected baseline. |
| AAP-04 | aap_configuration:39–43,50–57 | E/A | Verify native dispatch/order and compatibility in the existing shared importer. Preserve approved importer/schema; do not add a wrapper/second importer or migrate architecture for an example. |
| AAP-05 | aap_configuration:63–70 | E/N | Verify applicable dependency order. Unused object types are N, not objects to fabricate. |
| AAP-06 | aap_configuration:77–78 | E/A | Existing owner-selected environment/group-var schema may be retained with reason; verify loader behavior instead of wholesale reshaping. |
| AAP-07 | aap_configuration:125 | E | Shared credentials/inventories/schedules/teams/orgs/labels must not be duplicated inconsistently; private evidence needed. |
| AAP-08 | aap_configuration:126 | E/A | Existing schema must reproducibly capture coupled EE/project/JT references; exact JT-bundle file layout is optional if relationships are coherent. |
| AAP-09 | aap_configuration:187 | P/E | Public source holds no credential values observed; private ciphertext assessment is separate. |
| AAP-10 | aap_configuration:188 | P/E | vars/main.yml:7–10 uses env lookup; whole-file Vault companion described README:325. Actual encryption/key storage must be checked privately. |
| AAP-11 | aap_configuration:220–225 | E | Exact configuration collection pin is not visible in this public project; owning importer baseline needed. |
| AAP-12 | aap_configuration:251–252 | E | Repeated apply and actual resource readback required; successful first import is insufficient. |
| AAP-13 | aap_configuration:253 | E | Authorized production check/diff preview requires actual evidence; no remote launch in this fix phase. |
| AAP-14 | aap_configuration:281–285 | A/E | Public CI-triggered CaC pipeline absent. Manual explicit workshop import may be accepted as a documented process deviation, not called pipeline PASS. |

## 10. Git workflow and versioning

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| GIT-01 | git_workflow:10 | E | Local linear history does not establish hosted/default branch configuration. |
| GIT-02 | git_workflow:11 | A/E | No PR/CI review evidence supplied. Manual maintainer workshop workflow can be a proportionate process deviation; do not invent approving reviews. |
| GIT-03 | git_workflow:12,18 | E | Remote environment branches and actual immutable promotion references require evidence. |
| GIT-04 | git_workflow:44–46 | E/A | Branch lifetime and PR size not established. Do not create feature flags merely to imitate an example. |
| GIT-05 | git_workflow:75–78 | P | Numeric SemVer VERSION/README0.5.7; no CalVer migration needed. |
| GIT-06 | git_workflow:108 | N | No CalVer collection or PEP440 release interface. |
| GIT-07 | git_workflow:115 | E | Hosted tag immutability cannot be proven by local inspection alone; never rewrite existing refs. |
| GIT-08 | git_workflow:116 | A/E | Local tag listing returned none. Exact implementation commits exist; establish future annotated release practice if worthwhile rather than invent historical tags. |
| GIT-09 | git_workflow:150–155 | N | Same-day CalVer examples do not replace the project's numeric version scheme. |
| GIT-10 | git_workflow:163–164 | P/E | Satellite minor/full exact-version reuse is explicit (create_minor_update.yml:151–178; promote_content_view.yml:17–62). Source/CaC/EE artifact equality requires separate immutable references. |
| GIT-11 | git_workflow:190 | E | Actual project SCM/image references and digest require private readback. Workshop Prod label is not proof of enterprise release governance. |
| GIT-12 | git_workflow:225 | A | Independent upstream dependencies cannot share project0.5.7. Record one coherent exact source/CaC/EE/core/Python/collection baseline rather than force unrelated version numbers to match. |
| GIT-13 | git_workflow:254 | E | Hosted branch protection unknown; no access-control changes authorized by this assessment. |
| GIT-14 | git_workflow:256 | E | No-direct-main-commit enforcement is not established. |
| GIT-15 | git_workflow:257 | E | Approving-review protection not established; independent agents are not human approvers. |
| GIT-16 | git_workflow:258 | E | CI checks absent/unverified; manual lint/tests are distinct evidence. |
| GIT-17 | git_workflow:259 | E | Hosted force-push/deletion controls unknown. |
| GIT-18 | git_workflow:286 | A/F | Design history records real implementation commits; no CHANGELOG/tags evidenced. No history rewrite; add prominent migration notes if a fix actually breaks an interface. |

## 11. Testing

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| TST-01 | testing:10–11 | P/E | Existing offline suites support fast-to-slow verification. Actual command outcomes belong to the main review; this reviewer ran none. |
| TST-02 | testing:28 | E | Exact target-core syntax/YAML/strict lint and real dependency coverage required. |
| TST-03 | testing:29 | P/A/N | Unit tests exist; retain unittest. Molecule role tests N because no authored role. |
| TST-04 | testing:30 | E | Final AAP end-to-end follows correction, restarted full review and artifact freeze. |
| TST-05 | testing:37 | E | Current strict production lint required; historical decision-history results are not the current run. |
| TST-06 | testing:38 | A | No tracked precommit/CI automation. Record manual gate and future-bypass risk. |
| TST-07 | testing:54–55 | A | Local policy:426–431 forbids blanket ignores; illustrative generate-ignore does not override it. |
| TST-08 | testing:63–69 | N | No role Molecule/container lifecycle. Synthetic actual-Ansible fixtures plus real AAP workflow are proportionate project verification. |
| TST-09 | testing:134–139 | N | RHEL7.9-only declared acceptance. RHEL8/9 branches are unverified, not proven incompatible or newly supported. |
| TST-10 | testing:164 | P/A/E | Local filters and RPM proof have meaningful unittest contracts; actual results remain root-owned. |
| TST-11 | testing:165 | P/E | Isolated temporary fixtures/synthetic inputs and meaningful assertions exercise behavior. Generated local collection modules are test doubles, not remote jobs; test execution still required. |
| TST-12 | testing:209–211 | E/A | Verify repeat desired-state/recovery operations and host readback. Intentional fresh publication needs explicit repeat semantics, not fictitious zero-change proof. |
| TST-13 | testing:236–240 | P | Descriptive test names identify expected behavior, e.g. tests/test_runtime.py:16,30; test_dynamic_resolution.py:108,121; test_sniper.py:85. |

## 12. CI/CD and promotion

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| CIC-01 | cicd_and_promotion:10 | A | No tracked precommit configuration. Manual workshop checks can be accepted with documented bypass risk/revisit condition. |
| CIC-02 | cicd_and_promotion:11 | E/A | Actual syntax/lint/secrets/format results mandatory; automatic integration absent. |
| CIC-03 | cicd_and_promotion:37–42 | E/A | YAML/Ansible/secret checks require evidence; whitespace/EOF may use existing equivalent checks. Do not add redundant tooling without benefit. |
| CIC-04 | cicd_and_promotion:50–55 | A/E | No CI workflow or authoritative non-bypass gate evidenced. Record missing governance layer honestly. |
| CIC-05 | cicd_and_promotion:79–80 | N/E | No pipeline to optimize with cache/matrix. Measure actual local/AAP timings; no speculative framework. |
| CIC-06 | cicd_and_promotion:116–117 | P/E | Offline tests require no production secrets; release/import is separate authorized action. No configured pipeline claimed. |
| CIC-07 | cicd_and_promotion:121–124 | E | Actual private credential/privilege separation requires evidence; no permissions changed to make tests pass. |
| CIC-08 | cicd_and_promotion:142 | P/A | Explicit human gates between standalone stages: README:84–86,186–188. This is not an enterprise Dev/QA/Prod pipeline implementation. |
| CIC-09 | cicd_and_promotion:144 | E/N | Actual mandatory static/unit results required; Molecule N. |
| CIC-10 | cicd_and_promotion:145 | A | No separate QA-lead organization in owner workshop; record agent review as agent assessment, not human QA signoff. |
| CIC-11 | cicd_and_promotion:146 | A/E | Enterprise CAB/QA structure outside workshop; exact user authority, security disposition, recovery and final AAP acceptance still required. |
| CIC-12 | cicd_and_promotion:181–187 | A | Automated PR size/title/changed-file/docs/conflict checks disproportionate to small maintainer workflow. Focused commits and manual staged/docs review remain necessary; revisit with contributors/CI/scale. |
| CIC-13 | cicd_and_promotion:215 | F/E | Final evidence must bind exact source/CaC/secrets refs, EE digest and dependencies. A separate release-manifest framework/service is unnecessary if the report provides that immutable baseline. |
| CIC-14 | cicd_and_promotion:255 | F/A | Document stop/inspect retained candidate and only proven minor recovery. Code/CaC revert does not downgrade RPMs; snapshot rollback remains on hold. No new destructive reset implementation. |
| CIC-15 | cicd_and_promotion:266–275 | N | Rollback examples do not authorize moving/deleting tags or host rollback. |

## 13. Security

| ID | Source | Disposition | Evidence and reason |
|---|---|---|---|
| SEC-01 | security:10–11 | P/E | Manual public-source review observed generic examples/env references, no plaintext secret. Complete code/history scan evidence still required. |
| SEC-02 | security:15 | P/E | Whole-file Vault companion documented README:325; actual encryption/key audit private. Never copy ciphertext/keys to public source. |
| SEC-03 | security:16 | P | vars/main.yml:7–10 uses builtin env lookup for Satellite access. |
| SEC-04 | security:17 | N | No additional secret-manager integration required by chosen architecture. |
| SEC-05 | security:18 | E | Actual AAP credential bindings/external access values require private readback. |
| SEC-06 | security:58 | E | Current-code automated secret detection completion required. |
| SEC-07 | security:60 | E | detect-secrets is an example; selected equivalent scanner must show actual coverage/findings. |
| SEC-08 | security:61 | E | Git-history scanner/Gitleaks completion, source scope and findings required; exit status without coverage is insufficient. |
| SEC-09 | security:63 | A/E | No CI merge-block gate configured/evidenced; process gap cannot be called an automated PASS. |
| SEC-10 | security:91–97 | E | Hosted push protection unknown. GitHub/GitLab are alternatives, not both required. No organization settings changed here. |
| SEC-11 | security:119 | P/E | Code boundaries visible: tasks/connect.yml:12–22 exact namespace/pair and :41–43 ownership; host_context.yml:36–49 selected existing consumer; no forced promotion. Actual least-privilege accounts/RBAC unverified. |
| SEC-12 | security:121 | P/E | Offline fixtures need no production secrets; no actual CI access configuration claimed. |
| SEC-13 | security:122 | E | Private deployment credential destination scope unverified. |
| SEC-14 | security:123 | E | AAP account/org/resource grants unknown; no permission expansion authorized. |
| SEC-15 | security:145–148 | P/E | Public automation references protected inputs. Actual Machine/SCM/Satellite/Vault storage and bindings require separate private evidence. |
| SEC-16 | security:179–180 | F/E | Document external owner rotation/revocation procedure. Rotation is not implemented or authorized merely by this assessment. |
| SEC-17 | security:189–198 | A/E | Suggested intervals must be reconciled with owner's selected policy; do not impose/change keys/passwords to satisfy an example. |
| SEC-18 | security:206 | E | Immutable actual EE scan/vendor evidence required. No custom EE authored, but inherited images are not automatically clean. |
| SEC-19 | security:207 | N/E | Scanner brand is optional; use approved existing coverage and record completion. |
| SEC-20 | security:208 | E | Image/component SBOM or explicit unresolved/owner-authorized limitation needed; no SBOM generation claimed. |
| SEC-21 | security:210 | E | Select environment severity policy and disposition actual findings. |
| SEC-22 | security:231–233 | E/N | Actual selected dependency-audit completion required. Do not invent a separate Python requirements set: helpers use stdlib plus required Ansible/PyYAML/native rpm. |
| SEC-23 | security:236–243 | A/E | Stage-threshold examples do not authorize ignoring real security failures. Workshop-only limitations must be explicit. |
| SEC-24 | security:251–257 | P/E | Public history records implementations/reasons; exact private CaC/readback alignment required. No assumption that manual drift is absent. |
| SEC-25 | security:278–279 | N/E | Enterprise multi-environment network segmentation not implemented by patch-demo source; explicitly unassessed. No network/firewall/AAP-org change authorized. |
| SEC-26 | security:290–293 | N | Listed infrastructure segmentation mechanisms are alternatives, not requirements to implement all. |
| SEC-27 | security:300–305 | F/E | Document external ownership/cadence for service-account permissions, stale credentials, pipeline trigger access and AAP RBAC; actual audits remain unknown. |
| SEC-28 | security:317–322 | A/E | Cadences are guidance; use selected operator policy/evidence. No background schedules added. |

## 14. Full local-policy accounting

| ID | Policy README.md source | Disposition | Evidence and reason |
|---|---|---|---|
| POL-01 | 15–25,27–43 | P/E | All13CoP sections read in full, including bullets/rationale/examples; map above. Fresh upstream-change confirmation main-owned. |
| POL-02 | 45–57 | P | Distinguish static alignment from N/A/deviation/gap/evidence. Explicit owner names/runtime override incompatible generic advice. |
| POL-03 | 59–81 | P | No manufactured functional/security finding. Demonstrable documentation omissions and missing evidence only in this scope; tool leads require actual code/runtime validation. |
| POL-04 | 83–111 | P/A | Proportionate dispositions listed below with benefit/effort/risk/revisit. Mandatory functionality and security evidence are not waived. |
| POL-05 | 113–131 | P/E | Scope matches README:48–72 and owner selection; no universal platform requirement. Receiving AAP host SSH remains unproven; final scope tests pending. |
| POL-06 | 135–152 | E | Release-matched Red Hat Develop/Secure procedures, edition and runtime differences need exact main-review evidence; CoP reading alone does not establish it. |
| POL-07 | 154–160 | E | Select applicable CIS product/version/profile/controls and code implications. Generic code scan cannot certify hosts; no hardening/access changes authorized. |
| POL-08 | 162–169 | N | Optional OpenSCAP/NIST/STIG only where selected; no arbitrary framework expansion. |
| POL-09 | 174–184 | P/E | Owner-selected workshop baseline documented current_status_for_handover.md:30–34. Actual EE digest/installed baseline and checks still needed. Do not silently substitute Satellite6/core2.16+, latest core or a new EE. |
| POL-10 | 186–192 | E/P | No deprecation setting disabled in ansible.cfg; actual native/lint/AAP warning investigation required. interpreter auto_silent is not blanket deprecation suppression. |
| POL-11 | 196–207 | P/E | Coherent/readable source assessment; independent agents/scopes/disagreements should be recorded. No human verification or functional proof claimed from consensus. |
| POL-12 | 211–237 | F/A/E | Naming scheme absent in baseline README; current sniper/action/imperative conventions evident. Preserve public interfaces and document deviations; actual APME naming-rule coverage required. |
| POL-13 | 239–248 | P/F | Shared files and guards serve real observed failures; avoid speculative refactoring. Add concise reasons for custom/native code gaps. |
| POL-14 | 252–260 | P/E/F | Certified Satellite content predominates; exact3.14 in dependencies/satellite.yml. Actual support/interface/PAH evidence main-owned. Incremental URI gap in design_decisions_history.md:305–309, but linked execution-point rationale missing. |
| POL-15 | 262–265 | N | No runtime MCP dependency required. Do not add MCP into playbooks merely because agent platform operations can use it. |
| POL-16 | 269–278 | F | Purpose-specific rationale needed for filters, RPM proof, runtime diagnostic, native commands, incremental URI and synthetic test code: alternatives, dependencies, limits and verification. |
| POL-17 | 280–294 | F | Required reason/document links missing at all four Python headers and relevant command/URI/filter execution points; verify anchors after root's batch. |
| POL-18 | 298–305 | E/A/F | Repeat-state proof pending; publication intentionally creates a fresh artifact. Document mutation check-mode limits/read-only behavior and diagnostic limitation. |
| POL-19 | 307–314 | P/E | Minor125–136 waits and checks state/result; :188–240 validates before promotion. Publication130–136 retries only read inspection, not mutation. Actual recovery outcomes need test evidence; retain ambiguous/failed candidates. |
| POL-20 | 318–334 | P/E | No private values observed in public inputs; TLS true, credential POST no_log/netrc disabled/no redirects, command argv, exact ownership/target boundaries. Full scan/RBAC/rotation/provenance/image evidence pending. |
| POL-21 | 338–354 | P/E/N | Exact dependency declared, no vendored installed collection/archive observed. PAH provenance/availability pending. No authored collection requiring its own release system. |
| POL-22 | 358–366 | P/E | Actual AAP templates/surveys/credentials/limits/SCM/RBAC/concurrency/timeouts/EE readback pending. README:80 empty-limit rule and final host assertions are static evidence, not receiver host readiness. |
| POL-23 | 368–382 | N/P | No new custom EE justified/authored; no job-time interactive dependency installation observed. No need invent build architecture. |
| POL-24 | 386–401 | E/A | Private CaC completeness/bootstrap/import order/restoration/reapply/no implicit jobs pending. Preserve companion/shared importer; no repository consolidation. |
| POL-25 | 405–415 | P/E | Historical stage timings README:108–112; fresh equivalent AAP timings needed. No speculative concurrency or safety-check removal. |
| POL-26 | 419–431 | E | Current strict lint across all content, exact target core/real dependencies/discovery/exclusions and supporting-language checks required. No blanket ignore/skip introduced. |
| POL-27 | 434–459 | E | Record APME version/core/policy/rule revision, enabled/required backend health/completion/findings. Native,OPA,Ansible,Gitleaks,CollectionHealth,DependencyAudit each actually completed/skipped/failed; missing coverage is not clean. No installs by this reviewer. |
| POL-28 | 463–472 | P/E | tasks/smoke.yml exists; actual configured service/HTTP readiness and meaningful unit/integration/recovery tests must run. |
| POL-29 | 474–479 | E | Final complete authorized AAP workflow after fixed artifact/full review freeze. Define starting state/scenarios/outcomes/preservation/smoke first; no remote jobs in this phase. |
| POL-30 | 481–504 | P/E | Fix batch, focused functionality/regression, then full restarted review and finalAAP. Acceptance binds exact artifact/dependencies; historical cycles cannot certify new edits. |
| POL-31 | 528–541 | E/F | Final evidence must bind exact source/CaC/secrets, guide/policy, runtime/dependencies, commands/jobs, deprecations/timings/gaps and per-finding resolution. Sensitive evidence private; unrelated work untouched. |
| POL-32 | 545–557 | E | No completed Code_Review report until all mandatory stages pass. Report belongs in reviewed repo, linked README, identifying functional revision separately from later report-only commit. |
| POL-33 | 561–575 | E | Scope/agents/baseline/coverage/exclusions/findings/batches/results and explicit exact-revision functionality confirmation required; job launch is not completion. |
| POL-34 | 576–581 | F | Record guidance contradictions below, chosen approach, alternatives, functionality protection and verification. |
| POL-35 | 582–587 | E/A | Final deviation cost/benefit and evidence-limited conclusion; no premature accepted-artifact claim. |
| POL-36 | 588–603 | A | Optional modules/collections/typing/pytest/CI suggestions need real gap/benefit/effort/maintenance/priority; compare certified content/tool overlap before implementation. |
| POL-37 | 605–607 | P/E | Raw sensitive evidence stays private; no completed reports deleted/fabricated. Root sanitizes publication. |
| POL-38 | 611–623 | P/F | README/history explain purpose, environment, historical vs unverified results and real commits. Baseline lacks complete inputs/outputs/setup/validation/recovery and supporting-code links; root validates corrections. |
| POL-39 | 625–628 | F | No baseline TLDR. Add linked concise overview preserving prerequisites/TLS/exact pair/empty limit/reboot/no-reset cautions. |
| POL-40 | 630–635 | F/E | Complex workflow requires sourced maintained GitHubPages overview with stages/dependencies/inputs/success/recovery and README/TLDR links. Source creation is not hosting/publication proof. |
| POL-41 | 643–646 | P/E | Publishing policy itself does not review this project. Mandatory tool/finalAAP evidence still pending. |

## Concrete minimal baseline corrections

1. Add README-linked TLDR and focused operation/reference documentation: selected scope, naming, complete variables/outputs/precedence, protected CaC restore/import entry, reproducible validation commands, expected outcomes, troubleshooting/recovery and exclusions.
2. Document each non-Ansible purpose and native alternative considered. Link it from four Python implementation headers and relevant command/API/filter execution points. Pure filters, native RPM proof, EE introspection, package-manager/reboot/identity reads and synthetic test fixtures have distinct purposes.
3. Document the nineteen exported filters' inputs, outputs and practical examples; concise public contracts are preferable to collection scaffolding.
4. Explain check-mode limitations honestly. Mutation guards must stay safe. The baseline read-only runtime diagnostic skips its command under check mode then lacks report data; root may document or correct with focused testing, but this draft does not verify later edits.
5. Explain full publication's fresh-major release semantics and safe failure handling. Preserve exact tested-version promotion and no blind mutation retry.
6. Add a sourced process overview and verify required GitHubPages availability separately. Use sanitized data; source-only changes do not establish publication.
7. State credential rotation/revocation/access-audit ownership without changing credentials, RBAC, firewalls or schedules.
8. Root reports two flags corrected and 98-test validation pending; retain this historical baseline map, then record each actual correction/fix commit and new-revision evidence separately.

## Supporting-code decisions and linked-comment targets

- Pure filters: validate/transform Satellite IDs, bounded queries, metadata, authoritative epochs, baseline/cutoff preservation and recovery provenance. Large Jinja programs would obscure these guards. Dependencies are controller Python/Ansible plus stdlib; verification uses existing unit and actual-Ansible synthetic fixtures.
- Native RPM proof: package_facts does not establish full native EVR comparison across installed architectures and the running kernel. Use host librpm labelCompare and explicit structured proof; preserve Python2.7 compatibility for RHEL7 and test grammar/contract plus actual host result.
- Runtime probe: selected EE's installed ansible-doc schemas and syntax expose interface differences that ordinary syntax checks alone miss. It only inspects/parses; it does not execute patching stages or install content. Dependencies Ansible/PyYAML/CLI commands are already part of the chosen runtime.
- Native commands: exact advisory upgrade-minimal plus approved RHSM repository flags; subscription-manager consumer identity; native RPM snapshots; needs-restarting system/process detection and full no-pending-update result. argv avoids shell interpretation. Native modules considered must be checked against the exact baseline; package-fact-only or generic package actions do not establish all these properties.
- Incremental API: selected Satellite3.14 content does not expose this action, per recorded implementation inspection (design_decisions_history.md:305–309). Keep the small verified-HTTPS POST, no redirects/netrc, protected output, task completion and actual candidate validation. No custom module/collection/service needed solely to wrap one endpoint.
- Synthetic test code: generated modules/state files emulate Satellite in private temporary directories to execute actual task templating and recovery branches. They are test fixtures, not runtime replacements for certified content or live acceptance.
- Add short purpose/justification links at implementation headers and command/URI/filter execution points. Comments should explain the gap; detailed docs hold alternatives, versions, limits and verification.

## Accepted-deviation cost, risk and revisit register

These are resolved low-impact dispositions under proportionality, not claims of literal conformance. Effort estimates are qualitative; no invented precise duration. Mandatory evidence and unknown security conditions remain E.

| IDs / requirement | Benefit of strict correction | Effort and regression/maintenance cost | Accepted reason and practical impact | Revisit condition |
|---|---|---|---|---|
| NAM-03, NAM-04, NAM-09, COD-01/03; repository/playbook/AAP names | Closer consistency with one guide naming section; cosmetic discoverability | Public paths, surveys, presenter instructions and private CaC/deployed references could break; coordinated migration | Preserve explicit owner name and understandable existing conventions; document scheme. No demonstrated execution defect from current names. | New public API, unavoidable renaming or materially larger resource namespace. |
| STR-03, ROL-12, PLB-01; playbook/task structure instead of roles/collection | Potential reuse/distribution | Broad source/reference/test migration and extra packaging surface | Bounded independently launched workshop stages already share task components; no real external consumer. | Multiple genuine consumers, reusable role capability or justified collection release need. |
| INV-04/06/08; small inventory and pair API loop | Formal inventory separation/native generality | More files/indirection; changing pair restrictions could weaken safety | Two synthetic example hosts and deliberate exact pair are clear. Actual host work uses native inventory iteration. | Example inventory grows or approved scope becomes general host provisioning. |
| INV-10/11/15/16, COD-29/40; central vars and runtime facts/surveys | Less precedence breadth and tighter variable scope | Existing independent entrypoints, CaC/survey interfaces and cross-play proof readback can regress | Persistent environment identity remains protected; per-launch advisory/date/stage choices intentional. Explain precedence; no privileged-override containment claim. | Real collision/override defect, new reusable interface or simplified native readback demonstrated. |
| ROL-23/40, COD-21/22/32/34; brackets, task prefixes, bool casts and quoting | Minor consistency/searchability | Whole-tree churn and review noise; possible inadvertent expression changes | Existing fixed-key access, typed derived booleans and descriptive tasks show no observed failure. Prefer improved style in meaningful touched code. | Actual key collision/truthiness bug, strict lint finding with cheap safe fix, or substantial relevant rewrite. |
| PLG-05/06; exhaustive reST/type annotations | Better generated API/static tooling | Boilerplate/type migration; annotations incompatible with required host Python2.7 | Add meaningful public contracts and non-obvious intent; preserve host syntax. No new type-system dependency justified. | Host baseline drops Python2.7 or interface complexity/static tooling has demonstrated benefit. |
| PLG-07, TST-03/10; unittest retained | Alignment with Ansible Engineering pytest convention | Suite rewrite/new dependency with regression risk | Existing tests are meaningful and isolated; framework choice alone adds no functional assurance. | New tooling integration needs pytest or maintenance benefit becomes concrete. |
| PLG-09/10; no plugin-utils/scaffolding migration | Smaller entry files/conventional scaffolding | New indirection/package distribution paths, broader test/import maintenance | Cohesive manageable local helpers; no demonstrated cross-plugin consumer requiring extraction. | Shared functions materially duplicate or files become hard to maintain. |
| PLB-04; visible outcome debug | Less routine output | Presenter loses exact versions/results/next action; evidence becomes less visible | These messages are functional outputs in a human-led demo, not incidental logging. Sensitive credentials remain protected. | Production-oriented logging/UI consumer or excessive/noisy/unsafe output actually observed. |
| ROL-13/14, COD-28, TST-12; check-mode/release semantics | Uniform check mode/second changed=0 | Simulating async publication can falsely promise success; suppressing a requested fresh artifact changes purpose | Mutators fail explicitly; read-only checks remain read-only. Fresh publication inherently creates a release. Documentation and operation-specific recovery/repeat tests required. | Suitable native dry-run semantics become available or desired behavior changes. |
| NAM-07/08, GIT-02/04/08/18, CIC-01/04/12, AAP-14; manual workflow/no CI or tag framework | Automatic quality/review enforcement and release history | New integration/hosting/access/secrets maintenance; can exceed workshop scope | Document manual checks and future-bypass risk. Existing clear commits remain useful; do not claim hosted protection. Mandatory scans/tests still required independently. | External contributors, repeated releases/production operations or owner approval for CI/governance setup. |
| CIC-08/10/11; no enterprise QA/CAB pipeline | Scaled separation of duties | New organizational process outside bounded owner workshop | Explicit owner/manual Test-before-Prod gates retained; agent review not relabeled human signoff. | Production adoption or organization requires formal approvals. |
| GIT-12; independent component versions | Single identical version string | Renaming upstream artifacts misrepresents provenance and breaks compatibility | One immutable baseline records distinct compatible source/CaC/EE/core/Python/collection identifiers. | No revisit needed absent actual version mismatch; manifest completeness still required. |
| SEC-17/23/28; owner-selected rotation/audit/severity practices | Uniform published example intervals/thresholds | Credential/access/schedule changes are material security actions needing owner authority | Document external responsibility; actual security state remains E. Examples alone do not authorize changes or waive findings. | Owner selects policy or real findings require explicit security decision. |

## Guidance contradictions and chosen resolutions

| Sources | Context and choice | Alternatives and verification needed |
|---|---|---|
| naming_conventions:13,40,65 vs coding_style:16,26–27 and local policy:51–57,233–237 | Guide recommends hyphens/action-noun in one area and snake_case/object-action in another; owner explicitly chose repository name. Retain descriptive existing action_noun.yml/sniper_* interfaces and document them. | Broad rename could break CaC/public references. Strict lint/APME naming coverage and unchanged functional references still required. |
| coding_style:349–364 vs owner-selected AAP EE/core2.15 and policy:51–55 | Historical EL7 control-node Jinja warning does not apply merely because managed hosts are RHEL7. Preserve equality tests supported by the actual EE. | Regex workaround would obscure equality. Verify actual installed EE/Jinja/core and execution, not only local CLI. |
| coding_style:404–414 vs :452–454 and policy:252–260,269–294 | Generic module preference is qualified when exact advisory/repository behavior needs specific native tools. Keep argv commands and certified Satellite modules; add explicit native-gap rationale. | Exact baseline module interfaces must be checked; custom module/collection only if a concrete gap and worthwhile maintenance case exists. |
| playbooks:6–12, roles:167–176 vs structures:80–86 and proportionality policy:83–111 | Roles/collections improve real reuse, but user-requested independently launched workshop stages already share tasks. Preserve architecture. | Converting all stages introduces migration risk without demonstrated reuse; reconsider if genuine consumers emerge. |
| General current-AAP policy:174–184 vs explicit selected workshop runtime and handover:30–34 | Owner chose core2.15.11/Python3.9.19/Satellite3.14.0; receiverAAP2.7 is separate CaC/runtime diagnostic evidence. Do not silently upgrade or claim receiver host support. | Exact digest/support/compatibility/deprecations and final scoped AAP evidence still required. New runtime needs its own acceptance. |
| plugins:67–70/testing:164 vs existing unittest suites and proportionality | Preserve meaningful existing tests; add behavior coverage where fixes warrant it. Framework migration alone is low value. | Pytest may be optional future integration, not mandatory extra test architecture; actual test outcomes still required. |
| CoP strict lint generate-ignore example vs local policy:426–431 | Local stricter rule governs: no blanket ignore list or disabled rules to obtain green output. | Narrow documented deviations must identify true coverage and consequences. |
| CoP uniform idempotence wording vs explicit release action and local policy:312–314 | Fresh full publication intentionally creates a new major release; no claim that repeating it is a no-op. | Document release/recovery semantics, guard mutation and prove no unintended effects; other desired-state operations still need repeat/readback evidence. |

## Remaining evidence and publication boundary

- This inventory covers all13CoPareas and the full local policy. It does not supply completed mandatory tool/runtime tests or confirm later root fixes.
- Root must reconcile baseline findings with actual changed files/fix commits, run focused functionality/regressions (98-test validation currently pending per root), restart complete review as required and finish with the authorized full AAP workflow.
- Required evidence includes fresh guide revision check; exact source/CaC/secrets revisions; actual EE digest/core/Python/collections and PAH provenance; release-matched vendor/CIS control scope; strict lint/syntax/supporting-language checks; actual APME backend completion/findings; appropriate smoke/repeat/recovery outcomes; timings and final user-visible AAP completion/preservation.
- Private CaC restoration/reapply/readback, real credential/RBAC/rotation/audit state, hosted protection, image scans/SBOM and final source promotion must be marked with actual evidence or unresolved/authorized scoped disposition. Do not manufacture passes or conceal unknown security conditions.
- GitHubPages source creation and hosted publication are distinct evidence. No source task here publishes a site.
- No completed Code_Review_YYYY-MM-DD.md acceptance report or functionality confirmation:PASS is warranted before every mandatory stage succeeds on the exact corrected baseline.

## Inventory index

The inventory contains 280 source-located directive groups: 239 CoP groups across all13areas, plus41local-policy groups. Closely related bullets/repetitions/rationale/examples may share a group, as defined above. No count denotes passing independent tests.

| Area | Groups |
|---|---:|
| STR | 3 |
| NAM | 10 |
| ROL | 42 |
| COL | 5 |
| PLB | 4 |
| INV | 17 |
| PLG | 13 |
| COD | 57 |
| AAP | 14 |
| GIT | 18 |
| TST | 13 |
| CIC | 15 |
| SEC | 28 |
| POL | 41 |


## Additions in policy ee8db417

The policy remote was freshly checked and fetched at
`ee8db41797988d4e9b9fbfdf7c7b66f4dc410a36`; CoP remained
`fb5fcd6f03c544909dbad352a352b421c41d7203`. These groups supplement the original
matrix without changing its line numbers or claiming completed acceptance.
Sources refer to that newer policy README. Related bullets/rationale are grouped.

| ID | Source lines | Current disposition |
|---|---|---|
| NEW-01 | 115–118 | Static alignment: corrections retain the approved simple stages/tasks/filters. No speculative feature/framework added. |
| NEW-02 | 120–127 | Preserve consultation for extra architecture and existing approvals. Temporary analysis service/dependencies were explicitly authorized; no extra application architecture selected. |
| NEW-03 | 129–135 | Apply simplicity to documentation/recommendations while preserving security, functionality and meaningful tests; no complexity defect manufactured. |
| NEW-04 | 293–300 | Source/caller inventory now covers all four runtime Python files, every test suite and generated snippet group, and native command/API callers. Static source review does not imply executed coverage. |
| NEW-05 | 302–306 | Inventory records purpose, input/output, dependencies, context, effects and error/sensitive-data behavior. All runtime helpers are retained with concrete reasons. |
| NEW-06 | 308–314 | Built-in module interfaces and selected Satellite source were inspected before retention. Exact certified artifact/EE provenance and broader vendor security evidence remain gaps; namespace/hub presence alone is not certification proof. |
| NEW-07 | 316–320 | Explicit retain dispositions and reasons recorded in implementation inventory. No useful replacement/removal defect established; do not refactor merely to manufacture a finding. |
| NEW-08 | 322–329 | Assessed declarative alternatives to proof loading, commands and generated test snippets. Exact librpm/runtime/API contracts remain clearer in focused helpers; moving files alone would not simplify logic. |
| NEW-09 | 331–334 | Inventory and limitations belong in the eventual successful report. Current record remains incomplete and does not claim supporting code absent. |
| NEW-10 | 545–549 | Applicable to RPM deployment. Existing check_patch.yml checks real CV/consumer/native fix/reboot/smoke outcomes beyond readiness; corrected-source execution still pending. |
| NEW-11 | 551–552 | README documents the existing Check patch JT, prerequisites, protected inputs, authorized pair and expected result. No new runner/framework. |
| NEW-12 | 553–555 | Assertions and AAP terminal status give machine pass/fail. Read-only owned-pair checks create no test data and require no cleanup. Actual final result pending. |
| NEW-13 | 557–561 | Relevant actual-instance post-update checks and full AAP acceptance remain future work after this fix phase. Missing receiver SSH/runtime evidence remains unverified. |
| NEW-14 | 558–560 | Reuse existing Ansible/unittest/JTs and small meaningful scenarios. No speculative platform matrix. |
| NEW-15 | 562–566 | Non-deploying exemption does not apply to RPM patching. Functional check supplements full AAP acceptance and grants no new target/testing authority. |
| NEW-16 | 666–670 | Final report must include supporting-code analysis, dispositions/YAML alternatives and unresolved coverage. No successful report exists yet. |

## Reconciliation of baseline documentation findings

The added README naming/validation commands, TLDR, operations/process guides,
implementation interfaces/inventory and linked implementation/caller comments
address the documentation portions of STR-02, NAM-01, ROL-13/15/28/31/34/38,
COL-04, INV-01/14/15, PLG-03/04/05, COD-01/18/31, CIC-14 and
POL-12/13/14/16/17/18/34/38/39. This does not close any separate E evidence gap
or turn accepted deviations into literal conformance. The debug-kernel scope
limitation is explicit. The diagnostic check-mode defect is fixed with a real
behavior regression, rather than merely documented.

CIC-13/POL-31 artifact/runtime/CaC binding remains incomplete. SEC-16/27 ownership
is documented, but current credential rotation/revocation policy/cadence and
actual audits remain the environment owner's unverified responsibility. POL-40
GitHub Pages remains unconfigured; maintained diagram source is not hosting proof.
All final acceptance depends on actual required evidence, not group counts.
