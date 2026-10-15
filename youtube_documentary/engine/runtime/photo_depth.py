"""Shared perspective photo planes/page turns. Genuine 2.5D, not surveyed geometry.
Textures stay original pixels. Profiles supply sources, masks and camera intent.
"""
import math
import cv2
import numpy as np
from xyz_scene import Camera


def smooth(t):
    t=float(np.clip(t,0,1));return t*t*(3-2*t)


def project_texture(image,points,camera,background=None):
    h,w=image.shape[:2];H,W=camera.height,camera.width
    q=camera.project(points)
    if np.any(q[:,2]<=.02):raise ValueError('Photo plane crossed camera near plane')
    dst=q[:,:2].astype(np.float32)
    matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[w,0],[w,h],[0,h]]),dst)
    if background is None:
        return cv2.warpPerspective(image,matrix,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    rgb=image[:,:,:3];alpha=image[:,:,3] if image.shape[2]==4 else np.full((h,w),255,np.uint8)
    premul=(rgb.astype(np.uint16)*alpha[:,:,None]//255).astype(np.uint8)
    fg=cv2.warpPerspective(premul,matrix,(W,H),flags=cv2.INTER_LINEAR)
    a=cv2.warpPerspective(alpha,matrix,(W,H),flags=cv2.INTER_LINEAR)
    return np.minimum(255,fg.astype(np.uint16)+background.astype(np.uint16)*(255-a[:,:,None])//255).astype(np.uint8)


def view(image,center,span,shape=(1920,1080),yaw=0,pitch=0):
    W,H=shape;h,w=image.shape[:2];scale=2/span
    pts=np.array([[(0-center[0])*scale,0,(center[1]-0)*scale],[(w-center[0])*scale,0,center[1]*scale],[(w-center[0])*scale,0,(center[1]-h)*scale],[-center[0]*scale,0,(center[1]-h)*scale]])
    c,s=math.cos(yaw),math.sin(yaw);pts=pts@np.array([[c,s,0],[-s,c,0],[0,0,1]])
    camera=Camera((pitch,-1/math.tan(math.radians(43/2)),0),(0,0,0),43,W,H)
    return project_texture(image,pts,camera)


def page_turn(front,back,t,shape=(1920,1080)):
    """Physical ruled page on a common spine; blank reverse is an editorial prop."""
    W,H=shape;canvas=document(back,back.shape[1]*2.285,shape)
    u=smooth(t);angle=u*math.pi;cam=Camera((0,-4.89,0),(0,0,0),43,W,H)
    width=1.684;height=width*front.shape[0]/front.shape[1]
    strips=20
    for i in range(strips):
        a=i/strips;b=(i+1)/strips
        if u<.5:tex=front[:,round(a*front.shape[1]):round(b*front.shape[1])]
        else:tex=np.full((front.shape[0],max(1,round(front.shape[1]/strips)),3),(205,197,177),np.uint8)
        def point(v,z):
            curl=.12*math.sin(math.pi*v)*math.sin(angle)
            return [-width/2+width*v*math.cos(angle),-width*v*math.sin(angle)-curl,z]
        pts=[point(a,height/2),point(b,height/2),point(b,-height/2),point(a,-height/2)]
        canvas=project_texture(tex,pts,cam,canvas)
    return canvas


def document(image,span=1470,shape=(1920,1080),yaw=0):
    """Whole portrait document with real edges; no repeated border pixels."""
    W,H=shape;h,w=image.shape[:2];scale=2/span;cx=w/2;cy=h/2
    pts=np.array([[-cx*scale,0,cy*scale],[cx*scale,0,cy*scale],[cx*scale,0,-cy*scale],[-cx*scale,0,-cy*scale]])
    c,s=math.cos(yaw),math.sin(yaw);pts=pts@np.array([[c,s,0],[-s,c,0],[0,0,1]])
    camera=Camera((0,-1/math.tan(math.radians(43/2)),0),(0,0,0),43,W,H)
    bg=np.full((H,W,3),(12,15,17),np.uint8)
    return project_texture(image,pts,camera,bg)


class PhotoDepth:
    """Original-pixel cutout over an inpainted hidden background.
    Most reconstructed pixels stay occluded; small exposed edge gutters may show.
    No subject animation, new faces, or invented actions. The hidden edge fill is
    computational reconstruction, not archival evidence. Caller must disclose it.
    """
    def __init__(self,image,mask):
        self.image=image;self.mask=mask;hidden=cv2.dilate(mask,np.ones((7,7),np.uint8))
        self.background=cv2.inpaint(image,hidden,5,cv2.INPAINT_TELEA)
        self.foreground=np.dstack([image,cv2.GaussianBlur(mask,(3,3),.55)])

    def render(self,center,span,u,shape=(1920,1080),depth=.16,travel=.11):
        W,H=shape;h,w=self.image.shape[:2];D=1/math.tan(math.radians(43/2));s=2/span
        pts=np.array([[-center[0]*s,0,center[1]*s],[(w-center[0])*s,0,center[1]*s],[(w-center[0])*s,0,(center[1]-h)*s],[-center[0]*s,0,(center[1]-h)*s]])
        x=travel*(2*smooth(u)-1);camera=Camera((x,-D,.012*math.sin(u*math.pi)),(0,0,0),43,W,H)
        bg=project_texture(self.background,pts,camera)
        fgpts=pts*((D-depth)/D);fgpts[:,1]=-depth
        return project_texture(self.foreground,fgpts,camera,bg)
