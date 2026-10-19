import { fetchJSON } from './data.js';
import { MARKETS, MARKET_BY_COIN, CHART_RANGES, marketCoins } from './market-definitions.js';

export const COINS = Object.freeze(Object.fromEntries(MARKETS.map(m=>[m.coin,m.symbol])));
const positive = value => (typeof value === 'string' && value.trim() || typeof value === 'number') && Number.isFinite(Number(value)) && Number(value) > 0 ? Number(value) : null;
const info = (body,fetcher) => fetchJSON('https://api.hyperliquid.xyz/info', {
  method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),...(fetcher?{fetcher}:{}),
});

// Native and HIP-3 mark prices retain the exact contract identity. No FX,
// index/ETF scaling, yield conversion, or stablecoin/USD conversion is applied.
export function normalizeAsset(coin,ctx,receivedAt=Date.now()) {
  const market=MARKET_BY_COIN.get(coin),price=positive(ctx?.markPx),previous=positive(ctx?.prevDayPx);
  if(!market || price===null || !Number.isFinite(receivedAt))return null;
  return {symbol:market.symbol,coin,price,previous,change:previous===null?null:(price/previous-1)*100,
    timestamp:receivedAt,source:'Hyperliquid',venue:market.dex||'native',instrument:'perpetual',
    currency:market.unit,collateral:'USDC',
    note:`${coin} / 無期限先物 / ${market.unit} / USDC証拠金 / マーク価格 / 24時間変化率 / 時刻は受信時刻`};
}

export async function getMarketSnapshot(dex='',{fetcher,now=Date.now,coins=marketCoins(dex)}={}) {
  const data=await info({type:'metaAndAssetCtxs',...(dex?{dex}:{})},fetcher);
  if(!Array.isArray(data?.[0]?.universe) || !Array.isArray(data?.[1]))throw new Error('Hyperliquidの価格データがありません');
  if(data[0].collateralToken!==undefined && data[0].collateralToken!==0)throw new Error('証拠金通貨の変更を確認してください');
  const fetchedAt=now(),quotes=[],activeCoins=[],unavailable=[];
  for(const coin of coins){
    if(MARKET_BY_COIN.get(coin)?.dex!==dex)continue;
    const index=data[0].universe.findIndex(asset=>asset.name===coin);
    if(index<0 || data[0].universe[index].isDelisted){unavailable.push({coin,symbol:COINS[coin],reason:index<0?'not-listed':'delisted'});continue;}
    activeCoins.push(coin);
    const q=normalizeAsset(coin,data[1][index],fetchedAt);
    if(q)quotes.push(q);else unavailable.push({coin,symbol:COINS[coin],reason:'price-missing'});
  }
  return {dex,quotes,activeCoins,unavailable,fetchedAt};
}

// Retained for callers needing just the two native coins.
export async function getHyperliquid(options={}) {
  const result=await getMarketSnapshot('',options);
  if(result.unavailable.length)throw new Error('Hyperliquidの価格データがありません');
  return result.quotes;
}

export function normalizeCandles(data,{coin,range='1d',end=Date.now()}={}) {
  const spec=CHART_RANGES[range];
  if(!spec || !MARKET_BY_COIN.has(coin) || !Array.isArray(data) || !Number.isFinite(end))throw new Error('チャートデータがありません');
  const start=end-spec.duration,unique=new Map();
  for(const row of data){
    if(!row || typeof row!=='object')continue;
    const open=positive(row.o),value=positive(row.c);
    if(row.s!==coin || row.i!==spec.interval || !Number.isFinite(row.t) || !Number.isFinite(row.T) || row.T<row.t || row.T-row.t>spec.intervalMs || row.t>end || row.T<start || open===null || value===null)continue;
    unique.set(row.t,{time:Math.min(row.T,end),start:row.t,value,open});
  }
  const points=[...unique.values()].sort((a,b)=>a.start-b.start);
  if(points.length<2)throw new Error('表示できる価格履歴がありません');
  return {coin,range,start,end,intervalMs:spec.intervalMs,points,baseline:points[0].open,lastTime:points.at(-1).time};
}
export async function getMarketCandles(coin,range='1d',{fetcher,now=Date.now}={}) {
  const spec=CHART_RANGES[range];if(!spec || !MARKET_BY_COIN.has(coin))throw new Error('不明な銘柄です');
  const end=now();
  const data=await info({type:'candleSnapshot',req:{coin,interval:spec.interval,startTime:end-spec.duration,endTime:end}},fetcher);
  return normalizeCandles(data,{coin,range,end});
}

// One public connection. Listing metadata must be checked before adding HIP-3
// subscriptions. Frames for inactive, unrequested, and unknown coins are ignored.
export class HyperliquidStream {
  constructor({onQuotes,onStatus=()=>{},coins=['BTC','HYPE'],WebSocketClass=globalThis.WebSocket,now=Date.now}) {
    Object.assign(this,{onQuotes,onStatus,WebSocketClass,now});
    this.coins=new Set(coins.filter(c=>MARKET_BY_COIN.has(c)));
    this.stopped=true;this.attempt=0;this.pending=new Map();this.seen=new Map();
  }
  setCoins(coins) {
    const next=new Set(coins.filter(c=>MARKET_BY_COIN.has(c))),socket=this.socket;
    for(const coin of this.coins)if(!next.has(coin)){
      this.seen.delete(coin);this.pending.delete(COINS[coin]);
      if(socket?.readyState===1)this.sendSubscription('unsubscribe',coin);
    }
    const added=[...next].filter(c=>!this.coins.has(c));this.coins=next;
    if(!next.size){clearTimeout(this.retryTimer);this.retryTimer=null;this.closeSocket();return;}
    if(socket?.readyState===1)for(const coin of added)this.sendSubscription('subscribe',coin);
    if(!this.stopped && !socket && next.size && !this.retryTimer)this.connect();
  }
  sendSubscription(method,coin){try{this.socket?.send(JSON.stringify({method,subscription:{type:'activeAssetCtx',coin}}));}catch{this.disconnectAndRetry();}}
  start(){if(!this.stopped)return;this.stopped=false;if(this.coins.size)this.connect();}
  connect(){
    if(this.stopped || !this.coins.size)return;
    this.onStatus('connecting');this.seen.clear();this.pending.clear();const openedAt=this.now();
    let socket;try{socket=new this.WebSocketClass('wss://api.hyperliquid.xyz/ws');}catch{this.retry();return;}
    this.socket=socket;
    socket.onopen=()=>{if(this.stopped || this.socket!==socket)return;for(const coin of this.coins)this.sendSubscription('subscribe',coin);};
    socket.onmessage=event=>{
      if(this.stopped || this.socket!==socket)return;
      try{
        const message=JSON.parse(event.data);
        if(message.channel!=='activeAssetCtx' || !this.coins.has(message.data?.coin))return;
        const quote=normalizeAsset(message.data.coin,message.data.ctx,this.now());if(!quote)return;
        this.pending.set(quote.symbol,quote);this.seen.set(quote.coin,this.now());this.attempt=0;
        if(!this.flushTimer)this.flushTimer=setTimeout(()=>{
          this.flushTimer=null;if(this.stopped || this.socket!==socket)return;
          const rows=[...this.pending.values()];this.pending.clear();if(rows.length)this.onQuotes(rows);
          this.onStatus(this.healthy()?'live':'partial');
        },1000);
      }catch{/* Ignore malformed/unrelated public feed messages. */}
    };
    socket.onerror=()=>{if(this.socket===socket)this.disconnectAndRetry();};
    socket.onclose=()=>{if(this.socket===socket)this.disconnectAndRetry();};
    this.heartbeat=setInterval(()=>{
      if(this.socket!==socket)return;
      // A quiet instrument must not tear down fresh feeds for other markets.
      const newest=Math.max(openedAt,...this.seen.values());
      if(this.now()-newest>45000){this.disconnectAndRetry();return;}
      if(socket.readyState===1){try{socket.send(JSON.stringify({method:'ping'}));}catch{this.disconnectAndRetry();}}
    },15000);
  }
  healthy(coins=[...this.coins]){return coins.length>0 && coins.every(c=>this.seen.has(c) && this.now()-this.seen.get(c)<20000);}
  disconnectAndRetry(){this.closeSocket();if(!this.stopped)this.retry();}
  retry(){if(this.stopped || this.retryTimer)return;this.onStatus('fallback');this.retryTimer=setTimeout(()=>{this.retryTimer=null;this.connect();},Math.min(1000*2**this.attempt++,30000));}
  closeSocket(){
    clearInterval(this.heartbeat);clearTimeout(this.flushTimer);this.flushTimer=null;this.pending.clear();this.seen.clear();
    const socket=this.socket;this.socket=null;if(socket){socket.onopen=socket.onmessage=socket.onclose=socket.onerror=null;try{socket.close();}catch{}}
  }
  stop(){this.stopped=true;clearTimeout(this.retryTimer);this.retryTimer=null;this.closeSocket();}
}
