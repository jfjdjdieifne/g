"""Generic encoded-result evidence extraction; does not claim human approval/listening."""
import json,math,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
from film_runtime import FF

def sheet(files,path,labels,cols=4):
    rows=math.ceil(len(files)/cols);im=Image.new('RGB',(400*cols,248*rows),(10,12,14));d=ImageDraw.Draw(im)
    for i,f in enumerate(files):
        p=Image.open(f).convert('RGB');p.thumbnail((400,225));x=i%cols*400;y=i//cols*248;im.paste(p,(x,y));d.text((x+8,y+228),labels[i],fill='white')
    im.save(path,quality=94)

def review(video,destination,fps,frames,cuts,motion_windows,*,sheet_size=16):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True);video=Path(video)
    groups={'half':list(range(0,frames,round(fps/2))),'join':sorted(set([max(0,min(frames-1,math.ceil(t*fps)+offset)) for t in cuts for offset in [-1,0,1]]+[frames-1])),'motion':sorted(set([n for a,b in motion_windows for n in range(max(0,math.floor(a*fps)),min(frames,math.ceil(b*fps)),2)]))}
    for key,indices in groups.items():
        # Mixed original/encoded square-pixel H264 can change SAR metadata.
        # Keep one filter graph so select's n is the GLOBAL decoded frame index.
        for stale in destination.glob(key+'_[0-9][0-9][0-9][0-9].jpg'):stale.unlink()
        if not indices:continue
        expr='+'.join(f'eq(n,{n})' for n in indices).replace(',',r'\,')
        subprocess.run([FF,'-v','error','-xerror','-reinit_filter','0','-i',str(video),'-vf',f'select={expr},scale=400:225','-vsync','0','-q:v','2','-y',str(destination/f'{key}_%04d.jpg')],check=True)
        files=sorted(destination.glob(key+'_[0-9][0-9][0-9][0-9].jpg'))
        if len(files)!=len(indices):raise ValueError('Review evidence frame count mismatch')
        for start in range(0,len(files),sheet_size):sheet(files[start:start+sheet_size],destination/f'{key}_sheet_{start//sheet_size+1}.jpg',[f'Frame {n}  /  {n/fps:.4f}s' for n in indices[start:start+sheet_size]])
    result=subprocess.run([FF,'-hide_banner','-xerror','-i',str(video),'-af','loudnorm=I=-16:TP=-1.4:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
    m=json.loads(result[result.rfind('{'):result.rfind('}')+1]);(destination/'loudness.json').write_text(json.dumps(m,indent=2));(destination/'full_decode.log').write_text(result)
    audit={'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'encoded_frames_decoded':frames,'review_indices':groups,'frame_counts':{k:len(v)for k,v in groups.items()},'manual_listening_claimed':False,'manual_visual_review_complete':False,'read_loudness_input_not_output':{'LUFS':float(m['input_i']),'dBTP':float(m['input_tp']),'LRA':float(m['input_lra'])}}
    (destination/'audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps({k:v for k,v in audit.items()if k!='review_indices'},indent=2),flush=True)
