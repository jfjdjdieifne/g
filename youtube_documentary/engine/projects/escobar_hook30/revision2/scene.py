"""Escobar revision2 staging profile. Shared World/Cycles runtime, not a new engine.
Illustrative architectural model: not a surveyed site or a claimed escape route.
Real factual objects: fortified boundary, guards, football pitch, office/telephone.
No historical likeness, invented document, trajectory, moving escape figure or tower.
"""
import math
import numpy as np
from xyz_scene import World, Camera, cylinder

CONCRETE=(141,145,133)
STONE=(92,101,94)
STEEL=(66,80,82)
WIRE=(113,128,124)
WOOD=(113,71,41)
PAPER=(222,213,188)
UNIFORM=(57,72,66)


def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)


def guard(w,x,y):
    # Anonymous architectural scale figure, with human proportions rather than blocks.
    skin=(147,139,119)
    def oval(c,r,col):soft_pillow(w,c,r,col)
    for side in [-1,1]:
        hip=(x+side*.11,y,.93);knee=(x+side*.12,y-.015,.52);ankle=(x+side*.13,y,.12)
        cylinder(w,hip,knee,.092,UNIFORM,24);oval(knee,(.087,.085,.09),UNIFORM)
        cylinder(w,knee,ankle,.068,UNIFORM,24)
        oval((x+side*.13,y-.06,.09),(.085,.17,.085),(29,37,34))
    rings=[(.86,.16,.105),(1.0,.17,.12),(1.19,.22,.14),(1.33,.23,.13),(1.41,.12,.085)]
    for ra,rb in zip(rings,rings[1:]):
        for j in range(32):
            pts=[]
            for row,k in [(ra,j),(ra,j+1),(rb,j+1),(rb,j)]:
                z,rx,ry=row;angle=k*math.tau/32;pts.append((x+rx*math.cos(angle),y+ry*math.sin(angle),z))
            w.face(pts,UNIFORM)
    for side in [-1,1]:
        shoulder=(x+side*.22,y,1.32);elbow=(x+side*.30,y-.035,1.03);wrist=(x+side*.27,y-.105,.85)
        oval(shoulder,(.095,.10,.11),UNIFORM);cylinder(w,shoulder,elbow,.073,UNIFORM,24)
        oval(elbow,(.07,.071,.075),UNIFORM);cylinder(w,elbow,wrist,.056,UNIFORM,24)
        oval((wrist[0],wrist[1],.80),(.048,.055,.085),skin)
        w.box((x+side*.17,y,1.405),(.11,.12,.02),(112,120,95))
    cylinder(w,(x,y,1.39),(x,y,1.54),.068,skin,24)
    oval((x,y,1.64),(.123,.108,.155),skin)
    oval((x,y-.106,1.64),(.025,.034,.035),skin)
    cylinder(w,(x,y,1.76),(x,y,1.81),.135,UNIFORM,32)
    oval((x,y-.105,1.762),(.147,.12,.018),UNIFORM)
    for z in [.89,.94]:
        w.line([(x+.17*math.cos(t),y+.125*math.sin(t),z) for t in np.linspace(0,math.tau,48)],(30,39,34),2)
    w.box((x-.12,y-.145,1.14),(.09,.045,.14),(27,32,31))
    cylinder(w,(x-.12,y-.14,1.23),(x-.12,y-.14,1.39),.007,(27,32,31),8)


def fence(w,a,b,gate=False):
    a=np.array(a,float);b=np.array(b,float);v=b-a;length=np.linalg.norm(v);d=v/length
    # Mesh is geometry in the scene, not a screen-space prison icon.
    for u in np.linspace(0,length,math.ceil(length/1.5)+1):
        q=a+d*u;cylinder(w,(*q,.03),(*q,2.55),.04,STEEL)
    for z in [.15,1.25,2.45]:w.line([(*a,z),(*b,z)],WIRE,2)
    # Diamond mesh clipped exactly at its actual spatial boundary.
    for sign in [-1,1]:
        for k in np.arange(-2.5,length+2.5,.34):
            lo=max(0,-k/sign) if sign>0 else max(0,k-length)
            hi=min(2.38,(length-k)/sign) if sign>0 else min(2.38,k)
            if hi<=lo:continue
            pts=[(*(a+d*(k+sign*z)),z+.06) for z in [lo,hi]]
            w.line(pts,(91,109,105),.85)
    # Restrained coil on the boundary; no invented guard towers/escape route.
    steps=max(24,int(length*32))
    coil=[]
    for u in np.linspace(0,length,steps):
        angle=u*math.tau/.52;q=a+d*u
        coil.append((q[0],q[1]+.13*math.cos(angle),2.64+.13*math.sin(angle)))
    w.line(coil,WIRE,1.3)


def window_wall(w):
    # Back wall has real window openings, not painted black rectangles.
    for x,width in [(1.0,1.1),(4.05,.65),(7.5,1.0)]:
        w.box((x,4.3,.04),(width,.22,2.8),CONCRETE)
    for x,width in [(2.55,2.0),(5.85,2.85)]:
        w.box((x,4.3,.04),(width,.22,.91),CONCRETE)
        w.box((x,4.3,2.3),(width,.22,.54),CONCRETE)
        w.box((x,4.12,.9),(width+.1,.34,.08),(159,150,123))
        for dx in np.arange(-width/2+.12,width/2,.25):
            cylinder(w,(x+dx,4.27,.98),(x+dx,4.27,2.3),.018,STEEL)
        w.line([(x-width/2,4.27,1.64),(x+width/2,4.27,1.64)],STEEL,1.8)


def telephone(w,x,y,z):
    # An illustrated 1990s office prop, not a claimed exact historical device.
    w.box((x,y,z),(.70,.52,.11),(35,43,42))
    w.box((x,y+.07,z+.11),(.60,.33,.045),(46,53,50))
    for dx in [-.12,0,.12]:
        for dy in [-.14,-.055,.03,.115]:
            w.box((x+dx,y+dy-.04,z+.16),(.082,.055,.018),(167,167,149))
    # Proper receiver: earpieces + curved grip + curled cord, persistent in XYZ.
    for dx in [-.26,.26]:
        w.box((x+dx,y+.225,z+.145),(.18,.19,.095),(25,30,30))
    curve=[(x+u,y+.24,z+.22+.065*math.sin(math.pi*(u+.26)/.52)) for u in np.linspace(-.26,.26,20)]
    w.line(curve,(28,33,32),6)
    cord=[]
    for u in np.linspace(0,1,160):
        cord.append((x+.37+.16*u+.026*math.cos(u*math.tau*15),y+.15-.65*u,z+.12+.025*math.sin(u*math.tau*15)))
    w.line(cord,(33,39,36),.8)


def soft_pillow(w,center,radii,color):
    c=np.array(center);r=np.array(radii)
    for i in range(12):
        a=-math.pi/2+i*math.pi/12;b=a+math.pi/12
        for j in range(32):
            pts=[]
            for lat,lon in [(a,j*math.tau/32),(a,(j+1)*math.tau/32),(b,(j+1)*math.tau/32),(b,j*math.tau/32)]:
                pts.append(c+r*np.array([math.cos(lat)*math.cos(lon),math.cos(lat)*math.sin(lon),math.sin(lat)]))
            w.face(pts,color)


def blanket(w):
    # A continuous cloth mesh with small folds, not a floating rectangular tile.
    xs=np.linspace(5.48,7.02,25);ys=np.linspace(1.38,3.02,33)
    def point(x,y):
        edge=max(0,abs(x-6.25)-.68)*1.1
        z=.80-edge+.018*math.sin(y*12+x*5)+.011*math.sin(x*17+y*3)
        return (x,y,z)
    for x1,x2 in zip(xs,xs[1:]):
        for y1,y2 in zip(ys,ys[1:]):w.face([point(x1,y1),point(x2,y1),point(x2,y2),point(x1,y2)],(183,184,164))


def build_world(detail=False):
    w=World();rng=np.random.default_rng(72)
    # Irregular earth section rather than a square model pedestal.
    outline=[]
    for i in range(40):
        a=i*math.tau/40;r=1+rng.uniform(-.035,.035)
        outline.append((13.8*math.cos(a)*r,10.2*math.sin(a)*r,0))
    for i,p in enumerate(outline):
        q=outline[(i+1)%len(outline)]
        w.face([(0,0,.01),p,q],(73,85,71))
        for depth,col in [(.35,(77,67,52)),(.85,(58,55,45))]:
            top=0 if depth==.35 else -.35
            w.face([(p[0],p[1],top),(q[0],q[1],top),(q[0]*.99,q[1]*.99,-depth),(p[0]*.99,p[1]*.99,-depth)],col)
    # Courtyard paving, drains and approach route live on the ground plane.
    w.box((1,-3.8,.015),(18,3.0,.025),(113,116,103))
    w.box((0,-7.8,.02),(3.3,5,.03),(114,115,101))
    for x in np.arange(-8,10,.9):w.line([(x,-5.2,.046),(x,-2.4,.046)],(99,103,92),.5)
    for x in [-1.85,1.85]:
        w.box((x,-6.9,.04),(.14,2.3,.025),(44,54,49))
        for y in np.arange(-8,-5.8,.13):w.line([(x-.065,y,.07),(x+.065,y,.07)],(106,117,107),.8)
    # Documented luxury: field within the same secure boundary.
    w.box((-5.2,1.25,.015),(7.0,4.3,.03),(49,88,64))
    for j in range(7):
        w.box((-8.2+j,1.25,.047),(.48,4.1,.004),(54,92,66))
    for yy in [-.65,3.15]:w.line([(-8.45,yy,.057),(-1.95,yy,.057)],(187,192,164),1.4)
    for xx in [-8.45,-5.2,-1.95]:w.line([(xx,-.65,.057),(xx,3.15,.057)],(187,192,164),1.4)
    w.line([(-5.2+.53*math.cos(a),1.25+.53*math.sin(a),.06) for a in np.linspace(0,math.tau,65)],(187,192,164),1.3)
    for xx in [-8.45,-1.95]:
        for yy in [.55,1.95]:cylinder(w,(xx,yy,.07),(xx,yy,1.02),.027,(190,195,174))
        cylinder(w,(xx,.55,1.02),(xx,1.95,1.02),.027,(190,195,174))
        for yy in np.arange(.55,1.96,.18):w.line([(xx,yy,.08),(xx,yy,1.02)],(117,133,117),.5)
    # Roofless architectural cutaway; every interior remains in one world.
    w.box((4,1.75,.04),(8.0,5.35,.14),(115,104,80))
    for x in np.arange(.2,7.9,.4):
        for y in np.arange(-.7,4.1,.8):
            w.box((x,y,.184),(.385,.78,.012),(126+int(x*4)%12,91,57))
    window_wall(w)
    w.box((7.95,1.7,.19),(.20,5.4,2.65),CONCRETE)
    w.box((.05,1.7,.19),(.20,5.4,1.05),CONCRETE)
    w.box((4,-.9,.19),(8.1,.20,.5),CONCRETE)
    # Doorway between office and sleeping room; lintel makes the opening real.
    for yy,dep in [(.15,2.0),(3.6,1.3)]:w.box((4.9,yy,.19),(.16,dep,2.5),CONCRETE)
    w.box((4.9,1.95,2.3),(.16,2.05,.4),CONCRETE)
    # Timber desk, actual legs, drawers, papers, landline and fax.
    w.box((2.7,1.85,.93),(2.45,1.05,.09),WOOD,top=(148,104,62))
    for x in [1.62,3.78]:
        for y in [1.43,2.25]:w.box((x,y,.2),(.1,.1,.73),WOOD)
    w.box((3.6,1.85,.23),(.42,.83,.65),WOOD)
    for z in ([.34,.54,.74] if detail else [.43,.64,.85]):
        w.box((3.6,1.42,z),(.34,.04,.17),(133,87,50))
        w.line([(3.52,1.39,z+.08),(3.68,1.39,z+.08)],(174,154,105),1.5)
    telephone(w,2.10,1.64,1.03)
    for i in range(5):w.box((2.96+i*.004,1.59,1.03+i*.009),(.46,.55,.006),PAPER)
    # Blank paper is a prop, not a fabricated signed document.
    w.box((3.5,2.02,1.03),(.52,.38,.17),(160,159,134))
    w.box((3.5,2.08,1.20),(.44,.13,.02),(59,66,59))
    w.box((3.5,2.18,1.22),(.41,.24,.015),PAPER)
    # Chair with real legs, seat and padded back.
    w.box((2.7,2.85,.58),(.57,.52,.10),(69,54,40))
    w.box((2.7,3.08,.65),(.57,.09,.65),(79,59,40))
    for x in [2.47,2.93]:
        for y in [2.64,3.03]:cylinder(w,(x,y,.2),(x,y,.59),.024,(66,67,54))
    # Bed and side table: absence, not an invented escape animation.
    w.box((6.25,2.45,.20),(1.5,2.1,.35),WOOD)
    w.box((6.25,2.45,.55),(1.5,2.1,.22),(190,181,150))
    blanket(w)
    soft_pillow(w,(6.25,3.13,.84),(.59,.26,.13),(225,218,194))
    w.box((6.25,3.54,.2),(1.6,.10,.9),WOOD)
    w.box((7.37,3.12,.2),(.5,.5,.56),WOOD)
    # Perimeter. Front gate has no animated route or arbitrary escaping figure.
    for a,b in [((-10,-7.3),(-1.65,-7.3)),((1.65,-7.3),(10,-7.3)),((10,-7.3),(10,7.0)),((10,7.0),(-10,7.0)),((-10,7.0),(-10,-7.3))]:fence(w,a,b)
    for xx in [-1.65,1.65]:w.box((xx,-7.3,.01),(.28,.3,2.85),STONE)
    for xx in np.linspace(-1.5,1.5,17):cylinder(w,(xx,-7.3,.06),(xx,-7.3,2.55),.022,STEEL)
    for zz in [.12,1.25,2.55]:w.line([(-1.55,-7.3,zz),(1.55,-7.3,zz)],WIRE,3)
    w.box((0,-7.43,1.1),(.18,.12,.28),(127,122,95))
    guard(w,-2.45,-6.7);guard(w,2.45,-6.7)
    # Low entrance shelter, not a speculative watchtower.
    for xx in [-3.4,-1.65]:
        for yy in [-6.95,-5.55]:w.box((xx,yy,.05),(.10,.10,2.7),WOOD)
    w.box((-2.525,-6.25,2.75),(2.05,1.7,.10),(117,102,77))
    return w


# Motivated cuts. Small within-shot camera movement; never interpolate across cuts.
SHOTS=[
 {'id':'establish','start':7.6,'end':11.8,'a':([18,-24,21],[0,-.3,.5]),'b':([16.8,-22.8,19.7],[.2,-.1,.6]),'fov':43,'focus':[0,0,.8],'aperture':8},
 {'id':'guards','start':11.8,'end':13.3,'a':([-7.4,-3.7,3.1],[-2.45,-6.7,1.15]),'b':([-7.05,-3.85,3.0],[-2.45,-6.7,1.15]),'fov':39,'focus':[-2.45,-6.7,1.2],'aperture':5.6},
 {'id':'office','resolution':[1280,720],'start':13.3,'end':16.15,'a':([3.6,-.65,2.95],[2.5,1.8,1.02]),'b':([3.35,-.5,2.85],[2.45,1.8,1.02]),'fov':45,'focus':[2.4,1.85,1.1],'aperture':5.6},
 {'id':'contradiction','start':16.15,'end':21.95,'a':([-11,-12.5,9.4],[-1,1.3,.8]),'b':([-10.2,-11.7,9.9],[-.8,1.1,.8]),'fov':43,'focus':[-2,1.1,.6],'aperture':8},
 {'id':'absence','start':21.95,'end':24.5,'a':([7.0,-.45,2.9],[6.3,2.4,.9]),'b':([6.85,-.25,2.8],[6.3,2.45,.85]),'fov':44,'focus':[6.25,2.45,.9],'aperture':5.6},
 {'id':'questions','start':24.5,'end':30,'a':([15.5,-21.5,15.5],[.1,.2,.9]),'b':([18,-24,18.5],[0,0,.8]),'fov':43,'focus':[0,0,1],'aperture':8},
]


def shot_camera(shot,t,width=1920,height=1080):
    u=smooth((t-shot['start'])/(shot['end']-shot['start']))
    eye=np.array(shot['a'][0])*(1-u)+np.array(shot['b'][0])*u
    target=np.array(shot['a'][1])*(1-u)+np.array(shot['b'][1])*u
    return Camera(eye,target,shot['fov'],width,height)
