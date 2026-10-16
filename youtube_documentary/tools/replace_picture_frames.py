#!/usr/bin/env python3
"""Replace an exact silent-picture frame range after an authored scene correction.
Re-encodes the picture; never claims unchanged decoded pixels outside the patch.
Audio must be muxed once afterwards. This is not approved-prefix preservation.
"""
import sys,subprocess,json,hashlib
from pathlib import Path
import cv2,imageio_ffmpeg
base,patch,out=map(Path,sys.argv[1:4]);a,b=map(int,sys.argv[4:6])
def spec(f):
 c=cv2.VideoCapture(str(f));v=(round(c.get(cv2.CAP_PROP_FRAME_COUNT)),c.get(cv2.CAP_PROP_FPS),round(c.get(cv2.CAP_PROP_FRAME_WIDTH)),round(c.get(cv2.CAP_PROP_FRAME_HEIGHT)));c.release();return v
s,p=spec(base),spec(patch);assert s[1:]==p[1:] and p[0]==b-a and 0<a<b<s[0],(s,p,a,b)
f=f'[0:v]split=2[s0][s1];[s0]trim=end_frame={a},setpts=PTS-STARTPTS[pre];[1:v]setpts=PTS-STARTPTS[part];[s1]trim=start_frame={b},setpts=PTS-STARTPTS[post];[pre][part][post]concat=n=3:v=1:a=0[v]'
r=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-y','-i',str(base),'-i',str(patch),'-filter_complex',f,'-map','[v]','-an','-c:v','libx264','-preset','fast','-threads','2','-crf','18','-pix_fmt','yuv420p','-r',str(s[1]),'-movflags','+faststart',str(out)],capture_output=True,text=True,check=True)
assert spec(out)==s,(spec(out),s)
out.with_suffix('.patch.json').write_text(json.dumps({'base':str(base),'patch':str(patch),'output':str(out),'absolute_frames':[a,b],'frame_spec':s,'note':'Silent-picture revision, fully re-encoded. No claim of unchanged outside pixels. Not applied to approved Escobar or approved prefix.','sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2));out.with_suffix('.patch.log').write_text(r.stderr);print(out)
