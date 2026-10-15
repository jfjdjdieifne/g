#!/usr/bin/env python3
"""30-second narrated opening. Voice-02 exact approved take, no synthetic news.
Real 2019 site photo + clearly identified typeset excerpts + illustrative XYZ
cutaway, NOT a historical reconstruction of the real La Catedral footprint.
Software perspective renderer: face-depth sorting / lighting / model shadows.
"""
import argparse
import json
import math
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
from production_policy import enforce_display,enforce_design,enforce_editorial_review

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine/runtime'))
from xyz_scene import Camera, World, cylinder
PROJECT=ROOT/'engine/projects/escobar_hook30'
BUILD=Path('/home/user/build/escobar_hook30/render')
W,H,FPS,DUR=1920,1080,24,30
MANIFEST=enforce_display(json.loads((PROJECT/'display.json').read_text()))
enforce_design(MANIFEST['design'])
TXT=MANIFEST['texts']
INK=(241,235,219);GOLD=(210,170,103);BG=(10,18,25);CYAN=(90,141,155)
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF=str(ROOT/'DEMO1_ESCOBAR/assets/fonts/PlayfairDisplay.ttf')
FONT_CACHE={};TEXT_CACHE={}


def smooth(x):
    x=max(0.,min(1.,float(x)));return x*x*(3-2*x)
def interval(t,a,b):return smooth((t-a)/(b-a))
def window(t,a,b,c,d):return interval(t,a,b)*(1-interval(t,c,d))


def font(size,serif=False,bold=False):
    path=SERIF if serif else BOLD if bold else SANS
    k=(size,path)
    if k not in FONT_CACHE:FONT_CACHE[k]=ImageFont.truetype(path,size)
    return FONT_CACHE[k]


def label(img,xy,key,size=32,color=INK,alpha=1,serif=False,anchor='mm',bold=False):
    if alpha<=0:return
    s=TXT[key];k=(key,size,color,serif,bold)
    if k not in TEXT_CACHE:
        f=font(size,serif,bold)
        lay=Image.new('RGBA',(math.ceil(f.getlength(s))+40,size*2+20))
        ImageDraw.Draw(lay).text((20,lay.height/2),s,font=f,fill=color+(255,),anchor='lm')
        TEXT_CACHE[k]=lay
    lay=TEXT_CACHE[k].copy();lay.putalpha(lay.getchannel('A').point(lambda p:round(p*alpha)))
    x,y=xy;x-=lay.width/2 if anchor[0]=='m' else lay.width if anchor[0]=='r' else 0;y-=lay.height/2
    sh=Image.new('RGBA',lay.size,(2,5,8,0));sh.putalpha(lay.getchannel('A').point(lambda p:round(p*.7)))
    img.paste(sh,(round(x+1),round(y+2)),sh);img.paste(lay,(round(x),round(y)),lay)




KEYS=[
 (5.4,[18,-24,23],[0,0,.5]),
 (6.9,[13,-18,15],[0,-.4,.6]),
 (8.6,[9,-12,10],[2,-2,.7]),
 (11.3,[10,-7,8],[2.8,.5,.8]),
 (15.,[14,-19,16],[0,-1,.5]),
 (18.4,[7,-13,9],[0,-2,.6]),
 (21.,[-3,-12,7],[0,-3,.7]),
 (24.,[-11,-16,13],[0,-.7,.5]),
 (30.,[-21,-21,23],[0,0,.5])]


def camera(t):
    if t<=KEYS[0][0]:return Camera(KEYS[0][1],KEYS[0][2])
    for a,b in zip(KEYS,KEYS[1:]):
        if a[0]<=t<=b[0]:
            u=interval(t,a[0],b[0]);return Camera(np.array(a[1])*(1-u)+np.array(b[1])*u,np.array(a[2])*(1-u)+np.array(b[2])*u)
    return Camera(KEYS[-1][1],KEYS[-1][2])


class PrisonWorld(World):
    def guard(self,x,y):
        col=(57,65,67)
        # Neutral architectural figure, not a portrait or fabricated evidence.
        cylinder(self,(x-.055,y,.12),(x-.065,y,.43),.045,col)
        cylinder(self,(x+.055,y,.12),(x+.065,y,.43),.045,col)
        self.ball((x,y,.53),.13,col)
        cylinder(self,(x,y,.43),(x,y,.68),.10,col)
        cylinder(self,(x-.1,y,.62),(x-.15,y,.39),.035,col)
        cylinder(self,(x+.1,y,.62),(x+.15,y,.39),.035,col)
        self.ball((x,y,.82),.09,col)


def world_scene(t):
    w=PrisonWorld()
    # Physical model plinth, cutaway building walls, road and restrained materials.
    w.box((0,0,-.55),(16,11,.55),(35,51,57),top=(54,69,68))
    w.box((0,-4.35,.005),(15,.65,.025),(48,57,59))
    w.box((0,-3.1,.006),(.7,2.1,.026),(70,77,74))
    # Football field is documented; placement is explicitly NOT a real floorplan.
    w.box((-3.5,1,.03),(4.3,2.8,.05),(42,66,58))
    for y in [-.25,2.25]:w.line([(-5.45,y,.1),(-1.55,y,.1)],(143,155,129),2)
    for x in [-5.45,-1.55,-3.5]:w.line([(x,-.25,.1),(x,2.25,.1)],(143,155,129),2)
    # Main room, roofless for a readable illustrative cutaway.
    for c,s in [((2.5,2,.04),(4.8,.22,1.8)),((4.8,.5,.04),(.22,3.2,1.8)),((2.5,-1,.04),(4.8,.22,1.1)),((.2,.5,.04),(.22,3.2,1.8))]:
        w.box(c,s,(134,137,125))
    # Stone paving and office detail are artistic staging, not measured history.
    for i in range(9):
        for j in range(5):
            w.box((.5+i*.48,-.68+j*.52,.043),(.465,.505,.018),(105+i%3*3,109,100))
    for i in range(3):
        w.box((4.48,.1+i*.47,.08),(.35,.42,.85),(102,82,57))
        for z in [.37,.65]:w.box((4.28,.1+i*.47,z),(.04,.20,.018),(171,152,115))
    # Desk chair, gently rounded silhouette rather than a floating block.
    w.box((2.7,1.05,.48),(.45,.40,.07),(71,55,42))
    w.box((2.7,1.2,.52),(.45,.06,.48),(88,65,43))
    for x in [2.52,2.88]:
        for y in [.9,1.2]:cylinder(w,(x,y,.05),(x,y,.49),.018,(80,85,78))
    # Football goals and centre circle.
    for x in [-5.45,-1.55]:
        for y in [.65,1.35]:cylinder(w,(x,y,.10),(x,y,.54),.016,(178,182,159))
        cylinder(w,(x,.65,.54),(x,1.35,.54),.016,(178,182,159))
    circle=[(-3.5+.36*math.cos(a),1+.36*math.sin(a),.106) for a in np.linspace(0,math.tau,48)]
    w.line(circle,(143,155,129),1)
    # Lintels and repeated windows provide scale without popup badges.
    for x in [.8,1.8,2.8,3.8]:
        w.box((x,1.86,.6),(.65,.12,.8),(37,58,65))
        w.box((x,1.79,.58),(.7,.06,.04),(180,157,110))
    # Office desk, folders and a telephone as persistent 3D props.
    w.box((2.8,.45,.07),(1.6,.7,.62),(68,51,39),top=(144,111,71))
    w.box((3.2,.46,.71),(.36,.28,.035),(205,190,154))
    w.box((3.2,.46,.75),(.30,.24,.018),(225,216,190))
    w.box((2.35,.43,.7),(.38,.28,.065),(26,31,33))
    w.box((2.35,.43,.78),(.44,.10,.06),(51,58,59))
    for x in [2.22,2.35,2.48]:
        for y in [.33,.40]:w.box((x,y,.77),(.025,.025,.01),(175,169,146))
    # Second building / service shed.
    w.box((-3,-2,.03),(3,1.3,.82),(104,112,107),top=(74,90,88))
    # Perimeter fence. Front has an actual gap with two moving gate leaves.
    pts=[(-6.7,-3.3),(6.7,-3.3),(6.7,3.6),(-6.7,3.6)]
    for a,b in zip(pts,pts[1:]+pts[:1]):
        L=math.dist(a,b);N=math.ceil(L/.9)
        for i in range(N+1):
            u=i/N;x=a[0]*(1-u)+b[0]*u;y=a[1]*(1-u)+b[1]*u
            if abs(y+3.3)<.1 and abs(x)<.8:continue
            w.box((x,y,.02),(.045,.045,1.2),(100,120,123))
        for z in [.35,.7,1.05]:
            if a[1]==b[1]==-3.3:
                w.line([(a[0],a[1],z),(-.8,a[1],z)],(93,115,116),1)
                w.line([(.8,a[1],z),(b[0],b[1],z)],(93,115,116),1)
            else:w.line([(a[0],a[1],z),(b[0],b[1],z)],(93,115,116),1)
    angle=math.radians(82*interval(t,18.6,20.5))
    for side in [-1,1]:
        hinge=side*.8
        end=hinge-side*.8*math.cos(angle)
        yy=-3.3-.8*math.sin(angle)
        for z in [.2,.6,1.05]:w.line([(hinge,-3.3,z),(end,yy,z)],(155,164,145),2)
        w.line([(end,yy,.1),(end,yy,1.1)],(155,164,145),2)
    for x,y in [(-.95,-2.7),(.95,-2.7),(5.8,2.7),(-5.8,2.8)]:w.guard(x,y)
    # Time-driven escape movement; no claim this was the real route.
    if t>=18.6:
        u=interval(t,18.7,21.1)
        w.guard(-.2,-2.4-2.3*u)
        w.line([(-.2,-2.1,.10),(-.2,-2.1-2.65*u,.10)],GOLD,3)
    return w


def route_lines(img,cam,t):
    if not (8.4<t<11.3):return
    p=interval(t,8.5,10.0)
    lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    for end in [[-7,3,1.8],[7,-3,1.8],[6,3,1.8]]:
        a=np.array([2.8,.4,.9]);b=np.array(end);u=np.linspace(0,p,60)
        pts=np.stack([a*(1-v)+b*v+[0,0,1.3*math.sin(math.pi*v)] for v in u])
        q=cam.project(pts)[:,:2]
        d.line([tuple(v) for v in q],fill=GOLD+(200,),width=3)
        x,y=q[-1];d.ellipse((x-4,y-4,x+4,y+4),fill=INK+(255,))
    img.paste(lay,(0,0),lay)


def cover(im,scale=1.,offset=(0,0)):
    ratio=max(W/im.width,H/im.height)*scale
    out=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.LANCZOS)
    x=(out.width-W)/2+offset[0];y=(out.height-H)/2+offset[1]
    return out.crop((round(x),round(y),round(x+W),round(y+H)))


class Demo:
    def __init__(self):
        BUILD.mkdir(parents=True,exist_ok=True)
        self.photo=Image.open(PROJECT/'assets/la_catedral_site_2019.jpg').convert('RGB')
        self.paper=self.paper_texture()
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
        self.vig=np.clip(1-.22*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2),.60,1.)
        self.bg=self.background()
        self.press=[self.make_press(False),self.make_press(True)]
    def background(self):
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
        glow=np.exp(-(((xx-1100)/1100)**2+((yy-450)/700)**2))
        a=np.zeros((H,W,3),np.uint8)
        for i,c in enumerate(BG):a[:,:,i]=(c+glow*(12 if i==0 else 21))
        return Image.fromarray(a)
    def paper_texture(self):
        rng=np.random.default_rng(13);a=rng.normal(0,1.25,(1400,2000)).astype(np.float32)
        out=np.zeros((1400,2000,3),np.uint8)
        for i,c in enumerate((224,216,194)):out[:,:,i]=np.clip(c+a,0,255)
        return Image.fromarray(out)
    def make_press(self,comfort):
        im=self.paper.copy();d=ImageDraw.Draw(im)
        d.text((120,115),TXT['article_header'] if comfort else TXT['front_header'],font=font(52,bold=True),fill=(35,38,37))
        d.text((120,205),(TXT['article_date'] if comfort else TXT['archive']),font=font(26),fill=(83,80,71))
        d.line([(120,265),(1880,265)],fill=(84,79,66),width=3)
        if comfort:
            d.text((120,370),TXT['comfort1'],font=font(100,serif=True),fill=(31,35,35))
            d.text((120,530),TXT['comfort2'],font=font(100,serif=True),fill=(31,35,35))
            d.rectangle((115,640,1380,663),fill=(170,92,62))
            d.text((125,738),TXT['comfort_credit'],font=font(30),fill=(64,64,57))
        else:
            d.text((120,335),TXT['press_title1'],font=font(118,serif=True),fill=(30,34,33))
            d.text((120,485),TXT['press_title2'],font=font(118,serif=True),fill=(30,34,33))
            d.text((125,730),TXT['quote1'],font=font(63,serif=True),fill=(58,59,51))
            d.text((125,820),TXT['quote2'],font=font(63,serif=True),fill=(58,59,51))
            d.text((125,944),TXT['attribution'],font=font(27),fill=(83,80,71))
        d.line([(120,1080),(1880,1080)],fill=(125,118,99),width=2)
        d.text((125,1140),(TXT['article_footer'] if comfort else TXT['pbs_footer']),font=font(25),fill=(80,78,69))
        d.text((125,1200),(TXT['article_url'] if comfort else TXT['pbs_url']),font=font(25),fill=(80,78,69))
        return im
    def press_frame(self,t,comfort=False):
        local=t-11.3 if comfort else t
        u=interval(local,0,3.7 if comfort else 3)
        cam=Camera([.35-.2*u,-9.6+.25*u,13.6-.35*u],[0,0,0],41)
        paper=self.press[int(comfort)]
        quad=[[-5,3.5,.1],[5,3.5,.1],[5,-3.5,.1],[-5,-3.5,.1]]
        img=self.bg.copy()
        # Two sheets in depth, one editorial object; no annotation popup system.
        back=cam.quad(paper,[[p[0]+.25,p[1]+.3,p[2]-.14] for p in quad])
        rgba=back.convert('RGBA');rgba.putalpha(cam.quad(Image.new('L',paper.size,130),[[p[0]+.25,p[1]+.3,p[2]-.14] for p in quad]))
        img.paste(rgba,(0,0),rgba)
        front=cam.quad(paper,quad)
        mask=cam.quad(Image.new('L',paper.size,255),quad, )
        img.paste(front,(0,0),mask)
        label(img,(W-60,H-44),'excerpt',24,anchor='rm',alpha=.75)
        return img
    def photo_frame(self,t):
        img=cover(self.photo,scale=1.03+.045*interval(t,3,5.8),offset=(35*interval(t,3,5.8),-6))
        a=np.asarray(img,dtype=np.float32)
        a[:,:,0]*=.73;a[:,:,1]*=.83;a[:,:,2]*=.90
        img=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
        # Legible modern-photo date: never pretend this is a 1991 image.
        label(img,(90,132),'prison',66,serif=True,anchor='lm')
        label(img,(90,215),'site_date',32,anchor='lm')
        # Dark bottom band is a soft photographic gradient, not a floating card.
        ov=Image.new('RGBA',(W,H));d=ImageDraw.Draw(ov)
        for y in range(H-190,H):d.line([(0,y),(W,y)],fill=(4,10,14,round(170*(y-(H-190))/190)))
        img=Image.alpha_composite(img.convert('RGBA'),ov).convert('RGB')
        label(img,(75,H-53),'photo_credit',24,anchor='lm')
        return img
    def model_frame(self,t):
        cam=camera(t);img=self.bg.copy()
        cache=BUILD/'model_frames'/f'{round(t*FPS):04d}.jpg'
        if cache.exists():
            img=Image.open(cache).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
            route_lines(img,cam,t)
            self.model_labels(img,t)
            return img
        # Ground contact shadow (coherent with the model), then XYZ stage.
        shadow=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(shadow)
        p=cam.project([[-8.5,-5.6,-.56],[8.5,-5.6,-.56],[8.5,5.6,-.56],[-8.5,5.6,-.56]])
        sd.polygon([tuple(v) for v in p[:,:2]],fill=(0,0,0,190))
        shadow=shadow.filter(ImageFilter.GaussianBlur(22));img.paste(shadow,(0,0),shadow)
        world_scene(t).render(img,cam);route_lines(img,cam,t)
        self.model_labels(img,t)
        return img
    def model_labels(self,img,t):
        # Minimal direct text: each meaning lives in the same persistent world.
        label(img,(70,64),'prison',28,anchor='lm',alpha=.7)
        label(img,(70,H-44),'model',28,anchor='lm',alpha=.65)
        for key,a,b,c,d in [('design',5.65,6,7,7.3),('guards',7.2,7.45,8.5,8.8),('business',8.7,9,10.9,11.3)]:
            label(img,(W/2,115),key,40,alpha=window(t,a,b,c,d),bold=True)
        if 15<=t<18.5:label(img,(W-70,78),'year1',34,anchor='rm',color=GOLD)
        if 18.5<=t<24:label(img,(W-70,78),'year2',34,anchor='rm',color=GOLD,alpha=interval(t,18.5,18.8))
        return img
    def render(self,t):
        if t<3:
            img=self.press_frame(t)
            if t>2.6:img=Image.blend(img,self.photo_frame(3),interval(t,2.6,3))
        elif t<5.9:
            img=self.photo_frame(t)
            if t>5.45:img=Image.blend(img,self.model_frame(t),interval(t,5.45,5.9))
        elif t<11.3:img=self.model_frame(t)
        elif t<15:img=self.press_frame(t,True)
        else:img=self.model_frame(t)
        if t>28.1:
            u=interval(t,28.1,28.8)
            img=Image.blend(img,Image.new('RGB',(W,H),BG),u*.85)
            label(img,(W/2,H/2-36),'title',82,serif=True,alpha=u)
            label(img,(W/2,H/2+72),'subtitle',30,alpha=u*.8,color=GOLD)
        a=np.asarray(img,dtype=np.float32)*self.vig[:,:,None]
        a*=interval(t,0,.18)*(1-interval(t,29.7,30))
        return Image.fromarray(np.clip(a,0,255).astype(np.uint8))


def make_audio():
    ff=imageio_ffmpeg.get_ffmpeg_exe();wav=BUILD/'narrator_source.wav'
    subprocess.run([ff,'-y','-v','error','-i',str(PROJECT/'assets/narrator_approved.mp3'),'-ac','1','-ar','48000',str(wav)],check=True)
    with wave.open(str(wav),'rb') as w:src=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
    sr=48000;n=sr*DUR;voice=np.zeros(n);split=round(8.30*sr)
    voice[3*sr:3*sr+split]=src[:split]
    tail=src[split:];voice[15*sr:15*sr+len(tail)]=tail
    # The approved performance is never regenerated, speed-shifted or pitch-shifted.
    rms=np.sqrt(np.mean(src**2));gain=min(1.8,.135/max(rms,1e-6));voice*=gain
    t=np.arange(n)/sr
    bed=(.011*np.sin(2*np.pi*55*t)+.005*np.sin(2*np.pi*82.5*t+.7)+.003*np.sin(2*np.pi*110*t))
    # Gentle underscore pulses; room/paper transitions under the narrator.
    bed*=.74+.18*np.sin(2*np.pi*.11*t)
    rng=np.random.default_rng(7);sfx=np.zeros(n)
    for at,dur in [(0,.45),(2.65,.5),(5.45,.45),(11.3,.55),(15,.45),(18.6,.6)]:
        count=round(dur*sr);noise=rng.normal(0,1,count)
        noise=np.convolve(noise,np.ones(75)/75,mode='same')
        env=np.sin(np.pi*np.arange(count)/count)**2
        start=round(at*sr);sfx[start:start+count]+=noise*env*.016
    env=np.minimum(t/.4,1)*np.clip((30-t)/.7,0,1)
    mix=(voice+bed+sfx)*env
    peak=np.max(abs(mix));mix*=min(1,.89/max(peak,1e-6))
    stereo=np.stack([mix,mix],axis=1)
    out=BUILD/'mix.wav'
    with wave.open(str(out),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(stereo,-1,1)*32767).astype('<i2').tobytes())
    audit={'voice_id':'voice-02','approved_take_reused':True,'source_samples':len(src),'sample_rate':sr,'source_split_seconds':8.30,'timeline_voice_ranges':[[3,11.30],[15,15+len(tail)/sr]],'archive_only_ranges':[[0,3],[11.3,15]],'actual_broadcast_audio':False,'peak_dbfs':20*math.log10(max(abs(mix))),'voice_gain':gain,'scope':'Synthetic underscore, not an orchestral score. Authentic broadcast insert still pending.'}
    (BUILD/'audio_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');p.add_argument('--historical-rebuild',action='store_true');args=p.parse_args()
    enforce_editorial_review(PROJECT,args.historical_rebuild)
    demo=Demo();picks=[1.1,4.1,6.5,7.9,10,13,16.5,19.8,23.5,29.1]
    for t in picks:demo.render(t).save(BUILD/f'preview_{t:04.1f}.jpg',quality=96)
    if args.preview:return
    required=[n for n in range(FPS*DUR) if 5.45<=n/FPS<11.3 or 15<=n/FPS<30]
    missing=[n for n in required if not (BUILD/'model_frames'/f'{n:04d}.jpg').exists()]
    if missing:raise RuntimeError(f'Final encode refuses software placeholders: {len(missing)} missing Cycles/interpolated frames. Run escobar_hook30_models.py and escobar_hook30_finish.py first.')
    audio=make_audio();ff=imageio_ffmpeg.get_ffmpeg_exe();out=BUILD/'escobar_hook30_v1.mp4'
    with (BUILD/'encode.log').open('w') as log:
        proc=subprocess.Popen([ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
             '-i',str(audio),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','30','-movflags','+faststart','-metadata','comment=Photo: Stefanomione, La Catedral site, 2019. Source: https://commons.wikimedia.org/wiki/File:Helipad_at_La_Catedral,_the_former_Pablo_Escobar_prison_overlooking_the_City_of_Medellin.jpg . Photo adaptation (crop, color grade, animation, text) licensed CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/ . Written retrospective excerpts: PBS FRONTLINE 1997; Amusing Planet / Kaushik Patowary 2023. Illustrative model, not a measured reconstruction. No authentic news audio. AI narration approved by user.',str(out)],stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(FPS*DUR):
                proc.stdin.write(demo.render(n/FPS).tobytes())
                if n%96==0:print(f'{n}/{FPS*DUR}',flush=True)
        finally:proc.stdin.close()
        if proc.wait():raise RuntimeError('Encode failed; see encode.log')
    print('DONE',out,out.stat().st_size,flush=True)

if __name__=='__main__':main()
