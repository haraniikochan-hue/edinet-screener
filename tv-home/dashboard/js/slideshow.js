import { safeUrl } from './data.js';
import { themeFor } from './daypart.js';
import { looksLike } from './frost.js';
export const SAMPLE_PHOTOS = [{
  url:'assets/nyc-luca-bravo.jpg', title:'ニューヨーク · ミッドタウン', photographer:'Luca Bravo',
  profile:'https://unsplash.com/@lucabravo?utm_source=tv_home&utm_medium=referral', source:'CC0 / Wikimedia Commons',
  sourceUrl:'https://commons.wikimedia.org/wiki/File:City_of_lights_(Unsplash).jpg', sample:true, period:'night',
}];
// Each photo carries its time of day (js/feeds.js); the theme follows the photo on screen (onTheme), so the
// glass and the text always match the picture behind them. A photo whose brightness contradicts its time
// of day (a night shot found by a daytime search) is skipped.
export class Slideshow {
  constructor({layers,caption,title,onError,frost,onFrost,onTheme}) { this.layers=layers; this.caption=caption; this.title=title; this.onError=onError; this.frost=frost; this.onFrost=onFrost; this.onTheme=onTheme; this.photos=[]; this.index=-1; this.layer=0; this.version=0; this.skipped=new Set(); }
  setPhotos(photos) {
    const valid = photos.filter(p => safeUrl(p.url,{relative:true}) && typeof p.photographer === 'string');
    if (!valid.length) return;
    // Settings saves and start-up hand over the same list again; reloading it would cross-fade
    // the photo into itself and repaint the TV's frosted copy for nothing.
    const same = valid.length===this.photos.length && valid.every((photo,i) => photo.url===this.photos[i].url);
    if (same && (this.index>=0 || this.loading)) return;
    this.version++; this.loading=false; this.photos=valid; this.index=-1; this.skipped=new Set(); void this.next();
  }
  async next() {
    if (this.loading || !this.photos.length || (this.photos.length===1 && this.index===0)) return;
    this.loading=true; const version=this.version;
    let next=(this.index+1)%this.photos.length;
    // Photos found out of place are passed over for good, unless nothing else is left.
    for (let tries=0; tries<this.photos.length && this.skipped.has(next); tries++) next=(next+1)%this.photos.length;
    const photo=this.photos[next], period=photo.period || 'night', theme=themeFor(period);
    let retry=false;
    try {
      const load=cors => new Promise((resolve,reject) => {
        const img=new Image(); if(cors)img.crossOrigin='anonymous'; const timeout=setTimeout(() => reject(new Error('写真の読み込みがタイムアウトしました')),15000);
        img.onload=() => {clearTimeout(timeout); resolve(img);}; img.onerror=() => {clearTimeout(timeout); reject(new Error('写真を読み込めませんでした'));}; img.src=photo.url;
      });
      // Read with CORS (Unsplash allows it) so the frosted copy can measure the photo behind the text;
      // a host that refuses still shows its photo, with default shading.
      const img=await load(true).catch(() => load(false));
      if (version!==this.version) return;
      const layer=1-this.layer;
      // The frosted copy is painted before the swap so both cross-fade together.
      const frosted=this.frost?.paint(layer,img,theme);
      if (frosted && !looksLike(period,this.frost.scene(layer)) && this.skipped.size<this.photos.length-1) {
        this.skipped.add(next); this.index=next; retry=true; return;
      }
      this.layers[layer].style.backgroundImage=`url(${JSON.stringify(photo.url)})`;
      this.layers[layer].classList.add('is-active'); this.layers[this.layer].classList.remove('is-active'); this.layer=layer; this.index=next;
      if (frosted) this.frost.activate(layer);
      this.onFrost?.(Boolean(frosted));
      this.onTheme?.(theme);
      this.title.textContent=photo.title || 'ニューヨーク';
      this.caption.replaceChildren();
      const addLink=(text,url) => { const a=document.createElement('a');a.textContent=text; const safe=safeUrl(url);if(safe){a.href=safe;a.target='_blank';a.rel='noopener noreferrer';}this.caption.append(a); };
      this.caption.append('Photo: '); addLink(photo.photographer,photo.profile); this.caption.append(' / '); addLink(photo.source || 'Unsplash',photo.sourceUrl);
      this.caption.append(` · ${next+1}/${this.photos.length}${photo.sample ? ' · 同梱写真' : ''}`);
    } catch(error) {if(version===this.version)this.onError?.(error);} finally {if(version===this.version){this.loading=false; if(retry)void this.next();}}
  }
  schedule(seconds) { clearInterval(this.timer);this.timer=setInterval(() => {if(!document.hidden)void this.next();},seconds*1000); }
}
