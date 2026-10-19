import test from 'node:test';
import assert from 'node:assert/strict';
import { chartGeometry, niceTicks, timeTicks } from '../dashboard/js/market-chart.js';
import { CHART_RANGES } from '../dashboard/js/market-definitions.js';
import { normalizeCandles } from '../dashboard/js/hyperliquid.js';

const HOUR = 3600000, DAY = 24 * HOUR, JST = 9 * HOUR;

test('detail ranges grow from a day to a year with a sensible number of candles each',()=>{
  assert.deepEqual(Object.keys(CHART_RANGES),['1d','1w','1m','3m','1y']);
  let previous=0;
  for(const spec of Object.values(CHART_RANGES)){
    assert.ok(spec.duration>previous);previous=spec.duration;
    const candles=spec.duration/spec.intervalMs;
    assert.ok(candles>=90 && candles<=400,`${spec.name}: ${candles} candles`);
    assert.ok(spec.name && spec.bar);
  }
});
test('longer ranges normalise their own candle interval',()=>{
  const end=Date.UTC(2026,9,19),spec=CHART_RANGES['1w'];
  const rows=[0,1,2].map(i=>({s:'BTC',i:spec.interval,t:end-3*HOUR+i*HOUR,T:end-2*HOUR+i*HOUR-1,o:'100',c:String(101+i)}));
  const series=normalizeCandles(rows,{coin:'BTC',range:'1w',end});
  assert.equal(series.intervalMs,HOUR);assert.equal(series.points.length,3);assert.equal(series.baseline,100);
  // A 15-minute candle is not a 1-hour one
  assert.throws(()=>normalizeCandles(rows.map(r=>({...r,i:'15m'})),{coin:'BTC',range:'1w',end}),/履歴/);
});
test('price scale uses round steps and the decimals they need',()=>{
  const a=niceTicks(7601,7735,5);
  assert.equal(a.step,25);assert.deepEqual(a.ticks,[7625,7650,7675,7700,7725]);assert.equal(a.decimals,0);
  const b=niceTicks(157.9,158.6,5);
  assert.ok(Math.abs(b.step-.1)<1e-12 || Math.abs(b.step-.2)<1e-12);assert.equal(b.decimals,1);
  assert.ok(b.ticks.every(t=>t>=157.9 && t<=158.6));
  const flat=niceTicks(5,5);assert.ok(flat.ticks.length>=2);
});
test('time marks follow Japan time: hours in a day, months in a year',()=>{
  const end=Date.UTC(2026,9,19,15,0)-JST+HOUR*0; // 10/19 15:00 JST
  const day=timeTicks(end-DAY,end);
  assert.ok(day.length>=4 && day.length<=7);
  assert.ok(day.every(t=>(t.time+JST)%(4*HOUR)===0));
  assert.ok(day.some(t=>t.label==='10/19'),'midnight shows the date');
  assert.ok(day.some(t=>t.label==='20:00'));
  const year=timeTicks(end-365*DAY,end);
  assert.ok(year.length>=4 && year.length<=7);
  assert.ok(year.every(t=>new Date(t.time+JST).getUTCDate()===1 && new Date(t.time+JST).getUTCHours()===0));
  assert.ok(year.some(t=>t.label==='2026年'),'January shows its year');
});
test('chart geometry can inset the plot and fix its value range',()=>{
  const series={start:0,end:100,intervalMs:100,baseline:10,points:[{time:0,value:10},{time:100,value:20}]};
  const plain=chartGeometry(series,160,52);
  assert.equal(plain.paths[0].points[0].x,4);assert.equal(plain.paths[0].points[1].y,7);
  const framed=chartGeometry(series,200,100,{left:0,right:40,top:20,bottom:20,lo:0,hi:40});
  assert.equal(framed.paths[0].points[1].x,160);
  assert.equal(framed.paths[0].points[0].y,100-20-10/40*60);
  assert.equal(framed.baseline,100-20-10/40*60);
});
