"""Geographic, perspective-camera explanatory route scene. Never archival evidence.
Coordinates are lon/lat; a local equirectangular projection, NOT surveyed routes.
"""
import json,math
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from xyz_scene import Camera,World
from photo_depth import project_texture,smooth

class GeoRoute:
    def __init__(self,geo_dir,font_dir,size):
        self.size=size;self.font_dir=Path(font_dir)
        self.geo=json.loads((Path(geo_dir)/'latam_10m.json').read_text())
        extra=Path(geo_dir)/'supply_route_supplement_110m.json'
        if extra.exists():self.geo.update(json.loads(extra.read_text())['features'])
        self.bounds=(-92,-25,-57,35);self.TW=1400;self.TH=1900
        self.texture=self.make_texture()
    def xy(self,lon,lat):return ((lon+75)*.83,(lat-5))
    def pixels(self,lon,lat):
        a,b,c,d=self.bounds;return ((lon-a)/(c-a)*self.TW,(d-lat)/(d-b)*self.TH)
    def make_texture(self):
        im=Image.new('RGB',(self.TW,self.TH),(12,23,30));d=ImageDraw.Draw(im)
        for lon in range(-90,-55,5):
            x=self.pixels(lon,0)[0];d.line((x,0,x,self.TH),fill=(23,36,43),width=1)
        for lat in range(-25,36,5):
            y=self.pixels(0,lat)[1];d.line((0,y,self.TW,y),fill=(23,36,43),width=1)
        for key,geom in self.geo.items():
            polygons=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
            for poly in polygons:
                ring=poly[0];stride=max(1,len(ring)//1600);pts=[self.pixels(*p[:2]) for p in ring[::stride]]
                if len(pts)<3:continue
                d.polygon(pts,fill=(44,57,59) if key!='COL' else (79,84,72));d.line(pts+[pts[0]],fill=(111,123,119),width=2)
        return np.array(im)
    def render(self,s,u):
        W,H=self.size;k=smooth(u);mode=s.get('stage','andes')
        if mode=='andes':look=np.array([0.,-7+k,0]);eye=np.array([3-k,-54+4*k,93-4*k])
        elif mode=='north':look=np.array([-1.,16+2*k,0]);eye=np.array([5-2*k,-28+4*k,80-3*k])
        else:look=np.array([0.,8.,0]);eye=np.array([5-2*k,-48+4*k,118-4*k])
        cam=Camera(eye,look,43,W,H);a,b,c,d=self.bounds
        pts=[(*self.xy(a,d),0),(*self.xy(c,d),0),(*self.xy(c,b),0),(*self.xy(a,b),0)]
        bg=np.full((H,W,3),(7,13,18),np.uint8);out=project_texture(self.texture,pts,cam,bg)
        world=World();nodes=s.get('nodes',[]);progress=np.clip(u*1.4,0,1)
        edges=s.get('edges',[(i,i+1) for i in range(len(nodes)-1)])
        for edge_i,(a,b) in enumerate(edges):
            start,end=nodes[a],nodes[b]
            p=np.array([*self.xy(start['lon'],start['lat']),.25]);q=np.array([*self.xy(end['lon'],end['lat']),.25]);arc=[]
            for t in np.linspace(0,min(1,progress*len(nodes)-edge_i),70):
                if t<0:continue
                v=p*(1-t)+q*t;v[2]+=(2.0 if mode=='andes' else 3.0)*math.sin(math.pi*t);arc.append(v)
            if len(arc)>1:world.line(arc,(210,171,99),max(2,round(W/500)))
        for node in nodes:
            x,y=self.xy(node['lon'],node['lat']);world.ball((x,y,.3),.23,(232,213,168))
        im=world.render(Image.fromarray(out),cam);d=ImageDraw.Draw(im)
        font=ImageFont.truetype(str(self.font_dir/'DejaVuSans.ttf'),max(18,round(W/56)))
        for node in nodes:
            q=cam.project([*self.xy(node['lon'],node['lat']),.5])[0];dx,dy=node.get('label_offset',[13,-25]);x,y=q[0]+dx,q[1]+dy
            if 30<x<W-140 and 35<y<H-140:d.text((x,y),node['label'],font=font,fill=(239,229,207),stroke_width=2,stroke_fill=(8,15,19))
        return np.array(im)
