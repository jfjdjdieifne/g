#!/usr/bin/env python3
"""V3 cartographic design study, NOT an approved reference-quality renderer.
16s continuous Escobar style test, no VO. No documentary statistics asserted.
Reference evidence / timing are in engine/projects/ww2_demo/v3_design/PLAN.md.
Run --preview for three full-size stills; run normally for the 16s animation.
"""
import argparse
import json
import math
import subprocess
from pathlib import Path

import arabic_reshaper
import imageio_ffmpeg
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/user/build/ww2_demo_v3')
W, H, FPS, DUR = 1920, 1080, 24, 16
AW, AH = 5760, 4320
COS = math.cos(math.radians(15))
AK, ALON, ALAT = AW / 48, -77., 15.
MED = (-75.56, 6.25)
# Nearest inland geometry point, 0.02 degrees west of the nominal city centre.
MIA = (-80.21, 25.76)
NAVY, LAND, FOCUS = (12, 17, 47), (59, 82, 143), (199, 167, 65)
WHITE, GOLD, RED = (245, 239, 218), (247, 210, 92), (175, 47, 69)
AR = ROOT / 'assets_global/fonts/NotoNaskhArabic-Bold.ttf'
LAT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
FONT_CACHE = {}
CMAP = set(TTFont(str(AR)).getBestCmap())
WORLD = json.loads((ROOT / 'assets_global/geo/latam_10m.json').read_text())


def smooth(x):
    x = np.clip(x, 0., 1.)
    return float(x*x*(3-2*x))


def interval(t, a, b):
    return smooth((t-a)/(b-a))


def atlas_xy(lon, lat):
    return ((lon-ALON)*COS*AK+AW/2, -(lat-ALAT)*AK+AH/2)


def polygons(code):
    g = WORLD[code]
    return g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]


def contains(code, point):
    def inside(ring):
        x, y = point
        hit = False
        for (x0,y0), (x1,y1) in zip(ring, ring[1:]+ring[:1]):
            if (y0>y) != (y1>y) and x < (x1-x0)*(y-y0)/(y1-y0)+x0:
                hit = not hit
        return hit
    return any(inside(poly[0]) and not any(inside(hole) for hole in poly[1:])
               for poly in polygons(code))


def noise(size, seed, coarse=False):
    rng = np.random.default_rng(seed)
    w,h = size
    arr = rng.integers(0, 256, (max(2,h//65), max(2,w//65)) if coarse else (h,w), dtype=np.uint8)
    im = Image.fromarray(arr)
    return im.resize(size, Image.Resampling.BICUBIC) if coarse else im


def textured(size, color, seed, strength=17):
    # Texture is fixed in WORLD space; camera movement cannot swim or flicker it.
    low = np.asarray(noise(size, seed, True), dtype=np.float32)/255-.5
    fine = np.asarray(noise(size, seed+1), dtype=np.float32)/255-.5
    out = np.empty((size[1], size[0],3), dtype=np.uint8)
    for i,c in enumerate(color):
        out[:,:,i] = np.clip(c + low*strength + fine*6, 0,255)
    return Image.fromarray(out)


def country_mask(code, size=None):
    size = size or (AW, AH)
    mask = Image.new('L',size)
    d = ImageDraw.Draw(mask)
    for poly in polygons(code):
        for i, ring in enumerate(poly):
            d.polygon([atlas_xy(*p) for p in ring], fill=255 if i==0 else 0)
    return mask


def make_atlas():
    BUILD.mkdir(parents=True, exist_ok=True)
    path = BUILD/'atlas_v3.png'
    if path.exists() and (BUILD/'atlas_version.txt').exists() and (BUILD/'atlas_version.txt').read_text()=='4':
        return Image.open(path).convert('RGB'), Image.open(BUILD/'col_mask.png').convert('L')
    img = textured((AW,AH), NAVY, 16, strength=7)
    land = textured((AW,AH), LAND, 38)
    allmask = Image.new('L',(AW,AH))
    masks = {}
    for code in WORLD:
        m = country_mask(code)
        allmask = ImageChops.lighter(allmask,m)
        if code=='COL':
            masks[code] = m
    # Fine coastal shelf, rather than a UI drop shadow.
    coast = allmask.filter(ImageFilter.GaussianBlur(8))
    img.paste((38,56,94), (0,0), coast)
    img.paste(land,(0,0),allmask)
    del land
    col = masks['COL']
    img.paste(textured((AW,AH),FOCUS,58),(0,0),col)
    d = ImageDraw.Draw(img)
    # Geographically exact continuous boundaries. No random jitter per frame.
    for code in WORLD:
        for poly in polygons(code):
            ring = poly[0]
            d.line([atlas_xy(*p) for p in ring], fill=(22,31,62),width=4,joint='curve')
    # Thin cartographic graticule; subordinate to land and events.
    grid=Image.new('RGBA',(AW,AH))
    gd=ImageDraw.Draw(grid)
    for lon in range(-110,-40,5):
        x,_=atlas_xy(lon,0)
        gd.line([(x,0),(x,AH)],fill=(177,194,228,12),width=1)
    for lat in range(-10,40,5):
        _,y=atlas_xy(0,lat)
        gd.line([(0,y),(AW,y)],fill=(177,194,228,12),width=1)
    img=Image.alpha_composite(img.convert('RGBA'),grid).convert('RGB')
    img.save(path)
    col.save(BUILD/'col_mask.png')
    (BUILD/'atlas_version.txt').write_text('4')
    return img,col


def font(path,size):
    key=(str(path),int(size))
    if key not in FONT_CACHE:
        FONT_CACHE[key]=ImageFont.truetype(str(path),int(size))
    return FONT_CACHE[key]


def text_layer(text,size,color=WHITE,arabic=False):
    from production_policy import enforce_display
    enforce_display({"language":"en","texts":{"rendered_text":text}})
    s=get_display(arabic_reshaper.reshape(text)) if arabic else text
    # Group same-font characters: Arabic connections are never letter-spaced/jittered.
    groups=[]
    for c in s:
        path=AR if ord(c) in CMAP or c==' ' else LAT
        if groups and groups[-1][0]==path:
            groups[-1]=(path,groups[-1][1]+c)
        else:
            groups.append((path,c))
    widths=[font(p,size).getlength(s) for p,s in groups]
    w=math.ceil(sum(widths))
    lay=Image.new('RGBA',(w+36,size*2))
    d=ImageDraw.Draw(lay)
    x=18
    for (p,s),ww in zip(groups,widths):
        d.text((x,size),s,font=font(p,size),fill=color+(255,),anchor='lm',
               stroke_width=1,stroke_fill=color+(255,))
        x+=ww
    return lay


TEXT_CACHE={}
def title(img,xy,text,size,color=WHITE,alpha=1,anchor='mm',arabic=False):
    if alpha<=0:return
    key=(text,size,color,arabic)
    if key not in TEXT_CACHE:TEXT_CACHE[key]=text_layer(text,size,color,arabic)
    lay=TEXT_CACHE[key].copy()
    lay.putalpha(lay.getchannel('A').point(lambda p:round(p*min(1,alpha))))
    x,y=xy
    x-=lay.width/2 if anchor[0]=='m' else lay.width if anchor[0]=='r' else 0
    y-=lay.height/2
    # Small typographic contrast shadow, not a background box.
    shadow=Image.new('RGBA',lay.size,(5,8,22,0))
    shadow.putalpha(lay.getchannel('A').point(lambda p:round(p*.6)))
    img.paste(shadow,(round(x+2),round(y+3)),shadow)
    img.paste(lay,(round(x),round(y)),lay)


def camera(t):
    # Same world, one camera: local -> regional -> local. Zero shot reset.
    wide=interval(t,2.8,5.6)*(1-interval(t,9.4,11.9))
    lon=-74.9+(-77.+74.9)*wide
    lat=6.5+(16.-6.5)*wide
    span=15.+(47.-15.)*wide
    return lon,lat,span,wide


def point_at(lon,lat,cam):
    cx,cy,span,_=cam
    k=W/span
    return ((lon-cx)*COS*k+W/2,-(lat-cy)*k+H/2)


def city(img,point,name,t,cam,opacity=1,offset=(48,30)):
    if opacity<=0:return
    x,y=point_at(*point,cam)
    if not (45<x<W-45 and 80<y<H-100):return
    d=ImageDraw.Draw(img)
    r=7
    d.ellipse((x-r-2,y-r-2,x+r+2,y+r+2),fill=(12,18,42))
    d.ellipse((x-r,y-r,x+r,y+r),fill=WHITE)
    title(img,(x+offset[0],y+offset[1]),name,30,alpha=opacity,anchor='lm')


def bezier(start,end,control,n=180):
    return [((1-u)**2*start[0]+2*(1-u)*u*control[0]+u*u*end[0],
             (1-u)**2*start[1]+2*(1-u)*u*control[1]+u*u*end[1])
            for u in np.linspace(0,1,n)]


def draw_route(img,world_pts,cam,progress,color=GOLD,width=5,arrow=False):
    if progress<=0:return
    pts=[point_at(*p,cam) for p in world_pts]
    end=max(2,min(len(pts),int(len(pts)*progress)))
    pts=pts[:end]
    lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    d.line(pts,fill=(8,13,31,230),width=width+4,joint='curve')
    d.line(pts,fill=color+(255,),width=width,joint='curve')
    x,y=pts[-1]
    if arrow:
        ang=math.atan2(y-pts[-2][1],x-pts[-2][0])
        d.polygon([(x+15*math.cos(ang),y+15*math.sin(ang)),
                   (x-11*math.cos(ang)+9*math.sin(ang),y-11*math.sin(ang)-9*math.cos(ang)),
                   (x-11*math.cos(ang)-9*math.sin(ang),y-11*math.sin(ang)+9*math.cos(ang))],fill=color+(255,))
    else:
        d.ellipse((x-6,y-6,x+6,y+6),fill=WHITE+(255,))
    img.paste(lay,(0,0),lay)


class Demo:
    def __init__(self):
        self.atlas,self.col=make_atlas()
        self.route=bezier(MED,MIA,(-83,16))
        # All convoy positions must be on land inside Colombia.
        self.convoys=[bezier((-74.6,9.3),MED,(-74.3,7.5)),
                      bezier((-76.4,5.2),MED,(-76.5,6.4)),
                      bezier((-74.2,5.2),MED,(-74.1,6.2))]
        if not contains('COL',MED):raise RuntimeError('Medellin is not in COL')
        if not contains('USA',MIA):raise RuntimeError('Miami is not in USA')
        for path in self.convoys:
            if not all(contains('COL',p) for p in path):raise RuntimeError('Convoy crosses sea/country boundary')
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
        self.vig=np.clip(1-.17*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2),.70,1.)

    def render(self,t):
        cam=camera(t)
        cx,cy,span,wide=cam
        ax,ay=atlas_xy(cx,cy)
        ratio=AK/(W/span)
        coeff=(ratio,0,ax-ratio*W/2,0,ratio,ay-ratio*H/2)
        img=self.atlas.transform((W,H),Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC)
        # Country-only operational emphasis, revealing without an ellipse/blob.
        operational=interval(t,11.7,13.3)
        if operational>0:
            mask=self.col.transform((W,H),Image.Transform.AFFINE,coeff,Image.Resampling.BILINEAR)
            mask=mask.point(lambda p:round(p*operational*.58))
            img.paste(RED,(0,0),mask)
        routep=interval(t,5.65,8.5)
        if routep>0:draw_route(img,self.route,cam,routep,width=5)
        for i,route in enumerate(self.convoys):
            progress=interval(t,11.9+i*.35,13.2+i*.35)
            if progress>0:
                draw_route(img,route,cam,progress,WHITE,width=4)
                # A tiny map symbol travelling WITH the path; never an onscreen popup.
                pos=route[min(len(route)-1,int(progress*(len(route)-1)))]
                x,y=point_at(*pos,cam)
                d=ImageDraw.Draw(img)
                d.rounded_rectangle((x-14,y-7,x+14,y+7),radius=4,fill=WHITE,outline=(12,16,30),width=2)
                d.rectangle((x-5,y-5,x+5,y+5),fill=(29,40,70))
        city(img,MED,'MEDELLÍN',t,cam,offset=(0,0),opacity=0)
        mx,my=point_at(*MED,cam)
        # One label continuously follows the camera, away from caption and routes.
        d=ImageDraw.Draw(img)
        d.ellipse((mx-8,my-8,mx+8,my+8),fill=WHITE,outline=(12,18,42),width=2)
        title(img,(mx-145+290*wide,my-67),'MEDELLÍN',30)
        city(img,MIA,'MIAMI',t,cam,opacity=interval(t,5.1,5.8),offset=(48,18))
        # Geographical country name, not a selection badge.
        cp=point_at(-72.9,3.2,cam)
        title(img,cp,'COLOMBIA',42,alpha=(1-wide)*.68*(1-interval(t,2.2,2.8)))
        title(img,(W-84,92),'COLOMBIA / 1993',23,alpha=.65,anchor='rm')
        intro=interval(t,.25,.9)*(1-interval(t,2.3,2.85))
        title(img,(1480,240),'THE LAST STRONGHOLD',39,alpha=intro)
        title(img,(1480,328),'PABLO ESCOBAR',24,alpha=intro*.80)
        caption=(('FROM MEDELLÍN, THE NETWORK EXPANDED',interval(t,3.,3.5)*(1-interval(t,8.7,9.2))),
                 ('THEN THE HUNT CLOSED IN',interval(t,11.5,12.1)*(1-interval(t,14.2,14.7))))
        for txt,alpha in caption:title(img,(W/2,H-105),txt,29,alpha=alpha)
        ending=interval(t,14.2,14.85)
        if ending:
            img=Image.blend(img,Image.new('RGB',(W,H),NAVY),ending*.76)
            title(img,(W/2,H/2-25),'THE END OF THE HUNT',55,alpha=ending)
            title(img,(W/2,H/2+94),'MEDELLÍN / 1993',26,color=GOLD,alpha=ending)
        arr=np.asarray(img,dtype=np.float32)
        arr*=self.vig[:,:,None]
        introfade=interval(t,0,.5)
        outfade=1-interval(t,15.5,16)
        arr*=introfade*outfade
        return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    from production_policy import enforce_display
    enforce_display(json.loads((ROOT/'engine/projects/ww2_demo/v4_depth/display.json').read_text()))
    demo=Demo()
    picks=[1.8,7.8,13.8]
    for t in picks:
        demo.render(t).save(BUILD/f'preview_{t:.1f}.jpg',quality=96)
    if args.preview:return
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    silent=BUILD/'v3_silent.mp4'
    cmd=[ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)]
    with (BUILD/'encode.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(DUR*FPS):
                proc.stdin.write(demo.render(n/FPS).tobytes())
                if n%48==0:print(f'{n}/{DUR*FPS}',flush=True)
        finally:proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('ffmpeg failed; see encode.log')
    out=finish_audio(silent)
    print(f'DONE {out} ({out.stat().st_size} bytes)',flush=True)


def finish_audio(silent):
    # Same synthesis as v2, but cues follow this camera rather than the old edit.
    # This is a restrained synthetic drone, NOT a licensed orchestral score.
    from ww2demo import build_audio
    audio=BUILD/'v3_audio.wav'
    cues=[{'k':'whoosh','t':2.8,'d':1.1,'g':.035},
          {'k':'whoosh','t':5.65,'d':.9,'g':.025},
          {'k':'tick','t':8.5,'g':.020},
          {'k':'whoosh','t':9.4,'d':1.0,'g':.035},
          {'k':'paper','t':11.9,'g':.030},
          {'k':'impact','t':14.2,'g':.035}]
    build_audio(audio,cues)
    out=BUILD/'escobar_ww2drive_v3_design_test.mp4'
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff,'-y','-i',str(silent),'-i',str(audio),'-map','0:v:0','-map','1:a:0',
                    '-af','volume=0.35,afade=t=in:st=0:d=0.5,afade=t=out:st=14.5:d=1.5',
                    '-c:v','copy','-c:a','aac','-b:a','192k','-t',str(DUR),
                    '-movflags','+faststart',str(out)],check=True,capture_output=True)
    return out


if __name__=='__main__':main()
