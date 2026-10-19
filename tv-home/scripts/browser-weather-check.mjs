// Controlled forecast fixtures; these are not live weather observations.
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
const base=process.env.DASHBOARD_URL || 'http://127.0.0.1:4173/';
const HOUR=3600000,now=Date.parse('2026-10-19T23:35:00+09:00');
const local=timestamp=>new Date(timestamp+9*HOUR).toISOString().slice(0,16);
const start=Date.parse('2026-10-19T00:00:00+09:00');
function fixture(){
  return {current:{time:local(now),temperature_2m:18,weather_code:0,is_day:0},daily:{time:['2026-10-19','2026-10-20'],temperature_2m_max:[25,22],temperature_2m_min:[18,16],sunrise:['2026-10-19T06:11','2026-10-20T06:12'],sunset:['2026-10-19T17:00','2026-10-20T16:59']},hourly:{
    time:Array.from({length:48},(_,i)=>local(start+i*HOUR)),
    temperature_2m:Array.from({length:48},(_,i)=>[17,16,15,14,13,12][i%6]),
    precipitation_probability:Array.from({length:48},(_,i)=>[0,10,60,80,90,100][i%6]),
    weather_code:Array.from({length:48},(_,i)=>[0,2,61,63,95,71][i%6]),
    is_day:Array.from({length:48},(_,i)=>i%24>=6 && i%24<17?1:0),
  }};
}
const errors=[],report=[];let mode='fresh',requests=[];
try{
  const context=await browser.newContext({viewport:{width:1920,height:1080},timezoneId:'America/Los_Angeles',reducedMotion:'reduce'});
  const page=await context.newPage();page.on('pageerror',error=>errors.push(error.message));
  await page.clock.setFixedTime(new Date(now));
  await page.route('https://api.hyperliquid.xyz/**',route=>route.abort());
  await page.route('https://api.open-meteo.com/**',route=>{
    const url=new URL(route.request().url());requests.push(url);
    if(mode==='offline' || url.searchParams.get('latitude')==='35.69')return route.abort();
    const data=fixture();
    if(mode==='partial'){
      data.hourly.temperature_2m[24]=0;data.hourly.temperature_2m[26]=null;
      data.hourly.precipitation_probability[25]=null;data.hourly.weather_code[27]=null;
    }
    if(mode==='legacy')delete data.hourly;
    return route.fulfill({json:data});
  });
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelectorAll('.hourly-item').length===6);
  assert.equal(requests[0].searchParams.get('timezone'),'Asia/Tokyo');
  assert.match(requests[0].searchParams.get('hourly'),/precipitation_probability/);
  assert.equal(await page.locator('.hourly-time').first().textContent(),'明日 0時');
  assert.equal(await page.locator('.hourly-icon .weather-moon').count(),1);
  assert.equal(await page.locator('.hourly-icon .weather-partly-night').count(),1);
  assert.equal(await page.locator('.hourly-icon .weather-rain').count(),2);
  assert.equal(await page.locator('.hourly-icon .weather-thunder').count(),1);
  assert.equal(await page.locator('.hourly-icon .weather-snow').count(),1);
  assert.deepEqual(await page.locator('.hourly-rain').allTextContents(),['0%','10%','60%','80%','90%','100%']);
  assert.equal(await page.locator('.hourly-trend .hourly-point').count(),6);
  assert.equal(await page.getByRole('button',{name:'U-NEXT',exact:true}).count(),1);
  assert.equal(await page.locator('[data-app=tv]').count(),0);
  report.push('Six forecasts use JST even in an American browser timezone; midnight, moon, cloud, rain, snow, thunder and 0–100% probabilities render correctly.');

  await page.clock.setFixedTime(new Date(now+4*HOUR));
  await page.locator('#hourly-status').filter({hasText:'更新待ち'}).waitFor();
  report.push('Previously fresh forecast ages into an explicit stale state without waiting for another successful fetch.');
  await page.clock.setFixedTime(new Date(now));await page.reload({waitUntil:'domcontentloaded'});
  await page.locator('#hourly-status').filter({hasText:'この先6時間'}).waitFor();
  mode='offline';await page.reload({waitUntil:'domcontentloaded'});
  await page.locator('#hourly-status').filter({hasText:'更新待ち'}).waitFor();
  assert.deepEqual(await page.locator('.hourly-temperature').allTextContents(),['17°','16°','15°','14°','13°','12°']);
  await page.clock.setFixedTime(new Date(now+30*60000));
  await page.waitForFunction(()=>document.querySelector('.hourly-time')?.textContent==='1時');
  assert.equal(await page.locator('#sunrise').textContent(),'日の出 06:12');
  assert.equal(await page.locator('.hourly-temperature').first().textContent(),'16°');
  report.push('Offline reload keeps the original cached forecast with a stale label; the hour/day rolls forward and sunrise follows the correct local date.');

  mode='partial';await page.clock.setFixedTime(new Date(now));await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('.hourly-temperature')?.textContent==='0°');
  assert.equal(await page.locator('.hourly-temperature').nth(2).textContent(),'—');
  assert.equal(await page.locator('.hourly-rain').nth(1).textContent(),'—');
  assert.equal(await page.locator('.hourly-icon .weather-unknown').count(),1);
  assert.equal(await page.locator('.hourly-trend .hourly-point').count(),5);
  assert.equal(await page.locator('.hourly-trend .hourly-line').count(),2);
  report.push('Partial data retains a real 0°C, shows missing values as dashes and breaks the curve at the missing hour.');

  await page.route('https://geocoding-api.open-meteo.com/**',route=>route.fulfill({json:{results:[{name:'新宿',admin1:'東京都',admin2:'新宿区',country_code:'JP',latitude:35.69,longitude:139.7}]}}));
  await page.locator('[data-open-settings=general]').click();await page.locator('#city-search').fill('Shinjuku');await page.locator('#search-city').click();await page.locator('#city-results button').click();
  await page.getByRole('button',{name:'設定を保存',exact:true}).click();
  await page.locator('#hourly-forecast').filter({hasText:'取得できません'}).waitFor();
  assert.equal(await page.locator('#location-name').textContent(),'新宿区');assert.equal(await page.locator('.hourly-item').count(),0);
  report.push('Changing location clears the previous region immediately; a failed new-region request never reuses Shibuya data.');

  mode='legacy';await page.evaluate(()=>localStorage.removeItem('tv-home-config'));await page.reload({waitUntil:'domcontentloaded'});
  await page.locator('#hourly-status').filter({hasText:'未取得'}).waitFor();
  assert.equal(await page.locator('#temperature').textContent(),'18°');assert.equal(await page.locator('.hourly-item').count(),0);
  report.push('A valid current forecast without hourly fields keeps current weather and explicitly reports hourly data unavailable.');
  assert.deepEqual(errors,[]);await context.close();
  await mkdir('artifacts',{recursive:true});await writeFile('artifacts/weather-check.json',JSON.stringify({checkedAt:new Date().toISOString(),scope:'Controlled forecast fixtures, not live weather',report,errors},null,2));
  console.log(report.join('\n'));
}finally{await browser.close();}
