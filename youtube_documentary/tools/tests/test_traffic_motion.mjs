// Source invariants only: these assertions are NOT traffic-model validation or art approval.
import assert from 'node:assert/strict';
import {makeRingMotion,bufferState} from '../../engine/runtime/traffic_motion.mjs';
const m=makeRingMotion();
assert.deepEqual(m.state(19.7),m.state(19.7),'seek must be deterministic');
let minimumGap=Infinity,minimumSpeed=Infinity,bufferGap=Infinity;
for(let i=0;i<=12000;i++){
 const s=m.state(i/120);assert.equal(s.cars.length,22);
 assert(s.cars.every(c=>[c.x,c.z,c.theta,c.speed,c.acceleration].every(Number.isFinite)));
 minimumGap=Math.min(minimumGap,s.minCenterGap);minimumSpeed=Math.min(minimumSpeed,...s.cars.map(c=>c.speed));
}
assert(minimumGap>4.47,'visible body extents must not overlap');assert(minimumSpeed>0,'cars must always progress forward');
assert(m.state(30).waveWorldSpeed<0,'authored steady wave must travel backward');
assert(m.state(16).cars[0].speed<1,'opening selected car must actually crawl, not drive quickly under crawling VO');
for(let i=0;i<2400;i++){const s=bufferState(i/120);for(let j=1;j<s.length;j++)bufferGap=Math.min(bufferGap,s[j].x-s[j-1].x-4.47);}
assert(bufferGap>0,'open-road example must not overlap');
console.log(JSON.stringify({result:'PASS: source invariants only',minimumCenterGap:minimumGap,minimumForwardSpeed:minimumSpeed,minimumBufferBumperGap:bufferGap}));
