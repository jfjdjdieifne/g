"""Source-led new opening; data/decisions only. Shared engine renders and mixes it."""
from pathlib import Path
import json,math,hashlib,shutil
import numpy as np
from film_runtime import decode,wav
from speech_edit import tighten,map_time
PROJECT=Path(__file__).parent;ROOT=PROJECT.parents[2]
BUILD=Path('/home/user/build/escobar_intro5');MEDIA=BUILD/'selected_media'
FPS=24;SIZE=(1920,1080);BPM=144;OUTPUT='Escobar_Intro_Revision5_New_Cut.mp4'
ASSET_DIRS=[PROJECT.parent/'escobar_intro3/assets',PROJECT.parent/'escobar_intro4/assets']
FONT_DIR=ROOT/'assets_global/fonts'
VOICE='voice-02'
DEPTH_SPECS=json.loads((PROJECT.parent/'escobar_intro3/depth_masks.json').read_text())

def prepare():
    (BUILD/'clips').mkdir(exist_ok=True,parents=True);(PROJECT/'voice').mkdir(exist_ok=True);audit={};narr={}
    for key in ['hook','industry','close']:
        src=BUILD/'voice'/f'{key}_take1.wav';asr=src.with_name(f'{key}_take1_asr.json');j=json.loads(asr.read_text());words=[w for s in j['segments']for w in s.get('result',[])];x=decode(src);full_duration=len(x)/48000
        if key=='industry':
            # The first sentence only: all rest of the new raw take remains preserved.
            x=x[:round(6.55*48000)];words=[w for w in words if w['end']<=6.45]
        y,edits=tighten(x,words,threshold=.30,target=.18)
        edits['complete_raw_duration']=full_duration;edits['selected_source_bounds']=[0,len(x)/48000];edits['source_sha256']=hashlib.sha256(src.read_bytes()).hexdigest();edits['words']=[{**w,'edited_start':map_time(w['start'],edits['mapping']),'edited_end':map_time(w['end'],edits['mapping'])}for w in words];edits['wpm']=len(words)/(len(y)/48000)*60
        wav(BUILD/'clips'/f'{key}.wav',y);audit[key]=edits;narr[key]=len(y)/48000
        for f in [src,asr]:
            dest=PROJECT/'voice'/f.name
            if not dest.exists():shutil.copy2(f,dest)
    audio=[];at=0
    for key,kind,dur,source,source_in in [
        ('hook','narration',narr['hook'],BUILD/'clips/hook.wav',0),
        ('cash','archive',3.99,MEDIA/'pbs_cash.mp4',0),
        ('industry','narration',narr['industry'],BUILD/'clips/industry.wav',0),
        ('max','archive',3.22,MEDIA/'pbs_max.mp4',.63),
        ('close','narration',narr['close'],BUILD/'clips/close.wav',0)]:
        if kind=='archive':
            x=decode(source,source_in,dur);x[:192]*=np.linspace(0,1,192);x[-192:]*=np.linspace(1,0,192);wav(BUILD/'clips'/f'{key}.wav',x);source=BUILD/'clips'/f'{key}.wav';dur=len(x)/48000
        start=math.ceil(at*FPS)/FPS;audio.append({'id':key,'kind':kind,'file':str(source),'start':start,'end':start+dur,'duration':dur});at=start+dur+.04
    clips={c['id']:c for c in audio};D=math.ceil((audio[-1]['end']+1.0)*FPS)/FPS;rows=[]
    def add(start,end,id,kind,**kwargs):
        first=round(start*FPS);last=round(end*FPS)
        if last<=first:raise ValueError('Empty shot')
        rows.append({'id':id,'kind':kind,'first':first,'last':last,'start':first/FPS,'end':last/FPS,**kwargs})
    def video(start,end,id,key,source_in,credit,meaning,**kwargs):
        add(start,end,id,'video',path=str(MEDIA/(key+'.mp4')),source_in=source_in,credit=credit,meaning=meaning,**kwargs)
    def image(start,end,id,asset,center,span,credit,meaning):
        add(start,end,id,'image',asset=asset,center=center,span=span,push=.035,yaw=.025,travel=[4,-2],credit=credit,meaning=meaning)
    s=clips['hook']['start'];end=clips['cash']['start']
    video(s,s+1.12,'cold_flight','pbs_takeoff',.05,['FRONTLINE / 1995','Aircraft imagery from its Escobar report'],'Trafficking: moving aircraft, contextual not a claimed photographed cocaine load')
    image(s+1.12,s+2.556,'billionaire_entry','forbes_entry.png',[315,641],650,['Forbes / 1987 billionaires issue'],'Actual Escobar entry; NOT a claim he was the richest man')
    image(s+2.556,s+4.172,'congress','congress.jpg',[300,220],600,['Congress, 1983 / El Tiempo archive'],'Elected alternate representative, not president')
    image(s+4.172,s+5.492,'homes','housing1983.jpg',[600,420],1180,['Housing construction, 1983','Edgar El Chino Jimenez / El Pais'],'The actual housing project, not a generic town')
    video(s+5.492,s+7.408,'city_terror','aj_aftermath',2.05,['Historical footage / Al Jazeera report, 2018'],'Actual response footage, continuous rather than falsely counted as two new shots; no literal added gunfire',watermark=True)
    video(s+7.408,s+8.904,'actual_escobar','pbs_escobar',.30,['Pablo Escobar / FRONTLINE, 1995'],'Actual moving subject on his name, not a portrait repeated as new sources')
    video(s+8.904,s+10.70,'estate','pbs_estate',1.0,['Hacienda Napoles / FRONTLINE, 1995'],'His estate on the word rich')
    # A motivated return to the subject in a DIFFERENT filmed moment/clothing, not a still crop.
    add(s+10.70,end+.416667,'public_power_prelap','depth',asset='football.jpg',center=[300,262],span=575,credit=['Public appearance, 1983 / El Tiempo archive','Animated photograph'],meaning='Public/political standing rather than a repeated private-wealth clip; Cash prelap lasts 10 frames')
    c=clips['cash'];i=clips['industry'];video(end+.416667,i['start'],'cash_reveal','pbs_cash',.416667,['THOMAS CASH / DEA official','FRONTLINE / 1995'],'Same source picture and audio timestamps; editorial 7% push toward the comparison',speaker=True,push=.07,watermark=False)
    s=i['start'];end=clips['max']['start']
    video(s,s+1.34,'single_flight','pbs_aircraft',4.20,['FRONTLINE / 1995','Contextual aircraft imagery'],'A single flight: native aircraft view, never a claim this is the stated particular flight')
    video(s+1.34,s+2.45,'carry','pbs_takeoff',1.65,['FRONTLINE / 1995','Contextual aircraft imagery'],'Continuing flight transport, distinct source time without loop')
    video(s+2.45,s+4.35,'four_hundred_kilos','pbs_load',6.0,['FRONTLINE / 1995','Smuggling-route imagery'],'Source footage accompanies its own 400kg/trip reporting; not a visible weighing of 400kg')
    video(s+4.35,end,'ten_million','pbs_interdiction',2.0,['FRONTLINE / 1995','Smuggling-route imagery'],'The source reports a flight could net $10M; imagery does not purport to show the cash')
    c=clips['max'];end=clips['close']['start'];video(c['start'],end,'insider_threat','pbs_max',.63,['MAX MERMELSTEIN / Cartel insider (in disguise)','FRONTLINE / 1995'],'Actual on-camera speaker on the three-million-dollar contract claim',speaker=True)
    c=clips['close'];s=c['start']
    video(s,s+2.42,'power_question','pbs_night',.10,['FRONTLINE / 1995','Miami street imagery from its Escobar report'],
        'The operating environment of the cocaine economy, rather than repeating the Escobar home-movie scene')
    video(s+2.42,s+3.916667,'residents','bbc_housing',1.10,['Medellin residents / BBC News, 2013'],'Modern housing/community context, not an asserted specific recipient identity or 1980s record',watermark=True)
    video(s+3.916667,D,'public_image','aj_mural',1.8,['Medellin mural / Al Jazeera, 2018'],'Present-day public iconography on the question about defenders, followed by one editorial film title',watermark=True,freeze_tail=True,title_after=c['end']-(s+3.916667))
    for left,right in zip(rows,rows[1:]):
        if left['last']!=right['first']:raise ValueError('Timeline gap/overlap')
    assert rows[0]['first']==0 and rows[-1]['last']==round(D*FPS)
    (BUILD/'voice_edits.json').write_text(json.dumps(audit,indent=2));(PROJECT/'voice_edit_audit.json').write_text(json.dumps(audit,indent=2))
    return {'schema':'sequence-film/1','fps':FPS,'frames':round(D*FPS),'audio':audio,'shots':rows,'effects':[1.12,2.556,5.492,7.408,i['start'],clips['max']['start'],c['end']],'source_rights_cleared':False,'manual_listening_claimed':False,'global_speedup':False,'voice_regenerated_same_approved_identity':True,'native_footage_retimed':False,'title_freeze_disclosed':True}
