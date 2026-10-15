#!/usr/bin/env python3
"""Expanded source-led intro authoring. Uses shared XYZ/photo-depth primitives.
Sources and actual clips precede this profile. Output is an internal review cut.
"""
import argparse,json,hashlib,math,subprocess,sys,wave,shutil,importlib.util
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'engine/runtime'));sys.path.insert(0,str(ROOT/'engine/projects/escobar_intro3'))
spec=importlib.util.spec_from_file_location('escobar_intro3_profile',ROOT/'engine/projects/escobar_intro3/profile.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
from photo_depth import view,page_turn,smooth,document,PhotoDepth
B=P.BUILD;A=B/'assets';W,H=P.W,P.H;FPS=P.FPS;FF=imageio_ffmpeg.get_ffmpeg_exe()
ARCHIVE=Path('/home/user/build/escobar_archive_official/original_opening.mp4')
FONT=ROOT/'assets_global/fonts/DejaVuSans.ttf';FONTB=ROOT/'assets_global/fonts/DejaVuSans-Bold.ttf'
if not FONT.exists():FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');FONTB=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
cv2.setNumThreads(2)

def validate():
    from production_policy import enforce_display,enforce_design
    from documentary_materials import material_errors
    project=ROOT/'engine/projects/escobar_intro3'
    display=json.loads((project/'display_manifest.json').read_text());enforce_display(display);enforce_design(display['design'])
    errors=material_errors(json.loads((project/'MATERIALS.json').read_text()))
    if errors:raise ValueError('; '.join(errors))


def decode(path,start=0,dur=None):
    args=[FF,'-v','error','-ss',str(start),'-i',str(path)]
    if dur is not None:args+=['-t',str(dur)]
    return np.frombuffer(subprocess.check_output(args+['-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4').astype(np.float64)

def wav(path,x):
    if x.ndim==1:x=np.column_stack([x,x])
    with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())

def rms(x):return float(np.sqrt(np.mean(x*x)))

@lru_cache(maxsize=24)
def image(name):return np.array(Image.open(A/name).convert('RGB'))

@lru_cache(maxsize=40)
def font(size,bold=False):return ImageFont.truetype(str(FONTB if bold else FONT),size)

def caption(frame,text,right=False):
    frame=frame.copy();ramp=np.linspace(0,.68,110,dtype=np.float32)[:,None,None];frame[-110:]=(frame[-110:].astype(np.float32)*(1-ramp)).astype(np.uint8)
    im=Image.fromarray(frame);d=ImageDraw.Draw(im);f=font(32);x=64
    if right:x=W-64-d.textlength(text,font=f)
    d.text((x,H-57),text,font=f,fill=(224,224,215),stroke_width=2,stroke_fill=(12,14,16));return np.array(im)

def region(name,c0,c1,span0,span1,u,yaw=.0):
    k=smooth(u);center=np.array(c0)*(1-k)+np.array(c1)*k
    return view(image(name),center,span0*(1-k)+span1*k,(W,H),yaw=yaw*math.sin(math.pi*k))

def prepare():
    B.mkdir(parents=True,exist_ok=True);(B/'frames').mkdir(exist_ok=True)
    for sub in ['assets','voice']:
        (B/sub).mkdir(exist_ok=True)
        for asset in (ROOT/'engine/projects/escobar_intro3'/sub).iterdir():
            if asset.is_file():shutil.copy2(asset,B/sub/asset.name)
    expected='6b533a7506d8996607780271ed627dbc49fe9f2e348fc061dec7596ce8e754e7'
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()!=expected:raise ValueError('Wrong genuine archive source')
    for key in ['ship','fear']:
        s=P.ARCHIVE[key];dest=B/'frames'/key;dest.mkdir(exist_ok=True)
        if not (dest/'complete').exists():
            subprocess.run([FF,'-v','error','-ss',str(s['source_in']),'-i',str(ARCHIVE),'-t',str(s['source_out']-s['source_in']),'-vf','fps=24,scale=1440:960','-q:v','2','-y',str(dest/'%05d.jpg')],check=True)
            (dest/'complete').write_text('Original AV source, bounded resample, no interpolated frames.')
    assets={n:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in A.iterdir() if p.suffix.lower() in ['.jpg','.png'] for n in [p.name]}
    (B/'input_hashes.json').write_text(json.dumps(assets,indent=2))

def audio():
    sr=48000;n=round(P.DURATION*sr);t=np.arange(n)/sr;dialog=np.zeros(n);audit=[]
    for key in ['ship','wealth','wanted','social','fear','questions','close']:
        start=P.STARTS[key]
        if key in P.ARCHIVE:
            a=P.ARCHIVE[key];x=decode(ARCHIVE,a['source_in'],a['source_out']-a['source_in'])
            edge=min(144,len(x)//2);x[:edge]*=np.linspace(0,1,edge);x[-edge:]*=np.linspace(1,0,edge)
        else:x=decode(B/'voice'/f'broad_{key}.mp3')
        frames=x[:len(x)//960*960].reshape(-1,960);active=np.sqrt(np.mean(frames**2,axis=1))>.012
        gain=min(.14/max(rms(frames[active]),1e-8),.79/max(abs(x)))
        at=round(start*sr);dialog[at:at+len(x)]+=x*gain
        audit.append({'key':key,'start':start,'decoded_duration':len(x)/sr,'constant_gain':gain,'voice':None if key in P.ARCHIVE else P.VOICE})
    # Newly composed restrained underscore: warm detuned pads, low plucked ostinato,
    # soft kick/paper textures. No borrowed commercial recording.
    bed=np.zeros(n);rng=np.random.default_rng(193)
    for at,end,notes in [(0,20,[55,130.8128,164.8138]),(17,39,[43.6535,130.8128,174.6141]),(36,53,[51.9131,123.4708,155.5635]),(50,65,[48.9994,146.8324,195.9977])]:
        env=np.clip((t-at)/2,0,1)*np.clip((end-t)/3,0,1);chord=np.zeros(n)
        for j,f in enumerate(notes):chord+=(np.sin(2*np.pi*f*t+j*.4)+.16*np.sin(2*np.pi*f*1.002*t)) / (1+j*.7)
        bed+=chord*env*.010
    for at in np.arange(5.3,61,.48):
        k=round(at*sr);count=min(round(.8*sr),n-k);u=np.arange(count)/sr
        freq=[110,164.8138,130.8128,146.8324][int(at/.48)%4]
        pluck=(np.sin(2*np.pi*freq*u)+.18*np.sin(2*np.pi*freq*2*u))*np.exp(-u*9)*np.clip(u/.008,0,1)
        bed[k:k+count]+=pluck*(.004+.005*np.clip((at-45)/13,0,1))
    # Breath beneath speech; changes affect music, never the approved voice identity.
    energy=np.sqrt(np.convolve(dialog[::480]**2,np.ones(9)/9,mode='same'))
    duck=np.interp(t,np.arange(len(energy))*.01,np.clip(1-energy*3,.48,1))
    bed*=duck*np.clip(t/.3,0,1)*np.clip((P.DURATION-t)/.8,0,1)
    sfx=np.zeros(n);events=[(5.15,.3,'paper arrival'),(10.1,.45,'page turn'),(23.7,.35,'portrait match'),(29.3,.2,'contact print'),(40.5,.22,'archive cut')]
    events += [(57.8+i*.25,.09,'press match') for i in range(10)]
    for at,length,kind in events:
        count=round(length*sr);k=round(at*sr);u=np.arange(count)/sr
        noise=rng.normal(0,1,count);noise=np.convolve(noise,np.ones(28)/28,mode='same');noise*=np.sin(np.pi*np.arange(count)/count)**2
        target=rms(bed[k:k+count])*10**(-9/20);noise*=target/max(rms(noise),1e-8);sfx[k:k+count]+=noise
    mix=dialog+bed+sfx;wav(B/'unmastered.wav',mix)
    result=subprocess.run([FF,'-hide_banner','-i',str(B/'unmastered.wav'),'-af','loudnorm=I=-16:TP=-1.4:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
    m=json.loads(result[result.rfind('{'):result.rfind('}')+1]);g=min(-16-float(m['input_i']),-1.5-float(m['input_tp']))
    wav(B/'mix.wav',mix*10**(g/20));wav(B/'dialogue_stem.wav',dialog*10**(g/20))
    (B/'audio_audit.json').write_text(json.dumps({'clips':audit,'master_constant_gain_db':g,'sfx_db_relative_to_local_music':-9,'narrator_regenerated_from_approved_identity':True,'original_approved_take_untouched':True,'no_voice_retiming_or_pitch_change':True,'manual_listening_claimed':False},indent=2))

@lru_cache(maxsize=300)
def tv_frame(key,index):
    files=sorted((B/'frames'/key).glob('*.jpg'));return np.array(Image.open(files[min(index,len(files)-1)]).convert('RGB'))

def television(key,t):
    frame=np.full((H,W,3),(5,7,9),np.uint8);im=tv_frame(key,max(0,int((t-P.STARTS[key])*FPS)));frame[60:1020,240:1680]=im
    return caption(frame,'Charlie Rose  /  Nov 12, 1992')


@lru_cache(maxsize=4)
def depth_scene(name):
    im=image(name);h,w=im.shape[:2];mask=np.zeros((h,w),np.uint8)
    if name=='football.jpg':
        pts=[(321,115),(335,122),(341,145),(351,155),(367,182),(374,214),(379,232),(373,244),(367,240),(365,220),(358,206),(356,253),(345,302),(335,348),(332,386),(327,409),(312,418),(304,411),(301,393),(306,363),(310,319),(306,286),(292,308),(285,340),(282,382),(270,403),(259,407),(252,400),(260,381),(263,351),(267,312),(276,285),(272,252),(260,241),(251,230),(249,204),(256,180),(270,162),(285,153),(290,146),(294,134),(299,122)]
        cv2.fillPoly(mask,[np.int32(pts)],255)
        # Refine the actual silhouette using image edges, not a guessed person shape.
        gc=np.zeros((h,w),np.uint8);gc[98:433,230:395]=cv2.GC_PR_BGD;gc[mask>0]=cv2.GC_PR_FGD;gc[cv2.erode(mask,np.ones((9,9),np.uint8))>0]=cv2.GC_FGD
        cv2.setRNGSeed(193)
        cv2.grabCut(im,gc,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),5,cv2.GC_INIT_WITH_MASK)
        mask=np.where((gc==1)|(gc==3),255,0).astype(np.uint8)
        cv2.circle(mask,(263,377),25,255)
    elif name=='city.jpg':
        pts=[(0,320),(100,309),(166,268),(235,269),(260,241),(305,244),(336,228),(369,216),(405,217),(437,244),(491,254),(541,273),(574,251),(634,250),(681,257),(711,239),(779,237),(779,h),(0,h)]
        cv2.fillPoly(mask,[np.int32(pts)],255)
    return PhotoDepth(im,mask)


def name_clip(source,box,u):
    # Actual printed-word pixels. Context is deliberately defocused, not rewritten.
    im=image(source);x,y,w,h=box;crop=im[int(y):int(y+h),int(x):int(x+w)]
    bg=cv2.resize(crop,(W,H));bg=cv2.GaussianBlur(bg,(0,0),45)
    bg=(bg.astype(np.float32)*.16+200).clip(0,255).astype(np.uint8)
    width=int(740*(1+.025*u));height=round(width*crop.shape[0]/crop.shape[1]);patch=cv2.resize(crop,(width,height),interpolation=cv2.INTER_CUBIC)
    x0=W//2-width//2;y0=H//2-height//2;bg[y0:y0+height,x0:x0+width]=patch
    return bg


def compose(t):
    if t<5.15:return television('ship',t)
    if t<8.5:
        # Whole authentic cover: Forbes branding visible, no Escobar portrait added.
        return caption(document(image('forbes_cover.png'),1515-45*smooth((t-5.15)/3.35),(W,H),yaw=.007*math.sin((t-5.15)/3.35*math.pi)),'Forbes  /  Oct 5, 1987')
    if t<9.5:return caption(page_turn(image('forbes_cover.png'),image('forbes_entry.png'),(t-8.5),(W,H)),'Forbes  /  Oct 5, 1987')
    if t<17.8:return caption(region('forbes_entry.png',(316,640),(323,648),570,535,(t-9.5)/8.3,yaw=-.025),'Forbes  /  original 1987 entry')
    if t<23.84:return caption(region('forbes_entry.png',(284,690),(291,690),430,409,(t-17.8)/6.04,yaw=.025),'Forbes  /  original 1987 entry' if t<21 else 'Image: Forbes 1987  /  Audio: Charlie Rose 1992')
    if t<29.3:
        # Original photograph inset from the1983profile; Spanish article text excluded.
        return caption(region('semana.jpg',(190,119),(196,115),365,347,(t-23.84)/5.46,yaw=-.035),'Semana  /  Apr 19, 1983  /  photograph detail')
    if t<35.3:
        return caption(depth_scene('football.jpg').render((300,262),585-25*smooth((t-29.3)/6),(t-29.3)/6,(W,H),travel=.045),'1983  /  El Tiempo archive  /  animated photograph')
    if t<40.70:
        return caption(region('congress.jpg',(300,197),(294,197),595,565,(t-35.3)/5.4,yaw=-.035),'Escobar in Congress  /  El Tiempo archive')
    if t<46.30:return television('fear',t)
    if t<50.2:
        return caption(region('congress.jpg',(284,189),(294,188),565,540,(t-46.3)/3.9,yaw=.04),'Escobar in Congress  /  El Tiempo archive')
    if t<54:
        return caption(region('semana.jpg',(190,119),(197,119),350,335,(t-50.2)/3.8,yaw=.025),'Semana  /  original 1983 photograph')
    if t<57.8:
        return caption(depth_scene('city.jpg').render((390,270),775-35*smooth((t-54)/3.8),(t-54)/3.8,(W,H),depth=.12,travel=.07),'Medellin  /  contemporary establishing view')
    if t<60.30:
        # Genuine independent1987/1983/1992print fragments; no outcome/headline spoilers.
        cards=[('forbes_entry.png',(42,491,48,10)),('semana.jpg',(166,243,30,7)),('daily_page7.jpg',(290,493,40,10)),('forbes_entry.png',(42,491,48,10)),('daily_page7.jpg',(94,720,28,9))]
        step=int((t-57.8)/.25);name,box=cards[step%len(cards)]
        return name_clip(name,box,((t-57.8)%.25)/.25)
    # Original editorial title, never a forged historical document.
    im=Image.fromarray(region('city.jpg',(390,270),(401,267),775,725,(t-60.3)/2.95))
    dark=Image.new('RGB',(W,H),(5,11,15));im=Image.blend(dark,im,.20)
    d=ImageDraw.Draw(im);u=smooth((t-60.3)/.55);f=font(177,True)
    for text,y,delay in [('PABLO',270,0),('ESCOBAR',475,.12)]:
        a=smooth((t-60.3-delay)/.45);tw=d.textlength(text,font=f);d.text(((W-tw)/2,y+26*(1-a)),text,font=f,fill=tuple(int(c*a) for c in [232,228,211]))
    return np.array(im)


def frame(t):
    x=compose(t)
    # Short purposeful exposure pulse hides physical page-cut seams, not bad assets.
    # No global grain that would manufacture archive provenance.
    fade=min(1,t/.055,max(0,(P.DURATION-1/FPS-t)/.28))
    if fade<1:x=(x.astype(np.float32)*fade).astype(np.uint8)
    return x


def stills():
    (B/'review').mkdir(exist_ok=True);times=[1,7,10.4,13,20,26,32,37,43,48,52,55.5,58.05,58.55,60.8,62.5]
    sheet=Image.new('RGB',(1600,4*246),(15,17,18));d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        im=Image.fromarray(frame(t));im.save(B/'review'/f'still_{t}.jpg',quality=94);im.thumbnail((400,225));x=i%4*400;y=i//4*246;sheet.paste(im,(x,y));d.text((x+8,y+227),f'{t:.2f}s',fill='white')
    sheet.save(B/'review/staging.jpg',quality=94)


def finish():
    if not (B/'mix.wav').exists():raise ValueError('Audio not mixed')
    output=B/'Escobar_Expanded_Intro_Revision3.mp4';tmp=B/'encoding.tmp.mp4';count=round(P.DURATION*FPS)
    with (B/'encode.log').open('w') as log:
        proc=subprocess.Popen([FF,'-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-i',str(B/'mix.wav'),'-t',str(P.DURATION),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','title=Pablo Escobar — expanded spoiler-free documentary opening','-metadata','comment=Internal editorial review. Authentic Charlie Rose excerpts and actual Forbes1987/Semana1983/press photographs. Original-pixel2.5D editorial animation, not recorded camera motion or surveyed reconstruction. Contemporary Medellin view labeled. No publication license claimed. Approved voice-02 identity, new performance. No prison/escape/fate spoilers.',str(tmp)],stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(count):
                proc.stdin.write(frame(n/FPS).tobytes())
                if n%120==0:print('FRAME',n,'/',count,flush=True)
        finally:proc.stdin.close()
        if proc.wait():raise RuntimeError('Encode failed')
    tmp.replace(output);print('DONE',output,flush=True)
    (B/'render.json').write_text(json.dumps({'duration':P.DURATION,'frames':count,'fps':FPS,'resolution':[W,H],'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'method':'Native24fps1080pcomposition of lower-resolution authentic sources and perspective photo planes, not nativeHD archives','voice_identity':P.VOICE,'new_performance':True,'prison_scenes':0,'escape_or_death_reveals':0,'visual_review_complete':False,'user_approved':False,'publication_license_obtained':False},indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['prepare','audio','stills','finish']);args=a.parse_args();validate();globals()[args.action]()
