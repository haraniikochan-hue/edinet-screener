// Preserve the observation times: gaps and a quiet last trade stay visible.
export function chartGeometry(series, width=160, height=52) {
  if(!series || !Array.isArray(series.points) || series.points.length<2 || !Number.isFinite(series.baseline) || !(series.end>series.start))return null;
  const points=series.points.filter(p=>Number.isFinite(p.time) && Number.isFinite(p.value) && p.time>=series.start && p.time<=series.end);
  if(points.length<2)return null;
  const values=[series.baseline,...points.map(p=>p.value)],lo=Math.min(...values),hi=Math.max(...values),span=hi-lo;
  const x=t=>4+(t-series.start)/(series.end-series.start)*(width-8);
  const y=v=>span?height-7-(v-lo)/span*(height-14):height/2;
  const baseline=y(series.baseline),segments=[];
  for(const p of points){
    const prev=segments.at(-1)?.at(-1);
    if(!prev || p.time-prev.time>series.intervalMs*1.6)segments.push([]);
    segments.at(-1).push({...p,x:x(p.time),y:y(p.value)});
  }
  const n=v=>v.toFixed(2);
  const paths=segments.map(segment=>({
    line:segment.map((p,i)=>`${i?'L':'M'}${n(p.x)},${n(p.y)}`).join(' '),
    area:`M${n(segment[0].x)},${n(baseline)} ${segment.map(p=>`L${n(p.x)},${n(p.y)}`).join(' ')} L${n(segment.at(-1).x)},${n(baseline)} Z`,
    points:segment,
  }));
  return {width,height,baseline,paths,last:segments.at(-1).at(-1)};
}

const svgNode=(tag,attrs={})=>{const node=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))node.setAttribute(k,String(v));return node;};
export function drawMarketChart(container,series,id,label) {
  const g=chartGeometry(series);if(!g)return false;
  const svg=svgNode('svg',{viewBox:`0 0 ${g.width} ${g.height}`,role:'img','aria-label':label,preserveAspectRatio:'none'});
  const title=svgNode('title');title.textContent=label;svg.append(title);
  const defs=svgNode('defs');
  for(const side of ['up','down']){
    const clip=svgNode('clipPath',{id:`chart-${id}-${side}`});
    clip.append(svgNode('rect',{x:0,y:side==='up'?0:g.baseline,width:g.width,height:side==='up'?g.baseline:g.height-g.baseline}));
    // Each side's fill fades from the outer edge to nothing at the baseline.
    const fill=svgNode('linearGradient',{id:`chart-${id}-${side}-fill`,class:`chart-fill chart-${side}`,gradientUnits:'userSpaceOnUse',x1:0,x2:0,y1:side==='up'?0:g.height,y2:g.baseline});
    fill.append(svgNode('stop',{offset:0,'stop-opacity':.34}),svgNode('stop',{offset:1,'stop-opacity':0}));
    defs.append(clip,fill);
  }
  svg.append(defs,svgNode('line',{x1:0,x2:g.width,y1:g.baseline,y2:g.baseline,class:'chart-baseline'}));
  for(const side of ['up','down']){
    const group=svgNode('g',{'clip-path':`url(#chart-${id}-${side})`,class:`chart-${side}`});
    for(const path of g.paths){
      group.append(svgNode('path',{d:path.area,class:'chart-area',fill:`url(#chart-${id}-${side}-fill)`}),svgNode('path',{d:path.line,class:'chart-line'}));
      if(path.points.length===1)group.append(svgNode('circle',{cx:path.points[0].x,cy:path.points[0].y,r:1.4}));
    }
    svg.append(group);
  }
  const lastSide=g.last.value>=series.baseline?'chart-up':'chart-down';
  svg.append(svgNode('circle',{cx:g.last.x,cy:g.last.y,r:5,class:`chart-halo ${lastSide}`}),svgNode('circle',{cx:g.last.x,cy:g.last.y,r:2.4,class:lastSide}));
  container.replaceChildren(svg);return true;
}
