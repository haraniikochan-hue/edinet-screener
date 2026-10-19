// Preserve the observation times: gaps and a quiet last trade stay visible.
// `frame` insets the plot inside the box and may fix its value range (lo–hi), as the detail chart does.
export function chartGeometry(series, width=160, height=52, frame={}) {
  if(!series || !Array.isArray(series.points) || series.points.length<2 || !Number.isFinite(series.baseline) || !(series.end>series.start))return null;
  const points=series.points.filter(p=>Number.isFinite(p.time) && Number.isFinite(p.value) && p.time>=series.start && p.time<=series.end);
  if(points.length<2)return null;
  const {left=4,right=4,top=7,bottom=7}=frame,values=[series.baseline,...points.map(p=>p.value)];
  const lo=Number.isFinite(frame.lo)?frame.lo:Math.min(...values),hi=Number.isFinite(frame.hi)?frame.hi:Math.max(...values),span=hi-lo;
  const x=t=>left+(t-series.start)/(series.end-series.start)*(width-left-right);
  const y=v=>span?height-bottom-(v-lo)/span*(height-top-bottom):(top+height-bottom)/2;
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
export function drawMarketChart(container,series,id,label,{width=160,height=52}={}) {
  const g=chartGeometry(series,width,height);if(!g)return false;
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

// Round price levels for the detail chart's scale: about `count` ticks covering lo–hi, and the
// decimals they need.
export function niceTicks(lo, hi, count=4) {
  if(!(hi>lo)){const pad=Math.abs(lo)*.01||1;lo-=pad;hi+=pad;}
  const raw=(hi-lo)/count,magnitude=10**Math.floor(Math.log10(raw)),norm=raw/magnitude;
  const step=(norm<1.5?1:norm<2.25?2:norm<3.5?2.5:norm<7.5?5:10)*magnitude;
  const ticks=[];
  for(let v=Math.ceil(lo/step-1e-9)*step;v<=hi+step*1e-9;v+=step)ticks.push(+v.toPrecision(12));
  return {step,ticks,decimals:(String(+step.toPrecision(6)).split('.')[1]||'').length};
}

// Time marks in Japan time for a chart from start to end: hours within a day, then days, weeks and
// months, at most about `max` of them. A day mark replaces midnight, and January shows its year.
const HOUR=3600000,DAY=24*HOUR,JST=9*HOUR;
const STEPS=[[1,'h'],[2,'h'],[3,'h'],[4,'h'],[6,'h'],[12,'h'],[1,'d'],[2,'d'],[7,'d'],[14,'d'],[1,'M'],[2,'M'],[3,'M'],[6,'M']];
export function timeTicks(start, end, max=6) {
  const unitMs={h:HOUR,d:DAY,M:30.44*DAY};
  const [n,unit]=STEPS.find(([n,u])=>(end-start)/(n*unitMs[u])<=max)||STEPS.at(-1),ticks=[];
  if(unit==='M'){
    const first=new Date(start+JST);
    for(let y=first.getUTCFullYear(),m=first.getUTCMonth()+1;;m++){
      if(m>11){y++;m-=12;}
      const time=Date.UTC(y,m,1)-JST;if(time>end)break;
      if(m%n===0)ticks.push({time,label:m===0?`${y}年`:`${m+1}月`});
    }
  }else{
    const step=n*unitMs[unit];
    for(let time=Math.ceil((start+JST)/step)*step-JST;time<=end;time+=step){
      const d=new Date(time+JST);
      ticks.push({time,label:unit==='h' && d.getUTCHours()?`${d.getUTCHours()}:00`:`${d.getUTCMonth()+1}/${d.getUTCDate()}`});
    }
  }
  return ticks;
}

// The detail sheet's chart: a price scale on the right, time marks below and, while it is being
// scrubbed, a cursor with that moment's price, change from the period's first open, and time.
// Sized to its container in CSS pixels. Returns {length, scrub(index|null)} or null without data.
export function drawDetailChart(container, series, {label, price, change, when}) {
  const width=container.clientWidth,height=container.clientHeight;
  const points=series?.points?.filter(p=>Number.isFinite(p.value))||[];
  if(points.length<2 || !width || !height)return null;
  const values=[series.baseline,...points.map(p=>p.value)],lo=Math.min(...values),hi=Math.max(...values);
  const pad=(hi-lo||Math.abs(hi)*.01||1)*.1,scale=niceTicks(lo-pad,hi+pad,5);
  const frame={left:0,right:84,top:60,bottom:36,lo:lo-pad,hi:hi+pad};
  const g=chartGeometry(series,width,height,frame);if(!g)return null;
  const plotRight=width-frame.right,y=v=>height-frame.bottom-(v-frame.lo)/(frame.hi-frame.lo)*(height-frame.top-frame.bottom);
  const svg=svgNode('svg',{width,height,viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':label});
  const title=svgNode('title');title.textContent=label;svg.append(title);
  const marks=document.createElement('div');marks.className='detail-marks';marks.setAttribute('aria-hidden','true');
  const mark=(className,text,style)=>{const node=document.createElement('span');node.className=className;node.textContent=text;Object.assign(node.style,style);marks.append(node);};
  for(const tick of scale.ticks){
    if(tick<frame.lo || tick>frame.hi)continue;
    svg.append(svgNode('line',{x1:0,x2:plotRight,y1:y(tick),y2:y(tick),class:'detail-grid'}));
    mark('detail-price-mark',price(tick,scale.decimals),{top:`${y(tick)}px`,left:`${plotRight+12}px`});
  }
  for(const tick of timeTicks(series.start,series.end)){
    const x=frame.left+(tick.time-series.start)/(series.end-series.start)*(plotRight-frame.left);
    if(x<28 || x>plotRight-28)continue;
    svg.append(svgNode('line',{x1:x,x2:x,y1:height-frame.bottom,y2:height-frame.bottom+5,class:'detail-tick'}));
    mark('detail-time-mark',tick.label,{left:`${x}px`,top:`${height-frame.bottom+10}px`});
  }
  const defs=svgNode('defs');
  for(const side of ['up','down']){
    const clip=svgNode('clipPath',{id:`detail-${side}`});
    clip.append(svgNode('rect',{x:0,y:side==='up'?0:g.baseline,width,height:side==='up'?g.baseline:height-g.baseline}));
    const fill=svgNode('linearGradient',{id:`detail-${side}-fill`,class:`chart-fill chart-${side}`,gradientUnits:'userSpaceOnUse',x1:0,x2:0,y1:side==='up'?frame.top:height-frame.bottom,y2:g.baseline});
    fill.append(svgNode('stop',{offset:0,'stop-opacity':.3}),svgNode('stop',{offset:1,'stop-opacity':0}));
    defs.append(clip,fill);
  }
  svg.append(defs,svgNode('line',{x1:0,x2:plotRight,y1:g.baseline,y2:g.baseline,class:'chart-baseline'}));
  for(const side of ['up','down']){
    const group=svgNode('g',{'clip-path':`url(#detail-${side})`,class:`chart-${side}`});
    for(const path of g.paths)group.append(svgNode('path',{d:path.area,class:'chart-area',fill:`url(#detail-${side}-fill)`}),svgNode('path',{d:path.line,class:'chart-line'}));
    svg.append(group);
  }
  const side=v=>v>=series.baseline?'chart-up':'chart-down';
  const last=svgNode('g');last.append(svgNode('circle',{cx:g.last.x,cy:g.last.y,r:7,class:`chart-halo ${side(g.last.value)}`}),svgNode('circle',{cx:g.last.x,cy:g.last.y,r:3.6,class:side(g.last.value)}));
  const cursor=svgNode('g',{class:'detail-cursor',visibility:'hidden'});
  const cursorLine=svgNode('line',{x1:0,x2:0,y1:frame.top-8,y2:height-frame.bottom}),cursorDot=svgNode('circle',{r:6});
  cursor.append(cursorLine,cursorDot);svg.append(last,cursor);
  const readout=document.createElement('div');readout.className='detail-readout';readout.hidden=true;
  const [readPrice,readChange,readTime]=['detail-read-price','detail-read-change','detail-read-time'].map(className=>{const node=document.createElement('span');node.className=className;readout.append(node);return node;});
  container.replaceChildren(svg,marks,readout);
  const flat=g.paths.flatMap(path=>path.points);
  return {
    length:flat.length,
    scrub(index){
      const p=index===null || index===undefined ? null : flat[Math.max(0,Math.min(flat.length-1,index))];
      cursor.setAttribute('visibility',p?'visible':'hidden');last.setAttribute('visibility',p?'hidden':'visible');readout.hidden=!p;
      if(!p)return null;
      cursorLine.setAttribute('x1',p.x);cursorLine.setAttribute('x2',p.x);
      cursorDot.setAttribute('cx',p.x);cursorDot.setAttribute('cy',p.y);cursorDot.setAttribute('class',side(p.value));
      const delta=(p.value-series.baseline)/series.baseline*100;
      readPrice.textContent=price(p.value);readChange.textContent=change(delta);readChange.className=`detail-read-change ${delta>0?'up':delta<0?'down':'neutral'}`;readTime.textContent=when(p);
      readout.style.left=`${Math.max(0,Math.min(plotRight-readout.offsetWidth,p.x-readout.offsetWidth/2))}px`;
      return `${when(p)} ${price(p.value)} ${change(delta)}`;
    },
    nearest(x){let best=0;flat.forEach((p,i)=>{if(Math.abs(p.x-x)<Math.abs(flat[best].x-x))best=i;});return best;},
  };
}
