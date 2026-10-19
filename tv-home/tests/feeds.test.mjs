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

import { PHOTO_PERIODS, PHOTO_QUERIES, PHOTOS_PER_QUERY, loadPhotos, unsplashRandom, validPhotoQuery } from '../dashboard/js/feeds.js';
const photo = id => ({ urls:{regular:`https://images.unsplash.com/${id}?ixid=x`}, user:{name:`P${id}`, links:{html:`https://unsplash.com/@${id}`}}, links:{html:`https://unsplash.com/photos/${id}`} });

test('photos are New York at the time of day, from both searches, each kept once', async () => {
  const asked = [];
  const rows = await loadPhotos(async query => { asked.push(query); return query.includes('blue sky') ? [photo('b'), photo('shared')] : [photo('a'), photo('shared')]; }, 'day', () => 0);
  assert.deepEqual(asked, PHOTO_PERIODS.day.queries);
  assert.equal(rows.length, 3, 'a photo found by both searches appears once');
  assert.ok(rows.every(r => r.period === 'day' && r.title === 'ニューヨーク · 日中'));
  assert.match(rows[0].url, /w=1920/);
});

test('a failing search is skipped, every search refused reports the limit, and an unknown time is refused', async () => {
  const rows = await loadPhotos(async query => { if (query.includes('golden')) throw new Error('down'); return [photo(query.length)]; }, 'dusk');
  assert.equal(rows.length, 1); assert.equal(rows[0].period, 'dusk');
  await assert.rejects(loadPhotos(async () => { throw Object.assign(new Error('x'), { status:429 }); }, 'night'), /上限/);
  await assert.rejects(loadPhotos(async () => [photo(1)], 'noon'), /時間帯/);
});

test('only the listed searches build a random-photo URL', () => {
  assert.equal(PHOTO_QUERIES.length, 6); assert.ok(PHOTO_QUERIES.every(q => /new york|manhattan/.test(q)));
  assert.ok(validPhotoQuery('new york city skyline night')); assert.ok(!validPhotoQuery('paris city'));
  assert.equal(unsplashRandom('new york city skyline night'), `https://api.unsplash.com/photos/random?query=new%20york%20city%20skyline%20night&count=${PHOTOS_PER_QUERY}&orientation=landscape&content_filter=high`);
});
