import { cp, mkdir, rm, readdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
const root = fileURLToPath(new URL('../', import.meta.url));
for (const name of await readdir(resolve(root, 'dashboard/js'))) {
  if (name.endsWith('.js')) execFileSync(process.execPath, ['--check', resolve(root,'dashboard/js',name)]);
}
await rm(resolve(root,'dist'), { recursive:true, force:true });
await mkdir(resolve(root,'dist'), { recursive:true });
await cp(resolve(root,'dashboard'), resolve(root,'dist'), {
  recursive:true, filter: path => !path.split('/').some(part => part.startsWith('.')) && !path.endsWith('config.local.json'),
});
console.log('Built dist/ — static WebView assets (no credentials). API-backed widgets need server.mjs.');
