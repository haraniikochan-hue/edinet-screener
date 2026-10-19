// News and economic calendar loaders shared by server.mjs and the TV app.
// Both pass a fetchText(url) that reaches the upstream feed: Node fetches it directly,
// the TV app goes through its native proxy because the feeds send no CORS headers.
import { CALENDAR_FEEDS, parseEconomicICS, mergeCalendar } from './economic-calendar.js';

// NHK ONE (news.web.nhk) replaced the www3.nhk.or.jp feeds, which stopped updating in August 2026.
export const NHK_RSS = 'https://news.web.nhk/n-data/conf/na/rss/cat5.xml';
const NHK_LINK = /^https:\/\/(?:(?:[a-z0-9-]+\.)*nhk\.(?:or\.jp|jp)|news\.web\.nhk)\//;
// The only upstream addresses the TV app's native proxy may fetch.
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

// Background photos: downtowns of world cities, day and night, a few random ones per city each hour.
// The Access Key stays with the server or the TV app; the page only names the search.
export const PHOTO_CITIES = [
  ['new york city skyline', 'ニューヨーク'], ['london city skyline', 'ロンドン'], ['paris city', 'パリ'],
  ['chicago downtown', 'シカゴ'], ['tokyo city', '東京'], ['hong kong skyline', '香港'],
  ['singapore skyline', 'シンガポール'], ['dubai downtown', 'ドバイ'],
];
export const PHOTOS_PER_CITY = 3;
export const unsplashRandom = query => `https://api.unsplash.com/photos/random?query=${encodeURIComponent(query)}&count=${PHOTOS_PER_CITY}&orientation=landscape&content_filter=high`;
export const validPhotoQuery = query => PHOTO_CITIES.some(([q]) => q === query);
export function unsplashPhotos(photos, title) {
  return (Array.isArray(photos) ? photos : photos?.results || []).filter(p => p.urls?.regular && p.user?.name && p.user?.links?.html).map(p => {
    const url = new URL(p.urls.regular); url.searchParams.set('w','1920'); url.searchParams.set('q','85');
    return { url:url.href, title, photographer:p.user.name, profile:`${p.user.links.html}?utm_source=tv_home&utm_medium=referral`, source:'Unsplash', sourceUrl:'https://unsplash.com/?utm_source=tv_home&utm_medium=referral', photoUrl:`${p.links.html}?utm_source=tv_home&utm_medium=referral` };
  });
}
// fetchCity(query) returns Unsplash's JSON for one city; cities that fail are skipped, and the result is shuffled.
export async function loadPhotos(fetchCity, random = Math.random) {
  const results = await Promise.allSettled(PHOTO_CITIES.map(async ([query, title]) => unsplashPhotos(await fetchCity(query), title)));
  const rows = results.flatMap(r => r.status === 'fulfilled' ? r.value : []);
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
