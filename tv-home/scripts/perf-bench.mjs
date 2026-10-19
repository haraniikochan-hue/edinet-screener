// Optional performance check: steady-state cost of the running dashboard.
// PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs node scripts/perf-bench.mjs [url] [seconds] [cpuThrottle]
// Reports total Chromium CPU (renderer + GPU/compositor + browser, Linux /proc only), main-thread
// time from DevTools metrics, frames, long tasks and DOM size. FRAMES=1 adds a requestAnimationFrame
// counter (which itself forces a frame every vsync); INIT_CONFIG='{"motion":true}' seeds settings.
import { readFileSync, readdirSync } from 'node:fs';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const url = process.argv[2] || process.env.DASHBOARD_URL || 'http://127.0.0.1:4173/';
const seconds = Number(process.argv[3] || 20), throttle = Number(process.argv[4] || 1);
const browser = await chromium.launch({ headless:true, ...(process.env.CHROMIUM_PATH ? { executablePath:process.env.CHROMIUM_PATH } : {}), args:['--no-sandbox'] });
const page = await (await browser.newContext({ viewport:{ width:1920, height:1080 } })).newPage();
const cdp = await page.context().newCDPSession(page);
await cdp.send('Performance.enable');
if (throttle > 1) await cdp.send('Emulation.setCPUThrottlingRate', { rate:throttle });
if (process.env.INIT_CONFIG) await page.addInitScript(config => { if (!sessionStorage.getItem('bench')) { sessionStorage.setItem('bench','1'); localStorage.setItem('tv-home-config',config); } }, process.env.INIT_CONFIG);
await page.addInitScript(countFrames => {
  window.__frames = []; window.__long = [];
  if (countFrames) { const loop = t => { window.__frames.push(t); requestAnimationFrame(loop); }; requestAnimationFrame(loop); }
  try { new PerformanceObserver(list => { for (const entry of list.getEntries()) window.__long.push(entry.duration); }).observe({ type:'longtask', buffered:true }); } catch {}
}, Boolean(process.env.FRAMES));
await page.goto(url, { waitUntil:'domcontentloaded' });
try { await page.waitForFunction(() => document.querySelectorAll('.stock-chart svg').length >= 12, { timeout:60000 }); } catch { console.warn('Not every chart loaded; measuring anyway.'); }
await page.waitForTimeout(6000);

// Chromium's browser process is the one launched with --remote-debugging-pipe; sum it and its descendants.
function processTree() {
  const rows = readdirSync('/proc').filter(pid => /^\d+$/.test(pid)).map(pid => {
    try { const stat = readFileSync(`/proc/${pid}/stat`,'utf8').split(') ')[1].split(' '); return { pid:Number(pid), ppid:Number(stat[1]), ticks:Number(stat[11]) + Number(stat[12]), cmd:readFileSync(`/proc/${pid}/cmdline`,'utf8') }; } catch { return null; }
  }).filter(Boolean);
  const roots = rows.filter(row => row.cmd.includes('--remote-debugging-pipe') && row.ppid === process.pid).map(row => row.pid);
  const tree = new Set(roots);
  for (let grew = true; grew;) { grew = false; for (const row of rows) if (!tree.has(row.pid) && tree.has(row.ppid)) { tree.add(row.pid); grew = true; } }
  return rows.filter(row => tree.has(row.pid)).reduce((sum,row) => sum + row.ticks, 0) / 100;
}
const metrics = async () => Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(m => [m.name,m.value]));
let cpu0 = null; try { cpu0 = processTree(); } catch {}
const m0 = await metrics(), t0 = Date.now();
await page.evaluate(() => { window.__frames.length = 0; window.__long.length = 0; });
await page.waitForTimeout(seconds * 1000);
const m1 = await metrics(), wall = (Date.now() - t0) / 1000;
let cpu1 = null; try { cpu1 = processTree(); } catch {}
const browserSide = await page.evaluate(() => {
  const f = window.__frames, gaps = f.slice(1).map((t,i) => t - f[i]);
  return { frames:f.length, janky:gaps.filter(gap => gap > 50).length, longTasks:window.__long.length, longTaskMs:Math.round(window.__long.reduce((a,b) => a + b, 0)) };
});
const perSecond = key => +((m1[key] - m0[key]) / wall * 1000).toFixed(1);
console.log(JSON.stringify({
  url, throttle, seconds:+wall.toFixed(1),
  chromiumCpuPercent: cpu0 === null || cpu1 === null ? 'n/a' : +((cpu1 - cpu0) / wall * 100).toFixed(1),
  mainThreadMsPerSecond:{ task:perSecond('TaskDuration'), script:perSecond('ScriptDuration'), layout:perSecond('LayoutDuration'), style:perSecond('RecalcStyleDuration') },
  layoutsPerSecond:+((m1.LayoutCount - m0.LayoutCount) / wall).toFixed(2), styleRecalcsPerSecond:+((m1.RecalcStyleCount - m0.RecalcStyleCount) / wall).toFixed(2),
  ...(process.env.FRAMES ? { framesPerSecond:+(browserSide.frames / wall).toFixed(1), framesOver50ms:browserSide.janky } : {}),
  longTasks:browserSide.longTasks, longTaskMs:browserSide.longTaskMs, domNodes:m1.Nodes, jsHeapMB:+(m1.JSHeapUsedSize / 1048576).toFixed(1),
}, null, 2));
await browser.close();
