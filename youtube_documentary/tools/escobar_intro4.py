#!/usr/bin/env python3
"""Rhythm profile using existing shared photo/XYZ runtime and authentic sources.
No global video speed-up, regenerated voice or recreated historical newspapers.
"""
import argparse,importlib.util,json,sys,math,hashlib,subprocess,shutil,wave
from pathlib import Path
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'engine/runtime'))
from speech_edit import tighten,map_time
from photo_depth import smooth,document,page_turn,view
from film_runtime import FilmVisuals,decode,wav,rms,FF
spec=importlib.util.spec_from_file_location('intro4_profile',ROOT/'engine/projects/escobar_intro4/profile.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
B=P.BUILD;PROJ=P.PROJECT;SRC=P.REFERENCE;W,H=P.WIDTH,P.HEIGHT;FPS=P.FPS
visuals=FilmVisuals([PROJ/'assets',SRC/'assets'],(W,H),ROOT/'assets_global/fonts',P.DEPTH)
image=visuals.image


def validate():
    from documentary_materials import material_errors
    from production_policy import enforce_display,enforce_design
    d=json.loads((PROJ/'display_manifest.json').read_text());enforce_display(d);enforce_design(d['design'])
    errors=material_errors(json.loads((PROJ/'MATERIALS.json').read_text()))
    if errors:raise ValueError('; '.join(errors))
    for a in json.loads((PROJ/'research/verified_asset_hashes.json').read_text()).values():
        if hashlib.sha256((ROOT/a['path']).read_bytes()).hexdigest()!=a['sha256']:raise ValueError('Reviewed visual source changed')


def prepare():
    validate()
    B.mkdir(parents=True,exist_ok=True);(B/'clips').mkdir(exist_ok=True);audit={};narr={}
    if hashlib.sha256(P.ARCHIVE_FILE.read_bytes()).hexdigest()!='6b533a7506d8996607780271ed627dbc49fe9f2e348fc061dec7596ce8e754e7':raise ValueError('Genuine source hash mismatch')
    for key in P.NARRATOR_ORDER:
        source=SRC/'voice'/f'broad_{key}.mp3';x=decode(source)
        words=json.loads((SRC/'research'/f'broad_{key}_asr.json').read_text())['words']
        y,edits=tighten(x,words,explicit=P.VOICE_PHRASE_REMOVALS.get(key,()))
        wav(B/'clips'/f'{key}.wav',y);narr[key]=len(y)/48000
        edits['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();edits['words']=[{**w,'edited_start':map_time(w['start'],edits['mapping']),'edited_end':map_time(w['end'],edits['mapping'])} for w in words];audit[key]=edits
    sequence=['name_host','name_guest','ship','wealth','wanted','social','fear','questions','close'];timeline=[];at=0
    for key in sequence:
        if key in P.ARCHIVE:
            a=P.ARCHIVE[key];x=decode(P.ARCHIVE_FILE,a['in'],a['out']-a['in']);fade=144;x[:fade]*=np.linspace(0,1,fade);x[-fade:]*=np.linspace(1,0,fade);wav(B/'clips'/f'{key}.wav',x);duration=len(x)/48000
        else:duration=narr[key]
        timeline.append({'id':key,'start':at,'duration':duration,'end':at+duration});at+=duration+(.065 if key.startswith('name') else P.NARRATOR_GAP)
    duration=math.ceil((timeline[-1]['end']+P.ENDING_HOLD)*FPS)/FPS
    (B/'timeline.json').write_text(json.dumps({'clips':timeline,'duration':duration,'fps':FPS},indent=2));(B/'voice_edits.json').write_text(json.dumps(audit,indent=2))
    # Decode authentic moving pictures at the new original source bounds.
    for key in ['name_guest','ship','fear']:
        path=B/'frames'/key;path.mkdir(parents=True,exist_ok=True);a=P.ARCHIVE[key]
        if not (path/'complete').exists():
            subprocess.run([FF,'-v','error','-ss',str(a['in']),'-i',str(P.ARCHIVE_FILE),'-t',str(a['out']-a['in']),'-vf','fps=24,scale=1440:960','-q:v','2','-y',str(path/'%05d.jpg')],check=True);(path/'complete').write_text('Original bounded source; sampled, not interpolated.')
    print(json.dumps(json.loads((B/'timeline.json').read_text()),indent=2),flush=True)


@lru_cache(maxsize=1)
def timeline():return json.loads((B/'timeline.json').read_text())

def clip(key):return next(c for c in timeline()['clips'] if c['id']==key)

@lru_cache(maxsize=300)
def tv(key,n):
    files=sorted((B/'frames'/key).glob('*.jpg'));im=np.array(Image.open(files[min(max(0,n),len(files)-1)]).convert('RGB'));out=np.full((H,W,3),(5,7,9),np.uint8);out[60:1020,240:1680]=im
    return visuals.caption(out,'Charlie Rose  /  Nov 12, 1992')


def photo(name,center,span,u,credit,travel=(4,-1),yaw=.025):
    return visuals.caption(visuals.region(name,center,(center[0]+travel[0],center[1]+travel[1]),span,span*.965,u,yaw=yaw),credit)


def word_card(name,u,credit):
    """Real readable headline pixels, static scale/anchor. Marker is editorial.
    No blur, resynthesized glyphs, or outcome context anywhere in this frame.
    """
    crop=image(name);gray=cv2.cvtColor(crop,cv2.COLOR_RGB2GRAY)
    ys,xs=np.where(gray<155)
    if len(xs)==0:raise ValueError('Blank source-word crop')
    # Align actual ink bounds rather than differing screenshot margins.
    crop=crop[max(0,ys.min()-4):min(crop.shape[0],ys.max()+5),max(0,xs.min()-4):min(crop.shape[1],xs.max()+5)]
    width=790;height=round(width*crop.shape[0]/crop.shape[1]);patch=cv2.resize(crop,(width,height),interpolation=cv2.INTER_LANCZOS4)
    paper=np.full((H,W,3),(233,231,219),np.uint8);x=W//2-width//2;y=H//2-height//2
    # Paper fragment presented as a fragment, never a fabricated full newspaper.
    paper[y-24:y+height+24,x-35:x+width+35]=[249,248,242];paper[y:y+height,x:x+width]=patch
    progress=smooth((u-.04)/.24);length=round((width+26)*progress)
    if length:
        layer=np.full_like(paper,255);color=(255,227,96);start=x-13;yy=y+round(height*.63);thick=max(28,round(height*.68))
        cv2.line(layer,(start,yy+3),(start+length,yy-2),color,thick,cv2.LINE_AA)
        # Multiplication preserves dark original ink; no yellow wash over glyphs.
        paper=(paper.astype(np.uint16)*layer.astype(np.uint16)//255).astype(np.uint8)
    return visuals.caption(paper,credit+'  /  original headline pixels; editorial highlight')


def title(u):
    a=photo('city.jpg',(390,270),765,min(1,u/2),'Medellin  /  contemporary view',travel=(5,-1),yaw=.015)
    bg=Image.fromarray((a.astype(np.float32)*.20).astype(np.uint8));overlay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(overlay);f=visuals.font(174,True)
    for text,y,delay in [('PABLO',280,0),('ESCOBAR',480,.08)]:
        k=smooth((u-delay)/.25);tw=d.textlength(text,font=f);d.text(((W-tw)/2,y+12*(1-k)),text,font=f,fill=(235,230,212,round(k*255)))
    return np.array(Image.alpha_composite(bg.convert('RGBA'),overlay).convert('RGB'))


@lru_cache(maxsize=1)
def shots():
    rows=[]
    def add(start,end,kind,**kwargs):
        if end<=start:raise ValueError('Non-positive shot')
        rows.append({'start':start,'end':end,'kind':kind,**kwargs})
    c=clip('name_host');add(c['start'],clip('name_guest')['start'],'portrait',name='semana.jpg',center=[190,119],span=350,credit='Image: Semana 1983  /  Audio: Charlie Rose 1992')
    c=clip('name_guest');add(c['start'],clip('ship')['start'],'tv',key='name_guest')
    c=clip('ship');add(c['start'],clip('wealth')['start'],'tv',key='ship')
    c=clip('wealth');s=c['start'];end=clip('wanted')['start']
    add(s,s+1.9,'cover');add(s+1.9,s+2.55,'turn');add(s+2.55,s+4.65,'entry')
    add(s+4.65,s+6.8,'portrait',name='semana.jpg',center=[190,119],span=350,credit='Semana  /  1983 photograph')
    add(s+6.8,s+8.8,'entry_name')
    add(s+8.8,end,'entry_close')
    c=clip('wanted');add(c['start'],clip('social')['start'],'congress_audio')
    c=clip('social');s=c['start'];end=clip('fear')['start']
    #2schanges, but never change for every sentence. Exact housing photo, not a generic city.
    add(s,s+3.35,'portrait',name='semana.jpg',center=[190,119],span=350,credit='Semana  /  1983 photograph')
    add(s+3.35,s+4.67,'housing');add(s+4.67,s+5.9,'football')
    add(s+5.9,s+8.05,'housing_close');add(s+8.05,end,'congress')
    c=clip('fear');s=c['start'];end=clip('questions')['start'];add(s,s+3.2,'tv',key='fear');add(s+3.2,end,'portrait',name='forbes_entry.png',center=[284,681],span=390,credit='Image: Forbes 1987  /  Audio: Charlie Rose 1992')
    c=clip('questions');s=c['start'];end=clip('close')['start']
    add(s,s+1.9,'portrait',name='semana.jpg',center=[190,119],span=350,credit='Semana  /  1983 photograph')
    add(s+1.9,s+4.85,'congress');add(s+4.85,s+6.65,'football_close');add(s+6.65,s+8.4,'housing');add(s+8.4,end,'city')
    c=clip('close');s=c['start'];add(s,s+2,'press',name='guardian_word.png',credit='The Guardian  /  archive webpage name only');add(s+2,s+4,'press',name='elpais_word.png',credit='El Pais  /  2021 article headline');add(s+4,timeline()['duration'],'title')
    return rows


def frame(t):
    ss=shots();s=next((r for r in ss if r['start']<=t<r['end']),ss[-1]);u=(t-s['start'])/(s['end']-s['start']);kind=s['kind']
    if kind=='tv':out=tv(s['key'],int(max(0,t-clip(s['key'])['start'])*FPS))
    elif kind=='press':out=word_card(s['name'],u,s['credit'])
    elif kind=='portrait':out=photo(s['name'],s['center'],s['span'],u,s['credit'])
    elif kind=='cover':out=visuals.caption(document(image('forbes_cover.png'),1490-30*smooth(u),(W,H)),'Forbes  /  Oct 5, 1987')
    elif kind=='turn':out=visuals.caption(page_turn(image('forbes_cover.png'),image('forbes_entry.png'),u,(W,H)),'Forbes  /  Oct 5, 1987')
    elif kind in ['entry','entry_close']:out=photo('forbes_entry.png',(316,640) if kind=='entry' else (283,675),570 if kind=='entry' else 445,u,'Forbes  /  original 1987 entry')
    elif kind=='entry_name':
        im=image('forbes_entry.png').copy();layer=np.full_like(im,255);length=round(139*smooth(u/.22));cv2.line(layer,(5,497),(5+length,497),(255,232,105),15,cv2.LINE_AA);im=(im.astype(np.uint16)*layer.astype(np.uint16)//255).astype(np.uint8)
        out=visuals.caption(view(im,(184+4*smooth(u),550),405,(W,H),yaw=.012*math.sin(u*math.pi)),'Forbes 1987  /  original entry; editorial highlight')
    elif kind in ['housing','housing_close']:
        im=image('housing1983.jpg');h,w=im.shape[:2];center=(w*.5,h*.5) if kind=='housing' else (w*.61,h*.60)
        out=photo('housing1983.jpg',center,w*.98 if kind=='housing' else w*.67,u,'Housing under construction, 1983  /  Edgar El Chino Jimenez; El Pais')
    elif kind in ['football','football_close']:out=visuals.caption(visuals.depth_scene('football.jpg').render((300,262) if kind=='football' else (317,265),575 if kind=='football' else 470,u,(W,H),travel=.045),'1983  /  El Tiempo archive  /  animated photograph')
    elif kind in ['congress','congress_audio']:out=photo('congress.jpg',(295,197),585,u,'Escobar in Congress, 1983  /  Audio: Charlie Rose 1992' if kind=='congress_audio' else 'Escobar in Congress  /  El Tiempo archive')
    elif kind=='city':out=visuals.caption(visuals.depth_scene('city.jpg').render((390,270),770,u,(W,H),depth=.12,travel=.07),'Medellin  /  contemporary establishing view')
    elif kind=='title':out=title(t-s['start'])
    else:raise ValueError(kind)
    fade=min(1,t/.04,max(0,(timeline()['duration']-1/FPS-t)/.18))
    return out if fade>=1 else (out.astype(np.float32)*fade).astype(np.uint8)


def audio():
    D=timeline()['duration'];sr=48000;n=round(D*sr);time=np.arange(n)/sr;dialog=np.zeros(n);audit=[]
    for c in timeline()['clips']:
        x=decode(B/'clips'/f"{c['id']}.wav");blocks=x[:len(x)//960*960].reshape(-1,960);a=np.sqrt(np.mean(blocks**2,axis=1))>.012
        gain=min(.14/max(rms(blocks[a]),1e-8),.78/max(abs(x)));at=round(c['start']*sr);dialog[at:at+len(x)]+=x*gain;audit.append({**c,'gain':gain})
    rng=np.random.default_rng(104);bed=np.zeros(n)
    for start,end,notes in [(0,18,[55,130.8128,164.8138]),(15,34,[43.6535,130.8128,174.6141]),(31,46,[51.9131,123.4708,155.5635]),(43,D+2,[48.9994,146.8324,195.9977])]:
        env=np.clip((time-start)/1.3,0,1)*np.clip((end-time)/2.2,0,1)
        for j,f in enumerate(notes):bed+=(np.sin(2*np.pi*f*time+j*.4)+.14*np.sin(2*np.pi*f*1.002*time))*env*.010/(1+j*.7)
    for j,at in enumerate(np.arange(clip('wealth')['start'],D-.5,60/110/2)):
        k=round(at*sr);count=min(round(.55*sr),n-k);u=np.arange(count)/sr;f=[110,164.8138,130.8128,146.8324][j%4]
        pulse=(np.sin(2*np.pi*f*u)+.13*np.sin(2*np.pi*f*2*u))*np.exp(-u*12)*np.clip(u/.007,0,1)
        strength=.004 if j%4 else .008
        if clip('fear')['start']<=at<clip('questions')['start']:strength*=.25
        bed[k:k+count]+=pulse*strength
    envelope=np.sqrt(np.convolve(dialog[::480]**2,np.ones(9)/9,mode='same'));duck=np.interp(time,np.arange(len(envelope))*.01,np.clip(1-envelope*3,.5,1));bed*=1.7*duck*np.clip(time/.2,0,1)*np.clip((D-time)/.5,0,1)
    sfx=np.zeros(n);events=[]
    for s in shots():
        if s['kind'] in ['press','entry','housing'] or s['kind']=='cover':events.append((s['start'],'camera shutter'))
        if s['kind']=='turn':events.append((s['start'],'paper turn'))
    for at,kind in events:
        k=round(at*sr);count=round(.21*sr);u=np.arange(count)/sr
        noise=rng.normal(0,1,count)
        if kind=='camera shutter':
            env=np.exp(-np.maximum(0,u-.008)*95)*(u>=.008)+.6*np.exp(-np.maximum(0,u-.085)*105)*(u>=.085)
            x=(noise*.48+np.sin(2*np.pi*420*u)*.40+np.sin(2*np.pi*1900*u)*.15)*env
        else:x=np.convolve(noise,np.ones(23)/23,mode='same')*np.sin(np.pi*u/.21)**2
        local=bed[k:k+count];x*=rms(local)*10**(-8/20)/max(rms(x),1e-8);sfx[k:k+count]+=x
    mix=dialog+bed+sfx;wav(B/'unmastered.wav',mix)
    log=subprocess.run([FF,'-hide_banner','-i',str(B/'unmastered.wav'),'-af','loudnorm=I=-16:TP=-1.4:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;m=json.loads(log[log.rfind('{'):log.rfind('}')+1]);gain=min(-16-float(m['input_i']),-1.6-float(m['input_tp']));wav(B/'mix.wav',mix*10**(gain/20));wav(B/'dialogue_stem.wav',dialog*10**(gain/20));wav(B/'music_stem.wav',bed*10**(gain/20));wav(B/'sfx_stem.wav',sfx*10**(gain/20))
    (B/'audio_audit.json').write_text(json.dumps({'clips':audit,'sfx_events':events,'sfx_relative_to_music_db':-8,'master_constant_gain_db':gain,'global_time_stretch':False,'pitch_shift':False,'new_voice_generation':False,'manual_listening_claimed':False,'name_bites_source':'Two speakers from the SAME1992CharlieRoseprogramme, not separate news broadcasts. ABC acquisition was blocked and excluded.'},indent=2))


def stills():
    (B/'review').mkdir(exist_ok=True);ss=shots();ims=[]
    for i,s in enumerate(ss):
        t=(s['start']+s['end'])/2;im=Image.fromarray(frame(t));im.save(B/'review'/f'shot_{i:02}.jpg',quality=94);im.thumbnail((400,225));ims.append(im)
    for start in range(0,len(ims),16):
        sheet=Image.new('RGB',(1600,4*248),(10,12,14));d=ImageDraw.Draw(sheet)
        for j,im in enumerate(ims[start:start+16]):
            sheet.paste(im,(j%4*400,j//4*248));s=ss[j+start];d.text((j%4*400+5,j//4*248+228),f"{s['start']:.2f}-{s['end']:.2f}s {s['kind']}",fill='white')
        sheet.save(B/'review'/f'staging_{start//16+1}.jpg',quality=94)
    (B/'shots.json').write_text(json.dumps(ss,indent=2))


def finish():
    validate()
    D=timeline()['duration'];count=round(D*FPS);out=B/'Escobar_Intro_Revision4_Faster_Rhythm.mp4'
    with (B/'encode.log').open('w')as log:
        proc=subprocess.Popen([FF,'-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-i',str(B/'mix.wav'),'-t',str(D),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','title=Pablo Escobar — Revision4, faster varied rhythm','-metadata','comment=Internal review. Authentic sources, two real name voices from one1992programme; no invented multibroadcast montage. Original narrator performance pause-edited, not sped up.2.5Dphoto animation/background reconstruction disclosed; contemporary city labeled. Genuine press-word pixels highlighted editorially. No prison/fate/escape spoilers; rights not cleared.',str(out)],stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(count):
                proc.stdin.write(frame(n/FPS).tobytes())
                if n%120==0:print('FRAME',n,'/',count,flush=True)
        finally:proc.stdin.close()
        if proc.wait():raise RuntimeError('Encoding failed')
    (B/'render.json').write_text(json.dumps({'duration':D,'frames':count,'fps':FPS,'resolution':[W,H],'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'user_approved':False,'visual_review_complete':False,'manual_listening_claimed':False,'revision3_untouched':True,'composition':'Shared XYZ/photo_depth engine; native1080pcomposition of lower-resolution authentic sources.'},indent=2));print('DONE',out,flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['prepare','audio','stills','finish']);args=a.parse_args();globals()[args.action]()
