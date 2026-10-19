import { readStorage, writeStorage, fetchJSON } from './data.js';
const TOKEN_KEY = 'tv-spotify-session';
const AUTH_KEY = 'tv-spotify-auth';
// The TV app keeps the login across restarts (a private device); a browser keeps it for the tab only.
const store = () => location.hostname === 'appassets.androidplatform.net' ? localStorage : sessionStorage;
const base64url = bytes => btoa(String.fromCharCode(...bytes)).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
export const redirectUri = () => `${location.origin}${location.pathname}`;
export function connected() { return Boolean(readStorage(store(),TOKEN_KEY,null)?.access_token); }
export function disconnect() { store().removeItem(TOKEN_KEY); store().removeItem(AUTH_KEY); }
export async function connect(clientId) {
  if (!/^[a-f0-9]{32}$/.test(clientId)) throw new Error('設定にSpotifyのClient IDを入力してください');
  if (!crypto.subtle || (location.protocol !== 'https:' && !['127.0.0.1','[::1]'].includes(location.hostname))) throw new Error('Spotify連携はHTTPS、または http://127.0.0.1 で開いてください');
  const verifier = base64url(crypto.getRandomValues(new Uint8Array(48)));
  const state = base64url(crypto.getRandomValues(new Uint8Array(24)));
  const challenge = base64url(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(verifier))));
  if (!writeStorage(store(),AUTH_KEY,{verifier,state,clientId,redirectUri:redirectUri(),createdAt:Date.now()})) throw new Error('ブラウザのセッション保存を有効にしてください');
  const params = new URLSearchParams({client_id:clientId,response_type:'code',redirect_uri:redirectUri(),scope:'user-read-currently-playing',code_challenge_method:'S256',code_challenge:challenge,state});
  location.assign(`https://accounts.spotify.com/authorize?${params}`);
}
async function exchange(body) {
  return fetchJSON('https://accounts.spotify.com/api/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(body)});
}
export async function completeCallback() {
  const params = new URLSearchParams(location.search);
  if (!params.has('code') && !params.has('error')) return false;
  const auth = readStorage(store(),AUTH_KEY,null);
  const code = params.get('code'), state = params.get('state'), error = params.get('error');
  for (const key of ['code','state','error','error_description']) params.delete(key);
  history.replaceState({},'',`${location.pathname}${params.size ? `?${params}` : ''}${location.hash}`);
  store().removeItem(AUTH_KEY);
  if (!auth || state !== auth.state || Date.now() - auth.createdAt > 600000) throw new Error('Spotifyの連携を設定からやり直してください');
  if (error) throw new Error('Spotifyの連携はキャンセルされました');
  const token = await exchange({client_id:auth.clientId,grant_type:'authorization_code',code,redirect_uri:auth.redirectUri,code_verifier:auth.verifier});
  if (!token.access_token || !token.expires_in) throw new Error('Spotifyの認証情報を取得できません');
  if (!writeStorage(store(),TOKEN_KEY,{...token,clientId:auth.clientId,expiresAt:Date.now()+token.expires_in*1000})) throw new Error('認証情報をセッションに保存できません');
  return true;
}
let refreshPromise;
async function getAccessToken() {
  let token = readStorage(store(),TOKEN_KEY,null);
  if (!token) return null;
  if (Date.now() > token.expiresAt - 60000) {
    if (!refreshPromise) refreshPromise = (async () => {
      try {
        if (!token.refresh_token) throw new Error('再連携が必要です');
        const result = await exchange({grant_type:'refresh_token',refresh_token:token.refresh_token,client_id:token.clientId});
        if (!result.access_token || !result.expires_in) throw new Error('再連携が必要です');
        token = {...token,...result,expiresAt:Date.now()+result.expires_in*1000};
        writeStorage(store(),TOKEN_KEY,token); return token;
      } catch(error) { if ([400,401].includes(error.status)) disconnect(); throw error; }
      finally { refreshPromise = null; }
    })();
    token = await refreshPromise;
  }
  return token.access_token;
}
export async function currentlyPlaying() {
  const token = await getAccessToken();
  if (!token) return {connected:false};
  const response = await fetch('https://api.spotify.com/v1/me/player/currently-playing',{headers:{Authorization:`Bearer ${token}`},signal:AbortSignal.timeout(12000)});
  if (response.status === 204) return {connected:true,item:null};
  if (response.status === 401) { disconnect(); throw new Error('Spotifyを再連携してください'); }
  if (response.status === 403) throw new Error('Spotifyアプリの利用権限を確認してください');
  if (response.status === 429) throw new Error('Spotify取得制限・しばらく待って再試行');
  if (!response.ok) throw new Error('Spotifyに接続できません');
  return {connected:true,...await response.json(),fetchedAt:Date.now()};
}
