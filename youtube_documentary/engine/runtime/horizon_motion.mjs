/* Reusable NONROTATING spherical-horizon causal illustration.
 * Units: c = horizon radius = 1. Painleve-Gullstrand radial coordinate time.
 * dr/dT = +/-1 - sqrt(1/r) for radial light. NOT an optical ray tracer,
 * crew survival simulation, rotating-hole model, or measured mission.
 */
export const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
export const smooth=v=>{v=clamp(v);return v*v*(3-2*v);};
export function radialLightVelocity(r,direction=1){
 if(!(r>0)||![-1,1].includes(direction))throw Error('Positive radius and radial light direction required');
 return direction-Math.sqrt(1/r);
}
export function lightPath(r0,direction=1,duration=1.2,step=.002){
 if(!(r0>0)||!(duration>0)||!(step>0))throw Error('Positive path parameters required');
 let r=r0;const rows=[{t:0,r}];
 for(let t=step;t<=duration+step/2;t+=step){
  const a=radialLightVelocity(r,direction),mid=r+a*step/2;
  if(mid<=.025)break;
  const next=r+radialLightVelocity(mid,direction)*step;
  if(next<=.025)break;r=next;rows.push({t:Math.min(t,duration),r});
 }
 return rows;
}
export function futureRadialRange(r){return [radialLightVelocity(r,-1),radialLightVelocity(r,1)];}
// Relative Newtonian radial tidal-gradient scaling for a fixed-size small object:
// at equal r / Schwarzschild radius, gradient is proportional to 1 / M^2.
// Ratios only: NOT a human tolerance or exact general-relativistic stress solver.
export const horizonTidalRatio=(massA,massB)=>{if(!(massA>0&&massB>0))throw Error('Positive masses required');return (massB/massA)**2;};
