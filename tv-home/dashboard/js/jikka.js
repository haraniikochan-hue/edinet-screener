// The parents' TV (js/profile.js): "continue watching" — the apps opened most recently — and the input switcher.
// Google TV's own continue-watching row is not readable by another launcher on this TV (its Watch Next table is
// empty and the rest comes from Google's servers), so the most recent apps stand in: each reopens where it was left.
import { nativeAppTile } from './launcher.js';

const el = (tag, className = '', content = '') => { const node = document.createElement(tag); node.className = className; node.textContent = content; return node; };
const icon = (name, className = 'icon') => {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('class', className); svg.setAttribute('aria-hidden', 'true');
  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use'); use.setAttribute('href', `#i-${name}`); svg.append(use); return svg;
};
const call = (name, fallback) => {
  try { return typeof window.Android?.[name] === 'function' ? JSON.parse(window.Android[name]()) : fallback; } catch { return fallback; }
};
const banner = value => typeof value === 'string' && /^data:image\/(?:png|webp);base64,[A-Za-z0-9+/=]+$/.test(value) ? value : '';
export const RECENT_COUNT = 6;

const DAY = 86400000;
const TIME = new Intl.DateTimeFormat('ja-JP', { timeZone:'Asia/Tokyo', hour:'2-digit', minute:'2-digit', hourCycle:'h23' });
const DAY_KEY = new Intl.DateTimeFormat('en-CA', { timeZone:'Asia/Tokyo', year:'numeric', month:'2-digit', day:'2-digit' });
// "今日 19:20", "昨日", "3日前": when the app was last opened, in Japan time.
export function lastUsedLabel(at, now = Date.now()) {
  const days = Math.round((Date.parse(DAY_KEY.format(now)) - Date.parse(DAY_KEY.format(at))) / DAY);
  return days <= 0 ? `今日 ${TIME.format(at)}` : days === 1 ? '昨日' : `${days}日前`;
}

// The two inputs used most lead as large buttons: HDMI 1 (the recorder), then the TV app; the rest follow as pills.
export function arrangeInputs(inputs) {
  const list = Array.isArray(inputs) ? inputs.filter(i => i && typeof i.id === 'string' && typeof i.label === 'string') : [];
  const hdmi1 = list.find(i => i.kind === 'hdmi' && /^HDMI\s*1$/i.test(i.label)) || list.find(i => i.kind === 'hdmi');
  const tv = list.find(i => i.kind === 'tv');
  const main = [hdmi1, tv].filter(Boolean);
  return { main, others:list.filter(i => !main.includes(i)) };
}

// Every input on one row, HDMI 1 and the TV app first and a little wider. Re-read on every return home: the
// inputs register a little after the TV starts, and a recorder may be switched on later.
export function renderInputs(row) {
  const inputs = call('inputs', []);
  const key = JSON.stringify(inputs);
  if (row.dataset.key === key) return;
  row.dataset.key = key;
  const focused = row.contains(document.activeElement) ? document.activeElement.dataset.input : null;
  const { main, others } = arrangeInputs(inputs);
  row.replaceChildren(...[...main, ...others].map(input => {
    const button = el('button', 'input-button'); button.type = 'button'; button.dataset.input = input.id;
    if (main.includes(input)) button.dataset.main = '';
    button.dataset.connected = String(input.connected !== false); button.setAttribute('aria-label', `${input.label}に切り替え`);
    button.append(icon(input.kind === 'tv' ? 'tv' : 'hdmi'), el('span', '', input.label));
    return button;
  }));
  if (!main.length && !others.length) row.append(el('p', 'recent-empty', '入力を確認できません'));
  if (focused) row.querySelector(`[data-input="${CSS.escape(focused)}"]`)?.focus({ preventScroll:true });
}
// False when the TV has no such input any more, or nothing can show it.
export function switchInput(id) {
  try { return window.Android?.switchInput?.(id) === true; } catch { return false; }
}

// apps: the launcher's app list ({packageName, name, icon}); only those can be opened from the page.
export function renderRecent(grid, apps, now = Date.now()) {
  const result = call('recentApps', { granted:false }) || { granted:false };
  // The app is still reading its app list at start-up: the row keeps what it shows until it is told again.
  if (result.pending || !apps.length) return;
  const byPackage = new Map(apps.map(app => [app.packageName, app]));
  const recent = result.granted && Array.isArray(result.apps) ? result.apps.filter(r => byPackage.has(r?.packageName) && Number.isFinite(r.lastUsed)).slice(0, RECENT_COUNT) : [];
  // Rebuilding the row would drop the focus a viewer has on it, so an unchanged list is left as it is.
  const key = JSON.stringify([result.granted, recent.map(r => r.packageName), recent.map(r => lastUsedLabel(r.lastUsed, now))]);
  if (grid.dataset.key === key) return;
  const focused = grid.contains(document.activeElement) ? document.activeElement.dataset.package : null;
  grid.dataset.key = key;
  if (!result.granted) { grid.replaceChildren(el('p', 'recent-empty', '使用状況へのアクセスを許可すると、最近使ったアプリが並びます')); return; }
  if (!recent.length) { grid.replaceChildren(el('p', 'recent-empty', 'アプリを使うと、ここから続きを見られます')); return; }
  grid.replaceChildren(...recent.map(({ packageName, lastUsed, banner:art }) => {
    const app = byPackage.get(packageName);
    const button = el('button', 'recent-app'); button.type = 'button'; button.dataset.package = packageName;
    button.setAttribute('aria-label', `${app.name}の続きを見る`);
    const frame = el('span', 'recent-banner'); frame.setAttribute('aria-hidden', 'true');
    const image = banner(art);
    if (image) { const img = el('img'); img.src = image; img.alt = ''; frame.append(img); }
    else frame.append(nativeAppTile(app).querySelector('.app-icon'));
    const meta = el('span', 'recent-meta'); meta.append(el('span', 'recent-name', app.name), el('span', 'recent-when', lastUsedLabel(lastUsed, now)));
    button.append(frame, meta);
    return button;
  }));
  if (focused) grid.querySelector(`[data-package="${CSS.escape(focused)}"]`)?.focus({ preventScroll:true });
}
