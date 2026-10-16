#!/usr/bin/env python3
"""Measure and extract actual encoded review evidence; not an art certificate."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import imageio_ffmpeg
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import escobar_hook30_revision2_finish as film


def main():
    video=film.BUILD/'Escobar_First30_English_Revision2.mp4'
    if not video.exists():raise SystemExit('No actual encoded revision2 movie')
    folder=film.BUILD/'encoded_review';folder.mkdir(exist_ok=True)
    base=list(range(0,720,12));between=[n+1 for n in base]
    edges=[181,182,183,184,282,283,284,318,319,320,387,388,526,527,528,587,588,589,704,705,706,707,718,719]
    targets=set(base+between+edges)
    gen=imageio_ffmpeg.read_frames(str(video),pix_fmt='rgb24');meta=next(gen)
    if tuple(meta['size'])!=(1920,1080) or abs(meta['fps']-24)>.001:raise ValueError('Unexpected encoded geometry/fps')
    means=[];count=0
    for n,raw in enumerate(gen):
        frame=np.frombuffer(raw,np.uint8).reshape(1080,1920,3)
        means.append(float(frame.mean()));count+=1
        if n in targets:Image.fromarray(frame).save(folder/f'frame_{n:04d}.jpg',quality=94)
    if count!=720:raise ValueError('Actual frame count '+str(count))
    font=ImageFont.truetype(film.FONT,22)
    for label,indices in [('base_2fps',base),('interstitial',between)]:
        for page in range(3):
            canvas=Image.new('RGB',(1920,1500),'#0b1014');d=ImageDraw.Draw(canvas)
            for k,n in enumerate(indices[page*20:(page+1)*20]):
                image=Image.open(folder/f'frame_{n:04d}.jpg');image.thumbnail((480,270))
                x=k%4*480;y=k//4*300;canvas.paste(image,(x,y))
                d.text((x+8,y+272),f'{n/24:06.3f}s  frame{n}',font=font,fill='white')
            canvas.save(folder/f'{label}_{page+1}.jpg',quality=94)
    # All edit boundaries reviewed together, including first frames after each cut.
    canvas=Image.new('RGB',(1920,math_ceil_rows(len(edges),3)*390),'#0b1014');d=ImageDraw.Draw(canvas)
    for k,n in enumerate(edges):
        image=Image.open(folder/f'frame_{n:04d}.jpg');image.thumbnail((640,360));x=k%3*640;y=k//3*390;canvas.paste(image,(x,y))
        d.text((x+8,y+362),f'{n/24:.3f}s frame{n}',font=font,fill='white')
    canvas.save(folder/'edit_boundaries.jpg',quality=94)
    log=subprocess.run([film.FF,'-hide_banner','-i',str(video),'-af','loudnorm=I=-16:TP=-1.4:LRA=11:print_format=json','-f','null','-'],text=True,capture_output=True,check=True).stderr
    loud=json.loads(log[log.rfind('{'):log.rfind('}')+1])
    if not (-17<float(loud['input_i'])<-15):raise ValueError('Loudness out of review range')
    if float(loud['input_tp'])>-.5:raise ValueError('Encoded true peak too high')
    result={'video':str(video),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,
            'metadata':meta,'decoded_frames':count,'full_decode_without_error':True,'black_frames':[i for i,v in enumerate(means) if v<.5],
            'base_2fps_samples':len(base),'interstitial_samples':len(between),'extra_boundary_samples':len(set(edges)-set(base+between)),
            'sampled_frame_files':len(targets),'encoded_audio_loudness':loud,'manual_listening':False,'visual_agent_review_complete':False,
            'visual_review_pending':'Actually view all six chronological sheets, edit-boundary sheet and detail frames. Do not set pass from technical success.',
            'technical_tests_are_art_approval':False,'publication_license_obtained':False}
    (film.BUILD/'encoded_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


def math_ceil_rows(n,cols):return (n+cols-1)//cols

if __name__=='__main__':main()
