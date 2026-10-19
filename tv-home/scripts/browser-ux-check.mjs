// Remote-control and detail-sheet behaviour on the TV stage, with fixtures for every feed.
// PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs node scripts/browser-ux-check.mjs
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { MARKETS } from '../dashboard/js/market-definitions.js';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch({ headless:true, ...(process.env.CHROMIUM_PATH ? { executablePath:process.env.CHROMIUM_PATH } : {}), args:['--no-sandbox'] });
const base = process.env.DASHBOARD_URL || 'http://127.0.0.1:4173/';
const report = [];

async function fixturePage({ clock = false } = {}) {
  const context = await browser.newContext({ viewport:{ width:1920, height:1080 } });
  const page = await context.newPage(), errors = [];
  page.on('pageerror', error => errors.push(error.message));
  if (clock) await page.clock.install();
  const now = Date.now();
  await page.route('https://api.open-meteo.com/**', route => route.abort());
  await page.route('https://air-quality-api.open-meteo.com/**', route => route.abort());
  await page.route('**/api/news', route => route.fulfill({ json:{ fetchedAt:now, stale:false, data:[1,2].map(i => ({ title:`テスト見出し${i}`, summary:`テスト要約${i}。`, url:`https://news.web.nhk/newsweb/na/test${i}`, publishedAt:new Date(now - i * 3600000).toUTCString(), source:'NHK 経済' })) } }));
  await page.routeWebSocket('wss://api.hyperliquid.xyz/ws', socket => socket.close());
  await page.route('https://api.hyperliquid.xyz/info', route => {
    const request = JSON.parse(route.request().postData());
    if (request.type === 'candleSnapshot') {
      const { coin, startTime } = request.req, step = 900000;
      return route.fulfill({ json:Array.from({ length:96 }, (_, i) => ({ s:coin, i:'15m', t:startTime + i * step, T:startTime + (i + 1) * step - 1, o:'50', c:String(50 + Math.sin(i / 6) * 3 + i / 48) })) });
    }
    const markets = MARKETS.filter(m => m.dex === (request.dex || ''));
    return route.fulfill({ json:[{ collateralToken:0, universe:markets.map(m => ({ name:m.coin, isDelisted:false })) }, markets.map(() => ({ markPx:'52', prevDayPx:'50' }))] });
  });
  await page.goto(base, { waitUntil:'domcontentloaded' });
  await page.waitForFunction(() => document.querySelectorAll('.calendar-event').length === 6 && document.querySelector('#news-title').textContent.startsWith('テスト見出し'), { timeout:30000 });
  return { context, page, errors };
}
const focused = page => page.evaluate(() => {
  const e = document.activeElement;
  return e?.dataset.app || e?.dataset.symbol || (e?.classList.contains('calendar-event') ? `cal${[...e.parentNode.children].indexOf(e)}` : e?.id) || e?.tagName;
});

try {
  const { context, page, errors } = await fixturePage();
  await page.waitForFunction(() => document.querySelectorAll('.stock-chart svg').length === 12, { timeout:30000 });
  assert.equal(await focused(page), 'smarttube', 'the TV starts on the app dock');

  // Remote navigation: natural edges, focus memory and Back.
  await page.locator('[data-app="netflix"]').focus();
  await page.keyboard.press('ArrowDown'); assert.equal(await focused(page), 'netflix', 'nothing below the dock');
  await page.keyboard.press('ArrowUp'); assert.equal(await focused(page), 'news-title');
  await page.keyboard.press('ArrowDown'); assert.equal(await focused(page), 'netflix', 'down returns to the app you came from');
  await page.locator('#refresh').focus(); await page.keyboard.press('ArrowDown');
  assert.equal(await page.evaluate(() => document.activeElement.classList.contains('stock-row')), true, 'top buttons lead down into the market');
  // Weather is offline in this fixture, so the waiting badge is shown and is the leftmost top control.
  await page.locator('#connection-status[data-state="waiting"]').waitFor({ timeout:20000 });
  await page.locator('#refresh').focus(); await page.keyboard.press('ArrowLeft'); assert.equal(await focused(page), 'connection-status');
  await page.keyboard.press('ArrowLeft'); assert.equal(await focused(page), 'connection-status', 'nothing further left of the top controls');
  await page.locator('.calendar-event').first().focus(); await page.keyboard.press('ArrowRight');
  assert.equal(await page.evaluate(() => document.activeElement.closest('.market-card') !== null), true, 'calendar rows lead right into the market');
  await page.locator('.calendar-event').last().focus(); await page.keyboard.press('ArrowDown');
  assert.equal(await focused(page), 'cal0'); assert.match(await page.locator('#calendar-page').textContent(), /^7–12 \//, 'moving past the last release turns the page');
  await page.keyboard.press('ArrowUp'); assert.equal(await focused(page), 'cal5'); assert.match(await page.locator('#calendar-page').textContent(), /^1–6 \//);
  await page.keyboard.press('Escape'); assert.equal(await focused(page), 'netflix', 'Back returns to the last app on the dock');
  await page.locator('[data-brand="settings"]').focus(); await page.keyboard.press('ArrowRight');
  assert.equal(await page.evaluate(() => document.activeElement.dataset.brand), 'settings', 'credits and the hidden photo switch are not focus stops');
  assert.equal(await page.locator('#next-photo').isHidden(), true, 'no photo switch while there is one photo');
  report.push('Remote: dock is the floor, up/down retraces to the same app, top buttons lead into the market, calendar pages by moving past its edges, Back returns to the dock, credits and the single-photo switch are skipped.');

  // Detail sheets instead of leaving the launcher.
  await page.locator('[data-symbol="SP500"]').focus(); await page.keyboard.press('Enter');
  await page.locator('#detail-overlay').waitFor({ state:'visible' });
  assert.match(await page.locator('#detail-title').textContent(), /^SP500/);
  assert.match(await page.locator('#detail-facts').textContent(), /xyz:SP500.*無期限先物/);
  assert.equal(await page.locator('#detail-chart svg').count(), 1, 'a large 24h chart');
  await page.keyboard.press('Escape'); await page.locator('#detail-overlay').waitFor({ state:'hidden' });
  assert.equal(await focused(page), 'SP500', 'closing returns focus to the row');
  await page.locator('.calendar-event').first().focus(); await page.keyboard.press('Enter');
  await page.locator('#detail-overlay').waitFor({ state:'visible' });
  assert.match(await page.locator('#detail-facts').textContent(), /米国東部時間/);
  assert.match(await page.locator('#detail-link').getAttribute('href'), /^https:\/\/www\.(federalreserve|bls|bea)\.gov\//);
  await page.keyboard.press('Escape');
  await page.locator('#news-title').focus(); await page.keyboard.press('Enter');
  await page.locator('#detail-overlay').waitFor({ state:'visible' });
  assert.equal(await page.locator('#detail-body').textContent(), 'テスト要約1。');
  assert.match(await page.locator('#detail-link').getAttribute('href'), /^https:\/\/news\.web\.nhk\//);
  assert.equal(page.url(), base, 'OK never navigates away from the dashboard');
  await page.keyboard.press('Escape');
  await page.locator('#connection-status[data-state="waiting"]').waitFor({ timeout:20000 });
  await page.locator('#connection-status').focus(); await page.keyboard.press('Enter');
  await page.locator('#detail-overlay').waitFor({ state:'visible' });
  assert.equal(await page.locator('#detail-title').textContent(), 'データの状態');
  assert.match(await page.locator('#detail-facts').textContent(), /天気(取得できません|更新待ち)/);
  await page.keyboard.press('Escape');
  report.push('OK opens a detail sheet in place: market rows show a large 24h chart, contract, unit and received time; releases show US Eastern time; headlines show the lead; the status badge lists each feed. Back closes and restores focus.');

  // Settings with a remote only: arrows leave selects and text fields, OK toggles switches.
  await page.locator('[data-brand="settings"]').focus(); await page.keyboard.press('Enter');
  await page.locator('#settings-dialog').waitFor({ state:'visible' });
  const visited = [];
  for (let i = 0; i < 40; i++) {
    await page.keyboard.press('ArrowDown');
    const id = await page.evaluate(() => document.activeElement.id || document.activeElement.tagName);
    if (visited.at(-1) === id) break;
    visited.push(id);
  }
  for (const id of ['market-mode','crypto-source-select','photo-mode','photo-interval','motion','SUMMARY','spotify-client-id','adblock-check','cancel-settings']) assert.ok(visited.includes(id), `remote reaches ${id}: ${visited.join(' → ')}`);
  await page.keyboard.press('ArrowRight');
  assert.equal(await page.evaluate(() => document.activeElement.textContent), '設定を保存', 'Save sits right of Cancel');
  assert.equal(await page.locator('#market-mode').inputValue(), 'custom', 'arrows never change a select');
  await page.locator('#motion').focus(); await page.keyboard.press('Enter');
  assert.equal(await page.locator('#motion').isChecked(), true, 'OK toggles a switch');
  await page.keyboard.press('Enter'); assert.equal(await page.locator('#motion').isChecked(), false);
  await page.keyboard.press('Escape'); await page.locator('#settings-overlay').waitFor({ state:'hidden' });
  report.push('Settings by remote: Down walks every field to Save without changing selects; OK toggles switches; Back closes.');
  assert.deepEqual(errors, []);
  await context.close();

  // An idle TV comes back to rest on the dock.
  const idle = await fixturePage({ clock:true });
  await idle.page.locator('.calendar-event').nth(2).focus();
  await idle.page.clock.runFor(75000);
  assert.equal(await idle.page.evaluate(() => document.activeElement.closest('#apps') !== null), true, 'idle focus returns to the dock');
  report.push('After a minute without input, focus returns to the dock so no highlight lingers on a card.');
  assert.deepEqual(idle.errors, []);
  await idle.context.close();

  await mkdir('artifacts', { recursive:true });
  await writeFile('artifacts/ux-check.json', JSON.stringify({ checkedAt:new Date().toISOString(), scope:'Fixture feeds; keyboard events stand in for a TV remote', report }, null, 2));
  console.log(report.join('\n'));
} finally { await browser.close(); }
