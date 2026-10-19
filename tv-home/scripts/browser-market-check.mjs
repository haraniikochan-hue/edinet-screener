// Deterministic public-feed fixtures; no fixture prices are shipped in the app.
import assert from 'node:assert/strict';
import { writeFile, mkdir } from 'node:fs/promises';
import { MARKETS } from '../dashboard/js/market-definitions.js';
const { chromium }=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
const base=process.env.DASHBOARD_URL || 'http://127.0.0.1:4173/';
const report=[];
try {
  const page=await browser.newPage({viewport:{width:1920,height:1080}}), errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  let socket,allowSocket=true,httpFails=false,httpCalls=0,nativeCalls=0,coinGeckoCalls=0,candleCalls=0,delistSOXL=false,fixtureNow=Date.now();
  const subscriptions=new Set(),unsubscriptions=[];
  const message=(coin,markPx)=>JSON.stringify({channel:'activeAssetCtx',data:{coin,ctx:{markPx,prevDayPx:coin==='BTC'?'80000':'50'}}});
  await page.clock.install({time:new Date(fixtureNow)});
  await page.routeWebSocket('wss://api.hyperliquid.xyz/ws',ws=>{
    if(!allowSocket){ws.close();return;}
    socket=ws;
    ws.onMessage(raw=>{
      const request=JSON.parse(raw);
      if(request.method==='subscribe'){
        subscriptions.add(request.subscription.coin);
        ws.send(message(request.subscription.coin,request.subscription.coin==='BTC'?'82000':'55'));
      }
      if(request.method==='unsubscribe')unsubscriptions.push(request.subscription.coin);
    });
  });
  await page.route('https://api.hyperliquid.xyz/info',route=>{
    const request=JSON.parse(route.request().postData());
    if(request.type==='candleSnapshot'){
      candleCalls++;if(httpFails)return route.abort();
      const {coin,startTime}=request.req,step=900000;
      return route.fulfill({json:Array.from({length:96},(_,i)=>({s:coin,i:'15m',t:startTime+i*step,T:startTime+(i+1)*step-1,o:'50',c:String(50+Math.sin(i/4)*3+i/96)}))});
    }
    httpCalls++;if(!request.dex)nativeCalls++;
    if(httpFails)return route.abort();
    const markets=MARKETS.filter(m=>m.dex===(request.dex||'')).toReversed();
    return route.fulfill({json:[{collateralToken:0,universe:markets.map(m=>({name:m.coin,isDelisted:delistSOXL && m.symbol==='SOXL'}))},markets.map(m=>({markPx:m.symbol==='BTC'?'81000':'54',prevDayPx:m.symbol==='BTC'?'80000':'50'}))]});
  });
  await page.route('https://api.coingecko.com/**',route=>{
    coinGeckoCalls++;
    return route.fulfill({json:{bitcoin:{usd:90000,usd_24h_change:1,last_updated_at:Math.floor(fixtureNow/1000)},hyperliquid:{usd:70,usd_24h_change:2,last_updated_at:Math.floor(fixtureNow/1000)}}});
  });
  await page.goto(base,{waitUntil:'domcontentloaded'});
  const btc=page.locator('[data-symbol="BTC"]'), hype=page.locator('[data-symbol="HYPE"]');
  await page.locator('#crypto-feed').filter({hasText:'LIVE'}).waitFor({state:'attached'});
  await page.waitForFunction(()=>document.querySelectorAll('.stock-chart svg').length===12);
  assert.equal(await btc.count(),1);assert.equal(await hype.count(),1);assert.equal(await page.locator('.crypto-card').count(),0);
  assert.deepEqual([...subscriptions].sort(),MARKETS.map(m=>m.coin).sort());
  assert.match(await btc.getAttribute('title'),/USDT.*マーク価格/);
  assert.match(await hype.getAttribute('title'),/USDC.*マーク価格/);
  assert.match(await btc.locator('.stock-price-row').textContent(),/82,000/);
  socket.send(message('BTC','82500'));
  await btc.locator('.stock-price-row').filter({hasText:'82,500'}).waitFor();
  assert.equal(candleCalls,12,'initial listing batches must share the history cache');
  report.push('All 12 exact contract subscriptions, icons and real-history rendering; BTC/HYPE appear once; mark price units retained.');

  // The listing check must remove a delisted coin even if a socket still sends it.
  delistSOXL=true;
  for(let i=0;i<16;i++){
    for(const market of MARKETS)socket.send(message(market.coin,market.symbol==='BTC'?'82500':'55'));
    await page.waitForTimeout(30);fixtureNow+=19000;await page.clock.fastForward(19000);
  }
  const soxl=page.locator('[data-symbol="SOXL"]');
  await soxl.locator('.stock-unavailable').filter({hasText:'上場廃止'}).waitFor();
  assert.equal(await soxl.locator('.stock-chart svg').count(),0);
  assert.ok(unsubscriptions.includes('xyz:SOXL'));
  socket.send(message('xyz:SOXL','9999'));await page.clock.fastForward(1100);
  assert.equal(await soxl.locator('.stock-price-row>span').first().textContent(),'—');
  report.push('Delisted HIP-3 contract removes both price and chart, unsubscribes, and ignores subsequent stale frames.');

  allowSocket=false;socket.close();
  const before=httpCalls;fixtureNow+=31000;await page.clock.fastForward(31000);
  await btc.locator('.stock-price-row').filter({hasText:'81,000'}).waitFor();
  assert.ok(httpCalls>before);assert.doesNotMatch(await page.locator('#crypto-feed').textContent(),/LIVE/);
  report.push('Socket disconnect clears LIVE and activates HTTP fallback with fresh per-DEX snapshots.');

  httpFails=true;fixtureNow+=120000;await page.clock.fastForward(120000);
  await btc.locator('.company-name').filter({hasText:'更新待ち'}).waitFor();
  assert.match(await btc.locator('.stock-price-row').textContent(),/81,000/);
  assert.match(await page.locator('#crypto-feed').textContent(),/更新待ち/);
  report.push('Failed feeds retain original cached prices with stale labels and never claim LIVE.');

  await page.locator('[data-open-settings="general"]').click();
  await page.locator('#crypto-source-select').selectOption('coingecko');
  await page.getByRole('button',{name:'設定を保存',exact:true}).click();
  await btc.locator('.stock-price-row').filter({hasText:'90,000'}).waitFor();
  assert.match(await page.locator('#crypto-note').textContent(),/USD参考価格/);
  assert.equal(await btc.locator('.stock-symbol').textContent(),'BTC');
  assert.match(await hype.locator('.stock-price-row').textContent(),/70.000/);
  assert.equal(await btc.locator('.stock-chart svg').count(),0,'CoinGecko prices must not be paired with Hyperliquid history');
  assert.match(await btc.locator('.stock-chart').textContent(),/履歴未接続/);
  assert.ok(coinGeckoCalls>0);
  const nativeBeforeReload=nativeCalls;
  await page.reload({waitUntil:'domcontentloaded'});
  await btc.locator('.stock-price-row').filter({hasText:'90,000'}).waitFor();
  assert.equal(nativeCalls,nativeBeforeReload,'switching native coins leaves HIP-3 connections intact');
  report.push('CoinGecko source switch persists without using native perpetual quotes/charts; HIP-3 rows remain independent.');
  assert.deepEqual(errors,[]);
  await mkdir('artifacts',{recursive:true});
  await writeFile('artifacts/market-check.json',JSON.stringify({checkedAt:new Date().toISOString(),scope:'Deterministic API and WebSocket fixtures',report,errors},null,2));
  console.log(report.join('\n'));
} finally { await browser.close(); }
