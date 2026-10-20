import { MARKETS } from './market-definitions.js';
import { DEFAULT_ADBLOCK_DNS, validDnsHost } from './adblock.js';
import { JIKKA } from './profile.js';
export const SYMBOLS = MARKETS.map(m=>[m.symbol,m.name,m.symbol]);

export const DEFAULT_CONFIG = {
  // The parents' TV is in Kunitachi (js/profile.js).
  location: JIKKA ? { name: '国立市', latitude: 35.6839, longitude: 139.4414 } : { name: '渋谷区', latitude: 35.6589, longitude: 139.70665 },
  timeZone: 'Asia/Tokyo', marketMode: 'custom', cryptoSource: 'hyperliquid', photoMode: 'sample',
  photoInterval: 60, motion: false, apiBase: '', spotifyClientId: '', chartRange: '1d', adblockDns: DEFAULT_ADBLOCK_DNS,
};
export const isNumber = n => typeof n === 'number' && Number.isFinite(n);
// toLocaleString builds a new NumberFormat on every call; prices update every second.
const moneyFormats = new Map();
export const money = (n, digits = 2) => {
  if (!isNumber(n)) return '—';
  if (!moneyFormats.has(digits)) moneyFormats.set(digits, new Intl.NumberFormat('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits }));
  return moneyFormats.get(digits).format(n);
};
export function signed(n, suffix = '%', digits = 2) {
  return isNumber(n) ? `${n > 0 ? '+' : n < 0 ? '−' : '±'}${Math.abs(n).toFixed(digits)}${suffix}` : '—';
}
export const tone = n => !isNumber(n) || n === 0 ? 'neutral' : n > 0 ? 'up' : 'down';
export function safeUrl(value, { relative = false } = {}) {
  try {
    if (typeof value !== 'string' || !value) return '';
    if (relative && /^(\.\/)?(?:assets|photos)\/[a-z0-9_./-]+$/i.test(value) && !value.includes('..')) return value;
    const url = new URL(value);
    return url.protocol === 'https:' ? url.href : '';
  } catch { return ''; }
}
export function normalizeConfig(input = {}) {
  const result = { ...DEFAULT_CONFIG };
  const loc = input.location;
  if (loc && isNumber(loc.latitude) && Math.abs(loc.latitude) <= 90 && isNumber(loc.longitude) && Math.abs(loc.longitude) <= 180 && typeof loc.name === 'string' && loc.name.trim()) {
    result.location = { name: loc.name.slice(0, 50), latitude: loc.latitude, longitude: loc.longitude };
  }
  if (['custom','tradingview'].includes(input.marketMode)) result.marketMode = input.marketMode;
  if (['hyperliquid','coingecko'].includes(input.cryptoSource)) result.cryptoSource = input.cryptoSource;
  if (['sample','unsplash'].includes(input.photoMode)) result.photoMode = input.photoMode;
  if (isNumber(input.photoInterval)) result.photoInterval = Math.min(600, Math.max(30, input.photoInterval));
  if (typeof input.motion === 'boolean') result.motion = input.motion;
  if (validDnsHost(input.adblockDns)) result.adblockDns = input.adblockDns.toLowerCase();
  if (typeof input.spotifyClientId === 'string' && /^[a-f0-9]{32}$/.test(input.spotifyClientId)) result.spotifyClientId = input.spotifyClientId;
  // Optional backend origin. Secrets must remain on that server.
  if (input.apiBase && safeUrl(input.apiBase)) result.apiBase = input.apiBase.replace(/\/$/, '');
  return result;
}
export function readStorage(storage, key, fallback) {
  try { const value = storage.getItem(key); return value ? JSON.parse(value) : fallback; } catch { return fallback; }
}
export function writeStorage(storage, key, data) {
  try { storage.setItem(key, JSON.stringify(data)); return true; } catch { return false; }
}
export async function fetchJSON(url, { fetcher = fetch, timeout = 12000, ...options } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetcher(url, { ...options, signal: controller.signal, headers: { Accept: 'application/json', ...options.headers } });
    if (!response.ok) {
      const error = new Error(response.status === 429 ? '取得回数の上限・後で再試行します' : `取得できませんでした (${response.status})`);
      error.status = response.status;
      throw error;
    }
    return await response.json();
  } finally { clearTimeout(timer); }
}
export async function cachedLoad({key, load, storage, now = Date.now(), maxAge = 86400000}) {
  const saved = readStorage(storage, `tv-cache:${key}`, null);
  try {
    const data = await load();
    const value = { data, fetchedAt: now };
    writeStorage(storage, `tv-cache:${key}`, value);
    return { ...value, stale: false };
  } catch (error) {
    if (saved && Number.isFinite(saved.fetchedAt) && now >= saved.fetchedAt && now - saved.fetchedAt <= maxAge) {
      return { ...saved, stale: true, error: error.message };
    }
    throw error;
  }
}
export function sparkline(values, width = 180, height = 40) {
  if (!Array.isArray(values) || values.length < 2 || !values.every(isNumber)) return '';
  const min = Math.min(...values), max = Math.max(...values), range = max - min;
  return values.map((v,i) => `${(i / (values.length - 1) * width).toFixed(1)},${(range ? height - 4 - (v - min) / range * (height - 8) : height / 2).toFixed(1)}`).join(' ');
}
export function weatherLabel(code) {
  if (code === 0) return '快晴';
  if ([1,2].includes(code)) return '晴れ時々くもり';
  if (code === 3) return 'くもり';
  if ([45,48].includes(code)) return '霧';
  if ([71,73,75,77,85,86].includes(code)) return '雪';
  if ([95,96,99].includes(code)) return '雷雨';
  if (code >= 51 && code <= 82) return '雨';
  return '天気情報なし';
}
export function airLabel(aqi) {
  return !isNumber(aqi) ? '—' : aqi <= 50 ? '良い' : aqi <= 100 ? '普通' : aqi <= 150 ? '敏感な方は注意' : aqi <= 200 ? '悪い' : '非常に悪い';
}
// One request every 15 minutes feeds both the card and the weather detail (a week ahead, wind in m/s).
export async function getWeather(location) {
  const params = new URLSearchParams({latitude: location.latitude, longitude: location.longitude,
    current: 'temperature_2m,weather_code,is_day,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m,pressure_msl,uv_index',
    hourly:'temperature_2m,precipitation_probability,weather_code,is_day',
    daily: 'temperature_2m_max,temperature_2m_min,sunrise,sunset,weather_code,precipitation_probability_max,precipitation_sum,uv_index_max',
    wind_speed_unit: 'ms', timezone: 'Asia/Tokyo', forecast_days: 7});
  const data = await fetchJSON(`https://api.open-meteo.com/v1/forecast?${params}`);
  if (!isNumber(data.current?.temperature_2m) || !Array.isArray(data.daily?.time)) throw new Error('天気データがありません');
  return data;
}
export async function getAir(location) {
  const params = new URLSearchParams({latitude: location.latitude, longitude: location.longitude, current: 'us_aqi,pm2_5', timezone: 'Asia/Tokyo'});
  const data = await fetchJSON(`https://air-quality-api.open-meteo.com/v1/air-quality?${params}`);
  if (!isNumber(data.current?.us_aqi)) throw new Error('空気質データがありません');
  return data;
}
export async function getCrypto() {
  const data = await fetchJSON('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,hyperliquid&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true');
  const rows = ['bitcoin','hyperliquid'].map(id => ({ id, ...data[id] }));
  if (rows.some(r => !isNumber(r.usd) || !isNumber(r.last_updated_at) || r.last_updated_at <= 0)) throw new Error('価格データがありません');
  return rows;
}
export async function getFx(now = new Date()) {
  const start = new Date(now); start.setUTCDate(start.getUTCDate() - 10);
  const data = await fetchJSON(`https://api.frankfurter.dev/v2/rates?base=USD&quotes=JPY&providers=ECB&from=${start.toISOString().slice(0,10)}`);
  const rows = Array.isArray(data) ? data.filter(r => /^\d{4}-\d{2}-\d{2}$/.test(r.date) && isNumber(r.rate)).sort((a,b) => a.date.localeCompare(b.date)) : [];
  if (!rows.length) throw new Error('為替データがありません');
  return rows;
}
