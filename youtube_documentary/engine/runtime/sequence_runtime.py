"""Profile-driven AV sequence renderer. Timing/content live in film profiles.
Video stays at native speed and in its full frame; source logos are never replaced.
"""
import json,math,subprocess,hashlib,shutil
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from film_runtime import FF,FilmVisuals
from photo_depth import smooth,view,document

class SequenceFilm:
    def __init__(self,profile,plan):
        self.p=profile;self.plan=plan;self.W,self.H=profile.SIZE;self.fps=profile.FPS
        self.visuals=FilmVisuals(profile.ASSET_DIRS,profile.SIZE,profile.FONT_DIR,getattr(profile,'DEPTH_SPECS',{}))
        self.cache=profile.BUILD/'video_frames';self.cache.mkdir(exist_ok=True,parents=True)
    def prepare_video(self):
        for s in self.plan['shots']:
            if s['kind']!='video':continue
            folder=self.cache/s['id'];folder.mkdir(exist_ok=True);n=s['last']-s['first']
            fingerprint=json.dumps([s['path'],Path(s['path']).stat().st_mtime_ns,s['source_in'],n,self.fps,s.get('freeze_tail'),s.get('freeze_duration',1.2)])
            if (folder/'complete').exists() and (folder/'complete').read_text()==fingerprint:continue
            for f in folder.glob('*.jpg'):f.unlink()
            subprocess.run([FF,'-v','error','-ss',str(s['source_in']),'-i',s['path'],'-vf',f'fps={self.fps},scale=1280:-2'+(f",tpad=stop_mode=clone:stop_duration={s.get('freeze_duration',1.2)}" if s.get('freeze_tail') else ',tpad=stop_mode=clone:stop_duration=0.12'),'-frames:v',str(n),'-q:v','2','-y',str(folder/'%05d.jpg')],check=True)
            if len(list(folder.glob('*.jpg')))!=n:raise ValueError('Not enough source frames: '+s['id'])
            (folder/'complete').write_text(fingerprint)
    def text(self,frame,s,n):
        im=Image.fromarray(frame);layer=Image.new('RGBA',(self.W,self.H));d=ImageDraw.Draw(layer)
        lines=s.get('credit',[]);base=self.H-42-42*len(lines)
        if lines:
            for y in range(max(0,base-36),self.H):
                alpha=round(185*min(1,(y-base+36)/80));d.line((0,y,self.W,y),fill=(3,7,10,alpha))
            for i,line in enumerate(lines):
                font=self.visuals.font(31,i==0 and bool(s.get('speaker')));x=self.W-54-d.textlength(line,font=font) if s.get('watermark') else 54
                d.text((x,base+42*i),line,font=font,fill=(231,231,222),stroke_width=1,stroke_fill=(0,0,0,180))
        if s.get('title_after') is not None and n/self.fps>=s['title_after']:
            k=smooth((n/self.fps-s['title_after'])/.18)
            # Film title only, not a fabricated clipping/name-marker montage.
            d.rectangle((0,0,self.W,base-32),fill=(0,0,0,round(95*k)))
            for line,y in [('PABLO',300),('ESCOBAR',480)]:
                font=self.visuals.font(153,True);w=d.textlength(line,font=font)
                d.text(((self.W-w)/2,y+12*(1-k)),line,font=font,fill=(238,235,225,round(255*k)))
        # Preserve the original lower-left broadcaster bug byte-for-byte after fitting.
        if s.get('watermark'):layer.paste((0,0,0,0),(0,self.H-240,230,self.H))
        return np.array(Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB'))
    def frame(self,n):
        s=next(s for s in self.plan['shots']if s['first']<=n<s['last']);local=n-s['first'];u=local/max(1,s['last']-s['first']-1)
        if s['kind']=='video':
            im=np.array(Image.open(self.cache/s['id']/f'{local+1:05d}.jpg').convert('RGB'));h,w=im.shape[:2];scale=min(self.W/w,self.H/h);a=cv2.resize(im,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_CUBIC)
            out=np.full((self.H,self.W,3),(3,5,7),np.uint8);y=(self.H-a.shape[0])//2;x=(self.W-a.shape[1])//2;out[y:y+a.shape[0],x:x+a.shape[1]]=a
            if s.get('push'):
                if s.get('watermark'):raise ValueError('Cannot push/crop watermarked source')
                z=1+s['push']*smooth(u);out=cv2.warpAffine(out,np.float32([[z,0,self.W*(1-z)/2],[0,z,self.H*(1-z)/2]]),(self.W,self.H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
        elif s['kind']=='depth':
            out=self.visuals.depth_scene(s['asset']).render(s['center'],s['span'],u,self.p.SIZE,travel=.055)
        elif s['kind']=='image':
            im=self.visuals.image(s['asset']);c=np.array(s['center']);move=np.array(s.get('travel',[0,0]));k=smooth(u)
            out=view(im,c+move*k,s['span']*(1-s.get('push',.035)*k),self.p.SIZE,yaw=s.get('yaw',0)*math.sin(math.pi*u))
        else:raise ValueError(s['kind'])
        return self.text(out,s,local)
    def render(self,destination):
        destination=Path(destination)
        if destination.exists() and destination.stat().st_size:
            versions=self.p.BUILD/'versions';versions.mkdir(exist_ok=True)
            previous=versions/(destination.stem+'__'+hashlib.sha256(destination.read_bytes()).hexdigest()[:12]+destination.suffix)
            if not previous.exists():shutil.copy2(destination,previous)
        self.prepare_video();command=[FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{self.W}x{self.H}','-r',str(self.fps),'-i','-','-i',str(self.p.BUILD/'mix.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-threads','4','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',str(self.plan['frames']/self.fps),str(destination)]
        p=subprocess.Popen(command,stdin=subprocess.PIPE)
        try:
            for n in range(self.plan['frames']):
                p.stdin.write(self.frame(n).tobytes())
                if n%120==0:print('FRAME',n,'/',self.plan['frames'],flush=True)
        finally:p.stdin.close()
        if p.wait():raise RuntimeError('Encoder failed')
