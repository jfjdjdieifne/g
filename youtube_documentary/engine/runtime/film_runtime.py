"""Shared source I/O, attribution and original-pixel scene preparation.
Film-specific subjects, silhouettes, crops and timeline decisions belong in profiles.
"""
import math,subprocess,wave
from pathlib import Path
from functools import lru_cache
import numpy as np,cv2,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from photo_depth import view,smooth,PhotoDepth
FF=imageio_ffmpeg.get_ffmpeg_exe()
cv2.setNumThreads(2)

def decode(path,start=0,dur=None):
    args=[FF,'-v','error','-ss',str(start),'-i',str(path)]
    if dur is not None:args+=['-t',str(dur)]
    return np.frombuffer(subprocess.check_output(args+['-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4').astype(np.float64)

def wav(path,x):
    if x.ndim==1:x=np.column_stack([x,x])
    with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())

def rms(x):return float(np.sqrt(np.mean(x*x)))

class FilmVisuals:
    def __init__(self,asset_dirs,size,font_dir,depth_specs):
        self.asset_dirs=tuple(map(Path,asset_dirs));self.W,self.H=size;self.font_dir=Path(font_dir);self.depth_specs=depth_specs
    @lru_cache(maxsize=32)
    def image(self,name):
        for root in self.asset_dirs:
            if (root/name).exists():return np.array(Image.open(root/name).convert('RGB'))
        raise FileNotFoundError(name)
    @lru_cache(maxsize=40)
    def font(self,size,bold=False):
        file='DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf';path=self.font_dir/file
        if not path.exists():path=Path('/usr/share/fonts/truetype/dejavu')/file
        return ImageFont.truetype(str(path),size)
    def caption(self,frame,text,right=False):
        frame=frame.copy();ramp=np.linspace(0,.68,110,dtype=np.float32)[:,None,None];frame[-110:]=(frame[-110:].astype(np.float32)*(1-ramp)).astype(np.uint8)
        im=Image.fromarray(frame);d=ImageDraw.Draw(im);f=self.font(32);x=64
        if right:x=self.W-64-d.textlength(text,font=f)
        d.text((x,self.H-57),text,font=f,fill=(224,224,215),stroke_width=2,stroke_fill=(12,14,16));return np.array(im)
    def region(self,name,c0,c1,span0,span1,u,yaw=0):
        k=smooth(u);center=np.array(c0)*(1-k)+np.array(c1)*k
        return view(self.image(name),center,span0*(1-k)+span1*k,(self.W,self.H),yaw=yaw*math.sin(math.pi*k))
    @lru_cache(maxsize=8)
    def depth_scene(self,name):
        im=self.image(name);h,w=im.shape[:2];mask=np.zeros((h,w),np.uint8);spec=self.depth_specs[name]
        if [w,h]!=spec['native_size']:raise ValueError('Silhouette/source dimensions differ')
        cv2.fillPoly(mask,[np.int32(spec['polygon'])],255)
        if spec.get('refine'):
            x0,y0,x1,y1=spec['refine_region'];gc=np.zeros((h,w),np.uint8);gc[y0:y1,x0:x1]=cv2.GC_PR_BGD;gc[mask>0]=cv2.GC_PR_FGD;gc[cv2.erode(mask,np.ones((9,9),np.uint8))>0]=cv2.GC_FGD
            cv2.setRNGSeed(193);cv2.grabCut(im,gc,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),5,cv2.GC_INIT_WITH_MASK);mask=np.where((gc==1)|(gc==3),255,0).astype(np.uint8)
            for x,y,r in spec.get('include_circles',[]):cv2.circle(mask,(x,y),r,255)
        return PhotoDepth(im,mask)
