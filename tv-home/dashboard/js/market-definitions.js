// Explicit, reviewed contract identities. Do not match by substring or silently
// replace an index with an ETF/another contract. Prices are passed through.
export const MARKETS = Object.freeze([
  {symbol:'SP500',coin:'xyz:SP500',name:'S&P 500',digits:1,unit:'指数ポイント'},
  {symbol:'BTC',coin:'BTC',name:'Bitcoin',digits:0,unit:'USDT'},
  {symbol:'HYPE',coin:'HYPE',name:'Hyperliquid',digits:3,unit:'USDC'},
  {symbol:'JP225',coin:'xyz:JP225',name:'日経225',digits:0,unit:'指数ポイント'},
  {symbol:'SOXL',coin:'xyz:SOXL',name:'半導体ブル3倍',digits:3,unit:'USD'},
  {symbol:'XYZ100',coin:'xyz:XYZ100',name:'米国テック100',digits:1,unit:'指数ポイント'},
  {symbol:'JPY',coin:'xyz:JPY',name:'米ドル / 円',digits:3,unit:'円 / 1米ドル'},
  {symbol:'DRAM',coin:'xyz:DRAM',name:'DRAM · trade.xyz',digits:3,unit:'契約価格'},
  {symbol:'GOLD',coin:'xyz:GOLD',name:'金',digits:2,unit:'USD / トロイオンス'},
  {symbol:'CL',coin:'xyz:CL',name:'WTI原油',digits:3,unit:'USD / バレル'},
  {symbol:'30Y',coin:'para:30Y',name:'米30年金利',digits:3,unit:'契約価格'},
  {symbol:'10Y',coin:'para:10Y',name:'米10年金利',digits:3,unit:'契約価格'},
].map(m=>Object.freeze({...m,dex:m.coin.includes(':')?m.coin.split(':')[0]:'',
  icon:`assets/markets/${m.coin.replace(':','-')}.svg`,collateral:'USDC'})));
export const MARKET_BY_SYMBOL = new Map(MARKETS.map(m=>[m.symbol,m]));
export const MARKET_BY_COIN = new Map(MARKETS.map(m=>[m.coin,m]));
export const marketCoins = (dex, cryptoSource='hyperliquid') => MARKETS.filter(m=>m.dex===dex && (dex!=='' || cryptoSource==='hyperliquid')).map(m=>m.coin);
export const CHART_RANGES = Object.freeze({
  '1d':{label:'24H',duration:86400000,interval:'15m',intervalMs:900000},
});
