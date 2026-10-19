import test from 'node:test';
import assert from 'node:assert/strict';
import { parseEconomicICS, fomcEvents, mergeCalendar } from '../lib/economic-calendar.mjs';
import { eventPage, upcomingEvents, jstDay } from '../dashboard/js/calendar.js';
const event=(summary,date,extras='')=>`BEGIN:VEVENT\nSUMMARY:${summary}\nDTSTART${date}\n${extras}\nEND:VEVENT\n`;

test('official Eastern releases convert through US daylight saving and JST midnight',()=>{
  const rows=parseEconomicICS(event('Employment Situation',';TZID=US-Eastern:20261002T083000')+event('Employment Situation',';TZID=US-Eastern:20261106T083000')+event('Job Openings and Labor Turnover Survey',';TZID=US-Eastern:20261103T100000'),'BLS');
  assert.deepEqual(rows.map(r=>new Date(r.timestamp).toISOString()),['2026-10-02T12:30:00.000Z','2026-11-03T15:00:00.000Z','2026-11-06T13:30:00.000Z']);
  assert.equal(jstDay(rows[1].timestamp),'2026-11-04');
  assert.equal(rows[2].indicator,'NFP');
});
test('BEA UTC times, folded titles and GDP estimate stages retain separate simultaneous releases',()=>{
  const text=event('GDP (Advance Estimate)\\, 3rd Quarter 2026',':20261029T123000Z')+event('Personal Income and \n Outlays\\, September 2026',':20261029T123000Z')+event('GDP (Second Estimate) and Corporate Profits\\, 3rd Quarter 2026',':20261125T133000Z');
  const rows=parseEconomicICS(text,'BEA');
  assert.equal(rows.length,3);assert.equal(rows[0].title,'GDP 速報値');assert.equal(rows[1].indicator,'PCE');assert.equal(rows[0].timestamp,rows[1].timestamp);assert.equal(rows[2].title,'GDP 改定値');
});
test('calendar skips cancelled, malformed, all-day and unverified timezone entries without guessing',()=>{
  const good=event('Consumer Price Index',';TZID=America/New_York:20261110T083000');
  const rows=parseEconomicICS(good+event('Producer Price Index',';TZID=UTC:20261110T083000')+event('Consumer Price Index',':20261110T083000')+event('Employment Situation',';VALUE=DATE:20261106')+event('Consumer Price Index',';TZID=US-Eastern:20261310T083000')+event('Employment Situation',';TZID=US-Eastern:20261106T083000','STATUS:CANCELLED'),'BLS');
  assert.equal(rows.length,1);assert.equal(rows[0].indicator,'CPI');
  assert.throws(()=>parseEconomicICS(event('Unrelated report',':20261110T083000Z'),'BLS'),/見つかりません/);
});
test('a revised or cancelled UID supersedes its older schedule',()=>{
  const rows=parseEconomicICS(event('Consumer Price Index',';TZID=US-Eastern:20261110T083000','UID:cpi\nSEQUENCE:0')+event('Consumer Price Index',';TZID=US-Eastern:20261112T083000','UID:cpi\nSEQUENCE:1')+event('Employment Situation',';TZID=US-Eastern:20261106T083000','UID:jobs\nSEQUENCE:0')+event('Employment Situation',';TZID=US-Eastern:20261106T083000','UID:jobs\nSEQUENCE:1\nSTATUS:CANCELLED'),'BLS');
  assert.equal(rows.length,1);assert.equal(new Date(rows[0].timestamp).toISOString(),'2026-11-12T13:30:00.000Z');
});
test('FOMC is a policy announcement at the stated scheduled ET time, not an invented release result',()=>{
  const rows=fomcEvents({meetings:['2026-10-28','2026-12-09']});
  assert.deepEqual(rows.map(r=>new Date(r.timestamp).toISOString()),['2026-10-28T18:00:00.000Z','2026-12-09T19:00:00.000Z']);
  assert.equal(jstDay(rows[0].timestamp),'2026-10-29');assert.ok(rows.every(r=>!('actual' in r) && !('forecast' in r)));
});
test('upcoming pages preserve simultaneous events, reject invalid entries, and clamp after expiry',()=>{
  const all=mergeCalendar([fomcEvents({meetings:['2026-10-28']}),parseEconomicICS(event('GDP (Advance Estimate)',':20261029T123000Z')+event('Personal Income and Outlays',':20261029T123000Z'),'BEA')]);
  const before=Date.parse('2026-10-18T00:00Z'),after=Date.parse('2026-10-29T20:00Z');
  assert.equal(upcomingEvents([...all,all[0],null,{timestamp:before}],before).length,3);
  const first=eventPage(all,0,2,before),last=eventPage(all,99,2,before);
  assert.equal(first.events.length,2);assert.equal(last.index,1);assert.equal(last.events.length,1);
  assert.equal(eventPage(all,10,2,after).events.length,0);assert.equal(eventPage(all,10,2,after).index,0);
});
