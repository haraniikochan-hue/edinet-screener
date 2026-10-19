import { nyInstant } from '../dashboard/js/market-clock.js';

export const CALENDAR_FEEDS = {
  BLS:'https://www.bls.gov/schedule/news_release/bls.ics',
  BEA:'https://www.bea.gov/news/schedule/ics/online-calendar-subscription.ics',
};
const urls={BLS:'https://www.bls.gov/schedule/',BEA:'https://www.bea.gov/news/schedule',FRB:'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'};
const definitions=[
  ['BLS',/^Consumer Price Index$/,'CPI','消費者物価指数','インフレ'],
  ['BLS',/^Employment Situation$/,'NFP','雇用統計','雇用・失業率'],
  ['BLS',/^Producer Price Index$/,'PPI','生産者物価指数','インフレ'],
  ['BLS',/^Job Openings and Labor Turnover Survey$/,'JOLTS','求人件数','雇用'],
  ['BEA',/^Personal Income and Outlays\b/,'PCE','PCE・個人所得','個人消費・インフレ'],
  ['BEA',/^GDP\s*\(/,'GDP','GDP','経済成長'],
];

export function parseEconomicICS(text,source) {
  if(!CALENDAR_FEEDS[source] || typeof text!=='string')throw new Error('カレンダーの配信元を確認してください');
  const unfolded=text.replace(/\r?\n[ \t]/g,''),events=new Map(),latest=new Map();
  for(const [,block] of unfolded.matchAll(/BEGIN:VEVENT\r?\n([\s\S]*?)END:VEVENT/g)){
    const fields=Object.fromEntries(block.split(/\r?\n/).map(line=>{const i=line.indexOf(':');return [line.slice(0,i),line.slice(i+1)];}));
    const identity=fields.UID||block,old=latest.get(identity);
    if(!old || Number(fields.SEQUENCE||0)>=Number(old.SEQUENCE||0))latest.set(identity,fields);
  }
  for(const fields of latest.values()){
    if(fields.STATUS==='CANCELLED' || Object.keys(fields).some(k=>k==='RRULE' || k.startsWith('RECURRENCE-ID')))continue;
    const summary=(fields.SUMMARY||'').replace(/\\n/g,' ').replace(/\\([,;\\])/g,'$1');
    const definition=definitions.find(([provider,re])=>provider===source && re.test(summary));if(!definition)continue;
    const dt=Object.entries(fields).find(([k])=>k==='DTSTART' || k.startsWith('DTSTART;'));if(!dt)continue;
    const [key,value]=dt,match=value.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})(Z?)$/);if(!match)continue;
    const [,year,month,day,hour,minute,second,z]=match,date=`${year}-${month}-${day}`;
    // Only explicit UTC or the official Eastern timezone is accepted.
    if(!z && !/TZID=(?:US-Eastern|US\/Eastern|America\/New_York)(?:;|$)/.test(key))continue;
    const dayTimestamp=Date.parse(`${date}T00:00:00Z`);
    if(+hour>23 || +minute>59 || +second>59 || !Number.isFinite(dayTimestamp) || new Date(dayTimestamp).toISOString().slice(0,10)!==date)continue;
    const timestamp=z?Date.parse(`${date}T${hour}:${minute}:${second}Z`):nyInstant(date,+hour,+minute).getTime()+Number(second)*1000;
    if(!Number.isFinite(timestamp))continue;
    const [,,indicator,baseTitle,category]=definition;
    const estimate=indicator==='GDP'?/Advance Estimate/.test(summary)?'速報値':/Second Estimate/.test(summary)?'改定値':/Third Estimate/.test(summary)?'確報値':'':'';
    const id=`${source}:${indicator}:${timestamp}`;
    events.set(id,{id,indicator,title:estimate?`${baseTitle} ${estimate}`:baseTitle,category,timestamp,source,url:urls[source],originalTitle:summary});
  }
  const rows=[...events.values()].sort((a,b)=>a.timestamp-b.timestamp || a.indicator.localeCompare(b.indicator));
  if(!rows.length)throw new Error(`${source}の主要経済指標が見つかりません`);
  return rows;
}

export function fomcEvents(data) {
  if(!Array.isArray(data?.meetings))return [];
  return data.meetings.filter(d=>/^\d{4}-\d{2}-\d{2}$/.test(d)).map(date=>({
    id:`FRB:FOMC:${date}`,indicator:'FOMC',title:'FOMC 政策金利',category:'金融政策',
    timestamp:nyInstant(date,14).getTime(),source:'FRB',url:urls.FRB,
    originalTitle:'FOMC policy decision',note:'通常の14:00 ETを予定時刻として表示',
  }));
}

export function mergeCalendar(sources) {
  return [...new Map(sources.flat().map(event=>[event.id,event])).values()].sort((a,b)=>a.timestamp-b.timestamp || a.indicator.localeCompare(b.indicator));
}
