/* Reusable AUTHORED travelling-wave illustration, NOT a calibrated traffic model.
 * Distances/speeds stage an explanation; no measured experimental data are used.
 */
export const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
export function makeRingMotion({radius=38,count=22,meanSpeed=5.5,amplitude=18,omega=.28,phase=Math.PI-.28*16}={}){
 const spacing=2*Math.PI*radius/count,k=2*Math.PI/count,base=-.65;
 function A(t){return amplitude*smooth((t-6)/10);}
 function distance(i,t){
  const a=A(t),pulseWeight=1-smooth(a/9);
  const pulse=i<3?[2.0,3.5,5.0][i]*smooth((t-[1.5,4.2,7.2][i])/2.8):0;
  return base*radius-i*spacing+meanSpeed*t+a*Math.sin(-i*k+omega*t+phase)-pulse*pulseWeight;
 }
 function state(t){
  const eps=1/120,values=[];
  for(let i=0;i<count;i++){
   const s=distance(i,t),speed=(distance(i,t+eps)-distance(i,t-eps))/(2*eps),acceleration=(distance(i,t+eps)-2*s+distance(i,t-eps))/(eps*eps);
   values.push({id:i,distance:s,theta:s/radius,speed,acceleration,x:radius*Math.cos(s/radius),z:radius*Math.sin(s/radius)});
  }
  const L=2*Math.PI*radius,sorted=values.map(v=>((v.distance%L)+L)%L).sort((a,b)=>a-b);
  const minCenterGap=Math.min(...sorted.map((s,i)=>(i+1<count?sorted[i+1]:sorted[0]+L)-s));
  return {cars:values,amplitude:A(t),minCenterGap,jamAngle:base+(meanSpeed/radius-omega)*t-phase+Math.PI,waveWorldSpeed:meanSpeed-radius*omega};
 }
 return {state,distance,radius,count,spacing,disclosure:'Authored explanatory motion; not a driver-following calibration or road prediction.'};
}

export function bufferState(t){
 const leadPulse=4*smooth((t-4.3)/2.3),goldPulse=2*smooth((t-5.4)/3.4),opening=8*smooth(t/3.0);
 return Array.from({length:6},(_,i)=>{
  let x=(i-2)*11+5.5*t;
  if(i>=3)x+=opening-leadPulse;
  else if(i===2)x-=goldPulse;
  else x-=(i===1?.8:.35)*smooth((t-7)/4);
  return {id:i,x,z:0,distance:x,speed:5.5,acceleration:i===3&&t>4.4&&t<5.5?-.6:(i===2&&t>5.5&&t<7?-.12:0)};
 });
}
