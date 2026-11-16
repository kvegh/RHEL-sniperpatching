'use strict';
// Reason: verify explanatory state transitions without running infrastructure.
// Justification: ../README.md#verification.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const story = require('../src/scenario.js');
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, '../../docs/rhel94-cve-candidates.json'), 'utf8'));

function position(cycle, kind) {
  const index = story.steps.findIndex(step => step.cycle === cycle && step.kind === kind);
  assert.notEqual(index, -1, `Missing cycle ${cycle + 1} ${kind}`);
  return index;
}

for (const cycle of [0, 1]) {
  test(`cycle ${cycle + 1}: selected scenario matches the accepted CVE catalog`, () => {
    const scenario = story.scenarios[cycle];
    const recorded = catalog.candidates.find(candidate => candidate.cve === scenario.cve);
    assert.ok(recorded);
    assert.equal(scenario.advisory, recorded.advisory);
    assert.ok(scenario.cutoff >= recorded.fix_date);
    if (cycle === 0) {
      const second = catalog.candidates.find(candidate => candidate.cve === story.scenarios[1].cve);
      assert.ok(scenario.cutoff < second.fix_date, 'First broader update must leave the second example outstanding');
    }
  });

  test(`cycle ${cycle + 1}: minor publication changes availability, not installed packages`, () => {
    const index = position(cycle, 'minor');
    const before = story.stateAt(index - 1);
    const after = story.stateAt(index);
    assert.notEqual(after.testCV, before.testCV);
    assert.equal(after.prodCV, before.prodCV);
    assert.deepEqual(after.test, before.test);
    assert.deepEqual(after.prod, before.prod);
  });

  test(`cycle ${cycle + 1}: approval does not change production or promote content`, () => {
    for (const kind of ['approve-targeted', 'approve-full']) {
      const index = position(cycle, kind);
      const before = story.stateAt(index - 1);
      const approval = story.stateAt(index);
      assert.equal(approval.test.verification, 'Passed');
      assert.equal(approval.prodCV, before.prodCV);
      assert.deepEqual(approval.prod, before.prod);
      assert.notEqual(approval.testCV, approval.prodCV);
    }
  });

  test(`cycle ${cycle + 1}: exact-version promotions do not install packages`, () => {
    for (const kind of ['promote-targeted', 'full-promote']) {
      const index = position(cycle, kind);
      const before = story.stateAt(index - 1);
      const promoted = story.stateAt(index);
      assert.equal(promoted.prodCV, promoted.testCV);
      assert.deepEqual(promoted.prod, before.prod);
      assert.notEqual(promoted.prod.installedCV, promoted.prodCV);
    }
  });

  test(`cycle ${cycle + 1}: complete state has verified fixes and all offered updates on both hosts`, () => {
    const state = story.stateAt(position(cycle, 'complete'));
    const expected = story.scenarios.slice(0, cycle + 1).map(scenario => scenario.cve);
    for (const host of [state.test, state.prod]) {
      assert.deepEqual(host.fixed, expected);
      assert.equal(host.verification, 'Passed');
      assert.equal(host.status, 'All offered updates verified');
    }
    assert.equal(state.testCV, state.prodCV);
    assert.equal(state.test.installedCV, state.testCV);
    assert.equal(state.prod.installedCV, state.prodCV);
  });
}

test('kernel installation remains ineffective until the separate reboot stop', () => {
  for (const [patch, reboot, host] of [['patch-test', 'reboot-test', 'test'], ['patch-prod', 'reboot-prod', 'prod']]) {
    const installed = story.stateAt(position(1, patch))[host];
    assert.equal(installed.reboot, 'Required');
    assert.equal(installed.fixed.includes(story.scenarios[1].cve), false);
    const booted = story.stateAt(position(1, reboot))[host];
    assert.equal(booted.reboot, 'Completed');
    assert.equal(booted.fixed.includes(story.scenarios[1].cve), true);
    assert.equal(booted.verification, 'Pending');
    assert.equal(booted.fixed.includes(story.scenarios[0].cve), true);
  }
});

test('rewind, restart and repeated reads do not retain future or caller-mutated state', () => {
  const initial = story.stateAt(0);
  const firstComplete = story.stateAt(position(0, 'complete'));
  const final = story.stateAt(story.steps.length - 1);
  assert.equal(final.prod.fixed.length, 2);
  assert.deepEqual(story.stateAt(0), initial);
  assert.deepEqual(story.stateAt(position(0, 'complete')), firstComplete);
  final.test.fixed.push('caller mutation');
  final.versions.push({ version: '99.0', label: 'caller mutation' });
  assert.equal(story.stateAt(story.steps.length - 1).test.fixed.length, 2);
  assert.equal(story.stateAt(story.steps.length - 1).versions.length, 5);
});

test('every step has a unique deep link and a real code source with a prepared excerpt', () => {
  assert.equal(new Set(story.steps.map(step => step.id)).size, story.steps.length);
  assert.match(story.sourceRevision, /^[0-9a-f]{40}$/);
  const allowedRoutes = new Set(['none', 'resolve', 'content-test', 'execute-test', 'promote-prod', 'execute-prod']);
  for (const step of story.steps) {
    assert.ok(allowedRoutes.has(step.route), step.id);
    assert.ok(step.summary && step.detail && step.code, step.id);
    assert.equal(fs.existsSync(path.join(__dirname, '../..', step.source)), true, step.source);
  }
  assert.match(story.scenarios[1].description, /local user/i);
});

test('invalid and out-of-range navigation inputs clamp to a valid story stop', () => {
  assert.equal(story.stateAt(-1).index, 0);
  assert.equal(story.stateAt(NaN).index, 0);
  assert.equal(story.stateAt(Infinity).index, 0);
  assert.equal(story.stateAt(1.9).index, 1);
  assert.equal(story.stateAt(10000).index, story.steps.length - 1);
});
