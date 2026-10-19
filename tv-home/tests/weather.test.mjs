import test from 'node:test';
import assert from 'node:assert/strict';
import { HOUR, weatherTimestamp, weatherIsStale, hourlyForecast, temperatureTrend, weatherSymbol, dailyForecast, windDirection, uvLabel } from '../dashboard/js/weather.js';
import { getWeather } from '../dashboard/js/data.js';

const start=Date.parse('2026-10-19T23:40:00+09:00');
function forecast() {
  return {current:{time:'2026-10-19T23:30',temperature_2m:18},daily:{time:['2026-10-19','2026-10-20']},hourly:{
    time:['2026-10-19T23:00',...Array.from({length:8},(_,i)=>`2026-10-20T0${i}:00`)],
    temperature_2m:[18,17,16,15,14,13,12,11,10],
    precipitation_probability:[0,0,10,30,60,90,100,90,80],
    weather_code:[0,0,2,3,61,63,95,61,3],is_day:[0,0,0,0,0,0,0,1,1],
  }};
}
test('six hourly forecasts start at the next full JST hour and label the midnight rollover',()=>{
  const rows=hourlyForecast(forecast(),start);
  assert.equal(rows.length,6);
  assert.equal(rows[0].timestamp,Date.parse('2026-10-20T00:00:00+09:00'));
  assert.equal(rows[0].label,'明日 0時');assert.equal(rows[5].label,'5時');
  assert.deepEqual(rows.map(row=>row.temperature),[17,16,15,14,13,12]);
  const afterMidnight=hourlyForecast(forecast(),Date.parse('2026-10-20T00:05:00+09:00'));
  assert.equal(afterMidnight[0].label,'1時');assert.equal(afterMidnight[0].temperature,16);
});
test('a missing hour never compresses time and missing fields never become dry weather or zero degrees',()=>{
  const data=forecast();data.hourly.time[2]='invalid';
  data.hourly.temperature_2m[3]=null;data.hourly.precipitation_probability[4]=null;
  data.hourly.precipitation_probability[5]=110;data.hourly.temperature_2m[6]='0';
  const rows=hourlyForecast(data,start);
  assert.equal(rows[1].label,'1時');assert.equal(rows[1].temperature,null);assert.equal(rows[1].probability,null);
  assert.equal(rows[2].temperature,null);assert.equal(rows[2].probability,30);
  assert.equal(rows[3].probability,null);assert.equal(rows[4].probability,null);assert.equal(rows[5].temperature,null);
  assert.equal(rows[0].probability,0);
  assert.equal(hourlyForecast({current:data.current},start).every(row=>row.temperature===null && row.probability===null && row.code===null),true);
});
test('temperature zero and below freezing remain valid values',()=>{
  const data=forecast();data.hourly.temperature_2m[1]=0;data.hourly.temperature_2m[2]=-3.2;
  assert.equal(hourlyForecast(data,start)[0].temperature,0);
  assert.equal(hourlyForecast(data,start)[1].temperature,-3.2);
});
test('weather icons distinguish nighttime, rain, snow, fog and thunder, with unknown values left unknown',()=>{
  assert.equal(weatherSymbol(0,1),'sun');assert.equal(weatherSymbol(0,0),'moon');
  assert.equal(weatherSymbol(2,1),'partly-day');assert.equal(weatherSymbol(2,0),'partly-night');
  assert.equal(weatherSymbol(63,1),'rain');assert.equal(weatherSymbol(85,0),'snow');
  assert.equal(weatherSymbol(48,1),'fog');assert.equal(weatherSymbol(95,0),'thunder');
  assert.equal(weatherSymbol(null,null),'unknown');assert.equal(weatherSymbol(0,null),'unknown');assert.equal(weatherSymbol(200,1),'unknown');
});
test('temperature curve keeps missing gaps and does not magnify a nearly flat forecast',()=>{
  const result=temperatureTrend([10,10.1,null,10.1,10].map(temperature=>({temperature})));
  assert.deepEqual(result.segments.map(segment=>segment.length),[2,2]);assert.equal(result.points[2],null);
  assert.ok(Math.abs(result.points[0].y-result.points[1].y)<1);
  assert.equal(temperatureTrend([{temperature:null}]).segments.length,0);
  const flat=temperatureTrend([{temperature:0},{temperature:0}]);assert.equal(flat.points[0].y,flat.points[1].y);
});
test('forecast timestamps are explicit JST and stale status preserves original observation/cache age',()=>{
  assert.equal(weatherTimestamp('2026-10-19T23:30'),Date.parse('2026-10-19T14:30Z'));
  for(const value of [null,'2026-02-30T10:00','2026-10-19T25:00','2026-10-19T23:60','2026-10-19T23:30Z'])assert.ok(Number.isNaN(weatherTimestamp(value)));
  const result={data:forecast(),fetchedAt:start,stale:false};
  assert.equal(weatherIsStale(result,start),false);assert.equal(weatherIsStale({...result,stale:true},start),true);
  assert.equal(weatherIsStale(result,start+4*HOUR),true);
  assert.equal(weatherIsStale({...result,fetchedAt:start-4*HOUR},start),true);
});
test('one Open-Meteo request retrieves current, daily and hourly data in Japan time',async()=>{
  const original=globalThis.fetch;let requested;
  globalThis.fetch=async url=>{requested=new URL(url);return {ok:true,json:async()=>forecast()};};
  try {
    const data=await getWeather({latitude:35.6589,longitude:139.70665});
    assert.equal(data.hourly.time.length,9);
    assert.equal(requested.searchParams.get('timezone'),'Asia/Tokyo');
    assert.deepEqual(requested.searchParams.get('hourly').split(','),['temperature_2m','precipitation_probability','weather_code','is_day']);
    assert.match(requested.searchParams.get('current'),/temperature_2m/);
    assert.match(requested.searchParams.get('daily'),/sunrise/);
  } finally {globalThis.fetch=original;}
});
test('the weather detail reads every second hour across midnight',()=>{
  const rows=hourlyForecast(forecast(),start,{count:4,step:2});
  assert.deepEqual(rows.map(row=>row.label),['明日 0時','2時','4時','6時']);
  assert.deepEqual(rows.map(row=>row.temperature),[17,15,13,11]);
  assert.equal(rows[1].timestamp-rows[0].timestamp,2*HOUR);
});
test('the week ahead starts today in Japan time and drops impossible values',()=>{
  const data={daily:{time:['2026-10-18','2026-10-19','2026-10-20','2026-10-21'],weather_code:[0,3,61,1.5],
    temperature_2m_max:[20,26,120,24],temperature_2m_min:[10,17,15,16],precipitation_probability_max:[0,37,-5,80],
    precipitation_sum:[0,6.3,1,0],uv_index_max:[3,5,2,40]}};
  const days=dailyForecast(data,start);
  assert.deepEqual(days.map(day=>day.label),['今日','明日','水']);
  assert.deepEqual(days.map(day=>day.max),[26,null,24]);
  assert.deepEqual(days.map(day=>day.probability),[37,null,80]);
  assert.deepEqual(days.map(day=>day.code),[3,61,null]);
  assert.equal(days[2].uv,null);
  assert.deepEqual(dailyForecast({},start),[]);
});
test('wind is named by where it blows from, and UV by the WHO bands',()=>{
  assert.equal(windDirection(0),'北');assert.equal(windDirection(333),'北北西');assert.equal(windDirection(360),'北');
  assert.equal(windDirection(-90),'西');assert.equal(windDirection(180),'南');assert.equal(windDirection(null),null);
  assert.deepEqual([0,2.9,3,6,8,11].map(uvLabel),['弱い','弱い','中程度','強い','非常に強い','極端に強い']);
  assert.equal(uvLabel(undefined),null);
});
test('the forecast request covers a week of the detail fields with wind in m/s',async()=>{
  const original=globalThis.fetch;let requested;
  globalThis.fetch=async url=>{requested=new URL(url);return {ok:true,json:async()=>forecast()};};
  try {
    await getWeather({latitude:35.6589,longitude:139.70665});
    assert.equal(requested.searchParams.get('forecast_days'),'7');
    assert.equal(requested.searchParams.get('wind_speed_unit'),'ms');
    for(const field of ['apparent_temperature','relative_humidity_2m','wind_speed_10m','wind_direction_10m','pressure_msl','uv_index'])assert.match(requested.searchParams.get('current'),new RegExp(field));
    for(const field of ['weather_code','precipitation_probability_max','precipitation_sum','uv_index_max'])assert.match(requested.searchParams.get('daily'),new RegExp(field));
  } finally {globalThis.fetch=original;}
});
