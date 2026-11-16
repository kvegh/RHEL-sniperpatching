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
  assert.equal(text(v, 'scenario-title'), 'Python malicious package download');
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
    assert.equal(text(v, 'step-count'), `STEP ${index + 1} OF ${v.story.steps.length}`);
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
  assert.equal(text(v, 'scenario-title'), 'Network Privilege Escalation');
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
