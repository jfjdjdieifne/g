#!/usr/bin/env python3
"""Evidence extraction for the actual final encode, including source-internal cuts.
Never sets manual-review flags itself. A contact sheet is evidence, not approval.
"""
import argparse,json,sys,subprocess,re,importlib.util
from pathlib import Path
import cv2
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'engine/runtime'))
from film_runtime import FF
from encoded_review import review
p=argparse.ArgumentParser();p.add_argument('profile');p.add_argument('--file',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
f=ROOT/'engine/projects'/a.profile/'profile.py';spec=importlib.util.spec_from_file_location('P',f);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
plan=json.loads((P.BUILD/'timeline.json').read_text());prefix=0
if plan.get('intro_prefix_external_locked'):
    pc=cv2.VideoCapture(str(P.INTRO));prefix=pc.get(cv2.CAP_PROP_FRAME_COUNT)/pc.get(cv2.CAP_PROP_FPS);pc.release()
cap=cv2.VideoCapture(str(a.file));frames=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);size=[round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))];cap.release()
assert fps==P.FPS and size==list(P.SIZE)
expected=plan['frames']+round(prefix*fps);assert frames==expected,(frames,expected)
a.out.mkdir(parents=True,exist_ok=True)
scan=subprocess.run([FF,'-hide_banner','-reinit_filter','0','-i',str(a.file),'-an','-vf',"scale=160:90,select='gt(scene,0.30)',showinfo",'-f','null','-'],capture_output=True,text=True,check=True)
(a.out/'scene_detection.log').write_text(scan.stderr)
detected=[float(t) for t in re.findall(r'pts_time:([0-9.]+)',scan.stderr)]
cuts=sorted(set([prefix]+[s['start']+prefix for s in plan['shots']]+detected))
windows=[]
for s in plan['shots']:
    if s['kind'] not in ['route','depth']:continue
    start,end=s['start']+prefix,s['end']+prefix;middle=(start+end)/2
    windows.append((start,end))  # Inspect the whole authored map/depth movement at12fps.
windows.extend([(max(0,prefix-.3),prefix+.3),(frames/fps-1,frames/fps)])
for c in plan['audio']:
    if c['kind']=='archive':windows.append((c['start']+prefix-.1,c['start']+prefix+.6))
review(a.file,a.out,fps,frames,cuts,windows,sheet_size=32)
(a.out/'review_spec.json').write_text(json.dumps({'profile':a.profile,'frames':frames,'fps':fps,'size':size,'planned_and_detected_cut_count':len(cuts),'detected_internal_and_planned_cuts':detected,'sampled_every_seconds':.5,'motion_sampling_every_frames':2,'windows':windows,'visual_inspection_pending':True,'manual_listening_claimed':False},indent=2))
