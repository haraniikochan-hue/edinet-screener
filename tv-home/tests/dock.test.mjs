import test from 'node:test';
import assert from 'node:assert/strict';
import { arrangeDock, moveInDock, setOnDock, normalizeDock } from '../dashboard/js/dock.js';

const apps = [['SmartTube','org.smarttube.stable'],['Netflix','com.netflix.ninja'],['ABEMA','tv.abema'],['ブラウザー','com.internet.tvbrowser']]
  .map(([name, packageName]) => ({ name, packageName }));
const names = list => list.map(app => app.name);

test('without preferences the dock keeps the launcher order and lists every app by name', () => {
  const { dock, all } = arrangeDock(apps, undefined);
  assert.deepEqual(names(dock), ['SmartTube','Netflix','ABEMA','ブラウザー']);
  assert.deepEqual(names(all), ['ABEMA','Netflix','SmartTube','ブラウザー']);
});

test('apps taken off the dock stay in the app list and can come back', () => {
  let prefs = setOnDock({}, 'com.internet.tvbrowser', false);
  assert.deepEqual(names(arrangeDock(apps, prefs).dock), ['SmartTube','Netflix','ABEMA']);
  assert.equal(arrangeDock(apps, prefs).all.length, 4);
  prefs = setOnDock(prefs, 'com.internet.tvbrowser', true);
  assert.deepEqual(names(arrangeDock(apps, prefs).dock), ['SmartTube','Netflix','ABEMA','ブラウザー']);
});

test('moving swaps neighbours, stops at the ends, and new installs join the end', () => {
  const shown = arrangeDock(apps, {}).dock.map(app => app.packageName);
  let prefs = moveInDock({}, shown, 'tv.abema', -1);
  assert.deepEqual(names(arrangeDock(apps, prefs).dock), ['SmartTube','ABEMA','Netflix','ブラウザー']);
  assert.deepEqual(moveInDock(prefs, shown, 'org.smarttube.stable', -1).order, prefs.order);
  const installed = [...apps, { name:'TVer', packageName:'jp.co.tver.tvapp' }];
  assert.deepEqual(names(arrangeDock(installed, prefs).dock).at(-1), 'TVer');
});

test('stored preferences are cleaned of anything that is not a package name', () => {
  assert.deepEqual(normalizeDock({ order:['a.b','a.b','javascript:x',3], hidden:'x' }), { order:['a.b'], hidden:[] });
});
