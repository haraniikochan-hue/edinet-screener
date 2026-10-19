import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeAsset, getHyperliquid, getMarketSnapshot, getMarketCandles, normalizeCandles, HyperliquidStream } from '../dashboard/js/hyperliquid.js';
import { chartGeometry } from '../dashboard/js/market-chart.js';
import { normalizeConfig } from '../dashboard/js/data.js';

test('mark prices retain instrument/unit and invalid or missing prices never become zero', () => {
  const quote=normalizeAsset('HYPE',{markPx:'77.125',prevDayPx:'80',midPx:'77.111',oraclePx:'77.2'},1234);
  assert.equal(quote.price,77.125); assert.ok(Math.abs(quote.change-(-3.59375))<1e-10);
  assert.equal(quote.currency,'USDC'); assert.equal(quote.instrument,'perpetual'); assert.equal(quote.timestamp,1234);
  assert.equal(quote.symbol,'HYPE'); assert.match(quote.note,/受信時刻/);
  for(const markPx of [null,undefined,'',false,'bad','Infinity','0','-10'])assert.equal(normalizeAsset('BTC',{markPx}),null);
  for(const prevDayPx of [null,'',0,'bad'])assert.equal(normalizeAsset('BTC',{markPx:'10',prevDayPx}).change,null);
  assert.equal(normalizeAsset('toString',{markPx:'10'}),null);
  assert.equal(normalizeAsset('BTC',{markPx:'81000'}).currency,'USDT');
  assert.equal(normalizeAsset('BTC',{markPx:'81000'}).collateral,'USDC');
  assert.equal(normalizeConfig({cryptoSource:'unknown'}).cryptoSource,'hyperliquid');
  assert.equal(normalizeConfig({cryptoSource:'coingecko'}).cryptoSource,'coingecko');
});

test('REST metadata is resolved by coin name, never by a hardcoded asset index', async () => {
  let payload;
  const fetcher=async(url,options)=>{
    assert.equal(url,'https://api.hyperliquid.xyz/info');assert.equal(options.method,'POST');assert.equal(options.headers.Authorization,undefined);
    payload=JSON.parse(options.body);
    return {ok:true,json:async()=>[{universe:[{name:'HYPE'},{name:'ETH'},{name:'BTC'}]},[{markPx:'70',prevDayPx:'80'},{markPx:'10'},{markPx:'81000',prevDayPx:'80000'}]]};
  };
  const rows=await getHyperliquid({fetcher,now:()=>5000});
  assert.deepEqual(payload,{type:'metaAndAssetCtxs'});
  assert.deepEqual(rows.map(r=>[r.symbol,r.price,r.timestamp]),[['BTC',81000,5000],['HYPE',70,5000]]);
  await assert.rejects(getHyperliquid({fetcher:async()=>({ok:true,json:async()=>[{universe:[{name:'BTC'}]},[{markPx:'1'}]]})}),/価格データ/);
  await assert.rejects(getHyperliquid({fetcher:async()=>({ok:true,json:async()=>[{universe:[{name:'BTC',isDelisted:true},{name:'HYPE'}]},[{markPx:'1'},{markPx:'2'}]]})}),/価格データ/);
});

function fakeSocketClass() {
  return class {
    static instances=[];
    constructor(url){this.url=url;this.sent=[];this.readyState=0;this.closed=false;this.constructor.instances.push(this);}
    open(){this.readyState=1;this.onopen?.();}
    send(data){this.sent.push(JSON.parse(data));}
    receive(data){this.onmessage?.({data:JSON.stringify(data)});}
    close(){this.closed=true;this.readyState=3;this.onclose?.();}
  };
}
const message=(coin,markPx='100')=>({channel:'activeAssetCtx',data:{coin,ctx:{markPx,prevDayPx:'90'}}});

test('socket batches two subscriptions, detects stale quotes despite pongs, and reconnects', t => {
  t.mock.timers.enable({apis:['Date','setTimeout','setInterval'],now:100000});
  const Socket=fakeSocketClass(),updates=[],states=[];
  const stream=new HyperliquidStream({WebSocketClass:Socket,onQuotes:rows=>updates.push(rows),onStatus:s=>states.push(s)});
  try {
    stream.start();stream.start();assert.equal(Socket.instances.length,1);
    const socket=Socket.instances[0];socket.open();
    assert.deepEqual(socket.sent,[{method:'subscribe',subscription:{type:'activeAssetCtx',coin:'BTC'}},{method:'subscribe',subscription:{type:'activeAssetCtx',coin:'HYPE'}}]);
    socket.receive({channel:'pong'});socket.receive(message('ETH'));socket.receive(message('BTC','100'));socket.receive(message('BTC','102'));socket.receive(message('HYPE','60'));
    assert.equal(updates.length,0);t.mock.timers.tick(1000);
    assert.deepEqual(updates[0].map(q=>q.price),[102,60]);assert.equal(stream.healthy(),true);assert.equal(states.at(-1),'live');
    t.mock.timers.tick(21000);socket.receive({channel:'pong'});assert.equal(stream.healthy(),false);
    t.mock.timers.tick(39000);assert.equal(socket.closed,true);assert.ok(states.includes('fallback'));
    t.mock.timers.tick(1000);assert.equal(Socket.instances.length,2);
  } finally { stream.stop(); }
});

test('stopping a stream cancels pending draws/reconnect and allows a clean resume', t => {
  t.mock.timers.enable({apis:['Date','setTimeout','setInterval'],now:100000});
  const Socket=fakeSocketClass(),updates=[];
  const stream=new HyperliquidStream({WebSocketClass:Socket,onQuotes:rows=>updates.push(rows)});
  stream.start();const first=Socket.instances[0];first.open();first.receive(message('BTC'));
  stream.stop();t.mock.timers.tick(120000);
  assert.equal(updates.length,0);assert.equal(Socket.instances.length,1);assert.equal(first.closed,true);
  stream.start();assert.equal(Socket.instances.length,2);
  const second=Socket.instances[1];second.open();second.receive(message('BTC'));t.mock.timers.tick(1000);
  assert.equal(updates.length,1);assert.equal(stream.healthy(),false,'one coin cannot make the whole feed live');
  stream.stop();
});

test('HIP-3 requires an exact active contract and does not turn partial metadata into a zero quote',async()=>{
  let request;
  const fetcher=async(_,options)=>{request=JSON.parse(options.body);return {ok:true,json:async()=>[{collateralToken:0,universe:[
    {name:'xyz:SOXL'}, {name:'SOXL'}, {name:'xyz:SP500',isDelisted:true}, {name:'xyz:JPY'}, {name:'xyz:DRAM'},
  ]},[{markPx:'89.282',prevDayPx:'94.393'},{markPx:'9000'},{markPx:'7600'},{markPx:'157.89'},{markPx:''}]]};};
  const result=await getMarketSnapshot('xyz',{fetcher,now:()=>1234,coins:['xyz:SP500','xyz:SOXL','xyz:XYZ100','xyz:JPY','xyz:DRAM']});
  assert.deepEqual(request,{type:'metaAndAssetCtxs',dex:'xyz'});
  assert.deepEqual(result.quotes.map(q=>[q.symbol,q.price]),[['SOXL',89.282],['JPY',157.89]]);
  assert.deepEqual(result.activeCoins,['xyz:SOXL','xyz:JPY','xyz:DRAM']);
  assert.deepEqual(result.unavailable.map(q=>[q.symbol,q.reason]),[['SP500','delisted'],['XYZ100','not-listed'],['DRAM','price-missing']]);
  assert.equal(result.quotes[1].currency,'円 / 1米ドル','JPY must never be inverted');
  const yieldQuote=normalizeAsset('para:10Y',{markPx:'5.14',prevDayPx:'5.1'});
  assert.equal(yieldQuote.price,5.14);assert.equal(yieldQuote.currency,'契約価格');
  assert.ok(Math.abs(yieldQuote.change-0.78431372549)<1e-8,'24h price percent, not a basis-point delta');
  await assert.rejects(getMarketSnapshot('xyz',{fetcher:async()=>({ok:true,json:async()=>[{collateralToken:2,universe:[]},[]]})}),/証拠金通貨/);
});

test('HIP-3 streaming subscribes only to approved exact coins and isolates quiet assets', t=>{
  t.mock.timers.enable({apis:['Date','setTimeout','setInterval'],now:100000});
  const Socket=fakeSocketClass(),updates=[],stream=new HyperliquidStream({coins:[],WebSocketClass:Socket,onQuotes:r=>updates.push(r)});
  try{
    stream.start();assert.equal(Socket.instances.length,0);
    stream.setCoins(['xyz:SOXL','xyz:JPY','unknown']);const ws=Socket.instances[0];ws.open();
    assert.deepEqual(ws.sent.map(s=>s.subscription.coin),['xyz:SOXL','xyz:JPY']);
    ws.receive(message('BTC'));ws.receive(message('SOXL'));ws.receive(message('xyz:SOXL','89'));
    t.mock.timers.tick(1000);assert.equal(updates.length,1);assert.equal(updates[0][0].symbol,'SOXL');
    assert.equal(stream.healthy(),false);assert.equal(stream.healthy(['xyz:SOXL']),true);
    for(let i=0;i<3;i++){t.mock.timers.tick(15000);ws.receive(message('xyz:SOXL','90'));}
    assert.equal(ws.closed,false,'a quiet JPY must not drop a fresh SOXL stream');
    stream.setCoins(['xyz:SOXL']);assert.ok(ws.sent.some(s=>s.method==='unsubscribe' && s.subscription.coin==='xyz:JPY'));
    ws.receive(message('xyz:JPY','100'));t.mock.timers.tick(1000);assert.ok(updates.flat().every(q=>q.symbol==='SOXL'));
    stream.setCoins([]);assert.equal(ws.closed,true);t.mock.timers.tick(120000);assert.equal(Socket.instances.length,1);
  }finally{stream.stop();}
});

test('24-hour candles keep identities and timestamps, reject malformed rows and deduplicate bars',async()=>{
  const end=200000000,start=end-86400000,interval=900000;
  const candle=(offset,value,extra={})=>({s:'xyz:SOXL',i:'15m',t:start+offset*interval,T:start+(offset+1)*interval-1,o:'100',c:String(value),...extra});
  let payload;
  const input=[candle(2,102),candle(0,101),candle(0,103),candle(4,99),candle(96,110),candle(7,0),candle(6,111,{s:'SOXL'}),candle(6,111,{i:'1h'}),null,candle(2,10,{T:Infinity})];
  const data=await getMarketCandles('xyz:SOXL','1d',{now:()=>end,fetcher:async(_,options)=>{payload=JSON.parse(options.body);return {ok:true,json:async()=>input};}});
  assert.deepEqual(payload,{type:'candleSnapshot',req:{coin:'xyz:SOXL',interval:'15m',startTime:start,endTime:end}});
  assert.deepEqual(data.points.map(p=>p.value),[103,102,99,110]);
  assert.equal(data.points.at(-1).time,end,'current candle stops at observation time');
  assert.equal(data.baseline,100,'baseline is the first bar open, not prevDay mark');
  assert.throws(()=>normalizeCandles([candle(0,100)],{coin:'xyz:SOXL',end}),/履歴/);
  assert.throws(()=>normalizeCandles(input,{coin:'xyz:SOXL',range:'7d',end}),/チャート/);
});

test('chart geometry preserves missing intervals and never stretches the last bar to now',()=>{
  const series={start:0,end:1000,intervalMs:100,baseline:10,points:[{time:100,value:11},{time:200,value:9},{time:600,value:12},{time:700,value:13}]};
  const chart=chartGeometry(series,160,52);
  assert.equal(chart.paths.length,2);assert.equal(chart.paths[0].points.length,2);
  assert.ok(chart.last.x<120,'last observation is at 70% of the time window');
  assert.ok(chart.baseline>7 && chart.baseline<45);
  assert.equal(chartGeometry({...series,points:[]}),null);
  const flat=chartGeometry({...series,baseline:2,points:[{time:100,value:2},{time:200,value:2}]});
  assert.equal(flat.baseline,26);assert.ok(!flat.paths[0].line.includes('NaN'));
});
