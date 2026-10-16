import assert from 'node:assert/strict';
import {radialLightVelocity,lightPath,futureRadialRange,horizonTidalRatio} from '../../engine/runtime/horizon_motion.mjs';
assert.equal(radialLightVelocity(1,1),0);
assert(radialLightVelocity(1.2,1)>0);
for(const r of [.98,.9,.6,.2,.03]){
 const [lo,hi]=futureRadialRange(r);assert(lo<hi&&hi<0);
 for(const direction of [-1,1]){
  const p=lightPath(r,direction);
  assert(p.every(s=>Number.isFinite(s.r)&&s.r>0&&s.r<1));
  assert(p.slice(1).every((s,i)=>s.r<=p[i].r));
 }
}
const p=lightPath(1.2,1);assert(p.at(-1).r>1.2);
const h=lightPath(1,1);assert(h.every(x=>x.r===1));
assert.equal(horizonTidalRatio(1,2),4);
assert.throws(()=>radialLightVelocity(0));
assert.throws(()=>lightPath(-1));
console.log('PASS: nonrotating radial null velocity, exterior escape, horizon tangent, inside inward-only paths, finite integration, tidal mass ratio. Source consistency, not a ray trace or artistic certificate.');
