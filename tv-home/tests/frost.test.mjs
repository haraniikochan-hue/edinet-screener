import test from 'node:test';
import assert from 'node:assert/strict';
import { roundedRectsPath } from '../dashboard/js/frost.js';

test('frost clip is one rounded sub-path per card in viewport pixels',()=>{
  const path=roundedRectsPath([{x:216,y:270,width:500,height:286},{x:844,y:270,width:860,height:432}],32);
  assert.equal(path.match(/M/g).length,2);
  assert.ok(path.startsWith('M248 270H684A32 32 0 0 1 716 302V524'));
  assert.ok(path.endsWith('Z'));
});
test('frost clip radius never exceeds half a small card',()=>{
  assert.equal(roundedRectsPath([{x:0,y:0,width:40,height:20}],32),'M10 0H30A10 10 0 0 1 40 10V10A10 10 0 0 1 30 20H10A10 10 0 0 1 0 10V10A10 10 0 0 1 10 0Z');
});
