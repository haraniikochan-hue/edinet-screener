import test from 'node:test';
import assert from 'node:assert/strict';
import { roundedRectsPath, photoRegion, shadeFor, looksLike } from '../dashboard/js/frost.js';

test('frost clip is one rounded sub-path per card in viewport pixels',()=>{
  const path=roundedRectsPath([{x:216,y:270,width:500,height:286},{x:844,y:270,width:860,height:432}],32);
  assert.equal(path.match(/M/g).length,2);
  assert.ok(path.startsWith('M248 270H684A32 32 0 0 1 716 302V524'));
  assert.ok(path.endsWith('Z'));
});
test('frost clip radius never exceeds half a small card',()=>{
  assert.equal(roundedRectsPath([{x:0,y:0,width:40,height:20}],32),'M10 0H30A10 10 0 0 1 40 10V10A10 10 0 0 1 30 20H10A10 10 0 0 1 0 10V10A10 10 0 0 1 10 0Z');
});
test('a stage rectangle maps onto the covering photo like .photo-layer',()=>{
  const full=photoRegion({x:0,y:0,width:1920,height:1080},16/9);
  assert.ok(Math.abs(full.x0-.02/1.04)<1e-9 && Math.abs(full.x1-1.02/1.04)<1e-9);
  // A wider photo is cropped at the sides; a taller one at top and bottom (positioned at 48%)
  const wide=photoRegion({x:0,y:0,width:1920,height:1080},2);
  assert.ok(wide.x0>full.x0 && wide.x1<full.x1 && Math.abs(wide.y0-full.y0)<1e-9);
  const tall=photoRegion({x:0,y:0,width:1920,height:1080},4/3);
  assert.ok(tall.y0>full.y0 && tall.y1<full.y1 && Math.abs(tall.x0-full.x0)<1e-9);
});
test('text on the photo gets a shade only when the photo behind it is bright',()=>{
  assert.equal(shadeFor(.05),0);assert.equal(shadeFor(.1),0);assert.equal(shadeFor(Number.NaN),0);
  assert.ok(shadeFor(.2)>.2 && shadeFor(.2)<.35);
  assert.ok(shadeFor(.5)>shadeFor(.2));assert.equal(shadeFor(1),.55);
});
test('a photo that contradicts its time of day is recognised by its brightness',()=>{
  assert.equal(looksLike('day',.3),true);assert.equal(looksLike('day',.02),false,'a night shot in the day set');
  assert.equal(looksLike('night',.03),true);assert.equal(looksLike('night',.4),false,'a daylight shot in the night set');
  assert.equal(looksLike('dusk',.01),true);assert.equal(looksLike('dusk',.6),true);
  assert.equal(looksLike('day',Number.NaN),true,'an unreadable photo is kept');
});
