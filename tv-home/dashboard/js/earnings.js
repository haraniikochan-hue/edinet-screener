// Earnings dates of the companies that move the US market, for the calendar card's later pages.
// Source: Nasdaq's public earnings calendar (one request per US trading day, no key). It lists every
// company that reports; only these are kept: the index heavyweights (the Magnificent Seven, Eli Lilly,
// Walmart, JPMorgan, which opens each season), the semiconductors behind the SOX index — including
// the US-listed TSMC, ASML and Arm, which move it as much as any US name — and the AI and software
// bellwethers. The TV shows each by its ticker and logo (assets/earnings/<SYMBOL>.png); a symbol added here
// without a logo shows its ticker alone.
export const MAJOR_US = Object.freeze([
  'AAPL','MSFT','NVDA','GOOGL','AMZN','META','TSLA',
  'AVGO','AMD','MU','QCOM','INTC','TXN','AMAT','LRCX','KLAC','TSM','ASML','ARM',
  'ORCL','PLTR','NFLX',
  'JPM','LLY','WMT',
]);
const LISTED = new Set(MAJOR_US);

// Eight weeks covers a whole reporting season.
export const EARNINGS_DAYS = 56;
export const earningsUrl = date => `https://api.nasdaq.com/api/calendar/earnings?date=${date}`;
export const EARNINGS_URL = /^https:\/\/api\.nasdaq\.com\/api\/calendar\/earnings\?date=\d{4}-\d{2}-\d{2}$/;

const NY = 'America/New_York', clocks = new Map();
const parts = (timestamp, zone) => {
  if (!clocks.has(zone)) clocks.set(zone, new Intl.DateTimeFormat('en-US',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}));
  return Object.fromEntries(clocks.get(zone).formatToParts(timestamp).filter(p => p.type !== 'literal').map(p => [p.type, Number(p.value)]));
};
const etDate = timestamp => { const p = parts(timestamp, NY); return `${p.year}-${String(p.month).padStart(2,'0')}-${String(p.day).padStart(2,'0')}`; };
// The instant of a wall-clock time in a city's time zone (daylight saving included).
export function zonedTime(date, zone, hour, minute = 0) {
  const [y, m, d] = date.split('-').map(Number), wall = Date.UTC(y, m - 1, d, hour, minute);
  const p = parts(wall, zone), seen = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute);
  return wall - (seen - wall);
}
export const newYorkTime = (date, hour, minute = 0) => zonedTime(date, NY, hour, minute);

// The US weekdays from today (New York) for `days` calendar days.
export function earningsDates(now = Date.now(), days = EARNINGS_DAYS) {
  const dates = [], start = etDate(now);
  for (let i = 0; i < days; i++) {
    const date = new Date(Date.parse(`${start}T12:00Z`) + i * 86400000), weekday = date.getUTCDay();
    if (weekday !== 0 && weekday !== 6) dates.push(date.toISOString().slice(0, 10));
  }
  return dates;
}

const money = value => {
  if (typeof value !== 'string' || !value.trim()) return null;
  const negative = /^\(.*\)$/.test(value.trim()), number = Number(value.replace(/[$,()\s]/g, ''));
  return Number.isFinite(number) ? (negative ? -number : number) : null;
};
const TIMING = { 'time-pre-market':'pre', 'time-after-hours':'after' };
// Nasdaq only says "before the open" or "after the close". Each company releases at much the same
// time every quarter, so that usual time (in its release city, from its recent reports) gives the
// hour and minute. TSMC and ASML release at home, overnight for New York. When Nasdaq's session
// disagrees with the usual time the company may have moved, so only the session is shown.
export const RELEASE_TIMES = Object.freeze({
  AAPL:[NY,16,30], NVDA:[NY,16,20], AVGO:[NY,16,15], AMD:[NY,16,15], NFLX:[NY,16,0],
  MSFT:[NY,16,5], GOOGL:[NY,16,5], AMZN:[NY,16,5], META:[NY,16,5], TSLA:[NY,16,5], MU:[NY,16,5], QCOM:[NY,16,5],
  INTC:[NY,16,5], TXN:[NY,16,5], AMAT:[NY,16,5], LRCX:[NY,16,5], KLAC:[NY,16,5], ARM:[NY,16,5], ORCL:[NY,16,5], PLTR:[NY,16,5],
  JPM:[NY,6,45], LLY:[NY,6,45], WMT:[NY,7,0], TSM:['Asia/Taipei',13,30], ASML:['Europe/Amsterdam',7,0],
});
// Without a usual time, a report sits at the session's typical time: 8:00 or 16:05 in New York.
const AT = { pre:[8,0], after:[16,5], unknown:[12,0] };
function releaseTime(symbol, date, timing) {
  const usual = RELEASE_TIMES[symbol];
  if (usual) {
    const timestamp = zonedTime(date, ...usual), session = timestamp < newYorkTime(date, 9, 30) ? 'pre' : 'after';
    if (timing === 'unknown' || timing === session) return { timestamp, timing:session, exact:true };
  }
  return { timestamp:newYorkTime(date, ...AT[timing]), timing, exact:false };
}

export function parseEarnings(text, date) {
  const data = typeof text === 'string' ? JSON.parse(text) : text, rows = data?.data?.rows;
  if (!Array.isArray(rows)) throw new Error('決算予定がありません');
  return rows.filter(row => typeof row?.symbol === 'string' && LISTED.has(row.symbol)).map(row => {
    const { timestamp, timing, exact } = releaseTime(row.symbol, date, TIMING[row.time] || 'unknown');
    const quarter = /^([A-Z][a-z]{2})\/(\d{4})$/.exec(row.fiscalQuarterEnding || '');
    const month = quarter ? ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].indexOf(quarter[1]) + 1 : 0;
    return {
      id:`${row.symbol}:${date}`, symbol:row.symbol, company:String(row.name || '').trim(),
      date, timing, timestamp, exact,
      quarter:month ? `${quarter[2]}年${month}月までの四半期` : '',
      epsForecast:money(row.epsForecast), estimates:Number.isInteger(Number(row.noOfEsts)) && Number(row.noOfEsts) > 0 ? Number(row.noOfEsts) : null,
      lastYearEps:money(row.lastYearEPS), lastYearDate:/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(row.lastYearRptDt || '') ? row.lastYearRptDt : '',
      marketCap:money(row.marketCap),
    };
  });
}

// Reads the coming weeks three days at a time. A few missing days still give a calendar (and are
// counted); fewer than half answered is a failure.
export async function loadEarnings(fetchText, now = Date.now()) {
  const dates = earningsDates(now), settled = [];
  for (let i = 0; i < dates.length; i += 3) {
    settled.push(...await Promise.allSettled(dates.slice(i, i + 3).map(async date => parseEarnings(await fetchText(earningsUrl(date)), date))));
  }
  const answered = settled.filter(item => item.status === 'fulfilled');
  if (answered.length < Math.ceil(dates.length / 2)) throw new Error('決算予定を取得できません');
  const events = answered.flatMap(item => item.value).sort((a, b) => a.timestamp - b.timestamp || (b.marketCap ?? 0) - (a.marketCap ?? 0));
  return { events, from:dates[0], through:dates.at(-1), missing:dates.length - answered.length, companies:MAJOR_US.length };
}

// Reports still to come: one stays listed for two hours after its typical time.
export const upcomingEarnings = (events, now = Date.now()) => (events || []).filter(event => event.timestamp >= now - 2 * 3600000);
