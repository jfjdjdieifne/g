#!/usr/bin/env python3
"""Scene-first 1914 explainer map. Authored vector geography + motion; no archive on screen."""
import json, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import shape, box, Polygon, MultiPolygon, GeometryCollection
import imageio_ffmpeg

ROOT=Path(__file__).parent
DATA=json.loads((ROOT/'assets/world_1914.geojson').read_text())
W,H,FPS=1600,900,25
MAP_W,MAP_H=3000,2100
OUT=ROOT/'map_animation_v1.mp4'
NAVY=(7,17,29); SEA=(8,24,38); LAND=(24,42,55); BORDER=(63,86,99)
CYAN=(101,205,214); GOLD=(242,184,83); RED=(219,100,85); WHITE=(238,242,241); DIM=(156,177,188)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def proj(lon,lat):
    # Lambert conformal conic, standard parallels 35/60 N, central meridian 15 E.
    p1,p2,p0=map(math.radians,(35,60,47.5)); lam0=math.radians(15); p=math.radians(max(-80,min(80,lat))); lam=math.radians(lon)
    n=math.log(math.cos(p1)/math.cos(p2))/math.log(math.tan(math.pi/4+p2/2)/math.tan(math.pi/4+p1/2))
    F=math.cos(p1)*math.tan(math.pi/4+p1/2)**n/n
    rho=F/math.tan(math.pi/4+p/2)**n; rho0=F/math.tan(math.pi/4+p0/2)**n
    return rho*math.sin(n*(lam-lam0)), rho0-rho*math.cos(n*(lam-lam0))

# Projection extent, clipped to the European theatre used in this opening.
BOUNDS=(-13,36,35,64)
pts=[proj(x,y) for x in (BOUNDS[0],BOUNDS[1]) for y in (BOUNDS[2],BOUNDS[3])]
px0,px1=min(p[0] for p in pts),max(p[0] for p in pts); py0,py1=min(p[1] for p in pts),max(p[1] for p in pts)
PAD=100
SCALE=min((MAP_W-2*PAD)/(px1-px0),(MAP_H-2*PAD)/(py1-py0))
OX=(MAP_W-(px1-px0)*SCALE)/2-px0*SCALE; OY=(MAP_H-(py1-py0)*SCALE)/2+py1*SCALE

def mp(lon,lat):
    x,y=proj(lon,lat); return (OX+x*SCALE, OY-y*SCALE)

CLIP=box(*BOUNDS)
def parts(geom):
    if not geom: return []
    try: clipped=shape(geom).intersection(CLIP)
    except Exception: return []
    if clipped.is_empty: return []
    if clipped.geom_type=='Polygon': return [clipped]
    if clipped.geom_type=='MultiPolygon': return list(clipped.geoms)
    if clipped.geom_type=='GeometryCollection': return [g for g in clipped.geoms if g.geom_type=='Polygon']
    return []

def poly_pixels(ring):
    return [mp(p[0],p[1]) for p in ring.coords]

# Build map layers once from the cited historical polygons.
base=Image.new('RGB',(MAP_W,MAP_H),SEA); d=ImageDraw.Draw(base)
for feat in DATA['features']:
    name=feat.get('properties',{}).get('NAME') or ''
    for polygon in parts(feat.get('geometry') or {}):
        outer=poly_pixels(polygon.exterior)
        if len(outer)<3: continue
        # Broad monochrome fill; highlighted state changes are drawn as a separate reveal layer.
        d.polygon(outer,fill=LAND,outline=BORDER)
        for hole in polygon.interiors:
            q=poly_pixels(hole)
            if len(q)>2: d.polygon(q,fill=SEA)
# Re-draw borders crisply on top for legibility.
for feat in DATA['features']:
    for polygon in parts(feat.get('geometry') or {}):
        q=poly_pixels(polygon.exterior)
        if len(q)>1: d.line(q,fill=(44,67,81),width=2)

# Reusable geographic state layers: modestly differentiated, not allegiances-as-automatic-arrows.
state_colors={
    'Serbia':GOLD,'Austro-Hungarian Empire':RED,
    'Russian Empire':(91,146,190),'German Empire':(211,137,87),
    'France':(113,158,202),'Belgium':(236,205,125),
    'United Kingdom of Great Britain and Ireland':(111,178,161),
}
states={}
for target,color in state_colors.items():
    layer=Image.new('RGBA',(MAP_W,MAP_H),(0,0,0,0)); ld=ImageDraw.Draw(layer)
    for feat in DATA['features']:
        if feat.get('properties',{}).get('NAME')!=target: continue
        for polygon in parts(feat.get('geometry') or {}):
            q=poly_pixels(polygon.exterior)
            if len(q)>=3: ld.polygon(q,fill=(*color,110),outline=(*color,230),width=3)
    states[target]=layer

CITIES={
 'Sarajevo':(18.4131,43.8563),'Belgrade':(20.4489,44.7866),'Vienna':(16.3738,48.2082),
 'Berlin':(13.405,52.52),'St. Petersburg':(30.3351,59.9343),'Paris':(2.3522,48.8566),
 'Brussels':(4.3517,50.8503),'London':(-0.1276,51.5072)
}
# Smooth travel between meaningful map anchors; no repeated reset-to-card shots.
CAM=[(0,14.0,49.5,.82),(0.8,19.4,46.0,1.40),(1.6,20.5,45.7,1.82),(3.6,20.5,45.7,1.82),(8.6,19.5,46.0,1.55),(10.5,16,49,1.18),(17,16,49,1.18),(22,18,50.2,1.06),(27,5.5,50.4,1.62),(31,-0.1,51.3,1.55),(36,7.0,50.4,1.08),(42,12.0,49.5,.98),(48.9,14.0,49.5,.70)]

def ease(a,b,u):
    u=max(0,min(1,u)); u=u*u*(3-2*u); return a+(b-a)*u

def camera(t):
    for i in range(len(CAM)-1):
        a,b=CAM[i],CAM[i+1]
        if a[0]<=t<=b[0]:
            u=(t-a[0])/(b[0]-a[0]); return tuple(ease(a[j],b[j],u) for j in range(1,4))
    return CAM[-1][1:]

def event_state(t):
    active=[]
    if t>=0: active += ['Serbia','Austro-Hungarian Empire']
    if t>=18: active += ['Russian Empire','German Empire']
    if t>=21: active += ['France']
    if t>=26: active += ['Belgium','United Kingdom of Great Britain and Ireland']
    return active

def screen_xy(lon,lat,t):
    cl,ct,z=camera(t); cx,cy=mp(cl,ct); x,y=mp(lon,lat)
    cw=MAP_W/(1.45*z); ch=cw*H/W
    return ((x-(cx-cw/2))/cw*W,(y-(cy-ch/2))/ch*H)

def pill(d,xy,text,font,fill,anchor='mm'):
    d.text(xy,text,font=font,fill=fill,anchor=anchor,stroke_width=0)

def makeframe(t):
    cl,ct,z=camera(t); cx,cy=mp(cl,ct); cw=MAP_W/(1.45*z); ch=cw*H/W
    box=(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2)
    crop=base.crop(tuple(map(int,box))).resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')
    # Gentle cinematic grade, not texture-as-substitute for legibility.
    for name in event_state(t):
        lay=states[name].crop(tuple(map(int,box))).resize((W,H),Image.Resampling.LANCZOS)
        crop=Image.alpha_composite(crop,lay)
    d=ImageDraw.Draw(crop,'RGBA')
    # Header is a small source-context masthead, not a subtitle panel.
    pill(d,(70,46),'1914  /  JULY CRISIS',ImageFont.truetype(BOLD,21),(141,183,196,240),'la')
    # Active factual locations stay attached to their geography.
    visible=[]
    if t<11: visible=['Sarajevo','Belgrade','Vienna']
    elif t<22: visible=['Vienna','Berlin','St. Petersburg']
    elif t<29: visible=['Paris','Brussels','Berlin']
    elif t<35: visible=['London','Brussels']
    for city in visible:
        x,y=screen_xy(*CITIES[city],t)
        if -60<x<W+60 and -40<y<H+40:
            rr=6 if city not in ('Sarajevo','Brussels') else 8
            col=GOLD if city in ('Sarajevo','Belgrade','Vienna') else CYAN
            d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(*col,255),outline=(5,18,27,255),width=2)
            dx=13; dy=-14 if y>H*.5 else 15
            pill(d,(x+dx,y+dy),city.upper(),ImageFont.truetype(BOLD,15),(228,236,234,245),'lm')
    # Country labels are map anchors, shown only while that region carries the explanation.
    regions=[]
    if t<10.5: regions=[('AUSTRO-HUNGARY',(19.0,50.3),RED),('SERBIA',(21.5,43.6),GOLD)]
    elif t<22.0: regions=[('GERMAN EMPIRE',(10.5,51.2),(211,137,87)),('RUSSIAN EMPIRE',(29.0,56.0),(91,146,190))]
    elif t<31.0: regions=[('FRANCE',(1.0,47.2),(113,158,202)),('BELGIUM',(4.5,51.7),(236,205,125))]
    else: regions=[('BELGIUM',(4.5,51.7),(236,205,125)),('BRITAIN',(-3.4,54.2),(111,178,161))]
    for name,loc,col in regions:
        x,y=screen_xy(*loc,t)
        if 20<x<W-20 and 70<y<H-70:
            pill(d,(x,y),name,ImageFont.truetype(BOLD,16),(*col,190),'mm')
    # Only a few motivated words/dates; no full narration captions.
    if 0<=t<2.8:
        a=max(0,min(1,(t-.08)/.28)); xx=(W+480)-(W+480-(W-72))*ease(0,1,(t-.08)/.42)
        if a>0: pill(d,(xx,112),'ALMOST ALL',ImageFont.truetype(BOLD,39),(238,242,241,int(255*a)),'ra')
    elif 2.8<=t<7.5:
        a=max(0,min(1,(t-2.8)/.45)); pill(d,(W-72,112),'ONE REFUSAL',ImageFont.truetype(BOLD,39),(247,200,114,int(255*a)),'ra')
        d.line((W-390,164,W-78,164),fill=(247,200,114,int(190*a)),width=3)
    elif 8.6<=t<10.3:
        pill(d,(W-70,108),'28 JULY 1914',ImageFont.truetype(BOLD,28),(240,244,240,255),'ra')
    elif 10.3<=t<17.1:
        pill(d,(W-70,108),'28 JUNE  /  28 JULY',ImageFont.truetype(BOLD,25),(240,244,240,255),'ra')
    elif 17.1<=t<22.0:
        pill(d,(W-70,108),'1 AUG  /  3 AUG',ImageFont.truetype(BOLD,28),(240,244,240,255),'ra')
    elif 24.1<=t<30.4:
        pill(d,(W-70,108),'4 AUGUST',ImageFont.truetype(BOLD,31),(247,200,114,255),'ra')
    elif 30.4<=t<37.1:
        # A real geographic crossing is shown only for Germany's invasion of Belgium.
        p1=screen_xy(6.1,50.8,t); p2=screen_xy(4.35,50.85,t)
        d.line((p1[0],p1[1],p2[0],p2[1]),fill=(242,184,83,235),width=5)
        d.ellipse((p2[0]-8,p2[1]-8,p2[0]+8,p2[1]+8),fill=(*GOLD,255))
        pill(d,(W-70,108),'BELGIUM  /  BRITAIN',ImageFont.truetype(BOLD,24),(240,244,240,255),'ra')
    elif 37.1<=t<43.0:
        pill(d,(W-70,108),'37 DAYS',ImageFont.truetype(BOLD,39),(247,200,114,255),'ra')
    elif t>=43.0:
        pill(d,(W-70,108),'CHOICES',ImageFont.truetype(BOLD,39),(247,200,114,255),'ra')
    # Dated chronology: factual event marks, not a generic progress bar.
    events=['28 JUN','23 JUL','28 JUL','1 AUG','3 AUG','4 AUG']
    active_i=(1 if t<8.6 else 2 if t<10.4 else 0 if t<17.0 else 3 if t<21.0 else 4 if t<24.0 else 5)
    x0,x1=95,W-95; y=H-47; d.line((x0,y,x1,y),fill=(133,160,171,125),width=2)
    for j,label in enumerate(events):
        x=x0+(x1-x0)*j/(len(events)-1); active=(j==active_i)
        col=GOLD if active else DIM
        d.ellipse((x-5,y-5,x+5,y+5),fill=(*col,245 if active else 135))
        pill(d,(x,y-18),label,ImageFont.truetype(BOLD,14),(*col,245 if active else 145),'ms')
    # Deep edge vignette focuses the viewer toward the mapped change.
    vign=Image.new('L',(W,H),0); vd=ImageDraw.Draw(vign)
    vd.rectangle((0,0,W,H),fill=55)
    crop.putalpha(255)
    return crop.convert('RGB')

def render(seconds=48.98,path=OUT):
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    writer=imageio_ffmpeg.write_frames(str(path),(W,H),fps=FPS,codec='libx264',pix_fmt_out='yuv420p',quality=8,macro_block_size=1)
    writer.send(None)
    count=round(seconds*FPS)
    for i in range(count):
        t=i/FPS
        frame=makeframe(t)
        writer.send(frame.tobytes())
    writer.close()
    print(path, count, 'frames')

if __name__=='__main__':
    import sys
    secs=float(sys.argv[1]) if len(sys.argv)>1 else 48.98
    render(secs,ROOT/f'map_animation_{secs:.2f}s.mp4')
