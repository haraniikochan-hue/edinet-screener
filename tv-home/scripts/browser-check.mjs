// Optional QA tool: use an installed Playwright package and Chromium.
// PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/usr/bin/chromium node scripts/browser-check.mjs
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { MARKETS } from '../dashboard/js/market-definitions.js';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
const url=process.env.DASHBOARD_URL || 'http://127.0.0.1:4173/';
const out=resolve('artifacts');await mkdir(out,{recursive:true});
const errors=[];const report=[];
try{
  const context=await browser.newContext({viewport:{width:1920,height:1080}});
  const page=await context.newPage();page.on('pageerror',error=>errors.push(error.message));
  const streamedCoins=new Set();
  page.on('websocket',socket=>socket.on('framereceived',event=>{try{const message=JSON.parse(String(event.payload));if(message.channel==='activeAssetCtx')streamedCoins.add(message.data.coin);}catch{}}));
  const calendarResponse=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/calendar');
  await page.goto(url,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#temperature').textContent!=='--°',{timeout:20000});
  await page.waitForFunction(()=>document.querySelectorAll('.hourly-item').length===6,{timeout:15000});
  assert.equal(await page.locator('.hourly-icon svg').count(),6);
  assert.equal(await page.locator('.hourly-trend .hourly-point').count(),6);
  assert.equal(await page.locator('[data-app=tv]').count(),0);
  assert.equal(await page.getByRole('button',{name:'U-NEXT',exact:true}).count(),1);
  const calendarResult=await calendarResponse;
  assert.equal(calendarResult.ok(),true);
  const calendarPayload=await calendarResult.json();
  const calendarStatus=calendarPayload.stale?'更新待ち':'自動更新';
  await page.waitForFunction(status=>document.querySelectorAll('.calendar-event').length===6 && document.querySelector('#calendar-source').textContent.includes(status),calendarStatus,{timeout:25000});
  assert.equal(await page.locator('#ny-clock,#fx-price,#yield-price,#countdown').count(),0);
  const firstCalendar=await page.locator('.calendar-event').first().getAttribute('aria-label');
  await page.locator('#calendar-next').click();
  assert.notEqual(await page.locator('.calendar-event').first().getAttribute('aria-label'),firstCalendar);
  assert.match(await page.locator('#calendar-page').textContent(),/^7–12 \//);
  await page.locator('#calendar-prev').click();
  assert.equal(await page.locator('.calendar-event').first().getAttribute('aria-label'),firstCalendar);
  assert.match(await page.locator('#calendar-page').textContent(),/^1–6 \//);
  await page.locator('[data-app=smarttube]').focus();
  await page.locator('#stock-source').filter({hasText:'12 / 12'}).waitFor({state:'attached',timeout:20000});
  await page.locator('#crypto-feed').filter({hasText:'LIVE'}).waitFor({state:'attached',timeout:20000});
  assert.equal(await page.locator('.market-card #crypto-feed,.market-card .market-caption').count(),0);
  assert.equal(await page.locator('.market-card h2,.market-card .eyebrow,.market-card button,.market-card .chart-period').count(),0);
  assert.equal(await page.locator('.market-card').getAttribute('aria-label'),'マーケットの銘柄一覧');
  assert.equal(await page.locator('#crypto-feed').isVisible(),false);
  assert.deepEqual([...streamedCoins].sort(),MARKETS.map(m=>m.coin).sort());
  await page.waitForFunction(()=>document.querySelectorAll('.stock-chart svg').length===12,{timeout:45000});
  assert.equal(await page.locator('.symbol-icon').evaluateAll(images=>images.every(i=>i.complete && i.naturalWidth>0)),true);
  assert.equal(await page.locator('[data-chart-range]').count(),0,'charts stay on 24 hours');
  assert.equal(await page.locator('[data-symbol=SOXL]').count(),1);
  assert.equal(await page.locator('[data-symbol=DRAM]').count(),1);
  assert.equal(await page.locator('[data-symbol=DJI], [data-symbol=VIX], [data-symbol=SILVER]').count(),0);
  await page.evaluate(()=>document.fonts.ready);
  await page.locator('[data-app=spotify]').focus();
  await page.waitForTimeout(450);
  await page.screenshot({path:resolve(out,'dashboard-desktop.png')});
  const dock=await page.locator('#apps').evaluate(nav=>{
    const buttons=[...nav.querySelectorAll('button')];
    const label=nav.querySelector(':focus .app-label').getBoundingClientRect();
    const content=document.querySelector('.dashboard-grid').getBoundingClientRect();
    return {names:buttons.map(b=>b.getAttribute('aria-label')),visibleLabels:buttons.filter(b=>getComputedStyle(b.querySelector('.app-label')).opacity==='1').length,labelClear:label.top>=content.bottom+6};
  });
  assert.deepEqual(dock.names,['SmartTube','U-NEXT','Netflix','Prime Video','Disney+','Spotify','設定']);
  assert.equal(dock.visibleLabels,1);assert.equal(dock.labelClear,true);
  assert.match(await page.locator('[data-app=smarttube] .app-brand-mark').evaluate(e=>getComputedStyle(e).maskImage),/youtube.svg/);
  assert.match(await page.locator('[data-app=spotify] .app-brand-mark').evaluate(e=>getComputedStyle(e).maskImage),/spotify.svg/);
  assert.equal(await page.locator('[data-app=disneyplus] img').evaluate(image=>image.complete && image.naturalWidth===180),true);
  await page.locator('[data-app=smarttube]').focus();
  assert.equal(await page.locator('.stock-symbol').count(),12);
  assert.equal(await page.locator('[data-symbol="BTC"]').count(),1);
  assert.equal(await page.locator('[data-symbol="HYPE"]').count(),1);
  assert.equal(await page.locator('.crypto-card').count(),0);
  assert.match(await page.locator('#crypto-note').textContent(),/無期限先物.*マーク価格.*24h.*取引価格/);
  assert.equal(await page.locator('#location-name').textContent(),'渋谷区');
  assert.equal(await page.locator('#apps button:focus').getAttribute('data-app'),'smarttube');
  await page.keyboard.press('ArrowRight');assert.equal(await page.locator('#apps button:focus').getAttribute('data-app'),'unext');
  await page.keyboard.press('Enter');await page.locator('#toast').filter({hasText:'Web版では'}).waitFor();
  for(const name of ['Netflix','Prime Video','Disney+','Spotify','設定']){
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#apps button:focus').getAttribute('aria-label'),name);
    if(name==='Disney+' || name==='Spotify'){
      await page.keyboard.press('Enter');await page.locator('#toast').filter({hasText:'Web版では'}).waitFor();
    }
  }
  await page.keyboard.press('Enter');await page.locator('#settings-dialog').waitFor({state:'visible'});
  await page.keyboard.press('Shift+Tab');assert.equal(await page.locator(':focus').textContent(),'設定を保存');
  await page.keyboard.press('Tab');assert.equal(await page.locator(':focus').getAttribute('id'),'close-settings');
  await page.locator('#motion').uncheck();await page.getByRole('button',{name:'設定を保存',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('#settings-overlay').hidden);
  assert.equal(await page.locator('body').evaluate(el=>el.classList.contains('motion')),false);
  report.push('Desktop: all 12 live quotes and real 24h charts; ticker icons; D-pad, Enter, modal focus trap, save verified.');
  report.push('Seven-logo dock: Disney+ official app icon and Spotify symbol added; all apps reachable by D-pad, new buttons show the Web launch limitation, accessible names and focused labels retained with no card overlap.');
  report.push(`US calendar: ${calendarPayload.data.sources.map(source=>`${source.source} ${source.status}`).join(', ')}; source freshness displayed correctly, JST dates and working six-item pagination; NY clock and duplicated rate widgets removed.`);
  report.push('Weather: six real hourly forecasts with weather icons, temperature curve and precipitation probability; U-NEXT replaces broadcast TV in the launcher.');
  report.push('Real Hyperliquid public WebSocket received activeAssetCtx updates for all 12 exact native/HIP-3 contracts.');
  await page.locator('#toast').waitFor({state:'hidden'});
  const collision=await page.evaluate(()=>{
    const box=s=>document.querySelector(s).getBoundingClientRect();
    const failures=[];if(box('.dashboard-grid').bottom>box('.launcher-footer').top-4)failures.push('widgets overlap launcher');
    if(box('.market-card').width>innerWidth*.5)failures.push('market panel is too large');
    if(box('.calendar-card').right>box('.market-card').left)failures.push('calendar overlaps market');
    if(box('.market-card').height>451)failures.push('market panel has not become compact');
    if(Math.abs(box('.market-card').top-box('.weather-section').top)>1)failures.push('market floats above weather');
    if(box('.market-card').top<box('.overview').bottom+20)failures.push('clock and widget bands overlap');
    if(box('.side-stack').top-box('.market-card').bottom<20)failures.push('spacing below market was lost');
    if(Math.abs(box('.side-stack').bottom-box('.calendar-card').bottom)>1)failures.push('lower widgets do not share a baseline');
    if(box('.market-card').bottom>box('.side-stack').top)failures.push('market overlaps lower widgets');
    if(box('#calendar-source').bottom>box('.calendar-card').bottom)failures.push('calendar caption overflow');
    if(box('#weather-source').bottom>box('.weather-section').bottom)failures.push('weather card overflow');
    if(box('.weather-section').bottom>box('.calendar-card').top)failures.push('weather overlaps calendar');
    if(box('.news-title').bottom>box('.news-footer').top+1)failures.push('news headline overlaps source');
    if(box('.news-footer').bottom>box('.news-card').bottom-12)failures.push('news source overflows');
    if(box('.music-details').bottom>box('.music-card').bottom-12)failures.push('music details overflow');
    for(const row of document.querySelectorAll('.stock-row')){
      const labels=row.querySelector('.stock-labels').getBoundingClientRect(),values=row.querySelector('.stock-price-row').getBoundingClientRect();
      const chart=row.querySelector('.stock-chart').getBoundingClientRect();
      const overlaps=(a,b)=>a.left<b.right-1 && a.right>b.left+1 && a.top<b.bottom-1 && a.bottom>b.top+1;
      if(overlaps(labels,chart) || overlaps(chart,values) || overlaps(labels,values))failures.push('labels/chart/prices overlap');
    }
    if(box('#apps').bottom>box('#stage').bottom-40)failures.push('app dock lost its bottom safe margin');
    return failures;
  });assert.deepEqual(collision,[]);
  for(const viewport of [{width:1366,height:768},{width:768,height:1024},{width:660,height:1000},{width:390,height:844},{width:320,height:720}]){
    await page.setViewportSize(viewport);await page.waitForTimeout(200);
    if(viewport.width<=700){
      await page.locator('[data-app=smarttube]').focus();
      await page.locator('[data-app=smarttube]').evaluate(button=>button.scrollIntoView({block:'nearest',inline:'nearest'}));
      for(const name of ['U-NEXT','Netflix','Prime Video','Disney+','Spotify','設定']){
        await page.keyboard.press('ArrowRight');
        assert.equal(await page.locator('#apps button:focus').getAttribute('aria-label'),name);
        assert.equal(await page.locator('#apps').evaluate(nav=>{const a=nav.getBoundingClientRect(),b=document.activeElement.getBoundingClientRect();return b.left>=a.left-1 && b.right<=a.right+1;}),true,`focused app visible at ${viewport.width}`);
      }
      await page.keyboard.press('ArrowLeft');
      assert.equal(await page.locator('#apps button:focus').getAttribute('data-app'),'spotify');
      assert.ok(await page.locator('#apps').evaluate(nav=>nav.scrollLeft)>0,'mobile dock scrolls to reveal the added apps');
    }
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,`overflow ${viewport.width}`);
    const suffix=viewport.width===390?'mobile':String(viewport.width);
    assert.equal(await page.locator('.stock-row').evaluateAll(rows=>rows.every(row=>{const a=row.querySelector('.stock-labels').getBoundingClientRect(),b=row.querySelector('.stock-chart').getBoundingClientRect(),c=row.querySelector('.stock-price-row').getBoundingClientRect();const overlap=(x,y)=>x.left<y.right-1 && x.right>y.left+1 && x.top<y.bottom-1 && x.bottom>y.top+1;return !overlap(a,b) && !overlap(b,c) && !overlap(a,c) && c.right<=row.getBoundingClientRect().right+1;})),true,`market collision ${viewport.width}`);
    await page.screenshot({path:resolve(out,`dashboard-${suffix}.png`),fullPage:viewport.width<=1000});
    report.push(`${viewport.width}×${viewport.height}: no horizontal page overflow.${viewport.width<=700?' All seven dock buttons reachable through horizontal scrolling.':''}`);
  }
  await page.setViewportSize({width:1920,height:1080});
  await page.route('https://api.open-meteo.com/**',route=>route.abort());
  await page.route('https://api.hyperliquid.xyz/**',route=>route.abort());
  await page.routeWebSocket('wss://api.hyperliquid.xyz/ws',socket=>socket.close());
  await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#weather-source').textContent.includes('更新待ち'));
  assert.notEqual(await page.locator('#temperature').textContent(),'--°');
  assert.match(await page.locator('#hourly-status').textContent(),/更新待ち/);
  assert.equal(await page.locator('.hourly-item').count(),6);
  await page.locator('[data-symbol="BTC"] .company-name').filter({hasText:'更新待ち'}).waitFor();
  assert.match(await page.locator('#crypto-feed').textContent(),/更新待ち/);
  assert.equal(await page.locator('.stock-chart svg').count(),12);
  report.push('Network failure: cached quotes and charts retained with explicit stale labels.');
  await page.unroute('https://api.open-meteo.com/**');await page.unroute('https://api.hyperliquid.xyz/**');
  // Geocoding uses an explicit test fixture; this does not verify the provider's availability.
  await page.route('https://geocoding-api.open-meteo.com/**',route=>route.fulfill({json:{results:[{name:'新宿',admin1:'東京都',admin2:'新宿区',country_code:'JP',latitude:35.69,longitude:139.7}]}}));
  await page.locator('[data-open-settings="general"]').click();await page.locator('#city-search').fill('Shinjuku');await page.locator('#search-city').click();
  await page.locator('#city-results button').click();await page.getByRole('button',{name:'設定を保存',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('#location-name').textContent==='新宿区');
  await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.querySelector('#location-name').textContent==='新宿区');
  report.push('Location selection/save survives reload (mocked geocoding).');
  // Restore the user default before testing the alternate widget mode.
  await page.evaluate(()=>localStorage.removeItem('tv-home-config'));await page.reload({waitUntil:'domcontentloaded'});
  await page.locator('[data-open-settings="general"]').click();
  assert.equal(await page.locator('#crypto-feed').isVisible(),true);
  report.push('Balanced layout: clock has its own upper band; weather and market share a top edge; calendar, news and Spotify share a bottom edge. Compact lower cards have no text collisions. Watchlist has no extra heading or status footer.');
  await page.locator('#market-mode').selectOption('tradingview');
  await page.getByRole('button',{name:'設定を保存',exact:true}).click();await page.locator('#tradingview iframe').first().waitFor();
  await page.waitForTimeout(6000);
  const frames=page.frames().filter(f=>f.url().includes('tradingview-widget.com'));
  assert.equal(frames.length,2,'TradingView provider iframes did not mount');
  report.push(`TradingView: two cross-origin sandboxed widgets mounted. Provider price availability varies by symbol.`);
  await page.screenshot({path:resolve(out,'dashboard-tradingview.png')});
  await page.locator('[data-open-settings="general"]').click();await page.locator('#spotify-client-id').fill('invalid');
  await page.getByRole('button',{name:'設定を保存',exact:true}).click();assert.match(await page.locator('#settings-error').textContent(),/Client ID/);
  await page.keyboard.press('Escape');assert.equal(await page.locator('#settings-overlay').isHidden(),true);
  report.push('Spotify configuration rejects malformed Client ID; live OAuth requires user credentials.');
  assert.deepEqual(errors,[]);report.push('No application JavaScript errors.');
  await writeFile(resolve(out,'browser-check.json'),JSON.stringify({checkedAt:new Date().toISOString(),report,errors},null,2));
  console.log(report.join('\n'));
}finally{await browser.close();}
