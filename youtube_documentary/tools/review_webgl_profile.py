#!/usr/bin/env python3
"""Extract actual-encode evidence for a WebGL profile. Never auto-claims inspection."""
import sys,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'engine/runtime'))
from encoded_review import review
import cv2
p=Path(sys.argv[1]);video=Path(sys.argv[2]);out=Path(sys.argv[3]);c=json.loads((p/'render.json').read_text());m=json.loads((p/'MATERIALS.json').read_text())
cap=cv2.VideoCapture(str(video));frames=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);size=[round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))];cap.release()
assert frames==round(c['duration']*c['fps']) and fps==c['fps'] and size==[c['width'],c['height']],(frames,fps,size)
cuts=sorted(set([b['in']for b in m['beats']]+c.get('review_joins',[])+[c['duration']-.8]))
review(video,out,fps,frames,cuts,c.get('review_motion_windows',[]),sheet_size=20)
(out/'review_spec.json').write_text(json.dumps({'every_half_second':True,'motion_windows':c.get('review_motion_windows',[]),'join_seconds':cuts,'source':'Final muxed MP4, not authoring stills','actual_inspection_pending':True,'ear_listening_claimed':False},indent=2))
