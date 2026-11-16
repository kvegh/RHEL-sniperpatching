/* Actual presenter handlers exercised with built-in DOM substitutes.
 * Reason and scope: ../README.md#verification. Browser layout is a separate check.
 */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const demo = process.env.SNIPER_DEMO_DIR || path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(demo, 'index.html'), 'utf8');
const model = fs.readFileSync(path.join(demo, 'src/scenario.js'), 'utf8');
const app = fs.readFileSync(path.join(demo, 'src/app.js'), 'utf8');

class Element {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase(); this.children = []; this.attributes = {};
    this.listeners = {}; this.dataset = {}; this.className = ''; this.disabled = false;
    this.ownText = '';
    this.classList = {
      add: name => this.classes(true, name), remove: name => this.classes(false, name),
      toggle: (name, force) => this.classes(force === undefined ? !this.className.split(' ').includes(name) : force, name),
    };
  }
  classes(add, name) {
    const values = new Set(this.className.split(' ').filter(Boolean));
    if (add) values.add(name); else values.delete(name);
    this.className = [...values].join(' '); return add;
  }
  set textContent(value) { this.ownText = String(value); this.children = []; }
  get textContent() { return this.ownText + this.children.map(child => child.textContent).join(''); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; this.ownText = ''; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  addEventListener(name, handler) { (this.listeners[name] ||= []).push(handler); }
  dispatch(name, event = {}) { for (const handler of this.listeners[name] || []) handler(event); }
  click() { if (!this.disabled) this.dispatch('click'); }
}
function launch(hash = '', reduce = false) {
  const nodes = new Map();
  for (const match of html.matchAll(/<([a-z][\w-]*)\b([^>]*)>/gi)) {
    const id = /\bid="([^"]+)"/.exec(match[2]);
    if (!id) continue;
    const node = new Element(match[1]);
    node.id = id[1]; node.className = /\bclass="([^"]+)"/.exec(match[2])?.[1] || '';
    nodes.set(node.id, node);
  }
  const satellite = new Element();
  const document = new Element('document');
  document.getElementById = id => { assert.ok(nodes.has(id), `Missing real HTML element ${id}`); return nodes.get(id); };
  document.createElement = tag => new Element(tag);
  document.querySelector = selector => { assert.equal(selector, '.satellite'); return satellite; };
  const media = new Element(); media.matches = reduce;
  const window = new Element('window');
  window.location = { hash };
  window.history = { replaceState(_state, _unused, value) { window.location.hash = value; } };
  window.matchMedia = () => media;
  const context = vm.createContext({ window, document, URLSearchParams });
  vm.runInContext(model, context, { filename: 'deployed-scenario.js' });
  vm.runInContext(app, context, { filename: 'deployed-app.js' });
  return { nodes, document, window, media, story: window.SniperStory, get: id => nodes.get(id) };
}
function text(view, id) { return view.get(id).textContent; }
function at(view, cycle, kind) { return view.story.steps.find(step => step.cycle === cycle && step.kind === kind); }
function go(view, step) {
  view.window.location.hash = `#step=${step.id}`;
  view.window.dispatch('hashchange');
}

test('real HTML and scripts render the first story and restore the baseline on restart', () => {
  const v = launch();
  assert.equal(text(v, 'scenario-title'), 'All systems up to date');
  assert.equal(v.get('test-host').dataset.health, 'healthy');
  assert.equal(v.get('prod-host').dataset.health, 'healthy');
  assert.match(text(v, 'test-status'), /^✓/);
  assert.doesNotMatch(text(v, 'test-fixes'), /CVE-/);
  assert.equal(text(v, 'test-available'), 'CV 1.0');
  assert.equal(v.get('previous').disabled, true);
  v.get('next').click();
  assert.notEqual(v.window.location.hash, '#step=baseline');
  v.get('restart').click();
  assert.equal(v.window.location.hash, '#step=baseline');
  assert.equal(text(v, 'prod-installed'), 'CV 1.0');
});

test('all real Next handlers traverse both cycles and expose four approval checkpoints', () => {
  const v = launch(); let approvals = 0;
  for (let index = 0; index < v.story.steps.length; index += 1) {
    const step = v.story.steps[index];
    assert.equal(text(v, 'step-title'), step.title);
    assert.equal(text(v, 'step-count'), `SCENE ${step.scene} OF 7`);
    assert.equal(v.get('step-list').children.length, 7);
    if (step.kind.startsWith('approve-')) {
      approvals += 1;
      assert.equal(text(v, 'next'), 'Approve Prod →');
      const currentHash = v.window.location.hash;
      v.document.dispatch('keydown', { key: 'ArrowRight', target: { tagName: 'BODY' }, preventDefault() {} });
      assert.equal(v.window.location.hash, currentHash, 'Approval needs its explicit action');
    }
    v.get('next').click();
  }
  assert.equal(approvals, 4);
  assert.equal(v.get('next').disabled, true);
  assert.equal(text(v, 'prod-installed'), 'CV 3.0');
  assert.equal((text(v, 'prod-fixes').match(/Fixed/g) || []).length, 2);
  v.get('previous').click();
  assert.equal(text(v, 'step-title'), v.story.steps.at(-2).title);
});

test('publication and promotion visibly separate available content from installed packages', () => {
  const v = launch();
  go(v, at(v, 0, 'minor'));
  assert.equal(text(v, 'test-available'), 'CV 1.1');
  assert.equal(text(v, 'test-installed'), 'CV 1.0');
  go(v, at(v, 0, 'approve-targeted'));
  assert.equal(text(v, 'prod-available'), 'CV 1.0');
  assert.equal(text(v, 'prod-installed'), 'CV 1.0');
  v.get('next').click();
  assert.equal(text(v, 'prod-available'), 'CV 1.1');
  assert.equal(text(v, 'prod-installed'), 'CV 1.0');
});

test('kernel reboot and verification are separate visible steps and retain the Python fix', () => {
  const v = launch();
  v.get('cycle-1').click();
  assert.equal(v.window.location.hash, '#step=run-2-baseline');
  assert.equal(text(v, 'scenario-title'), 'All systems up to date');
  assert.equal(v.get('test-host').dataset.health, 'healthy');
  assert.doesNotMatch(text(v, 'test-fixes'), /CVE-2024-36883/);
  go(v, at(v, 1, 'patch-test'));
  assert.equal(text(v, 'test-reboot'), 'Required');
  assert.equal(text(v, 'test-verification'), 'Pending');
  assert.equal((text(v, 'test-fixes').match(/Fixed/g) || []).length, 1);
  v.get('next').click();
  assert.equal(text(v, 'test-reboot'), 'Completed');
  assert.equal(text(v, 'test-verification'), 'Pending');
  v.get('next').click();
  assert.equal(text(v, 'test-verification'), 'Passed');
});

test('workflow buttons, deep links, motion controls and source details remain usable', () => {
  const v = launch('#step=run-2-full-promote', true);
  assert.equal(text(v, 'prod-available'), 'CV 3.0');
  assert.equal(text(v, 'prod-installed'), 'CV 2.1');
  assert.equal(text(v, 'motion'), 'Motion off');
  v.get('motion').click();
  assert.equal(text(v, 'motion'), 'Motion on');
  const firstButton = v.get('step-list').children[0].children[0];
  firstButton.click();
  assert.equal(v.window.location.hash, '#step=run-2-baseline');
  v.get('step-list').children[1].children[0].click();
  assert.equal(v.window.location.hash, '#step=run-2-input');
  assert.match(v.get('source-link').href, /^https:\/\/github\.com\/kvegh\/RHEL-sniperpatching\/blob\/[a-f0-9]{40}\/playbooks\/new\//);
  assert.ok(text(v, 'source-code').includes('sniper_patch_id'));
  assert.match(text(v, 'scenario-description'), /local user/i);
  v.media.dispatch('change', { matches: true });
  assert.equal(v.get('walkthrough').dataset.motion, 'off');
});

test('an unknown deep link returns to a safe baseline', () => {
  const v = launch('#step=not-a-real-scene');
  assert.equal(text(v, 'test-installed'), 'CV 1.0');
  assert.equal(text(v, 'step-title'), v.story.steps[0].title);
});


test('CVE alerts change known host risk without revealing the next story early', () => {
  const v = launch();
  assert.equal(text(v, 'api-label'), 'HTTPS API');
  assert.equal(v.get('story-event').dataset.tone, 'healthy');
  go(v, at(v, 0, 'input'));
  assert.equal(v.get('story-event').dataset.tone, 'alert');
  assert.equal(text(v, 'api-label'), 'Query: fix available?');
  assert.match(v.get('flow-resolve').className, /is-active/);
  assert.equal(v.get('test-host').dataset.health, 'affected');
  assert.equal(v.get('prod-host').dataset.health, 'affected');
  assert.equal(text(v, 'test-verification'), 'Pending');
  assert.equal(text(v, 'prod-verification'), 'Pending');
  assert.match(text(v, 'event-title'), /Python malicious package download/);
  assert.match(text(v, 'test-fixes'), /CVE-2024-6345/);
  assert.doesNotMatch(text(v, 'test-fixes'), /CVE-2024-36883/);
  go(v, at(v, 0, 'host-scope'));
  assert.match(text(v, 'target-scope'), /Test node.*Production node/);
  assert.equal(text(v, 'api-label'), 'HTTPS API');
  assert.equal(text(v, 'cv-update'), 'CV 1.0 + fix == CV 1.1');
  assert.equal(v.get('cv-update').hidden, false);
  go(v, at(v, 0, 'complete'));
  assert.equal(v.get('test-host').dataset.health, 'healthy');
  assert.equal(v.get('story-event').dataset.tone, 'healthy');
  assert.doesNotMatch(text(v, 'prod-fixes'), /CVE-2024-36883/);
  go(v, at(v, 1, 'input'));
  assert.match(text(v, 'prod-fixes'), /CVE-2024-36883/);
  assert.equal(text(v, 'api-label'), 'Query: fix available?');
  assert.equal(v.get('cv-update').hidden, true);
  go(v, at(v, 1, 'minor'));
  assert.equal(text(v, 'cv-update'), 'CV 2.0 + fix == CV 2.1');
  assert.equal(v.get('cv-update').hidden, false);
  assert.match(text(v, 'prod-fixes'), /Python malicious package download.*Fixed/);
});

test('Red Hat supply distinguishes the single-fix request from the later bulk update', () => {
  const v = launch();
  go(v, at(v, 0, 'ensure-content'));
  assert.equal(v.get('redhat-supply').dataset.delivery, 'targeted');
  assert.equal(text(v, 'delivery-label'), 'Download fix');
  assert.equal(v.get('package-stream').children.length, 2);
  assert.match(text(v, 'package-stream'), /Selected security fix.*Required dependencies/);
  go(v, at(v, 0, 'time-passes'));
  assert.equal(v.get('story-event').dataset.tone, 'maintenance');
  assert.match(text(v, 'event-title'), /patch window/);
  assert.match(text(v, 'test-fixes'), /Fixed/);
  go(v, at(v, 0, 'full-publish'));
  assert.equal(v.get('redhat-supply').dataset.delivery, 'bulk');
  assert.equal(text(v, 'delivery-label'), 'Download updates');
  assert.ok(v.get('package-stream').children.length >= 8);
  assert.match(text(v, 'package-stream'), /Earlier fix ✓/);
  assert.equal(text(v, 'test-installed'), 'CV 1.1');
  assert.equal(text(v, 'test-available'), 'CV 2.0');
  assert.match(text(v, 'test-fixes'), /Fixed/);
  v.get('previous').click();
  assert.equal(v.get('redhat-supply').dataset.delivery, 'none');
  assert.equal(v.get('package-stream').children.length, 0);
});

test('seven scene buttons open their first action within each fixed cycle', () => {
  const v = launch();
  for (const cycle of [0, 1]) {
    v.get(`cycle-${cycle}`).click();
    for (let number = 1; number <= 7; number += 1) {
      v.get('step-list').children[number - 1].children[0].click();
      const first = v.story.steps.find(step => step.cycle === cycle && step.scene === number);
      assert.equal(v.window.location.hash, `#step=${first.id}`);
      assert.equal(text(v, 'step-count'), `SCENE ${number} OF 7`);
      assert.equal(v.get('step-list').children[number - 1].children[0].attributes['aria-current'], 'step');
    }
  }
});


test('the architecture skip link preserves the current story state', () => {
  const v = launch();
  go(v, at(v, 0, 'minor'));
  const title = text(v, 'step-title');
  assert.equal(text(v, 'test-available'), 'CV 1.1');
  v.window.location.hash = '#architecture';
  v.window.dispatch('hashchange');
  assert.equal(text(v, 'step-title'), title);
  assert.equal(text(v, 'test-available'), 'CV 1.1');
  v.get('next').click();
  assert.equal(v.window.location.hash, '#step=run-1-host-scope');
});


test('AAP orchestrates query, repository update, CV update and publication before host installation', () => {
  const v = launch();
  for (const cycle of [0, 1]) {
    go(v, at(v, cycle, 'resolve'));
    assert.equal(text(v, 'api-label'), 'Query: fix available?');
    const baseline = text(v, 'test-available');
    const installed = text(v, 'test-installed');
    v.get('next').click();
    assert.equal(v.window.location.hash, `#step=run-${cycle + 1}-trigger-sync`);
    assert.equal(text(v, 'api-label'), 'Trigger software repository update');
    assert.equal(v.get('cv-update').hidden, true);
    v.get('next').click();
    assert.equal(text(v, 'delivery-label'), 'Download fix');
    assert.equal(v.get('redhat-supply').dataset.delivery, 'targeted');
    v.get('next').click();
    assert.equal(text(v, 'api-label'), 'Trigger Content View update');
    assert.equal(text(v, 'cv-update'), `CV ${cycle + 1}.0 + fix == CV ${cycle + 1}.1`);
    assert.equal(v.get('cv-update').hidden, false);
    assert.match(text(v, 'cv-availability'), /not published yet/);
    assert.equal(text(v, 'test-available'), baseline);
    v.get('next').click();
    assert.equal(text(v, 'api-label'), 'Trigger publishing updated Content View');
    assert.match(v.get('flow-resolve').className, /is-active/);
    assert.equal(text(v, 'cv-availability'), `CV ${cycle + 1}.1 available to Test hosts`);
    assert.equal(text(v, 'test-available'), `CV ${cycle + 1}.1`);
    assert.match(v.get('test-available').className, /is-new-content/);
    assert.equal(text(v, 'test-installed'), installed);
    assert.equal(text(v, 'prod-available'), baseline);
    v.get('previous').click();
    assert.equal(text(v, 'api-label'), 'Trigger Content View update');
    assert.equal(text(v, 'test-available'), baseline);
  }
});


test('AAP launches a CVE-scoped job before clients request and receive the fix', () => {
  const v = launch();
  for (const cycle of [0, 1]) {
    for (const environment of ['test', 'prod']) {
      go(v, at(v, cycle, `deploy-${environment}`));
      const installed = text(v, `${environment}-installed`);
      assert.match(text(v, 'job-label'), new RegExp(v.story.scenarios[cycle].cve));
      assert.match(v.get(`flow-execute-${environment}`).className, /is-active/);
      assert.doesNotMatch(v.get(`flow-content-${environment}`).className, /is-active/);
      v.get('next').click();
      assert.equal(v.window.location.hash, `#step=run-${cycle + 1}-request-${environment}`);
      assert.match(v.get(`flow-content-${environment}`).className, /is-active/);
      assert.match(v.get(`flow-content-${environment}`).className, /is-requesting/);
      assert.match(text(v, 'host-content-label'), /requests fix from Satellite/);
      assert.equal(text(v, `${environment}-installed`), installed);
      v.get('next').click();
      assert.match(text(v, 'host-content-label'), /Satellite returns fix packages/);
      assert.doesNotMatch(v.get(`flow-content-${environment}`).className, /is-requesting/);
      assert.equal(text(v, `${environment}-installed`), `CV ${cycle + 1}.1`);
    }
  }
});
