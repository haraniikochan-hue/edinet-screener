// Deterministic integration fixtures. No real OAuth account, token, or API key.
import assert from 'node:assert/strict';
import {writeFile,mkdir} from 'node:fs/promises';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
const base=process.env.DASHBOARD_URL || 'http://127.0.0.1:4173/';
const report=[];
async function contextWithAuth(state){
  const context=await browser.newContext({viewport:{width:1920,height:1080}});
  await context.addInitScript(({state})=>{if(!sessionStorage.getItem('qa-initialized')){
    sessionStorage.setItem('qa-initialized','true');
    sessionStorage.setItem('tv-spotify-auth',JSON.stringify({state,verifier:'b'.repeat(64),clientId:'a'.repeat(32),redirectUri:location.origin+'/',createdAt:Date.now()}));
  }},{state});
  return context;
}
try{
  const context=await contextWithAuth('qa-state');const page=await context.newPage();let tokenRequests=0;
  await page.route('https://accounts.spotify.com/api/token',route=>{tokenRequests++;const body=new URLSearchParams(route.request().postData());assert.equal(body.get('code_verifier'),'b'.repeat(64));assert.equal(body.has('client_secret'),false);return route.fulfill({json:{access_token:'qa-fixture-token',refresh_token:'qa-fixture-refresh',expires_in:3600}});});
  await page.route('https://api.spotify.com/v1/me/player/currently-playing',route=>route.fulfill({json:{is_playing:true,progress_ms:30000,item:{name:'テスト用トラック',duration_ms:180000,artists:[{name:'テスト用アーティスト'}],album:{images:[]},external_urls:{spotify:'https://open.spotify.com/track/test'}}}}));
  await page.goto(`${base}?code=qa-code&state=qa-state`,{waitUntil:'domcontentloaded'});
  await page.locator('#track-name').filter({hasText:'テスト用トラック'}).waitFor();assert.equal(tokenRequests,1);assert.equal(page.url(),base);
  assert.equal(await page.evaluate(()=>localStorage.getItem('tv-spotify-session')),null);
  assert.ok(await page.evaluate(()=>Boolean(sessionStorage.getItem('tv-spotify-session'))));
  await page.locator('[data-open-settings="general"]').click();await page.locator('#disconnect-spotify').click();
  assert.equal(await page.evaluate(()=>sessionStorage.getItem('tv-spotify-session')),null);await page.keyboard.press('Escape');
  report.push('Spotify PKCE success fixture: code verifier sent, client secret absent, callback URL cleaned, track rendered, token kept only in sessionStorage, disconnect clears token.');
  await context.close();
  const invalidContext=await contextWithAuth('expected');const invalid=await invalidContext.newPage();let invalidRequests=0;
  await invalid.route('https://accounts.spotify.com/api/token',route=>{invalidRequests++;return route.abort();});
  await invalid.goto(`${base}?code=qa-code&state=wrong`,{waitUntil:'domcontentloaded'});
  await invalid.locator('#toast').filter({hasText:'やり直して'}).waitFor();assert.equal(invalidRequests,0);
  report.push('Spotify mismatched OAuth state is rejected before any token request.');await invalidContext.close();
  const photosContext=await browser.newContext({viewport:{width:1920,height:1080}}),photos=await photosContext.newPage();
  await photos.route('**/api/config',route=>route.fulfill({json:{backend:true,market:false,unsplash:true,spotifyClientId:''}}));
  await photos.route('**/api/photos/*',route=>route.fulfill({json:{fetchedAt:Date.now(),stale:false,data:[1,2].map(i=>({url:'assets/nyc-luca-bravo.jpg',title:`テスト写真${i}`,photographer:`テスト撮影者${i}`,profile:'https://example.org/photographer',source:'Test fixture',sourceUrl:'https://example.org/'}))}}));
  await photos.goto(base,{waitUntil:'domcontentloaded'});await photos.locator('[data-open-settings="general"]').click();await photos.locator('#photo-mode').selectOption('unsplash');await photos.getByRole('button',{name:'設定を保存',exact:true}).click();
  await photos.locator('#photo-title').filter({hasText:'テスト写真1'}).waitFor();await photos.locator('#next-photo').click();await photos.locator('#photo-title').filter({hasText:'テスト写真2'}).waitFor();
  assert.match(await photos.locator('#photo-credit').textContent(),/テスト撮影者2/);assert.equal(await photos.locator('.photo-layer.is-active').count(),1);
  report.push('Photo API fixture: preload, next-photo transition, single active layer, and matching photographer attribution verified.');await photosContext.close();
  const nativeContext=await browser.newContext({viewport:{width:1920,height:1080}});await nativeContext.addInitScript(()=>{
    localStorage.setItem('tv-home-config',JSON.stringify({marketMode:'tradingview'}));
    const apps=[{name:'SmartTube',packageName:'org.fixture.playback'},{name:'U-NEXT',packageName:'org.fixture.movies'},{name:'Netflix',packageName:'org.fixture.series'},{name:'Prime Video',packageName:'org.fixture.prime'},{name:'Disney+',packageName:'org.fixture.disney'},{name:'Spotify',packageName:'org.fixture.music'},{name:'Test app',packageName:'org.test.app'},...Array.from({length:5},(_,i)=>({name:`Fixture ${i+1}`,packageName:`org.fixture.extra${i}`}))];
    window.Android={getApps:()=>JSON.stringify(apps),launchApp:pkg=>{window.launchedPackage=pkg;}};
  });const native=await nativeContext.newPage();await native.goto(base,{waitUntil:'domcontentloaded'});
  assert.equal(await native.locator('#apps button').count(),13);
  assert.equal(await native.locator('[data-package="org.fixture.movies"]').getAttribute('data-brand'),'unext');
  assert.equal(await native.locator('[data-package="org.fixture.series"]').getAttribute('data-brand'),'netflix');
  assert.equal(await native.locator('[data-package="org.fixture.prime"]').getAttribute('data-brand'),'prime');
  assert.equal(await native.locator('[data-package="org.fixture.disney"]').getAttribute('data-brand'),'disneyplus');
  assert.equal(await native.locator('[data-package="org.fixture.music"]').getAttribute('data-brand'),'spotify');
  assert.match(await native.locator('[data-package="org.fixture.playback"] .app-brand-mark').evaluate(e=>getComputedStyle(e).maskImage),/youtube.svg/);
  await native.getByRole('button',{name:'SmartTube',exact:true}).click();assert.equal(await native.evaluate(()=>window.launchedPackage),'org.fixture.playback');
  await native.getByRole('button',{name:'Disney+',exact:true}).click();assert.equal(await native.evaluate(()=>window.launchedPackage),'org.fixture.disney');
  await native.getByRole('button',{name:'Spotify',exact:true}).click();assert.equal(await native.evaluate(()=>window.launchedPackage),'org.fixture.music');
  await native.locator('[data-package="org.test.app"]').click();assert.equal(await native.evaluate(()=>window.launchedPackage),'org.test.app');
  await native.getByRole('button',{name:'SmartTube',exact:true}).focus();
  for(let i=0;i<12;i++)await native.keyboard.press('ArrowRight');
  assert.equal(await native.locator(':focus').getAttribute('data-open-settings'),'general');
  const nativeDock=await native.locator('#apps').evaluate(nav=>{const r=nav.getBoundingClientRect(),focus=document.activeElement.getBoundingClientRect();return{scroll:nav.scrollLeft,visible:focus.left>=r.left && focus.right<=r.right};});
  assert.ok(nativeDock.scroll>0);assert.equal(nativeDock.visible,true);
  await native.locator('[data-open-settings="general"]').click();assert.equal(await native.locator('#market-mode').inputValue(),'custom');assert.equal(await native.locator('#market-mode [value="tradingview"]').isDisabled(),true);assert.equal(await native.locator('#tradingview iframe').count(),0);
  await native.keyboard.press('Escape');await native.emulateMedia({reducedMotion:'reduce'});
  await native.getByRole('button',{name:'SmartTube',exact:true}).click();
  assert.equal(await native.locator('[data-package="org.fixture.playback"] .app-icon').evaluate(e=>e.getAnimations().length),0);
  report.push('Android bridge fixture: Disney+ and Spotify branding and supplied package launches verified; YouTube artwork still launches the supplied SmartTube package; unknown apps retained; all 13 buttons reachable through scrolling; reduced-motion disables press animation; external TradingView frames disabled.');await nativeContext.close();
  // Ad blocking: reachability against fixtures, and the optional launcher bridge for Private DNS.
  const adContext=await browser.newContext({viewport:{width:1920,height:1080}});
  await adContext.addInitScript(()=>{
    window.__dns={mode:'opportunistic',specifier:''};window.__dnsCalls=[];
    window.Android={getPrivateDns:()=>JSON.stringify(window.__dns),setPrivateDns:host=>{window.__dnsCalls.push(host);window.__dns=host?{mode:'hostname',specifier:host}:{mode:'opportunistic',specifier:''};return JSON.stringify({ok:true});}};
  });
  const ads=await adContext.newPage();let adsBlocked=true;
  await ads.route(/googlesyndication\.com|doubleclick\.net/,route=>adsBlocked?route.abort():route.fulfill({status:200,body:''}));
  await ads.route('https://www.gstatic.com/generate_204',route=>route.fulfill({status:204,body:''}));
  await ads.goto(base,{waitUntil:'domcontentloaded'});await ads.locator('[data-open-settings="general"]').click();
  await ads.locator('#adblock-state').filter({hasText:'広告ブロック 有効'}).waitFor();
  assert.equal(await ads.locator('#adblock-native').isVisible(),true);assert.equal(await ads.locator('#adblock-toggle').isChecked(),false);
  await ads.locator('#adblock-toggle').check();
  assert.deepEqual(await ads.evaluate(()=>window.__dnsCalls),['dns.adguard-dns.com']);
  await ads.locator('#adblock-message').filter({hasText:'dns.adguard-dns.com'}).waitFor();
  await ads.locator('#adblock-toggle').uncheck();
  assert.deepEqual(await ads.evaluate(()=>window.__dnsCalls),['dns.adguard-dns.com','']);
  await ads.locator('#adblock-dns').fill('bad host');await ads.getByRole('button',{name:'設定を保存',exact:true}).click();
  assert.match(await ads.locator('#settings-error').textContent(),/DNSサーバー/);
  adsBlocked=false;await ads.locator('#adblock-check').click();await ads.locator('#adblock-state').filter({hasText:'広告ブロック 無効'}).waitFor();
  report.push('Ad blocking fixture: blocked ad hosts read as active and reachable ones as inactive; the launcher bridge receives only the validated AdGuard DNS hostname, an empty value to restore automatic DNS, and a malformed server is rejected on save.');
  await adContext.close();
  await mkdir('artifacts',{recursive:true});await writeFile('artifacts/integration-check.json',JSON.stringify({checkedAt:new Date().toISOString(),scope:'Mock responses only; real credentials and TV hardware not tested',report},null,2));
  console.log(report.join('\n'));
}finally{await browser.close();}
