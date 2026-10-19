import test from 'node:test';
import assert from 'node:assert/strict';
import { dayPart, themeFor } from '../dashboard/js/daypart.js';

const at = hhmm => Date.parse(`2026-10-20T${hhmm}:00+09:00`);
const sunrise = at('05:51'), sunset = at('17:00');

test('the time of day follows the sun: dawn and sunset light, day, night',()=>{
  const part = hhmm => dayPart(at(hhmm), sunrise, sunset);
  assert.equal(part('03:00'),'night');assert.equal(part('05:05'),'night');
  assert.equal(part('05:10'),'dusk');assert.equal(part('06:30'),'dusk');
  assert.equal(part('06:40'),'day');assert.equal(part('12:00'),'day');assert.equal(part('15:59'),'day');
  assert.equal(part('16:00'),'dusk');assert.equal(part('17:44'),'dusk');
  assert.equal(part('17:45'),'night');assert.equal(part('23:30'),'night');
});
test('without a forecast the sun is taken as 6:00 and 17:30 in Japan',()=>{
  assert.equal(dayPart(at('12:00'),NaN,NaN),'day');
  assert.equal(dayPart(at('17:00'),undefined,undefined),'dusk');
  assert.equal(dayPart(at('21:00'),NaN,NaN),'night');
});
test('the light theme goes with daytime photos only',()=>{
  assert.equal(themeFor('day'),'light');assert.equal(themeFor('dusk'),'dark');assert.equal(themeFor('night'),'dark');
});
