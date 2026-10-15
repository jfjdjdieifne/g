#!/usr/bin/env python3
"""Assemble the source-led 30s revision2 editorial review cut.
No placeholders, quotation slides, caption transcription or cross-cut interpolation.
Approved narration stays one intact, unretimed recording. Not publication clearance.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import wave

import imageio_ffmpeg
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import escobar_hook30_revision2 as profile

FF=imageio_ffmpeg.get_ffmpeg_exe()
BUILD=profile.BUILD
W,H,FPS,DURATION=1920,1080,24,30
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ARCHIVE=Path('/home/user/build/escobar_archive_official/original_opening.mp4')


def decode(path,start=0,duration=None):
    args=[FF,'-v','error','-ss',str(start),'-i',str(path)]
    if duration is not None:args+=['-t',str(duration)]
    raw=subprocess.check_output(args+['-f','f32le','-acodec','pcm_f32le','-ar','48000','-ac','1','-'])
    return np.frombuffer(raw,dtype='<f4').astype(np.float64)


def write_wav(path,data):
    if data.ndim==1:data=np.column_stack([data,data])
    with wave.open(str(path),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(48000)
        out.writeframes((np.clip(data,-1,1)*32767).astype('<i2').tobytes())


def rms(a):return float(np.sqrt(np.mean(a*a)))


def speech_gain(a):
    n=len(a)//960;frames=a[:n*960].reshape(n,960);active=np.sqrt(np.mean(frames**2,axis=1))>.012
    level=rms(frames[active]) if active.any() else rms(a)
    return min(.135/max(level,1e-8),.78/max(abs(a)))


def make_audio():
    review=profile.verify_edit_gate();BUILD.mkdir(parents=True,exist_ok=True)
    sr=48000;n=sr*30;t=np.arange(n)/sr
    narrator=decode(profile.PROJECT/'assets/narrator_approved.mp3')
    archive=decode(ARCHIVE,29.8,7.4)
    dialog=np.zeros(n);ng=speech_gain(narrator);ag=speech_gain(archive)
    start=round(7.6*sr);dialog[start:start+len(narrator)]+=narrator*ng
    archive=archive[:round(7.4*sr)]
    fade=min(480,len(archive)//2);archive[:fade]*=np.linspace(0,1,fade);archive[-fade:]*=np.linspace(1,0,fade)
    dialog[:len(archive)]+=archive*ag
    # Original sparse minor-key underscore, not a borrowed score or orchestra.
    bed=np.zeros(n)
    for at,end,notes in [(0,8.2,[65.406,155.563,195.998]),(6.8,16.7,[51.913,130.813,155.563]),(15.2,24.8,[43.654,130.813,174.614]),(23.2,31,[48.999,146.832,195.998])]:
        attack=np.clip((t-at)/1.4,0,1);release=np.clip((end-t)/1.8,0,1);env=attack*release
        chord=np.zeros(n)
        for j,f in enumerate(notes):
            chord+=(np.sin(2*np.pi*f*t+j*.63)+.22*np.sin(2*np.pi*2*f*t+.4))/(1+j*.35)
        bed+=chord*env
    bed*=.012/max(rms(bed),1e-9)
    # Underscore comes forward gently at the narrator, not over archive speech.
    bed*=.42+.58*np.clip((t-7.1)/.8,0,1)
    bed*=np.clip(t/.5,0,1)*np.clip((30-t)/.65,0,1)
    sfx=np.zeros(n);rng=np.random.default_rng(19);sfx_audit=[]
    for at,length,kind in [(7.6,.55,'soft spatial arrival'),(11.8,.22,'subtle metal texture'),(13.3,.30,'desk transition'),(21.95,.45,'soft room change')]:
        count=round(length*sr);u=np.arange(count)/sr
        noise=rng.normal(0,1,count);noise=np.convolve(noise,np.ones(55)/55,mode='same')
        raw=noise*np.sin(np.pi*np.arange(count)/count)**2
        where=round(at*sr);reference=rms(bed[where:where+count]);target=reference*10**(-9/20)
        raw*=target/max(rms(raw),1e-9);sfx[where:where+count]+=raw
        sfx_audit.append({'time':at,'event':kind,'rms_db_relative_to_local_bed':20*math.log10(max(rms(raw),1e-9)/max(reference,1e-9))})
    mix=dialog+bed+sfx
    if np.max(abs(mix))>=.99:raise ValueError('Mix overload; no silent limiting of narration')
    write_wav(BUILD/'mix_unmastered.wav',mix)
    # Measure, then use ONLY constant master gain. No loudnorm dynamic fallback.
    analysis=subprocess.run([FF,'-hide_banner','-i',str(BUILD/'mix_unmastered.wav'),'-af','loudnorm=I=-16:TP=-1.2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
    measured=json.loads(analysis[analysis.rfind('{'):analysis.rfind('}')+1])
    gain_db=min(-16-float(measured['input_i']),-1.4-float(measured['input_tp']))
    master_gain=10**(gain_db/20)
    write_wav(BUILD/'mix.wav',mix*master_gain)
    stem=np.zeros(n);stem[start:start+len(narrator)]=narrator*ng*master_gain
    write_wav(BUILD/'narrator_stem.wav',stem)
    validation=subprocess.run([FF,'-hide_banner','-i',str(BUILD/'mix.wav'),'-af','loudnorm=I=-16:TP=-1.4:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
    checked=json.loads(validation[validation.rfind('{'):validation.rfind('}')+1])
    actual={'method':'constant gain only, no compressor/limiter/time change',
            'gain_db':gain_db,'output_i':checked['input_i'],'output_tp':checked['input_tp'],'output_lra':checked['input_lra']}
    audit={'actual_broadcast_audio':True,'archive_program':'Charlie Rose, 1992-11-12','source_in':29.8,'source_audio_out':37.2,'source_timeline':[0,7.4],
           'voice_id':'voice-02','voice_sha256':review['voice_sha256'],'narration_samples':len(narrator),'narration_sr':sr,'narrator_timeline':[7.6,7.6+len(narrator)/sr],
           'approved_voice_intact':True,'source_speed_change':False,'voice_pitch_change':False,'voice_speed_change':False,'voice_split':False,
           'narrator_constant_gain':ng,'archive_constant_gain':ag,'mastering':actual,'sfx':sfx_audit,
           'music':'Original synthesized minor-key ambient underscore; not orchestral','manual_listening':False,'review_methods':['primary source captions','ASR','waveform and mix measurements']}
    (BUILD/'audio_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print('AUDIO_READY',audit['narrator_timeline'],flush=True)


def prepare_frames():
    profile.verify_edit_gate()
    if not (BUILD/'samples_complete.json').exists():raise ValueError('Actual model renders not complete')
    for shot in profile.scene.SHOTS:
        src=BUILD/'samples'/shot['id'];dest=BUILD/'interpolated'/shot['id'];dest.mkdir(parents=True,exist_ok=True)
        count=math.ceil((shot['end']-shot['start'])*24)+3
        if (dest/'complete.json').exists():continue
        subprocess.run([FF,'-y','-v','error','-framerate','8','-i',str(src/'%05d.jpg'),
            '-vf','tpad=stop_mode=clone:stop_duration=0.5,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none',
            '-frames:v',str(count),'-q:v','2',str(dest/'%05d.jpg')],check=True)
        paths=list(dest.glob('*.jpg'))
        if len(paths)<count:raise ValueError('Incomplete interpolation for '+shot['id'])
        (dest/'complete.json').write_text(json.dumps({'frames':len(paths),'cross_cut_interpolation':False}))
        print('SHOT_PREPARED',shot['id'],flush=True)
    archive=BUILD/'archive_frames';archive.mkdir(exist_ok=True)
    subprocess.run([FF,'-y','-v','error','-ss','29.8','-i',str(ARCHIVE),'-t','7.7','-vf','fps=24,scale=1380:920:flags=lanczos','-q:v','2',str(archive/'%05d.jpg')],check=True)


def draw_label(image,xy,text,size,color=(238,233,218),bold=False):
    d=ImageDraw.Draw(image);f=ImageFont.truetype(BOLD if bold else FONT,size)
    d.text((xy[0]+1,xy[1]+2),text,font=f,fill=(8,13,16),anchor='ls',stroke_width=2,stroke_fill=(8,13,16))
    d.text(xy,text,font=f,fill=color,anchor='ls')


def compose(t,n):
    if t<7.6:
        frame=Image.open(BUILD/'archive_frames'/f'{n+1:05d}.jpg').convert('RGB')
        image=Image.new('RGB',(W,H),(7,10,12));image.paste(frame,(270,34))
        draw_label(image,(270,1025),'Archive: Charlie Rose  /  Nov 12, 1992',34)
    else:
        shot=next(s for s in profile.scene.SHOTS if s['start']<=t<s['end'])
        index=max(0,int((t-shot['start'])*24))+1
        path=BUILD/'interpolated'/shot['id']/f'{index:05d}.jpg'
        if not path.exists():raise ValueError('No model fallback permitted: '+str(path))
        image=Image.open(path).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
        image=image.filter(ImageFilter.UnsharpMask(radius=1.2,percent=45,threshold=4))
        if t<11.05:
            draw_label(image,(76,105),'La Catedral',60,bold=True)
            draw_label(image,(78,150),'Illustrative cutaway',32,color=(193,200,187))
    fade=min(1,t/.08,max(0,(30-t)/.22))
    if fade<1:image=Image.blend(Image.new('RGB',(W,H)),image,fade)
    return image


def finish():
    prepare_frames()
    if not (BUILD/'mix.wav').exists():make_audio()
    output=BUILD/'Escobar_First30_English_Revision2.mp4';temporary=BUILD/'encoding.tmp.mp4'
    with (BUILD/'encode.log').open('w') as log:
        args=[FF,'-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','24','-i','-',
              '-i',str(BUILD/'mix.wav'),'-t','30','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',
              '-movflags','+faststart','-metadata','title=Pablo Escobar — First 30 seconds, English, revision2',
              '-metadata','comment=Editorial review cut. Short authentic Charlie Rose interview quotation, November 12 1992, https://charlierose.com/videos/15564 . No publication license claimed. AI narrator: exact user-approved voice-02. Model: illustrative schematic, not surveyed architecture or evidence of an escape route. Model samples 960x540 (office1280x720) at8fps, interpolated per shot to24fps; final compositing1080p. No captions, fabricated anchor or quotation slides.',str(temporary)]
        proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(720):
                proc.stdin.write(compose(n/24,n).tobytes())
                if n%120==0:print('COMPOSITING',n,'/720',flush=True)
        finally:proc.stdin.close()
        if proc.wait():raise ValueError('Encoding failed; see encode.log')
    temporary.replace(output)
    pipeline={'version':'revision2','output':str(output),'duration':30,'frames':720,'delivery_resolution':[1920,1080],'fps':24,
        'model_samples_resolution':[960,540],'model_resolution_overrides':{'office':[1280,720]},'model_samples_fps':8,'model_samples_per_pixel':4,'backend':'Shared Cycles CPU World renderer',
        'interpolation':'Per shot MCI only, never across source/model or scene edits','narrator_retimed':False,
        'actual_source_video_audio':True,'on_screen_text':['Archive: Charlie Rose / Nov 12, 1992','La Catedral','Illustrative cutaway'],
        'captions':False,'quote_slides':False,'historical_reconstruction':False,'publication_rights_cleared':False,
        'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
    (BUILD/'image_pipeline.json').write_text(json.dumps(pipeline,indent=2)+'\n')
    print('ENCODE_COMPLETE',output,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audio',action='store_true');p.add_argument('--finish',action='store_true');a=p.parse_args()
    if a.audio:make_audio()
    elif a.finish:finish()
    else:p.error('Use --audio or --finish')
