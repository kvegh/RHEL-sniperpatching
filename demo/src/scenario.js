/* Reason: model browser-local educational states without running automation.
 * Justification: ../README.md#implementation-and-source-mapping.
 */
(function (root) {
  'use strict';

  const version = '0.19.20';
  const sourceRevision = '2fe10cd27c874691780c72eb66105f87cd5c12fa';
  const source = name => `playbooks/new/${name}`;
  const scenes = [
    { number: 1, title: 'All systems up to date' },
    { number: 2, title: 'CVE announced' },
    { number: 3, title: 'Ensure fix content is available' },
    { number: 4, title: 'Publish targeted CV' },
    { number: 5, title: 'Apply selected fix' },
    { number: 6, title: 'Routine patch window' },
    { number: 7, title: 'Apply broader updates' },
  ];
  const sceneByKind = {
    baseline: 1, resolve: 2, 'trigger-sync': 3, 'ensure-content': 3, 'cv-build': 4, minor: 4,
    'deploy-test': 5, 'patch-test': 5, 'verify-test': 5,
    'approve-targeted': 5, 'promote-targeted': 5, 'deploy-prod': 5, 'patch-prod': 5,
    'verify-prod': 5, 'time-passes': 6, 'full-publish': 6,
    'full-test': 7, 'approve-full': 7, 'full-promote': 7, 'full-prod': 7, complete: 7,
  };
  const scenarios = [
    {
      title: 'Python malicious package download',
      cve: 'CVE-2024-6345',
      advisory: 'RHSA-2024:5534',
      component: 'Python setuptools',
      cutoff: '2024-08-23',
      description: 'Untrusted package-download input can execute commands through affected setuptools functions.',
    },
    {
      title: 'Network Privilege Escalation',
      cve: 'CVE-2024-36883',
      advisory: 'RHSA-2024:6567',
      component: 'Linux kernel',
      cutoff: '2024-09-13',
      description: 'A local user can trigger a race in Linux networking to crash the system or potentially gain privileges.',
    },
  ];

  const snippets = {
    baseline: 'sniper_baseline_end_date: "2024-04-30"\nsniper_prepare_content_only: true\n# Verify baseline content before direct Test/Prod registration.',
    resolve: 'redhat.satellite.resource_info:\n  resource: errata\n  params:\n    repository_id: "{{ item.0.id }}"\n    cve: "{{ item.1 }}"',
    triggerSync: '# Explanatory repository-update trigger; not a per-CVE runtime job.\nredhat.satellite.repository_sync:\n  repository: \"{{ sniper_repository_name }}\"\n# The full-publication stage explicitly syncs selected repositories.\n# Targeted updates consume already synchronized content.',
    ensureContent: '# Confirm the selected fix exists in synchronized Satellite content.\nredhat.satellite.resource_info:\n  resource: errata\n# Targeted patching reads already synchronized repositories; no new per-CVE sync job.',
    timePasses: 'sniper_update_end_date: "{cutoff}"\n# A later maintenance window is an explanatory story transition.\n# Launch the existing full-update stage separately.',
    cvBuild: '# Explanatory composition stop before publishing the updated CV.\nadd_content:\n  errata_ids: \"{{ sniper_missing_errata }}\"\nresolve_dependencies: true\n# Baseline + selected fix + dependencies; not yet available to Test.',
    minor: '# Condensed incremental-update body; no host patching here.\nadd_content:\n  errata_ids: "{{ sniper_missing_errata }}"\nresolve_dependencies: true\n# Validate additions, then promote the exact minor to Test.',
    deployScoped: 'sniper_patch_id: \"{cve}\"\nsniper_patch_scope: targeted\n# AAP launches the existing host job for the selected host.\n# The CVE resolves to advisory-scoped packages and dependencies.',
    patch: '# Condensed native package transaction, constrained to the CV repositories.\ndnf upgrade-minimal --advisory={advisory}\n# Record changed RPMs and inspect needs-restarting.',
    verify: 'ansible.builtin.import_tasks: tasks/check_final.yml\n# Native installed-RPM and running-kernel proof.\n# Require no outstanding reboot; run configured smoke tests.',
    approve: '# Operator checkpoint between separately launched AAP stages.\n# Review Test evidence before launching the Prod operation.\n# No automatic approval node is added by the visualization.',
    promoteMinor: '# The Prod invocation reuses Test\'s exact minor.\nredhat.satellite.content_view_version:\n  version: "{{ sniper_new_version.version }}"\n  lifecycle_environments: "{{ [sniper_environment_name] }}"\n  force_promote: false',
    fullPublish: 'redhat.satellite.content_view_filter_rule:\n  end_date: "{cutoff}"\n  date_type: issued\n  types: [security, bugfix, enhancement]\n# Verify prior advisories are retained; promote the new major to Test.',
    fullPatch: '# The full scope uses the same selected CV repositories.\ndnf --setopt=metadata_expire=0 upgrade\n# Check reboot, fix proof and smoke tests; require no pending updates.',
    promoteFull: 'sniper_environment: prod\nsniper_version: "v{full}"\n# Compare exact version text with Test before promotion.\nredhat.satellite.content_view_version:\n  version: "{{ sniper_promotion_version }}"\n  lifecycle_environments: "{{ [sniper_prod_environment] }}"',
    check: '# Separate read-only final check.\n# Verify requested fixes, current CV binding, reboot state and smoke tests.\n# Use check_patch.yml with the same selected CVE/RHSA.',
  };

  function excerpt(name, scenario, full) {
    return snippets[name].replaceAll('{cve}', scenario.cve)
      .replaceAll('{advisory}', scenario.advisory)
      .replaceAll('{cutoff}', scenario.cutoff)
      .replaceAll('{full}', full);
  }

  const steps = [];

  scenarios.forEach((scenario, cycle) => {
    const minor = cycle === 0 ? '1.1' : '2.1';
    const full = cycle === 0 ? '2.0' : '3.0';
    const add = (kind, title, summary, detail, file, snippet, route, phase = 'Targeted fix') => {
      steps.push({ id: cycle === 0 && kind === 'baseline' ? 'baseline' : `run-${cycle + 1}-${kind}`,
        title, phase, cycle, kind, scene: sceneByKind[kind], summary, detail,
        source: source(file), code: excerpt(snippet, scenario, full), route });
    };

    add('baseline', 'All systems up to date',
      cycle === 0 ? 'Test Server and Prod Server start on the same verified baseline.' : 'The previous cycle is complete; both environments are up to date.',
      cycle === 0
        ? 'Both illustrative RHEL clients start on CV 1.0 with completed checks. No new CVE has been announced in the story. Satellite controls available content; installed packages are shown separately.'
        : 'Both environments retain CV 2.0 and the verified Python fix from the previous cycle. No next vulnerability has been announced yet; the completed state carries forward without resetting packages.',
      cycle === 0 ? 'prepare_demo.yml' : 'check_patch.yml', cycle === 0 ? 'baseline' : 'check', 'none', 'Baseline');
    add('resolve', 'Find the applicable security advisory', `AAP asks Satellite whether a fix for ${scenario.cve} is available.`,
      `${scenario.description} The alert first appears at this query action. The example input is fixed; the actual survey accepts a CVE list or one explicit RHSA. Satellite supplies ${scenario.advisory} and package metadata from the configured repositories. A CVE can resolve to more than one advisory; this prepared example follows its cataloged RHEL 9.4 advisory.`,
      'tasks/resolve.yml', 'resolve', 'resolve');
    add('trigger-sync', 'Trigger software repository update', 'AAP instructs Satellite to update its Red Hat software repositories.',
      'This explicit trigger is an explanatory mockup action. The full-publication playbook explicitly synchronizes selected repositories; the targeted playbook consumes already synchronized content and does not launch a per-CVE synchronization job. No automation is changed by this presentation stop.',
      'publish_full_update.yml', 'triggerSync', 'resolve');
    add('ensure-content', 'Ensure the fix content is available', 'Satellite confirms that the selected Red Hat fix content is ready.',
      'The incoming content flow explains Red Hat content availability. The targeted playbook reads already synchronized Satellite repositories and validates advisory/package metadata; it does not launch a new per-CVE repository synchronization job.',
      'create_minor_update.yml', 'ensureContent', 'upstream');
    add('cv-build', 'Trigger Content View update', `AAP instructs Satellite to prepare baseline content plus the selected fix for CV ${minor}.`,
      `This explanatory composition stop shows the selected advisory and dependencies being added to the existing baseline. It does not publish CV ${minor}, change Test Server or Prod Server content availability, or install any packages; publication is the next separately displayed action.`,
      'create_minor_update.yml', 'cvBuild', 'resolve');
    add('minor', 'Trigger publishing updated Content View', `AAP instructs Satellite to publish CV ${minor} and make it available to Test Server.`,
      `The incremental update adds the selected advisory and dependencies, preserving baseline content. CV ${minor} is available to Test Server; the host has not installed it, and Prod Server still serves its previous version.`,
      'create_minor_update.yml', 'minor', 'content-test');
    add('deploy-test', `Deploy ${scenario.cve} to Test Server`, `AAP triggers the CVE-scoped deployment on the selected Test Server.`,
      `AAP launches the existing targeted host job with ${scenario.cve}. It resolves to ${scenario.advisory}, selecting the advisory packages and required dependencies from Test Server's CV repositories. The existing job checks its explicitly selected Satellite host, CV/lifecycle binding and inventory/consumer identity; it does not discover or automatically select an entire fleet. This explanatory launch stop does not install packages.`,
      'patch_hosts.yml', 'deployScoped', 'execute-test');
    add('patch-test', 'Test Server pulls and applies the selected fix', `Test Server pulls ${scenario.advisory} packages from Satellite and applies the fix.`,
      `Under AAP control, Test Server's DNF transaction requests ${scenario.advisory} packages and required dependencies from its CV repositories. Satellite returns that requested content rather than initiating an unsolicited push; the host installs it and records changed packages. ${cycle === 1 ? 'This grouped kernel update includes the required reboot. The next verification action confirms the effective running kernel and service checks.' : 'The illustrative Python update needs no reboot; the real job checks the OS and running processes.'}`,
      'patch_hosts.yml', 'patch', 'execute-test');
    add('verify-test', 'Verify Test Server before proceeding', 'Confirm the effective fix, reboot state and service checks.',
      'The existing final checks use native RPM comparisons, running-kernel proof where relevant, no-pending-reboot verification and configured smoke tests. This stop represents successful simulated evidence.',
      'tasks/check_final.yml', 'verify', 'execute-test');
    add('approve-targeted', 'Approve the targeted Prod Server rollout', 'Test Server passed. Prod Server stays unchanged while the operator reviews.',
      `Review the Test Server result before continuing. The next action promotes the same tested CV ${minor}; it does not create another production-specific minor. Approval here models an operator checkpoint between the repository's separate AAP launches.`,
      'create_minor_update.yml', 'approve', 'none');
    add('promote-targeted', `Promote CV ${minor} to Prod Server`, 'Satellite makes the exact tested minor available to Prod Server.',
      'The production minor-update invocation reads the version already serving Test Server and reuses it through the normal lifecycle path. Promotion changes available content, not installed packages.',
      'create_minor_update.yml', 'promoteMinor', 'promote-prod');
    add('deploy-prod', `Deploy ${scenario.cve} to Prod Server`, `AAP triggers the same CVE-scoped deployment after approval and exact-version promotion.`,
      `AAP launches the existing targeted host job on the selected Prod Server with ${scenario.cve}. It selects ${scenario.advisory} packages and required dependencies from Prod Server's exact tested CV. This explanatory launch stop does not install packages.`,
      'patch_hosts.yml', 'deployScoped', 'execute-prod');
    add('patch-prod', 'Prod Server pulls and applies the selected fix', `Prod Server pulls ${scenario.advisory} packages from Satellite and applies the same fix.`,
      `Under AAP control, Prod Server's DNF transaction requests ${scenario.advisory} packages and required dependencies from its exact tested CV. Satellite returns the requested content; the host installs it rather than receiving an unsolicited push. ${cycle === 1 ? 'This grouped kernel update includes the required reboot while retaining the earlier Python fix. The next action verifies the running kernel and services.' : 'The illustrative Python update needs no reboot; the real job checks before deciding.'}`,
      'patch_hosts.yml', 'patch', 'execute-prod');
    add('verify-prod', 'Verify the targeted fix in Prod Server', 'Both hosts now have the selected fix verified.',
      'Installed and effective package proof, no pending reboot and smoke checks complete the targeted phase. Broader repository updates remain a later, separate operation.',
      'tasks/check_final.yml', 'verify', 'execute-prod');
    add('time-passes', 'A routine patch window arrives', 'Time passes after the targeted fix; broader maintenance is now due.',
      `The urgent security fix is already verified on both hosts. The later maintenance window uses the fixed content cutoff ${scenario.cutoff} to prepare the broader update. This transition explains elapsed time; it creates no runtime scheduler or automatic launch.`,
      'publish_full_update.yml', 'timePasses', 'none', 'Routine patch window');
    add('full-publish', `Publish the broader CV ${full}`, `Satellite includes all configured content through ${scenario.cutoff}.`,
      `The later maintenance update includes security, bug-fix and enhancement advisories through the explicit cutoff and keeps earlier fixes. ${cycle === 0 ? 'This cutoff precedes the second story\'s September 11 kernel fix, leaving that example outstanding.' : 'Both selected security fixes are retained.'} Only Test Server receives the new major CV at this stop.`,
      'publish_full_update.yml', 'fullPublish', 'content-test', 'Broader update');
    add('full-test', 'Fully update and verify Test Server', `AAP updates Test Server from CV ${full}.`,
      'Full scope updates all applicable packages offered by the selected CV repositories. The grouped operation includes required reboot handling, fix/service proof and a fresh check that no updates remain. Earlier security fixes remain installed.',
      'patch_hosts.yml', 'fullPatch', 'execute-test', 'Broader update');
    add('approve-full', 'Approve the broader Prod Server rollout', 'The full Test Server update passed. Review before changing Prod Server.',
      `The operator chooses to continue with exact Test Server version ${full}. Prod Server still serves the targeted minor and its installed state is unchanged at this checkpoint.`,
      'promote_content_view.yml', 'approve', 'none', 'Broader update');
    add('full-promote', `Promote exact CV ${full} to Prod Server`, 'Satellite serves the tested major CV to Prod Server.',
      'The promotion playbook requires explicit exact version text, matches it against the Test Server version, checks the lifecycle path and reads back the production binding. Host installation remains a separate job.',
      'promote_content_view.yml', 'promoteFull', 'promote-prod', 'Broader update');
    add('full-prod', 'Fully update and verify Prod Server', `AAP updates Prod Server from CV ${full}.`,
      'The full host job installs the remaining applicable repository updates, handles reboot needs and verifies the fix, services and no pending updates. Both hosts finish on the same available and installed illustrative CV.',
      'patch_hosts.yml', 'fullPatch', 'execute-prod', 'Broader update');
    add('complete', cycle === 0 ? 'Cycle complete: systems up to date' : 'Two cycles. One repeatable process.',
      cycle === 0 ? 'The Python fix is retained and both hosts are ready for normal operation.' : 'Both selected fixes and the broader updates are complete on Test Server and Prod Server.',
      'The independent read-only check can verify the selected fix and host state again. CV numbers and outcomes here are illustrative; the actual jobs return their own version and evidence.',
      'check_patch.yml', 'check', 'none', 'Cycle complete');
  });

  function initialHost() {
    return { installedCV: '1.0', fixed: [], reboot: 'Not required', verification: 'Passed', status: 'Baseline verified' };
  }

  function markFixed(host, cve) {
    if (!host.fixed.includes(cve)) host.fixed.push(cve);
  }

  function installTarget(host, scenario, cycle, minor) {
    host.installedCV = minor;
    host.status = 'Fix installed';
    host.verification = 'Pending';
    host.reboot = cycle === 1 ? 'Completed' : 'Not required';
    // The grouped kernel update includes reboot; the next action verifies its effective result.
    markFixed(host, scenario.cve);
  }

  function verifyTarget(host, scenario) {
    markFixed(host, scenario.cve);
    host.verification = 'Passed';
    host.status = 'Fix verified';
  }

  function updateAll(host, full) {
    host.installedCV = full;
    host.verification = 'Passed';
    host.reboot = 'Checks complete';
    host.status = 'All offered updates verified';
  }

  function stateAt(requestedIndex) {
    const numeric = Number(requestedIndex);
    const index = Math.max(0, Math.min(steps.length - 1, Number.isFinite(numeric) ? Math.trunc(numeric) : 0));
    const state = {
      index, cycle: steps[index].cycle, scenario: scenarios[steps[index].cycle],
      testCV: '1.0', prodCV: '1.0',
      versions: [{ version: '1.0', label: 'Controlled baseline' }],
      test: initialHost(), prod: initialHost(), job: steps[index].title,
      announced: [], delivery: 'none', maintenance: steps[index].scene === 6,
    };

    // Rebuild from the baseline so Previous, direct links and Restart cannot leak later state.
    for (const step of steps.slice(0, index + 1)) {
      const scenario = scenarios[step.cycle];
      const minor = step.cycle === 0 ? '1.1' : '2.1';
      const full = step.cycle === 0 ? '2.0' : '3.0';
      switch (step.kind) {
        case 'resolve':
          state.announced.push(scenario.cve);
          state.test.status = 'Selected fix needed';
          state.prod.status = 'Selected fix needed';
          state.test.verification = 'Pending';
          state.prod.verification = 'Pending';
          break;
        case 'minor':
          state.versions.push({ version: minor, label: scenario.title });
          state.testCV = minor;
          break;
        case 'patch-test': installTarget(state.test, scenario, step.cycle, minor); break;
        case 'patch-prod': installTarget(state.prod, scenario, step.cycle, minor); break;
        case 'verify-test': verifyTarget(state.test, scenario); break;
        case 'verify-prod': verifyTarget(state.prod, scenario); break;
        case 'promote-targeted': state.prodCV = minor; break;
        case 'full-publish':
          state.versions.push({ version: full, label: 'All updates until date cutoff' });
          state.testCV = full;
          break;
        case 'full-test': updateAll(state.test, full); break;
        case 'full-promote': state.prodCV = full; break;
        case 'full-prod': updateAll(state.prod, full); break;
        default: break;
      }
    }
    const current = steps[index];
    state.delivery = current.kind === 'ensure-content' ? 'targeted'
      : current.kind === 'full-publish' ? 'bulk' : 'none';
    for (const [host, available] of [[state.test, state.testCV], [state.prod, state.prodCV]]) {
      const affected = state.announced.some(cve => !host.fixed.includes(cve));
      host.health = affected ? 'affected'
        : host.verification === 'Pending' ? 'verifying'
          : available !== host.installedCV ? 'updates' : 'healthy';
    }
    return state;
  }

  const story = { version, sourceRevision, scenarios, scenes, steps, stateAt };
  if (typeof module !== 'undefined' && module.exports) module.exports = story;
  if (root) root.SniperStory = story;
}(typeof window !== 'undefined' ? window : globalThis));
