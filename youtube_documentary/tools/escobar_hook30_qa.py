#!/usr/bin/env python3
"""Decode every delivery frame; make 60 half-second visual samples.
Visual judgement remains manual; this script does not certify art or hearing.
"""
import json
import re
import subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from escobar_hook30 import BUILD,FPS,W,H,DUR,BOLD

video=BUILD/'escobar_hook30_v1.mp4';out=BUILD/'qa';out.mkdir(exist_ok=True)
reader=imageio_ffmpeg.read_frames(str(video),pix_fmt='rgb24');meta=next(reader)
assert meta['size']==(W,H),meta
assert abs(meta['fps']-FPS)<.01,meta
assert abs(meta['duration']-DUR)<.05,meta
count=0;sample_count=0;contact=None
for i,raw in enumerate(reader):
    count+=1
    if i%12:continue
    im=Image.fromarray(np.frombuffer(raw,np.uint8).reshape(H,W,3))
    im.save(out/f'frame_{i:04d}.jpg',quality=95)
    j=sample_count%20
    if j==0:contact=Image.new('RGB',(1920,1500),(12,18,24))
    thumb=im.resize((480,270),Image.Resampling.LANCZOS)
    x=(j%4)*480;y=(j//4)*300
    contact.paste(thumb,(x,y));ImageDraw.Draw(contact).text((x+12,y+274),f'{i/FPS:05.2f} s',font=ImageFont.truetype(BOLD,19),fill='white')
    sample_count+=1
    if j==19:contact.save(out/f'contact_{sample_count//20:02d}.jpg',quality=96)
assert count==FPS*DUR,count
assert sample_count==60,sample_count
ff=imageio_ffmpeg.get_ffmpeg_exe()
p=subprocess.run([ff,'-hide_banner','-i',str(video),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
(out/'loudness.log').write_text(p.stderr)
m=re.search(r'\{\s*"input_i".*?\}',p.stderr,re.S);loudness=json.loads(m.group()) if m else {'error':'measurement missing'}
report={'file':str(video),'bytes':video.stat().st_size,'decoded_frames':count,'visual_samples':sample_count,'duration':meta['duration'],'fps':meta['fps'],'size':meta['size'],'loudness':loudness,'visual_review_status':'pending manual viewing of contact sheets and selected full frames','hearing_review_status':'No full listening-based certification. Exact narrator take previously user approved.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
