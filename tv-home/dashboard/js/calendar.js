const format=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'});
export const jstDay=date=>format.format(new Date(date));
export function upcomingEvents(events,now=Date.now()) {
  const seen=new Set();
  return (Array.isArray(events)?events:[]).filter(e=>{
    if(!e || typeof e.id!=='string' || seen.has(e.id) || typeof e.title!=='string' || typeof e.indicator!=='string' || !['BLS','BEA','FRB'].includes(e.source) || !Number.isFinite(e.timestamp) || e.timestamp<now)return false;
    seen.add(e.id);return true;
  }).sort((a,b)=>a.timestamp-b.timestamp || a.indicator.localeCompare(b.indicator));
}
export function eventPage(events,page=0,size=5,now=Date.now()) {
  const upcoming=upcomingEvents(events,now),pages=Math.max(1,Math.ceil(upcoming.length/size)),index=Math.min(Math.max(0,page),pages-1);
  return {events:upcoming.slice(index*size,(index+1)*size),index,pages,total:upcoming.length};
}
