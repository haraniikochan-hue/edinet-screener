import test from 'node:test';
import assert from 'node:assert/strict';
import { NHK_RSS, UPSTREAM_FEEDS, loadNews, loadCalendar } from '../dashboard/js/feeds.js';
import { CALENDAR_FEEDS } from '../dashboard/js/economic-calendar.js';

const rss = `<rss><channel><item><title>見出し</title><link>https://news.web.nhk/newsweb/na/1</link><pubDate>Mon, 19 Oct 2026 09:00:00 +0900</pubDate><description>要約</description></item></channel></rss>`;
const ics = summary => `BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:1\nDTSTART;TZID=US-Eastern:20261110T083000\nSUMMARY:${summary}\nEND:VEVENT\nEND:VCALENDAR`;
const snapshot = { events:[
  {id:'BEA:GDP:1',indicator:'GDP',title:'GDP',timestamp:1,source:'BEA'},
  {id:'FRB:FOMC:2',indicator:'FOMC',title:'FOMC 政策金利',timestamp:2,source:'FRB'},
], sources:[{source:'BEA',verifiedAt:'2026-10-18'},{source:'FRB',verifiedAt:'2026-10-18'}] };

test('the native proxy allowlist is exactly the news and calendar feeds', () => {
  assert.deepEqual(UPSTREAM_FEEDS, [NHK_RSS, CALENDAR_FEEDS.BLS, CALENDAR_FEEDS.BEA]);
});

test('news loads through the supplied fetcher and rejects an empty feed', async () => {
  const rows = await loadNews(async url => { assert.equal(url, NHK_RSS); return rss; });
  assert.equal(rows[0].title, '見出し'); assert.equal(rows[0].summary, '要約');
  await assert.rejects(loadNews(async () => '<rss></rss>'), /ニュースがありません/);
});

test('calendar uses live feeds and falls back to the snapshot per provider', async () => {
  const result = await loadCalendar(async url => {
    if (url === CALENDAR_FEEDS.BLS) return ics('Consumer Price Index');
    throw new Error('offline');
  }, snapshot);
  assert.deepEqual(result.sources.map(s => [s.source, s.status]), [['BLS','live'],['BEA','stale'],['FRB',undefined]]);
  assert.deepEqual(result.events.map(e => e.indicator).sort(), ['CPI','FOMC','GDP']);
});
