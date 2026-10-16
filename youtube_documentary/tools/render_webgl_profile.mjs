#!/usr/bin/env node
/* Shared headless WebGL profile capture. Dependencies stay in an external cache.
 * DOCENGINE_NODE_MODULES, DOCENGINE_PYTHON select the installed toolchain.
 * --stills 0,3,8 captures authoring compositions; default captures encoded movie.
 */
import fs from 'node:fs';import path from 'node:path';import http from 'node:http';
import {fileURLToPath,pathToFileURL} from 'node:url';import {spawn,spawnSync} from 'node:child_process';import {once} from 'node:events';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2),project=path.resolve(args[0]||'');
const stillAt=args.indexOf('--stills'),mode=stillAt>=0?'stills':'render';
const deps=process.env.DOCENGINE_NODE_MODULES||path.join(ROOT,'engine/node_modules');
const python=process.env.DOCENGINE_PYTHON||'python3';
const gate=spawnSync(python,[path.join(ROOT,'tools/style_contract.py'),'check','--project',project],{stdio:'inherit'});if(gate.status!==0)process.exit(gate.status||1);
const displayGate=spawnSync(python,[path.join(ROOT,'tools/production_policy.py'),path.join(project,'display_manifest.json')],{stdio:'inherit'});if(displayGate.status!==0)process.exit(displayGate.status||1);
const cfg=JSON.parse(fs.readFileSync(path.join(project,'render.json'),'utf8'));
const out=path.resolve(process.env.DOCENGINE_BUILD||cfg.build);fs.mkdirSync(out,{recursive:true});
const {default:puppeteer}=await import(pathToFileURL(path.join(deps,'puppeteer-core/lib/esm/puppeteer/puppeteer-core.js')));
const {default:chromium}=await import(pathToFileURL(path.join(deps,'@sparticuz/chromium/build/esm/index.js')));
// Minimal hosts may lack NSS/NSPR; use the matching packaged shared libraries.
const {inflate}=await import(pathToFileURL(path.join(deps,'@sparticuz/chromium/build/esm/lambdafs.js')));
const browserLibs=await inflate(path.join(deps,'@sparticuz/chromium/bin/al2023.tar.br'));
const ff=spawnSync(python,['-c','import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8'});if(ff.status!==0)throw Error(ff.stderr);const FF=ff.stdout.trim();
const html=`<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Doc;src:url('/fonts/DejaVuSans.ttf')}@font-face{font-family:Doc;src:url('/fonts/DejaVuSans-Bold.ttf');font-weight:700}
*{box-sizing:border-box}body{margin:0;overflow:hidden;background:#101e28;color:#f2ede1;font-family:Doc,sans-serif}canvas{display:block}#title,#subtitle{position:absolute;pointer-events:none;white-space:pre-line;max-width:850px}#title{font-weight:700;line-height:1.02;letter-spacing:-2px}#subtitle{font-size:25px;color:#b3c2c5;line-height:1.4}#disclosure{position:absolute;right:48px;bottom:32px;font-size:20px;color:#bbc8ca;letter-spacing:1px;pointer-events:none}#annotations{position:absolute;inset:0;pointer-events:none}
</style><script type="importmap">{"imports":{"three":"/vendor/three/build/three.module.js","three/addons/":"/vendor/three/examples/jsm/"}}</script></head><body><div id="stage"></div><div id="title"></div><div id="subtitle"></div><svg id="annotations" width="${cfg.width}" height="${cfg.height}"></svg><div id="disclosure">EXPLANATORY ANIMATION</div><script type="module">
import {createStage} from '/runtime/webgl_stage.mjs';import {createFilm} from '/project/scene.mjs';
const config=await(await fetch('/params.json')).json();const stage=await createStage(config);const film=await createFilm(stage,config);
window.seek=async t=>{film.seek(t);stage.render();await document.fonts.ready;return {...stage.stats(),...(film.stats?film.stats():{})};};window.ready=true;await window.seek(0);
</script></body></html>`;
const mime={'.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.ttf':'font/ttf','.wav':'audio/wav','.mp3':'audio/mpeg'};
const server=http.createServer((req,res)=>{
 try{
  const u=new URL(req.url,'http://unused');if(u.pathname==='/'){res.setHeader('Content-Type','text/html');res.end(html);return;}
  if(u.pathname==='/params.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(cfg));return;}
  const roots={'/vendor/':deps,'/project/':project,'/runtime/':path.join(ROOT,'engine/runtime'),'/fonts/':path.join(ROOT,'assets_global/fonts')};
  const prefix=Object.keys(roots).find(k=>u.pathname.startsWith(k));if(!prefix){res.writeHead(404);res.end();return;}
  const base=roots[prefix],p=path.resolve(base,decodeURIComponent(u.pathname.slice(prefix.length)));if(!p.startsWith(path.resolve(base)+path.sep)||!fs.existsSync(p)){res.writeHead(404);res.end();return;}
  res.setHeader('Content-Type',mime[path.extname(p)]||'application/octet-stream');fs.createReadStream(p).pipe(res);
 }catch(e){res.writeHead(500);res.end(String(e));}
});await new Promise(r=>server.listen(0,'0.0.0.0',r));console.log('Animation stage listening',server.address().port);
let browser,encoder;
try{
 browser=await puppeteer.launch({executablePath:await chromium.executablePath(),headless:true,env:{...process.env,LD_LIBRARY_PATH:browserLibs+'/lib:'+browserLibs+':'+(process.env.LD_LIBRARY_PATH||'')},args:[...chromium.args.filter(a=>a!=='--disable-gpu'),'--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--hide-scrollbars']});
 const page=await browser.newPage();await page.setViewport({width:cfg.width,height:cfg.height,deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>{errors.push(String(e));console.error('PAGE',String(e));});
 await page.goto('http://127.0.0.1:'+server.address().port,{waitUntil:'networkidle0',timeout:120000});await page.waitForFunction('window.ready === true',{timeout:120000});
 await page.evaluate(()=>document.fonts.ready);const client=await page.createCDPSession();
 async function capture(t,format='jpeg'){
  const clock=Date.now();const stats=await page.evaluate(t=>window.seek(t),t);if(errors.length)throw Error(errors.join('\n'));
  const shot=await client.send('Page.captureScreenshot',{format,quality:format==='jpeg'?94:undefined,fromSurface:true,captureBeyondViewport:false});return {buffer:Buffer.from(shot.data,'base64'),stats:{...stats,captureMs:Date.now()-clock}};
 }
 if(mode==='stills'){
  const times=args[stillAt+1].split(',').map(Number);for(const t of times){const {buffer,stats}=await capture(t,'png');fs.writeFileSync(path.join(out,`author_${t.toFixed(3)}.png`),buffer);console.log('STILL',t,JSON.stringify(stats));}
 }else{
  const frames=Math.round(cfg.duration*cfg.fps),rangeAt=args.indexOf('--frames'),outputAt=args.indexOf('--output');
  const [first,last]=rangeAt>=0?args[rangeAt+1].split(':').map(Number):[0,frames];
  if(!Number.isInteger(first)||!Number.isInteger(last)||first<0||last>frames||last<=first)throw Error('Invalid absolute frame range');
  const dest=path.join(out,outputAt>=0?args[outputAt+1]:(cfg.silent_output||'picture.mp4'));
  const log=fs.openSync(path.join(out,'picture_encode.log'),'w');
  encoder=spawn(FF,['-v','warning','-y','-f','image2pipe','-vcodec','mjpeg','-framerate',String(cfg.fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-threads','2','-crf','19','-maxrate','4500k','-bufsize','9000k','-pix_fmt','yuv420p','-movflags','+faststart',dest],{stdio:['pipe','ignore',log]});
  let fail;encoder.on('error',e=>{fail=e;});encoder.stdin.on('error',e=>{fail=e;});
  const started=Date.now();for(let n=first;n<last;n++){
   const {buffer,stats}=await capture(n/cfg.fps);if(fail)throw fail;
   if(!encoder.stdin.write(buffer))await once(encoder.stdin,'drain');
   if((n-first)%24===0)console.log('FRAME',n,'/',frames,'elapsed',((Date.now()-started)/1000).toFixed(1),JSON.stringify(stats));
  }
  encoder.stdin.end();const [code]=await once(encoder,'exit');fs.closeSync(log);if(code!==0)throw Error('FFmpeg failed '+code);console.log('PICTURE COMPLETE',dest,last-first,'absolute range',first,last);
 }
}finally{if(encoder&&encoder.exitCode===null)encoder.kill('SIGTERM');if(browser)await browser.close();server.close();}
