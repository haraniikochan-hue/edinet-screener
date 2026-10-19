import { isNumber, weatherLabel } from './data.js';

export const HOUR = 3600000;
const JST = 9 * HOUR;
const NS = 'http://www.w3.org/2000/svg';
const dayKey = timestamp => new Date(timestamp + JST).toISOString().slice(0,10);

// Open-Meteo returns local ISO times for the explicitly requested Asia/Tokyo zone.
// Never parse these in the browser's own timezone.
export function weatherTimestamp(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::00)?$/.test(value)) return NaN;
  const timestamp = Date.parse(`${value}+09:00`);
  if (!Number.isFinite(timestamp) || new Date(timestamp + JST).toISOString().slice(0,16) !== value.slice(0,16)) return NaN;
  return timestamp;
}

export function weatherIsStale(result, now = Date.now()) {
  const observed = weatherTimestamp(result?.data?.current?.time);
  return Boolean(result?.stale) || !Number.isFinite(observed) || now - observed > 3 * HOUR
    || !isNumber(result?.fetchedAt) || now - result.fetchedAt > 3 * HOUR;
}

export function weatherSymbol(code, isDay) {
  if (code === 0 || code === 1 || code === 2) {
    if (isDay !== 0 && isDay !== 1) return 'unknown';
    return code === 0 ? (isDay ? 'sun' : 'moon') : (isDay ? 'partly-day' : 'partly-night');
  }
  if (code === 3) return 'cloud';
  if ([45,48].includes(code)) return 'fog';
  if ([51,53,55,56,57,61,63,65,66,67,80,81,82].includes(code)) return 'rain';
  if ([71,73,75,77,85,86].includes(code)) return 'snow';
  if ([95,96,99].includes(code)) return 'thunder';
  return 'unknown';
}

export function hourlyForecast(data, now = Date.now()) {
  const hourly = data?.hourly || {};
  const byTime = new Map();
  for (const [index,value] of (Array.isArray(hourly.time) ? hourly.time : []).entries()) {
    const timestamp = weatherTimestamp(value);
    if (Number.isFinite(timestamp)) byTime.set(timestamp,index);
  }
  const first = (Math.floor(now / HOUR) + 1) * HOUR;
  return Array.from({length:6}, (_,index) => {
    const timestamp = first + index * HOUR, source = byTime.get(timestamp);
    const read = key => source === undefined ? null : hourly[key]?.[source];
    const temperature = read('temperature_2m'), probability = read('precipitation_probability');
    const code = read('weather_code'), isDay = read('is_day');
    const newDay = dayKey(timestamp) !== dayKey(index ? timestamp - HOUR : now);
    return {
      timestamp, label:`${newDay ? '明日 ' : ''}${new Date(timestamp + JST).getUTCHours()}時`,
      temperature:isNumber(temperature) && temperature >= -100 && temperature <= 70 ? temperature : null,
      probability:isNumber(probability) && probability >= 0 && probability <= 100 ? probability : null,
      code:Number.isInteger(code) ? code : null, isDay:isDay === 0 || isDay === 1 ? isDay : null,
    };
  });
}

export function temperatureTrend(rows) {
  const temperatures = rows.map(row=>row.temperature).filter(isNumber);
  if (!temperatures.length) return {points:rows.map(()=>null),segments:[]};
  const min = Math.min(...temperatures), max = Math.max(...temperatures);
  // A minimum 6°C vertical scale prevents nearly flat forecasts looking volatile.
  const span = Math.max(6,max-min), middle = (min+max)/2;
  const points = rows.map((row,index)=>isNumber(row.temperature)
    ? {x:(index+.5)*600/rows.length,y:35-(row.temperature-middle)/span*18} : null);
  const segments = [];let segment = [];
  for (const point of points) {
    if (point) segment.push(point);
    else if (segment.length) {segments.push(segment);segment=[];}
  }
  if (segment.length) segments.push(segment);
  return {points,segments};
}

// Apple Weather–style temperature colours: cold blue through mint and yellow to hot red.
const TEMPERATURE_COLORS = [[-10,[122,167,255]],[0,[90,200,250]],[10,[99,230,190]],[17,[181,230,85]],[22,[255,214,10]],[27,[255,159,10]],[32,[255,107,61]],[38,[255,55,95]]];
export function temperatureColor(celsius) {
  const stops = TEMPERATURE_COLORS, value = Math.min(stops.at(-1)[0],Math.max(stops[0][0],celsius));
  const upper = stops.findIndex(([t])=>t>=value), [t1,c1] = stops[Math.max(0,upper-1)], [t2,c2] = stops[upper];
  const ratio = t2===t1 ? 0 : (value-t1)/(t2-t1);
  return `rgb(${c1.map((c,i)=>Math.round(c+(c2[i]-c)*ratio)).join(',')})`;
}

function svgNode(tag, attributes = {}) {
  const node = document.createElementNS(NS,tag);
  for (const [key,value] of Object.entries(attributes)) node.setAttribute(key,String(value));
  return node;
}
function node(tag, className, text) {
  const element = document.createElement(tag);element.className=className;
  if (text !== undefined) element.textContent=text;
  return element;
}

export function makeWeatherIcon(code, isDay) {
  const kind = weatherSymbol(code,isDay);
  const svg = svgNode('svg',{viewBox:'0 0 32 32',class:`weather-glyph weather-${kind}`,'aria-hidden':'true'});
  const path = (d,className='') => svg.append(svgNode('path',{d,class:className}));
  const circle = (cx,cy,r,className='') => svg.append(svgNode('circle',{cx,cy,r,class:className}));
  const sun = (small=false) => {
    const group = svgNode('g',small ? {transform:'translate(0 -1) scale(.8)'} : {});
    group.append(svgNode('circle',{cx:16,cy:16,r:6,class:'glyph-sun'}),svgNode('path',{d:'M16 3v3m0 20v3M3 16h3m20 0h3M6.8 6.8l2.1 2.1m14.2 14.2 2.1 2.1M6.8 25.2l2.1-2.1M23.1 8.9l2.1-2.1',class:'glyph-rays'}));
    svg.append(group);
  };
  const moon = small => path(small ? 'M17 3a9 9 0 1 0 10 11A10 10 0 0 1 17 3Z' : 'M20 3a13 13 0 1 0 10 18A14 14 0 0 1 20 3Z','glyph-moon');
  const cloud = () => path('M7 24a5.5 5.5 0 0 1-.9-10.9 8 8 0 0 1 15.3-2.2A6.5 6.5 0 1 1 25 24Z','glyph-cloud');
  if (kind === 'sun') sun();
  else if (kind === 'moon') moon(false);
  else if (kind === 'unknown') path('M11 16h10','glyph-unknown');
  else {
    if (kind === 'partly-day') sun(true);
    if (kind === 'partly-night') moon(true);
    const before = svg.childNodes.length;cloud();
    if (['rain','snow','thunder','fog'].includes(kind)) svg.childNodes[before].setAttribute('transform','translate(0 -4)');
    if (kind === 'rain') path('m9 24-2 4m10-4-2 4m10-4-2 4','glyph-rain');
    if (kind === 'snow') {circle(9,27,1.4,'glyph-snow');circle(16,25,1.4,'glyph-snow');circle(23,27,1.4,'glyph-snow');}
    if (kind === 'thunder') path('m17 20-5 6h5l-2 5 7-8h-5l2-3','glyph-lightning');
    if (kind === 'fog') path('M5 25h22M8 29h16','glyph-fog');
  }
  return svg;
}

export function renderHourlyForecast(container, rows) {
  container.replaceChildren();
  const hasData = rows.some(row=>isNumber(row.temperature) || isNumber(row.probability) || weatherSymbol(row.code,row.isDay)!=='unknown');
  if (!hasData) {
    container.append(node('p','hourly-empty','時間別予報を取得できません'));
    return false;
  }
  const {points,segments} = temperatureTrend(rows);
  const graph = svgNode('svg',{viewBox:'0 0 600 52',preserveAspectRatio:'none',class:'hourly-trend','aria-hidden':'true'});
  const gradient = svgNode('linearGradient',{id:'hourly-temperature',gradientUnits:'userSpaceOnUse',x1:0,x2:600,y1:0,y2:0});
  rows.forEach((row,index)=>{
    if (points[index]) gradient.append(svgNode('stop',{offset:(points[index].x/600).toFixed(4),'stop-color':temperatureColor(row.temperature)}));
  });
  // The fill under the line fades out downwards instead of forming a flat band.
  const fade = svgNode('linearGradient',{id:'hourly-fade',x1:0,x2:0,y1:0,y2:1});
  fade.append(svgNode('stop',{offset:0,'stop-color':'#fff','stop-opacity':.9}),svgNode('stop',{offset:1,'stop-color':'#fff','stop-opacity':0}));
  const mask = svgNode('mask',{id:'hourly-area-mask',maskUnits:'userSpaceOnUse',x:0,y:0,width:600,height:52});
  mask.append(svgNode('rect',{x:0,y:0,width:600,height:52,fill:'url(#hourly-fade)'}));
  const defs = svgNode('defs');defs.append(gradient,fade,mask);graph.append(defs);
  for (const segment of segments) {
    if (segment.length < 2) continue;
    const d = segment.map((p,i)=>`${i?'L':'M'}${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(' ');
    graph.append(svgNode('path',{d:`${d} L${segment.at(-1).x},52 L${segment[0].x},52 Z`,class:'hourly-area',fill:'url(#hourly-temperature)',mask:'url(#hourly-area-mask)'}));
    graph.append(svgNode('path',{d,class:'hourly-line',stroke:'url(#hourly-temperature)'}));
  }
  points.filter(Boolean).forEach(p=>graph.append(svgNode('circle',{cx:p.x,cy:p.y,r:2.2,class:'hourly-point'})));
  const list = node('ol','hourly-grid');
  rows.forEach((row,index)=>{
    const temperature = isNumber(row.temperature) ? `${Math.round(row.temperature)}°` : '—';
    const chance = isNumber(row.probability) ? `${Math.round(row.probability)}%` : '—';
    const description = `${row.label}、${weatherLabel(row.code)}、${isNumber(row.temperature)?`${Math.round(row.temperature)}度`:'気温未取得'}、降水確率${isNumber(row.probability)?chance:'未取得'}`;
    const item = node('li','hourly-item');item.dataset.timestamp=row.timestamp;item.title=description;item.setAttribute('aria-label',description);
    const at = node('time','hourly-time number',row.label);at.dateTime=new Date(row.timestamp).toISOString();
    const symbol = node('span','hourly-icon');symbol.append(makeWeatherIcon(row.code,row.isDay));
    const degrees = node('div','hourly-temperature');
    const label = node('span','number',temperature);label.style.top=`${(points[index]?.y ?? 35)-26}px`;degrees.append(label);
    const probability = node('span','hourly-rain number',chance);
    probability.classList.toggle('rain-likely',row.probability>=40);
    const bar = node('span','hourly-rain-bar');bar.setAttribute('aria-hidden','true');
    if (isNumber(row.probability)) {const fill = node('i','');fill.style.width=`${row.probability}%`;bar.append(fill);}
    probability.append(bar);item.append(at,symbol,degrees,probability);list.append(item);
  });
  container.append(graph,list);
  return true;
}
