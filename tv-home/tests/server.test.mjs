import test from 'node:test';
import assert from 'node:assert/strict';
import {createAppServer,parseRSS,parseYieldCSV,memo} from '../server.mjs';
test('yield parser skips missing observations without treating holiday blanks as zero',()=>{
  assert.deepEqual(parseYieldCSV('observation_date,DGS10,DGS30\n2026-10-14,4.2,4.8\n2026-10-15,,\n2026-10-16,.,5\n2026-10-17,4.3,4.9'),[
    {date:'2026-10-14',value:4.2,thirty:4.8},{date:'2026-10-17',value:4.3,thirty:4.9},
  ]);
});
test('RSS returns headlines, source timestamps, and NHK links without article bodies or scripts',()=>{
  const xml='<rss><item><title><![CDATA[経済 &amp; IT <script>test</script>]]></title><link>http://www3.nhk.or.jp/news/1</link><pubDate>Sun, 18 Oct 2026 14:00:00 +0900</pubDate><description>full article</description></item><item><title>unsafe</title><link>javascript:alert(1)</link><pubDate>Sun, 18 Oct 2026 14:00:00 +0900</pubDate></item></rss>';
  const rows=parseRSS(xml);assert.equal(rows.length,1);assert.equal(rows[0].title,'経済 & IT test');assert.equal(rows[0].url,'https://www3.nhk.or.jp/news/1');assert.equal(rows[0].description,undefined);
});
test('RSS accepts NHK ONE article links and rejects look-alike hosts',()=>{
  const item=(link)=>`<item><title>見出し</title><link>${link}</link><pubDate>Sun, 18 Oct 2026 23:44:18 +0900</pubDate></item>`;
  const rows=parseRSS(`<rss>${item('https://news.web.nhk/newsweb/na/nd-20261018de61309')}${item('https://evilnhk.jp/news/1')}${item('https://news.web.nhk.example.com/x')}</rss>`);
  assert.deepEqual(rows.map(row=>row.url),['https://news.web.nhk/newsweb/na/nd-20261018de61309']);
});
test('server coalesces concurrent upstream requests',async()=>{
  let calls=0;let finish;const gate=new Promise(r=>{finish=r;});
  const loader=async()=>{calls++;await gate;return 42;};
  const a=memo('test-concurrent',60000,loader),b=memo('test-concurrent',60000,loader);finish();
  const results=await Promise.all([a,b]);assert.equal(calls,1);assert.equal(results[0].data,42);assert.deepEqual(results[0],results[1]);
});
test('HTTP serves only the dashboard and never local secrets or project source',async()=>{
  const server=createAppServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const base=`http://127.0.0.1:${server.address().port}`;
  try{
    const home=await fetch(base);assert.equal(home.status,200);assert.match(await home.text(),/TV Home/);assert.match(home.headers.get('content-security-policy'),/object-src 'none'/);
    for(const path of ['/.env.local','/config.local.json','/server.mjs','/HANDOFF.md','/%2eenv','/api/missing'])assert.equal((await fetch(base+path)).status,404,path);
    assert.equal((await fetch(base+'/api/config',{method:'POST'})).status,405);
    const config=await (await fetch(base+'/api/config')).json();assert.deepEqual(Object.keys(config).sort(),['backend','market','spotifyClientId','unsplash']);
  }finally{server.closeAllConnections();await new Promise(r=>server.close(r));}
});

test('calendar API keeps other providers available and labels a failed provider snapshot',async()=>{
  const server=createAppServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const base=`http://127.0.0.1:${server.address().port}`,original=globalThis.fetch;
  globalThis.fetch=async(url,options)=>{
    if(String(url).includes('bls.gov'))throw new Error('fixture: BLS unavailable');
    if(String(url).includes('bea.gov'))return {ok:true,text:async()=> 'BEGIN:VCALENDAR\nBEGIN:VEVENT\nSUMMARY:Personal Income and Outlays\\, September 2026\nDTSTART:20261029T123000Z\nEND:VEVENT\nEND:VCALENDAR'};
    return original(url,options);
  };
  try{
    const response=await original(base+'/api/calendar'),result=await response.json();
    assert.equal(response.status,200);assert.equal(result.stale,true);
    assert.equal(result.data.sources.find(s=>s.source==='BLS').status,'stale');
    assert.equal(result.data.sources.find(s=>s.source==='BEA').status,'live');
    assert.ok(result.data.events.some(e=>e.indicator==='CPI'));assert.ok(result.data.events.some(e=>e.indicator==='PCE'));assert.ok(result.data.events.some(e=>e.indicator==='FOMC'));
    assert.ok(result.data.events.every(e=>!('actual' in e)));
  }finally{globalThis.fetch=original;server.closeAllConnections();await new Promise(r=>server.close(r));}
});
