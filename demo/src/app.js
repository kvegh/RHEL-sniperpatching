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
  function renderHost(name, state, available) {
    byId(`${name}-available`).textContent = `CV ${available}`;
    byId(`${name}-installed`).textContent = `CV ${state.installedCV}`;
    byId(`${name}-status`).textContent = state.status;
    byId(`${name}-reboot`).textContent = state.reboot;
    byId(`${name}-verification`).textContent = state.verification;
    byId(`${name}-fixes`).replaceChildren(...story.scenarios.map(scenario => {
      const fixed = state.fixed.includes(scenario.cve);
      const row = element('div', 'fix-row');
      const label = element('div', 'fix-name', scenario.title);
      label.append(element('small', '', scenario.cve));
      row.append(label, element('span', `fix-state${fixed ? ' fixed' : ''}`, fixed ? 'Fixed' : 'Pending'));
      return row;
    }));
  }
  function render() {
    const state = story.stateAt(index);
    const step = story.steps[index];
    const approval = step.kind.startsWith('approve-');
    root.classList.toggle('is-approval', approval);
    root.dataset.motion = motion ? 'on' : 'off';
    byId('run-label').textContent = `RUN 0${step.cycle + 1} / 02`;
    byId('scenario-title').textContent = state.scenario.title;
    byId('scenario-cve').textContent = `${state.scenario.cve} · ${state.scenario.advisory}`;
    byId('step-count').textContent = `STEP ${index + 1} OF ${story.steps.length}`;
    byId('step-title').textContent = step.title;
    byId('step-summary').textContent = step.summary;
    byId('phase-label').textContent = step.phase;
    byId('phase-badge').textContent = approval ? 'Approval required' : step.phase;
    byId('job-label').textContent = state.job;
    byId('binding-test').textContent = `CV ${state.testCV}`;
    byId('binding-prod').textContent = `CV ${state.prodCV}`;
    byId('previous').disabled = index === 0;
    byId('next').disabled = index === story.steps.length - 1;
    byId('next').textContent = approval ? 'Approve Prod →' : index === story.steps.length - 1 ? 'Complete ✓' : 'Next →';
    byId('next').classList.toggle('approval', approval);
    byId('motion').textContent = motion ? 'Motion on' : 'Motion off';
    byId('motion').setAttribute('aria-pressed', String(motion));
    for (let cycle = 0; cycle < 2; cycle += 1) byId(`cycle-${cycle}`).setAttribute('aria-pressed', String(step.cycle === cycle));
    renderHost('test', state.test, state.testCV);
    renderHost('prod', state.prod, state.prodCV);
    for (const route of routeNames) byId(`flow-${route}`).classList.toggle('is-active', step.route === route);
    // Package bytes flow from Satellite; the host is the repository client.
    if (step.route === 'execute-test') byId('flow-content-test').classList.add('is-active');
    if (step.route === 'execute-prod') byId('flow-content-prod').classList.add('is-active');
    byId('test-host').classList.toggle('is-active', step.route === 'execute-test' || step.route === 'content-test');
    byId('prod-host').classList.toggle('is-active', step.route === 'execute-prod' || step.route === 'content-prod');
    document.querySelector('.satellite').classList.toggle('is-promoting', step.route === 'promote-prod');
    byId('step-list').replaceChildren(...story.steps.flatMap((item, itemIndex) => {
      if (item.cycle !== step.cycle) return [];
      const row = element('li', itemIndex < index ? 'is-complete' : '');
      const button = element('button');
      button.type = 'button';
      if (itemIndex === index) button.setAttribute('aria-current', 'step');
      button.append(element('span', 'step-number', itemIndex < index ? '✓' : String(itemIndex + 1)), element('span', '', item.title));
      button.addEventListener('click', () => navigate(itemIndex));
      row.append(button);
      return [row];
    }));
    byId('version-list').replaceChildren(...state.versions.map(version => {
      const row = element('li');
      const content = element('div', 'version-item');
      content.append(element('strong', '', `CV ${version.version}`), element('span', '', version.label));
      row.append(content);
      return row;
    }));
    byId('technical-description').textContent = step.detail;
    byId('scenario-description').textContent = `${state.scenario.description} Full-update content cutoff: ${state.scenario.cutoff}. CV numbers and outcomes are illustrative.`;
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
  window.addEventListener('hashchange', () => { index = indexFromHash(); render(); });
  reducedMotion.addEventListener('change', event => { motion = !event.matches; render(); });
  index = indexFromHash();
  render();
}());
