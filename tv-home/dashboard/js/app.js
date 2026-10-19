import { DEFAULT_CONFIG, normalizeConfig, readStorage, writeStorage, fetchJSON, cachedLoad, money, signed, tone, isNumber, safeUrl, weatherLabel, airLabel, getWeather, getAir, getCrypto } from './data.js';
import { eventPage, jstDay } from './calendar.js';
import { installNavigation } from './navigation.js';
import { nativeAppTile, pressApp } from './launcher.js';
import { Slideshow, SAMPLE_PHOTOS } from './slideshow.js';
import { Frost, frostSupported } from './frost.js';
import { DEFAULT_ADBLOCK_DNS, adBlockStatus, nativePrivateDns, setNativePrivateDns, validDnsHost } from './adblock.js';
import * as spotify from './spotify.js';
import { mountTradingView } from './tradingview.js';
import { getMarketSnapshot, getMarketCandles, HyperliquidStream } from './hyperliquid.js';
import { MARKETS, MARKET_BY_SYMBOL, CHART_RANGES, marketCoins } from './market-definitions.js';
import { drawMarketChart } from './market-chart.js';
import { HOUR, weatherTimestamp, weatherIsStale, hourlyForecast, makeWeatherIcon, renderHourlyForecast } from './weather.js';

const $ = id => document.getElementById(id);
const CALENDAR_PAGE_SIZE = 6, NEWS_INTERVAL = 20000, CARD_RADIUS = 32, IDLE_HOME = 60000;
const storage = { getItem:key => { try{return localStorage.getItem(key);}catch{return null;} }, setItem:(key,value) => localStorage.setItem(key,value) };
let config = normalizeConfig(readStorage(storage,'tv-home-config',DEFAULT_CONFIG));
let backend = {backend:false,market:false,unsplash:false};
let generation=0, jobs=[], news=[], newsIndex=0, music=null, toastTimer, returnFocus, selectedLocation=config.location;
let calendarInfo=null, calendarIndex=0, calendarNextTime=0;
let weatherResult=null, nextForecastHour=0, weatherWasStale=false;
let cryptoStream=null, streamStatus='connecting', chartVersion=0, chartQueue=Promise.resolve();
let stageScale=1, lastMinute='', frost=null;
const quotes = new Map();
const histories = new Map(), unavailable = new Map(), activeDexCoins = new Map(), metadata = new Map();
const stockElements = new Map();
const feedState = new Map();
// Building an Intl formatter costs far more than using one, especially on a TV CPU,
// and the market rows format times every second — so each one is built once.
const formats = new Map();
const format = (locale, options) => {const key=locale+JSON.stringify(options);if(!formats.has(key))formats.set(key,new Intl.DateTimeFormat(locale,options));return formats.get(key);};
const TIME = format('ja-JP',{timeZone:'Asia/Tokyo',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}), DATED = format('ja-JP',{timeZone:'Asia/Tokyo',month:'numeric',day:'numeric'});
const HOUR_OF_DAY = format('en-US',{timeZone:'Asia/Tokyo',hour:'numeric',hourCycle:'h23'}), ISO_DAY = format('en-CA',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'});
const MONTH_DAY = format('en-US',{timeZone:'Asia/Tokyo',month:'numeric',day:'numeric'}), WEEKDAY_SHORT = format('ja-JP',{timeZone:'Asia/Tokyo',weekday:'short'});
const FULL_JST = format('ja-JP',{timeZone:'Asia/Tokyo',month:'long',day:'numeric',weekday:'short',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}), FULL_ET = format('ja-JP',{timeZone:'America/New_York',month:'long',day:'numeric',weekday:'short',hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
const time = date => TIME.format(date);
const dated = date => DATED.format(date);
// DOM writes are skipped when nothing changed, so an idle second costs no style or layout work.
const setText = (node, text) => {if(node.textContent!==text)node.textContent=text;};
const setAttr = (node, name, value) => {if(node.getAttribute(name)!==value)node.setAttribute(name,value);};
const stamp = ts => `${dated(new Date(ts))} ${time(new Date(ts))}`;
const el = (tag, className='', content='') => {const node=document.createElement(tag);node.className=className;node.textContent=content;return node;};
const errorText = error => error.message || 'データを取得できません';
const api = path => fetchJSON(`${config.apiBase}/api/${path}`);
const reducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const EASE = 'cubic-bezier(.2,.8,.2,1)';
const greeting = date => {const hour=Number(HOUR_OF_DAY.format(date));return hour>=4 && hour<10?'おはようございます':hour>=10 && hour<17?'こんにちは':'こんばんは';};
// Like iOS numeric text transitions, only the digits that changed blur and rise in.
function renderClock(text) {
  const clock=$('clock'),previous=clock.dataset.text||'';if(previous===text)return;
  const animate=previous.length===text.length && !reducedMotion();
  clock.replaceChildren(...[...text].map((char,index)=>{
    const digit=el('span','',char);
    if(animate && previous[index]!==char)digit.animate?.([{opacity:0,transform:'translateY(.14em)',filter:'blur(8px)'},{opacity:1,transform:'none',filter:'blur(0)'}],{duration:700,easing:EASE});
    return digit;
  }));
  clock.dataset.text=text;
}
function toast(message) { clearTimeout(toastTimer);$('toast').textContent=message;$('toast').hidden=false;toastTimer=setTimeout(() => {$('toast').hidden=true;},5500); }
function setFeed(key, state) {
  feedState.set(key,state);
  const waiting=[...feedState.values()].some(v => v==='error' || v==='stale');
  setText($('connection-status'),!navigator.onLine ? 'オフライン' : waiting ? '一部更新待ち' : 'データ接続中');
  setAttr($('connection-status'),'data-state',!navigator.onLine || waiting ? 'waiting' : 'ok');
}
function freshness(result, observation, ttl) {return result.stale || !Number.isFinite(observation) || Date.now()-observation>ttl;}
function fit() {
  const tv=innerWidth>1000 && innerWidth>innerHeight;
  document.body.classList.toggle('tv',tv);
  if(tv){stageScale=Math.min(innerWidth/1920,innerHeight/1080);Object.assign($('stage').style,{transform:`scale(${stageScale})`,left:`${(innerWidth-1920*stageScale)/2}px`,top:`${(innerHeight-1080*stageScale)/2}px`});}
  else Object.assign($('stage').style,{transform:'',left:'',top:''});
  updateFrost();
}
// The fixed TV stage never scrolls, so the frosted layer only needs re-clipping when the stage is refitted.
function updateFrost() {
  const on=Boolean(frost?.ready) && document.body.classList.contains('tv');
  if(on)frost.clip([...document.querySelectorAll('#stage .card')],CARD_RADIUS*stageScale);
  document.body.classList.toggle('frosted',on);
}
function tick() {
  const now=new Date(),minute=time(now);
  if(minute!==lastMinute){
    // Clock, greeting and date only change with the minute.
    lastMinute=minute;renderClock(minute);$('clock').dateTime=now.toISOString();
    setText($('greeting'),greeting(now));
    setText($('date'),format('ja-JP',{timeZone:config.timeZone,month:'long',day:'numeric'}).format(now));
    setText($('weekday'),format('ja-JP',{timeZone:config.timeZone,weekday:'long'}).format(now));
  }
  if(calendarNextTime && now.getTime()>=calendarNextTime)showCalendar();
  if(weatherResult && (now.getTime()>=nextForecastHour || (!weatherWasStale && weatherIsStale(weatherResult,now.getTime()))))renderWeather(weatherResult);
  updateCryptoStatus();
  if(music?.item && isNumber(music.progress_ms) && isNumber(music.item.duration_ms)){
    const progress=Math.min(music.item.duration_ms,music.progress_ms+(music.is_playing?Date.now()-music.fetchedAt:0));
    // A transform update is composited only: no layout or repaint of the card each second.
    $('music-progress').firstElementChild.style.transform=`scaleX(${(progress/music.item.duration_ms).toFixed(4)})`;
  }
}
function buildStocks() {
  $('stocks').replaceChildren();stockElements.clear();
  MARKETS.forEach(({symbol,name,icon}) => {
    // Rows open a detail sheet with OK: on a TV there is no hover tooltip for the contract details.
    const row=el('div','stock-row'), badge=el('img','symbol-icon');row.dataset.symbol=symbol;row.tabIndex=0;row.setAttribute('role','button');
    badge.src=icon;badge.alt='';badge.width=44;badge.height=44;badge.addEventListener('error',()=>{badge.style.visibility='hidden';},{once:true});
    const labels=el('div','stock-labels'), label=el('span','stock-symbol',symbol), source=el('span','company-name',name);
    const chart=el('div','stock-chart'), chartStatus=el('span','chart-status','履歴を取得中');chart.append(chartStatus);
    const values=el('div','stock-price-row number'), price=el('span','','—'), change=el('span','stock-unavailable','取得中');
    labels.append(label,source);values.append(price,change);row.append(badge,labels,chart,values);$('stocks').append(row);stockElements.set(symbol,{row,label,source,price,change,name,chart});
  });
}
function renderStocks() {
  for(const [symbol,item] of stockElements){
    const q=quotes.get(symbol), market=MARKET_BY_SYMBOL.get(symbol);
    item.row.classList.toggle('unavailable',!q);item.row.classList.toggle('quote-stale',Boolean(q?.stale));
    if(!q){setText(item.price,'—');item.change.className='stock-unavailable';setText(item.change,unavailable.get(symbol)||'取得待ち');setText(item.source,item.name);item.row.removeAttribute('title');item.row.removeAttribute('aria-label');continue;}
    setText(item.price,money(q.price,market.digits));
    setText(item.change,isNumber(q.change)?`${q.change>0?'+':q.change<0?'−':''}${Math.abs(q.change).toFixed(2)}%`:'—');setAttr(item.change,'class',`stock-change ${tone(q.change)}`);
    const received=stamp(q.timestamp);
    setText(item.source,q.stale?`更新待ち · ${received}`:item.name);
    const title=`${item.name} / ${q.source} / ${received} JST受信 / ${q.note || '24時間変化率'}${q.stale?' / 最終取得値':''}`;
    setAttr(item.row,'title',title);setAttr(item.row,'aria-label',`${symbol} ${title} ${item.price.textContent} ${item.change.textContent}`);
  }
  if(config.marketMode==='custom'){
    const fresh=[...quotes.values()].filter(q=>!q.stale).length;
    setText($('stock-source'),`${fresh} / ${MARKETS.length} 銘柄`);
    setAttr($('market-dot'),'class',`status-dot ${fresh===MARKETS.length?'connected':'stale'}`);
  }
}
function renderChart(market) {
  const item=stockElements.get(market.symbol),key=`${market.coin}:${config.chartRange}`;
  if(!histories.has(key)){
    const saved=readStorage(storage,`tv-cache:hip3-chart-v1:${key}`,null);
    if(saved?.data?.coin===market.coin && Array.isArray(saved.data.points) && saved.fetchedAt<=Date.now() && Date.now()-saved.fetchedAt<3600000)histories.set(key,{...saved.data,stale:true});
  }
  const series=histories.get(key);
  const status=text=>{if(item.chartState!==text){item.chartState=text;item.chart.replaceChildren(el('span','chart-status',text));}};
  if(config.cryptoSource!=='hyperliquid' && !market.dex){status('履歴未接続');return;}
  if(unavailable.has(market.symbol)){status(unavailable.get(market.symbol));return;}
  if(!series){status('履歴を取得中');return;}
  const lag=Date.now()-series.lastTime>series.intervalMs*2;
  // Twelve SVG charts are rebuilt only when their data or freshness actually changes.
  const state=`${series.start}|${series.lastTime}|${series.points.length}|${series.points.at(-1)?.value}|${series.stale}|${lag}`;
  if(item.chartState===state)return;item.chartState=state;
  const label=`${market.symbol} ${CHART_RANGES[config.chartRange].label}の取引価格。点線は期間最初の足の始値。最終足 ${stamp(series.lastTime)} JST${series.stale?'。履歴の更新待ち':''}`;
  if(drawMarketChart(item.chart,series,market.symbol,label)){
    item.chart.title=label;
    if(series.stale || lag)item.chart.append(el('span','chart-age',`${series.stale?'更新待ち · ':''}${time(new Date(series.lastTime))}まで`));
  }
}
function renderCharts(){MARKETS.forEach(renderChart);}
function queueCharts() {
  const version=chartVersion,gen=generation,range=config.chartRange;
  // Serialise batches and cap requests at three, including settings changes.
  chartQueue=chartQueue.catch(()=>{}).then(async()=>{
    const current=()=>version===chartVersion && gen===generation && !document.hidden;
    if(!current())return;
    const pending=MARKETS.filter(m=>activeDexCoins.get(m.dex)?.includes(m.coin));
    await Promise.all(Array.from({length:3},async()=>{
      while(pending.length && current()){
        const market=pending.shift(),key=`${market.coin}:${range}`,storageKey=`hip3-chart-v1:${key}`;
        const saved=readStorage(storage,`tv-cache:${storageKey}`,null);
        try{
          const result=saved && Date.now()>=saved.fetchedAt && Date.now()-saved.fetchedAt<5*60000?saved:await cachedLoad({key:storageKey,storage,maxAge:3600000,load:()=>getMarketCandles(market.coin,range)});
          if(!current())return;
          histories.set(key,{...result.data,stale:Boolean(result.stale)});renderChart(market);
        }catch{
          if(current()){histories.delete(key);const item=stockElements.get(market.symbol);item.chartState='履歴の取得待ち';item.chart.replaceChildren(el('span','chart-status','履歴の取得待ち'));}
        }
      }
    }));
  });
  return chartQueue;
}
function renderWeather(result) {
  const {current,daily}=result.data, observed=weatherTimestamp(current.time), stale=weatherIsStale(result);
  weatherResult=result;weatherWasStale=stale;nextForecastHour=(Math.floor(Date.now()/HOUR)+1)*HOUR;
  $('temperature').textContent=`${Math.round(current.temperature_2m)}°`;$('weather-label').textContent=weatherLabel(current.weather_code);
  $('weather-icon').replaceChildren(makeWeatherIcon(current.weather_code,current.is_day));
  const today=ISO_DAY.format(new Date());
  const todayIndex=daily.time.indexOf(today), tomorrowIndex=todayIndex<0?-1:todayIndex+1;
  $('tomorrow').textContent=isNumber(daily.temperature_2m_max?.[tomorrowIndex]) && isNumber(daily.temperature_2m_min?.[tomorrowIndex]) ? `明日 ${Math.round(daily.temperature_2m_max[tomorrowIndex])}° / ${Math.round(daily.temperature_2m_min[tomorrowIndex])}°` : '明日の予報は未取得';
  $('sunrise').textContent=`日の出 ${daily.sunrise?.[todayIndex]?.slice(11,16)||'—'}`;$('sunset').textContent=`日の入 ${daily.sunset?.[todayIndex]?.slice(11,16)||'—'}`;
  const available=renderHourlyForecast($('hourly-forecast'),hourlyForecast(result.data));
  $('hourly-status').textContent=!available?'未取得':stale?'保存した予報 · 更新待ち':'この先6時間';
  $('hourly-status').classList.toggle('forecast-stale',stale || !available);
  // A fresh forecast only needs the time; a stale one keeps its date.
  $('weather-source').textContent=`Open-Meteo · ${Number.isFinite(observed)?stale?stamp(observed):time(new Date(observed)):'時刻不明'} 予測${stale?' · 更新待ち':''}`;
  $('weather-source').title=Number.isFinite(observed)?`Open-Meteo（CC BY 4.0）· ${stamp(observed)} JSTのモデル予測`:'Open-Meteo';
  $('weather-source').dataset.state=stale?'stale':'ok';
  setFeed('weather',stale || !available?'stale':'ok');
}
function renderAir(result) {
  const observed=Date.parse(`${result.data.current.time}+09:00`), stale=freshness(result,observed,6*3600000);
  $('air').textContent=`空気 ${airLabel(result.data.current.us_aqi)}${stale?'（更新待ち）':''}`;
  $('air').title=`米国AQI ${result.data.current.us_aqi} · CAMSモデル予測 · ${stamp(observed)}`;setFeed('air',stale?'stale':'ok');
}
function renderCrypto(result) {
  for(const row of result.data){
    const quote=row.symbol?row:{symbol:row.id==='bitcoin'?'BTC':'HYPE',price:row.usd,change:row.usd_24h_change,timestamp:row.last_updated_at*1000,source:'CoinGecko',note:'24時間変化率 / USD参考価格'};
    const current=quotes.get(quote.symbol);
    if(!MARKET_BY_SYMBOL.has(quote.symbol) || current?.source===quote.source && current.timestamp>quote.timestamp)continue;
    const old=freshness(result,quote.timestamp,quote.source==='Hyperliquid'?90000:15*60000);
    quotes.set(quote.symbol,{...quote,stale:old});
    unavailable.delete(quote.symbol);
  }
  renderStocks();updateCryptoStatus();
}
function updateCryptoStatus() {
  if(!$('crypto-feed'))return;
  let changed=false;
  for(const [symbol,q] of quotes){
    const age=Date.now()-q.timestamp;
    if(age>86400000){quotes.delete(symbol);changed=true;continue;}
    if(!q.stale && (age>(q.source==='Hyperliquid'?90000:15*60000)||!navigator.onLine)){q.stale=true;changed=true;}
  }
  if(changed)renderStocks();
  const available=MARKETS.every(m=>quotes.has(m.symbol) && !quotes.get(m.symbol).stale),live=available && cryptoStream?.healthy();
  setFeed('markets',available?'ok':'stale');
  const label=config.cryptoSource==='hyperliquid'?'Hyperliquid':'Hyperliquid + CoinGecko';
  setText($('crypto-feed'),`${label} · ${live?(config.cryptoSource==='hyperliquid'?'LIVE':'HIP-3 LIVE / BTC・HYPE 2分更新'):available?'HTTP 30秒更新':streamStatus==='connecting' && !quotes.size?'接続中':'一部更新待ち'}`);
  setAttr($('crypto-feed'),'data-state',live?'live':available?'ok':'waiting');
  setText($('crypto-note'),`${config.cryptoSource==='hyperliquid'?'価格：無期限先物のマーク価格':'BTC・HYPE：USD参考価格 / 他：無期限先物'} · 変化率：24h · チャート：取引価格`);
}
function renderNews(result) {news=result.data;newsIndex=Math.min(newsIndex,news.length-1);showNews();setFeed('news',result.stale || news.every(n=>Date.now()-Date.parse(n.publishedAt)>2*86400000)?'stale':'ok');}
function showNews() {
  if(!news.length){$('news-title').textContent='ニュースがありません';$('news-title').removeAttribute('href');return;}
  const current=news[newsIndex],title=$('news-title'),changed=title.textContent!==current.title;title.textContent=current.title;
  if(changed && !reducedMotion())title.animate?.([{opacity:0,transform:'translateY(8px)'},{opacity:1,transform:'none'}],{duration:600,easing:EASE});
  const url=safeUrl(current.url);if(url)title.href=url;else title.removeAttribute('href');
  const old=Date.now()-Date.parse(current.publishedAt)>2*86400000;
  $('news-source').textContent=`${current.source} · ${stamp(Date.parse(current.publishedAt))}${old?' · 過去の配信':''}`;
  $('next-news').setAttribute('aria-label',`次のニュース（${newsIndex+1} / ${news.length}）`);
  $('news-dots').replaceChildren(...news.map((_,i)=>el('i',i===newsIndex?'active':'')));
}
function renderMusic(data) {
  music=data;$('spotify-connect').hidden=Boolean(data.connected);$('music-progress').hidden=!data.item;
  if(!data.connected){$('track-name').textContent='音楽を、この画面に。';$('artist-name').textContent='再生中の曲を表示';$('music-state').dataset.state='idle';$('track-name').removeAttribute('href');resetAlbum();return;}
  if(!data.item){$('track-name').textContent='再生していません';$('artist-name').textContent='Spotifyで音楽を再生してください';$('music-state').dataset.state='paused';$('track-name').removeAttribute('href');resetAlbum();return;}
  $('track-name').textContent=data.item.name || 'タイトルなし';const url=safeUrl(data.item.external_urls?.spotify);if(url)$('track-name').href=url;else $('track-name').removeAttribute('href');
  $('artist-name').textContent=data.item.artists?.map(a=>a.name).join(' / ') || data.item.show?.publisher || '';
  $('music-state').dataset.state=data.is_playing?'playing':'paused';
  const imageUrl=safeUrl(data.item.album?.images?.at(-2)?.url || data.item.album?.images?.[0]?.url || data.item.images?.[0]?.url);
  if(imageUrl){
    let img=$('album').querySelector('img');if(!img){img=el('img');img.alt='アルバムジャケット';img.onload=()=>paintWash(img);$('album').replaceChildren(img);}if(img.getAttribute('src')!==imageUrl)img.src=imageUrl;
  }
  else resetAlbum();tick();
}
const originalAlbum=$('album').firstElementChild.cloneNode(true), musicCard=$('album').closest('.music-card');
function resetAlbum(){if(!$('album').querySelector('svg'))$('album').replaceChildren(originalAlbum.cloneNode(true));delete musicCard.dataset.art;}
// The artwork tints the card like Now Playing. It is drawn once into a 24px canvas that CSS
// stretches into a soft wash, instead of a live blur filter repainted with the card.
function paintWash(image) {
  try{
    const canvas=$('album-wash'),context=canvas.getContext('2d');
    context.clearRect(0,0,canvas.width,canvas.height);if('filter' in context)context.filter='blur(2px) saturate(1.5)';
    context.drawImage(image,0,0,canvas.width,canvas.height);musicCard.dataset.art='';
  }catch{delete musicCard.dataset.art;}
}
function renderCalendar(result) {
  calendarInfo=result;showCalendar();
  const sources=result.data.sources||[],expired=sources.some(source=>Date.parse(source.coverageThrough)<Date.now());
  const stale=result.stale || expired;
  const live=sources.filter(source=>source.status==='live').map(source=>source.source);
  const frb=sources.find(source=>source.source==='FRB');
  $('calendar-source').textContent=stale?'保存済み日程 · 一部更新待ち':`${live.join('・')} 自動更新 / FRB ${frb?.verifiedAt?.slice(5,10).replace('-','/')||'—'}確認`;
  $('calendar-source').title=sources.map(source=>`${source.source}: ${source.status==='live'?'自動取得':'保存済み'} / ${source.verifiedAt}確認 / ${source.coverageThrough}まで収録`).join('\n')+'\n予定は変更される場合があります。';
  setFeed('calendar',stale?'stale':'ok');
}
function showCalendar() {
  if(!calendarInfo)return;
  const focusedId=document.activeElement?.dataset.eventId,focusedPage=document.activeElement?.id;
  const data=eventPage(calendarInfo.data.events,calendarIndex,CALENDAR_PAGE_SIZE);calendarIndex=data.index;
  $('calendar-events').replaceChildren();
  if(!data.events.length)$('calendar-events').append(el('p','calendar-empty','今後の予定を確認できません。公式日程の更新をお待ちください。'));
  const today=jstDay(Date.now()),tomorrow=jstDay(Date.now()+86400000);let previousDay='';
  data.events.forEach((event,index)=>{
    const row=el('a','calendar-event');row.href=safeUrl(event.url);row.target='_blank';row.rel='noopener noreferrer';row.dataset.indicator=event.indicator;row.dataset.eventId=event.id;
    const date=new Date(event.timestamp),day=el('div','calendar-day number'),eventDay=jstDay(event.timestamp);
    day.append(el('strong','',MONTH_DAY.format(date)),el('span','',eventDay===today?'今日':eventDay===tomorrow?'明日':WEEKDAY_SHORT.format(date)));
    // Like a calendar list, a date is written once for releases on the same day.
    if(eventDay===previousDay)row.classList.add('same-day');previousDay=eventDay;
    const detail=el('div','calendar-detail'),title=el('span','calendar-title',event.title),meta=el('span','calendar-meta',`${index===0 && calendarIndex===0?'次の発表 · ':''}${event.category}`);
    detail.append(title,meta);
    const at=el('time','calendar-time number',time(date));at.dateTime=date.toISOString();
    row.append(day,detail,at);row.title=`${event.originalTitle} / ${event.source} / ${date.toISOString()}${event.note?' / '+event.note:''}`;
    row.setAttribute('aria-label',`${dated(date)} ${time(date)} 日本時間 ${event.title} ${event.source}の公式日程を開く`);
    if(index===0 && calendarIndex===0)row.classList.add('next-event');
    $('calendar-events').append(row);
  });
  $('calendar-page').textContent=data.total?`${calendarIndex*CALENDAR_PAGE_SIZE+1}–${Math.min((calendarIndex+1)*CALENDAR_PAGE_SIZE,data.total)} / ${data.total} 件`:'日程未取得';
  $('calendar-prev').disabled=calendarIndex===0;$('calendar-next').disabled=calendarIndex>=data.pages-1;
  if(focusedId){const links=[...$('calendar-events').children];(links.find(link=>link.dataset.eventId===focusedId)||links[0])?.focus({preventScroll:true});}
  if(['calendar-prev','calendar-next'].includes(focusedPage) && $(focusedPage).disabled){const alternate=$(focusedPage==='calendar-prev'?'calendar-next':'calendar-prev');if(!alternate.disabled)alternate.focus({preventScroll:true});}
  // Only advance automatically when the first upcoming release passes.
  calendarNextTime=eventPage(calendarInfo.data.events,0,1).events[0]?.timestamp||0;
}
async function loadCalendarSnapshot() {
  try{const data=await fetchJSON('data/economic-calendar.json');if(!calendarInfo)renderCalendar({data,stale:true});}catch{$('calendar-source').textContent='公式日程を取得できません';}
}

function makeJob(id, period, task, onError) {
  let last=0, busy=false, failures=0;const myGeneration=generation;
  const job={
    async run(manual=false){
      const now=Date.now();if(busy || document.hidden || now-last<(manual?30000:period*Math.min(2**failures,8)))return;
      busy=true;last=now;
      try{await task(()=>myGeneration===generation);failures=0;}catch(error){failures++;if(myGeneration===generation){setFeed(id,'error');onError?.(error);}}finally{busy=false;}
    },
    stop(){clearInterval(job.timer);},
  };
  job.timer=setInterval(()=>void job.run(),Math.min(period,30000));void job.run(true);return job;
}
function cachedTask(id, load, render, {maxAge=86400000,server=false}={}) {
  const cacheKey=`${config.apiBase || 'local'}:${id}${['weather','air'].includes(id)?`:${config.location.latitude},${config.location.longitude}`:''}`;
  return async current => {
    const result=await cachedLoad({key:cacheKey,storage,maxAge,load});
    if(!current())return;
    if(server){const envelope=result.data;render({...envelope,stale:result.stale || envelope.stale});}
    else render(result);
  };
}
function clearQuotes(symbols){for(const symbol of symbols)quotes.delete(symbol);renderStocks();}
function resetHourlyForecast(message='時間別予報を取得しています'){
  weatherResult=null;nextForecastHour=0;weatherWasStale=false;
  $('hourly-forecast').replaceChildren(el('p','hourly-empty',message));$('hourly-status').textContent='';$('hourly-status').classList.remove('forecast-stale');
  $('weather-icon').replaceChildren(makeWeatherIcon(null,null));
}
function clearWeather(error){
  resetHourlyForecast('時間別予報を取得できません');
  $('temperature').textContent='--°';$('weather-label').textContent='取得できません';$('tomorrow').textContent='予報は未取得です';
  $('sunrise').textContent='日の出 —';$('sunset').textContent='日の入 —';$('weather-source').textContent=`Open-Meteo · ${errorText(error)}`;$('weather-source').dataset.state='stale';
}
function clearCrypto(error){
  $('crypto-feed').title=errorText(error);streamStatus='fallback';updateCryptoStatus();
}
function restartJobs() {
  jobs.forEach(job=>job.stop());jobs=[];generation++;chartVersion++;cryptoStream?.stop();cryptoStream=null;streamStatus='connecting';activeDexCoins.clear();metadata.clear();
  feedState.clear();setFeed('connection','ok');
  const location={...config.location};
  const base=config.apiBase, apiForJob=path=>fetchJSON(`${base}/api/${path}`);
  const sameLocation=()=>location.latitude===config.location.latitude && location.longitude===config.location.longitude;
  jobs.push(makeJob('weather',15*60000,cachedTask('weather',()=>getWeather(location),result=>{if(sameLocation())renderWeather(result);}),error=>{if(sameLocation())clearWeather(error);}));
  jobs.push(makeJob('air',30*60000,cachedTask('air',()=>getAir(location),renderAir),()=>{$('air').textContent='空気 未取得';}));
  if(config.marketMode==='custom'){
    const myGeneration=generation;
    cryptoStream=new HyperliquidStream({coins:[],onQuotes:rows=>{
      if(myGeneration!==generation)return;
      renderCrypto({data:rows,stale:false});
      for(const dex of new Set(rows.map(q=>MARKET_BY_SYMBOL.get(q.symbol).dex)))setFeed(`market:${dex}`, 'ok');
    },onStatus:status=>{if(myGeneration===generation){streamStatus=status;updateCryptoStatus();}}});
    if(!document.hidden)cryptoStream.start();
    for(const dex of ['', 'xyz', 'para']){
      const coins=marketCoins(dex,config.cryptoSource);if(!coins.length)continue;
      jobs.push(makeJob(`market:${dex}`,30000,async current=>{
        // Healthy streaming needs only an occasional listing check; a quiet or
        // disconnected instrument still gets a 30-second REST fallback.
        if(cryptoStream?.healthy(coins) && Date.now()-(metadata.get(dex)?.fetchedAt||0)<5*60000)return;
        const result=await cachedLoad({key:`hip3-v1:${dex||'native'}`,storage,load:()=>getMarketSnapshot(dex,{coins})});
        if(!current())return;
        let listingsChanged=false;
        if(!result.stale){
          listingsChanged=JSON.stringify(activeDexCoins.get(dex))!==JSON.stringify(result.data.activeCoins);
          metadata.set(dex,result.data);activeDexCoins.set(dex,result.data.activeCoins);
          for(const missing of result.data.unavailable){
            if(missing.reason==='price-missing')continue;
            quotes.delete(missing.symbol);unavailable.set(missing.symbol,missing.reason==='delisted'?'上場廃止':'未上場');
            histories.delete(`${missing.coin}:${config.chartRange}`);
          }
          cryptoStream.setCoins([...activeDexCoins.values()].flat());
        }
        renderCrypto({data:result.data.quotes,stale:result.stale});
        setFeed(`market:${dex}`,result.stale?'stale':'ok');
        renderCharts();if(listingsChanged)void queueCharts();
        if(result.stale)throw new Error(result.error||'Hyperliquidの更新待ち');
      },clearCrypto));
    }
    if(config.cryptoSource==='coingecko')jobs.push(makeJob('crypto',2*60000,cachedTask('crypto:coingecko',getCrypto,result=>{renderCrypto(result);setFeed('crypto',result.stale?'stale':'ok');}),clearCrypto));
    jobs.push(makeJob('charts',5*60000,async()=>{await queueCharts();}));
  }
  if(backend.backend || config.apiBase){
    jobs.push(makeJob('calendar',6*3600000,cachedTask('economic-calendar',()=>apiForJob('calendar'),renderCalendar,{server:true,maxAge:7*86400000}),()=>{if(calendarInfo)renderCalendar({...calendarInfo,stale:true});else void loadCalendarSnapshot();}));
    jobs.push(makeJob('news',15*60000,cachedTask('news',()=>apiForJob('news'),renderNews,{server:true}),()=>{news=[];$('news-title').textContent='ニュースを取得できません';$('news-title').removeAttribute('href');$('news-source').textContent='NHK · しばらくして再取得します';$('next-news').setAttribute('aria-label','次のニュース');$('news-dots').replaceChildren();}));
    if(config.photoMode==='unsplash')jobs.push(makeJob('photos',3600000,cachedTask('photos',()=>apiForJob('photos'),result=>{setPhotos(result.data);setFeed('photos',result.stale?'stale':'ok');},{server:true,maxAge:7*86400000}),()=>{toast('Unsplashを取得できません。同梱写真を表示しています。');}));
  }else{
    $('news-title').textContent='ニュースはサーバー接続後に表示';$('news-source').textContent='設定でデータサーバーを指定できます';
    if(config.photoMode==='unsplash')toast('Unsplashの自動取得にはAPIサーバーが必要です');
  }
  jobs.push(makeJob('spotify',30000,async current=>{const data=await spotify.currentlyPlaying();if(current())renderMusic(data);},error=>{$('artist-name').textContent=errorText(error);$('music-state').dataset.state='error';music=null;$('music-progress').hidden=true;$('spotify-connect').hidden=false;}));
}
function configureMarket() {
  // A legacy Android JavascriptInterface is injected into every frame, even
  // cross-origin frames. Do not load vendor frames when that bridge is present.
  if(window.Android && config.marketMode==='tradingview')config.marketMode='custom';
  const tv=config.marketMode==='tradingview';$('stocks').hidden=tv;$('tradingview').hidden=!tv;
  $('crypto-feed').hidden=tv;$('crypto-note').hidden=tv;
  $('chart-legend').hidden=tv;
  if(tv && !$('tradingview').firstElementChild)mountTradingView($('tradingview'));
  if(!tv)$('tradingview').replaceChildren();
  if(tv){$('stock-source').textContent='TradingView · 遅延・配信可否は銘柄ごとに異なります';$('market-dot').className='status-dot';}
  else {renderStocks();renderCharts();}
}
function applyConfig() {
  $('location-name').textContent=config.location.name;
  document.body.classList.toggle('motion',config.motion && !matchMedia('(prefers-reduced-motion: reduce)').matches);
  configureMarket();setPhotos(SAMPLE_PHOTOS);slideshow.schedule(config.photoInterval);restartJobs();tick();
}
const ADBLOCK = {checking:['確認中…',''],active:['広告ブロック 有効','live'],partial:['一部の広告のみ遮断','waiting'],inactive:['広告ブロック 無効',''],unknown:['確認できません（オフライン）','']};
let adblockCheckedAt=0, adblockStatus='', adblockVersion=0;
function showAdBlock(status){adblockStatus=status;const [label,state]=ADBLOCK[status];$('adblock-state').textContent=label;$('adblock-state').dataset.state=state;}
async function checkAdBlock(){
  const version=++adblockVersion;showAdBlock('checking');
  const status=await adBlockStatus();
  if(version===adblockVersion){adblockCheckedAt=Date.now();showAdBlock(status);}
}
// With the Phase 3 launcher bridge, the switch changes the TV's Private DNS directly.
function renderNativeAdBlock(){
  const state=nativePrivateDns();$('adblock-native').hidden=!state;if(!state)return;
  const host=state.mode==='hostname'?state.host:'';
  $('adblock-toggle').checked=Boolean(host);if(host)$('adblock-dns').value=host;
  $('adblock-help').textContent=`オンにすると、TVのプライベートDNSを上のサーバー（初期値は広告とトラッカーを遮断するAdGuard DNS）に切り替えます。オフでAndroid標準の「自動」に戻ります。アプリが動かなくなったらオフにしてください。YouTubeの広告はSmartTubeが除去します。動画や音声に組み込まれた広告は消せません。`;
}
// Detail sheet: what OK shows for a market row, a release, a headline or the data status.
let detailReturn=null;
function openDetail({eyebrow='',title,subtitle='',body='',facts=[],chart=null,link=null,action=null,accent=''}){
  detailReturn=document.activeElement;
  $('detail-eyebrow').textContent=eyebrow;$('detail-title').textContent=title;
  $('detail-subtitle').textContent=subtitle;$('detail-subtitle').hidden=!subtitle;
  $('detail-body').textContent=body;$('detail-body').hidden=!body;
  $('detail-facts').replaceChildren(...facts.filter(([,value])=>value).flatMap(([term,value,tone])=>[el('dt','',term),el('dd',tone?`tone-${tone}`:'',value)]));
  const chartShown=Boolean(chart) && drawMarketChart($('detail-chart'),chart.series,`detail-${chart.symbol}`,chart.label,{width:640,height:200});
  $('detail-chart').hidden=!chartShown;
  if(!chartShown)$('detail-chart').replaceChildren();
  else{
    // Time runs left to right; the dotted line is the first candle's open.
    const axis=el('div','detail-axis');axis.setAttribute('aria-hidden','true');
    const start=time(new Date(chart.series.start)),yesterday=jstDay(chart.series.start)!==jstDay(chart.series.lastTime);
    axis.append(el('span','',`${yesterday?'昨日 ':''}${start}`),el('span','',`点線 ${chart.baseline}`),el('span','',time(new Date(chart.series.lastTime))));
    $('detail-chart').append(axis);
  }
  // Links would leave the TV app, so they are offered only in a browser.
  const url=link && !window.Android ? safeUrl(link.href) : '';
  $('detail-link').hidden=!url && !action;
  if(url){$('detail-link').href=url;$('detail-link').textContent=link.label;$('detail-link').onclick=null;$('detail-link').removeAttribute('role');$('detail-link').removeAttribute('tabindex');}
  else if(action){$('detail-link').removeAttribute('href');$('detail-link').textContent=action.label;$('detail-link').setAttribute('role','button');$('detail-link').tabIndex=0;$('detail-link').onclick=event=>{event.preventDefault();action.run();};}
  $('detail-sheet').style.setProperty('--sheet-accent',accent||'transparent');
  $('detail-overlay').hidden=false;$('stage').inert=true;document.body.classList.add('modal-open');
  $('close-detail').focus();
}
// If the row was re-rendered meanwhile (a calendar page turn), focus rests on the dock instead of nowhere.
function closeDetail(){ $('detail-overlay').hidden=true;$('stage').inert=false;document.body.classList.remove('modal-open');if(detailReturn?.isConnected)detailReturn.focus({preventScroll:true});else navigation.focusHome(); }
function openMarketDetail(symbol){
  const market=MARKET_BY_SYMBOL.get(symbol),q=quotes.get(symbol),series=histories.get(`${market.coin}:${config.chartRange}`);
  const values=series?.points?.map(point=>point.value).filter(isNumber)||[];
  const change=q && isNumber(q.change)?`${q.change>0?'+':q.change<0?'−':''}${Math.abs(q.change).toFixed(2)}%`:'';
  openDetail({eyebrow:market.name,title:q?`${symbol} ${money(q.price,market.digits)}`:symbol,
    subtitle:q?`24時間 ${change}${q.stale?' · 更新待ち':''}`:(unavailable.get(symbol)||'価格を取得しています'),
    chart:series && config.marketMode==='custom'?{series,symbol,label:`${symbol} 24時間の取引価格`,baseline:money(series.baseline,market.digits)}:null,
    facts:[['24時間の高値・安値',values.length?`${money(Math.max(...values),market.digits)} / ${money(Math.min(...values),market.digits)}（取引価格）`:''],
      ['契約',`${market.coin} · 無期限先物`],['単位',market.unit],['配信元',q?.source||''],
      ['受信',q?`${stamp(q.timestamp)} JST${q.stale?'（最終取得値）':''}`:''],['注記',q && q.source!=='Hyperliquid'?q.note:'価格はマーク価格、変化率は24時間比。チャートは15分足の取引価格。']],
    accent:q && isNumber(q.change) && q.change<0?'var(--down)':'var(--up)'});
}
const RELEASE_SOURCES={BLS:'米労働統計局（BLS）',BEA:'米経済分析局（BEA）',FRB:'米連邦準備制度理事会（FRB）'};
function openEventDetail(row){
  const event=calendarInfo?.data.events.find(item=>item.id===row.dataset.eventId);if(!event)return;
  const date=new Date(event.timestamp),days=Math.round((Date.parse(jstDay(event.timestamp))-Date.parse(jstDay(Date.now())))/86400000);
  const when=days===0?'今日':days===1?'明日':days>1?`あと${days}日`:'';
  openDetail({eyebrow:event.category,title:event.title,subtitle:`${when?`${when} · `:''}${FULL_JST.format(date)}`,
    facts:[['日本時間',FULL_JST.format(date)],['米国東部時間',FULL_ET.format(date)],['発表元',RELEASE_SOURCES[event.source]],['予想・結果','未接続（公式の発表日程のみ）'],['備考',event.note||'']],
    link:{href:event.url,label:'公式日程を開く'},accent:getComputedStyle(row).getPropertyValue('--cat').trim()});
}
function openNewsDetail(){
  const item=news[newsIndex];if(!item)return;
  openDetail({eyebrow:item.source,title:item.title,body:item.summary||'',facts:[['配信',`${stamp(Date.parse(item.publishedAt))} JST`]],link:{href:item.url,label:'NHKで続きを読む'}});
}
const FEEDS={connection:'ネットワーク',weather:'天気',air:'空気の状態',markets:'相場（12銘柄）','market:':'Hyperliquid','market:xyz':'trade.xyz','market:para':'para',charts:'チャート',crypto:'CoinGecko',calendar:'米国経済指標',news:'ニュース',spotify:'Spotify',photos:'背景写真'};
const FEED_STATES={ok:'最新',stale:'更新待ち（保存済みの値を表示）',error:'取得できません'};
function openStatusDetail(){
  const rows=Object.entries(FEEDS).filter(([key])=>feedState.has(key)).map(([key,label])=>[label,FEED_STATES[feedState.get(key)]||feedState.get(key),feedState.get(key)==='ok'?'':'warn']);
  const waiting=[...feedState.values()].some(state=>state!=='ok');
  openDetail({eyebrow:'TV HOME',title:'データの状態',subtitle:!navigator.onLine?'オフラインです。接続が戻ると自動で再取得します。':waiting?'一部の情報が更新を待っています。自動で再取得します。':'すべて最新です。',
    facts:rows,action:{label:'今すぐ再取得',run:()=>{closeDetail();$('refresh').click();}}});
}
// The economic calendar behaves like a scrolling list: moving past an edge turns the page.
function calendarEdge(current,direction){
  if(!current.classList.contains('calendar-event'))return false;
  const rows=[...$('calendar-events').querySelectorAll('.calendar-event')],index=rows.indexOf(current);
  if(direction==='down' && index===rows.length-1 && !$('calendar-next').disabled){calendarIndex++;showCalendar();$('calendar-events').querySelector('.calendar-event')?.focus({preventScroll:true});return true;}
  if(direction==='up' && index===0 && calendarIndex>0){calendarIndex--;showCalendar();[...$('calendar-events').querySelectorAll('.calendar-event')].at(-1)?.focus({preventScroll:true});return true;}
  return false;
}
function closeSettings(){ $('settings-overlay').hidden=true;$('stage').inert=false;document.body.classList.remove('modal-open');returnFocus?.focus({preventScroll:true}); }
function openSettings(section='general') {
  returnFocus=document.activeElement;selectedLocation={...config.location};
  $('city-search').value='';$('city-results').replaceChildren();$('selected-city').textContent=`現在：${selectedLocation.name}`;
  $('market-mode').value=config.marketMode;$('crypto-source-select').value=config.cryptoSource;$('photo-mode').value=config.photoMode;$('photo-interval').value=String(config.photoInterval);$('motion').checked=config.motion;
  $('market-mode').querySelector('[value="tradingview"]').disabled=Boolean(window.Android);
  $('spotify-client-id').value=config.spotifyClientId || backend.spotifyClientId || '';$('api-base').value=config.apiBase;$('spotify-redirect').textContent=spotify.redirectUri();
  $('photo-help').textContent=backend.unsplash?'Unsplash APIキー設定済み。NYの風景を1時間ごとに取得します。':'Unsplashはサーバー側のUNSPLASH_ACCESS_KEY設定後に利用できます。';
  $('adblock-dns').value=config.adblockDns;$('adblock-message').textContent='';renderNativeAdBlock();
  if(Date.now()-adblockCheckedAt>60000 || !adblockStatus)void checkAdBlock();
  $('spotify-message').textContent='';$('settings-error').textContent='';$('settings-overlay').hidden=false;$('stage').inert=true;document.body.classList.add('modal-open');
  // On the TV app, focusing the Client ID field would pop up the on-screen keyboard straight away.
  (section==='market' ? $('market-mode') : section==='spotify' ? (window.Android ? $('connect-in-settings') : $('spotify-client-id')) : $('close-settings')).focus();
}
async function saveSettings({close=true}={}) {
  const clientId=$('spotify-client-id').value.trim(), apiBase=$('api-base').value.trim();
  if(clientId && !/^[a-f0-9]{32}$/.test(clientId))throw new Error('Spotify Client IDは32文字の英数字です');
  if(apiBase && !safeUrl(apiBase))throw new Error('データサーバーにはHTTPSのURLを指定してください');
  const adblockDns=$('adblock-dns').value.trim().toLowerCase()||DEFAULT_ADBLOCK_DNS;
  if(!validDnsHost(adblockDns))throw new Error('広告ブロックのDNSサーバーの形式を確認してください');
  // A new server is applied straight away when the TV is already blocking through the old one.
  const native=nativePrivateDns();
  if(native?.mode==='hostname' && native.host && native.host!==adblockDns){const result=setNativePrivateDns(adblockDns);if(!result.ok)throw new Error(result.error);}
  const next=normalizeConfig({...config,location:selectedLocation,marketMode:$('market-mode').value,cryptoSource:$('crypto-source-select').value,photoMode:$('photo-mode').value,photoInterval:Number($('photo-interval').value),motion:$('motion').checked,spotifyClientId:clientId,apiBase,adblockDns});
  if(config.spotifyClientId && config.spotifyClientId!==next.spotifyClientId)spotify.disconnect();
  const locationChanged=config.location.latitude!==next.location.latitude || config.location.longitude!==next.location.longitude;
  if(config.apiBase!==next.apiBase){quotes.clear();renderStocks();}
  if(config.cryptoSource!==next.cryptoSource){clearQuotes(['BTC','HYPE']);unavailable.delete('BTC');unavailable.delete('HYPE');}
  config=next;
  const persisted=writeStorage(storage,'tv-home-config',config);
  if(locationChanged){resetHourlyForecast();$('temperature').textContent='--°';$('weather-label').textContent='取得中';$('tomorrow').textContent='予報を取得しています';$('sunrise').textContent='日の出 —';$('sunset').textContent='日の入 —';$('air').textContent='空気 —';}
  backend=await api('config').catch(()=>({backend:false,market:false,unsplash:false}));
  applyConfig();if(close)closeSettings();toast(persisted?'設定を保存しました':'このブラウザでは設定を保存できません。現在の画面にのみ反映しました');
}
let searchVersion=0;
async function searchCity() {
  const query=$('city-search').value.trim();if(!query)return;
  const version=++searchVersion;$('search-city').disabled=true;$('city-results').textContent='検索中…';
  try{
    const response=await fetchJSON(`https://geocoding-api.open-meteo.com/v1/search?${new URLSearchParams({name:query,count:6,language:'ja',format:'json',countryCode:'JP'})}`);
    if(version!==searchVersion)return;$('city-results').replaceChildren();
    const rows=(response.results || []).filter(r=>r.country_code==='JP');
    if(!rows.length)$('city-results').textContent='地域が見つかりません。英語表記（例：Shibuya）でも検索できます。';
    rows.forEach(row=>{const button=el('button','',`${row.name} · ${row.admin1 || ''} ${row.admin2 || ''}`);button.type='button';button.onclick=()=>{selectedLocation={name:row.admin2 || row.name,latitude:row.latitude,longitude:row.longitude};$('selected-city').textContent=`選択：${selectedLocation.name}`;$('city-results').replaceChildren();$('search-city').focus();};$('city-results').append(button);});
  }catch{$('city-results').textContent='地域を検索できませんでした。再度お試しください。';}finally{if(version===searchVersion)$('search-city').disabled=false;}
}
function initializeBridge() {
  try{
    if(!window.Android || typeof window.Android.getApps!=='function')return;
    const apps=JSON.parse(window.Android.getApps());if(!Array.isArray(apps))return;
    const valid=apps.filter(a=>typeof a.name==='string' && /^[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+$/.test(a.packageName)).slice(0,12);
    if(!valid.length)return;
    const settings=$('apps').querySelector('[data-open-settings]');$('apps').replaceChildren();
    for(const app of valid)$('apps').append(nativeAppTile(app));
    $('apps').append(settings);$('apps').classList.add('native-apps');
  }catch{toast('アプリ一覧を取得できません。Web版の一覧を表示します。');}
}

if(frostSupported())frost=new Frost(document.querySelector('.frost'),[...document.querySelectorAll('.frost-layer')]);
const slideshow=new Slideshow({layers:[...document.querySelectorAll('.photo-layer')],caption:$('photo-credit'),title:$('photo-title'),frost,onFrost:updateFrost,onError:()=>{setFeed('photos','error');$('photo-title').textContent='背景写真を読み込めませんでした';}});
// The photo switch is only offered when there is another photo to switch to.
function setPhotos(photos){slideshow.setPhotos(photos);$('next-photo').hidden=slideshow.photos.length<2;}
document.addEventListener('click',event=>{
  const open=event.target.closest('[data-open-settings]');if(open){openSettings(open.dataset.openSettings);return;}
  // OK on a row or headline shows details in place: following a link would leave the launcher.
  const row=event.target.closest('#stage .stock-row');if(row){openMarketDetail(row.dataset.symbol);return;}
  const release=event.target.closest('#stage .calendar-event');if(release){event.preventDefault();openEventDetail(release);return;}
  if(event.target.closest('#news-title') && news.length){event.preventDefault();openNewsDetail();return;}
  if(event.target.closest('#connection-status')){openStatusDetail();return;}
  const app=event.target.closest('[data-app],[data-package]');if(!app)return;
  pressApp(app);
  if(app.dataset.package && typeof window.Android?.launchApp==='function'){
    try{window.Android.launchApp(app.dataset.package);}catch{toast('アプリを起動できませんでした');}
  }else toast('Web版ではアプリを起動できません。TV版のランチャーで接続します。');
});
$('apps').addEventListener('pointermove',event=>{
  if(event.pointerType==='mouse')event.target.closest('.app-tile')?.focus({preventScroll:true});
});
$('close-settings').onclick=closeSettings;$('cancel-settings').onclick=closeSettings;
$('close-detail').onclick=closeDetail;
$('detail-overlay').addEventListener('click',event=>{if(event.target===$('detail-overlay'))closeDetail();});
$('settings-overlay').addEventListener('click',event=>{if(event.target===$('settings-overlay'))closeSettings();});
$('settings-form').onsubmit=async event=>{event.preventDefault();try{await saveSettings();}catch(error){$('settings-error').textContent=errorText(error);}};
$('search-city').onclick=searchCity;$('city-search').onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();void searchCity();}};
$('calendar-prev').onclick=()=>{calendarIndex=Math.max(0,calendarIndex-1);showCalendar();};
$('calendar-next').onclick=()=>{calendarIndex++;showCalendar();};
$('next-news').onclick=()=>{if(news.length){newsIndex=(newsIndex+1)%news.length;showNews();scheduleNews();}};
$('next-photo').onclick=()=>{if(slideshow.photos.length<2)toast('現在は同梱写真1枚です。設定でUnsplashを接続すると自動切替できます。');else void slideshow.next();};
$('refresh').onclick=async()=>{const button=$('refresh');button.disabled=true;try{await Promise.allSettled(jobs.map(job=>job.run(true)));toast('データを確認しました。取得制限のため連続更新は30秒間隔です。');}finally{button.disabled=false;}};
$('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else if(document.documentElement.requestFullscreen)await document.documentElement.requestFullscreen();else toast('このブラウザでは全画面表示を利用できません');}catch{toast('全画面表示を開始できませんでした');}};
document.addEventListener('fullscreenchange',()=>{$('fullscreen').setAttribute('aria-label',document.fullscreenElement?'全画面を終了':'全画面に切り替え');});
$('spotify-connect').onclick=()=>openSettings('spotify');
$('adblock-check').onclick=()=>void checkAdBlock();
$('adblock-toggle').onchange=()=>{
  const on=$('adblock-toggle').checked,host=$('adblock-dns').value.trim().toLowerCase()||DEFAULT_ADBLOCK_DNS;
  const result=setNativePrivateDns(on?host:'');
  $('adblock-message').textContent=!result.ok?result.error:on?`プライベートDNSを ${host} にしました。反映まで少し時間がかかることがあります。`:'プライベートDNSをAndroid標準の「自動」に戻しました。';
  renderNativeAdBlock();if(result.ok)setTimeout(()=>void checkAdBlock(),2500);
};
$('connect-in-settings').onclick=async()=>{try{await saveSettings({close:false});await spotify.connect(config.spotifyClientId || backend.spotifyClientId);}catch(error){$('spotify-message').textContent=errorText(error);}};
$('disconnect-spotify').onclick=()=>{spotify.disconnect();renderMusic({connected:false});$('spotify-message').textContent='このブラウザの連携情報を削除しました';};
const navigation=installNavigation({modals:[{element:$('settings-overlay'),close:closeSettings},{element:$('detail-overlay'),close:closeDetail}],home:()=>$('apps'),onEdge:calendarEdge});
// A passive dashboard rests with focus on the dock, so a forgotten highlight never lingers on a card.
let lastInput=Date.now();
for(const type of ['keydown','pointerdown'])addEventListener(type,()=>{lastInput=Date.now();},{capture:true,passive:true});
setInterval(()=>{if(document.body.classList.contains('tv') && !document.hidden && Date.now()-lastInput>IDLE_HOME && $('settings-overlay').hidden && $('detail-overlay').hidden)navigation.focusHome();},10000);
addEventListener('resize',fit);addEventListener('online',()=>{setFeed('connection','ok');jobs.forEach(job=>void job.run());});addEventListener('offline',()=>{setFeed('connection','error');});
document.addEventListener('visibilitychange',()=>{if(document.hidden)cryptoStream?.stop();else{cryptoStream?.start();tick();jobs.forEach(job=>void job.run());}});
addEventListener('pagehide',()=>cryptoStream?.stop());
addEventListener('pageshow',event=>{if(event.persisted && !document.hidden)cryptoStream?.start();});
setInterval(()=>{if(!document.hidden)tick();},1000);
// Restarted on manual paging so a headline chosen by hand gets its full time on screen.
let newsTimer;
function scheduleNews(){clearInterval(newsTimer);newsTimer=setInterval(()=>{if(!document.hidden && $('settings-overlay').hidden && $('detail-overlay').hidden && news.length>1 && document.activeElement!==$('news-title')){newsIndex=(newsIndex+1)%news.length;showNews();}},NEWS_INTERVAL);}
scheduleNews();
// Loaded as a print sheet so it never blocks the first paint; the CSP forbids an inline onload.
function enableJapaneseFont(){const link=$('font-ja');if(!link)return;const on=()=>{link.media='all';};if(link.sheet)on();else link.addEventListener('load',on,{once:true});}
async function start(){
  enableJapaneseFont();
  fit();buildStocks();tick();setPhotos(SAMPLE_PHOTOS);initializeBridge();void loadCalendarSnapshot();
  // The TV app already runs full screen; the button only helps in a desktop browser.
  $('fullscreen').hidden=Boolean(window.Android) || !document.fullscreenEnabled;
  document.body.classList.add('ready');
  if(document.body.classList.contains('tv'))$('apps').querySelector('button')?.focus({preventScroll:true});
  try{if(await spotify.completeCallback())toast('Spotifyを連携しました');}catch(error){toast(errorText(error));}
  backend=await api('config').catch(()=>({backend:false,market:false,unsplash:false}));
  applyConfig();
}
void start();
