/* Browser rendering and presenter controls; rationale: ../README.md#supporting-code. */
(function () {
  'use strict';
  const story = window.SniperStory;
  const byId = id => document.getElementById(id);
  const root = byId('walkthrough');
  const routeNames = ['resolve', 'content-test', 'content-prod', 'execute-test', 'execute-prod'];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let motion = !reducedMotion.matches;
  let index = 0;

  function indexFromHash() {
    const requested = new URLSearchParams(window.location.hash.slice(1)).get('step');
    const aliases = {
      'run-1-input': 'run-1-resolve', 'run-2-input': 'run-2-resolve',
      'run-1-host-scope': 'run-1-deploy-test', 'run-2-host-scope': 'run-2-deploy-test',
      'run-1-request-test': 'run-1-patch-test', 'run-2-request-test': 'run-2-patch-test',
      'run-1-request-prod': 'run-1-patch-prod', 'run-2-request-prod': 'run-2-patch-prod',
      'run-2-reboot-test': 'run-2-patch-test', 'run-2-reboot-prod': 'run-2-patch-prod',
    };
    const id = aliases[requested] || requested;
    const found = story.steps.findIndex(step => step.id === id);
    return found < 0 ? 0 : found;
  }

  function element(tag, className, text) {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text !== undefined) item.textContent = text;
    return item;
  }

  function renderCV(id, version) {
    const node = byId(id);
    const value = `CV ${version}`;
    node.classList.add('cv-counter');
    node.setAttribute('aria-label', value);
    if (!motion) {
      node.classList.remove('is-rolling');
      node.dataset.previous = '';
    }
    if (node.textContent === value) return;
    const previous = node.textContent;
    node.classList.remove('is-rolling');
    node.dataset.previous = motion ? previous : '';
    const oldValue = element('span', 'cv-counter-previous');
    oldValue.dataset.previous = motion ? previous : '';
    oldValue.setAttribute('aria-hidden', 'true');
    node.replaceChildren(oldValue, element('span', 'cv-counter-value', value));
    if (previous && motion) {
      // Flush the removed class so consecutive CV changes restart the counter.
      void node.offsetWidth;
      node.classList.add('is-rolling');
    }
  }

  function renderHost(name, host, available, announced, currentCve) {
    byId(`${name}-host`).dataset.health = host.health;
    renderCV(`${name}-available`, available);
    renderCV(`${name}-installed`, host.installedCV);
    byId(`${name}-status`).textContent = `${host.health === 'healthy' ? '✓ ' : ''}${host.status}`;
    byId(`${name}-reboot`).textContent = host.reboot;
    byId(`${name}-verification`).textContent = host.verification;
    const rows = story.scenarios.filter(scenario => announced.includes(scenario.cve)).map(scenario => {
      const fixed = host.fixed.includes(scenario.cve);
      const verifying = fixed && scenario.cve === currentCve && host.verification === 'Pending';
      const row = element('div', 'fix-row');
      const label = element('div', 'fix-name', scenario.title);
      label.append(element('small', '', scenario.cve));
      const stateClass = verifying ? ' verifying' : fixed ? ' fixed' : '';
      row.append(label, element('span', `fix-state${stateClass}`, verifying ? 'Verifying' : fixed ? 'Fixed' : 'Needs fix'));
      return row;
    });
    if (!rows.length) {
      const row = element('div', 'fix-row');
      row.append(element('div', 'fix-name', 'Defined baseline'), element('span', 'fix-state fixed', '✓ Verified'));
      rows.push(row);
    }
    byId(`${name}-fixes`).replaceChildren(...rows);
  }

  function eventContent(step, state, approval) {
    if (step.scene === 1) return ['healthy', 'BASELINE VERIFIED', 'All systems up to date', `Test Server and Prod Server verified on baseline CV ${state.testCV}.`];
    if (step.scene === 2) return ['alert', 'CVE ANNOUNCED', state.scenario.title, `${state.scenario.cve} is announced and named to AAP.`];
    if (step.kind === 'trigger-sync') return ['content', 'AAP ORCHESTRATES', 'Update the software repositories', 'AAP instructs Satellite to update its repository content before preparing the fix.'];
    if (step.scene === 3) return ['content', 'RED HAT CONTENT', 'Download fix', 'Satellite obtains the selected security fix and required dependencies.'];
    if (step.kind === 'cv-build') return ['content', 'AAP ORCHESTRATES', 'Update the Content View', 'The baseline plus the selected fix prepares the next minor CV. It is not available to hosts until publication.'];
    if (step.scene === 4) return ['content', 'TARGETED CONTENT VIEW', 'Baseline + selected fix + dependencies', `CV ${state.testCV} is available to Test Server. Publishing content has not installed packages on either host.`];
    if (approval) return ['approval', 'OPERATOR CHECKPOINT', 'Test Server passed. Approve production.', 'Prod Server stays on its current content and installed packages until the operator continues with the exact tested version.'];
    if (step.kind === 'verify-prod') return ['healthy', 'TARGETED FIX VERIFIED', 'Both hosts have the selected fix', 'The urgent vulnerability is addressed. Broader routine updates will follow at the maintenance window.'];
    if (step.kind === 'time-passes') return ['maintenance', 'TIME PASSES', 'The next patch window approaches', 'The urgent fix stays installed while new security fixes, bug fixes and enhancements accumulate.'];
    if (step.scene === 6) return ['maintenance', 'REGULAR PATCH WINDOW', 'New updates pour in', `Satellite prepares broader content through ${state.scenario.cutoff}, retaining the already-applied security fix.`];
    if (step.kind === 'complete') return ['healthy', 'BASELINE VERIFIED', 'All systems up to date', `Both hosts are verified on CV ${state.testCV}. ${step.cycle === 0 ? 'The next run starts healthy before a new CVE is announced.' : 'Both fixed examples have completed their targeted and regular maintenance cycles.'}`];
    return ['info', step.scene === 5 ? 'TARGETED ROLLOUT' : 'BROADER ROLLOUT', step.title, 'Check the selected Test Server and Prod Server hosts, apply only the required package changes, and verify the result.'];
  }

  function renderEvent(step, state, approval) {
    const [tone, kicker, title, detail] = eventContent(step, state, approval);
    byId('story-event').dataset.tone = tone;
    byId('event-kicker').textContent = kicker;
    byId('event-title').textContent = title;
    byId('event-detail').textContent = detail;
  }

  function updateUpstreamRoute() {
    const surface = byId('architecture').getBoundingClientRect();
    if (!surface.width || !surface.height) return;
    const source = byId('redhat-source').getBoundingClientRect();
    const satellite = byId('satellite-platform').getBoundingClientRect();
    const startX = source.right - surface.left;
    const startY = source.top + source.height / 2 - surface.top;
    const endX = satellite.left + satellite.width / 2 - surface.left;
    const endY = satellite.top - surface.top;
    const bendX = Math.min(surface.width - 3, Math.max(startX + 18, endX + 18));
    // Leave the horizontal arrival lane below the wrapping package list.
    const transfer = byId('supply-transfer').getBoundingClientRect();
    const contentBottom = Math.max(source.bottom, transfer.bottom) - surface.top;
    const bendY = (contentBottom + endY) / 2;
    byId('upstream-route').setAttribute('viewBox', `0 0 ${surface.width} ${surface.height}`);
    const path = `M ${startX} ${startY} H ${bendX} V ${bendY} H ${endX} V ${endY}`;
    byId('upstream-path').setAttribute('d', path);
    byId('upstream-pulse').setAttribute('d', path);
  }

  function renderDelivery(state) {
    byId('redhat-supply').dataset.delivery = state.delivery;
    byId('supply-transfer').hidden = state.delivery === 'none';
    byId('upstream-route').classList.toggle('is-visible', state.delivery !== 'none');
    byId('upstream-pulse').classList.toggle('is-active', state.delivery !== 'none');
    const labels = state.delivery === 'targeted'
      ? ['Selected security fix', 'Required dependencies']
      : state.delivery === 'bulk'
        ? ['Earlier fix ✓', 'Security updates', 'Bug fixes', 'Enhancements', 'Libraries', 'System tools', 'Drivers', 'Package updates', 'Maintenance fixes']
        : [];
    byId('delivery-label').textContent = state.delivery === 'targeted'
      ? 'Download fix'
      : state.delivery === 'bulk' ? 'Download updates' : '';
    byId('package-stream').replaceChildren(...labels.map((label, position) => {
      const kind = position === 0 ? 'selected-fix' : state.delivery === 'targeted' ? 'dependency' : 'routine-update';
      return element('span', `content-parcel ${kind}`, label);
    }));
  }

  function renderSceneNavigation(step) {
    byId('step-list').replaceChildren(...story.scenes.map(scene => {
      const row = element('li', scene.number < step.scene ? 'is-complete' : '');
      const button = element('button');
      button.type = 'button';
      if (scene.number === step.scene) button.setAttribute('aria-current', 'step');
      button.append(element('span', 'step-number', scene.number < step.scene ? '✓' : String(scene.number)), element('span', '', scene.title));
      button.addEventListener('click', () => navigate(story.steps.findIndex(item => item.cycle === step.cycle && item.scene === scene.number)));
      row.append(button);
      return row;
    }));
  }

  function render() {
    const state = story.stateAt(index);
    const step = story.steps[index];
    const approval = step.kind.startsWith('approve-');
    const currentAnnounced = state.announced.includes(state.scenario.cve);
    const actions = story.steps.filter(item => item.cycle === step.cycle && item.scene === step.scene);
    const actionNumber = actions.findIndex(item => item.id === step.id) + 1;
    root.classList.toggle('is-approval', approval);
    root.classList.toggle('is-alert', step.scene === 2);
    root.classList.toggle('is-maintenance', state.maintenance);
    root.dataset.motion = motion ? 'on' : 'off';
    root.dataset.scene = String(step.scene);
    byId('run-label').textContent = `RUN 0${step.cycle + 1} / 02`;
    byId('scenario-title').textContent = currentAnnounced ? state.scenario.title : 'All systems up to date';
    byId('scenario-cve').textContent = currentAnnounced ? `${state.scenario.cve} · ${state.scenario.advisory}` : 'Baseline verified · no active security alerts';
    byId('step-count').textContent = `SCENE ${step.scene} OF ${story.scenes.length}`;
    byId('scene-progress').textContent = actions.length > 1 ? `: Action ${actionNumber} of ${actions.length}` : '';
    byId('step-title').textContent = step.title;
    byId('step-summary').textContent = step.summary;
    byId('phase-label').textContent = step.phase;
    byId('phase-badge').textContent = approval ? 'Approval required' : step.phase;
    byId('job-label').textContent = state.job;
    renderCV('binding-test', state.testCV);
    renderCV('binding-prod', state.prodCV);
    const previousApiAction = byId('api-label').textContent;
    byId('api-label').textContent = step.kind === 'trigger-sync'
      ? 'Trigger software repository update'
      : step.kind === 'cv-build' ? 'Trigger Content View update'
        : step.kind === 'minor' ? 'Trigger publishing updated Content View'
          : step.scene === 2 ? 'Query: fix available?' : '';
    byId('flow-resolve').hidden = !byId('api-label').textContent;
    byId('flow-resolve').setAttribute('aria-label', byId('api-label').textContent);
    if (previousApiAction !== byId('api-label').textContent) {
      const pulse = byId('api-pulse');
      pulse.classList.remove('is-moving');
      pulse.dataset.action = byId('api-label').textContent;
      if (pulse.dataset.action) {
        // Restart the highlight for each distinct query or trigger action.
        void pulse.offsetWidth;
        pulse.classList.add('is-moving');
      }
    }
    byId('cv-update').hidden = step.scene !== 4 && step.scene !== 5;
    byId('cv-update').textContent = `CV ${step.cycle + 1}.0 + fix == CV ${step.cycle + 1}.1`;
    byId('cv-availability').hidden = byId('cv-update').hidden;
    byId('cv-availability').textContent = step.kind === 'cv-build'
      ? 'Prepared in Satellite · not published yet'
      : `CV ${state.testCV} available to ${state.prodCV === state.testCV ? 'Test Server and Prod Server' : 'Test Server'}`;
    byId('test-available').classList.toggle('is-new-content', step.kind === 'minor');
    const affected = [['Test Server', state.test], ['Prod Server', state.prod]]
      .filter(([, host]) => state.announced.some(cve => !host.fixed.includes(cve)))
      .map(([name]) => name);
    byId('target-scope').textContent = affected.length ? `Affected in selected scope: ${affected.join(' · ')}` : 'Selected scope: Test Server · Prod Server';
    byId('previous').disabled = index === 0;
    byId('next').disabled = index === story.steps.length - 1;
    byId('next').textContent = approval ? 'Approve Prod Server →' : index === story.steps.length - 1 ? 'Complete ✓' : 'Next →';
    byId('next').classList.toggle('approval', approval);
    byId('motion').textContent = motion ? 'Motion on' : 'Motion off';
    byId('motion').setAttribute('aria-pressed', String(motion));
    for (let cycle = 0; cycle < 2; cycle += 1) byId(`cycle-${cycle}`).setAttribute('aria-pressed', String(step.cycle === cycle));
    renderHost('test', state.test, state.testCV, state.announced, state.scenario.cve);
    renderHost('prod', state.prod, state.prodCV, state.announced, state.scenario.cve);
    renderEvent(step, state, approval);
    renderDelivery(state);
    for (const route of routeNames) byId(`flow-${route}`).classList.toggle('is-active', step.route === route);
    if (step.scene === 2 || step.kind === 'trigger-sync' || step.kind === 'cv-build' || step.kind === 'minor') byId('flow-resolve').classList.add('is-active');
    // The DNF client requests packages; Satellite returns the selected content.
    for (const environment of ['test', 'prod']) {
      const route = byId(`flow-content-${environment}`);
      const requesting = step.kind === `patch-${environment}`;
      route.classList.toggle('is-requesting', requesting);
      if (requesting || (step.route === `execute-${environment}` && step.kind !== `deploy-${environment}`)) route.classList.add('is-active');
    }
    for (const routeName of ['execute-test', 'execute-prod', 'content-test', 'content-prod']) {
      const route = byId(`flow-${routeName}`);
      const pulse = byId(`flow-${routeName}-pulse`);
      pulse.setAttribute('d', route.getAttribute('d'));
      pulse.classList.toggle('is-active', route.classList.contains('is-active'));
      pulse.classList.toggle('is-requesting', route.classList.contains('is-requesting'));
    }
    byId('execution-label').textContent = step.kind.startsWith('deploy-')
      ? `AAP deploys fix · ${state.scenario.cve}` : 'AAP executes host automation';
    const environment = step.kind.endsWith('-prod') ? 'Prod Server' : 'Test Server';
    byId('host-content-label').textContent = step.kind === 'patch-test' || step.kind === 'patch-prod'
      ? `${environment} pulls the selected fix from Satellite` : 'Satellite provides updates';
    byId('host-routes').setAttribute('aria-label', `${byId('execution-label').textContent}; ${byId('host-content-label').textContent}`);
    byId('test-host').classList.toggle('is-active', step.route === 'execute-test' || step.route === 'content-test');
    byId('prod-host').classList.toggle('is-active', step.route === 'execute-prod' || step.route === 'content-prod');
    document.querySelector('.satellite').classList.toggle('is-promoting', step.route === 'promote-prod');
    renderSceneNavigation(step);
    byId('version-list').replaceChildren(...state.versions.map(version => {
      const row = element('li');
      const content = element('div', 'version-item');
      content.append(element('strong', '', `CV ${version.version}`), element('span', '', version.label));
      row.append(content);
      return row;
    }));
    byId('technical-description').textContent = step.detail;
    byId('scenario-description').textContent = currentAnnounced
      ? `${state.scenario.description} Full-update content cutoff: ${state.scenario.cutoff}. CV numbers and outcomes are illustrative.`
      : 'Both selected hosts comply with the defined baseline. Already verified fixes are retained; later alerts are introduced only when announced.';
    byId('source-code').textContent = step.code;
    const source = byId('source-link');
    source.href = `https://github.com/kvegh/RHEL-sniperpatching/blob/${story.sourceRevision}/${step.source}`;
    source.textContent = `${step.source} ↗`;
    byId('version-label').textContent = `Version ${story.version}`;
    updateUpstreamRoute();
  }

  function navigate(nextIndex) {
    index = Math.min(story.steps.length - 1, Math.max(0, nextIndex));
    window.history.replaceState(null, '', `#step=${story.steps[index].id}`);
    render();
  }

  byId('previous').addEventListener('click', () => navigate(index - 1));
  byId('next').addEventListener('click', () => navigate(index + 1));
  byId('restart').addEventListener('click', () => navigate(0));
  byId('motion').addEventListener('click', () => { motion = !motion; render(); });
  for (let cycle = 0; cycle < 2; cycle += 1) byId(`cycle-${cycle}`).addEventListener('click', () => navigate(story.steps.findIndex(step => step.cycle === cycle)));
  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON', 'SUMMARY', 'A'].includes(event.target.tagName)) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); navigate(index - 1); }
    if (event.key === 'ArrowRight' && !story.steps[index].kind.startsWith('approve-')) { event.preventDefault(); navigate(index + 1); }
    if (event.key.toLowerCase() === 'r') { event.preventDefault(); navigate(0); }
  });
  window.addEventListener('hashchange', () => {
    // Native section links move focus without changing the selected story action.
    if (!new URLSearchParams(window.location.hash.slice(1)).has('step')) return;
    index = indexFromHash();
    render();
  });
  window.addEventListener('resize', updateUpstreamRoute);
  if (typeof window.ResizeObserver === 'function') {
    // Follow wrapping and card-size changes as well as viewport resizes.
    const observer = new window.ResizeObserver(updateUpstreamRoute);
    for (const id of ['architecture', 'redhat-source', 'satellite-platform']) observer.observe(byId(id));
  }
  reducedMotion.addEventListener('change', event => { motion = !event.matches; render(); });
  index = indexFromHash();
  render();
}());
