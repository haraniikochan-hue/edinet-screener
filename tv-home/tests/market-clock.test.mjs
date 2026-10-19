import test from 'node:test';
import assert from 'node:assert/strict';
import {marketStatus,sessionFor,nyInstant,countdown} from '../dashboard/js/market-clock.js';
test('NY market open converts correctly on both sides of the US DST boundary',()=>{
  assert.equal(nyInstant('2026-03-06',9,30).toISOString(),'2026-03-06T14:30:00.000Z');
  assert.equal(nyInstant('2026-03-09',9,30).toISOString(),'2026-03-09T13:30:00.000Z');
  assert.equal(nyInstant('2026-11-02',9,30).toISOString(),'2026-11-02T14:30:00.000Z');
  assert.equal(marketStatus(new Date('2026-03-09T13:29:59Z')).state,'closed');
  assert.equal(marketStatus(new Date('2026-03-09T13:30:00Z')).state,'open');
});
test('holidays, weekends, and next open are based on New York dates',()=>{
  assert.equal(sessionFor('2026-04-03'),null); // Good Friday
  assert.equal(sessionFor('2026-07-03'),null); // Independence Day observed
  const sunday=marketStatus(new Date('2026-10-18T18:00:00Z'));
  assert.equal(sunday.state,'closed');assert.equal(sunday.target.toISOString(),'2026-10-19T13:30:00.000Z');
  assert.ok(sunday.progress>0 && sunday.progress<1);
  assert.equal(marketStatus(new Date('2026-11-26T15:00:00Z')).target.toISOString(),'2026-11-27T14:30:00.000Z');
});
test('early closes end at 13:00 Eastern, never normal 16:00',()=>{
  const before=marketStatus(new Date('2026-11-27T17:59:00Z'));
  assert.equal(before.state,'open');assert.equal(before.remaining,60000);assert.match(before.label,/短縮/);
  const after=marketStatus(new Date('2026-11-27T18:00:00Z'));
  assert.equal(after.state,'closed');assert.equal(after.target.toISOString(),'2026-11-30T14:30:00.000Z');
  assert.equal(sessionFor('2028-07-03').close.toISOString(),'2028-07-03T17:00:00.000Z');
});
test('year end handles the Saturday New Year exception and fails closed beyond coverage',()=>{
  assert.ok(sessionFor('2027-12-31'));
  assert.equal(marketStatus(new Date('2029-01-03T16:00:00Z')).state,'unknown');
  assert.equal(marketStatus(new Date('2028-12-29T22:00:00Z')).state,'unknown');
});
test('countdown does not say zero minutes before the opening boundary',()=>{
  assert.equal(countdown(1),'0時間01分');assert.equal(countdown(90060000),'1日 1時間01分');
});
