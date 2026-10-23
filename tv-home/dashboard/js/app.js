import { DEFAULT_CONFIG, normalizeConfig, readStorage, writeStorage, fetchJSON, cachedLoad, money, signed, tone, isNumber, safeUrl, weatherLabel, airLabel, getWeather, getAir, getCrypto } from './data.js';
import { eventPage, jstDay } from './calendar.js';
import { loadEarnings, upcomingEarnings } from './earnings.js';
import { installNavigation } from './navigation.js';
import { nativeAppTile, pressApp } from './launcher.js';
import { DOCK_KEY, arrangeDock, moveInDock, setOnDock, normalizeDock } from './dock.js';
import { Slideshow, SAMPLE_PHOTOS } from './slideshow.js';
import { Frost, frostSupported } from './frost.js';
import { dayPart, photoRetryDelay, photosPart } from './daypart.js';
import { DEFAULT_ADBLOCK_DNS, adBlockStatus, nativePrivateDns, setNativePrivateDns, validDnsHost } from './adblock.js';
import * as spotify from './spotify.js';
import { mountTradingView } from './tradingview.js';
import { getMarketSnapshot, getMarketCandles, HyperliquidStream } from './hyperliquid.js';
import { MARKETS, MARKET_BY_SYMBOL, CHART_RANGES, marketCoins } from './market-definitions.js';
import { drawMarketChart, drawDetailChart } from './market-chart.js';
import { loadNews, loadCalendar, loadPhotos } from './feeds.js';
import { JIKKA } from './profile.js';
import { readInputs, renderInputs, renderRecent, switchInput } from './jikka.js';
import { HOUR, weatherTimestamp, weatherIsStale, hourlyForecast, makeWeatherIcon, renderHourlyForecast, dailyForecast, temperatureColor, windDirection, uvLabel } from './weather.js';

const $ = id => document.getElementById(id);
const CALENDAR_PAGE_SIZE = 6, NEWS_INTERVAL = 20000, CARD_RADIUS = 32, IDLE_HOME = 60000;
const storage = { getItem:key => { try{return localStorage.getItem(key);}catch{return null;} }, setItem:(key,value) => localStorage.setItem(key,value) };
let config = normalizeConfig(readStorage(storage,'tv-home-config',DEFAULT_CONFIG));
let backend = {backend:false,market:false,unsplash:false};
let photoPart='night', photosJob=null, themeTimer=0, photoRetry={at:0,attempt:0}, photoToastAt=0;
let generation=0, jobs=[], news=[], newsIndex=0, music=null, toastTimer, returnFocus, selectedLocation=config.location;
let calendarInfo=null, calendarIndex=0, calendarNextTime=0, earningsInfo=null, calendarSource={text:'',title:''};
let weatherResult=null, airResult=null, nextForecastHour=0, weatherWasStale=false;
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
// The TV app serves this page from its own origin with no Node server: news and the calendar are
// parsed here, and the feeds (which send no CORS headers) are fetched by the app's native proxy.
const IN_APP = location.hostname==='appassets.androidplatform.net';
const appText = async url => (await fetchJSON(`/api/upstream?url=${encodeURIComponent(url)}`)).text;
async function appApi(path) {
  if(path==='config'){
    const spotifyClientId=typeof window.Android?.spotifyClientId==='function' ? String(window.Android.spotifyClientId()) : '';
    const unsplash=typeof window.Android?.hasUnsplash==='function' && window.Android.hasUnsplash()===true;
    return {backend:true,market:false,unsplash,spotifyClientId:/^[a-f0-9]{32}$/.test(spotifyClientId)?spotifyClientId:''};
  }
  // The app adds the Unsplash Access Key itself; the page never sees it.
  const data = path==='news' ? await loadNews(appText) : path==='calendar' ? await loadCalendar(appText,await fetchJSON('data/economic-calendar.json')) : path==='earnings' ? await loadEarnings(appText) : path.startsWith('photos/') ? await loadPhotos(query=>fetchJSON(`/api/unsplash?query=${encodeURIComponent(query)}`),path.slice(7)) : null;
  if(!data)throw new Error('TV版では使えません');
  return {data,fetchedAt:Date.now(),stale:path==='calendar' && data.sources.some(s=>s.status==='stale')};
}
const apiAt = (base, path) => IN_APP && !base ? appApi(path) : fetchJSON(`${base}/api/${path}`);
const api = path => apiAt(config.apiBase, path);
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
// TV only: the whole 1920×1080 screen (dashboard, sheets, toast) is scaled to the WebView, which
// usually reports 960×540 CSS px on a 1080p/4K Google TV, and letterboxed if the aspect differs.
function fit() {
  // The Cast receiver on the Xiaomi TV (Chrome 92) reports innerWidth 3840×2160 while showing 960×540,
  // so measure the visible area of the root element instead.
  const root=document.documentElement,width=root.clientWidth||innerWidth,height=root.clientHeight||innerHeight;
  stageScale=Math.min(width/1920,height/1080);
  Object.assign($('screen').style,{transform:`scale(${stageScale})`,left:`${(width-1920*stageScale)/2}px`,top:`${(height-1080*stageScale)/2}px`});
  updateFrost();
}
// The screen never scrolls, so the frosted layer only needs re-clipping when it is refitted
// or the dock shelf changes width.
function updateFrost() {
  const on=Boolean(frost?.ready);
  if(on)frost.clip([...document.querySelectorAll('#stage .card,#stage .dock')],CARD_RADIUS*stageScale);
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
  updateDayPart(now.getTime());
  if(calendarNextTime && now.getTime()>=calendarNextTime)showCalendar();
  if(weatherResult && (now.getTime()>=nextForecastHour || (!weatherWasStale && weatherIsStale(weatherResult,now.getTime()))))renderWeather(weatherResult);
  if(!JIKKA)updateCryptoStatus();
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
  $('hourly-status').textContent=!available?'未取得':stale?'保存した予報 · 更新待ち':'';
  $('hourly-status').classList.toggle('forecast-stale',stale || !available);
  // A fresh forecast only needs the time; a stale one keeps its date.
  $('weather-source').textContent=`Open-Meteo · ${Number.isFinite(observed)?stale?stamp(observed):time(new Date(observed)):'時刻不明'} 予測${stale?' · 更新待ち':''}`;
  $('weather-source').title=Number.isFinite(observed)?`Open-Meteo（CC BY 4.0）· ${stamp(observed)} JSTのモデル予測`:'Open-Meteo';
  $('weather-source').dataset.state=stale?'stale':'ok';
  setFeed('weather',stale || !available?'stale':'ok');
}
function renderAir(result) {
  airResult=result;
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
  if(JIKKA)setText($('news-summary'),current.summary||'');
  const old=Date.now()-Date.parse(current.publishedAt)>2*86400000;
  $('news-source').textContent=`${current.source} · ${stamp(Date.parse(current.publishedAt))}${old?' · 過去の配信':''}`;
  $('next-news').setAttribute('aria-label',`次のニュース（${newsIndex+1} / ${news.length}）`);
  $('news-dots').replaceChildren(...news.map((_,i)=>el('i',i===newsIndex?'active':'')));
}
// In the TV app, the Spotify TV app's own now playing (read from its media session) needs no Spotify login.
// Null when the app cannot read it (no notification access), so the web login is used instead.
function tvNowPlaying() {
  try{const raw=typeof window.Android?.nowPlaying==='function' ? window.Android.nowPlaying() : '';return raw ? JSON.parse(raw) : null;}catch{return null;}
}
// Album art from the media session arrives as a JPEG data URL; nothing else is accepted from it.
const tvArtwork = url => typeof url==='string' && /^data:image\/jpeg;base64,[A-Za-z0-9+/=]+$/.test(url) ? url : '';
// The app calls this whenever the track or play state changes, so the card follows without waiting for the poll.
window.tvHomeMedia = () => {const data=tvNowPlaying();if(data)renderMusic(data);};
function renderMusic(data) {
  music=data;$('spotify-connect').hidden=Boolean(data.connected);$('music-progress').hidden=!data.item;
  if(!data.connected){$('track-name').textContent='音楽を、この画面に。';$('artist-name').textContent='再生中の曲を表示';$('music-state').dataset.state='idle';$('track-name').removeAttribute('href');resetAlbum();return;}
  if(!data.item){$('track-name').textContent='再生していません';$('artist-name').textContent='Spotifyで音楽を再生してください';$('music-state').dataset.state='paused';$('track-name').removeAttribute('href');resetAlbum();return;}
  $('track-name').textContent=data.item.name || 'タイトルなし';const url=safeUrl(data.item.external_urls?.spotify);if(url)$('track-name').href=url;else $('track-name').removeAttribute('href');
  $('artist-name').textContent=data.item.artists?.map(a=>a.name).join(' / ') || data.item.show?.publisher || '';
  $('music-state').dataset.state=data.is_playing?'playing':'paused';
  const imageUrl=data.source==='tv' ? tvArtwork(data.item.album?.images?.[0]?.url) : safeUrl(data.item.album?.images?.at(-2)?.url || data.item.album?.images?.[0]?.url || data.item.images?.[0]?.url);
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
  calendarInfo=result;
  const sources=result.data.sources||[],expired=sources.some(source=>Date.parse(source.coverageThrough)<Date.now());
  const stale=result.stale || expired;
  const live=sources.filter(source=>source.status==='live').map(source=>source.source);
  const frb=sources.find(source=>source.source==='FRB');
  calendarSource.text=stale?'保存済み日程 · 一部更新待ち':`${live.join('・')} 自動更新 / FRB ${frb?.verifiedAt?.slice(5,10).replace('-','/')||'—'}確認`;
  calendarSource.title=sources.map(source=>`${source.source}: ${source.status==='live'?'自動取得':'保存済み'} / ${source.verifiedAt}確認 / ${source.coverageThrough}まで収録`).join('\n')+'\n予定は変更される場合があります。';
  showCalendar();setFeed('calendar',stale?'stale':'ok');
}
function renderEarnings(result){earningsInfo=result;showCalendar();setFeed('earnings',result.stale || result.data.missing?'stale':'ok');}
// The card's first page is the next six US releases; turning it shows the coming weeks' earnings of
// major US companies, six at a time (js/earnings.js), since releases further out matter little.
function showCalendar() {
  if(!calendarInfo && !earningsInfo)return;
  const focusedId=document.activeElement?.dataset.eventId,focusedPage=document.activeElement?.id;
  const earnings=upcomingEarnings(earningsInfo?.data.events),earningPages=earningsInfo?Math.max(1,Math.ceil(earnings.length/CALENDAR_PAGE_SIZE)):0;
  const pages=1+earningPages;calendarIndex=Math.min(Math.max(0,calendarIndex),pages-1);
  $('calendar-page').textContent=pages>1?`${calendarIndex+1} / ${pages}`:'';
  $('calendar-prev').disabled=calendarIndex===0;$('calendar-next').disabled=calendarIndex>=pages-1;
  if(calendarIndex>0){showEarnings(earnings.slice((calendarIndex-1)*CALENDAR_PAGE_SIZE,calendarIndex*CALENDAR_PAGE_SIZE),focusedId,focusedPage);return;}
  setText($('calendar-title'),'米国経済指標');$('calendar-source').textContent=calendarSource.text;$('calendar-source').title=calendarSource.title;
  $('calendar-events').replaceChildren();
  if(!calendarInfo){$('calendar-events').append(el('p','calendar-empty','公式日程を確認しています'));return;}
  const data=eventPage(calendarInfo.data.events,0,CALENDAR_PAGE_SIZE);
  if(!data.events.length)$('calendar-events').append(el('p','calendar-empty','今後の予定を確認できません。公式日程の更新をお待ちください。'));
  const today=jstDay(Date.now()),tomorrow=jstDay(Date.now()+86400000);let previousDay='';
  data.events.forEach((event,index)=>{
    const row=el('a','calendar-event');row.href=safeUrl(event.url);row.target='_blank';row.rel='noopener noreferrer';row.dataset.indicator=event.indicator;row.dataset.eventId=event.id;
    const date=new Date(event.timestamp),day=el('div','calendar-day number'),eventDay=jstDay(event.timestamp);
    day.append(el('strong','',MONTH_DAY.format(date)),el('span','',eventDay===today?'今日':eventDay===tomorrow?'明日':WEEKDAY_SHORT.format(date)));
    // Like a calendar list, a date is written once for releases on the same day.
    if(eventDay===previousDay)row.classList.add('same-day');previousDay=eventDay;
    const detail=el('div','calendar-detail');detail.append(el('span','calendar-title',event.title));
    const at=el('time','calendar-time number',time(date));at.dateTime=date.toISOString();
    row.append(day,detail,at);row.title=`${event.originalTitle} / ${event.source} / ${date.toISOString()}${event.note?' / '+event.note:''}`;
    row.setAttribute('aria-label',`${dated(date)} ${time(date)} 日本時間 ${event.title} ${event.source}の公式日程を開く`);
    if(index===0)row.classList.add('next-event');
    $('calendar-events').append(row);
  });
  restoreCalendarFocus(focusedId,focusedPage);
  // Only advance automatically when the first upcoming release passes.
  calendarNextTime=eventPage(calendarInfo.data.events,0,1).events[0]?.timestamp||0;
}
function restoreCalendarFocus(focusedId,focusedPage){
  if(focusedId){const links=[...$('calendar-events').children];(links.find(link=>link.dataset.eventId===focusedId)||links[0])?.focus({preventScroll:true});}
  if(['calendar-prev','calendar-next'].includes(focusedPage) && $(focusedPage).disabled){const alternate=$(focusedPage==='calendar-prev'?'calendar-next':'calendar-prev');if(!alternate.disabled)alternate.focus({preventScroll:true});}
}
// An earnings row: the Japan-time date of the report, the company, and whether it comes before the
// New York open (that evening in Japan) or after the close (the next morning in Japan).
const TIMING_LABEL={pre:'寄り前',after:'引け後',unknown:'時刻未定'};
// A company's logo (bundled, see js/earnings.js); without one the ticker stands alone.
const earningsLogo=(symbol,className)=>{const logo=el('img',className);logo.alt='';logo.src=`assets/earnings/${symbol}.png`;logo.onerror=()=>logo.remove();return logo;};
function showEarnings(rows,focusedId,focusedPage){
  setText($('calendar-title'),'主要企業の決算');
  const info=earningsInfo.data,stale=earningsInfo.stale || info.missing>0;
  $('calendar-source').textContent=`Nasdaq · ${info.companies}社${stale?' · 一部更新待ち':''}`;
  $('calendar-source').title=`Nasdaqの決算カレンダー（${info.from}〜${info.through}、米国の日付）から市況への影響が大きい${info.companies}社を表示。日付と時刻は日本時間で、時刻は各社のいつもの発表時刻。発表日は変更される場合があります。`;
  $('calendar-events').replaceChildren();
  if(!rows.length)$('calendar-events').append(el('p','calendar-empty','今後8週間、主要企業の決算予定はありません'));
  const today=jstDay(Date.now()),tomorrow=jstDay(Date.now()+86400000);let previousDay='';
  rows.forEach((event,index)=>{
    const row=el('a','calendar-event earnings-event');row.href=`https://www.nasdaq.com/market-activity/stocks/${event.symbol.toLowerCase().replace('.','-')}/earnings`;row.target='_blank';row.rel='noopener noreferrer';
    row.dataset.indicator=`EARNINGS-${event.timing}`;row.dataset.eventId=event.id;row.dataset.earnings='';
    const date=new Date(event.timestamp),eventDay=jstDay(event.timestamp),day=el('div','calendar-day number');
    day.append(el('strong','',MONTH_DAY.format(date)),el('span','',eventDay===today?'今日':eventDay===tomorrow?'明日':WEEKDAY_SHORT.format(date)));
    if(eventDay===previousDay)row.classList.add('same-day');previousDay=eventDay;
    const detail=el('div','calendar-detail calendar-company');detail.append(earningsLogo(event.symbol,'calendar-logo'),el('span','calendar-title',event.symbol));
    // The usual release time in Japan; when Nasdaq disagrees with it, only the session.
    const at=event.exact?el('time','calendar-time number',time(date)):el('span','calendar-time calendar-timing',TIMING_LABEL[event.timing]);
    if(event.exact)at.dateTime=date.toISOString();
    row.append(day,detail,at);
    row.setAttribute('aria-label',`${dated(date)} ${event.exact?time(date):TIMING_LABEL[event.timing]} 日本時間 ${event.symbol}（${event.company}）決算`);
    if(index===0 && calendarIndex===1)row.classList.add('next-event');
    $('calendar-events').append(row);
  });
  restoreCalendarFocus(focusedId,focusedPage);
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
  const base=config.apiBase, apiForJob=path=>apiAt(base,path);
  const sameLocation=()=>location.latitude===config.location.latitude && location.longitude===config.location.longitude;
  jobs.push(makeJob('weather',15*60000,cachedTask('weather',()=>getWeather(location),result=>{if(sameLocation())renderWeather(result);}),error=>{if(sameLocation())clearWeather(error);}));
  jobs.push(makeJob('air',30*60000,cachedTask('air',()=>getAir(location),renderAir),()=>{$('air').textContent='空気 未取得';}));
  if(!JIKKA && config.marketMode==='custom'){
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
    if(!JIKKA)jobs.push(makeJob('calendar',6*3600000,cachedTask('economic-calendar',()=>apiForJob('calendar'),renderCalendar,{server:true,maxAge:7*86400000}),()=>{if(calendarInfo)renderCalendar({...calendarInfo,stale:true});else void loadCalendarSnapshot();}));
    if(!JIKKA)jobs.push(makeJob('earnings',12*3600000,cachedTask('earnings',()=>apiForJob('earnings'),renderEarnings,{server:true,maxAge:3*86400000}),()=>{if(earningsInfo)renderEarnings({...earningsInfo,stale:true});}));
    jobs.push(makeJob('news',15*60000,cachedTask('news',()=>apiForJob('news'),renderNews,{server:true}),()=>{news=[];$('news-title').textContent='ニュースを取得できません';$('news-title').removeAttribute('href');$('news-source').textContent='NHK · しばらくして再取得します';$('next-news').setAttribute('aria-label','次のニュース');$('news-dots').replaceChildren();}));
    // The parents' TV starts on Unsplash, so it waits quietly on the bundled photo until a key is built in.
    if(config.photoMode==='unsplash' && (backend.unsplash || !JIKKA))jobs.push(photosJob=makeJob('photos',3600000,async current=>{
      // New York at this time of day; each period keeps its own saved set for a quick switch.
      const part=photoPart,result=await cachedLoad({key:photoCacheKey(part),storage,maxAge:7*86400000,load:()=>apiForJob(`photos/${part}`)});
      if(!current() || part!==photoPart)return;
      setPhotos(result.data.data);setFeed('photos',result.stale || result.data.stale?'stale':'ok');
    },()=>{
      // Retries keep coming while offline; one note an hour is enough.
      if(Date.now()-photoToastAt>3600000){photoToastAt=Date.now();toast('Unsplashを取得できません。同梱写真を表示しています。');}
    }));
  }else{
    $('news-title').textContent='ニュースはサーバー接続後に表示';$('news-source').textContent='設定でデータサーバーを指定できます';
    if(config.photoMode==='unsplash')toast('Unsplashの自動取得にはAPIサーバーが必要です');
  }
  // The parents' TV: the recent apps change whenever an app is used, so they are re-read on every return home.
  if(JIKKA){jobs.push(makeJob('recent',60000,async()=>{showJikka();setFeed('recent','ok');}));return;}
  jobs.push(makeJob('spotify',30000,async current=>{const data=tvNowPlaying() ?? await spotify.currentlyPlaying();if(current())renderMusic(data);},error=>{$('artist-name').textContent=errorText(error);$('music-state').dataset.state='error';music=null;$('music-progress').hidden=true;$('spotify-connect').hidden=false;}));
}
function configureMarket() {
  if(JIKKA)return;
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
  configureMarket();photoPart=currentDayPart();photosJob=null;setPhotos(startingPhotos());slideshow.schedule(config.photoInterval);restartJobs();tick();
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
function openDetail({eyebrow='',title,subtitle='',body='',facts=[],chart=null,link=null,action=null,accent='',wide=false}){
  detailReturn=document.activeElement;
  // Markets use the wide sheet with a period switch (openMarketDetail fills it in).
  $('detail-sheet').classList.toggle('market-detail',wide);$('detail-ranges').hidden=!wide;
  $('detail-sheet').classList.remove('weather-detail');$('detail-weather').hidden=true;
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
function closeDetail(){ detailLoad++;detailChart=null;$('detail-overlay').hidden=true;$('stage').inert=false;document.body.classList.remove('modal-open');if(detailReturn?.isConnected)detailReturn.focus({preventScroll:true});else navigation.focusHome(); }
// A market's detail: a period switch, a large chart with price and time scales, and a cursor that
// reads the price at any moment (← → on the chart). Longer ranges are fetched when first chosen and
// kept for a few minutes; the 24-hour range reuses the home screen's chart data.
const DETAIL_RANGES=['1d','1w','1m','3m','1y'],PERIOD_NAMES={'1d':'24時間','1w':'1週間','1m':'1か月','3m':'3か月','1y':'1年'};
const detailSeries=new Map();
let detailRange='1d',detailMarket=null,detailChart=null,detailIndex=null,detailLoad=0;
async function marketSeries(market,range){
  const key=`${market.coin}:${range}`,cached=detailSeries.get(key);
  if(range===config.chartRange && histories.has(key) && !histories.get(key).stale)return histories.get(key);
  if(cached && Date.now()-cached.fetchedAt<Math.max(5*60000,CHART_RANGES[range].intervalMs))return cached.series;
  const series=await getMarketCandles(market.coin,range);
  detailSeries.set(key,{series,fetchedAt:Date.now()});return series;
}
const ISO_DATE=day=>day.replaceAll('-','/');
function openMarketDetail(symbol){
  const market=MARKET_BY_SYMBOL.get(symbol),q=quotes.get(symbol);
  detailMarket=market;detailChart=null;
  openDetail({eyebrow:market.name,title:q?`${symbol} ${money(q.price,market.digits)}`:symbol,wide:true,
    accent:q && isNumber(q.change) && q.change<0?'var(--down)':'var(--up)'});
  const charts=config.marketMode==='custom' && (config.cryptoSource==='hyperliquid' || Boolean(market.dex));
  $('detail-ranges').hidden=!charts;
  $('detail-ranges').replaceChildren(...DETAIL_RANGES.map(range=>{
    const button=el('button','range-option',CHART_RANGES[range].name);button.type='button';button.dataset.range=range;
    button.onclick=()=>void showMarketRange(range);return button;
  }));
  if(!charts){renderMarketFacts(market,null,'1d');return;}
  void showMarketRange(detailRange);
  $('detail-ranges').querySelector(`[data-range="${detailRange}"]`).focus();
}
function renderMarketFacts(market,series,range){
  const q=quotes.get(market.symbol),spec=CHART_RANGES[range],values=series?.points.map(p=>p.value).filter(isNumber)||[];
  const periodChange=range==='1d' ? q?.change : series ? (series.points.at(-1).value-series.baseline)/series.baseline*100 : null;
  const subtitle=$('detail-subtitle');subtitle.hidden=false;
  if(!q && !series)subtitle.replaceChildren(unavailable.get(market.symbol)||'価格を取得しています');
  else{
    const change=el('span',`detail-change ${tone(periodChange)}`,isNumber(periodChange)?signed(periodChange):'—');
    const period=series?.since ? `${ISO_DATE(ISO_DAY.format(series.start))}から` : PERIOD_NAMES[range];
    subtitle.replaceChildren(`${period} `,change,range==='1d' && q?.stale?' · 更新待ち':'');
  }
  $('detail-sheet').style.setProperty('--sheet-accent',isNumber(periodChange) && periodChange<0?'var(--down)':'var(--up)');
  const fact=(term,value,wide=false)=>{const item=el('div',`detail-fact${wide?' wide':''}`);item.append(el('dt','',term),el('dd','',value||'—'));return item;};
  const price=v=>`${money(v,market.digits)}`;
  const note=q && q.source!=='Hyperliquid' ? q.note
    : `見出しの価格はマーク価格。チャートと高値・安値は${spec.bar}の取引価格で、点線は期間最初の足の始値${range==='1d'?'。変化率は24時間比':'。変化率はその始値との比較'}。${series?.since?`上場が新しいため、${ISO_DATE(ISO_DAY.format(series.start))}からの表示です。`:''}`;
  $('detail-facts').replaceChildren(
    fact('期間の高値',values.length?price(Math.max(...values)):''),fact('期間の安値',values.length?price(Math.min(...values)):''),fact('期間の始値',series?price(series.baseline):''),
    fact('契約',`${market.coin} · 無期限先物`),fact('単位',market.unit),fact('受信',q?`${stamp(q.timestamp)} JST${q.stale?'（最終取得値）':''} · ${q.source}`:''),
    fact('注記',note,true));
}
async function showMarketRange(range){
  const market=detailMarket,load=++detailLoad,box=$('detail-chart'),spec=CHART_RANGES[range];
  detailRange=range;detailChart=null;detailIndex=null;
  for(const button of $('detail-ranges').children)button.setAttribute('aria-pressed',String(button.dataset.range===range));
  box.hidden=false;box.removeAttribute('tabindex');box.removeAttribute('role');box.replaceChildren(el('p','detail-chart-status','読み込み中'));
  renderMarketFacts(market,null,range);
  let series=null;
  try{series=await marketSeries(market,range);}catch{}
  if(load!==detailLoad || $('detail-overlay').hidden)return;
  if(!series){box.replaceChildren(el('p','detail-chart-status','この期間の価格履歴を取得できません'));return;}
  // A market listed within the range is drawn from its first candle, and says so.
  const since=series.points[0].start>series.start+2*spec.intervalMs;
  const shown=since?{...series,start:series.points[0].start,since:true}:series;
  // Each candle is named by its opening time (a round hour or day).
  const when=range==='1y' ? p=>ISO_DATE(ISO_DAY.format(p.start)) : p=>stamp(p.start);
  detailChart=drawDetailChart(box,shown,{label:`${market.symbol} ${PERIOD_NAMES[range]}の取引価格`,price:(v,digits=market.digits)=>money(v,digits),change:v=>signed(v),when});
  if(!detailChart){box.replaceChildren(el('p','detail-chart-status','この期間の価格履歴が足りません'));return;}
  box.tabIndex=0;box.setAttribute('role','slider');box.setAttribute('aria-label',`${market.symbol} ${PERIOD_NAMES[range]}のチャート。左右で時点を移動`);
  box.setAttribute('aria-valuemin','0');box.setAttribute('aria-valuemax',String(detailChart.length-1));
  box.dataset.hint='チャートを選んで ← → で各時点の価格';
  renderMarketFacts(market,shown,range);
}
function scrubDetail(index){
  if(!detailChart)return;
  detailIndex=index===null ? null : Math.max(0,Math.min(detailChart.length-1,index));
  const text=detailChart.scrub(detailIndex);
  if(text){$('detail-chart').setAttribute('aria-valuenow',String(detailIndex));$('detail-chart').setAttribute('aria-valuetext',text);}
}
$('detail-chart').addEventListener('focus',()=>scrubDetail(detailChart ? detailChart.length-1 : null));
$('detail-chart').addEventListener('blur',()=>scrubDetail(null));
$('detail-chart').addEventListener('keydown',event=>{
  if(!detailChart)return;
  // Holding ← or → speeds up, so a year of daily candles crosses in a few seconds.
  if(event.key==='ArrowLeft' || event.key==='ArrowRight'){
    event.preventDefault();event.stopPropagation();
    const step=(event.repeat?Math.max(1,Math.round(detailChart.length/60)):1)*(event.key==='ArrowLeft'?-1:1);
    scrubDetail((detailIndex ?? detailChart.length-1)+step);
  }else if(event.key==='ArrowUp'){
    event.preventDefault();event.stopPropagation();$('detail-ranges').querySelector('[aria-pressed="true"]')?.focus();
  }
});
$('detail-chart').addEventListener('pointermove',event=>{
  if(!detailChart || event.pointerType!=='mouse')return;
  const box=$('detail-chart'),rect=box.getBoundingClientRect();
  if(document.activeElement!==box)box.focus({preventScroll:true});
  scrubDetail(detailChart.nearest((event.clientX-rect.left)*box.clientWidth/rect.width));
});
// The weather detail: now, the next 24 hours, the week ahead and the conditions behind today's
// forecast, all from the same Open-Meteo request as the card (and the CAMS air reading).
function openWeatherDetail(){
  const data=weatherResult?.data,current=data?.current,days=data?dailyForecast(data):[],today=days[0];
  const round=v=>isNumber(v)?`${Math.round(v)}°`:'—';
  openDetail({eyebrow:`天気 · ${$('location-name').textContent}`,
    title:current?`${round(current.temperature_2m)} ${weatherLabel(current.weather_code)}`:'天気',
    subtitle:current?[today && `最高 ${round(today.max)} · 最低 ${round(today.min)}`,isNumber(current.apparent_temperature) && `体感 ${round(current.apparent_temperature)}`,weatherWasStale && '更新待ち'].filter(Boolean).join(' · '):'天気を取得しています',
    accent:current && isNumber(current.temperature_2m)?temperatureColor(current.temperature_2m):''});
  $('detail-sheet').classList.add('weather-detail');
  const body=$('detail-weather');body.hidden=false;
  if(!current){body.replaceChildren(el('p','detail-chart-status','天気を取得しています'));return;}
  const block=(title,...children)=>{const section=el('section','weather-block');section.append(el('h3','weather-block-title',title),...children);return section;};
  const hours=el('div','hourly-forecast');
  renderHourlyForecast(hours,hourlyForecast(data,Date.now(),{count:12,step:2}),{id:'detail-hourly'});
  // Each day's low–high bar sits on the week's overall range, coloured like the temperature curve.
  const lows=days.map(d=>d.min).filter(isNumber),highs=days.map(d=>d.max).filter(isNumber);
  const lo=Math.min(...lows),hi=Math.max(...highs),at=v=>hi>lo?(v-lo)/(hi-lo)*100:50;
  const week=el('ol','week-list');
  for(const day of days){
    const row=el('li','week-row'),icon=el('span','week-icon');icon.append(makeWeatherIcon(day.code,1));
    const bar=el('span','week-bar');
    if(isNumber(day.min) && isNumber(day.max)){
      const fill=el('i');Object.assign(fill.style,{left:`${at(day.min)}%`,width:`${Math.max(2,at(day.max)-at(day.min))}%`,background:`linear-gradient(90deg,${temperatureColor(day.min)},${temperatureColor(day.max)})`});bar.append(fill);
      if(day===today && isNumber(current.temperature_2m)){const now=el('b','week-now');now.style.left=`${at(Math.min(hi,Math.max(lo,current.temperature_2m)))}%`;bar.append(now);}
    }
    row.setAttribute('aria-label',`${day.label} ${weatherLabel(day.code)} 最低${round(day.min)} 最高${round(day.max)}${isNumber(day.probability)?` 降水確率${day.probability}%`:''}`);
    row.append(el('span','week-day',day.label),icon,el('span',`week-rain number${day.probability>=40?' rain-likely':''}`,isNumber(day.probability) && day.probability>=20?`${day.probability}%`:''),
      el('span','week-min number',round(day.min)),bar,el('span','week-max number',round(day.max)));
    week.append(row);
  }
  const tile=(label,value,sub)=>{const item=el('div','weather-tile');item.append(el('span','tile-label',label),el('span','tile-value number',value),el('span','tile-sub',sub||''));return item;};
  const fixed=(v,digits,unit)=>isNumber(v)?`${v.toFixed(digits)}${unit}`:'—';
  const feels=current.apparent_temperature-current.temperature_2m,direction=windDirection(current.wind_direction_10m),aqi=airResult?.data?.current;
  const tiles=el('div','weather-tiles');
  tiles.append(
    tile('体感温度',round(current.apparent_temperature),isNumber(feels)?Math.abs(feels)<1?'実際の気温とほぼ同じ':`実際より${Math.round(Math.abs(feels))}°${feels>0?'高い':'低い'}`:''),
    tile('湿度',isNumber(current.relative_humidity_2m)?`${Math.round(current.relative_humidity_2m)}%`:'—','相対湿度'),
    tile('風',fixed(current.wind_speed_10m,1,' m/s'),[direction && `${direction}の風`,isNumber(current.wind_gusts_10m) && `最大瞬間 ${current.wind_gusts_10m.toFixed(1)} m/s`].filter(Boolean).join(' · ')),
    tile('気圧',isNumber(current.pressure_msl)?`${Math.round(current.pressure_msl)} hPa`:'—','海面気圧'),
    tile('UV指数',isNumber(current.uv_index)?String(Math.round(current.uv_index)):'—',[uvLabel(current.uv_index),isNumber(today?.uv) && `今日の最大 ${Math.round(today.uv)}`].filter(Boolean).join(' · ')),
    tile('今日の降水量',fixed(today?.precipitation,1,' mm'),isNumber(today?.probability)?`降水確率 最大${today.probability}%`:''),
    tile('日の出・日の入',`${data.daily?.sunrise?.[0]?.slice(11,16)||'—'} / ${data.daily?.sunset?.[0]?.slice(11,16)||'—'}`,'今日'),
    tile('空気',isNumber(aqi?.us_aqi)?airLabel(aqi.us_aqi):'—',isNumber(aqi?.us_aqi)?`米国AQI ${Math.round(aqi.us_aqi)}${isNumber(aqi.pm2_5)?` · PM2.5 ${aqi.pm2_5.toFixed(0)} μg/m³`:''}`:'未取得'));
  const columns=el('div','weather-columns');columns.append(block('7日間',week),tiles);
  const observed=weatherTimestamp(current.time);
  body.replaceChildren(block('24時間（2時間ごと）',hours),columns,
    el('p','weather-source',`Open-Meteo（CC BY 4.0）· ${Number.isFinite(observed)?stamp(observed):'時刻不明'} JSTのモデル予測${weatherWasStale?' · 更新待ち':''}${aqi?' · 空気はCAMSのモデル予測':''}`));
}
// OK on an earnings row: when (New York and Japan), which quarter, and what analysts expect.
function openEarningsDetail(row){
  const event=earningsInfo?.data.events.find(item=>item.id===row.dataset.eventId);if(!event)return;
  const date=new Date(event.timestamp),days=Math.round((Date.parse(jstDay(event.timestamp))-Date.parse(jstDay(Date.now())))/86400000);
  const when=days===0?'今日':days===1?'明日':days>1?`あと${days}日`:'';
  const usd=v=>isNumber(v)?`${v<0?'−':''}$${Math.abs(v).toFixed(2)}`:'';
  const cap=v=>!isNumber(v)?'':v>=1e12?`約${(v/1e12).toFixed(1)}兆ドル`:`約${Math.round(v/1e8).toLocaleString('ja-JP')}億ドル`;
  const us=`${event.date.slice(5).replace('-','/')}（米国）`;
  const session=event.timing==='pre'?'寄り前（取引開始前）':event.timing==='after'?'引け後（取引終了後）':'時刻未定';
  const japan=event.exact?FULL_JST.format(date):event.timing==='pre'?`${dated(date)}（${WEEKDAY_SHORT.format(date)}）の夜（およそ20〜23時）`:event.timing==='after'?`${dated(date)}（${WEEKDAY_SHORT.format(date)}）の朝（およそ5〜7時）`:'未定';
  openDetail({eyebrow:`決算発表 · ${event.company||'Nasdaq'}`,title:event.symbol,subtitle:[when,`${dated(date)}（${WEEKDAY_SHORT.format(date)}）${event.exact?time(date):TIMING_LABEL[event.timing]}`].filter(Boolean).join(' · '),
    facts:[[event.exact?'日本時間':'日本時間の目安',japan],['米国東部時間',event.exact?`${FULL_ET.format(date)}・${session}`:`${us} ${session}`],['対象',event.quarter],
      ['予想EPS',event.epsForecast===null?'':`${usd(event.epsForecast)}${event.estimates?`（アナリスト${event.estimates}人の平均）`:''}`],
      ['前年同期のEPS',event.lastYearEps===null?'':`${usd(event.lastYearEps)}${event.lastYearDate?`（${event.lastYearDate}発表）`:''}`],
      ['時価総額',cap(event.marketCap)],['会社名',event.company],['注記',event.exact?'日付と寄り前／引け後はNasdaqの決算カレンダー、時刻はこの会社のいつもの発表時刻（直近の決算から）。会社の都合で変わることがあります。':'Nasdaqの決算カレンダー。いつもの発表時刻と寄り前／引け後が食い違うため、時刻は出していません。発表日や時刻は会社の都合で変わることがあります。']],
    link:{href:row.href,label:'Nasdaqで見る'},accent:getComputedStyle(row).getPropertyValue('--cat').trim()});
  $('detail-title').prepend(earningsLogo(event.symbol,'detail-logo'));
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
const FEEDS={connection:'ネットワーク',weather:'天気',air:'空気の状態',markets:'相場（12銘柄）','market:':'Hyperliquid','market:xyz':'trade.xyz','market:para':'para',charts:'チャート',crypto:'CoinGecko',calendar:'米国経済指標',earnings:'主要企業の決算',news:'ニュース',spotify:'Spotify',recent:'最近使ったアプリ',photos:'背景写真'};
const FEED_STATES={ok:'最新',stale:'更新待ち（保存済みの値を表示）',error:'取得できません'};
function openStatusDetail(){
  const rows=Object.entries(FEEDS).filter(([key])=>feedState.has(key)).map(([key,label])=>[label,FEED_STATES[feedState.get(key)]||feedState.get(key),feedState.get(key)==='ok'?'':'warn']);
  const waiting=[...feedState.values()].some(state=>state!=='ok');
  openDetail({eyebrow:'TV HOME',title:'データの状態',subtitle:!navigator.onLine?'オフラインです。接続が戻ると自動で再取得します。':waiting?'一部の情報が更新を待っています。自動で再取得します。':'すべて最新です。',
    facts:rows,action:{label:'今すぐ再取得',run:()=>{closeDetail();$('refresh').click();}}});
}
// The economic calendar behaves like a scrolling list: moving past an edge turns the page.
// Pages turn only with the buttons at the card's lower right. Down from the last row lands on them
// (▶, or ◀ on the last page), and Down again reaches the dock; with a single page it goes straight there.
function calendarEdge(current,direction){
  if(!current.classList.contains('calendar-event') || direction!=='down')return false;
  const rows=[...$('calendar-events').querySelectorAll('.calendar-event')];
  if(current!==rows.at(-1))return false;
  const button=[$('calendar-next'),$('calendar-prev')].find(item=>!item.disabled);
  if(!button)return false;
  button.focus({preventScroll:true});return true;
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
// TV app: the dock shows the installed apps in the user's order, then the app list and settings.
let nativeApps=[], dockPrefs=normalizeDock(readStorage(storage,DOCK_KEY,{})), movingPackage=null;
const settingsTile=$('apps').querySelector('[data-open-settings]');
const appListTile=(()=>{
  const button=el('button','app-tile');button.type='button';button.dataset.brand='applist';button.dataset.openApps='';button.setAttribute('aria-label','アプリ');
  const icon=el('span','app-icon');icon.setAttribute('aria-hidden','true');
  icon.innerHTML='<svg viewBox="0 0 24 24"><rect x="3" y="3" width="8" height="8" rx="2.4" fill="currentColor"/><rect x="13" y="3" width="8" height="8" rx="2.4" fill="currentColor"/><rect x="3" y="13" width="8" height="8" rx="2.4" fill="currentColor"/><rect x="13" y="13" width="8" height="8" rx="2.4" fill="currentColor"/></svg>';
  const label=el('span','app-label','アプリ');label.setAttribute('aria-hidden','true');button.append(icon,label);return button;
})();
// Input (home): the stock Google TV home, with its input list, is off and the remote has no input button. The user
// plays on one input — the PlayStation 5 and the Nintendo Switch both report HDMI 3 over HDMI-CEC — so the dock
// switches straight to it in one press, under the TV's own name for it (v0.32.0).
const HOME_INPUT='com.mediatek.tis/.HdmiInputService/HW4';
const inputTile=(()=>{
  const button=el('button','app-tile');button.type='button';button.dataset.brand='input';button.dataset.switchInput=HOME_INPUT;
  const icon=el('span','app-icon');icon.setAttribute('aria-hidden','true');icon.append(el('span','app-brand-mark'));
  const label=el('span','app-label');label.setAttribute('aria-hidden','true');button.append(icon,label);return button;
})();
// Renamed in the TV's settings, the tile follows; the inputs register a little after the TV starts.
const inputName=()=>readInputs().find(input=>input.id===HOME_INPUT)?.label || 'HDMI 3';
function nameInputTile(){const name=inputName();inputTile.setAttribute('aria-label',name);setText(inputTile.querySelector('.app-label'),name);}
const hasInputs=()=>!JIKKA && typeof window.Android?.inputs==='function' && typeof window.Android?.switchInput==='function';
const dockPackages=()=>[...$('apps').querySelectorAll('[data-package]')].map(tile=>tile.dataset.package);
function renderDock(focusPackage){
  const {dock}=arrangeDock(nativeApps,dockPrefs);
  $('apps').replaceChildren(...dock.map(app=>nativeAppTile(app)),...(hasInputs()?[inputTile]:[]),appListTile,settingsTile);if(hasInputs())nameInputTile();fitDock();updateFrost();
  const tile=focusPackage && $('apps').querySelector(`[data-package="${CSS.escape(focusPackage)}"]`);
  if(tile){tile.focus({preventScroll:true});tile.scrollIntoView({block:'nearest',inline:'nearest'});}
  return tile;
}
// Like the Mac's Dock every app fits on one centred row: icons shrink (to 56 px at the least) only when
// the row would be wider than the screen's content area; beyond that the row scrolls.
function fitDock(){
  const tiles=$('apps').children.length,room=1920-2*216-32,gap=16;
  const size=tiles?Math.max(56,Math.min(72,Math.floor((room-gap*(tiles-1))/tiles))):72;
  $('apps').style.setProperty('--app-size',`${size}px`);
}
function saveDock(prefs){dockPrefs=normalizeDock(prefs);writeStorage(storage,DOCK_KEY,dockPrefs);}
function initializeBridge() {
  try{
    if(!window.Android || typeof window.Android.getApps!=='function')return;
    const apps=JSON.parse(window.Android.getApps());if(!Array.isArray(apps))return;
    nativeApps=apps.filter(a=>typeof a.name==='string' && /^[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+$/.test(a.packageName));
    if(!nativeApps.length)return;
    renderDock();$('apps').classList.add('native-apps');updateFrost();
    $('tv-settings-group').hidden=typeof window.Android.openTvSettings!=='function';
  }catch{toast('アプリ一覧を取得できません。Web版の一覧を表示します。');}
}
// The app calls this when an app is installed, updated or removed.
window.tvHomeAppsChanged=()=>{initializeBridge();if(JIKKA)showJikka();};
// App list: every installed TV app by name. OK opens it; a long press adds it to or takes it off the dock.
let appsReturn=null;
function openAppList(){
  appsReturn=document.activeElement;
  const onDock=new Set(arrangeDock(nativeApps,dockPrefs).dock.map(app=>app.packageName));
  $('app-grid').replaceChildren(...arrangeDock(nativeApps,dockPrefs).all.map(app=>{
    const item=el('button','grid-app');item.type='button';item.dataset.package=app.packageName;item.setAttribute('aria-label',app.name);
    if(!onDock.has(app.packageName))item.dataset.offDock='';
    item.append(nativeAppTile(app).querySelector('.app-icon'),el('span','grid-name',app.name));return item;
  }));
  $('apps-overlay').hidden=false;$('stage').inert=true;document.body.classList.add('modal-open');
  $('app-grid').querySelector('button')?.focus();
}
function closeAppList(){ $('apps-overlay').hidden=true;$('stage').inert=false;document.body.classList.remove('modal-open');(appsReturn?.isConnected?appsReturn:appListTile).focus({preventScroll:true}); }
// Long-press menu, like iOS: reorder or take an app off the dock (nothing is uninstalled).
let menuReturn=null;
function openAppMenu(packageName){
  const app=nativeApps.find(a=>a.packageName===packageName);if(!app)return;
  const inList=!$('apps-overlay').hidden,onDock=arrangeDock(nativeApps,dockPrefs).dock.some(a=>a.packageName===packageName);
  menuReturn=document.activeElement;
  const action=(label,run,className='')=>{const button=el('button',className,label);button.type='button';button.onclick=()=>{closeMenu();run();};return button;};
  const actions=[];
  if(!inList)actions.push(action('並べ替え',()=>startMove(packageName)));
  actions.push(onDock
    ? action('ドックから外す',()=>{saveDock(setOnDock(dockPrefs,packageName,false));renderDock();if(inList)openAppList();else navigation.focusHome();},'destructive')
    : action('ドックに追加',()=>{saveDock(setOnDock(dockPrefs,packageName,true));renderDock();if(inList)openAppList();}));
  actions.push(action('キャンセル',()=>{}));
  $('menu-title').textContent=app.name;$('menu-actions').replaceChildren(...actions);
  $('menu-overlay').hidden=false;$('stage').inert=true;document.body.classList.add('modal-open');
  actions[0].focus();
}
function closeMenu(){
  $('menu-overlay').hidden=true;
  if($('apps-overlay').hidden){$('stage').inert=false;document.body.classList.remove('modal-open');}
  if(menuReturn?.isConnected)menuReturn.focus({preventScroll:true});
}
// Reordering: ←→ move the lifted app, OK or Back puts it down.
function startMove(packageName){
  movingPackage=packageName;renderDock(packageName)?.classList.add('moving');document.body.classList.add('dock-editing');
  toast('←→で移動　決定で完了');
}
function endMove(){
  const packageName=movingPackage;movingPackage=null;document.body.classList.remove('dock-editing');
  renderDock(packageName);$('toast').hidden=true;
}
let press=null;
document.addEventListener('keydown',event=>{
  if(movingPackage){
    event.preventDefault();event.stopImmediatePropagation();
    if(event.key==='ArrowLeft' || event.key==='ArrowRight'){
      saveDock(moveInDock(dockPrefs,dockPackages(),movingPackage,event.key==='ArrowLeft'?-1:1));
      renderDock(movingPackage)?.classList.add('moving');
    }else if(['Enter','Escape','BrowserBack','GoBack'].includes(event.key))endMove();
    return;
  }
  // The held OK key keeps repeating after the menu opens; none of it may press a menu button.
  // A repeat is the remote's own long-press signal, so it opens the menu at once.
  if(event.key==='Enter' && press){
    event.preventDefault();event.stopImmediatePropagation();
    if(event.repeat && !press.long){clearTimeout(press.timer);press.long=true;openAppMenu(press.tile.dataset.package);}
    return;
  }
  const tile=event.key==='Enter' && !event.repeat && event.target.closest?.('#apps [data-package],#app-grid [data-package]');
  if(!tile)return;
  // OK on an app waits for the key to come up: a short press opens it, a long press shows the menu.
  event.preventDefault();event.stopImmediatePropagation();
  press={tile,long:false,timer:setTimeout(()=>{if(press){press.long=true;openAppMenu(tile.dataset.package);}},550)};
},{capture:true});
document.addEventListener('keyup',event=>{
  if(event.key!=='Enter' || !press)return;
  clearTimeout(press.timer);const {tile,long}=press;press=null;
  if(!long)tile.click();
},{capture:true});
document.addEventListener('contextmenu',event=>{
  const tile=event.target.closest('#apps [data-package],#app-grid [data-package]');
  if(tile){event.preventDefault();openAppMenu(tile.dataset.package);}
});

if(frostSupported())frost=new Frost(document.querySelector('.frost'),[...document.querySelectorAll('.frost-layer')]);
const slideshow=new Slideshow({layers:[...document.querySelectorAll('.photo-layer')],caption:$('photo-credit'),title:$('photo-title'),frost,onFrost:updateFrost,onTheme:applyTheme,onError:()=>{setFeed('photos','error');$('photo-title').textContent='背景写真を読み込めませんでした';}});
// The time of day from the sun at the weather's location (js/daypart.js); a change brings that time's photos.
function sunTimes(){
  const daily=weatherResult?.data?.daily,index=daily?.time?.indexOf(ISO_DAY.format(new Date())) ?? -1;
  return index<0 ? [NaN,NaN] : [weatherTimestamp(daily.sunrise?.[index]),weatherTimestamp(daily.sunset?.[index])];
}
function currentDayPart(now=Date.now()){return dayPart(now,...sunTimes());}
// Checked every second the screen is on, and at once when it comes back from sleep or the screensaver.
function updateDayPart(now){
  const part=currentDayPart(now),changed=part!==photoPart;
  if(changed){photoPart=part;photoRetry={at:0,attempt:0};}
  if(config.photoMode!=='unsplash')return;
  if(changed){const saved=readStorage(storage,`tv-cache:${photoCacheKey(part)}`,null)?.data?.data;if(Array.isArray(saved) && saved.length)setPhotos(saved);}
  // A fetch skipped while the screen was off, or failed while Wi-Fi was coming back, is retried
  // until photos for this time of day are on screen (js/daypart.js photoRetryDelay).
  if(!photosJob || (!changed && photosPart(slideshow.photos)===part) || now<photoRetry.at)return;
  photoRetry={at:now+photoRetryDelay(photoRetry.attempt),attempt:photoRetry.attempt+1};
  void photosJob.run(true);
}
const photoCacheKey=part=>`${config.apiBase || 'local'}:photos:${part}`;
function startingPhotos(){
  const saved=config.photoMode==='unsplash' ? readStorage(storage,`tv-cache:${photoCacheKey(photoPart)}`,null)?.data?.data : null;
  return Array.isArray(saved) && saved.length ? saved : SAMPLE_PHOTOS;
}
// The theme follows the photo on screen: light over a daytime photo, dark over sunset and night. It turns
// halfway through the 2.4 s cross-fade, when the new photo and its glass are mostly in.
function applyTheme(theme){
  clearTimeout(themeTimer);
  const set=()=>{if(theme==='light')document.documentElement.dataset.theme='light';else delete document.documentElement.dataset.theme;};
  if(!document.body.classList.contains('ready') || (document.documentElement.dataset.theme || 'dark')===theme)set();
  else themeTimer=setTimeout(set,1200);
}
// The photo switch is only offered when there is another photo to switch to.
function setPhotos(photos){slideshow.setPhotos(photos);$('next-photo').hidden=slideshow.photos.length<2;}
document.addEventListener('click',event=>{
  const open=event.target.closest('[data-open-settings]');if(open){openSettings(open.dataset.openSettings);return;}
  if(event.target.closest('[data-open-apps]')){openAppList();return;}
  const input=event.target.closest('[data-switch-input]');
  if(input){pressApp(input);if(!switchInput(input.dataset.switchInput))toast(`${inputName()}に切り替えられませんでした。テレビをつけた直後は、少し待ってからもう一度どうぞ。`);return;}
  // Opening an app from the list leaves the list closed behind it.
  if(event.target.closest('#app-grid [data-package]'))closeAppList();
  // OK on a row or headline shows details in place: following a link would leave the launcher.
  const row=event.target.closest('#stage .stock-row');if(row){openMarketDetail(row.dataset.symbol);return;}
  if(event.target.closest('#stage .weather-section')){openWeatherDetail();return;}
  const release=event.target.closest('#stage .calendar-event');if(release){event.preventDefault();if(release.dataset.earnings!==undefined)openEarningsDetail(release);else openEventDetail(release);return;}
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
const navigation=installNavigation({modals:[{element:$('menu-overlay'),close:closeMenu},{element:$('apps-overlay'),close:closeAppList},{element:$('settings-overlay'),close:closeSettings},{element:$('detail-overlay'),close:closeDetail}],home:()=>$('apps'),onEdge:calendarEdge});
$('close-apps').onclick=closeAppList;
$('apps-overlay').addEventListener('click',event=>{if(event.target===$('apps-overlay'))closeAppList();});
$('menu-overlay').addEventListener('click',event=>{if(event.target===$('menu-overlay'))closeMenu();});
$('open-tv-settings').onclick=()=>{try{window.Android?.openTvSettings?.();}catch{toast('テレビの設定を開けませんでした');}};
// A passive dashboard rests with focus on the dock, so a forgotten highlight never lingers on a card.
let lastInput=Date.now();
for(const type of ['keydown','pointerdown'])addEventListener(type,()=>{lastInput=Date.now();},{capture:true,passive:true});
setInterval(()=>{if(!document.hidden && Date.now()-lastInput>IDLE_HOME && !document.querySelector('.modal-overlay:not([hidden])'))navigation.focusHome();},10000);
// A layer kept for a smooth lift (will-change: transform in styles.css) is drawn once, at rest, and the TV's
// WebView then magnifies that bitmap: a lifted dock icon or row looked soft. When a lift settles, its layers
// are dropped for a frame and drawn again at their new size.
document.addEventListener('transitionend',event=>{
  const lifted=event.target;if(event.propertyName!=='transform' || !lifted.matches?.('.app-icon,.stock-row,.calendar-event'))return;
  const layers=[lifted,...lifted.querySelectorAll('.stock-price-row')];
  for(const layer of layers)layer.style.willChange='auto';
  requestAnimationFrame(()=>requestAnimationFrame(()=>{for(const layer of layers)layer.style.removeProperty('will-change');}));
});
addEventListener('resize',fit);addEventListener('online',()=>{setFeed('connection','ok');jobs.forEach(job=>void job.run());});addEventListener('offline',()=>{setFeed('connection','error');});
// Coming back home must feel instant: the clock updates at once, refreshes follow a little later and one at a time.
document.addEventListener('visibilitychange',()=>{if(document.hidden)cryptoStream?.stop();else{tick();setTimeout(()=>cryptoStream?.start(),300);jobs.forEach((job,i)=>setTimeout(()=>{if(!document.hidden)void job.run();},600+i*200));}});
// The parents' TV: the screen comes back first; the inputs are checked just after, and the app tells the page
// when the recent apps (read on its own thread) have changed.
document.addEventListener('visibilitychange',()=>{if(JIKKA && !document.hidden)setTimeout(()=>{if(!document.hidden)renderInputs($('inputs'));},400);});
window.tvHomeRecentChanged=()=>{if(JIKKA)renderRecent($('recent-apps'),nativeApps);};
addEventListener('pagehide',()=>cryptoStream?.stop());
addEventListener('pageshow',event=>{if(event.persisted && !document.hidden)cryptoStream?.start();});
setInterval(()=>{if(!document.hidden)tick();},1000);
// Restarted on manual paging so a headline chosen by hand gets its full time on screen.
let newsTimer;
function scheduleNews(){clearInterval(newsTimer);newsTimer=setInterval(()=>{if(!document.hidden && $('settings-overlay').hidden && $('detail-overlay').hidden && news.length>1 && document.activeElement!==$('news-title')){newsIndex=(newsIndex+1)%news.length;showNews();}},NEWS_INTERVAL);}
scheduleNews();
// Loaded as a print sheet so it never blocks the first paint; the CSP forbids an inline onload.
function enableJapaneseFont(){const link=$('font-ja');if(!link)return;const on=()=>{link.media='all';};if(link.sheet)on();else link.addEventListener('load',on,{once:true});}
// The parents' TV (js/profile.js): continue watching and the inputs in place of the market, calendar and Spotify.
function showJikka(){renderInputs($('inputs'));renderRecent($('recent-apps'),nativeApps);}
function setUpJikka(){
  document.body.classList.add('jikka');
  for(const id of ['recent-card','inputs-card'])$(id).hidden=false;
  // The market, calendar and Spotify cards stay in the page but hidden, so nothing navigates to them.
  for(const card of document.querySelectorAll('.market-card,.calendar-card,.music-card'))card.hidden=true;
  document.querySelector('.weather-section').dataset.navDown='news';
  $('recent-card').dataset.navDown='inputs';
  Object.assign(document.querySelector('.news-card').dataset,{navUp:'weather',navLeft:'none',navRight:'inputs',navDown:'dock'});
  $('news-summary').hidden=false;
  for(const control of [$('market-mode'),$('spotify-client-id')])control.closest('fieldset').hidden=true;
  $('photo-title').closest('.photo-caption').dataset.navDown='recent';$('connection-status').closest('.utility').dataset.navDown='recent';
  // The recent row waits for the app list (initializeBridge); its job fills it right after.
  renderInputs($('inputs'));
  $('inputs-card').addEventListener('click',event=>{
    const input=event.target.closest('[data-input]');if(!input)return;
    if(!switchInput(input.dataset.input))toast('入力を切り替えられませんでした');
  });
}
async function start(){
  enableJapaneseFont();
  if(JIKKA)setUpJikka();
  fit();if(!JIKKA)buildStocks();photoPart=currentDayPart();tick();setPhotos(startingPhotos());initializeBridge();if(!JIKKA)void loadCalendarSnapshot();
  // The TV app already runs full screen; the button only helps in a desktop browser.
  $('fullscreen').hidden=Boolean(window.Android) || !document.fullscreenEnabled;
  // The TV app rebuilds the page after freeing memory; coming back home must not replay the entrance.
  if(new URLSearchParams(location.search).has('instant')){document.body.classList.add('instant');history.replaceState({},'',location.pathname);}
  document.body.classList.add('ready');
  $('apps').querySelector('button')?.focus({preventScroll:true});
  try{if(await spotify.completeCallback())toast('Spotifyを連携しました');}catch(error){toast(errorText(error));}
  backend=await api('config').catch(()=>({backend:false,market:false,unsplash:false}));
  applyConfig();
}
void start();
