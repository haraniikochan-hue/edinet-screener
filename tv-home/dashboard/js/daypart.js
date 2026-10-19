// The time of day, from the sun at the weather's location: it picks the background photos (New York by
// day, at sunset, by night) and, through the photo on screen, the theme. Sunset light lasts from an hour
// before sunset to 45 minutes after; dawn (45 minutes either side of sunrise) uses the sunset photos too.
const MINUTE = 60000, HOUR = 60 * MINUTE, JST = 9 * HOUR;
export const DAY_PARTS = Object.freeze(['day', 'dusk', 'night']);

export function dayPart(now, sunrise, sunset) {
  if (!Number.isFinite(sunrise) || !Number.isFinite(sunset) || !(sunset > sunrise)) [sunrise, sunset] = fallbackSun(now);
  if (now >= sunset - HOUR && now < sunset + 45 * MINUTE) return 'dusk';
  if (now >= sunrise - 45 * MINUTE && now < sunrise + 45 * MINUTE) return 'dusk';
  return now >= sunrise + 45 * MINUTE && now < sunset - HOUR ? 'day' : 'night';
}

// Without a forecast: 6:00 and 17:30 in Japan, the year's middle.
function fallbackSun(now) {
  const midnight = Math.floor((now + JST) / (24 * HOUR)) * 24 * HOUR - JST;
  return [midnight + 6 * HOUR, midnight + 17.5 * HOUR];
}

// Light glass with dark text over daytime photos, the dark smoke glass over sunset and night ones.
export const themeFor = part => part === 'day' ? 'light' : 'dark';
