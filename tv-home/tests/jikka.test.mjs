import test from 'node:test';
import assert from 'node:assert/strict';
import { arrangeInputs, lastUsedLabel } from '../dashboard/js/jikka.js';

test('HDMI 1 and the TV app lead the inputs, the rest follow in order', () => {
  const inputs = [
    { id:'tv', label:'テレビ', kind:'tv', connected:true },
    { id:'hw2', label:'HDMI 1', kind:'hdmi', connected:true },
    { id:'hw3', label:'HDMI 2', kind:'hdmi', connected:true },
    { id:'hw5', label:'AV', kind:'av', connected:false },
  ];
  const { main, others } = arrangeInputs(inputs);
  assert.deepEqual(main.map(i => i.id), ['hw2', 'tv']);
  assert.deepEqual(others.map(i => i.id), ['hw3', 'hw5']);
});

test('inputs without HDMI 1 or the TV app, and malformed entries', () => {
  assert.deepEqual(arrangeInputs([{ id:'hw3', label:'HDMI 2', kind:'hdmi' }]).main.map(i => i.id), ['hw3']);
  assert.deepEqual(arrangeInputs(null), { main:[], others:[] });
  assert.deepEqual(arrangeInputs([{ id:1 }, { label:'x' }]), { main:[], others:[] });
});

test('last used reads as today with the time, yesterday, or days ago in Japan time', () => {
  const now = Date.parse('2026-10-20T12:00:00Z'); // 21:00 JST
  assert.equal(lastUsedLabel(Date.parse('2026-10-20T10:20:00Z'), now), '今日 19:20');
  assert.equal(lastUsedLabel(Date.parse('2026-10-19T15:30:00Z'), now), '今日 00:30');
  assert.equal(lastUsedLabel(Date.parse('2026-10-19T12:00:00Z'), now), '昨日');
  assert.equal(lastUsedLabel(Date.parse('2026-10-16T12:00:00Z'), now), '4日前');
});
