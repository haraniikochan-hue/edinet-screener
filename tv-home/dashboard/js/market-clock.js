// Regular NYSE cash-equity sessions only. No extended-hours or emergency closures.
// Calendar verified 2026-10-18 against the NYSE/ICE 2026–2028 official calendar.
export const CALENDAR_SOURCE = 'https://www.nyse.com/markets/hours-calendars';
export const HOLIDAYS = {
  2026: ['01-01','01-19','02-16','04-03','05-25','06-19','07-03','09-07','11-26','12-25'],
  2027: ['01-01','01-18','02-15','03-26','05-31','06-18','07-05','09-06','11-25','12-24'],
  2028: ['01-17','02-21','04-14','05-29','06-19','07-04','09-04','11-23','12-25'],
};
const EARLY_CLOSE = new Set(['2026-11-27','2026-12-24','2027-11-26','2028-07-03','2028-11-24']);
const nyFormat = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
});
export function nyParts(date) {
  return Object.fromEntries(nyFormat.formatToParts(date).filter(p => p.type !== 'literal').map(p => [p.type, Number(p.value)]));
}
const pad = n => String(n).padStart(2, '0');
export const dateKey = ({year,month,day}) => `${year}-${pad(month)}-${pad(day)}`;
export function nyInstant(date, hour, minute = 0) {
  const [year, month, day] = date.split('-').map(Number);
  const target = Date.UTC(year, month - 1, day, hour, minute);
  let guess = target;
  for (let i = 0; i < 3; i++) {
    const p = nyParts(new Date(guess));
    guess += target - Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute, p.second);
  }
  return new Date(guess);
}
export function sessionFor(date) {
  const year = Number(date.slice(0, 4));
  if (!HOLIDAYS[year]) return undefined;
  const day = new Date(`${date}T12:00:00Z`).getUTCDay();
  if (day === 0 || day === 6 || HOLIDAYS[year].includes(date.slice(5))) return null;
  return { open: nyInstant(date, 9, 30), close: nyInstant(date, EARLY_CLOSE.has(date) ? 13 : 16), early: EARLY_CLOSE.has(date) };
}
export function marketStatus(now = new Date()) {
  const key = dateKey(nyParts(now));
  const today = sessionFor(key);
  if (today === undefined) return { state: 'unknown', label: '取引カレンダーの更新が必要', progress: 0 };
  if (today && now >= today.open && now < today.close) {
    return { state: 'open', label: today.early ? '短縮取引・クローズまで' : 'クローズまで', target: today.close, remaining: today.close - now, progress: (now - today.open) / (today.close - today.open) };
  }
  const day = new Date(`${key}T12:00:00Z`);
  let previous;
  for (let offset = 0; offset < 12; offset++) {
    const d = new Date(day); d.setUTCDate(day.getUTCDate() - offset);
    const s = sessionFor(d.toISOString().slice(0, 10));
    if (s && s.close <= now) { previous = s.close; break; }
  }
  for (let offset = 0; offset < 12; offset++) {
    const d = new Date(day); d.setUTCDate(day.getUTCDate() + offset);
    const s = sessionFor(d.toISOString().slice(0, 10));
    if (s === undefined) break;
    if (s && s.open > now) return {
      state: 'closed', label: '次のオープンまで', target: s.open, remaining: s.open - now,
      progress: previous ? Math.max(0, Math.min(1, (now - previous) / (s.open - previous))) : 0,
    };
  }
  return { state: 'unknown', label: '取引カレンダーの更新が必要', progress: 0 };
}
export function countdown(milliseconds) {
  const total = Math.max(0, Math.ceil(milliseconds / 60000));
  const days = Math.floor(total / 1440), hours = Math.floor(total % 1440 / 60), minutes = total % 60;
  return `${days ? `${days}日 ` : ''}${hours}時間${String(minutes).padStart(2, '0')}分`;
}
