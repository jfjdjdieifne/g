/* Shared deterministic 3D stage. Film geometry/camera/timing lives in a profile.
 * Not an automatic director or an artistic-quality certificate.
 */
import * as THREE from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
export async function createStage(config) {
  const scene=new THREE.Scene();
  scene.background=new THREE.Color(config.background||'#101e28');
  const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,alpha:false});
  renderer.setPixelRatio(1);renderer.setSize(config.width,config.height);
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=config.exposure||1.15;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  document.querySelector('#stage').appendChild(renderer.domElement);
  const camera=new THREE.PerspectiveCamera(40,config.width/config.height,.1,600);
  const pmrem=new THREE.PMREMGenerator(renderer);
  const environment=new RoomEnvironment();scene.environment=pmrem.fromScene(environment,.04).texture;
  scene.environmentIntensity=config.environmentIntensity??.35;
  environment.dispose();pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xc5e5ed,0x18222a,.75));
  const light=new THREE.DirectionalLight(0xffedcf,3.0);light.position.set(-20,65,26);light.castShadow=true;
  light.shadow.mapSize.set(2048,2048);Object.assign(light.shadow.camera,{left:-65,right:65,top:65,bottom:-65,near:1,far:150});
  light.shadow.bias=-.00025;light.shadow.normalBias=.035;scene.add(light);
  const fill=new THREE.DirectionalLight(0x82bfd7,1.0);fill.position.set(45,25,-35);scene.add(fill);
  function material(color,options={}){if(options.diffuseOnly){const {diffuseOnly,roughness,metalness,...rest}=options;return new THREE.MeshLambertMaterial({color,...rest});}const Mat=options.clearcoat!==undefined?THREE.MeshPhysicalMaterial:THREE.MeshStandardMaterial;return new Mat({color,roughness:.5,metalness:.12,...options});}
  function mesh(geometry,mat,parent=scene){const o=new THREE.Mesh(geometry,mat);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;}
  function roundedBox(w,h,d,r=.08){
    const x=-w/2,y=-h/2,s=new THREE.Shape();
    s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);
    s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
    s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);
    const g=new THREE.ExtrudeGeometry(s,{depth:d,bevelEnabled:true,bevelSize:r*.35,bevelThickness:r*.35,bevelSegments:2,steps:1,curveSegments:4});g.translate(0,0,-d/2);return g;
  }
  function line(points,color=0x86d8c5,radius=.025,parent=scene){
    const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));
    return mesh(new THREE.TubeGeometry(curve,Math.max(6,points.length*3),radius,5,false),material(color,{roughness:.7}),parent);
  }
  function project(p){const v=new THREE.Vector3(...p).project(camera);return {x:(v.x*.5+.5)*config.width,y:(-.5*v.y+.5)*config.height,visible:v.z<1&&v.z>-1};}
  const label=document.querySelector('#title'),sub=document.querySelector('#subtitle');
  function text({heading='',detail='',color='#f2ede1',x=68,y=64,size=70,opacity=1}={}){
    label.textContent=heading;sub.textContent=detail;label.style.color=color;label.style.left=x+'px';label.style.top=y+'px';label.style.fontSize=size+'px';label.style.opacity=opacity;
    sub.style.left=x+'px';sub.style.top=(y+heading.split('\n').length*size*1.02+24)+'px';sub.style.opacity=opacity;
  }
  // Batch repeated originals without changing the author's object hierarchy or motion.
  // Parent visibility, per-material brake changes, world transforms and shadows survive.
  // Originals are restored immediately after each draw, so seek/stats remain truthful.
  let batches;
  function draw(){
    if(config.batchMeshes===false){renderer.render(scene,camera);return;}
    if(!batches){
      const groups=new Map();scene.traverse(o=>{if(!o.isMesh||o.isInstancedMesh||Array.isArray(o.material))return;
        const key=[o.geometry.uuid,o.material.uuid,o.castShadow,o.receiveShadow].join(':');if(!groups.has(key))groups.set(key,[]);groups.get(key).push(o);
      });
      batches=[...groups.values()].filter(g=>g.length>1).map(objects=>{const first=objects[0],instance=new THREE.InstancedMesh(first.geometry,first.material,objects.length);instance.castShadow=first.castShadow;instance.receiveShadow=first.receiveShadow;instance.frustumCulled=false;instance.instanceMatrix.setUsage(THREE.DynamicDrawUsage);scene.add(instance);return {objects,instance};});
    }
    scene.updateMatrixWorld(true);const restore=[];
    for(const {objects,instance}of batches){let count=0;
      for(const o of objects){let visible=o.visible;for(let p=o.parent;visible&&p;p=p.parent)visible=p.visible;
        if(visible)instance.setMatrixAt(count++,o.matrixWorld);restore.push([o,o.visible]);o.visible=false;
      }
      instance.count=count;instance.visible=count>0;instance.instanceMatrix.needsUpdate=true;
    }
    try{renderer.render(scene,camera);}finally{for(const [o,v]of restore)o.visible=v;}
  }
  return {THREE,scene,renderer,camera,material,mesh,roundedBox,line,project,text,config,
    render:draw,
    stats(){return {drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,renderer:renderer.getContext().getParameter(renderer.getContext().RENDERER)};}};
}
