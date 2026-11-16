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
    assert.equal(story.steps[index].title, 'Trigger publishing updated Content View');
    assert.equal(after.job, 'Trigger publishing updated Content View');
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
      const { health: beforeHealth, ...beforeInstalled } = before.prod;
      const { health: promotedHealth, ...promotedInstalled } = promoted.prod;
      assert.deepEqual(promotedInstalled, beforeInstalled);
      assert.equal(promotedHealth, kind === 'full-promote' ? 'updates' : beforeHealth);
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
  final.announced.push('caller mutation');
  assert.equal(story.stateAt(story.steps.length - 1).test.fixed.length, 2);
  assert.equal(story.stateAt(story.steps.length - 1).versions.length, 5);
  assert.equal(story.stateAt(story.steps.length - 1).announced.length, 2);
});

test('every step has a unique deep link and a real code source with a prepared excerpt', () => {
  assert.equal(new Set(story.steps.map(step => step.id)).size, story.steps.length);
  assert.match(story.sourceRevision, /^[0-9a-f]{40}$/);
  const allowedRoutes = new Set(['none', 'resolve', 'content-test', 'execute-test', 'promote-prod', 'execute-prod', 'request-test', 'request-prod', 'upstream']);
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


test('both fixed cycles follow all seven explanatory scenes in order', () => {
  assert.equal(story.steps.length, 52);
  assert.deepEqual(story.scenes.map(scene => [scene.number, scene.title]), [
    [1, 'All systems up to date'], [2, 'CVE announced'],
    [3, 'Ensure fix content is available'], [4, 'Publish targeted CV'],
    [5, 'Apply selected fix'], [6, 'Routine patch window'], [7, 'Apply broader updates'],
  ]);
  for (const cycle of [0, 1]) {
    const scenes = story.steps.filter(step => step.cycle === cycle).map(step => step.scene);
    assert.deepEqual([...new Set(scenes)], [1, 2, 3, 4, 5, 6, 7]);
    assert.deepEqual(scenes, [...scenes].sort((left, right) => left - right));
    assert.equal(position(cycle, 'resolve') + 1, position(cycle, 'trigger-sync'));
    assert.equal(position(cycle, 'trigger-sync') + 1, position(cycle, 'ensure-content'));
    assert.equal(position(cycle, 'ensure-content') + 1, position(cycle, 'cv-build'));
    assert.equal(position(cycle, 'cv-build') + 1, position(cycle, 'minor'));
    assert.equal(story.steps[position(cycle, 'cv-build')].scene, 4);
    assert.equal(story.steps[position(cycle, 'trigger-sync')].scene, 3);
    assert.equal(story.steps[position(cycle, 'baseline')].scene, 1);
    assert.equal(story.steps[position(cycle, 'host-scope')].scene, 5);
    assert.equal(position(cycle, 'host-scope') + 1, position(cycle, 'deploy-test'));
    assert.equal(position(cycle, 'deploy-test') + 1, position(cycle, 'request-test'));
    assert.equal(position(cycle, 'request-test') + 1, position(cycle, 'patch-test'));
    assert.ok(position(cycle, 'verify-test') < position(cycle, 'approve-targeted'));
    assert.ok(position(cycle, 'approve-targeted') < position(cycle, 'promote-targeted'));
    assert.equal(position(cycle, 'promote-targeted') + 1, position(cycle, 'deploy-prod'));
    assert.equal(position(cycle, 'deploy-prod') + 1, position(cycle, 'request-prod'));
    assert.equal(position(cycle, 'request-prod') + 1, position(cycle, 'patch-prod'));
    assert.equal(story.steps[position(cycle, 'time-passes')].scene, 6);
  }
});

test('every cycle starts green and reveals its CVE only when the announcement arrives', () => {
  for (const cycle of [0, 1]) {
    const baseline = story.stateAt(position(cycle, 'baseline'));
    const prior = story.scenarios.slice(0, cycle).map(scenario => scenario.cve);
    assert.deepEqual(baseline.announced, prior);
    for (const host of [baseline.test, baseline.prod]) {
      assert.equal(host.health, 'healthy');
      assert.equal(host.verification, 'Passed');
      assert.deepEqual(host.fixed, prior);
    }
    const alert = story.stateAt(position(cycle, 'input'));
    assert.deepEqual(alert.announced, story.scenarios.slice(0, cycle + 1).map(scenario => scenario.cve));
    assert.equal(alert.test.health, 'affected');
    assert.equal(alert.prod.health, 'affected');
    assert.equal(alert.test.fixed.includes(story.scenarios[cycle].cve), false);
  }
  assert.equal(story.steps[position(0, 'baseline')].id, 'baseline');
  assert.equal(story.steps[position(1, 'baseline')].id, 'run-2-baseline');
  const prior = story.stateAt(position(0, 'complete'));
  const next = story.stateAt(position(1, 'baseline'));
  for (const key of ['test', 'prod', 'testCV', 'prodCV', 'versions', 'announced']) {
    assert.deepEqual(next[key], prior[key], `Second baseline must preserve ${key}`);
  }
});

test('targeted and bulk content deliveries occur only at their explanatory stops', () => {
  for (let index = 0; index < story.steps.length; index += 1) {
    const step = story.steps[index];
    const state = story.stateAt(index);
    const expected = step.kind === 'ensure-content' ? 'targeted'
      : step.kind === 'full-publish' ? 'bulk' : 'none';
    assert.equal(state.delivery, expected, step.id);
    assert.equal(state.maintenance, step.scene === 6, step.id);
    if (step.kind === 'trigger-sync') {
      assert.equal(step.route, 'resolve');
      assert.equal(step.title, 'Trigger software repository update');
      assert.match(step.detail, /explanatory mockup/i);
      assert.match(step.detail, /full-publication.*explicitly synchronizes/i);
      assert.match(step.detail, /does not launch a per-CVE/i);
      assert.equal(state.job, 'Trigger software repository update');
      const before = story.stateAt(index - 1);
      for (const key of ['testCV', 'prodCV', 'versions', 'test', 'prod']) {
        assert.deepEqual(state[key], before[key], `Repository trigger must not change ${key}`);
      }
    }
    if (step.kind === 'cv-build') {
      assert.equal(step.route, 'resolve');
      assert.equal(step.title, 'Trigger Content View update');
      assert.equal(state.job, 'Trigger Content View update');
      assert.match(step.detail, /does not publish/i);
      const before = story.stateAt(index - 1);
      for (const key of ['testCV', 'prodCV', 'versions', 'test', 'prod']) {
        assert.deepEqual(state[key], before[key], `CV composition must not change ${key}`);
      }
    }
    if (['deploy-test', 'request-test', 'deploy-prod', 'request-prod'].includes(step.kind)) {
      const target = step.kind.endsWith('test') ? 'test' : 'prod';
      assert.equal(step.scene, 5);
      assert.equal(step.route, step.kind.startsWith('request-') ? `request-${target}` : `execute-${target}`);
      assert.ok(step.title.includes(story.scenarios[step.cycle].cve));
      assert.ok(state.job.includes(story.scenarios[step.cycle].cve));
      assert.match(step.detail, /dependencies/i);
      assert.equal(step.source, 'playbooks/new/patch_hosts.yml');
      const before = story.stateAt(index - 1);
      for (const key of ['testCV', 'prodCV', 'versions', 'test', 'prod']) {
        assert.deepEqual(state[key], before[key], `Deployment/request stop must not change ${key}`);
      }
    }
    if (step.kind === 'ensure-content') {
      assert.equal(step.route, 'upstream');
      assert.match(step.detail, /already synchronized/i);
      assert.match(step.detail, /does not launch a new per-CVE/i);
    }
  }
});

test('health follows announced risk, verification, available updates and completed state', () => {
  for (const cycle of [0, 1]) {
    assert.equal(story.stateAt(position(cycle, 'approve-targeted')).test.health, 'healthy');
    assert.equal(story.stateAt(position(cycle, 'approve-targeted')).prod.health, 'affected');
    assert.equal(story.stateAt(position(cycle, 'full-publish')).test.health, 'updates');
    assert.equal(story.stateAt(position(cycle, 'full-test')).test.health, 'healthy');
    assert.equal(story.stateAt(position(cycle, 'full-promote')).prod.health, 'updates');
    assert.equal(story.stateAt(position(cycle, 'complete')).prod.health, 'healthy');
    assert.equal(story.stateAt(position(cycle, 'time-passes')).maintenance, true);
  }
  assert.equal(story.stateAt(position(0, 'patch-test')).test.health, 'verifying');
  assert.equal(story.stateAt(position(1, 'patch-test')).test.health, 'affected');
  assert.equal(story.stateAt(position(1, 'reboot-test')).test.health, 'verifying');
});

test('applicability explanation keeps the explicitly selected pair instead of discovering a fleet', () => {
  for (const cycle of [0, 1]) {
    const scope = story.steps[position(cycle, 'host-scope')];
    assert.match(scope.detail, /explicitly selected/i);
    assert.match(scope.detail, /does not discover or automatically select an entire fleet/i);
    assert.equal(scope.source, 'playbooks/new/tasks/host_context.yml');
  }
});
