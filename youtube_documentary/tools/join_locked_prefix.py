#!/usr/bin/env python3
"""Join a previously approved clip without re-encoding any of its AV packets.
Validate every decoded approved picture frame and every stereo audio sample.
This is not a listening or artistic approval test.
"""
import argparse,importlib.util,sys,json,hashlib,subprocess
from pathlib import Path
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'engine/runtime'))
from film_runtime import FF
p=argparse.ArgumentParser();p.add_argument('profile');p.add_argument('--output');p.add_argument('--verify-only',action='store_true');a=p.parse_args()
f=ROOT/'engine/projects'/a.profile/'profile.py';spec=importlib.util.spec_from_file_location('P',f);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
prefix=P.INTRO;body=P.BUILD/P.OUTPUT;target=P.BUILD/(a.output or getattr(P,'FULL_OUTPUT',a.profile+'_Full_Film_Review.mp4'))
assert hashlib.sha256(prefix.read_bytes()).hexdigest()==P.INTRO_SHA256,'Approved original changed'
cap=cv2.VideoCapture(str(prefix));prefix_frames=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);cap.release();prefix_seconds=prefix_frames/fps
listing=P.BUILD/'locked_prefix_concat.txt';listing.write_text(f"file '{prefix}'\nduration {prefix_seconds:.12f}\nfile '{body}'\n")
# The concat demuxer includes the first AAC encoder-delay packet. Compensate
# its1024-sample priming on the AUDIO clock only; picture packets remain at t=0.
priming_samples=getattr(P,'AAC_PRIMING_SAMPLES',1024);sample_rate=48000
if not a.verify_only:
    r=subprocess.run([FF,'-hide_banner','-y','-f','concat','-safe','0','-i',str(listing),'-itsoffset',str(-priming_samples/sample_rate),'-f','concat','-safe','0','-i',str(listing),'-map','0:v','-map','1:a','-c','copy','-movflags','+faststart',str(target)],capture_output=True,text=True,check=True)
    (P.BUILD/'concat.log').write_text(r.stderr)
def frame_hashes(file):
 data=subprocess.check_output([FF,'-v','error','-i',str(file),'-map','0:v','-frames:v',str(prefix_frames),'-f','framemd5','-']).decode()
 return [line.split(',')[-1].strip() for line in data.splitlines() if line and not line.startswith('#')]
left,right=frame_hashes(prefix),frame_hashes(target)
assert len(left)==prefix_frames and left==right,'Decoded approved picture prefix changed'
# Compare ALL approved samples. Slice by sample count because FFmpeg's time
# stopping can emit a complete AAC frame beyond -t at a concat discontinuity.
count=round(prefix_seconds*sample_rate)
def stereo(file):
    raw=subprocess.check_output([FF,'-v','error','-i',str(file),'-t',str(prefix_seconds+.05),'-vn','-ac','2','-ar',str(sample_rate),'-f','f32le','pipe:1'])
    return np.frombuffer(raw,dtype='<f4').reshape(-1,2)[:count]
x=stereo(prefix);y=stereo(target)
assert len(x)==len(y)==count,'Approved audio prefix is incomplete'
err=float(np.max(np.abs(x-y)))
assert np.array_equal(x,y),'Approved decoded audio prefix changed'
report={'output':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'approved_input_sha256':P.INTRO_SHA256,'approved_prefix_seconds':prefix_seconds,'prefix_video_decoded_frames_identical':prefix_frames,'prefix_audio_compared_seconds':len(x)/48000,'prefix_audio_max_difference':err,'prefix_audio_channels':2,'prefix_audio_compared_samples_per_channel':count,'codec':'H264/AAC packet-copy join; no speech/video speed change','aac_priming_compensation_samples':priming_samples,'aac_boundary_note':f'All {count} approved-prefix samples in EACH of two audio channels and every approved picture frame checked. Packet boundary after the prefix may contain sub-frame AAC padding; no speech is stretched.','manual_listening_claimed':False}
(P.PROJECT/'prefix_preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
