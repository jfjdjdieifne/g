#!/usr/bin/env python3
"""Software-rendered XYZ cartographic stage with a perspective camera.
Raised Colombia slab, side-wall geometry, shadow on the sea/map plane,
elevated route arcs and world-anchored upright English labels.
This is actual perspective geometry, not terrain/photorealism or a globe.
"""
import argparse
import json
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import ww2demo_v3 as base
from production_policy import enforce_display, enforce_design

ROOT=Path(__file__).resolve().parents[1]
BUILD=Path('/home/user/build/ww2_demo_v4_depth')
W,H,FPS,DUR=1920,1080,24,16
# Wider world coverage prevents atlas-edge holes during the tilted camera orbit.
base.AW,base.AH=7680,5760
base.BUILD=BUILD
DISPLAY_PATH=ROOT/'engine/projects/ww2_demo/v4_depth/display.json'
DISPLAY=enforce_display(json.loads(DISPLAY_PATH.read_text()))
enforce_design(DISPLAY['design'])
TEXTS=DISPLAY['texts']
LAND_Z=.52
GOLD=(244,211,105)
WHITE=(243,242,228)
FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
TEXT_CACHE={}


def world(lon,lat,z=0):
    return np.array([(lon-base.ALON)*base.COS,lat-base.ALAT,z],dtype=float)


class Camera:
    def __init__(self,t):
        lon,lat,span,wide=base.camera(t)
        # A gentle lateral orbit produces height-dependent parallax.
        yaw=math.radians(-10+18*base.interval(t,0,12))
        tilt=math.radians(43-19*wide)
        distance=span/(2*math.tan(math.radians(21)))
        self.target=world(lon,lat,.10)
        self.eye=self.target+distance*np.array([math.sin(yaw)*math.sin(tilt),
                                              -math.cos(yaw)*math.sin(tilt),math.cos(tilt)])
        forward=(self.target-self.eye)/distance
        right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right)
        up=np.cross(right,forward)
        self.R=np.stack([right,-up,forward])
        self.f=W/(2*math.tan(math.radians(21)))
        self.wide=wide

    def project(self,pts):
        pts=np.asarray(pts,float)
        q=(pts-self.eye)@self.R.T
        return np.column_stack([W/2+self.f*q[:,0]/q[:,2],H/2+self.f*q[:,1]/q[:,2],q[:,2]])

    def plane_matrix(self,z):
        # Homography is induced by a genuine 3D camera and a specified Z plane.
        M=np.column_stack([self.R[:,0],self.R[:,1],self.R@([0,0,z]-self.eye)])
        K=np.array([[self.f,0,W/2],[0,self.f,H/2],[0,0,1.]])
        uv_to_xy=np.array([[1/base.AK,0,-base.AW/(2*base.AK)],
                           [0,-1/base.AK,base.AH/(2*base.AK)],[0,0,1.]])
        return K@M@uv_to_xy

    def plane(self,image,z,resample=Image.Resampling.BICUBIC):
        inv=np.linalg.inv(self.plane_matrix(z));inv/=inv[2,2]
        return image.transform((W,H),Image.Transform.PERSPECTIVE,tuple(inv.flat)[:8],resample)


def text(img,xy,key,size,alpha=1,color=WHITE,anchor='mm'):
    if alpha<=0:return
    value=TEXTS[key]
    cache=(value,size,color)
    if cache not in TEXT_CACHE:
        f=ImageFont.truetype(str(FONT),size)
        box=f.getbbox(value)
        lay=Image.new('RGBA',(math.ceil(f.getlength(value))+20,size*2))
        ImageDraw.Draw(lay).text((10,size),value,font=f,fill=color+(255,),anchor='lm')
        TEXT_CACHE[cache]=lay
    lay=TEXT_CACHE[cache].copy()
    lay.putalpha(lay.getchannel('A').point(lambda p:round(p*min(1,alpha))))
    x,y=xy;x-=lay.width/2 if anchor[0]=='m' else lay.width if anchor[0]=='r' else 0;y-=lay.height/2
    shadow=Image.new('RGBA',lay.size,(3,8,25,0));shadow.putalpha(lay.getchannel('A').point(lambda p:round(p*.7)))
    img.paste(shadow,(round(x+1),round(y+3)),shadow)
    img.paste(lay,(round(x),round(y)),lay)


def ribbon(img,cam,path,progress,color=GOLD,width=5):
    if progress<=0:return
    pts=cam.project(path[:max(2,int(progress*len(path)))])[:,:2]
    lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    line=[tuple(p) for p in pts]
    d.line(line,fill=(7,12,30,230),width=width+3,joint='curve')
    d.line(line,fill=color+(255,),width=width,joint='curve')
    x,y=line[-1];d.ellipse((x-5,y-5,x+5,y+5),fill=WHITE+(255,))
    img.paste(lay,(0,0),lay)


def slab_walls(cam,rings):
    # Explicit vertical side quads, sorted far -> near. Not a drop-shadow trick.
    faces=[]
    light=np.array([-.5,-.7,.5]);light/=np.linalg.norm(light)
    for ring in rings:
        for a,b in zip(ring,ring[1:]+ring[:1]):
            wa=world(*a,0);wb=world(*b,0)
            edge=wb-wa
            if np.linalg.norm(edge)<.014:continue
            quad=np.stack([wa,wb,wb+[0,0,LAND_Z],wa+[0,0,LAND_Z]])
            projected=cam.project(quad)
            if np.any(projected[:,2]<=0):continue
            if (projected[:,0].max()<0 or projected[:,0].min()>W or projected[:,1].max()<0 or projected[:,1].min()>H):continue
            normal=np.array([edge[1],-edge[0],0.]);normal/=np.linalg.norm(normal)
            intensity=.58+.30*abs(float(normal@light))
            color=tuple(int(c*intensity) for c in (147,120,55))
            faces.append((float(projected[:,2].mean()),[tuple(p) for p in projected[:,:2]],color))
    return sorted(faces,key=lambda f:f[0],reverse=True)


class Demo:
    def __init__(self):
        BUILD.mkdir(parents=True,exist_ok=True)
        atlas,col=base.make_atlas()
        self.top=atlas.copy()
        self.col=col
        self.floor=atlas.copy()
        self.floor.paste(base.LAND,(0,0),col)
        # Directional contact shadow is cast onto Z=0 from the slab above it.
        shadow=col.transform(col.size,Image.Transform.AFFINE,(1,0,18,0,1,-28),Image.Resampling.BILINEAR)
        self.shadow=shadow.filter(ImageFilter.GaussianBlur(18))
        self.rings=[]
        for poly in base.polygons('COL'):
            # Small offshore islands stay on the map plane; main land gets a slab.
            ring=poly[0]
            if len(ring)>100:self.rings.append(ring)
        route=base.bezier(base.MED,base.MIA,(-83,16))
        self.route=np.stack([world(*p,LAND_Z*(1-i/(len(route)-1))+.10*i/(len(route)-1)
                                          +2.4*math.sin(math.pi*i/(len(route)-1)))
                             for i,p in enumerate(route)])
        self.route_shadow=np.stack([world(*p,.03) for p in route])
        self.convoys=[]
        for start,control in [((-74.6,9.3),(-74.3,7.5)),((-76.4,5.2),(-76.5,6.4)),((-74.2,5.2),(-74.1,6.2))]:
            points=base.bezier(start,base.MED,control)
            if not all(base.contains('COL',p) for p in points):raise RuntimeError('Offshore convoy')
            self.convoys.append(np.stack([world(*p,LAND_Z+.05) for p in points]))
        if not base.contains('USA',base.MIA):raise RuntimeError('Offshore Miami')
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
        self.vig=np.clip(1-.14*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2),.72,1)

    def render(self,t):
        cam=Camera(t)
        img=cam.plane(self.floor,0)
        sh=cam.plane(self.shadow,0,Image.Resampling.BILINEAR)
        img.paste((6,10,27),(0,0),sh.point(lambda p:round(p*.48)))
        d=ImageDraw.Draw(img)
        for _,face,color in slab_walls(cam,self.rings):d.polygon(face,fill=color)
        mask=cam.plane(self.col,LAND_Z,Image.Resampling.BILINEAR)
        top=cam.plane(self.top,LAND_Z)
        operational=base.interval(t,11.7,13.3)
        if operational:top=Image.blend(top,Image.new('RGB',(W,H),base.RED),operational*.52)
        img.paste(top,(0,0),mask)
        p=base.interval(t,5.65,8.5)
        if p:
            # Arc shadow reveals that the path is above, not painted onto, the map.
            q=cam.project(self.route_shadow[:max(2,int(len(self.route)*p))])[:,:2]
            lay=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(lay)
            ld.line([tuple(a) for a in q],fill=(3,7,20,85),width=8)
            lay=lay.filter(ImageFilter.GaussianBlur(4));img.paste(lay,(0,0),lay)
            ribbon(img,cam,self.route,p)
        for i,route in enumerate(self.convoys):
            p=base.interval(t,11.9+i*.35,13.2+i*.35)
            if p:
                ribbon(img,cam,route,p,WHITE,4)
                pos=route[min(len(route)-1,int(p*(len(route)-1)))]
                # Low-poly bevelled vehicle: eight XYZ vertices, not a floating popup.
                box=np.array([[-.06,-.025,0],[.06,-.025,0],[.06,.025,0],[-.06,.025,0],
                              [-.045,-.021,.05],[.045,-.021,.05],[.045,.021,.05],[-.045,.021,.05]])+pos
                scr=cam.project(box)[:,:2];d=ImageDraw.Draw(img)
                for face,color in [([0,1,5,4],(133,145,164)),([1,2,6,5],(112,126,150)),([4,5,6,7],WHITE)]:
                    d.polygon([tuple(scr[j]) for j in face],fill=color)
        # Upright billboards stay readable; their anchors and pin masts live in XYZ.
        mx,my,_=cam.project([world(*base.MED,LAND_Z)])[0]
        lx,ly,_=cam.project([world(*base.MED,LAND_Z+.48)])[0]
        d=ImageDraw.Draw(img)
        d.line([(mx,my),(lx,ly)],fill=WHITE,width=2)
        d.ellipse((mx-6,my-6,mx+6,my+6),fill=WHITE,outline=(12,18,42),width=2)
        text(img,(lx-140+280*cam.wide,ly-43),'medellin',30)
        if cam.wide>.78:
            x,y,_=cam.project([world(*base.MIA,.10)])[0]
            if 40<x<W-180 and 60<y<H-90:
                d.ellipse((x-5,y-5,x+5,y+5),fill=WHITE)
                text(img,(x+38,y-22),'miami',30,alpha=base.interval(t,5.1,5.8),anchor='lm')
        text(img,(W-72,72),'eyebrow',23,alpha=.58,anchor='rm')
        intro=base.interval(t,.25,.9)*(1-base.interval(t,2.3,2.85))
        text(img,(1430,226),'intro',39,alpha=intro)
        text(img,(1430,292),'name',24,alpha=intro*.72)
        captions=[('network',base.interval(t,3,3.5)*(1-base.interval(t,8.7,9.2))),
                  ('hunt',base.interval(t,11.5,12.1)*(1-base.interval(t,14.2,14.7)))]
        for key,alpha in captions:text(img,(W/2,H-72),key,29,alpha=alpha)
        ending=base.interval(t,14.2,14.85)
        if ending:
            img=Image.blend(img,Image.new('RGB',(W,H),base.NAVY),ending*.76)
            text(img,(W/2,H/2-20),'ending',55,alpha=ending)
            text(img,(W/2,H/2+68),'date',26,alpha=ending,color=GOLD)
        arr=np.asarray(img,dtype=np.float32)*self.vig[:,:,None]
        arr*=base.interval(t,0,.5)*(1-base.interval(t,15.5,16))
        return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');args=parser.parse_args()
    demo=Demo()
    for t in [1.8,7.8,13.8]:demo.render(t).save(BUILD/f'preview_{t:.1f}.jpg',quality=95)
    if args.preview:return
    ff=imageio_ffmpeg.get_ffmpeg_exe();silent=BUILD/'v4_silent.mp4'
    with (BUILD/'encode.log').open('w') as log:
        p=subprocess.Popen([ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
            '-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(DUR*FPS):
                p.stdin.write(demo.render(n/FPS).tobytes())
                if n%48==0:print(f'{n}/{DUR*FPS}',flush=True)
        finally:p.stdin.close()
        if p.wait():raise RuntimeError('Encode failed')
    # Reuse already aligned, restrained synthesis; no added loud effects.
    base.BUILD=BUILD
    temp=base.finish_audio(silent)
    out=BUILD/'escobar_ww2drive_v4_depth_en.mp4'
    temp.replace(out)
    print(f'DONE {out} ({out.stat().st_size} bytes)',flush=True)

if __name__=='__main__':main()
