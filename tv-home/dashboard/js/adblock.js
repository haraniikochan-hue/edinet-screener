// Ad blocking for the whole TV is done by Android's Private DNS (DNS over TLS),
// e.g. AdGuard DNS, which answers 0.0.0.0 for ad and tracker domains. The web
// page cannot change it; it can only check whether ad servers are reachable.
// A Phase 3 launcher may expose window.Android.getPrivateDns/setPrivateDns.
export const DEFAULT_ADBLOCK_DNS = 'dns.adguard-dns.com';
// Ad-serving hosts that DNS blocklists cover, and a host they never block.
export const AD_PROBES = Object.freeze(['https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js','https://securepubads.g.doubleclick.net/tag/js/gpt.js']);
export const CONTROL_PROBE = 'https://www.gstatic.com/generate_204';

export const validDnsHost = host => typeof host === 'string' && host.length <= 253 && /^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{0,61}[a-z0-9]$/i.test(host);

// Only reachability is tested: no-cors, no cookies, and the response is never read or run.
export async function reachable(url, { fetcher = fetch, timeout = 6000 } = {}) {
  try { await fetcher(url, { mode:'no-cors', cache:'no-store', credentials:'omit', redirect:'follow', signal:AbortSignal.timeout(timeout) }); return true; }
  catch { return false; }
}

// active: every ad host is blocked; partial: some are; inactive: none; unknown: offline.
export async function adBlockStatus(options = {}) {
  const [control, ...ads] = await Promise.all([CONTROL_PROBE, ...AD_PROBES].map(url => reachable(url, options)));
  if (!control) return 'unknown';
  const blocked = ads.filter(ok => !ok).length;
  return blocked === ads.length ? 'active' : blocked ? 'partial' : 'inactive';
}

// Reads the optional launcher bridge; anything malformed counts as unavailable.
export function nativePrivateDns(bridge = globalThis.window?.Android) {
  if (!bridge || typeof bridge.getPrivateDns !== 'function' || typeof bridge.setPrivateDns !== 'function') return null;
  try {
    const state = JSON.parse(bridge.getPrivateDns());
    if (!['off','opportunistic','hostname'].includes(state?.mode)) return null;
    return { mode:state.mode, host:typeof state.specifier === 'string' ? state.specifier : '' };
  } catch { return null; }
}

// Turning blocking off restores Android's default ("automatic") private DNS.
export function setNativePrivateDns(host, bridge = globalThis.window?.Android) {
  if (host && !validDnsHost(host)) return { ok:false, error:'DNSサーバーの形式を確認してください' };
  try {
    const result = JSON.parse(bridge.setPrivateDns(host || ''));
    return result?.ok === true ? { ok:true } : { ok:false, error:result?.error === 'permission' ? 'TVでの権限付与が必要です（READMEの手順）' : 'TVの設定を変更できませんでした' };
  } catch { return { ok:false, error:'TVの設定を変更できませんでした' }; }
}
