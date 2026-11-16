/* Reason: model browser-local educational states without running automation.
 * Justification: ../README.md#implementation-and-source-mapping.
 */
(function (root) {
  'use strict';

  const version = '0.16.0';
  const sourceRevision = '2fe10cd27c874691780c72eb66105f87cd5c12fa';
  const source = name => `playbooks/new/${name}`;
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
    input: 'sniper_patch_id: "{cve}"\nsniper_environment: test\nsniper_patch_scope: targeted',
    resolve: 'redhat.satellite.resource_info:\n  resource: errata\n  params:\n    repository_id: "{{ item.0.id }}"\n    cve: "{{ item.1 }}"',
    minor: '# Condensed incremental-update body; no host patching here.\nadd_content:\n  errata_ids: "{{ sniper_missing_errata }}"\nresolve_dependencies: true\n# Validate additions, then promote the exact minor to Test.',
    patch: '# Condensed native package transaction, constrained to the CV repositories.\ndnf upgrade-minimal --advisory={advisory}\n# Record changed RPMs and inspect needs-restarting.',
    reboot: 'ansible.builtin.reboot:\n  reboot_timeout: "{{ sniper_reboot_timeout }}"\n  post_reboot_delay: 10\n# Triggered by OS, kernel, advisory or stale-process evidence.',
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

  const steps = [{
    id: 'baseline', title: 'Start with a controlled baseline', phase: 'Baseline', cycle: 0,
    kind: 'baseline', summary: 'Satellite serves the same baseline to Test and Prod.',
    detail: 'Both illustrative RHEL clients start on CV 1.0. Satellite controls available content; installed packages are shown separately. The two selected fixes are not yet applied. This is an explanatory mockup, not evidence of the live environment.',
    source: source('prepare_demo.yml'), code: snippets.baseline, route: 'none',
  }];

  scenarios.forEach((scenario, cycle) => {
    const minor = cycle === 0 ? '1.1' : '2.1';
    const full = cycle === 0 ? '2.0' : '3.0';
    const add = (kind, title, summary, detail, file, snippet, route, phase = 'Targeted fix') => {
      steps.push({ id: `run-${cycle + 1}-${kind}`, title, phase, cycle, kind, summary, detail,
        source: source(file), code: excerpt(snippet, scenario, full), route });
    };

    add('input', scenario.title, `AAP receives ${scenario.cve}.`,
      `${scenario.description} The example input is fixed for this story. The actual survey accepts a CVE list or one explicit RHSA.`,
      'tasks/resolve.yml', 'input', 'none');
    add('resolve', 'Find the applicable security advisory', `AAP asks Satellite to resolve ${scenario.cve}.`,
      `Satellite supplies ${scenario.advisory} and package metadata from the configured repositories. A CVE can resolve to more than one advisory; this prepared example follows its cataloged RHEL 9.4 advisory.`,
      'tasks/resolve.yml', 'resolve', 'resolve');
    add('minor', `Add the fix in CV ${minor}`, `Satellite creates a minor CV update and promotes it to Test.`,
      `The incremental update adds the selected advisory and dependencies, preserving baseline content. CV ${minor} is available to Test; the host has not installed it, and Prod still serves its previous version.`,
      'create_minor_update.yml', 'minor', 'content-test');
    add('patch-test', 'Apply the selected fix to Test', `AAP runs the targeted package update on Test.`,
      `The host job installs the selected advisory from Test's CV repositories and records changed packages. ${cycle === 1 ? 'The fixed kernel is installed, but its running-kernel proof still requires a reboot.' : 'The illustrative Python update needs no reboot; the real job checks the OS and running processes.'}`,
      'patch_hosts.yml', 'patch', 'execute-test');
    if (cycle === 1) add('reboot-test', 'Boot Test into the fixed kernel', 'AAP reboots Test before declaring the fix effective.',
      'A newly installed kernel is not the running kernel until boot. The actual job checks the OS reboot signal, kernel proof, advisory hints, changed packages and stale processes.',
      'patch_hosts.yml', 'reboot', 'execute-test');
    add('verify-test', 'Verify Test before proceeding', 'Confirm the effective fix, reboot state and service checks.',
      'The existing final checks use native RPM comparisons, running-kernel proof where relevant, no-pending-reboot verification and configured smoke tests. This stop represents successful simulated evidence.',
      'tasks/check_final.yml', 'verify', 'execute-test');
    add('approve-targeted', 'Approve the targeted Prod rollout', 'Test passed. Prod stays unchanged while the operator reviews.',
      `Review the Test result before continuing. The next action promotes the same tested CV ${minor}; it does not create another production-specific minor. Approval here models an operator checkpoint between the repository's separate AAP launches.`,
      'create_minor_update.yml', 'approve', 'none');
    add('promote-targeted', `Promote CV ${minor} to Prod`, 'Satellite makes the exact tested minor available to Prod.',
      'The production minor-update invocation reads the version already serving Test and reuses it through the normal lifecycle path. Promotion changes available content, not installed packages.',
      'create_minor_update.yml', 'promoteMinor', 'promote-prod');
    add('patch-prod', 'Apply the selected fix to Prod', 'AAP runs the same targeted update against the production host.',
      `The existing host-patching job uses Prod's newly promoted CV. ${cycle === 1 ? 'Its fixed kernel is installed first; reboot and running-kernel verification follow.' : 'The illustrative Python update needs no reboot; the real job checks before deciding.'}`,
      'patch_hosts.yml', 'patch', 'execute-prod');
    if (cycle === 1) add('reboot-prod', 'Boot Prod into the fixed kernel', 'AAP reboots Prod using the normal host-patching logic.',
      'The earlier Python fix stays installed. Reboot activates the selected kernel update before final proof and service checks.',
      'patch_hosts.yml', 'reboot', 'execute-prod');
    add('verify-prod', 'Verify the targeted fix in Prod', 'Both hosts now have the selected fix verified.',
      'Installed and effective package proof, no pending reboot and smoke checks complete the targeted phase. Broader repository updates remain a later, separate operation.',
      'tasks/check_final.yml', 'verify', 'execute-prod');
    add('full-publish', `Publish the broader CV ${full}`, `Satellite includes all configured content through ${scenario.cutoff}.`,
      `The later maintenance update includes security, bug-fix and enhancement advisories through the explicit cutoff and keeps earlier fixes. ${cycle === 0 ? 'This cutoff precedes the second story\'s September 11 kernel fix, leaving that example outstanding.' : 'Both selected security fixes are retained.'} Only Test receives the new major CV at this stop.`,
      'publish_full_update.yml', 'fullPublish', 'content-test', 'Broader update');
    add('full-test', 'Fully update and verify Test', `AAP updates Test from CV ${full}.`,
      'Full scope updates all applicable packages offered by the selected CV repositories. The grouped operation includes required reboot handling, fix/service proof and a fresh check that no updates remain. Earlier security fixes remain installed.',
      'patch_hosts.yml', 'fullPatch', 'execute-test', 'Broader update');
    add('approve-full', 'Approve the broader Prod rollout', 'The full Test update passed. Review before changing Prod.',
      `The operator chooses to continue with exact Test version ${full}. Prod still serves the targeted minor and its installed state is unchanged at this checkpoint.`,
      'promote_content_view.yml', 'approve', 'none', 'Broader update');
    add('full-promote', `Promote exact CV ${full} to Prod`, 'Satellite serves the tested major CV to Prod.',
      'The promotion playbook requires explicit exact version text, matches it against the Test version, checks the lifecycle path and reads back the production binding. Host installation remains a separate job.',
      'promote_content_view.yml', 'promoteFull', 'promote-prod', 'Broader update');
    add('full-prod', 'Fully update and verify Prod', `AAP updates Prod from CV ${full}.`,
      'The full host job installs the remaining applicable repository updates, handles reboot needs and verifies the fix, services and no pending updates. Both hosts finish on the same available and installed illustrative CV.',
      'patch_hosts.yml', 'fullPatch', 'execute-prod', 'Broader update');
    add('complete', cycle === 0 ? 'One cycle complete. Another fix arrives.' : 'Two cycles. One repeatable process.',
      cycle === 0 ? 'The Python fix is retained; the next story introduces the kernel fix.' : 'Both selected fixes and the broader updates are complete on Test and Prod.',
      'The independent read-only check can verify the selected fix and host state again. CV numbers and outcomes here are illustrative; the actual jobs return their own version and evidence.',
      'check_patch.yml', 'check', 'none', 'Cycle complete');
  });

  function initialHost() {
    return { installedCV: '1.0', fixed: [], reboot: 'Not required', verification: 'Baseline', status: 'Baseline ready' };
  }

  function markFixed(host, cve) {
    if (!host.fixed.includes(cve)) host.fixed.push(cve);
  }

  function installTarget(host, scenario, cycle, minor) {
    host.installedCV = minor;
    host.status = cycle === 1 ? 'Kernel installed; reboot pending' : 'Package fix installed';
    host.verification = 'Pending';
    host.reboot = cycle === 1 ? 'Required' : 'Not required';
    // Kernel package installation alone is not proof that the running kernel is fixed.
    if (cycle === 0) markFixed(host, scenario.cve);
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
    };

    // Rebuild from the baseline so Previous, direct links and Restart cannot leak later state.
    for (const step of steps.slice(0, index + 1)) {
      const scenario = scenarios[step.cycle];
      const minor = step.cycle === 0 ? '1.1' : '2.1';
      const full = step.cycle === 0 ? '2.0' : '3.0';
      switch (step.kind) {
        case 'minor':
          state.versions.push({ version: minor, label: scenario.title });
          state.testCV = minor;
          break;
        case 'patch-test': installTarget(state.test, scenario, step.cycle, minor); break;
        case 'patch-prod': installTarget(state.prod, scenario, step.cycle, minor); break;
        case 'reboot-test':
        case 'reboot-prod': {
          const host = step.kind === 'reboot-test' ? state.test : state.prod;
          host.reboot = 'Completed';
          host.status = 'Fixed kernel running';
          markFixed(host, scenario.cve);
          break;
        }
        case 'verify-test': verifyTarget(state.test, scenario); break;
        case 'verify-prod': verifyTarget(state.prod, scenario); break;
        case 'promote-targeted': state.prodCV = minor; break;
        case 'full-publish':
          state.versions.push({ version: full, label: `All updates through ${scenario.cutoff}` });
          state.testCV = full;
          break;
        case 'full-test': updateAll(state.test, full); break;
        case 'full-promote': state.prodCV = full; break;
        case 'full-prod': updateAll(state.prod, full); break;
        default: break;
      }
    }
    return state;
  }

  const story = { version, sourceRevision, scenarios, steps, stateAt };
  if (typeof module !== 'undefined' && module.exports) module.exports = story;
  if (root) root.SniperStory = story;
}(typeof window !== 'undefined' ? window : globalThis));
