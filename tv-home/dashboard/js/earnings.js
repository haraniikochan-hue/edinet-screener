// Earnings dates of major US companies for the calendar card's later pages. Source: Nasdaq's
// public earnings calendar (one request per US trading day, no key). It lists every company that
// reports; only the companies below are kept. The list is US companies near the top of the S&P 500
// by size — edit it to follow other names (Nasdaq symbol → name shown on the TV).
export const MAJOR_US = Object.freeze({
  AAPL:'アップル', MSFT:'マイクロソフト', NVDA:'エヌビディア', GOOGL:'アルファベット', AMZN:'アマゾン', META:'メタ',
  AVGO:'ブロードコム', TSLA:'テスラ', ORCL:'オラクル', CRM:'セールスフォース', ADBE:'アドビ', AMD:'AMD', INTC:'インテル',
  CSCO:'シスコ', IBM:'IBM', QCOM:'クアルコム', TXN:'テキサス・インスツルメンツ', NOW:'サービスナウ', INTU:'インテュイット',
  AMAT:'アプライド・マテリアルズ', LRCX:'ラムリサーチ', MU:'マイクロン', KLAC:'KLA', ADI:'アナログ・デバイセズ',
  PLTR:'パランティア', NFLX:'ネットフリックス', UBER:'ウーバー', PANW:'パロアルト', ANET:'アリスタ',
  JPM:'JPモルガン', V:'ビザ', MA:'マスターカード', BAC:'バンク・オブ・アメリカ', WFC:'ウェルズ・ファーゴ',
  GS:'ゴールドマン・サックス', MS:'モルガン・スタンレー', C:'シティグループ', AXP:'アメックス', BLK:'ブラックロック',
  SCHW:'チャールズ・シュワブ', SPGI:'S&Pグローバル', CME:'CMEグループ', COF:'キャピタル・ワン', 'BRK.B':'バークシャー',
  LLY:'イーライリリー', UNH:'ユナイテッドヘルス', JNJ:'J&J', ABBV:'アッヴィ', MRK:'メルク', PFE:'ファイザー',
  TMO:'サーモフィッシャー', ABT:'アボット', DHR:'ダナハー', AMGN:'アムジェン', ISRG:'インテュイティブ', GILD:'ギリアド',
  BMY:'ブリストル・マイヤーズ', CVS:'CVSヘルス',
  WMT:'ウォルマート', COST:'コストコ', HD:'ホーム・デポ', LOW:'ロウズ', PG:'P&G', KO:'コカ・コーラ', PEP:'ペプシコ',
  MCD:'マクドナルド', NKE:'ナイキ', SBUX:'スターバックス', DIS:'ディズニー', TJX:'TJX', PM:'フィリップ・モリス',
  CMCSA:'コムキャスト', T:'AT&T', VZ:'ベライゾン', TMUS:'Tモバイル', BKNG:'ブッキング',
  XOM:'エクソンモービル', CVX:'シェブロン', CAT:'キャタピラー', GE:'GEエアロスペース', BA:'ボーイング', RTX:'RTX',
  HON:'ハネウェル', UNP:'ユニオン・パシフィック', LMT:'ロッキード', DE:'ディア', UPS:'UPS', NEE:'ネクステラ',
});

export const EARNINGS_DAYS = 21;
export const earningsUrl = date => `https://api.nasdaq.com/api/calendar/earnings?date=${date}`;
export const EARNINGS_URL = /^https:\/\/api\.nasdaq\.com\/api\/calendar\/earnings\?date=\d{4}-\d{2}-\d{2}$/;

const ET = new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
const etParts = timestamp => Object.fromEntries(ET.formatToParts(timestamp).filter(p => p.type !== 'literal').map(p => [p.type, Number(p.value)]));
const etDate = timestamp => { const p = etParts(timestamp); return `${p.year}-${String(p.month).padStart(2,'0')}-${String(p.day).padStart(2,'0')}`; };
// The instant of a New York wall-clock time (daylight saving included).
export function newYorkTime(date, hour, minute = 0) {
  const [y, m, d] = date.split('-').map(Number), wall = Date.UTC(y, m - 1, d, hour, minute);
  const p = etParts(wall), seen = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute);
  return wall - (seen - wall);
}

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
// Reports are placed at a typical time: before the open (8:00 New York) or after the close (16:05).
const AT = { pre:[8,0], after:[16,5], unknown:[12,0] };

export function parseEarnings(text, date) {
  const data = typeof text === 'string' ? JSON.parse(text) : text, rows = data?.data?.rows;
  if (!Array.isArray(rows)) throw new Error('決算予定がありません');
  return rows.filter(row => typeof row?.symbol === 'string' && Object.prototype.hasOwnProperty.call(MAJOR_US, row.symbol)).map(row => {
    const timing = TIMING[row.time] || 'unknown', [hour, minute] = AT[timing];
    const quarter = /^([A-Z][a-z]{2})\/(\d{4})$/.exec(row.fiscalQuarterEnding || '');
    const month = quarter ? ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].indexOf(quarter[1]) + 1 : 0;
    return {
      id:`${row.symbol}:${date}`, symbol:row.symbol, name:MAJOR_US[row.symbol], company:String(row.name || '').trim(),
      date, timing, timestamp:newYorkTime(date, hour, minute),
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
  return { events, from:dates[0], through:dates.at(-1), missing:dates.length - answered.length, companies:Object.keys(MAJOR_US).length };
}

// Reports still to come: one stays listed for two hours after its typical time.
export const upcomingEarnings = (events, now = Date.now()) => (events || []).filter(event => event.timestamp >= now - 2 * 3600000);
