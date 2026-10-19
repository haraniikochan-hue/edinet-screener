import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { MAJOR_US, EARNINGS_URL, earningsUrl, earningsDates, newYorkTime, parseEarnings, loadEarnings, upcomingEarnings } from '../dashboard/js/earnings.js';

const HOUR = 3600000;
const row = (symbol, time, extra = {}) => ({ symbol, name:`${symbol} Inc.`, time, marketCap:'$1,234,567,890', fiscalQuarterEnding:'Sep/2026',
  epsForecast:'$1.23', noOfEsts:'7', lastYearEPS:'($0.10)', lastYearRptDt:'10/21/2025', ...extra });
const page = rows => JSON.stringify({ data:{ rows } });

test('only the market movers are kept, with timing, quarter and numbers',()=>{
  assert.equal(MAJOR_US.length,25);assert.equal(new Set(MAJOR_US).size,25);
  for(const symbol of ['NVDA','AAPL','MSFT','TSM','ASML','MU','AMD','JPM'])assert.ok(MAJOR_US.includes(symbol),symbol);
  const rows=parseEarnings(page([row('META','time-after-hours'),row('SAP','time-after-hours'),row('JPM','time-pre-market'),row('PM','time-pre-market'),row('NVDA','time-not-supplied',{epsForecast:''})]),'2026-10-21');
  assert.deepEqual(rows.map(r=>r.symbol),['META','JPM','NVDA']);
  const meta=rows[0];
  assert.equal(meta.company,'META Inc.');assert.equal(meta.timing,'after');assert.equal(meta.id,'META:2026-10-21');
  assert.equal(meta.quarter,'2026年9月までの四半期');assert.equal(meta.epsForecast,1.23);assert.equal(meta.estimates,7);
  assert.equal(meta.lastYearEps,-0.1);assert.equal(meta.marketCap,1234567890);
  assert.equal(rows[1].timing,'pre');assert.equal(rows[2].timing,'unknown');assert.equal(rows[2].epsForecast,null);
  assert.throws(()=>parseEarnings('{}','2026-10-21'),/決算/);
  assert.ok(!MAJOR_US.includes('GOOG'),'Alphabet is listed once (GOOGL)');
  for(const symbol of MAJOR_US)assert.ok(existsSync(new URL(`../dashboard/assets/earnings/${symbol}.png`,import.meta.url)),`${symbol} has a logo`);
});
test('report times follow New York, including the end of daylight saving',()=>{
  // Before the open: 8:00 New York is 21:00 in Japan in October, 22:00 after 1 November
  assert.equal(newYorkTime('2026-10-21',8),Date.parse('2026-10-21T21:00:00+09:00'));
  assert.equal(newYorkTime('2026-11-03',8),Date.parse('2026-11-03T22:00:00+09:00'));
  const [pre]=parseEarnings(page([row('JPM','time-pre-market')]),'2026-10-21'),[after]=parseEarnings(page([row('META','time-after-hours')]),'2026-10-21');
  assert.equal(pre.timestamp,Date.parse('2026-10-21T21:00:00+09:00'));
  assert.equal(after.timestamp,Date.parse('2026-10-22T05:05:00+09:00'),'after the close is the next morning in Japan');
});
test('the weeks ahead are US weekdays starting from New York\'s today',()=>{
  // 01:00 on Tue 20 Oct in Japan is still Mon 19 Oct in New York
  const dates=earningsDates(Date.parse('2026-10-20T01:00:00+09:00'),14);
  assert.equal(dates[0],'2026-10-19');assert.equal(dates.length,10);
  assert.ok(dates.every(d=>![0,6].includes(new Date(`${d}T12:00Z`).getUTCDay())));
  assert.ok(EARNINGS_URL.test(earningsUrl(dates[0])));
  assert.ok(!EARNINGS_URL.test('https://api.nasdaq.com/api/calendar/earnings?date=2026-10-19&x=1'));
});
test('a calendar survives a few missing days, is sorted, and drops reports long past',async()=>{
  const now=Date.parse('2026-10-20T01:00:00+09:00'),asked=[];
  const fetchText=async url=>{
    const date=url.slice(-10);asked.push(date);
    if(date==='2026-10-23')throw new Error('timeout');
    return page(date==='2026-10-21'?[row('META','time-after-hours',{marketCap:'$2,000,000,000,000'}),row('JPM','time-pre-market')]:date==='2026-10-19'?[row('AAPL','time-after-hours')]:[]);
  };
  const result=await loadEarnings(fetchText,now);
  assert.equal(asked.length,40,'eight weeks of US weekdays');assert.equal(result.missing,1);assert.equal(result.companies,MAJOR_US.length);
  assert.deepEqual(result.events.map(e=>e.symbol),['AAPL','JPM','META']);
  assert.deepEqual(upcomingEarnings(result.events,Date.parse('2026-10-21T00:00:00+09:00')).map(e=>e.symbol),['JPM','META'],'a report two hours past drops off');
  await assert.rejects(loadEarnings(async()=>{throw new Error('down');},now),/決算予定/);
});
