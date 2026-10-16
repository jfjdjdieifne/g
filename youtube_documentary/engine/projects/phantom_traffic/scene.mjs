import {makeRingMotion,bufferState,smooth} from '/runtime/traffic_motion.mjs';
export async function createFilm(S,cfg){
 const T=S.THREE,{scene,camera,mesh,material,roundedBox,line,text}=S,C=cfg.cues;
 const ring=new T.Group(),straight=new T.Group();scene.add(ring,straight);
 const dark=material('#263941',{roughness:.8}),edge=material('#92a8ac',{diffuseOnly:true}),white=material('#e0e3db',{roughness:.29,metalness:.35,clearcoat:.8});
 const gold=material('#cfa357',{roughness:.28,metalness:.64,clearcoat:.8}),glass=material('#152c39',{roughness:.16,metalness:.63,clearcoat:1});
 const black=material('#10181d',{roughness:.75}),chrome=material('#a5b9c0',{roughness:.22,metalness:.8});
 const roadCanvas=document.createElement('canvas');roadCanvas.width=roadCanvas.height=512;const ctx=roadCanvas.getContext('2d');let seed=5394;const rand=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
 const pixels=ctx.createImageData(512,512);for(let i=0;i<pixels.data.length;i+=4){const n=rand()*13;pixels.data[i]=64+n;pixels.data[i+1]=77+n;pixels.data[i+2]=83+n;pixels.data[i+3]=255;}ctx.putImageData(pixels,0,0);
 const tex=new T.CanvasTexture(roadCanvas);tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(16,16);tex.colorSpace=T.SRGBColorSpace;
 const asphalt=material('#bbc3bf',{diffuseOnly:true,map:tex}),paint=material('#d3d7ce',{diffuseOnly:true});
 const ground=mesh(new T.PlaneGeometry(1000,1000),material('#182c3c',{diffuseOnly:true}));ground.rotation.x=-Math.PI/2;ground.position.y=-1.1;ground.castShadow=false;ground.receiveShadow=false;
 const plinth=mesh(new T.CylinderGeometry(45.5,46.0,.8,128),material('#203c4d',{diffuseOnly:true}),ring);plinth.position.y=-.68;plinth.receiveShadow=false;
 const road=mesh(new T.RingGeometry(34.1,41.9,192),asphalt,ring);road.rotation.x=-Math.PI/2;road.position.y=-.21;road.castShadow=false;
 const curb=mesh(new T.RingGeometry(33.65,34.08,192),edge,ring);curb.rotation.x=-Math.PI/2;curb.position.y=-.2;
 const curb2=mesh(new T.RingGeometry(41.9,42.28,192),edge,ring);curb2.rotation.x=-Math.PI/2;curb2.position.y=-.2;
 const ringDashGeom=new T.BoxGeometry(1.55,.022,.10);
 for(let i=0;i<72;i++){
  const a=i/72*Math.PI*2;for(const r of [34.9,41.1]){
   const dash=mesh(ringDashGeom,paint,ring);dash.position.set(r*Math.cos(a),-.17,r*Math.sin(a));dash.rotation.y=-a-Math.PI/2;dash.castShadow=false;
  }
 }
 function silhouette(points,depth,bevel=.045){const sh=new T.Shape();points.forEach((p,i)=>i?sh.lineTo(...p):sh.moveTo(...p));sh.closePath();const g=new T.ExtrudeGeometry(sh,{depth,bevelEnabled:true,bevelSize:bevel,bevelThickness:bevel,bevelSegments:2,steps:1});g.translate(0,0,-depth/2);return g;}
 const bodyGeom=silhouette([[-2.12,.37],[-2.13,.60],[-1.75,.78],[-.85,.88],[.85,.88],[1.95,.69],[2.16,.48],[2.12,.37]],1.66,.075);
 const glassGeom=silhouette([[-1.17,.85],[-.61,1.37],[.60,1.37],[1.29,.85]],1.39,.035);
 const roofGeom=roundedBox(1.18,.055,1.36,.035),tireGeom=new T.CylinderGeometry(.37,.37,.22,16);tireGeom.rotateX(Math.PI/2);
 const hubGeom=new T.CylinderGeometry(.18,.18,.235,12);hubGeom.rotateX(Math.PI/2);
 const ringCars=[],openCars=[];
 const bumperGeom=roundedBox(.055,.15,1.3,.025),mirrorGeom=roundedBox(.24,.13,.16,.04),sillGeom=new T.BoxGeometry(2.85,.065,.035),handleGeom=new T.BoxGeometry(.21,.045,.035),pillarGeom=new T.BoxGeometry(.075,.48,1.44),tailGeom=new T.BoxGeometry(.045,.14,.33),headGeom=new T.BoxGeometry(.04,.12,.36),headMat=material('#fff0cb',{emissive:'#fff0cb',emissiveIntensity:.5});
 function car(parent,isGold=false){
  const group=new T.Group();parent.add(group);mesh(bodyGeom,isGold?gold:white,group);mesh(glassGeom,glass,group);
  const roof=mesh(roofGeom,isGold?gold:white,group);roof.position.set(-.02,1.40,0);
  const bumper=mesh(bumperGeom,chrome,group);bumper.position.set(2.17,.44,0);
  const pillar=mesh(pillarGeom,isGold?gold:white,group);pillar.position.set(.0,1.07,0);
  for(const z of [-.91,.91]){
   const mirror=mesh(mirrorGeom,isGold?gold:white,group);mirror.position.set(.85,.94,z);
   const sill=mesh(sillGeom,black,group);sill.position.set(0,.42,z*.95);
   const handle=mesh(handleGeom,chrome,group);handle.position.set(-.45,.81,z*.95);
  }
  const wheels=[];for(const x of [-1.34,1.35])for(const z of [-.85,.85]){const w=new T.Group();w.position.set(x,.37,z);mesh(tireGeom,black,w);mesh(hubGeom,chrome,w);group.add(w);wheels.push(w);}
  const tailMat=material('#9c252b',{emissive:'#f52e32',emissiveIntensity:.4,roughness:.35});
  for(const z of [-.53,.53]){let tail=mesh(tailGeom,tailMat,group);tail.position.set(-2.17,.60,z);const head=mesh(headGeom,headMat,group);head.position.set(2.18,.62,z);}
  return {group,wheels,tailMat};
 }
 for(let i=0;i<22;i++)ringCars.push(car(ring,i===0));for(let i=0;i<6;i++)openCars.push(car(straight,i===2));
 // Brake-wave wash lies on the road, not an invented measurement or screen panel.
 const waveWash=mesh(new T.RingGeometry(34.95,41.05,48,1,-.58,1.16),new T.MeshBasicMaterial({color:'#ff6559',transparent:true,opacity:.22,depthWrite:false}),ring);waveWash.rotation.x=-Math.PI/2;waveWash.position.y=-.145;waveWash.castShadow=false;
 function arcArrow(radius,start,sweep,color){
  const g=new T.Group();const points=Array.from({length:25},(_,i)=>{const a=start+sweep*i/24;return [radius*Math.cos(a),.08,radius*Math.sin(a)];});line(points,color,.17,g);
  const end=start+sweep,head=mesh(new T.ConeGeometry(.68,1.75,16),material(color,{roughness:.6}),g);head.position.set(radius*Math.cos(end),.08,radius*Math.sin(end));const v=new T.Vector3(-Math.sin(end)*Math.sign(sweep),0,Math.cos(end)*Math.sign(sweep));head.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),v);return g;
 }
 const carArrow=arcArrow(45.0,-.6,.65,'#7cdac7'),waveArrow=arcArrow(30.3,.4,-.8,'#fa7768');ring.add(carArrow,waveArrow);
 // A second view of the mechanism: authored open-road example, not a new data set.
 const strip=mesh(new T.BoxGeometry(270,.22,7.8),asphalt,straight);strip.position.y=-.33;
 const straightDashGeom=new T.BoxGeometry(1.5,.025,.10);
 for(let i=-30;i<70;i++)for(const z of [-3.3,3.3]){const dash=mesh(straightDashGeom,paint,straight);dash.position.set(i*3.5,-.19,z);dash.castShadow=false;}
 const bufferLine=mesh(new T.BoxGeometry(1,.03,.045),material('#8be0c9',{emissive:'#28574a',emissiveIntensity:.3}),straight);
 const caps=[-1,1].map(()=>mesh(new T.BoxGeometry(.04,.03,1.25),material('#8be0c9'),straight));
 const motion=makeRingMotion();let lastStats={};
 const keyLight=scene.children.find(o=>o.isDirectionalLight&&o.castShadow);
 function posOf(state,i){return new T.Vector3(state.cars[i].x,0,state.cars[i].z);}
 function tracking(state,i){const car=state.cars[i],p=posOf(state,i),tan=new T.Vector3(-Math.sin(car.theta),0,Math.cos(car.theta)),normal=new T.Vector3(Math.cos(car.theta),0,Math.sin(car.theta));return {p:p.clone().addScaledVector(tan,-12).addScaledVector(normal,8.5).add(new T.Vector3(0,7.8,0)),look:p.clone().addScaledVector(tan,2)};}
 const wide={p:new T.Vector3(74,94,88),look:new T.Vector3(0,0,0)};
 function blend(a,b,u){u=smooth(u);return {p:a.p.clone().lerp(b.p,u),look:a.look.clone().lerp(b.look,u)};}
 function fade(t,a,b){return smooth((t-a)/.4)*(1-smooth((t-b+.4)/.4));}
 function labels(items){document.querySelector('#annotations').innerHTML=items.map(({p,word,color='#e3e8df',size=29})=>{const q=S.project(p);return q.visible&&q.x>110&&q.x<cfg.width-110&&q.y>120&&q.y<cfg.height-80?`<text x="${q.x}" y="${q.y}" text-anchor="middle" fill="${color}" stroke="#10212b" stroke-width="2" paint-order="stroke" font-family="Doc" font-size="${size}" font-weight="700">${word}</text>`:'';}).join('');}
 function place(c,state){c.group.position.set(state.x,-.19,state.z);c.group.rotation.y=state.theta===undefined?0:-state.theta-Math.PI/2;for(const w of c.wheels)w.rotation.z=-state.distance/.37;c.tailMat.emissiveIntensity=state.acceleration<-.12?3.7:.38;}
 function seek(t){
  const onStraight=t>=C.room&&t<C.closing+1.6;ring.visible=!onStraight;straight.visible=onStraight;
  const episode=t<C.gold?16+t:Math.max(0,t-C.gold),state=motion.state(episode);
  ringCars.forEach((c,i)=>place(c,state.cars[i]));
  waveWash.visible=state.amplitude>4;waveWash.rotation.z=-state.jamAngle;
  waveWash.material.opacity=.06+.15*smooth((state.amplitude-4)/12);
  carArrow.visible=waveArrow.visible=t>=C.forward&&t<C.disclosure;
  carArrow.rotation.y=-(state.cars[6].theta+.5);waveArrow.rotation.y=-state.jamAngle;
  let cam;
  if(t<C.gold){cam=blend(tracking(state,0),wide,(t-3.2)/6.8);}
  else if(t<C.behind){cam=tracking(state,0);}
  else if(t<C.next){cam=blend(tracking(state,0),tracking(state,1),(t-C.behind)/.8);}
  else if(t<C.queue){cam=blend(tracking(state,1),tracking(state,2),(t-C.next)/.65);}
  else{cam=blend(tracking(state,2),wide,(t-C.queue)/3.7);}
  if(t>=C.join+1&&t<C.disclosure){
   const a=state.jamAngle,p=new T.Vector3(38*Math.cos(a),0,38*Math.sin(a)),n=new T.Vector3(Math.cos(a),0,Math.sin(a));
   const close={p:p.clone().addScaledVector(n,32).add(new T.Vector3(0,42,0)),look:p.clone()};
   cam=blend(wide,close,(t-C.join-1)/1.7);if(t>C.pattern-.4)cam=blend(cam,wide,(t-C.pattern+.4)/1.5);
  }
  let annotation=[];
  if(onStraight){
   const u=t-C.room,cars=bufferState(u);openCars.forEach((c,i)=>place(c,cars[i]));const p=new T.Vector3(cars[2].x,0,0);
   cam={p:p.clone().add(new T.Vector3(-13,13,24)),look:p.clone().add(new T.Vector3(8,0,0))};
   if(t>C.cure)cam.p.add(new T.Vector3(-3,8,5).multiplyScalar(smooth((t-C.cure)/5)));
   const a=cars[2].x+2.35,b=cars[3].x-2.35;bufferLine.position.set((a+b)/2,-.155,0);bufferLine.scale.x=b-a;
   caps[0].position.set(a,-.15,0);caps[1].position.set(b,-.15,0);const show=t>C.room+.6&&t<C.cure;bufferLine.visible=show;caps.forEach(o=>o.visible=show);
   if(show)annotation.push({p:[(a+b)/2,.1,-2.5],word:'ROOM TO REACT',color:'#9fe4cf',size:28});
   lastStats={mode:'buffer',gap:b-a,carCount:6};
  }else{
   if(t>=C.closing+1.6){cam=blend(tracking(state,0),wide,(t-C.closing-1.6)/4.2);}
   if(carArrow.visible&&!(t>C.join+2&&t<C.pattern-.4)){const a=state.cars[6].theta+.8;annotation.push({p:[47*Math.cos(a),.2,47*Math.sin(a)],word:'CARS',color:'#8ee3cc',size:31});const b=state.jamAngle+.2;annotation.push({p:[27*Math.cos(b),.2,27*Math.sin(b)],word:'WAVE',color:'#ff9688',size:31});}
   if(t>C.join+2&&t<C.pattern-.4){for(const [offset,word,color]of [[-.72,'JOIN','#ffad9a'],[.78,'LEAVE','#93e6cb']]){const a=state.jamAngle+offset;annotation.push({p:[42*Math.cos(a),.7,42*Math.sin(a)],word,color,size:33});}}
   lastStats={mode:'ring',minCenterGap:state.minCenterGap,minimumSpeed:Math.min(...state.cars.map(c=>c.speed)),waveSpeed:state.waveWorldSpeed,carCount:22};
  }
  keyLight.position.set((onStraight?bufferState(t-C.room)[2].x:0)-20,65,26);keyLight.target.position.set(onStraight?bufferState(t-C.room)[2].x:0,0,0);keyLight.target.updateMatrixWorld();
  camera.position.copy(cam.p);camera.lookAt(cam.look);camera.updateProjectionMatrix();camera.updateMatrixWorld();
  let title={heading:'',opacity:1};
  if(t>.7&&t<6.0)title={heading:'NO CRASH.\nNO ROADWORKS.',size:66,opacity:fade(t,.7,6)};
  else if(t>=6&&t<C.wave)title={heading:'NO BLOCKAGE.',size:76,opacity:fade(t,6,C.wave)};
  else if(t>=C.wave&&t<C.gold+.2)title={heading:'A WAVE.',color:'#8fddc9',size:88,opacity:fade(t,C.wave,C.gold+.2)};
  else if(t>=C.gold+.3&&t<C.behind)title={heading:'ONE SMALL BRAKE.',color:'#e3bd77',size:64,opacity:fade(t,C.gold+.3,C.behind)};
  else if(t>=C.behind&&t<C.queue)title={heading:'A LITTLE LATER.',size:67,opacity:fade(t,C.behind,C.queue)};
  else if(t>=C.backwards&&t<C.join+1.3)title={heading:'THE WAVE\nMOVES BACK.',color:'#f19684',size:73,opacity:fade(t,C.backwards,C.join+1.3)};
  else if(t>=C.pattern&&t<C.disclosure)title={heading:'NOT THE SAME CARS.\nTHE SAME PATTERN.',size:62,opacity:fade(t,C.pattern,C.disclosure)};
  else if(t>=C.room+.3&&t<C.cure)title={heading:'SPACE IS A BUFFER.',color:'#95e1ca',size:63,opacity:fade(t,C.room+.3,C.cure)};
  else if(t>=C.cure&&t<C.closing)title={heading:'NOT A CURE-ALL.',size:63,opacity:fade(t,C.cure,C.closing)};
  else if(t>=C.final-.3)title={heading:'YOU DROVE\nTHROUGH A WAVE.',size:74,opacity:fade(t,C.final-.3,cfg.duration-.5)};
  text(title);labels(annotation);
  const end=smooth((t-(cfg.duration-.8))/.8);document.querySelector('#stage').style.opacity=1-end;document.querySelector('#annotations').style.opacity=1-end;document.querySelector('#disclosure').style.opacity=1-end;
 }
 return {seek,stats:()=>lastStats};
}
