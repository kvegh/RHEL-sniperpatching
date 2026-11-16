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
    const id = new URLSearchParams(window.location.hash.slice(1)).get('step');
    const found = story.steps.findIndex(step => step.id === id);
    return found < 0 ? 0 : found;
  }

  function element(tag, className, text) {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text !== undefined) item.textContent = text;
    return item;
  }

  function renderHost(name, host, available, announced, currentCve) {
    byId(`${name}-host`).dataset.health = host.health;
    byId(`${name}-available`).textContent = `CV ${available}`;
    byId(`${name}-installed`).textContent = `CV ${host.installedCV}`;
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
    if (step.scene === 1) return ['healthy', 'BASELINE VERIFIED', 'All systems up to date', `Test and Prod verified on baseline CV ${state.testCV}.`];
    if (step.scene === 2) return ['alert', 'NEW SECURITY ALERT', state.scenario.title, `${state.scenario.cve} is announced and named to AAP. Only this newly announced issue changes the hosts’ security status.`];
    if (step.scene === 3) return ['content', 'RED HAT CONTENT', 'One fix, scoped content', 'AAP asks Satellite to ensure the required fix is available from synchronized Red Hat content.'];
    if (step.scene === 4) return ['content', 'TARGETED CONTENT VIEW', 'Baseline + selected fix + dependencies', `CV ${state.testCV} is available to Test. Publishing content has not installed packages on either host.`];
    if (approval) return ['approval', 'OPERATOR CHECKPOINT', 'Test passed. Approve production.', 'Prod stays on its current content and installed packages until the operator continues with the exact tested version.'];
    if (step.kind === 'verify-prod') return ['healthy', 'TARGETED FIX VERIFIED', 'Both hosts have the selected fix', 'The urgent vulnerability is addressed. Broader routine updates will follow at the maintenance window.'];
    if (step.kind === 'time-passes') return ['maintenance', 'TIME PASSES', 'The next patch window approaches', 'The urgent fix stays installed while new security fixes, bug fixes and enhancements accumulate.'];
    if (step.scene === 6) return ['maintenance', 'REGULAR PATCH WINDOW', 'New updates pour in', `Satellite prepares broader content through ${state.scenario.cutoff}, retaining the already-applied security fix.`];
    if (step.kind === 'complete') return ['healthy', 'BASELINE VERIFIED', 'All systems up to date', `Both hosts are verified on CV ${state.testCV}. ${step.cycle === 0 ? 'The next run starts healthy before a new CVE is announced.' : 'Both fixed examples have completed their targeted and regular maintenance cycles.'}`];
    return ['info', step.scene === 5 ? 'TARGETED ROLLOUT' : 'BROADER ROLLOUT', step.title, 'Check the selected Test and Prod hosts, apply only the required package changes, and verify the result.'];
  }

  function renderEvent(step, state, approval) {
    const [tone, kicker, title, detail] = eventContent(step, state, approval);
    byId('story-event').dataset.tone = tone;
    byId('event-kicker').textContent = kicker;
    byId('event-title').textContent = title;
    byId('event-detail').textContent = detail;
  }

  function renderDelivery(state) {
    byId('redhat-supply').dataset.delivery = state.delivery;
    const labels = state.delivery === 'targeted'
      ? ['Selected security fix', 'Required dependencies']
      : state.delivery === 'bulk'
        ? ['Earlier fix ✓', 'Security updates', 'Bug fixes', 'Enhancements', 'Libraries', 'System tools', 'Drivers', 'Package updates', 'Maintenance fixes']
        : [];
    byId('delivery-label').textContent = state.delivery === 'targeted'
      ? 'Ensure the selected fix is available'
      : state.delivery === 'bulk' ? 'Regular maintenance content arrives' : 'Red Hat content → Satellite';
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
    byId('scene-progress').textContent = actions.length > 1 ? `Action ${actionNumber} of ${actions.length}` : '';
    byId('step-title').textContent = step.title;
    byId('step-summary').textContent = step.summary;
    byId('phase-label').textContent = step.phase;
    byId('phase-badge').textContent = approval ? 'Approval required' : step.phase;
    byId('job-label').textContent = state.job;
    byId('binding-test').textContent = `CV ${state.testCV}`;
    byId('binding-prod').textContent = `CV ${state.prodCV}`;
    const affected = [['Test node', state.test], ['Production node', state.prod]]
      .filter(([, host]) => state.announced.some(cve => !host.fixed.includes(cve)))
      .map(([name]) => name);
    byId('target-scope').textContent = affected.length ? `Affected in selected scope: ${affected.join(' · ')}` : 'Selected scope: Test node · Production node';
    byId('previous').disabled = index === 0;
    byId('next').disabled = index === story.steps.length - 1;
    byId('next').textContent = approval ? 'Approve Prod →' : index === story.steps.length - 1 ? 'Complete ✓' : 'Next →';
    byId('next').classList.toggle('approval', approval);
    byId('motion').textContent = motion ? 'Motion on' : 'Motion off';
    byId('motion').setAttribute('aria-pressed', String(motion));
    for (let cycle = 0; cycle < 2; cycle += 1) byId(`cycle-${cycle}`).setAttribute('aria-pressed', String(step.cycle === cycle));
    renderHost('test', state.test, state.testCV, state.announced, state.scenario.cve);
    renderHost('prod', state.prod, state.prodCV, state.announced, state.scenario.cve);
    renderEvent(step, state, approval);
    renderDelivery(state);
    for (const route of routeNames) byId(`flow-${route}`).classList.toggle('is-active', step.route === route);
    // Package bytes flow from Satellite; the host is the repository client.
    if (step.route === 'execute-test') byId('flow-content-test').classList.add('is-active');
    if (step.route === 'execute-prod') byId('flow-content-prod').classList.add('is-active');
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
  reducedMotion.addEventListener('change', event => { motion = !event.matches; render(); });
  index = indexFromHash();
  render();
}());
