"""Shared segmented encoding path for long profiles. Same scene renderer for
animated stills/maps; native source video goes through FFmpeg at unchanged speed.
Preserves codec/frame rate across segments. No film-specific editorial decisions.
"""
import json,subprocess,hashlib
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from film_runtime import FF


def render_segments(film,destination):
    p=film.p;root=p.BUILD/'render_segments';root.mkdir(parents=True,exist_ok=True)
    W,H=p.SIZE;fps=p.FPS;segments=[]
    for index,s in enumerate(film.plan['shots']):
        n=s['last']-s['first'];dest=root/f'{index:04d}_{s["id"]}.mp4';stamp=dest.with_suffix('.json')
        base_fingerprint=hashlib.sha256(json.dumps({'shot':s,'size':p.SIZE,'fps':fps,'engine':3},sort_keys=True).encode()).hexdigest()
        options=getattr(p,'ENCODE',{'crf':19})
        fingerprint=hashlib.sha256((base_fingerprint+json.dumps(options,sort_keys=True)).encode()).hexdigest()
        reusable_hq=dest.exists() and stamp.exists() and stamp.read_text()==base_fingerprint
        segments.append(dest)
        if dest.exists() and stamp.exists() and stamp.read_text()==fingerprint:continue
        encode=['-an','-c:v','libx264','-threads','2','-preset','fast','-crf',str(options.get('crf',19)),'-pix_fmt','yuv420p','-r',str(fps),'-video_track_timescale','12288']
        if options.get('maxrate'):encode+=['-maxrate',options['maxrate'],'-bufsize',options['bufsize']]
        if reusable_hq:
            temporary=dest.with_name(dest.stem+'_recode.mp4')
            subprocess.run([FF,'-v','error','-y','-i',str(dest),'-frames:v',str(n),*encode,str(temporary)],check=True)
            temporary.replace(dest)
        elif s['kind']=='video':
            if s.get('push') or s.get('title_after') or s.get('freeze_tail'):raise ValueError('Native segmented video cannot silently alter motion; use standard renderer for these effects')
            layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer);lines=s.get('credit',[]);base=H-42-42*len(lines)
            if lines:
                for y in range(max(0,base-36),H):d.line((0,y,W,y),fill=(3,7,10,round(185*min(1,(y-base+36)/80))))
                for i,line in enumerate(lines):
                    font=film.visuals.font(31,i==0 and bool(s.get('speaker')));x=W-54-d.textlength(line,font=font) if s.get('watermark') else 54
                    d.text((x,base+42*i),line,font=font,fill=(231,231,222),stroke_width=1,stroke_fill=(0,0,0,180))
            if s.get('watermark'):layer.paste((0,0,0,0),(0,H-240,230,H))
            overlay=root/f'{index:04d}_credit.png';layer.save(overlay)
            fade=f",fade=t=out:st={max(0,n/fps-s['fade_out'])}:d={s['fade_out']}" if s.get('fade_out') else ''
            filt=f'[0:v]fps={fps},scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x030507,setsar=1[v];[v][1:v]overlay=0:0:shortest=1{fade},format=yuv420p[out]'
            subprocess.run([FF,'-v','error','-y','-ss',str(s['source_in']),'-i',s['path'],'-loop','1','-i',str(overlay),'-filter_complex_threads','1','-filter_complex',filt,'-map','[out]','-frames:v',str(n),*encode,str(dest)],check=True)
        else:
            proc=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-frames:v',str(n),*encode,str(dest)],stdin=subprocess.PIPE)
            try:
                for frame in range(s['first'],s['last']):proc.stdin.write(film.frame(frame).tobytes())
            finally:proc.stdin.close()
            if proc.wait():raise RuntimeError('Animated segment failed '+s['id'])
        cap=cv2.VideoCapture(str(dest));actual=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));cap.release()
        if actual!=n:raise ValueError(f'Segment frame count mismatch: {s["id"]}: {actual} != {n}')
        stamp.write_text(fingerprint);print('SHOT',index+1,'/',len(film.plan['shots']),s['id'],flush=True)
    listing=root/'concat.txt';listing.write_text(''.join("file '"+str(f).replace("'","'\\''")+"'\n" for f in segments))
    subprocess.run([FF,'-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-i',str(p.BUILD/'mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(film.plan['frames']/fps),'-movflags','+faststart',str(destination)],check=True)
    return destination
