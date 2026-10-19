import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, dirname, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SYMBOLS, isNumber } from './dashboard/js/data.js';
import { CALENDAR_FEEDS, parseEconomicICS, mergeCalendar } from './lib/economic-calendar.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), 'dashboard');
const cache = new Map();
const pending = new Map();
const types = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.json':'application/json; charset=utf-8', '.jpg':'image/jpeg', '.png':'image/png', '.svg':'image/svg+xml', '.woff2':'font/woff2', '.ico':'image/x-icon' };
const httpError = (status, message) => Object.assign(new Error(message), { status });
async function upstream(url, { json = true, headers = {} } = {}) {
  const response = await fetch(url, { signal: AbortSignal.timeout(12000), headers: { 'User-Agent':'TVHomeDashboard/0.4 (personal dashboard)', ...headers } });
  if (!response.ok) throw httpError(response.status === 429 ? 429 : 502, `配信元から取得できません (${response.status})`);
  return json ? response.json() : response.text();
}
export async function memo(key, ttl, loader, staleLimit = 86400000) {
  const old = cache.get(key);
  if (old && Date.now() - old.fetchedAt < ttl) return old;
  if (pending.has(key)) return pending.get(key);
  const work = (async () => {
    try {
      const data = await loader();
      const result = { data, fetchedAt: Date.now(), stale: false };
      cache.set(key, result); return result;
    } catch (error) {
      if (old && Date.now() - old.fetchedAt < staleLimit) return { ...old, stale: true };
      throw error;
    } finally { pending.delete(key); }
  })();
  pending.set(key, work); return work;
}
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
    return { title: tag('title').slice(0,180), url: tag('link').replace(/^http:/, 'https:'), publishedAt: tag('pubDate'), source:'NHK 経済' };
  }).filter(item => item.title && /^https:\/\/[^/]*nhk\.(or\.jp|jp)\//.test(item.url) && Number.isFinite(Date.parse(item.publishedAt))).slice(0, 3);
}
export function parseYieldCSV(csv) {
  return csv.trim().split(/\r?\n/).slice(1).map(line => {
    const [date, value, thirty] = line.split(',');
    const numeric = s => s?.trim() && s.trim() !== '.' ? Number(s) : null;
    return { date, value: numeric(value), thirty: numeric(thirty) };
  }).filter(row => /^\d{4}-\d{2}-\d{2}$/.test(row.date) && isNumber(row.value)).sort((a,b) => a.date.localeCompare(b.date)).slice(-8);
}
async function api(pathname) {
  if (pathname === '/api/config') return {
    market: Boolean(process.env.MARKET_DATA_URL), unsplash: Boolean(process.env.UNSPLASH_ACCESS_KEY),
    spotifyClientId: /^[a-f0-9]{32}$/.test(process.env.SPOTIFY_CLIENT_ID || '') ? process.env.SPOTIFY_CLIENT_ID : '',
    backend: true,
  };
  if (pathname === '/api/news') return memo('news', 900000, async () => {
    const rows = parseRSS(await upstream('https://www3.nhk.or.jp/rss/news/cat5.xml', { json:false }));
    if (!rows.length) throw httpError(502, 'ニュースがありません');
    return rows;
  });
  if (pathname === '/api/calendar') {
    const result=await memo('calendar',6*3600000,async()=>{
      const snapshot=JSON.parse(await readFile(resolve(root,'data/economic-calendar.json'),'utf8'));
      const providers=Object.keys(CALENDAR_FEEDS),sources=[],lists=[];
      const results=await Promise.allSettled(providers.map(async source=>parseEconomicICS(await upstream(CALENDAR_FEEDS[source],{json:false}),source)));
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
    });
    return {...result,stale:result.stale || result.data.sources.some(s=>s.status==='stale')};
  }
  if (pathname === '/api/yield') return memo('yield', 3600000, async () => {
    const start = new Date(); start.setUTCDate(start.getUTCDate() - 20);
    const rows = parseYieldCSV(await upstream(`https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10,DGS30&cosd=${start.toISOString().slice(0,10)}`, { json:false }));
    if (!rows.length) throw httpError(502, '金利データがありません');
    return rows;
  }, 604800000);
  if (pathname === '/api/market') {
    if (!process.env.MARKET_DATA_URL) throw httpError(503, '総合マーケットAPI未設定');
    return memo('market', 30000, async () => {
      const url = new URL(process.env.MARKET_DATA_URL);
      if (url.protocol !== 'https:') throw httpError(503, 'マーケットAPIはHTTPSで設定してください');
      const response = await upstream(url, { headers:process.env.MARKET_DATA_TOKEN ? { Authorization:`Bearer ${process.env.MARKET_DATA_TOKEN}` } : {} });
      if (!Array.isArray(response.quotes)) throw httpError(502, 'マーケットAPIのデータ形式を確認してください');
      const rows = response.quotes.filter(q => SYMBOLS.some(([symbol]) => symbol === q.symbol) && isNumber(q.price) && isNumber(q.timestamp) && q.timestamp > 0).map(q => ({symbol:q.symbol, price:q.price, change:isNumber(q.change) ? q.change : null, timestamp:q.timestamp, source:String(q.source || 'Market API').slice(0,60), delay:String(q.delay || '遅延情報なし').slice(0,60)}));
      if (!rows.length) throw httpError(502, '価格を取得できません');
      return rows;
    });
  }
  if (pathname === '/api/photos') {
    if (!process.env.UNSPLASH_ACCESS_KEY) throw httpError(503, 'Unsplash APIキー未設定');
    return memo('photos', 3600000, async () => {
      const response = await upstream('https://api.unsplash.com/search/photos?query=new%20york%20city%20night&orientation=landscape&per_page=24&content_filter=high', { headers:{ Authorization:`Client-ID ${process.env.UNSPLASH_ACCESS_KEY}`, 'Accept-Version':'v1' } });
      const rows = (response.results || []).filter(p => p.urls?.regular && p.user?.name && p.user?.links?.html).map(p => {
        const url = new URL(p.urls.regular); url.searchParams.set('w','1920'); url.searchParams.set('q','85');
        return { url:url.href, title:'ニューヨーク', photographer:p.user.name, profile:`${p.user.links.html}?utm_source=tv_home&utm_medium=referral`, source:'Unsplash', sourceUrl:'https://unsplash.com/?utm_source=tv_home&utm_medium=referral', photoUrl:`${p.links.html}?utm_source=tv_home&utm_medium=referral` };
      });
      if (!rows.length) throw httpError(502, '写真がありません');
      return rows;
    });
  }
  throw httpError(404, 'APIがありません');
}
const CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' https: data:; connect-src 'self' https: wss://api.hyperliquid.xyz; frame-src 'self' https://*.tradingview.com https://*.tradingview-widget.com; object-src 'none'; base-uri 'self'; frame-ancestors 'self'";
export function createAppServer() {
  return createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options','nosniff');
    res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');
    res.setHeader('Content-Security-Policy', CSP);
    res.setHeader('Permissions-Policy','geolocation=(), microphone=(), camera=()');
    try {
      if (!['GET','HEAD'].includes(req.method)) throw httpError(405, 'Method not allowed');
      const path = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      if (path.startsWith('/api/')) {
        res.setHeader('Content-Type', types['.json']); res.setHeader('Cache-Control','no-store');
        const data = await api(path);
        res.end(req.method === 'HEAD' ? '' : JSON.stringify(data)); return;
      }
      // Serve only public dashboard assets, never project files, tokens, or local configuration.
      if (path.split('/').some(part => part.startsWith('.') || part.endsWith('.local.json'))) throw httpError(404, 'Not found');
      const file = resolve(root, `.${path === '/' ? '/index.html' : path}`);
      if (!file.startsWith(root + sep) || !types[extname(file)]) throw httpError(404, 'Not found');
      const info = await stat(file); if (!info.isFile()) throw httpError(404, 'Not found');
      res.setHeader('Content-Type', types[extname(file)]);
      res.setHeader('Cache-Control', extname(file) === '.html' ? 'no-cache' : 'public, max-age=300');
      res.end(req.method === 'HEAD' ? '' : await readFile(file));
    } catch (error) {
      res.statusCode = error.status || (error.code === 'ENOENT' ? 404 : 502);
      res.setHeader('Content-Type',types['.json']); res.setHeader('Cache-Control','no-store');
      res.end(JSON.stringify({ error: error.status ? error.message : res.statusCode === 404 ? 'Not found' : 'データを取得できません。しばらくして再試行してください。' }));
    }
  });
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const server = createAppServer();
  const port = Number(process.env.PORT || 4173), host = process.env.HOST || '127.0.0.1';
  server.listen(port, host, () => console.log(`TV Home: http://${host}:${port}/`));
}
