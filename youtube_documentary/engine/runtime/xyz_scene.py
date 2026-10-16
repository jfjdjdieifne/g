"""Shared software XYZ scene runtime (camera, texture homography, lit geometry).
Not a terrain/globe engine or a physically based renderer. Painter-depth ordering
can fail at intersecting geometry: author non-intersecting primitives and inspect.
Film scripts supply props, staging, timeline and editorial typography.
"""
import math
import numpy as np
from PIL import Image, ImageDraw


class Camera:
    def __init__(self,pos,look,fov=43,width=1920,height=1080):
        self.width=width;self.height=height
        self.eye=np.array(pos,float)
        f=np.array(look,float)-self.eye;f/=np.linalg.norm(f)
        r=np.cross(f,[0,0,1.]);r/=np.linalg.norm(r)
        up=np.cross(r,f)
        self.R=np.stack([r,-up,f]);self.f=self.width/(2*math.tan(math.radians(fov/2)))
    def project(self,p):
        p=np.atleast_2d(p);q=(p-self.eye)@self.R.T
        return np.column_stack([self.width/2+self.f*q[:,0]/q[:,2],self.height/2+self.f*q[:,1]/q[:,2],q[:,2]])
    def quad(self,img,points):
        target=self.project(points)[:,:2]
        src=[(0,0),(img.width,0),(img.width,img.height),(0,img.height)]
        # Inverse projective map (screen pixel -> texture pixel).
        A=[];B=[]
        for (x,y),(u,v) in zip(target,src):
            A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
            B.extend([u,v])
        coeff=np.linalg.solve(np.array(A,float),np.array(B,float))
        return img.transform((self.width,self.height),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)


class World:
    def __init__(self):self.faces=[];self.lines=[];self.shadows=[]
    def face(self,points,color,emissive=False,outline=None):
        self.faces.append((np.asarray(points,float),color,emissive,outline))
    def box(self,c,size,col,top=None):
        x,y,z=c;w,d,h=size
        p=np.array([[x-w/2,y-d/2,z],[x+w/2,y-d/2,z],[x+w/2,y+d/2,z],[x-w/2,y+d/2,z],
                    [x-w/2,y-d/2,z+h],[x+w/2,y-d/2,z+h],[x+w/2,y+d/2,z+h],[x-w/2,y+d/2,z+h]])
        for ids in [[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]:self.face(p[ids[::-1]],col)
        self.face(p[[4,5,6,7]],top or col)
    def line(self,points,color,width=1):self.lines.append((np.asarray(points,float),color,width))
    def ball(self,c,r,col):
        # Small faceted silhouette heads; no generated historical faces.
        x,y,z=c
        for lat in range(5):
            a=-math.pi/2+lat*math.pi/5;b=a+math.pi/5
            for i in range(8):
                p=[]
                for ph,th in [(a,i*math.pi/4),(a,(i+1)*math.pi/4),(b,(i+1)*math.pi/4),(b,i*math.pi/4)]:
                    p.append((x+r*math.cos(ph)*math.cos(th),y+r*math.cos(ph)*math.sin(th),z+r*math.sin(ph)))
                self.face(p,col)
    def render(self,img,cam):
        faces=[];light=np.array([-.4,-.6,.7]);light/=np.linalg.norm(light)
        for pts,col,emissive,outline in self.faces:
            q=cam.project(pts)
            if np.any(q[:,2]<.3):continue
            if q[:,0].max()<0 or q[:,0].min()>img.width or q[:,1].max()<0 or q[:,1].min()>img.height:continue
            n=np.cross(pts[1]-pts[0],pts[2]-pts[0]);L=np.linalg.norm(n)
            shade=1 if emissive else .48+.52*max(0,float(n@light/max(L,1e-8)))
            color=tuple(int(max(0,min(255,c*shade))) for c in col)
            faces.append((q[:,2].mean(),[tuple(v) for v in q[:,:2]],color,outline))
        items=[(z,0,p,col,out) for z,p,col,out in faces]
        for pts,col,width in self.lines:
            q=cam.project(pts)
            if np.any(q[:,2]<.3):continue
            for a,b in zip(q,q[1:]):
                items.append(((a[2]+b[2])/2,1,[tuple(a[:2]),tuple(b[:2])],col,width))
        d=ImageDraw.Draw(img)
        for _,kind,p,col,out in sorted(items,key=lambda p:p[0],reverse=True):
            if kind:d.line(p,fill=col,width=out,joint='curve')
            else:
                d.polygon(p,fill=col)
                if out:d.line(p+[p[0]],fill=out,width=1)
        return img


def cylinder(world,a,b,r,color,segments=12):
    """Append an oriented capped cylinder to any World (shared geometry helper)."""
    a=np.array(a,float);b=np.array(b,float);axis=b-a;axis/=np.linalg.norm(axis)
    ref=np.array([0,0,1.]) if abs(axis[2])<.9 else np.array([1.,0,0])
    u=np.cross(axis,ref);u/=np.linalg.norm(u);v=np.cross(axis,u)
    ring=[r*(math.cos(i*2*math.pi/segments)*u+math.sin(i*2*math.pi/segments)*v) for i in range(segments)]
    for i in range(segments):
        j=(i+1)%segments
        world.face([a+ring[i],a+ring[j],b+ring[j],b+ring[i]],color)
    world.face([a+x for x in ring[::-1]],color);world.face([b+x for x in ring],color)
