// Use the official widget iframe URL, keeping all third-party JavaScript on its
// own origin. Never run vendor scripts in the same origin as Spotify tokens or
// the future Android bridge. Exact index symbols are intentionally not CFDs.
export const TV_SYMBOLS = [
  ['SP:SPX','S&P 500'],['CRYPTO:BTCUSD','BTC / USD'],['CRYPTO:HYPEUSD','HYPE / USD'],['TVC:NI225','日経225'],
  ['AMEX:SOXL','SOXL ETF（参考）'],['NASDAQ:NDX','NASDAQ 100'],['FX_IDC:USDJPY','USD / JPY'],['AMEX:DRAM','DRAM ETF（参考）'],
  ['TVC:GOLD','金 CFD'],['TVC:USOIL','WTI原油 CFD'],['TVC:US30Y','米30年債利回り'],['TVC:US10Y','米10年債利回り'],
];
export function mountTradingView(container) {
  const grid=document.createElement('div');grid.className='tradingview-grid';
  for(let column=0;column<2;column++){
    const settings={width:'100%',height:'100%',colorTheme:'dark',backgroundColor:'#0a0d14',isTransparent:false,showSymbolLogo:false,locale:'ja',
      symbolsGroups:[{name:column===0?'マーケット':'ウォッチリスト',symbols:TV_SYMBOLS.filter((_,index)=>index%2===column).map(([name,displayName])=>({name,displayName}))}],
      'page-uri':`${location.origin}${location.pathname}`};
    const iframe=document.createElement('iframe');
    iframe.src=`https://www.tradingview-widget.com/embed-widget/market-quotes/?locale=ja#${encodeURIComponent(JSON.stringify(settings))}`;
    iframe.title=`TradingView公式マーケット ${column+1}/2`;
    iframe.setAttribute('sandbox','allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox');
    iframe.tabIndex=-1;iframe.setAttribute('scrolling','no');grid.append(iframe);
  }
  const credit=document.createElement('a');credit.className='tradingview-credit';credit.href=`https://www.tradingview.com/markets/?utm_source=${encodeURIComponent(location.hostname)}&utm_medium=widget&utm_campaign=market-quotes`;credit.target='_blank';credit.rel='noopener noreferrer';credit.textContent='Track all markets on TradingView';
  container.replaceChildren(grid,credit);
}
