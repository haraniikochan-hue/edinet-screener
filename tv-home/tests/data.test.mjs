import test from 'node:test';
import assert from 'node:assert/strict';
import {cachedLoad,normalizeConfig,sparkline,safeUrl,signed,money,fetchJSON,SYMBOLS,getCrypto} from '../dashboard/js/data.js';
const memory=()=>{const m=new Map();return {getItem:k=>m.get(k),setItem:(k,v)=>m.set(k,v)};};
test('only verified cached values survive network failure, with original acquisition time',async()=>{
  const storage=memory();
  await cachedLoad({key:'weather',load:async()=>({temperature:17}),storage,now:1000});
  const fail=async()=>{throw new Error('offline');};
  const result=await cachedLoad({key:'weather',load:fail,storage,now:2000,maxAge:5000});
  assert.equal(result.stale,true);assert.equal(result.fetchedAt,1000);assert.equal(result.data.temperature,17);
  await assert.rejects(cachedLoad({key:'weather',load:fail,storage,now:9000,maxAge:5000}),/offline/);
  await assert.rejects(cachedLoad({key:'another-location',load:fail,storage,now:2000}),/offline/);
});
test('blocked storage does not break fresh data and malformed cache never becomes a quote',async()=>{
  const storage={getItem:()=>'{bad',setItem:()=>{throw new Error('quota');}};
  const result=await cachedLoad({key:'fx',load:async()=>123,storage,now:1000});assert.equal(result.data,123);
  await assert.rejects(cachedLoad({key:'fx',load:async()=>{throw new Error('offline');},storage}),/offline/);
});
test('invalid location, mode, and executable URLs cannot enter configuration',()=>{
  const config=normalizeConfig({location:{name:'bad',latitude:999,longitude:1},marketMode:'evil',photoInterval:1,apiBase:'javascript:alert(1)',spotifyClientId:'secret'});
  assert.equal(normalizeConfig({chartRange:'7d'}).chartRange,'1d');assert.equal(config.location.name,'渋谷区');assert.equal(config.photoInterval,30);assert.equal(config.apiBase,'');assert.equal(config.spotifyClientId,'');
  assert.equal(safeUrl('javascript:alert(1)'),'');assert.equal(safeUrl('data:text/html,hi'),'');
  assert.equal(safeUrl('assets/../secret',{relative:true}),'');assert.equal(safeUrl('assets/photo.jpg',{relative:true}),'assets/photo.jpg');
});
test('missing market data is never a numeric zero or fabricated sparkline',()=>{
  assert.equal(money(null),'—');assert.equal(signed(null),'—');assert.equal(signed(-1.2),'−1.20%');
  assert.equal(sparkline([1,null,3]),'');assert.equal(sparkline([2]),'');assert.equal(sparkline([3,3,3]),'0.0,20.0 90.0,20.0 180.0,20.0');
});
test('watchlist reflects HIP-3 aliases and requested SOXL / DRAM replacements',()=>{
  assert.deepEqual(SYMBOLS.map(r=>r[0]),['SP500','BTC','HYPE','JP225','SOXL','XYZ100','JPY','DRAM','GOLD','CL','30Y','10Y']);
});
test('rate limit responses are errors and never parsed into usable prices',async()=>{
  let parsed=false;
  await assert.rejects(fetchJSON('https://example.test',{fetcher:async()=>({ok:false,status:429,json:()=>{parsed=true;}})}),error=>error.status===429);
  assert.equal(parsed,false);
});
test('provider missing coin is a failure, not a zero price',async()=>{
  const original=globalThis.fetch;
  globalThis.fetch=async()=>({ok:true,json:async()=>({bitcoin:{usd:100,last_updated_at:100}})});
  try{await assert.rejects(getCrypto(),/価格データ/);}finally{globalThis.fetch=original;}
});
