import test from 'node:test';
import assert from 'node:assert/strict';
import { AD_PROBES, CONTROL_PROBE, DEFAULT_ADBLOCK_DNS, adBlockStatus, nativePrivateDns, setNativePrivateDns, validDnsHost } from '../dashboard/js/adblock.js';
import { normalizeConfig } from '../dashboard/js/data.js';

const fetcherFor = blocked => async url => { if (blocked.includes(url)) throw new TypeError('Failed to fetch'); return {}; };

test('private DNS hostnames are validated before reaching the TV',()=>{
  for (const host of [DEFAULT_ADBLOCK_DNS,'abc123.dns.nextdns.io','adblock.dns.mullvad.net']) assert.equal(validDnsHost(host),true,host);
  for (const host of ['', '1.1.1.1', 'localhost', 'dns..example.com', '-bad.example.com', 'dns.example.com; rm -rf /', 'https://dns.adguard-dns.com', 'a'.repeat(64)+'.com']) assert.equal(validDnsHost(host),false,host);
});
test('ad blocking status compares ad hosts with a host blocklists never cover',async()=>{
  assert.equal(await adBlockStatus({fetcher:fetcherFor(AD_PROBES)}),'active');
  assert.equal(await adBlockStatus({fetcher:fetcherFor([])}),'inactive');
  assert.equal(await adBlockStatus({fetcher:fetcherFor([AD_PROBES[0]])}),'partial');
  assert.equal(await adBlockStatus({fetcher:fetcherFor([CONTROL_PROBE,...AD_PROBES])}),'unknown');
});
test('probes never send cookies or read the response',async()=>{
  const seen=[];await adBlockStatus({fetcher:async(url,options)=>{seen.push(options);return {};}});
  assert.equal(seen.length,AD_PROBES.length+1);
  assert.ok(seen.every(options=>options.mode==='no-cors' && options.credentials==='omit' && options.cache==='no-store'));
});
test('launcher bridge state is read defensively',()=>{
  assert.equal(nativePrivateDns(undefined),null);
  assert.equal(nativePrivateDns({getPrivateDns:()=>'{}'}),null,'setter missing');
  assert.equal(nativePrivateDns({getPrivateDns:()=>'not json',setPrivateDns:()=>''}),null);
  assert.equal(nativePrivateDns({getPrivateDns:()=>'{"mode":"strange"}',setPrivateDns:()=>''}),null);
  assert.deepEqual(nativePrivateDns({getPrivateDns:()=>'{"mode":"hostname","specifier":"dns.adguard-dns.com"}',setPrivateDns:()=>''}),{mode:'hostname',host:'dns.adguard-dns.com'});
});
test('switching private DNS passes only a validated hostname, or empty to restore automatic',()=>{
  const calls=[];const bridge={setPrivateDns:host=>{calls.push(host);return '{"ok":true}';}};
  assert.deepEqual(setNativePrivateDns(DEFAULT_ADBLOCK_DNS,bridge),{ok:true});
  assert.deepEqual(setNativePrivateDns('',bridge),{ok:true});
  assert.equal(setNativePrivateDns('evil host',bridge).ok,false);
  assert.deepEqual(calls,[DEFAULT_ADBLOCK_DNS,'']);
  assert.match(setNativePrivateDns(DEFAULT_ADBLOCK_DNS,{setPrivateDns:()=>'{"ok":false,"error":"permission"}'}).error,/権限/);
  assert.equal(setNativePrivateDns(DEFAULT_ADBLOCK_DNS,{setPrivateDns:()=>{throw new Error('bridge');}}).ok,false);
});
test('config keeps a valid ad-blocking DNS server and falls back to AdGuard DNS',()=>{
  assert.equal(normalizeConfig({}).adblockDns,DEFAULT_ADBLOCK_DNS);
  assert.equal(normalizeConfig({adblockDns:'ABC.dns.nextdns.io'}).adblockDns,'abc.dns.nextdns.io');
  assert.equal(normalizeConfig({adblockDns:'bad host'}).adblockDns,DEFAULT_ADBLOCK_DNS);
});
