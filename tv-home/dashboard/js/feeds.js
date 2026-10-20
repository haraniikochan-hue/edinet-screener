// News and economic calendar loaders shared by server.mjs and the TV app.
// Both pass a fetchText(url) that reaches the upstream feed: Node fetches it directly,
// the TV app goes through its native proxy because the feeds send no CORS headers.
import { CALENDAR_FEEDS, parseEconomicICS, mergeCalendar } from './economic-calendar.js';
import { JIKKA } from './profile.js';

// NHK ONE (news.web.nhk) replaced the www3.nhk.or.jp feeds, which stopped updating in August 2026.
export const NHK_RSS = 'https://news.web.nhk/n-data/conf/na/rss/cat5.xml';
const NHK_LINK = /^https:\/\/(?:(?:[a-z0-9-]+\.)*nhk\.(?:or\.jp|jp)|news\.web\.nhk)\//;
// The only upstream addresses the TV app's native proxy may fetch, besides Nasdaq's earnings calendar
// by date (js/earnings.js EARNINGS_URL).
export const UPSTREAM_FEEDS = [NHK_RSS, ...Object.values(CALENDAR_FEEDS)];

export function decodeXML(value) {
  return value.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1').replace(/<[^>]*>/g, '')
    .replace(/&#(x[\da-f]+|\d+);/gi, (_, n) => {
      const code = n[0].toLowerCase() === 'x' ? parseInt(n.slice(1),16) : Number(n);
      return code > 0 && code <= 0x10ffff ? String.fromCodePoint(code) : '';
    }).replace(/&(amp|lt|gt|quot|apos);/g, (_, e) => ({ amp:'&',lt:'<',gt:'>',quot:'"',apos:"'" })[e]).trim();
}
export function parseRSS(xml) {
  return [...xml.matchAll(/<item(?:\s[^>]*)?>([\s\S]*?)<\/item>/g)].map(([,item]) => {
    const tag = name => decodeXML(item.match(new RegExp(`<${name}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${name}>`))?.[1] || '');
    // The feed's description is a one- or two-sentence lead; the TV shows it when a headline is opened.
    return { title: tag('title').slice(0,180), summary: tag('description').slice(0,240), url: tag('link').replace(/^http:/, 'https:'), publishedAt: tag('pubDate'), source:'NHK 経済' };
  }).filter(item => item.title && NHK_LINK.test(item.url) && Number.isFinite(Date.parse(item.publishedAt))).slice(0, 3);
}

// Background photos: New York's downtown at the time of day (js/daypart.js) — by day, at sunset, by
// night — from two searches each, a few random photos per search each hour. The Access Key stays with
// the server or the TV app; the page only names the search (the TV app allows exactly these).
const NEW_YORK = Object.freeze({
  day: { title:'ニューヨーク · 日中', queries:['new york city skyline daytime', 'manhattan skyline blue sky'] },
  dusk: { title:'ニューヨーク · 夕暮れ', queries:['new york city skyline sunset', 'manhattan skyline golden hour'] },
  night: { title:'ニューヨーク · 夜景', queries:['new york city skyline night', 'manhattan skyline night lights'] },
});
// The parents' TV (js/profile.js) shows nature instead: mountains, lakes and sea by day, at sunset, under the stars.
const NATURE = Object.freeze({
  day: { title:'自然の風景 · 日中', queries:['mountain lake landscape', 'green forest sunlight'] },
  dusk: { title:'自然の風景 · 夕暮れ', queries:['mountain sunset landscape', 'ocean sunset'] },
  night: { title:'自然の風景 · 星空', queries:['starry night mountains', 'milky way landscape'] },
});
export const PHOTO_PERIODS = JIKKA ? NATURE : NEW_YORK;
// Every search either TV may make, so one server or app allows both.
export const PHOTO_QUERIES = Object.freeze([NEW_YORK, NATURE].flatMap(set => Object.values(set).flatMap(period => period.queries)));
export const PHOTOS_PER_QUERY = 8;
export const unsplashRandom = query => `https://api.unsplash.com/photos/random?query=${encodeURIComponent(query)}&count=${PHOTOS_PER_QUERY}&orientation=landscape&content_filter=high`;
export const validPhotoQuery = query => PHOTO_QUERIES.includes(query);
export function unsplashPhotos(photos, title) {
  return (Array.isArray(photos) ? photos : photos?.results || []).filter(p => p.urls?.regular && p.user?.name && p.user?.links?.html).map(p => {
    const url = new URL(p.urls.regular); url.searchParams.set('w','1920'); url.searchParams.set('q','85');
    return { url:url.href, title, photographer:p.user.name, profile:`${p.user.links.html}?utm_source=tv_home&utm_medium=referral`, source:'Unsplash', sourceUrl:'https://unsplash.com/?utm_source=tv_home&utm_medium=referral', photoUrl:`${p.links.html}?utm_source=tv_home&utm_medium=referral` };
  });
}
// fetchQuery(query) returns Unsplash's JSON for one search. Searches that fail are skipped, a photo found
// by both is kept once, every photo is marked with its time of day, and the result is shuffled.
export async function loadPhotos(fetchQuery, period = 'night', random = Math.random) {
  const spec = PHOTO_PERIODS[period];
  if (!spec) throw Object.assign(new Error('時間帯が不明です'), { status:400 });
  const results = await Promise.allSettled(spec.queries.map(async query => unsplashPhotos(await fetchQuery(query), spec.title)));
  const seen = new Set();
  const rows = results.flatMap(r => r.status === 'fulfilled' ? r.value : [])
    .filter(row => { const id = row.photoUrl; if (seen.has(id)) return false; seen.add(id); return true; })
    .map(row => ({ ...row, period }));
  if (!rows.length) {
    const limited = results.some(r => r.reason?.status === 429);
    throw Object.assign(new Error(limited ? 'Unsplashの取得回数の上限です' : '写真がありません'), { status: limited ? 429 : 502 });
  }
  for (let i = rows.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [rows[i], rows[j]] = [rows[j], rows[i]]; }
  return rows;
}

export async function loadNews(fetchText) {
  const rows = parseRSS(await fetchText(NHK_RSS));
  if (!rows.length) throw Object.assign(new Error('ニュースがありません'), { status:502 });
  return rows;
}
// A provider that cannot be reached falls back to the bundled snapshot and is marked stale.
export async function loadCalendar(fetchText, snapshot) {
  const providers=Object.keys(CALENDAR_FEEDS),sources=[],lists=[];
  const results=await Promise.allSettled(providers.map(async source=>parseEconomicICS(await fetchText(CALENDAR_FEEDS[source]),source)));
  for(const [i,item] of results.entries()){
    const source=providers[i];
    if(item.status==='fulfilled'){
      lists.push(item.value);sources.push({source,status:'live',verifiedAt:new Date().toISOString(),coverageThrough:new Date(item.value.at(-1).timestamp).toISOString(),url:CALENDAR_FEEDS[source]});
    }else{
      lists.push(snapshot.events.filter(e=>e.source===source));
      sources.push({...snapshot.sources.find(s=>s.source===source),status:'stale'});
    }
  }
  lists.push(snapshot.events.filter(e=>e.source==='FRB'));sources.push(snapshot.sources.find(s=>s.source==='FRB'));
  return {events:mergeCalendar(lists),sources};
}
