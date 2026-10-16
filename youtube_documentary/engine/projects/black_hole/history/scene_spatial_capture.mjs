import {smooth,clamp,lightPath,futureRadialRange} from '/runtime/horizon_motion.mjs';
// Original authored geometry and conceptual optical treatment. NOT a GR ray trace.
export async function createFilm(S,cfg){
 const T=S.THREE,{scene,camera,mesh,material,roundedBox,text}=S,C=cfg.cues;
 S.renderer.shadowMap.enabled=false;
 scene.traverse(o=>{if(o.isDirectionalLight)o.intensity*=.67;if(o.isHemisphereLight)o.intensity=.45;});
 const W=new T.Group(),D=new T.Group();scene.add(W,D);let phase='';
 const v=(x,y,z)=>new T.Vector3(x,y,z),mix=(a,b,u)=>a.clone().lerp(b,smooth(u));
 const pose=(p,look,up=v(0,1,0))=>({p,look,up});
 function blend(a,b,u){return pose(mix(a.p,b.p,u),mix(a.look,b.look,u),mix(a.up,b.up,u).normalize());}
 function basic(color,options={}){return new T.MeshBasicMaterial({color,...options});}
 function ball(r,mat,parent=W){return mesh(new T.SphereGeometry(r,32,20),mat,parent);}
 function tube(points,col,r=.035,parent=W,opacity=1){const curve=new T.CatmullRomCurve3(points.map(a=>Array.isArray(a)?v(...a):a));const m=basic(col,{transparent:opacity<1,opacity,depthWrite:opacity===1});return mesh(new T.TubeGeometry(curve,Math.max(24,points.length*3),r,7,false),m,parent);}
 function hoop(r,col,parent=W,opacity=1){const g=mesh(new T.TorusGeometry(r,.022,6,128),basic(col,{transparent:true,opacity,depthWrite:false}),parent);return g;}
 function arrow(a,b,color,parent=W,width=.045){
  const g=new T.Group();parent.add(g);const p=v(...a),q=v(...b),dir=q.clone().sub(p),len=dir.length();
  const shaft=mesh(new T.CylinderGeometry(width,width,Math.max(.01,len-.25),8),basic(color),g);shaft.position.copy(p).addScaledVector(dir,.5);shaft.quaternion.setFromUnitVectors(v(0,1,0),dir.clone().normalize());
  const head=mesh(new T.ConeGeometry(width*3.2,.38,12),basic(color),g);head.position.copy(q).addScaledVector(dir,-.19/len);head.quaternion.copy(shaft.quaternion);return g;
 }
 // Seeded painted star sphere: no photographs, no generated historical evidence.
 const skyCanvas=document.createElement('canvas');skyCanvas.width=2048;skyCanvas.height=1024;const k=skyCanvas.getContext('2d');
 k.fillStyle='#030712';k.fillRect(0,0,2048,1024);let seed=9247;const rnd=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
 for(let i=0;i<240;i++){
  const x=rnd()*2048,y=460+120*Math.sin(x/360)+(rnd()-.5)*230,r=40+rnd()*120;
  const grad=k.createRadialGradient(x,y,0,x,y,r);grad.addColorStop(0,`rgba(${25+Math.floor(rnd()*15)},${43+Math.floor(rnd()*12)},90,${.025+rnd()*.04})`);grad.addColorStop(1,'rgba(0,0,0,0)');k.fillStyle=grad;k.fillRect(x-r,y-r,2*r,2*r);
 }
 for(let i=0;i<14500;i++){
  const x=rnd()*2048,y=rnd()*1024,r=.18+rnd()**6*1.4,alpha=.15+rnd()*.75;
  k.fillStyle=`rgba(${165+Math.floor(rnd()*80)},${180+Math.floor(rnd()*65)},255,${alpha})`;k.beginPath();k.arc(x,y,r,0,Math.PI*2);k.fill();
  if(r>1.35){k.fillStyle='rgba(139,191,255,.12)';k.fillRect(x-4,y-.3,8,.6);k.fillRect(x-.3,y-4,.6,8);}
 }
 const skyTex=new T.CanvasTexture(skyCanvas);skyTex.colorSpace=T.SRGBColorSpace;
 const sky=mesh(new T.SphereGeometry(245,48,24),basic('#ffffff',{map:skyTex,side:T.BackSide}),scene);sky.rotation.y=.8;sky.renderOrder=-10;
 // Apparent dark silhouette is intentionally distinct from the SMALLER diagram horizon.
 // This camera-facing optical motif is not a physical black surface or accurate lensing.
 const optical=new T.Group();W.add(optical);
 const silhouette=mesh(new T.CircleGeometry(20.78,160),basic('#010208'),optical);
 const lenses=new T.Group();optical.add(lenses);
 for(let j=0;j<22;j++){
  const rr=20.8+j*.12,start=rnd()*Math.PI*2,arc=.10+rnd()*.65;
  const pts=Array.from({length:24},(_,i)=>[rr*Math.cos(start+i/23*arc),rr*Math.sin(start+i/23*arc),.025]);
  tube(pts,j%4===0?'#d6e6fb':'#4f8bba',j%4===0?.028:.012,lenses,.18+rnd()*.45);
 }
 const horizon=new T.Group();W.add(horizon);
 const shell=ball(8,basic('#5c94b0',{transparent:true,opacity:.045,side:T.DoubleSide,depthWrite:false}),horizon);
 for(let j=0;j<3;j++){const h=hoop(8,'#76abc0',horizon,.32);if(j===1)h.rotation.x=Math.PI/2;if(j===2)h.rotation.y=Math.PI/2;}
 const dotted=[];for(let j=0;j<64;j++){let a=j/64*Math.PI*2;const m=ball(.035,basic('#b1d6e2'),horizon);m.position.set(8*Math.cos(a),8*Math.sin(a),0);dotted.push(m);}
 function astronaut(){
  const g=new T.Group();W.add(g);const mats=[];
  function mat(c,o={}){const m=material(c,{roughness:.47,metalness:.14,transparent:true,...o});mats.push({m,c:new T.Color(c),e:m.emissive?.clone()});return m;}
  const suit=mat('#d5dfe4'),trim=mat('#223749'),gold=mat('#bc986b',{metalness:.7,roughness:.3}),glass=mat('#153d57',{metalness:.8,roughness:.16}),rubber=mat('#3d5060'),lamp=mat('#8acbe8',{emissive:'#4a94bc',emissiveIntensity:.7});
  const body=mesh(roundedBox(1.12,1.34,.70,.17),suit,g);body.position.y=.16;
  const pack=mesh(roundedBox(.93,1.22,.46,.10),trim,g);pack.position.set(0,.2,-.54);
  const packPlate=mesh(roundedBox(.79,.97,.05,.06),suit,g);packPlate.position.set(0,.2,-.80);
  for(let j=0;j<7;j++){const vent=mesh(new T.BoxGeometry(.54,.025,.018),rubber,g);vent.position.set(0,.56-j*.095,-.84);}
  const neck=mesh(new T.CylinderGeometry(.39,.39,.17,32),gold,g);neck.position.y=.94;
  const helm=ball(.64,suit,g);helm.position.y=1.48;helm.scale.set(1,1.03,.91);
  const rim=ball(.51,gold,g);rim.position.set(0,1.49,.31);rim.scale.set(1,.84,.48);
  const visor=ball(.48,glass,g);visor.position.set(0,1.50,.36);visor.scale.set(1,.83,.49);
  const reflection=tube([[-.35,1.66,.54],[-.2,1.78,.57],[.12,1.81,.55]],'#94bdd3',.015,g,.65);
  for(const x of [-.44,.44]){const l=mesh(new T.BoxGeometry(.12,.07,.10),lamp,g);l.position.set(x,1.87,.18);}
  const control=mesh(roundedBox(.56,.42,.12,.035),trim,g);control.position.set(0,.35,.42);
  for(let j=0;j<3;j++){const q=mesh(new T.BoxGeometry(.07,.035,.02),j===2?gold:lamp,g);q.position.set(-.14+j*.14,.39,.49);}
  function limb(a,b,r,mat){const x=v(...a),y=v(...b),z=y.clone().sub(x);const m=mesh(new T.CylinderGeometry(r,r*.94,z.length(),16),mat,g);m.position.copy(x).add(y).multiplyScalar(.5);m.quaternion.setFromUnitVectors(v(0,1,0),z.normalize());return m;}
  for(const side of [-1,1]){
   const shoulder=ball(.30,suit,g);shoulder.position.set(side*.69,.59,0);
   limb([side*.68,.52,0],[side*.89,-.10,.12],.235,suit);const elbow=ball(.225,rubber,g);elbow.position.set(side*.89,-.10,.12);
   limb([side*.89,-.10,.12],[side*1.05,-.39,.48],.205,suit);const cuff=ball(.215,gold,g);cuff.position.set(side*1.04,-.37,.44);
   const glove=ball(.23,suit,g);glove.position.set(side*1.10,-.70,.60);glove.scale.y=1.3;
   limb([side*.31,-.48,0],[side*.33,-1.25,.06],.245,suit);const knee=ball(.245,trim,g);knee.position.set(side*.33,-1.25,.08);
   limb([side*.33,-1.25,.08],[side*.36,-1.92,.08],.22,suit);
   const boot=mesh(roundedBox(.46,.33,.79,.09),rubber,g);boot.position.set(side*.36,-2.02,.23);
   for(let j=0;j<3;j++){const joint=mesh(new T.TorusGeometry(.23,.022,6,20),rubber,g);joint.rotation.x=Math.PI/2;joint.position.set(side*.33,-1.4-j*.12,.08);}
  }
  tube([[-.4,.48,.38],[-.68,.26,.56],[-.60,-.36,.48],[-.32,-.48,.36]],'#a5bac4',.047,g);
  const watch=new T.Group();watch.position.set(1.015,-.30,.78);g.add(watch);
  const wc=mesh(new T.CylinderGeometry(.23,.23,.08,48),gold,watch);wc.rotation.x=Math.PI/2;
  const wf=mesh(new T.CircleGeometry(.202,48),basic('#0e1d2a'),watch);wf.position.z=.046;
  for(let i=0;i<12;i++){const a=i/12*Math.PI*2,q=mesh(new T.BoxGeometry(.012,.032,.006),basic('#c8e7ed'),watch);q.position.set(Math.sin(a)*.167,Math.cos(a)*.167,.052);q.rotation.z=-a;}
  const hand=mesh(new T.BoxGeometry(.011,.173,.008),basic('#a7e4ea'),watch);hand.geometry.translate(0,.069,0);hand.position.z=.066;
  const short=mesh(new T.BoxGeometry(.015,.11,.008),basic('#e0b985'),watch);short.geometry.translate(0,.038,0);short.position.z=.061;
  const beacon=ball(.09,lamp,g);beacon.position.set(-.70,.82,.16);
  g.traverse(o=>{if(o.isMesh&&o.material?.color&&!mats.some(e=>e.m===o.material)){o.material.transparent=true;mats.push({m:o.material,c:o.material.color.clone()});}});
  function tint(opacity=1,u=0){for(const {m,c,e}of mats){m.opacity=opacity;m.color.copy(c).lerp(new T.Color('#bd493b'),u);if(e&&(e.r+e.g+e.b)>0)m.emissive.copy(e).lerp(new T.Color('#a53d27'),u);m.depthWrite=opacity>.98;}beacon.material.emissiveIntensity=.4+2.0*Math.max(0,Math.sin(phaseTime*Math.PI*2))**18;}
  let phaseTime=0;
  return {g,watch,hand,short,beacon,mats,tint,tick(t){phaseTime=t;hand.rotation.z=-(Math.floor(t)+17)*Math.PI*2/60;short.rotation.z=-(t+312)*Math.PI*2/3600;},watchPosition(){g.updateMatrixWorld(true);return watch.getWorldPosition(new T.Vector3());}};
 }
 const A=astronaut(),smallA=astronaut();A.g.rotation.z=-Math.PI/2;smallA.g.rotation.z=-Math.PI/2;
 const small=new T.Group();W.add(small);small.position.set(-19,0,0);
 ball(2.2,basic('#010208'),small);const smh=hoop(2.2,'#b0d4e7',small,.6);smh.rotation.y=Math.PI/2;
 for(let j=0;j<2;j++){const q=hoop(2.2,'#648a9d',small,.22);q.rotation.x=j*Math.PI/2;}
 const ship=new T.Group();W.add(ship);ship.position.set(42,0,0);
 const metal=material('#7c95a4',{metalness:.65,roughness:.36}),pale=material('#d9e4e8',{roughness:.43}),dark=material('#12374d',{metalness:.6,roughness:.28});
 const hull=mesh(new T.CylinderGeometry(.65,.8,3.6,16),pale,ship);hull.rotation.z=Math.PI/2;
 const nose=ball(.72,dark,ship);nose.position.x=-1.8;nose.scale.x=.55;
 for(const side of [-1,1]){
  const spar=mesh(new T.BoxGeometry(.14,.12,7.2),metal,ship);spar.position.set(.25,0,side*3.1);
  const panel=mesh(new T.BoxGeometry(2.5,.07,4.0),dark,ship);panel.position.set(.25,0,side*4.4);
  for(let j=0;j<8;j++){const q=mesh(new T.BoxGeometry(2.44,.016,.018),metal,ship);q.position.set(.25,.045,side*4.4-1.8+j*.5);}
  const engine=mesh(new T.CylinderGeometry(.34,.46,1.0,16),metal,ship);engine.rotation.z=Math.PI/2;engine.position.set(2.1,0,side*.8);
 }
 const antenna=mesh(new T.CylinderGeometry(.025,.025,1.9,10),metal,ship);antenna.position.y=1.3;
 const dish=mesh(new T.SphereGeometry(.7,24,12,0,Math.PI*2,0,.65),pale,ship);dish.position.y=2.25;dish.rotation.z=Math.PI/2;
 const pulses=[];for(let i=0;i<7;i++){const g=new T.Group();W.add(g);const core=ball(.12,basic('#b5eff7',{transparent:true}),g),halo=ball(.28,basic('#62b4d7',{transparent:true,opacity:.13,depthWrite:false}),g);pulses.push({g,core,halo});}
 const channel=tube([[9.3,.6,0],[23,.6,0],[41,.6,0]],'#35576a',.014,W,.6);
 const receiver=hoop(1.1,'#9cd6e8',ship,.6);receiver.rotation.y=Math.PI/2;receiver.position.x=-2.4;
 const pullArrows=new T.Group();W.add(pullArrows);
 const pullFeet=arrow([0,0,0],[-1.05,0,0],'#f29b77',pullArrows,.045),pullHead=arrow([0,0,0],[-.48,0,0],'#92cbe0',pullArrows,.045);
 // Explicit radius-versus-future diagram, not a photographed interior.
 const plot=new T.Group();D.add(plot);
 for(let i=0;i<7;i++)tube([[-31,-8+i*5,-.08],[23,-8+i*5,-.08]],'#24404f',.012,plot,.7);
 for(let i=0;i<12;i++)tube([[-31+i*5,-8,-.08],[-31+i*5,23,-.08]],'#24404f',.012,plot,.7);
 for(let i=0;i<20;i++)tube([[0,-8+i*1.6,.1],[0,-7.3+i*1.6,.1]],'#d6b980',.038,plot,.8);
 arrow([-31,-10,0],[23,-10,0],'#9cb8c5',plot,.025);arrow([25,-8,0],[25,22,0],'#9cb8c5',plot,.025);
 const paths=[];
 for(const [r0,d,col]of [[1.28,1,'#89e2cf'],[.86,1,'#fb987d'],[.86,-1,'#97bcd1']]){
  const samples=lightPath(r0,d,1.5),pts=samples.map(s=>v((s.r-1)*31,s.t*18-7,0));
  const curve=new T.CatmullRomCurve3(pts),body=mesh(new T.TubeGeometry(curve,180,.055,8,false),basic(col),plot),aura=mesh(new T.TubeGeometry(curve,180,.19,6,false),basic(col,{transparent:true,opacity:.10,depthWrite:false}),plot);
  const bead=ball(.21,basic(col),plot);const head=mesh(new T.ConeGeometry(.24,.7,12),basic(col),plot);
  const end=curve.getPoint(1),before=curve.getPoint(.97);head.position.copy(end);head.quaternion.setFromUnitVectors(v(0,1,0),end.clone().sub(before).normalize());
  paths.push({r0,d,curve,body,aura,bead,head});
 }
 const fan=new T.Group();plot.add(fan);
 for(const [r,y]of [[.84,2.0],[.56,12]]){
  const [lo,hi]=futureRadialRange(r),x=(r-1)*31,dt=.16;
  const geom=new T.BufferGeometry().setFromPoints([v(x,y,0),v(x+lo*31*dt,y+18*dt,0),v(x+hi*31*dt,y+18*dt,0)]);geom.setIndex([0,1,2]);geom.computeVertexNormals();mesh(geom,basic('#e9a084',{transparent:true,opacity:.22,side:T.DoubleSide,depthWrite:false}),fan);
  for(let i=0;i<5;i++)arrow([x,y,.08],[x+(lo+(hi-lo)*i/4)*31*dt,y+18*dt,.08],'#dda18c',fan,.025);
 }
 function labels(items){
  const test=document.createElement('canvas').getContext('2d');
  document.querySelector('#annotations').innerHTML=items.map(({p,word,color='#c4d7e3',size=28})=>{const q=S.project(p);test.font=`700 ${size}px Doc`;const w=test.measureText(word).width;return q.visible&&q.x>w/2+50&&q.x<cfg.width-w/2-50&&q.y>190&&q.y<cfg.height-95?`<text x="${q.x}" y="${q.y}" text-anchor="middle" fill="${color}" stroke="#030712" stroke-width="3" paint-order="stroke" font-family="Doc" font-size="${size}" font-weight="700">${word}</text>`:'';}).join('');
 }
 const wide=pose(v(36,28,67),v(7,0,0)),compare=pose(v(7,34,80),v(-4,0,0));
 function follow(x,offset=v(8,4,14),up=v(0,1,0)){return pose(v(x,0,0).add(offset),v(x,0,0),up);}
 function opacity(t,a,b){return smooth((t-a)/.25)*(1-smooth((t-b+.3)/.3));}
 function seek(t){
  let title={heading:''},anno=[],cam=wide;const at=t-C.beacon;
  W.visible=true;D.visible=false;small.visible=smallA.g.visible=false;ship.visible=true;channel.visible=false;pullArrows.visible=false;
  optical.visible=t<C.surface;optical.quaternion.copy(camera.quaternion);horizon.visible=!optical.visible;horizon.scale.setScalar(1);
  sky.material.color.setScalar(1);A.g.visible=true;A.g.scale.set(1,1,1);A.g.position.set(12,0,0);A.g.rotation.set(0,0,-Math.PI/2);A.tick(t);A.tint(1,0);smallA.tick(t);smallA.tint(1,0);
  pulses.forEach(p=>p.g.visible=false);fan.visible=false;
  document.querySelector('#disclosure').textContent=optical.visible?'ILLUSTRATIVE LENSING · NOT TO SCALE':'EXPLANATORY ANIMATION · NOT TO SCALE';
  if(t<C.surface){
   phase='cold_open';ship.visible=t>C.message;
   const x=10.4-3.2*smooth((t-2)/10);A.g.position.x=x;
   const close=blend(follow(x,v(13,8,28),v(.2,.98,0)),follow(x,v(5,2,11),v(.5,.86,0)),t/3);cam=blend(close,wide,(t-4)/7);
   if(t>C.message){const q=pulses[0];q.g.visible=true;const u=clamp((t-C.message)/3);q.g.position.set(7.35-.85*u,.3,1.2);q.core.material.color.set('#f6a58a');q.halo.material.color.set('#d5826d');}
   if(t>C.nothing&&t<C.message)title={heading:'NO WALL.\nNO IMPACT.',size:69,opacity:opacity(t,C.nothing,C.message)};
   if(t>C.never)title={heading:'NO WAY BACK.',size:77,color:'#f2b194',opacity:opacity(t,C.never,C.surface)};
  }else if(t<C.small){
   phase='boundary_and_destination';cam=blend(wide,pose(v(31,21,55),v(9,0,0)),(t-C.surface)/8);A.g.position.x=12.6;
   if(t>C.follow)cam=blend(cam,follow(12.6,v(7,3,16)),(t-C.follow)/5);
   if(t<C.follow){title={heading:'NOT A SURFACE.\nA BOUNDARY.',size:67,color:'#b3d9e6',opacity:opacity(t,C.surface,C.follow)};anno.push({p:[-2,-8,0],word:'SCHEMATIC HORIZON'});}
   else if(t>C.quiet){title={heading:'SUPERMASSIVE.\nQUIET.',size:65,opacity:opacity(t,C.quiet,C.small)};}
  }else if(t<C.beacon){
   phase='tidal_comparison';small.visible=smallA.g.visible=true;smallA.g.position.set(-12.8,0,.6);const elongate=smooth((t-C.small)/6.2);smallA.g.scale.set(.8-.22*elongate,.8+.7*elongate,.8-.22*elongate);A.g.position.set(11.7,0,.6);A.g.scale.setScalar(.8);ship.visible=false;
   cam=compare;const detail=pose(v(-9,10,25),v(-16,0,0));
   if(t<C.large)cam=blend(compare,detail,(t-C.small)/2.5);else cam=blend(detail,pose(v(24,13,32),v(9,0,0)),(t-C.large)/2.2);
   anno=[{p:[-19,-5,0],word:'SMALL BLACK HOLE',color:'#e9ad96'},{p:[3,-9,0],word:'SUPERMASSIVE',color:'#aad7e5'}];
   title=t<C.large?{heading:'ONE SIDE IS\nPULLED HARDER.',size:62,color:'#eeb296',opacity:opacity(t,C.pull,C.large)}:{heading:'YOU COULD\nCROSS ALIVE.',size:70,color:'#a0dddb',opacity:opacity(t,C.alive-.1,C.beacon)};
  }else if(t<C.watch){
   phase='distant_observer';A.g.position.set(9.2,0,0);channel.visible=true;cam=blend(pose(v(29,20,56),v(23,0,0)),pose(v(44,9,31),v(21,0,0)),at/15);
   title={heading:'FROM THE SHIP',size:50,color:'#bad7e6',opacity:opacity(t,C.beacon,C.watch)};
   const emission=[0,1.3,2.6,3.9,5.2,6.5],arrivals=[1.2,2.8,4.9,7.5,11.0,15.4];
   for(let i=0;i<6;i++){const u=(at-emission[i])/(arrivals[i]-emission[i]),p=pulses[i];if(u>=0&&u<=1){p.g.visible=true;p.g.position.set(9.4+30.3*smooth(u),.6,0);const col=new T.Color('#9bdeeb').lerp(new T.Color('#f49478'),i/5);p.core.material.color.copy(col);p.halo.material.color.copy(col);p.core.material.opacity=1-i*.12;}}
   const blink=arrivals.reduce((a,b)=>Math.max(a,Math.max(0,1-Math.abs(at-b)/.4)),0);receiver.material.opacity=.17+.8*blink;receiver.scale.setScalar(1+blink*.3);
   const fading=smooth((t-C.red)/Math.max(.5,C.fade-C.red+1));A.tick(C.beacon+5*(1-Math.exp(-at/5)));A.tint(1-fading,fading*.9);
   anno=[{p:[42,-3,0],word:'DISTANT RECEIVER'},{p:[20,3,0],word:t<C.red?'ARRIVALS SPREAD APART':'REDDER. FAINTER.',color:t<C.red?'#b2dce8':'#f4ac91'}];
   if(t>C.fade)title={heading:'YOUR IMAGE\nFADES OUT.',size:68,color:'#e5a18c',opacity:opacity(t,C.fade,C.watch)};
   document.querySelector('#disclosure').textContent='SIGNAL-TIMING ILLUSTRATION · NOT TO SCALE';
  }else if(t<C.model){
   phase='astronaut_clock_and_crossing';ship.visible=false;const u=smooth((t-C.cross)/2.4),x=9.3-2.2*u;A.g.position.x=x;
   const wp=A.watchPosition(),watchCam=pose(wp.clone().add(v(.6,.3,1.55)),wp,v(1,0,0));
   cam=t<C.cross?watchCam:blend(watchCam,follow(x,v(3,5,13)),(t-C.cross)/2.1);
   title=t<C.cross?{heading:'ON YOUR WATCH',x:1260,y:100,size:43,color:'#c2deea',opacity:opacity(t,C.watch,C.cross)}:{heading:'YOU KEEP\nMOVING.',size:69,opacity:opacity(t,C.cross,C.turn)};
   if(t>C.turn){cam=follow(x,v(3,5,13));title={heading:'A BIGGER ENGINE\nWON\'T HELP.',size:64,color:'#eab398',opacity:opacity(t,C.turn,C.model)};}
   anno=t>C.cross+2?[{p:[-1,-8,0],word:'HORIZON — NOT A WALL'}]:[];
  }else if(t<C.survival){
   phase='radial_causal_diagram';W.visible=false;D.visible=true;sky.material.color.setScalar(.45);
   cam=blend(pose(v(12,9,69),v(-1,5,0)),pose(v(22,17,76),v(-3,7,0)),(t-C.model)/14);
   const run=smooth((t-C.model)/3.0);paths.forEach((p,i)=>{const visible=i===0||t>C.future+.4;p.body.visible=p.aura.visible=p.bead.visible=p.head.visible=visible;const n=Math.floor(p.body.geometry.index.count*run/3)*3;p.body.geometry.setDrawRange(0,n);p.aura.geometry.setDrawRange(0,n);p.bead.position.copy(p.curve.getPoint(Math.min(run,(t-C.model)*(i===2?.27:.14)%1)));const tip=p.curve.getPoint(Math.max(.002,run)),prev=p.curve.getPoint(Math.max(0,run-.01));p.head.position.copy(tip);p.head.quaternion.setFromUnitVectors(v(0,1,0),tip.clone().sub(prev).normalize());});
   fan.visible=t>C.future;title=t<C.future?{heading:'FOLLOW THE\nLIGHT.',size:67,color:'#a8dece',opacity:opacity(t,C.model,C.future)}:{heading:'EVERY WAY FORWARD\nLEADS IN.',size:62,color:'#eeb59a',opacity:opacity(t,C.future,C.exit)};
   if(t>C.outward&&t<C.exit)title={heading:'EVEN OUTWARD LIGHT\nGOES INWARD.',size:63,color:'#efb193',opacity:opacity(t,C.outward,C.exit)};
   if(t>C.exit)title={heading:'THE EXIT ISN\'T\nIN YOUR FUTURE.',size:67,color:'#f0b196',opacity:opacity(t,C.exit,C.survival)};
   anno=[{p:[0,-10,0],word:'HORIZON',color:'#e1c28e',size:27},{p:[-23,-12.3,0],word:'CENTER',size:25},{p:[17,-12.3,0],word:'OUTWARD',size:25},{p:[26,17,0],word:'FUTURE',size:25},{p:[14,12,0],word:'OUTSIDE',color:'#9bdecd',size:27},{p:[-14,3,0],word:'INSIDE',color:'#f3aa91',size:27}];
   document.querySelector('#disclosure').textContent='RADIAL LIGHT PATHS · NONROTATING MODEL';
  }else if(t<C.return){
   phase='interior_and_model_limit';ship.visible=false;optical.visible=false;const stretch=1+.65*smooth((t-C.tides)/5.4),x=4.8-.9*smooth((t-C.tides)/7);A.g.position.x=x;A.g.scale.set(1/Math.sqrt(stretch),stretch,1/Math.sqrt(stretch));
   cam=blend(follow(x,v(3,5,13)),pose(v(18,16,39),v(0,0,0)),(t-C.singularity)/7);sky.material.color.setScalar(.30);pullArrows.visible=t>C.tides&&t<C.singularity;pullFeet.position.set(x-1.6*stretch,-.65,1);pullHead.position.set(x+1.6*stretch,-.65,1);
   title=t<C.singularity?{heading:'ALIVE AT THE EDGE.\nNOT SAFE INSIDE.',size:61,color:'#efb499',opacity:opacity(t,C.survival,C.singularity)}:{heading:'A LIMIT OF\nOUR THEORY.',size:69,color:'#c5d6e8',opacity:opacity(t,C.singularity,C.return)};
   if(t>C.portal)A.tint(1-smooth((t-C.portal)/2),.4);
   if(t>C.unknown){horizon.scale.setScalar(1-.18*smooth((t-C.unknown)/3));title={heading:'NOT A CONFIRMED\nPORTAL.',size:68,color:'#b6c9df',opacity:opacity(t,C.unknown,C.return)};}
   document.querySelector('#disclosure').textContent='CONCEPTUAL CUTAWAY · NOT A CAMERA VIEW';
  }else{
   phase='return_to_calm_crossing';ship.visible=false;optical.visible=false;const x=9.4-2.1*smooth((t-C.point)/2.4);A.g.position.x=x;
   cam=blend(follow(x,v(5,3,13)),pose(v(26,19,46),v(4,0,0)),(t-C.alarm)/3.4);
   title={heading:'NO WALL.\nNO WAY BACK.',size:73,color:'#e5c6a9',opacity:opacity(t,C.point,cfg.duration-.35)};
   document.querySelector('#disclosure').textContent='EXPLANATORY ANIMATION · NOT TO SCALE';
  }
  camera.position.copy(cam.p);camera.up.copy(cam.up);camera.lookAt(cam.look);camera.updateProjectionMatrix();camera.updateMatrixWorld();optical.quaternion.copy(camera.quaternion);
  text(title);labels(anno);
  const end=1-smooth((t-(cfg.duration-.65))/.65);for(const id of ['stage','annotations','title','subtitle','disclosure'])document.querySelector('#'+id).style.opacity=id==='title'?Number(title.opacity??1)*end:end;
 }
 return {seek,stats:()=>({phase,diagramModel:'nonrotating radial PG',insideOutwardVelocity:futureRadialRange(.86)[1],frameIsAuthoredIllustration:true})};
}
